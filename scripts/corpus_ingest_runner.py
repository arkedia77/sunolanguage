#!/usr/bin/env python3
"""corpus_ingest_runner.py — 전파정책 v3.2 Class A 원자 실행 오케스트레이터.

설계: docs/corpus_update_reference_matching_design.md §2 (P1)
정책: docs/corpus_propagation_policy.md — A0~A7 부분 전파 금지, 실패 시 전체 롤백.

사용법:
    python3 scripts/corpus_ingest_runner.py ingest REPLY_JSON --kind {A,C}
        [--with-lyrics]   # 원곡 가사 보유 배치: lyrics 청크+게이트+Qdrant까지
        [--db]            # A5 DB 적재 실행 (admin DDL 개통 후. 기본=db_pending)
        [--no-rollback]   # 실패 시 자동 롤백 생략 (디버깅용)
        [--force]         # 락/직전 FAIL 무시
    python3 scripts/corpus_ingest_runner.py status      # 카운터 + B1 임계 판정
    python3 scripts/corpus_ingest_runner.py rollback --run N --execute
    python3 scripts/corpus_ingest_runner.py init-db     # 상태 테이블 생성+카운터 시드

원자성 모델: 실패 시 자동 롤백 후 원인 수정 → 같은 커맨드 재실행이 재개 경로
(A3 Qdrant upsert는 chunk_id diff 기반 idempotent).

단계:
    A0   게이트: merge dry-run 검증 (스키마/별칭/중복/sanitizer)
    A0.5 스냅샷: 산출 파일 백업 + Qdrant chunk_id 기준선 기록
    A1   병합: merge_batch_reanalysis.py --execute
    A2   엔티티 재파싱: parse_slot_entities_v3.py
    A3   청크 재빌드 + Qdrant 증분: chunk_builder → qdrant_incremental_upsert
    A4   coverage_map 갱신: build_map_and_manuals.py
    A5   DB 증분 적재: json_to_db.py load (--db 시)
    A6   회귀: pytest tests/ -q
    A7   상태DB 카운터 갱신 + B1 임계 판정 출력
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V3 = ROOT / "data" / "reanalysis_v2"
MERGED = V3 / "merged_4values.json"
CHUNKS = ROOT / "data" / "chunks.json"
LYRICS_CHUNKS = ROOT / "data" / "lyrics_chunks.json"
STATE_DB = ROOT / "sunolang.db"
BACKUP_ROOT = ROOT / "data" / "backups"
LOCK = ROOT / "data" / ".ingest.lock"
PY = str(ROOT / ".venv" / "bin" / "python3") if (ROOT / ".venv" / "bin" / "python3").exists() else sys.executable
PYTEST = str(ROOT / ".venv" / "bin" / "pytest")

# A0.5 스냅샷 대상 (A1~A4가 변경하는 산출 파일 전부)
SNAPSHOT_TARGETS = [
    "data/reanalysis_v2/merged_4values.json",
    "data/reanalysis_v2/sp_entities_v3.json",
    "data/reanalysis_v2/bracket_entities_v3.json",
    "data/reanalysis_v2/instrument_details_v3.json",
    "data/reanalysis_v2/drum_details_v3.json",
    "data/reanalysis_v2/bracket_instrument_details_v3.json",
    "data/reanalysis_v2/bracket_drum_details_v3.json",
    "data/reanalysis_v2/vocal_details_v3.json",
    "data/chunks.json",
    "data/lyrics_chunks.json",
    "docs/coverage_map.md",
    "docs/manual_A_sp_sample.md",
    "docs/manual_B_lyrics_sample.md",
]

DDL = """
CREATE TABLE IF NOT EXISTS ingest_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_name TEXT NOT NULL,
  source_kind TEXT NOT NULL CHECK(source_kind IN ('reanalysis','external_upload','gap_queue')),
  songs_added INTEGER NOT NULL DEFAULT 0,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL DEFAULT 'running'
    CHECK(status IN ('running','done','rolled_back','failed','db_pending')),
  steps_done TEXT,
  backup_path TEXT,
  qdrant_new_chunk_ids TEXT,
  notes TEXT
);
CREATE TABLE IF NOT EXISTS pipeline_state (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
"""

# 카운터 시드 — 전파정책 문서 카운터 표(2026-06-12 v3.2 리셋) 기준
STATE_SEED = {
    "corpus_songs": "497",
    "dict_version": "v3.2",
    "last_rebuild_at": "2026-06-12",
    "rebuild_counter": "0",
    "qdrant_presets": "12818",
}

THIN_THRESHOLD = 5           # 표본 <5 = thin 장르
B1_SONGS = 30                # 누적 신규 ≥30곡
B1_THIN_ENTRIES = 5          # thin 장르 ≥5개가 임계 돌파
B1_DAYS = 90                 # 90일 + ≥10곡
B1_DAYS_MIN_SONGS = 10


def now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(DDL)
    for k, v in STATE_SEED.items():
        conn.execute(
            "INSERT OR IGNORE INTO pipeline_state(key, value, updated_at) VALUES (?,?,?)",
            (k, v, now()),
        )
    conn.commit()


def state_get(conn, key: str, default: str = "") -> str:
    row = conn.execute("SELECT value FROM pipeline_state WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def state_set(conn, key: str, value) -> None:
    conn.execute(
        "INSERT INTO pipeline_state(key, value, updated_at) VALUES (?,?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
        (key, str(value), now()),
    )
    conn.commit()


def run_cmd(label: str, cmd: list[str]) -> None:
    print(f"\n[{label}] $ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        raise RuntimeError(f"{label} 실패 (exit {proc.returncode})")


def normalize_genre(raw: str, canon: dict[str, str]) -> str:
    key = " ".join((raw or "").lower().replace("-", " ").replace("_", " ").split())
    return canon.get(key, key)


def load_canonical_map() -> dict[str, str]:
    try:
        data = json.loads((ROOT / "rag" / "genre_aliases.json").read_text())
        canon = {}
        for canonical, variants in data.get("canonical_map", {}).items():
            for v in variants:
                key = " ".join(v.lower().replace("-", " ").replace("_", " ").split())
                canon[key] = canonical.lower()
        return canon
    except Exception:
        return {}


def genre_counts(corpus: list[dict]) -> dict[str, int]:
    canon = load_canonical_map()
    counts: dict[str, int] = {}
    for rec in corpus:
        g = normalize_genre(rec.get("genre", ""), canon)
        if g:
            counts[g] = counts.get(g, 0) + 1
    return counts


def chunk_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {c["chunk_id"] for c in json.loads(path.read_text()) if "chunk_id" in c}


# ─────────────────────────── ingest ───────────────────────────

def mark_step(conn, run_id: int, step: str, steps: list[str]) -> None:
    steps.append(step)
    conn.execute("UPDATE ingest_runs SET steps_done=? WHERE id=?", (json.dumps(steps), run_id))
    conn.commit()
    print(f"[{step}] ✅")


def snapshot(backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    for rel in SNAPSHOT_TARGETS:
        src = ROOT / rel
        if src.exists():
            dst = backup_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def restore(backup_dir: Path) -> list[str]:
    restored = []
    for rel in SNAPSHOT_TARGETS:
        src = backup_dir / rel
        if src.exists():
            shutil.copy2(src, ROOT / rel)
            restored.append(rel)
    return restored


def qdrant_delete_chunks(new_ids: set[str]) -> int:
    """롤백: 이번 run에서 upsert된 chunk_id의 포인트를 presets 컬렉션에서 삭제."""
    if not new_ids:
        return 0
    sys.path.insert(0, str(ROOT / "scripts"))
    import embed_pipeline  # noqa: 지연 임포트 (qdrant_client 필요)

    client = embed_pipeline.get_qdrant_client()
    collection = embed_pipeline.COLLECTION_NAME
    point_ids, offset = [], None
    while True:
        points, offset = client.scroll(
            collection_name=collection, limit=1000, offset=offset,
            with_payload=["chunk_id"], with_vectors=False,
        )
        for p in points:
            if (p.payload or {}).get("chunk_id") in new_ids:
                point_ids.append(p.id)
        if offset is None:
            break
    if point_ids:
        client.delete(collection_name=collection, points_selector=point_ids)
    print(f"[rollback] Qdrant {collection}: {len(point_ids)}포인트 삭제")
    return len(point_ids)


def do_rollback(conn, run_id: int) -> None:
    row = conn.execute("SELECT * FROM ingest_runs WHERE id=?", (run_id,)).fetchone()
    if not row:
        raise SystemExit(f"run {run_id} 없음")
    backup = Path(row["backup_path"]) if row["backup_path"] else None
    if backup and backup.exists():
        restored = restore(backup)
        print(f"[rollback] 파일 {len(restored)}건 복원 ← {backup}")
    new_ids = set(json.loads(row["qdrant_new_chunk_ids"] or "[]"))
    steps = json.loads(row["steps_done"] or "[]")
    if "A3" in steps and new_ids:
        qdrant_delete_chunks(new_ids)
    if "A7" in steps:  # A7까지 갔으면 카운터도 원복
        state_set(conn, "corpus_songs", len(json.loads(MERGED.read_text())))
        state_set(conn, "rebuild_counter",
                  max(0, int(state_get(conn, "rebuild_counter", "0")) - row["songs_added"]))
        state_set(conn, "qdrant_presets",
                  max(0, int(state_get(conn, "qdrant_presets", "0")) - len(new_ids)))
        print("[rollback] pipeline_state 카운터 원복")
    conn.execute(
        "UPDATE ingest_runs SET status='rolled_back', finished_at=? WHERE id=?",
        (now(), run_id),
    )
    conn.commit()
    print(f"[rollback] run {run_id} → rolled_back")


def eval_b1(conn, thin_transitions: list[str]) -> list[str]:
    """B1 사전 재빌드 임계 판정. 충족 사유 목록 반환 (빈 목록 = 미도달)."""
    reasons = []
    counter = int(state_get(conn, "rebuild_counter", "0"))
    if counter >= B1_SONGS:
        reasons.append(f"누적 신규 {counter}곡 ≥ {B1_SONGS}")
    if len(thin_transitions) >= 1:
        reasons.append(f"thin 장르 임계 돌파: {', '.join(thin_transitions)}")
    last = state_get(conn, "last_rebuild_at", "2026-06-12")
    days = (datetime.now() - datetime.fromisoformat(last[:10])).days
    if days >= B1_DAYS and counter >= B1_DAYS_MIN_SONGS:
        reasons.append(f"경과 {days}일 ≥ {B1_DAYS} + 누적 {counter}곡 ≥ {B1_DAYS_MIN_SONGS}")
    return reasons


def print_b1(reasons: list[str]) -> None:
    if reasons:
        print("\n🔔 B1 사전 재빌드 임계 도달:")
        for r in reasons:
            print(f"   - {r}")
        print("   정식 경로(사람 개시): ① lexical_search_cli.py build → "
              "② dictionary_incremental_merge.py (dry-run) → ③ --apply --version X.Y → ④ pytest")
    else:
        print("\nB1 사전 재빌드: 미도달")


def cmd_ingest(args) -> None:
    reply = Path(args.reply)
    if not reply.exists():
        raise SystemExit(f"회신 파일 없음: {reply}")
    if LOCK.exists() and not args.force:
        raise SystemExit(f"락 존재({LOCK}) — 다른 인제스트 진행 중이거나 비정상 종료. --force로 해제")

    conn = db()
    ensure_tables(conn)
    prev_fail = conn.execute(
        "SELECT id FROM ingest_runs WHERE status='failed' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if prev_fail and not args.force:
        raise SystemExit(f"직전 run {prev_fail['id']}가 failed 상태(미롤백) — rollback 후 재시도 또는 --force")
    health = state_get(conn, "health_status", "")
    if health.startswith("FAIL") and not args.force:
        raise SystemExit(f"health_check FAIL 상태({health}) — corpus_health_check.py로 원인 해소 후 재시도 또는 --force")

    LOCK.write_text(now())
    cur = conn.execute(
        "INSERT INTO ingest_runs(batch_name, source_kind, started_at) VALUES (?,?,?)",
        (reply.stem, "external_upload" if args.kind == "A" else "reanalysis", now()),
    )
    conn.commit()
    run_id = cur.lastrowid
    steps: list[str] = []
    backup_dir = BACKUP_ROOT / f"run_{run_id}"
    print(f"=== ingest run {run_id}: {reply.name} (batch {args.kind}) ===")

    try:
        corpus_before = json.loads(MERGED.read_text())
        genres_before = genre_counts(corpus_before)
        chunks_before = chunk_ids(CHUNKS)

        # A0 게이트 (dry-run 검증)
        run_cmd("A0", [PY, "scripts/merge_batch_reanalysis.py", str(reply), "--batch", args.kind])
        mark_step(conn, run_id, "A0", steps)

        # A0.5 스냅샷
        snapshot(backup_dir)
        conn.execute("UPDATE ingest_runs SET backup_path=? WHERE id=?", (str(backup_dir), run_id))
        conn.commit()
        mark_step(conn, run_id, "A0.5", steps)

        # A1 병합
        run_cmd("A1", [PY, "scripts/merge_batch_reanalysis.py", str(reply), "--batch", args.kind, "--execute"])
        corpus_after = json.loads(MERGED.read_text())
        songs_added = len(corpus_after) - len(corpus_before)
        conn.execute("UPDATE ingest_runs SET songs_added=? WHERE id=?", (songs_added, run_id))
        conn.commit()
        if songs_added == 0:
            print("[A1] 신규 0곡 (전부 중복/거부) — 전파 불필요, run 종료")
            conn.execute("UPDATE ingest_runs SET status='done', finished_at=?, notes='신규 0곡' WHERE id=?",
                         (now(), run_id))
            conn.commit()
            return
        mark_step(conn, run_id, "A1", steps)

        # A2 엔티티 재파싱
        run_cmd("A2", [PY, "scripts/parse_slot_entities_v3.py"])
        mark_step(conn, run_id, "A2", steps)

        # A3 청크 재빌드 + Qdrant 증분
        run_cmd("A3-chunks", [PY, "scripts/chunk_builder.py", "build"])
        new_ids = chunk_ids(CHUNKS) - chunks_before
        conn.execute("UPDATE ingest_runs SET qdrant_new_chunk_ids=? WHERE id=?",
                     (json.dumps(sorted(new_ids)), run_id))
        conn.commit()
        run_cmd("A3-qdrant", [PY, "scripts/qdrant_incremental_upsert.py", "--target", "presets", "--execute"])
        if args.with_lyrics:
            run_cmd("A3-lyrics-chunks", [PY, "scripts/lyrics_chunk_builder.py", "build"])
            run_cmd("A3-lyrics-gate", [PY, "scripts/corpus_quality_gate.py", "validate", str(LYRICS_CHUNKS)])
            run_cmd("A3-lyrics-qdrant", [PY, "scripts/qdrant_incremental_upsert.py", "--target", "lyrics", "--execute"])
        mark_step(conn, run_id, "A3", steps)

        # A4 coverage_map
        run_cmd("A4", [PY, "scripts/build_map_and_manuals.py"])
        mark_step(conn, run_id, "A4", steps)

        # A5 DB 적재
        db_pending = not args.db
        if args.db:
            run_cmd("A5", [PY, "scripts/json_to_db.py", "load"])
            mark_step(conn, run_id, "A5", steps)
        else:
            print("[A5] ⏸ admin DDL 대기 — db_pending 표기 (개통 후 json_to_db.py load가 최신분 자동 반영)")

        # A6 회귀
        run_cmd("A6", [PYTEST, "tests/", "-q"])
        mark_step(conn, run_id, "A6", steps)

        # A7 카운터 + B1 판정
        state_set(conn, "corpus_songs", len(corpus_after))
        counter = int(state_get(conn, "rebuild_counter", "0")) + songs_added
        state_set(conn, "rebuild_counter", counter)
        state_set(conn, "qdrant_presets", int(state_get(conn, "qdrant_presets", "0")) + len(new_ids))
        state_set(conn, "last_ingest_at", now())
        genres_after = genre_counts(corpus_after)
        thin_transitions = sorted(
            g for g, n in genres_after.items()
            if n >= THIN_THRESHOLD and genres_before.get(g, 0) < THIN_THRESHOLD
        )
        status = "db_pending" if db_pending else "done"
        conn.execute(
            "UPDATE ingest_runs SET status=?, finished_at=?, notes=? WHERE id=?",
            (status, now(),
             json.dumps({"thin_transitions": thin_transitions, "new_chunks": len(new_ids)},
                        ensure_ascii=False),
             run_id),
        )
        conn.commit()
        mark_step(conn, run_id, "A7", steps)

        # A7.5 gap 자동 해소 (매칭 시스템 gap_candidates 재확인 — 실패해도 인제스트는 성립)
        try:
            has_gaps = conn.execute(
                "SELECT count(*) FROM gap_candidates WHERE status='open'").fetchone()[0]
            if has_gaps:
                run_cmd("A7.5", [PY, "scripts/reference_matcher.py", "recheck-gaps"])
        except Exception as exc:  # noqa: BLE001 — 후행 단계, 비치명
            print(f"[A7.5] ⚠️ gap 재확인 생략: {exc}")

        print(f"\n=== run {run_id} {status.upper()} ===")
        print(f"코퍼스 {len(corpus_before)}→{len(corpus_after)}곡 (+{songs_added}) / 신규 청크 {len(new_ids)}")
        print(f"재빌드 카운터 {counter}/{B1_SONGS}")
        if thin_transitions:
            print(f"thin 장르 진입: {', '.join(thin_transitions)}")
        print_b1(eval_b1(conn, thin_transitions))

    except Exception as exc:
        print(f"\n❌ 실패: {exc}", file=sys.stderr)
        conn.execute("UPDATE ingest_runs SET status='failed', finished_at=?, notes=? WHERE id=?",
                     (now(), str(exc), run_id))
        conn.commit()
        if not args.no_rollback and "A0.5" in steps:
            do_rollback(conn, run_id)
        elif not steps or "A0.5" not in steps:
            conn.execute("UPDATE ingest_runs SET status='rolled_back' WHERE id=?", (run_id,))
            conn.commit()  # 파일 무변경 단계 실패 = 복원 불요
        sys.exit(1)
    finally:
        LOCK.unlink(missing_ok=True)


# ─────────────────────────── status ───────────────────────────

def cmd_status(_args) -> None:
    conn = db()
    ensure_tables(conn)
    print("=== pipeline_state ===")
    for row in conn.execute("SELECT key, value, updated_at FROM pipeline_state ORDER BY key"):
        print(f"  {row['key']:20s} = {row['value']:12s} ({row['updated_at'][:10]})")
    merged_n = len(json.loads(MERGED.read_text()))
    state_n = state_get(conn, "corpus_songs")
    mark = "✅" if str(merged_n) == state_n else "⚠️ 불일치"
    print(f"\n실측 merged_4values: {merged_n}곡 vs 상태DB {state_n}곡 {mark}")
    print("\n=== 최근 runs ===")
    for row in conn.execute("SELECT * FROM ingest_runs ORDER BY id DESC LIMIT 5"):
        print(f"  #{row['id']} {row['batch_name']} [{row['status']}] +{row['songs_added']}곡 {row['started_at'][:16]}")
    print_b1(eval_b1(conn, []))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ingest", help="Class A 원자 인제스트")
    p.add_argument("reply", help="sunomusic 회신 JSON")
    p.add_argument("--kind", required=True, choices=["A", "C"], help="merge --batch 종별")
    p.add_argument("--with-lyrics", action="store_true")
    p.add_argument("--db", action="store_true", help="A5 DB 적재 실행")
    p.add_argument("--no-rollback", action="store_true")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("status", help="카운터 + B1 판정")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("rollback", help="run 스냅샷 복원 + Qdrant 신규분 삭제")
    p.add_argument("--run", type=int, required=True)
    p.add_argument("--execute", action="store_true")
    def _rb(a):
        conn = db()
        ensure_tables(conn)
        if not a.execute:
            row = conn.execute("SELECT * FROM ingest_runs WHERE id=?", (a.run,)).fetchone()
            if not row:
                raise SystemExit(f"run {a.run} 없음")
            print(f"[dry-run] run {a.run} [{row['status']}] backup={row['backup_path']} "
                  f"새청크={len(json.loads(row['qdrant_new_chunk_ids'] or '[]'))} — --execute로 실행")
            return
        do_rollback(conn, a.run)
    p.set_defaults(func=_rb)

    p = sub.add_parser("init-db", help="상태 테이블 생성 + 카운터 시드")
    def _init(a):
        conn = db()
        ensure_tables(conn)
        print(f"OK — ingest_runs/pipeline_state @ {STATE_DB}")
    p.set_defaults(func=_init)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
