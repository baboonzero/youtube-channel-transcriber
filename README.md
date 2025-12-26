# YouTube Channel Bulk Transcriber - GPU Accelerated

A production-ready system for transcribing entire YouTube channels using GPU-accelerated Whisper AI with faster-whisper for maximum performance.

## 🎯 Features

- **GPU Accelerated** - 35-40x realtime speed with faster-whisper on CUDA
- **Bulk Processing** - Transcribe entire channels (1000+ videos)
- **Channel Organization** - Automatic folder structure per channel
- **Resumable** - Interrupt and resume anytime without losing progress
- **Parallel Downloads** - Download up to 10 videos simultaneously
- **Smart Storage** - Auto-cleanup of audio files after transcription
- **Progress Tracking** - SQLite database tracks every video
- **Voice Activity Detection** - Automatically skip silence to save compute
- **Error Handling** - Robust retry logic and error recovery

## 📁 Project Structure

```
YT Transcribe/
├── src/                    # Source code
│   └── channel_transcriber.py      # Full channel transcription orchestrator
│
├── scripts/                # Runner scripts
│   └── run_transcriber.py          # Main entry point (use this!)
│
├── config/                 # Configuration files
│   └── config.py                   # User configuration
│
└── data/                   # Runtime data (auto-created)
    ├── temp_audio/                 # Temporary audio files
    │   └── {Channel Name}/         # Per-channel folders
    ├── transcripts/                # Output transcripts
    │   └── {Channel Name}/         # Per-channel folders
    ├── transcription.log           # Detailed logs
    └── transcription_progress.db   # Progress database
```

## 🚀 Quick Start

### Just Want to Start? **TL;DR**

**👉 Fastest path:** [QUICKSTART.md](QUICKSTART.md) - Edit config, run 1-2 commands, done!

### First Time User? Need Full Setup?

**👉 Complete guide:** [Getting Started Guide](docs/GETTING_STARTED.md)

This comprehensive guide will help you:
- ✅ Check if you have a compatible GPU
- ✅ Choose between Local GPU or Cloud GPU (Modal)
- ✅ Install all prerequisites step-by-step
- ✅ Run your first transcription in 5-30 minutes
- ✅ Troubleshoot common issues

**📋 Prefer a checklist?** See [Setup Checklist](docs/SETUP_CHECKLIST.md)

---

### Which Approach Should You Use?

| Scenario | Recommended Approach | Why |
|----------|---------------------|-----|
| **Have NVIDIA GPU (4GB+ VRAM)** | Local GPU | Free, fast enough (35-40x realtime) |
| **Large channel (500+ videos)** | Hybrid: Download locally + Modal transcribe | Fastest (70-200x realtime), costs $30-40/1000hrs |
| **No NVIDIA GPU** | Hybrid: Download locally + Modal transcribe | Only option for GPU acceleration |
| **Urgent deadline** | Hybrid: Download locally + Modal transcribe | Parallel processing = done in minutes |

**⚠️ Important:** Modal Cloud requires **hybrid approach** (download locally, transcribe on cloud)
- **Why?** YouTube blocks Modal's cloud IPs with bot detection
- **Solution:** Download from your home IP, upload to Modal only for transcription
- **Proven:** 430 videos successfully transcribed using this method

---

### Already Set Up? Quick Commands

**Local GPU (All-in-one):**
```bash
cd scripts
python run_transcriber.py
# Downloads + transcribes on your GPU
```

**Modal Cloud (Hybrid - 2 steps required):**
```bash
# Step 1: Scrape channel + Download audio (on YOUR computer)
# This scrapes the channel, creates database, downloads all audio
cd scripts
python prepare_for_modal.py

# Step 2: Transcribe on Modal GPUs (parallel, 70-200x realtime)
modal run scripts/modal_hybrid.py --max-files 10
```

**Check Progress:**
```bash
cd scripts/utils
python check_status.py
```

## 💻 System Requirements

### Hardware
- **GPU:** NVIDIA GPU with 4GB+ VRAM (8GB recommended)
  - RTX 4060: Tested, works great (8GB VRAM)
  - RTX 3060+: Recommended
  - GTX 1660+: Minimum
- **RAM:** 16GB+ recommended for large channels
- **Storage:** 50-100GB free space for temp audio files

### Software
- **Python:** 3.9 or higher
- **CUDA:** 12.x runtime (faster-whisper requirement)
- **OS:** Windows 10/11, Linux, macOS

## ⚙️ Configuration

Edit `config/config.py` to customize:

```python
# ============================================================================
# CHANNEL SETTINGS
# ============================================================================
CHANNEL_URL = "https://www.youtube.com/@YourChannel"

# ============================================================================
# WHISPER MODEL SETTINGS
# ============================================================================
MODEL_SIZE = "base"  # tiny, base, small, medium, large

# Recommended by GPU VRAM:
#   4GB:  tiny or base
#   6GB:  small
#   8GB:  small or medium
#   12GB: medium or large
#   16GB+: large

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================
DOWNLOAD_WORKERS = 10    # Parallel downloads (10-15 recommended)
TRANSCRIBE_WORKERS = 1   # GPU transcriptions (KEEP AT 1)
BATCH_SIZE = 20          # Videos per batch

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================
AUDIO_DIR = "data/temp_audio"
TRANSCRIPT_DIR = "data/transcripts"
DELETE_AUDIO_AFTER_TRANSCRIPTION = True  # Save disk space

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================
LANGUAGE = "en"          # Language code or None for auto-detect
DEVICE = "cuda"          # "cuda" for GPU, "cpu" for CPU
```

## 📊 Performance

### Actual Performance (Tested on RTX 4060 Laptop GPU, 8GB VRAM)

**Model: base**
- **Speed:** 35-40x realtime
- **Example:** 60-minute video → 90-120 seconds transcription
- **Throughput:** ~50-60 videos/hour (12-minute average videos)

**Processing 1000 hours of content:**
- **Local (RTX 4060):** ~25-30 hours
- **Speed varies by:** Video length, speech density, audio quality

### Model Comparison

| Model  | Speed (RTX 4060) | Quality    | VRAM   | Use Case              |
|--------|------------------|------------|--------|-----------------------|
| tiny   | 60-80x realtime  | Good       | 1GB    | Quick drafts          |
| base   | 35-40x realtime  | Better     | 1-2GB  | **Recommended**       |
| small  | 20-25x realtime  | Great      | 2-3GB  | Higher accuracy       |
| medium | 10-15x realtime  | Excellent  | 5GB    | Professional use      |
| large  | 5-8x realtime    | Best       | 10GB   | Maximum accuracy      |

## 🔧 How It Works

### Processing Pipeline

```
1. SCRAPE CHANNEL
   ├─ Fetch all video metadata
   ├─ Store in SQLite database
   └─ Calculate total duration

2. DOWNLOAD BATCH (20 videos)
   ├─ Parallel download with 10 workers
   ├─ Extract audio only (saves time/bandwidth)
   └─ Store in data/temp_audio/{Channel}/

3. TRANSCRIBE BATCH
   ├─ Load faster-whisper model on GPU
   ├─ Process each video sequentially
   ├─ Apply Voice Activity Detection (VAD)
   ├─ Generate timestamped transcript
   ├─ Save to data/transcripts/{Channel}/
   └─ Delete audio file (configurable)

4. REPEAT
   └─ Continue until all videos processed
```

### Database Schema

SQLite database tracks:
- Video ID, title, URL
- Status: pending → downloaded → completed
- Audio file path
- Transcript file path
- Error messages (if any)

**Resumable:** If interrupted, restart script and it continues from where it left off.

## 🛠️ Troubleshooting

### "Library cublas64_12.dll is not found"

**Solution:** Install CUDA 12.x runtime
```bash
# Download from: https://developer.nvidia.com/cuda-downloads
# Install CUDA 12.6 or later
# Verify: nvidia-smi should show CUDA 12.x
```

The script automatically adds CUDA 12 to PATH:
```python
# In run_transcriber.py
cuda12_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin"
os.environ['PATH'] = cuda12_path + os.pathsep + os.environ['PATH']
```

### Unicode Encoding Errors in Logs

**Status:** ✅ Fixed in run_transcriber.py

The script now properly handles UTF-8 encoding:
```python
logging.FileHandler(LOG_FILE, encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
```

### GPU Not Detected

```bash
# Check CUDA version
nvidia-smi

# Verify PyTorch sees GPU
python -c "import torch; print(torch.cuda.is_available())"

# Verify faster-whisper can use GPU
python -c "from faster_whisper import WhisperModel; model = WhisperModel('base', device='cuda')"
```

### Out of Memory

If you get CUDA out of memory errors:
1. Use smaller model (try `tiny` or `base`)
2. Close other GPU applications
3. Reduce batch size in config.py

### Parallel Transcription Not Supported

**Why TRANSCRIBE_WORKERS must be 1:**
- Whisper models are not thread-safe
- SQLite connections can't be shared across processes
- GPU memory conflicts with multiple models

For faster processing, use a bigger GPU or rent cloud GPUs (see future plans).

## 📈 Status Monitoring

Check progress anytime:

```python
import sqlite3

conn = sqlite3.connect('data/transcription_progress.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT status, COUNT(*)
    FROM videos
    GROUP BY status
''')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]}')
```

Or check the log file:
```bash
tail -f data/transcription.log
```

## 🎯 Best Practices

### For Small Channels (< 100 videos)
- Use `base` or `small` model
- Default settings work great

### For Large Channels (500+ videos)
- Use `base` model for speed
- Enable `DELETE_AUDIO_AFTER_TRANSCRIPTION = True`
- Run overnight
- Monitor disk space

### For Maximum Accuracy
- Use `medium` or `large` model
- Increase VRAM requirements
- Accept slower processing

### For Maximum Speed
- Use `tiny` model
- Accept lower accuracy
- Great for quick drafts

## 🔬 Technical Details

### Why faster-whisper?

- **4x faster** than openai-whisper
- Uses CTranslate2 (optimized inference)
- Same accuracy as original Whisper
- Lower memory usage
- Better batching

### Modal Hybrid Architecture (Why 2 Steps?)

**Question:** Why can't Modal download YouTube videos directly?

**Answer:** YouTube's bot detection blocks cloud IPs (AWS, GCP, Modal, etc.)

**The Problem:**
```
Full Cloud Approach (doesn't work):
Your Computer → Modal Cloud → YouTube
                     ↓
                YouTube: "Sign in to confirm you're not a bot" ❌
```

**The Solution (Hybrid):**
```
Hybrid Approach (proven to work):
Your Computer → YouTube (downloads from your home IP) ✅
     ↓
Your Computer → Modal Cloud (uploads audio only)
     ↓
Modal GPUs → Transcribe in parallel
     ↓
Your Computer ← Results stream back
```

**Why this works:**
- ✅ Downloads from YOUR home IP (YouTube doesn't block you)
- ✅ Only audio files go to Modal (not YouTube URLs)
- ✅ Modal never touches YouTube directly
- ✅ **Proven:** 430 videos successfully processed

**Performance:**
- Download locally: ~5-10 minutes for 100 videos (your bandwidth)
- Transcribe on Modal: ~3-5 minutes for 100 videos (70-200x realtime, parallel)
- **Total:** ~8-15 minutes vs 25+ hours on local GPU

---

### Whisper Implementation: Local vs Cloud

This project uses **different Whisper implementations** depending on where transcription runs:

| Environment | Library | Speed | Reason |
|-------------|---------|-------|--------|
| **Local GPU** (RTX 4060) | `faster-whisper` | 35-40x realtime | 4x faster than openai-whisper; worth the complex CTranslate2+cuDNN setup for sustained local use |
| **Modal Cloud** | `openai-whisper` | 70-200x realtime | Simpler deployment; faster-whisper has cuDNN library incompatibility on Modal's environment |

**Why not use faster-whisper everywhere?**

We tested faster-whisper on Modal and it failed with cuDNN errors:
```
Unable to load any of {libcudnn_ops.so.9.1.0, ...}
Invalid handle. Cannot load symbol cudnnCreateTensorDescriptor
```

**Why this works well:**
- **Local:** faster-whisper optimization matters for 25+ hour processing jobs
- **Modal:** openai-whisper is fast enough with A10G GPUs + 100 parallel workers
- Individual GPU speed less critical when running 100 GPUs simultaneously

**See also:** `docs/MODAL_QUICKSTART.md` for detailed cloud GPU setup

### Voice Activity Detection (VAD)

Automatically skips silence:
- Typical savings: 15-30% compute time
- No accuracy loss
- Configurable threshold

### Channel-Specific Folders

Outputs organized by channel:
```
data/
├── temp_audio/
│   ├── My First Million/
│   ├── Lex Fridman/
│   └── ...
└── transcripts/
    ├── My First Million/
    │   ├── video1_abc123.txt
    │   ├── video2_def456.txt
    │   └── ...
    └── Lex Fridman/
        └── ...
```

## 📄 License

MIT License - Free to use and modify

## 🙏 Credits

- **Whisper:** OpenAI
- **faster-whisper:** Systran (CTranslate2 implementation)
- **yt-dlp:** yt-dlp contributors
- **PyTorch:** Facebook AI Research

---

**Happy Transcribing! 🎉**

**Current System Status:**
- ✅ GPU acceleration with faster-whisper
- ✅ CUDA 12 support
- ✅ Channel-specific organization
- ✅ Resumable processing
- ✅ Production-ready and battle-tested
