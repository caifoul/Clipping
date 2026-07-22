from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# Celery workers run synchronously; the FastAPI app uses the async engine in
# app/db.py instead. Both point at the same database.
_sync_url = settings.database_url.replace("+asyncpg", "+psycopg")
sync_engine = create_engine(_sync_url, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)


def sync_session() -> Session:
    return SyncSessionLocal()
