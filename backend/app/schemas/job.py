from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.job import JobStatus, JobType


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_type: JobType
    status: JobStatus
    progress_pct: int | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
