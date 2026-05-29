#!/usr/bin/env python3
"""
song_forms.py — Genre-aware song form template library.

Classifies SP genre text into 6 groups and provides
multiple form variants per group for structure diversity.
"""

import random
import re

GENRE_GROUPS = {
    "BALLAD": [
        "ballad", "piano ballad", "orchestral ballad", "k-ballad",
        "korean ballad", "power ballad", "slow ballad",
    ],
    "RNB": [
        "r&b", "rnb", "neo-soul", "neo soul", "city pop", "lo-fi r&b",
        "soul", "smooth", "k-r&b",
    ],
    "HIPHOP": [
        "hip-hop", "hip hop", "hiphop", "boom bap", "trap", "rap",
        "k-hip-hop", "k-hiphop", "drill", "grime", "phonk",
    ],
    "ROCK": [
        "rock", "punk", "metal", "grunge", "alternative rock", "indie rock",
        "k-rock", "post-punk", "shoegaze", "garage rock", "metalcore",
        "pop-punk", "pop punk",
    ],
    "ACOUSTIC": [
        "folk", "acoustic", "bossa nova", "bossa", "singer-songwriter",
        "fingerstyle", "unplugged", "chamber", "classical", "waltz",
        "jazz", "dream pop", "ambient",
    ],
    "POP": [
        "pop", "k-pop", "kpop", "dance", "electro", "synth", "edm",
        "disco", "funk", "reggae", "latin", "trot", "foxtrot",
        "future bass", "synthwave", "new wave", "city pop",
    ],
}

GENRE_FORMS = {
    "BALLAD": {
        "standard": ["intro", "verse", "chorus", "interlude", "verse", "chorus", "bridge", "outro"],
        "minimal":  ["verse", "chorus", "verse", "chorus", "bridge", "outro"],
        "reflective": ["verse", "chorus", "verse", "chorus", "bridge", "verse", "outro"],
    },
    "RNB": {
        "standard": ["intro", "verse", "pre_chorus", "chorus", "verse", "chorus", "bridge", "outro"],
        "groove":   ["verse", "pre_chorus", "chorus", "verse", "chorus", "bridge", "chorus", "outro"],
    },
    "HIPHOP": {
        "standard": ["intro", "verse", "hook", "verse", "hook", "verse", "hook", "outro"],
        "bridge":   ["verse", "hook", "verse", "bridge", "hook", "outro"],
    },
    "ROCK": {
        "standard": ["intro", "verse", "chorus", "verse", "chorus", "interlude", "bridge", "chorus", "outro"],
        "minimal":  ["verse", "chorus", "verse", "bridge", "chorus", "outro"],
        "heavy":    ["verse", "chorus", "verse", "chorus", "bridge", "chorus", "chorus", "outro"],
    },
    "ACOUSTIC": {
        "standard": ["verse", "chorus", "verse", "chorus", "bridge", "outro"],
        "minimal":  ["verse", "verse", "bridge", "verse"],
        "folk":     ["verse", "chorus", "verse", "chorus", "verse", "outro"],
    },
    "POP": {
        "standard": ["verse", "pre_chorus", "chorus", "verse", "pre_chorus", "chorus", "bridge", "chorus"],
        "minimal":  ["verse", "chorus", "verse", "chorus", "bridge", "outro"],
        "hook_heavy": ["chorus", "verse", "chorus", "verse", "bridge", "chorus", "outro"],
    },
}

SECTION_ROLES = {
    "verse":      {"role": "narrative",    "query_hint": "narrative story scene imagery"},
    "chorus":     {"role": "hook",         "query_hint": "emotional hook declaration repetition"},
    "bridge":     {"role": "contrast",     "query_hint": "perspective shift contrast quiet"},
    "pre_chorus": {"role": "buildup",      "query_hint": "tension building anticipation"},
    "hook":       {"role": "declaration",  "query_hint": "short punch declaration slogan"},
    "intro":      {"role": "opening",      "query_hint": "atmospheric opening sparse"},
    "outro":      {"role": "closing",      "query_hint": "closing resolution fade"},
    "interlude":  {"role": "break",        "query_hint": "instrumental break transition"},
    "drop":       {"role": "climax",       "query_hint": "bass drop climax energy"},
    "tag":        {"role": "closing",      "query_hint": "closing tag refrain fade"},
}


def classify_genre_group(sp_genre: str) -> str:
    if not sp_genre:
        return "POP"

    text = sp_genre.lower().strip()

    for group, keywords in GENRE_GROUPS.items():
        for kw in keywords:
            if kw in text:
                if group == "ACOUSTIC" and "city pop" in text:
                    continue
                return group

    genre_signals = {
        "BALLAD":   ["slow", "emotional", "piano", "orchestral", "strings", "intimate"],
        "RNB":      ["groove", "soulful", "smooth", "silky"],
        "HIPHOP":   ["beat", "flow", "bars", "808"],
        "ROCK":     ["guitar", "distorted", "driving", "power chord", "riff"],
        "ACOUSTIC": ["fingerpick", "unplugged", "gentle", "sparse"],
    }
    for group, signals in genre_signals.items():
        if any(s in text for s in signals):
            return group

    return "POP"


def select_form(genre_group: str, variant: str = None) -> list[str]:
    forms = GENRE_FORMS.get(genre_group, GENRE_FORMS["POP"])
    if variant and variant in forms:
        return list(forms[variant])
    return list(random.choice(list(forms.values())))


def get_required_sections(form: list[str]) -> list[str]:
    seen = []
    for tag in form:
        if tag not in seen:
            seen.append(tag)
    return seen


def count_section_occurrences(form: list[str]) -> dict[str, int]:
    counts = {}
    for tag in form:
        counts[tag] = counts.get(tag, 0) + 1
    return counts


def get_section_query_hint(section_tag: str) -> str:
    return SECTION_ROLES.get(section_tag, {}).get("query_hint", "")


def form_to_arrow(form: list[str]) -> str:
    return " → ".join(form)


if __name__ == "__main__":
    test_genres = [
        "Cinematic orchestral fusion with electronic elements",
        "K-Pop educational pop track",
        "Bossa Nova",
        "K-Indie R&B ballad",
        "K-Pop Hip-Hop track featuring a prominent male rapper",
        "K-Rock with pop-punk influences",
        "K-Pop and Future Bass fusion",
        "Lo-fi hip hop track at 85 BPM in C minor",
        "K-Pop Indie Rock track in E Major at 115 BPM",
        "K-Pop Rock with a driving pop-punk influence",
    ]

    print("=== Genre Classification Test ===\n")
    for g in test_genres:
        group = classify_genre_group(g)
        form = select_form(group)
        print(f"  {g[:50]:<50} → {group:<10} | {form_to_arrow(form)}")

    print("\n=== All Forms ===\n")
    for group, forms in GENRE_FORMS.items():
        print(f"  {group}:")
        for name, form in forms.items():
            print(f"    [{name}] {form_to_arrow(form)}")
