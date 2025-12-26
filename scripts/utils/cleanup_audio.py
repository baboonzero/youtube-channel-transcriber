from pathlib import Path
import shutil

audio_dir = Path("data/temp_audio/My First Million")
archive_dir = audio_dir / "already_transcribed"

# Get all audio files
audio_files = []
if audio_dir.exists():
    audio_files = list(audio_dir.glob("*.webm")) + list(audio_dir.glob("*.m4a"))

audio_video_ids = {}
for f in audio_files:
    audio_video_ids[f.stem] = f

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

# Find audio files that are already transcribed
already_transcribed = set(audio_video_ids.keys()) & transcript_video_ids
needs_transcription = set(audio_video_ids.keys()) - transcript_video_ids

print("\n" + "="*70)
print("MOVING ALREADY-TRANSCRIBED AUDIO FILES")
print("="*70)
print(f"\nSource folder:      {audio_dir}")
print(f"Destination folder: {archive_dir}")
print(f"\nTotal audio files:           {len(audio_files)}")
print(f"  - Already transcribed:     {len(already_transcribed)} (will move)")
print(f"  - Need transcription:      {len(needs_transcription)} (will keep)")
print("="*70)

if len(already_transcribed) == 0:
    print("\nNo files to move! All audio files still need transcription.")
    print("="*70)
else:
    # Create archive directory
    archive_dir.mkdir(exist_ok=True)
    print(f"\nCreated archive folder: {archive_dir}")

    # Move files
    moved_count = 0
    failed_count = 0

    print(f"\nMoving {len(already_transcribed)} files...")

    for vid_id in sorted(already_transcribed):
        if vid_id in audio_video_ids:
            source_file = audio_video_ids[vid_id]
            dest_file = archive_dir / source_file.name

            try:
                shutil.move(str(source_file), str(dest_file))
                moved_count += 1
                if moved_count <= 10:
                    print(f"  [OK] Moved: {source_file.name}")
            except Exception as e:
                failed_count += 1
                print(f"  [FAIL] Failed: {source_file.name} - {e}")

    if moved_count > 10:
        print(f"  ... and {moved_count - 10} more")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Files moved:        {moved_count}")
    print(f"Files failed:       {failed_count}")
    print(f"Remaining in main:  {len(needs_transcription)}")
    print("="*70)

    print(f"\nNext step:")
    print(f"Run Modal on the {len(needs_transcription)} remaining files in:")
    print(f"  {audio_dir}")
    print("\nThe moved files are safely archived in:")
    print(f"  {archive_dir}")
    print("="*70)
