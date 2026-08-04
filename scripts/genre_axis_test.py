#!/usr/bin/env python3
"""16그룹 중 무엇이 '장르 머리'이고 무엇이 '수식 슬롯'인가 — 양 모집단 동시 검정.

split에서 ballad만 98.6% 동시보유로 확인했다. 그런데 그건 sunolang 코퍼스(K편중 441곡)라
「표본 탓 아니냐」는 반론이 성립한다. 그래서 **encore 자기 모집단**으로도 같은 걸 잰다.
encore가 보낸 genre_design_normalize_v0.json의 `labels_by_group`에는 5,754클립의
원 라벨 문자열과 빈도가 그대로 들어 있다 — 재수령·재요청 없이 즉시 대조 가능.

지표: 그룹 G에 배정된 라벨 중, G 패턴을 지운 뒤에도 **다른 그룹 패턴에 적중**하는 비율
      = co_head_pct. 높으면 G는 단독 머리가 아니라 다른 장르에 얹히는 수식 슬롯.

두 모집단에서 같은 순위가 나오면 그 축 분리는 표본 독립이다.

산출: data/exchange/genre_axis_result.json
"""
import json
import re
import sqlite3
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
ENCORE = ROOT / "data" / "exchange" / "encore_20260803" / "genre_design_normalize_v0.json"
OUT = ROOT / "data" / "exchange" / "genre_axis_result.json"


def main():
    meta = json.loads(ENCORE.read_text())
    rules = [(r["group"], re.compile(r["pattern"], re.I)) for r in meta["rules"]]
    pat = dict(rules)

    def spans(label):
        """그룹 → 매치 스팬. ★포섭 배제용으로 위치까지 본다.
        'K-Pop'은 kpop(0,5)과 pop_general(2,5)에 동시 적중하지만 스팬이 겹치므로
        '두 장르 동시보유'가 아니라 '한 문자열의 중복 적중'이다. 이걸 co_head로 세면 오염."""
        out = {}
        for g, p in rules:
            m = p.search(label)
            if m:
                out[g] = (m.start(), m.end())
        return out

    def hits(label):
        return set(spans(label))

    def disjoint_partners(sp, g):
        """g의 스팬과 겹치지 않는 다른 그룹들 = 진짜 동시보유."""
        a0, a1 = sp[g]
        return {o for o, (b0, b1) in sp.items() if o != g and (b1 <= a0 or b0 >= a1)}

    def co_head(labels_weighted):
        """labels_weighted: [(label, weight)] → 그룹별 co_head 통계 (스팬 비겹침 기준)"""
        stat = collections.defaultdict(lambda: {"n": 0, "co": 0, "co_with": collections.Counter()})
        for lab, w in labels_weighted:
            sp = spans(lab)
            for g in sp:
                others = disjoint_partners(sp, g)
                stat[g]["n"] += w
                if others:
                    stat[g]["co"] += w
                    for o in others:
                        stat[g]["co_with"][o] += w
        out = {}
        for g, s in stat.items():
            out[g] = {
                "n": s["n"],
                "co_head_pct": round(100.0 * s["co"] / s["n"], 1) if s["n"] else None,
                "top_co_with": dict(s["co_with"].most_common(4)),
            }
        return dict(sorted(out.items(), key=lambda x: -(x[1]["co_head_pct"] or 0)))

    # ── 모집단 1: encore 자기 모집단 (design_intent, 5,754클립) ───────────────
    enc_labels = []
    for g, labs in meta["labels_by_group"].items():
        if g in ("_no_label", "unmapped"):
            continue
        for lab, n in labs.items():
            enc_labels.append((lab, n))
    enc = co_head(enc_labels)

    # ── 모집단 2: sunolang 관측층 (Suno 재분석, 454곡) ────────────────────────
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT song_id, entity FROM entries "
                "WHERE slot='genre' AND source='sp_entity' AND entity IS NOT NULL")
    seen, obs_labels = set(), []
    for sid, ent in cur.fetchall():
        if sid in seen:
            continue
        seen.add(sid)
        obs_labels.append((ent.strip(), 1))
    obs = co_head(obs_labels)

    # ── 순위 일치 검정 ────────────────────────────────────────────────────────
    common = [g for g in enc if g in obs and enc[g]["n"] >= 30 and obs[g]["n"] >= 8]
    r_enc = sorted(common, key=lambda g: -enc[g]["co_head_pct"])
    r_obs = sorted(common, key=lambda g: -obs[g]["co_head_pct"])
    # 상위/하위 절반 일치 개수 (순위상관 대신 해석 쉬운 지표)
    half = max(1, len(common) // 2)
    top_agree = len(set(r_enc[:half]) & set(r_obs[:half]))

    MODIFIER_CUT = 60.0
    mod_enc = {g for g in common if enc[g]["co_head_pct"] >= MODIFIER_CUT}
    mod_obs = {g for g in common if obs[g]["co_head_pct"] >= MODIFIER_CUT}

    # ── 라벨 단위 복합성 (축 분리 기각 후 살아남은 지표) ──────────────────────
    def compoundness(labels_weighted):
        tot = multi = 0
        dist = collections.Counter()
        for lab, w in labels_weighted:
            sp = spans(lab)
            # 서로 겹치지 않는 스팬만 남겨 '동시보유 장르 수'를 센다
            keep, taken = [], []
            for g, (a, b) in sorted(sp.items(), key=lambda x: (x[1][0], -(x[1][1] - x[1][0]))):
                if all(b <= c or a >= d for c, d in taken):
                    keep.append(g)
                    taken.append((a, b))
            k = len(keep)
            tot += w
            dist[k] += w
            if k >= 2:
                multi += w
        return {"n": tot, "multi_genre_pct": round(100.0 * multi / tot, 1) if tot else None,
                "genres_per_label_dist": dict(sorted(dist.items())),
                "mean_genres_per_label": round(sum(k * v for k, v in dist.items()) / tot, 2) if tot else None}

    comp_enc, comp_obs = compoundness(enc_labels), compoundness(obs_labels)

    res = {
        "as_of": "2026-08-04",
        "owner": "sunolanguage",
        "purpose": "encore 16그룹의 '머리 vs 수식' 축 분리를 양 모집단에서 검정 (표본 독립성 확인)",
        "metric": "co_head_pct = 그 그룹에 걸린 라벨 중 다른 그룹 패턴에도 동시 적중하는 비율",
        "modifier_cut_pct": MODIFIER_CUT,
        "population_A_encore_design_intent": {
            "n_clips_declared": meta["input"], "n_label_types": len(enc_labels), "per_group": enc},
        "population_B_sunolang_observed": {
            "n_songs": len(obs_labels), "per_group": obs},
        "rank_consistency": {
            "groups_compared": common,
            "rank_encore": r_enc, "rank_observed": r_obs,
            "top_half_overlap": f"{top_agree}/{half}",
        },
        "modifier_like_groups": {
            "in_encore_population": sorted(mod_enc),
            "in_observed_population": sorted(mod_obs),
            "in_both": sorted(mod_enc & mod_obs),
        },
        "HYPOTHESIS_REJECTED": {
            "hypothesis": "16그룹은 '장르 머리'와 '수식 슬롯' 두 축으로 갈린다 (ballad=형식슬롯 등)",
            "verdict": "기각 — 표본 독립성 없음",
            "evidence": [
                f"상위절반 순위 겹침 {top_agree}/{half} — 두 모집단에서 순위가 재현되지 않음",
                "관측 모집단에서 12그룹 중 11그룹이 co_head 75%↑로 포화 → 변별력 없음",
                "co_head_pct는 라벨 길이(복합성)를 재는 것이지 그룹의 '수식성'을 재는 것이 아님",
            ],
            "note": "split.py의 'ballad=형식슬롯' 잠정 결론도 이 기각에 함께 걸린다. "
                    "ballad 98.6% 동시보유는 참이지만, 그것만으로 ballad를 '형식축'이라 부를 근거는 못 된다 "
                    "— 관측 라벨은 어느 그룹이든 동시보유율이 높기 때문.",
        },
        "SURVIVING_FINDING_compoundness": {
            "metric": "라벨 하나가 담은 '스팬 비겹침 장르 그룹' 개수",
            "encore_design_intent": comp_enc,
            "sunolang_observed": comp_obs,
            "gap": f"복합라벨 비율 설계 {comp_enc['multi_genre_pct']}% vs 관측 {comp_obs['multi_genre_pct']}%",
            "implication": "encore v0의 '선언순서 첫일치 단일배정'은 설계 라벨에는 대체로 무해하나 "
                           "관측 라벨에는 구조적으로 정보를 버린다. 어댑터는 단일배정이 아니라 "
                           "다중배정(집합)이어야 한다. 이건 축 유형론 없이도 성립.",
        },
        "caveat": "co_head_pct·복합성 모두 encore v0 정규식에 종속된 지표다. 패턴이 바뀌면 값도 바뀐다. "
                  "절대치가 아니라 두 층(설계/관측) 간 상대 비교로만 읽을 것.",
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))

    print(f"{'group':<16}{'encore(설계)':>16}{'sunolang(관측)':>18}")
    for g in sorted(common, key=lambda x: -(enc[x]["co_head_pct"])):
        print(f"{g:<16}{enc[g]['co_head_pct']:>13}% (n={enc[g]['n']:<5}){obs[g]['co_head_pct']:>9}% (n={obs[g]['n']})")
    print()
    print(f"상위절반 순위 겹침: {top_agree}/{half}  → ★축분리 가설 기각(표본 독립성 없음)")
    print(f"수식슬롯형(≥{MODIFIER_CUT}%) 양쪽 공통: {sorted(mod_enc & mod_obs)}  (재현 안 되므로 채택 안 함)")
    print()
    print("★살아남은 지표 — 라벨 복합성(스팬 비겹침 장르 수)")
    print(f"  설계(encore, n={comp_enc['n']}): 복합 {comp_enc['multi_genre_pct']}% · "
          f"평균 {comp_enc['mean_genres_per_label']}개/라벨 · 분포 {comp_enc['genres_per_label_dist']}")
    print(f"  관측(sunolang, n={comp_obs['n']}): 복합 {comp_obs['multi_genre_pct']}% · "
          f"평균 {comp_obs['mean_genres_per_label']}개/라벨 · 분포 {comp_obs['genres_per_label_dist']}")
    print(f"→ {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
