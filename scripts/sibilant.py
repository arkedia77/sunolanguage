"""★교체한 판독기 — 포먼트가 아니라 «치찰음 수»를 센다.

왜 바꿨나: LPC 포먼트가 양성통제에서 떨어졌다(같은 클립 /a/「만나」가 F1=309Hz — 여성 가창 F0
하모닉을 잡은 값. 믹스 분리도 없다). ⇒ 그 축은 미측정으로 적고, **음고에 안 흔들리는 자**로 간다.

가르는 것: 「네시에」=/n/+/ɕ/ → 치찰 **1회** · 「사시에」=/s/+/ɕ/ → 치찰 **2회**.
★내부 양성통제 = 「시」의 치찰은 **반드시** 잡혀야 한다. 안 잡히면 그 구간은 「판별 불가」다.
"""
import json, subprocess, sys, numpy as np
from scipy.io import wavfile
SR = 32000
def decode(mp3):
    wav = mp3.replace(".mp3", f".{SR}.wav")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),wav], check=True)
    sr, x = wavfile.read(wav); return sr, x.astype(np.float64)/32768.0

def hf_curve(x, sr, t0, t1, win=0.020, hop=0.005):
    """4~8kHz 대역 비율의 시간 곡선 — 치찰음은 여기서 솟는다(피아노·기타는 저역 지배)."""
    s, e = int(t0*sr), int(t1*sr)
    n, h = int(win*sr), int(hop*sr)
    ts, vals = [], []
    w = np.hanning(n)
    for p in range(s, max(s+1, e-n), h):
        seg = x[p:p+n]*w
        S = np.abs(np.fft.rfft(seg))**2
        f = np.fft.rfftfreq(n, 1/sr)
        tot = S[(f>200)&(f<8000)].sum() + 1e-12
        hf  = S[(f>4000)&(f<8000)].sum()
        ts.append(p/sr); vals.append(hf/tot)
    return np.array(ts), np.array(vals)

def bursts(ts, v, thr):
    """문턱 넘는 연속 구간(최소 30ms)을 1회로 센다."""
    out, run = [], None
    for t, val in zip(ts, v):
        if val >= thr:
            run = (run[0], t) if run else (t, t)
        else:
            if run and run[1]-run[0] >= 0.03: out.append(run)
            run = None
    if run and run[1]-run[0] >= 0.03: out.append(run)
    return out

if __name__ == "__main__":
    mp3, asrp = sys.argv[1], sys.argv[2]
    asr = json.load(open(asrp, encoding="utf-8")); sr, x = decode(mp3)
    # 문턱 = 이 클립의 «무가창» 바닥이 아니라, 전 구간 분포의 상위에서 잡는다(클립마다 믹스가 다르다)
    ts_all, v_all = hf_curve(x, sr, 1.0, min(len(x)/sr-1, 175.0), hop=0.02)
    thr = float(np.percentile(v_all, 97))
    print(f"■ {mp3.split('/')[-1]}  (4~8kHz 비율 문턱 = 전 구간 97퍼센타일 = {thr:.3f})")
    rows = []
    for s_ in asr["segments"]:
        ws = s_["words"]
        if not ws: continue
        t = ws[0]["w"].strip()
        if t not in ("날씨에","내","네","의시에","내시에","네시에"): continue
        # 표적 토막 시작 ~ 「시에」 끝(또는 토막 끝 + 0.6s)
        t0 = ws[0]["s"]
        t1 = next((w["e"] for w in ws[1:2] if w["w"].strip() in ("시에","시","씨에")), ws[0]["e"]+0.6)
        ts, v = hf_curve(x, sr, max(0,t0-0.20), t1+0.10)
        bs = [(round(a-t0,3), round(b-t0,3)) for a,b in bursts(ts, v, thr)]
        # ★자리로 가른다: «첫머리»(=/s/ 「사」) 와 «뒤»(=/ɕ/ 「시」·내부 양성통제)
        onset = [b for b in bs if b[0] < 0.18]          # 토막 시작 ±: 「사」의 /s/ 자리
        ctrl  = [b for b in bs if b[0] >= 0.18]         # 「시」의 /ɕ/ 자리
        verdict = ("판별불가(양성통제 실패)" if not ctrl else
                   "「사시」꼴(첫머리 치찰 있음)" if onset else "「네시」꼴(첫머리 치찰 없음)")
        rows.append((t0, t, bool(onset), bool(ctrl), verdict))
        print(f"   {t0:7.2f} 「{t}」 첫머리 치찰 {'있음' if onset else '없음':4} · 뒤 치찰(양성통제) {'있음' if ctrl else '⛔없음':5} ⇒ {verdict}   {bs}")
    ok = [r for r in rows if r[3]]
    ne = sum(1 for r in ok if not r[2]); sa = sum(1 for r in ok if r[2])
    print(f"   ── 발화 {len(rows)} · 양성통제 통과 {len(ok)} ⇒ 「네시」꼴 {ne} · 「사시」꼴 {sa} · 판별불가 {len(rows)-len(ok)}")
