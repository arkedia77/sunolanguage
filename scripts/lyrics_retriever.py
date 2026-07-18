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
# 별도 계보 — 가사변형(패러프레이즈) 코퍼스. 본코퍼스 불혼입, opt-in 참조 전용.
# 승격: scripts/promote_lyric_variants_qdrant.py (동일 384dim 다국어 공간)
VARIANTS_COLLECTION = "sunolang_lyric_variants"
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


def variant_search(query: str, section_tag: str = None, limit: int = 10,
                   exclude_song_ids: set = None, min_cosine_to_src: float = None,
                   client=None, model=None) -> list[dict]:
    """opt-in 가사변형(패러프레이즈) 검색 — 풀고갈(exclude-history 고갈) 완화용 다양성 소스.

    본코퍼스(sunolang_lyrics)와 분리된 별도 계보. 기본 리트리버 경로는 호출하지 않음
    (엔진이 잔여 풀 고갈 시에만 명시적으로 참조). 반환 dict엔 source='variation'과
    변형↔원문 추적(source_song_id/original_text)을 붙여 하류가 비-네이티브임을 구분.

    section_tag=변형의 섹션(verse/chorus 등), exclude_song_ids=원곡 song_id 배제,
    min_cosine_to_src=변형-원문 의미보존 하한(저보존 변형 컷).
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    conditions = []
    if section_tag:
        conditions.append(FieldCondition(key="section_tag", match=MatchValue(value=section_tag)))
    if min_cosine_to_src is not None:
        conditions.append(FieldCondition(key="cosine_to_src", range=Range(gte=min_cosine_to_src)))
    must_not = []
    if exclude_song_ids:
        for sid in exclude_song_ids:
            must_not.append(FieldCondition(key="source_song_id", match=MatchValue(value=sid)))
    query_filter = Filter(must=conditions or None, must_not=must_not or None) \
        if (conditions or must_not) else None

    response = client.query_points(
        collection_name=VARIANTS_COLLECTION,
        query=model.encode(query).tolist(),
        query_filter=query_filter,
        limit=limit,
    )
    return [{
        "score": hit.score,
        "source": "variation",
        "text": hit.payload.get("variant_text"),
        "source_song_id": hit.payload.get("source_song_id"),
        "original_text": hit.payload.get("original_text"),
        "section_tag": hit.payload.get("section_tag"),
        "cosine_to_src": hit.payload.get("cosine_to_src"),
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
                            batch_used_song_ids: set = None,
                            jaccard_reject: float = None,
                            use_variants: bool = False,
                            variant_min_cosine: float = 0.85) -> dict[str, list[dict]]:
    from song_forms import get_section_query_hint, classify_genre_group
    from bracket_presets import retrieve_bracket_directives, format_bracket_section

    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    # jaccard_reject 미지정 시 모듈 기본값. 완화모드(풀 고갈)에선 lyrics_engine이
    # 더 낮은 값(예: 0.35)을 주입 — source song 재사용 허용을 텍스트 유사도 가드
    # 강화로 보상(재사용 곡이 근사중복 텍스트를 내는 것 차단). 2026-06-24.
    jr = JACCARD_REJECT if jaccard_reject is None else jaccard_reject

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

        def _is_lyric_leak(text: str) -> bool:
            # 코어 가사섹션(verse/pre_chorus/bridge)에 한글이 전혀 없으면 영어 악기
            # 디렉티브 누출로 간주("Synth lead melody soars above" 류). is_sp_directive가
            # 못 잡는 영어 악기서술을 차단 — N시리즈는 한국어 가사. 2026-06-19.
            return re.search(r"[가-힣]", text) is None

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
                if needs_min_lines and _is_lyric_leak(t):
                    continue
                # T1-3: song_id가 달라도 유사 텍스트(동일 코러스 변형 등) reject
                if _max_jaccard(t, used_texts) > jr:
                    continue
                return [h]
            # 코어섹션 중간 폴백: 최소행은 유지한 채 유사도(Jaccard)만 완화.
            # 1순위가 모두 걸러져도 1행/악기누출 섹션으로 떨어지지 않게 함. 2026-06-19.
            if needs_min_lines:
                for h in candidates:
                    t = h["payload"].get("text", "").strip()
                    if (t and t not in used_texts and not is_sp_directive(t)
                            and not _is_lyric_leak(t)
                            and _count_lyric_lines(t) >= MIN_VERSE_LINES):
                        return [h]
            for h in candidates:
                t = h["payload"].get("text", "").strip()
                if not (t and t not in used_texts and not is_sp_directive(t)
                        and _max_jaccard(t, used_texts) <= jr):
                    continue
                # 코어섹션은 이 폴백에서도 누출/1행 거부(영어 악기서술 가로채기 방지). 2026-06-19.
                if needs_min_lines and (_is_lyric_leak(t)
                                        or _count_lyric_lines(t) < MIN_VERSE_LINES):
                    continue
                return [h]
            # 최종 폴백: 코어섹션은 누출/1행을 절대 반환 안 함. 정상(한글+최소행)
            # 비중복 섹션이 없으면 빈 반환(악기누출/1행/V1=V2 < 빈 섹션). 2026-06-19.
            if needs_min_lines:
                for h in candidates:
                    t = h["payload"].get("text", "").strip()
                    if (t and t not in used_texts and not is_sp_directive(t)
                            and not _is_lyric_leak(t)
                            and _count_lyric_lines(t) >= MIN_VERSE_LINES):
                        return [h]
                return []
            return candidates[:1] if candidates else []

        def _variant_fill(needs_min_lines: bool):
            # 풀 고갈 최종 폴백 — 별도 계보(가사변형) 참조. 정규 코퍼스가 신규 라인을
            # 못 내는 섹션에 한해, 의미보존(cosine_to_src≥임계) 변형을 조립해 빈 섹션을
            # 방지. song_id=0·source='variation'으로 비-네이티브 표기(원장 오염 없음).
            from corpus_quality_gate import is_sp_directive
            cands = variant_search(
                section_query, section_tag=tag, limit=25,
                exclude_song_ids=exclude_song_ids or None,
                min_cosine_to_src=variant_min_cosine, client=client, model=model,
            )
            picked, picked_texts = [], set(used_texts)
            for h in cands:
                t = (h.get("text") or "").strip()
                if not t or t in picked_texts or is_sp_directive(t) or _is_lyric_leak(t):
                    continue
                if _max_jaccard(t, picked_texts) > jr:
                    continue
                picked.append(h)
                picked_texts.add(t)
                if not needs_min_lines or len(picked) >= MIN_VERSE_LINES:
                    break
            if not picked or (needs_min_lines and len(picked) < MIN_VERSE_LINES):
                return []  # 코어섹션 1행 방지 불변 유지
            block = "\n".join((h.get("text") or "").strip() for h in picked)
            return [{
                "score": picked[0]["score"],
                "point_id": None,
                "payload": {
                    "text": block, "section_tag": tag, "genre": genre,
                    "song_id": 0, "source": "variation",
                    "variant_source_song_ids": [h.get("source_song_id") for h in picked],
                },
            }]

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

        # 완화모드(풀 고갈) 한정: 무제한 base_query 재사용(배제곡 포함) 전에 가사변형 폴백을
        # 우선 시도 — 신규 다양성을 stale 재사용보다 앞세운다. base_query가 배제 무시로 항상
        # 채워 variant를 선점하던 문제 수정(2026-07-18, Leo 승인). variant 실패 시 아래 base_query가
        # 최종 net으로 1행/빈섹션 방지(코어섹션 min-lines 불변 유지).
        if not hits and use_variants:
            hits = _variant_fill(tag in ("verse", "pre_chorus", "bridge"))

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
