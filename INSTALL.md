# Installation Guide

Complete installation instructions for the YouTube Channel Transcriber.

---

## Quick Install (Recommended)

### Option 1: Interactive Setup Wizard

**Windows:**
```bash
# Double-click setup.bat
# OR in terminal:
python setup.py
```

**macOS/Linux:**
```bash
python3 setup.py
```

The wizard will:
- ✅ Check Python version
- ✅ Install dependencies
- ✅ Create config file
- ✅ Test GPU/Modal setup
- ✅ Guide you through everything

### Option 2: Quick Setup (Advanced Users)

```bash
# Install everything (local + Modal)
python quick-setup.py

# OR install specific components:
python quick-setup.py --local   # Local GPU only
python quick-setup.py --modal   # Modal Cloud only
```

---

## Manual Installation

If you prefer to set up manually or the wizard doesn't work:

### Step 1: Prerequisites

**Required:**
- Python 3.9 or higher
- pip (Python package manager)

**For Local GPU Transcription:**
- NVIDIA GPU with CUDA support (RTX 3060+ recommended)
- 8GB+ VRAM for base model
- CUDA 12.x installed

**For Modal Cloud Transcription:**
- Modal account (free $30 credits)
- Internet connection

### Step 2: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/youtube-channel-transcriber.git
cd youtube-channel-transcriber
```

Or download ZIP from GitHub and extract.

### Step 3: Install Dependencies

**For Local GPU:**
```bash
pip install -r requirements.txt
```

**For Modal Cloud:**
```bash
pip install -r requirements.txt
pip install -r requirements-modal.txt
```

**For Both:**
```bash
pip install -r requirements.txt
pip install -r requirements-modal.txt
```

### Step 4: Create Configuration

```bash
# Copy example config
cp config/config.example.py config/config.py

# Edit with your settings
# Windows:
notepad config/config.py

# macOS/Linux:
nano config/config.py
# or
vim config/config.py
```

**Required Changes:**
```python
# Set your YouTube channel URL
CHANNEL_URL = "https://www.youtube.com/@your-channel"

# Choose model size (tiny/base/small/medium/large)
MODEL_SIZE = "base"  # Recommended for most users

# Delete audio after transcription? (saves disk space)
DELETE_AUDIO_AFTER_TRANSCRIPTION = True
```

### Step 5: Create Data Directories

```bash
mkdir -p data/temp_audio
mkdir -p data/transcripts
```

**Windows:**
```cmd
mkdir data\temp_audio
mkdir data\transcripts
```

### Step 6: Setup Modal (if using cloud)

```bash
# Install Modal
pip install modal

# Authenticate (opens browser)
modal setup
```

Follow the prompts to:
1. Create free account or login
2. Get API token
3. Verify connection

### Step 7: Verify Installation

**Test Local GPU:**
```bash
python src/utils/check_gpu.py
```

Expected output:
```
✓ CUDA detected
✓ GPU: NVIDIA RTX 4060
✓ VRAM: 8.0 GB
```

**Test Modal:**
```bash
modal run scripts/modal_hybrid.py --help
```

Expected: Help text displayed

---

## Troubleshooting

### Python Version Issues

**Error:** "Python 3.9 or higher is required"

**Solution:**
```bash
# Check version
python --version

# If too old, download latest from:
# https://www.python.org/downloads/
```

### GPU Not Detected

**Error:** "No CUDA-capable GPU found"

**Solutions:**
1. **Install CUDA Toolkit 12.x:**
   - Download: https://developer.nvidia.com/cuda-downloads
   - Windows: Run installer, restart
   - Linux: Follow NVIDIA instructions

2. **Update GPU drivers:**
   - NVIDIA: https://www.nvidia.com/download/index.aspx
   - Download latest for your GPU

3. **Verify installation:**
   ```bash
   nvidia-smi
   ```
   Should show GPU info

4. **Reinstall PyTorch with CUDA:**
   ```bash
   pip uninstall torch
   pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```

### Modal Authentication Failed

**Error:** "Modal authentication failed"

**Solutions:**
1. **Run setup again:**
   ```bash
   modal setup
   ```

2. **Check firewall:**
   - Ensure browser can open modal.com
   - Allow terminal to access network

3. **Manual token:**
   - Get token from: https://modal.com/settings/tokens
   - Add to `~/.modal.toml`

### Dependency Installation Failed

**Error:** "Failed to install requirements"

**Solutions:**
1. **Upgrade pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install one by one:**
   ```bash
   pip install yt-dlp
   pip install faster-whisper
   pip install torch
   # ... etc
   ```

3. **Use virtual environment:**
   ```bash
   python -m venv venv

   # Windows:
   venv\Scripts\activate

   # macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

### Config File Not Found

**Error:** "config.py not found"

**Solution:**
```bash
# Make sure you're in project root
cd path/to/youtube-channel-transcriber

# Copy example config
cp config/config.example.py config/config.py

# Edit it
notepad config/config.py  # Windows
nano config/config.py     # macOS/Linux
```

### Permission Denied Errors

**Windows:**
- Run terminal as Administrator
- Or: Right-click setup.bat → Run as Administrator

**macOS/Linux:**
```bash
chmod +x setup.py quick-setup.py
chmod +x scripts/*.py
chmod +x scripts/utils/*.py
```

---

## System Requirements

### Minimum Requirements

**For Local GPU:**
- Python 3.9+
- NVIDIA GPU with 6GB+ VRAM (GTX 1660, RTX 3060, etc.)
- CUDA 12.x
- 20GB free disk space
- Windows 10/11, Ubuntu 20.04+, or macOS 12+

**For Modal Cloud:**
- Python 3.9+
- Internet connection
- Modal account
- 10GB free disk space (for audio downloads)

### Recommended Specifications

**For Local GPU:**
- Python 3.10+
- NVIDIA RTX 3060+ (8GB+ VRAM)
- CUDA 12.6
- 100GB+ free disk space
- 16GB RAM

**For Modal Cloud:**
- Python 3.10+
- Fast internet (for large channel downloads)
- 50GB+ free disk space

---

## Installation Verification Checklist

Use this to verify your installation:

- [ ] Python 3.9+ installed (`python --version`)
- [ ] pip available (`pip --version`)
- [ ] Dependencies installed (`pip list | grep whisper`)
- [ ] Config file created (`ls config/config.py`)
- [ ] Channel URL set in config
- [ ] Data directories exist (`ls data/`)
- [ ] GPU detected (local) OR Modal authenticated (cloud)
- [ ] Can run help command: `python scripts/run_transcriber.py --help`

---

## Next Steps

Once installation is complete:

**For Local GPU:**
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run: `python scripts/run_transcriber.py`

**For Modal Cloud:**
1. Read [docs/MODAL_QUICKSTART.md](docs/MODAL_QUICKSTART.md)
2. Run: `python scripts/prepare_for_modal.py`
3. Run: `modal run scripts/modal_hybrid.py --max-files 3`

---

## Getting Help

**Documentation:**
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) - Detailed guide
- [docs/MODAL_QUICKSTART.md](docs/MODAL_QUICKSTART.md) - Modal guide
- [docs/MULTI_CHANNEL_GUIDE.md](docs/MULTI_CHANNEL_GUIDE.md) - Managing channels
- [CHANGELOG.md](CHANGELOG.md) - Version history

**Community:**
- Open an issue: [GitHub Issues](https://github.com/YOUR_USERNAME/youtube-channel-transcriber/issues)
- Check existing issues for solutions
- Read the FAQ in README.md

**Common Issues:**
- GPU not detected → Check CUDA installation
- Modal auth failed → Run `modal setup` again
- Slow transcription → Check model size in config
- Out of memory → Use smaller model or Modal Cloud

---

## Uninstallation

To remove the transcriber:

```bash
# 1. Delete project folder
rm -rf youtube-channel-transcriber

# 2. Uninstall dependencies (optional)
pip uninstall -r requirements.txt
pip uninstall -r requirements-modal.txt

# 3. Remove Modal authentication (optional)
rm ~/.modal.toml
```

**Note:** Your downloaded videos and transcripts are in the `data/` folder. Back them up before deleting if needed.

---

## Alternative Installation Methods

### Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Use normally
python setup.py
```

### Using Conda

```bash
# Create conda environment
conda create -n transcriber python=3.10

# Activate
conda activate transcriber

# Install dependencies
pip install -r requirements.txt

# Use normally
python setup.py
```

### Docker (Advanced)

A Dockerfile is not currently provided, but you can create one:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scripts/run_transcriber.py"]
```

---

**Installation complete? Start transcribing!** 🎉
