"""⛔「첫머리 치찰 없음」이 뜻을 가지려면 **내 창이 치찰을 잡을 수 있다**는 걸 먼저 보여야 한다.
   대조군 = 같은 클립에서 **ㅅ으로 시작하는 다른 낱말**(시계를·손에·서…)의 첫머리."""
import json, sys, numpy as np
sys.path.insert(0, sys.argv[3] if len(sys.argv) > 3 else ".")
from sibilant import decode, hf_curve, bursts
mp3, asrp = sys.argv[1], sys.argv[2]
asr = json.load(open(asrp, encoding="utf-8")); sr, x = decode(mp3)
ts_all, v_all = hf_curve(x, sr, 1.0, min(len(x)/sr-1, 175.0), hop=0.02)
thr = float(np.percentile(v_all, 97))
SIB_INIT = ("시", "손", "서", "쉬", "수", "사", "소", "새", "선", "숨", "씨", "사랑")
rows = []
for s_ in asr["segments"]:
    for w in s_["words"]:
        t = w["w"].strip()
        if not t or not any(t.startswith(p) for p in SIB_INIT): continue
        t0, t1 = w["s"], min(w["e"], w["s"] + 0.5)
        ts, v = hf_curve(x, sr, max(0, t0 - 0.20), t1 + 0.05)
        bs = [(round(a - t0, 3), round(b - t0, 3)) for a, b in bursts(ts, v, thr)]
        onset = [b for b in bs if b[0] < 0.18]
        rows.append((t0, t, bool(onset)))
hit = sum(1 for r in rows if r[2])
print(f"■ 대조군 {mp3.split('/')[-1]} — ㅅ-초성 낱말 {len(rows)}개 · 첫머리 치찰 검출 {hit}/{len(rows)}")
for t0, t, o in rows[:10]:
    print(f"   {t0:7.2f} 「{t}」 첫머리 치찰 {'있음' if o else '⛔없음'}")
