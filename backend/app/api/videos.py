from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db import get_db
from app.models.source_video import SourceType, SourceVideo, SourceVideoStatus
from app.models.user import User
from app.schemas.video import SourceVideoCreateResponse, SourceVideoOut
from app.services.storage import save_upload, source_video_dir
from app.tasks.ingest import ingest_source_video

router = APIRouter(prefix="/api/videos", tags=["videos"])


async def get_owned_video(
    video_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SourceVideo:
    video = await db.get(SourceVideo, video_id)
    if video is None or video.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="video not found")
    return video


@router.post("", response_model=SourceVideoCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    url: str | None = Form(None),
    file: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SourceVideoCreateResponse:
    if not url and not file:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="provide either 'url' or 'file'",
        )
    if url and file:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="provide only one of 'url' or 'file'",
        )

    video = SourceVideo(
        user_id=user.id,
        source_type=SourceType.youtube_url if url else SourceType.upload,
        source_url=url,
        original_filename=file.filename if file else None,
        status=SourceVideoStatus.pending,
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    if file:
        source_video_dir(video.id)  # ensure dir exists before streaming to it
        save_upload(video.id, file.filename or "upload.mp4", file.file)

    ingest_source_video.delay(str(video.id))

    return SourceVideoCreateResponse(source_video_id=video.id)


@router.get("", response_model=list[SourceVideoOut])
async def list_videos(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[SourceVideo]:
    result = await db.scalars(
        select(SourceVideo)
        .where(SourceVideo.user_id == user.id)
        .order_by(SourceVideo.created_at.desc())
    )
    return list(result)


@router.get("/{video_id}", response_model=SourceVideoOut)
async def get_video(video: SourceVideo = Depends(get_owned_video)) -> SourceVideo:
    return video
