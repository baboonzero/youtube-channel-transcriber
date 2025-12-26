#!/bin/bash
# Remote GPU Setup Script for YouTube Transcription System
# Run this on the Vast.ai instance after SSH connection

set -e  # Exit on error

echo "================================"
echo "Setting up Remote GPU Instance"
echo "================================"

# Update system
echo "[1/7] Updating system packages..."
apt-get update
apt-get install -y python3-pip python3-dev git wget curl

# Install CUDA toolkit if needed (most Vast.ai images have it)
echo "[2/7] Verifying CUDA installation..."
if ! command -v nvcc &> /dev/null; then
    echo "Installing CUDA 12..."
    # Most Vast.ai instances come with CUDA pre-installed
    apt-get install -y nvidia-cuda-toolkit
fi

# Verify GPU
echo "[3/7] Checking GPU..."
nvidia-smi

# Install Python dependencies
echo "[4/7] Installing Python packages..."
pip3 install --upgrade pip
pip3 install faster-whisper yt-dlp torch torchaudio

# Install ffmpeg
echo "[5/7] Installing ffmpeg..."
apt-get install -y ffmpeg

# Create project directory
echo "[6/7] Creating project structure..."
mkdir -p ~/youtube-transcriber/{data,config,src,scripts}
cd ~/youtube-transcriber

# Test faster-whisper with GPU
echo "[7/7] Testing faster-whisper GPU..."
python3 << 'PYTHON_TEST'
from faster_whisper import WhisperModel
import torch

print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    # Quick model test
    print("Loading Whisper model...")
    model = WhisperModel("base", device="cuda", compute_type="float16")
    print("✅ Model loaded successfully on GPU!")
else:
    print("❌ CUDA not available!")
    exit(1)
PYTHON_TEST

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Upload your code: scp -r src config scripts root@<instance-ip>:~/youtube-transcriber/"
echo "2. Upload database: scp data/transcription_progress.db root@<instance-ip>:~/youtube-transcriber/data/"
echo "3. SSH in and run: cd ~/youtube-transcriber/scripts && python3 run_transcriber.py"
