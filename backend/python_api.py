#!/usr/bin/env python3
import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.join(PROJECT_ROOT, 'vendor')
if os.path.isdir(VENDOR_DIR):
    sys.path.insert(0, VENDOR_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from youtube_downloader import download_youtube_media

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

app = FastAPI(title='YouTube Converter API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class DownloadRequest(BaseModel):
    url: str
    mode: str = 'mp3'


@app.get('/api/health')
def health_check():
    return {'ok': True, 'status': 'online'}


@app.post('/api/download')
def download_video(payload: DownloadRequest):
    url = payload.url.strip()
    mode = payload.mode.lower() if payload.mode else 'mp3'

    if not url or not re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/', url, flags=re.I):
        raise HTTPException(status_code=400, detail='Bitte gib eine gültige YouTube-URL ein.')

    if mode not in ('mp3', 'mp4'):
        mode = 'mp3'

    try:
        result = download_youtube_media(url, mode=mode)
        return {
            'ok': True,
            'mode': mode,
            'message': f'Download für {mode.upper()} wurde gestartet.',
            'result': result,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('python_api:app', host='127.0.0.1', port=3001, reload=False)
