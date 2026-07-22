from __future__ import annotations

import json
from pathlib import Path

import typer

from . import ingest as ingest_module
from . import transcribe as transcribe_module
from .config import RAW_DIR
from .pipeline import analyze, make_medium_clip, make_short_clip, run_pipeline
from .medium_select import select_medium_segments

app = typer.Typer(help="AI-assisted long-form -> medium-form -> short-form video clipper")


@app.command(name="ingest")
def ingest_cmd(url: str):
    """Download a YouTube/Twitch VOD."""
    video_id, path = ingest_module.ingest(url)
    typer.echo(f"Downloaded {video_id} -> {path}")


@app.command(name="transcribe")
def transcribe_cmd(path: Path):
    """Transcribe a local video file."""
    video_id = path.stem
    transcript = transcribe_module.transcribe(video_id, path)
    typer.echo(f"Transcribed {video_id}: {len(transcript.segments)} segments, {transcript.duration:.1f}s")


@app.command(name="mediums")
def mediums_cmd(
    path: Path,
    topic: str = typer.Option(None, "--topic", help="Topic to find matching segments for (omit for general highlight detection)"),
    max_segments: int = 5,
):
    """Analyze + cut medium clips (reframed + captioned) matching a topic, from a local video file."""
    video_id = path.stem
    transcript, boundaries = analyze(video_id, path)
    candidates = select_medium_segments(transcript, boundaries, topic, max_segments=max_segments)
    for i, candidate in enumerate(candidates):
        final_path = make_medium_clip(video_id, path, transcript, i, candidate)
        typer.echo(f"Medium clip {i}: {final_path} (score={candidate.relevance_score:.2f})")


@app.command(name="shorts")
def shorts_cmd(medium_raw_clip: Path):
    """Pick and cut the best short highlight from a medium_raw clip, using cached transcript/boundaries."""
    sidecar = medium_raw_clip.with_suffix(".json")
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    video_id, idx = medium_raw_clip.stem.rsplit("_", 1)
    source = RAW_DIR / f"{video_id}.mp4"
    transcript, boundaries = analyze(video_id, source)
    short_path = make_short_clip(video_id, source, transcript, boundaries, int(idx), data["start"], data["end"])
    typer.echo(f"Short clip: {short_path}")


@app.command(name="run")
def run_cmd(
    url: str,
    topic: str = typer.Option(None, "--topic", help="Topic to find matching segments for (omit for general highlight detection)"),
    max_segments: int = 5,
):
    """Full pipeline: ingest -> transcribe -> analyze -> medium clips (reframed+captioned) -> short clips (plain)."""
    result = run_pipeline(url, topic, max_medium=max_segments)
    for p in result.medium:
        typer.echo(f"Medium clip: {p}")
    for p in result.short:
        typer.echo(f"Short clip: {p}")


@app.command(name="serve")
def serve_cmd(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True):
    """Start the local web UI (open http://<host>:<port> in your browser)."""
    import webbrowser

    import uvicorn

    url = f"http://{host}:{port}"
    typer.echo(f"Starting clipper web UI at {url}")
    if open_browser:
        webbrowser.open(url)
    uvicorn.run("clipper.web.app:app", host=host, port=port)


if __name__ == "__main__":
    app()
