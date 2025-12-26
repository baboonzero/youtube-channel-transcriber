from pathlib import Path

# Get audio files
audio_dir = Path("data/temp_audio/My First Million")
audio_files = set()
if audio_dir.exists():
    audio_files.update(f.stem for f in audio_dir.glob("*.webm"))
    audio_files.update(f.stem for f in audio_dir.glob("*.m4a"))

# Get transcripts
local_dir = Path("data/transcripts/My First Million")
modal_dir = Path("modal_transcripts")

transcripts = set()
if local_dir.exists():
    transcripts.update(f.stem for f in local_dir.glob("*.txt"))
if modal_dir.exists():
    transcripts.update(f.stem for f in modal_dir.glob("*.txt"))

# Find audio without transcripts
needs_transcription = audio_files - transcripts

print(f"\nAudio files needing transcription: {len(needs_transcription)}")
print(f"\nFirst 10:")
for i, video_id in enumerate(sorted(list(needs_transcription))[:10]):
    print(f"  {i+1}. {video_id}")

print(f"\n... and {len(needs_transcription) - 10} more")
print(f"\nTotal to process: {len(needs_transcription)}")
