#!/usr/bin/env python3
"""표현 레이어 검색 CLI — 설계: docs/expression_layer_design.md

임의 레지스터의 텍스트(한국어/영어)로 개념을 찾아 전 레지스터 병렬 표현을 반환.
인바운드 별칭(dead-zone/차단 규칙) 적중 시 대체 안내를 먼저 표시.

사용:
  python3 scripts/expression_search.py --search "찰랑거리는 기타"   # FTS 교차 검색
  python3 scripts/expression_search.py --term "electric bass"       # 정본 용어 직조회
  python3 scripts/expression_search.py --alias suspenseful          # 별칭/dead-zone 조회
  python3 scripts/expression_search.py --category mood --limit 20   # 카테고리 열람
  python3 scripts/expression_search.py --export data/expressions/crosswalk_v0.json
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_expression_db import slugify  # 정본 키 규칙 단일 기재(G-K4)

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "sunolang.db"

REGISTER_ORDER = ["suno_native", "music_theory_en", "plain_ko", "plain_en", "llm_prompt", "tags"]


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def concept_bundle(conn, concept_id):
    c = conn.execute("SELECT * FROM expr_concepts WHERE concept_id=?", (concept_id,)).fetchone()
    if not c:
        return None
    exprs = {r["register"]: {"text": r["text"], "confidence": r["confidence"], "method": r["method"]}
             for r in conn.execute(
                 "SELECT register, text, confidence, method FROM expr_expressions WHERE concept_id=?",
                 (concept_id,))}
    aliases = [dict(r) for r in conn.execute(
        "SELECT alias_text, alias_lang, kind, replacement_note FROM expr_inbound_aliases"
        " WHERE target_concept_id=?", (concept_id,))]
    return {
        "concept_id": c["concept_id"], "category": c["category"], "suno_term": c["suno_term"],
        "attested_count": c["attested_count"], "origin": c["origin"],
        "registers": {k: exprs[k] for k in REGISTER_ORDER if k in exprs},
        "inbound_aliases": aliases,
    }


def print_bundle(b, verbose=True):
    print(f"\n■ {b['suno_term']}  [{b['category']}]  attested≈{b['attested_count']}"
          f"{'' if b['origin'] == 'dictionary' else ' (origin:' + b['origin'] + ')'}")
    for reg in REGISTER_ORDER:
        e = b["registers"].get(reg)
        if not e:
            continue
        conf = "" if e["confidence"] == "high" else f"  ({e['confidence']})"
        print(f"  {reg:16s} {e['text']}{conf}")
    if verbose and b["inbound_aliases"]:
        ins = ", ".join(f"{a['alias_text']}[{a['kind']}]" for a in b["inbound_aliases"])
        print(f"  {'← inbound':16s} {ins}")


# 한국어 조사 제거 휴리스틱 (교착어 토큰 불일치 완화 — '승리의'→'승리')
KO_JOSA = ["으로", "에서", "부터", "까지", "처럼", "보다", "과", "와", "의", "을", "를",
           "이", "가", "은", "는", "에", "로", "도", "만"]


def ko_strip_josa(tok):
    for j in sorted(KO_JOSA, key=len, reverse=True):
        if tok.endswith(j) and len(tok) - len(j) >= 1:
            return tok[: -len(j)]
    return tok


def check_aliases(conn, query):
    toks = {query} | {t for t in query.split() if t} | {ko_strip_josa(t) for t in query.split() if t}
    marks = ",".join("?" * len(toks))
    rows = conn.execute(
        f"SELECT * FROM expr_inbound_aliases WHERE alias_text COLLATE NOCASE IN ({marks})",
        sorted(toks)).fetchall()
    for r in rows:
        tag = {"dead_zone": "⚠ DEAD-ZONE", "blocked": "⛔ 차단 규칙", "ko_glossary": "↔ 글로서리"}[r["kind"]]
        print(f"{tag}: '{r['alias_text']}' — {r['replacement_note'] or ''} (근거: {r['source']})")
        if r["target_concept_id"]:
            b = concept_bundle(conn, r["target_concept_id"])
            if b:
                print_bundle(b, verbose=False)
    return bool(rows)


def _fts_toks(q):
    return [t.replace('"', '') for t in q.split() if t.strip()]


def fts_ladder(q):
    """완화 사다리: ①전 토큰 AND ②OR ③조사제거+prefix OR. (mode, match_expr) 순서 반환."""
    toks = _fts_toks(q)
    if not toks:
        return
    yield ("AND", " ".join(f'"{t}"' for t in toks))
    if len(toks) > 1:
        yield ("OR", " OR ".join(f'"{t}"' for t in toks))
    stripped = [ko_strip_josa(t) for t in toks]
    if stripped != toks:
        yield ("조사제거 OR", " OR ".join(f'"{t}" OR "{t}"*' for t in stripped))


def cmd_search(query, limit):
    conn = connect()
    hit = check_aliases(conn, query)
    rows, mode = [], None
    for mode, expr in fts_ladder(query):
        rows = conn.execute(
            "SELECT DISTINCT concept_id, register FROM expr_fts WHERE expr_fts MATCH ?"
            " AND concept_id != '' ORDER BY rank LIMIT ?", (expr, limit)).fetchall()
        if rows:
            break
    if not rows and not hit:
        print(f"매칭 없음: '{query}'")
        return
    if rows and mode != "AND":
        print(f"(완화 매칭: {mode} — 전체 구 일치는 없음)")
    seen = set()
    for r in rows:
        if r["concept_id"] in seen:
            continue
        seen.add(r["concept_id"])
        b = concept_bundle(conn, r["concept_id"])
        if b:
            print_bundle(b)
            print(f"  {'(적중 레지스터)':16s} {r['register']}")


def cmd_term(term):
    conn = connect()
    row = conn.execute(
        "SELECT concept_id FROM expr_concepts WHERE suno_term = ? COLLATE NOCASE", (term,)).fetchone()
    if not row:
        # 정본 키는 concept_id의 슬러그다(build_expression_db.slugify가 원자 중복을 여기서 접는다).
        # 표기 변종(하이픈/공백/대소문자)으로 들어온 조회를 같은 개념으로 붙인다 — 코퍼스에 둘 다 실재.
        # LIKE 금지 — 슬러그의 `_`가 LIKE 단일문자 와일드카드라 오탐이 난다. 접미 정확비교로 자른다.
        row = conn.execute(
            "SELECT concept_id FROM expr_concepts"
            " WHERE substr(concept_id, instr(concept_id, ':') + 1) = ?", (slugify(term),)).fetchone()
    if not row:
        print(f"개념 없음: '{term}' — --search 로 유사 검색을 시도하세요")
        if check_aliases(conn, term):
            return
        return
    print_bundle(concept_bundle(conn, row["concept_id"]))


def cmd_category(cat, limit):
    conn = connect()
    rows = conn.execute(
        "SELECT concept_id FROM expr_concepts WHERE category=? ORDER BY attested_count DESC LIMIT ?",
        (cat, limit)).fetchall()
    if not rows:
        cats = [r[0] for r in conn.execute("SELECT DISTINCT category FROM expr_concepts")]
        print(f"카테고리 없음: {cat} / 보유: {sorted(cats)}")
        return
    for r in rows:
        print_bundle(concept_bundle(conn, r["concept_id"]), verbose=False)


def cmd_export(path):
    conn = connect()
    out = {"_provenance": "표현 레이어 v0 crosswalk export — 정본: sunolang.db expr_* "
                          "(빌드: scripts/build_expression_db.py)",
           # ★`attestation`을 반드시 같이 내보낸다 — 이게 빠지면 소비 측에서 `llm_prompt`(엔진
           #   이름이 붙은 레지스터)를 실측치로 읽는다. 한정자는 표 밖이 아니라 행 안에.
           "registers": {r["register"]: {"audience": r["audience"],
                                         "attestation": r["attestation"],
                                         "description": r["description"]}
                         for r in conn.execute("SELECT * FROM expr_registers")},
           "concepts": [], "inbound_aliases": []}
    for r in conn.execute("SELECT concept_id FROM expr_concepts ORDER BY category, attested_count DESC"):
        b = concept_bundle(conn, r["concept_id"])
        b["registers"] = {k: v["text"] for k, v in b["registers"].items()}
        out["concepts"].append(b)
    out["inbound_aliases"] = [dict(r) for r in conn.execute("SELECT * FROM expr_inbound_aliases")]
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"export: {p} (개념 {len(out['concepts'])} / 별칭 {len(out['inbound_aliases'])})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--search", metavar="TEXT")
    ap.add_argument("--term", metavar="SUNO_TERM")
    ap.add_argument("--alias", metavar="TEXT")
    ap.add_argument("--category", metavar="CAT")
    ap.add_argument("--export", metavar="PATH")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
    if args.search:
        cmd_search(args.search, args.limit)
    elif args.term:
        cmd_term(args.term)
    elif args.alias:
        if not check_aliases(connect(), args.alias):
            print("별칭 없음")
    elif args.category:
        cmd_category(args.category, args.limit)
    elif args.export:
        cmd_export(args.export)
    else:
        ap.print_help()
