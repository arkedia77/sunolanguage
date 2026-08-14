#!/usr/bin/env python3
"""곡 내 **take 산포** — 같은 입력으로 2 take를 뽑았을 때 길이가 얼마나 벌어지는가.

★왜 지금 되나: B-1(uuid↔곡 매핑)이 풀려서 **어느 두 클립이 같은 곡의 2 take인지**를 알게 됐다.
   그 전에는 8클립이 파일명으로만 있어 짝을 못 지었다.

★이 측정의 지위 — **사전등록 아님(exploratory)**:
   나는 B-1을 풀면서 **8클립의 길이를 이미 봤다.** 그러니 이건 「값 보기 전 설계」가 아니다.
   그렇게 적고 시작한다. 방향을 정해 놓고 자를 고르지 않았다는 것만 말할 수 있다.

★왜 분량 쌍(lyric_length_mapping)에는 안 넣나:
   렌더된 것은 **v2.3**인데 리포에 통짜로 남은 가사는 **v2.2 핸드오프**다(v2.3은 변경분 3건만 기록).
   음절·행 수를 v2.2로 세면 **스테일 가사로 재는 것**이 된다. ⇒ 분량 축은 건드리지 않는다.
   ★단 **take 산포는 영향받지 않는다** — 같은 곡의 두 take는 **서로 같은 입력**이기 때문이다.

실행: python3 scripts/vd_take_spread_v1.py
"""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VD = REPO / "data" / "vd_duet3"
OUT = REPO / "data" / "exchange" / "vd_take_spread_v1.json"

# 조건 = 같은 입력(가사·SP)으로 뽑힌 2 take 묶음. ★take 이름(a/b)은 안 쓴다(B-1 잔여 미확정).
CONDITIONS = {
    "뮤지컬-재제작(RM)": ["70365338-0b63-4369-a5e3-83ad4de94bb0",
                          "7a028e80-b6f7-47ce-846c-cb919ef55b5f"],
    "뮤지컬-v2.3": ["66621da8-7d04-4cea-b5c7-7808dbdc659c",
                    "b6cb18a6-6212-4893-bbdc-5230b50c3d63"],
    "발라드-v2.3": ["2b33b2a6-b35d-490c-af60-b783186ad6ab",
                    "28c2e16c-36e9-4e88-8bcf-aaf983f838f7"],
    "가스펠-v2.3": ["3776c8d9-9c2c-4f44-ab17-9cf4cdef5ac4",
                    "35bec5aa-28b0-4d91-a4ba-b2be2bcca7af"],
}
# 대조 상대 — leomusic3 Lyria 실측(08-13 11:27 제출 §4). ★내가 잰 값이 아니다. 출처 그대로 옮긴다.
LYRIA = {"A(153음절)": [180.4, 154.8], "B(223음절)": [131.7, 178.5], "C(294음절)": [155.3, 182.5]}
CM1_WINDOW = (150.0, 180.0)   # encore CM-2026-0001 요건 구간


def dur(uuid):
    p = VD / "audio_final" / f"{uuid}.mp3"
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return round(float(r.stdout.strip()), 2)


def spread(vals):
    lo, hi = min(vals), max(vals)
    mean = sum(vals) / len(vals)
    return {"take_초": sorted(vals), "평균": round(mean, 2),
            "폭_초": round(hi - lo, 2), "상대폭_%": round(100 * (hi - lo) / mean, 1)}


def main():
    suno = {name: spread([dur(u) for u in us]) for name, us in CONDITIONS.items()}
    lyria = {name: spread(v) for name, v in LYRIA.items()}

    s_rel = [v["상대폭_%"] for v in suno.values()]
    l_rel = [v["상대폭_%"] for v in lyria.values()]
    win = CM1_WINDOW[1] - CM1_WINDOW[0]

    result = {
        "무엇": "같은 입력 2 take의 길이 산포 — Suno(우리 VD 8클립) vs Lyria(leomusic3 회신값)",
        "★지위": "★**exploratory**(사전등록 아님) — B-1을 풀며 길이를 이미 본 뒤에 설계했다.",
        "재현": "python3 scripts/vd_take_spread_v1.py",
        "★Suno(내가_잰_것)": {
            "원자료": "data/vd_duet3/audio_final/*.mp3 (ffprobe) · 짝짓기 근거=VD_uuid_remap_posthoc.json",
            "조건별": suno,
            "상대폭_범위_%": [min(s_rel), max(s_rel)],
        },
        "★Lyria(남이_잰_것_—_옮긴_값)": {
            "출처": "leomusic3 → sunolanguage 2026-08-13 11:27 제출 §4(★내가 잰 값이 아니다)",
            "조건별": lyria,
            "상대폭_범위_%": [min(l_rel), max(l_rel)],
        },
        "★읽기": [
            f"**Suno도 take 산포가 작지 않다** — 상대폭 {min(s_rel)}~{max(s_rel)}%"
            f"(절대 {min(v['폭_초'] for v in suno.values())}~{max(v['폭_초'] for v in suno.values())}초). "
            "★같은 가사·같은 SP인데 이만큼 벌어진다.",
            f"Lyria는 {min(l_rel)}~{max(l_rel)}%로 **더 크다**. 다만 **범위가 겹친다** — "
            "「Lyria만 흔들린다」가 아니라 **「둘 다 흔들리고 Lyria가 더」**다.",
            f"★**요건 창이 {win:.0f}초인데 Suno의 take 폭이 "
            f"{min(v['폭_초'] for v in suno.values())}~{max(v['폭_초'] for v in suno.values())}초다.** "
            "⇒ **단일 take가 창에 드는 것은 상당 부분 운이다.** 분량 설계로 평균을 맞춰도 "
            "**한 take만 뽑으면 창을 벗어날 수 있다.**",
        ],
        "★B-3에_주는_것": {
            "무엇이_달라지나": "계획 §4.1은 「Suno=분량이 하한 지배 / Lyria=분량 무상관」의 대비를 "
                               "**엔진 차이**로 정리해 뒀다. ★여기서 나온 것은 **그 대비를 좁히는 쪽**이다 — "
                               "**Suno도 같은 입력에서 7.8~16.8% 흔들린다.**",
            "★그래도_충돌은_여전히_「충돌_아님」": "Suno 쪽 실측(9run 17클립)은 **Duration 락 180**이 걸린 조건이고 "
                                                 "여기 VD 8클립은 **락 기재가 없다.** 여전히 같은 조건이 아니다. "
                                                 "**락 유무 통제 대조는 아직 0건**이다.",
            "다음_한_수": "락을 건 조건과 안 건 조건에서 **같은 가사로 take를 여러 개** 뽑아야 갈린다 — "
                          "★생성이 필요하므로 **B-2(범위 확인) 소관**이다. 내가 임의로 안 연다.",
        },
        "★한계": [
            "★**조건당 take가 2개뿐**이다. 「폭」은 **범위**이지 산포 추정치가 아니다(표준편차 못 냄).",
            "조건마다 곡·장르·SP가 다르다 — **조건 간 비교는 안 한다**(곡 내 폭만 본다).",
            "VD 배치의 **Duration 락 설정 여부를 모른다.** CM-1 실측(락 180)과 같은 조건이 아니다.",
            "VD는 200~250초대, CM-1 요건은 150~180초대다 — **길이 대역이 다르다.** "
            "상대폭(%)으로 옮겨 적었으나 **대역 이동이 안전하다는 근거는 없다.**",
            "Lyria 값은 **내가 잰 것이 아니라 회신에서 옮긴 것**이다. 재현 책임은 그쪽에 있다.",
        ],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
