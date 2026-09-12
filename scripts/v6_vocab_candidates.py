#!/usr/bin/env python3
"""v6_vocab_candidates.py — 대조본이 «다시 쓴» SP에서 사전 후보 어휘를 뽑는다.

왜 도구인가: 결과통이 배치마다 온다. 같은 집계를 손으로 반복하면 자가 흔들린다
             (09-12 실측: 자를 네 번 고쳤다 — 아래 ★자 이력).

★자 이력(⛔같은 실수를 되풀이하지 않으려고 남긴다)
  ⑴사전 `words_output_layer`(1988종) 기저 ⇒ and·with가 「신규」로 나왔다. **걸러진 목록**이었다.
  ⑵`words` 표 전체(5649종) 기저 ⇒ 기능어 여전히 없음. 표 자체가 걸러진 것.
  ⑶재분석 코퍼스 **원문**(`entries.sentence` + `phrases`) 기저 ⇒ ★양성통제 통과(and>0).
  ⑷하이픈 **성분층**을 갈랐다 ⇒ 「신규 낱말」과 「신규 결합」은 다른 것이다.
     ⛔young·plain·sway는 성분층에도 없다(내 코퍼스가 좁은 것이지 하이픈 탓이 아니다 —
       09-12 내가 재기 «전»에 하이픈 탓으로 단정했고 양성통제가 반증했다).

관문(⛔1배치 1회 출현은 관측이지 어휘가 아니다)
  G1 재출현: **2개 이상 배치**에서 나와야 승격 후보
  G2 문맥: 승격 전에 칸(악기·주법·구조·정서)을 사람이 지정 — 이 도구는 **예시 문장만** 대 준다
  ⚠토큰 파편·오타 의심(`gl`·`waltting` 류)은 G1을 통과해도 사람이 배제한다

사용: .venv/bin/python scripts/v6_vocab_candidates.py [--min-batches 2]
"""
from __future__ import annotations
import argparse, collections, glob, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEX = ROOT / 'data/reanalysis_v2/lexical_index.sqlite'
INBOX = Path('/Users/purple/projects/agent-comm/projects/sunolanguage/messages')
# ★자 5판(09-12) — 종전 ASCII 전용 정규식이 **악센트 낱말을 쪼갰다**:
#   électrique → "lectrique" · coréen → "cor"+"en" · superposées → "superpos".
#   그 파편이 「신규 낱말」로 71종까지 부풀었다(오염). ⇒ 유니코드 글자 기준으로 잡는다.
TOK = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", re.UNICODE)
# ★그리고 더 큰 것: **수노가 일부 SP를 프랑스어로 다시 썼다**(N021·N022·N023·N025·N037 실측).
#   영어 어휘 후보와 비영어 SP를 한 칸에 섞으면 사전이 깨진다 ⇒ SP 단위로 언어를 갈라 센다.
#   ⛔판별은 표지 낱말 + 악센트 비율의 **거친 자**다(언어 판별기가 아니다) — 경계 사례는 사람이 본다.
FR_MARK = {'avec', 'et', 'en', 'à', 'au', 'aux', 'mesure', 'voix', 'basse', 'batterie',
           'guitare', 'claire', 'des', 'les', 'une', 'sur', 'dans', 'légèrement'}
ACCENT = re.compile(r"[àâäçéèêëîïôöùûüÿœæ]", re.I)


HANGUL = re.compile(r"[가-힣]")


def lang_of(sp: str) -> str:
    """'en' / 'ko' / 'fr'. ⛔거친 자다(언어 판별기 아님) — 경계 사례는 사람이 본다.
    ★09-12: 종전 판은 프랑스어 표지만 봐서 **한국어 재작성분이 영어 칸에 섞였다**
      (신규 낱말이 767종으로 부풀었다 — 베이스·따뜻한·킥과 …). 한글을 먼저 본다."""
    h = len(HANGUL.findall(sp))
    if h >= 5:
        return 'ko'
    toks = [t.lower() for t in TOK.findall(sp)]
    if sum(1 for t in toks if t in FR_MARK) >= 2 or len(ACCENT.findall(sp)) >= 3:
        return 'fr'
    # ★한글이 조금 섞인 판 = **혼합**(한국어 장르 라벨 + 영어 본문). 09-12 실측:
    #   「인디 팝, 112 BPM, C Major, 4/4: warm conversational …」 ⇒ 임계 5로는 안 걸렸고
    #   `팝`이 영어 후보 칸에 샜다. ⇒ 혼합으로 갈라 적고, 한글 토큰은 영어 칸에서 뺀다.
    return 'mixed' if h >= 1 else 'en'


def baseline():
    """기저 2층 — 전체토큰 / 하이픈 성분낱말. ★코퍼스 «원문»에서 만든다."""
    con = sqlite3.connect(LEX)
    whole, comp = collections.Counter(), collections.Counter()
    for sql in ("SELECT sentence FROM entries WHERE sentence IS NOT NULL",
                "SELECT phrase FROM phrases WHERE phrase IS NOT NULL"):
        for (t,) in con.execute(sql):
            for w in TOK.findall(t):
                wl = w.lower(); whole[wl] += 1
                for part in wl.split('-'):
                    if part: comp[part] += 1
    con.close()
    # ★양성통제 — 기능어가 기저에 «있어야» 한다. 없으면 걸러진 목록을 잡은 것이다.
    ctrl = {w: comp[w] for w in ('and', 'with', 'the', 'a', 'in')}
    if min(ctrl.values()) == 0:
        sys.exit(f"⛔양성통제 실패 — 기저에 기능어가 없다(걸러진 목록을 잡았다): {ctrl}")
    return whole, comp, ctrl


def cans():
    seen = {}
    for f in sorted(glob.glob(str(INBOX / '**/sunolanguage_sunomusic_*_생성결과.json'), recursive=True)):
        b = json.load(open(f, encoding='utf-8')); b = b.get('body', b)
        tag = b.get('batch')
        if tag and str(tag).startswith('N'):
            seen[tag] = b           # 같은 배치 재발행이면 최신 통이 이긴다
    return seen


def main(min_batches):
    whole, comp, ctrl = baseline()
    print(f"■ 기저 = 재분석 코퍼스 원문 · 전체토큰 {len(whole)}종 / 성분낱말 {len(comp)}종 "
          f"· 양성통제 {ctrl}")
    lex = collections.defaultdict(lambda: {"n": 0, "batches": set(), "ex": None})
    comb = collections.defaultdict(lambda: {"n": 0, "batches": set(), "ex": None})
    n_rw = n_clip = 0
    nonen = []      # (tag, gid, 앞 60자) — 비영어로 다시 쓰인 SP
    for tag, b in sorted(cans().items()):
        for s in b.get('songs', []):
            pc = s.get('pair_clips'); pc = pc[0] if isinstance(pc, list) else pc
            if not pc: continue
            for r in pc.get('rendered_sp', []):
                n_clip += 1
                if r.get('무수정'): continue
                n_rw += 1
                sp = r.get('렌더입력SP') or ''
                lg = lang_of(sp)
                if lg == 'mixed':
                    nonen.append((tag, s['id'], lg, sp[:56].replace('\n', ' ')))
                    # 혼합은 영어 부분만 센다(한글 토큰 제외 — 아래 skip)
                elif lg != 'en':
                    nonen.append((tag, s['id'], lg, sp[:56].replace('\n', ' ')))
                    continue        # ★영어 어휘 후보 칸에 섞지 않는다
                for w in TOK.findall(sp):
                    if HANGUL.search(w):
                        continue        # ★한글 토큰은 ko 층 소관 — 영어 후보 칸에 넣지 않는다
                    wl = w.lower(); parts = [p for p in wl.split('-') if p]
                    miss = [p for p in parts if p not in comp]
                    if miss:
                        for m in miss:
                            e = lex[m]; e["n"] += 1; e["batches"].add(tag)
                            if not e["ex"]: e["ex"] = context(sp, w)
                    elif wl not in whole and len(parts) > 1:
                        e = comb[wl]; e["n"] += 1; e["batches"].add(tag)
                        if not e["ex"]: e["ex"] = context(sp, w)
    print(f"■ 대조본 클립 {n_clip} 중 **재작성 {n_rw}건** · 그중 **비영어 {len(nonen)}건 제외** "
          f"⇒ 영어 분모 {n_rw - len(nonen)}건 (⛔무수정 건은 내 발주문이라 분모 밖)")
    if nonen:
        by = collections.Counter(l for _, _, l, _ in nonen)
        print(f"■ ★**수노가 영어 아닌 판으로 다시 쓴 SP = {len(nonen)}건 / 재작성 {n_rw}건 "
              f"({len(nonen)/n_rw*100:.1f}%)** · 언어 {dict(by)} "
              f"(⛔`mixed`=한국어 라벨+영어 본문 · 영어 부분은 후보 칸에 셈)")
        for lg in sorted(by):
            rows = [r for r in nonen if r[2] == lg]
            bt = sorted({t for t, _, _, _ in rows})
            print(f"   [{lg}] {len(rows)}건 · {len(bt)}배치 {bt}")
            print(f"       예: {rows[0][0]} gid={rows[0][1]} 「{rows[0][3]}…」")
    for name, d in (("신규 낱말", lex), ("신규 결합", comb)):
        pas = {k: v for k, v in d.items() if len(v["batches"]) >= min_batches}
        obs = {k: v for k, v in d.items() if len(v["batches"]) < min_batches}
        print(f"\n■ {name} — 총 {len(d)}종 · ★G1 통과(≥{min_batches}배치) **{len(pas)}종** "
              f"/ 1배치 관측 {len(obs)}종")
        for k, v in sorted(pas.items(), key=lambda x: (-len(x[1]["batches"]), -x[1]["n"])):
            print(f"   ✅{k}  ×{v['n']} · {len(v['batches'])}배치 {sorted(v['batches'])}")
            print(f"       예: …{v['ex']}…")
        if obs:
            print(f"   ⛔G1 미통과(관측만): {' · '.join(f'{k}×{v[chr(110)]}' for k, v in sorted(obs.items(), key=lambda x:-x[1]['n']))}")


def context(sp, w, span=46):
    i = sp.lower().find(w.lower())
    if i < 0: return None
    return sp[max(0, i - span):i + len(w) + span].replace('\n', ' ')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--min-batches', type=int, default=2)
    main(ap.parse_args().min_batches)
