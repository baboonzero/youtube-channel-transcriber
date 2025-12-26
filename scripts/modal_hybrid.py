"""
Hybrid Modal Transcriber - Best of both worlds
Downloads locally (bypasses YouTube bot detection)
Transcribes on Modal GPUs (parallel processing)
"""

import modal
import sys
import os
from pathlib import Path

# Add config to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "config"))
sys.path.insert(0, str(project_root))

# Change to project root directory so relative paths work
os.chdir(project_root)

# Import config
try:
    from config import CHANNEL_URL, AUDIO_DIR, DATABASE_FILE
except ImportError:
    CHANNEL_URL = None
    AUDIO_DIR = "data/temp_audio"
    DATABASE_FILE = "data/transcription_progress.db"

app = modal.App("youtube-transcriber-hybrid")

# Simple GPU image - no YouTube downloads needed!
# Using openai-whisper (faster-whisper has cuDNN incompatibility on Modal)
# Using uv_pip_install for 4x faster builds
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("ffmpeg")
    .uv_pip_install(
        "openai-whisper",
        "torch",
        "torchaudio",
    )
)

# GPU transcription class - model loaded once per container
@app.cls(
    image=image,
    gpu="A10G",
    timeout=600,
    retries=2,
)
class WhisperTranscriber:
    """
    Whisper transcriber that loads model once per container
    Uses @enter to load model when container starts (saves 5-10s per transcription)
    """

    @modal.enter()
    def load_model(self):
        """Load Whisper model once when container starts"""
        import whisper
        print("[CONTAINER] Loading Whisper model...")
        self.model = whisper.load_model("base", device="cuda")
        print("[CONTAINER] Model loaded and ready!")

    @modal.method()
    def transcribe(self, audio_bytes: bytes, video_id: str, video_title: str):
        """
        Transcribe audio on GPU using pre-loaded model
        Receives audio as bytes, saves to temp file for processing
        """
        import tempfile
        import whisper
        from pathlib import Path

        print(f"[{video_id}] Transcribing: {video_title[:50]}...")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Save audio bytes to file
            audio_file = Path(temp_dir) / f"{video_id}.webm"
            audio_file.write_bytes(audio_bytes)

            # Transcribe using pre-loaded model
            print(f"[{video_id}] Transcribing with Whisper...")
            result = whisper.transcribe(
                self.model,
                str(audio_file),
                language="en",
            )

        # Build transcript with timestamps
        transcript_lines = []
        duration = 0
        for segment in result['segments']:
            timestamp = f"{int(segment['start'] // 60):02d}:{int(segment['start'] % 60):02d}"
            transcript_lines.append(f"[{timestamp}] {segment['text'].strip()}")
            # Duration is the end time of the last segment
            if segment['end'] > duration:
                duration = segment['end']

        transcript = "\n".join(transcript_lines)

        print(f"[{video_id}] [OK] Complete! Duration: {duration:.1f}s")

        return {
            'video_id': video_id,
            'video_title': video_title,
            'transcript': transcript,
            'duration': duration,
        }


@app.local_entrypoint()
def main(
    audio_dir: str = None,
    output_dir: str = None,
    max_files: int = 10,
):
    """
    Main entry point
    Reads audio files from local disk, sends to Modal GPUs for transcription

    If audio_dir/output_dir not specified, automatically detects channel from database
    and uses proper channel-specific folders (matches local transcription structure)
    """
    import time
    import sqlite3
    from pathlib import Path

    print("="*70)
    print("Hybrid Modal Transcriber")
    print("Downloads: Local | Transcription: Modal GPUs")
    print("="*70)
    print()

    # Auto-detect channel if audio_dir not specified
    if audio_dir is None:
        db_path = Path(DATABASE_FILE)
        if not db_path.exists():
            print(f"Error: Database not found at {DATABASE_FILE}")
            print("Please run download_only.py first to download audio files.")
            return

        # Get channel name from database by matching config CHANNEL_URL
        # This is the SAME logic as prepare_for_modal.py
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        channel_name = None

        # Get all unique channels from database
        cursor.execute('SELECT DISTINCT channel FROM videos WHERE channel IS NOT NULL')
        all_channels = [row[0] for row in cursor.fetchall()]

        if not all_channels:
            conn.close()
            print("Error: No channels found in database")
            print("Please run prepare_for_modal.py first to scrape and download videos.")
            return

        # Try to match config CHANNEL_URL to a database channel
        if CHANNEL_URL:
            # Extract keywords from URL (remove common words, special chars)
            import re
            # Split on common delimiters first, then extract words
            url_text = CHANNEL_URL.lower()
            url_text = re.sub(r'[@/\-_]', ' ', url_text)  # Replace delimiters with spaces
            url_keywords = set(re.findall(r'[a-z0-9]{2,}', url_text))  # 2+ chars (not 3, to catch "AI")
            url_keywords -= {'http', 'https', 'www', 'youtube', 'com', 'channel', 'the'}

            # Try to find matching channel
            best_match = None
            best_score = 0

            for db_channel in all_channels:
                # Extract keywords from channel name (same process)
                channel_text = db_channel.lower()
                channel_text = re.sub(r'[@/\-_]', ' ', channel_text)
                channel_keywords = set(re.findall(r'[a-z0-9]{2,}', channel_text))

                # Calculate match score (how many keywords match)
                match_score = len(url_keywords & channel_keywords)

                if match_score > best_score and match_score > 0:
                    best_match = db_channel
                    best_score = match_score

            # Fallback: Try substring matching (e.g., "How I AI" → "howiai" in "howiaipodcast")
            if best_match is None:
                url_normalized = re.sub(r'[^a-z0-9]', '', CHANNEL_URL.lower())
                for db_channel in all_channels:
                    channel_normalized = re.sub(r'[^a-z0-9]', '', db_channel.lower())
                    # Check if channel name appears in URL or vice versa
                    if channel_normalized in url_normalized or url_normalized in channel_normalized:
                        # Longer match is better
                        score = max(len(channel_normalized), len(url_normalized))
                        if score > best_score:
                            best_match = db_channel
                            best_score = score

            if best_match:
                channel_name = best_match
                print(f"Using channel from config: {channel_name}")
            else:
                # No match found - show available channels
                conn.close()
                print("Error: Could not match config CHANNEL_URL to any channel in database")
                print()
                print(f"Config URL: {CHANNEL_URL}")
                print(f"URL keywords extracted: {url_keywords}")
                print()
                print("Available channels in database:")
                for ch in all_channels:
                    ch_text = re.sub(r'[@/\-_]', ' ', ch.lower())
                    ch_keywords = set(re.findall(r'[a-z0-9]{2,}', ch_text))
                    print(f"  - {ch} (keywords: {ch_keywords})")
                print()
                print("Please update config/config.py with the correct CHANNEL_URL")
                return
        else:
            # No CHANNEL_URL in config
            conn.close()
            print("Error: CHANNEL_URL not set in config.py")
            print()
            print("Available channels in database:")
            for ch in all_channels:
                print(f"  - {ch}")
            print()
            print("Please set CHANNEL_URL in config/config.py")
            return

        conn.close()

        audio_dir = f"{AUDIO_DIR}/{channel_name}"
        print(f"Audio directory: {audio_dir}")

        # If output_dir not specified, use proper channel-specific folder
        # (matches local transcription structure)
        if output_dir is None:
            try:
                from config import TRANSCRIPT_DIR
            except ImportError:
                TRANSCRIPT_DIR = "data/transcripts"
            output_dir = f"{TRANSCRIPT_DIR}/{channel_name}"
            print(f"Transcript directory: {output_dir}")
        print()

    audio_path = Path(audio_dir)
    if not audio_path.exists():
        print(f"Error: Audio directory not found: {audio_dir}")
        print()
        print("Make sure you've downloaded audio files first using download_only.py")
        return

    # Find audio files
    audio_files = list(audio_path.glob("*.webm")) + list(audio_path.glob("*.m4a"))
    audio_files = audio_files[:max_files]

    if not audio_files:
        print(f"No audio files found in: {audio_dir}")
        return

    print(f"Found {len(audio_files)} audio files")
    print(f"Processing {min(len(audio_files), max_files)} files with Modal GPUs...")
    print()

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    # Get video titles from database
    db_path = Path(DATABASE_FILE)
    video_titles = {}
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get all video IDs and titles
        video_ids = [f.stem for f in audio_files]
        placeholders = ','.join('?' * len(video_ids))
        cursor.execute(f'''
            SELECT video_id, title
            FROM videos
            WHERE video_id IN ({placeholders})
        ''', video_ids)

        for video_id, title in cursor.fetchall():
            video_titles[video_id] = title

        conn.close()

    # Create transcriber instance
    transcriber = WhisperTranscriber()

    # Spawn parallel GPU workers
    results = []
    for audio_file in audio_files:
        # Read audio file
        audio_bytes = audio_file.read_bytes()
        video_id = audio_file.stem

        # Get title from database or use video_id as fallback
        video_title = video_titles.get(video_id, video_id)

        # Spawn GPU worker using class method
        result = transcriber.transcribe.spawn(audio_bytes, video_id, video_title)
        results.append((audio_file.name, result))

    # Collect results
    print("[*] Collecting results...")
    print()

    completed = 0
    failed = 0
    total_duration = 0

    # Open database connection for updating transcript paths
    db_conn = None
    db_cursor = None
    if db_path.exists():
        db_conn = sqlite3.connect(str(db_path))
        db_cursor = db_conn.cursor()

    for filename, result_future in results:
        try:
            result = result_future.get()

            # Format filename like local transcription: {safe_title}_{video_id}.txt
            video_title = result['video_title']
            video_id = result['video_id']

            # Create safe filename (remove special chars, limit length)
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:80]
            transcript_filename = f"{safe_title}_{video_id}.txt"

            # Save transcript
            transcript_file = output_path / transcript_filename
            transcript_file.write_text(result['transcript'], encoding='utf-8')

            # Update database with transcript path
            if db_cursor:
                db_cursor.execute('''
                    UPDATE videos
                    SET status = 'completed', transcript_path = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE video_id = ?
                ''', (str(transcript_file), video_id))
                db_conn.commit()

            completed += 1
            total_duration += result['duration']
            print(f"[OK] {safe_title[:50]}... ({video_id})")

        except Exception as e:
            failed += 1
            print(f"[FAIL] {filename} - {str(e)}")

    # Close database connection
    if db_conn:
        db_conn.close()

    elapsed = time.time() - start_time

    # Summary
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Completed:        {completed}/{len(audio_files)}")
    print(f"Failed:           {failed}")
    print(f"Total duration:   {total_duration/60:.1f} minutes")
    print(f"Processing time:  {elapsed:.1f} seconds")
    print(f"Realtime factor:  {total_duration/elapsed:.1f}x")
    print(f"Output directory: {output_path}")
    print("="*70)
