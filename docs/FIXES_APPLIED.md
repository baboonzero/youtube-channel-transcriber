# Documentation & Workflow Fixes

## Problem Identified

The original workflow for Modal hybrid mode was **completely broken** for new users.

### What Was Wrong

**Documentation said:**
```bash
# Step 1: Download audio
python download_only.py

# Step 2: Transcribe on Modal
modal run scripts/modal_hybrid.py
```

**What actually happened for a new user:**
1. User edits `config.py` with their channel URL
2. User runs `python download_only.py`
3. **ERROR**: `Database not found at data/transcription_progress.db`

**Why it failed:**
- `download_only.py` **requires** the database to already exist with video records
- It only downloads videos marked as "pending" in the database
- For a brand new channel, there IS no database yet!

**The insane workaround that we discovered:**
1. Edit config.py
2. Run `run_transcriber.py` (starts scraping, downloading, transcribing)
3. **Manually kill it with Ctrl+C** after it starts downloading
4. Run `download_only.py` to download the rest
5. Run Modal

This is ridiculous! You can't expect users to kill a script mid-execution.

---

## What Was Fixed

### 1. Created `scripts/prepare_for_modal.py`

**New one-command workflow for Modal:**
```bash
# Edit config.py first, then:
python scripts/prepare_for_modal.py  # Does EVERYTHING
modal run scripts/modal_hybrid.py    # Transcribe on Modal
```

**What `prepare_for_modal.py` does:**
1. ✅ Scrapes the YouTube channel to discover all videos
2. ✅ Creates/updates the database with video records
3. ✅ Downloads ALL audio files (in batches)
4. ✅ NO transcription - just prepares files for Modal
5. ✅ Resumable if interrupted
6. ✅ Clear progress indicators
7. ✅ Tells you exactly what to run next

### 2. Updated All Documentation

**Files updated:**
- `README.md` - Fixed Modal hybrid workflow (lines 81-90)
- `docs/GETTING_STARTED.md` - Fixed Step 5 (lines 316-335)
- `WORKFLOW.md` - Fixed hybrid workflow section
- Created `QUICKSTART.md` - TL;DR guide for impatient users

**Key changes:**
- Replaced `python download_only.py` → `python prepare_for_modal.py`
- Added clear explanation of what each script does
- Removed confusing references to manually killing scripts
- Created simple decision tree for which path to use

### 3. Fixed All Scripts to Work from Any Directory

**Problem:** Scripts only worked if run from project root.

**Fix:** Added to ALL scripts:
```python
# Add project root to path
project_root = Path(__file__).parent.parent
os.chdir(project_root)  # Change to project root
```

**Scripts fixed:**
- `scripts/run_transcriber.py`
- `scripts/download_only.py`
- `scripts/download_pending.py`
- `scripts/modal_hybrid.py`
- `scripts/prepare_for_modal.py` (new)

**Now works from anywhere:**
```bash
cd scripts && python download_only.py  ✅
cd .. && python scripts/download_only.py  ✅
python "C:\Full\Path\To\scripts\download_only.py"  ✅
```

### 4. Improved Modal Script Channel Detection

**Problem:** `modal_hybrid.py` had hardcoded channel path.

**Fix:** Now auto-detects channel from config.py using keyword matching:
- Extracts keywords from CHANNEL_URL
- Matches against database channel names
- Picks best match with downloaded videos
- Falls back to channel with most downloads

**Example:**
```python
# config.py
CHANNEL_URL = "https://www.youtube.com/@playbooks-anshumani"

# Auto-matches to database channel:
# "Playbooks by Anshumani Ruddra"
# (keywords "playbooks" + "anshumani" match)
```

---

## New User Experience (BEFORE vs AFTER)

### BEFORE (Broken)

```bash
# User edits config.py
vim config/config.py

# User runs what docs say
python scripts/download_only.py
❌ Error: Database not found

# User confused, tries other things...
python scripts/run_transcriber.py
# It starts transcribing locally (wrong!)

# User gives up or asks for help
```

### AFTER (Fixed)

```bash
# User edits config.py
vim config/config.py

# User runs prepare script
python scripts/prepare_for_modal.py
✅ Scraping channel...
✅ Found 39 videos
✅ Downloading batch 1/2...
✅ Downloaded 20/39 videos
✅ Downloading batch 2/2...
✅ Downloaded 39/39 videos
✅ COMPLETE! Audio ready at data/temp_audio/Channel Name/

Next step: modal run scripts/modal_hybrid.py --max-files 39

# User runs Modal
modal run scripts/modal_hybrid.py --max-files 39
✅ Using channel from config: Playbooks by Anshumani Ruddra
✅ Transcribing 39 files on Modal GPUs...
✅ DONE!
```

---

## Summary of Scripts & Their Purposes

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `run_transcriber.py` | All-in-one: Scrape + Download + Transcribe locally | Local GPU workflow |
| `prepare_for_modal.py` | **NEW!** Scrape + Download only (no transcribe) | **Modal workflow - START HERE** |
| `download_only.py` | Download pending videos (requires DB to exist) | Resume interrupted downloads |
| `modal_hybrid.py` | Transcribe on Modal GPUs | After prepare_for_modal.py |

**Key insight:** For Modal workflow, **NEW USERS** should use `prepare_for_modal.py`, not `download_only.py`.

---

## Files Created/Modified

### Created:
- `scripts/prepare_for_modal.py` - Main fix (new one-command workflow)
- `QUICKSTART.md` - TL;DR guide
- `WORKFLOW.md` - Configuration workflow guide
- `docs/FIXES_APPLIED.md` - This document

### Modified:
- `README.md` - Fixed Modal workflow section
- `docs/GETTING_STARTED.md` - Fixed Step 5
- `scripts/run_transcriber.py` - Added os.chdir fix
- `scripts/download_only.py` - Added os.chdir fix
- `scripts/download_pending.py` - Added os.chdir fix
- `scripts/modal_hybrid.py` - Added os.chdir fix + auto channel detection

---

## Testing Recommendations

Before releasing, test the following scenarios:

### 1. Brand New User with Modal
```bash
# Clean slate
rm -rf data/

# Configure
edit config/config.py  # Set CHANNEL_URL

# Run workflow
python scripts/prepare_for_modal.py  # Should scrape + download
modal run scripts/modal_hybrid.py --max-files 5  # Should transcribe
```

**Expected:** No errors, all 5 files transcribed.

### 2. Resume After Interruption
```bash
# Start download
python scripts/prepare_for_modal.py
# Press Ctrl+C after 10 videos downloaded

# Resume
python scripts/prepare_for_modal.py
# Should skip already downloaded, continue with rest
```

**Expected:** Resumes from where it stopped.

### 3. Run from Different Directories
```bash
cd scripts
python prepare_for_modal.py  # Should work

cd ..
python scripts/prepare_for_modal.py  # Should work

cd /some/other/path
python "/full/path/to/scripts/prepare_for_modal.py"  # Should work
```

**Expected:** All work correctly.

### 4. Multiple Channels in Same Database
```bash
# Channel 1
edit config/config.py  # Set Channel A
python scripts/prepare_for_modal.py

# Channel 2
edit config/config.py  # Set Channel B
python scripts/prepare_for_modal.py

# Transcribe Channel B
modal run scripts/modal_hybrid.py
```

**Expected:** Auto-detects and uses Channel B files.

---

## Conclusion

The workflow is now **user-friendly** and **actually works** for new users without requiring them to:
- Read complex documentation
- Manually kill scripts
- Run multiple confusing steps
- Edit scripts directly

**New workflow is:** Edit config → Run one script → Run Modal → Done!
