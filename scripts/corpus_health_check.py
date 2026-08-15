#!/usr/bin/env python3
"""corpus_health_check.py — 코퍼스 4레이어 동기 검증 (H1~H5).

설계: docs/corpus_update_reference_matching_design.md §2.3 (P2)
용도: 인제스트 후행 + 세션 시작 시 주기 실행. FAIL이면 corpus_ingest_runner가
다음 ingest를 거부한다(--force로만 해제) — pipeline_state.health_status 경유.

사용법:
    python3 scripts/corpus_health_check.py            # 전체 검사
    python3 scripts/corpus_health_check.py --no-net   # Qdrant 원격 조회 생략(H2 부분)

검사:
    H1 곡수 정합   merged_4values == 상태DB corpus_songs == 기준선+runs 합산
    H2 인덱스 정합 Qdrant live == 상태DB qdrant_presets == chunks.json / lexical entries
    H3 사전 신선도 rebuild_counter·경과일 → B1 임계 근접 경고
    H4 백업 존재   최근 run backup_path 실존
    H5 게이트 재검 lyrics_chunks 품질게이트 재통과
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus_ingest_runner import (  # noqa: E402 — 단일 진실원 재사용
    CHUNKS, LYRICS_CHUNKS, MERGED, PY, ROOT, STATE_DB,
    B1_SONGS, db, ensure_tables, eval_b1, state_get, state_set, now,
)

BASELINE_SONGS = 497  # 상태DB 시드 시점(v3.2, 2026-06-12 이후 07-10 시드) 기준선
LEXICAL_DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
# ★상수가 아니라 **상태DB의 실측 기록**을 기준선으로 쓴다 (2026-08-16).
#   구판은 `LEXICAL_SEED_ENTRIES = 17822`를 소스에 박아 두고 "v3.2 기준"이라 찍었다.
#   08-15 v3.3 재빌드로 19,084가 된 뒤에도 화면은 계속 "v3.2 기준 17822"였다 —
#   ★라벨이 거짓말을 한 것이고, 고치려면 사람이 소스를 편집해야 하니 필연적으로 늙는다.
#   ⇒ 기준선은 `record-rebuild`가 실측해 넣은 `lexical_entries`에서 읽는다.
LEXICAL_FALLBACK_ENTRIES = 17822  # 기록 이전(v3.2 시드) 폴백 — 기록이 있으면 안 쓴다


def check(results: list, name: str, ok: bool, detail: str, warn_only: bool = False):
    level = "PASS" if ok else ("WARN" if warn_only else "FAIL")
    results.append((level, name, detail))
    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[level]
    print(f"  {icon} [{name}] {detail}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--no-net", action="store_true", help="Qdrant 원격 조회 생략")
    args = ap.parse_args()

    conn = db()
    ensure_tables(conn)
    results: list[tuple[str, str, str]] = []
    print("=== corpus_health_check ===")

    # H1 곡수 정합
    merged_n = len(json.loads(MERGED.read_text()))
    state_n = int(state_get(conn, "corpus_songs", "0"))
    runs_sum = BASELINE_SONGS + sum(
        r["songs_added"] for r in conn.execute(
            "SELECT songs_added FROM ingest_runs WHERE status IN ('done','db_pending')")
    )
    check(results, "H1", merged_n == state_n == runs_sum,
          f"merged {merged_n} / 상태DB {state_n} / 기준선+runs {runs_sum}")

    # H2 인덱스 정합
    chunks_n = len(json.loads(CHUNKS.read_text()))
    state_q = int(state_get(conn, "qdrant_presets", "0"))
    if args.no_net:
        check(results, "H2", chunks_n == state_q,
              f"chunks.json {chunks_n} / 상태DB {state_q} (Qdrant 원격 생략)", warn_only=True)
    else:
        try:
            import embed_pipeline
            live = embed_pipeline.get_qdrant_client().get_collection(
                embed_pipeline.COLLECTION_NAME).points_count
            check(results, "H2", live == state_q == chunks_n,
                  f"Qdrant live {live} / 상태DB {state_q} / chunks.json {chunks_n}")
        except Exception as exc:
            check(results, "H2", False, f"Qdrant 조회 실패: {exc}", warn_only=True)
    if LEXICAL_DB.exists():
        lex_n = sqlite3.connect(LEXICAL_DB).execute("SELECT count(*) FROM entries").fetchone()[0]
        recorded = state_get(conn, "lexical_entries", "")
        base = int(recorded) if recorded else LEXICAL_FALLBACK_ENTRIES
        ver = state_get(conn, "dict_version", "?")
        src = f"{ver} 기록" if recorded else f"v3.2 시드·★record-rebuild 미기록"
        check(results, "H2-lex", lex_n == base,
              f"lexical entries {lex_n} ({src} {base}; B1 재빌드 시에만 변동)",
              warn_only=True)

    # H3 사전 신선도
    counter = int(state_get(conn, "rebuild_counter", "0"))
    last = state_get(conn, "last_rebuild_at", "2026-06-12")
    days = (datetime.now() - datetime.fromisoformat(last[:10])).days
    b1 = eval_b1(conn, [])
    near = counter >= B1_SONGS * 0.8 or days >= 80
    detail = f"카운터 {counter}/{B1_SONGS}, 재빌드 후 {days}일"
    if b1:
        check(results, "H3", False, f"{detail} — B1 도달: {'; '.join(b1)}", warn_only=True)
    elif near:
        check(results, "H3", False, f"{detail} — B1 근접", warn_only=True)
    else:
        check(results, "H3", True, detail)

    # H4 백업 존재
    row = conn.execute(
        "SELECT id, backup_path FROM ingest_runs WHERE backup_path IS NOT NULL "
        "ORDER BY id DESC LIMIT 1").fetchone()
    if row:
        ok = Path(row["backup_path"]).exists()
        check(results, "H4", ok, f"run {row['id']} 백업 {row['backup_path']}", warn_only=not ok)
    else:
        check(results, "H4", True, "백업 보유 run 없음 (인제스트 이력 없음)")

    # H5 게이트 재검 (lyrics 코퍼스 보유 시)
    if LYRICS_CHUNKS.exists():
        proc = subprocess.run(
            [PY, "scripts/corpus_quality_gate.py", "validate", str(LYRICS_CHUNKS)],
            cwd=ROOT, capture_output=True, text=True)
        tail = (proc.stdout or proc.stderr).strip().splitlines()
        check(results, "H5", proc.returncode == 0,
              tail[-1] if tail else f"exit {proc.returncode}")
    else:
        check(results, "H5", True, "lyrics_chunks.json 없음 — 생략")

    # 종합
    fails = [r for r in results if r[0] == "FAIL"]
    warns = [r for r in results if r[0] == "WARN"]
    status = "FAIL" if fails else "PASS"
    state_set(conn, "health_status", f"{status}@{now()}")
    print(f"\n종합: {status} (FAIL {len(fails)} / WARN {len(warns)} / "
          f"PASS {len(results) - len(fails) - len(warns)})")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
