#!/usr/bin/env python3
"""CM-2026-0001 「아빠가 딸에게(가칭)」 A·B·C 3안 생성기.

★설계 원칙 = **포함관계** A ⊂ B ⊂ C.
가장 긴 C를 먼저 쓰고 절을 덜어내 B·A를 만든다. 남는 행은 글자 하나 안 고친다.
발주(encore 08-13 §2)가 「세 안의 정서·화자 구조는 같게 유지 — 분량만 흔드는 미니멀 페어」를
요구했기 때문이다. 서로 다른 가사로 쓰면 어휘·정서·음절밀도가 같이 변해 교락한다.

★행 수·음절 수는 손으로 세지 않는다 — 내 수치는 늘 낙관 방향이라 기계로 센다.
"""
import json
import re

# ── 섹션 정의 ────────────────────────────────────────────────────────────
# in_: 어느 안에 들어가는가. 'ABC' = 전 안 공통(=A), 'BC' = B와 C, 'C' = C 전용.
# bracket: R1 — 화자는 vocal_main 브라켓 독립 행으로, 섹션 브라켓 바로 다음 줄.
SECTIONS = [
    dict(name="Intro", in_="ABC", bracket="[baritone male vocals]", 화자="아버지(말)", lines=[
        "불 꺼진 링크에 너 혼자 남던 새벽 (spoken)",
        "나는 늘 저 끝에 서 있었어 (spoken)",
    ]),
    dict(name="Verse 1", in_="ABC", bracket="[baritone male vocals]", 화자="아버지", lines=[
        "숨이 하얗게 번지던 자리",
        "네가 처음 발을 딛던 자리",
        "작은 날이 얼음을 긋고",
        "그 소리가 아직 남아 있어",
    ]),
    dict(name="Verse 2", in_="ABC", bracket="[female vocals enter, breathy]", 화자="딸", lines=[
        "불빛이 나를 감싸면",
        "발끝부터 조용해져",
        "아무도 모르는 박자로",
        "여기서 나는 숨을 쉬어",
    ]),
    dict(name="Pre-Chorus", in_="C", bracket="[breathy female vocals]", 화자="딸", lines=[
        "손끝이 먼저 알아",
        "이제는 놓아도 된다고",
    ]),
    dict(name="Chorus", in_="ABC", bracket="[unison male and female vocals, full band energy]",
         화자="둘", lines=[
        "돌아, 네가 그리는 선을 따라",
        "빛이 너를 따라 돌고 있어",
        "아무리 멀어도 같은 자리",
        "나는 네 원 안에 있어",
    ]),
    dict(name="Verse 3", in_="BC", bracket="[baritone male vocals]", 화자="아버지", lines=[
        "내가 비운 계절만큼",
        "너는 혼자 자랐고",
        "이제 네가 앞서 가고",
        "나는 뒤에서 웃는다",
    ]),
    # ★한 섹션 안에서 화자가 바뀐다 — 정본 §3.2 C_1484가 실증한 형태
    # ([Verse 2] / [male vocals] / [male and female duet]). 중간 화자 브라켓은 attested.
    dict(name="Bridge", in_="C", bracket="[baritone male vocals]", 화자="아버지(말)→딸", lines=[
        "오늘은 아빠가 아니라 관객이야 (spoken)",
        "마음껏 해, 다 보고 있을게 (spoken)",
        "[breathy female vocals]",
        "그 목소리가 번져와",
        "얼음 위로 퍼져와",
        "이제는 두렵지 않아",
        "이 넓은 데가 내 자리야",
    ]),
    dict(name="Chorus", in_="BC", bracket="[unison male and female vocals, full band energy]",
         화자="둘", lines=[
        "돌아, 네가 그리는 선을 따라",
        "빛이 너를 따라 돌고 있어",
        "아무리 멀어도 같은 자리",
        "나는 네 원 안에 있어",
    ]),
    dict(name="Outro", in_="ABC", bracket="[unison male and female vocals, full band energy]",
         화자="둘", lines=[
        "같은 자리 같은 숨으로",
        "끝까지 너와 함께 돈다",
    ]),
]

# ── SP (style prompt) — R6: ①듀엣 선언 ②교대/합창 관계 ③남녀 각 음역 ────────
# 전부 attested 조각의 결합. 신조어 0을 목표로 했다.
SP = (
    "A male and female vocal duet in a warm, cinematic Korean ballad. "
    "Male and female vocals alternate and harmonize in a breathy, intimate delivery. "
    "The male vocal is a warm baritone delivered in a low-register, intimate, spoken-word "
    "style that transitions into melodic singing. "
    "The female vocal is a clear, airy soprano with breathy delivery and gentle vibrato. "
    "Sparse piano and soft sustained strings, gentle acoustic guitar, brushed drums entering "
    "at the chorus, building to a full unison chorus with both voices in unison and full band "
    "energy. Steady mid-tempo, emotional and restrained in the verses, open and soaring in "
    "the chorus."
)

HANGUL = re.compile(r"[가-힣]")
PAREN = re.compile(r"\s*\(spoken\)\s*$")


def syllables(line):
    """한국어 음절 = 완성형 한글 글자 수. (spoken) 표기와 구두점은 세지 않는다."""
    return len(HANGUL.findall(PAREN.sub("", line)))


def is_lyric(line):
    """브라켓 행은 가사 행이 아니다 — 행 수 집계에서 뺀다."""
    return not line.startswith("[")


def build(plan):
    secs = [s for s in SECTIONS if plan in s["in_"]]
    body, rows = [], []
    for s in secs:
        body.append(f"[{s['name']}]")
        body.append(s["bracket"])
        body.extend(s["lines"])
        body.append("")
        ly = [l for l in s["lines"] if is_lyric(l)]
        rows.append(dict(섹션=s["name"], 화자=s["화자"], 브라켓=s["bracket"],
                         행=len(ly), 음절=sum(syllables(l) for l in ly)))
    lines = [l for s in secs for l in s["lines"] if is_lyric(l)]
    return dict(
        가사="\n".join(body).strip(),
        행수=len(lines),
        음절수=sum(syllables(l) for l in lines),
        spoken행수=sum(1 for l in lines if "(spoken)" in l),
        섹션구성=rows,
        섹션수=len(secs),
    )


def main():
    out = {}
    for plan in ("A", "B", "C"):
        out[plan] = build(plan)

    # ★포함관계 검증 — 설계 주장을 코드가 확인한다(주장만 하고 안 재는 것 금지)
    la = [l for s in SECTIONS if "A" in s["in_"] for l in s["lines"] if is_lyric(l)]
    lb = [l for s in SECTIONS if "B" in s["in_"] for l in s["lines"] if is_lyric(l)]
    lc = [l for s in SECTIONS if "C" in s["in_"] for l in s["lines"] if is_lyric(l)]
    assert all(l in lb for l in la), "A ⊄ B — 포함관계 깨짐"
    assert all(l in lc for l in lb), "B ⊄ C — 포함관계 깨짐"

    # ★금지어 검증
    joined = "".join(lc)
    for ban in ("넘어져", "일어나", "일어서"):
        assert ban not in joined, f"금지 표현 검출: {ban}"

    out["_SP"] = SP
    out["_SP_글자수"] = len(SP)
    out["_포함관계_검증"] = "A ⊂ B ⊂ C 통과 (행 문자열 동일성으로 확인)"
    out["_금지어_검증"] = "「넘어져」·「일어나」·「일어서」 0건"
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
