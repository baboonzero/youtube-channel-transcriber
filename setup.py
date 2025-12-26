#!/usr/bin/env python3
"""
YouTube Channel Transcriber - Interactive Setup Wizard

This script will guide you through setting up the transcriber.
It will:
- Check system requirements
- Install dependencies
- Create configuration file
- Test GPU/Modal setup
- Validate installation

Usage:
    python setup.py
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a header with formatting"""
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def ask_question(question, default=None):
    """Ask a question and get user input"""
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "

    response = input(prompt).strip()
    return response if response else default

def ask_yes_no(question, default='y'):
    """Ask a yes/no question"""
    response = ask_question(f"{question} (y/n)", default).lower()
    return response == 'y'

def check_python_version():
    """Check if Python version is 3.9+"""
    print_header("Checking System Requirements")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error("Python 3.9 or higher is required!")
        print(f"You have Python {version.major}.{version.minor}.{version.micro}")
        return False

    print_success("Python version OK")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      capture_output=True, check=True)
        print_success("pip is available")
        return True
    except:
        print_error("pip is not available!")
        return False

def ask_installation_type():
    """Ask user which installation type they want"""
    print_header("Choose Installation Type")

    print("How do you want to transcribe videos?\n")
    print("1. Local GPU (RTX 3060+, 8GB+ VRAM recommended)")
    print("   - Fast setup, no cloud costs")
    print("   - Limited to one GPU at a time")
    print("   - Speed: 35-40x realtime (with faster-whisper)")
    print()
    print("2. Modal Cloud (A10G GPUs)")
    print("   - Requires Modal account ($30 free credits)")
    print("   - Parallel processing (100+ GPUs)")
    print("   - Pay per use (~$3-4 per 100 videos)")
    print()
    print("3. Both (recommended for flexibility)")
    print("   - Install everything")
    print("   - Choose which to use each time")
    print()

    while True:
        choice = ask_question("Choice", "3")
        if choice in ['1', '2', '3']:
            return choice
        print_error("Invalid choice. Please enter 1, 2, or 3.")

def install_dependencies(install_type):
    """Install required dependencies based on installation type"""
    print_header("Installing Dependencies")

    # Base requirements
    requirements = ['requirements.txt']

    # Add Modal requirements if needed
    if install_type in ['2', '3']:
        requirements.append('requirements-modal.txt')

    for req_file in requirements:
        print(f"\nInstalling from {req_file}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_file],
                check=True
            )
            print_success(f"Installed dependencies from {req_file}")
        except subprocess.CalledProcessError:
            print_error(f"Failed to install dependencies from {req_file}")
            return False

    return True

def check_gpu():
    """Check if CUDA-capable GPU is available"""
    print_header("Checking GPU Availability")

    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9

            print_success(f"CUDA detected")
            print_success(f"GPU: {gpu_name}")
            print_success(f"VRAM: {gpu_memory:.1f} GB")

            if gpu_memory < 6:
                print_warning("Less than 6GB VRAM - use 'tiny' or 'base' model")
            elif gpu_memory < 8:
                print_info("6-8GB VRAM - 'small' model recommended")
            else:
                print_info("8GB+ VRAM - 'medium' or 'large' model available")

            return True, gpu_memory
        else:
            print_warning("No CUDA-capable GPU found")
            print_info("You can still use CPU mode (very slow) or Modal Cloud")
            return False, 0
    except ImportError:
        print_warning("PyTorch not installed - cannot check GPU")
        return False, 0

def setup_modal():
    """Help user setup Modal"""
    print_header("Setting Up Modal")

    # Check if Modal is installed
    try:
        import modal
        print_success("Modal is installed")
    except ImportError:
        print_warning("Modal not installed")
        if ask_yes_no("Install Modal now?", "y"):
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "modal"],
                    check=True
                )
                print_success("Modal installed")
            except:
                print_error("Failed to install Modal")
                return False

    # Check if Modal is authenticated
    print("\nChecking Modal authentication...")
    print_info("This will open a browser window for authentication")
    print_info("You'll need to sign up or login to Modal")
    print()

    if ask_yes_no("Run 'modal setup' now?", "y"):
        try:
            subprocess.run(["modal", "setup"], check=True)
            print_success("Modal authentication complete")
            return True
        except:
            print_error("Modal setup failed")
            print_info("You can run 'modal setup' manually later")
            return False
    else:
        print_info("Skipped Modal setup - run 'modal setup' manually later")
        return False

def create_config():
    """Create config.py from template"""
    print_header("Creating Configuration File")

    config_dir = Path("config")
    config_file = config_dir / "config.py"
    example_file = config_dir / "config.example.py"

    # Check if config already exists
    if config_file.exists():
        print_warning(f"Config file already exists: {config_file}")
        if not ask_yes_no("Overwrite existing config?", "n"):
            print_info("Keeping existing config")
            return True

    # Read example config
    try:
        with open(example_file, 'r', encoding='utf-8') as f:
            config_content = f.read()
    except FileNotFoundError:
        print_error(f"Example config not found: {example_file}")
        return False

    # Ask for configuration values
    print("\nLet's configure your YouTube channel:\n")

    channel_url = ask_question(
        "YouTube Channel URL",
        "https://www.youtube.com/@username"
    )

    print("\nWhisper model size (affects accuracy and speed):")
    print("  tiny   - Fastest, least accurate")
    print("  base   - Good balance (recommended)")
    print("  small  - Better accuracy, slower")
    print("  medium - High accuracy, requires more VRAM")
    print("  large  - Best accuracy, slow, high VRAM")

    model_size = ask_question("Model size", "base")

    delete_audio = ask_yes_no(
        "Delete audio files after transcription? (saves disk space)",
        "y"
    )

    # Update config content
    config_content = config_content.replace(
        'CHANNEL_URL = "https://www.youtube.com/@username"',
        f'CHANNEL_URL = "{channel_url}"'
    )

    config_content = config_content.replace(
        'MODEL_SIZE = "base"',
        f'MODEL_SIZE = "{model_size}"'
    )

    config_content = config_content.replace(
        'DELETE_AUDIO_AFTER_TRANSCRIPTION = True',
        f'DELETE_AUDIO_AFTER_TRANSCRIPTION = {delete_audio}'
    )

    # Write config file
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print_success(f"Created config file: {config_file}")
        return True
    except Exception as e:
        print_error(f"Failed to create config: {e}")
        return False

def create_directories():
    """Create necessary data directories"""
    print_header("Creating Data Directories")

    directories = [
        "data",
        "data/temp_audio",
        "data/transcripts"
    ]

    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created: {directory}/")
        else:
            print_info(f"Already exists: {directory}/")

    return True

def show_next_steps(install_type):
    """Show user what to do next"""
    print_header("Setup Complete! 🎉")

    print("Your transcriber is ready to use!\n")

    if install_type == '1':
        # Local GPU only
        print(f"{Colors.BOLD}Next Steps - Local GPU Transcription:{Colors.ENDC}\n")
        print("1. Run the transcriber:")
        print(f"   {Colors.OKCYAN}python scripts/run_transcriber.py{Colors.ENDC}")
        print()
        print("   This will:")
        print("   - Scrape your YouTube channel")
        print("   - Download all videos as audio")
        print("   - Transcribe using your local GPU")
        print()

    elif install_type == '2':
        # Modal Cloud only
        print(f"{Colors.BOLD}Next Steps - Modal Cloud Transcription:{Colors.ENDC}\n")
        print("1. Prepare channel (scrape + download):")
        print(f"   {Colors.OKCYAN}python scripts/prepare_for_modal.py{Colors.ENDC}")
        print()
        print("2. Transcribe on Modal (test with 3 files first):")
        print(f"   {Colors.OKCYAN}modal run scripts/modal_hybrid.py --max-files 3{Colors.ENDC}")
        print()
        print("3. If test works, process all files:")
        print(f"   {Colors.OKCYAN}modal run scripts/modal_hybrid.py --max-files 100{Colors.ENDC}")
        print()

    else:
        # Both
        print(f"{Colors.BOLD}Next Steps - You have both options:{Colors.ENDC}\n")
        print("Option A - Local GPU:")
        print(f"   {Colors.OKCYAN}python scripts/run_transcriber.py{Colors.ENDC}")
        print()
        print("Option B - Modal Cloud:")
        print(f"   {Colors.OKCYAN}python scripts/prepare_for_modal.py{Colors.ENDC}")
        print(f"   {Colors.OKCYAN}modal run scripts/modal_hybrid.py --max-files 3{Colors.ENDC}")
        print()

    print(f"{Colors.BOLD}Documentation:{Colors.ENDC}")
    print(f"  • Quick Start: {Colors.OKCYAN}QUICKSTART.md{Colors.ENDC}")
    print(f"  • Full Guide: {Colors.OKCYAN}docs/GETTING_STARTED.md{Colors.ENDC}")
    print(f"  • Modal Guide: {Colors.OKCYAN}docs/MODAL_QUICKSTART.md{Colors.ENDC}")
    print()

    print(f"{Colors.BOLD}Need Help?{Colors.ENDC}")
    print("  • Check the documentation in the docs/ folder")
    print("  • Open an issue on GitHub")
    print()

def main():
    """Main setup function"""
    print_header("YouTube Channel Transcriber - Setup Wizard")
    print("This wizard will guide you through setting up the transcriber.\n")

    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)

    if not check_pip():
        sys.exit(1)

    # Step 2: Ask installation type
    install_type = ask_installation_type()

    # Step 3: Install dependencies
    if not install_dependencies(install_type):
        print_error("Failed to install dependencies")
        sys.exit(1)

    # Step 4: Check GPU (if local installation)
    gpu_available = False
    if install_type in ['1', '3']:
        gpu_available, vram = check_gpu()

        if not gpu_available and install_type == '1':
            print_warning("You chose Local GPU but no GPU was detected")
            if not ask_yes_no("Continue anyway? (CPU mode will be very slow)", "n"):
                print_info("Setup cancelled. Consider using Modal Cloud instead.")
                sys.exit(0)

    # Step 5: Setup Modal (if cloud installation)
    if install_type in ['2', '3']:
        setup_modal()

    # Step 6: Create config file
    if not create_config():
        print_error("Failed to create config")
        sys.exit(1)

    # Step 7: Create data directories
    create_directories()

    # Step 8: Show next steps
    show_next_steps(install_type)

    print(f"{Colors.OKGREEN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}Setup completed successfully!{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{'='*70}{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
