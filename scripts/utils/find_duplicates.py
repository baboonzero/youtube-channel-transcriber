from pathlib import Path
from collections import Counter

local_dir = Path("data/transcripts/My First Million")
local_files = list(local_dir.glob("*.txt"))

# Extract video IDs from all local files
video_ids = []
filename_map = {}  # video_id -> list of filenames

for f in local_files:
    parts = f.stem.split('_')
    if len(parts) > 0:
        video_id = parts[-1]
        video_ids.append(video_id)

        if video_id not in filename_map:
            filename_map[video_id] = []
        filename_map[video_id].append(f.name)

# Find duplicates
id_counts = Counter(video_ids)
duplicates = {vid: count for vid, count in id_counts.items() if count > 1}

print("\n" + "="*70)
print("DUPLICATE VIDEO IDs IN LOCAL FOLDER")
print("="*70)

if duplicates:
    print(f"\nFound {len(duplicates)} video IDs with multiple transcripts:")
    print()

    for video_id, count in duplicates.items():
        print(f"Video ID: {video_id} (appears {count} times)")
        print(f"  Filenames:")
        for filename in filename_map[video_id]:
            print(f"    - {filename}")
        print()
else:
    print("\nNo duplicates found!")

print("="*70)
