#!/usr/bin/env python3
"""
lyrics_retriever.py — Lyrics section retrieval from Qdrant.

Three retrieval modes:
  1. Theme Search    — Korean/English keyword → matching lyrics sections
  2. SP Match        — SP preset text → genre/mood-matched lyrics
  3. Coherent Assemble — seed section → suggest complementary sections

Usage:
    python scripts/lyrics_retriever.py search "밤하늘 아래" --section=chorus
    python scripts/lyrics_retriever.py match-sp "K-Pop ballad..." --sections=verse,chorus
    python scripts/lyrics_retriever.py assemble --seed-song=42
"""

import json
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

COLLECTION_NAME = "sunolang_lyrics"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

QDRANT_HOST = os.environ.get("QDRANT_HOST", "100.90.35.121")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", None)

DEFAULT_STRUCTURE = ["verse", "pre_chorus", "chorus", "verse", "bridge", "chorus", "outro"]

MOOD_WORDS = {
    "intimate", "emotional", "warm", "melancholic", "dreamy", "nostalgic",
    "energetic", "driving", "aggressive", "smooth", "groovy", "bright",
    "dark", "atmospheric", "raw", "soulful", "euphoric", "chill",
    "passionate", "gentle", "powerful", "serene", "lush", "sparse",
}


def get_client():
    from qdrant_client import QdrantClient
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY)


def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def make_filter(section_tag: str = None, genre: str = None, language: str = None,
                granularity: str = None, exclude_song_ids: set = None):
    from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchText

    conditions = []
    if section_tag:
        conditions.append(FieldCondition(key="section_tag", match=MatchValue(value=section_tag)))
    if genre:
        conditions.append(FieldCondition(key="genre", match=MatchText(text=genre)))
    if language:
        conditions.append(FieldCondition(key="language", match=MatchValue(value=language)))
    if granularity:
        conditions.append(FieldCondition(key="granularity", match=MatchValue(value=granularity)))

    must_not = []
    if exclude_song_ids:
        for sid in exclude_song_ids:
            must_not.append(FieldCondition(key="song_id", match=MatchValue(value=sid)))

    if not conditions and not must_not:
        return None
    return Filter(must=conditions or None, must_not=must_not or None)


def theme_search(query: str, section_tag: str = None, genre: str = None,
                 language: str = None, granularity: str = None, limit: int = 10,
                 exclude_song_ids: set = None,
                 client=None, model=None) -> list[dict]:
    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    embedding = model.encode(query).tolist()
    query_filter = make_filter(section_tag, genre, language, granularity,
                               exclude_song_ids=exclude_song_ids)

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        query_filter=query_filter,
        limit=limit,
    )

    return [{
        "score": hit.score,
        "payload": hit.payload,
    } for hit in response.points]


def extract_sp_mood(sp_text: str) -> list[str]:
    words = set(re.findall(r"\b\w+\b", sp_text.lower()))
    return sorted(words & MOOD_WORDS)


def extract_sp_genre(sp_text: str) -> str:
    return sp_text.split(".")[0].strip() if sp_text else ""


def match_sp(sp_text: str, sections: list[str] = None,
             granularity: str = None, limit_per_section: int = 3,
             client=None, model=None) -> dict[str, list[dict]]:
    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    if sections is None:
        sections = ["verse", "chorus", "bridge"]

    genre = extract_sp_genre(sp_text)
    moods = extract_sp_mood(sp_text)
    query = genre
    if moods:
        query += " " + " ".join(moods)

    results = {}
    for section in sections:
        hits = theme_search(
            query, section_tag=section, granularity=granularity,
            limit=limit_per_section, client=client, model=model,
        )
        results[section] = hits

    return results


def match_sp_differentiated(sp_text: str, form: list[str],
                            granularity: str = None, limit_per_section: int = 3,
                            client=None, model=None) -> dict[str, list[dict]]:
    from song_forms import get_section_query_hint

    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    genre = extract_sp_genre(sp_text)
    moods = extract_sp_mood(sp_text)
    base_query = genre
    if moods:
        base_query += " " + " ".join(moods)

    section_counts = {}
    results = {}
    used_song_ids = {}

    for tag in form:
        section_counts[tag] = section_counts.get(tag, 0) + 1
        occurrence = section_counts[tag]
        indexed_key = f"{tag}_{occurrence}"

        if tag in ("intro", "outro", "interlude"):
            if tag in results:
                continue
            hits = theme_search(
                base_query, section_tag=tag, granularity=granularity,
                limit=limit_per_section, client=client, model=model,
            )
            results[tag] = hits
            continue

        role_hint = get_section_query_hint(tag)
        section_query = f"{base_query} {role_hint}".strip()

        exclude = used_song_ids.get(tag, set()) if occurrence > 1 else set()

        hits = theme_search(
            section_query, section_tag=tag, granularity=granularity,
            limit=limit_per_section, exclude_song_ids=exclude if exclude else None,
            client=client, model=model,
        )

        if not hits and exclude:
            hits = theme_search(
                section_query, section_tag=tag, granularity=granularity,
                limit=limit_per_section, client=client, model=model,
            )

        results[indexed_key] = hits

        if hits and hits[0]["payload"].get("song_id"):
            if tag not in used_song_ids:
                used_song_ids[tag] = set()
            used_song_ids[tag].add(hits[0]["payload"]["song_id"])

    return results


def coherent_assemble(seed_song_id: int = None, seed_text: str = None,
                      structure: list[str] = None,
                      limit_per_slot: int = 3,
                      client=None, model=None) -> dict[str, list[dict]]:
    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    if structure is None:
        structure = DEFAULT_STRUCTURE

    if seed_text:
        seed_vec = model.encode(seed_text).tolist()
    elif seed_song_id is not None:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        scroll_results = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(must=[
                FieldCondition(key="song_id", match=MatchValue(value=seed_song_id)),
                FieldCondition(key="section_tag", match=MatchValue(value="chorus")),
            ]),
            limit=1,
            with_vectors=True,
        )[0]
        if not scroll_results:
            scroll_results = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=Filter(must=[
                    FieldCondition(key="song_id", match=MatchValue(value=seed_song_id)),
                ]),
                limit=1,
                with_vectors=True,
            )[0]
        if not scroll_results:
            print(f"No sections found for song_id={seed_song_id}")
            return {}
        seed_vec = scroll_results[0].vector
    else:
        print("Need --seed-song or --seed-text")
        return {}

    seen_tags = set()
    results = {}
    for tag in structure:
        if tag in seen_tags:
            continue
        seen_tags.add(tag)

        from qdrant_client.models import Filter, FieldCondition, MatchValue
        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=seed_vec,
            query_filter=Filter(must=[
                FieldCondition(key="section_tag", match=MatchValue(value=tag)),
            ]),
            limit=limit_per_slot,
        )

        results[tag] = [{
            "score": hit.score,
            "payload": hit.payload,
        } for hit in response.points]

    return results


def format_results(results: list[dict], max_lines: int = 4) -> str:
    lines = []
    for i, r in enumerate(results):
        p = r["payload"]
        gran = p.get("granularity", "section")
        repeat = p.get("repeat_count", 1)
        header = (f"  [{i + 1}] score={r['score']:.4f} [{p.get('section_tag_raw', '')}] "
                  f"song={p.get('song_id', '?')} ({gran})")
        if repeat > 1:
            header += f" ×{repeat}"
        lines.append(header)
        text_lines = p.get("text", "").split("\n")
        for tl in text_lines[:max_lines]:
            lines.append(f"      {tl}")
        if len(text_lines) > max_lines:
            lines.append(f"      ... ({len(text_lines)} lines)")
        lines.append(f"      genre: {p.get('genre', '')}")
    return "\n".join(lines)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: lyrics_retriever.py search|match-sp|assemble [options]")
        sys.exit(1)

    mode = args[0]

    if mode == "search":
        query = args[1] if len(args) > 1 else "사랑"
        section = None
        genre = None
        granularity = None
        limit = 5
        for a in args[2:]:
            if a.startswith("--section="):
                section = a.split("=")[1]
            elif a.startswith("--genre="):
                genre = a.split("=")[1]
            elif a.startswith("--granularity="):
                granularity = a.split("=")[1]
            elif a.startswith("--limit="):
                limit = int(a.split("=")[1])

        label = f"Theme Search: '{query}'"
        if section:
            label += f" section={section}"
        if granularity:
            label += f" granularity={granularity}"
        if genre:
            label += f" genre={genre}"
        print(label)
        results = theme_search(query, section_tag=section, genre=genre,
                               granularity=granularity, limit=limit)
        print(format_results(results))

    elif mode == "match-sp":
        sp = args[1] if len(args) > 1 else ""
        sections = ["verse", "chorus", "bridge"]
        granularity = None
        for a in args[2:]:
            if a.startswith("--sections="):
                sections = a.split("=")[1].split(",")
            elif a.startswith("--granularity="):
                granularity = a.split("=")[1]
        print(f"SP Match: '{sp[:60]}...'" +
              (f" granularity={granularity}" if granularity else ""))
        results = match_sp(sp, sections=sections, granularity=granularity)
        for section, hits in results.items():
            print(f"\n--- {section} ---")
            print(format_results(hits))

    elif mode == "assemble":
        seed_song = None
        seed_text = None
        for a in args[1:]:
            if a.startswith("--seed-song="):
                seed_song = int(a.split("=")[1])
            elif a.startswith("--seed-text="):
                seed_text = a.split("=")[1]
        print(f"Coherent Assemble: seed_song={seed_song}")
        results = coherent_assemble(seed_song_id=seed_song, seed_text=seed_text)
        for tag, hits in results.items():
            print(f"\n--- {tag} ---")
            print(format_results(hits))
