# YouTube Channel Bulk Transcriber - GPU Accelerated

A powerful, production-ready system for transcribing entire YouTube channels using GPU-accelerated Whisper AI.

## Features

- 🚀 **GPU Accelerated** - 10-30x faster than CPU transcription
- 📦 **Bulk Processing** - Transcribe entire channels (hundreds of videos)
- 🔄 **Resumable** - Interrupt and resume anytime without losing progress
- 🎯 **Parallel Downloads** - Download 10+ videos simultaneously
- 💾 **Smart Storage** - Auto-cleanup of audio files to save disk space
- 📊 **Progress Tracking** - SQLite database tracks everything
- 🛡️ **Error Handling** - Robust retry logic and error recovery
- 📝 **Detailed Logs** - Complete logging to file and console

## System Requirements

### Hardware
- **GPU:** NVIDIA GPU with 4GB+ VRAM (8GB+ recommended)
- **RAM:** 8GB minimum (16GB recommended)
- **Storage:** 50-100GB free space for temp audio files
- **Internet:** Stable connection (10+ Mbps recommended)

### Software
- **Python:** 3.8 or higher
- **CUDA:** 11.7 or higher
- **Windows/Linux/Mac:** All supported

## Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements_gpu.txt
```

### Step 2: Install PyTorch with CUDA

**For CUDA 11.8:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**For CUDA 12.1:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Check your CUDA version:**
```bash
nvidia-smi
```

### Step 3: Verify GPU Setup

```bash
python check_gpu.py
```

You should see:
```
✓ PyTorch installed
✓ CUDA is available
✓ GPU Devices Found: 1
✓ GPU computation test PASSED
✓ Whisper installed
```

## Quick Start

### Option 1: Edit the Script Directly

1. Open `channel_transcriber.py`
2. Find line ~470:
   ```python
   CHANNEL_URL = "https://www.youtube.com/@channel_name"  # CHANGE THIS
   ```
3. Replace with your channel URL
4. Run:
   ```bash
   python channel_transcriber.py
   ```

### Option 2: Use Configuration File

1. Edit `config.py`:
   ```python
   CHANNEL_URL = "https://www.youtube.com/@YourChannel"
   MODEL_SIZE = "base"  # or small, medium, large
   ```

2. Modify `channel_transcriber.py` to import config:
   ```python
   from config import *
   ```

3. Run:
   ```bash
   python channel_transcriber.py
   ```

## Usage Examples

### Example 1: Basic Usage

```bash
python channel_transcriber.py
```

### Example 2: Different Model Sizes

Edit the script to change model:
```python
MODEL_SIZE = "small"  # More accurate, slower
```

### Example 3: More Parallel Downloads

```python
DOWNLOAD_WORKERS = 15  # Download 15 videos at once
```

### Example 4: Resume Interrupted Process

Just run the script again! It automatically resumes:
```bash
python channel_transcriber.py
```

The database tracks all progress, so it picks up where it left off.

## How It Works

### Architecture

```
1. SCRAPE CHANNEL
   ↓
   Extract all video URLs and metadata
   ↓
2. DOWNLOAD AUDIO
   ↓
   Parallel download (10 workers) → temp_audio/
   ↓
3. TRANSCRIBE (GPU)
   ↓
   Whisper AI processes audio → transcripts/
   ↓
4. CLEANUP
   ↓
   Delete audio files to save space
```

### Processing Pipeline

1. **Channel Scraper** uses yt-dlp to extract all video metadata
2. **Progress Tracker** saves everything to SQLite database
3. **Audio Downloader** downloads in batches with parallel workers
4. **GPU Transcriber** processes audio with Whisper on GPU
5. **Auto-cleanup** removes audio files after successful transcription

## Performance

### Speed Estimates (500 videos, 40 min avg per video)

| Model  | GPU       | Total Time | Quality |
|--------|-----------|------------|---------|
| tiny   | RTX 3060  | 4-6 hours  | Good    |
| base   | RTX 3060  | 6-8 hours  | Better  |
| small  | RTX 3060  | 10-12 hours| Great   |
| medium | RTX 4070  | 15-20 hours| Excellent|
| large  | RTX 4090  | 12-15 hours| Best    |

### VRAM Requirements

| Model  | VRAM | Parallel Jobs |
|--------|------|---------------|
| tiny   | 1GB  | 4-8           |
| base   | 1GB  | 2-4           |
| small  | 2GB  | 1-2           |
| medium | 5GB  | 1             |
| large  | 10GB | 1             |

## Output Format

Each video gets a transcript file:

```
transcripts/
├── Video_Title_1_abc123.txt
├── Video_Title_2_def456.txt
└── Video_Title_3_ghi789.txt
```

### Transcript Structure

```
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
[Complete text without timestamps]

DETAILED TRANSCRIPT WITH TIMESTAMPS
--------------------------------------------------------------------------------
[00:00] First sentence with timestamp
[00:05] Second sentence with timestamp
...
================================================================================
END OF TRANSCRIPT
================================================================================
```

## Database Schema

Progress is tracked in `transcription_progress.db`:

```sql
videos (
    video_id TEXT PRIMARY KEY,
    url TEXT,
    title TEXT,
    duration INTEGER,
    channel TEXT,
    status TEXT,  -- pending, downloading, downloaded, transcribing, completed, error
    audio_path TEXT,
    transcript_path TEXT,
    error_message TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Check Progress

```python
import sqlite3
conn = sqlite3.connect('transcription_progress.db')
cursor = conn.cursor()

# Get stats
cursor.execute("SELECT status, COUNT(*) FROM videos GROUP BY status")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} videos")
```

## Advanced Usage

### Custom Processing Script

```python
from channel_transcriber import ChannelTranscriptionOrchestrator

orchestrator = ChannelTranscriptionOrchestrator(
    channel_url="https://www.youtube.com/@YourChannel",
    model_size="small",
    download_workers=15,
    transcribe_workers=2  # If you have 16GB+ VRAM
)

orchestrator.run()
```

### Filter Videos by Duration

Edit the scraper to skip long/short videos:

```python
# In ChannelScraper.scrape()
for entry in result['entries']:
    duration = entry.get('duration', 0)

    # Skip videos longer than 2 hours
    if duration > 7200:
        continue

    # Skip videos shorter than 5 minutes
    if duration < 300:
        continue

    videos.append(video)
```

### Process Specific Videos

```python
# Skip already processed videos in database
cursor.execute("DELETE FROM videos WHERE video_id = 'abc123'")
```

## Troubleshooting

### GPU Not Detected

```bash
# Check CUDA
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Out of Memory Error

Reduce model size or parallel workers:
```python
MODEL_SIZE = "tiny"  # Use smaller model
TRANSCRIBE_WORKERS = 1  # Reduce parallel jobs
```

### Download Errors

YouTube may rate-limit. Reduce workers:
```python
DOWNLOAD_WORKERS = 5  # Slower but more reliable
```

### Disk Space Issues

The system auto-deletes audio after transcription. If still running out:
- Reduce `BATCH_SIZE` to process fewer videos at once
- Clear `temp_audio/` directory manually

## Monitoring Progress

### Live Logs

```bash
# Watch log file in real-time
tail -f transcription.log

# On Windows
Get-Content transcription.log -Wait
```

### Check Statistics

The script prints stats periodically:
```
Total videos: 500
Completed: 234
Pending: 250
Errors: 16
Total duration: 333.3 hours
Completed duration: 156.0 hours
```

## Best Practices

1. **Start Small:** Test with a small channel first
2. **Monitor GPU Temp:** Keep below 80°C
3. **Use Base Model:** Best speed/quality balance
4. **Stable Internet:** Downloads can fail otherwise
5. **Backup Database:** Copy `transcription_progress.db` periodically
6. **Disk Space:** Keep 100GB free minimum

## Batch Processing Multiple Channels

```python
channels = [
    "https://www.youtube.com/@Channel1",
    "https://www.youtube.com/@Channel2",
    "https://www.youtube.com/@Channel3",
]

for channel in channels:
    orchestrator = ChannelTranscriptionOrchestrator(
        channel_url=channel,
        model_size="base"
    )
    orchestrator.run()
```

## Cost Analysis

### Local GPU (This System)
- **Hardware:** $300-800 (one-time GPU cost)
- **Electricity:** ~$2-5 for 500 videos
- **Total:** Essentially FREE after hardware

### Cloud Alternatives
- **OpenAI Whisper API:** ~$120 for 500 videos
- **AWS GPU Instances:** ~$25-50 for 500 videos

**ROI:** If you transcribe 10+ channels, local GPU pays for itself!

## Limitations

- YouTube age-restricted videos may fail
- Private videos are skipped
- Very long videos (3+ hours) may timeout
- Rate limiting can slow downloads

## Future Enhancements

Potential improvements (not yet implemented):
- [ ] Web UI for monitoring
- [ ] Speaker diarization
- [ ] Auto-summarization with GPT
- [ ] SRT subtitle export
- [ ] Multi-language support
- [ ] Playlist support
- [ ] Real-time progress bars

## License

MIT License - Free to use and modify

## Support

Having issues? Check:
1. `transcription.log` for errors
2. `transcription_progress.db` for stuck videos
3. GPU memory with `nvidia-smi`
4. Disk space with `df -h` (Linux) or `dir` (Windows)

## Credits

- **Whisper:** OpenAI
- **yt-dlp:** yt-dlp contributors
- **PyTorch:** Facebook AI Research

---

**Happy Transcribing! 🎉**
