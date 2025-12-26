#!/usr/bin/env python3
"""
Progress Checker - View transcription status without running the main process
"""

import sqlite3
import os
from datetime import datetime

def format_duration(seconds):
    """Format seconds into human-readable duration"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"

def check_progress(db_path="../../data/transcription_progress.db"):
    """Check and display current progress"""

    if not os.path.exists(db_path):
        print(f"[X] Database not found: {db_path}")
        print("   No transcription has been started yet.")
        print(f"   Looking for: {os.path.abspath(db_path)}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("TRANSCRIPTION PROGRESS REPORT")
    print("=" * 80)
    print()

    # Overall statistics
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'downloading' THEN 1 ELSE 0 END) as downloading,
            SUM(CASE WHEN status = 'downloaded' THEN 1 ELSE 0 END) as downloaded,
            SUM(CASE WHEN status = 'transcribing' THEN 1 ELSE 0 END) as transcribing,
            SUM(duration) as total_duration,
            SUM(CASE WHEN status = 'completed' THEN duration ELSE 0 END) as completed_duration
        FROM videos
    ''')

    stats = cursor.fetchone()
    total, completed, errors, pending, downloading, downloaded, transcribing, total_dur, comp_dur = stats

    if total == 0:
        print("No videos found in database.")
        conn.close()
        return

    # Progress percentage
    progress = (completed / total * 100) if total > 0 else 0

    print(f"[STATS] OVERALL STATISTICS")
    print("-" * 80)
    print(f"Total Videos:          {total}")
    print(f"Completed:             {completed} ({progress:.1f}%)")
    print(f"Pending:               {pending}")
    print(f"Downloading:           {downloading}")
    print(f"Downloaded:            {downloaded}")
    print(f"Transcribing:          {transcribing}")
    print(f"Errors:                {errors}")
    print()
    print(f"Total Duration:        {format_duration(total_dur or 0)}")
    print(f"Completed Duration:    {format_duration(comp_dur or 0)}")
    print()

    # Progress bar
    bar_length = 50
    filled = int(bar_length * progress / 100)
    bar = "#" * filled + "-" * (bar_length - filled)
    print(f"Progress: [{bar}] {progress:.1f}%")
    print()

    # Status breakdown
    print(f"[STATUS] STATUS BREAKDOWN")
    print("-" * 80)
    cursor.execute('''
        SELECT status, COUNT(*), SUM(duration)
        FROM videos
        GROUP BY status
        ORDER BY COUNT(*) DESC
    ''')

    for row in cursor.fetchall():
        status, count, duration = row
        dur_str = format_duration(duration or 0)
        print(f"  {status:12s}: {count:4d} videos  ({dur_str})")
    print()

    # Recent completed videos
    print(f"[DONE] RECENTLY COMPLETED (Last 10)")
    print("-" * 80)
    cursor.execute('''
        SELECT title, duration, updated_at
        FROM videos
        WHERE status = 'completed'
        ORDER BY updated_at DESC
        LIMIT 10
    ''')

    completed_videos = cursor.fetchall()
    if completed_videos:
        for title, duration, updated in completed_videos:
            dur_str = format_duration(duration or 0)
            title_short = title[:60] + "..." if len(title) > 60 else title
            print(f"  • {title_short}")
            print(f"    Duration: {dur_str} | Completed: {updated}")
    else:
        print("  No videos completed yet.")
    print()

    # Errors (if any)
    cursor.execute('''
        SELECT COUNT(*) FROM videos WHERE status = 'error'
    ''')
    error_count = cursor.fetchone()[0]

    if error_count > 0:
        print(f"[ERROR] ERRORS ({error_count} videos)")
        print("-" * 80)
        cursor.execute('''
            SELECT title, error_message, updated_at
            FROM videos
            WHERE status = 'error'
            ORDER BY updated_at DESC
            LIMIT 5
        ''')

        for title, error_msg, updated in cursor.fetchall():
            title_short = title[:60] + "..." if len(title) > 60 else title
            error_short = error_msg[:80] + "..." if error_msg and len(error_msg) > 80 else error_msg
            print(f"  • {title_short}")
            print(f"    Error: {error_short}")
            print(f"    Time: {updated}")
        print()

    # Channel info
    cursor.execute('SELECT DISTINCT channel FROM videos')
    channels = cursor.fetchall()
    if channels:
        print(f"[CHANNELS] CHANNELS")
        print("-" * 80)
        for channel in channels:
            channel_name = channel[0]
            cursor.execute('''
                SELECT COUNT(*), SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
                FROM videos WHERE channel = ?
            ''', (channel_name,))
            ch_total, ch_completed = cursor.fetchone()
            ch_progress = (ch_completed / ch_total * 100) if ch_total > 0 else 0
            print(f"  {channel_name}: {ch_completed}/{ch_total} ({ch_progress:.1f}%)")
        print()

    # ETA estimation
    if completed > 0 and pending > 0:
        cursor.execute('''
            SELECT AVG(CAST((julianday(updated_at) - julianday(created_at)) * 24 * 60 AS REAL))
            FROM videos
            WHERE status = 'completed'
        ''')
        avg_time = cursor.fetchone()[0]

        if avg_time and avg_time > 0:
            remaining_time = avg_time * pending
            print(f"[ETA] ESTIMATED TIME REMAINING")
            print("-" * 80)
            print(f"  Average time per video: {avg_time:.1f} minutes")
            print(f"  Estimated completion:   {remaining_time:.0f} minutes ({remaining_time/60:.1f} hours)")
            print()

    # Word count statistics
    print(f"[WORDS] TRANSCRIPTION STATISTICS")
    print("-" * 80)

    cursor.execute('SELECT transcript_path FROM videos WHERE status = "completed" AND transcript_path IS NOT NULL')
    transcript_paths = cursor.fetchall()

    total_words = 0
    total_file_size = 0
    transcript_count = 0

    for (transcript_path,) in transcript_paths:
        if transcript_path and os.path.exists(transcript_path):
            try:
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    words = len(content.split())
                    total_words += words
                    total_file_size += os.path.getsize(transcript_path)
                    transcript_count += 1
            except Exception:
                pass

    if transcript_count > 0:
        print(f"  Total Words:           {total_words:,} words")
        print(f"  Average Words/Video:   {total_words//transcript_count:,} words")
        print(f"  Total Transcript Size: {total_file_size/1024/1024:.1f} MB")
    else:
        print(f"  No transcripts completed yet.")
    print()

    # Database info
    db_size = os.path.getsize(db_path) / 1024
    print(f"[DB] DATABASE INFO")
    print("-" * 80)
    print(f"  File: {db_path}")
    print(f"  Size: {db_size:.2f} KB")
    print()

    print("=" * 80)
    print("[TIP] Run 'python run_transcriber.py' to resume processing")
    print("=" * 80)

    conn.close()

if __name__ == "__main__":
    check_progress()
