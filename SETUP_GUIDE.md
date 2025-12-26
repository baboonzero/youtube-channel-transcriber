# Setup System Guide

This project includes multiple setup options to make installation easy for all users.

---

## Setup Options Overview

| Method | Best For | Command | Features |
|--------|----------|---------|----------|
| **Interactive Wizard** | New users | `python setup.py` | Full guidance, GPU check, Modal setup |
| **Windows Launcher** | Windows users | Double-click `setup.bat` | Easy double-click install |
| **Quick Setup** | Advanced users | `python quick-setup.py` | Fast minimal setup |
| **Manual Install** | Power users | See `INSTALL.md` | Full control |

---

## 1. Interactive Wizard (Recommended for New Users)

### What It Does
- ✅ Checks Python version and pip
- ✅ Asks which installation type (Local/Modal/Both)
- ✅ Installs correct dependencies
- ✅ Tests GPU availability
- ✅ Helps setup Modal authentication
- ✅ Creates config file interactively
- ✅ Creates data directories
- ✅ Shows personalized next steps

### How to Use

**Windows:**
```cmd
python setup.py
```

**macOS/Linux:**
```bash
python3 setup.py
```

### Example Session
```
======================================================================
         YouTube Channel Transcriber - Setup Wizard
======================================================================

Checking System Requirements
Python version: 3.10.11
✓ Python version OK
✓ pip is available

Choose Installation Type
How do you want to transcribe videos?

1. Local GPU (RTX 3060+, 8GB+ VRAM recommended)
2. Modal Cloud (A10G GPUs)
3. Both (recommended for flexibility)

Choice [3]: 3

Installing Dependencies
Installing from requirements.txt...
✓ Installed dependencies from requirements.txt
Installing from requirements-modal.txt...
✓ Installed dependencies from requirements-modal.txt

Checking GPU Availability
✓ CUDA detected
✓ GPU: NVIDIA RTX 4060
✓ VRAM: 8.0 GB

Setting Up Modal
✓ Modal is installed
Checking Modal authentication...
Run 'modal setup' now? (y/n) [y]: y
✓ Modal authentication complete

Creating Configuration File
Let's configure your YouTube channel:

YouTube Channel URL [https://www.youtube.com/@username]: https://www.youtube.com/@mychannel

Model size [base]: base
Delete audio files after transcription? (saves disk space) (y/n) [y]: y
✓ Created config file: config/config.py

Creating Data Directories
✓ Created: data/
✓ Created: data/temp_audio/
✓ Created: data/transcripts/

Setup Complete! 🎉
...
```

---

## 2. Windows Launcher (Easiest for Windows)

### What It Does
- Checks if Python is installed
- Runs the interactive wizard
- Pauses at end so you can read results

### How to Use
1. Navigate to project folder
2. Double-click `setup.bat`
3. Follow the wizard prompts

### Requirements
- Python must be installed and in PATH
- If Python not found, it will show download instructions

---

## 3. Quick Setup (For Advanced Users)

### What It Does
- Minimal setup with sensible defaults
- No interactive prompts (unless config exists)
- Fast installation

### How to Use

**Install everything (default):**
```bash
python quick-setup.py
```

**Install local GPU only:**
```bash
python quick-setup.py --local
```

**Install Modal Cloud only:**
```bash
python quick-setup.py --modal
```

**Skip dependencies (already installed):**
```bash
python quick-setup.py --no-deps
```

**Force overwrite config:**
```bash
python quick-setup.py --force
```

### Example Output
```
======================================================================
YouTube Channel Transcriber - Quick Setup
======================================================================

Installing dependencies (both)...
  Installing from requirements.txt...
  Installing from requirements-modal.txt...
  ✓ Dependencies installed
Creating config file...
  ✓ Created: config/config.py

  Edit config/config.py to set your YouTube channel URL
  Example: CHANNEL_URL = "https://www.youtube.com/@username"

Creating data directories...
  ✓ Directories created

======================================================================
Setup Complete!
======================================================================

Next steps:

  Local GPU:
    python scripts/run_transcriber.py

  Modal Cloud:
    1. modal setup                           # Authenticate
    2. python scripts/prepare_for_modal.py   # Download audio
    3. modal run scripts/modal_hybrid.py --max-files 3  # Test

Documentation:
  • QUICKSTART.md - Quick start guide
  • docs/GETTING_STARTED.md - Full setup guide
```

---

## 4. Manual Installation

### When to Use
- Setup scripts don't work
- You want full control
- Corporate environment with restrictions
- Using containers or virtual environments

### How to Use
See complete instructions in **[INSTALL.md](INSTALL.md)**

---

## Comparison Table

| Feature | Interactive Wizard | Windows Launcher | Quick Setup | Manual |
|---------|-------------------|------------------|-------------|--------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Speed** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Customization** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **GPU Testing** | ✅ | ✅ | ❌ | Manual |
| **Modal Setup** | ✅ | ✅ | ❌ | Manual |
| **Validation** | ✅ | ✅ | ❌ | Manual |
| **Platform** | All | Windows only | All | All |

---

## Common Issues

### "Python not found" Error

**Windows (setup.bat):**
- Install Python from https://python.org
- **Important:** Check "Add Python to PATH" during installation
- Restart terminal/command prompt after installing

**macOS/Linux:**
```bash
# Use python3 instead of python
python3 setup.py
```

### "Permission denied" Error

**Windows:**
- Right-click `setup.bat` → "Run as administrator"

**macOS/Linux:**
```bash
chmod +x setup.py quick-setup.py
python3 setup.py
```

### Setup Script Won't Run

**Try Quick Setup instead:**
```bash
python quick-setup.py --no-deps
# Then manually install dependencies
pip install -r requirements.txt
```

**Or Manual Installation:**
See [INSTALL.md](INSTALL.md)

---

## After Setup

Once setup is complete, choose your workflow:

### Local GPU Workflow
```bash
python scripts/run_transcriber.py
```
See: [QUICKSTART.md](QUICKSTART.md)

### Modal Cloud Workflow
```bash
# Step 1: Download audio
python scripts/prepare_for_modal.py

# Step 2: Transcribe on cloud
modal run scripts/modal_hybrid.py --max-files 3
```
See: [docs/MODAL_QUICKSTART.md](docs/MODAL_QUICKSTART.md)

---

## Need Help?

1. **Check documentation:**
   - [INSTALL.md](INSTALL.md) - Detailed installation guide
   - [QUICKSTART.md](QUICKSTART.md) - Quick start guide
   - [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) - Full guide

2. **Common issues:**
   - See "Troubleshooting" section in [INSTALL.md](INSTALL.md)

3. **Still stuck?**
   - Open an issue on GitHub
   - Include error message and what you tried

---

**Ready to transcribe!** 🎉

Choose any setup method above and get started in minutes!
