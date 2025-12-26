from pathlib import Path

# Count what we actually have
audio_dir = Path("data/temp_audio/My First Million")
local_dir = Path("data/transcripts/My First Million")
modal_dir = Path("modal_transcripts")

# Get all unique video IDs we have
all_videos = set()

# Audio files
if audio_dir.exists():
    all_videos.update(f.stem for f in audio_dir.glob("*.webm"))
    all_videos.update(f.stem for f in audio_dir.glob("*.m4a"))

# Transcripts
if local_dir.exists():
    all_videos.update(f.stem for f in local_dir.glob("*.txt"))
if modal_dir.exists():
    all_videos.update(f.stem for f in modal_dir.glob("*.txt"))

print("\n" + "="*70)
print("CURRENT PROJECT STATUS")
print("="*70)
print(f"\nTotal unique videos (audio + transcripts): {len(all_videos)}")
print(f"YouTube channel total:                      1,054")
print(f"Still missing:                              {1054 - len(all_videos)}")
print("="*70)

# Breakdown
audio_files = set()
if audio_dir.exists():
    audio_files.update(f.stem for f in audio_dir.glob("*.webm"))
    audio_files.update(f.stem for f in audio_dir.glob("*.m4a"))

local_transcripts = set()
if local_dir.exists():
    local_transcripts = set(f.stem for f in local_dir.glob("*.txt"))

modal_transcripts = set()
if modal_dir.exists():
    modal_transcripts = set(f.stem for f in modal_dir.glob("*.txt"))

all_transcripts = local_transcripts | modal_transcripts

print(f"\nDETAILED BREAKDOWN:")
print(f"  Audio files downloaded:        {len(audio_files)}")
print(f"  Local transcripts:             {len(local_transcripts)}")
print(f"  Modal transcripts:             {len(modal_transcripts)}")
print(f"  Total unique transcripts:      {len(all_transcripts)}")
print(f"  Audio without transcript:      {len(audio_files - all_transcripts)}")
print("="*70)
