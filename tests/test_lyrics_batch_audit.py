#!/usr/bin/env python3
"""lyrics_batch_audit 재점검 게이트 회귀 (2026-06-24 자가점검).

check_core_english_leak 정밀도: 괄호 보컬디렉션·외국어곡 오탐 제외, 실제
한국어곡의 영어 코어섹션 누출만 검출.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import lyrics_batch_audit as A


def _song(gid, lyrics):
    return {"index": gid, "title": f"t{gid}", "lyrics": lyrics}


def test_english_leak_flags_korean_song_with_english_core():
    # 한국어곡인데 Verse가 전부 영어 = 누출
    lyr = ("[Verse 1]\nGuitars cascade like waterfalls\nEndless echo in the hall\n"
           "[Chorus]\n사랑이야 그래 사랑이야\n끝없이 너를 부를게\n")
    hits = A.check_core_english_leak([_song(1, lyr)])
    assert len(hits) == 1 and hits[0]["section"].lower().startswith("verse")


def test_english_leak_ignores_foreign_language_song():
    # 곡 전체가 비한국어(이탈리아 벨칸토) = 정상 외국어곡, 누출 아님
    lyr = ("[Verse 1]\nNel silenzio della sera\nO luce eterna che risplendi\n"
           "[Chorus]\nCanto la mia melodia\nVolando verso il cielo\n")
    assert A.check_core_english_leak([_song(2, lyr)]) == []


def test_english_leak_ignores_paren_vocal_direction():
    # 괄호전용 보컬디렉션은 가사내용 아님 — 한국어곡에 섞여도 누출 아님
    lyr = ("[Verse 1]\n(soft, breathy)\n비가 내리는 거리에서\n"
           "[Chorus]\n널 기다린 시간\n")
    assert A.check_core_english_leak([_song(3, lyr)]) == []


def test_english_leak_clean_korean_song():
    lyr = ("[Verse 1]\n별이 쏟아지던 밤\n너를 처음 만났지\n"
           "[Chorus]\n사랑이야 그래\n")
    assert A.check_core_english_leak([_song(4, lyr)]) == []
