# Modal Hybrid Transcript Naming & Organization Fix

## Problems Identified

### 1. Bad File Naming
**Before:**
```
data/modal_transcripts/
├── abc123.txt
├── def456.txt
└── ghi789.txt
```

Files were named using only video IDs (`abc123.txt`), making them impossible to identify without looking inside.

**Local transcription (correct naming):**
```
data/transcripts/Playbooks by Anshumani Ruddra/
├── Playbook - The Rule of 3 and 10_abc123.txt
├── Weekend Reading - Thinking in Bets_def456.txt
└── Green Eggs and Ham_ghi789.txt
```

Files use format: `{safe_title}_{video_id}.txt`

### 2. Wrong Folder Structure
**Before:**
```
data/modal_transcripts/          # Wrong - not channel-specific
├── all_transcripts_mixed.txt
└── ...
```

**Should be (matches local):**
```
data/transcripts/
├── Playbooks by Anshumani Ruddra/    # Channel-specific folders
│   ├── transcript1.txt
│   └── ...
└── My First Million/
    ├── transcript1.txt
    └── ...
```

---

## What Was Fixed

### 1. Proper File Naming

**Changed:** `scripts/modal_hybrid.py` lines 305-312

```python
# OLD (just video ID)
transcript_file = output_path / f"{result['video_id']}.txt"

# NEW (matches local transcription)
# Format filename: {safe_title}_{video_id}.txt
video_title = result['video_title']
video_id = result['video_id']

# Create safe filename (remove special chars, limit length)
safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
safe_title = safe_title[:80]
transcript_filename = f"{safe_title}_{video_id}.txt"

transcript_file = output_path / transcript_filename
```

**Result:**
- ✅ Filenames now include video title
- ✅ Special characters removed (safe for all filesystems)
- ✅ Limited to 80 characters (prevents too-long filenames)
- ✅ Matches local transcription format exactly

### 2. Channel-Specific Folders

**Changed:** `scripts/modal_hybrid.py` lines 214-220

```python
# OLD (hardcoded modal_transcripts folder)
output_dir: str = "data/modal_transcripts"

# NEW (auto-detects channel, uses proper structure)
output_dir: str = None  # Default to None

# Later in code:
if output_dir is None:
    try:
        from config import TRANSCRIPT_DIR
    except ImportError:
        TRANSCRIPT_DIR = "data/transcripts"
    output_dir = f"{TRANSCRIPT_DIR}/{channel_name}"
```

**Result:**
- ✅ Transcripts saved to `data/transcripts/{Channel Name}/`
- ✅ Matches local transcription folder structure
- ✅ Multiple channels organized separately
- ✅ Easy to find transcripts by channel

### 3. Get Video Titles from Database

**Added:** `scripts/modal_hybrid.py` lines 248-267

```python
# Get video titles from database
db_path = Path(DATABASE_FILE)
video_titles = {}
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get all video IDs and titles
    video_ids = [f.stem for f in audio_files]
    placeholders = ','.join('?' * len(video_ids))
    cursor.execute(f'''
        SELECT video_id, title
        FROM videos
        WHERE video_id IN ({placeholders})
    ''', video_ids)

    for video_id, title in cursor.fetchall():
        video_titles[video_id] = title

    conn.close()
```

**Result:**
- ✅ Fetches actual video titles from database
- ✅ Passes titles to transcription workers
- ✅ Enables proper filename formatting

### 4. Update Database with Transcript Paths

**Added:** `scripts/modal_hybrid.py` lines 318-325

```python
# Update database with transcript path
if db_cursor:
    db_cursor.execute('''
        UPDATE videos
        SET status = 'completed', transcript_path = ?, updated_at = CURRENT_TIMESTAMP
        WHERE video_id = ?
    ''', (str(transcript_file), video_id))
    db_conn.commit()
```

**Result:**
- ✅ Database tracks where transcripts are saved
- ✅ Status updated to "completed"
- ✅ Can query database to find transcript locations
- ✅ Matches local transcription behavior

### 5. Better Output Messages

**Changed:** Line 329

```python
# OLD
print(f"[OK] {filename}")

# NEW
print(f"[OK] {safe_title[:50]}... ({video_id})")
```

**Result:**
- ✅ Shows video title in progress output
- ✅ Easy to track which video is being processed
- ✅ More informative than just filenames

---

## Before & After Comparison

### Before (Broken)

**Running Modal:**
```bash
modal run scripts/modal_hybrid.py --max-files 5
```

**Output:**
```
[OK] abc123.webm
[OK] def456.webm
[OK] ghi789.webm
```

**Files created:**
```
data/modal_transcripts/
├── abc123.txt    # Who knows what this is?
├── def456.txt    # No idea
└── ghi789.txt    # ???
```

**Problems:**
- ❌ Can't tell which video each file is
- ❌ All channels mixed in one folder
- ❌ Database not updated (can't track progress)

---

### After (Fixed)

**Running Modal:**
```bash
modal run scripts/modal_hybrid.py --max-files 5
```

**Output:**
```
Using channel from config: Playbooks by Anshumani Ruddra
Audio directory: data/temp_audio/Playbooks by Anshumani Ruddra
Transcript directory: data/transcripts/Playbooks by Anshumani Ruddra

[*] Collecting results...

[OK] Playbook - The Rule of 3 and 10... (abc123)
[OK] Weekend Reading - Thinking in Bets... (def456)
[OK] Green Eggs and Ham... (ghi789)
```

**Files created:**
```
data/transcripts/Playbooks by Anshumani Ruddra/
├── Playbook - The Rule of 3 and 10_abc123.txt
├── Weekend Reading - Thinking in Bets_def456.txt
└── Green Eggs and Ham_ghi789.txt
```

**Benefits:**
- ✅ Clear, readable filenames with video titles
- ✅ Organized by channel (same as local transcription)
- ✅ Database updated with paths and status
- ✅ Easy to find and identify transcripts
- ✅ Consistent with local transcription structure

---

## Testing the Fix

### Test 1: File Naming
```bash
modal run scripts/modal_hybrid.py --max-files 3
```

**Check:**
- Files have format: `{Title}_{VideoID}.txt`
- Special characters removed from titles
- Filenames under 100 characters

### Test 2: Folder Structure
```bash
ls data/transcripts/
```

**Expected:**
```
Playbooks by Anshumani Ruddra/
My First Million/
```

**Check:**
- Each channel has its own folder
- Matches `data/temp_audio/` structure
- NO `modal_transcripts/` folder

### Test 3: Database Update
```python
import sqlite3
conn = sqlite3.connect('data/transcription_progress.db')
cursor = conn.cursor()
cursor.execute("SELECT video_id, status, transcript_path FROM videos WHERE status='completed' LIMIT 5")
for row in cursor.fetchall():
    print(row)
```

**Expected:**
```
('abc123', 'completed', 'data/transcripts/Playbooks.../Title_abc123.txt')
('def456', 'completed', 'data/transcripts/Playbooks.../Title_def456.txt')
```

**Check:**
- Status = 'completed'
- transcript_path contains full path to channel-specific folder
- Paths use proper filenames with titles

---

## Summary

**Modal transcription now:**
1. ✅ Names files exactly like local transcription: `{title}_{id}.txt`
2. ✅ Saves to channel-specific folders: `data/transcripts/{Channel}/`
3. ✅ Updates database with paths and status
4. ✅ Shows clear progress with video titles
5. ✅ Fully consistent with local transcription workflow

**No more:**
- ❌ Cryptic video ID filenames
- ❌ Mixed transcripts in wrong folders
- ❌ Database out of sync
- ❌ Confusion about which file is which

**The Modal and Local workflows are now identical in their output structure!**
