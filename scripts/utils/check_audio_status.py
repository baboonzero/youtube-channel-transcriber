from pathlib import Path

audio_dir = Path("data/temp_audio/My First Million")

# Get all audio files
audio_files = []
if audio_dir.exists():
    audio_files = list(audio_dir.glob("*.webm")) + list(audio_dir.glob("*.m4a"))

audio_video_ids = set()
for f in audio_files:
    # Audio files are named as VideoID.webm or VideoID.m4a
    audio_video_ids.add(f.stem)

# Get all transcripts (local + modal)
local_dir = Path("data/transcripts/My First Million")
modal_dir = Path("modal_transcripts")

transcript_video_ids = set()

# Local transcripts: extract last 11 characters (YouTube video ID)
if local_dir.exists():
    for f in local_dir.glob("*.txt"):
        video_id = f.stem[-11:]  # Last 11 characters
        transcript_video_ids.add(video_id)

# Modal transcripts: already in VideoID.txt format
if modal_dir.exists():
    for f in modal_dir.glob("*.txt"):
        transcript_video_ids.add(f.stem)

# Find audio files that need transcription
needs_transcription = audio_video_ids - transcript_video_ids
already_transcribed = audio_video_ids & transcript_video_ids

print("\n" + "="*70)
print("AUDIO FILES STATUS")
print("="*70)
print(f"\nAudio folder: {audio_dir}")
print(f"\nTotal audio files:                {len(audio_files)}")
print(f"  - Already transcribed:          {len(already_transcribed)}")
print(f"  - Still need transcription:     {len(needs_transcription)}")
print("="*70)

if len(already_transcribed) > 0:
    print(f"\nWARNING: {len(already_transcribed)} audio files already have transcripts!")
    print(f"These are REDUNDANT and will waste Modal resources if processed again.")
    print(f"\nFirst 10 already transcribed (can be deleted from audio folder):")
    for i, vid_id in enumerate(sorted(list(already_transcribed))[:10]):
        # Find the actual filename
        matching_files = [f.name for f in audio_files if f.stem == vid_id]
        if matching_files:
            print(f"  {i+1:3d}. {matching_files[0]}")

if len(needs_transcription) > 0:
    print(f"\n" + "="*70)
    print(f"AUDIO FILES THAT NEED TRANSCRIPTION: {len(needs_transcription)}")
    print("="*70)
    print(f"\nFirst 20 files to process:")
    for i, vid_id in enumerate(sorted(list(needs_transcription))[:20]):
        matching_files = [f.name for f in audio_files if f.stem == vid_id]
        if matching_files:
            print(f"  {i+1:3d}. {matching_files[0]}")

    if len(needs_transcription) > 20:
        print(f"\n... and {len(needs_transcription) - 20} more")

print("\n" + "="*70)
print("RECOMMENDATION:")
print("="*70)
if len(already_transcribed) > 0:
    print(f"DELETE the {len(already_transcribed)} already-transcribed audio files BEFORE running Modal")
    print(f"This will prevent re-transcribing and wasting resources.")
print(f"\nThen run Modal on the remaining {len(needs_transcription)} files.")
print("="*70)
