from __future__ import annotations

from pathlib import Path

from .config import SETTINGS


def detect_scene_cuts(video_path: Path) -> list[float]:
    """Returns timestamps (seconds) of visual scene-cut boundaries."""
    from scenedetect import SceneManager, open_video
    from scenedetect.detectors import ContentDetector

    video = open_video(str(video_path))
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=SETTINGS.scene_detector_threshold))
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()

    if not scene_list:
        return []

    # Boundary = start of every scene after the first (start of first scene is t=0, not a cut)
    return [start.get_seconds() for start, _end in scene_list[1:]]
