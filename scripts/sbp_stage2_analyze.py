#!/usr/bin/env python3
"""
S_BP 2단계 — [] 브래킷 vs () 괄호 채널 대조 (지시 B: 보컬 질감 큐).

설계 정본: data/bracket_vs_paren_test_protocol.md (2026-05-12)
1단계 산출: data/s_bp/s_bp_stage1_results.json (2026-05-26, 21곡 생성·UUID 확보, 재분석 null)

지시 B = `breathy female vocals` 를 [Chorus] 에 삽입.
  BP_B1 = [] 브래킷 (독립 행)   / BP_B2 = () 괄호 (인라인) / BP_CTRL = 지시 없음
공통 SP는 **male tenor vocal** 고정 → 지시가 먹히면 후렴 F0가 여성역으로 상승해야 한다.

판정법(VD 8클립과 동일):
  faster_whisper ASR → 후렴 텍스트('돌아올 수 없는','나 홀로 서 있어') 매칭으로 구간 특정
  → librosa.pyin 으로 해당 구간 유성 프레임 F0 median
  → 벌스 구간 F0 와 대조 (곡 내 자기대조 = 개체차 제거)

★한계: 지시 A(악기 큐)는 기계 판정 불가(청취/Suno 재분석 필요) — 본 스크립트 대상 아님.
"""
import glob, json, os, re, sys
import numpy as np
import librosa
from faster_whisper import WhisperModel

# ★demucs 보컬 스템 사용 — 믹스 직접 분석은 ASR·pyin 공히 실패(2026-08-03 1차 시도)
AUDIO = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      '..', 'data', 's_bp', 'stems', 'htdemucs', '*', 'vocals.wav')))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'data', 's_bp', 's_bp_stage2_results.json')

CHORUS_CUES = ["돌아올", "그 길 위에", "홀로", "서 있어"]
VERSE_CUES = ["어둠", "기억", "스며", "시간이", "멈춘", "이 자리"]

# 성별 판정 기준 (VD 판정과 동일 계열)
# male tenor 기저 ~130~260Hz / female ~200~400Hz. 경계는 곡 내 상대 비교로 보정.
FEMALE_HZ = 260.0

print(f"클립 {len(AUDIO)}건 분석 시작", flush=True)
model = WhisperModel("medium", device="cpu", compute_type="int8")

results = []
for path in AUDIO:
    name = os.path.basename(os.path.dirname(path))
    code = name.rsplit('_', 2)[0]
    print(f"\n=== {name} ({code})", flush=True)

    segs, _ = model.transcribe(path, language="ko", vad_filter=False, beam_size=5)
    segs = [(s.start, s.end, s.text.strip()) for s in segs]

    y, sr = librosa.load(path, sr=22050, mono=True)
    f0, voiced, _ = librosa.pyin(y, fmin=80, fmax=600, sr=sr,
                                 frame_length=2048, hop_length=256)
    times = librosa.times_like(f0, sr=sr, hop_length=256)

    def band(t0, t1):
        m = (times >= t0) & (times <= t1) & voiced & ~np.isnan(f0)
        v = f0[m]
        return (float(np.median(v)), int(m.sum())) if v.size >= 20 else (None, int(m.sum()))

    chorus, verse = [], []
    for (t0, t1, txt) in segs:
        if any(c in txt for c in CHORUS_CUES):
            chorus.append((t0, t1, txt))
        elif any(c in txt for c in VERSE_CUES):
            verse.append((t0, t1, txt))

    ch_f0 = [band(t0, t1)[0] for t0, t1, _ in chorus]
    vs_f0 = [band(t0, t1)[0] for t0, t1, _ in verse]
    ch_f0 = [x for x in ch_f0 if x]
    vs_f0 = [x for x in vs_f0 if x]

    ch_med = float(np.median(ch_f0)) if ch_f0 else None
    vs_med = float(np.median(vs_f0)) if vs_f0 else None
    delta = (ch_med - vs_med) if (ch_med and vs_med) else None

    verdict = "판정불가"
    if ch_med:
        if ch_med >= FEMALE_HZ:
            verdict = "여성역(지시 반영 가능)"
        elif delta is not None and delta >= 40:
            verdict = "상승했으나 남성역(부분)"
        else:
            verdict = "남성역 유지(지시 미반영)"

    print(f"  ASR seg={len(segs)}  후렴매칭={len(chorus)}  벌스매칭={len(verse)}")
    print(f"  F0 후렴 median={ch_med}  벌스 median={vs_med}  Δ={delta}  → {verdict}")

    results.append(dict(clip=name, code=code,
                        n_seg=len(segs), n_chorus=len(chorus), n_verse=len(verse),
                        chorus_f0_median=ch_med, verse_f0_median=vs_med,
                        delta=delta, verdict=verdict,
                        chorus_samples=[t[2] for t in chorus[:4]]))

json.dump(results, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(f"\n저장: {OUT}")

print("\n=== 조건별 집계 ===")
from collections import defaultdict
agg = defaultdict(list)
for r in results:
    if r['chorus_f0_median']:
        agg[r['code']].append(r['chorus_f0_median'])
for code in ('BP_B1', 'BP_B2', 'BP_CTRL'):
    v = agg.get(code, [])
    if v:
        print(f"  {code:<9} n={len(v)}  후렴F0 median={np.median(v):.1f}Hz  "
              f"범위 {min(v):.1f}~{max(v):.1f}")
    else:
        print(f"  {code:<9} n=0 (판정불가)")
