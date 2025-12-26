"""
Configuration file for YouTube Channel Bulk Transcriber
Edit these settings to customize the transcription process

CURRENT SYSTEM PERFORMANCE (RTX 4060, 8GB VRAM, base model):
- Speed: 35-40x realtime
- Example: 60-minute video transcribes in ~90-120 seconds
- Throughput: ~50-60 videos/hour (12-min average length)
- 1000 hours of content: ~25-30 hours processing time

TECH STACK:
- faster-whisper (CTranslate2) for GPU acceleration
- CUDA 12.x required
- yt-dlp for video downloads
- SQLite for progress tracking
"""

# ============================================================================
# CHANNEL SETTINGS
# ============================================================================

# YouTube channel URL to transcribe
# Examples:
#   - "https://www.youtube.com/@username"
#   - "https://www.youtube.com/c/channelname"
#   - "https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxx"
#
# SETUP: Replace with your desired channel URL
CHANNEL_URL = "https://www.youtube.com/@YourChannelHere"


# ============================================================================
# WHISPER MODEL SETTINGS
# ============================================================================

# Model size: tiny, base, small, medium, large
# Larger = more accurate but slower and more VRAM
#
# Recommended by GPU VRAM:
#   4GB:  tiny or base
#   6GB:  small
#   8GB:  small or medium
#   12GB: medium or large
#   16GB+: large
MODEL_SIZE = "base"


# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

# Number of parallel downloads (10-15 recommended)
# More = faster downloads but may hit rate limits
DOWNLOAD_WORKERS = 10

# Number of parallel GPU transcriptions
# IMPORTANT: MUST be set to 1 (Whisper models are not thread-safe)
# Parallel transcription requires distributed architecture (not yet implemented)
TRANSCRIBE_WORKERS = 1

# Batch size - how many videos to download before transcribing
# Lower = less disk space used, Higher = more efficient
BATCH_SIZE = 20


# ============================================================================
# OUTPUT SETTINGS
# ============================================================================

# Directory for temporary audio files
# NOTE: Files are organized by channel automatically
#   Structure: data/temp_audio/{channel_name}/
#   For single videos: data/temp_audio/{video_title}_{video_id}/
AUDIO_DIR = "data/temp_audio"

# Directory for transcripts
# NOTE: Transcripts are organized by channel automatically
#   Structure: data/transcripts/{channel_name}/
#   For single videos: data/temp_audio/{video_title}_{video_id}/
TRANSCRIPT_DIR = "data/transcripts"

# Database file for progress tracking
DATABASE_FILE = "data/transcription_progress.db"

# Log file
LOG_FILE = "data/transcription.log"


# ============================================================================
# TRANSCRIPTION SETTINGS
# ============================================================================

# Language for transcription
# Options:
#   - "en" for English
#   - "es" for Spanish
#   - "fr" for French
#   - None for auto-detect
LANGUAGE = "en"

# Task type
# Options:
#   - "transcribe" - transcribe in original language
#   - "translate" - translate to English
TASK = "transcribe"


# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Delete audio files after successful transcription (saves disk space)
DELETE_AUDIO_AFTER_TRANSCRIPTION = True

# Skip videos longer than X minutes (0 = no limit)
MAX_VIDEO_DURATION_MINUTES = 0

# Skip videos shorter than X minutes (0 = no limit)
MIN_VIDEO_DURATION_MINUTES = 0

# Retry failed downloads this many times
DOWNLOAD_RETRY_ATTEMPTS = 3

# Device for Whisper (usually "cuda" for GPU, "cpu" for CPU)
DEVICE = "cuda"
