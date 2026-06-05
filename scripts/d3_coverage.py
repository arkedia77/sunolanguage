#!/usr/bin/env python3
"""D3: v1 vs v2(v1+Suno 신규) 어휘 커버리지 before/after — leomusic SP 대상.

데이터 소스: legion PostgreSQL (read-only). 구머신(mushin@172.30.1.77)
sqlite3 leomusic.db 직읽기에서 전환 — LEO 결정 'legion PG 직접읽기로 전환'.
"""
import configparser
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V1 = json.loads((ROOT / "rag/suno_dictionary.json").read_text())
NEW = json.loads((ROOT / "data/reanalysis_v2/d2_new_candidates.json").read_text())
OUT = ROOT / "data/reanalysis_v2/d3_coverage.json"
DB_CONF = Path.home() / ".config" / "leofamily_music" / "db.conf"
# 구 leomusic.db 는 leomusic 프로젝트 곡만 보유 → 통합 songs 테이블에서 동일 범위로 스코프.
CREATOR_SCOPE = "leomusic"


def fetch_leomusic_sps():
    """legion PG에서 leomusic-origin 곡의 SP 조회 (read-only). 구 sqlite 쿼리와 동일 컬럼."""
    import psycopg2
    c = configparser.ConfigParser()
    c.read(DB_CONF)
    cfg = dict(c["postgresql"])
    conn = psycopg2.connect(host=cfg["host"], port=int(cfg["port"]),
                            dbname=cfg["dbname"], user=cfg["user"], password=cfg["password"])
    cur = conn.cursor()
    cur.execute(
        "SELECT global_id, batch, genre, style_prompt FROM songs "
        "WHERE creator = %s AND style_prompt IS NOT NULL AND length(style_prompt) > 30;",
        (CREATOR_SCOPE,),
    )
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

CATS = ["instrument_phrases","technique_patterns","production_vocab",
        "mood_emotion","vocal_expressions","timbre_texture",
        "harmony_vocab","tempo_rhythm","dynamics_structure"]

v1_terms = set()
for c in CATS:
    v1_terms.update(k.lower() for k in V1.get(c, {}).keys())

# 신규: Suno 재분석 빈도 3+ 만 채택 (노이즈 컷)
new_terms = {k.lower() for k, v in NEW.items() if v >= 3 and len(k) >= 3}
v2_terms = v1_terms | new_terms

print(f"[D3] v1 terms: {len(v1_terms)}, new(freq>=3): {len(new_terms)}, v2 total: {len(v2_terms)}")

# leomusic 전곡 style_prompt 샘플링 (phase별 분포 확인 위해 Phase 태그 대신 batch prefix 기준)
rows = fetch_leomusic_sps()
print(f"[D3] leomusic SPs: {len(rows)}")

def phase_of(batch):
    if not batch: return "unknown"
    b = batch.upper()
    if b.startswith("P3") or b.startswith("PHASE3"): return "P3"
    if b.startswith("P2") or b.startswith("PHASE2"): return "P2"
    if b.startswith("P1") or b.startswith("PHASE1"): return "P1"
    if b.startswith("K"): return "K"
    if b.startswith("B"): return "B"
    return "other"

def coverage(text, terms):
    t = text.lower()
    return sum(1 for term in terms if term in t)

stats = defaultdict(lambda: {"songs": 0, "v1_hits": 0, "v2_hits": 0,
                             "v1_nonzero": 0, "v2_nonzero": 0})
for r in rows:
    sp = r["style_prompt"] or ""
    ph = phase_of(r.get("batch", ""))
    v1h = coverage(sp, v1_terms)
    v2h = coverage(sp, v2_terms)
    for bucket in (ph, "ALL"):
        s = stats[bucket]
        s["songs"] += 1
        s["v1_hits"] += v1h
        s["v2_hits"] += v2h
        s["v1_nonzero"] += 1 if v1h > 0 else 0
        s["v2_nonzero"] += 1 if v2h > 0 else 0

out = {}
for bucket, s in stats.items():
    n = max(s["songs"], 1)
    out[bucket] = {
        "songs": s["songs"],
        "v1_avg_hits": round(s["v1_hits"]/n, 2),
        "v2_avg_hits": round(s["v2_hits"]/n, 2),
        "delta_avg": round((s["v2_hits"] - s["v1_hits"])/n, 2),
        "v1_coverage_pct": round(s["v1_nonzero"]/n*100, 1),
        "v2_coverage_pct": round(s["v2_nonzero"]/n*100, 1),
    }
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(f"[D3] 결과:")
for k in sorted(out.keys()):
    v = out[k]
    print(f"  {k:6} n={v['songs']:5}  v1_avg={v['v1_avg_hits']:6.2f}  v2_avg={v['v2_avg_hits']:6.2f}  Δ={v['delta_avg']:+6.2f}  cov {v['v1_coverage_pct']:5.1f}%→{v['v2_coverage_pct']:5.1f}%")
print(f"[D3] out: {OUT}")
