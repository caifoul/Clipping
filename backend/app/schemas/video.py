from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.source_video import SourceType, SourceVideoStatus


class SourceVideoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_type: SourceType
    source_url: str | None
    original_filename: str | None
    title: str | None
    duration_seconds: float | None
    status: SourceVideoStatus
    error_message: str | None
    created_at: datetime


class SourceVideoCreateResponse(BaseModel):
    source_video_id: uuid.UUID
