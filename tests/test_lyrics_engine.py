"""Regression locks for the lyrics generation engine.

Covers: title_generator Kiwi noun extraction, lyrics_assembler verse/chorus
rendering invariants, lyrics_engine._load_history_song_ids round-trip (temp dir),
and lyrics_themes integrity.
"""
import json
import tempfile
from pathlib import Path

import title_generator
import lyrics_assembler
import lyrics_engine
import lyrics_themes


# --- (a) title_generator: Kiwi NNG/NNP extraction ---------------------------

KIWI_AVAILABLE = title_generator._get_kiwi() is not None

# Verb/adjective stems that the OLD regex approach used to wrongly emit as
# "nouns" (the bug fixed 2026-05-31). They must NOT appear in Kiwi output.
_FORBIDDEN_STEM_FRAGMENTS = {"따뜻하", "흐르", "통화했", "관조하", "떠나", "올린"}


def test_extract_korean_nouns_yields_real_nouns():
    text = "핸드폰이 아직 따뜻해\n방금까지 통화했던 거니까\n추억이 흐른다"
    nouns = title_generator._extract_korean_nouns(text)
    assert nouns, "expected at least one noun candidate"
    # Real nouns present
    assert "핸드폰" in nouns
    assert "추억" in nouns


def test_extract_korean_nouns_excludes_verb_adj_stems():
    text = "핸드폰이 아직 따뜻해\n방금까지 통화했던 거니까\n추억이 흐른다"
    nouns = title_generator._extract_korean_nouns(text)
    for frag in _FORBIDDEN_STEM_FRAGMENTS:
        assert frag not in nouns, f"verb/adj stem fragment leaked into nouns: {frag}"


def test_generate_title_returns_noun_for_ballad():
    lyrics = (
        "[Verse 1]\n핸드폰이 아직 따뜻해\n방금까지 통화했던 거니까\n"
        "[Chorus]\n다시 전화하면 될 것 같은데\n온도가 식기 전에\n"
    )
    res = title_generator.generate_title(lyrics, "K-Pop ballad.", genre_group="BALLAD")
    assert res["title"]
    assert "strategy" in res


# --- (b) lyrics_assembler: V1!=V2 + chorus repeats from first occurrence ------

def test_distinct_verses_render_as_verse_1_and_verse_2():
    sections = {
        "verse_1": {"text": "첫번째 절 가사입니다"},
        "verse_2": {"text": "두번째 절 완전히 다른 가사"},
        "chorus": {"text": "후렴구 가사"},
    }
    structure = ["verse", "chorus", "verse", "chorus"]
    out = lyrics_assembler.assemble_lyrics(sections, structure)
    assert "[Verse 1]" in out
    assert "[Verse 2]" in out
    assert "첫번째 절 가사입니다" in out
    assert "두번째 절 완전히 다른 가사" in out
    # V1 != V2 invariant: the two verse blocks must carry different text.
    assert out.index("첫번째") != out.index("두번째")


def test_chorus_repeats_from_first_occurrence():
    # Second chorus payload differs; assembler must reuse the FIRST chorus text.
    sections = {
        "verse_1": {"text": "절 하나"},
        "verse_2": {"text": "절 둘"},
        "chorus_1": {"text": "첫 후렴 고정 텍스트"},
        "chorus_2": {"text": "두번째 후렴은 무시되어야 한다"},
    }
    structure = ["verse", "chorus", "verse", "chorus"]
    out = lyrics_assembler.assemble_lyrics(sections, structure)
    assert out.count("첫 후렴 고정 텍스트") == 2
    assert "두번째 후렴은 무시되어야 한다" not in out


# --- (c) lyrics_engine._load_history_song_ids round-trip (TEMP dir) ----------

def test_load_history_song_ids_roundtrip(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)
        batch = [
            {"index": 0, "_source_song_ids": [11, 22, 33]},
            {"index": 1, "_source_song_ids": [33, 44]},
        ]
        (tmpdir / "lyrics_batch_20990101_000000.json").write_text(
            json.dumps(batch, ensure_ascii=False))
        # Point the loader's module-level HISTORY_DIR at our temp dir.
        monkeypatch.setattr(lyrics_engine, "HISTORY_DIR", tmpdir)
        ids = lyrics_engine._load_history_song_ids()
    assert ids == {11, 22, 33, 44}


def test_load_history_song_ids_missing_dir(monkeypatch):
    monkeypatch.setattr(lyrics_engine, "HISTORY_DIR", Path("/nonexistent/xyzqq"))
    assert lyrics_engine._load_history_song_ids() == set()


def test_load_history_song_ids_skips_bad_json(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)
        (tmpdir / "lyrics_batch_bad.json").write_text("{not valid json")
        (tmpdir / "lyrics_batch_ok.json").write_text(
            json.dumps([{"_source_song_ids": [7]}]))
        monkeypatch.setattr(lyrics_engine, "HISTORY_DIR", tmpdir)
        ids = lyrics_engine._load_history_song_ids()
    assert ids == {7}


# --- (d) lyrics_themes integrity ---------------------------------------------

def test_every_theme_has_required_fields():
    for name, theme in lyrics_themes.THEMES.items():
        assert theme.get("keywords_kr"), f"{name} missing kr keywords"
        assert theme.get("keywords_en"), f"{name} missing en keywords"
        assert theme.get("mood"), f"{name} missing mood"
        subs = theme.get("sub_themes", {})
        assert len(subs) >= 2, f"{name} has fewer than 2 sub_themes"
        for sub_name, sub in subs.items():
            assert sub.get("keywords_kr"), f"{name}/{sub_name} missing kr"


def test_get_theme_query_never_empty_for_known_themes():
    for name in lyrics_themes.list_themes():
        q = lyrics_themes.get_theme_query(name)
        assert q.strip(), f"empty query for theme {name}"
        # also with explicit sub_theme
        sub = lyrics_themes.pick_sub_theme(name)
        if sub:
            q2 = lyrics_themes.get_theme_query(name, sub)
            assert q2.strip(), f"empty query for {name}/{sub}"


def test_get_theme_query_unknown_is_empty():
    assert lyrics_themes.get_theme_query("__no_such_theme__") == ""
