#!/usr/bin/env python3
"""믹스 희석 검정 v1 — 「보컬에만 걸린 전화 필터가 **믹스에서도** 보이는가」

계기: N022 판정에 vocals 스템이 필요하다고 발주했더니 상대가 **Advanced Split 20cr/곡 × 12 = 240cr**을 제안.
      ★쓰기 전에 잰다 — 스템 없이 **믹스만으로** 판정선(Δtel_ratio ≥ +0.15)을 넘는지.

방법(크레딧 0): 우리가 이미 가진 같은 곡의 vocals/no_vocals 스템으로
      ⑴원본 믹스 = vocals + no_vocals
      ⑵처치 믹스 = **전화필터(vocals)** + no_vocals      ← `[Phone Vocals]`가 하는 일의 모사
      두 믹스의 tel_ratio 차이가 판정선을 넘으면 **스템 불요**.
"""
import subprocess, sys, json, tempfile, pathlib
import numpy as np
from scipy import signal

SR = 16000
TEL = "highpass=f=300,highpass=f=300,lowpass=f=3400,lowpass=f=3400"
BANDS = {"low": (20, 300), "tel": (300, 3400), "high": (3400, 8000)}
ROOT = pathlib.Path(__file__).resolve().parent.parent

def dec(path, af=None):
    o = tempfile.NamedTemporaryFile(suffix=".raw", delete=False).name
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), *(["-af", af] if af else []),
                    "-ac", "1", "-ar", str(SR), "-f", "f32le", o], check=True)
    x = np.fromfile(o, dtype=np.float32); pathlib.Path(o).unlink(missing_ok=True); return x

def met(x):
    f, p = signal.welch(x, fs=SR, nperseg=2048)
    tot = p[(f >= 20) & (f < 8000)].sum()
    m = {f"{k}_ratio": round(float(p[(f >= a) & (f < b)].sum() / tot), 4) for k, (a, b) in BANDS.items()}
    m["centroid_hz"] = round(float((f[(f >= 20) & (f < 8000)] * p[(f >= 20) & (f < 8000)]).sum() / tot), 1)
    return m

rows = []
for d in sorted((ROOT / "data/vd_duet3/stems_final/htdemucs").iterdir())[:4]:
    v, nv = d / "vocals.wav", d / "no_vocals.wav"
    if not (v.exists() and nv.exists()): continue
    V, N = dec(v), dec(nv)
    Vf = dec(v, TEL)
    n = min(len(V), len(N), len(Vf))
    base_mix, treat_mix = V[:n] + N[:n], Vf[:n] + N[:n]
    b, t = met(base_mix), met(treat_mix)
    bv, tv = met(V), met(Vf)
    rows.append({"clip": d.name[:8],
                 "★믹스_Δtel": round(t["tel_ratio"] - b["tel_ratio"], 4),
                 "보컬스템_Δtel": round(tv["tel_ratio"] - bv["tel_ratio"], 4),
                 "믹스_원본": b, "믹스_처치": t,
                 "보컬_에너지_점유": round(float((V[:n] ** 2).sum() / ((V[:n] ** 2).sum() + (N[:n] ** 2).sum())), 4)})
    r = rows[-1]
    print(f"{r['clip']}  보컬점유 {r['보컬_에너지_점유']:.3f} | ★믹스 Δtel {r['★믹스_Δtel']:+.4f} | 보컬스템 Δtel {r['보컬스템_Δtel']:+.4f}")

GATE = 0.15
mn = min(r["★믹스_Δtel"] for r in rows)
ok = mn >= GATE
print(f"\n판정선 Δtel ≥ {GATE} · 믹스 최소값 {mn:+.4f}")
print("★결론:", "**믹스만으로 충분 — 스템 불요(240cr 절약)**" if ok else
      "**믹스로는 부족 — 스템이 필요하다**  ⇒ 희석이 실재한다")
out = ROOT / "data/metatag_external/channel_mix_dilution_v1.json"
out.write_text(json.dumps({"무엇": "보컬에만 건 전화필터가 믹스에서도 보이는가", "재현": "scripts/channel_mix_dilution_v1.py",
                           "판정선": GATE, "믹스_최소_Δtel": mn, "결론": "스템 불요" if ok else "스템 필요",
                           "★한계": "VD 편성(듀엣 발라드·뮤지컬) 4클립. N022 좌표(Upbeat Psychedelic·sub-bass 두꺼움)와 보컬 점유가 다를 수 있다.",
                           "결과": rows}, ensure_ascii=False, indent=1))
print("→", out.name)
