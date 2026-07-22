from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.videos import get_owned_video
from app.db import get_db
from app.models.job import Job
from app.models.source_video import SourceVideo
from app.models.user import User
from app.schemas.job import JobOut

router = APIRouter(tags=["jobs"])


@router.get("/api/videos/{video_id}/jobs", response_model=list[JobOut])
async def list_jobs_for_video(
    video: SourceVideo = Depends(get_owned_video), db: AsyncSession = Depends(get_db)
) -> list[Job]:
    result = await db.scalars(
        select(Job).where(Job.source_video_id == video.id).order_by(Job.created_at.asc())
    )
    return list(result)


@router.get("/api/jobs/{job_id}", response_model=JobOut)
async def get_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Job:
    job = await db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")

    video = await db.get(SourceVideo, job.source_video_id)
    if video is None or video.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")

    return job
