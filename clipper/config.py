from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
ANALYSIS_DIR = DATA_DIR / "analysis"
MODELS_DIR = DATA_DIR / "models"
OUT_MEDIUM_RAW_DIR = DATA_DIR / "out" / "medium_raw"
OUT_MEDIUM_DIR = DATA_DIR / "out" / "medium"
OUT_SHORT_DIR = DATA_DIR / "out" / "short"

for d in (RAW_DIR, TRANSCRIPTS_DIR, ANALYSIS_DIR, MODELS_DIR, OUT_MEDIUM_RAW_DIR, OUT_MEDIUM_DIR, OUT_SHORT_DIR):
    d.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    llm_backend: str = os.environ.get("CLIPPER_LLM_BACKEND", "ollama")  # "ollama" (free/local) or "anthropic"

    anthropic_api_key: str | None = os.environ.get("ANTHROPIC_API_KEY")
    claude_model: str = os.environ.get("CLIPPER_CLAUDE_MODEL", "claude-sonnet-4-5")

    ollama_model: str = os.environ.get("CLIPPER_OLLAMA_MODEL", "llama3.1:8b")
    ollama_host: str = os.environ.get("CLIPPER_OLLAMA_HOST", "http://localhost:11434")
    whisper_model_size: str = os.environ.get("CLIPPER_WHISPER_MODEL", "small")
    whisper_device: str = os.environ.get("CLIPPER_WHISPER_DEVICE", "cpu")
    whisper_compute_type: str = os.environ.get("CLIPPER_WHISPER_COMPUTE", "int8")

    medium_target_seconds: float = 60.0
    medium_min_seconds: float = 40.0
    medium_max_seconds: float = 90.0

    short_min_seconds: float = 10.0
    short_max_seconds: float = 30.0

    scene_detector_threshold: float = 27.0
    silence_noise_db: float = -30.0
    silence_min_duration: float = 0.4

    reframe_aspect_ratio: float = 9.0 / 16.0
    reframe_sample_fps: float = 3.0
    reframe_smoothing_window: int = 9


SETTINGS = Settings()
