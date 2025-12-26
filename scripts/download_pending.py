"""
Simple download script - downloads pending videos only
Run from scripts/ directory
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "config"))

# Change to project root directory so relative paths work
os.chdir(project_root)

from config import *
import sqlite3
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_video(video_info, audio_dir):
    """Download a single video"""
    video_id = video_info['video_id']
    url = video_info['url']

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{audio_dir}/{video_id}.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading: {video_id}")
            ydl.download([url])

        # Update database
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE videos
            SET status = 'downloaded',
                audio_path = ?
            WHERE video_id = ?
        ''', (f"data/temp_audio/My First Million/{video_id}.webm", video_id))
        conn.commit()
        conn.close()

        return True
    except Exception as e:
        logger.error(f"Failed {video_id}: {e}")
        return False

def main():
    # Get pending videos
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT video_id, title, url
        FROM videos
        WHERE status = 'pending'
        ORDER BY video_id
    ''')

    pending = [{'video_id': r[0], 'title': r[1], 'url': r[2]} for r in cursor.fetchall()]
    conn.close()

    print(f"Found {len(pending)} pending videos")

    if not pending:
        print("Nothing to download!")
        return

    # Create audio directory
    audio_dir = Path("data/temp_audio/My First Million")
    audio_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading with {DOWNLOAD_WORKERS} workers...")

    # Download in parallel
    with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as executor:
        futures = [executor.submit(download_video, video, str(audio_dir)) for video in pending]

        completed = sum(1 for f in futures if f.result())

    print(f"\nCompleted: {completed}/{len(pending)}")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    main()
