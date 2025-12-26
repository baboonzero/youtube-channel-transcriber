#!/usr/bin/env python3
"""
YouTube Video Transcription Script
Downloads audio from YouTube and transcribes using OpenAI Whisper
"""

import whisper
import yt_dlp
import os
import sys
from datetime import datetime
from pathlib import Path
import imageio_ffmpeg
import subprocess

# Get ffmpeg path and set it in environment
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_path)

# Add to PATH
if ffmpeg_dir not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

# Also create a symlink/copy named 'ffmpeg' if it doesn't exist
if not os.path.exists(os.path.join(ffmpeg_dir, "ffmpeg.exe")):
    import shutil
    ffmpeg_target = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    try:
        shutil.copy2(ffmpeg_path, ffmpeg_target)
        print(f"Created ffmpeg.exe at {ffmpeg_target}")
    except Exception as e:
        print(f"Note: Could not create ffmpeg.exe: {e}")

def download_youtube_audio(youtube_url, base_output_dir="data/temp_audio"):
    """
    Download audio from YouTube video
    Creates a video-specific subfolder
    """
    print(f"\n[1/3] Downloading audio from YouTube...")
    print(f"URL: {youtube_url}")

    # First, get video info to create appropriate folder
    ydl_info_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_title = info.get('title', 'Unknown Title')
            video_id = info.get('id', 'unknown_id')
            duration = info.get('duration', 0)

        # Create safe folder name from video title
        safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:80]  # Limit length
        folder_name = f"{safe_title}_{video_id}"

        # Create video-specific subfolder
        video_dir = Path(base_output_dir) / folder_name
        video_dir.mkdir(parents=True, exist_ok=True)

        output_path = str(video_dir / "audio")

        print(f"\nVideo Title: {video_title}")
        print(f"Duration: {duration // 60} minutes {duration % 60} seconds")
        print(f"Output folder: {video_dir}")

        # Download audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path + '.%(ext)s',
            'quiet': False,
            'no_warnings': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            ext = info.get('ext', 'webm')

            print(f"Audio format: {ext}")

            actual_file = output_path + '.' + ext
            return actual_file, video_title, duration, video_dir
    except Exception as e:
        print(f"Error downloading audio: {e}")
        sys.exit(1)

def transcribe_audio(audio_file, model_size="base"):
    """
    Transcribe audio using Whisper
    """
    print(f"\n[2/3] Loading Whisper model ({model_size})...")
    print("This may take a moment on first run (downloading model)...")

    try:
        # Verify audio file exists
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        # Get absolute path
        audio_file = os.path.abspath(audio_file)
        print(f"Audio file: {audio_file}")
        print(f"File size: {os.path.getsize(audio_file) / (1024*1024):.2f} MB")

        model = whisper.load_model(model_size)

        print(f"\n[2/3] Transcribing audio...")
        print("This may take several minutes depending on video length...")
        print("Processing in progress...\n")

        # Transcribe with detailed options for maximum accuracy
        result = model.transcribe(
            audio_file,
            language="en",  # Auto-detect if not specified
            task="transcribe",
            verbose=True,
            word_timestamps=True,
            temperature=0.0,  # More deterministic output
            fp16=False,  # Use FP32 for CPU
        )

        return result
    except Exception as e:
        import traceback
        print(f"Error transcribing audio: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def structure_transcript(result, video_title):
    """
    Structure the transcript with timestamps and sections
    """
    structured_text = []

    # Header
    structured_text.append("=" * 80)
    structured_text.append(f"TRANSCRIPT: {video_title}")
    structured_text.append("=" * 80)
    structured_text.append(f"Transcription Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    structured_text.append(f"Transcription Tool: OpenAI Whisper")
    structured_text.append("=" * 80)
    structured_text.append("\n")

    # Full transcript without timestamps
    structured_text.append("FULL TRANSCRIPT")
    structured_text.append("-" * 80)
    structured_text.append(result['text'].strip())
    structured_text.append("\n" * 3)

    # Detailed transcript with timestamps
    structured_text.append("DETAILED TRANSCRIPT WITH TIMESTAMPS")
    structured_text.append("-" * 80)
    structured_text.append("\n")

    for segment in result['segments']:
        timestamp = format_timestamp(segment['start'])
        text = segment['text'].strip()
        structured_text.append(f"[{timestamp}] {text}")

    structured_text.append("\n" * 2)
    structured_text.append("=" * 80)
    structured_text.append("END OF TRANSCRIPT")
    structured_text.append("=" * 80)

    return "\n".join(structured_text)

def save_transcript(transcript_text, video_title, video_dir):
    """
    Save transcript to video-specific folder
    """
    # Create safe filename
    safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title[:100]  # Limit length

    filename = f"{safe_title}_transcript.txt"
    filepath = video_dir / filename

    print(f"\n[3/3] Saving transcript...")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(transcript_text)

        print(f"\nTranscript saved successfully!")
        print(f"Location: {filepath}")
        print(f"File size: {os.path.getsize(filepath) / 1024:.2f} KB")

        # Count words
        word_count = len(transcript_text.split())
        print(f"Word count: {word_count:,} words")

        return filepath
    except Exception as e:
        print(f"Error saving transcript: {e}")
        sys.exit(1)

def cleanup_audio_file(audio_file):
    """
    Remove temporary audio file
    """
    try:
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"\nCleaned up temporary audio file: {audio_file}")
    except Exception as e:
        print(f"Warning: Could not remove temporary file: {e}")

def main():
    youtube_url = "https://www.youtube.com/watch?v=peVGXTQcWig"

    print("=" * 80)
    print("YOUTUBE VIDEO TRANSCRIPTION")
    print("=" * 80)

    # Step 1: Download audio
    audio_file, video_title, duration, video_dir = download_youtube_audio(youtube_url)

    # Estimate processing time
    estimated_time = (duration / 60) * 0.5  # Roughly 30 seconds per minute of video
    print(f"\nEstimated transcription time: ~{estimated_time:.1f} minutes")

    # Step 2: Transcribe
    result = transcribe_audio(audio_file, model_size="base")

    # Step 3: Structure and save
    structured_transcript = structure_transcript(result, video_title)
    output_file = save_transcript(structured_transcript, video_title, video_dir)

    # Cleanup audio (optional - you can keep it if you want)
    # cleanup_audio_file(audio_file)

    print("\n" + "=" * 80)
    print("TRANSCRIPTION COMPLETE!")
    print("=" * 80)
    print(f"\nYour transcript is ready at:")
    print(f"{output_file}")
    print(f"\nAll files saved to: {video_dir}")
    print("\n")

if __name__ == "__main__":
    main()
