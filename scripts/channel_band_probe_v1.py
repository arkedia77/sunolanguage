#!/usr/bin/env python3
"""채널 대역 프로브 v1 — 「전화 음색」을 물리량으로 잰다.

★왜 이 지표인가: 전화 채널은 정의가 물리적이다(대역 제한). 말/노래 판정처럼 애매하지 않다.
   ITU 협대역 음성 = 약 300~3400Hz. 전화 필터가 걸리면 **저역과 고역이 함께 죽는다.**

지표 (사전 고정):
  tel_ratio  = E[300..3400] / E[20..8000]     ← 전화 대역 집중도. 필터 걸리면 ↑
  low_ratio  = E[20..300]   / E[20..8000]     ← 저역. 걸리면 ↓
  high_ratio = E[3400..8000]/ E[20..8000]     ← 고역. 걸리면 ↓
  centroid   = 스펙트럼 무게중심(Hz)

사용:
  measure  <audio...>                 지표 출력
  poscontrol <audio>                  ★양성 대조 — 같은 파일에 전화 필터를 걸어 지표가 반응하는지 확인
"""
import subprocess, sys, json, tempfile, pathlib
import numpy as np
from scipy import signal

SR = 16000
BANDS = {"low": (20, 300), "tel": (300, 3400), "high": (3400, 8000)}

def decode(path, extra_filter=None):
    af = ["-af", extra_filter] if extra_filter else []
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as f:
        out = f.name
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(path), *af,
           "-ac", "1", "-ar", str(SR), "-f", "f32le", out]
    subprocess.run(cmd, check=True)
    x = np.fromfile(out, dtype=np.float32)
    pathlib.Path(out).unlink(missing_ok=True)
    return x

def metrics(x):
    f, p = signal.welch(x, fs=SR, nperseg=2048)
    tot = p[(f >= 20) & (f < 8000)].sum()
    m = {}
    for k, (a, b) in BANDS.items():
        m[f"{k}_ratio"] = round(float(p[(f >= a) & (f < b)].sum() / tot), 4)
    m["centroid_hz"] = round(float((f[(f >= 20) & (f < 8000)] * p[(f >= 20) & (f < 8000)]).sum() / tot), 1)
    return m

TEL_FILTER = "highpass=f=300,highpass=f=300,lowpass=f=3400,lowpass=f=3400"

def main():
    if len(sys.argv) < 3: print(__doc__); return
    mode, files = sys.argv[1], sys.argv[2:]
    if mode == "measure":
        for f in files:
            print(pathlib.Path(f).name, json.dumps(metrics(decode(f)), ensure_ascii=False))
    elif mode == "poscontrol":
        rows = []
        for f in files:
            base, filt = metrics(decode(f)), metrics(decode(f, TEL_FILTER))
            d = {k: round(filt[k] - base[k], 4) for k in base}
            rows.append({"file": pathlib.Path(f).name, "원본": base, "전화필터": filt, "델타": d})
            print(f"\n{pathlib.Path(f).name}")
            for k in base:
                print(f"   {k:<12} 원본 {base[k]:>9}   전화필터 {filt[k]:>9}   Δ {d[k]:>9}")
        ok = all(r["델타"]["tel_ratio"] > 0.15 and r["델타"]["low_ratio"] < -0.05
                 and r["델타"]["high_ratio"] < -0.01 for r in rows)
        print(f"\n★양성 대조 판정: {'통과 — 지표가 전화 필터에 반응한다' if ok else '★실패 — 이 지표로는 못 잰다'}")
        print("   기준(사전 고정): Δtel_ratio > +0.15 · Δlow_ratio < −0.05 · Δhigh_ratio < −0.01")
        out = pathlib.Path(__file__).resolve().parent.parent / "data/metatag_external/channel_band_poscontrol_v1.json"
        out.write_text(json.dumps({"무엇": "채널 대역 지표 양성 대조", "재현": "scripts/channel_band_probe_v1.py poscontrol",
                                   "필터": TEL_FILTER, "판정": "통과" if ok else "실패", "결과": rows}, ensure_ascii=False, indent=1))
        print("→", out.name)

main()
