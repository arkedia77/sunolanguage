#!/usr/bin/env python3
"""sp_lengthening_input_axes_v1.py — Suno 가 SP 를 늘리는(length_ratio>1.0) 입력 조건 · 곡 단위.

사전등록 = docs/sp_lengthening_input_axes_prereg.md (k=8 · p<0.00625). 쓰기 = data/sp_lengthening_input_axes_v1.json 하나 · DB 쓰기 0.
"""
import collections, json, sqlite3, sys
from pathlib import Path
from scipy.stats import mannwhitneyu, fisher_exact, chi2_contingency

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from json_to_db import get_conn

ALPHA = 0.05 / 8
V = lambda p: "유의" if p < ALPHA else ("신호 후보" if p < 0.05 else "못 가림")


def main():
    db = sqlite3.connect(REPO / "sunolang.db")
    song = collections.defaultdict(lambda: {"y": False, "len": None, "aug": set()})
    for gid, aug, lr, osp in db.execute("select gid, aug_creativity, length_ratio, ordered_sp from suno_sp_emissions "
                                        "where aug_creativity in (2,3,4)"):
        s = song[gid]; s["y"] |= (lr or 0) > 1.0; s["len"] = len(osp); s["aug"].add(aug)
    cur = get_conn().cursor()
    cur.execute("select global_id, genre_group from songs where global_id = any(%s)", (list(song),))
    gg = dict(cur.fetchall())
    rows = [dict(gid=g, genre=gg.get(g), y=s["y"], len=s["len"], aug=min(s["aug"]), mixed_aug=len(s["aug"]) > 1) for g, s in song.items()]
    out = {"n_songs": len(rows), "events": sum(r["y"] for r in rows), "mixed_aug_songs": sum(r["mixed_aug"] for r in rows),
           "genre_missing": sum(r["genre"] is None for r in rows), "alpha": ALPHA}
    a = [r["len"] for r in rows if r["y"]]; b = [r["len"] for r in rows if not r["y"]]
    med = lambda v: sorted(v)[len(v) // 2]
    p = mannwhitneyu(a, b, alternative="two-sided").pvalue
    out["X1"] = {"median_event": med(a), "median_rest": med(b), "p": p, "verdict": V(p)}
    qs = sorted(r["len"] for r in rows); cuts = [qs[len(qs) * k // 4] for k in (1, 2, 3)]
    qb = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        q = sum(r["len"] >= c for c in cuts); qb[f"Q{q+1}"][0] += r["y"]; qb[f"Q{q+1}"][1] += 1
    out["X1_quartiles_desc"] = {"cuts": cuts, **{k: f"{v[0]}/{v[1]}" for k, v in sorted(qb.items())}}
    out["X3"] = {}
    E = out["events"]; N = len(rows)
    for g in sorted({r["genre"] for r in rows if r["genre"]}):
        k = sum(r["y"] for r in rows if r["genre"] == g); n = sum(r["genre"] == g for r in rows)
        p = fisher_exact([[k, n - k], [E - k, N - n - (E - k)]])[1]
        out["X3"][g] = {"events": k, "n": n, "rate": round(k / n, 4), "rest_rate": round((E - k) / (N - n), 4), "p": p, "verdict": V(p)}
    tab = [[sum(r["y"] for r in rows if r["aug"] == x), sum(not r["y"] for r in rows if r["aug"] == x)] for x in (2, 3, 4)]
    p = chi2_contingency(tab)[1]
    out["A"] = {f"aug{x}": f"{t[0]}/{t[0]+t[1]}" for x, t in zip((2, 3, 4), tab)} | {"p": p, "verdict": V(p)}
    (REPO / "data/sp_lengthening_input_axes_v1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
