import json
from pathlib import Path

from clipper.cutter import write_sidecar


def test_write_sidecar_roundtrip(tmp_path: Path):
    out_path = tmp_path / "clip_0.mp4"
    data = {"start": 1.5, "end": 12.25, "relevance_score": 0.8, "reasoning": "on topic"}

    write_sidecar(out_path, data)

    sidecar_path = tmp_path / "clip_0.json"
    assert sidecar_path.exists()
    assert json.loads(sidecar_path.read_text(encoding="utf-8")) == data
