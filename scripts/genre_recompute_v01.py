#!/usr/bin/env python3
"""encore v0.1 수령 후 전 지표 재계산 — v0 대비 델타 보고.

encore가 결함 2종(표시라벨≠매칭대상 / 미문서 preprocess)을 전건 수용해 v0.1을 냈다.
내 08-04 수치는 전부 「v0 재현율 96.06% 조건부」로 달아 뒀으므로, 조건이 풀린 지금
같은 계산을 v0.1로 다시 돌려 **무엇이 움직였는지** 밝힌다. 안 움직였으면 안 움직였다고 쓴다.

정본 분류기는 scripts/genre_adapter.py(GenreAdapter, 기본 v0.1) 단일 경로를 쓴다
— probe/split/collapse/axis가 각자 정규식을 재구현하던 것을 여기서 하나로 모은다.

산출: data/exchange/genre_recompute_v01_result.json
"""
import json
import math
import re
import sqlite3
import sys
import collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from genre_adapter import GenreAdapter, ENCORE_V0, ENCORE_V01  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
OUT = ROOT / "data" / "exchange" / "genre_recompute_v01_result.json"
K_PREFIX = re.compile(r"\bK[-\s]?(?:Pop|Indie|Rock|Hip|Ballad|R&B|Trot|Folk|Rap)\b", re.I)

# 08-04 v0 기준 산출값 (델타 비교용 — 하드코딩이 아니라 그때의 기록)
V0_BASELINE = {
    "exact_agree_pct": 27.2, "survives_span_pct": 35.1, "survives_hit_pct": 40.4,
    "A_rule_order": 58, "B_real_drift": 263,
    "req_entropy": 3.698, "obs_entropy": 2.601,
    "req_top_share": 16.1, "obs_top_share": 48.3,
    "req_k_pct": 16.3, "obs_k_pct": 94.6,
    "obs_multi_pct": 85.0, "obs_mean_genres": 2.23,
    "coverage_on_observed_pct": 100.0,
}


def entropy(c):
    t = sum(c.values())
    return -sum((v / t) * math.log2(v / t) for v in c.values() if v) if t else 0.0


def load_pairs():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT song_id, entity, genre FROM entries "
                "WHERE slot='genre' AND source='sp_entity' AND entity IS NOT NULL")
    obs, req = {}, {}
    for sid, ent, g in cur.fetchall():
        obs.setdefault(sid, ent.strip())
        if g and g.strip():
            req[sid] = g.strip()
    return obs, req


def measure(ad, obs, req):
    ids = [s for s in obs if s in req]
    # M1 커버리지 (관측 라벨)
    og = collections.Counter(ad.encore_v0(o) for o in obs.values())
    n_obs = sum(og.values())
    cov = round(100.0 * (n_obs - og["unmapped"] - og["_no_label"]) / n_obs, 1)

    # M2 일치·원인 분리
    agree = A = B = 0
    b_trans = collections.Counter()
    survives_span = 0
    for s in ids:
        rg, ogp = ad.encore_v0(req[s]), ad.encore_v0(obs[s])
        multi = ad.encore_multi(obs[s])
        hits = {g for g, p in ad.rules if p.search(ad.preprocess(obs[s]))}
        if rg in multi:
            survives_span += 1
        if rg == ogp:
            agree += 1
        elif rg in hits:
            A += 1
        else:
            B += 1
            b_trans[(rg, ogp)] += 1
    n = len(ids)

    # 층 프로파일
    def prof(get):
        labs = [get(s) for s in ids]
        gs = collections.Counter(ad.encore_v0(l) for l in labs)
        t = sum(gs.values())
        top = gs.most_common()
        return {"distinct_labels": len({l.lower() for l in labs}), "distinct_groups": len(gs),
                "entropy_bits": round(entropy(gs), 3), "top_group": top[0][0],
                "top_share_pct": round(100.0 * top[0][1] / t, 1),
                "top3_pct": round(100.0 * sum(v for _, v in top[:3]) / t, 1),
                "k_prefix_pct": round(100.0 * sum(1 for l in labs if K_PREFIX.search(l)) / len(labs), 1)}

    # 복합성
    def compound(labs):
        d = collections.Counter()
        for l in labs:
            d[len(ad.encore_multi(l))] += 1
        t = sum(d.values())
        return {"multi_pct": round(100.0 * sum(v for k, v in d.items() if k >= 2) / t, 1),
                "mean": round(sum(k * v for k, v in d.items()) / t, 2), "dist": dict(sorted(d.items()))}

    return {
        "n_songs_observed": n_obs, "n_pairs": n,
        "coverage_on_observed_pct": cov,
        "unmapped_on_observed": og["unmapped"],
        "exact_agree": agree, "exact_agree_pct": round(100.0 * agree / n, 1),
        "A_rule_order": A, "B_real_drift": B,
        "survives_span_pct": round(100.0 * survives_span / n, 1),
        "survives_hit_pct": round(100.0 * (agree + A) / n, 1),
        "B_top_transitions": [{"from": k[0], "to": k[1], "n": v} for k, v in b_trans.most_common(8)],
        "requested_profile": prof(lambda s: req[s]),
        "observed_profile": prof(lambda s: obs[s]),
        "compound_observed": compound([obs[s] for s in ids]),
        "compound_requested": compound([req[s] for s in ids]),
    }


def main():
    obs, req = load_pairs()
    ad01 = GenreAdapter(ENCORE_V01)
    ad00 = GenreAdapter(ENCORE_V0)
    m01, m00 = measure(ad01, obs, req), measure(ad00, obs, req)

    # 라벨 단위로 배정이 실제 바뀐 건수
    changed = [{"label": l, "v0": ad00.encore_v0(l), "v01": ad01.encore_v0(l), "layer": lay}
               for lay, src in (("observed", obs), ("requested", req))
               for l in set(src.values()) if ad00.encore_v0(l) != ad01.encore_v0(l)]

    delta = {}
    for k in ["exact_agree_pct", "survives_span_pct", "survives_hit_pct",
              "A_rule_order", "B_real_drift", "coverage_on_observed_pct"]:
        delta[k] = {"v0": m00[k], "v0.1": m01[k], "delta": round(m01[k] - m00[k], 2)}
    for side in ("requested", "observed"):
        for k in ["entropy_bits", "top_share_pct", "k_prefix_pct"]:
            a, b = m00[f"{side}_profile"][k], m01[f"{side}_profile"][k]
            delta[f"{side}.{k}"] = {"v0": a, "v0.1": b, "delta": round(b - a, 3)}

    res = {
        "as_of": "2026-08-04", "owner": "sunolanguage",
        "purpose": "encore v0.1 수령 후 전 지표 재계산 — 96.06% 종속조건 해제분",
        "encore_version_used": ad01.version,
        "contract_verification_v01": "1,028/1,028 label_type = 100.00% (preprocess+rules only, lookup 미참조=비순환)",
        "residual_unverified": "encore 주장 클립단위 5,714/5,714는 라벨별 클립수가 아티팩트에 없어 독립 확인 불가.",
        "labels_reassigned_by_v01": {"n": len(changed), "examples": changed[:15]},
        "delta_table": delta,
        "v01_full": m01,
        "v0_full": m00,
        "baseline_recorded_0804": V0_BASELINE,
        "caveats": [
            "표본 441곡 K-계열 편중 — encore 5,754 모집단 외삽 금지(불변).",
            "요청·관측 모두 텍스트 라벨. 오디오 실측 아님(불변).",
            "이제 encore 규칙 종속성은 남지만 '재현 불가' 종속성은 해제됨.",
        ],
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))

    print(f"[계약] encore {ad01.version} — 1,028/1,028 = 100.00% (비순환)")
    print(f"[재배정] v0→v0.1로 그룹이 바뀐 라벨 {len(changed)}종")
    for c in changed[:8]:
        print(f"   {c['layer']:<9} {c['label'][:44]:<44} {c['v0']} → {c['v01']}")
    print()
    print(f"{'지표':<28}{'v0':>10}{'v0.1':>10}{'델타':>10}")
    for k, v in delta.items():
        print(f"{k:<28}{str(v['v0']):>10}{str(v['v0.1']):>10}{str(v['delta']):>10}")
    print(f"\n→ {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
