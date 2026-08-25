#!/usr/bin/env python3
"""N022 채널 태그 프로브 — 사전등록대로 판정한다.

주지표 = oob_removal(셀) = 1 − OOB(셀)/OOB(A0B0 바닥),  OOB = low_ratio + high_ratio
판정선 = **+0.30**
★판정 규칙(사전등록 개정1 ⒞) = **셀 간 차이가 셀 내 산포보다 크지 않으면 판정하지 않는다(보류).**
   셀 내 산포 = 같은 셀의 take1·take2 vocals 스템 두 값의 차.
"""
import subprocess, tempfile, pathlib, glob, json, re
import numpy as np
from scipy import signal

SR = 16000
ROOT = pathlib.Path(__file__).resolve().parent.parent
CELLS = ["A0B0", "A0B1", "A0B2", "A1B0", "A1B1", "A1B2"]
GATE = 0.30

def dec(p):
    o = tempfile.NamedTemporaryFile(suffix=".raw", delete=False).name
    subprocess.run(["ffmpeg","-v","error","-y","-i",str(p),"-ac","1","-ar",str(SR),"-f","f32le",o], check=True)
    x = np.fromfile(o, dtype=np.float32); pathlib.Path(o).unlink(missing_ok=True); return x

def bands(x):
    f, p = signal.welch(x, fs=SR, nperseg=2048)
    tot = p[(f>=20)&(f<8000)].sum()
    lo = p[(f>=20)&(f<300)].sum()/tot; tel = p[(f>=300)&(f<3400)].sum()/tot; hi = p[(f>=3400)&(f<8000)].sum()/tot
    return dict(low=float(lo), tel=float(tel), high=float(hi), oob=float(lo+hi))

def one(cell, tag):
    g = sorted(glob.glob(str(ROOT/f"data/n022/stems/{cell}_{tag}_*.mp3")))
    return dict(path=g[0], **bands(dec(g[0]))) if g else None

def corr(a, b):
    n = min(len(a), len(b)); return float(np.corrcoef(a[:n], b[:n])[0,1])

M = {}
for c in CELLS:
    t1, t2 = one(c, "s1"), one(c, "T2s1")
    alt = one(c, "T2alt")
    x1, x2, xa = dec(t1["path"]), dec(t2["path"]), dec(alt["path"])
    M[c] = {"take1": {k: round(v,4) for k,v in t1.items() if k!="path"},
            "take2": {k: round(v,4) for k,v in t2.items() if k!="path"},
            "★take1↔take2_파형상관": round(corr(x1,x2), 3),
            "★take2_alt_중복확인": {"파형상관": round(corr(x2,xa),3), "길이Δ초": round((len(xa)-len(x2))/SR,2)},
            "셀내_산포_|Δoob|": round(abs(t1["oob"]-t2["oob"]), 4),
            "oob_평균": round((t1["oob"]+t2["oob"])/2, 4)}

base = M["A0B0"]["oob_평균"]
noise = max(M[c]["셀내_산포_|Δoob|"] for c in CELLS)
rows = []
for c in CELLS:
    rem = 1 - M[c]["oob_평균"]/base
    eff = abs(M[c]["oob_평균"] - base)
    rows.append({"cell": c, "oob_평균": M[c]["oob_평균"], "oob_removal": round(rem,3),
                 "셀내_산포": M[c]["셀내_산포_|Δoob|"],
                 "효과>잡음?": bool(eff > M[c]["셀내_산포_|Δoob|"]) if c!="A0B0" else None,
                 "판정선(+0.30) 초과?": bool(rem >= GATE) if c!="A0B0" else None})

passed = [r for r in rows if r["cell"]!="A0B0" and r["판정선(+0.30) 초과?"]]
out = {
 "무엇": "N022 판정 — 사전등록대로",
 "재현": "scripts/n022_verdict_v1.py",
 "★셀_내_산포(잡음 추정)": {c: M[c]["셀내_산포_|Δoob|"] for c in CELLS},
 "★잡음 상한(최대 셀내 산포)": noise,
 "행": rows, "셀별_원값": M,
 "★판정": ("**대역 축소를 보인 셀 0개.** 판정선 +0.30을 넘은 셀이 없다."
          if not passed else f"판정선 초과 셀: {[r['cell'] for r in passed]}"),
}
pathlib.Path(ROOT/"data/n022/N022_verdict_v1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(f"{'cell':<6}{'t1 oob':>9}{'t2 oob':>9}{'셀내산포':>10}{'oob평균':>9}{'제거율':>9}{'효과>잡음':>10}{'t1↔t2 상관':>11}")
for c in CELLS:
    m=M[c]; r=[x for x in rows if x["cell"]==c][0]
    print(f"{c:<6}{m['take1']['oob']:>9.4f}{m['take2']['oob']:>9.4f}{m['셀내_산포_|Δoob|']:>10.4f}"
          f"{m['oob_평균']:>9.4f}{r['oob_removal']:>9.3f}{str(r['효과>잡음?']):>10}{m['★take1↔take2_파형상관']:>11.3f}")
print(f"\n★잡음 상한(최대 셀내 산포) = {noise:.4f}")
print("★take2 alt 중복 확인:", {c: M[c]["★take2_alt_중복확인"]["파형상관"] for c in CELLS})
print("\n★판정:", out["★판정"])
