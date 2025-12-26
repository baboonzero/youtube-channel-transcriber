# Quick Start Guide - GPU Channel Transcriber

## 🚀 Get Started in 5 Minutes

### Step 1: Verify GPU Setup (1 minute)

```bash
python check_gpu.py
```

**Expected output:**
```
✓ PyTorch installed
✓ CUDA is available
✓ GPU Devices Found: 1
✓ GPU computation test PASSED
```

**If you see errors:** Follow the installation instructions in README_CHANNEL_TRANSCRIBER.md

---

### Step 2: Configure Your Channel (30 seconds)

Edit `config.py`:

```python
# Change this line:
CHANNEL_URL = "https://www.youtube.com/@YourChannelHere"

# Optional: Change model size
MODEL_SIZE = "base"  # Options: tiny, base, small, medium, large
```

---

### Step 3: Run the Transcriber (1 click)

```bash
python run_transcriber.py
```

That's it! The system will:
1. ✅ Scrape all videos from the channel
2. ✅ Download audio files in parallel
3. ✅ Transcribe with GPU acceleration
4. ✅ Save transcripts to `transcripts/` folder
5. ✅ Auto-cleanup temporary files

---

### Step 4: Monitor Progress

**While it's running:**
```bash
# In another terminal
python check_progress.py
```

**You'll see:**
```
📊 OVERALL STATISTICS
Total Videos:          500
Completed:             123 (24.6%)
Pending:               377
Errors:                0

Progress: [████████████░░░░░░░░] 24.6%
```

---

## 💡 Common Scenarios

### Scenario 1: Interrupt and Resume

Press `Ctrl+C` to stop anytime. Run again to resume:
```bash
python run_transcriber.py
```

Progress is saved in `transcription_progress.db`

---

### Scenario 2: Check What's Done

```bash
python check_progress.py
```

---

### Scenario 3: Change Settings Mid-Process

1. Stop the transcriber (`Ctrl+C`)
2. Edit `config.py`
3. Run again: `python run_transcriber.py`

Only pending videos will use new settings.

---

### Scenario 4: Start Fresh

```bash
# Delete the database to start over
rm transcription_progress.db  # Linux/Mac
del transcription_progress.db  # Windows
```

---

## 📁 File Structure

```
YT Transcribe/
├── config.py                    ← EDIT THIS (your settings)
├── run_transcriber.py          ← RUN THIS (main script)
├── channel_transcriber.py      ← Core engine (don't edit)
├── check_gpu.py                ← Verify GPU setup
├── check_progress.py           ← Monitor progress
├── transcription_progress.db   ← Auto-generated (progress tracking)
├── transcription.log           ← Auto-generated (logs)
├── temp_audio/                 ← Auto-generated (temp files)
└── transcripts/                ← Auto-generated (OUTPUT HERE!)
    ├── Video_1_abc123.txt
    ├── Video_2_def456.txt
    └── ...
```

---

## ⚙️ Settings Explained

### Model Size (Speed vs Quality)

| Model  | Speed     | Quality | VRAM | Best For                |
|--------|-----------|---------|------|-------------------------|
| tiny   | Fastest   | Good    | 1GB  | Quick drafts            |
| base   | Fast      | Better  | 1GB  | **RECOMMENDED**         |
| small  | Medium    | Great   | 2GB  | High quality needed     |
| medium | Slow      | Excellent| 5GB | Professional work       |
| large  | Slowest   | Best    | 10GB | Perfect accuracy needed |

### Worker Settings

```python
DOWNLOAD_WORKERS = 10     # How many videos to download at once
                          # More = faster, but may hit rate limits
                          # Recommended: 10-15

TRANSCRIBE_WORKERS = 1    # How many to transcribe in parallel
                          # GPU limited by VRAM
                          # Recommended: 1 (or 2 if 16GB+ VRAM)

BATCH_SIZE = 20          # Videos per batch
                          # Lower = less disk space
                          # Higher = more efficient
```

---

## 🎯 Performance Examples

### Example 1: Small Channel (50 videos, 20 min avg)

```
Model: base
GPU: RTX 3060
Total time: ~1.5 hours
```

### Example 2: Medium Channel (200 videos, 30 min avg)

```
Model: base
GPU: RTX 3070
Total time: ~5 hours
```

### Example 3: Large Channel (500 videos, 40 min avg)

```
Model: small
GPU: RTX 4070
Total time: ~12 hours
```

**Tip:** Run overnight for large channels!

---

## 🔧 Troubleshooting

### "CUDA not available"

```bash
# Check CUDA version
nvidia-smi

# Reinstall PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### "Out of memory"

Edit `config.py`:
```python
MODEL_SIZE = "tiny"  # Use smaller model
```

### "Download failed"

Edit `config.py`:
```python
DOWNLOAD_WORKERS = 5  # Reduce parallel downloads
```

### Check logs

```bash
tail -f transcription.log  # Linux/Mac
Get-Content transcription.log -Wait  # Windows
```

---

## 📊 Understanding Output Files

### Transcript Format

```
transcripts/My_Video_Title_abc123.txt

================================================================================
TRANSCRIPT: My Video Title
Video ID: abc123
================================================================================
Transcription Date: 2025-12-25 10:30:00
Model: Whisper base (GPU: cuda)
Language: en
================================================================================

FULL TRANSCRIPT
--------------------------------------------------------------------------------
[Complete text without timestamps for easy reading]

DETAILED TRANSCRIPT WITH TIMESTAMPS
--------------------------------------------------------------------------------
[00:00] First sentence
[00:05] Second sentence
[00:10] Third sentence
...
```

---

## 🎬 Real-World Workflow

### Morning: Start Processing

```bash
# 9 AM - Start transcription
python run_transcriber.py

# Let it run in background
# Go about your day
```

### Afternoon: Check Progress

```bash
# 2 PM - Check how it's going
python check_progress.py

# Output:
# Completed: 45/100 (45%)
# Estimated completion: 3 hours
```

### Evening: Resume if Needed

```bash
# 5 PM - Need to shutdown?
# Press Ctrl+C

# Later...
# 10 PM - Resume
python run_transcriber.py

# Picks up where it left off!
```

---

## 💰 Cost Comparison

**This System (Local GPU):**
- Electricity: ~$2-5 for 500 videos
- **Total: Essentially FREE**

**Alternatives:**
- OpenAI Whisper API: ~$120 for 500 videos
- Human transcription: ~$1,000+ for 500 videos

**ROI:** System pays for itself after 1-2 large channels!

---

## 🆘 Need Help?

1. Check `transcription.log` for errors
2. Run `python check_progress.py` to see status
3. Run `python check_gpu.py` to verify GPU
4. See README_CHANNEL_TRANSCRIBER.md for detailed docs

---

## 🎉 You're Ready!

```bash
python run_transcriber.py
```

**Happy transcribing!**
