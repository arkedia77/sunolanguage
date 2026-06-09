#!/usr/bin/env python3
"""업로드 후보를 '코퍼스 갭 키워드 밀도'로 재선별.

mine_novel_songs.py는 novel_unique(전반적 신규성)로 랭킹한다. 본 스크립트는
그 후보(upload_queue.json)를 **문서화된 갭 영역**(coverage_map / supplement_plan /
external_source_leads)에 맞춰 재가중한다. 각 후보의 novel_words 중 갭 영역
키워드에 적중하는 수를 세어, 갭을 직접 메우는 곡을 상위로 끌어올린다.

사용:
    python3 scripts/rank_gap_candidates.py            # upload_queue.json → upload_queue_gap.json
    python3 scripts/rank_gap_candidates.py --top 60

산출:
    data/reanalysis_v2/upload_queue_gap.json  — 갭가중 재정렬 큐 + 적중 갭 라벨

주의: 입력 upload_queue.json은 DB 마이닝 상위 100건. 전체 760 풀 재선별이 필요하면
mine_novel_songs.py를 DB 접속하에 먼저 갱신 후 본 스크립트 재실행.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_IN = ROOT / "data" / "reanalysis_v2" / "upload_queue.json"
QUEUE_OUT = ROOT / "data" / "reanalysis_v2" / "upload_queue_gap.json"

# 갭 영역별 키워드 (novel_words 토큰과 부분일치). 문서 근거:
#   coverage_map §5 (Orchestral/Cinematic 2곡, Jazz 9곡 thin)
#   genre_supplement_plan Tier-1/2
#   corpus_unmined / external_source_leads (악기·이펙트 갭)
GAP_KEYWORDS = {
    "orchestral_cinematic": [
        "orchestral", "cinematic", "strings", "string", "brass", "timpani", "choir",
        "pizzicato", "arco", "bow", "rosin", "cathedral", "hymn", "hymn-like", "sacred",
        "gospel", "organ", "leslie", "harp", "oboe", "clarinet", "cello", "viola",
        "violin", "contrabass", "woodwind", "french-horn", "legato", "swell", "swells",
        "sweeping", "stately", "dignified", "reverence", "choral",
    ],
    "jazz": [
        "swing", "swung", "brushes", "brushed", "ride", "walking", "comping", "bebop",
        "modal", "rubato", "upright", "double-bass", "muted-trumpet", "saxophone",
        "sax", "trumpet", "cross-stick", "rimshot", "voicing", "voicings",
    ],
    "non_western_instrument": [
        "gayageum", "haegeum", "geomungo", "janggu", "daegeum", "buk", "pansori",
        "erhu", "pipa", "guzheng", "dizi", "koto", "shamisen", "shakuhachi",
        "sitar", "tabla", "tanpura", "oud", "bouzouki", "balalaika", "accordion",
        "bandoneon", "berimbau", "kalimba", "theremin", "hurdy", "mellotron",
    ],
    "effects": [
        "riser", "sweep", "whoosh", "impact", "vinyl", "vinyl-crackle", "crackle",
        "tape", "hiss", "bitcrush", "bitcrushed", "granular", "detuned", "pitch-shifted",
        "reverse", "reversed", "dropout", "sp-404", "sp404", "sampler", "chopped",
        "chops", "sidechain", "glitch", "stutter", "stutters", "lo-fi", "textural",
        "field", "sfx", "fono",
    ],
    "tier1_genre": [
        "amapiano", "drum-and-bass", "dnb", "flamenco", "math-rock", "chillout",
        "post-rock", "darkwave", "synthwave", "afrobeat", "dubstep", "tech-house",
        "alt-rock", "new-wave", "trap", "phonk", "drill", "phrygian", "dorian",
    ],
}


def score(novel_words: list[str]) -> tuple[int, dict]:
    toks = {w.lower() for w in novel_words}
    hits: dict[str, list[str]] = {}
    for area, kws in GAP_KEYWORDS.items():
        matched = sorted({w for w in toks for kw in kws if kw in w})
        if matched:
            hits[area] = matched
    total = sum(len(v) for v in hits.values())
    return total, hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=100)
    args = ap.parse_args()

    data = json.loads(QUEUE_IN.read_text())
    items = data["items"]

    ranked = []
    for it in items:
        gap_score, hits = score(it.get("novel_words", []))
        ranked.append({
            "gid": it["gid"], "batch": it["batch"], "title": it["title"],
            "sp_len": it["sp_len"], "novel_unique": it["novel_unique"],
            "gap_score": gap_score,
            "gap_areas": sorted(hits.keys()),
            "gap_hits": hits,
        })

    # 갭 적중(>0) 우선, 그 안에서 gap_score desc, tie-break novel_unique desc
    ranked.sort(key=lambda r: (r["gap_score"] > 0, r["gap_score"], r["novel_unique"]), reverse=True)
    out = ranked[: args.top]

    # 갭 영역 커버리지 요약
    area_cover: dict[str, int] = {a: 0 for a in GAP_KEYWORDS}
    for r in out:
        for a in r["gap_areas"]:
            area_cover[a] += 1

    result = {
        "generated_at": "2026-06-09",
        "source": "upload_queue.json (DB mining top 100)",
        "method": "novel_words × GAP_KEYWORDS 적중수 재가중",
        "gap_hit_candidates": sum(1 for r in ranked if r["gap_score"] > 0),
        "area_coverage": area_cover,
        "items": out,
    }
    QUEUE_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"입력 {len(items)} → 갭적중 {result['gap_hit_candidates']}건")
    print("갭 영역별 커버(상위 {}건):".format(len(out)))
    for a, n in sorted(area_cover.items(), key=lambda x: -x[1]):
        print(f"  {n:3}  {a}")
    print(f"\n상위 12 (gap_score · areas · title):")
    for r in out[:12]:
        print(f"  {r['gap_score']:2}  [{','.join(r['gap_areas'])}]  {r['title']}")
    print(f"\n→ {QUEUE_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
