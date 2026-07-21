from __future__ import annotations

from .models import Boundary, Transcript

_SOURCE_WEIGHT = {
    "scene": 0.40,
    "silence": 0.45,
    "sentence": 0.25,
}

CLUSTER_EPSILON = 0.35  # seconds; points closer than this are treated as the same cut point


def merge_boundaries(
    scene_cuts: list[float],
    silences: list[tuple[float, float]],
    transcript: Transcript,
    cluster_epsilon: float = CLUSTER_EPSILON,
) -> list[Boundary]:
    """Merge scene cuts, silence gaps, and sentence ends into one sorted list of
    candidate cut points, each tagged with its contributing source(s) and a
    confidence score (higher when multiple independent signals agree)."""
    points: list[tuple[float, str]] = []
    points += [(t, "scene") for t in scene_cuts]
    points += [((start + end) / 2, "silence") for start, end in silences]
    points += [(seg.end, "sentence") for seg in transcript.segments]
    points.sort(key=lambda p: p[0])

    clusters: list[list[tuple[float, str]]] = []
    for point in points:
        if clusters and point[0] - clusters[-1][-1][0] <= cluster_epsilon:
            clusters[-1].append(point)
        else:
            clusters.append([point])

    boundaries: list[Boundary] = []
    for cluster in clusters:
        avg_time = sum(p[0] for p in cluster) / len(cluster)
        sources = sorted({p[1] for p in cluster})
        confidence = min(1.0, sum(_SOURCE_WEIGHT[p[1]] for p in cluster))
        boundaries.append(Boundary(time=avg_time, sources=sources, confidence=confidence))

    return boundaries


def snap_to_boundary(target_time: float, boundaries: list[Boundary], max_distance: float = 2.0) -> float:
    """Return the nearest boundary time within max_distance seconds, else the original target."""
    if not boundaries:
        return target_time
    nearest = min(boundaries, key=lambda b: abs(b.time - target_time))
    if abs(nearest.time - target_time) <= max_distance:
        return nearest.time
    return target_time


def expand_to_duration(
    anchor_start: float,
    anchor_end: float,
    boundaries: list[Boundary],
    target: float,
    min_len: float,
    max_len: float,
    floor: float = 0.0,
    ceiling: float | None = None,
) -> tuple[float, float]:
    """Treat [anchor_start, anchor_end] as a point of interest rather than a trustworthy
    final window (small/local LLMs are unreliable at following exact duration instructions
    when the prompt is long) and grow it outward, snapped to the boundary grid, until it
    falls within [min_len, max_len] and centered near `target` seconds around the anchor's
    midpoint. Falls back to the anchor itself if it's already an acceptable length."""
    length = anchor_end - anchor_start
    if min_len <= length <= max_len:
        return anchor_start, anchor_end

    ceiling = ceiling if ceiling is not None else anchor_end + max_len
    center = (anchor_start + anchor_end) / 2
    half = target / 2
    desired_start = max(floor, center - half)
    desired_end = min(ceiling, center + half)

    times = sorted(b.time for b in boundaries)

    def at_or_before(t: float) -> float:
        candidates = [x for x in times if x <= t]
        return max(candidates) if candidates else floor

    def at_or_after(t: float) -> float:
        candidates = [x for x in times if x >= t]
        return min(candidates) if candidates else ceiling

    start = at_or_before(desired_start)
    end = at_or_after(desired_end)

    if end - start > max_len:
        end = at_or_after(min(ceiling, start + max_len))
    if end - start < min_len:
        end = min(ceiling, start + min_len)

    return start, end
