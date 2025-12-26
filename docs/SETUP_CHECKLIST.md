# Setup Checklist

Use this checklist to track your setup progress.

---

## 🎯 Choose Your Path

- [ ] **Path A: Local GPU** (I have NVIDIA GPU with 4GB+ VRAM)
- [ ] **Path B: Modal Cloud** (I don't have NVIDIA GPU or want faster processing)

---

## Path A: Local GPU Setup

### Prerequisites
- [ ] NVIDIA GPU with 4GB+ VRAM
- [ ] Python 3.9+ installed (`python --version`)
- [ ] Git installed (or download ZIP)

### NVIDIA Setup
- [ ] NVIDIA drivers installed (`nvidia-smi` works)
- [ ] CUDA 12.x toolkit installed (shows in `nvidia-smi` output)
- [ ] Verified CUDA version: __________

### Python Environment
- [ ] Cloned/downloaded repository
- [ ] Installed PyTorch with CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu121`
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Verified GPU available in Python:
  ```bash
  python -c "import torch; print(torch.cuda.is_available())"
  ```
  Result: ☐ True ☐ False

### Configuration
- [ ] Created config file: `cp config/config.example.py config/config.py`
- [ ] Set channel URL in `config/config.py`
- [ ] Channel URL: ___________________________________

### First Run
- [ ] Ran test transcription: `cd scripts && python run_transcriber.py`
- [ ] Verified transcripts created in `data/transcripts/`
- [ ] Tested stop/resume (Ctrl+C and restart)

### Success Criteria
- [ ] GPU detected and used for transcription
- [ ] Transcription speed: ~35-40x realtime
- [ ] No CUDA errors
- [ ] Transcripts readable and accurate

---

## Path B: Modal Cloud Setup

### Prerequisites
- [ ] Python 3.9+ installed (`python --version`)
- [ ] Git installed (or download ZIP)
- [ ] Credit card for Modal (free $30 credit included)

### Modal Account
- [ ] Created account at https://modal.com
- [ ] Installed Modal: `pip install modal`
- [ ] Authenticated: `modal setup` (browser opened and logged in)
- [ ] Verified auth: `modal token` shows token

### Repository Setup
- [ ] Cloned/downloaded repository
- [ ] Installed yt-dlp: `pip install -r requirements-modal.txt`

### Configuration
- [ ] Created config file: `cp config/config.example.py config/config.py`
- [ ] Set channel URL in `config/config.py`
- [ ] Channel URL: ___________________________________

### Download Audio
- [ ] Downloaded audio locally: `cd scripts && python download_only.py`
- [ ] Verified audio files in `data/temp_audio/{Channel Name}/`
- [ ] Number of audio files: __________

### First Modal Run
- [ ] Ran test: `modal run scripts/modal_hybrid.py --max-files 3`
- [ ] Verified 3 GPU containers spawned
- [ ] Verified transcripts in `data/modal_transcripts/`
- [ ] Checked costs at https://modal.com/home

### Success Criteria
- [ ] Modal deployed successfully (no errors)
- [ ] All 3 test files transcribed
- [ ] Transcription speed: ~70-200x realtime
- [ ] Costs as expected (~$0.03 per hour of content)

---

## Common Issues Checklist

### GPU Not Detected (Local)
- [ ] Ran `nvidia-smi` - works?
- [ ] CUDA version shows in `nvidia-smi`?
- [ ] PyTorch installed with CUDA (`--index-url` flag)?
- [ ] Tested: `python -c "import torch; print(torch.cuda.is_available())"`

### Out of Memory (Local)
- [ ] Checked VRAM: `nvidia-smi` shows Memory-Usage
- [ ] Reduced model size in `config/config.py` to `"tiny"`
- [ ] Closed other GPU applications

### YouTube Download Errors (Both)
- [ ] Using latest yt-dlp: `pip install --upgrade yt-dlp`
- [ ] Channel URL correct format?
- [ ] YouTube not blocking your IP?

### Modal Errors
- [ ] Used hybrid approach (download local first)?
- [ ] Modal authenticated: `modal token` shows valid token?
- [ ] Free credits remaining?

---

## Post-Setup Checklist

### Understanding Your System
- [ ] Know where transcripts are saved: `data/transcripts/{Channel Name}/`
- [ ] Know how to check progress: `scripts/utils/check_status.py`
- [ ] Know how to resume: Just run same command again
- [ ] Know how to stop safely: Ctrl+C

### Performance Verification
- [ ] Noted transcription speed: ________x realtime
- [ ] Estimated time for full channel: __________
- [ ] Verified transcript quality (checked 2-3 files)

### Next Steps
- [ ] Read `docs/MODAL_QUICKSTART.md` (if using Modal)
- [ ] Read `README.md` for advanced features
- [ ] Explored utility scripts in `scripts/utils/`
- [ ] Joined community / starred repo

---

## Troubleshooting Resources

If stuck, check in this order:

1. [ ] Re-read relevant section in `docs/GETTING_STARTED.md`
2. [ ] Check `docs/TROUBLESHOOTING.md` for common issues
3. [ ] Search existing GitHub issues
4. [ ] Create new issue with bug report template

---

## My Setup Summary

**Date Completed:** _______________

**Path Chosen:** ☐ Local GPU ☐ Modal Cloud

**Hardware:**
- GPU: ___________________________
- VRAM: __________ GB
- CPU: ___________________________
- RAM: __________ GB

**Performance:**
- Transcription speed: __________ x realtime
- Model size: __________
- Typical video length: __________ minutes
- Time per video: __________ seconds

**Notes:**
```
(Any custom settings, issues encountered, solutions found)






```

---

**Status:** ☐ Setup Complete ☐ Ready for Production ☐ Need Help

**Setup Duration:** __________ minutes
