#!/usr/bin/env python3
"""gender_break_song_axes_v1.py — 성별어 깨짐 곡 단위 원인축(사전등록 = docs/gender_break_song_axes_prereg.md).

분모 = data/v6_obs/v6_input_layer_running.json 의 성별어 항목(N021~N080 · 610곡) × PG songs.
Y1 = 역전·소실 / Y2 = 유지 아님. X1 SP 길이 · X2 발주 성별어 첫 위치 비율 · X3 genre_group.
판정선 = p < 0.05/8 (U 2 + Fisher 6). 출력 = data/gender_break_song_axes_v1.json (쓰기 = 이 파일 하나 · DB 쓰기 0).
"""
import collections, json, re, sys
from pathlib import Path
from scipy.stats import mannwhitneyu, fisher_exact, chi2_contingency

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from json_to_db import get_conn

ALPHA = 0.05 / 8


def main():
    d = json.loads((REPO / "data/v6_obs/v6_input_layer_running.json").read_text())
    ent = {}
    for bn, b in d["batches"].items():
        for e in b.get("성별어", []):
            ent[e["gid"]] = dict(e, batch=bn, bucket=b.get("대조본_칸"))
    cur = get_conn().cursor()
    cur.execute("select global_id, style_prompt, genre_group from songs where global_id = any(%s)", (list(ent),))
    rows = []
    for gid, sp, gg in cur.fetchall():
        e = ent[gid]
        low = sp.lower()
        pos = [m.start() for t in e["발주"] for m in [re.search(rf"(?<![a-z\-]){re.escape(t.lower())}(?![a-z])", low)] if m]
        rows.append({"gid": gid, "batch": e["batch"], "bucket": e["bucket"], "판정": e["판정"],
                     "y1": e["판정"] in ("역전", "소실"), "y2": e["판정"] != "유지",
                     "x1": len(sp), "x2": (min(pos) / len(sp)) if pos else None, "x3": gg})
    out = {"n": len(rows), "alpha": ALPHA, "x2_missing": sum(r["x2"] is None for r in rows), "tests": {}}
    for y in ("y1", "y2"):
        T = out["tests"][y] = {"events": sum(r[y] for r in rows)}
        for x in ("x1", "x2"):
            a = [r[x] for r in rows if r[y] and r[x] is not None]
            b = [r[x] for r in rows if not r[y] and r[x] is not None]
            p = mannwhitneyu(a, b, alternative="two-sided").pvalue
            med = lambda v: sorted(v)[len(v) // 2]
            T[x] = {"n_event": len(a), "n_rest": len(b), "median_event": round(med(a), 3), "median_rest": round(med(b), 3),
                    "p": p, "verdict": "유의" if p < ALPHA else ("신호 후보" if p < 0.05 else "못 가림")}
        groups = sorted({r["x3"] for r in rows})
        tab = [[sum(r[y] for r in rows if r["x3"] == g), sum(not r[y] for r in rows if r["x3"] == g)] for g in groups]
        T["x3_chi2_p"] = chi2_contingency(tab)[1]
        T["x3"] = {}
        for g, (k, m) in zip(groups, tab):
            rk = T["events"] - k; rm = len(rows) - T["events"] - m
            p = fisher_exact([[k, m], [rk, rm]])[1]
            T["x3"][g] = {"events": k, "n": k + m, "rate": round(k / (k + m), 4), "rest_rate": round(rk / (rk + rm), 4),
                          "p": p, "verdict": "유의" if p < ALPHA else ("신호 후보" if p < 0.05 else "못 가림")}
        bk = collections.defaultdict(lambda: [0, 0])
        for r in rows:
            bk[r["bucket"]][0] += r[y]; bk[r["bucket"]][1] += 1
        T["bucket_desc"] = {k: f"{v[0]}/{v[1]}" for k, v in sorted(bk.items(), key=lambda kv: str(kv[0]))}
    (REPO / "data/gender_break_song_axes_v1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
