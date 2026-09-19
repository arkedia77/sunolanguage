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
    H6 표현 저작 커버 사전 원자 == 저작 레지스터(정본 파일) == expr_concepts(DB 파생)
    H7 커넥터 신선도 발행된 OUT 스냅샷 == 현행 코어(사전·개념) 스냅샷
    H8 정책표 대조   corpus_propagation_policy.md 표의 값 == 실측(미검사 칸도 센다)
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

    # H6 표현 레이어 저작 커버리지 (2026-09-13 신설)
    # ★왜 기계로 옮겼나: 이 칸은 08-15부터 「5줄 점검」의 손 항목(ⓒ)이었는데,
    #   09-02 v3.4 재빌드가 신규 원자 7건을 들여오고 저작을 안 한 상태가 11일 살아남았다.
    #   그동안 H1~H5는 PASS 6/6이었다 — ★기계가 안 보는 칸은 「정상」으로 보인다.
    #   사전이 앞서고 표현이 뒤처지면 커넥터 OUT은 「라벨만 새 버전」인 빈 통지가 된다(08-15 실물).
    # 레벨: WARN. 저작은 결재 대기일 수 있고 FAIL은 corpus_ingest_runner의 인제스트를
    #   막으므로(모듈 docstring), 인제스트와 무관한 미완으로 수집을 잠그지 않는다.
    try:
        import build_expression_db as BX  # 단일 진실원 재사용 (원자 추출·저작 로드)
        atoms, dict_ver = BX.extract_atoms()
        authored = BX.load_authored()
        missing = sorted(n for n in atoms if n not in authored)
        detail = f"사전 v{dict_ver} 원자 {len(atoms)} / 저작 {len(authored)} / 미저작 {len(missing)}"
        if missing:
            head = ", ".join(atoms[n]["suno_term"] for n in missing[:3])
            detail += f" — 미저작 예: {head}{' …' if len(missing) > 3 else ''}"
        check(results, "H6", not missing, detail, warn_only=True)
        # H6-db 정본 파일 ↔ DB 파생 동기 (08-15 별칭 6건이 DB 전용이라 재빌드로 소실된 병)
        expr_db = ROOT / "sunolang.db"
        if expr_db.exists():
            with sqlite3.connect(expr_db) as ec:
                has = ec.execute(
                    "SELECT count(*) FROM sqlite_master "
                    "WHERE type='table' AND name='expr_concepts'").fetchone()[0]
                if has:
                    db_n = ec.execute("SELECT count(*) FROM expr_concepts").fetchone()[0]
                    check(results, "H6-db", db_n == len(authored),
                          f"expr_concepts {db_n} / 저작 정본 {len(authored)}"
                          + ("" if db_n == len(authored) else " — build 미반영"),
                          warn_only=True)
                else:
                    check(results, "H6-db", True, "expr_concepts 테이블 없음 — 생략")
    except Exception as exc:  # 점검기가 죽어 「없음」으로 보이지 않게 경고로 남긴다
        check(results, "H6", False, f"표현 커버리지 조회 실패: {exc}", warn_only=True)


    # H7 커넥터 OUT 스냅샷 신선도 (2026-09-19 신설)
    # ★왜 기계로 옮겼나: 이 칸은 08-15부터 5줄 점검의 손 항목(ⓓ)이었다.
    #   실물 = 08-17 발행분 `cs-3.3-589-20260815`가 09-02 층 분리·09-14 저작(개념 446→453)
    #   뒤에도 그대로 남았는데, 그동안 H1~H6는 PASS 8/8을 찍었다 — 기계가 안 보는 칸은
    #   「정상」으로 보인다(H6 주석과 같은 병의 3회차). 발행 여부는 결재 칸이므로 WARN.
    pub_id = None  # H8이 이 값을 쓴다 — H7이 죽어도 「없음」이 「일치」로 안 보이게 선언
    try:
        import corpus_connector as CC  # 단일 진실원 재사용(스냅샷 산식·매니페스트 로더)
        with sqlite3.connect(CC.DB_PATH) as cc_conn:
            cur_snap = CC.corpus_snapshot(cc_conn)
            pub = (CC.load_manifest().get("corpus_snapshot") or {})
            pub_id = pub.get("snapshot_id") or "(미발행)"
            last_out = cc_conn.execute(
                "SELECT started_at FROM connector_runs WHERE port='out' AND status='ok' "
                "ORDER BY id DESC LIMIT 1").fetchone()
        same = pub_id == cur_snap["snapshot_id"]
        detail = f"발행 {pub_id} / 현행 {cur_snap['snapshot_id']}"
        if not same:
            gap = []
            for k, label in (("dict_version", "사전"), ("corpus_tracks", "트랙"),
                             ("expr_concepts", "개념")):
                if pub.get(k) != cur_snap[k]:
                    gap.append(f"{label} {pub.get(k, '?')}→{cur_snap[k]}")
            detail += " — 불일치(" + " · ".join(gap) + ")"
            if last_out and last_out[0]:
                days = (datetime.now() - datetime.fromisoformat(last_out[0])).days
                detail += f" · 마지막 OUT 발행 {last_out[0][:10]}({days}일 전)"
        check(results, "H7", same, detail, warn_only=True)
    except Exception as exc:
        check(results, "H7", False, f"커넥터 스냅샷 조회 실패: {exc}", warn_only=True)

    # H8 전파정책 표 ↔ 실측 대조 (2026-09-19 신설)
    # ★왜 기계로 옮겼나: 5줄 점검의 손 항목(ⓔ). 이 표는 「전파 수행 시마다 갱신」이라
    #   적어 놓고 06-12~08-15 두 달간 안 고쳤다(문서 497곡 / 실제 530곡 — 문서 자체가 자인).
    #   ⛔값을 JSON 사이드카로 빼지 않는다 — 같은 수가 두 곳이 되면 「자 두 벌」이다.
    #   ⇒ 표(정본)를 읽고 기계가 다시 재서 대조만 한다.
    # ★미검사 칸을 «세어서 찍는다» — 안 보는 칸이 「정상」으로 보이지 않게.
    try:
        import re
        policy = ROOT / "docs" / "corpus_propagation_policy.md"
        rows = {}
        for line in policy.read_text().splitlines():
            if line.startswith("|") and line.count("|") >= 3:
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if len(cells) >= 2:
                    rows[cells[0]] = cells[1]

        def num(pat, text):
            m = re.search(pat, text)
            return int(m.group(1).replace(",", "")) if m else None

        checked, bad = [], []

        def cmp_cell(label, declared, measured):
            if declared is None:
                bad.append(f"{label} 표기 파싱 실패")
            elif declared != measured:
                bad.append(f"{label} 표 {declared} ↔ 실측 {measured}")
            else:
                checked.append(label)

        r = rows.get("파일 코퍼스", "")
        cmp_cell("파일코퍼스곡", num(r"\*\*([\d,]+)곡", r), merged_n)

        r = rows.get("lexical_index", "")
        with sqlite3.connect(LEXICAL_DB) as lx:
            lx_e, lx_t, lx_g = lx.execute(
                "SELECT count(*), count(DISTINCT song_id), count(DISTINCT genre) "
                "FROM entries").fetchone()
        cmp_cell("lexical트랙", num(r"([\d,]+)트랙", r), lx_t)
        cmp_cell("lexical엔트리", num(r"([\d,]+) entries", r), lx_e)
        cmp_cell("lexical장르", num(r"([\d,]+)장르", r), lx_g)

        dict_j = json.loads((ROOT / "rag" / "suno_dictionary_v3.json").read_text())
        r = rows.get("사전 최신", "")
        mv = re.search(r"\*\*v([\d.]+)", r)
        cmp_cell("사전버전", mv.group(1) if mv else None, str(dict_j.get("version")))
        cmp_cell("사전기준트랙", num(r"([\d,]+)트랙", r),
                 int(dict_j.get("corpus", {}).get("tracks_count", -1)))

        r = rows.get("표현 레이어", "")
        with sqlite3.connect(ROOT / "sunolang.db") as ex:
            def cnt(t):
                return ex.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            cmp_cell("표현개념", num(r"\*\*([\d,]+)개념", r), cnt("expr_concepts"))
            cmp_cell("표현수", num(r"([\d,]+)표현", r), cnt("expr_expressions"))
            cmp_cell("인바운드별칭", num(r"별칭 ([\d,]+)", r), cnt("expr_inbound_aliases"))

        r = rows.get("커넥터 OUT", "")
        ms = re.search(r"snapshot `([^`]+)`", r)
        if pub_id is None:
            bad.append("커넥터스냅샷 실측 불가(H7 실패) — 대조 안 함")
        else:
            cmp_cell("커넥터스냅샷", ms.group(1) if ms else None, pub_id)

        # ⛔여기서 «안» 보는 칸을 이름으로 남긴다(측정에 망·외부 자원이 필요한 칸).
        uncovered = ["Qdrant presets(원격 100.90.35.121:6333)", "DB 테이블(A5 보류)",
                     "webapp 사전(B2 종속)"]
        detail = f"대조 {len(checked)}칸 일치 / 불일치 {len(bad)} · ⛔미검사 {len(uncovered)}칸: " \
                 + ", ".join(uncovered)
        if bad:
            detail = "⛔" + " · ".join(bad) + " || " + detail
        check(results, "H8", not bad, detail, warn_only=True)
    except Exception as exc:
        check(results, "H8", False, f"정책표 대조 실패: {exc}", warn_only=True)

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
