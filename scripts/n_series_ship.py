#!/usr/bin/env python3
"""n_series_ship.py — 설계 JSON 1건을 게이트→raw→적재→DB 실물 검증까지 한 번에.

왜 도구인가: 라인 하나가 10배치다. 같은 절차를 손으로 열 번 반복하면 자가 흔들린다
             (N021~N040 라인 교훈 — 반복 절차는 규율이 아니라 도구로 고정한다).
⛔게이트 hard fail이면 적재까지 가지 않는다. ⛔--execute 없으면 dry-run까지만.

사용: .venv/bin/python scripts/n_series_ship.py N051 30519 [--execute]
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv/bin/python")


def run(args, **kw):
    return subprocess.run([PY] + args, cwd=ROOT, text=True, capture_output=True, **kw)


def main(tag, gid_start, execute):
    design = ROOT / f"data/{tag.lower()}/{tag}_design.json"
    if not design.exists():
        sys.exit(f"⛔설계 없음: {design}")

    g = run(["scripts/n_series_gate.py", str(design)])
    print(g.stdout.rstrip())
    if g.returncode != 0:
        sys.exit(f"\n⛔{tag} 게이트 HARD FAIL — 적재 중단(설계를 고치고 다시 돌린다).")
    warns = [l.strip() for l in g.stdout.splitlines() if "미관측" in l]
    # ★게이트 출력을 «적재 전»에 박제한다. 적재 후 다시 돌리면 대조군에 자기 배치가 들어가
    #   jaccard가 1.000으로 나온다(2026-09-12 N051 통지 도구에서 실제로 찍혔다 — 발신 전 적발).
    (design.parent / f"{tag}_gate.txt").write_text(g.stdout, encoding="utf-8")

    b = run(["scripts/n_series_build_raw.py", str(design)])
    print(b.stdout.rstrip(), b.stderr.rstrip())
    raw = design.parent / f"{tag}_raw.json"

    ins = ["scripts/db_insert.py", str(raw), "--batch", tag,
           "--gid-start", str(gid_start), "--music-engine", "suno_v6"]
    if execute:
        ins.append("--execute")
    i = run(ins)
    print(i.stdout.rstrip()[-800:], i.stderr.rstrip())
    if i.returncode != 0:
        sys.exit(f"⛔{tag} 적재 실패")
    if not execute:
        print(f"\n[DRY-RUN] {tag} — --execute 로 실적재")
        return

    # ★적재는 「성공 출력」이 아니라 DB 실물로 확인한다
    sys.path.insert(0, str(ROOT / "scripts"))
    from json_to_db import get_conn
    n = len(json.loads(design.read_text(encoding="utf-8"))["songs"])
    end = gid_start + n - 1
    con = get_conn(); cur = con.cursor()
    cur.execute("SELECT count(*), count(DISTINCT global_id), min(global_id), max(global_id), "
                "count(*) FILTER (WHERE status='pending_suno'), "
                "count(*) FILTER (WHERE music_engine='suno_v6') "
                "FROM songs WHERE global_id BETWEEN %s AND %s", (gid_start, end))
    c, dc, mn, mx, pend, v6 = cur.fetchone()
    con.close()
    ok = (c == n and dc == n and mn == gid_start and mx == end and pend == n and v6 == n)
    print(f"\n■ DB 실물 검증 {tag}: {c}행(고유 {dc}) gid {mn}~{mx} · pending_suno {pend} · suno_v6 {v6}")
    print("✅ 적재 검증 PASS" if ok else "⛔검증 불일치 — 확인 필요")
    if warns:
        print(f"⚠ 장르 라벨 미관측 {len(warns)}건(발주 차단 아님 · 관측 라벨로 인용 금지)")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--execute"]
    main(a[0], int(a[1]), "--execute" in sys.argv)
