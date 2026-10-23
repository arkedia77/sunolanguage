#!/usr/bin/env python3
"""sp_length_attractor_confirm_v1.py — Suno 재작성 길이 수렴 독립 확인(사전등록 docs/sp_length_attractor_confirm_prereg.md).

쓰기 = data/sp_length_attractor_confirm_v1.json 하나 · DB 쓰기 0.
"""
import collections, json, sqlite3, statistics as st, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from json_to_db import get_conn

NON_GEN = ("stem", "edit_upsample", "edit_infill", "upload")


def main():
    used = [g for g, in sqlite3.connect(REPO / "sunolang.db").execute("select distinct gid from suno_sp_emissions")]
    cur = get_conn().cursor()
    cur.execute("""select aug_creativity_api, sp_input_len_at_render, char_length(sp_suno) from suno_clip_style
                   where model_name='v6' and aug_creativity_api in (2,3,4) and sp_suno is not null
                   and coalesce(gen_method,'') not in %s and not (global_id = any(%s))""", (NON_GEN, used))
    X = cur.fetchall()
    cur.execute("""select char_length(s.sp_suno)::float / char_length(g.style_prompt) from suno_clip_style s
                   join songs g on g.global_id=s.global_id where s.model_name='chirp-hawk' and s.aug_creativity_api=0
                   and s.sp_suno is not null and g.style_prompt is not null and coalesce(s.gen_method,'') not in %s""", (NON_GEN,))
    neg = [r for r, in cur.fetchall()]
    out = {"n_independent": len(X), "n_negative_control": len(neg)}
    out["C0"] = {"median_ratio": round(st.median(neg), 4), "pass": 0.85 <= st.median(neg) <= 1.05}
    ins = sorted(i for _, i, _ in X); cuts = [ins[len(ins) * k // 4] for k in (1, 2, 3)]
    q = collections.defaultdict(list)
    for a, i, o in X:
        q[sum(i >= c for c in cuts) + 1].append((i, o))
    out["C1"] = {"cuts": cuts, "quartiles": {f"Q{k}": {"n": len(v), "input_median": st.median(i for i, _ in v),
                                                        "output_median": st.median(o for _, o in v)} for k, v in sorted(q.items())}}
    out["C1"]["pass"] = all(280 <= d["output_median"] <= 380 for d in out["C1"]["quartiles"].values())
    out["C1_by_aug_desc"] = {f"aug{a}": {"n": sum(1 for x in X if x[0] == a), "input_median": st.median(i for aa, i, _ in X if aa == a),
                                         "output_median": st.median(o for aa, _, o in X if aa == a)} for a in (2, 3, 4)}
    b = collections.defaultdict(lambda: [0, 0])
    for _, i, o in X:
        b[i // 20 * 20][0] += o > i; b[i // 20 * 20][1] += 1
    bins = {k: (v[0], v[1], round(v[0] / v[1], 3)) for k, v in sorted(b.items())}
    out["C2_bins"] = {str(k): f"{u}/{n}={r}" for k, (u, n, r) in bins.items()}
    cross = next((k for k, (u, n, r) in bins.items() if r < 0.5), None)
    out["C2"] = {"first_bin_below_half": cross, "pass": cross is not None and 280 <= cross <= 370}
    c = out["C1"]["pass"] + out["C2"]["pass"]
    out["verdict"] = "판정 보류(C0 실패)" if not out["C0"]["pass"] else ("확인" if c == 2 else "부분" if c == 1 else "기각")
    (REPO / "data/sp_length_attractor_confirm_v1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
