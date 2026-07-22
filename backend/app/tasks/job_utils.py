from __future__ import annotations

import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus, JobType
from app.tasks.db import sync_session


@contextmanager
def job_run(source_video_id: uuid.UUID, job_type: JobType, celery_task_id: str | None):
    """Create a Job row, mark it running/succeeded/failed, yield the db session.

    Every pipeline stage should wrap its work in this so the API always has
    a Job row to poll status from.
    """
    db: Session = sync_session()
    job = Job(
        source_video_id=source_video_id,
        job_type=job_type,
        celery_task_id=celery_task_id,
        status=JobStatus.running,
        started_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        yield db, job
    except Exception as exc:
        job.status = JobStatus.failed
        job.error_message = str(exc)
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.close()
        raise
    else:
        job.status = JobStatus.succeeded
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.close()
