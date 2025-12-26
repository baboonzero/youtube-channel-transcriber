"""
Export YouTube cookies from your browser for Modal
Run this once to create a cookies.txt file
"""

import subprocess
import sys

def export_cookies():
    """
    Export cookies from your browser using yt-dlp
    """
    print("="*70)
    print("YouTube Cookies Exporter")
    print("="*70)
    print()
    print("This will export YouTube cookies from your browser.")
    print("Choose your browser:")
    print()
    print("1. Chrome")
    print("2. Firefox")
    print("3. Edge")
    print("4. Brave")
    print()

    choice = input("Enter number (1-4): ").strip()

    browser_map = {
        '1': 'chrome',
        '2': 'firefox',
        '3': 'edge',
        '4': 'brave',
    }

    browser = browser_map.get(choice)
    if not browser:
        print("Invalid choice!")
        return

    print(f"\nExporting cookies from {browser.capitalize()}...")
    print("(This may take a few seconds)")
    print()

    try:
        # Use yt-dlp to export cookies
        cmd = [
            'yt-dlp',
            '--cookies-from-browser', browser,
            '--cookies', 'youtube_cookies.txt',
            'https://www.youtube.com',
            '--skip-download',
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Cookies exported successfully!")
            print()
            print("File created: youtube_cookies.txt")
            print()
            print("NOTE: This is for LOCAL downloads only (yt-dlp on your machine)")
            print("The hybrid Modal approach downloads locally, so it will use")
            print("your browser cookies automatically - no need to pass them explicitly.")
            print()
            print("If you need to use cookies with yt-dlp directly, you can:")
            print("  yt-dlp --cookies youtube_cookies.txt <youtube_url>")
            print()
        else:
            print("✗ Failed to export cookies")
            print()
            print("Error:", result.stderr)
            print()
            print("Make sure:")
            print("1. You're logged into YouTube in your browser")
            print("2. yt-dlp is installed: pip install yt-dlp")
            print("3. Your browser is closed (sometimes required)")

    except FileNotFoundError:
        print("✗ yt-dlp not found!")
        print()
        print("Install it with: pip install yt-dlp")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    export_cookies()
