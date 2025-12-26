import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "config"))

from config import *
import sqlite3

conn = sqlite3.connect('data/transcription_progress.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT video_id, title, url
    FROM videos
    WHERE status = 'error'
    ORDER BY video_id
''')

error_videos = cursor.fetchall()
conn.close()

print("\n" + "="*70)
print(f"VIDEOS THAT FAILED TO DOWNLOAD (status='error'): {len(error_videos)}")
print("="*70)

if len(error_videos) > 0:
    print(f"\nFirst 20 error videos:")
    for i, row in enumerate(error_videos[:20]):
        video_id = row[0]
        title = (row[1][:50] + "...") if row[1] and len(row[1]) > 50 else (row[1] or "Unknown")
        print(f"  {i+1:3d}. {video_id:<20} {title}")

    print(f"\n... and {len(error_videos) - 20} more")

print("\n" + "="*70)
print(f"Total error videos in database: {len(error_videos)}")
print("="*70)
