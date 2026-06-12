#!/usr/bin/env python3
"""
사전 증분 큐레이션 병합기 (v3.1 → v3.2+)

build_dictionary_v3.py는 RETIRED (재실행 시 hand-curated v3.1을 v3.0으로 퇴행).
그 WARNING 블록이 요구하는 "incremental curated merge"의 구현이 이 스크립트다.

동작:
  1. 현행 큐레이션 사전(rag/suno_dictionary_v3.json)을 로드
  2. lexical_index.sqlite(최신 코퍼스로 재빌드된 상태여야 함)에서
     빈도 기반 섹션을 build_dictionary_v3의 섹션 함수로 재계산
  3. 병합 규칙:
     - 재계산 값이 베이스 (코퍼스 증분 반영)
     - 현행 사전에만 있는 키 = 수작업 큐레이션 추가분 → 그대로 보존
     - 양쪽에 있는 키: 재계산 값 우선 + 현행 엔트리의 추가 필드는 보존
     - 큐레이션 전용 축(negative_vocab/top_anchor_weights/genre_frontier/
       output_variance/studio_stem_map/dead_budget_findings/suno_does_not_use/
       inferred_vocab_status/sp_slot_vocab/update_notes)은 무변경
  4. version 범프 + update_notes 누적 + 사전 백업 후 기록

사용:
  python3 scripts/dictionary_incremental_merge.py                # dry-run (기본)
  python3 scripts/dictionary_incremental_merge.py --apply \
      --version 3.2 --note "Batch C 60곡 코퍼스 증분 (496→556트랙)"

전제: scripts/lexical_search_cli.py build 로 인덱스가 최신 코퍼스 기준으로
재빌드되어 있을 것. (전파 정책 docs/corpus_propagation_policy.md Class B1)
"""
import argparse
import json
import shutil
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_dictionary_v3 as b3  # 섹션 함수만 사용 — build()는 호출하지 않음 (import는 안전)

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "data/reanalysis_v2/lexical_index.sqlite"
DICT_PATH = BASE / "rag/suno_dictionary_v3.json"

# 재계산 대상 = 빈도 기반 섹션 (sqlite에서 산출되는 것 전부)
RECOMPUTED_SECTIONS = [
    "corpus", "instrument_phrases", "drum_vocab", "technique_patterns",
    "production_vocab", "key_signatures", "harmony_vocab", "mood_emotion",
    "tempo_rhythm", "dynamics_structure", "timbre_texture",
    "vocal_expressions", "vocal_chorus", "genre_vocabulary_map",
    "descriptor_combos",
]


def recompute_sections(cur):
    mood, timbre = b3.build_mood_and_timbre(cur)
    vocal_expr, vocal_chorus = b3.build_vocal(cur)
    return {
        "corpus": b3.build_corpus_stats(cur),
        "instrument_phrases": b3.build_instrument_phrases(cur),
        "drum_vocab": b3.build_drum_vocab(cur),
        "technique_patterns": b3.build_technique_patterns(cur),
        "production_vocab": b3.build_production_vocab(cur),
        "key_signatures": b3.build_key_signatures(cur),
        "harmony_vocab": b3.build_harmony_vocab(cur),
        "mood_emotion": mood,
        "tempo_rhythm": b3.build_tempo_rhythm(cur),
        "dynamics_structure": b3.build_dynamics_structure(cur),
        "timbre_texture": timbre,
        "vocal_expressions": vocal_expr,
        "vocal_chorus": vocal_chorus,
        "genre_vocabulary_map": b3.build_genre_vocabulary_map(cur),
        "descriptor_combos": b3.build_descriptor_combos(cur),
    }


def merge_section(current, computed):
    """재계산 베이스 + 큐레이션 보존. (merged, curated_kept, enriched_kept) 반환."""
    merged = dict(computed)
    curated_kept, enriched_kept = [], []
    for key, cur_val in current.items():
        if key not in computed:
            merged[key] = cur_val            # 큐레이션 추가분 보존
            curated_kept.append(key)
        elif isinstance(cur_val, dict) and isinstance(computed[key], dict):
            extra = {k: v for k, v in cur_val.items() if k not in computed[key]}
            if extra:
                merged[key] = {**computed[key], **extra}  # 추가 필드 보존
                enriched_kept.append(key)
    return merged, curated_kept, enriched_kept


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="실제 기록 (기본은 dry-run)")
    ap.add_argument("--version", default=None, help="새 버전 문자열 (예: 3.2)")
    ap.add_argument("--note", default=None, help="update_notes에 추가할 변경 요지")
    args = ap.parse_args()

    if not DB_PATH.exists():
        sys.exit(f"❌ 인덱스 없음: {DB_PATH} — lexical_search_cli.py build 먼저")
    current = json.loads(DICT_PATH.read_text())

    conn = sqlite3.connect(str(DB_PATH))
    computed = recompute_sections(conn.cursor())
    conn.close()

    old_tracks = current.get("corpus", {}).get("tracks_count")
    new_tracks = computed["corpus"]["tracks_count"]
    if new_tracks < (old_tracks or 0):
        sys.exit(f"❌ 축소 가드: 재계산 코퍼스 {new_tracks} < 현행 {old_tracks} — 인덱스가 stale일 가능성. 중단.")

    # corpus.sources는 빌더 하드코딩 대신 현행 사전의 목록을 승계 (호출자가 --note로 이력 기록)
    computed["corpus"]["sources"] = current.get("corpus", {}).get("sources", [])

    merged_dict = dict(current)
    summary = {}
    for sec in RECOMPUTED_SECTIONS:
        if sec == "corpus":
            merged_dict["corpus"] = computed["corpus"]
            continue
        cur_sec = current.get(sec, {})
        merged, curated, enriched = merge_section(cur_sec, computed[sec])
        merged_dict[sec] = merged
        summary[sec] = {
            "before": len(cur_sec), "after": len(merged),
            "curated_kept": curated, "enriched_kept": enriched,
        }

    # 메타 갱신
    if args.version:
        merged_dict["previous_version"] = (
            f"{current.get('version')} ({current.get('created_at')}, "
            f"{old_tracks}트랙)")
        merged_dict["version"] = args.version
    merged_dict["created_at"] = str(date.today())
    if args.note:
        prev_note = current.get("update_notes", "")
        merged_dict["update_notes"] = (prev_note + " | " if prev_note else "") + args.note

    # stats 재계산 (빌더와 동일 정의)
    merged_dict["stats"] = {
        "total_instrument_phrases": len(merged_dict["instrument_phrases"]),
        "total_drum_entities": len(merged_dict["drum_vocab"]),
        "total_technique_patterns": len(merged_dict["technique_patterns"]),
        "total_production_terms": len(merged_dict["production_vocab"]),
        "total_harmony_terms": len(merged_dict["harmony_vocab"]),
        "total_mood_terms": len(merged_dict["mood_emotion"]),
        "total_timbre_terms": len(merged_dict["timbre_texture"]),
        "total_vocal_expressions": len(merged_dict["vocal_expressions"]),
        "total_genres_mapped": len(merged_dict["genre_vocabulary_map"]),
        "total_descriptor_combos": len(merged_dict["descriptor_combos"]),
        "genre_frontier_count": current.get("stats", {}).get("genre_frontier_count", 0),
        "negative_vocab_categories": current.get("stats", {}).get("negative_vocab_categories", 0),
        "studio_stem_tracks": current.get("stats", {}).get("studio_stem_tracks", 0),
    }

    # 리포트
    print(f"코퍼스: {old_tracks} → {new_tracks}트랙 "
          f"(단어 {current.get('corpus',{}).get('unique_words')}→{computed['corpus']['unique_words']}, "
          f"장르 {current.get('corpus',{}).get('genres_count')}→{computed['corpus']['genres_count']})")
    total_curated = 0
    for sec, s in summary.items():
        if s["before"] != s["after"] or s["curated_kept"] or s["enriched_kept"]:
            tag = ""
            if s["curated_kept"]:
                tag = f"  [큐레이션 보존 {len(s['curated_kept'])}: {', '.join(s['curated_kept'][:6])}{'…' if len(s['curated_kept'])>6 else ''}]"
            total_curated += len(s["curated_kept"])
            print(f"  {sec:24s} {s['before']:5d} → {s['after']:5d}{tag}")
    print(f"큐레이션 보존 총계: {total_curated}건")
    if args.version:
        print(f"버전: {current.get('version')} → {args.version}")

    if not args.apply:
        print("\n(dry-run — 기록하려면 --apply)")
        return

    bak = DICT_PATH.with_suffix(f".json.bak_v{current.get('version','x')}")
    shutil.copy2(DICT_PATH, bak)
    DICT_PATH.write_text(json.dumps(merged_dict, ensure_ascii=False, indent=2))
    print(f"\n✅ 기록 완료: {DICT_PATH} (백업: {bak.name})")


if __name__ == "__main__":
    main()
