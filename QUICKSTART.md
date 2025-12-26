# Quick Start Guide - TL;DR

**For people who just want to get started FAST.**

---

## 📝 Step 0: Configure

Edit `config/config.py`:
```python
CHANNEL_URL = "https://www.youtube.com/@YourChannelHere"
```

That's the ONLY thing you need to edit.

---

## 🚀 Choose Your Path

### Path A: Local GPU (Free, Slower)

**Requirements:** NVIDIA GPU with 4GB+ VRAM

**One command:**
```bash
python scripts/run_transcriber.py
```

That's it. It downloads + transcribes everything on your GPU.

**Speed:** 35-40x realtime (60 min video → 2 min transcription)

---

### Path B: Modal Cloud GPU (Paid, FAST)

**Requirements:** Any computer + Modal account ($30 free credit)

**Two commands:**
```bash
# 1. Download audio locally (scrapes channel, creates DB, downloads)
python scripts/prepare_for_modal.py

# 2. Transcribe on Modal GPUs (parallel, super fast)
modal run scripts/modal_hybrid.py --max-files 100
```

**Speed:** 70-200x realtime with parallel processing

**Cost:** ~$30-40 per 1000 hours of content

---

## ❓ Which Should I Use?

| You have... | Use... | Why |
|-------------|--------|-----|
| NVIDIA GPU (4GB+) + small channel (<100 videos) | **Local GPU** | Free! |
| NVIDIA GPU (4GB+) + large channel (500+ videos) | **Modal Cloud** | Faster |
| No NVIDIA GPU | **Modal Cloud** | Only option |
| Deadline/urgent | **Modal Cloud** | 10-50x faster than local |

---

## 📊 What Gets Created

After running:
```
data/
├── temp_audio/           # Downloaded audio files
│   └── {Channel Name}/   # One folder per channel
├── transcripts/          # Final transcripts
│   └── {Channel Name}/   # One folder per channel
│       ├── video1.txt
│       ├── video2.txt
│       └── ...
└── transcription_progress.db  # Tracks progress (resumable)
```

---

## ⚠️ Common Mistakes

### ❌ DON'T run `download_only.py` for a new channel
It requires the database to already exist (for resuming interrupted downloads).

### ✅ DO run `prepare_for_modal.py` for a new channel
It scrapes the channel, creates database, AND downloads.

### ❌ DON'T try to run Modal without downloading first
YouTube blocks cloud IPs. Always download locally first.

### ✅ DO edit `config.py` before running anything
All scripts read from this ONE config file.

---

## 🔄 Resuming After Interruption

**If you stopped/crashed mid-way:**

**Local GPU:**
```bash
python scripts/run_transcriber.py
# It will resume from where it stopped
```

**Modal Cloud:**
```bash
# If interrupted during download:
python scripts/prepare_for_modal.py

# If interrupted during transcription:
modal run scripts/modal_hybrid.py --max-files 100
```

Everything is resumable! The database tracks what's done.

---

## 🆘 Help!

**GPU not working?**
```bash
nvidia-smi  # Should show your GPU
```

**Modal authentication?**
```bash
modal setup  # Follow browser prompts
```

**Check progress:**
```bash
python scripts/utils/check_status.py
```

**Full docs:** See `docs/GETTING_STARTED.md`

---

**That's it! Now go transcribe something! 🎉**
