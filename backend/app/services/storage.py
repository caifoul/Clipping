from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from app.config import settings


def source_video_dir(source_video_id: uuid.UUID) -> Path:
    path = settings.media_root / "source" / str(source_video_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload(source_video_id: uuid.UUID, filename: str, fileobj) -> Path:
    """Stream an uploaded file to disk. Never holds the whole file in memory."""
    suffix = Path(filename).suffix or ".mp4"
    dest = source_video_dir(source_video_id) / f"original{suffix}"
    with dest.open("wb") as out:
        shutil.copyfileobj(fileobj, out)
    return dest


def export_dir(source_video_id: uuid.UUID) -> Path:
    path = settings.media_root / "exports" / str(source_video_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clips_dir(export_id: uuid.UUID) -> Path:
    path = settings.media_root / "clips" / str(export_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def to_media_url(path: Path) -> str:
    relative = path.relative_to(settings.media_root)
    return f"/media/{relative.as_posix()}"
