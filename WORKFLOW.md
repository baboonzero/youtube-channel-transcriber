# YouTube Transcription Workflow - Configuration Guide

## The Problem You Identified
Previously, you had to manually update channel names in every Python script. This was a design flaw - the whole point of `config.py` is to configure once and use everywhere!

## The Solution
Now **ALL scripts** automatically use `config.py`. You only need to edit channel settings in ONE place.

## Complete Workflow

### 1. Configure Your Channel (ONCE)
Edit `config/config.py`:
```python
CHANNEL_URL = "https://www.youtube.com/@your-channel-name"
```

That's it! All scripts will automatically:
- Detect the channel name from the database
- Use the correct audio directory
- Match the channel intelligently using keywords

### 2. Prepare Channel for Modal (Scrape + Download)
```bash
python scripts/prepare_for_modal.py
```

What it does:
- **Scrapes** the channel in `config.py` to discover all videos
- **Creates database** with video records
- **Downloads** all audio files to `data/temp_audio/{channel_name}/`
- **NO transcription** - just prepares for Modal
- Can be interrupted and resumed anytime

### 3. Transcribe on Modal (Later)
```bash
# Auto-detects channel from config.py
modal run scripts/modal_hybrid.py

# Or specify number of files
modal run scripts/modal_hybrid.py --max-files 50

# Or override audio directory
modal run scripts/modal_hybrid.py --audio-dir "data/temp_audio/Your Channel"
```

What it does:
- Automatically detects which channel to process based on `config.py`
- Reads audio files from local disk
- Sends to Modal GPUs for parallel transcription
- Saves transcripts to `data/modal_transcripts/`

## How Channel Detection Works

The `modal_hybrid.py` script now:
1. Extracts keywords from `CHANNEL_URL` in config.py (e.g., "playbooks", "anshumani")
2. Matches against channel names in database
3. Picks the channel with best keyword match that has downloaded videos
4. Falls back to channel with most downloads if no match

Example:
- Config: `https://www.youtube.com/@playbooks-anshumani`
- Database: "Playbooks by Anshumani Ruddra"
- Match: ✓ (keywords "playbooks" + "anshumani" match)

## Switching Channels

To work on a different channel:
1. Edit `config.py` - change `CHANNEL_URL`
2. Run `python scripts/prepare_for_modal.py`
3. Run `modal run scripts/modal_hybrid.py`

That's it! No need to edit any other files.

## Status Checking

Check download status:
```bash
python scripts/utils/check_status.py
```

## Benefits
- ✅ Single source of truth (`config.py`)
- ✅ No hardcoded channel names in scripts
- ✅ Intelligent channel matching
- ✅ Works with multiple channels in same database
- ✅ Automatic path detection
