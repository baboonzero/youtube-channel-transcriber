#!/usr/bin/env python3
"""
YouTube Channel Bulk Transcriber with GPU Acceleration
Scrapes all videos from a channel and transcribes them using local Whisper with GPU
"""

import os
import sys
import json
import sqlite3
from faster_whisper import WhisperModel
import yt_dlp
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional
import logging
import time
import threading

# Set ffmpeg path BEFORE importing whisper's audio functions
try:
    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
except Exception as e:
    print(f"Warning: Could not set FFmpeg path: {e}")

# Configure logging (will be set up in run_transcriber.py with proper paths)
logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Data class for video information"""
    video_id: str
    url: str
    title: str
    duration: int
    channel: str


class ProgressTracker:
    """SQLite-based progress tracker for resumability"""

    def __init__(self, db_path: str = "transcription_progress.db"):
        self.db_path = db_path

        # Create parent directory if it doesn't exist
        db_dir = Path(db_path).parent
        if db_dir and str(db_dir) != '.':
            db_dir.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._lock = threading.Lock()  # Add thread lock for database operations
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT,
                duration INTEGER,
                channel TEXT,
                status TEXT DEFAULT 'pending',
                audio_path TEXT,
                transcript_path TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_video(self, video: VideoInfo):
        """Add a video to the database"""
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO videos (video_id, url, title, duration, channel, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            ''', (video.video_id, video.url, video.title, video.duration, video.channel))
            self.conn.commit()

    def update_status(self, video_id: str, status: str, **kwargs):
        """Update video status and optional fields"""
        with self._lock:
            cursor = self.conn.cursor()

            # Build dynamic update query
            fields = ['status = ?', 'updated_at = CURRENT_TIMESTAMP']
            values = [status]

            for key, value in kwargs.items():
                fields.append(f'{key} = ?')
                values.append(value)

            values.append(video_id)
            query = f"UPDATE videos SET {', '.join(fields)} WHERE video_id = ?"

            cursor.execute(query, values)
            self.conn.commit()

    def get_pending_videos(self, channel_filter: str = None) -> List[dict]:
        """Get all videos that haven't been processed yet

        Args:
            channel_filter: Optional channel name to filter by. If None, returns all channels.
        """
        cursor = self.conn.cursor()

        if channel_filter:
            cursor.execute('''
                SELECT video_id, url, title, duration, channel
                FROM videos
                WHERE (status = 'pending' OR status = 'downloading' OR status = 'downloaded')
                  AND channel = ?
                ORDER BY duration ASC
            ''', (channel_filter,))
        else:
            cursor.execute('''
                SELECT video_id, url, title, duration, channel
                FROM videos
                WHERE status = 'pending' OR status = 'downloading' OR status = 'downloaded'
                ORDER BY duration ASC
            ''')

        columns = ['video_id', 'url', 'title', 'duration', 'channel']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_stats(self, channel_filter: str = None) -> dict:
        """Get current processing statistics

        Args:
            channel_filter: Optional channel name to filter by. If None, returns stats for all channels.
        """
        cursor = self.conn.cursor()

        if channel_filter:
            cursor.execute('''
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(duration) as total_duration,
                    SUM(CASE WHEN status = 'completed' THEN duration ELSE 0 END) as completed_duration
                FROM videos
                WHERE channel = ?
            ''', (channel_filter,))
        else:
            cursor.execute('''
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(duration) as total_duration,
                    SUM(CASE WHEN status = 'completed' THEN duration ELSE 0 END) as completed_duration
                FROM videos
            ''')

        row = cursor.fetchone()
        return {
            'total': row[0] or 0,
            'completed': row[1] or 0,
            'errors': row[2] or 0,
            'pending': row[3] or 0,
            'total_hours': (row[4] or 0) / 3600,
            'completed_hours': (row[5] or 0) / 3600
        }

    def close(self):
        """Close database connection"""
        self.conn.close()


class ChannelScraper:
    """Scrapes all video URLs and metadata from a YouTube channel"""

    def __init__(self, channel_url: str):
        self.channel_url = channel_url

    def scrape(self) -> List[VideoInfo]:
        """
        Scrape all videos from the channel
        Returns list of VideoInfo objects
        """
        # Ensure we're scraping the /videos tab to get all uploads
        channel_url = self.channel_url
        if not channel_url.endswith('/videos'):
            channel_url = channel_url.rstrip('/') + '/videos'

        logger.info(f"Scraping channel: {channel_url}")

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download, just get metadata
            'force_generic_extractor': False,
            'playlistend': None,  # Get all videos, not just first few
            'ignoreerrors': True,  # Continue on errors
        }

        videos = []

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("Fetching channel information...")
                result = ydl.extract_info(channel_url, download=False)

                if 'entries' not in result:
                    logger.error("No videos found in channel")
                    return videos

                channel_name = result.get('channel', result.get('uploader', 'Unknown'))
                logger.info(f"Channel: {channel_name}")
                logger.info(f"Found {len(result['entries'])} videos")

                for entry in result['entries']:
                    if entry is None:
                        continue

                    video_id = entry.get('id')
                    if not video_id:
                        continue

                    # Skip if this is a channel/playlist entry (not a video)
                    # Video IDs are exactly 11 characters, channel IDs start with UC and are longer
                    if len(video_id) != 11 or video_id.startswith('UC'):
                        logger.debug(f"Skipping non-video entry: {video_id}")
                        continue

                    video = VideoInfo(
                        video_id=video_id,
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        title=entry.get('title', 'Unknown'),
                        duration=entry.get('duration', 0),
                        channel=channel_name
                    )
                    videos.append(video)

                logger.info(f"Successfully scraped {len(videos)} videos")

        except Exception as e:
            logger.error(f"Error scraping channel: {e}")
            raise

        return videos


class AudioDownloader:
    """Handles parallel audio downloads from YouTube"""

    def __init__(self, output_dir: str = "temp_audio", channel_name: str = None, max_workers: int = 10):
        self.base_dir = Path(output_dir)

        # Create channel-specific subdirectory
        if channel_name:
            # Sanitize channel name for folder
            safe_channel = "".join(c for c in channel_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_channel = safe_channel[:100]  # Limit length
            self.output_dir = self.base_dir / safe_channel
        else:
            self.output_dir = self.base_dir

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers

        logger.info(f"Audio download directory: {self.output_dir}")

    def download_single(self, video: dict, tracker: ProgressTracker) -> Optional[str]:
        """
        Download audio for a single video
        Returns path to downloaded audio file or None on error
        """
        video_id = video['video_id']
        url = video['url']

        try:
            tracker.update_status(video_id, 'downloading')
            logger.info(f"Downloading: {video['title'][:50]}...")

            output_template = str(self.output_dir / f"{video_id}.%(ext)s")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                ext = info.get('ext', 'webm')
                audio_path = str(self.output_dir / f"{video_id}.{ext}")

                if os.path.exists(audio_path):
                    tracker.update_status(video_id, 'downloaded', audio_path=audio_path)
                    logger.info(f"Downloaded: {video_id}")
                    return audio_path
                else:
                    logger.error(f"Audio file not found after download: {video_id}")
                    tracker.update_status(video_id, 'error', error_message="Audio file not found after download")
                    return None

        except Exception as e:
            logger.error(f"Error downloading {video_id}: {e}")
            tracker.update_status(video_id, 'error', error_message=str(e))
            return None

    def download_batch(self, videos: List[dict], tracker: ProgressTracker) -> List[str]:
        """
        Download multiple videos in parallel
        Returns list of successfully downloaded audio paths
        """
        logger.info(f"Starting parallel download of {len(videos)} videos with {self.max_workers} workers")

        audio_paths = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.download_single, video, tracker): video
                for video in videos
            }

            for future in as_completed(futures):
                audio_path = future.result()
                if audio_path:
                    audio_paths.append(audio_path)

        logger.info(f"Downloaded {len(audio_paths)}/{len(videos)} videos successfully")
        return audio_paths


class GPUTranscriber:
    """GPU-accelerated Whisper transcription"""

    def __init__(self, model_size: str = "base", output_dir: str = "transcripts", channel_name: str = None, device: str = "cuda"):
        self.model_size = model_size
        self.base_dir = Path(output_dir)

        # Create channel-specific subdirectory
        if channel_name:
            # Sanitize channel name for folder
            safe_channel = "".join(c for c in channel_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_channel = safe_channel[:100]  # Limit length
            self.output_dir = self.base_dir / safe_channel
        else:
            self.output_dir = self.base_dir

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.model = None

        logger.info(f"Initializing GPU Transcriber with model: {model_size}")
        logger.info(f"Transcript directory: {self.output_dir}")
        self._load_model()

    def _load_model(self):
        """Load Whisper model using faster-whisper"""
        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
                logger.info(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

                # Try GPU first, fall back to CPU if CUDA 12 libraries missing
                try:
                    self.model = WhisperModel(
                        self.model_size,
                        device="cuda",
                        compute_type="float16",
                        num_workers=4
                    )
                    self.device = "cuda"
                    logger.info(f"Model loaded on GPU successfully (faster-whisper)")
                except Exception as cuda_error:
                    if "cublas" in str(cuda_error).lower() or "cuda" in str(cuda_error).lower():
                        logger.warning(f"GPU initialization failed (likely CUDA 12 libs missing): {cuda_error}")
                        logger.info("Falling back to optimized CPU mode (still 2-3x faster than original)")
                        self.device = "cpu"
                        self.model = WhisperModel(
                            self.model_size,
                            device="cpu",
                            compute_type="int8",
                            num_workers=4
                        )
                        logger.info(f"Model loaded on CPU with int8 optimization")
                    else:
                        raise
            else:
                logger.warning("CUDA not available, using CPU mode")
                self.device = "cpu"
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8",
                    num_workers=4
                )
                logger.info(f"Model loaded on CPU with int8 optimization")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.warning("Falling back to basic CPU mode")
            self.device = "cpu"
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")

    def transcribe_single(self, video_id: str, audio_path: str, tracker: ProgressTracker) -> Optional[str]:
        """
        Transcribe a single audio file
        Returns path to transcript file or None on error
        """
        try:
            tracker.update_status(video_id, 'transcribing')
            logger.info(f"Transcribing: {video_id}")

            # Get video info for title
            cursor = tracker.conn.cursor()
            cursor.execute('SELECT title FROM videos WHERE video_id = ?', (video_id,))
            result = cursor.fetchone()
            title = result[0] if result else video_id

            start_time = time.time()

            # Transcribe with GPU using faster-whisper
            segments, info = self.model.transcribe(
                audio_path,
                language="en",  # Change to None for auto-detect
                task="transcribe",
                vad_filter=True,  # Voice Activity Detection - skip silence
                word_timestamps=True,
                temperature=0.0,
            )

            # Convert generator to list and build result dict
            segments_list = list(segments)
            result = {
                'text': ' '.join([seg.text for seg in segments_list]),
                'segments': segments_list,
                'language': info.language,
                'duration': info.duration
            }

            elapsed = time.time() - start_time

            # Format transcript
            transcript = self._format_transcript(result, title, video_id)

            # Save transcript
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:80]
            transcript_filename = f"{safe_title}_{video_id}.txt"
            transcript_path = self.output_dir / transcript_filename

            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcript)

            logger.info(f"Transcribed {video_id} in {elapsed:.1f}s → {transcript_path.name}")

            # Update database
            tracker.update_status(video_id, 'completed', transcript_path=str(transcript_path))

            # Cleanup audio file to save space
            try:
                os.remove(audio_path)
                logger.info(f"Cleaned up audio: {audio_path}")
            except Exception as e:
                logger.warning(f"Could not remove audio file: {e}")

            return str(transcript_path)

        except Exception as e:
            logger.error(f"Error transcribing {video_id}: {e}")
            tracker.update_status(video_id, 'error', error_message=str(e))
            return None

    def _format_transcript(self, result: dict, title: str, video_id: str) -> str:
        """Format transcription result into readable text"""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(f"TRANSCRIPT: {title}")
        lines.append(f"Video ID: {video_id}")
        lines.append("=" * 80)
        lines.append(f"Transcription Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Model: Whisper {self.model_size} (GPU: {self.device})")
        lines.append(f"Language: {result.get('language', 'unknown')}")
        lines.append("=" * 80)
        lines.append("\n")

        # Full transcript
        lines.append("FULL TRANSCRIPT")
        lines.append("-" * 80)
        lines.append(result['text'].strip())
        lines.append("\n" * 3)

        # Timestamped transcript
        lines.append("DETAILED TRANSCRIPT WITH TIMESTAMPS")
        lines.append("-" * 80)
        lines.append("\n")

        for segment in result['segments']:
            # Handle both dict (old) and Segment object (faster-whisper) formats
            if hasattr(segment, 'start'):
                timestamp = self._format_timestamp(segment.start)
                text = segment.text.strip()
            else:
                timestamp = self._format_timestamp(segment['start'])
                text = segment['text'].strip()
            lines.append(f"[{timestamp}] {text}")

        lines.append("\n" * 2)
        lines.append("=" * 80)
        lines.append("END OF TRANSCRIPT")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


class ChannelTranscriptionOrchestrator:
    """Main orchestrator for the entire transcription pipeline"""

    def __init__(
        self,
        channel_url: str,
        model_size: str = "base",
        download_workers: int = 10,
        transcribe_workers: int = 1,  # GPU: usually 1-2 depending on VRAM
        audio_base_dir: str = "data/temp_audio",
        transcript_base_dir: str = "data/transcripts",
        db_path: str = "data/transcription_progress.db",
    ):
        self.channel_url = channel_url
        self.model_size = model_size
        self.download_workers = download_workers
        self.transcribe_workers = transcribe_workers
        self.channel_name = None

        # Initialize components
        self.tracker = ProgressTracker(db_path=db_path)
        self.scraper = ChannelScraper(channel_url)

        # Scraper will set channel_name, but we need to get it first for folder creation
        # We'll initialize downloader and transcriber after getting channel name
        self.audio_base_dir = audio_base_dir
        self.transcript_base_dir = transcript_base_dir
        self.downloader = None
        self.transcriber = None

    def run(self):
        """Execute the complete transcription pipeline"""
        logger.info("=" * 80)
        logger.info("YouTube Channel Bulk Transcriber - GPU Accelerated")
        logger.info("=" * 80)

        # Step 1: Scrape channel
        logger.info("\n[STEP 1/3] Scraping channel for videos...")
        videos = self.scraper.scrape()

        if not videos:
            logger.error("No videos found. Exiting.")
            return

        # Get channel name from first video
        self.channel_name = videos[0].channel if videos else "Unknown_Channel"
        logger.info(f"Channel: {self.channel_name}")

        # Now initialize downloader and transcriber with channel name
        self.downloader = AudioDownloader(
            output_dir=self.audio_base_dir,
            channel_name=self.channel_name,
            max_workers=self.download_workers
        )
        self.transcriber = GPUTranscriber(
            model_size=self.model_size,
            output_dir=self.transcript_base_dir,
            channel_name=self.channel_name
        )

        # Add videos to database
        for video in videos:
            self.tracker.add_video(video)

        # Step 2: Check what needs to be processed
        logger.info("\n[STEP 2/3] Checking processing status...")
        stats = self.tracker.get_stats()
        logger.info(f"Total videos: {stats['total']}")
        logger.info(f"Completed: {stats['completed']}")
        logger.info(f"Pending: {stats['pending']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info(f"Total duration: {stats['total_hours']:.1f} hours")
        logger.info(f"Completed duration: {stats['completed_hours']:.1f} hours")

        if stats['pending'] == 0:
            logger.info("All videos already processed!")
            return

        # Get pending videos
        pending_videos = self.tracker.get_pending_videos()
        logger.info(f"\n{len(pending_videos)} videos to process")

        # Step 3: Download audio files
        logger.info("\n[STEP 3/3] Downloading and transcribing...")

        # Process in batches to manage disk space
        batch_size = 20  # Download 20 at a time, then transcribe

        for i in range(0, len(pending_videos), batch_size):
            batch = pending_videos[i:i+batch_size]
            logger.info(f"\nProcessing batch {i//batch_size + 1}/{(len(pending_videos)-1)//batch_size + 1}")

            # Download batch
            logger.info("Downloading batch...")
            self.downloader.download_batch(batch, self.tracker)

            # Get downloaded videos for this batch
            downloaded = []
            for v in batch:
                cursor = self.tracker.conn.cursor()
                cursor.execute('SELECT status FROM videos WHERE video_id = ?', (v['video_id'],))
                result = cursor.fetchone()
                if result and result[0] == 'downloaded':
                    downloaded.append(v)

            # Transcribe batch
            logger.info("Transcribing batch...")
            for video in downloaded:
                cursor = self.tracker.conn.cursor()
                cursor.execute('SELECT audio_path FROM videos WHERE video_id = ?', (video['video_id'],))
                result = cursor.fetchone()
                if result and result[0]:
                    self.transcriber.transcribe_single(video['video_id'], result[0], self.tracker)

        # Final statistics
        logger.info("\n" + "=" * 80)
        logger.info("TRANSCRIPTION COMPLETE!")
        logger.info("=" * 80)

        final_stats = self.tracker.get_stats()

        # Calculate word counts and file statistics
        total_words = 0
        total_file_size = 0
        transcript_count = 0

        cursor = self.tracker.conn.cursor()
        cursor.execute('SELECT transcript_path FROM videos WHERE status = "completed" AND transcript_path IS NOT NULL')
        transcript_paths = cursor.fetchall()

        for (transcript_path,) in transcript_paths:
            if transcript_path and os.path.exists(transcript_path):
                try:
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        words = len(content.split())
                        total_words += words
                        total_file_size += os.path.getsize(transcript_path)
                        transcript_count += 1
                except Exception as e:
                    logger.debug(f"Could not read {transcript_path}: {e}")

        # Display comprehensive statistics
        logger.info("\n[SUMMARY] TRANSCRIPTION STATISTICS")
        logger.info("-" * 80)
        logger.info(f"Total Videos:          {final_stats['total']:,}")
        logger.info(f"Successfully Processed: {final_stats['completed']:,} ({final_stats['completed']/final_stats['total']*100:.1f}%)")
        logger.info(f"Failed/Errors:         {final_stats['errors']:,}")
        logger.info(f"Pending:               {final_stats['pending']:,}")
        logger.info("")
        logger.info(f"Total Audio Duration:  {final_stats['completed_hours']:.1f} hours")
        logger.info(f"Total Words:           {total_words:,} words")
        if transcript_count > 0:
            logger.info(f"Average Words/Video:   {total_words//transcript_count:,} words")
        logger.info(f"Total Transcript Size: {total_file_size/1024/1024:.1f} MB")
        logger.info("")
        logger.info(f"Transcripts Location:  {self.transcriber.output_dir.absolute()}")
        logger.info("=" * 80)

        self.tracker.close()


def main():
    """Main entry point"""

    # Configuration
    CHANNEL_URL = "https://www.youtube.com/@channel_name"  # CHANGE THIS
    MODEL_SIZE = "base"  # Options: tiny, base, small, medium, large
    DOWNLOAD_WORKERS = 10  # Parallel downloads
    TRANSCRIBE_WORKERS = 1  # GPU workers (1-2 depending on VRAM)

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║          YouTube Channel Bulk Transcriber - GPU Accelerated                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    print(f"Channel URL: {CHANNEL_URL}")
    print(f"Whisper Model: {MODEL_SIZE}")
    print(f"Download Workers: {DOWNLOAD_WORKERS}")
    print(f"GPU Workers: {TRANSCRIBE_WORKERS}")
    print()

    # Create and run orchestrator
    orchestrator = ChannelTranscriptionOrchestrator(
        channel_url=CHANNEL_URL,
        model_size=MODEL_SIZE,
        download_workers=DOWNLOAD_WORKERS,
        transcribe_workers=TRANSCRIBE_WORKERS
    )

    try:
        orchestrator.run()
    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user. Progress saved. Run again to resume.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
