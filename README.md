# YouTube Channel Bulk Transcriber - GPU Accelerated

A production-ready system for transcribing entire YouTube channels using GPU-accelerated Whisper AI with faster-whisper for maximum performance.

## 🎯 Features

- **GPU Accelerated** - 35-40x realtime speed with faster-whisper on CUDA
- **Modal Cloud Support** - 70-200x realtime with parallel A10G GPUs
- **Bulk Processing** - Transcribe entire channels (1000+ videos)
- **Multi-Channel** - Process unlimited channels with automatic organization
- **Resumable** - Interrupt and resume anytime without losing progress
- **Parallel Downloads** - Download up to 10 videos simultaneously
- **Smart Storage** - Auto-cleanup of audio files after transcription
- **Progress Tracking** - SQLite database tracks every video
- **Voice Activity Detection** - Automatically skip silence to save compute
- **Error Handling** - Robust retry logic and error recovery

---

## 🚀 Quick Start

### New User? Install First (5-10 minutes)

**Windows:**
```cmd
# Option 1: Double-click setup.bat
# Option 2: Run in terminal
python setup.py
```

**macOS/Linux:**
```bash
python3 setup.py
```

The interactive wizard will:
- ✅ Check your system requirements
- ✅ Install dependencies (Local GPU / Modal Cloud / Both)
- ✅ Test GPU availability
- ✅ Setup Modal authentication
- ✅ Create config file
- ✅ Guide you through everything

**Other options:**
- **Advanced users:** `python quick-setup.py` for minimal setup
- **Manual setup:** See [INSTALL.md](INSTALL.md)
- **Complete guide:** [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)

---

### Already Installed? Run It Now

**Local GPU (All-in-one):**
```bash
python scripts/run_transcriber.py
# Downloads + transcribes on your GPU
```

**Modal Cloud (Hybrid - 2 steps):**
```bash
# Step 1: Download audio locally
python scripts/prepare_for_modal.py

# Step 2: Transcribe on Modal GPUs (parallel, 70-200x realtime)
modal run scripts/modal_hybrid.py --max-files 10
```

**Check Progress:**
```bash
python scripts/utils/check_status.py
```

---

### Which Approach Should You Use?

| Scenario | Recommended | Why |
|----------|-------------|-----|
| **Have NVIDIA GPU (4GB+ VRAM)** | Local GPU | Free, fast enough (35-40x realtime) |
| **Large channel (500+ videos)** | Modal Cloud | Fastest (70-200x realtime), costs $30-40/1000hrs |
| **No NVIDIA GPU** | Modal Cloud | Only option for GPU acceleration |
| **Urgent deadline** | Modal Cloud | Parallel processing = done in minutes |

**Note:** Modal requires hybrid approach (download locally, transcribe on cloud) due to YouTube bot detection. See [docs/MODAL_QUICKSTART.md](docs/MODAL_QUICKSTART.md)

---

### Additional Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - TL;DR for impatient users
- **[INSTALL.md](INSTALL.md)** - Complete installation guide
- **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** - Comprehensive beginner guide
- **[docs/MODAL_QUICKSTART.md](docs/MODAL_QUICKSTART.md)** - Modal cloud setup
- **[docs/MULTI_CHANNEL_GUIDE.md](docs/MULTI_CHANNEL_GUIDE.md)** - Managing multiple channels
- **[WORKFLOW.md](WORKFLOW.md)** - Configuration workflow
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Setup methods comparison
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

---

## 💻 System Requirements

### Hardware

**For Local GPU:**
- **GPU:** NVIDIA GPU with 4GB+ VRAM (8GB recommended)
  - RTX 4060: Tested, works great (8GB VRAM)
  - RTX 3060+: Recommended
  - GTX 1660+: Minimum
- **RAM:** 16GB+ recommended for large channels
- **Storage:** 50-100GB free space for temp audio files

**For Modal Cloud:**
- **Storage:** 10-50GB for audio downloads
- **Internet:** Fast connection recommended

### Software

- **Python:** 3.9 or higher
- **CUDA:** 12.x runtime (for local GPU only)
- **OS:** Windows 10/11, Linux, macOS

---

## ⚙️ Configuration

Edit `config/config.py` to customize:

```python
# Channel to transcribe
CHANNEL_URL = "https://www.youtube.com/@YourChannel"

# Whisper model (tiny/base/small/medium/large)
MODEL_SIZE = "base"  # Recommended for most users

# Recommended by GPU VRAM:
#   4GB:  tiny or base
#   6GB:  small
#   8GB:  small or medium
#   12GB+: medium or large

# Performance settings
DOWNLOAD_WORKERS = 10    # Parallel downloads
TRANSCRIBE_WORKERS = 1   # Must stay at 1 (GPU limitation)
BATCH_SIZE = 20          # Videos per batch

# Output settings
DELETE_AUDIO_AFTER_TRANSCRIPTION = True  # Save disk space
LANGUAGE = "en"          # Language or None for auto-detect
DEVICE = "cuda"          # "cuda" or "cpu"
```

---

## 📊 Performance

### Tested Performance (RTX 4060 Laptop GPU, 8GB VRAM)

**Model: base**
- **Speed:** 35-40x realtime
- **Example:** 60-minute video → 90-120 seconds
- **Throughput:** ~50-60 videos/hour (12-min average)
- **1000 hours of content:** ~25-30 hours processing

### Model Comparison

| Model  | Speed (RTX 4060) | Quality    | VRAM   | Use Case              |
|--------|------------------|------------|--------|-----------------------|
| tiny   | 60-80x realtime  | Good       | 1GB    | Quick drafts          |
| base   | 35-40x realtime  | Better     | 1-2GB  | **Recommended**       |
| small  | 20-25x realtime  | Great      | 2-3GB  | Higher accuracy       |
| medium | 10-15x realtime  | Excellent  | 5GB    | Professional use      |
| large  | 5-8x realtime    | Best       | 10GB   | Maximum accuracy      |

### Modal Cloud Performance

- **Speed:** 70-200x realtime per GPU
- **Parallelization:** 100+ GPUs simultaneously
- **Example:** 1000 hours → ~8-15 minutes with 100 GPUs
- **Cost:** ~$30-40 per 1000 hours

---

## 📁 Project Structure

```
YT Transcribe/
├── setup.py                # Interactive setup wizard
├── quick-setup.py          # Quick setup for advanced users
├── setup.bat               # Windows launcher
│
├── config/
│   ├── config.example.py   # Configuration template
│   └── config.py           # Your configuration (gitignored)
│
├── scripts/
│   ├── run_transcriber.py           # Local GPU (all-in-one)
│   ├── prepare_for_modal.py         # Modal step 1: Download audio
│   ├── modal_hybrid.py              # Modal step 2: Transcribe
│   └── utils/
│       ├── check_status.py          # Check progress
│       ├── reset_channel.py         # Manage channels
│       └── ...
│
├── src/
│   └── channel_transcriber.py       # Core transcription engine
│
└── data/                   # Auto-created, gitignored
    ├── temp_audio/
    │   └── {Channel Name}/          # Downloaded audio
    ├── transcripts/
    │   └── {Channel Name}/          # Output transcripts
    ├── transcription.log            # Detailed logs
    └── transcription_progress.db    # Progress database
```

---

## 🔧 How It Works

### Processing Pipeline

```
1. SCRAPE CHANNEL
   ├─ Fetch all video metadata from YouTube
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

### Multi-Channel Support

Process unlimited channels with automatic organization:

```
data/
├── temp_audio/
│   ├── My First Million/
│   ├── Lex Fridman/
│   └── Your Channel/
└── transcripts/
    ├── My First Million/
    │   ├── video1_abc123.txt
    │   └── video2_def456.txt
    ├── Lex Fridman/
    └── Your Channel/
```

Switch channels by editing `config.py`. Database tracks all channels separately.

---

## 🛠️ Troubleshooting

### GPU Not Detected

```bash
# Check CUDA version
nvidia-smi

# Verify PyTorch sees GPU
python -c "import torch; print(torch.cuda.is_available())"

# Test faster-whisper
python -c "from faster_whisper import WhisperModel; model = WhisperModel('base', device='cuda')"
```

### Out of Memory

If you get CUDA out of memory errors:
1. Use smaller model (`tiny` or `base`)
2. Close other GPU applications
3. Reduce batch size in config.py

### "Library cublas64_12.dll not found"

Install CUDA 12.x runtime from: https://developer.nvidia.com/cuda-downloads

The script automatically adds CUDA to PATH on Windows.

### Modal Authentication Failed

```bash
# Re-run Modal setup
modal setup

# Verify authentication
modal token list
```

For more help, see:
- [INSTALL.md](INSTALL.md) - Installation troubleshooting
- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) - Complete guide

---

## 🔬 Technical Details

### Why faster-whisper?

- **4x faster** than openai-whisper
- Uses CTranslate2 (optimized inference)
- Same accuracy as original Whisper
- Lower memory usage
- Better batching

### Modal Hybrid Architecture

**Why download locally?**

YouTube blocks cloud IPs (AWS, GCP, Modal) with bot detection. Solution:

```
✅ Hybrid Approach (works):
Your Computer → YouTube (downloads from home IP)
     ↓
Your Computer → Modal (uploads audio only)
     ↓
Modal GPUs → Transcribe in parallel (70-200x realtime)
     ↓
Your Computer ← Results stream back
```

**Performance:**
- Download locally: ~5-10 min for 100 videos
- Transcribe on Modal: ~3-5 min for 100 videos (parallel)
- **Total:** ~8-15 min vs 25+ hours on local GPU

**Proven:** 1000+ videos successfully transcribed using this approach.

### Why Different Whisper Implementations?

| Environment | Library | Speed | Reason |
|-------------|---------|-------|--------|
| **Local GPU** | `faster-whisper` | 35-40x | 4x faster, worth complex setup for sustained use |
| **Modal Cloud** | `openai-whisper` | 70-200x | Simpler, faster-whisper has cuDNN issues on Modal |

With 100 parallel GPUs on Modal, individual GPU speed matters less.

---

## 🎯 Best Practices

### For Small Channels (< 100 videos)
- Use `base` or `small` model
- Local GPU is perfect
- Default settings work great

### For Large Channels (500+ videos)
- Use Modal Cloud for speed
- Or use local GPU with `base` model overnight
- Enable `DELETE_AUDIO_AFTER_TRANSCRIPTION = True`
- Monitor disk space

### For Maximum Accuracy
- Use `medium` or `large` model
- Accept slower processing
- Ensure sufficient VRAM

### For Maximum Speed
- Use Modal Cloud with 100+ parallel GPUs
- Or use `tiny` model on local GPU
- Accept lower accuracy for drafts

---

## 📄 License

MIT License - Free to use and modify

## 🙏 Credits

- **Whisper:** OpenAI
- **faster-whisper:** Systran (CTranslate2 implementation)
- **yt-dlp:** yt-dlp contributors
- **PyTorch:** Facebook AI Research
- **Modal:** Modal Labs

---

**Happy Transcribing! 🎉**

**Current System Status:**
- ✅ GPU acceleration with faster-whisper (35-40x realtime)
- ✅ Modal Cloud support (70-200x realtime, parallel)
- ✅ Multi-channel support with automatic organization
- ✅ Interactive setup wizard
- ✅ Resumable processing
- ✅ Production-ready and battle-tested on 1000+ videos
