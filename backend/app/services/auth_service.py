from __future__ import annotations

import uuid

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from passlib.context import CryptContext

from app.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_serializer = URLSafeTimedSerializer(settings.secret_key, salt="clipping-session")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


def create_session_token(user_id: uuid.UUID) -> str:
    return _serializer.dumps({"user_id": str(user_id)})


def read_session_token(token: str) -> uuid.UUID | None:
    try:
        data = _serializer.loads(token, max_age=settings.session_max_age_seconds)
    except (BadSignature, SignatureExpired):
        return None
    try:
        return uuid.UUID(data["user_id"])
    except (KeyError, ValueError, TypeError):
        return None
