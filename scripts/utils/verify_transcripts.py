from pathlib import Path

print("\n" + "="*70)
print("VERIFYING ALL TRANSCRIPTS ARE UNIQUE")
print("="*70)

# 1. Local transcripts
local_dir = Path("data/transcripts/My First Million")
local_files = list(local_dir.glob("*.txt")) if local_dir.exists() else []
local_file_count = len(local_files)
local_unique_ids = set(f.stem for f in local_files)
local_unique_count = len(local_unique_ids)

print(f"\n1. LOCAL TRANSCRIPTS:")
print(f"   Folder: {local_dir}")
print(f"   Total files:        {local_file_count}")
print(f"   Unique video IDs:   {local_unique_count}")
print(f"   Duplicates in folder: {local_file_count - local_unique_count}")

if local_file_count == local_unique_count:
    print(f"   Status: OK - No duplicates")
else:
    print(f"   Status: WARNING - {local_file_count - local_unique_count} duplicate files!")

# 2. Modal transcripts
modal_dir = Path("modal_transcripts")
modal_files = list(modal_dir.glob("*.txt")) if modal_dir.exists() else []
modal_file_count = len(modal_files)
modal_unique_ids = set(f.stem for f in modal_files)
modal_unique_count = len(modal_unique_ids)

print(f"\n2. MODAL TRANSCRIPTS:")
print(f"   Folder: {modal_dir}")
print(f"   Total files:        {modal_file_count}")
print(f"   Unique video IDs:   {modal_unique_count}")
print(f"   Duplicates in folder: {modal_file_count - modal_unique_count}")

if modal_file_count == modal_unique_count:
    print(f"   Status: OK - No duplicates")
else:
    print(f"   Status: WARNING - {modal_file_count - modal_unique_count} duplicate files!")

# 3. Check for overlap between folders
overlap = local_unique_ids & modal_unique_ids

print(f"\n3. OVERLAP CHECK (same video in both folders):")
print(f"   Videos in both local AND modal: {len(overlap)}")

if len(overlap) == 0:
    print(f"   Status: OK - No overlap")
else:
    print(f"   Status: WARNING - {len(overlap)} videos transcribed in BOTH places!")
    print(f"\n   First 10 overlapping video IDs:")
    for i, vid_id in enumerate(sorted(list(overlap))[:10]):
        print(f"      {i+1}. {vid_id}")

# 4. Total unique transcripts
all_unique_ids = local_unique_ids | modal_unique_ids
total_unique = len(all_unique_ids)

print(f"\n" + "="*70)
print("FINAL VERIFICATION:")
print("="*70)
print(f"   Local files:          {local_file_count}")
print(f"   Modal files:          {modal_file_count}")
print(f"   Total files:          {local_file_count + modal_file_count}")
print(f"   ----------------------------------------")
print(f"   Unique video IDs:     {total_unique}")
print(f"   ----------------------------------------")

if (local_file_count + modal_file_count) == total_unique:
    print(f"   Status: PERFECT - All transcripts are unique!")
else:
    duplicates = (local_file_count + modal_file_count) - total_unique
    print(f"   Status: WARNING - {duplicates} duplicate transcripts found!")

print("="*70)

# 5. Summary against YouTube
print(f"\nPROJECT SUMMARY:")
print(f"   YouTube Channel:      1,054 videos")
print(f"   Unique Transcripts:   {total_unique} videos")
print(f"   Missing:              {1054 - total_unique} videos")
print("="*70)
