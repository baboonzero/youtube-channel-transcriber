# Changelog

All notable changes and improvements to the YouTube Channel Bulk Transcriber.

## [3.1.0] - 2025-12-26 - Modal Workflow & File Naming Fixes

### New Features - Modal Hybrid Workflow
- ✅ **Created `scripts/prepare_for_modal.py`** - One-command Modal preparation script
  - Scrapes YouTube channel to discover videos
  - Creates/updates database with video records
  - Downloads ALL audio files (no transcription)
  - Replaces broken workflow that required manually killing scripts
  - Fully resumable if interrupted

### Bug Fixes - Modal Transcription
- ✅ **Fixed file naming:** Modal now uses `{Title}_{VideoID}.txt` format (matches local transcription)
  - Before: Cryptic filenames like `abc123.txt`
  - After: Readable names like `Playbook - The Rule of 3 and 10_abc123.txt`
- ✅ **Fixed folder structure:** Transcripts now save to `data/transcripts/{Channel}/` (matches local)
  - Before: All transcripts mixed in `data/modal_transcripts/`
  - After: Channel-specific folders like local transcription
- ✅ **Fixed database sync:** Modal now updates database with transcript paths and status
- ✅ **Fixed channel detection:** Auto-detects channel from config.py using keyword matching
- ✅ **Fixed script paths:** All scripts work from any directory (added `os.chdir(project_root)`)
- ✅ **Fixed multi-channel support:** Scripts now filter by current channel
  - `get_pending_videos()` and `get_stats()` now accept `channel_filter` parameter
  - `prepare_for_modal.py` only processes videos from current channel in config
  - Multiple channels can coexist in database without conflicts
  - Created `scripts/utils/reset_channel.py` for managing channel data

### Documentation Updates
- ✅ **Rewrote `docs/MODAL_QUICKSTART.md`** - Completely updated with correct workflow
- ✅ **Updated `README.md`** - Fixed Modal hybrid workflow section
- ✅ **Updated `docs/GETTING_STARTED.md`** - Fixed Step 5 to use prepare_for_modal.py
- ✅ **Created `QUICKSTART.md`** - TL;DR guide for impatient users
- ✅ **Created `WORKFLOW.md`** - Configuration workflow guide
- ✅ **Created `docs/FIXES_APPLIED.md`** - Detailed explanation of workflow fixes
- ✅ **Created `docs/MODAL_NAMING_FIX.md`** - File naming and organization fix details
- ✅ **Created `docs/MULTI_CHANNEL_GUIDE.md`** - Guide for managing multiple YouTube channels

### Breaking Changes
- **Modal workflow:** Must use `prepare_for_modal.py` for new channels (not `download_only.py`)
  - `download_only.py` now only for resuming interrupted downloads
  - `prepare_for_modal.py` handles: scrape + create DB + download
- **Modal output:** Transcripts save to `data/transcripts/{Channel}/` instead of `data/modal_transcripts/`
  - Matches local transcription structure
  - Organized by channel automatically

### Migration Guide
**For existing Modal users:**
1. Old transcripts remain in `data/modal_transcripts/` (won't be moved automatically)
2. New transcripts will go to `data/transcripts/{Channel}/`
3. For new channels: Use `python scripts/prepare_for_modal.py`
4. For resuming: Use `python scripts/download_only.py` (still works)

**New Modal workflow:**
```bash
# 1. Edit config
vim config/config.py  # Set CHANNEL_URL

# 2. Prepare channel (NEW - one command!)
python scripts/prepare_for_modal.py

# 3. Transcribe on Modal
modal run scripts/modal_hybrid.py --max-files 100
```

---

## [3.0.0] - 2025-12-26 - GitHub Release

### Major Refactor - Professional Repository Structure

**Organization & Cleanup:**
- ✅ Reorganized folder structure (14 root scripts → 0 Python files in root)
- ✅ Consolidated data directories (3 locations → 1 central `data/`)
- ✅ Moved all scripts to proper locations (`scripts/` and `scripts/utils/`)
- ✅ Created comprehensive GitHub templates (bug reports, feature requests, PR template)
- ✅ Deleted 17 duplicate/temporary files (50% reduction in clutter)

**New Documentation:**
- ✅ Created `LICENSE` (MIT)
- ✅ Created `requirements.txt` and `requirements-modal.txt`
- ✅ Created `config/config.example.py` template
- ✅ Created `.github/` templates for issues and PRs
- ✅ Created `docs/INSTALLATION.md`
- ✅ Updated `.gitignore` with comprehensive rules
- ✅ Documented Modal comparison and architectural decisions

**Breaking Changes:**
- **Database path:** `scripts/data/transcription_progress.db` → `data/transcription_progress.db`
- **Transcripts path:** `scripts/data/transcripts/` → `data/transcripts/`
- **Modal transcripts:** `modal_transcripts/` → `data/modal_transcripts/` (later changed to `data/transcripts/{Channel}/` in v3.1.0)
- **Config:** Now requires copying `config.example.py` → `config.py`
- **Script locations:** All Python scripts moved from root to `scripts/` or `scripts/utils/`

**New Folder Structure:**
```
YT Transcribe/
├── scripts/              # Main execution scripts
│   ├── modal_hybrid.py
│   ├── download_only.py
│   ├── run_transcriber.py
│   └── utils/            # Utility scripts
│       ├── verify_transcripts.py
│       ├── check_status.py
│       └── ...
├── data/                 # Centralized data directory
│   ├── transcripts/
│   ├── modal_transcripts/
│   ├── temp_audio/
│   ├── transcription.log
│   └── transcription_progress.db
├── docs/                 # Documentation
├── config/               # Configuration
├── src/                  # Source code
├── .github/              # GitHub templates
├── README.md
├── CHANGELOG.md
├── LICENSE
└── requirements.txt
```

**Modal Cloud Integration:**
- ✅ Deleted `modal_transcribe.py` (full cloud approach doesn't work with YouTube bot detection)
- ✅ Kept `modal_hybrid.py` as proven solution (430 videos transcribed successfully)
- ✅ Documented why hybrid approach is required (local downloads, cloud GPUs)
- ✅ Documented why faster-whisper doesn't work on Modal (cuDNN incompatibility)

**Migration Guide:**
1. Backup your `config/config.py`
2. Pull latest changes
3. Copy `config/config.example.py` → `config/config.py`
4. Restore your channel URL in `config/config.py`
5. All data automatically migrated to `data/` directory

**Data Integrity:** ✅ 100% preserved (1,044 transcripts, 430 archived audio files, all database records intact)

---

## [2.0.0] - 2025-12-25 - Production System

### ✅ Implemented & Deployed

#### Performance Upgrades

**Migration to faster-whisper (December 2025)**
- Replaced openai-whisper with faster-whisper (CTranslate2 implementation)
- **Performance gain: 43% faster** (23x → 35-40x realtime)
- Same accuracy, lower memory usage
- Better batching and optimization

**CUDA 12 Support**
- Upgraded from CUDA 11.8 to CUDA 12.6
- Required for faster-whisper GPU acceleration
- Automatic PATH injection in run_transcriber.py
- Verified working on RTX 4060 Laptop GPU (8GB VRAM)

#### Core Features

**Channel-Specific Organization**
- Automatic folder structure: `data/{temp_audio|transcripts}/{Channel Name}/`
- Clean separation of multiple channels
- Example: "My First Million" gets its own folders

**Voice Activity Detection (VAD)**
- Automatically skip silence during transcription
- Typical time savings: 15-30% per video
- No accuracy loss
- Built into faster-whisper

**Resumable Processing**
- SQLite database tracks all video states
- Status progression: pending → downloaded → completed
- Safe interruption with Ctrl+C
- Automatic resume from last checkpoint

**Parallel Downloads**
- 10 concurrent video downloads (configurable)
- Sequential GPU transcription (1 worker)
- Batch size: 20 videos per cycle
- Optimal for bandwidth + GPU utilization

**Automatic Cleanup**
- Configurable audio file deletion after transcription
- Saves significant disk space on large channels
- `DELETE_AUDIO_AFTER_TRANSCRIPTION = True` (default)

#### Bug Fixes

**UTF-8 Encoding Fix**
- Fixed Unicode character errors in Windows console logs
- Added `encoding='utf-8'` to logging handlers
- Reconfigured stdout/stderr for UTF-8 support
- Clean logs with arrow symbols (→) working correctly

**Database Path Resolution**
- Fixed relative path issues with audio files
- Proper path handling from scripts/ directory
- Status and audio_path now update together

**Thread Safety**
- SQLite locking prevents concurrent write issues
- Parallel downloads work without database corruption
- Proper error handling and recovery

#### Configuration System

**Centralized Config (config/config.py)**
```python
# All settings in one place
CHANNEL_URL = "https://www.youtube.com/@YourChannel"
MODEL_SIZE = "base"
DOWNLOAD_WORKERS = 10
TRANSCRIBE_WORKERS = 1  # Must stay at 1
BATCH_SIZE = 20
DEVICE = "cuda"
DELETE_AUDIO_AFTER_TRANSCRIPTION = True
```

**Model Recommendations by VRAM:**
- 4GB: tiny or base
- 6GB: small
- 8GB: small or medium
- 12GB: medium or large
- 16GB+: large

#### Production Readiness

**Error Handling**
- Retry logic for failed downloads
- Skip and log failed transcriptions
- Continue processing on errors
- Detailed logging to data/transcription.log

**Progress Monitoring**
- Real-time batch progress (X/Y batches)
- Video completion tracking
- Duration calculations
- Status reporting (completed/pending/errors)

### 📊 Verified Performance Metrics

**Hardware Tested:** NVIDIA RTX 4060 Laptop GPU (8GB VRAM)

**Model: base**
- Speed: 35-40x realtime
- Example: 60-minute video → 90-120 seconds
- Throughput: ~50-60 videos/hour (for 12-min videos)

**Real-World Test:**
- Channel: My First Million
- Videos: 1,054 total
- Content: Mix of 12-60 minute episodes
- Time: ~10-12 hours for 500+ hours of content
- Success rate: 100% download, 98%+ transcription

### 🏗️ Architecture Decisions

**Why TRANSCRIBE_WORKERS = 1?**
- Whisper models are not thread-safe
- SQLite can't handle concurrent writes from multiple processes
- GPU memory conflicts with multiple model instances
- For parallel transcription, need distributed architecture (future: Modal/cloud)

**Why faster-whisper over openai-whisper?**
- 4x speedup with zero accuracy loss
- CTranslate2 optimization
- Better memory efficiency
- Active maintenance and updates
- Required CUDA 12 (worth the upgrade)

**Why Batch Processing?**
- Balance between disk usage and efficiency
- 20 videos = ~200-400MB temp storage
- Download batch → transcribe batch → cleanup
- Prevents disk overflow on large channels

### 🔧 Technical Stack

**Core Dependencies:**
- faster-whisper >= 1.0.0
- yt-dlp (latest)
- torch >= 2.0 (with CUDA support)
- Python 3.9+
- CUDA 12.x runtime

**Database:**
- SQLite3 (built-in Python)
- Single-file database
- Thread-safe with locking
- Suitable for local/single-machine use

**Video Processing:**
- yt-dlp for downloads
- FFmpeg (via imageio-ffmpeg)
- Audio extraction only (saves bandwidth)

---

## 📋 Future Enhancements (Not Yet Implemented)

These are planned but not yet deployed:

### Remote GPU Testing
- Vast.ai / RunPod integration scripts prepared
- A100 rental guide created
- Not deployed (cost vs benefit for current use case)

### Modal.com Distributed Architecture
- Design for 50-100 parallel GPU workers
- 500x+ realtime speed potential
- For weekly processing of 1000+ hour channels
- Architecture documented, not implemented

### PostgreSQL Migration
- Replace SQLite for true multi-worker support
- Required for distributed processing
- Not needed for current local setup

### S3/R2 Storage Integration
- Cloud storage for transcripts
- Required for distributed workers
- Local file system works fine currently

---

## Version History

### v2.0 (Current - December 2025)
- faster-whisper integration
- CUDA 12 support
- 35-40x realtime performance
- Production-ready for local GPU

### v1.0 (Original)
- openai-whisper
- CUDA 11.8
- 23x realtime performance
- Basic batch processing

---

**Deployment Status:** ✅ Production | Battle-tested on 500+ hours of content
