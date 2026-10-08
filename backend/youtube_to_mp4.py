#!/usr/bin/env python3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from youtube_downloader import download_youtube_media

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python youtube_to_mp4.py <YouTube_URL_or_ID>')
        sys.exit(1)

    try:
        download_youtube_media(sys.argv[1], mode='mp4')
    except Exception as exc:
        print(f'❌ Error: {exc}')
        sys.exit(1)
