from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class SourceType(str, enum.Enum):
    youtube_url = "youtube_url"
    upload = "upload"


class SourceVideoStatus(str, enum.Enum):
    pending = "pending"
    downloading = "downloading"
    downloaded = "downloaded"
    failed = "failed"


class SourceVideo(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "source_videos"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType, name="source_type"))
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)

    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[SourceVideoStatus] = mapped_column(
        Enum(SourceVideoStatus, name="source_video_status"),
        default=SourceVideoStatus.pending,
    )
    error_message: Mapped[str | None] = mapped_column(String(2048), nullable=True)
