#!/usr/bin/env python3
"""emission_measure.py — 수노 산출 SP층(`suno_sp_emissions`)을 «한 번에» 잰다.

⛔이 도구가 지키는 경계:
  · **값을 상수로 안 박는다** — 매번 DB·사전에서 다시 잰다(자 두 벌 방지).
  · **판정 낱말을 안 쓴다** — 사전등록 선(검정력 80%) 도달 전에는 수만 적는다.
  · 버킷은 클립에 적힌 **실제값**(`aug_creativity`).
  · ★**V0은 대조군이 «못 된다»**: 수노가 Variety 0에서 우리 SP를 그대로 돌려주므로
    V0의 신규 어휘는 **구조적으로 0**이다(분자가 0으로 «고정»). ⇒ 곡 내 쌍 대조는
    이 물음에서 **퇴화**한다. 그 사실을 숨기지 않고 먼저 찍는다.

사용: .venv/bin/python scripts/emission_measure.py [--json]
"""
import json, re, sqlite3, sys, collections

DB = 'sunolang.db'
DICT = 'rag/suno_dictionary_v3.json'
LEX = 'data/reanalysis_v2/lexical_index.sqlite'
WORD = re.compile(r"[a-z][a-z0-9'\-]*")
# ⛔2026-09-14 자적발 2건 — 첫 측정에서 「사전 미등재 739」가 나왔는데 «둘 다 내 결함»이었다.
#   ⑴**기능어**(as·an·each·for·while…)가 올라왔다 — 사전은 도메인 어휘만 담으니 당연하고,
#     그걸 「신어」라 부르면 분자가 통째로 거짓이 된다.
#   ⑵**하이픈**: `electric-guitar`가 미등재로 찍혔는데 사전엔 `electric guitar`(공백)로 **있다**.
#     ⇒ ★내 토크나이저가 «가짜 신어»를 만들었다. 대조 전에 하이픈을 접는다.
#   ★교훈 = 「미등재」는 대상의 성질이 아니라 **내 대조기의 출력**이다.
STOP = set("""a an and as at be been but by each for from had has have if in into is it its
kept made make of on onto or our out over per plain so than that the their them then there
these they this those through to under until up upon was were what when where which while
with within without you your featured rooted based given taking using also both each either
neither one two three four five six seven eight nine ten first second third next last same
other another such very more most less least much many few own just only even still yet""".split())


def fold(w):
    """★대조 전 정규화 — 하이픈을 공백으로 접고 낱말로 다시 쪼갠다."""
    return [x for x in w.replace('-', ' ').split() if x]
BR = re.compile(r'\[([^\[\]]{1,120})\]')


def known_vocab():
    """사전이 «이미 아는» 낱말 집합. ⛔출처를 셋 다 합친다 — 하나만 쓰면 신어가 부풀려진다."""
    ks, src = set(), {}
    d = json.load(open(DICT))
    for sec, v in d.items():
        if not isinstance(v, dict):
            continue
        for k in v:
            cands = [k]
            if k.startswith('['):
                try:
                    cands = json.loads(k)
                except Exception:
                    cands = [k]
            for cand in cands:
                for w in WORD.findall(str(cand).lower()):
                    ks.update(fold(w))
    src['dictionary'] = len(ks)
    c = sqlite3.connect(DB)
    for (t,) in c.execute('select suno_term from expr_concepts'):
        for w in WORD.findall(t.lower()):
            ks.update(fold(w))
    src['+expr_concepts'] = len(ks)
    try:
        lx = sqlite3.connect(LEX)
        for (w,) in lx.execute('select word from words'):
            for x in WORD.findall(str(w).lower()):
                ks.update(fold(x))
        src['+lexical_words'] = len(ks)
    except Exception as e:
        print(f'⛔lexical_index 못 읽음 — 신어가 «부풀려진다»: {e}', file=sys.stderr)
    return ks, src


def main():
    c = sqlite3.connect(DB)
    rows = c.execute("""select clip_uuid,batch,aug_creativity,emitted_sp,ordered_sp,rewritten,length_ratio
                        from suno_sp_emissions""").fetchall()
    ks, src = known_vocab()
    per = collections.defaultdict(lambda: {'clip': 0, 'rew': 0, 'newtok_clips': 0,
                                           'newtok': collections.Counter(),
                                           'unknown': collections.Counter(), 'br': 0})
    for u, b, a, emit, order, rw, lr in rows:
        k = f'V{a}'
        p = per[k]
        p['clip'] += 1
        p['br'] += len(BR.findall(emit or ''))
        if not rw or not order:
            continue
        p['rew'] += 1
        e = set(WORD.findall((emit or '').lower()))
        o = set(WORD.findall((order or '').lower()))
        new = e - o
        if new:
            p['newtok_clips'] += 1
            p['newtok'].update(new)
            # ★미등재 판정은 «접은 형태 전부»가 사전 밖일 때만. 기능어는 분자에서 뺀다.
            for w in new:
                parts = fold(w)
                if not parts or all(x in STOP for x in parts):
                    continue
                if any(x in ks for x in parts):
                    continue
                p['unknown'][w] += 1

    print('=== 수노 산출 SP층 측정 (suno_sp_emissions) ===')
    print(f"사전이 아는 낱말 {src.get('+lexical_words', src.get('+expr_concepts'))}개 "
          f"(사전 {src['dictionary']} → +개념 {src['+expr_concepts']} → +lexical {src.get('+lexical_words','—')})")
    print()
    for k in sorted(per, key=lambda x: int(x[1:])):
        p = per[k]
        rate = f"{100*p['newtok_clips']/p['rew']:.1f}%" if p['rew'] else '—'
        print(f"  {k}: 클립 {p['clip']} · 재작성 {p['rew']} · 신규 낱말 든 클립 {p['newtok_clips']} ({rate})")
        print(f"       고유 신규 낱말 {len(p['newtok'])} · ★그중 «사전 미등재» {len(p['unknown'])}"
              f" · SP 대괄호 {p['br']}")
        if p['unknown']:
            print(f"       미등재 상위: {', '.join(w+'×'+str(n) for w, n in p['unknown'].most_common(12))}")
    print()
    print('★V0 확인(구조적 0이어야 한다):',
          f"재작성 {per['V0']['rew']} · 신규 낱말 클립 {per['V0']['newtok_clips']}",
          '✅' if per['V0']['rew'] == 0 else '⛔V0이 재작성됐다 — 전제가 깨졌다')
    allunk = collections.Counter()
    for k, p in per.items():
        if k != 'V0':
            allunk.update(p['unknown'])
    print(f"\n★변주 버킷 전체 «사전 미등재» 고유 낱말 = {len(allunk)}")
    print(f"   상위 30: {', '.join(w+'×'+str(n) for w, n in allunk.most_common(30))}")
    print("\n⛔판정 안 함 — 이 수는 «후보»다. 후보 선반(격리) 경유 전까지 사전·커넥터에 넣지 않는다.")
    if '--json' in sys.argv:
        json.dump({k: {'clip': p['clip'], 'rew': p['rew'], 'newtok_clips': p['newtok_clips'],
                       'unknown': dict(p['unknown'])} for k, p in per.items()},
                  open('data/emission_measure.json', 'w'), ensure_ascii=False, indent=1)
        print('→ data/emission_measure.json')


if __name__ == '__main__':
    main()
