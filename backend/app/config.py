from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "dev-secret-key-change-me"
    database_url: str = "postgresql+asyncpg://clipping:clipping@localhost:5432/clipping"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    openai_api_key: str = ""

    media_root: Path = Path("./data/media")

    session_cookie_name: str = "clipping_session"
    session_max_age_seconds: int = 60 * 60 * 24 * 30  # 30 days

    # Whisper API hard-rejects requests with an audio payload larger than this.
    whisper_max_bytes: int = 25 * 1024 * 1024

    short_clip_min_seconds: float = 60.0
    short_clip_max_seconds: float = 75.0
    micro_clip_target_seconds: float = 8.0


settings = Settings()
settings.media_root.mkdir(parents=True, exist_ok=True)
