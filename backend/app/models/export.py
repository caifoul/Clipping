from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class LongFormExport(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "long_form_exports"

    source_video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_videos.id", ondelete="CASCADE"), index=True
    )
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    captions_srt_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    captions_vtt_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    captions_burned_in: Mapped[bool] = mapped_column(Boolean, default=False)
    # Snapshot of RecommendedCut ids accepted at render time (not a live FK)
    # so later edits to cuts don't retroactively alter export history.
    applied_cut_ids: Mapped[list] = mapped_column(JSONB, default=list)
    title_used: Mapped[str | None] = mapped_column(String(512), nullable=True)
    chapters_used: Mapped[list] = mapped_column(JSONB, default=list)
