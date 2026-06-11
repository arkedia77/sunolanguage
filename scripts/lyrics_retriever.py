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

MIN_VERSE_LINES = 3

# T1-3 Jaccard 단편중복 인루프 가드 (가사워크플로우 보강안):
# song_id dedup 사각지대 — id가 달라도 동일/유사 코러스 텍스트 존재.
# 후보 vs 이미 선택된 섹션 토큰 Jaccard > 0.5 → reject.
# 임계 0.5는 echo 측정 평균(7.6%) 대비 충분히 보수적.
JACCARD_REJECT = 0.5


def _token_set(text: str) -> frozenset:
    """한/영/숫자 토큰셋 — 한국어 가사 호환 (measure_echo의 영문 전용 토큰화 일반화)."""
    return frozenset(re.findall(r"[가-힣a-zA-Z0-9]+", text.lower()))


def _max_jaccard(text: str, used_texts: set) -> float:
    """후보 텍스트 vs 기선택 섹션들 최대 토큰 Jaccard."""
    toks = _token_set(text)
    if not toks:
        return 0.0
    best = 0.0
    for u in used_texts:
        ut = _token_set(u)
        if not ut:
            continue
        inter = len(toks & ut)
        if inter:
            best = max(best, inter / len(toks | ut))
    return best

MOOD_WORDS = {
    "intimate", "emotional", "warm", "melancholic", "dreamy", "nostalgic",
    "energetic", "driving", "aggressive", "smooth", "groovy", "bright",
    "dark", "atmospheric", "raw", "soulful", "euphoric", "chill",
    "passionate", "gentle", "powerful", "serene", "lush", "sparse",
    "breathy", "punchy", "crisp", "distorted", "clean", "soft", "heavy",
    "funky", "mellow", "haunting", "uplifting", "lonely", "romantic",
}


def get_client():
    from qdrant_client import QdrantClient
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY)


def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def make_filter(section_tag: str = None, genre: str = None, language: str = None,
                granularity: str = None, exclude_song_ids: set = None,
                exclude_point_ids: set = None):
    from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchText, HasIdCondition

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
    if exclude_point_ids:
        must_not.append(HasIdCondition(has_id=list(exclude_point_ids)))

    if not conditions and not must_not:
        return None
    return Filter(must=conditions or None, must_not=must_not or None)


def theme_search(query: str, section_tag: str = None, genre: str = None,
                 language: str = None, granularity: str = None, limit: int = 10,
                 exclude_song_ids: set = None,
                 exclude_point_ids: set = None,
                 client=None, model=None) -> list[dict]:
    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    embedding = model.encode(query).tolist()
    query_filter = make_filter(section_tag, genre, language, granularity,
                               exclude_song_ids=exclude_song_ids,
                               exclude_point_ids=exclude_point_ids)

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        query_filter=query_filter,
        limit=limit,
    )

    return [{
        "score": hit.score,
        "payload": hit.payload,
        "point_id": hit.id,
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


def _detect_language(text: str) -> str:
    korean_chars = len(re.findall(r'[가-힯]', text))
    ascii_chars = len(re.findall(r'[a-zA-Z]', text))
    if korean_chars > ascii_chars:
        return "Korean"
    if ascii_chars > korean_chars:
        return "English"
    return ""


def match_sp_differentiated(sp_text: str, form: list[str],
                            granularity: str = None, limit_per_section: int = 5,
                            client=None, model=None,
                            sp_client=None, sp_model=None,
                            genre_group: str = None,
                            theme: str = None,
                            batch_used_ids: set = None,
                            batch_used_texts: set = None,
                            batch_used_song_ids: set = None) -> dict[str, list[dict]]:
    from song_forms import get_section_query_hint, classify_genre_group
    from bracket_presets import retrieve_bracket_directives, format_bracket_section

    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    genre = extract_sp_genre(sp_text)
    moods = extract_sp_mood(sp_text)
    base_query = genre
    if moods:
        base_query += " " + " ".join(moods)

    sub_theme = None
    if theme:
        from lyrics_themes import get_theme_query, pick_sub_theme
        sub_theme = pick_sub_theme(theme)
        theme_query = get_theme_query(theme, sub_theme=sub_theme)
        if theme_query:
            base_query = f"{theme_query} {base_query}"

    _sub_theme_tag = sub_theme or ""

    if genre_group is None:
        genre_group = classify_genre_group(genre)

    NON_LYRIC_TAGS = {"intro", "outro", "interlude", "instrumental"}

    section_counts = {}
    results = {}
    used_song_ids = {}
    used_bracket_texts = set()
    song_point_ids = set(batch_used_ids) if batch_used_ids else set()
    used_texts = set(batch_used_texts) if batch_used_texts else set()
    exclude_song_ids = set(batch_used_song_ids) if batch_used_song_ids else set()
    detected_lang = None
    prev_verse_text = None

    for tag in form:
        section_counts[tag] = section_counts.get(tag, 0) + 1
        occurrence = section_counts[tag]
        indexed_key = f"{tag}_{occurrence}"

        if tag in NON_LYRIC_TAGS:
            if tag in results:
                continue
            directives = retrieve_bracket_directives(
                section_type=tag,
                sp_text=sp_text,
                genre_group=genre_group,
                client=sp_client,
                model=sp_model,
                exclude_texts=used_bracket_texts,
            )
            if directives:
                bracket_text = format_bracket_section(tag, directives)
                for d in directives:
                    used_bracket_texts.add(d["text"])
                results[tag] = [{
                    "score": directives[0]["score"],
                    "payload": {
                        "text": bracket_text,
                        "section_tag": tag,
                        "genre": directives[0].get("genre", ""),
                        "song_id": 0,
                        "source": "bracket_preset",
                        "directives": directives,
                    },
                }]
            else:
                results[tag] = []
            continue

        if tag in ("chorus", "hook") and occurrence > 1:
            first_key = f"{tag}_1"
            if first_key in results and results[first_key]:
                results[indexed_key] = results[first_key]
                continue

        role_hint = get_section_query_hint(tag)
        section_query = f"{base_query} {role_hint}".strip()

        if tag == "verse" and occurrence > 1 and prev_verse_text:
            keywords = prev_verse_text[:60]
            section_query = f"{section_query} {keywords}"

        exclude = used_song_ids.get(tag, set()) if occurrence > 1 else set()

        lang_filter = detected_lang if detected_lang else None

        def _count_lyric_lines(text: str) -> int:
            lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
            return sum(1 for l in lines if not l.startswith("[") and not l.startswith("("))

        def _pick_novel(candidates):
            from corpus_quality_gate import is_sp_directive
            needs_min_lines = tag in ("verse", "pre_chorus", "bridge")
            for h in candidates:
                t = h["payload"].get("text", "").strip()
                if not t or t in used_texts:
                    continue
                if is_sp_directive(t):
                    continue
                if needs_min_lines and _count_lyric_lines(t) < MIN_VERSE_LINES:
                    continue
                # T1-3: song_id가 달라도 유사 텍스트(동일 코러스 변형 등) reject
                if _max_jaccard(t, used_texts) > JACCARD_REJECT:
                    continue
                return [h]
            for h in candidates:
                t = h["payload"].get("text", "").strip()
                if (t and t not in used_texts and not is_sp_directive(t)
                        and _max_jaccard(t, used_texts) <= JACCARD_REJECT):
                    return [h]
            return candidates[:1] if candidates else []

        combined_exclude = exclude | exclude_song_ids if exclude else (exclude_song_ids or None)

        hits = theme_search(
            section_query, section_tag=tag, granularity=granularity,
            language=lang_filter,
            limit=limit_per_section,
            exclude_song_ids=combined_exclude if combined_exclude else None,
            exclude_point_ids=song_point_ids if song_point_ids else None,
            client=client, model=model,
        )
        hits = _pick_novel(hits)

        if not hits and (song_point_ids or lang_filter):
            candidates = theme_search(
                section_query, section_tag=tag, granularity=granularity,
                limit=limit_per_section,
                exclude_song_ids=combined_exclude if combined_exclude else None,
                client=client, model=model,
            )
            hits = _pick_novel(candidates)

        if not hits and exclude:
            candidates = theme_search(
                section_query, section_tag=tag, granularity=granularity,
                limit=limit_per_section,
                exclude_song_ids=exclude_song_ids if exclude_song_ids else None,
                client=client, model=model,
            )
            hits = _pick_novel(candidates)

        FALLBACK_MAP = {"pre_chorus": "verse", "hook": "chorus", "drop": "chorus", "tag": "outro"}
        if not hits and tag in FALLBACK_MAP:
            fallback_tag = FALLBACK_MAP[tag]
            candidates = theme_search(
                section_query, section_tag=fallback_tag, granularity=granularity,
                limit=limit_per_section,
                exclude_song_ids=exclude_song_ids if exclude_song_ids else None,
                client=client, model=model,
            )
            hits = _pick_novel(candidates)

        if not hits:
            candidates = theme_search(
                base_query, section_tag=None, granularity=granularity,
                limit=limit_per_section, client=client, model=model,
            )
            hits = _pick_novel(candidates)

        results[indexed_key] = hits

        if hits:
            best = hits[0]
            best["payload"]["_sub_theme"] = _sub_theme_tag
            pid = best.get("point_id")
            if pid is not None:
                song_point_ids.add(pid)
            best_text = best["payload"].get("text", "").strip()
            if best_text:
                used_texts.add(best_text)
            sid = best["payload"].get("song_id")
            if sid:
                if tag not in used_song_ids:
                    used_song_ids[tag] = set()
                used_song_ids[tag].add(sid)
                exclude_song_ids.add(sid)
            if detected_lang is None and tag == "verse" and occurrence == 1:
                detected_lang = _detect_language(best_text) or None
            if tag == "verse":
                prev_verse_text = best_text

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
