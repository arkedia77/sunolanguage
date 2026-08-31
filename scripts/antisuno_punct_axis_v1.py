#!/usr/bin/env python3
"""antisuno · 구두점 축 **기저 조사** v1 (생성 0 · 크레딧 0 · 새 수집 0)

★왜: R2(E4)에서 새 조건축이 하나 나왔다 —
    「`[verse: Guitar (drop D tuning), energetic]` 에서 `),` 가 지시에서 튀어나오게 만든다」
    (Reddit·Suno·미검증). 우리 축 목록에 **없던 것**이다.

⛔★사전등록 — 재기 전에 적는다:
  ⑴ **이 측정은 「누출률 비교」가 아니다.** 기존 전수(`bracket_leak_corpus_wide_v1.json`)에서
     판정가능 낱말 5,968 중 **누출 0건**이다 ⇒ 종속변수의 분산이 0이고 **검정력이 없다.**
     그러므로 「구두점 있는 브라켓이 더 샌다」는 **이 자로는 못 잰다.** 잰다고 쓰지 않는다.
  ⑵ 이 측정이 답하는 것은 **오직 기저**다: 「우리 코퍼스에 그 조건이 **몇 건이나 발생하는가**」.
  ⑶ 판정: 구두점 보유 브라켓이 **0건이면** 이 축은 우리 코퍼스로 **검증 불가**(Phase 2 생성 필요).
     **충분히 있으면** 누출 0이 「조건이 없어서」가 아니라 **「조건이 있는데도 0」**이 되어 값이 세진다.
자: 입력 브라켓(`leomusic_original.lyrics`) 전수. `bracket_leak_corpus_wide_v1.py`와 **같은 정규식**.
"""
import json, re
from collections import Counter

SRC = 'data/reanalysis_v2/merged_4values.json'
OUT = 'data/antisuno/punct_axis_base_rate_v1.json'
BR = re.compile(r'\[([^\[\]\n]{1,200})\]')

PATS = {
    "★`),` (R2 문면 그대로)": re.compile(r'\),'),
    "중첩 소괄호 `(...)`": re.compile(r'\([^()]*\)'),
    "쉼표": re.compile(r','),
    "콜론": re.compile(r':'),
    "마침표": re.compile(r'\.'),
    "세미콜론": re.compile(r';'),
}

def main():
    m = json.load(open(SRC))
    tot = 0; songs = 0
    hits = Counter(); examples = {k: [] for k in PATS}
    for s in m:
        il = (s.get('leomusic_original') or {}).get('lyrics') or ''
        if not il:
            continue
        songs += 1
        for mm in BR.finditer(il):
            b = mm.group(1); tot += 1
            for k, p in PATS.items():
                if p.search(b):
                    hits[k] += 1
                    if len(examples[k]) < 5:
                        examples[k].append(f"[{b}]")
    res = {
        "날짜": "2026-08-31", "재현": "scripts/antisuno_punct_axis_v1.py",
        "★생성 0 · 크레딧 0 · 새 수집 0": True,
        "모집단": {"입력가사_보유곡": songs, "입력_브라켓_연인원": tot},
        "기저": {k: {"브라켓": hits[k], "비율": round(hits[k] / tot * 100, 2) if tot else None,
                    "예시": examples[k]} for k in PATS},
        "⛔이_측정이_못_하는_것": [
            "누출률 비교가 아니다 — 기존 전수에서 누출 0건이라 종속변수 분산이 0, 검정력 없음.",
            "입력 브라켓만 본다. 출력 오디오는 이 자의 사정권 밖이다(R2 §2의 사각과 같은 한계).",
            "R2 조건 문면은 E4(Reddit 개인 관측)다. 여기서 재는 건 그 조건의 **발생량**이지 효과가 아니다.",
        ],
    }
    json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f"모집단 곡 {songs} · 입력 브라켓 {tot}")
    for k in PATS:
        print(f"  {k:26} {hits[k]:5}  ({hits[k]/tot*100:5.2f}%)  {examples[k][:2]}")
    print(f"-> {OUT}")

if __name__ == '__main__':
    main()
