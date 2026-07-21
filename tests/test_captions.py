from pathlib import Path

from clipper.captions import _group_words, build_ass
from clipper.models import TranscriptWord


def _word(text, start, end):
    return TranscriptWord(word=text, start=start, end=end)


def test_group_words_splits_on_max_count():
    words = [_word(str(i), i * 0.3, i * 0.3 + 0.2) for i in range(9)]
    groups = _group_words(words, max_words=4, max_gap=10.0)
    assert [len(g) for g in groups] == [4, 4, 1]


def test_group_words_splits_on_gap():
    words = [
        _word("a", 0.0, 0.3),
        _word("b", 0.4, 0.6),
        _word("c", 2.0, 2.3),  # gap > max_gap since prev ended at 0.6
    ]
    groups = _group_words(words, max_words=10, max_gap=0.6)
    assert len(groups) == 2
    assert [w.word for w in groups[0]] == ["a", "b"]
    assert [w.word for w in groups[1]] == ["c"]


def test_build_ass_writes_karaoke_tags(tmp_path: Path):
    words = [_word("hello", 10.0, 10.4), _word("world", 10.4, 10.9)]
    out_path = tmp_path / "clip.ass"

    build_ass(words, clip_start=10.0, out_ass_path=out_path)

    content = out_path.read_text(encoding="utf-8")
    assert "[Events]" in content
    assert "\\k40" in content  # (10.4-10.0)*100 centiseconds
    assert "hello" in content
    assert "world" in content
    # timestamps should be relative to clip_start (i.e. start at 0:00:00.00)
    assert "0:00:00.00" in content
