#!/usr/bin/env python3
"""
lyrics_themes.py — Theme seed definitions for lyrics retrieval.

Provides theme keywords that bias ALL section queries toward a unified narrative.
Each theme has Korean search keywords + English mood hints for the multilingual model.

Usage:
    python scripts/lyrics_themes.py list
    python scripts/lyrics_themes.py show 이별
"""

import random
import sys

THEMES = {
    "이별": {
        "keywords_kr": ["이별", "떠나", "잊어", "보내", "헤어져", "안녕", "눈물", "아파", "그리워", "추억", "기억"],
        "keywords_en": "farewell goodbye separation pain longing memories",
        "mood": "melancholic nostalgic bittersweet",
        "description": "이별과 그리움",
    },
    "사랑": {
        "keywords_kr": ["사랑", "마음", "너를", "함께", "가슴", "설레", "심장", "고백", "눈빛", "손끝"],
        "keywords_en": "love heart together confession warmth",
        "mood": "romantic warm intimate passionate",
        "description": "사랑과 설렘",
    },
    "밤": {
        "keywords_kr": ["밤", "혼자", "어둠", "새벽", "고요", "침묵", "달빛", "별", "불빛", "창문"],
        "keywords_en": "night alone darkness silence moonlight solitude",
        "mood": "atmospheric dark dreamy lonely",
        "description": "밤과 고독",
    },
    "성장": {
        "keywords_kr": ["내일", "꿈", "시작", "앞으로", "용기", "세상", "빛", "걸어", "일어나", "변해"],
        "keywords_en": "tomorrow dream courage forward hope growth",
        "mood": "uplifting hopeful energetic powerful",
        "description": "성장과 희망",
    },
    "일상": {
        "keywords_kr": ["거리", "카페", "출근", "알람", "지하철", "버스", "매일", "오늘", "아침", "집"],
        "keywords_en": "daily routine city street morning commute cafe",
        "mood": "chill mellow gentle warm",
        "description": "일상과 도시 풍경",
    },
    "분노": {
        "keywords_kr": ["화가", "미쳐", "부숴", "소리쳐", "터져", "참아", "불타", "깨부숴", "거짓"],
        "keywords_en": "anger rage fire destroy scream rebellion",
        "mood": "aggressive driving heavy raw",
        "description": "분노와 반항",
    },
    "자유": {
        "keywords_kr": ["자유", "바람", "하늘", "날아", "달려", "놓아", "떠나자", "어디든", "바다"],
        "keywords_en": "freedom sky fly wind sea escape road",
        "mood": "bright energetic euphoric uplifting",
        "description": "자유와 해방",
    },
    "회상": {
        "keywords_kr": ["그때", "어린", "옛날", "기억", "사진", "일기", "학교", "고향", "엄마", "아빠"],
        "keywords_en": "memory childhood past photograph diary hometown",
        "mood": "nostalgic gentle warm melancholic",
        "description": "과거 회상과 추억",
    },
}


def get_theme(name: str) -> dict | None:
    return THEMES.get(name)


def get_theme_query(theme_name: str) -> str:
    theme = THEMES.get(theme_name)
    if not theme:
        return ""
    kr_sample = random.sample(theme["keywords_kr"], min(4, len(theme["keywords_kr"])))
    return " ".join(kr_sample) + " " + theme["keywords_en"]


def get_theme_mood(theme_name: str) -> str:
    theme = THEMES.get(theme_name)
    return theme["mood"] if theme else ""


def list_themes() -> list[str]:
    return list(THEMES.keys())


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "list":
        print("=== Available Themes ===")
        for name, t in THEMES.items():
            print(f"  {name:6s} — {t['description']:15s} ({len(t['keywords_kr'])} keywords)")
    elif args[0] == "show":
        name = args[1] if len(args) > 1 else "이별"
        t = THEMES.get(name)
        if t:
            print(f"Theme: {name} — {t['description']}")
            print(f"  KR: {', '.join(t['keywords_kr'])}")
            print(f"  EN: {t['keywords_en']}")
            print(f"  Mood: {t['mood']}")
            print(f"  Query sample: {get_theme_query(name)}")
        else:
            print(f"Unknown theme: {name}")
            print(f"Available: {', '.join(THEMES.keys())}")
