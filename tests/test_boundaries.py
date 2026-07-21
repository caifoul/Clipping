from clipper.boundaries import expand_to_duration, merge_boundaries, snap_to_boundary
from clipper.models import Boundary, Transcript, TranscriptSegment


def _transcript(segment_ends: list[float]) -> Transcript:
    segments = [
        TranscriptSegment(id=i, start=max(0.0, end - 2.0), end=end, text=f"segment {i}")
        for i, end in enumerate(segment_ends)
    ]
    return Transcript(video_id="test", language="en", duration=segment_ends[-1] + 1, segments=segments)


def test_merge_boundaries_clusters_agreeing_signals():
    transcript = _transcript([10.0, 20.05])
    scene_cuts = [10.02]
    silences = [(19.9, 20.1)]  # midpoint 20.0, close to sentence end 20.05

    boundaries = merge_boundaries(scene_cuts, silences, transcript)

    # Two clusters expected: ~10.0 (scene+sentence) and ~20.0 (silence+sentence)
    assert len(boundaries) == 2
    first, second = sorted(boundaries, key=lambda b: b.time)

    assert abs(first.time - 10.01) < 0.05
    assert set(first.sources) == {"scene", "sentence"}
    assert set(second.sources) == {"silence", "sentence"}


def test_merge_boundaries_keeps_distant_points_separate():
    transcript = _transcript([5.0, 50.0])
    boundaries = merge_boundaries(scene_cuts=[], silences=[], transcript=transcript)
    assert len(boundaries) == 2


def test_snap_to_boundary_within_range():
    transcript = _transcript([12.0])
    boundaries = merge_boundaries(scene_cuts=[12.1], silences=[], transcript=transcript)
    assert snap_to_boundary(11.0, boundaries, max_distance=2.0) != 11.0


def test_snap_to_boundary_returns_original_when_too_far():
    transcript = _transcript([12.0])
    boundaries = merge_boundaries(scene_cuts=[12.1], silences=[], transcript=transcript)
    assert snap_to_boundary(0.0, boundaries, max_distance=2.0) == 0.0


def test_snap_to_boundary_with_no_boundaries():
    assert snap_to_boundary(5.0, []) == 5.0


def _boundaries_every(step: float, count: int) -> list[Boundary]:
    return [Boundary(time=i * step, sources=["scene"], confidence=0.4) for i in range(count)]


def test_expand_to_duration_leaves_already_acceptable_window_untouched():
    boundaries = _boundaries_every(5.0, 40)
    start, end = expand_to_duration(100.0, 150.0, boundaries, target=60, min_len=40, max_len=90)
    assert (start, end) == (100.0, 150.0)


def test_expand_to_duration_grows_a_tiny_anchor_to_target():
    # boundaries every 5s from 0 to 195s
    boundaries = _boundaries_every(5.0, 40)
    # tiny 1s anchor around t=100
    start, end = expand_to_duration(100.0, 101.0, boundaries, target=60, min_len=40, max_len=90, ceiling=195.0)
    assert 40 <= end - start <= 90
    assert start <= 100.0 <= end


def test_expand_to_duration_clamps_near_video_start():
    boundaries = _boundaries_every(5.0, 40)
    start, end = expand_to_duration(2.0, 3.0, boundaries, target=60, min_len=40, max_len=90, floor=0.0, ceiling=195.0)
    assert start >= 0.0
    assert end - start >= 40 * 0.999
