#!/usr/bin/env python3
"""
Simple wrapper script that uses config.py
Makes it easier to run without editing the main script
"""

import sys
import os
import logging
from pathlib import Path

# Add CUDA 12 to PATH for faster-whisper
cuda12_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin"
if os.path.exists(cuda12_path):
    os.environ['PATH'] = cuda12_path + os.pathsep + os.environ.get('PATH', '')
    print(f"Added CUDA 12.6 to PATH: {cuda12_path}")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "config"))

# Change to project root directory so relative paths work
os.chdir(project_root)

# Import configuration
try:
    from config import *
except ImportError:
    print("Error: config.py not found!")
    print("Please create config/config.py from the template")
    sys.exit(1)

# Setup logging with proper paths
log_dir = Path(LOG_FILE).parent
if log_dir and str(log_dir) != '.':
    log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Configure stdout to handle UTF-8 on Windows
import sys
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr:
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Import main orchestrator
from channel_transcriber import ChannelTranscriptionOrchestrator

def main():
    """Main entry point using config.py settings"""

    print("""
================================================================================
         YouTube Channel Bulk Transcriber - GPU Accelerated
                        Running with config.py
================================================================================
    """)

    # Display configuration
    print("Configuration:")
    print("-" * 70)
    print(f"  Channel URL:         {CHANNEL_URL}")
    print(f"  Model Size:          {MODEL_SIZE}")
    print(f"  Download Workers:    {DOWNLOAD_WORKERS}")
    print(f"  Transcribe Workers:  {TRANSCRIBE_WORKERS}")
    print(f"  Batch Size:          {BATCH_SIZE}")
    print(f"  Language:            {LANGUAGE}")
    print(f"  Device:              {DEVICE}")
    print(f"  Audio Directory:     {AUDIO_DIR}")
    print(f"  Transcript Directory:{TRANSCRIPT_DIR}")
    print("-" * 70)

    # Validate channel URL
    if CHANNEL_URL == "https://www.youtube.com/@username":
        print("\n[!] WARNING: You haven't changed the CHANNEL_URL in config.py!")
        print("   Please edit config.py and set your YouTube channel URL")
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)

    print("\nStarting transcription process...")
    print("Press Ctrl+C to interrupt (progress will be saved)\n")

    # Create and run orchestrator
    orchestrator = ChannelTranscriptionOrchestrator(
        channel_url=CHANNEL_URL,
        model_size=MODEL_SIZE,
        download_workers=DOWNLOAD_WORKERS,
        transcribe_workers=TRANSCRIBE_WORKERS,
        audio_base_dir=AUDIO_DIR,
        transcript_base_dir=TRANSCRIPT_DIR,
        db_path=DATABASE_FILE
    )

    try:
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
        print("[+] Progress has been saved to the database")
        print("[+] Run this script again to resume from where you left off")
    except Exception as e:
        print(f"\n\n[X] Fatal error: {e}")
        print("\nCheck transcription.log for details")
        raise

if __name__ == "__main__":
    main()
