import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "config"))

from config import CHANNEL_URL
import yt_dlp

print("\n" + "="*70)
print("FINDING VIDEOS NOT DOWNLOADED")
print("="*70)

# 1. Get all videos from YouTube channel
print("\nFetching all videos from YouTube channel...")
channel_url = CHANNEL_URL.rstrip('/') + '/videos'

ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': 'in_playlist',
    'playlistend': 10000,
}

youtube_video_ids = []
youtube_video_titles = {}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        entries = info.get('entries', [])

        for entry in entries:
            if entry and entry.get('id') and entry.get('_type') == 'url':
                vid_id = entry.get('id')
                youtube_video_ids.append(vid_id)
                youtube_video_titles[vid_id] = entry.get('title', 'Unknown')

        print(f"YouTube channel has: {len(youtube_video_ids)} videos")
except Exception as e:
    print(f"Error fetching channel: {e}")
    sys.exit(1)

# 2. Get all videos we have (audio + transcripts)
audio_dir = Path("data/temp_audio/My First Million")
local_dir = Path("data/transcripts/My First Million")
modal_dir = Path("modal_transcripts")

our_videos = set()

# Add audio files
if audio_dir.exists():
    our_videos.update(f.stem for f in audio_dir.glob("*.webm"))
    our_videos.update(f.stem for f in audio_dir.glob("*.m4a"))

# Add transcripts
if local_dir.exists():
    our_videos.update(f.stem for f in local_dir.glob("*.txt"))
if modal_dir.exists():
    our_videos.update(f.stem for f in modal_dir.glob("*.txt"))

print(f"We have (audio + transcripts): {len(our_videos)} videos")

# 3. Find the difference
youtube_set = set(youtube_video_ids)
missing_videos = youtube_set - our_videos

print(f"\n" + "="*70)
print(f"MISSING VIDEOS: {len(missing_videos)}")
print("="*70)

if len(missing_videos) > 0:
    print(f"\nList of {len(missing_videos)} missing videos:")
    print(f"{'Video ID':<20} {'Title':<60}")
    print("-" * 80)

    for video_id in sorted(missing_videos):
        title = youtube_video_titles.get(video_id, 'Unknown')
        title_display = title[:57] + "..." if len(title) > 60 else title
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"{video_id:<20} {title_display:<60}")

else:
    print("\nNo missing videos! All YouTube videos have been downloaded.")

print("\n" + "="*70)
print(f"Summary: {len(our_videos)} downloaded, {len(missing_videos)} missing, {len(youtube_video_ids)} total")
print("="*70)
