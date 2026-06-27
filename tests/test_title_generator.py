#!/usr/bin/env python3
"""title_generator 폴백버그 회귀 (2026-06-24 자가점검).

gid30120 사례: 가사 빈약 시 strategy_sp_mood(가중치 0)가 유일 후보로 당첨돼
SP 장르명("K-Pop R&B ballad")이 제목이 되던 버그. 수정: 가중치0 전략 후보 제외
+ 폴백을 장르명 대신 첫 가창행(_first_lyric_line)으로.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import title_generator as T

SP = "K-Pop R&B ballad. Smooth electric piano. 90 BPM. key of C minor."


def _no_genre_label(title: str):
    for bad in ("K-Pop", "R&B", "ballad", "BPM", "key of"):
        assert bad not in title, f"장르/SP 토큰 '{bad}'이 제목에 누출: {title!r}"


def test_sparse_lyrics_never_yields_genre_label():
    r = T.generate_title("[Verse 1]\n[Chorus]\n", SP, genre_group="POP")
    _no_genre_label(r["title"])
    assert r["title"] == "Untitled"


def test_sparse_lyrics_uses_first_lyric_line():
    r = T.generate_title("[Verse 1]\n다시 잡은 손을 놓지 않을게\n", SP, genre_group="POP")
    _no_genre_label(r["title"])
    assert r["title"] == "다시 잡은 손을 놓지 않을게"


def test_normal_lyrics_use_lyric_strategy():
    full = ("[Verse 1]\n별이 쏟아지던 밤\n너를 처음 만났지\n"
            "[Chorus]\n사랑이야 그래 사랑이야\n끝없이 너를 부를게\n")
    r = T.generate_title(full, SP, genre_group="POP")
    assert r["strategy"] in ("chorus_phrase", "verse_noun", "short_punch")
    _no_genre_label(r["title"])


def test_first_lyric_line_skips_brackets_and_parens():
    assert T._first_lyric_line("[Intro]\n(soft humming)\n비가 내리는 거리에서") == "비가 내리는 거리에서"
    assert T._first_lyric_line("[Intro]\n") == ""
    assert T._first_lyric_line("") == ""
