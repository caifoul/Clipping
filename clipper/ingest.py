from __future__ import annotations

import json
from pathlib import Path

import yt_dlp

from .config import RAW_DIR


def _ydl_opts(**overrides) -> dict:
    opts = {
        "format": "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/best",
        "outtmpl": str(RAW_DIR / "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "retries": 10,
        "fragment_retries": 10,
        "http_chunk_size": 10 * 1024 * 1024,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    }
    opts.update(overrides)
    return opts


def ingest(url: str) -> tuple[str, Path]:
    """Download a YouTube/Twitch VOD (cached by video id). Returns (video_id, mp4_path)."""
    with yt_dlp.YoutubeDL(_ydl_opts(download=False)) as probe:
        info = probe.extract_info(url, download=False)
    video_id = info["id"]
    video_path = RAW_DIR / f"{video_id}.mp4"
    info_path = RAW_DIR / f"{video_id}.info.json"

    if video_path.exists() and info_path.exists():
        return video_id, video_path

    with yt_dlp.YoutubeDL(_ydl_opts()) as ydl:
        full_info = ydl.extract_info(url, download=True)

    info_path.write_text(
        json.dumps(
            {
                "id": full_info.get("id"),
                "title": full_info.get("title"),
                "uploader": full_info.get("uploader"),
                "duration": full_info.get("duration"),
                "webpage_url": full_info.get("webpage_url"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return video_id, video_path
