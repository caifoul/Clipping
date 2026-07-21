from __future__ import annotations

import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from ..config import DATA_DIR
from ..pipeline import run_pipeline

_OUT_DIR = DATA_DIR / "out"


def _clip_info(path: Path) -> dict:
    sidecar = path.with_suffix(".json")
    data = json.loads(sidecar.read_text(encoding="utf-8")) if sidecar.exists() else {}
    relative = path.relative_to(_OUT_DIR).as_posix()
    return {"url": f"/media/{relative}", **data}


@dataclass
class Job:
    id: str
    status: str = "queued"  # queued, running, done, error
    stages: list[str] = field(default_factory=list)
    error: str | None = None
    medium_clips: list[dict] = field(default_factory=list)
    short_clips: list[dict] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def append_stage(self, stage: str) -> None:
        with self._lock:
            self.stages.append(stage)

    def to_dict(self) -> dict:
        with self._lock:
            return {
                "id": self.id,
                "status": self.status,
                "stages": list(self.stages),
                "error": self.error,
                "medium_clips": self.medium_clips,
                "short_clips": self.short_clips,
            }


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._executor = ThreadPoolExecutor(max_workers=1)

    def submit(self, url: str, topic: str, max_segments: int) -> str:
        job_id = uuid.uuid4().hex[:12]
        job = Job(id=job_id)
        self._jobs[job_id] = job
        self._executor.submit(self._run, job, url, topic, max_segments)
        return job_id

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def _run(self, job: Job, url: str, topic: str, max_segments: int) -> None:
        job.status = "running"
        try:
            result = run_pipeline(url, topic, max_medium=max_segments, on_stage=job.append_stage)
            job.medium_clips = [_clip_info(p) for p in result.medium]
            job.short_clips = [_clip_info(p) for p in result.short]
            job.status = "done"
        except Exception as exc:  # noqa: BLE001 - surface any failure to the UI
            job.error = str(exc)
            job.status = "error"


job_manager = JobManager()
