from __future__ import annotations

from pydantic import BaseModel, Field


class TranscriptWord(BaseModel):
    word: str
    start: float
    end: float


class TranscriptSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    words: list[TranscriptWord] = Field(default_factory=list)


class Transcript(BaseModel):
    video_id: str
    language: str
    duration: float
    segments: list[TranscriptSegment]

    def text_between(self, start: float, end: float) -> str:
        parts = [s.text.strip() for s in self.segments if s.start >= start and s.end <= end + 0.05]
        return " ".join(parts)

    def words_between(self, start: float, end: float) -> list[TranscriptWord]:
        out: list[TranscriptWord] = []
        for seg in self.segments:
            for w in seg.words:
                if w.start >= start and w.end <= end + 0.05:
                    out.append(w)
        return out

    def to_prompt_text(self, start: float | None = None, end: float | None = None) -> str:
        lines = []
        for seg in self.segments:
            if start is not None and seg.start < start:
                continue
            if end is not None and seg.end > end:
                continue
            lines.append(f"[{seg.start:.2f}-{seg.end:.2f}] {seg.text}")
        return "\n".join(lines)


class Boundary(BaseModel):
    time: float
    sources: list[str]
    confidence: float


class MediumCandidate(BaseModel):
    start: float
    end: float
    relevance_score: float
    reasoning: str
    transcript_excerpt: str = ""


class ShortCandidate(BaseModel):
    start: float
    end: float
    virality_score: float
    reasoning: str
    transcript_excerpt: str = ""
