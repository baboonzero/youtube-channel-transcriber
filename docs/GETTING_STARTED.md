# Getting Started - First-Time User Guide

**Welcome!** This guide walks you through the complete setup process from scratch.

---

## 🤔 Step 0: Do I Have a GPU? Can I Use This?

### Check if you have an NVIDIA GPU

**Windows:**
1. Right-click on desktop → **Display settings**
2. Scroll down → **Advanced display**
3. Look for GPU name under "Display adapter properties"

OR open Command Prompt and run:
```bash
nvidia-smi
```

**Expected output if you have NVIDIA GPU:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 545.84       Driver Version: 545.84       CUDA Version: 12.3     |
|-------------------------------+----------------------+----------------------+
| GPU  Name            TCC/WDDM | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ... WDDM  | 00000000:01:00.0  On |                  N/A |
```

**If `nvidia-smi` works:** ✅ You have an NVIDIA GPU!
**If command not found:** ❌ Either no NVIDIA GPU or drivers not installed

---

### What GPU do I need?

**Minimum Requirements:**
- **GPU:** NVIDIA GTX 1660 or better
- **VRAM:** 4GB minimum, 8GB recommended
- **Examples of compatible GPUs:**
  - ✅ RTX 4060, 4070, 4080, 4090
  - ✅ RTX 3060, 3070, 3080, 3090
  - ✅ RTX 2060, 2070, 2080
  - ✅ GTX 1660, 1660 Ti, 1660 Super
  - ❌ GTX 1050, 1050 Ti (only 2-4GB VRAM - too small)

**Check your VRAM:**
```bash
nvidia-smi
```
Look for "Memory-Usage" - you need at least 4GB total.

---

### Decision Tree: Which Mode Should I Use?

```
Do you have an NVIDIA GPU with 4GB+ VRAM?
│
├─ YES → How big is your channel?
│         │
│         ├─ Small (<100 videos) → Local GPU (FREE)
│         │                         - Transcribe at 35-40x realtime
│         │                         - Free to run
│         │                         - 30 min setup (CUDA, PyTorch)
│         │                         - Best for: Regular use
│         │
│         └─ Large (500+ videos) → Hybrid (Download local + Modal)
│                                   - Downloads locally (FREE, your home IP)
│                                   - Transcribe on Modal (70-200x realtime)
│                                   - Cost: $30-40/1000hrs
│                                   - Best for: Speed
│
└─ NO → Hybrid (Download local + Modal transcribe)
         - Download with yt-dlp on your computer
         - Transcribe on Modal cloud GPUs (parallel)
         - Only option for GPU acceleration
         - Costs ~$30-40 per 1000 hours
```

**⚠️ CRITICAL: Modal Hybrid Approach Required**

Modal **CANNOT** download YouTube videos directly because:
- YouTube blocks cloud IPs (Modal, AWS, GCP, etc.) with bot detection
- Error: "Sign in to confirm you're not a bot"

**Solution (Hybrid):**
1. Download from YOUR computer (your home IP works ✅)
2. Upload audio files to Modal
3. Modal transcribes in parallel
4. Results stream back

**This is proven to work:** 430 videos successfully transcribed using hybrid approach.

**Not sure? Start with Modal** - it's faster to set up and test. You can always switch to local GPU later.

---

## 🚀 Path A: Local GPU Setup (FREE, 30 min setup)

**Follow this if you have an NVIDIA GPU with 4GB+ VRAM**

### Step 1: Check Your System

**Python Version:**
```bash
python --version
```
Need Python 3.9 or higher. If not installed:
- Download from: https://www.python.org/downloads/
- ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation

**NVIDIA Drivers:**
```bash
nvidia-smi
```
If this works, you're good. If not, install drivers:
- Download from: https://www.nvidia.com/download/index.aspx
- Select your GPU model
- Install and restart

---

### Step 2: Install CUDA Toolkit

**What is CUDA?** It's NVIDIA's software that lets Python use your GPU for fast processing.

**Download CUDA 12.x:**
1. Go to: https://developer.nvidia.com/cuda-downloads
2. Select:
   - OS: Windows / Linux / Mac
   - Architecture: x86_64
   - Version: 11 or 12
   - Installer: exe (local)
3. Download and install (~3GB)
4. Restart computer

**Verify CUDA installed:**
```bash
nvidia-smi
```
Look for "CUDA Version: 12.x" in top right

---

### Step 3: Clone This Repository

```bash
git clone https://github.com/yourusername/yt-transcribe.git
cd yt-transcribe
```

Don't have git? Download ZIP from GitHub instead.

---

### Step 4: Install Python Dependencies

**Install PyTorch with CUDA support:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
⚠️ This downloads ~2GB, takes 5-10 minutes

**Install other dependencies:**
```bash
pip install -r requirements.txt
```

---

### Step 5: Verify GPU Works with Python

Run this test:
```bash
python -c "import torch; print('GPU Available:', torch.cuda.is_available()); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Expected output:**
```
GPU Available: True
GPU Name: NVIDIA GeForce RTX 4060
```

**If False:** Something's wrong with PyTorch CUDA installation. See troubleshooting below.

---

### Step 6: Configure Your Settings

**Create your config file:**
```bash
cp config/config.example.py config/config.py
```

**Windows (if cp doesn't work):**
```bash
copy config\config.example.py config\config.py
```

**Edit config/config.py:**
Open in any text editor and change:
```python
CHANNEL_URL = "https://www.youtube.com/@YourChannelHere"
```

**Where to find channel URL:**
1. Go to YouTube
2. Navigate to the channel you want to transcribe
3. Copy URL from address bar
4. Examples:
   - `https://www.youtube.com/@LexFridman`
   - `https://www.youtube.com/@hubermanlab`
   - `https://www.youtube.com/c/mkbhd`

---

### Step 7: Run Your First Transcription

**Start small - test with 3 videos:**
```bash
cd scripts
python run_transcriber.py
```

Press Ctrl+C after a few videos to test stopping and resuming.

**What to expect:**
```
[1/3] Scraping channel...
Channel: Lex Fridman
Found 543 videos

[2/3] Downloading batch 1 (20 videos)...
[OK] Video 1/20: Einstein Interview.mp4
[OK] Video 2/20: Quantum Physics.mp4
...

[3/3] Transcribing batch 1...
[1/20] Transcribing: Einstein Interview (video_id: abc123)
Loading faster-whisper model on CUDA...
[OK] Complete! Duration: 720s (took 18s, 40x realtime)
```

**Transcripts saved to:** `data/transcripts/{Channel Name}/`

---

### Step 8: Monitor Progress

**Check status anytime:**
```bash
cd scripts/utils
python check_status.py
```

**View transcripts:**
```bash
ls data/transcripts/
```

---

## 🌩️ Path B: Modal Cloud GPU Setup ($$$, 5 min setup)

**Follow this if you DON'T have an NVIDIA GPU or want faster processing**

### Step 1: Create Modal Account

1. Go to: https://modal.com
2. Click "Sign Up"
3. Free tier includes **$30 credit** (enough for ~600 minutes of transcription)

---

### Step 2: Install Modal

```bash
pip install modal
```

---

### Step 3: Setup Modal Authentication

```bash
modal setup
```

This will:
1. Open a browser
2. Ask you to login
3. Generate API token automatically
4. Save credentials to `~/.modal.toml`

**Expected output:**
```
Opening browser to authenticate...
Successfully authenticated!
```

---

### Step 4: Clone Repository (if not done)

```bash
git clone https://github.com/yourusername/yt-transcribe.git
cd yt-transcribe
```

---

### Step 5: Prepare Channel for Modal

**Why?** Modal's cloud IPs get blocked by YouTube. We download locally first.

**Edit `config/config.py`** and set your `CHANNEL_URL`:
```python
CHANNEL_URL = "https://www.youtube.com/@YourChannelHere"
```

**Run the preparation script** (does everything in one step):
```bash
cd scripts
python prepare_for_modal.py
```

This script will:
1. Scrape your YouTube channel to discover all videos
2. Create database with video records
3. Download all audio files to: `data/temp_audio/{Channel Name}/`
4. NO transcription - just prepares files for Modal

---

### Step 6: Run Modal Transcription

**Start small - test with 3 files:**
```bash
modal run scripts/modal_hybrid.py --max-files 3
```

**What happens:**
1. Modal creates 3 GPU containers (A10G GPUs, 24GB VRAM each)
2. Uploads audio files to each container
3. All 3 transcribe in parallel
4. Results stream back to your computer
5. Modal auto-cleans up containers

**Expected output:**
```
======================================================================
Hybrid Modal Transcriber
Downloads: Local | Transcription: Modal GPUs
======================================================================

Found 103 audio files
Processing 3 files with Modal GPUs...

[abc123] Loading Whisper model...
[def456] Loading Whisper model...
[ghi789] Loading Whisper model...
[abc123] Transcribing...
[abc123] [OK] Complete! Duration: 720.0s

======================================================================
SUMMARY
======================================================================
Completed:        3/3
Total duration:   35.2 minutes
Processing time:  45.3 seconds
Realtime factor:  46.6x
Output directory: data/modal_transcripts
======================================================================
```

---

### Step 7: Check Costs

Visit: https://modal.com/home

- See real-time GPU usage
- Track costs per run
- Set budget alerts
- Monitor free tier credits

**Cost estimate:** ~$0.03 per hour of content transcribed

---

## 📊 Which Option Should I Choose?

| Factor | Local GPU | Modal Cloud |
|--------|-----------|-------------|
| **Setup Time** | 30 minutes | 5 minutes |
| **Cost** | Free (electricity) | ~$30-40 per 1000 hours |
| **Speed** | 35-40x realtime | 70-200x realtime (parallel) |
| **Processing 100 hours** | ~2.5 hours | ~3-5 minutes |
| **Processing 1000 hours** | ~25 hours | ~15-20 minutes |
| **Best For** | Regular use, large projects | One-time projects, urgent needs |
| **Hardware Needed** | NVIDIA GPU (4GB+ VRAM) | Any computer |

**My recommendation:**
- Have NVIDIA GPU? → Use Local GPU (free!)
- No NVIDIA GPU? → Use Modal
- Need it fast? → Use Modal (even if you have GPU)

---

## ❓ Troubleshooting

### "nvidia-smi: command not found"

**Problem:** NVIDIA drivers not installed or not in PATH

**Solution:**
1. Download drivers: https://www.nvidia.com/download/index.aspx
2. Install and restart
3. Run `nvidia-smi` again

---

### "GPU Available: False" (PyTorch test)

**Problem:** PyTorch installed without CUDA support

**Solution:**
```bash
# Uninstall wrong PyTorch
pip uninstall torch torchvision torchaudio

# Reinstall with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

### "Library cublas64_12.dll is not found"

**Problem:** CUDA toolkit not installed or not in PATH

**Solution:**
1. Install CUDA: https://developer.nvidia.com/cuda-downloads
2. Restart computer
3. Verify: `nvidia-smi` shows "CUDA Version: 12.x"

---

### "Out of memory" errors

**Problem:** GPU doesn't have enough VRAM for model size

**Solution:**
Edit `config/config.py`:
```python
MODEL_SIZE = "tiny"  # Change from "base" to "tiny"
```

**Model sizes vs VRAM:**
- `tiny`: 1GB VRAM
- `base`: 1-2GB VRAM
- `small`: 2-3GB VRAM
- `medium`: 5GB VRAM
- `large`: 10GB VRAM

---

### Modal: "Sign in to confirm you're not a bot"

**Problem:** Trying to use `modal_transcribe.py` (full cloud)

**Solution:** Use `modal_hybrid.py` instead (download locally first):
```bash
# Step 1: Prepare channel (scrape + download)
cd scripts
python prepare_for_modal.py

# Step 2: Transcribe on Modal
modal run scripts/modal_hybrid.py --max-files 10
```

---

## 🎓 Next Steps

Once you've successfully run your first transcription:

1. **Read the full documentation:**
   - `docs/INSTALLATION.md` - Detailed setup
   - `docs/MODAL_QUICKSTART.md` - Modal guide
   - `README.md` - Features and performance

2. **Optimize settings:**
   - Try different model sizes
   - Adjust batch sizes
   - Configure cleanup settings

3. **Process your full channel:**
   ```bash
   cd scripts
   python run_transcriber.py
   # Let it run overnight for large channels
   ```

4. **Explore utilities:**
   ```bash
   cd scripts/utils
   python check_status.py      # Check progress
   python find_missing.py      # Find gaps
   python verify_transcripts.py # Verify uniqueness
   ```

---

## 🆘 Still Stuck?

1. **Check the FAQ:** `docs/TROUBLESHOOTING.md`
2. **Search existing issues:** https://github.com/yourusername/yt-transcribe/issues
3. **Create new issue:** Use bug report template

**When creating an issue, include:**
- Your OS (Windows/Mac/Linux)
- Python version (`python --version`)
- GPU model and VRAM
- Complete error message
- What you've tried so far

---

**Welcome to the community! Happy transcribing! 🎉**
