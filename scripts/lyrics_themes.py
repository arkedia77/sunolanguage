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
        "sub_themes": {
            "연인": {"keywords_kr": ["너", "우리", "손잡고", "약속", "밤길"], "keywords_en": "lover couple relationship"},
            "가족": {"keywords_kr": ["엄마", "아빠", "집", "고향", "어린"], "keywords_en": "family home parents childhood"},
            "시간": {"keywords_kr": ["계절", "지나", "흘러", "세월", "겨울"], "keywords_en": "time seasons passing years fading"},
            "장소": {"keywords_kr": ["카페", "거리", "역", "공원", "골목"], "keywords_en": "place street station park alley"},
            "성찰": {"keywords_kr": ["나를", "혼자", "거울", "그림자", "돌아보"], "keywords_en": "self reflection alone mirror"},
        },
    },
    "사랑": {
        "keywords_kr": ["사랑", "마음", "너를", "함께", "가슴", "설레", "심장", "고백", "눈빛", "손끝"],
        "keywords_en": "love heart together confession warmth",
        "mood": "romantic warm intimate passionate",
        "description": "사랑과 설렘",
        "sub_themes": {
            "설렘": {"keywords_kr": ["처음", "떨리", "두근", "시작", "만남"], "keywords_en": "flutter first meeting excitement spring"},
            "고백": {"keywords_kr": ["말해", "용기", "전화", "편지", "목소리"], "keywords_en": "confession courage letter voice tell"},
            "일상": {"keywords_kr": ["아침", "커피", "산책", "소파", "저녁"], "keywords_en": "morning coffee walk routine daily together"},
            "그리움": {"keywords_kr": ["보고싶", "기다려", "멀리", "사진", "꿈에"], "keywords_en": "miss waiting distance longing dream"},
            "약속": {"keywords_kr": ["영원", "함께", "반지", "미래", "늙어"], "keywords_en": "forever promise future ring grow old"},
        },
    },
    "밤": {
        "keywords_kr": ["밤", "혼자", "어둠", "새벽", "고요", "침묵", "달빛", "별", "불빛", "창문"],
        "keywords_en": "night alone darkness silence moonlight solitude",
        "mood": "atmospheric dark dreamy lonely",
        "description": "밤과 고독",
        "sub_themes": {
            "고독": {"keywords_kr": ["혼자", "외로", "텅빈", "적막", "침대"], "keywords_en": "lonely empty solitude shadow bed"},
            "추억": {"keywords_kr": ["그때", "기억", "사진", "옛날", "생각"], "keywords_en": "memories past photo remember looking back"},
            "도시": {"keywords_kr": ["네온", "택시", "거리", "간판", "소음"], "keywords_en": "neon taxi street city lights urban"},
            "꿈": {"keywords_kr": ["잠들", "눈감", "꿈속", "흐릿", "깨어"], "keywords_en": "dream sleep floating blur awake drifting"},
            "새벽": {"keywords_kr": ["새벽", "동트", "첫차", "이슬", "여명"], "keywords_en": "dawn first light morning dew daybreak"},
        },
    },
    "성장": {
        "keywords_kr": ["내일", "꿈", "시작", "앞으로", "용기", "세상", "빛", "걸어", "일어나", "변해"],
        "keywords_en": "tomorrow dream courage forward hope growth",
        "mood": "uplifting hopeful energetic powerful",
        "description": "성장과 희망",
        "sub_themes": {
            "실패": {"keywords_kr": ["넘어져", "무릎", "상처", "다시", "일어나"], "keywords_en": "failure fall knees try again stand up"},
            "도전": {"keywords_kr": ["뛰어", "달려", "한계", "넘어", "땀"], "keywords_en": "challenge run push limits sweat overcome"},
            "변화": {"keywords_kr": ["달라져", "새로운", "문", "열려", "계절"], "keywords_en": "change new door open different transform"},
            "자립": {"keywords_kr": ["혼자서", "처음", "월급", "이사", "어른"], "keywords_en": "independent first salary adult living alone"},
            "여행": {"keywords_kr": ["길", "떠나", "지도", "낯선", "배낭"], "keywords_en": "journey road map stranger backpack travel"},
        },
    },
    "일상": {
        "keywords_kr": ["거리", "카페", "출근", "알람", "지하철", "버스", "매일", "오늘", "아침", "집"],
        "keywords_en": "daily routine city street morning commute cafe",
        "mood": "chill mellow gentle warm",
        "description": "일상과 도시 풍경",
        "sub_themes": {
            "출근": {"keywords_kr": ["지하철", "버스", "알람", "커피", "사무실"], "keywords_en": "commute subway bus alarm office"},
            "퇴근": {"keywords_kr": ["저녁", "퇴근", "맥주", "포장마차", "골목"], "keywords_en": "evening after work beer alley night"},
            "주말": {"keywords_kr": ["늦잠", "산책", "빨래", "햇살", "소파"], "keywords_en": "weekend lazy walk laundry sunlight couch"},
        },
    },
    "분노": {
        "keywords_kr": ["화가", "미쳐", "부숴", "소리쳐", "터져", "참아", "불타", "깨부숴", "거짓"],
        "keywords_en": "anger rage fire destroy scream rebellion",
        "mood": "aggressive driving heavy raw",
        "description": "분노와 반항",
        "sub_themes": {
            "반항": {"keywords_kr": ["부숴", "깨부숴", "거짓", "속지마", "일어서"], "keywords_en": "rebel break destroy lies stand up"},
            "억울": {"keywords_kr": ["왜", "불공평", "참아", "입막아", "눈물"], "keywords_en": "unfair why endure silence tears injustice"},
        },
    },
    "자유": {
        "keywords_kr": ["자유", "바람", "하늘", "날아", "달려", "놓아", "떠나자", "어디든", "바다"],
        "keywords_en": "freedom sky fly wind sea escape road",
        "mood": "bright energetic euphoric uplifting",
        "description": "자유와 해방",
        "sub_themes": {
            "탈출": {"keywords_kr": ["벗어나", "놓아", "사직서", "문밖", "뒤돌아"], "keywords_en": "escape quit leave behind break free"},
            "출발": {"keywords_kr": ["떠나자", "시작", "공항", "기차", "새벽"], "keywords_en": "depart start airport train dawn journey"},
            "자연": {"keywords_kr": ["바다", "산", "바람", "파도", "하늘"], "keywords_en": "sea mountain wind waves sky nature"},
            "방랑": {"keywords_kr": ["어디든", "길", "걷고", "낯선", "지도"], "keywords_en": "wander anywhere road walking stranger map"},
        },
    },
    "회상": {
        "keywords_kr": ["그때", "어린", "옛날", "기억", "사진", "일기", "학교", "고향", "엄마", "아빠"],
        "keywords_en": "memory childhood past photograph diary hometown",
        "mood": "nostalgic gentle warm melancholic",
        "description": "과거 회상과 추억",
        "sub_themes": {
            "어린시절": {"keywords_kr": ["학교", "운동장", "급식", "친구", "교실"], "keywords_en": "school playground childhood friend classroom"},
            "고향": {"keywords_kr": ["고향", "시골", "논", "할머니", "마을"], "keywords_en": "hometown village field grandmother rural"},
            "가족": {"keywords_kr": ["엄마", "아빠", "밥상", "김밥", "손"], "keywords_en": "mother father table food hands family"},
        },
    },
}


def get_theme(name: str) -> dict | None:
    return THEMES.get(name)


def get_theme_query(theme_name: str, sub_theme: str = None) -> str:
    theme = THEMES.get(theme_name)
    if not theme:
        return ""
    kr_sample = random.sample(theme["keywords_kr"], min(3, len(theme["keywords_kr"])))
    base = " ".join(kr_sample) + " " + theme["keywords_en"]

    if sub_theme is None:
        subs = theme.get("sub_themes", {})
        if subs:
            sub_theme = random.choice(list(subs.keys()))

    if sub_theme:
        sub = theme.get("sub_themes", {}).get(sub_theme)
        if sub:
            sub_kr = random.sample(sub["keywords_kr"], min(3, len(sub["keywords_kr"])))
            base = " ".join(sub_kr) + " " + sub.get("keywords_en", "") + " " + base

    return base


def pick_sub_theme(theme_name: str) -> str | None:
    theme = THEMES.get(theme_name)
    if not theme:
        return None
    subs = theme.get("sub_themes", {})
    if not subs:
        return None
    return random.choice(list(subs.keys()))


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
