#!/usr/bin/env python3
"""
Reset/Clear a specific channel's data from the database

This is useful when:
- Switching to a new channel
- Want to re-download a channel from scratch
- Old channel data is interfering with new channel

Usage:
    python reset_channel.py "Channel Name"
    python reset_channel.py --list  # List all channels
    python reset_channel.py --clear-all  # Clear everything
"""

import sys
import os
from pathlib import Path
import sqlite3

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "config"))
os.chdir(project_root)

from config import DATABASE_FILE

def list_channels():
    """List all channels in the database"""
    db_path = Path(DATABASE_FILE)
    if not db_path.exists():
        print("No database found!")
        return []

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute('''
        SELECT channel, COUNT(*) as video_count,
               SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
               SUM(CASE WHEN status='downloaded' THEN 1 ELSE 0 END) as downloaded,
               SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending
        FROM videos
        WHERE channel IS NOT NULL
        GROUP BY channel
    ''')

    channels = cursor.fetchall()
    conn.close()

    return channels

def reset_channel(channel_name):
    """Reset all videos for a specific channel to pending status"""
    db_path = Path(DATABASE_FILE)
    if not db_path.exists():
        print("No database found!")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Check if channel exists
    cursor.execute('SELECT COUNT(*) FROM videos WHERE channel = ?', (channel_name,))
    count = cursor.fetchone()[0]

    if count == 0:
        print(f"Channel '{channel_name}' not found in database!")
        conn.close()
        return

    print(f"\nResetting {count} videos for channel: {channel_name}")
    print("This will:")
    print("  - Set status to 'pending'")
    print("  - Clear audio_path")
    print("  - Clear transcript_path")
    print()

    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        conn.close()
        return

    # Reset the channel
    cursor.execute('''
        UPDATE videos
        SET status = 'pending',
            audio_path = NULL,
            transcript_path = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE channel = ?
    ''', (channel_name,))

    conn.commit()
    updated = cursor.rowcount
    conn.close()

    print(f"\n✅ Reset {updated} videos for '{channel_name}'")
    print("You can now run prepare_for_modal.py to re-download this channel")

def delete_channel(channel_name):
    """Completely delete all videos for a specific channel"""
    db_path = Path(DATABASE_FILE)
    if not db_path.exists():
        print("No database found!")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Check if channel exists
    cursor.execute('SELECT COUNT(*) FROM videos WHERE channel = ?', (channel_name,))
    count = cursor.fetchone()[0]

    if count == 0:
        print(f"Channel '{channel_name}' not found in database!")
        conn.close()
        return

    print(f"\n⚠️  WARNING: Deleting {count} videos for channel: {channel_name}")
    print("This will PERMANENTLY DELETE all records for this channel!")
    print()

    response = input("Are you sure? Type the channel name to confirm: ")
    if response != channel_name:
        print("Cancelled.")
        conn.close()
        return

    # Delete the channel
    cursor.execute('DELETE FROM videos WHERE channel = ?', (channel_name,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    print(f"\n✅ Deleted {deleted} videos for '{channel_name}'")

def clear_all():
    """Clear the entire database"""
    db_path = Path(DATABASE_FILE)
    if not db_path.exists():
        print("No database found!")
        return

    print("\n⚠️  WARNING: This will DELETE ALL DATA from the database!")
    print()
    response = input("Are you ABSOLUTELY sure? Type 'DELETE ALL' to confirm: ")
    if response != "DELETE ALL":
        print("Cancelled.")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute('DELETE FROM videos')
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    print(f"\n✅ Deleted {deleted} videos from database")

def main():
    if len(sys.argv) == 1:
        print("Usage:")
        print("  python reset_channel.py --list              # List all channels")
        print("  python reset_channel.py 'Channel Name'      # Reset a channel")
        print("  python reset_channel.py --delete 'Channel'  # Delete a channel")
        print("  python reset_channel.py --clear-all         # Clear everything")
        sys.exit(0)

    if sys.argv[1] == '--list':
        channels = list_channels()
        if not channels:
            print("No channels found in database")
            return

        print("\nChannels in database:")
        print("=" * 80)
        for channel, total, completed, downloaded, pending in channels:
            print(f"\n{channel}")
            print(f"  Total videos: {total}")
            print(f"  Completed:    {completed}")
            print(f"  Downloaded:   {downloaded}")
            print(f"  Pending:      {pending}")
        print("\n" + "=" * 80)

    elif sys.argv[1] == '--clear-all':
        clear_all()

    elif sys.argv[1] == '--delete':
        if len(sys.argv) < 3:
            print("Error: Please specify channel name")
            print("Example: python reset_channel.py --delete 'Channel Name'")
            sys.exit(1)
        delete_channel(sys.argv[2])

    else:
        # Reset channel
        channel_name = sys.argv[1]
        reset_channel(channel_name)

if __name__ == "__main__":
    main()
