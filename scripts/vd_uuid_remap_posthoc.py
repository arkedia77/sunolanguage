#!/usr/bin/env python3
"""B-1 사후 분석 — 「곡은 확정됐고 take 이름만 미확정」을 기계로 분리한다.

★ASR을 다시 돌리지 않는다. `VD_uuid_remap_v1.json`에 저장된 **재실행 전사**를 읽는다.
★사전등록(`docs/vd_uuid_remapping_preregistration.md`) §5의 1차 판정은 **그대로 둔다.**
   여기 있는 것은 **명시적 post-hoc**이고, 그렇게 표시한다.

왜 필요한가 — ★대조군이 규칙의 결함을 드러냈다:
  기지 4클립 배정은 **4/4 정확**했는데(§4 게이트 통과), 같은 §5 마진 규칙을 클립별로 걸면
  그중 **3건이 「미확정」**으로 떨어진다(RM1 0.0100 · RM2 0.0136 · G2 0.0317).
  ⇒ 규칙이 **맞은 답을 부정하고 있다.** 원인은 마진을 **전 라벨**에 대해 재기 때문이고,
     같은 곡의 2 take는 가사가 사실상 같아서 **원리상 텍스트로 안 갈린다.**

실행: python3 scripts/vd_uuid_remap_posthoc.py
"""
import json
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VD = REPO / "data" / "vd_duet3"
SRC = VD / "VD_uuid_remap_v1.json"
OUT = VD / "VD_uuid_remap_posthoc.json"

SONG = {  # 라벨 → 곡. take 접미(a/b·1/2)를 떼면 이 세 곡이다.
    "RM1": "뮤지컬(그날도 오늘 같았죠)-재제작", "RM2": "뮤지컬(그날도 오늘 같았죠)-재제작",
    "M23a": "뮤지컬(그날도 오늘 같았죠)-v2.3", "M23b": "뮤지컬(그날도 오늘 같았죠)-v2.3",
    "BL1": "발라드(그대 이름 하나만)", "BL2": "발라드(그대 이름 하나만)",
    "G1": "가스펠(모든 것이 은혜였죠)", "G2": "가스펠(모든 것이 은혜였죠)",
}
SONG_MARGIN = 0.05  # post-hoc 기준(1차 규칙 0.10과 구분해 별도 이름으로 둔다)


def norm(s):
    return "".join(ch for ch in s if ch.isalnum())


def sim(a, b):
    ca, cb = Counter(a), Counter(b)
    if not ca or not cb:
        return 0.0
    return sum((ca & cb).values()) / min(len(a), len(b))


def analyze(name, labels, uuids, clip_text, ledger_text, ledger_end, durs, truth=None):
    rows = {}
    for u in uuids:
        # 곡 단위로 접는다 — 같은 곡의 여러 라벨 중 최댓값을 그 곡의 점수로.
        by_song = {}
        for lb in labels:
            s = sim(clip_text[u], ledger_text[lb])
            by_song[SONG[lb]] = max(by_song.get(SONG[lb], 0.0), s)
        ranked = sorted(by_song.items(), key=lambda kv: -kv[1])
        margin = round(ranked[0][1] - ranked[1][1], 4) if len(ranked) > 1 else None
        # 길이 하한으로 배제되는 라벨(=원리상 후보 아님)
        infeasible = [lb for lb in labels if durs[u] < ledger_end[lb]]
        rows[u] = {
            "곡_1위": [ranked[0][0], round(ranked[0][1], 4)],
            "곡_2위": [ranked[1][0], round(ranked[1][1], 4)] if len(ranked) > 1 else None,
            "곡_마진": margin,
            "곡_판정": "확정" if margin is not None and margin >= SONG_MARGIN else "★미확정",
            "길이하한으로_배제된_라벨": infeasible or "없음",
        }
        if truth:
            rows[u]["정답_곡"] = SONG[truth[u]]
            rows[u]["곡_적중"] = (ranked[0][0] == SONG[truth[u]])
    return {"대상": name, "클립별": rows,
            "곡_확정": f"{sum(1 for r in rows.values() if r['곡_판정'] == '확정')}/{len(rows)}",
            **({"곡_적중": f"{sum(1 for r in rows.values() if r['곡_적중'])}/{len(rows)}"} if truth else {})}


def main():
    src = json.loads(SRC.read_text())
    ledger = json.loads((VD / "VD_final_asr.json").read_text())
    ledger_text = {k: norm("".join(s["t"] for s in v)) for k, v in ledger.items()}
    ledger_end = {k: v[-1]["e"] for k, v in ledger.items()}
    durs = src["길이_실측"]
    clip_text = {u: norm("".join(s["t"] for s in v["segs"]))
                 for u, v in src["재실행_전사"].items()}

    known = {v: k for k, v in
             {"RM1": "70365338-0b63-4369-a5e3-83ad4de94bb0",
              "RM2": "7a028e80-b6f7-47ce-846c-cb919ef55b5f",
              "BL2": "28c2e16c-36e9-4e88-8bcf-aaf983f838f7",
              "G2": "35bec5aa-28b0-4d91-a4ba-b2be2bcca7af"}.items()}
    unknown = src["본과제_미매핑4건"]["배정"]      # uuid -> label (1차 배정)

    ctrl = analyze("대조군(기지 4클립)", list(known.values()), list(known),
                   clip_text, ledger_text, ledger_end, durs, truth=known)
    task = analyze("본과제(미매핑 4클립)", ["M23a", "M23b", "BL1", "G1"], list(unknown),
                   clip_text, ledger_text, ledger_end, durs)

    # take 수준 분해 — 곡은 같은데 라벨이 둘인 경우만 남긴다.
    take_level = {}
    for u, lb in unknown.items():
        sibs = [x for x in ("M23a", "M23b", "BL1", "G1") if SONG[x] == SONG[lb]]
        if len(sibs) > 1:
            ss = {x: round(sim(clip_text[u], ledger_text[x]), 4) for x in sibs}
            top = sorted(ss.items(), key=lambda kv: -kv[1])
            take_level[u] = {"후보": ss, "1차배정": lb, "마진": round(top[0][1] - top[1][1], 4),
                             "판정": "★미확정 — 같은 곡 2 take는 가사가 사실상 같아 텍스트로 안 갈린다"}

    result = {
        "무엇": "B-1 사후 분석 — 곡 확정 / take 이름 미확정의 분리",
        "★지위": "★post-hoc이다. 사전등록 §5의 1차 판정(확정 2·미확정 2)은 취소하지 않고 그대로 둔다.",
        "재현": "python3 scripts/vd_uuid_remap_posthoc.py (★ASR 재실행 없음 — 저장된 전사 사용)",
        "1차_판정(사전등록_그대로)": {
            u: v["판정"] for u, v in src["본과제_미매핑4건"]["세부"]["클립별"].items()},
        "★대조군이_드러낸_규칙_결함": {
            "사실": "기지 4클립 **배정은 4/4 정확**한데, 같은 클립별 마진 규칙(≥0.10)을 걸면 "
                    "**3건이 미확정**으로 떨어진다(RM1 0.0100·RM2 0.0136·G2 0.0317).",
            "해석": "★규칙이 **맞은 답을 부정한다.** 마진을 **전 라벨**에 대해 재는데, "
                    "같은 곡 2 take는 가사가 사실상 같아 **원리상 텍스트로 안 갈린다.**",
            "★그래서_뭘_안_하나": "규칙을 소급해 고쳐 「확정」으로 바꾸지 않는다. "
                                  "사전등록의 값은 사전등록의 값으로 남기고, 아래를 **별도 판정**으로 병기한다.",
        },
        "곡_수준_판정(post_hoc)": {"대조군": ctrl, "본과제": task},
        "take_수준_판정(post_hoc)": take_level,
        "★결론": None,
        "★이_결론이_N=4_확장에_충분한가": None,
    }

    ok = (ctrl.get("곡_적중") == f"{len(known)}/{len(known)}"
          and task["곡_확정"] == "4/4")
    뮤지컬 = sorted(u for u, lb in unknown.items() if SONG[lb].startswith("뮤지컬") and lb.startswith("M23"))
    result["★결론"] = {
        "곡": "★확정" if ok else "★미확정",
        "내용": {
            "2b33b2a6-b35d-490c-af60-b783186ad6ab": "발라드(그대 이름 하나만) take — 원장 라벨 BL1",
            "3776c8d9-9c2c-4f44-ab17-9cf4cdef5ac4": "가스펠(모든 것이 은혜였죠) take — 원장 라벨 G1",
            **{u: "★뮤지컬 v2.3 take — 원장 라벨 M23a/M23b 중 하나(★어느 쪽인지는 미확정)"
               for u in 뮤지컬},
        },
        "★남은_미확정": "뮤지컬 2 take의 **이름(a/b)**. 해소하려면 sunomusic 생성 원장(생성 순서·uuid) 조회가 필요하다 — 오디오로는 원리상 못 가른다.",
    }
    result["★이_결론이_N=4_확장에_충분한가"] = {
        "답": "★충분하다.",
        "이유": "확장은 **뮤지컬 v2.3의 2 take를 표본에 넣는 것**이고, 두 클립이 모두 들어가면 "
                "집계값(말하기 n/4)은 **a와 b를 맞바꿔도 불변**이다. 이름은 측정에 안 쓰인다.",
        "★단_쓰면_안_되는_곳": "`VD_FINAL_judgment.json` §2의 **화자 순서 판정(M23a 미정합/M23b 정합)**과 "
                              "이 결과를 이름으로 이어 붙이면 안 된다 — 그 이름이 지금 미확정인 그 이름이다.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in result.items() if k != "곡_수준_판정(post_hoc)"},
                     ensure_ascii=False, indent=1))
    print("\n곡 수준:", json.dumps({"대조군": ctrl["곡_적중"], "대조군_확정": ctrl["곡_확정"],
                                   "본과제_확정": task["곡_확정"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
