"""
Download-only script
Downloads remaining videos without transcribing
Perfect for feeding Modal transcriber
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "config"))

# Change to project root directory so relative paths work
os.chdir(project_root)

# Import configuration
from config import *

# Setup logging
import logging
log_dir = Path(LOG_FILE).parent
if log_dir and str(log_dir) != '.':
    log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Configure stdout for UTF-8
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr:
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Import downloader components
from channel_transcriber import ChannelTranscriptionOrchestrator
import sqlite3

def main():
    """Download pending videos only - no transcription"""

    print("""
================================================================================
         YouTube Video Downloader - Download Only Mode
================================================================================
    """)

    print("Configuration:")
    print("-" * 70)
    print(f"  Database:            {DATABASE_FILE}")
    print(f"  Audio Directory:     {AUDIO_DIR}")
    print(f"  Download Workers:    {DOWNLOAD_WORKERS}")
    print(f"  Batch Size:          {BATCH_SIZE}")
    print("-" * 70)
    print()

    # Check database exists
    db_path = Path(DATABASE_FILE)
    if not db_path.exists():
        print(f"Error: Database not found at {DATABASE_FILE}")
        print("Please run the main transcriber first to create the database.")
        sys.exit(1)

    # Get pending videos
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT video_id, title, url, channel
        FROM videos
        WHERE status = 'pending'
        ORDER BY video_id
    ''')

    pending_videos = []
    channel_name = None
    for row in cursor.fetchall():
        pending_videos.append({
            'video_id': row[0],
            'title': row[1],
            'url': row[2],
        })
        if channel_name is None and row[3]:
            channel_name = row[3]

    conn.close()

    print(f"Found {len(pending_videos)} pending videos to download")

    if len(pending_videos) == 0:
        print("No pending videos to download!")
        return

    # Get channel name from database if not found in pending videos
    if channel_name is None:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT channel FROM videos WHERE channel IS NOT NULL LIMIT 1')
        result = cursor.fetchone()
        channel_name = result[0] if result else "Unknown_Channel"
        conn.close()

    print(f"Channel: {channel_name}")
    print()
    print(f"Starting download of {len(pending_videos)} videos...")
    print("Progress will be saved. Press Ctrl+C to stop anytime.")
    print()

    # Create orchestrator (we'll use its download functionality)
    orchestrator = ChannelTranscriptionOrchestrator(
        channel_url=CHANNEL_URL,
        model_size=MODEL_SIZE,
        download_workers=DOWNLOAD_WORKERS,
        transcribe_workers=1,
        audio_base_dir=AUDIO_DIR,
        transcript_base_dir=TRANSCRIPT_DIR,
        db_path=DATABASE_FILE
    )

    # Manually initialize downloader with channel name
    from channel_transcriber import AudioDownloader
    orchestrator.downloader = AudioDownloader(
        output_dir=AUDIO_DIR,
        channel_name=channel_name,
        max_workers=DOWNLOAD_WORKERS
    )

    # Process in batches
    total_batches = (len(pending_videos) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(pending_videos))
        batch = pending_videos[start_idx:end_idx]

        print(f"\nBatch {batch_num + 1}/{total_batches}")
        print(f"Downloading {len(batch)} videos...")

        # Download batch
        downloaded = orchestrator.downloader.download_batch(batch, orchestrator.tracker)

        print(f"Downloaded {len(downloaded)}/{len(batch)} videos successfully")

    print()
    print("="*70)
    print("DOWNLOAD COMPLETE")
    print("="*70)
    print(f"Total videos downloaded: Check {AUDIO_DIR}")
    print()
    print("Next step: Run Modal to transcribe:")
    print("  modal run --detach modal_hybrid.py --max-files 300")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("Progress has been saved to database")
    except Exception as e:
        print(f"\n\nError: {e}")
        raise
