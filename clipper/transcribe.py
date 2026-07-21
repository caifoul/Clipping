from __future__ import annotations

from pathlib import Path

from .config import SETTINGS, TRANSCRIPTS_DIR
from .models import Transcript, TranscriptSegment, TranscriptWord

_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        _model = WhisperModel(
            SETTINGS.whisper_model_size,
            device=SETTINGS.whisper_device,
            compute_type=SETTINGS.whisper_compute_type,
        )
    return _model


def transcribe(video_id: str, video_path: Path) -> Transcript:
    """Transcribe with word-level timestamps. Cached to disk per video_id."""
    cache_path = TRANSCRIPTS_DIR / f"{video_id}.json"
    if cache_path.exists():
        return Transcript.model_validate_json(cache_path.read_text(encoding="utf-8"))

    model = _get_model()
    raw_segments, info = model.transcribe(str(video_path), word_timestamps=True)

    segments: list[TranscriptSegment] = []
    for i, seg in enumerate(raw_segments):
        words = [
            TranscriptWord(word=w.word.strip(), start=w.start, end=w.end)
            for w in (seg.words or [])
        ]
        segments.append(
            TranscriptSegment(
                id=i,
                start=seg.start,
                end=seg.end,
                text=seg.text.strip(),
                words=words,
            )
        )

    transcript = Transcript(
        video_id=video_id,
        language=info.language,
        duration=info.duration,
        segments=segments,
    )
    cache_path.write_text(transcript.model_dump_json(indent=2), encoding="utf-8")
    return transcript
