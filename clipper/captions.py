from __future__ import annotations

import subprocess
from pathlib import Path

from .models import TranscriptWord

_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,72,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,0,2,80,80,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _fmt_time(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    centi = int(round((s - int(s)) * 100))
    return f"{h:d}:{m:02d}:{int(s):02d}.{centi:02d}"


def _escape(text: str) -> str:
    return text.replace("\\", "").replace("{", "").replace("}", "")


def _group_words(
    words: list[TranscriptWord], max_words: int = 4, max_gap: float = 0.6
) -> list[list[TranscriptWord]]:
    groups: list[list[TranscriptWord]] = []
    current: list[TranscriptWord] = []
    prev_end: float | None = None
    for w in words:
        if current and (len(current) >= max_words or (prev_end is not None and w.start - prev_end > max_gap)):
            groups.append(current)
            current = []
        current.append(w)
        prev_end = w.end
    if current:
        groups.append(current)
    return groups


def build_ass(words: list[TranscriptWord], clip_start: float, out_ass_path: Path) -> None:
    """Builds a word-highlight (karaoke-style) .ass subtitle, timestamps relative to clip_start."""
    groups = _group_words(words)
    lines = [_HEADER]
    for group in groups:
        line_start = group[0].start - clip_start
        line_end = group[-1].end - clip_start
        parts = []
        for w in group:
            dur_centi = max(1, int(round((w.end - w.start) * 100)))
            parts.append(f"{{\\k{dur_centi}}}{_escape(w.word)} ")
        text = "".join(parts).strip()
        lines.append(f"Dialogue: 0,{_fmt_time(line_start)},{_fmt_time(line_end)},Default,,0,0,0,,{text}")

    out_ass_path.parent.mkdir(parents=True, exist_ok=True)
    out_ass_path.write_text("\n".join(lines), encoding="utf-8")


def burn_captions(source: Path, words: list[TranscriptWord], clip_start: float, out_path: Path) -> None:
    ass_path = out_path.with_suffix(".ass")
    build_ass(words, clip_start, ass_path)

    # ffmpeg's subtitles filter treats ':' and '\' specially inside the filtergraph;
    # forward-slash the path and escape the drive-letter colon.
    filter_path = str(ass_path).replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vf",
        f"subtitles='{filter_path}'",
        "-c:a",
        "copy",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
