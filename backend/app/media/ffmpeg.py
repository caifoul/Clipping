from __future__ import annotations

import json
import subprocess
from pathlib import Path


class FFProbeError(RuntimeError):
    pass


def probe_duration_seconds(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise FFProbeError(result.stderr.strip() or "ffprobe failed")

    data = json.loads(result.stdout)
    try:
        return float(data["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise FFProbeError(f"could not read duration from ffprobe output: {data}") from exc
