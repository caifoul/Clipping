from __future__ import annotations

from celery import Celery

from app.config import settings

celery_app = Celery(
    "clipping",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.ingest"],
)

celery_app.conf.update(
    task_routes={
        "app.tasks.ingest.*": {"queue": "io"},
        "app.tasks.transcribe.*": {"queue": "io"},
        "app.tasks.analyze.*": {"queue": "io"},
        "app.tasks.select_tiktok.*": {"queue": "io"},
        "app.tasks.select_micro.*": {"queue": "io"},
        "app.tasks.detect_silence.*": {"queue": "cpu"},
        "app.tasks.detect_music.*": {"queue": "cpu"},
        "app.tasks.render_longform.*": {"queue": "cpu"},
        "app.tasks.render_tiktok.*": {"queue": "cpu"},
        "app.tasks.render_micro.*": {"queue": "cpu"},
    },
    task_track_started=True,
)
