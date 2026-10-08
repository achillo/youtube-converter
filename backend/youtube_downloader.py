import glob
import os
import re
import shutil
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import yt_dlp

COMMON_FFMPEG_LOCATIONS = [
    'C:/ffmpeg/bin',
    'C:/Program Files/ffmpeg/bin',
    'C:/Program Files/FFmpeg/bin',
    'C:/Program Files (x86)/ffmpeg/bin',
    '/usr/local/bin',
    '/usr/bin',
    '/opt/homebrew/bin',
]

OUTPUT_DIR = os.path.join(os.getcwd(), 'current_download')


def normalize_url(value: str) -> str:
    if not value or not value.strip():
        raise ValueError('No YouTube URL or video ID was provided.')

    candidate = value.strip()
    if '://' in candidate:
        return candidate

    if re.fullmatch(r'[A-Za-z0-9_-]{11}', candidate):
        return f'https://www.youtube.com/watch?v={candidate}'

    raise ValueError(f'Invalid YouTube URL or video ID: {value}')


def sanitize_file_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', '', str(name))


def ensure_output_dir(folder: str = OUTPUT_DIR) -> str:
    os.makedirs(folder, exist_ok=True)
    return folder


def find_binary(binary_name: str) -> str | None:
    executable = shutil.which(binary_name) or shutil.which(f'{binary_name}.exe')
    if executable:
        return executable

    for folder in COMMON_FFMPEG_LOCATIONS:
        candidate = os.path.join(folder, binary_name)
        if os.path.isfile(candidate):
            return candidate
        win_candidate = os.path.join(folder, f'{binary_name}.exe')
        if os.path.isfile(win_candidate):
            return win_candidate

    local_packages_root = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages')
    if os.path.isdir(local_packages_root):
        pattern = os.path.join(local_packages_root, '*', '*', 'bin', f'{binary_name}.exe')
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
        pattern = os.path.join(local_packages_root, '*', 'bin', f'{binary_name}.exe')
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]

    return None


def get_ffmpeg_paths() -> tuple[str, str]:
    ffmpeg_path = find_binary('ffmpeg')
    ffprobe_path = find_binary('ffprobe')

    if ffmpeg_path is None or ffprobe_path is None:
        raise EnvironmentError(
            'FFmpeg/FFprobe was not found. Please install FFmpeg on the server and ensure it is on PATH. '
            'Example: apt install ffmpeg on Linux or winget install Gyan.Dev.FFmpeg on Windows.'
        )

    return ffmpeg_path, ffprobe_path


def download_youtube_media(url: str, mode: str = 'mp3', output_dir: str = OUTPUT_DIR) -> str:
    final_url = normalize_url(url)
    ensure_output_dir(output_dir)

    with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'noplaylist': True}) as info_dl:
        info = info_dl.extract_info(final_url, download=False)

    title = sanitize_file_name(info.get('title') or 'youtube-video')
    target_file = os.path.join(output_dir, f'{title}.mp3' if mode == 'mp3' else f'{title}.mp4')

    ffmpeg_path, ffprobe_path = get_ffmpeg_paths()

    opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'ffmpeg_location': os.path.dirname(ffmpeg_path),
        'ffprobe_location': os.path.dirname(ffprobe_path),
    }

    if mode == 'mp3':
        opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
        })
    elif mode == 'mp4':
        opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        })
    else:
        raise ValueError(f'Unsupported mode: {mode}. Use "mp3" or "mp4".')

    print(f'⬇️ Downloading {mode.upper()} for: {title}')
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([final_url])

    if os.path.exists(target_file):
        print(f'✅ Saved: {target_file}')
        return target_file

    fallback = os.path.join(output_dir, f'{title}.webm' if mode == 'mp3' else f'{title}.mkv')
    if os.path.exists(fallback):
        print(f'✅ Saved: {fallback}')
        return fallback

    print(f'✅ Download finished. Check directory: {output_dir}')
    return target_file


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python youtube_downloader.py <YouTube_URL_or_ID> [mp3|mp4]')
        sys.exit(1)

    mode = (sys.argv[2] if len(sys.argv) > 2 else 'mp3').lower()
    try:
        download_youtube_media(sys.argv[1], mode)
    except Exception as exc:
        print(f'❌ Error: {exc}')
        sys.exit(1)
