#!/usr/bin/env python3
"""
GPU-Accelerated Batch Transcriber
Properly sets ffmpeg path and uses GPU acceleration
Supports channel-specific folder organization
"""

import os
import sys
import whisper
import torch
from pathlib import Path
from datetime import datetime
import time

# Set ffmpeg path BEFORE importing whisper's audio functions
ffmpeg_path = r"C:\Users\anshu\AppData\Roaming\Python\Python313\site-packages\imageio_ffmpeg\binaries"
os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ.get('PATH', '')

print("=" * 80)
print("GPU-ACCELERATED BATCH TRANSCRIBER")
print("=" * 80)

# Check GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"\n[GPU] {gpu_name}")
    print(f"[GPU] Memory: {gpu_memory:.2f} GB")
    print(f"[GPU] CUDA Version: {torch.version.cuda}")
else:
    print("\n[WARNING] No GPU detected, using CPU (this will be slow)")
    sys.exit(1)

# Configuration - CHANGE THIS to match your channel
# If you provide a channel_name, it will look for audio in data/temp_audio/{channel_name}/
# and save transcripts to data/transcripts/{channel_name}/
CHANNEL_NAME = None  # Set to None to use root directories, or specify channel name

# Setup
audio_base_dir = Path("data/temp_audio")
transcript_base_dir = Path("data/transcripts")

if CHANNEL_NAME:
    audio_dir = audio_base_dir / CHANNEL_NAME
    output_dir = transcript_base_dir / CHANNEL_NAME
    print(f"\n[CONFIG] Channel: {CHANNEL_NAME}")
else:
    audio_dir = audio_base_dir
    output_dir = transcript_base_dir
    print(f"\n[CONFIG] Using root directories (no channel specified)")

print(f"[CONFIG] Audio directory: {audio_dir}")
print(f"[CONFIG] Output directory: {output_dir}")

output_dir.mkdir(parents=True, exist_ok=True)

# Get all audio files (supports multiple formats)
audio_extensions = ['*.webm', '*.mp3', '*.m4a', '*.wav', '*.opus']
audio_files = []
for ext in audio_extensions:
    audio_files.extend(audio_dir.glob(ext))
audio_files = sorted(audio_files)

print(f"\n[INFO] Found {len(audio_files)} audio files to transcribe\n")

if len(audio_files) == 0:
    print(f"[ERROR] No audio files found in {audio_dir}/")
    print(f"[ERROR] Searched for: {', '.join(audio_extensions)}")
    sys.exit(1)

# Load Whisper model on GPU
print("[1/3] Loading Whisper 'base' model on GPU...")
print("      (This may take 1-2 minutes on first run)")
start_load = time.time()
model = whisper.load_model("base", device=device)
load_time = time.time() - start_load
print(f"      [OK] Model loaded in {load_time:.1f}s\n")

# Transcribe each file
print("[2/3] Transcribing videos on GPU...\n")
completed = 0
failed = 0

for i, audio_path in enumerate(audio_files, 1):
    video_id = audio_path.stem
    print(f"[{i}/{len(audio_files)}] {video_id}...")

    try:
        start = time.time()

        # Transcribe with FP16 for faster GPU processing
        result = model.transcribe(
            str(audio_path),
            language="en",
            task="transcribe",
            verbose=False,
            fp16=True  # Use FP16 on GPU for 2x speed
        )

        elapsed = time.time() - start

        # Save transcript
        transcript_path = output_dir / f"{video_id}_transcript.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"VIDEO ID: {video_id}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Transcribed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: Whisper base (GPU: {gpu_name})\n")
            f.write(f"Language: English\n")
            f.write(f"Processing time: {elapsed:.1f}s\n")
            f.write("=" * 80 + "\n\n")
            f.write(result['text'].strip())
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("END OF TRANSCRIPT\n")
            f.write("=" * 80 + "\n")

        # Delete audio file to save space
        audio_path.unlink()

        completed += 1
        print(f"      [OK] Completed in {elapsed:.1f}s")
        print(f"      [OK] Saved to {transcript_path.name}")
        print(f"      [OK] Deleted audio file\n")

    except Exception as e:
        failed += 1
        print(f"      [ERROR] {e}\n")
        continue

# Summary
print("=" * 80)
print("[3/3] BATCH TRANSCRIPTION COMPLETE")
print("=" * 80)
print(f"\nCompleted: {completed}/{len(audio_files)} videos")
print(f"Failed: {failed}")
print(f"\nTranscripts saved to: {output_dir.absolute()}")
print("=" * 80)
