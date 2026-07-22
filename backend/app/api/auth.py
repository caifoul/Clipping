from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.db import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest, UserOut
from app.services.auth_service import create_session_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, user_id) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=create_session_token(user_id),
        max_age=settings.session_max_age_seconds,
        httponly=True,
        samesite="lax",
    )


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(
    body: SignupRequest, response: Response, db: AsyncSession = Depends(get_db)
) -> User:
    existing = await db.scalar(select(User).where(User.email == body.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")

    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)

    _set_session_cookie(response, user.id)
    return user


@router.post("/login", response_model=UserOut)
async def login(
    body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
) -> User:
    user = await db.scalar(select(User).where(User.email == body.email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    _set_session_cookie(response, user.id)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(settings.session_cookie_name)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> User:
    return user
