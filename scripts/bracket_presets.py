#!/usr/bin/env python3
"""
bracket_presets.py — Bracket directive retriever for non-lyric song sections.

Retrieves genre-aware bracket directives (instrument cues, arrangement changes,
transitions) from the Qdrant sunolang_presets collection for sections that have
no lyrics: Intro, Interlude, Outro, Instrumental Break.

Architecture: corpus presets → generation → gate (자유도=코퍼스 프리셋)

Usage:
    python scripts/bracket_presets.py intro "K-Pop ballad warm piano"
    python scripts/bracket_presets.py outro "Indie Rock distorted guitar"
    python scripts/bracket_presets.py interlude "Bossa Nova fingerpicked guitar"
"""

import json
import os
import random
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

COLLECTION_NAME = "sunolang_presets"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

QDRANT_HOST = os.environ.get("QDRANT_HOST", "100.90.35.121")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", None)

SECTION_PROFILES = {
    "intro": {
        "description": "sparse opening, 1-2 instruments entering",
        "preferred_slots": ["instrument", "drums", "effect_electronic"],
        "preferred_actions": {"enters", "enter", ""},
        "max_directives": 2,
        "query_boost": "opening sparse atmospheric entrance",
    },
    "interlude": {
        "description": "instrumental break, texture change or solo",
        "preferred_slots": ["instrument", "arrangement", "effect_electronic"],
        "preferred_actions": {"continues", "continue", "slides", "slide", ""},
        "max_directives": 2,
        "query_boost": "instrumental solo melodic break",
    },
    "outro": {
        "description": "closing section, fading or resolving",
        "preferred_slots": ["instrument", "arrangement", "effect_electronic"],
        "preferred_actions": {"fades", "fade", "continues", "continue", ""},
        "max_directives": 2,
        "query_boost": "closing fade resolution ending",
    },
    "instrumental": {
        "description": "full instrumental section",
        "preferred_slots": ["instrument", "arrangement", "drums"],
        "preferred_actions": set(),
        "max_directives": 2,
        "query_boost": "instrumental full arrangement melodic",
    },
}

GENRE_GROUP_HINTS = {
    "BALLAD": "piano strings emotional gentle arpeggiated",
    "RNB": "groove bass synth smooth soulful",
    "HIPHOP": "beat 808 bass synth scratches",
    "ROCK": "distorted electric guitar drums power driving",
    "ACOUSTIC": "fingerpicked acoustic guitar gentle sparse",
    "POP": "synth bass drum bright energetic electronic",
}

INSTRUMENT_KEYWORDS = [
    "piano", "guitar", "bass", "drum", "violin", "cello", "strings",
    "synth", "saxophone", "sax", "trumpet", "flute", "harp", "organ",
    "harmonica", "banjo", "ukulele", "mandolin", "accordion", "oboe",
    "clarinet", "trombone", "horn", "percussion", "timpani", "marimba",
    "vibraphone", "xylophone", "glockenspiel", "bells", "tambourine",
    "shaker", "congas", "bongos", "djembe", "tabla", "sitar", "erhu",
    "koto", "gayageum", "guzheng", "berimbau", "balalaika", "whistle",
    "fiddle", "viola", "contrabass", "double bass", "rhodes", "wurlitzer",
    "mellotron", "theremin", "kalimba", "steel drum", "bagpipe",
]


def extract_sp_instruments(sp_text: str) -> set[str]:
    sp_lower = sp_text.lower()
    found = set()
    for kw in INSTRUMENT_KEYWORDS:
        if kw in sp_lower:
            found.add(kw)
    return found


def get_client():
    from qdrant_client import QdrantClient
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY)


def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def _build_bracket_filter(preferred_slots: list[str]):
    from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
    return Filter(must=[
        FieldCondition(key="source", match=MatchValue(value="bracket")),
        FieldCondition(key="slot", match=MatchAny(any=preferred_slots)),
    ])


def retrieve_bracket_directives(
    section_type: str,
    sp_text: str,
    genre_group: str = "POP",
    client=None,
    model=None,
    n_candidates: int = 20,
    exclude_texts: set[str] | None = None,
) -> list[dict]:
    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    profile = SECTION_PROFILES.get(section_type, SECTION_PROFILES["interlude"])
    genre_hint = GENRE_GROUP_HINTS.get(genre_group, "")
    query_text = f"{sp_text.split('.')[0]} {genre_hint} {profile['query_boost']}"

    query_vec = model.encode(query_text).tolist()
    qfilter = _build_bracket_filter(profile["preferred_slots"])

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec,
        query_filter=qfilter,
        limit=n_candidates,
    )

    if not response.points:
        return []

    candidates = []
    seen_texts = set()
    for hit in response.points:
        text = hit.payload.get("text", "")
        if not text or text in seen_texts:
            continue
        if exclude_texts and text in exclude_texts:
            continue
        if len(text) < 3:
            continue
        seen_texts.add(text)
        action = hit.payload.get("action", "")
        action_ok = (not profile["preferred_actions"] or
                     action in profile["preferred_actions"])
        candidates.append({
            "text": text,
            "score": hit.score,
            "slot": hit.payload.get("slot", ""),
            "entity": hit.payload.get("entity", ""),
            "genre": hit.payload.get("genre", ""),
            "action": action,
            "action_match": action_ok,
        })

    sp_instruments = extract_sp_instruments(sp_text)

    for c in candidates:
        c_text_lower = c["text"].lower()
        matched_inst = sum(1 for inst in sp_instruments if inst in c_text_lower)
        c["instrument_match"] = matched_inst

    action_matched = [c for c in candidates if c["action_match"]]
    pool = action_matched if action_matched else candidates

    if sp_instruments:
        inst_matched = [c for c in pool if c["instrument_match"] > 0]
        pool = inst_matched if inst_matched else pool

    pool.sort(key=lambda c: (-c["instrument_match"], -c["score"]))

    max_d = profile["max_directives"]
    selected = pool[:max_d]

    return selected


def format_bracket_section(section_tag: str, directives: list[dict]) -> str:
    lines = []
    for d in directives:
        lines.append(f"[{d['text']}]")
    return "\n".join(lines)


def compose_section_brackets(
    form: list[str],
    sp_text: str,
    genre_group: str = "POP",
    client=None,
    model=None,
) -> dict[str, list[dict]]:
    non_lyric_tags = {"intro", "outro", "interlude", "instrumental"}
    result = {}
    seen = set()
    used_texts = set()

    for tag in form:
        if tag not in non_lyric_tags:
            continue
        if tag in seen:
            continue
        seen.add(tag)

        directives = retrieve_bracket_directives(
            section_type=tag,
            sp_text=sp_text,
            genre_group=genre_group,
            client=client,
            model=model,
            exclude_texts=used_texts,
        )
        if directives:
            result[tag] = directives
            for d in directives:
                used_texts.add(d["text"])

    return result


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    section = args[0]
    sp = args[1] if len(args) > 1 else "K-Pop ballad warm piano"
    genre_group = "POP"
    for a in args:
        if a.startswith("--genre-group="):
            genre_group = a.split("=")[1]

    print(f"Bracket Retrieval: section={section}, genre_group={genre_group}")
    print(f"  SP: {sp[:60]}...")
    print()

    directives = retrieve_bracket_directives(section, sp, genre_group=genre_group)
    if directives:
        print(f"  {len(directives)} directives:")
        for d in directives:
            print(f"    [{d['text']}]  (slot={d['slot']}, score={d['score']:.4f}, "
                  f"action={d['action'] or '-'}, genre={d['genre'][:30]})")
        print()
        print("Formatted:")
        print(format_bracket_section(section, directives))
    else:
        print("  (no directives found)")
