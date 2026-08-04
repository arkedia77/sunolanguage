#!/usr/bin/env python3
"""B(실드리프트) 263건의 3차 원인 검정 — '곡별 오청' vs '서술 어휘 수축'.

split이 분리한 B=263건을 그냥 '드리프트'라 부르면 또 과대 진술이다.
B에는 최소 두 원인이 더 섞여 있다.

  (B1) 곡별 오청  — Suno가 곡마다 제각각 다른 장르로 들었다 → 관측 분포가 요청만큼 넓다
  (B2) 어휘 수축  — Suno가 어느 곡이든 좁은 어휘대(K-Pop/ballad)로 수렴한다
                    → 관측 분포가 요청보다 뚜렷이 좁다. 이건 곡의 문제가 아니라 서술기의 문제.

판별: 같은 441곡에 대해 요청/관측 각각의
  · 고유 라벨 수 · 그룹 엔트로피 · 최빈 그룹 점유율 · 상위3 그룹 누적점유율
을 나란히 잰다. 관측이 유의하게 좁으면 B2.

부가: 한국어 가사 앵커 가설 — 관측 라벨 K-접두율이 요청 라벨 K-접두율보다 크게 높은가.

산출: data/exchange/genre_collapse_result.json
"""
import json
import re
import math
import sqlite3
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
ENCORE = ROOT / "data" / "exchange" / "encore_20260803" / "genre_design_normalize_v0.json"
OUT = ROOT / "data" / "exchange" / "genre_collapse_result.json"

K_PREFIX = re.compile(r"\bK[-\s]?(?:Pop|Indie|Rock|Hip|Ballad|R&B|Trot|Folk|Rap)\b", re.I)


def entropy(counter):
    tot = sum(counter.values())
    if not tot:
        return 0.0
    return -sum((v / tot) * math.log2(v / tot) for v in counter.values() if v)


def main():
    meta = json.loads(ENCORE.read_text())
    rules = [(r["group"], re.compile(r["pattern"], re.I)) for r in meta["rules"]]

    def first(label):
        if not label or not label.strip():
            return "_no_label"
        for g, p in rules:
            if p.search(label):
                return g
        return "unmapped"

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT song_id, entity, genre FROM entries "
                "WHERE slot='genre' AND source='sp_entity' AND entity IS NOT NULL")
    obs, req = {}, {}
    for sid, ent, g in cur.fetchall():
        obs.setdefault(sid, ent.strip())
        if g and g.strip():
            req[sid] = g.strip()
    ids = [s for s in obs if s in req]

    def profile(getter, name):
        labels = [getter(s) for s in ids]
        groups = collections.Counter(first(l) for l in labels)
        tot = sum(groups.values())
        top = groups.most_common()
        return {
            "layer": name,
            "n": len(labels),
            "distinct_labels": len(set(l.lower() for l in labels)),
            "distinct_groups": len(groups),
            "group_entropy_bits": round(entropy(groups), 3),
            "top_group": top[0][0],
            "top_group_share_pct": round(100.0 * top[0][1] / tot, 1),
            "top3_cumulative_pct": round(100.0 * sum(v for _, v in top[:3]) / tot, 1),
            "k_prefix_pct": round(100.0 * sum(1 for l in labels if K_PREFIX.search(l)) / len(labels), 1),
            "group_mix": dict(top),
        }

    p_req = profile(lambda s: req[s], "requested(design_intent)")
    p_obs = profile(lambda s: obs[s], "observed(suno reanalysis)")

    # B 집합만 따로 — 실드리프트로 분류된 곡들의 관측 분포
    def allhits(l):
        return {g for g, p in rules if p.search(l)}
    b_ids = [s for s in ids if first(req[s]) != first(obs[s]) and first(req[s]) not in allhits(obs[s])]
    b_obs_groups = collections.Counter(first(obs[s]) for s in b_ids)
    b_tot = sum(b_obs_groups.values())

    verdict_ratio = round(p_req["group_entropy_bits"] / p_obs["group_entropy_bits"], 2) \
        if p_obs["group_entropy_bits"] else None

    res = {
        "as_of": "2026-08-04",
        "owner": "sunolanguage",
        "purpose": "B(실드리프트 263건)를 '곡별 오청(B1)'과 '서술 어휘 수축(B2)'으로 분리",
        "n_pairs": len(ids),
        "requested_profile": p_req,
        "observed_profile": p_obs,
        "entropy_ratio_req_over_obs": verdict_ratio,
        "B_subset": {
            "n": len(b_ids),
            "observed_group_mix": dict(b_obs_groups.most_common()),
            "observed_top_share_pct": round(100.0 * b_obs_groups.most_common()[0][1] / b_tot, 1)
            if b_tot else None,
            "note": "B가 곡별 오청(B1)이면 이 분포는 넓어야 한다. 좁으면 수축(B2).",
        },
        "verdict_rule": "관측 엔트로피 < 요청 엔트로피이고 관측 최빈점유율이 크게 높으면 B2(수축) 우세",
        "caveats": [
            "표본=sunolang 코퍼스 441곡(K-계열 편중). encore 5,754 모집단에 외삽 금지.",
            "그룹 정의는 encore v0 규칙을 그대로 씀 — ballad 우선순위 편향이 양 층에 동일 적용되므로 "
            "층간 비교(요청 vs 관측)는 유효하나, 그룹 절대치는 규칙에 종속.",
            "요청/관측 모두 텍스트 라벨. 오디오 실측 아님 — 음향 검증은 encore probe_v2 소관.",
        ],
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))

    print(f"{'':<26}{'요청(design_intent)':>22}{'관측(Suno 재분석)':>22}")
    for k in ["distinct_labels", "distinct_groups", "group_entropy_bits",
              "top_group_share_pct", "top3_cumulative_pct", "k_prefix_pct"]:
        print(f"{k:<26}{str(p_req[k]):>22}{str(p_obs[k]):>22}")
    print(f"{'top_group':<26}{p_req['top_group']:>22}{p_obs['top_group']:>22}")
    print()
    print(f"엔트로피 비(요청/관측) = {verdict_ratio}")
    print(f"B집합 {len(b_ids)}건의 관측 분포 최빈점유율 = {res['B_subset']['observed_top_share_pct']}% "
          f"({b_obs_groups.most_common()[0][0]})")
    print(f"→ {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
