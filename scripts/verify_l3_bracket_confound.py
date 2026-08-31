#!/usr/bin/env python3
"""leomusic3 08-31 자가정정 3건 재현기 — 「받아 적기 전에 센다」.

근거 경로: leomusic3:batches/{E3010,K3035}.json → results.stage_8.sps[].suno_lyrics
  (그쪽이 지정한 **전달층 정본**. 설계 카드가 아니다 — 08-29 bar 수 층 오류와 같은 함정 회피)

재는 것 셋:
  ⑴ 구간 라벨 브라켓 수 (그쪽 주장 60건/배치)
  ⑵ 주입 브라켓 수·낱말수 분포 (46 / 50, 최장 14 / 15어)
  ⑶ ★교락 = 브라켓이 부른 악기가 그 곡 SP에 없는가

★⑶의 자는 하나가 아니다 — 값이 자에 따라 20/20 ↔ 9/20으로 갈린다:
  ⓐ 브라켓 내용어 전체(enters·fades·breathy 포함) → SP 문체상 동사가 애초에 안 들어가
     분모가 부풀어 오른다.  ⓑ 악기 명사만·단복수 정규화 → 원 질문(「SP에 없는 **악기**」)에 맞음.
  ⇒ 정본은 ⓑ. ⓐ도 함께 산출해 「자에 따라 갈린다」를 값으로 남긴다.
"""
import json, re, sys
from pathlib import Path

BATCHES = Path("/Users/purple/leomusic3/batches")
OUT = Path(__file__).resolve().parent.parent / "data" / "l3_bracket_confound_verify.json"

SECTION = re.compile(r'^(intro|outro|verse|chorus|bridge|pre-chorus|prechorus|hook|refrain|interlude|breakdown)\b', re.I)
STRICT = set('organ glockenspiel string piano pad shaker synth guitar bass drum cello violin whistle '
             'bodhran snare kick tremolo mandolin banjo flute trumpet sax harp choir'.split())
STOP = set('a an the and or of in on to with for at by from into over under very more most this that then now'.split())


def lem(w):
    return w[:-1] if w.endswith('s') and w[:-1] in STRICT else w


def split_brackets(lyrics):
    """구간 라벨(하이픈 수식 없는 맨 라벨) / 주입 브라켓으로 분해."""
    sec, inj = [], []
    for b in re.findall(r'\[([^\[\]]+)\]', lyrics):
        (sec if SECTION.match(b.strip()) and '-' not in b else inj).append(b)
    return sec, inj


def run(name):
    sps = json.loads((BATCHES / f'{name}.json').read_text())['results']['stage_8']['sps']
    sec_n = inj_n = 0
    wc, sets, songs = {}, {}, []
    miss_a = miss_b = 0
    for s in sps:
        sec, inj = split_brackets(s['suno_lyrics'])
        sec_n += len(sec); inj_n += len(inj)
        for b in inj:
            wc[len(b.split())] = wc.get(len(b.split()), 0) + 1
        sets[s['position']] = tuple(sorted(inj))

        sp_raw = s['style_prompt'].lower()
        sp_lem = ' '.join(lem(w) for w in re.findall(r'[a-z]+', sp_raw))
        toks_a = {w for b in inj for w in re.findall(r"[a-z][a-z'\-]+", b.lower())
                  if w not in STOP and len(w) > 3}
        toks_b = {lem(w) for b in inj for w in re.findall(r'[a-z]+', b.lower())}
        toks_b = {w for w in toks_b if w in STRICT}
        absent_a = sorted(w for w in toks_a if w not in sp_raw)
        absent_b = sorted(w for w in toks_b if not re.search(r'\b' + w + r'\b', sp_lem))
        miss_a += bool(absent_a); miss_b += bool(absent_b)
        songs.append({'position': s['position'], 'brackets_section': len(sec),
                      'brackets_injected': len(inj), 'absent_instruments_strict': absent_b,
                      'absent_contentwords_n': len(absent_a)})
    uniq = len(set(sets.values()))
    return {'batch': name, 'songs_n': len(sps), 'section_labels_total': sec_n,
            'injected_total': inj_n, 'injected_wordcount_dist': dict(sorted(wc.items())),
            'injected_max_words': max(wc) if wc else 0,
            'unique_bracket_sets': uniq,
            'confound_a_contentwords': f'{miss_a}/{len(sps)}',
            'confound_b_instruments_strict': f'{miss_b}/{len(sps)}',
            'per_song': songs}


if __name__ == '__main__':
    res = [run(n) for n in (sys.argv[1:] or ['E3010', 'K3035'])]
    OUT.write_text(json.dumps({'source': 'leomusic3:batches/*.json results.stage_8.sps[].suno_lyrics',
                               'measured_at': '2026-08-31', 'batches': res}, ensure_ascii=False, indent=1))
    for r in res:
        print(f"{r['batch']}: 구간라벨 {r['section_labels_total']} · 주입 {r['injected_total']} "
              f"· 최장 {r['injected_max_words']}어 · 고유세트 {r['unique_bracket_sets']}/{r['songs_n']} "
              f"· 교락 ⓐ{r['confound_a_contentwords']} ⓑ{r['confound_b_instruments_strict']}")
    print(f'→ {OUT}')
