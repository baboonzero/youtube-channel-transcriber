# Installation Guide

## Prerequisites

- **Python:** 3.9 or higher
- **GPU:** NVIDIA GPU with 4GB+ VRAM (8GB recommended)
- **Storage:** 50-100GB free space

## Step 1: Install Python Dependencies

### For Local GPU Transcription

```bash
pip install -r requirements.txt
```

### For Modal Cloud Transcription

```bash
pip install -r requirements-modal.txt
```

## Step 2: Install CUDA (Local GPU Only)

Download CUDA 12.x from: https://developer.nvidia.com/cuda-downloads

Verify installation:
```bash
nvidia-smi
```

## Step 3: Install PyTorch with CUDA

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Verify GPU access:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## Step 4: Configure

```bash
cp config/config.example.py config/config.py
```

Edit `config/config.py` and set your YouTube channel URL.

## Step 5: First Run

```bash
cd scripts
python run_transcriber.py
```

For Modal cloud:
```bash
modal setup  # One-time setup
modal run scripts/modal_hybrid.py --max-files 3
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.
