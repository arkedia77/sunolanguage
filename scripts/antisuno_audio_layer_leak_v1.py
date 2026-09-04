#!/usr/bin/env python3
"""
antisuno Phase 2 R1 — 오디오층 브라켓/괄호 누출 실측 (S_BP 기존자산 재사용).

사전등록: data/antisuno/phase2/prereg_audio_layer_r1_v0.json (ASR 실행 전 커밋됨 21a588f)

왜: 대장 최다 인용 값 「브라켓 누출 0/4,166」의 자는 Suno 재분석 **텍스트층**이다.
    오디오층에서도 0인지는 안 재 봤다(AWARE05 10클립만 예외이고 모집단이 다름).

설계: S_BP(05-26) — 동일 SP·동일 가사, 변수는 지시 채널 하나.
    B1 = `[breathy female vocals]` 독립행 / B2 = `(breathy female vocals)` 인라인 / CTRL = 없음
자: demucs 보컬 스템(기존) → faster_whisper medium cpu int8 (AWARE05와 같은 자)
"""
import glob, json, os, re, sys, time

STEMS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), '..',
                                      'data/s_bp/stems/htdemucs/*/vocals.wav')))
OUT = os.path.join(os.path.dirname(__file__), '..', 'data/antisuno/phase2/audio_layer_r1_results.json')

# 누출 판정 토큰 (사전등록분)
LEAK_TOKENS = ['breathy', 'female', 'vocals', 'vocal']

# 양성대조 — 12클립 공통 한국어 가사 (프로토콜 §6.0)
LYRICS = ["어둠 속에 홀로 남은 밤", "기억 속에 네가 스며들어",
          "돌아올 수 없는 그 길 위에", "나 홀로 서 있어",
          "시간이 멈춘 듯 흘러가고", "이 자리에 여전히 남아",
          "언젠가 다시 만날 수 있을까", "그날을 기다리며"]
POS_CTRL_MIN = 0.50   # ★실행 전 고정: 한국어 문자 bigram recall 0.50 미만이면 그 클립은 '판정 제외'

def bigrams(s):
    s = re.sub(r'\s+', '', s)
    return {s[i:i+2] for i in range(len(s)-1)}

GOLD = set().union(*[bigrams(l) for l in LYRICS])

def cond_of(name):
    for c in ('BP_B1', 'BP_B2', 'BP_CTRL'):
        if name.startswith(c):
            return c.replace('BP_', '')
    return '?'

def main():
    from faster_whisper import WhisperModel
    print(f"클립 {len(STEMS)}건 · faster_whisper medium(cpu/int8) 적재 중", flush=True)
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    rows = []
    for i, path in enumerate(STEMS, 1):
        clip = os.path.basename(os.path.dirname(path))
        t0 = time.time()
        segs, info = model.transcribe(path, vad_filter=False, beam_size=5)
        text = ' '.join(s.text for s in segs)
        low = text.lower()
        hits = sorted({t for t in LEAK_TOKENS if re.search(r'\b' + t + r'\b', low)})
        got = bigrams(text)
        recall = round(len(GOLD & got) / len(GOLD), 3)
        rows.append({
            "clip": clip, "condition": cond_of(clip),
            "leak_hits": hits, "leaked": bool(hits),
            "positive_control_recall": recall,
            "positive_control": "PASS" if recall >= POS_CTRL_MIN else "FAIL(판정제외)",
            "asr_lang": info.language, "asr_sec": round(time.time() - t0, 1),
            "asr_text": text.strip(),
        })
        print(f"[{i}/{len(STEMS)}] {clip:16s} {cond_of(clip):5s} "
              f"누출={hits or '없음'} 양성대조={recall} ({rows[-1]['asr_sec']}s)", flush=True)

    judged = [r for r in rows if r["positive_control"] == "PASS"]
    by = {}
    for r in judged:
        b = by.setdefault(r["condition"], {"n": 0, "leaked": 0, "clips_leaked": []})
        b["n"] += 1
        if r["leaked"]:
            b["leaked"] += 1
            b["clips_leaked"].append(r["clip"])

    out = {
        "id": "ANTISUNO_P2_R1",
        "prereg": "data/antisuno/phase2/prereg_audio_layer_r1_v0.json (commit 21a588f · ASR 실행 전)",
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "layer": "★오디오층(가창 실물) — 재분석 텍스트층 아님",
        "method": "demucs 보컬 스템(기존 산출) → faster_whisper medium cpu int8 → 영어 지시토큰 대조",
        "generation": {"신규생성": 0, "크레딧": 0},
        "n_clips": len(rows), "n_judged": len(judged),
        "by_condition": by,
        "positive_control_min": POS_CTRL_MIN,
        "leak_tokens": LEAK_TOKENS,
        "clips": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=2)
    print("\n=== 조건별 ===", flush=True)
    for c in ('B1', 'B2', 'CTRL'):
        b = by.get(c)
        if b:
            print(f"  {c:5s} 누출 {b['leaked']}/{b['n']} {b['clips_leaked']}", flush=True)
    print(f"산출 → {OUT}", flush=True)

if __name__ == '__main__':
    main()
