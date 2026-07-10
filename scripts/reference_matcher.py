#!/usr/bin/env python3
"""reference_matcher.py — 외부 레퍼런스(곡/뉘앙스) → 코퍼스 매칭 (M1+M2+RRF).

설계: docs/corpus_update_reference_matching_design.md §3 (P3 MVP)
원칙: 매칭 결과는 코퍼스 실존 표현만 반환 (자유도=코퍼스 프리셋). 추정 어휘 생성 금지.

사용법:
    python3 scripts/reference_matcher.py match --text "misty riverside cello, restrained" [--top 20]
    python3 scripts/reference_matcher.py match --suno-sp data/incoming/ref.json   # Suno 앱 분석 SP
    python3 scripts/reference_matcher.py match --track-id 42                      # tracks(reklcli) 기존 분석
    python3 scripts/reference_matcher.py report --run 3                           # 리포트 재출력
    python3 scripts/reference_matcher.py gaps                                     # 열린 gap 목록

채널:
    M1 벡터   Qdrant sunolang_presets (all-MiniLM-L6-v2, 서빙과 동일 모델) — 의미 유사
    M2 렉시컬 lexical_index.sqlite entries_fts (FTS5 bm25) — 표현 실존
    융합      RRF(k=60), 프래그먼트별 → 곡 단위 집계

gap: 프래그먼트가 두 채널 모두에서 임계 미달이면 코퍼스 공백 → gap_candidates 등록.
τ(GAP_VECTOR_TAU)는 P4에서 goldset 방법론으로 캘리브레이션 예정(현값=보수적 잠정).
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

STATE_DB = ROOT / "sunolang.db"
LEXICAL_DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
MERGED = ROOT / "data" / "reanalysis_v2" / "merged_4values.json"
REPORT_DIR = ROOT / "docs" / "reviews"

RRF_K = 60
TOP_K = 20
GAP_VECTOR_TAU = 0.45   # 잠정 — P4 goldset 캘리브레이션 대상
GAP_LEX_MIN_HITS = 1

DDL = """
CREATE TABLE IF NOT EXISTS reference_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL CHECK(kind IN ('track','nuance_text','suno_analysis')),
  track_id INTEGER REFERENCES tracks(id),
  input_text TEXT,
  suno_uuid TEXT,
  requested_by TEXT DEFAULT 'leo',
  created_at TEXT DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS match_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reference_item_id INTEGER NOT NULL REFERENCES reference_items(id),
  corpus_version TEXT NOT NULL,
  channel_weights TEXT,
  status TEXT NOT NULL DEFAULT 'done' CHECK(status IN ('done','failed')),
  report_path TEXT,
  created_at TEXT DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS match_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL REFERENCES match_runs(id),
  slot TEXT NOT NULL,
  query_expr TEXT NOT NULL,
  matched_expr TEXT,
  corpus_song_id TEXT,
  channel TEXT NOT NULL CHECK(channel IN ('m1_vector','m2_lexical','m3_dict','fused')),
  score REAL NOT NULL,
  is_gap INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_mr_run ON match_results(run_id);
CREATE INDEX IF NOT EXISTS idx_mr_gap ON match_results(is_gap);
CREATE TABLE IF NOT EXISTS gap_candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  expr TEXT NOT NULL,
  slot TEXT,
  first_seen_run INTEGER REFERENCES match_runs(id),
  hit_count INTEGER DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'open'
    CHECK(status IN ('open','queued','recorded','ingested','wontfix')),
  resolution_note TEXT,
  updated_at TEXT DEFAULT (datetime('now','localtime'))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_gap_expr ON gap_candidates(expr, slot);
"""


def now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    conn.executescript(DDL)
    return conn


def corpus_version(conn) -> str:
    row = conn.execute("SELECT value FROM pipeline_state WHERE key='corpus_songs'").fetchone()
    songs = row["value"] if row else "?"
    row = conn.execute("SELECT value FROM pipeline_state WHERE key='dict_version'").fetchone()
    dictv = row["value"] if row else "?"
    return f"{songs}songs/{dictv}"


# ─────────────────────── 정규화 (프래그먼트 분해) ───────────────────────

def fragments(text: str) -> list[str]:
    """입력을 매칭 단위 프래그먼트로 분해 — 문장/쉼표절 단위, 3자 미만 제거."""
    parts = re.split(r"[.\n;]+", text)
    out = []
    for p in parts:
        for q in re.split(r",(?![^(]*\))", p):  # 괄호 안 쉼표는 유지
            q = q.strip(" -–—·")
            if len(q) >= 3:
                out.append(q)
    return out


FTS_TOKEN = re.compile(r"[A-Za-z0-9']+")


def fts_query(fragment: str) -> str:
    """FTS5 질의: 안전 토큰만 OR 결합 (unicode61 토크나이저 대응)."""
    toks = [t.lower() for t in FTS_TOKEN.findall(fragment) if len(t) >= 3]
    return " OR ".join(dict.fromkeys(toks))  # 순서 보존 dedup


# ─────────────────────────── 채널 ───────────────────────────

def m1_vector_search(frags: list[str], top: int) -> list[list[dict]]:
    import embed_pipeline
    model = embed_pipeline.get_embedding_model()
    client = embed_pipeline.get_qdrant_client()
    vectors = model.encode(frags, show_progress_bar=False)
    results = []
    for vec in vectors:
        hits = client.query_points(
            collection_name=embed_pipeline.COLLECTION_NAME,
            query=vec.tolist(), limit=top, with_payload=True).points
        results.append([
            {"expr": h.payload.get("text", ""), "slot": h.payload.get("slot", "?"),
             "song_id": str(h.payload.get("song_id", "?")), "score": float(h.score)}
            for h in hits
        ])
    return results


def m2_lexical_search(frags: list[str], top: int) -> list[list[dict]]:
    conn = sqlite3.connect(LEXICAL_DB)
    conn.row_factory = sqlite3.Row
    results = []
    for f in frags:
        q = fts_query(f)
        if not q:
            results.append([])
            continue
        rows = conn.execute(
            "SELECT e.sentence, e.slot, e.song_id, e.genre, bm25(entries_fts) AS rank "
            "FROM entries_fts JOIN entries e ON e.id = entries_fts.rowid "
            "WHERE entries_fts MATCH ? ORDER BY rank LIMIT ?", (q, top)).fetchall()
        results.append([
            {"expr": r["sentence"], "slot": r["slot"] or "?",
             "song_id": str(r["song_id"]), "score": -float(r["rank"])}  # bm25 낮을수록 좋음 → 부호 반전
            for r in rows
        ])
    return results


def rrf_fuse(per_channel: list[list[dict]]) -> list[dict]:
    """채널별 랭킹 리스트 → RRF 융합 (expr 단위)."""
    scores: dict[str, dict] = {}
    for ranked in per_channel:
        for rank, item in enumerate(ranked):
            key = item["expr"]
            ent = scores.setdefault(key, {**item, "rrf": 0.0})
            ent["rrf"] += 1.0 / (RRF_K + rank + 1)
    return sorted(scores.values(), key=lambda x: -x["rrf"])


# ─────────────────────────── 매칭 본체 ───────────────────────────

def load_input(args, conn) -> tuple[str, str, str | None, int | None]:
    """(kind, text, suno_uuid, track_id) 반환."""
    if args.text:
        return "nuance_text", args.text, None, None
    if args.suno_sp:
        raw = Path(args.suno_sp).read_text()
        try:
            data = json.loads(raw)
            text = data.get("sp") or data.get("suno_sp") or data.get("reanalysis_sp") or ""
            uuid = data.get("uuid") or data.get("suno_uuid")
            if not text:
                raise KeyError
            return "suno_analysis", text, uuid, None
        except (json.JSONDecodeError, KeyError):
            return "suno_analysis", raw.strip(), None, None
    if args.track_id:
        row = conn.execute("SELECT * FROM tracks WHERE id=?", (args.track_id,)).fetchone()
        if not row:
            raise SystemExit(f"tracks id {args.track_id} 없음")
        parts = [row["texture_description"] or "", row["overall_mood"] or ""]
        try:
            parts += json.loads(row["mood_keywords"] or "[]")
        except json.JSONDecodeError:
            pass
        for it in conn.execute(
                "SELECT instrument_name, technique, tone_character FROM instrument_textures "
                "WHERE track_id=?", (args.track_id,)):
            parts.append(" ".join(filter(None, it)))
        text = ". ".join(p for p in parts if p)
        print(f"[input] track #{args.track_id} 「{row['title']}」 — {row['artist']}")
        return "track", text, None, args.track_id
    raise SystemExit("--text / --suno-sp / --track-id 중 하나 필요")


def cmd_match(args) -> None:
    conn = db()
    kind, text, uuid, track_id = load_input(args, conn)
    frags = fragments(text)
    if not frags:
        raise SystemExit("매칭할 프래그먼트 없음")
    print(f"[match] kind={kind} / 프래그먼트 {len(frags)}개 / top={args.top}")

    cur = conn.execute(
        "INSERT INTO reference_items(kind, track_id, input_text, suno_uuid) VALUES (?,?,?,?)",
        (kind, track_id, text, uuid))
    item_id = cur.lastrowid
    cur = conn.execute(
        "INSERT INTO match_runs(reference_item_id, corpus_version, channel_weights) VALUES (?,?,?)",
        (item_id, corpus_version(conn), json.dumps({"m1": 1.0, "m2": 1.0})))
    run_id = cur.lastrowid
    conn.commit()

    m1 = m1_vector_search(frags, args.top)
    m2 = m2_lexical_search(frags, args.top)

    song_rrf: dict[str, float] = {}
    frag_reports = []
    gaps = []
    for i, frag in enumerate(frags):
        fused = rrf_fuse([m1[i], m2[i]])
        best_vec = m1[i][0]["score"] if m1[i] else 0.0
        is_gap = best_vec < GAP_VECTOR_TAU and len(m2[i]) < GAP_LEX_MIN_HITS
        top3 = fused[:3]
        for item in top3:
            conn.execute(
                "INSERT INTO match_results(run_id, slot, query_expr, matched_expr, "
                "corpus_song_id, channel, score, is_gap) VALUES (?,?,?,?,?,?,?,?)",
                (run_id, item["slot"], frag, item["expr"], item["song_id"],
                 "fused", item["rrf"], 0))
        if is_gap:
            slot = top3[0]["slot"] if top3 else None
            conn.execute(
                "INSERT INTO match_results(run_id, slot, query_expr, matched_expr, "
                "corpus_song_id, channel, score, is_gap) VALUES (?,?,?,?,?,?,?,?)",
                (run_id, slot or "?", frag, None, None, "fused", best_vec, 1))
            conn.execute(
                "INSERT INTO gap_candidates(expr, slot, first_seen_run) VALUES (?,?,?) "
                "ON CONFLICT(expr, slot) DO UPDATE SET hit_count=hit_count+1, updated_at=?",
                (frag.lower(), slot, run_id, now()))
            gaps.append((frag, best_vec))
        for item in fused[:10]:
            song_rrf[item["song_id"]] = song_rrf.get(item["song_id"], 0.0) + item["rrf"]
        frag_reports.append({"frag": frag, "top": top3, "is_gap": is_gap, "best_vec": best_vec})
    conn.commit()

    top_songs = sorted(song_rrf.items(), key=lambda x: -x[1])[:5]
    titles = {str(r["song_id"]): (r.get("title") or "?", r.get("genre") or "?")
              for r in json.loads(MERGED.read_text())}

    # 리포트
    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / f"match_run_{run_id}.md"
    lines = [f"# 매칭 리포트 — run {run_id} ({now()})", "",
             f"- 입력({kind}): {text[:300]}{'…' if len(text) > 300 else ''}",
             f"- 코퍼스 버전: {corpus_version(conn)} · 채널: M1벡터+M2렉시컬 RRF(k={RRF_K})",
             f"- τ(잠정): vector<{GAP_VECTOR_TAU} & lexical hit<{GAP_LEX_MIN_HITS} → gap", "",
             "## (a) 최근접 코퍼스 곡 top-5", "",
             "| song_id | 제목 | 장르 | RRF합 |", "|---|---|---|---:|"]
    for sid, score in top_songs:
        t, g = titles.get(sid, ("?", "?"))
        lines.append(f"| {sid} | {t} | {g} | {score:.4f} |")
    lines += ["", "## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)", "",
              "| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |", "|---|---|---|---|"]
    for fr in frag_reports:
        if fr["is_gap"]:
            continue
        for item in fr["top"][:1]:
            lines.append(f"| {fr['frag']} | {item['expr']} | {item['slot']} | {item['song_id']} |")
    lines += ["", "## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)", ""]
    by_slot: dict[str, list[str]] = {}
    for fr in frag_reports:
        for item in fr["top"]:
            by_slot.setdefault(item["slot"], []).append(item["expr"])
    for slot, exprs in sorted(by_slot.items()):
        uniq = list(dict.fromkeys(exprs))[:5]
        lines.append(f"- **{slot}**: " + " · ".join(uniq))
    lines += ["", "## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)", ""]
    if gaps:
        for frag, vec in gaps:
            lines.append(f"- `{frag}` (best vector {vec:.3f}) → gap_candidates 등록")
    else:
        lines.append("- 없음")
    report_path.write_text("\n".join(lines))
    conn.execute("UPDATE match_runs SET report_path=? WHERE id=?", (str(report_path), run_id))
    conn.commit()

    print(f"\n=== run {run_id} 완료 → {report_path} ===")
    for sid, score in top_songs:
        t, g = titles.get(sid, ("?", "?"))
        print(f"  근접곡 {sid} 「{t}」 [{g}] rrf={score:.4f}")
    print(f"  치환표 {sum(0 if f['is_gap'] else 1 for f in frag_reports)}행 / gap {len(gaps)}건")


def cmd_report(args) -> None:
    conn = db()
    row = conn.execute("SELECT report_path FROM match_runs WHERE id=?", (args.run,)).fetchone()
    if not row or not row["report_path"]:
        raise SystemExit(f"run {args.run} 리포트 없음")
    print(Path(row["report_path"]).read_text())


def cmd_gaps(_args) -> None:
    conn = db()
    rows = conn.execute(
        "SELECT * FROM gap_candidates WHERE status='open' ORDER BY hit_count DESC, id").fetchall()
    print(f"=== open gap {len(rows)}건 (hit_count 순 — 수집 배치 편성 후보) ===")
    for r in rows:
        print(f"  #{r['id']} [{r['slot'] or '?'}] {r['expr']} (hit {r['hit_count']}, run {r['first_seen_run']})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("match", help="레퍼런스 → 코퍼스 매칭")
    p.add_argument("--text", help="뉘앙스 텍스트")
    p.add_argument("--suno-sp", help="Suno 앱 분석 결과 JSON/텍스트 파일")
    p.add_argument("--track-id", type=int, help="tracks(reklcli) 기존 분석 id")
    p.add_argument("--top", type=int, default=TOP_K)
    p.set_defaults(func=cmd_match)

    p = sub.add_parser("report", help="리포트 재출력")
    p.add_argument("--run", type=int, required=True)
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("gaps", help="열린 gap 목록")
    p.set_defaults(func=cmd_gaps)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
