from __future__ import annotations

from .boundaries import expand_to_duration, snap_to_boundary
from .config import SETTINGS
from .llm_client import generate_structured
from .models import Boundary, MediumCandidate, Transcript

_SCHEMA = {
    "type": "object",
    "properties": {
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "number", "description": "Start time in seconds"},
                    "end": {"type": "number", "description": "End time in seconds"},
                    "relevance_score": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "How well this segment matches the requested topic and forms a coherent, self-contained clip",
                    },
                    "reasoning": {"type": "string", "description": "Brief justification"},
                },
                "required": ["start", "end", "relevance_score", "reasoning"],
            },
        }
    },
    "required": ["segments"],
}


def select_medium_segments(
    transcript: Transcript,
    boundaries: list[Boundary],
    topic: str | None = None,
    max_segments: int = 5,
) -> list[MediumCandidate]:
    boundary_hint = ", ".join(f"{b.time:.2f}" for b in boundaries)

    if topic:
        task_description = f"""Requested topic: "{topic}"

Find every segment of the transcript that is substantively about this topic and forms a \
coherent, self-contained clip (has a clear beginning and end, doesn't cut off mid-thought)."""
    else:
        task_description = """Find the most interesting, highlight-worthy, self-contained moments in \
the transcript (has a clear beginning and end, doesn't cut off mid-thought) — the kind of moments \
that would make a compelling standalone social clip: strong reactions, funny or surprising exchanges, \
skillful plays, notable turning points, or otherwise memorable content."""

    prompt = f"""You are selecting clips from a timestamped video transcript to turn into medium-length \
social clips (target length ~{SETTINGS.medium_target_seconds:.0f}s, acceptable range \
{SETTINGS.medium_min_seconds:.0f}-{SETTINGS.medium_max_seconds:.0f}s).

{task_description}
Prefer segments whose start/end land on or very near one of these candidate cut points \
(seconds): {boundary_hint}

Transcript:
{transcript.to_prompt_text()}

Return up to {max_segments} candidates, ranked by relevance_score descending. \
Respond with JSON only, matching this shape: \
{{"segments": [{{"start": <number>, "end": <number>, "relevance_score": <0-1>, "reasoning": "<string>"}}]}}"""

    result = generate_structured(prompt, _SCHEMA, "return_medium_segments")
    raw_segments = result["segments"]

    candidates: list[MediumCandidate] = []
    for seg in raw_segments:
        anchor_start, anchor_end = float(seg["start"]), float(seg["end"])
        if anchor_end < anchor_start:
            anchor_start, anchor_end = anchor_end, anchor_start

        start, end = expand_to_duration(
            anchor_start,
            anchor_end,
            boundaries,
            target=SETTINGS.medium_target_seconds,
            min_len=SETTINGS.medium_min_seconds,
            max_len=SETTINGS.medium_max_seconds,
            ceiling=transcript.duration,
        )
        start = snap_to_boundary(start, boundaries)
        end = snap_to_boundary(end, boundaries)
        if end - start < SETTINGS.medium_min_seconds * 0.5:
            continue
        candidates.append(
            MediumCandidate(
                start=start,
                end=end,
                relevance_score=float(seg["relevance_score"]),
                reasoning=seg["reasoning"],
                transcript_excerpt=transcript.text_between(start, end),
            )
        )

    candidates.sort(key=lambda c: c.relevance_score, reverse=True)
    return candidates[:max_segments]
