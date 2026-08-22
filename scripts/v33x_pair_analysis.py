#!/usr/bin/env python3
"""v33x_pair_analysis.py — V33X01 처방↔재분석 대조쌍 분석 (기저 대조군 포함).

이 배치의 목적: v3.3 신규 어휘를 **입력층에 처음 써넣은** 뒤, 재분석 SP에서 되받는지 본다.

★이 스크립트의 요점은 「V33X01을 재는 것」이 아니라 **「기저를 같이 재는 것」**이다.
  기저 없이 보면 아래 셋이 전부 발견처럼 보인다 — 셋 다 아니다:
    ⑴ K-Pop 편입 8/10(80%)  → 기저 80.9%. 차 -0.9%p. **이 배치의 성질이 아니라 코퍼스의 성질.**
    ⑵ BPM 정확일치 1/10     → 기저 4.9%. V33X01은 10%로 **오히려 위**. 재분석기 BPM은 원래 어긋난다(|차| 중앙값 16).
    ⑶ 어휘구 축자 회수 0/19 → 기저율 하 **기대 히트 0.17곡**. 0은 예상 범위. **검정력 없음**(상한 15.8%).

남는 관측은 하나뿐이다 — **구(句)는 안 지키고 낱말은 지킨다**:
    장르절 통짜 회수 0/10인데, **핵심 낱말 회수는 58.8%**(기저 33.3%, 층화 순열 p=0.0019).
⚠그러나 이 값은 **시점과 완전히 교락**돼 있다(기저 재분석=2026-04~05 / V33X01=2026-08, 동시기 대조군 0).
  ⇒ 「v3.3 Suno-native 라벨 덕분」이라고 **말할 수 없다.** 4개월 사이에 바뀐 모든 것이 후보다.
  ⇒ ★처방: 다음 배치는 **같은 세션에 v3.3 처방군 + 종전 방식 처방군을 반반** 넣고 둘 다 재분석한다.

사용: python3 scripts/v33x_pair_analysis.py
"""
from __future__ import annotations
import json, random, re, statistics as st, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_handoff import extract_genre          # ★양쪽에 같은 추출기 — 손으로 고르지 않는다

STOP = {"in", "the", "a", "and", "of", "with", "at", "on", "for", "featuring", "to"}
core = lambda s: [w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP and len(w) > 2]


def recall(clause: str, out: str):
    c = core(clause)
    return (sum(1 for w in c if w in out.lower()) / len(c), len(c)) if c else (None, 0)


def main():
    V = json.loads((ROOT / "data/v33x/V33X01_reanalysis.json").read_text(encoding="utf-8"))["rows"]
    base_raw = json.loads((ROOT / "data/reanalysis_v2/merged_4values.json").read_text(encoding="utf-8"))

    kp = re.compile(r"k-?pop|k-?indie", re.I)
    bpm = lambda s: (lambda m: int(m.group(1)) if m else None)(re.search(r"(\d{2,3})\s*BPM", s, re.I))

    pairs = []
    for m in base_raw:
        i = (m["leomusic_original"].get("sp") or "").strip()
        rs = m["suno_reanalysis"]
        if not i or not rs:
            continue
        pairs.append((i, " ".join((r.get("sp") or "") for r in rs), (rs[0].get("captured_at") or "")[:7]))

    print(f"기저 대조군 = 입력·출력 SP 짝 {len(pairs)}곡 / V33X01 = {len(V)}곡\n")

    # ⑴ K-Pop
    b = sum(1 for _, o, _ in pairs if kp.search(o)) / len(pairs)
    v = sum(1 for r in V if kp.search(r["재분석_SP"])) / len(V)
    print(f"⑴ K-Pop계 편입   V33X01 {v*100:.1f}%  vs 기저 {b*100:.1f}%   차 {(v-b)*100:+.1f}%p  → 기저 수준")

    # ⑵ BPM
    dd = [(bpm(o) - bpm(i)) for i, o, _ in pairs if bpm(i) and bpm(o)]
    be = sum(1 for x in dd if x == 0) / len(dd)
    ve = sum(1 for r in V if bpm(r["재분석_SP"]) == r["처방_bpm"]) / len(V)
    print(f"⑵ BPM 정확일치   V33X01 {ve*100:.1f}%  vs 기저 {be*100:.1f}%  (기저 |차| 중앙값 {st.median([abs(x) for x in dd])})  → 기저 이상")

    # ⑶ 어휘구 축자
    hit = sum(1 for r in V for x in r["처방_어휘"] if x.lower() in r["재분석_SP"].lower())
    n = sum(len(r["처방_어휘"]) for r in V)
    print(f"⑶ 어휘구 축자    {hit}/{n} = {hit/n*100:.1f}%   ★95% 상한 {3/n*100:.1f}% — 기저(0.2~3.2%)와 구분 불가 = 검정력 없음")

    # ⑷ 구 vs 낱말 + 층화 순열
    Vr = [recall(extract_genre(r["처방_SP"]), r["재분석_SP"]) for r in V]
    B = defaultdict(list)
    for i, o, _ in pairs:
        x, k = recall(extract_genre(i), o)
        if x is not None and k >= 1:
            B[k].append(x)
    obs = st.mean([x for x, _ in Vr])
    flat = [x for lst in B.values() for x in lst]
    random.seed(0)
    N = 20000
    p = sum(1 for _ in range(N)
            if st.mean([random.choice(B[k]) for _, k in Vr if B.get(k)]) >= obs) / N
    print(f"\n⑷ ★장르절 — 통짜 구 회수 0/10 = 0.0%  ·  핵심 낱말 회수 **{obs*100:.1f}%** vs 기저 {st.mean(flat)*100:.1f}%")
    print(f"   낱말수 층화 순열 p = {p:.4f}   (길이 교락 방향 점검: 낱말수≤3 기저 "
          f"{st.mean([x for k, l in B.items() if k <= 3 for x in l])*100:.1f}% < ≥4 기저 "
          f"{st.mean([x for k, l in B.items() if k >= 4 for x in l])*100:.1f}% — 짧은 쪽이 불리하므로 교락이 결과를 만든 게 아니다)")

    # ⑸ ★시점 교락
    tb = defaultdict(list)
    for i, o, ts in pairs:
        x, k = recall(extract_genre(i), o)
        if x is not None:
            tb[ts or "미상"].append(x)
    print(f"\n⑸ ⚠**시점 교락 — 이 관측의 결정적 한계**")
    for k in sorted(tb):
        print(f"     기저 {k:<8} n={len(tb[k]):>4}  {st.mean(tb[k])*100:>5.1f}%")
    print(f"     V33X01 2026-08  n={len(V):>4}  {obs*100:>5.1f}%")
    print("   ⇒ 동시기 대조군이 **0**이다. 4개월 시차의 모든 변화가 후보다(분석기 버전·우리 SP 관행·길이 규약).")
    print("   ⇒ ★다음 배치: 같은 세션에 v3.3 처방군 + 종전 방식 처방군을 반반 넣고 **둘 다** 재분석할 것.")


if __name__ == "__main__":
    main()
