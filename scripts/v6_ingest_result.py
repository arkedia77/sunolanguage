#!/usr/bin/env python3
"""v6 생성결과 수령 → 입력층 대장 갱신 (N0xx 배치 공통).

왜 스크립트인가: 배치 20개를 손으로 같은 집계를 반복하면 자가 흔들린다.
                 ★09-11 leomusic2 적발분(파이프가 실패를 삼킴)과 같은 계열 —
                 반복 절차는 규율이 아니라 도구로 고정한다.
사용: .venv/bin/python scripts/v6_ingest_result.py N027

★2026-09-12 14:3x 개정 — 대조본 칸이 `V4` 하드코딩이었다.
  sunomusic 통지(14:27): **LEO 지시로 대조본 Variety가 13:51부터 4→2**. 전 발주처 공통 레버.
  ⇒ N021~N040은 4 · N041~ 는 2 — **다른 조건**이다. 옛 코드대로면 두 조건이 한 열에
  누적돼 「V4 무수정 x/y」가 섞인 수가 된다. ⇒ 대조본 칸 이름을 **통에 실린 실제
  `variety` 값에서 파생**(`V2`/`V4`)하고, 누적은 **버킷별로 따로** 낸다.
  ⛔값이 통에 없으면 `V?`(미상)로 적는다 — 4로도 2로도 추정하지 않는다.
"""
import json, glob, re, sys

LEDGER = 'data/v6_obs/v6_input_layer_running.json'
GEN = re.compile(r'\b(male|female|tenor|alto|soprano|baritone)\b', re.I)
# ★2026-09-13 03:0x 수리(자적발·이 세션 최대) — 성별어 자가 **영어만** 봤다.
#   수노가 대조본 SP를 한국어·프랑스어로 다시 쓰면(재작성분의 약 19~21%) 「여성 보컬」·
#   「voix féminine」이 들어 있는데도 영어 정규식엔 0건 ⇒ **'소실'로 찍혔다.**
#   실측: 고유 260곡에서 깨짐 **39/260(15.0%) → 11/260(4.2%)**, 28건이 소실→유지(전부 ko).
#   남은 소실 3건은 전부 프랑스어 판이었고 둘은 `voix féminine` 명시 ⇒ fr까지 넣는다.
#   ⛔이 수는 세션 내내 내가 인용했고 KANBAN 대기 항목(「깨진 38곡 오디오층 회수」)의 근거였다.
#   ★교훈=**자가 한 언어만 보면 「없다」가 「깨졌다」로 찍힌다.**
GEN_ALT = {              # 표기 → 영어 정규형
    '여성': 'female', '여자': 'female', '남성': 'male', '남자': 'male',
    '테너': 'tenor', '알토': 'alto', '소프라노': 'soprano', '바리톤': 'baritone',
    '중성적': 'androgynous', '가성': 'falsetto',
    'féminine': 'female', 'feminine': 'female', 'masculine': 'male',
    'masculin': 'male', 'ténor': 'tenor', 'contralto': 'contralto',
}


# ★2026-09-13 07:0x 가드 추가(남의 정정통에서 온 점검 — ⑨-6 규율의 두 번째 작동).
#   sunomusic 09-13 06:45 §4: 자기 성별어 자에 한국어 18낱말을 넣으면서 **악기 결합**
#   (`테너 색소폰`·`알토 플루트`)은 일부러 뺐다고 고지. 내 GEN_ALT는 **부분문자열 매칭**이라
#   같은 함정이 원리상 열려 있었다. ⛔단 **내 데이터에서는 아직 0건**(한글 SP 79건 전수 실측
#   2026-09-13) ⇒ 이건 **과거 수치의 정정이 아니라 미발현 결함의 봉인**이다.
#   ★그래서 고친 뒤 **같은 79건을 다시 재서 판정 불변임을 확인**한다(양성통제).
_INSTR_TAIL = ('색소폰', '색스', '섹소폰', '플루트', '트롬본', '클라리넷', '호른',
               '리코더', '오보에', '바순', '트럼펫', '기타', 'saxophone', 'sax', 'flute')


def gender_words(text: str) -> list:
    """SP 문자열의 성별·음역 낱말을 «언어 불문» 뽑아 영어 정규형으로 돌려준다.

    ⛔음역어(테너·알토 등)가 **악기 이름 앞자리**면 성별어가 아니다(`테너 색소폰`).
    """
    out = {w.lower() for w in GEN.findall(text or '')}
    low = (text or '').lower()
    raw = text or ''
    for k, v in GEN_ALT.items():
        kl = k.lower()
        if kl not in low:
            continue
        # 한국어 표기는 뒤에 악기어가 붙은 자리를 뺀다(영문은 GEN 정규식이 단어경계로 봄)
        if any('가' <= ch <= '힣' for ch in k):
            hits = [m.end() for m in __import__('re').finditer(k, raw)]
            if hits and all(any(raw[e:e + 8].lstrip().startswith(w) for w in _INSTR_TAIL)
                            for e in hits):
                continue
        out.add(v)
    return sorted(out)
INBOX = '/Users/purple/projects/agent-comm/projects/sunolanguage/messages'

def main(tag):
    rec = json.load(open(LEDGER))
    fs = sorted(glob.glob(f'{INBOX}/**/sunolanguage_sunomusic_*_{tag}_생성결과.json', recursive=True))
    if not fs:
        sys.exit(f'⛔{tag} 결과통 없음 — 미측정(「없다」가 아님)')
    d = json.load(open(fs[-1])); b = d.get('body', d); songs = b['songs']
    print(f"{tag}: {b.get('summary')} · 결과통 {len(fs)}건 · uuid결손 "
          f"{sum(1 for s in songs if not s.get('suno_uuid1'))} · 원문변경 {'有' if b.get('⚠원문_변경_감지') else '無'}")
    design = json.load(open(f"data/{tag.lower()}/{tag}_design.json"))
    om = {s['title']: s['sp'] for s in design['songs']}
    v0 = [r for s in songs for r in s.get('rendered_sp', [])]
    if not v0:
        print('  ⚠rendered_sp 없는 판 — 대장 갱신 보류(다음 통 대기)'); return
    v4, gen, varieties = [], [], set()
    by_actual, intents, mismatch, unarmed = {}, set(), [], []
    for s in songs:
        pc = s['pair_clips'][0] if isinstance(s.get('pair_clips'), list) else s.get('pair_clips')
        if not pc: continue
        # ★2026-09-12 21:xx 수리(자적발) — N041 통의 칸 이름은 `variety`가 아니라
        #   **`pair_variety`**다(정본은 `primary_variety`). 옛 코드는 없는 칸을 찾다가
        #   곡 단위 `variety`(=정본 0)로 폴백해 **대조본을 V0으로 찍었다** — 조건이
        #   다른 두 버킷이 한 칸에 섞일 수 있었다. ⇒ pair_variety를 1순위로 읽는다.
        #   ★같은 통의 `patch_record`(sliders.aug_creativity)와 per-clip `aug_creativity`가
        #   pair_variety와 같은 값이다 ⇒ aug_creativity=variety 같은 칸(09-12 확인).
        # ★2026-09-12 21:5x 재수리 — sunomusic 회신(코드 근거 4건)으로 두 칸의 «뜻»이 갈렸다:
        #   `pair_variety`=**그쪽 입력(의도)** / `rendered_sp[].aug_creativity`=**수노가 클립에 적은 실제**.
        #   패치 무장이 실패하면 의도는 목표값으로 남고 클립은 UI 기본값(1)으로 나간다.
        #   ⇒ **어긋나면 클립 기록이 이긴다**(그쪽 칸의 뜻·내 처방 아님) ⇒ 버킷은 «실제»로 건다.
        #   ★실측(내가 쥔 통 전수, 09-12): 210곡 중 어긋남 1곡(N041 gid 30423 의도2→실제1).
        intent = pc.get('pair_variety', pc.get('variety', s.get('variety')))
        # ★2026-09-12 22:2x 추가 — sunomusic 확인통: **판별식이 이미 이 통 안에 있었다.**
        #   `pair_clips.patch_record`가 `[PATCH]`로 시작하지 않으면(`no_patch_record`·
        #   `arm_failed:`·`wait_failed:`) 그 곡의 대조본은 **레버가 안 걸린 채 UI 기본값(1)로 나간 것**.
        #   ⇒ 그쪽 로그를 청구하지 않고 내 대장에서 가른다. 원인=패처 무장이 Create보다 늦음
        #   (그쪽 수리 커밋 8a97946) ⚠**이미 기동한 워커엔 안 걸린다** ⇒ 지금 돌는 로트는 구판이라
        #   같은 사건이 또 날 수 있다 — 이 칸으로 매 배치 자동 검출한다.
        #   ⛔단 최종 판정은 계속 `aug_creativity`다(패치가 걸려도 값이 어긋날 자리가 이론상 남음).
        pr = str(pc.get('patch_record') or '')
        if not pr.startswith('[PATCH]'):
            unarmed.append({"gid": s['id'], "patch_record": pr or None, "의도": intent})
        for r in pc['rendered_sp']:
            act = r.get('aug_creativity', intent)
            varieties.add(act)
            by_actual.setdefault(act, []).append(r)
            if act != intent:
                mismatch.append({"gid": s['id'], "의도": intent, "실제": act})
        intents.add(intent)
        v4 += pc['rendered_sp']
        ask = gender_words(om[s['title']])
        # ★성별어는 통에 실린 칸(영어 추출분)에 **다국어 재추출**을 합집합한다.
        #   통의 `성별어`는 sunomusic이 영어 정규식 16종으로 뽑은 값이다(자기고지·`androgynous`
        #   `contralto` `falsetto` 포함) ⇒ 결함은 어휘가 아니라 **언어**뿐이라 내가 다시 본다.
        # ★2026-09-13 04:2x 재수리 — 여태 **첫 클립만** 봤다. sunomusic 코드 주석(:298-299)이
        #   「같은 곡의 두 클립이 다른 성별로 갈린다」(gid 10880 실측)를 이미 적어 두고 있었고,
        #   내 실측에서도 **쌍 280개 중 17개(6.1%)가 두 클립의 성별어가 다르다**.
        #   ⇒ 클립별로 다 적고 **단위를 셋 다** 낸다(어느 하나가 참이 아니라 물음이 다르다):
        #     ⒜첫 클립(임의) ⒝둘 중 하나라도 유지(=발주대로 난 테이크가 있는가·A&R용)
        #     ⒞둘 다 유지(엄격). ⛔단위를 안 적고 「깨짐 N건」이라 쓰면 그 수는 못 읽는다.
        _clips = [sorted(set(r.get('성별어') or []) | set(gender_words(r.get('렌더입력SP') or '')))
                  for r in pc['rendered_sp']]
        got = _clips[0]
        # ★2026-09-12 수리(자적발) — 옛 사다리엔 «확장» 칸이 없어서 발주 ['male'] →
        #   렌더 ['male','tenor'](=발주어 유지 + 음역어 추가)가 **'축소'**로 찍혔다
        #   (N041 gid 30419 실측). 늘어난 걸 줄었다고 적는 라벨이다. ⛔깨짐 수(소실+역전)는
        #   영향 없으나 라벨은 틀렸다 ⇒ 발주어가 전부 남아 있고 더 붙은 경우는 '확장'.
        verdict = ('유지' if sorted(got) == ask else
                   '소실' if not got else
                   '역전' if not set(got) & set(ask) else
                   '확장' if set(ask) <= set(got) else '축소')
        def _vd(g):
            if sorted(g) == ask: return '유지'
            if not g: return '소실'
            if not set(g) & set(ask): return '역전'
            return '확장' if set(ask) <= set(g) else '축소'
        _vs = [_vd(c) for c in _clips]
        gen.append({"gid": s['id'], "발주": ask, "v4": got, "판정": verdict,
                    "클립별": _clips, "클립별_판정": _vs,
                    "쌍_갈림": len(set(map(tuple, _clips))) > 1})
    vs = {v for v in varieties if v is not None}
    vkey = f"V{int(list(vs)[0])}" if len(vs) == 1 else ("V?" if not vs else "V혼재")
    # ★버킷은 «클립 실제값»별로 쪼갠다 — 한 배치 안에서도 갈릴 수 있다(패치 실패 곡).
    per = {}
    for act, rs in sorted(by_actual.items(), key=lambda x: (x[0] is None, x[0])):
        per[f"V{int(act)}" if act is not None else "V?"] = {
            "무수정": f"{sum(1 for r in rs if r['무수정'])}/{len(rs)}",
            "길이비_최소": min((r['길이비'] for r in rs), default=None),
            "길이비_최대": max((r['길이비'] for r in rs), default=None)}
    rec['batches'][tag] = {
        "n_songs": len(songs),
        "대조본_variety": (list(vs)[0] if len(vs) == 1 else sorted(vs) or None),
        "대조본_칸": vkey,
        "대조본_의도": (sorted(intents)[0] if len(intents) == 1 else sorted(intents) or None),
        "대조본_버킷_실제": per,
        "★의도_실제_불일치": mismatch,
        "★패치_미무장": unarmed,
        "V0": {"무수정": f"{sum(1 for r in v0 if r['무수정'])}/{len(v0)}",
               "길이비": sorted({r['길이비'] for r in v0})},
        vkey: {"무수정": f"{sum(1 for r in v4 if r['무수정'])}/{len(v4)}" if v4 else "0/0",
               "길이비_최소": min((r['길이비'] for r in v4), default=None),
               "길이비_최대": max((r['길이비'] for r in v4), default=None)},
        "성별어": gen}
    json.dump(rec, open(LEDGER, 'w'), ensure_ascii=False, indent=2)
    # ★누적은 버킷별로 — 대조본 조건(Variety)이 다른 배치를 한 수로 합치지 않는다.
    t0 = t0u = mm = 0; mg = set(); ua = set(); cnt = {'유지': 0, '확장': 0, '소실': 0, '역전': 0, '축소': 0}
    buckets = {}   # 대조본 칸 → [미수정, 전체, 배치수, 곡수]
    for bb in rec['batches'].values():
        a, x = bb['V0']['무수정'].split('/'); t0u += int(a); t0 += int(x)
        # ★누적도 «실제값» 버킷으로 — 의도로 합치면 패치 실패분이 남의 칸에 섞인다.
        pb = bb.get('대조본_버킷_실제')
        if pb:
            for k, v in pb.items():
                a, x = v['무수정'].split('/')
                e = buckets.setdefault(k, [0, 0, 0, 0])
                e[0] += int(a); e[1] += int(x); e[2] += 1; e[3] += bb['n_songs']
        else:
            k = bb.get('대조본_칸') or next((c for c in ('V4', 'V2', 'V?', 'V혼재') if c in bb), None)
            if k:
                a, x = bb[k]['무수정'].split('/')
                e = buckets.setdefault(k, [0, 0, 0, 0])
                e[0] += int(a); e[1] += int(x); e[2] += 1; e[3] += bb['n_songs']
        _mmx = bb.get('★의도_실제_불일치') or []
        mm += len(_mmx); mg |= {e['gid'] for e in _mmx}
        ua |= {e['gid'] for e in (bb.get('★패치_미무장') or [])}
        for g in bb['성별어']: cnt[g['판정']] = cnt.get(g['판정'], 0) + 1
    n = sum(x['n_songs'] for x in rec['batches'].values())
    broke = cnt['소실'] + cnt['역전']
    print(f"★누적 {len(rec['batches'])}배치({n}곡): V0 무수정 {t0u}/{t0}")
    for k, (u, x, nb, ns) in sorted(buckets.items()):
        print(f"   대조본 {k}(클립 실제값): 무수정 {u}/{x} · 해당 배치 {nb}  ⛔다른 칸과 합산 금지")
    print(f"   ★의도(pair_variety)≠실제(aug_creativity) = **곡 {len(mg)}건 / 클립 {mm}건**"
          f"{' — 실제 쪽으로 버킷팅했다(어긋나면 클립 기록이 이긴다)' if mm else ''}")
    print(f"   ★패치 미무장(`patch_record`가 [PATCH] 아님) = 곡 {len(ua)}건"
          f"{' ⇒ ' + str(sorted(ua)) if ua else ''}  ※대조본 조건 이탈분(버릴 것 아니라 갈라 적을 것)")
    # ★단위 3종 — 어느 하나가 참이 아니라 «물음이 다르다»
    u_first = u_any = u_all = 0; pair_split = 0; tot_pair = 0
    for bb in rec['batches'].values():
        for g in bb['성별어']:
            vs = g.get('클립별_판정') or [g['판정']]
            tot_pair += 1
            pair_split += 1 if g.get('쌍_갈림') else 0
            u_first += vs[0] in ('소실', '역전')
            u_any += all(v in ('소실', '역전') for v in vs)
            u_all += any(v in ('소실', '역전') for v in vs)
    print(f"   성별어 {cnt} ⇒ ★단위 3종(분모 {tot_pair}쌍): "
          f"⒜첫 클립 {u_first} · ⒝둘 다 깨짐 {u_any} · ⒞하나라도 깨짐 {u_all} "
          f"· **쌍 갈림 {pair_split}({pair_split/tot_pair*100:.1f}%)**")
    print(f"      ⛔단위를 안 적고 「깨짐 N건」이라 쓰지 말 것 · ※대조본 판정이라 버킷 혼재")

if __name__ == '__main__':
    main(sys.argv[1])
