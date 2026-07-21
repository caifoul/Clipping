from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..config import DATA_DIR
from .jobs import job_manager

STATIC_DIR = Path(__file__).parent / "static"
OUT_DIR = DATA_DIR / "out"

app = FastAPI(title="Clipper")


class JobRequest(BaseModel):
    url: str
    topic: str
    max_segments: int = 5


@app.post("/api/jobs")
def create_job(req: JobRequest) -> dict:
    job_id = job_manager.submit(req.url, req.topic, req.max_segments)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job.to_dict()


app.mount("/media", StaticFiles(directory=str(OUT_DIR)), name="media")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
