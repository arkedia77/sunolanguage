#!/usr/bin/env python3
"""
title_generator.py — Heuristic title extraction from lyrics + SP.

Extracts title candidates from assembled lyrics text and SP metadata
using 4 strategies adapted from leomusic2 step9-tqs.

Usage:
    python scripts/title_generator.py --lyrics "assembled lyrics" --sp "SP text"
    python scripts/title_generator.py --file lyrics.txt --sp-file sp.txt
"""

import random
import re
import sys

PARTICLES = re.compile(
    r"(이|가|은|는|을|를|에|에서|의|도|만|로|으로|과|와|하고|이나|나|처럼|보다|까지|부터|마저|조차|밖에|라도)$"
)

BANNED_TITLE_WORDS = {"사랑", "눈물", "바람", "마음", "세상", "하늘", "꿈"}

VERB_ENDINGS = re.compile(
    r"(거야|잖아|없어|있어|했어|겠어|한다|해요|해봐|할게|인걸|같아|는데|네요|어요|아요|해서|하고|니까|지만|라서|에요|더라|던데|했던|모르겠|줘|야|해|지|어|아)$"
)

BANNED_ADVERBS = {"이미", "다시", "아직", "정말", "너무", "진짜", "그냥", "어디", "왜"}

GENRE_STRATEGY_WEIGHTS = {
    "BALLAD":   {"verse_noun": 3, "chorus_phrase": 2, "short_punch": 1, "sp_mood": 0},
    "RNB":      {"chorus_phrase": 3, "verse_noun": 2, "short_punch": 1, "sp_mood": 0},
    "HIPHOP":   {"chorus_phrase": 3, "short_punch": 2, "verse_noun": 1, "sp_mood": 0},
    "ROCK":     {"chorus_phrase": 3, "short_punch": 2, "verse_noun": 1, "sp_mood": 0},
    "POP":      {"chorus_phrase": 3, "verse_noun": 2, "short_punch": 2, "sp_mood": 0},
    "ACOUSTIC": {"verse_noun": 3, "chorus_phrase": 2, "short_punch": 1, "sp_mood": 0},
}


def _parse_sections(lyrics: str) -> dict[str, str]:
    sections = {}
    current_tag = None
    current_lines = []

    for line in lyrics.split("\n"):
        m = re.match(r"^\[([^\]]+)\]$", line.strip())
        if m:
            if current_tag and current_lines:
                sections[current_tag] = "\n".join(current_lines).strip()
            current_tag = m.group(1).strip()
            current_lines = []
        elif current_tag:
            current_lines.append(line)

    if current_tag and current_lines:
        sections[current_tag] = "\n".join(current_lines).strip()

    return sections


def _is_korean(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text))


def _strip_particle(word: str) -> str:
    return PARTICLES.sub("", word)


def _extract_korean_nouns(text: str) -> list[str]:
    candidates = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or not _is_korean(line):
            continue
        words = re.findall(r"[가-힣]+", line)
        for w in words:
            noun = _strip_particle(w)
            if VERB_ENDINGS.search(noun):
                continue
            if 2 <= len(noun) <= 5 and noun not in BANNED_TITLE_WORDS and noun not in BANNED_ADVERBS:
                candidates.append(noun)
    return candidates


def _extract_short_lines(text: str, max_chars: int = 8) -> list[str]:
    candidates = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if 2 <= len(line) <= max_chars:
            if line not in BANNED_TITLE_WORDS:
                candidates.append(line)
    return candidates


def _extract_english_phrases(text: str) -> list[str]:
    candidates = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or _is_korean(line):
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and len(line) <= 25:
            candidates.append(line)
        elif len(words) > 4:
            for i in range(len(words) - 1):
                phrase = " ".join(words[i:i+3])
                if len(phrase) <= 20:
                    candidates.append(phrase)
    return candidates


def strategy_chorus_phrase(sections: dict[str, str]) -> list[str]:
    candidates = []
    for tag in ["Chorus", "Chorus 1", "Hook"]:
        text = sections.get(tag, "")
        if not text:
            continue
        candidates.extend(_extract_short_lines(text, max_chars=10))
        if _is_korean(text):
            candidates.extend(_extract_korean_nouns(text))
        else:
            candidates.extend(_extract_english_phrases(text))
    return candidates


def strategy_verse_noun(sections: dict[str, str]) -> list[str]:
    candidates = []
    for tag in ["Verse 1", "Verse"]:
        text = sections.get(tag, "")
        if not text:
            continue
        if _is_korean(text):
            candidates.extend(_extract_korean_nouns(text))
        else:
            candidates.extend(_extract_english_phrases(text))
        break
    return candidates


def strategy_short_punch(sections: dict[str, str]) -> list[str]:
    candidates = []
    for tag in ["Bridge", "Chorus", "Chorus 1", "Hook"]:
        text = sections.get(tag, "")
        if not text:
            continue
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if lines:
            last = lines[-1]
            if 2 <= len(last) <= 6:
                candidates.append(last)
            if _is_korean(last):
                words = re.findall(r"[가-힣]+", last)
                for w in words:
                    noun = _strip_particle(w)
                    if 2 <= len(noun) <= 4 and noun not in BANNED_TITLE_WORDS:
                        candidates.append(noun)
    return candidates


def strategy_sp_mood(sp_text: str) -> list[str]:
    genre = sp_text.split(".")[0].strip() if sp_text else ""
    words = genre.split()[:3]
    if words:
        return [" ".join(words)]
    return []


def generate_title(lyrics: str, sp_text: str = "",
                   genre_group: str = None) -> dict:
    sections = _parse_sections(lyrics)
    weights = GENRE_STRATEGY_WEIGHTS.get(genre_group or "POP",
                                          GENRE_STRATEGY_WEIGHTS["POP"])

    strategies = {
        "chorus_phrase": strategy_chorus_phrase(sections),
        "verse_noun":    strategy_verse_noun(sections),
        "short_punch":   strategy_short_punch(sections),
        "sp_mood":       strategy_sp_mood(sp_text),
    }

    weighted_candidates = []
    for name, candidates in strategies.items():
        w = weights.get(name, 1)
        for c in candidates:
            weighted_candidates.append((c, name, w))

    if not weighted_candidates:
        return {
            "title": sp_text.split(".")[0].strip()[:20] if sp_text else "Untitled",
            "strategy": "fallback",
            "alternatives": [],
        }

    seen = set()
    unique = []
    for c, name, w in weighted_candidates:
        if c not in seen:
            seen.add(c)
            unique.append((c, name, w))

    total_weight = sum(w for _, _, w in unique)
    pick = random.uniform(0, total_weight)
    cumulative = 0
    chosen = unique[0]
    for item in unique:
        cumulative += item[2]
        if cumulative >= pick:
            chosen = item
            break

    alternatives = [c for c, _, _ in unique if c != chosen[0]][:5]

    return {
        "title": chosen[0],
        "strategy": chosen[1],
        "alternatives": alternatives,
    }


def batch_titles(entries: list[dict]) -> list[dict]:
    recent_strategies = []
    for entry in entries:
        strategy = entry.get("title_strategy", "")
        if len(recent_strategies) >= 2 and all(s == strategy for s in recent_strategies[-2:]):
            alt = entry.get("title_alternatives", [])
            if alt:
                entry["title"] = alt[0]
                entry["title_strategy"] = "rebalanced"
        recent_strategies.append(entry.get("title_strategy", ""))
    return entries


if __name__ == "__main__":
    test_lyrics = """[Verse 1]
핸드폰이 아직 따뜻해
방금까지 통화했던 거니까
그 말은 어디로 갔는지
모르겠어

[Chorus]
다시 전화하면 될 것 같은데
이미 모르겠는 거야
온도가 식기 전에

[Verse 2]
창밖에 비가 내리잖아
우산 없이 걸어가는 중이야

[Bridge]
멈춰야 할 것 같은데
발이 안 떨어져"""

    test_sp = "K-Pop R&B ballad. Clean electric guitar plays arpeggiated patterns."

    for group in ["BALLAD", "POP", "ROCK", "HIPHOP", "ACOUSTIC", "RNB"]:
        result = generate_title(test_lyrics, test_sp, genre_group=group)
        print(f"{group:<10} → \"{result['title']}\" [{result['strategy']}]")
        print(f"           alt: {result['alternatives'][:3]}")
