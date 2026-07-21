from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .boundaries import merge_boundaries
from .captions import burn_captions
from .config import ANALYSIS_DIR, OUT_MEDIUM_DIR, OUT_MEDIUM_RAW_DIR, OUT_SHORT_DIR
from .cutter import cut_clip, write_sidecar
from .ingest import ingest
from .medium_select import select_medium_segments
from .models import Boundary, MediumCandidate, Transcript
from .reframe import reframe_to_vertical
from .scenes import detect_scene_cuts
from .short_select import select_short_window
from .silence import detect_silences
from .transcribe import transcribe

StageCallback = Callable[[str], None]


@dataclass
class PipelineResult:
    medium: list[Path] = field(default_factory=list)
    short: list[Path] = field(default_factory=list)


def _report(on_stage: StageCallback | None, stage: str) -> None:
    if on_stage is not None:
        on_stage(stage)


def analyze(
    video_id: str, video_path: Path, on_stage: StageCallback | None = None
) -> tuple[Transcript, list[Boundary]]:
    """Transcribe + detect cut-point boundaries, cached per video_id."""
    _report(on_stage, "transcribing")
    transcript = transcribe(video_id, video_path)

    boundaries_cache = ANALYSIS_DIR / f"{video_id}.boundaries.json"
    if boundaries_cache.exists():
        raw = json.loads(boundaries_cache.read_text(encoding="utf-8"))
        return transcript, [Boundary(**b) for b in raw]

    _report(on_stage, "detecting scene/silence/sentence boundaries")
    scene_cuts = detect_scene_cuts(video_path)
    silences = detect_silences(video_path)
    boundaries = merge_boundaries(scene_cuts, silences, transcript)
    boundaries_cache.write_text(
        json.dumps([b.model_dump() for b in boundaries], indent=2), encoding="utf-8"
    )
    return transcript, boundaries


def make_medium_clip(
    video_id: str,
    video_path: Path,
    transcript: Transcript,
    index: int,
    candidate: MediumCandidate,
    on_stage: StageCallback | None = None,
) -> Path:
    raw_path = OUT_MEDIUM_RAW_DIR / f"{video_id}_{index}.mp4"
    _report(on_stage, f"cutting medium clip {index + 1}")
    cut_clip(video_path, candidate.start, candidate.end, raw_path)
    write_sidecar(raw_path, candidate.model_dump())

    _report(on_stage, f"reframing medium clip {index + 1} to 9:16")
    reframed_path = OUT_MEDIUM_DIR / f"{video_id}_{index}.reframed.mp4"
    reframe_to_vertical(raw_path, reframed_path)

    _report(on_stage, f"burning captions for medium clip {index + 1}")
    final_path = OUT_MEDIUM_DIR / f"{video_id}_{index}.mp4"
    words = transcript.words_between(candidate.start, candidate.end)
    burn_captions(reframed_path, words, candidate.start, final_path)
    reframed_path.unlink(missing_ok=True)
    write_sidecar(final_path, candidate.model_dump())
    return final_path


def make_short_clip(
    video_id: str,
    video_path: Path,
    transcript: Transcript,
    boundaries: list[Boundary],
    index: int,
    medium_start: float,
    medium_end: float,
    on_stage: StageCallback | None = None,
) -> Path:
    _report(on_stage, f"selecting short highlight {index + 1}")
    short_cand = select_short_window(transcript, boundaries, medium_start, medium_end)
    _report(on_stage, f"cutting short clip {index + 1}")
    short_path = OUT_SHORT_DIR / f"{video_id}_{index}_short.mp4"
    cut_clip(video_path, short_cand.start, short_cand.end, short_path)
    write_sidecar(short_path, short_cand.model_dump())
    return short_path


def run_pipeline(
    url: str,
    topic: str,
    max_medium: int = 5,
    on_stage: StageCallback | None = None,
) -> PipelineResult:
    """Full pipeline: ingest -> transcribe -> analyze -> medium clips (reframed+captioned) -> short clips (plain)."""
    _report(on_stage, "ingesting video")
    video_id, video_path = ingest(url)
    transcript, boundaries = analyze(video_id, video_path, on_stage=on_stage)

    _report(on_stage, "selecting medium clips matching topic")
    medium_candidates = select_medium_segments(transcript, boundaries, topic, max_segments=max_medium)

    result = PipelineResult()
    for i, candidate in enumerate(medium_candidates):
        result.medium.append(make_medium_clip(video_id, video_path, transcript, i, candidate, on_stage=on_stage))
        result.short.append(
            make_short_clip(
                video_id, video_path, transcript, boundaries, i, candidate.start, candidate.end, on_stage=on_stage
            )
        )

    _report(on_stage, "done")
    return result
