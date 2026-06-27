#!/usr/bin/env python3
"""
lyrics_engine.py — Lyrics Corpus Retrieval Engine CLI.

Commands:
    search     Search lyrics sections by theme/keyword
    match-sp   Find lyrics matching an SP preset's genre/mood
    assemble   Build a coherent lyrics sheet from a seed section
    pair       Generate SP preset + matching lyrics in one shot
    batch      Generate N SP+lyrics packages with validation
    stats      Show Qdrant collection and corpus stats

Usage:
    python scripts/lyrics_engine.py search "밤하늘 아래" --section=chorus
    python scripts/lyrics_engine.py match-sp "K-Pop ballad. Clean electric guitar..."
    python scripts/lyrics_engine.py assemble --seed-song=1
    python scripts/lyrics_engine.py pair --seed="acoustic guitar" --drift=0.5
    python scripts/lyrics_engine.py batch --count=5 --validate
    python scripts/lyrics_engine.py stats
"""

import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

HISTORY_DIR = PROJECT_ROOT / "data" / "lyrics_history"
LYRICS_CORPUS_FILE = PROJECT_ROOT / "data" / "lyrics_chunks.json"

# 완화 가드 파라미터 (2026-06-24 자가점검: exclude-history가 코퍼스 source song의
# 97.7%(337/345)를 배제 → 잔여 8곡 → N017~N019 폴백/누출 연쇄의 근본원인).
# 잔여 가용 source song이 하한 밑이면 "전체 history 배제"를 풀어 최근 배치만 배제하고
# (오래된 source 재활용 허용) jaccard 임계를 강화해 근사중복을 막는다.
MIN_FRESH_POOL = 40       # 잔여 가용 source song 하한
RECENCY_WINDOW = 6        # 고갈 시 최근 N개 배치 파일만 배제
RELAXED_JACCARD = 0.35    # 재사용 허용 시 텍스트 유사도 가드 강화 (기본 0.5 → 0.35)


def _load_history_song_ids() -> set:
    """이전 배치 파일에서 사용된 song_id를 모두 수집 (크로스 배치 오염 방지)."""
    return _collect_history_song_ids(sorted(HISTORY_DIR.glob("lyrics_batch_*.json"))
                                     if HISTORY_DIR.exists() else [])


def _collect_history_song_ids(paths) -> set:
    """주어진 배치 파일 목록에서 _source_song_ids 수집."""
    sids = set()
    for p in paths:
        try:
            with open(p) as f:
                data = json.load(f)
            if not isinstance(data, list):
                continue
            for entry in data:
                for sid in entry.get("_source_song_ids", []):
                    sids.add(sid)
        except (json.JSONDecodeError, KeyError, OSError):
            continue
    return sids


def _corpus_song_count() -> int:
    """가사 코퍼스의 distinct source song 수 (풀 고갈 판정 기준)."""
    try:
        with open(LYRICS_CORPUS_FILE) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return 0
    chunks = data if isinstance(data, list) else data.get("chunks", [])
    sids = set()
    for ch in chunks:
        if not isinstance(ch, dict):
            continue
        sid = ch.get("song_id")
        if sid is None and isinstance(ch.get("payload"), dict):
            sid = ch["payload"].get("song_id")
        if sid is not None:
            sids.add(sid)
    return len(sids)


def _resolve_history_exclusion(default_jaccard: float):
    """exclude-history 적용 song_id와 jaccard 임계를 풀 잔여량에 따라 결정.

    잔여 가용 source song(코퍼스 - 누적배제)이 MIN_FRESH_POOL 미만이면 완화모드:
    전체 history 대신 최근 RECENCY_WINDOW개 배치만 배제하고 jaccard를 강화해
    오래된 source song 재사용을 허용한다. 반환: (exclude_sids, jaccard, relaxed, info).
    """
    all_paths = (sorted(HISTORY_DIR.glob("lyrics_batch_*.json"))
                 if HISTORY_DIR.exists() else [])
    all_sids = _collect_history_song_ids(all_paths)
    corpus_n = _corpus_song_count()
    fresh = (corpus_n - len(all_sids)) if corpus_n else None
    info = {"corpus_n": corpus_n, "excluded_all": len(all_sids), "fresh": fresh}
    if corpus_n and fresh is not None and fresh < MIN_FRESH_POOL:
        win_sids = _collect_history_song_ids(all_paths[-RECENCY_WINDOW:])
        info["windowed"] = len(win_sids)
        return win_sids, RELAXED_JACCARD, True, info
    return all_sids, default_jaccard, False, info


def cmd_search(args: list[str]):
    from lyrics_retriever import theme_search, format_results, get_client, get_model

    query = "사랑"
    section = None
    genre = None
    language = None
    limit = 5

    positional_done = False
    for a in args:
        if a.startswith("--section="):
            section = a.split("=")[1]
        elif a.startswith("--genre="):
            genre = a.split("=")[1]
        elif a.startswith("--language="):
            language = a.split("=")[1]
        elif a.startswith("--limit="):
            limit = int(a.split("=")[1])
        elif not a.startswith("--") and not positional_done:
            query = a
            positional_done = True

    print(f"Search: '{query}'" +
          (f" section={section}" if section else "") +
          (f" genre={genre}" if genre else ""))
    print()

    client = get_client()
    model = get_model()
    results = theme_search(query, section_tag=section, genre=genre,
                           language=language, limit=limit,
                           client=client, model=model)
    print(format_results(results))


def cmd_match_sp(args: list[str]):
    from lyrics_retriever import match_sp, format_results, get_client, get_model

    sp_text = ""
    sections = ["verse", "chorus", "bridge"]
    from_preset = False
    seed = "acoustic guitar"
    drift = 0.5

    for a in args:
        if a.startswith("--sections="):
            sections = a.split("=")[1].split(",")
        elif a.startswith("--from-preset"):
            from_preset = True
        elif a.startswith("--seed="):
            seed = a.split("=")[1]
        elif a.startswith("--drift="):
            drift = float(a.split("=")[1])
        elif not a.startswith("--"):
            sp_text = a

    if from_preset:
        from serendipity import controlled_drift, get_client as sp_client, get_model as sp_model
        from slot_assembler import assemble_sp
        preset = controlled_drift(seed, drift_factor=drift,
                                  client=sp_client(), model=sp_model())
        sp_text = assemble_sp(preset)
        print(f"Generated SP ({len(sp_text)} chars): {sp_text[:80]}...")
        print()

    if not sp_text:
        print("Need SP text or --from-preset flag")
        return

    client = get_client()
    model = get_model()
    results = match_sp(sp_text, sections=sections, client=client, model=model)

    for section, hits in results.items():
        print(f"--- {section} ---")
        print(format_results(hits))
        print()


def cmd_assemble(args: list[str]):
    from lyrics_retriever import coherent_assemble, get_client, get_model
    from lyrics_assembler import assemble_lyrics, lyrics_summary
    from lyrics_validator import validate_lyrics, print_validation

    seed_song = None
    seed_text = None
    do_validate = False

    for a in args:
        if a.startswith("--seed-song="):
            seed_song = int(a.split("=")[1])
        elif a.startswith("--seed-text="):
            seed_text = a.split("=")[1]
        elif a == "--validate":
            do_validate = True

    client = get_client()
    model = get_model()

    results = coherent_assemble(
        seed_song_id=seed_song, seed_text=seed_text,
        client=client, model=model,
    )

    if not results:
        return

    selected = {}
    metas = []
    for tag, hits in results.items():
        if hits:
            best = hits[0]["payload"]
            selected[tag] = best
            metas.append(best)

    print("=== Selected Sections ===")
    print(lyrics_summary(selected))
    print()

    lyrics = assemble_lyrics(selected)
    print("=== Assembled Lyrics ===")
    print(lyrics)
    print(f"\nLength: {len(lyrics)} chars")

    if do_validate:
        print()
        result = validate_lyrics(lyrics, sections_meta=metas)
        print_validation(result)


def cmd_pair(args: list[str]):
    from serendipity import controlled_drift
    from serendipity import get_client as sp_get_client, get_model as sp_get_model
    from slot_assembler import assemble_sp
    from preset_validator import validate_sp, print_validation as sp_print_validation
    from lyrics_retriever import (match_sp_differentiated, extract_sp_genre,
                                  get_client, get_model)
    from lyrics_assembler import assemble_lyrics
    from lyrics_validator import validate_lyrics, print_validation as lyr_print_validation
    from song_forms import classify_genre_group, select_form, form_to_arrow
    from title_generator import generate_title

    seed = "acoustic guitar"
    drift = 0.5
    do_validate = False
    genre_group_override = None
    form_variant = None
    theme = None
    do_refine = False

    for a in args:
        if a.startswith("--seed="):
            seed = a.split("=")[1]
        elif a.startswith("--drift="):
            drift = float(a.split("=")[1])
        elif a == "--validate":
            do_validate = True
        elif a.startswith("--genre-group="):
            genre_group_override = a.split("=")[1]
        elif a.startswith("--form="):
            form_variant = a.split("=")[1]
        elif a.startswith("--theme="):
            theme = a.split("=")[1]
        elif a == "--refine":
            do_refine = True

    theme_label = f", theme='{theme}'" if theme else ""
    print(f"Pair: seed='{seed}', drift={drift}{theme_label}")
    print()

    sp_client = sp_get_client()
    sp_model = sp_get_model()
    preset = controlled_drift(seed, drift_factor=drift, client=sp_client, model=sp_model)
    sp_text = assemble_sp(preset)

    genre_group = genre_group_override or classify_genre_group(extract_sp_genre(sp_text))
    form = select_form(genre_group, variant=form_variant)

    print(f"=== SP ({len(sp_text)} chars) ===")
    print(sp_text)
    print(f"\nGenre Group: {genre_group} | Form: {form_to_arrow(form)}")
    print()

    lyr_client = get_client()
    lyr_model = get_model()
    matched = match_sp_differentiated(sp_text, form=form,
                                      client=lyr_client, model=lyr_model,
                                      sp_client=sp_client, sp_model=sp_model,
                                      genre_group=genre_group,
                                      theme=theme)

    selected = {}
    metas = []
    bracket_count = 0
    for tag, hits in matched.items():
        if hits:
            best_payload = hits[0]["payload"]
            selected[tag] = best_payload
            if best_payload.get("source") == "bracket_preset":
                bracket_count += 1
            else:
                metas.append(best_payload)

    lyrics = assemble_lyrics(selected, structure=form)

    if do_refine and theme:
        from lyrics_refiner import refine_lyrics
        lyrics_before = lyrics
        lyrics = refine_lyrics(lyrics, theme=theme)
        if lyrics != lyrics_before:
            print(f"[Refined: theme='{theme}']")

    title_result = generate_title(lyrics, sp_text, genre_group=genre_group)

    print(f"=== Title: \"{title_result['title']}\" [{title_result['strategy']}] ===")
    if title_result["alternatives"]:
        print(f"    alt: {title_result['alternatives'][:3]}")
    print()
    print(f"=== Lyrics ({len(lyrics)} chars, brackets={bracket_count}) ===")
    print(lyrics)

    if do_validate:
        print()
        print("--- SP Validation ---")
        sp_result = validate_sp(sp_text)
        sp_print_validation(sp_result)

        print("--- Lyrics Validation ---")
        lyr_result = validate_lyrics(lyrics, sections_meta=metas, song_form=form)
        lyr_print_validation(lyr_result)


def cmd_batch(args: list[str]):
    from serendipity import controlled_drift
    from serendipity import get_client as sp_get_client, get_model as sp_get_model
    from slot_assembler import assemble_sp
    from preset_validator import validate_sp
    from lyrics_retriever import (match_sp_differentiated, extract_sp_genre,
                                  get_client, get_model)
    from lyrics_assembler import assemble_lyrics
    from lyrics_validator import validate_lyrics
    from song_forms import classify_genre_group, select_form, form_to_arrow
    from title_generator import generate_title, batch_titles
    from lyrics_themes import list_themes

    count = 5
    seed = "acoustic guitar"
    drift = 0.5
    do_validate = True
    save = False
    genre_group_override = None
    form_variant = None
    theme = None
    do_refine = False
    exclude_history = False
    genre_filter = None

    for a in args:
        if a.startswith("--count="):
            count = int(a.split("=")[1])
        elif a.startswith("--seed="):
            seed = a.split("=")[1]
        elif a.startswith("--drift="):
            drift = float(a.split("=")[1])
        elif a == "--save":
            save = True
        elif a == "--no-validate":
            do_validate = False
        elif a.startswith("--genre-group="):
            genre_group_override = a.split("=")[1]
        elif a.startswith("--form="):
            form_variant = a.split("=")[1]
        elif a.startswith("--theme="):
            theme = a.split("=")[1]
        elif a == "--refine":
            do_refine = True
        elif a == "--exclude-history":
            exclude_history = True
        elif a.startswith("--genre-filter="):
            genre_filter = a.split("=", 1)[1]

    theme_label = f", theme='{theme}'" if theme else ""
    refine_label = " +refine" if do_refine else ""
    excl_label = " +exclude-history" if exclude_history else ""
    excl_label += f" +genre-filter={genre_filter}" if genre_filter else ""
    print(f"Batch: {count} SP+lyrics packages, seed='{seed}', drift={drift}{theme_label}{refine_label}{excl_label}")
    print()

    sp_client = sp_get_client()
    sp_model = sp_get_model()
    lyr_client = get_client()
    lyr_model = get_model()

    results = []
    t0 = time.time()
    form_counts = {}
    batch_used_ids = set()
    batch_used_texts = set()
    batch_used_song_ids = set()
    batch_used_forms = []
    # --theme 미지정 시 테마 풀에서 곡별 로테이션 (theme/sub_theme 공란 + refine 무효 방지)
    theme_pool = list_themes()

    import lyrics_retriever
    jaccard_reject = lyrics_retriever.JACCARD_REJECT
    if exclude_history:
        excl_sids, jaccard_reject, relaxed, info = _resolve_history_exclusion(
            lyrics_retriever.JACCARD_REJECT)
        batch_used_song_ids.update(excl_sids)
        if relaxed:
            print(f"  [exclude-history] ⚠ 풀 고갈 — 코퍼스 {info['corpus_n']}곡 중 "
                  f"{info['excluded_all']} 배제 → 잔여 {info['fresh']} < {MIN_FRESH_POOL}. "
                  f"완화모드: 최근 {RECENCY_WINDOW}배치 {info['windowed']}곡만 배제 + "
                  f"jaccard {lyrics_retriever.JACCARD_REJECT}→{jaccard_reject}")
        else:
            print(f"  [exclude-history] {len(excl_sids)} song_ids loaded "
                  f"(잔여 가용 source {info['fresh']}곡)")
        print()

    for i in range(count):
        song_theme = theme if theme else theme_pool[i % len(theme_pool)]
        preset = controlled_drift(seed, drift_factor=drift,
                                  client=sp_client, model=sp_model,
                                  genre_filter=genre_filter)
        sp_text = assemble_sp(preset)

        genre_group = genre_group_override or classify_genre_group(
            extract_sp_genre(sp_text))
        form = select_form(genre_group, variant=form_variant,
                           avoid_forms=batch_used_forms)
        form_key = form_to_arrow(form)
        form_counts[form_key] = form_counts.get(form_key, 0) + 1
        batch_used_forms.append(form)

        matched = match_sp_differentiated(sp_text, form=form,
                                          client=lyr_client, model=lyr_model,
                                          sp_client=sp_client, sp_model=sp_model,
                                          genre_group=genre_group,
                                          theme=song_theme,
                                          batch_used_ids=batch_used_ids,
                                          batch_used_texts=batch_used_texts,
                                          batch_used_song_ids=batch_used_song_ids,
                                          jaccard_reject=jaccard_reject)
        selected = {}
        metas = []
        bracket_count = 0
        for tag, hits in matched.items():
            if hits:
                best = hits[0]
                pid = best.get("point_id")
                if pid is not None:
                    batch_used_ids.add(pid)
                best_payload = best["payload"]
                best_text = best_payload.get("text", "").strip()
                if best_text and best_payload.get("source") != "bracket_preset":
                    batch_used_texts.add(best_text)
                best_sid = best_payload.get("song_id")
                if best_sid and best_payload.get("source") != "bracket_preset":
                    batch_used_song_ids.add(best_sid)
                selected[tag] = best_payload
                if best_payload.get("source") == "bracket_preset":
                    bracket_count += 1
                else:
                    metas.append(best_payload)

        lyrics = assemble_lyrics(selected, structure=form)

        if do_refine:
            from lyrics_refiner import refine_lyrics
            lyrics = refine_lyrics(lyrics, theme=song_theme)

        title_result = generate_title(lyrics, sp_text, genre_group=genre_group)

        sub_theme_used = ""
        if matched and isinstance(matched, dict):
            for _k, _v in matched.items():
                if _v and isinstance(_v, list) and _v[0]:
                    _payload = _v[0].get("payload", {})
                    sub_theme_used = _payload.get("_sub_theme", "")
                    if sub_theme_used:
                        break

        song_source_ids = []
        for tag, hits in matched.items():
            if hits:
                sid = hits[0].get("payload", {}).get("song_id")
                if sid and hits[0].get("payload", {}).get("source") != "bracket_preset":
                    song_source_ids.append(sid)
        song_source_ids = sorted(set(song_source_ids), key=lambda x: str(x))

        entry = {
            "index": i,
            "title": title_result["title"],
            "title_strategy": title_result["strategy"],
            "title_alternatives": title_result["alternatives"],
            "sp": sp_text,
            "lyrics": lyrics,
            "sp_length": len(sp_text),
            "lyrics_length": len(lyrics),
            "genre_group": genre_group,
            "song_form": form,
            "song_form_type": form_key,
            "bracket_sections": bracket_count,
            "theme": song_theme,
            "sub_theme": sub_theme_used,
            "refined": do_refine,
            "_source_song_ids": song_source_ids,
        }

        if do_validate:
            sp_val = validate_sp(sp_text)
            lyr_val = validate_lyrics(lyrics, sections_meta=metas, song_form=form)
            entry["sp_validation"] = sp_val
            entry["lyrics_validation"] = lyr_val
            br_label = f" br={bracket_count}" if bracket_count else ""
            print(f"  [{i + 1:3d}/{count}] \"{title_result['title'][:15]}\" "
                  f"SP={len(sp_text)}c [{sp_val['verdict']}] "
                  f"| Lyrics={len(lyrics)}c [{lyr_val['verdict']}] "
                  f"coh={lyr_val['coherence_score']:.2f}{br_label} "
                  f"| {genre_group} [{form_key[:40]}]")
        else:
            br_label = f" br={bracket_count}" if bracket_count else ""
            print(f"  [{i + 1:3d}/{count}] \"{title_result['title'][:15]}\" "
                  f"SP={len(sp_text)}c | Lyrics={len(lyrics)}c{br_label} "
                  f"| {genre_group}")

        results.append(entry)

    results = batch_titles(results)

    elapsed = time.time() - t0
    print(f"\nGenerated {count} packages in {elapsed:.1f}s")
    print(f"  Forms used: {len(form_counts)} distinct")
    for fk, fc in sorted(form_counts.items(), key=lambda x: -x[1]):
        print(f"    {fc}x  {fk[:60]}")

    if do_validate:
        sp_pass = sum(1 for r in results if r["sp_validation"]["verdict"] == "PASS")
        lyr_pass = sum(1 for r in results if r["lyrics_validation"]["verdict"] == "PASS")
        avg_coh = sum(r["lyrics_validation"]["coherence_score"] for r in results) / len(results)
        print(f"  SP: {sp_pass}/{count} PASS")
        print(f"  Lyrics: {lyr_pass}/{count} PASS")
        print(f"  Avg coherence: {avg_coh:.2f}")

    if save:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_path = HISTORY_DIR / f"lyrics_batch_{ts}.json"
        with open(out_path, "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"  Saved to {out_path}")


def cmd_stats(args: list[str]):
    from lyrics_embed_pipeline import cmd_stats as qdrant_stats

    chunks_file = PROJECT_ROOT / "data" / "lyrics_chunks.json"
    if chunks_file.exists():
        with open(chunks_file) as f:
            chunks = json.load(f)
        print(f"Local lyrics chunks: {len(chunks)}")
        by_tag = {}
        for c in chunks:
            tag = c["payload"]["section_tag"]
            by_tag[tag] = by_tag.get(tag, 0) + 1
        for tag, count in sorted(by_tag.items(), key=lambda x: -x[1]):
            print(f"  {tag}: {count}")
        print()

    print("Qdrant collection:")
    try:
        qdrant_stats()
    except Exception as e:
        print(f"  (unavailable: {e})")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    rest = args[1:]

    commands = {
        "search": cmd_search,
        "match-sp": cmd_match_sp,
        "assemble": cmd_assemble,
        "pair": cmd_pair,
        "batch": cmd_batch,
        "stats": cmd_stats,
    }

    if cmd in commands:
        commands[cmd](rest)
    elif cmd in ("--help", "-h"):
        print(__doc__)
    else:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(commands.keys())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
