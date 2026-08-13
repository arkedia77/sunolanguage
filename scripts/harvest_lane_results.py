#!/usr/bin/env python3
"""서브에이전트 레인 산출물에서 최종 JSON을 원문 그대로 추출한다.

★왜 스크립트인가: 내가 손으로 옮겨 적으면 **내가 손실·변형 지점이 된다.**
이번 조사의 최대 교훈이 「내가 안 읽은 것을 읽은 것처럼 출처 표기했다」이므로,
수집 원문은 사람 손을 거치지 않고 파일에서 파일로 옮긴다.

사용: python3 scripts/harvest_lane_results.py <agent_id>=<lane명> [...]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "metatag_external" / "v2_lanes"
TX = Path.home() / ".claude" / "projects" / "-Users-purple-sunolanguage"

FENCE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.S)


def find_jsonl(agent_id):
    hits = list(TX.glob(f"*/subagents/agent-{agent_id}.jsonl"))
    if not hits:
        raise SystemExit(f"★산출물 없음: agent-{agent_id}.jsonl — 「없다」가 아니라 「못 찾았다」다.")
    return max(hits, key=lambda p: p.stat().st_mtime)


def last_text(path):
    """마지막 assistant 텍스트 = 에이전트의 반환값."""
    texts = []
    for line in path.open(encoding="utf-8"):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content")
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    texts.append(part["text"])
        elif isinstance(content, str):
            texts.append(content)
    if not texts:
        raise SystemExit(f"★{path.name}: assistant 텍스트 0건 — 파싱 실패이지 「빈 산출물」이 아니다.")
    return texts[-1]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for arg in sys.argv[1:]:
        agent_id, _, lane = arg.partition("=")
        raw = last_text(find_jsonl(agent_id))
        m = FENCE.search(raw)
        blob = m.group(1) if m else raw.strip()
        try:
            data = json.loads(blob)
        except json.JSONDecodeError as exc:
            dest = OUT / f"{lane}.RAW.txt"
            dest.write_text(raw, encoding="utf-8")
            print(f"⚠ {lane}: JSON 파싱 실패({exc}) → 원문 그대로 {dest.name} 에 보존")
            continue
        dest = OUT / f"{lane}.json"
        dest.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        n = len(data.get("tags", [])) + len(data.get("speaker_syntax", [])) + len(data.get("instances", []))
        na = len(data.get("not_accessed", []))
        total += n
        print(f"✅ {lane:28} 수집 {n:4}건 · ★못 읽은 출처 {na}건 → {dest.name}")
    print(f"\n합계 {total}건 (★전부 「수집된 표기」이며 반응 검증분이 아니다)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
