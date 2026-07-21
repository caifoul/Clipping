from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def cut_clip(source: Path, start: float, end: float, out_path: Path) -> None:
    """Cut [start, end) from source into out_path with an accurate, re-encoded trim.

    Input-side seeking (-ss before -i) is fast; combined with re-encoding (not
    stream copy) ffmpeg produces frame-accurate output starting exactly at `start`,
    unlike a pure `-c copy` cut which can only land on keyframes.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    duration = end - start
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(source),
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-avoid_negative_ts",
        "make_zero",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def write_sidecar(out_path: Path, data: dict[str, Any]) -> None:
    sidecar = out_path.with_suffix(".json")
    sidecar.write_text(json.dumps(data, indent=2), encoding="utf-8")
