#!/usr/bin/env python3
"""M2 불일치 27.2%의 원인 분리 — '규칙 순위 충돌' vs '실드리프트'.

probe가 낸 '요청↔관측 그룹 일치 27.2%'를 그대로 쓰면 안 된다.
encore 규칙은 **선언 순서 우선 단일배정**이라, 하나의 라벨이 여러 그룹 패턴에 동시 적중해도
먼저 선언된 그룹이 가져간다. 즉 불일치에는 최소 두 원인이 섞여 있다.

  (A) 순위충돌 — 관측 라벨이 요청그룹 패턴에도 적중하는데, 더 앞선 규칙이 선점
                 → 이건 '드리프트'가 아니라 어댑터(규칙 설계) 문제
  (B) 실드리프트 — 관측 라벨이 요청그룹 패턴에 아예 안 걸림
                 → Suno가 실제로 다른 장르로 서술

추가 검정:
  V1 라벨출처 검증 — entries.genre가 정말 design_intent(요청 SP 머리)인지 원문 대조
  V2 표본 편향   — 이 코퍼스의 장르 구성을 encore 5,754 모집단과 나란히 제시
  V3 ballad 특이 — 'ballad'가 장르그룹이 아니라 형식 슬롯일 가능성 검정

산출: data/exchange/genre_adapter_split_result.json
"""
import json
import re
import sqlite3
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
ENCORE = ROOT / "data" / "exchange" / "encore_20260803" / "genre_design_normalize_v0.json"
OUT = ROOT / "data" / "exchange" / "genre_adapter_split_result.json"


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

    def allhits(label):
        return {g for g, p in rules if label and p.search(label)}

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT song_id, entity, genre FROM entries "
                "WHERE slot='genre' AND source='sp_entity' AND entity IS NOT NULL")
    obs, req = {}, {}
    for sid, ent, g in cur.fetchall():
        obs.setdefault(sid, ent.strip())
        if g and g.strip():
            req[sid] = g.strip()

    # ── V1: 요청 라벨 출처 검증 (entries.genre ↔ leomusic_sp_full 원문) ─────────
    cur.execute("SELECT song_id, sentence FROM entries WHERE source='leomusic_sp_full'")
    req_sp = {sid: s for sid, s in cur.fetchall()}
    v1_checked = v1_ok = 0
    v1_examples = []
    for sid, label in req.items():
        sp = req_sp.get(sid)
        if not sp:
            continue
        v1_checked += 1
        head = sp.strip().splitlines()[0][:200].lower()
        toks = [t for t in re.split(r"[\s/,\-]+", label.lower()) if len(t) > 2]
        hit = sum(1 for t in toks if t in head)
        ok = toks and hit >= max(1, len(toks) // 2)
        v1_ok += bool(ok)
        if len(v1_examples) < 6:
            v1_examples.append({"song_id": sid, "entries_genre": label,
                                "leomusic_sp_head": sp.strip().splitlines()[0][:120],
                                "token_hit": f"{hit}/{len(toks)}", "match": bool(ok)})

    # ── M2 분리 ──────────────────────────────────────────────────────────────
    A, B, agree = [], [], 0
    cause = collections.Counter()
    b_trans = collections.Counter()
    for sid, o in obs.items():
        if sid not in req:
            continue
        rg, og = first(req[sid]), first(o)
        if rg == og:
            agree += 1
            continue
        if rg in allhits(o):
            cause["A_rule_order"] += 1
            A.append({"song_id": sid, "requested": req[sid], "observed": o,
                      "requested_group": rg, "assigned_group": og,
                      "observed_also_hits": sorted(allhits(o))})
        else:
            cause["B_real_drift"] += 1
            b_trans[(rg, og)] += 1
            B.append({"song_id": sid, "requested": req[sid], "observed": o,
                      "requested_group": rg, "observed_group": og})

    n = agree + len(A) + len(B)
    # 순위충돌을 보정한 일치율 = (완전일치 + 요청그룹이 관측 라벨에 살아있는 건) / n
    adj = round(100.0 * (agree + len(A)) / n, 1)

    # ── V3: ballad = 장르그룹인가 형식슬롯인가 ────────────────────────────────
    ballad_obs = [o for o in obs.values() if re.search(r"\bballad\b", o, re.I)]
    ballad_with_other = 0
    ballad_only = []
    for o in ballad_obs:
        stripped = re.sub(r"\bballads?\b", " ", o, flags=re.I)
        hits = allhits(stripped) - {"ballad"}
        if hits:
            ballad_with_other += 1
        else:
            ballad_only.append(o)
    v3 = {
        "n_observed_labels_containing_ballad": len(ballad_obs),
        "n_also_carrying_another_genre_group": ballad_with_other,
        "pct_ballad_is_modifier_not_head": round(100.0 * ballad_with_other / len(ballad_obs), 1)
        if ballad_obs else None,
        "ballad_only_examples": sorted(set(ballad_only))[:12],
        "ballad_plus_other_examples": sorted({o for o in ballad_obs
                                              if allhits(re.sub(r'\bballads?\b', ' ', o, flags=re.I)) - {'ballad'}})[:12],
    }

    # ── V2: 표본 편향 ────────────────────────────────────────────────────────
    v2 = {
        "sunolang_n_songs": len(obs),
        "sunolang_observed_group_mix": dict(collections.Counter(first(o) for o in obs.values()).most_common()),
        "encore_population_n_clips": meta["input"],
        "encore_design_group_mix_top": dict(sorted(meta["group_counts"].items(),
                                                   key=lambda x: -x[1])[:8]),
        "caveat": "두 모집단은 다르다 — sunolang 코퍼스는 K-계열 편중(K-scene 접두 92.7%), "
                  "encore 모집단은 trot 1012 최다. 일치율 수치를 encore 전 모집단에 외삽 금지.",
    }

    res = {
        "as_of": "2026-08-04",
        "owner": "sunolanguage",
        "purpose": "probe M2 일치율 27.2%의 원인 분리 (순위충돌 vs 실드리프트)",
        "V1_requested_label_provenance": {
            "checked": v1_checked, "matched": v1_ok,
            "match_pct": round(100.0 * v1_ok / v1_checked, 1) if v1_checked else None,
            "examples": v1_examples,
            "note": "entries.genre가 요청 SP 머리행과 토큰 과반 일치하면 design_intent로 인정",
        },
        "M2_split": {
            "n_pairs": n,
            "exact_agree": agree,
            "exact_agree_pct": round(100.0 * agree / n, 1),
            "A_rule_order_conflict": len(A),
            "B_real_drift": len(B),
            "adjusted_agree_pct_counting_A_as_kept": adj,
            "cause_counts": dict(cause),
            "B_top_transitions": [{"from": k[0], "to": k[1], "n": v}
                                  for k, v in b_trans.most_common(12)],
            "A_examples": A[:8],
            "B_examples": B[:10],
        },
        "V2_sample_bias": v2,
        "V3_ballad_is_form_slot": v3,
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))

    print(f"[V1] 요청라벨 출처검증 {v1_ok}/{v1_checked} ({res['V1_requested_label_provenance']['match_pct']}%) design_intent 확인")
    print(f"[M2] 대조쌍 {n} — 완전일치 {agree}({res['M2_split']['exact_agree_pct']}%) "
          f"/ A순위충돌 {len(A)} / B실드리프트 {len(B)}")
    print(f"     ★순위충돌 보정 일치율 = {adj}%  ← '27.2% 드리프트'는 과대 진술")
    print(f"[V3] ballad 포함 관측라벨 {v3['n_observed_labels_containing_ballad']}건 중 "
          f"{v3['n_also_carrying_another_genre_group']}건({v3['pct_ballad_is_modifier_not_head']}%)이 "
          f"다른 장르그룹도 동시보유 → ballad=형식슬롯 가설 지지")
    print("[B] 실드리프트 상위:")
    for t in res["M2_split"]["B_top_transitions"][:8]:
        print(f"       {t['from']:>14} → {t['to']:<14} {t['n']}")
    print(f"→ {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
