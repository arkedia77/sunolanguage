#!/usr/bin/env python3
"""N=4 확장 결과의 **정직한 집계** — 그리고 내 1차 집계문 폐기.

★왜 별도 파일인가: 1차 실행(`spoken_delivery_probe_n4.py`)이 낸 집계문이
   **「말하기 1/4」**였다. 이건 오도다 — 4클립 중 **2클립은 게이트가 기각**해서
   **판정 자체를 안 했는데**, 분모에 넣어 「말하기가 아닌 쪽」처럼 셌다.
   ⇒ **「측정 못 함」을 「아님」으로 접은 것**이고, 오늘 하루 내가 세 번 고친 바로 그 형태다.

★이 파일은 F0를 다시 계산하지 않는다. 1차 산출 JSON의 지표를 읽어 **집계만** 다시 낸다.

실행: python3 scripts/spoken_delivery_probe_n4_report.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "data" / "exchange" / "spoken_delivery_probe_n4.json"
OUT = REPO / "data" / "exchange" / "spoken_delivery_probe_n4_report.json"
KEYS = ("sustain_ratio", "delta_semitone_median", "voiced_ratio")
GATE = 0.15   # 사전등록 §6


def main():
    d = json.loads(SRC.read_text())
    B = d["말극_B_평균"]
    통과, 기각, posthoc = {}, {}, {}

    for lb, e in d["클립"].items():
        A, X = e.get("노래극_A"), e.get("spoken_대상_X")
        row = {"게이트_분리도": e.get("게이트_주지표_분리도"),
               "spoken_집계행수": e.get("spoken_집계행수")}
        if e.get("게이트") == "통과":
            통과[lb] = {**row, "판정": e.get("판정_규칙그대로"),
                        "z": e.get("z_정규화위치"),
                        "판정_분리지표만_post_hoc": e.get("판정_분리지표만_post_hoc")}
        else:
            기각[lb] = {**row, "판정": "★안 함 — 게이트 기각(자가 말/노래를 못 가름)"}
            # ★참고값: 규칙대로면 안 내는 값이다. 「판정 아님」을 이름에 박아 둔다.
            if A and X and B:
                z = {}
                for k in KEYS:
                    den = A[k] - B[k]
                    z[k] = round((X[k] - B[k]) / den, 3) if den else None
                posthoc[lb] = {
                    "★지위": "★판정 아님 — 게이트가 기각한 자로 낸 값이다. 인용 금지.",
                    "z_정규화위치": z,
                    "읽으면": "z가 1 부근이면 그 클립의 (spoken) 구간이 **그 클립의 가창부와 구분이 안 된다**는 뜻이지, "
                              "「노래로 렌더됐다」는 판정이 아니다. 자가 이미 기각됐기 때문이다.",
                }

    result = {
        "무엇": "N=4 확장의 정직한 집계 — 1차 집계문 폐기분",
        "재현": "python3 scripts/spoken_delivery_probe_n4_report.py (★F0 재계산 없음)",
        "원자료": "data/exchange/spoken_delivery_probe_n4.json",
        "★폐기한_내_1차_집계문": {
            "문면": d.get("★집계", {}).get("★인용문"),
            "왜_틀렸나": "★게이트 기각 2클립을 분모에 넣어 「말하기가 아닌 쪽」처럼 셌다. "
                         "**「측정 못 함」을 「아님」으로 접은 것**이다.",
        },
        "★정직한_집계": {
            "대상_클립": len(d["클립"]),
            "게이트_통과": f"{len(통과)}/{len(d['클립'])}",
            "게이트_기각": f"{len(기각)}/{len(d['클립'])}",
            "★판정_가능_표본": len(통과),
            "통과분_판정": {lb: v["판정"] for lb, v in 통과.items()},
            "★인용문": f"`(spoken)` 괄호 채널 — **판정 가능 표본은 {len(통과)}클립**"
                       f"(측정 시도 {len(d['클립'])}, 게이트 기각 {len(기각)}). "
                       f"그중 **말하기 {sum(1 for v in 통과.values() if (v['판정'] or '').startswith('말하기'))}"
                       f"·보류 {sum(1 for v in 통과.values() if '보류' in (v['판정'] or ''))}**. "
                       f"★**표본을 2배로 늘렸는데 판정 가능 표본은 안 늘었다.**",
        },
        "게이트_통과분": 통과,
        "게이트_기각분": 기각,
        "★참고값(판정_아님)": posthoc,
        "★이번_확장이_실제로_바꾼_것": [
            "★**N=2 → N=4는 「표본 2배」였지 「근거 2배」가 아니었다.** 추가된 2클립은 자가 기각됐다.",
            "★**기각 사유가 정보다**: 뮤지컬 v2.3 편곡은 **가창부의 sustain이 낮아**(A 0.45/0.44 vs RM 0.53/0.55) "
            "말 극과 노래 극이 붙어 버린다. ⇒ **이 자는 편곡을 탄다.** 곡을 바꾸면 분리력이 먼저 무너진다.",
            "★그래서 대장의 한정자는 **「N=2」가 아니라 「판정 가능 2클립 / 시도 4클립·같은 곡 계열」**로 적어야 한다.",
        ],
        "★여전히_못_하는_것": [
            "게이트를 통과시키려고 문턱(0.15)을 내리지 않는다 — 값을 보고 문턱을 고치면 사전등록이 무의미해진다.",
            "뮤지컬 2 take의 라벨(M23a/b)은 여전히 미확정 — 단 이 집계는 이름에 안 기댄다.",
            "가청 판정이 아니다. 최종은 LEO 청음 트랙.",
        ],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))

    # ★1차 JSON의 오도 집계문을 방치하지 않는다 — 그 파일만 읽는 사람이 생긴다.
    d["★집계"] = {"★폐기": "이 블록의 「말하기 1/4」는 게이트 기각분을 분모에 넣은 오도였다.",
                  "정본": "data/exchange/spoken_delivery_probe_n4_report.json"}
    SRC.write_text(json.dumps(d, ensure_ascii=False, indent=1))

    print(json.dumps({k: v for k, v in result.items()
                      if k in ("★폐기한_내_1차_집계문", "★정직한_집계", "★이번_확장이_실제로_바꾼_것")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
