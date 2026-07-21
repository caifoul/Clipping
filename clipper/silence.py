from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .config import SETTINGS

_START_RE = re.compile(r"silence_start:\s*([\d.]+)")
_END_RE = re.compile(r"silence_end:\s*([\d.]+)")


def detect_silences(video_path: Path) -> list[tuple[float, float]]:
    """Returns list of (start, end) silence intervals in seconds, via ffmpeg's silencedetect filter."""
    cmd = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-af",
        f"silencedetect=noise={SETTINGS.silence_noise_db}dB:d={SETTINGS.silence_min_duration}",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr

    starts = [float(m) for m in _START_RE.findall(stderr)]
    ends = [float(m) for m in _END_RE.findall(stderr)]

    # ffmpeg may log a trailing silence_start with no matching silence_end if
    # the file ends while still silent; drop any unmatched entries.
    n = min(len(starts), len(ends))
    return list(zip(starts[:n], ends[:n]))
