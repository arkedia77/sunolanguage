#!/usr/bin/env python3
"""입력 가사 브라켓 → 출력(Suno 재분석) 가사 본문 누출 전수 측정 v1.

★왜 지금 생겼나: 지시축 대장 v1·v1.1은 「우리 코퍼스는 Suno가 뱉은 것만 담아 원리상 못 잰다」를
   전제로 10건을 `impossible_by_design`에 넣고, 누출 근거를 VD 4클립·외부 1곡에서만 찾았다.
   ★그 전제가 틀렸다 — `merged_4values.json`은 **입력·출력 양쪽**을 담는다:
     leomusic_original.{sp,lyrics}(우리가 넣은 것) ↔ suno_reanalysis.{sp,lyrics}(Suno가 되돌려준 것).

자(측정 규칙, X1 방법을 전수로 확대):
  판정가능 낱말 = 입력 **브라켓 안**에 있고 입력 **가사 본문에는 없는** 영문 낱말
                  (본문과 공유하면 누출인지 원래 가사인지 못 가린다)
  누출        = 그 낱말이 **출력 가사 본문**(브라켓 제거분)에 나타남
  ★양성 대조   = 출력 가사 본문에 라틴 토큰이 실제로 나온다(=자가 라틴을 뱉을 수 있다)

★대조군: 브라켓 **낱말수**(D001 길이 조건축)와 **자기 줄/줄 안**(D006ⓐ 위치 조건축)으로 층화한다.
"""
import json, re, sys
from collections import Counter, defaultdict

SRC = 'data/reanalysis_v2/merged_4values.json'
OUT = 'data/metatag_external/bracket_leak_corpus_wide_v1.json'

BR = re.compile(r'\[([^\[\]\n]{1,200})\]')
PAREN = re.compile(r'\(([^()\n]{1,120})\)')
WORD = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")
STOP = set("""the and with for from into out over under this that then than are was were has have had
his her its our your their you not but all any one two too very more most just like now when where
who whom what which while into onto off yes yeah oh ooh ah hmm mm woo hey""".split())

def body(t):  # 브라켓·소괄호 주석 제거한 가사 본문
    return PAREN.sub(' ', BR.sub(' ', t or ''))

def own_line(lyr, span):
    """브라켓이 자기 줄에 단독으로 있는가"""
    ls = lyr.rfind('\n', 0, span[0]) + 1
    le = lyr.find('\n', span[1]);  le = len(lyr) if le < 0 else le
    return lyr[ls:le].strip() == lyr[span[0]:span[1]].strip()

def main():
    m = json.load(open(SRC))
    pairs = 0
    tot_br = 0
    stat = {'판정가능_낱말_연인원': 0, '누출_연인원': 0}
    by_len = defaultdict(lambda: {'브라켓': 0, '판정가능낱말': 0, '누출': 0, '누출브라켓': 0})
    by_pos = defaultdict(lambda: {'브라켓': 0, '판정가능낱말': 0, '누출': 0, '누출브라켓': 0})
    leaks = []
    pos_ctrl = {'출력본문_라틴토큰': 0, '출력본문_라틴보유_짝': 0}
    paren_in = Counter()
    for s in m:
        o = s.get('leomusic_original') or {}
        il = o.get('lyrics') or ''
        if not il:
            continue
        ibody_words = set(w.lower() for w in WORD.findall(body(il)))
        ibr = [(mm.group(1), mm.span(), own_line(il, mm.span())) for mm in BR.finditer(il)]
        for p in PAREN.findall(il):
            if WORD.findall(p): paren_in[p.strip().lower()] += 1
        for r in s.get('suno_reanalysis', []):
            ol = r.get('lyrics') or ''
            if not ol:
                continue
            pairs += 1
            obody = body(ol)
            olat = WORD.findall(obody)
            if olat:
                pos_ctrl['출력본문_라틴보유_짝'] += 1
                pos_ctrl['출력본문_라틴토큰'] += len(olat)
            obody_words = set(w.lower() for w in olat)
            for raw, span, own in ibr:
                tot_br += 1
                ws = [w.lower() for w in WORD.findall(raw)]
                nwords = len(ws)
                cand = [w for w in set(ws) if w not in STOP and w not in ibody_words]
                lk = [w for w in cand if w in obody_words]
                lb = f'{min(nwords,6)}어' if nwords else '0어'
                pb = '자기줄' if own else '★줄안'
                for k, d in ((lb, by_len), (pb, by_pos)):
                    d[k]['브라켓'] += 1
                    d[k]['판정가능낱말'] += len(cand)
                    d[k]['누출'] += len(lk)
                    if lk: d[k]['누출브라켓'] += 1
                stat['판정가능_낱말_연인원'] += len(cand)
                stat['누출_연인원'] += len(lk)
                if lk:
                    leaks.append({'song_id': s['song_id'], 'uuid': r.get('uuid'),
                                  '입력브라켓': raw, '낱말수': nwords, '위치': pb, '누출낱말': sorted(lk)})
    out = {
      '무엇': '입력 가사 브라켓 → 출력(Suno 재분석) 가사 본문 누출 전수 측정 v1',
      '날짜': '2026-08-27', '재현': 'scripts/bracket_leak_corpus_wide_v1.py',
      '★생성 0 · 크레딧 0 · 새 수집 0': '기존 코퍼스만',
      '★전제_정정': ('지시축 대장 v1의 「우리 코퍼스는 출력만 담는다」는 **틀렸다** — '
                     'merged_4values.json은 leomusic_original(입력 SP·가사)과 suno_reanalysis(출력 SP·가사)를 **둘 다** 담는다.'),
      '모집단': {'곡': len(m), '입력가사_보유곡': sum(1 for s in m if (s.get('leomusic_original') or {}).get('lyrics')),
                 '입력↔출력_가사짝': pairs, '입력_브라켓_연인원': tot_br},
      '★양성_대조': dict(pos_ctrl, **{'★뜻':
        '출력 가사 본문에 라틴 토큰이 실제로 나온다 ⇒ **이 자는 라틴을 뱉을 수 있다.** '
        'VD ASR(한국어 전용)의 계기 결함이 여기서는 해소된다.'}),
      '집계': stat,
      '★층화_낱말수(D001 길이 조건축)': {k: dict(v) for k, v in sorted(by_len.items())},
      '★층화_위치(D006ⓐ 위치 조건축)': {k: dict(v) for k, v in by_pos.items()},
      '누출_실물': leaks,
      '입력_소괄호_지시어(D003 조건축)': paren_in.most_common(40),
      '★이_측정이_못_하는_것': [
        '출력 가사는 **Suno가 그 음원을 듣고 쓴 것**이다. 전사가 아니라 재분석이라 오인식·요약·주석이 섞인다.',
        '「누출 0」은 「안 불렸다」가 아니라 「**이 자에 안 잡혔다**」다. 다만 양성 대조가 서 있어 VD보다 강하다.',
        '반대로 「누출 1」도 Suno의 **주석 습관**일 수 있다(브라켓 없이 `Full kit enters`를 한 줄로 쓰는 버릇). '
        '⇒ 누출 실물은 반드시 행 문면을 보고 판정할 것.',
        '입력 가사가 있는 곡만 본다(전 540곡 아님).',
      ],
    }
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print('WROTE', OUT)
    print('짝', pairs, '· 입력 브라켓', tot_br)
    print('양성대조', pos_ctrl)
    print('판정가능 낱말', stat['판정가능_낱말_연인원'], '· 누출', stat['누출_연인원'])
    print('낱말수 층화:', {k: dict(v) for k, v in sorted(by_len.items())})
    print('위치 층화:', {k: dict(v) for k, v in by_pos.items()})
    print('누출 브라켓 실물', len(leaks))

if __name__ == '__main__':
    main()
