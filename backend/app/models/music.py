from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class MusicAction(str, enum.Enum):
    mute = "mute"
    duck = "duck"


class MusicSegment(UUIDPKMixin, TimestampMixin, Base):
    """Heuristic background-music detection, not a rights-database match.

    Used to mute likely-copyrighted background music in renders; see plan
    risk note on false positives/negatives.
    """

    __tablename__ = "music_segments"

    source_video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_videos.id", ondelete="CASCADE"), index=True
    )
    start_seconds: Mapped[float] = mapped_column(Float)
    end_seconds: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    action: Mapped[MusicAction] = mapped_column(
        Enum(MusicAction, name="music_action"), default=MusicAction.mute
    )
