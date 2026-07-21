from __future__ import annotations

import subprocess
import urllib.request
from pathlib import Path

import cv2
import numpy as np

from .config import MODELS_DIR, SETTINGS

_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
_MODEL_PATH = MODELS_DIR / "face_detection_yunet_2023mar.onnx"

OUT_WIDTH = 1080
OUT_HEIGHT = 1920


def _ensure_face_model() -> Path:
    if not _MODEL_PATH.exists():
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
    return _MODEL_PATH


def _get_face_detector(width: int, height: int):
    model_path = _ensure_face_model()
    return cv2.FaceDetectorYN_create(str(model_path), "", (width, height))


def _ffill_bfill(values: np.ndarray) -> np.ndarray:
    values = values.copy()
    last = None
    for i in range(len(values)):
        if not np.isnan(values[i]):
            last = values[i]
        elif last is not None:
            values[i] = last
    last = None
    for i in range(len(values) - 1, -1, -1):
        if not np.isnan(values[i]):
            last = values[i]
        elif last is not None:
            values[i] = last
    return values


def _moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or len(values) == 0:
        return values
    pad = window // 2
    padded = np.pad(values, pad, mode="edge")
    kernel = np.ones(window) / window
    smoothed = np.convolve(padded, kernel, mode="same")
    return smoothed[pad : pad + len(values)]


def _detect_center_path(source: Path, width: int, height: int, fps: float, total_frames: int) -> np.ndarray:
    detector = _get_face_detector(width, height)
    sample_interval = max(1, round(fps / SETTINGS.reframe_sample_fps))

    cap = cv2.VideoCapture(str(source))
    sample_idxs: list[int] = []
    sample_vals: list[float] = []
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % sample_interval == 0:
            _, faces = detector.detect(frame)
            if faces is not None and len(faces):
                best = max(faces, key=lambda f: f[2] * f[3])
                cx = float(best[0] + best[2] / 2)
            else:
                cx = np.nan
            sample_idxs.append(frame_idx)
            sample_vals.append(cx)
        frame_idx += 1
    cap.release()

    if not sample_idxs:
        return np.full(total_frames, width / 2.0)

    vals = np.array(sample_vals)
    if np.isnan(vals).all():
        return np.full(total_frames, width / 2.0)

    vals = _ffill_bfill(vals)
    vals = _moving_average(vals, SETTINGS.reframe_smoothing_window)

    idxs = np.array(sample_idxs, dtype=float)
    all_idxs = np.arange(total_frames, dtype=float)
    return np.interp(all_idxs, idxs, vals)


def reframe_to_vertical(source: Path, out_path: Path) -> None:
    """Crop `source` to a 9:16 vertical clip that tracks the primary detected face,
    falling back to a center crop wherever no face is found. Re-renders video
    frame-by-frame (OpenCV) then remuxes the original audio back on via ffmpeg."""
    cap = cv2.VideoCapture(str(source))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    crop_w = min(width, int(round(height * SETTINGS.reframe_aspect_ratio)))
    half_w = crop_w / 2.0

    center_path = _detect_center_path(source, width, height, fps, total_frames)
    center_path = np.clip(center_path, half_w, width - half_w)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_video = out_path.with_name(out_path.stem + ".noaudio.mp4")

    cap = cv2.VideoCapture(str(source))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(tmp_video), fourcc, fps, (OUT_WIDTH, OUT_HEIGHT))

    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cx = center_path[idx] if idx < len(center_path) else center_path[-1]
        x0 = int(round(cx - half_w))
        x0 = max(0, min(width - crop_w, x0))
        cropped = frame[:, x0 : x0 + crop_w]
        resized = cv2.resize(cropped, (OUT_WIDTH, OUT_HEIGHT))
        writer.write(resized)
        idx += 1
    writer.release()
    cap.release()

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(tmp_video),
        "-i",
        str(source),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0?",
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
        "-shortest",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    tmp_video.unlink(missing_ok=True)
