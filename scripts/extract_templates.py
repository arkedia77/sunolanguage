#!/usr/bin/env python3
"""
R1 — sentence → 슬롯별 구문 템플릿 추출 (v3.1)

책 3장 "슬롯별 구문 템플릿"의 직접 자료.
placeholder 추상화: <INSTR>, <DRUM>, <VOCAL>, <BPM>, <KEY>, <TIME>,
                    <MOD>, <EFFECT>, <CHORD>, <NUM>

입력:  data/reanalysis_v2/sp_entities_v3.json
       data/reanalysis_v2/bracket_entities_v3.json
출력:  data/reanalysis_v2/templates_v3.json
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IN_DIR = REPO / "data" / "reanalysis_v2"
OUT = IN_DIR / "templates_v3.json"

# 파이프라인 재사용: 엔티티/수식어 사전
sys.path.insert(0, str(REPO / "scripts"))
from parse_slot_entities_v3 import (  # noqa: E402
    INSTRUMENT_ENTITIES, DRUM_ENTITIES, VOCAL_ENTITIES, ALL_MODIFIERS,
)

EFFECT_WORDS = [
    "plate reverb", "room reverb", "hall reverb", "spring reverb",
    "short reverb", "long reverb", "light chorus", "subtle chorus",
    "slap-back delay", "ping-pong delay",
    "chorus", "reverb", "delay", "distortion", "overdrive",
    "phaser", "flanger", "compression", "auto-tune", "echo",
]
CHORD_WORDS = [
    "arpeggiated chords", "sustained chords", "power chords",
    "jazz chords", "block chords", "open chords",
    "jazz voicings", "voicings", "chord progression",
    "seventh chords", "ninth chords",
]

# ─────────────────────────────────────────
# 추상화: sentence → template
# ─────────────────────────────────────────
# sentinel: 후속 regex에 매칭되지 않는 고정 토큰. 마지막에 <PLACEHOLDER>로 변환.
SENTINEL = "\x00{}\x01"
_PH_INSTR  = SENTINEL.format("INSTR")
_PH_DRUM   = SENTINEL.format("DRUM")
_PH_VOCAL  = SENTINEL.format("VOCAL")
_PH_BPM    = SENTINEL.format("BPM")
_PH_KEY    = SENTINEL.format("KEY")
_PH_TIME   = SENTINEL.format("TIME")
_PH_MOD    = SENTINEL.format("MOD")
_PH_EFFECT = SENTINEL.format("EFFECT")
_PH_CHORD  = SENTINEL.format("CHORD")
_PH_NUM    = SENTINEL.format("NUM")


def _collapse_repeats(s: str, ph: str) -> str:
    """`<X> <X>` → `<X>` (placeholder 인접 중복 축약)."""
    pat = re.compile(rf"{re.escape(ph)}(?:\s+{re.escape(ph)})+")
    return pat.sub(ph, s)


def abstract_sentence(sent: str) -> str:
    """sentence의 엔티티/수식어/숫자를 placeholder로 치환."""
    s = sent.strip()

    # 1) 숫자 단위 (BPM/TIME/KEY)
    s = re.sub(r"\b\d+\.?\d*\s*bpm\b", _PH_BPM, s, flags=re.I)
    s = re.sub(r"\b(\d+/\d+)\s*time\b", f"{_PH_TIME} time", s, flags=re.I)
    s = re.sub(r"\b\d+/\d+\b", _PH_TIME, s)
    s = re.sub(
        r"\b(in\s+the\s+key\s+of\s+)[a-g][#b]?\s*(?:major|minor)?\b",
        f"in the key of {_PH_KEY}", s, flags=re.I,
    )
    s = re.sub(
        r"\bkey\s+(?:of\s+|is\s+|:\s*)?[a-g][#b]?\s*(?:major|minor)\b",
        f"key of {_PH_KEY}", s, flags=re.I,
    )
    s = re.sub(r"\b[a-g][#b]?\s+(major|minor)\b", rf"{_PH_KEY} \1", s, flags=re.I)

    # 2) 이펙트 (긴 것부터)
    for eff in EFFECT_WORDS:
        s = re.sub(rf"\b{re.escape(eff)}\b", _PH_EFFECT, s, flags=re.I)

    # 3) 코드/보이싱
    for ch in CHORD_WORDS:
        s = re.sub(rf"\b{re.escape(ch)}\b", _PH_CHORD, s, flags=re.I)

    # 4) 악기/드럼/보컬 (사전 순서 유지 — 긴 패턴이 앞)
    for _name, pat in INSTRUMENT_ENTITIES:
        s = pat.sub(_PH_INSTR, s)
    for _name, pat in DRUM_ENTITIES:
        s = pat.sub(_PH_DRUM, s)
    for _name, pat in VOCAL_ENTITIES:
        s = pat.sub(_PH_VOCAL, s)

    # 5) 수식어 (sentinel은 \x00/\x01 포함이라 \w 매칭 안 됨)
    def _mod_sub(m):
        w = m.group(0).lower()
        return _PH_MOD if w in ALL_MODIFIERS else m.group(0)
    s = re.sub(r"\b[a-zA-Z][a-zA-Z\-]+\b", _mod_sub, s)

    # 6) 잔존 숫자
    s = re.sub(r"\b\d+\b", _PH_NUM, s)

    # 7) sentinel → <TAG>
    for ph, tag in (
        (_PH_INSTR, "<INSTR>"), (_PH_DRUM, "<DRUM>"), (_PH_VOCAL, "<VOCAL>"),
        (_PH_BPM, "<BPM>"), (_PH_KEY, "<KEY>"), (_PH_TIME, "<TIME>"),
        (_PH_MOD, "<MOD>"), (_PH_EFFECT, "<EFFECT>"),
        (_PH_CHORD, "<CHORD>"), (_PH_NUM, "<NUM>"),
    ):
        # 먼저 `ph ph` 인접 중복 축약 → 템플릿 가독성 확보
        s = _collapse_repeats(s, ph)
        s = s.replace(ph, tag)

    s = re.sub(r"\s+", " ", s).strip()
    return s


# ─────────────────────────────────────────
# 실행
# ─────────────────────────────────────────
def main():
    sp = json.loads((IN_DIR / "sp_entities_v3.json").read_text())
    br = json.loads((IN_DIR / "bracket_entities_v3.json").read_text())

    sp_templates = defaultdict(Counter)      # slot → template → count
    sp_examples = defaultdict(lambda: defaultdict(list))  # slot → template → [sentence]
    br_templates = defaultdict(Counter)
    br_examples = defaultdict(lambda: defaultdict(list))

    seen_sp = set()  # (slot, sentence) 중복 제거 — 한 sentence가 여러 슬롯에 분기하는 건 유지
    for e in sp:
        slot = e.get("slot", "unknown")
        sent = e.get("sentence", "")
        if not sent:
            continue
        key = (slot, sent)
        if key in seen_sp:
            continue
        seen_sp.add(key)
        tpl = abstract_sentence(sent)
        sp_templates[slot][tpl] += 1
        if len(sp_examples[slot][tpl]) < 3:
            sp_examples[slot][tpl].append(sent)

    seen_br = set()
    for e in br:
        slot = e.get("slot", "unknown")
        bracket = e.get("bracket", "")
        if not bracket:
            continue
        key = (slot, bracket)
        if key in seen_br:
            continue
        seen_br.add(key)
        tpl = abstract_sentence(bracket)
        br_templates[slot][tpl] += 1
        if len(br_examples[slot][tpl]) < 3:
            br_examples[slot][tpl].append(bracket)

    # 출력: 슬롯별 상위 50 템플릿 + 샘플 3개
    out = {"sp": {}, "lyrics_brackets": {}, "meta": {}}

    for slot, tpls in sp_templates.items():
        out["sp"][slot] = {
            "unique_templates": len(tpls),
            "total_occurrences": sum(tpls.values()),
            "top": [
                {
                    "template": t,
                    "count": c,
                    "examples": sp_examples[slot][t],
                }
                for t, c in tpls.most_common(50)
            ],
        }

    for slot, tpls in br_templates.items():
        out["lyrics_brackets"][slot] = {
            "unique_templates": len(tpls),
            "total_occurrences": sum(tpls.values()),
            "top": [
                {
                    "template": t,
                    "count": c,
                    "examples": br_examples[slot][t],
                }
                for t, c in tpls.most_common(50)
            ],
        }

    out["meta"] = {
        "placeholders": [
            "<INSTR>", "<DRUM>", "<VOCAL>",
            "<BPM>", "<KEY>", "<TIME>",
            "<MOD>", "<EFFECT>", "<CHORD>", "<NUM>",
        ],
        "source_sp_entities": len(sp),
        "source_bracket_entities": len(br),
        "sp_unique_sentence_slot_pairs": len(seen_sp),
        "br_unique_bracket_slot_pairs": len(seen_br),
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    # 콘솔 리포트
    print(f"✔ templates_v3.json 작성: {OUT}")
    print()
    print("=== SP 슬롯별 템플릿 요약 ===")
    for slot in sorted(sp_templates.keys(), key=lambda s: -sum(sp_templates[s].values())):
        uniq = len(sp_templates[slot])
        total = sum(sp_templates[slot].values())
        ratio = uniq / total if total else 0
        print(f"  {slot:22s} unique={uniq:4d}  total={total:4d}  uniq/total={ratio:.2f}")
    print()
    print("=== SP 슬롯별 상위 템플릿 3개 ===")
    for slot, tpls in sorted(
        sp_templates.items(), key=lambda x: -sum(x[1].values())
    ):
        print(f"\n  [{slot}]")
        for t, c in tpls.most_common(3):
            print(f"    {c:3d}x  {t[:130]}")


if __name__ == "__main__":
    main()
