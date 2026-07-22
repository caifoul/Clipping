from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class ClipStatus(str, enum.Enum):
    selected = "selected"
    rendering = "rendering"
    rendered = "rendered"
    failed = "failed"


class CropStrategy(str, enum.Enum):
    static_center = "static_center"
    face_tracked = "face_tracked"


class ShortClip(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "short_clips"

    long_form_export_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("long_form_exports.id", ondelete="CASCADE"), index=True
    )
    start_seconds: Mapped[float] = mapped_column(Float)
    end_seconds: Mapped[float] = mapped_column(Float)
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    selection_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    hook_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    crop_strategy: Mapped[CropStrategy] = mapped_column(
        Enum(CropStrategy, name="crop_strategy"), default=CropStrategy.static_center
    )
    status: Mapped[ClipStatus] = mapped_column(
        Enum(ClipStatus, name="clip_status"), default=ClipStatus.selected
    )


class MicroClip(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "micro_clips"

    short_clip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("short_clips.id", ondelete="CASCADE"), index=True
    )
    start_seconds: Mapped[float] = mapped_column(Float)
    end_seconds: Mapped[float] = mapped_column(Float)
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    selection_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ClipStatus] = mapped_column(
        Enum(ClipStatus, name="micro_clip_status"), default=ClipStatus.selected
    )
