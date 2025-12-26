#!/usr/bin/env python3
"""
Prepare Channel for Modal Transcription
This is the ONE script you need for hybrid Modal workflow.

What it does:
1. Scrapes the YouTube channel to discover all videos
2. Creates/updates the database with video records
3. Downloads ALL audio files (no transcription)
4. Ready for Modal GPU transcription

Usage:
    python prepare_for_modal.py

After this completes, run:
    modal run scripts/modal_hybrid.py --max-files 100
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
try:
    from config import *
except ImportError:
    print("Error: config.py not found!")
    print("Please create config/config.py from the template")
    sys.exit(1)

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

# Import components
from channel_transcriber import (
    ChannelScraper,
    AudioDownloader,
    ProgressTracker
)
import sqlite3

def main():
    """Prepare channel for Modal transcription - scrape, create DB, download all audio"""

    print("""
================================================================================
         Prepare Channel for Modal Transcription
         Scrape → Database → Download Audio (NO transcription)
================================================================================
    """)

    print("Configuration:")
    print("-" * 70)
    print(f"  Channel URL:         {CHANNEL_URL}")
    print(f"  Database:            {DATABASE_FILE}")
    print(f"  Audio Directory:     {AUDIO_DIR}")
    print(f"  Download Workers:    {DOWNLOAD_WORKERS}")
    print(f"  Batch Size:          {BATCH_SIZE}")
    print("-" * 70)
    print()

    # Validate channel URL
    if CHANNEL_URL == "https://www.youtube.com/@username":
        print("[!] WARNING: You haven't changed the CHANNEL_URL in config.py!")
        print("   Please edit config/config.py and set your YouTube channel URL")
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)

    # Initialize components
    tracker = ProgressTracker(db_path=DATABASE_FILE)
    scraper = ChannelScraper(CHANNEL_URL)

    # Step 1: Scrape channel
    print("\n[STEP 1/3] Scraping channel for videos...")
    print(f"This may take a minute for large channels...")
    print()

    videos = scraper.scrape()

    if not videos:
        print("ERROR: No videos found!")
        print("Check that your CHANNEL_URL is correct in config.py")
        sys.exit(1)

    channel_name = videos[0].channel if videos else "Unknown_Channel"
    print(f"Channel: {channel_name}")
    print(f"Found: {len(videos)} videos")
    print()

    # Step 2: Add videos to database
    print("[STEP 2/3] Creating/updating database...")
    for video in videos:
        tracker.add_video(video)

    # Get statistics FOR THIS CHANNEL ONLY
    stats = tracker.get_stats(channel_filter=channel_name)
    print(f"Total videos: {stats['total']}")
    print(f"Already completed: {stats['completed']}")
    print(f"Pending download: {stats['pending']}")
    print(f"Errors: {stats['errors']}")
    print(f"Total duration: {stats['total_hours']:.1f} hours")
    print()

    if stats['pending'] == 0:
        print("All videos already downloaded!")
        print()
        print("You can now run Modal to transcribe:")
        print(f"  modal run scripts/modal_hybrid.py --max-files {stats['total'] - stats['errors']}")
        print()
        return

    # Step 3: Download all pending videos FOR THIS CHANNEL ONLY
    print(f"[STEP 3/3] Downloading {stats['pending']} pending videos...")
    print("This will take some time depending on video count and sizes.")
    print("You can press Ctrl+C to stop anytime - progress is saved!")
    print()

    # Initialize downloader
    downloader = AudioDownloader(
        output_dir=AUDIO_DIR,
        channel_name=channel_name,
        max_workers=DOWNLOAD_WORKERS
    )

    # Get pending videos FOR THIS CHANNEL ONLY
    pending_videos = tracker.get_pending_videos(channel_filter=channel_name)

    # Download in batches
    total_batches = (len(pending_videos) + BATCH_SIZE - 1) // BATCH_SIZE
    total_downloaded = 0

    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(pending_videos))
        batch = pending_videos[start_idx:end_idx]

        print(f"\nBatch {batch_num + 1}/{total_batches}")
        print(f"Downloading {len(batch)} videos...")

        # Download batch
        downloaded = downloader.download_batch(batch, tracker)
        total_downloaded += len(downloaded)

        print(f"Downloaded {len(downloaded)}/{len(batch)} videos successfully")
        print(f"Total progress: {total_downloaded}/{len(pending_videos)} videos")

    # Final summary
    print()
    print("="*70)
    print("PREPARATION COMPLETE!")
    print("="*70)

    final_stats = tracker.get_stats(channel_filter=channel_name)
    audio_dir_path = Path(AUDIO_DIR) / channel_name
    audio_files = []
    if audio_dir_path.exists():
        audio_files = list(audio_dir_path.glob("*.webm")) + list(audio_dir_path.glob("*.m4a"))

    print(f"Channel: {channel_name}")
    print(f"Audio files ready: {len(audio_files)}")
    print(f"Location: {audio_dir_path}")
    print()
    print("Next step - Transcribe on Modal:")
    print(f"  modal run scripts/modal_hybrid.py --max-files {len(audio_files)}")
    print()
    print("Or test with a few files first:")
    print("  modal run scripts/modal_hybrid.py --max-files 10")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("Progress has been saved to database")
        print("Run this script again to resume downloading")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        raise
