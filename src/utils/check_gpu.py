#!/usr/bin/env python3
"""
GPU Check Script - Verify CUDA and GPU availability for Whisper
"""

import sys

def check_gpu():
    """Check if GPU is available and configured correctly"""

    print("=" * 70)
    print("GPU Configuration Check")
    print("=" * 70)
    print()

    # Check PyTorch
    try:
        import torch
        print("[OK] PyTorch installed")
        print(f"  Version: {torch.__version__}")
    except ImportError:
        print("[ERROR] PyTorch not installed")
        print("  Install with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return False

    # Check CUDA
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        print("[OK] CUDA is available")
        print(f"  CUDA Version: {torch.version.cuda}")
        print(f"  cuDNN Version: {torch.backends.cudnn.version()}")
    else:
        print("[ERROR] CUDA is NOT available")
        print("  Your PyTorch installation doesn't support CUDA")
        print("  Reinstall PyTorch with CUDA support:")
        print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return False

    # Check GPU devices
    num_gpus = torch.cuda.device_count()
    print(f"\n[OK] GPU Devices Found: {num_gpus}")

    for i in range(num_gpus):
        props = torch.cuda.get_device_properties(i)
        print(f"\n  GPU {i}: {props.name}")
        print(f"    Compute Capability: {props.major}.{props.minor}")
        print(f"    Total Memory: {props.total_memory / 1e9:.2f} GB")
        print(f"    Multi Processors: {props.multi_processor_count}")

    # Test GPU
    print("\n" + "-" * 70)
    print("Testing GPU computation...")
    try:
        device = torch.device("cuda:0")
        x = torch.randn(1000, 1000, device=device)
        y = torch.matmul(x, x)
        print("[OK] GPU computation test PASSED")
    except Exception as e:
        print(f"[ERROR] GPU computation test FAILED: {e}")
        return False

    # Check Whisper
    print("\n" + "-" * 70)
    try:
        import whisper
        print("[OK] Whisper installed")
        print(f"  Available models: {', '.join(whisper.available_models())}")
    except ImportError:
        print("[ERROR] Whisper not installed")
        print("  Install with: pip install openai-whisper")
        return False

    # Memory recommendations
    print("\n" + "=" * 70)
    print("Model Memory Requirements (approximate):")
    print("=" * 70)

    total_mem = torch.cuda.get_device_properties(0).total_memory / 1e9

    models = {
        'tiny': 1,
        'base': 1,
        'small': 2,
        'medium': 5,
        'large': 10,
    }

    print(f"\nYour GPU Memory: {total_mem:.2f} GB\n")

    for model, mem in models.items():
        if total_mem >= mem:
            print(f"  [OK] {model:8s} - {mem} GB   [RECOMMENDED]")
        else:
            print(f"  [--] {model:8s} - {mem} GB   [NOT RECOMMENDED]")

    # Speed estimates
    print("\n" + "=" * 70)
    print("Estimated Transcription Speed (GPU):")
    print("=" * 70)
    print("\nFor 1 hour of audio:")
    print(f"  tiny   model: ~2-3 minutes")
    print(f"  base   model: ~3-5 minutes")
    print(f"  small  model: ~5-8 minutes")
    print(f"  medium model: ~10-15 minutes")
    print(f"  large  model: ~20-30 minutes")

    print("\n" + "=" * 70)
    print("[OK] GPU Setup Complete - Ready for Transcription!")
    print("=" * 70)

    return True

if __name__ == "__main__":
    success = check_gpu()
    sys.exit(0 if success else 1)
