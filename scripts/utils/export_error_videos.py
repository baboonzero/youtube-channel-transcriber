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

print("\n215 FAILED DOWNLOADS - Complete List")
print("=" * 100)
print(f"{'Video ID':<20} {'Title':<60} {'URL'}")
print("-" * 100)

error_videos = cursor.fetchall()
for row in error_videos:
    video_id = row[0]
    title = (row[1][:57] + "...") if row[1] and len(row[1]) > 60 else (row[1] or "Unknown")
    url = row[2] or ""
    print(f"{video_id:<20} {title:<60} {url}")

print("\n" + "=" * 100)
print(f"Total error videos: {len(error_videos)}")

conn.close()
