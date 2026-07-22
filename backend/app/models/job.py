from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class JobType(str, enum.Enum):
    ingest = "ingest"
    transcribe = "transcribe"
    detect_silence = "detect_silence"
    detect_music = "detect_music"
    analyze = "analyze"
    render_longform = "render_longform"
    select_tiktok = "select_tiktok"
    render_tiktok = "render_tiktok"
    select_micro = "select_micro"
    render_micro = "render_micro"


class JobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class Job(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    source_video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_videos.id", ondelete="CASCADE"), index=True
    )
    job_type: Mapped[JobType] = mapped_column(Enum(JobType, name="job_type"))
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), default=JobStatus.queued
    )
    progress_pct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
