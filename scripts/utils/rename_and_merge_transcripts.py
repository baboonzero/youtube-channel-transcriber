from pathlib import Path
import sqlite3
import shutil
import re

print("\n" + "="*70)
print("RENAME & MERGE MODAL TRANSCRIPTS")
print("="*70)

# Connect to database to get video titles
db_path = Path("data/transcription_progress.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all video titles
cursor.execute("SELECT video_id, title FROM videos")
video_titles = {row[0]: row[1] for row in cursor.fetchall()}
conn.close()

print(f"\nLoaded {len(video_titles)} video titles from database")

# Modal transcripts folder
modal_dir = Path("data/modal_transcripts")
local_dir = Path("data/transcripts/My First Million")

# Get all modal transcript files
modal_files = list(modal_dir.glob("*.txt"))
print(f"Found {len(modal_files)} modal transcript files")

# Function to create safe filename
def create_safe_filename(title, video_id):
    """Create safe filename from title and video_id"""
    # Remove invalid characters for Windows filenames
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
    # Replace multiple spaces with single space
    safe_title = re.sub(r'\s+', ' ', safe_title)
    # Limit length
    safe_title = safe_title[:150].strip()
    # Create filename
    return f"{safe_title}_{video_id}.txt"

print(f"\n" + "="*70)
print("RENAMING & MOVING FILES")
print("="*70)

renamed_count = 0
moved_count = 0
failed_count = 0
no_title_count = 0

for modal_file in sorted(modal_files):
    video_id = modal_file.stem

    # Get title from database
    title = video_titles.get(video_id)

    if not title:
        no_title_count += 1
        print(f"[WARN] No title found for: {video_id}")
        # Use video_id as title if not found
        title = video_id

    # Create new filename with title
    new_filename = create_safe_filename(title, video_id)
    new_path = local_dir / new_filename

    # Check if file already exists in destination
    if new_path.exists():
        print(f"[SKIP] Already exists: {new_filename}")
        continue

    try:
        # Copy file to new location with new name
        shutil.copy2(modal_file, new_path)
        moved_count += 1
        renamed_count += 1

        if moved_count <= 10:
            print(f"[OK] {video_id} -> {new_filename[:60]}...")

    except Exception as e:
        failed_count += 1
        print(f"[FAIL] {video_id}: {e}")

if moved_count > 10:
    print(f"... and {moved_count - 10} more files renamed and moved")

print(f"\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Files renamed & moved:  {moved_count}")
print(f"Files failed:           {failed_count}")
print(f"No title found:         {no_title_count}")
print(f"Total processed:        {len(modal_files)}")

# Verify final state
print(f"\n" + "="*70)
print("VERIFICATION")
print("="*70)

local_files = list(local_dir.glob("*.txt"))
print(f"Total files in merged folder: {len(local_files)}")

# Count unique video IDs (extract last 11 characters from filename)
unique_ids = set()
for f in local_files:
    video_id = f.stem[-11:]  # YouTube video IDs are 11 characters
    unique_ids.add(video_id)

print(f"Unique video IDs:             {len(unique_ids)}")

if len(local_files) == len(unique_ids):
    print(f"Status: PERFECT - All transcripts are unique!")
else:
    duplicates = len(local_files) - len(unique_ids)
    print(f"Status: WARNING - {duplicates} duplicate video IDs found!")

print(f"\n" + "="*70)
print("NEXT STEPS")
print("="*70)
print(f"1. Verify merged folder: {local_dir}")
print(f"2. Original data/modal_transcripts/ folder can be deleted (files copied, not moved)")
print(f"3. All {len(unique_ids)} transcripts now in single location!")
print("="*70)
