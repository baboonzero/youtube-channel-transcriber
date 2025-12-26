# Managing Multiple Channels

## The Problem

When you have multiple YouTube channels in your database and switch to a new channel in `config.py`, the scripts were getting confused about which channel to process.

**What was happening:**
1. You'd change `CHANNEL_URL` in config to a new channel
2. Run `prepare_for_modal.py`
3. It would scrape the new channel correctly
4. **But then try to download videos from ALL channels in the database!**

This happened because the database tracking methods (`get_pending_videos()` and `get_stats()`) weren't filtering by channel.

---

## The Fix (Applied)

**Updated files:**
- `src/channel_transcriber.py` - Added `channel_filter` parameter to `get_pending_videos()` and `get_stats()`
- `scripts/prepare_for_modal.py` - Now filters by current channel name

**Now when you run `prepare_for_modal.py`:**
1. ✅ Scrapes the channel from config.py
2. ✅ Adds/updates videos in database
3. ✅ Gets stats **only for this channel**
4. ✅ Downloads videos **only for this channel**
5. ✅ Ignores other channels in the database

---

## Current Channels in Your Database

To see all channels:

```bash
cd scripts/utils
python reset_channel.py --list
```

**Example output:**
```
How I AI
  Total videos: 42
  Downloaded:   41
  Pending:      0

My First Million
  Total videos: 1054
  Completed:    614
  Downloaded:   215
  Pending:      0

Playbooks by Anshumani Ruddra
  Total videos: 39
  Completed:    4
  Downloaded:   33
  Pending:      0
```

---

## Switching Between Channels

### Method 1: Just Change Config (Recommended)

The database can hold multiple channels - this is totally fine!

```bash
# 1. Edit config
vim config/config.py
# Change: CHANNEL_URL = "https://www.youtube.com/@new-channel"

# 2. Run prepare_for_modal.py
cd scripts
python prepare_for_modal.py

# It will automatically work with ONLY the new channel!
# Old channels remain in database but are ignored
```

### Method 2: Clear Old Channel First (Optional)

If you want to remove an old channel's data:

```bash
# See all channels
cd scripts/utils
python reset_channel.py --list

# Delete a specific channel
python reset_channel.py --delete "Old Channel Name"

# Or reset a channel (keeps records, clears downloads)
python reset_channel.py "Old Channel Name"
```

---

## Workflow Examples

### Example 1: Processing 3 Different Channels

```bash
# Channel 1
vim config/config.py  # Set CHANNEL_URL to channel 1
python scripts/prepare_for_modal.py
modal run scripts/modal_hybrid.py --max-files 100

# Channel 2
vim config/config.py  # Set CHANNEL_URL to channel 2
python scripts/prepare_for_modal.py
modal run scripts/modal_hybrid.py --max-files 50

# Channel 3
vim config/config.py  # Set CHANNEL_URL to channel 3
python scripts/prepare_for_modal.py
modal run scripts/modal_hybrid.py --max-files 200
```

**Result:** Database contains all 3 channels, organized separately!

### Example 2: Re-processing a Channel

```bash
# Reset the channel (clears downloads but keeps video records)
cd scripts/utils
python reset_channel.py "My Channel Name"

# Re-download and transcribe
vim config/config.py  # Set CHANNEL_URL to this channel
python scripts/prepare_for_modal.py
modal run scripts/modal_hybrid.py --max-files 100
```

### Example 3: Starting Fresh

```bash
# Clear everything
cd scripts/utils
python reset_channel.py --clear-all

# Start with new channel
vim config/config.py  # Set CHANNEL_URL
python scripts/prepare_for_modal.py
```

---

## Benefits of Multi-Channel Support

✅ **No conflicts** - Each channel processes independently
✅ **Shared database** - All channels in one place
✅ **Easy switching** - Just change config.py
✅ **Organized storage** - Each channel gets its own folders:
- `data/temp_audio/{Channel Name}/`
- `data/transcripts/{Channel Name}/`

✅ **Resumable** - Switching channels doesn't lose progress
✅ **No cleanup needed** - Old channels don't interfere

---

## Utilities Reference

### List all channels
```bash
cd scripts/utils
python reset_channel.py --list
```

### Reset a channel (keeps records, clears progress)
```bash
python reset_channel.py "Channel Name"
```

### Delete a channel completely
```bash
python reset_channel.py --delete "Channel Name"
```

### Clear entire database
```bash
python reset_channel.py --clear-all
```

---

## FAQ

**Q: Can I have multiple channels in the database at once?**
A: Yes! This is now fully supported. Each channel is tracked separately.

**Q: Do I need to delete old channels before adding new ones?**
A: No! Just change `CHANNEL_URL` in config.py and run `prepare_for_modal.py`.

**Q: What if I want to switch back to an old channel?**
A: Just change `CHANNEL_URL` back in config.py. If it's already downloaded, `prepare_for_modal.py` will skip downloads.

**Q: Will Modal transcribe the wrong channel?**
A: No. Modal auto-detects the channel from config.py and processes only that channel's files.

**Q: How do I know which channel is currently active?**
A: Check `config/config.py` - the `CHANNEL_URL` setting determines the active channel.

**Q: Can I process multiple channels at the same time?**
A: Not with the same config. You'd need to run separate instances with different config files (advanced use case).

---

## Summary

**Before the fix:**
- Switching channels = chaos
- Had to manually kill scripts
- Database would mix channels
- Confusing errors

**After the fix:**
- Switching channels = change config + run prepare_for_modal.py
- Each channel processes independently
- Clean separation in database and folders
- No conflicts or confusion

**You can now manage unlimited YouTube channels in one database!** 🎉
