"""LPC 포먼트 추정 — ⛔절대 임계 금지. 같은 클립 안의 /a/·/i/ 와 «상대» 비교만 한다.
   도구 자체의 양성통제 = 같은 클립의 「만나」(/a/)·「시에」(/i/)가 알려진 꼴로 나오는가."""
import json, subprocess, sys, numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter

SR = 10000   # 포먼트용 — 5kHz 나이퀴스트면 F1~F4 가 들어온다
def decode(mp3):
    wav = mp3.replace(".mp3", f".{SR}.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav], check=True)
    sr, x = wavfile.read(wav)
    return sr, x.astype(np.float64) / 32768.0

def lpc(x, order):
    x = np.asarray(x, float)
    r = np.correlate(x, x, "full")[len(x) - 1:][:order + 1]
    if r[0] == 0: return None
    a, e = np.zeros(order + 1), r[0]
    a[0] = 1.0
    for i in range(1, order + 1):
        acc = r[i] + sum(a[j] * r[i - j] for j in range(1, i))
        k = -acc / e
        a_old = a.copy()
        for j in range(1, i):
            a[j] = a_old[j] + k * a_old[i - j]
        a[i] = k
        e *= (1 - k * k)
        if e <= 0: return None
    return a

def formants(seg, sr, order=12):
    if len(seg) < 200: return None
    seg = lfilter([1, -0.97], [1], seg) * np.hamming(len(seg))
    a = lpc(seg, order)
    if a is None: return None
    rts = [r for r in np.roots(a) if np.imag(r) > 0]
    out = []
    for r in rts:
        f = np.arctan2(np.imag(r), np.real(r)) * sr / (2 * np.pi)
        bw = -0.5 * (sr / (2 * np.pi)) * np.log(abs(r))
        if 150 < f < 4500 and bw < 500:
            out.append((f, bw))
    out.sort()
    return [round(f) for f, _ in out[:3]]

def measure(x, sr, t0, t1, frac=(0.15, 0.55), nframes=5):
    """해당 토막의 앞부분(=첫 음절 모음)에서 프레임 여러 개의 F1·F2 중앙값."""
    s, e = int((t0 + (t1 - t0) * frac[0]) * sr), int((t0 + (t1 - t0) * frac[1]) * sr)
    win = int(0.025 * sr)
    if e - s < win: e = s + win
    picks = np.linspace(s, max(s + 1, e - win), nframes).astype(int)
    F = [formants(x[p:p + win], sr) for p in picks]
    F = [f for f in F if f and len(f) >= 2]
    if not F: return None
    return {"F1": int(np.median([f[0] for f in F])), "F2": int(np.median([f[1] for f in F])), "n": len(F)}

if __name__ == "__main__":
    asr = json.load(open(sys.argv[2], encoding="utf-8"))
    sr, x = decode(sys.argv[1])
    tgt, refA, refI = [], [], []
    for s in asr["segments"]:
        ws = s["words"]
        for i, w in enumerate(ws):
            t = w["w"].strip()
            if t in ("날씨에", "내", "네", "의시에", "내시에", "네시에") and i == 0:
                m = measure(x, sr, w["s"], w["e"])
                if m: tgt.append((round(w["s"],2), t, m))
            if t in ("만나", "만난", "만날"):
                m = measure(x, sr, w["s"], w["e"], frac=(0.45, 0.9))   # 둘째 음절 /a/
                if m: refA.append(m)
            if t in ("시에",):
                m = measure(x, sr, w["s"], w["e"], frac=(0.1, 0.5))    # /i/
                if m: refI.append(m)
    def med(rows, k): return int(np.median([r[k] for r in rows])) if rows else None
    print(f"■ {sys.argv[1].split('/')[-1]}")
    for t0, tok, m in tgt:
        print(f"   표적 {t0:7.2f} 「{tok}」  F1={m['F1']:4}  F2={m['F2']:4}")
    print(f"   ── 표적 중앙값      F1={med([m for _,_,m in tgt],'F1')}  F2={med([m for _,_,m in tgt],'F2')}  (n={len(tgt)})")
    print(f"   ── 같은 클립 /a/(만나) F1={med(refA,'F1')}  F2={med(refA,'F2')}  (n={len(refA)})")
    print(f"   ── 같은 클립 /i/(시에) F1={med(refI,'F1')}  F2={med(refI,'F2')}  (n={len(refI)})")
