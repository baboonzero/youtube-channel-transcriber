from pathlib import Path

modal_dir = Path("modal_transcripts")
local_dir = Path("data/transcripts/My First Million")

modal_count = len(list(modal_dir.glob("*.txt"))) if modal_dir.exists() else 0
local_count = len(list(local_dir.glob("*.txt"))) if local_dir.exists() else 0

print(f"\nTranscript Count:")
print(f"  Modal transcripts:  {modal_count}")
print(f"  Local transcripts:  {local_count}")
print(f"  Total transcripts:  {modal_count + local_count}")
