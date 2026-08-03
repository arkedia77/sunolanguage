#!/usr/bin/env python3
"""
AWARE05 브라켓 누출 감사 — 지시 브라켓 텍스트가 실제로 가창됐는가.

배경: AWARE05는 브라켓 정본 `docs/duet_bracket_grammar_v1.md` 첫 전면 적용 배치.
      sunomusic은 metadata 레벨(SP/가사/제목 원문 무변형) 위반 0만 확인했고,
      실가창 누출은 "단정 불가"로 회신 → sunolanguage 자체 실측.
      kee 요건: 누출 0이든 검출이든 **반드시 보고**(0=정본 확증 / 검출=정본 수정 근거).

방법: demucs 보컬 스템 → faster_whisper ASR(en+ko) → 지시 브라켓 내부 어휘가
      전사 텍스트에 등장하는지 대조. 성별 판정 같은 해상도 문제 없음(순수 텍스트 매칭).

★판정 설계상 주의:
  - 섹션 브라켓([Verse 1] 등)은 대상 제외 — 원래 가창되지 않는 구조 마커.
  - 지시 브라켓 어휘는 **영어**이고 가사는 **한국어**라, 영어 단어가 전사에 뜨면
    강한 누출 신호다(한국어 곡에서 영어 악기명이 우연히 나올 확률 낮음).
  - ASR 오인식 방지: 2글자 이하 토큰·일반어(and, the, with, enters...) 제외.
"""
import glob, json, os, re, sys
from faster_whisper import WhisperModel

HERE = os.path.dirname(os.path.abspath(__file__))
SONGS = json.load(open(os.path.join(HERE, '..', 'data', 'aware', 'AWARE05_songs.json')))
STEMS = sorted(glob.glob(os.path.join(HERE, '..', 'data', 'aware', 'stems',
                                      'htdemucs', '*', 'vocals.wav')))
OUT = os.path.join(HERE, '..', 'data', 'aware', 'AWARE05_bracket_leak_audit.json')
GID0 = 30198

SECTION_RE = re.compile(r'^(Intro|Verse|Chorus|Pre-Chorus|Post-Chorus|Bridge|Outro|Hook|'
                        r'Instrumental|Interlude|Build|Breakdown|Vamp|Refrain|'
                        r'Final Chorus|Drop|Guitar Solo|Section)\b', re.I)
STOP = {'and', 'the', 'with', 'a', 'an', 'of', 'in', 'on', 'to', 'into', 'out',
        'enters', 'enter', 'drop', 'drops', 'fade', 'fades', 'up', 'down',
        'low', 'high', 'soft', 'full', 'single', 'one', 'all', 'play', 'plays'}

by_pos = {s['pos']: s for s in SONGS}

print(f"클립 {len(STEMS)}건 감사 시작", flush=True)
model = WhisperModel("medium", device="cpu", compute_type="int8")

results = []
for path in STEMS:
    name = os.path.basename(os.path.dirname(path))          # e.g. 30199_t1
    gid = int(name.split('_')[0])
    song = by_pos[gid - GID0]

    # 이 곡의 지시 브라켓 어휘 수집 (섹션 브라켓 제외)
    cues = set()
    directives = []
    for ln in song['lyrics'].split('\n'):
        ln = ln.strip()
        if not (ln.startswith('[') and ln.endswith(']')):
            continue
        body = ln[1:-1]
        if SECTION_RE.match(body):
            continue
        directives.append(body)
        for tok in re.findall(r'[a-zA-Z\-]+', body):
            t = tok.lower()
            if len(t) > 3 and t not in STOP:
                cues.add(t)

    segs, _ = model.transcribe(path, vad_filter=False, beam_size=5)
    text = ' '.join(s.text for s in segs)
    tl = text.lower()

    hits = sorted({c for c in cues if re.search(r'\b' + re.escape(c) + r'\b', tl)})

    print(f"  {name}  지시브라켓 {len(directives)}개 / 감시어 {len(cues)}개 "
          f"→ 누출 {len(hits)}건 {hits if hits else ''}", flush=True)

    results.append(dict(clip=name, gid=gid, title=song['title'],
                        n_directive_brackets=len(directives), n_cues=len(cues),
                        leak_hits=hits, leaked=bool(hits),
                        asr_text_head=text[:400]))

total_leak = sum(1 for r in results if r['leaked'])
summary = {
    "batch": "AWARE05",
    "audited_by": "sunolanguage",
    "audited_at": "2026-08-03",
    "method": "demucs 보컬 스템 → faster_whisper(medium) ASR → 지시 브라켓 어휘 텍스트 대조",
    "n_clips": len(results),
    "n_clips_with_leak": total_leak,
    "verdict": ("누출 0건 — 브라켓 정본 첫 전면 적용 확증"
                if total_leak == 0 else f"★누출 검출 {total_leak}/{len(results)} — 정본 수정 근거"),
    "★관측_여부": "관측 후 결과임(미관측 아님) — kee 요건 준수",
    "한계": "ASR 미검출이 곧 무가창은 아님(발음 뭉개짐·낮은 믹스 레벨 시 놓칠 수 있음). 검출=강한 양성, 무검출=약한 음성.",
    "clips": results,
}
json.dump(summary, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(f"\n=== 감사 결과: {total_leak}/{len(results)} 클립에서 누출 검출 ===")
print(f"저장: {OUT}")
