#!/usr/bin/env python3
"""connector_out_delta_v1.py — 발행분 ↔ 발행 «예정»분 델타를 기계가 낸다.

용도: 커넥터 OUT 재발행 고지문에 실을 수치. ★손으로 옮기는 단계를 없애는 것이 목적이다
     (09-13·09-14에 같은 칸을 기억으로 채워 두 번 틀렸다 — KANBAN ①-31).

⛔이 도구는 «발행하지 않는다». 읽기 전용(build_crosswalk는 exporter 재실행일 뿐).

대조: data/connector/out/crosswalk_latest.json (발행분)
   ↔ scripts/expression_search.py --export (현행 정본 재수출)

사용: .venv/bin/python scripts/connector_out_delta_v1.py [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_connector as CC  # noqa: E402 — 산식 단일 진실원


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", help="산출 JSON 경로")
    args = ap.parse_args()

    prev_path = CC.OUT_DIR / "crosswalk_latest.json"
    prev = json.loads(prev_path.read_text())
    cur = CC.build_crosswalk()

    pc = {c["concept_id"]: c for c in prev.get("concepts", [])}
    cc = {c["concept_id"]: c for c in cur.get("concepts", [])}
    added = sorted(set(cc) - set(pc))
    removed = sorted(set(pc) - set(cc))
    common = sorted(set(pc) & set(cc))

    up, down, to_zero = [], [], []
    for cid in common:
        a = pc[cid].get("attested_count")
        b = cc[cid].get("attested_count")
        if a == b:
            continue
        row = {"concept_id": cid, "suno_term": cc[cid].get("suno_term"), "from": a, "to": b}
        (up if (b or 0) > (a or 0) else down).append(row)
        if (b or 0) == 0 and (a or 0) > 0:
            to_zero.append(row)

    pa = {(a["alias_text"], a["kind"]) for a in prev.get("inbound_aliases", [])}
    ca = {(a["alias_text"], a["kind"]) for a in cur.get("inbound_aliases", [])}

    breaking, breaking_detail = CC.detect_breaking(cur)

    out = {
        "_provenance": f"발행분 {prev_path.name}(snapshot "
                       f"{(prev.get('_manifest') or {}).get('snapshot_id')}) ↔ 현행 정본 재수출. "
                       "산출 도구 = scripts/connector_out_delta_v1.py (읽기 전용·발행 안 함)",
        "개념": {"발행 446기준": len(pc), "현행": len(cc),
                 "신규": len(added), "소실": len(removed),
                 "신규_목록": [cc[i].get("suno_term") for i in added],
                 "소실_목록": [pc[i].get("suno_term") for i in removed]},
        "attested_count": {
            "변동_총": len(up) + len(down), "증가": len(up), "감소": len(down),
            "0으로_떨어짐": len(to_zero),
            "★0으로_떨어진_전건": [f"{r['suno_term']} {r['from']}→0" for r in to_zero],
            "감소_상위10": [f"{r['suno_term']} {r['from']}→{r['to']}"
                            for r in sorted(down, key=lambda r: (r["from"] or 0) - (r["to"] or 0),
                                            reverse=True)[:10]],
            "증가_상위5": [f"{r['suno_term']} {r['from']}→{r['to']}"
                           for r in sorted(up, key=lambda r: (r["to"] or 0) - (r["from"] or 0),
                                           reverse=True)[:5]],
        },
        "별칭": {"발행": len(pa), "현행": len(ca),
                 "신규": len(ca - pa), "소실": len(pa - ca)},
        "detect_breaking": {
            "flag": breaking, "detail": breaking_detail or None,
            "⛔한계": "detect_breaking은 «삭제·재타깃»만 본다 — attested_count 하락은 "
                      "이 플래그에 «안 잡힌다». 고지는 플래그가 아니라 위 델타 실물로 한다.",
        },
    }

    print(json.dumps(out, ensure_ascii=False, indent=2))
    if args.json:
        Path(args.json).write_text(json.dumps(out, ensure_ascii=False, indent=2))
        print(f"\n산출 → {args.json}", file=sys.stderr)


if __name__ == "__main__":
    main()
