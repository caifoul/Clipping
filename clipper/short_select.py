from __future__ import annotations

from .boundaries import expand_to_duration, snap_to_boundary
from .config import SETTINGS
from .llm_client import generate_structured
from .models import Boundary, ShortCandidate, Transcript

_SCHEMA = {
    "type": "object",
    "properties": {
        "start": {"type": "number", "description": "Start time in seconds"},
        "end": {"type": "number", "description": "End time in seconds"},
        "virality_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Predicted hook/shareability strength: strong opening line, emotional peak, punchline, or surprising/quotable moment",
        },
        "reasoning": {"type": "string", "description": "Brief justification"},
    },
    "required": ["start", "end", "virality_score", "reasoning"],
}


def select_short_window(
    transcript: Transcript,
    boundaries: list[Boundary],
    clip_start: float,
    clip_end: float,
) -> ShortCandidate:
    local_boundaries = [b for b in boundaries if clip_start <= b.time <= clip_end]
    boundary_hint = ", ".join(f"{b.time:.2f}" for b in local_boundaries)

    prompt = f"""Below is a timestamped transcript excerpt from {clip_start:.2f}s to {clip_end:.2f}s \
of a longer video. Find the single best short-form highlight window inside it \
(length {SETTINGS.short_min_seconds:.0f}-{SETTINGS.short_max_seconds:.0f}s) \
for a standalone social clip: the moment with the strongest hook, emotional peak, \
punchline, or most quotable/surprising line. It must make sense on its own without \
the rest of the clip for context.

Prefer a start/end that lands on or very near one of these candidate cut points \
(seconds): {boundary_hint}

Transcript excerpt:
{transcript.to_prompt_text(start=clip_start, end=clip_end)}

Respond with JSON only, matching this shape: \
{{"start": <number>, "end": <number>, "virality_score": <0-1>, "reasoning": "<string>"}}"""

    result = generate_structured(prompt, _SCHEMA, "return_short_window")

    anchor_start, anchor_end = float(result["start"]), float(result["end"])
    if anchor_end < anchor_start:
        anchor_start, anchor_end = anchor_end, anchor_start

    start, end = expand_to_duration(
        anchor_start,
        anchor_end,
        local_boundaries,
        target=(SETTINGS.short_min_seconds + SETTINGS.short_max_seconds) / 2,
        min_len=SETTINGS.short_min_seconds,
        max_len=SETTINGS.short_max_seconds,
        floor=clip_start,
        ceiling=clip_end,
    )
    start = snap_to_boundary(start, local_boundaries)
    end = snap_to_boundary(end, local_boundaries)
    start = max(clip_start, start)
    end = min(clip_end, end)

    return ShortCandidate(
        start=start,
        end=end,
        virality_score=float(result["virality_score"]),
        reasoning=result["reasoning"],
        transcript_excerpt=transcript.text_between(start, end),
    )
