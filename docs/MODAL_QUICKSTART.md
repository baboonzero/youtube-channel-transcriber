# Modal Quick Start Guide - Hybrid Approach

Get YouTube transcription running on cloud GPUs in 5 minutes.

**Hybrid Architecture:** Download videos locally (bypasses YouTube bot detection) + Transcribe on Modal GPUs (parallel processing)

---

## Prerequisites

1. **Python 3.9+** installed
2. **Config file set up:** Edit `config/config.py` and set your `CHANNEL_URL`
3. **Basic dependencies:** `pip install -r requirements.txt`

---

## Step 1: Install Modal (1 minute)

```bash
pip install modal
```

---

## Step 2: Setup Account (2 minutes)

```bash
modal setup
```

This will:
1. Open browser
2. Sign up / login (free account)
3. Get API token automatically
4. **Free tier: $30 credits included**

---

## Step 3: Test Modal Connection (30 seconds)

Quick test to verify it works:

```bash
cd scripts
modal run modal_hybrid.py --help
```

If you see help text, you're ready!

---

## Step 4: Prepare Channel for Modal

**IMPORTANT:** For a NEW channel, you MUST run this first:

```bash
cd scripts
python prepare_for_modal.py
```

**What this does:**
1. ✅ Scrapes your YouTube channel (from config.py)
2. ✅ Creates database with all video records
3. ✅ Downloads ALL audio files to `data/temp_audio/{Channel Name}/`
4. ✅ NO transcription - just prepares files for Modal

**This replaces the old broken workflow** where you had to kill scripts manually!

**Expected output:**
```
================================================================================
         Prepare Channel for Modal Transcription
================================================================================

Configuration:
  Channel URL:         https://www.youtube.com/@playbooks-anshumani
  Database:            data/transcription_progress.db
  Audio Directory:     data/temp_audio

[STEP 1/3] Scraping channel for videos...
Channel: Playbooks by Anshumani Ruddra
Found: 39 videos

[STEP 2/3] Creating/updating database...
Total videos: 39
Pending download: 39

[STEP 3/3] Downloading 39 pending videos...

Batch 1/2
Downloading 20 videos...
Downloaded 20/20 videos successfully

Batch 2/2
Downloading 19 videos...
Downloaded 19/19 videos successfully

======================================================================
PREPARATION COMPLETE!
======================================================================
Channel: Playbooks by Anshumani Ruddra
Audio files ready: 39
Location: data/temp_audio/Playbooks by Anshumani Ruddra

Next step - Transcribe on Modal:
  modal run scripts/modal_hybrid.py --max-files 39
```

---

## Step 5: Run Modal Transcription (1 minute)

**Start small - test with 3 files:**

```bash
modal run scripts/modal_hybrid.py --max-files 3
```

**What happens:**
1. ✅ Reads 3 audio files from local disk
2. ✅ Detects channel name automatically from config.py
3. ✅ Spawns 3 GPU containers in parallel (A10G GPUs)
4. ✅ Each audio file gets its own dedicated GPU
5. ✅ Upload → Transcribe → Return results
6. ✅ Saves to `data/transcripts/{Channel Name}/` (same structure as local!)
7. ✅ Files named: `{Title}_{VideoID}.txt` (readable names!)
8. ✅ Updates database with transcript paths
9. ✅ Auto-cleanup when done

**Expected output:**
```
======================================================================
Hybrid Modal Transcriber
Downloads: Local | Transcription: Modal GPUs
======================================================================

Using channel from config: Playbooks by Anshumani Ruddra
Audio directory: data/temp_audio/Playbooks by Anshumani Ruddra
Transcript directory: data/transcripts/Playbooks by Anshumani Ruddra

Found 39 audio files
Processing 3 files with Modal GPUs...

[abc123] Transcribing: Playbook - The Rule of 3 and 10...
[def456] Transcribing: Weekend Reading - Thinking in Bets...
[ghi789] Transcribing: Green Eggs and Ham...
[abc123] Loading Whisper model...
[def456] Loading Whisper model...
[ghi789] Loading Whisper model...
[abc123] [OK] Complete! Duration: 720.0s
[def456] [OK] Complete! Duration: 680.0s
[ghi789] [OK] Complete! Duration: 710.0s

[*] Collecting results...

[OK] Playbook - The Rule of 3 and 10... (abc123)
[OK] Weekend Reading - Thinking in Bets... (def456)
[OK] Green Eggs and Ham... (ghi789)

======================================================================
SUMMARY
======================================================================
Completed:        3/3
Failed:           0
Total duration:   35.2 minutes
Processing time:  45.3 seconds
Realtime factor:  46.6x
Output directory: data/transcripts/Playbooks by Anshumani Ruddra
======================================================================
```

**Files created:**
```
data/transcripts/Playbooks by Anshumani Ruddra/
├── Playbook - The Rule of 3 and 10_abc123.txt
├── Weekend Reading - Thinking in Bets_def456.txt
└── Green Eggs and Ham_ghi789.txt
```

---

## Complete Workflow Summary

```bash
# 1. Edit config (one time)
vim config/config.py  # Set CHANNEL_URL

# 2. Prepare channel (scrape + download)
cd scripts
python prepare_for_modal.py

# 3. Transcribe on Modal (test with 3)
modal run scripts/modal_hybrid.py --max-files 3

# 4. If test works, process all files
modal run scripts/modal_hybrid.py --max-files 100
```

---

## How It Works

### Architecture

```
Your Computer
    ↓
    1. prepare_for_modal.py scrapes channel + downloads audio
    ↓
    Audio files saved: data/temp_audio/{Channel}/
    ↓
    2. modal_hybrid.py reads audio files
    ↓
    Upload audio bytes to Modal + Spawn N GPU workers in parallel
    ↓
┌─────────┬─────────┬─────────┬─────────┐
│ GPU #1  │ GPU #2  │ GPU #3  │ GPU #N  │
│ Audio 1 │ Audio 2 │ Audio 3 │ Audio N │
└─────────┴─────────┴─────────┴─────────┘
    ↓         ↓         ↓         ↓
All complete in parallel
    ↓
Results streamed back to your computer
    ↓
Transcripts saved: data/transcripts/{Channel}/
    ↓
Database updated with paths and status
```

**Why Hybrid (vs Full Cloud)?**

✅ **Works Reliably:** Local downloads bypass YouTube bot detection
❌ **Full Cloud Fails:** Modal IPs get blocked by YouTube ("Sign in to confirm you're not a bot")
✅ **Proven:** Successfully transcribed 1000+ videos with hybrid approach

---

### Why openai-whisper on Modal?

Modal uses `openai-whisper`, NOT `faster-whisper` (which is used for local GPU).

**Reason:** faster-whisper fails on Modal with cuDNN incompatibility:
```
Unable to load any of {libcudnn_ops.so.9.1.0, ...}
Invalid handle. Cannot load symbol cudnnCreateTensorDescriptor
```

**Architectural Decision:**

| Environment | Library | Speed | Why |
|-------------|---------|-------|-----|
| Local GPU (RTX 4060) | `faster-whisper` | 35-40x realtime | 4x faster; complex setup justified for sustained local use |
| Modal Cloud (A10G) | `openai-whisper` | 70-200x realtime | Simpler; Modal's environment incompatible with CTranslate2 |

**Why it doesn't matter:**
- A10G GPUs are already 2x faster than RTX 4060
- Running 100 parallel GPUs = effective 7000x realtime speed
- Individual GPU optimization less critical with massive parallelization

---

## Cost Breakdown

**A10G GPU Pricing:** $1.10/hour = $0.0183/minute

**Example: 3 videos, 12 minutes each**
- Total content: 36 minutes
- GPU time: ~90 seconds (parallel)
- Cost: **$0.08**

**Scaling: 100 videos (20 hours content)**
- 100 parallel GPUs: ~2 minutes total time
- Cost: **~$3.60**

**Scaling: 1000 videos (1000 hours content)**
- 100 parallel GPUs: ~15-20 minutes
- Cost: **~$30-40**

---

## Configuration Options

### Process More/Fewer Files

```bash
# Test with 3
modal run scripts/modal_hybrid.py --max-files 3

# Process 50
modal run scripts/modal_hybrid.py --max-files 50

# Process all
modal run scripts/modal_hybrid.py --max-files 1000
```

### Change GPU Type

In `scripts/modal_hybrid.py`, line ~46:

```python
gpu="A10G",  # Options: "T4", "A10G", "A100-40GB", "A100-80GB"
```

**GPU Comparison:**
| GPU | Speed | VRAM | Cost/hr | Best For |
|-----|-------|------|---------|----------|
| T4 | 1x | 16GB | $0.60 | Testing |
| A10G | 2x | 24GB | $1.10 | **Recommended** |
| A100-40GB | 4x | 40GB | $4.00 | Large models |
| A100-80GB | 5x | 80GB | $5.00 | Maximum speed |

### Change Model Size

In `scripts/modal_hybrid.py`, line ~61:

```python
model = whisper.load_model("base", device="cuda")  # tiny, base, small, medium, large
```

---

## Comparison: Local vs Modal

### Local GPU (RTX 4060)
- Speed: 35-40x realtime
- 1000 hours: ~25-30 hours processing
- Cost: Free (electricity)
- Parallelization: 1 video at a time

### Modal with 50x A10G GPUs
- Speed: 70x realtime per GPU
- Effective: 3500x realtime (parallel)
- 1000 hours: ~17 minutes
- Cost: ~$30-40
- Parallelization: 50 videos simultaneously

### Modal with 100x A10G GPUs
- Effective: 7000x realtime
- 1000 hours: ~8-10 minutes
- Cost: ~$40-50

---

## Monitoring Costs

Check your Modal dashboard:
```
https://modal.com/home
```

- See real-time GPU usage
- Track costs per run
- View logs for each worker
- Set budget alerts

---

## Common Issues & Troubleshooting

### "modal: command not found"
```bash
pip install modal
```

### "No Modal token found"
```bash
modal setup
```

### "Database not found"
**Problem:** You didn't run prepare_for_modal.py first

**Solution:**
```bash
cd scripts
python prepare_for_modal.py
```

### No audio files found
**Problem:** prepare_for_modal.py didn't complete or failed

**Solution:**
1. Check `data/temp_audio/{Your Channel}/` for audio files
2. Re-run `python prepare_for_modal.py` (it's resumable)

### Wrong channel being processed
**Problem:** Multiple channels in database

**Solution:**
1. Check `config/config.py` - make sure CHANNEL_URL is correct
2. Modal auto-detects based on your config
3. Or specify manually: `modal run scripts/modal_hybrid.py --audio-dir "data/temp_audio/Your Channel"`

---

## Pro Tips

1. **Always start with 3-5 files** - Test before processing hundreds
2. **Use A10G GPUs** - Best price/performance for Whisper
3. **Monitor costs** - Check dashboard during first runs
4. **Parallel sweet spot** - 50-100 workers is optimal
5. **Free tier gives you** - $30 = ~600 minutes of A10G time

---

## Next Steps

Once you've tested successfully:

1. **Process all files:**
   ```bash
   modal run scripts/modal_hybrid.py --max-files 100
   ```

2. **Check transcripts:**
   ```bash
   ls "data/transcripts/Your Channel Name/"
   ```

3. **Verify database:**
   ```bash
   cd scripts/utils
   python check_status.py
   ```

---

## Why Modal Wins

✅ **No infrastructure** - Just Python code
✅ **Auto-scaling** - 1 GPU or 100 GPUs, same code
✅ **Pay-per-second** - Only charged when GPUs run
✅ **Simple deployment** - `modal run` and done
✅ **Built-in monitoring** - Dashboard shows everything
✅ **Automatic retries** - Failed jobs retry automatically
✅ **No SSH/setup** - Unlike Vast.ai or RunPod

---

**Ready to get started?**

```bash
# Step 1: Prepare channel
cd scripts
python prepare_for_modal.py

# Step 2: Transcribe on Modal
modal run scripts/modal_hybrid.py --max-files 3
```

Let's see cloud GPUs in action! 🚀
