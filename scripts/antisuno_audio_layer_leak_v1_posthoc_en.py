#!/usr/bin/env python3
"""R1 사후(post-hoc) 감도 점검 — ★사전등록분이 아니다. 규칙을 소급해 고치지 않고 병기한다.

왜: 본 라운드 판정 결과가 전 조건 0인데, 그 0의 상당 부분이 **자의 사각**일 수 있다.
    faster_whisper가 12클립 전부 `ko`로 판정했다 ⇒ 한국어 곡 중간의 영어 지시어를
    ⑴한글로 음차하거나 ⑵아예 흘릴 수 있다. (음차 탐색은 0건으로 이미 확인)
    ⇒ **같은 오디오를 `language='en'` 강제로 한 번 더 훑어** 영어 쪽 감도를 올린다.
자 교차 = 설계원칙 「ASR 2종 교차」의 축소판(모델 동일·디코딩 조건 상이).
"""
import glob, json, os, re, time
from faster_whisper import WhisperModel

STEMS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), '..',
                                      'data/s_bp/stems/htdemucs/*/vocals.wav')))
OUT = os.path.join(os.path.dirname(__file__), '..', 'data/antisuno/phase2/audio_layer_r1_posthoc_en.json')
LEAK_TOKENS = ['breathy', 'female', 'vocals', 'vocal']

def cond_of(n):
    for c in ('BP_B1', 'BP_B2', 'BP_CTRL'):
        if n.startswith(c): return c.replace('BP_', '')
    return '?'

model = WhisperModel("medium", device="cpu", compute_type="int8")
rows = []
for i, p in enumerate(STEMS, 1):
    clip = os.path.basename(os.path.dirname(p))
    t0 = time.time()
    segs, _ = model.transcribe(p, language='en', vad_filter=False, beam_size=5)
    text = ' '.join(s.text for s in segs)
    low = text.lower()
    hits = sorted({t for t in LEAK_TOKENS if re.search(r'\b' + t + r'\b', low)})
    lat = re.findall(r'[A-Za-z]{2,}', text)
    rows.append({"clip": clip, "condition": cond_of(clip), "leak_hits": hits,
                 "leaked": bool(hits), "n_latin_tokens": len(lat),
                 "latin_head": lat[:15], "asr_sec": round(time.time()-t0, 1),
                 "asr_text": text.strip()})
    print(f"[{i}/{len(STEMS)}] {clip:16s} {cond_of(clip):5s} 누출={hits or '없음'} "
          f"라틴토큰={len(lat)} ({rows[-1]['asr_sec']}s)", flush=True)

by = {}
for r in rows:
    b = by.setdefault(r["condition"], {"n": 0, "leaked": 0, "latin_total": 0})
    b["n"] += 1; b["leaked"] += int(r["leaked"]); b["latin_total"] += r["n_latin_tokens"]
json.dump({"id": "ANTISUNO_P2_R1_POSTHOC_EN",
           "★지위": "사후 감도 점검 — 사전등록 아님. 본 판정을 대체하지 않고 병기한다.",
           "method": "동일 스템 · faster_whisper medium · ★language='en' 강제",
           "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "by_condition": by, "clips": rows}, open(OUT, 'w'), ensure_ascii=False, indent=2)
print("\n=== 조건별(en 강제) ===")
for c in ('B1', 'B2', 'CTRL'):
    if c in by: print(f"  {c:5s} 누출 {by[c]['leaked']}/{by[c]['n']} · 라틴토큰 합 {by[c]['latin_total']}")
print("산출 →", OUT)
