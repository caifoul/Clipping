from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class CutReason(str, enum.Enum):
    silence = "silence"
    filler_word = "filler_word"
    false_start = "false_start"
    dead_air = "dead_air"
    redundant = "redundant"


class CutDetectedBy(str, enum.Enum):
    ffmpeg_silence = "ffmpeg_silence"
    claude = "claude"


class CutDecision(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class RecommendedCut(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "recommended_cuts"

    source_video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_videos.id", ondelete="CASCADE"), index=True
    )
    start_seconds: Mapped[float] = mapped_column(Float)
    end_seconds: Mapped[float] = mapped_column(Float)
    reason: Mapped[CutReason] = mapped_column(Enum(CutReason, name="cut_reason"))
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    detected_by: Mapped[CutDetectedBy] = mapped_column(
        Enum(CutDetectedBy, name="cut_detected_by")
    )
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_decision: Mapped[CutDecision] = mapped_column(
        Enum(CutDecision, name="cut_decision"), default=CutDecision.pending
    )
