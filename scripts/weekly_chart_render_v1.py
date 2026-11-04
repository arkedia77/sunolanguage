#!/usr/bin/env python3
"""weekly_chart_render_v1.py — data/weekly_chart/{label}.json 두 개 → 표 md(주별 결 흐름 비교 포함).

사용: weekly_chart_render_v1.py <이번 label> [<지난 label>] > out.md
채널 분리: 멜론·스포티파이 KR 은 따로 센다(합산 0).
"""
import collections, json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ORDER = ["걸그룹 댄스", "보이그룹", "밴드·싱어송라이터", "발라드", "힙합", "트롯", "그 밖"]


def load(label):
    return json.loads((REPO / f"data/weekly_chart/{label}.json").read_text())


def share(rows, top=100):
    c = collections.Counter(r.get("gyeol", "미측정") for r in rows if r["rank"] <= top)
    return c


def table(rows):
    out = ["| 순위 | 제목 | 가수 | 멜론 장르 | 아티스트 유형 | 결 | 기획사(앨범) | 발매일 | 출처 |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        cell = lambda k: (r.get(k) or "—").replace("|", "/")
        out.append(f"| {r['rank']} | {cell('title')} | {cell('artist')} | {cell('genre')} | {cell('artist_type')} | {cell('gyeol')} | {cell('agency')} | {cell('released')} | [곡 정보]({r.get('url', '')}) |")
    return "\n".join(out)


def main():
    cur = load(sys.argv[1])
    prev = load(sys.argv[2]) if len(sys.argv) > 2 else None
    print(f"# 주간 차트 장르·결 표 — {cur['label']}\n")
    print(f"- 출처: {cur['source']} · 곡마다 멜론 공개 곡 정보·아티스트·앨범 페이지 · ⛔오디오·가사 0")
    print("- **결 = 우리 판 체계로 내가 붙인 분류**(멜론 장르 칸과 다름). 규칙(위에서부터 먼저 걸리는 것):")
    for g, why in cur["rules"]:
        print(f"  - {g}: {why}")
    print("- 소속 유형: 앨범 «기획사» 원문만 적음 — 대형/중소/인디 나누는 기준이 없어 **분류 안 함**(추측 0)\n")
    for top in (100, 50, 10):
        c = share(cur["melon"], top)
        line = " · ".join(f"{g} {c.get(g, 0)}" for g in ORDER)
        if prev:
            p = share(prev["melon"], top)
            line += "  ← 지난 표: " + " · ".join(f"{g} {p.get(g, 0)}" for g in ORDER)
        print(f"- 멜론 top{top}: {line}")
    arts = lambda rows: collections.Counter(g for g, _ in {(r.get("gyeol"), r["artist"]) for r in rows})
    ca = arts(cur["melon"])
    line = " · ".join(f"{g} {ca.get(g, 0)}" for g in ORDER)
    if prev:
        pa = arts(prev["melon"])
        line += "  ← 지난 표: " + " · ".join(f"{g} {pa.get(g, 0)}" for g in ORDER)
    print(f"- 멜론 top100 **가수 수**(한 팀 앨범 쏠림 걷어낸 자): {line}")
    top = collections.Counter(r["artist"] for r in cur["melon"]).most_common(3)
    print("- 한 가수 최다 곡: " + " · ".join(f"{a} {n}" for a, n in top))
    if prev:
        c, p = share(cur["melon"]), share(prev["melon"])
        d = sorted(((c.get(g, 0) - p.get(g, 0), g) for g in ORDER), reverse=True)
        up = [f"{g} +{x}" for x, g in d if x > 0]; down = [f"{g} {x}" for x, g in d if x < 0]
        newin = [r for r in cur["melon"] if r.get("song_id") not in {q.get("song_id") for q in prev["melon"]}]
        print(f"\n**2주 비교(멜론 top100 · {prev['label']} → {cur['label']})**: 오름 {', '.join(up) or '없음'} · 내림 {', '.join(down) or '없음'} · 새로 든 곡 {len(newin)}(" +
              ", ".join(f"{r['rank']}위 {r['gyeol']}" for r in newin[:12]) + ")")
    if cur.get("spotify_kr"):
        sp = cur["spotify_kr"]
        c = share(sp, 1000)
        print(f"\n- 스포티파이 KR 주간({cur.get('spotify_kr_week')} · kworb.net 공개 집계 · 상위 {len(sp)} · 멜론과 합산 0): " + " · ".join(f"{g} {c.get(g, 0)}" for g in ORDER + ["미측정"] if c.get(g)))
    print("\n## 멜론 top100\n")
    print(table(cur["melon"]))
    if cur.get("spotify_kr"):
        print("\n## 스포티파이 KR 주간\n")
        print(table(cur["spotify_kr"]))


if __name__ == "__main__":
    main()
