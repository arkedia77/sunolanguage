#!/usr/bin/env python3
"""acelang_frame_v2.py — ACE 랭귀지 v2: v1 틀(머리 장르+BPM · 꼬리 구조)이 표본 늘어도 서나 (encore 151547 ④).
v1 셈(acelang_frame_v1.main) 그대로 · 표본만 셋으로: v1(70 = 수집 v2 40 + 시범 30) · v4(11-16 · 새 씨앗 9 × ✦5 = 45) · 합(115).
재료 v4 = repo:sunolanguage data/acelang/acelang_collect_v4_20261116.jsonl (Aside 브라우저 화면 ✦ · 생성 0)."""
import json, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import acelang_frame_v1 as F

V4 = REPO / "data/acelang/acelang_collect_v4_20261116.jsonl"


def load_v4():
    return [{"set": "v4", "seed": d["seed_id"] + " " + d["seed_text"], "n": d["press_n"], "out": d["out"]}
            for d in map(json.loads, V4.read_text().splitlines())]


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    rows = {"v4": load_v4(), "v1": F.load(), "all": F.load() + load_v4()}[which]
    F.main(rows, f"frame_v2_{which}.json")
