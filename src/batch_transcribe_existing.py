#!/usr/bin/env python3
"""
Simple batch transcriber for already-downloaded audio files
Transcribes all .webm files in temp_audio/ directory
"""

import os
import whisper
import torch
from pathlib import Path
from datetime import datetime

# Setup
audio_dir = Path("temp_audio")
output_dir = Path("transcripts")
output_dir.mkdir(exist_ok=True)

# Load Whisper model on GPU
print("Loading Whisper model on GPU...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=device)
print(f"Model loaded on {device}")

# Get all audio files
audio_files = list(audio_dir.glob("*.webm"))
print(f"\nFound {len(audio_files)} audio files to transcribe")

# Transcribe each file
for i, audio_path in enumerate(audio_files, 1):
    video_id = audio_path.stem
    print(f"\n[{i}/{len(audio_files)}] Transcribing {video_id}...")

    try:
        # Transcribe
        result = model.transcribe(
            str(audio_path),
            language="en",
            task="transcribe",
            verbose=False,
            fp16=(device == "cuda")
        )

        # Save transcript
        transcript_path = output_dir / f"{video_id}_transcript.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"TRANSCRIPT: {video_id}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Transcription Date: {datetime.now()}\n")
            f.write(f"Model: Whisper base (Device: {device})\n")
            f.write("=" * 80 + "\n\n")
            f.write(result['text'])
            f.write("\n\n" + "=" * 80 + "\n")

        print(f"   ✓ Saved to {transcript_path}")

        # Delete audio file to save space
        audio_path.unlink()
        print(f"   ✓ Deleted audio file")

    except Exception as e:
        print(f"   ✗ Error: {e}")
        continue

print(f"\n\nDone! Transcribed {len(list(output_dir.glob('*.txt')))} videos")
print(f"Transcripts saved to: {output_dir.absolute()}")
