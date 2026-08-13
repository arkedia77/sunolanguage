#!/usr/bin/env python3
"""(spoken) 판정의 ★대조군 민감도 — 정본화 전 게이트

왜 이걸 하는가:
  `spoken_delivery_probe`가 두 번 돌았고 **두 판정이 서로 뒤집혔다**(asrun1 vs 최종).
  차이는 대상 오디오가 아니라 **말 극(B)에 쓴 TTS 음성 구성**뿐이다.
  z = (X − B) / (A − B) 이므로 B가 움직이면 판정이 통째로 움직인다.

  ⇒ 「(spoken)이 말하기로 실현됐다」를 정본에 박기 전에,
     **그 결론이 대조군 선택에 얼마나 종속되는지**를 먼저 재야 한다.
     자가 흔들리면 결론이 아니라 자를 보고해야 한다.

★새로 측정하지 않는다. 기존 산출물의 측정값만 재조합한다(크레딧 0·재현 가능).
판정 규칙은 사전등록(docs/spoken_delivery_probe_preregistration.md §5·§6) 그대로 쓴다 — 고치지 않는다.
"""
import json
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "data" / "exchange" / "spoken_delivery_probe_result.json"
OUT = REPO / "data" / "exchange" / "spoken_probe_sensitivity.json"

METRICS = ("sustain_ratio", "delta_semitone_median", "voiced_ratio")
# 사전등록 §3 방향: 노래 극에 가까우면 '노래', 말 극에 가까우면 '말하기'
GATE_MIN = 0.15   # §6 기각 조건: 주지표에서 두 극이 이만큼도 안 벌어지면 판정 자체를 안 한다
LO, HI = 0.35, 0.65  # §5


def verdict_one(z):
    if z <= LO:
        return "말하기"
    if z >= HI:
        return "노래"
    return "보류"


def decide(votes):
    """§5: 3지표 중 2개 이상이 같은 방향일 때만 결론."""
    for side in ("말하기", "노래"):
        if sum(1 for v in votes.values() if v == side) >= 2:
            return side
    return "보류"


def main():
    src = json.loads(SRC.read_text())
    tts = src["말극_B_TTS"]
    voices = list(tts)

    rows = []
    for r in range(1, len(voices) + 1):
        for combo in combinations(voices, r):
            B = {m: sum(tts[v][m] for v in combo) / len(combo) for m in METRICS}
            entry = {"B극_구성": list(combo), "n": len(combo)}
            for clip, cd in src["클립"].items():
                A, X = cd["노래극_A"], cd["spoken_대상_X"]
                sep = abs(A["sustain_ratio"] - B["sustain_ratio"])
                if sep < GATE_MIN:
                    entry[clip] = {"게이트": "기각", "주지표_분리도": round(sep, 4),
                                   "판정": "판정안함(§6)"}
                    continue
                votes, zs = {}, {}
                for m in METRICS:
                    denom = A[m] - B[m]
                    if denom == 0:
                        votes[m], zs[m] = "보류", None
                        continue
                    z = (X[m] - B[m]) / denom
                    zs[m] = round(z, 3)
                    votes[m] = verdict_one(z)
                entry[clip] = {"게이트": "통과", "주지표_분리도": round(sep, 4),
                               "z": zs, "지표별": votes, "판정": decide(votes)}
            rows.append(entry)

    summary = {}
    for clip in src["클립"]:
        tally, gated = {}, 0
        for row in rows:
            v = row[clip]["판정"]
            if row[clip]["게이트"] == "기각":
                gated += 1
            tally[v] = tally.get(v, 0) + 1
        summary[clip] = {"대조군_조합수": len(rows), "게이트_기각": gated, "판정분포": tally}

    out = {
        "무엇": "(spoken) 판정이 말 극(B) 구성에 얼마나 종속되는지 — 대조군 전수 재조합",
        "★새_측정_없음": f"측정값 출처 = {SRC.relative_to(REPO)} (재조합만)",
        "판정규칙": "사전등록 §5·§6 그대로 (z≤0.35 말하기 / ≥0.65 노래 / 사이 보류, 2표 이상)",
        "대조군_후보": voices,
        "요약": summary,
        "전수": rows,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))

    print(f"대조군 후보 TTS {len(voices)}음성 → 조합 {len(rows)}가지 전수\n")
    for clip, s in summary.items():
        print(f"[{clip}] 게이트 기각 {s['게이트_기각']}/{s['대조군_조합수']}")
        for k, v in sorted(s["판정분포"].items(), key=lambda x: -x[1]):
            print(f"    {k:10s} {v:3d}/{s['대조군_조합수']}  ({v/s['대조군_조합수']*100:.0f}%)")
        print()

    print("── 단일 음성만 B극으로 썼을 때 (가장 극단) ──")
    for row in rows:
        if row["n"] != 1:
            continue
        cells = "  ".join(f"{c}={row[c]['판정']}" for c in src["클립"])
        print(f"  {row['B극_구성'][0]:22s} {cells}")
    print(f"\n저장: {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
