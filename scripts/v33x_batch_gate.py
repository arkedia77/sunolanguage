#!/usr/bin/env python3
"""v33x_batch_gate.py — V33X 배치(v3.3 신규 어휘 입력층 시행) 저작물 게이트.

발주: 오너 2026-08-18 「새로 추가된 코퍼스 셋 사용을 가지고 1배치 돌려서 핸드오프해」.
1~5번 저작 때 손으로 돌린 판정을 재현 가능하게 스크립트화(6~10 재검용).

판정 항목 (전부 hard_fail):
  G1 SP 길이 ≤ 1000자            — 오너 규칙(SP 1000자)
  G2 배정 어휘 축자 포함          — `_어휘_배정`의 각 구(句)가 SP에 그대로 있는가
  G3 명찰형 브라켓 0              — 가사의 [..] 중 섹션 태그가 아닌 것(=화자 명찰) 금지
  G4 장르 라벨이 v3.3 신규 20종   — 이 배치의 목적(신규 라벨 입력층 시행) 자체
  G5 SP 기재 BPM/키가 필드와 일치 — 적재 메타와 처방문 불일치 차단

★게이트 PASS는 곡의 품질을 보증하지 않는다. 여기서 보는 것은 「지시한 어휘가 실제로
  입력층에 들어갔는가」와 규격 위반 유무뿐이다.

사용: python3 scripts/v33x_batch_gate.py data/v33x/V33X01_tracks_1to10.json
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DELTA = Path("/Users/purple/projects/agent-comm/projects/leomusic-trot/messages/"
             "attachments/20260815_corpus_v33_crosswalk_v02/delta_v0.1_to_v0.2.json")

SP_MAX = 1000
SECTION = re.compile(
    r"^\[(Intro|Verse|Chorus|Pre-Chorus|Final Chorus|Bridge|Hook|Outro|Interlude|"
    r"Instrumental|Build|Climax|Refrain|Break|Drop|Solo)\b[^\]]*\]$", re.I)
BRACKET_LINE = re.compile(r"^\s*\[[^\]]*\]\s*$")
COUNT_SUFFIX = re.compile(r"\(\d+\)$")


def new_genre_labels() -> set[str]:
    """v3.3 신규 장르 라벨 20종 — 정본=08-15 전파문 첨부 delta(파생 DB로는 못 찾음)."""
    d = json.loads(DELTA.read_text(encoding="utf-8"))
    return set(d["사전_신규키_45"]["genre_vocabulary_map"]["added"])


def norm_key(k: str) -> str:
    k = k.replace("#", " sharp ").replace("♯", " sharp ").replace("♭", " flat ")
    return re.sub(r"\s+", " ", k).strip().lower()


def check(path: Path) -> int:
    d = json.loads(path.read_text(encoding="utf-8"))
    va = {str(k).replace("_미착수", ""): v for k, v in d["_어휘_배정"].items()}
    genres = new_genre_labels()
    fails: list[str] = []

    print(f"=== v33x_batch_gate — {path.name} ({len(d['songs'])}곡) ===")
    for s in sorted(d["songs"], key=lambda x: x["pos"]):
        pos, sp, ly = str(s["pos"]), s["sp"], s["lyrics"]
        bad: list[str] = []

        n = len(sp)
        if n > SP_MAX:
            bad.append(f"G1 SP {n}자 > {SP_MAX}")

        for raw in va.get(pos, []):
            phrase = COUNT_SUFFIX.sub("", raw).strip()
            if phrase not in sp:
                bad.append(f"G2 어휘 미포함: {phrase!r}")

        tags = [l.strip() for l in ly.splitlines() if BRACKET_LINE.match(l)]
        for t in tags:
            if not SECTION.match(t):
                bad.append(f"G3 명찰형 브라켓: {t}")

        if s["genre"] not in genres:
            bad.append(f"G4 v3.3 신규 라벨 아님: {s['genre']!r}")

        m = re.search(r"(\d+)\s*BPM", sp)
        if not m:
            bad.append("G5 SP에 BPM 기재 없음")
        elif int(m.group(1)) != int(s["bpm"]):
            bad.append(f"G5 BPM 불일치 SP={m.group(1)} field={s['bpm']}")
        if norm_key(s["key"]) not in norm_key(sp):
            bad.append(f"G5 SP에 키 미기재/불일치: {s['key']}")

        mark = "✅" if not bad else "❌"
        print(f"  {mark} #{pos:>2} {s['title']} — SP {n}자 · 태그 {len(tags)}개 · {s['genre'][:44]}")
        for b in bad:
            print(f"       └ {b}")
        fails += [f"#{pos} {b}" for b in bad]

    print(f"\n종합: {'PASS' if not fails else 'FAIL'} (위반 {len(fails)}건 / {len(d['songs'])}곡)")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(check(Path(sys.argv[1] if len(sys.argv) > 1
                        else ROOT / "data/v33x/V33X01_tracks_1to10.json")))
