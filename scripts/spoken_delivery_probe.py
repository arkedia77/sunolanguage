#!/usr/bin/env python3
"""(spoken) 구간이 말에 가까운가 노래에 가까운가 — 기계 판별.

★설계 정본 = `docs/spoken_delivery_probe_preregistration.md` (커밋 cbdbdd5, 값 보기 전 작성).
   지표·대조군·판정규칙·기각게이트·한계를 여기서 바꾸지 않는다. 어긋나면 결과에 그렇게 적는다.

실행: .venv/bin/python scripts/spoken_delivery_probe.py
"""
import json
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
VD = REPO / "data" / "vd_duet3"
OUT = REPO / "data" / "exchange" / "spoken_delivery_probe_result.json"

CLIPS = {  # 사전등록 §2
    "RM1": "70365338-0b63-4369-a5e3-83ad4de94bb0",
    "RM2": "7a028e80-b6f7-47ce-846c-cb919ef55b5f",
}
SPOKEN_LINES = [  # (spoken) 라벨 4행 — VD_REMAKE_M_v1.json /lyrics
    "여보, 우리 처음 만나던 날 기억해요?",
    "그럼요, 그날도 꼭 오늘 같았죠",
    "그때 그 마음, 지금도 같아요?",
    "아니요, 그때보다 더 커졌어요",
]
SR = 16000
HOP = 160          # 10ms
WIN = 1024
FMIN, FMAX = 70.0, 700.0
SUSTAIN_MS = 120   # §3 ⓐ
SUSTAIN_TOL = 0.5  # 반음


# ---------- 오디오 ----------
def load(path, start=None, end=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path)]
    if start is not None:
        cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", str(path)]
        if end is not None:
            cmd += ["-t", str(end - start)]
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    subprocess.run(cmd + ["-ac", "1", "-ar", str(SR), "-y", tmp], check=True)
    with wave.open(tmp) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    Path(tmp).unlink()
    return x


# ---------- F0 (YIN 계열 자기상관) ----------
def f0_track(x):
    """10ms 프레임 F0. 무성/불확실은 NaN."""
    tau_min, tau_max = int(SR / FMAX), int(SR / FMIN)
    out = []
    for i in range(0, max(0, len(x) - WIN), HOP):
        fr = x[i:i + WIN]
        if np.sqrt(np.mean(fr ** 2)) < 1e-3:      # 무음
            out.append(np.nan)
            continue
        fr = fr - fr.mean()
        # 차이함수 d(tau)
        cum = np.cumsum(fr ** 2)
        d = np.empty(tau_max + 1)
        for tau in range(tau_min, tau_max + 1):
            a = fr[:WIN - tau]
            b = fr[tau:WIN]
            d[tau] = np.sum((a - b) ** 2)
        d[:tau_min] = np.inf
        # 누적평균 정규화
        dn = np.full_like(d, np.inf)
        run = 0.0
        for tau in range(tau_min, tau_max + 1):
            run += d[tau]
            dn[tau] = d[tau] * (tau - tau_min + 1) / run if run > 0 else np.inf
        tau = int(np.argmin(dn))
        if dn[tau] > 0.35 or not np.isfinite(dn[tau]):   # 유성 판정 문턱
            out.append(np.nan)
            continue
        # 포물선 보간
        if tau_min < tau < tau_max:
            a, b, c = d[tau - 1], d[tau], d[tau + 1]
            den = a - 2 * b + c
            if den != 0:
                tau = tau + 0.5 * (a - c) / den
        out.append(SR / tau)
    return np.array(out, dtype=float)


# ---------- 지표 (사전등록 §3) ----------
def metrics(f0):
    n = len(f0)
    if n == 0:
        return None
    voiced = ~np.isnan(f0)
    nv = int(voiced.sum())
    if nv < 20:
        return None
    semi = 12 * np.log2(np.where(voiced, f0, np.nan) / 55.0)
    need = SUSTAIN_MS // 10
    # ⓐ sustain: 유성 연속 구간 안에서 ±0.5반음 이내로 need 프레임 이상 유지되는 프레임 수
    sustain = np.zeros(n, dtype=bool)
    i = 0
    while i < n:
        if not voiced[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and voiced[j + 1]:
            j += 1
        seg = semi[i:j + 1]
        k = 0
        while k < len(seg):
            m = k + 1
            while m < len(seg) and abs(seg[m] - seg[k]) <= SUSTAIN_TOL:
                m += 1
            if m - k >= need:
                sustain[i + k:i + m] = True
            k = m if m > k else k + 1
        i = j + 1
    # ⓑ 인접 유성 프레임 간 |Δ반음| 중앙값
    d = []
    for i in range(n - 1):
        if voiced[i] and voiced[i + 1]:
            d.append(abs(semi[i + 1] - semi[i]))
    return {
        "sustain_ratio": round(float(sustain.sum() / nv), 4),
        "delta_semitone_median": round(float(np.median(d)) if d else float("nan"), 4),
        "voiced_ratio": round(float(nv / n), 4),
        "voiced_frames": nv,
    }


def agg(chunks):
    """여러 구간을 프레임 단위로 이어붙여 하나로 잰다(구간별 길이 가중)."""
    f0 = np.concatenate(chunks) if chunks else np.array([])
    return metrics(f0)


def line_match(asr_text, lyric_texts):
    """가사 (spoken) 행 ↔ ASR 세그먼트 대응.

    ★1차판 버그(08-11 자기적발): 앞 12자 부분문자열로 맞췄더니 ASR이 「그럼요」를
      「그러면」으로 들은 1행을 **놓쳤다.** 놓친 행을 「없음」으로 접으면 이 스크립트가
      바로 그 오류형(「없음」과 「안 봄」 혼동)을 재현한다. → 문자 단위 유사도로 교체.
    ※판정 규칙(§5)은 안 건드린다. 이건 **구간 라벨링 수정**이지 자를 고치는 게 아니다.
    """
    a = "".join(ch for ch in asr_text if ch.isalnum())
    best = 0.0
    for lt in lyric_texts:
        b = "".join(ch for ch in lt if ch.isalnum())
        if not a or not b:
            continue
        # 문자 다중집합 겹침 비율 (짧은 쪽 기준)
        from collections import Counter
        ca, cb = Counter(a), Counter(b)
        inter = sum((ca & cb).values())
        best = max(best, inter / min(len(a), len(b)))
    return best >= 0.7


# ---------- 대조군 B: TTS ----------
def tts_control():
    """말 극(B). ★중복 제거 — 1차판에서 Yuna/Suhyun이 **소수점 4자리까지 동일**했다.
    같은 음성으로 폴백된 것을 두 표본으로 세면 B극 평균이 그쪽으로 기운다."""
    outs, seen = [], set()
    for voice in ("Yuna", "Suhyun", "Eddy (한국어(한국))", "Grandma (한국어(한국))", "Flo (한국어(한국))"):
        try:
            with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
                p = f.name
            subprocess.run(["say", "-v", voice, "-o", p, " ".join(SPOKEN_LINES)],
                           check=True, capture_output=True)
            x = load(p)
            Path(p).unlink()
        except subprocess.CalledProcessError:
            continue
        sig = (len(x), round(float(np.sum(x ** 2)), 6))
        if sig in seen:
            print(f"  [B극] {voice} = 앞 음성과 동일 오디오 → 중복 제거")
            continue
        seen.add(sig)
        outs.append((voice, f0_track(x)))
    return outs


def main():
    asr = json.loads((VD / "VD_final_asr.json").read_text())
    norm = lambda s: "".join(ch for ch in s if ch.isalnum())
    spoken_keys = [norm(s) for s in SPOKEN_LINES]

    result = {
        "사전등록": "docs/spoken_delivery_probe_preregistration.md (커밋 cbdbdd5 — 값 보기 전)",
        "대상": "RM1·RM2 2클립 (v2.3 3곡은 (spoken) 0건 — 대상 아님)",
        "클립": {},
    }

    # --- 말 극(B) ---
    tts = tts_control()
    b_metrics = [(v, metrics(f)) for v, f in tts]
    b_metrics = [(v, m) for v, m in b_metrics if m]
    result["말극_B_TTS"] = {v: m for v, m in b_metrics}
    B = {k: float(np.mean([m[k] for _, m in b_metrics]))
         for k in ("sustain_ratio", "delta_semitone_median", "voiced_ratio")} if b_metrics else None
    result["말극_B_평균"] = {k: round(v, 4) for k, v in B.items()} if B else None

    for label, uuid in CLIPS.items():
        stem = VD / "stems_final" / "htdemucs" / uuid / "vocals.wav"
        if not stem.exists():
            result["클립"][label] = {"오류": f"스템 없음 {stem}"}
            continue
        segs = asr[label]
        sp_chunks, sung_chunks, sp_detail, unmeasurable = [], [], [], []
        for s in segs:
            f0 = f0_track(load(stem, s["s"], s["e"]))
            if line_match(s["t"], SPOKEN_LINES):
                m = metrics(f0)
                row = {"구간": f'{s["s"]}~{s["e"]}s', "행": s["t"]}
                if m:
                    sp_chunks.append(f0)
                    row.update(m)
                else:
                    # ★유성 프레임 <20 = 측정 불가. 버리지 않고 따로 올린다(집계엔 안 넣음).
                    row["측정"] = "★불가 — 유성 프레임 20 미만(스템이 거의 비어 있음)"
                    unmeasurable.append(row)
                sp_detail.append(row)
            else:
                sung_chunks.append(f0)
        A = agg(sung_chunks)        # 노래 극
        X = agg(sp_chunks)          # 대상
        entry = {"uuid": uuid, "노래극_A": A, "spoken_대상_X": X, "spoken_행별": sp_detail,
                 "spoken_집계행수": len(sp_chunks), "★측정불가_구간": unmeasurable,
                 "가창_구간수": len(sung_chunks)}

        KEYS = ("sustain_ratio", "delta_semitone_median", "voiced_ratio")
        # --- 기각 게이트 (사전등록 §6 — 주지표 ⓐ에만 걸도록 쓰여 있었다) ---
        if A and B:
            sep = abs(A["sustain_ratio"] - B["sustain_ratio"])
            entry["게이트_주지표_분리도"] = round(sep, 4)
            entry["게이트"] = "통과" if sep >= 0.15 else "★기각 — 지표가 말/노래를 구분 못 함. 대상 판정 안 함"
            # ★지표별 분리도도 같이 낸다 — 분리 안 된 지표의 z는 0 나누기라 의미가 없다.
            entry["지표별_양극분리도"] = {k: round(abs(A[k] - B[k]), 4) for k in KEYS}
        # --- 판정 (§5 — 규칙 그대로) ---
        if A and B and X and entry.get("게이트") == "통과":
            z, votes = {}, []
            for k in KEYS:
                den = A[k] - B[k]
                zi = (X[k] - B[k]) / den if den else float("nan")
                z[k] = round(float(zi), 3)
                votes.append("말하기" if zi <= 0.35 else "노래" if zi >= 0.65 else "보류")
            entry["z_정규화위치"] = z
            entry["지표별_판정"] = dict(zip(KEYS, votes))
            def tally(vs):
                for v in ("말하기", "노래"):
                    if vs.count(v) >= 2:
                        return f"{v} 쪽 ({vs.count(v)}표)"
                return "★보류 — 2표 이상 한 방향으로 안 모임"
            entry["판정_규칙그대로"] = tally(votes)
            # ★사후 확장(post-hoc) — 사전등록 §6은 ⓐ에만 게이트를 걸었으나,
            #   같은 문서의 원칙은 「분리 안 되는 자로 잰 값을 결과로 내지 않는다」다.
            #   그 원칙을 지표별로 확장하면 어떻게 되는지 **병기**한다. 어느 쪽도 안 지운다.
            #   분리 기준(상대) = |A−B| 가 두 극 평균 크기의 30% 이상.
            live = [k for k in KEYS
                    if abs(A[k] - B[k]) >= 0.30 * (abs(A[k]) + abs(B[k])) / 2]
            entry["★사후_분리지표만"] = live
            entry["★탈락지표"] = {k: f"|A−B|={abs(A[k]-B[k]):.4f} — 두 극이 사실상 겹침"
                                  for k in KEYS if k not in live}
            entry["판정_분리지표만_post_hoc"] = tally([votes[KEYS.index(k)] for k in live]) if live else "지표 0개 — 판정 불가"
        result["클립"][label] = entry

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
