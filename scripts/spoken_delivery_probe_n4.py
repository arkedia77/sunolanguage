#!/usr/bin/env python3
"""`(spoken)` 전달 판정 — N=2 → **N=4 확장**.

★사전등록 정본 = `docs/spoken_delivery_probe_preregistration.md`(원판) +
   `docs/vd_uuid_remapping_preregistration.md` §7(확장 조건).
   **판정 규칙·지표·대조군은 원판 그대로다.** 여기서 바꾸는 것은 **대상 클립 수뿐**이다.

★왜 확장하나: 원 사전등록이 「v2.3 3곡은 `(spoken)` 0건」이라 적었는데 **사실오류**였다.
   뮤지컬 곡「그날도 오늘 같았죠」v2.3(M23a·M23b)은 RM과 **똑같은 `(spoken)` 4행**을 쓴다
   (`VD_HANDOFF_v2.json` /lyrics: `[Spoken Intro]`·`[Spoken Bridge]`).
   ⇒ 표본은 애초에 N=4였어야 했다. 08-13 자진 적발분.

★자를 복사하지 않는다: 지표·판정 함수를 **원 스크립트에서 import**한다.
   같은 날 「복사본은 한쪽만 늙는다」 사고를 2건 봤다(정본 스테일·gap 스크립트 19/15 분기).

실행: ~/leomusic3/.venv/bin/python scripts/spoken_delivery_probe_n4.py
      (선행 = scripts/vd_uuid_remap_v1.py 가 M23a·M23b uuid를 **확정**해 놓아야 함)
"""
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from spoken_delivery_probe import (  # noqa: E402  ★원판의 자를 그대로 쓴다
    SPOKEN_LINES, VD, agg, f0_track, line_match, load, metrics, tts_control,
)

REMAP = VD / "VD_uuid_remap_v1.json"
POSTHOC = VD / "VD_uuid_remap_posthoc.json"
OUT = REPO / "data" / "exchange" / "spoken_delivery_probe_n4.json"
KEYS = ("sustain_ratio", "delta_semitone_median", "voiced_ratio")
BASE = {  # 원판 대상(사전등록 §2) — 기록에 있던 2건
    "RM1": "70365338-0b63-4369-a5e3-83ad4de94bb0",
    "RM2": "7a028e80-b6f7-47ce-846c-cb919ef55b5f",
}


def tally(votes):
    for v in ("말하기", "노래"):
        if votes.count(v) >= 2:
            return f"{v} 쪽 ({votes.count(v)}표)"
    return "★보류 — 2표 이상 한 방향으로 안 모임"


def judge(label, uuid, segs_of_clip, B):
    stem = VD / "stems_final" / "htdemucs" / uuid / "vocals.wav"
    if not stem.exists():
        return {"오류": f"스템 없음 {stem}"}
    sp_chunks, sung_chunks, sp_detail, unmeasurable = [], [], [], []
    for s in segs_of_clip:
        f0 = f0_track(load(stem, s["s"], s["e"]))
        if line_match(s["t"], SPOKEN_LINES):
            m = metrics(f0)
            row = {"구간": f'{s["s"]}~{s["e"]}s', "행": s["t"]}
            if m:
                sp_chunks.append(f0)
                row.update(m)
            else:
                row["측정"] = "★불가 — 유성 프레임 20 미만"
                unmeasurable.append(row)
            sp_detail.append(row)
        else:
            sung_chunks.append(f0)
    A, X = agg(sung_chunks), agg(sp_chunks)
    e = {"uuid": uuid, "노래극_A": A, "spoken_대상_X": X, "spoken_행별": sp_detail,
         "spoken_집계행수": len(sp_chunks), "★측정불가_구간": unmeasurable,
         "가창_구간수": len(sung_chunks)}
    if A and B:
        sep = abs(A["sustain_ratio"] - B["sustain_ratio"])
        e["게이트_주지표_분리도"] = round(sep, 4)
        e["게이트"] = "통과" if sep >= 0.15 else "★기각 — 지표가 말/노래를 구분 못 함. 대상 판정 안 함"
        e["지표별_양극분리도"] = {k: round(abs(A[k] - B[k]), 4) for k in KEYS}
    if A and B and X and e.get("게이트") == "통과":
        z, votes = {}, []
        for k in KEYS:
            den = A[k] - B[k]
            zi = (X[k] - B[k]) / den if den else float("nan")
            z[k] = round(float(zi), 3)
            votes.append("말하기" if zi <= 0.35 else "노래" if zi >= 0.65 else "보류")
        e["z_정규화위치"] = z
        e["지표별_판정"] = dict(zip(KEYS, votes))
        e["판정_규칙그대로"] = tally(votes)
        live = [k for k in KEYS if abs(A[k] - B[k]) >= 0.30 * (abs(A[k]) + abs(B[k])) / 2]
        e["★사후_분리지표만"] = live
        e["판정_분리지표만_post_hoc"] = tally([votes[KEYS.index(k)] for k in live]) if live else "지표 0개 — 판정 불가"
    return e


def main():
    if not (REMAP.exists() and POSTHOC.exists()):
        sys.exit("★선행 미완 — vd_uuid_remap_v1.py → vd_uuid_remap_posthoc.py 순으로 먼저 돌릴 것(B-1)")
    remap = json.loads(REMAP.read_text())
    post = json.loads(POSTHOC.read_text())
    if post["★결론"]["곡"] != "★확정":
        sys.exit("★곡 수준도 미확정 — 확장 안 한다(추측 매핑 금지)")

    # ★take 이름(a/b)은 미확정이다. 이름을 쓰지 않고 **uuid로** 대상을 잡는다.
    #   집계값은 a/b를 맞바꿔도 불변이므로 이름 없이도 성립한다(posthoc 참조).
    뮤지컬 = sorted(u for u, v in post["★결론"]["내용"].items() if v.startswith("★뮤지컬"))
    대상 = dict(BASE)
    for i, u in enumerate(뮤지컬, 1):
        대상[f"M23-{u[:8]}"] = u          # ★a/b 대신 uuid 앞 8자로 부른다

    # 구간은 **각 클립 자신의 전사**로 잡는다.
    #  - RM1·RM2 = 원판과 동일하게 원장(VD_final_asr.json) 사용 → 원 결과와 비교 가능
    #  - 뮤지컬 2 take = 라벨이 미확정이라 원장 키를 못 쓴다 → 재실행 전사(같은 오디오에서 뜬 것) 사용
    #  ★두 클립군의 구간 출처가 다르다는 사실을 결과에 적는다(조용히 섞지 않는다).
    ledger = json.loads((VD / "VD_final_asr.json").read_text())
    rerun = remap["재실행_전사"]
    segs_for, seg_src = {}, {}
    for lb, u in 대상.items():
        if lb in BASE:
            segs_for[lb], seg_src[lb] = ledger[lb], "원장 VD_final_asr.json(원판과 동일)"
        else:
            segs_for[lb], seg_src[lb] = rerun[u]["segs"], "★재실행 전사(라벨 미확정이라 원장 키 사용 불가)"
    스킵 = []
    tts = tts_control()
    b_metrics = [(v, m) for v, m in ((v, metrics(f)) for v, f in tts) if m]
    B = {k: float(np.mean([m[k] for _, m in b_metrics])) for k in KEYS} if b_metrics else None

    result = {
        "사전등록": "docs/spoken_delivery_probe_preregistration.md(원판 규칙 그대로) + "
                    "docs/vd_uuid_remapping_preregistration.md §7(확장 조건)",
        "★확장_사유": "원 사전등록의 사실오류 자진 적발 — 「v2.3 3곡 (spoken) 0건」이 틀렸고 "
                      "뮤지컬 v2.3은 RM과 동일한 (spoken) 4행을 쓴다. 표본은 애초에 N=4.",
        "★대조군_아님": "M23a·M23b는 RM과 **같은 입력 조건(괄호 (spoken))**의 추가 표본이다. "
                        "SP·브라켓은 다르므로 **미니멀 페어가 아니다** — 기여 분리에 쓰면 안 된다.",
        "대상": {"계상": {lb: u for lb, u in 대상.items()}, "★제외": 스킵 or "없음"},
        "★라벨_주의": "뮤지컬 2 take는 **M23a/M23b 중 어느 쪽인지 미확정**이라 uuid 앞 8자로 부른다. "
                      "`VD_FINAL_judgment.json` §2의 화자 순서 판정(M23a/M23b)과 **이름으로 이어 붙이지 말 것.**",
        "★구간_출처": seg_src,
        "매핑_근거": "data/vd_duet3/VD_uuid_remap_v1.json(대조군 4/4 복원 통과) + "
                     "VD_uuid_remap_posthoc.json(곡 수준 확정 4/4)",
        "말극_B_TTS": {v: m for v, m in b_metrics},
        "말극_B_평균": {k: round(v, 4) for k, v in B.items()} if B else None,
        "클립": {},
    }
    for lb, u in 대상.items():
        print(f"[판정] {lb} {u[:8]} …", flush=True)
        result["클립"][lb] = judge(lb, u, segs_for[lb], B)

    판정 = {lb: e.get("판정_규칙그대로") for lb, e in result["클립"].items()}
    말 = sum(1 for v in 판정.values() if v and v.startswith("말하기"))
    result["★집계"] = {
        "클립별_판정(규칙그대로)": 판정,
        "N": len(대상),
        "말하기_판정": f"{말}/{len(대상)}",
        "★인용문": f"`(spoken)` 괄호 채널 — 기계 판정 **말하기 {말}/{len(대상)}** "
                   f"(N={len(대상)}, 대조군=TTS {len(b_metrics)}음성). "
                   f"★곡 수준 일반화 금지 — 곡 2편·take {len(대상)}개다.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(json.dumps(result["★집계"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
