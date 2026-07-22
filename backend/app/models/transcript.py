from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class Transcript(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "transcripts"

    source_video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source_videos.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(64))
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    # Array of {start, end, text, words: [{word, start, end}]} from Whisper verbose_json.
    segments: Mapped[list] = mapped_column(JSONB, default=list)
    full_text: Mapped[str] = mapped_column(Text, default="")
