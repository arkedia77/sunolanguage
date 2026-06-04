"""Regression locks for pure chunk-building / quality-gate functions.

Covers: lyrics_chunk_builder (split_couplets short-line merge, dedup_chorus
repeat_count, detect_language) and corpus_quality_gate.is_sp_directive.
"""
import lyrics_chunk_builder as lcb
import corpus_quality_gate as cqg


# --- detect_language ---------------------------------------------------------

def test_detect_language_korean():
    assert lcb.detect_language("밤하늘 아래 너와 나") == "ko"


def test_detect_language_english():
    assert lcb.detect_language("under the starry night sky") == "en"


def test_detect_language_mixed():
    assert lcb.detect_language("밤하늘 under the stars") == "mixed"


def test_detect_language_empty_defaults_ko():
    assert lcb.detect_language("12345 !!!") == "ko"


# --- split_couplets (short-line merge) ---------------------------------------

def test_split_couplets_pairs_two_lines():
    text = ("이것은 충분히 긴 첫번째 가사 줄입니다\n"
            "이것은 충분히 긴 두번째 가사 줄입니다\n"
            "이것은 충분히 긴 세번째 가사 줄입니다\n"
            "이것은 충분히 긴 네번째 가사 줄입니다")
    couplets = lcb.split_couplets(text)
    # 4 long lines -> 2 couplets of 2 lines each
    assert len(couplets) == 2
    assert all(c.count("\n") == 1 for c in couplets)


def test_split_couplets_merges_short_line_into_next():
    # First line is short (< MIN_COUPLET_CHARS=20) -> merged with next line.
    short = "짧은줄"  # well under 20 chars
    long1 = "이것은 충분히 긴 가사 줄로 이루어져 있습니다"
    long2 = "또 다른 충분히 긴 가사 줄로 이루어져 있습니다"
    text = f"{short}\n{long1}\n{long2}"
    couplets = lcb.split_couplets(text)
    # The short line must have been merged (not standalone) with the following line.
    joined = "\n".join(couplets)
    assert short in joined
    # short line should appear glued to long1 on adjacent lines
    assert f"{short}\n{long1}" in joined


def test_split_couplets_single_line_returns_empty():
    assert lcb.split_couplets("한 줄짜리 가사") == []


# --- dedup_chorus (repeat_count) ---------------------------------------------

def test_dedup_chorus_collapses_identical_and_counts():
    sections = [
        {"tag": "verse", "text": "절 가사", "index": 0},
        {"tag": "chorus", "text": "동일한 후렴", "index": 1},
        {"tag": "verse", "text": "다른 절", "index": 2},
        {"tag": "chorus", "text": "동일한 후렴", "index": 3},
        {"tag": "chorus", "text": "동일한 후렴", "index": 4},
    ]
    out = lcb.dedup_chorus(sections)
    choruses = [s for s in out if s["tag"] == "chorus"]
    assert len(choruses) == 1, "identical choruses must collapse to one"
    assert choruses[0]["repeat_count"] == 3
    # non-chorus sections retain repeat_count = 1
    verses = [s for s in out if s["tag"] == "verse"]
    assert all(v["repeat_count"] == 1 for v in verses)


def test_dedup_chorus_distinct_choruses_kept():
    sections = [
        {"tag": "chorus", "text": "후렴 A", "index": 0},
        {"tag": "chorus", "text": "후렴 B", "index": 1},
    ]
    out = lcb.dedup_chorus(sections)
    assert len([s for s in out if s["tag"] == "chorus"]) == 2
    assert all(s["repeat_count"] == 1 for s in out)


# --- corpus_quality_gate.is_sp_directive -------------------------------------

def test_is_sp_directive_flags_english_directive():
    # 'maximum energy' is a known SP directive keyword and the line is short
    # English (no Korean) -> must be flagged.
    assert cqg.is_sp_directive("Maximum energy, layered breaks") is True


def test_is_sp_directive_passes_normal_korean_lyric():
    assert cqg.is_sp_directive("밤하늘 아래 너와 둘이 걷던 그 길") is False


def test_is_sp_directive_passes_normal_english_lyric():
    # A normal narrative English lyric without directive keywords.
    assert cqg.is_sp_directive("we walked along the quiet shore at night") is False


def test_is_sp_directive_empty_is_false():
    assert cqg.is_sp_directive("") is False
    assert cqg.is_sp_directive("[Chorus]") is False
