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
    python3 scripts/reference_matcher.py calibrate                                # tracks 전량 스코어 분포 → τ 제안+파일럿10
    python3 scripts/reference_matcher.py recheck-gaps                             # 인제스트 후 open gap 재매칭·해소

채널:
    M1 벡터   Qdrant sunolang_presets (all-MiniLM-L6-v2, 서빙과 동일 모델) — 의미 유사
    M2 렉시컬 lexical_index.sqlite entries_fts (FTS5 bm25) — 표현 실존
    M3 사전   suno_dictionary_v3 (악기/무드/주법 카운트 근거) — 검증 어휘
    음수필터  suno_does_not_use — 코드명/진행표기/다이나믹마킹 감지 시 SP 사용금지 경고
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


FTS_TOKEN = re.compile(r"[A-Za-z0-9]+")


def fts_query(fragment: str) -> str:
    """FTS5 질의: 안전 토큰만 인용해 OR 결합 (unicode61 토크나이저 대응)."""
    toks = [t.lower() for t in FTS_TOKEN.findall(fragment) if len(t) >= 3]
    return " OR ".join(f'"{t}"' for t in dict.fromkeys(toks))  # 순서 보존 dedup


# ─────────────────────────── 채널 ───────────────────────────

_m1_cache: dict = {}


def m1_vector_search(frags: list[str], top: int) -> list[list[dict]]:
    import embed_pipeline
    if "model" not in _m1_cache:
        _m1_cache["model"] = embed_pipeline.get_embedding_model()
        _m1_cache["client"] = embed_pipeline.get_qdrant_client()
    model, client = _m1_cache["model"], _m1_cache["client"]
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


DICT_V3 = ROOT / "rag" / "suno_dictionary_v3.json"
_dict_cache: dict | None = None


def load_dict() -> dict:
    global _dict_cache
    if _dict_cache is None:
        _dict_cache = json.loads(DICT_V3.read_text())
    return _dict_cache


def m3_dict_search(frags: list[str], top: int) -> list[list[dict]]:
    """사전 v3 직조회 — 프래그먼트 내 등장하는 검증 어휘를 코퍼스 출현수 순으로."""
    d = load_dict()
    vocab: list[tuple[str, str, int]] = []  # (term, slot, count)
    for term, info in d.get("instrument_phrases", {}).items():
        vocab.append((term, "instrument", int(info.get("count", 0))))
    for term, info in d.get("mood_emotion", {}).items():
        vocab.append((term, "mood", int(info.get("count", 0))))
    for term, info in d.get("technique_patterns", {}).items():
        vocab.append((term, "technique", int(info.get("count", 0))))
    results = []
    for f in frags:
        low = " " + " ".join(FTS_TOKEN.findall(f.lower())) + " "
        hits = [
            {"expr": term, "slot": slot, "song_id": "dict_v3", "score": float(count)}
            for term, slot, count in vocab
            if len(term) >= 3 and f" {term.strip()} " in low
        ]
        results.append(sorted(hits, key=lambda x: -x["score"])[:top])
    return results


# suno_does_not_use 음수필터 — Suno가 0회 사용하는 표기 (rag/suno_dictionary_v3.json 근거)
NEGATIVE_PATTERNS = [
    (re.compile(r"\b[A-G](?:#|b)?(?:maj|min|dim|aug|sus)\d?\b|\b[A-G](?:#|b)?m?7\b"),
     "구체적 코드명(Am, Dm7, Cmaj7…) — Suno 0회. 'key of X'만 유효"),
    (re.compile(r"\b(?:[IViv]+)\s*[-–]\s*(?:[IViv]+)\s*[-–]\s*(?:[IViv]+)\b"),
     "코드 진행 표기(II-V-I…) — Suno 0회"),
    (re.compile(r"(?<![A-Za-z])(?:pp|mp|mf|ff|fff|ppp)(?![A-Za-z])"),
     "다이나믹 마킹(p/mf/ff…) — Suno 0회"),
    (re.compile(r"\bmaster(?:ing|ed)\b", re.I),
     "mastering 계열 — 전체 코퍼스 2건, SP 예산 낭비"),
]


def negative_scan(text: str) -> list[str]:
    warns = []
    for pat, msg in NEGATIVE_PATTERNS:
        m = pat.search(text)
        if m:
            warns.append(f"`{m.group(0)}` → {msg}")
    return warns


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
        (item_id, corpus_version(conn), json.dumps({"m1": 1.0, "m2": 1.0, "m3": 1.0})))
    run_id = cur.lastrowid
    conn.commit()

    m1 = m1_vector_search(frags, args.top)
    m2 = m2_lexical_search(frags, args.top)
    m3 = m3_dict_search(frags, args.top)
    neg_warns = negative_scan(text)

    song_rrf: dict[str, float] = {}
    frag_reports = []
    gaps = []
    for i, frag in enumerate(frags):
        fused = rrf_fuse([m1[i], m2[i], m3[i]])
        best_vec = m1[i][0]["score"] if m1[i] else 0.0
        is_gap = best_vec < GAP_VECTOR_TAU and len(m2[i]) < GAP_LEX_MIN_HITS and not m3[i]
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
            if item["song_id"] != "dict_v3":  # 사전 채널은 곡 집계에서 제외
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
             f"- 코퍼스 버전: {corpus_version(conn)} · 채널: M1벡터+M2렉시컬+M3사전 RRF(k={RRF_K})",
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
    lines += ["", "## (e) 음수필터 경고 (suno_does_not_use — SP에 넣지 말 것)", ""]
    lines += [f"- ⚠️ {w}" for w in neg_warns] if neg_warns else ["- 없음"]
    report_path.write_text("\n".join(lines))
    conn.execute("UPDATE match_runs SET report_path=? WHERE id=?", (str(report_path), run_id))
    conn.commit()

    print(f"\n=== run {run_id} 완료 → {report_path} ===")
    for sid, score in top_songs:
        t, g = titles.get(sid, ("?", "?"))
        print(f"  근접곡 {sid} 「{t}」 [{g}] rrf={score:.4f}")
    print(f"  치환표 {sum(0 if f['is_gap'] else 1 for f in frag_reports)}행 / gap {len(gaps)}건")


def is_gap_frag(m1_hits, m2_hits, m3_hits) -> tuple[bool, float]:
    best_vec = m1_hits[0]["score"] if m1_hits else 0.0
    return (best_vec < GAP_VECTOR_TAU and len(m2_hits) < GAP_LEX_MIN_HITS
            and not m3_hits), best_vec


def cmd_calibrate(args) -> None:
    """tracks(reklcli) 전량 매칭 스코어 분포 → τ 제안 + 파일럿 10건 선정 (gap 미등록)."""
    conn = db()
    rows = conn.execute(
        "SELECT id, title, artist, genre, texture_description FROM tracks "
        "WHERE texture_description IS NOT NULL AND texture_description != '' ORDER BY id").fetchall()
    print(f"[calibrate] 대상 {len(rows)}곡 (gap 미등록 모드)")
    track_stats = []
    all_scores: list[float] = []
    for row in rows:
        frags = fragments(row["texture_description"])
        if not frags:
            continue
        m1 = m1_vector_search(frags, 5)
        m2 = m2_lexical_search(frags, 5)
        m3 = m3_dict_search(frags, 5)
        scores = [is_gap_frag(m1[i], m2[i], m3[i])[1] for i in range(len(frags))]
        lex_cov = sum(1 for h in m2 if h) / len(frags)
        all_scores += scores
        track_stats.append({
            "id": row["id"], "title": row["title"], "artist": row["artist"],
            "genre": row["genre"], "n_frags": len(frags),
            "mean_vec": sum(scores) / len(scores), "min_vec": min(scores),
            "lex_cov": lex_cov,
        })
        print(f"  #{row['id']:3d} {row['title'][:28]:30s} frags={len(frags):2d} "
              f"mean={track_stats[-1]['mean_vec']:.3f} min={min(scores):.3f}")

    all_scores.sort()
    def pct(p): return all_scores[int(len(all_scores) * p)] if all_scores else 0.0
    taus = [0.35, 0.40, 0.45, 0.50, 0.55]
    gap_rates = [(t, sum(1 for s in all_scores if s < t) / len(all_scores)) for t in taus]

    # 파일럿 10: 스코어 층화 4(최저2+최고2) + 장르 다양성 6
    by_mean = sorted(track_stats, key=lambda x: x["mean_vec"])
    pilot = by_mean[:2] + by_mean[-2:]
    seen_genres = {t["genre"] for t in pilot}
    for t in by_mean[len(by_mean) // 4: -2]:
        if len(pilot) >= 10:
            break
        if t["genre"] not in seen_genres:
            pilot.append(t)
            seen_genres.add(t["genre"])

    REPORT_DIR.mkdir(exist_ok=True)
    out = REPORT_DIR / "tau_calibration_report.md"
    lines = [f"# τ 캘리브레이션 데이터셋 — reklcli {len(track_stats)}곡 ({now()})", "",
             f"- 프래그먼트 총 {len(all_scores)}개 · M1 best-vector 분포: "
             f"p10={pct(.10):.3f} p25={pct(.25):.3f} p50={pct(.50):.3f} p75={pct(.75):.3f}", "",
             "## τ 후보별 gap율 (vector 단독 기준)", "",
             "| τ | gap율 |", "|---|---:|"]
    lines += [f"| {t:.2f} | {r:.1%} |" for t, r in gap_rates]
    lines += ["", f"현행 잠정 τ={GAP_VECTOR_TAU} (M2·M3 무적중 동시조건이라 실제 gap율은 위보다 낮음)", "",
              "## 파일럿 10건 (Leo 검토·청음 대상 — 층화: 최저2+최고2+장르다양 6)", "",
              "| track_id | 제목 | 아티스트 | 장르 | mean_vec | 판정 포인트 |", "|---|---|---|---|---:|---|"]
    for t in pilot[:10]:
        point = "저스코어(코퍼스 공백 의심)" if t["mean_vec"] < pct(.25) else (
            "고스코어(매칭 신뢰 확인용)" if t["mean_vec"] > pct(.75) else "중간대(경계 판정용)")
        lines.append(f"| {t['id']} | {t['title']} | {t['artist']} | {t['genre']} | "
                     f"{t['mean_vec']:.3f} | {point} |")
    lines += ["", "판정 방법: 각 곡 `match --track-id N` 리포트의 치환표를 Leo가 검토 — "
              "\"이 치환이 원곡 뉘앙스를 담는가\" Y/N → Y/N 경계의 vec 스코어로 τ 확정."]
    out.write_text("\n".join(lines))
    print(f"\n[calibrate] → {out}")
    for t, r in gap_rates:
        print(f"  τ={t:.2f} → gap율 {r:.1%}")


def cmd_recheck_gaps(args) -> None:
    """open gap을 현 코퍼스로 재매칭 — τ 통과 시 ingested 마킹 (러너 인제스트 후행)."""
    conn = db()
    rows = conn.execute("SELECT * FROM gap_candidates WHERE status='open'").fetchall()
    if not rows:
        print("[recheck-gaps] open gap 없음")
        return
    frags = [r["expr"] for r in rows]
    m1 = m1_vector_search(frags, 5)
    m2 = m2_lexical_search(frags, 5)
    m3 = m3_dict_search(frags, 5)
    resolved = 0
    for i, r in enumerate(rows):
        gap, best_vec = is_gap_frag(m1[i], m2[i], m3[i])
        if not gap:
            best = m1[i][0]["expr"] if m1[i] else (m2[i][0]["expr"] if m2[i] else m3[i][0]["expr"])
            conn.execute(
                "UPDATE gap_candidates SET status='ingested', resolution_note=?, updated_at=? WHERE id=?",
                (f"재매칭 해소 vec={best_vec:.3f} → {best[:80]}", now(), r["id"]))
            resolved += 1
            print(f"  ✅ #{r['id']} [{r['slot'] or '?'}] {r['expr'][:50]} → 해소 (vec {best_vec:.3f})")
    conn.commit()
    print(f"[recheck-gaps] {len(rows)}건 중 {resolved}건 해소, {len(rows) - resolved}건 유지")


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

    p = sub.add_parser("calibrate", help="tracks 전량 스코어 분포 → τ 제안 + 파일럿10 (gap 미등록)")
    p.set_defaults(func=cmd_calibrate)

    p = sub.add_parser("recheck-gaps", help="open gap 재매칭 — 해소 시 ingested 마킹")
    p.set_defaults(func=cmd_recheck_gaps)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
