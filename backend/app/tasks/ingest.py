from __future__ import annotations

import uuid

from app.media.ffmpeg import probe_duration_seconds
from app.media.ytdlp import download_video
from app.models.job import JobType
from app.models.source_video import SourceType, SourceVideo, SourceVideoStatus
from app.services.storage import source_video_dir
from app.tasks.celery_app import celery_app
from app.tasks.job_utils import job_run


@celery_app.task(name="app.tasks.ingest.ingest_source_video", bind=True)
def ingest_source_video(self, source_video_id: str) -> None:
    video_id = uuid.UUID(source_video_id)

    with job_run(video_id, JobType.ingest, self.request.id) as (db, _job):
        video = db.get(SourceVideo, video_id)
        if video is None:
            raise ValueError(f"SourceVideo {video_id} not found")

        try:
            video.status = SourceVideoStatus.downloading
            db.commit()

            dest_dir = source_video_dir(video_id)

            if video.source_type == SourceType.youtube_url:
                if not video.source_url:
                    raise ValueError("youtube_url source is missing source_url")
                downloaded_path = download_video(video.source_url, dest_dir)
            else:
                candidates = sorted(dest_dir.glob("original.*"))
                if not candidates:
                    raise FileNotFoundError(
                        f"no uploaded file found in {dest_dir} for upload source"
                    )
                downloaded_path = candidates[0]

            duration = probe_duration_seconds(downloaded_path)

            video.storage_path = str(downloaded_path)
            video.duration_seconds = duration
            video.status = SourceVideoStatus.downloaded
            db.commit()
        except Exception as exc:
            video.status = SourceVideoStatus.failed
            video.error_message = str(exc)
            db.commit()
            raise
