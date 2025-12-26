#!/usr/bin/env python3
"""
YouTube Channel Transcriber - Quick Setup

Minimal setup script for advanced users who want to quickly:
- Install dependencies
- Create config file
- Get started

For full interactive wizard, use: python setup.py

Usage:
    python quick-setup.py              # Interactive (asks questions)
    python quick-setup.py --local      # Local GPU only
    python quick-setup.py --modal      # Modal Cloud only
    python quick-setup.py --both       # Both (default)
"""

import sys
import subprocess
import shutil
from pathlib import Path
import argparse

def install_deps(install_type='both'):
    """Install dependencies"""
    print(f"Installing dependencies ({install_type})...")

    requirements = ['requirements.txt']
    if install_type in ['modal', 'both']:
        requirements.append('requirements-modal.txt')

    for req_file in requirements:
        print(f"  Installing from {req_file}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "-r", req_file],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to install {req_file}")
            return False

    print("  ✓ Dependencies installed")
    return True

def create_config(interactive=True):
    """Create config from template"""
    print("Creating config file...")

    config_dir = Path("config")
    config_file = config_dir / "config.py"
    example_file = config_dir / "config.example.py"

    if config_file.exists():
        print(f"  ! Config already exists: {config_file}")
        if interactive:
            response = input("  Overwrite? (y/n) [n]: ").strip().lower()
            if response != 'y':
                print("  Keeping existing config")
                return True
        else:
            print("  Keeping existing config (use --force to overwrite)")
            return True

    # Copy example to config
    try:
        shutil.copy(example_file, config_file)
        print(f"  ✓ Created: {config_file}")

        if interactive:
            print("\n  Edit config/config.py to set your YouTube channel URL")
            print("  Example: CHANNEL_URL = \"https://www.youtube.com/@username\"\n")

        return True
    except Exception as e:
        print(f"  ✗ Failed to create config: {e}")
        return False

def create_dirs():
    """Create data directories"""
    print("Creating data directories...")

    directories = ["data", "data/temp_audio", "data/transcripts"]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("  ✓ Directories created")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Quick setup for YouTube Channel Transcriber"
    )
    parser.add_argument(
        '--local', action='store_true',
        help='Install local GPU dependencies only'
    )
    parser.add_argument(
        '--modal', action='store_true',
        help='Install Modal Cloud dependencies only'
    )
    parser.add_argument(
        '--both', action='store_true',
        help='Install both (default)'
    )
    parser.add_argument(
        '--no-deps', action='store_true',
        help='Skip dependency installation'
    )
    parser.add_argument(
        '--force', action='store_true',
        help='Overwrite existing config without asking'
    )

    args = parser.parse_args()

    # Determine installation type
    if args.local:
        install_type = 'local'
    elif args.modal:
        install_type = 'modal'
    else:
        install_type = 'both'

    print("="*70)
    print("YouTube Channel Transcriber - Quick Setup")
    print("="*70)
    print()

    # Install dependencies
    if not args.no_deps:
        if not install_deps(install_type):
            sys.exit(1)
    else:
        print("Skipping dependency installation (--no-deps)")

    # Create config
    interactive = not args.force
    if not create_config(interactive):
        sys.exit(1)

    # Create directories
    if not create_dirs():
        sys.exit(1)

    # Show next steps
    print()
    print("="*70)
    print("Setup Complete!")
    print("="*70)
    print()
    print("Next steps:")
    print()

    if install_type in ['local', 'both']:
        print("  Local GPU:")
        print("    python scripts/run_transcriber.py")
        print()

    if install_type in ['modal', 'both']:
        print("  Modal Cloud:")
        print("    1. modal setup                           # Authenticate")
        print("    2. python scripts/prepare_for_modal.py   # Download audio")
        print("    3. modal run scripts/modal_hybrid.py --max-files 3  # Test")
        print()

    print("Documentation:")
    print("  • QUICKSTART.md - Quick start guide")
    print("  • docs/GETTING_STARTED.md - Full setup guide")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
