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


def _known_failed_clips():
    """★렌더 실패가 «확인된» 정본(V0) 클립. ⛔비었다고 「없다」가 아니다 — 미측정이다.

    출처: `sunolang.db:suno_sp_emissions.clip_status`(그쪽이 전수로 잰 값을 옮겨 담은 칸).
    NULL은 「정상」이 아니라 «미측정»이다(sunomusic 배차기 재기동 이전 구간).
    """
    import sqlite3
    # ⛔2026-09-15 수리(자적발) — 직전 판은 `clip_status != 'complete'` 전부를 «실패»로 셌다.
    #   그래서 `streaming`(=통 작성 시점에 «진행 중»)이 「렌더 실패」로 찍혔다.
    #   ★sunomusic이 바로 그 층을 가른 참인데(「빼는 것과 안 보이게 하는 것은 다르다」)
    #     내가 내 도구 안에서 다시 합쳤다. ⇒ **실패(error)와 미완(submitted/streaming)을 가른다.**
    try:
        c = sqlite3.connect('sunolang.db')
        fail = [f"{g}:{u[:8]}" for u, g in c.execute(
            "select clip_uuid,gid from suno_sp_emissions "
            "where aug_creativity=0 and clip_status='error'")]
        pend = [f"{g}:{u[:8]}" for u, g in c.execute(
            "select clip_uuid,gid from suno_sp_emissions "
            "where aug_creativity=0 and clip_status in ('submitted','streaming')")]
        return fail, pend
    except Exception:
        return [], []
GEN = re.compile(r'\b(mezzo-soprano|bass-baritone|countertenor|counter-tenor|contralto|androgynous|falsetto|male|female|tenor|alto|soprano|baritone)\b', re.I)
# ★긴 낱말을 «앞»에 둔다 — 파이썬 교체는 «첫 일치»라 `baritone`이 앞에 있으면
#   `bass-baritone`을 통째로 못 집는다(2026-09-13 sunomusic이 `bass-baritone`을 언급해 확인).
#   ⛔내 표본엔 `bass-baritone` 0건이라 **과거 수치 영향은 없다** — 어휘만 넓힌다.
# ★2026-09-13 18:5x — 내 영어 정규식에 `androgynous`·`mezzo-soprano`·`falsetto`가 «없었다».
#   ⛔그 낱말들은 지금까지 **오로지 sunomusic 칸으로만** 들어왔다 — 즉 내 ⑨-8 발견
#   (「역전의 주된 모양은 androgynous 치환」)은 **두 자의 합의가 아니라 그쪽 자 단독**이었다.
#   ⇒ 넣어서 «내 자로도 독립 확인»이 되게 한다.
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
# ★2026-09-13 18:5x 재수리(sunomusic이 내 가드의 결함을 찾아 줌 — 상호 점검 3회차).
#   ⛔내 09-13 07시 가드는 **한국어 경로에만** 걸려 있었다: GEN 정규식(영어)과 GEN_ALT의
#   프랑스어 항목은 **가드를 아예 안 거쳤다.** ⇒ `tenor saxophone`·`saxophone ténor`가 그대로 통과.
#   ★그쪽이 佛 어순(`saxophone ténor` = 악기→음역어)에서 먼저 걸렸고, 내 쪽은 **영어에서 실물 1건**
#   (gid 30565 `baritone saxophone`)이 이미 있었다 — ⛔**내가 아침에 「발현 0건」이라 보고한 것은
#   «한국어만» 잰 결과였다**(분모를 안 적고 0을 말한 그 병).
#   ⇒ 수리: **세 경로(영어 정규식·한국어·프랑스어) 전부**에 **앞뒤 양방향** 악기 가드를 건다.
#   ★판정 영향 0: gid 30565 clip0은 `male`이 따로 있어 female→male 역전이 그대로 선다(전수 대조함).
_INSTR = ('색소폰', '색스', '섹소폰', '플루트', '트롬본', '클라리넷', '호른',
          '리코더', '오보에', '바순', '트럼펫', '기타',
          'saxophone', 'sax', 'flute', 'clarinet', 'guitar', 'horn', 'trombone',
          'oboe', 'recorder', 'cornet', 'bassoon', 'trumpet', 'ukulele',
          'flûte', 'clarinette', 'guitare', 'hautbois', 'basson', 'trompette')
_REGISTER = ('tenor', 'alto', 'soprano', 'baritone', 'contralto',
             '테너', '알토', '소프라노', '바리톤', 'ténor')
_WINDOW = 14


def _instrument_adjacent(text: str, start: int, end: int) -> bool:
    """음역어 앞·뒤 창에 악기어가 있으면 성별어가 아니다.

    ⛔앞뒤를 다 본다 — 영어·한국어는 `tenor sax`(음역어→악기)지만
    프랑스어는 `saxophone ténor`(악기→음역어)로 **어순이 뒤집힌다.**
    """
    low = text.lower()
    before = low[max(0, start - _WINDOW):start]
    after = low[end:end + _WINDOW]
    return any(w in before for w in _INSTR) or any(w in after for w in _INSTR)


def gender_words(text: str) -> list:
    """SP 문자열의 성별·음역 낱말을 «언어 불문» 뽑아 영어 정규형으로 돌려준다.

    ⛔음역어가 악기 이름과 붙어 있으면(앞이든 뒤든) 성별어가 아니다.
    """
    raw = text or ''
    low = raw.lower()
    out = set()
    for m in GEN.finditer(raw):
        w = m.group(0).lower()
        if w in _REGISTER and _instrument_adjacent(raw, m.start(), m.end()):
            continue
        out.add(w)
    for k, v in GEN_ALT.items():
        kl = k.lower()
        if kl not in low:
            continue
        hits = [(m.start(), m.end()) for m in re.finditer(re.escape(kl), low)]
        if kl in _REGISTER and hits and all(_instrument_adjacent(raw, s, e) for s, e in hits):
            continue
        out.add(v)
    return sorted(out)


# ★2026-09-13 20:3x — 상대 자의 «중첩어 이중 계수» 실측(4건·v1/v3/v6 전 판본에서 살아남음).
#   `mezzo-soprano`는 하이픈이 낱말경계를 만들어 `\bsoprano\b`가 «안쪽»에 걸린다 ⇒ 상대 칸이
#   `['female','soprano','mezzo-soprano']`를 낸다. 실물 확인: 그 SP에 **독립 `soprano`는 0회**.
#   (⛔`contralto⊃alto`는 6건 중 0건 — 'r'이 경계를 막아 상대도 정상. **하이픈 중첩만** 문제다.)
#   ⇒ 상대 토큰 중 **SP에 독립 출현이 0이고 더 긴 음역어 안에만 있는 것**은 버린다.
# ★2026-09-13 21:1x 일반화 — 목록식(`_NESTED`)은 **내가 안 적은 중첩쌍을 놓친다**
#   (그쪽이 `bass-baritone`을 언급해 드러났다). ⇒ **검출된 토큰끼리 포함관계를 스스로 본다.**
#   ⛔그쪽 반례 수용: `mezzo-soprano … and soprano`처럼 **짧은 낱말이 «독립으로도» 있으면 남긴다**
#   — 판정은 **출현 «횟수»**로 한다(짧은 것의 출현수 > 그것을 품는 긴 것들의 출현수 합 ⇒ 독립 있음).
def _drop_nested(tokens: set, sp: str) -> set:
    """중첩어 «이중 계수»만 걷어낸다 — ⛔독립 출현은 절대 안 지운다.

    ★2026-09-13 21:2x 재수리(sunomusic이 자기 v7에서 같은 결함을 찾아 알려 줌).
      내 종전 규칙은 「짧은 것의 출현수 ≤ 그것을 품는 긴 것들의 출현수」였는데,
      ⛔**하이픈이 없는 중첩어는 안쪽이 «애초에 안 잡힌다»**(`countertenor`의 `tenor`는
      앞이 `r`이라 낱말경계가 없다) ⇒ `n_in`이 이미 «독립분만» 센 값인데
      그걸 `n_out`과 비교해 **독립 출현을 안쪽 계수로 오판**했다.
      실측 결함: `countertenor and tenor` → `tenor` 삭제 · `contralto and alto` → `alto` 삭제.
    ⇒ ★**먼저 「긴 낱말 «안»에서 내 경계 규칙으로 실제로 잡히는가」를 본다.**
      안 잡히면 중첩 보정을 **아예 하지 않는다**(이중 계수가 원리상 불가능하므로).
    """
    low = (sp or '').lower()
    out = set(tokens)
    for inner in list(out):
        pat = r'\b' + re.escape(inner) + r'\b'
        outers = [o for o in out if o != inner and re.search(pat, o)]
        if not outers:                      # 경계 규칙상 안쪽에서 안 잡힌다 ⇒ 보정 안 함
            continue
        n_in = len(re.findall(pat, low))
        n_out = sum(len(re.findall(re.escape(o), low)) * len(re.findall(pat, o))
                    for o in outers)
        if n_in <= n_out:
            out.discard(inner)
    return out


def _peer_tokens(clip: dict) -> tuple:
    """상대 칸에서 토큰을 꺼낸다 — **v6부터는 상대가 정규화 칸을 같이 싣는다.**

    반환 = (합집합에 쓸 집합, 불일치 메모 or None)

    ⛔상대(sunomusic) v6 스키마: `성별어`=찾은 **원형** · `성별어_정규화`=상대의 **사상 결과**.
      그쪽이 원형을 남긴 이유가 「사상은 내 해석이라 틀릴 수 있다」이므로,
      ★**나는 둘 다 받아서 «내 사상»과 대조**한다 — 그게 그쪽이 원형을 남긴 값이다.
    ⛔v6 이전 통에는 정규화 칸이 없다 ⇒ **내가 원형을 사상**한다(종전 동작).
    """
    raw = clip.get('성별어')
    mine = _drop_nested(_norm_tokens(raw), clip.get('렌더입력SP') or '')
    theirs = clip.get('성별어_정규화')
    if theirs is None:
        return mine, None
    theirs = _drop_nested({str(w).strip().lower() for w in theirs}, clip.get('렌더입력SP') or '')
    mine = _drop_nested(mine, clip.get('렌더입력SP') or '')
    if theirs != mine:
        return theirs | mine, f"gid칸 사상 불일치: 그쪽 {sorted(theirs)} ↔ 내 사상 {sorted(mine)} (원형 {raw})"
    return theirs, None


def _norm_tokens(tokens) -> set:
    """상대 칸의 토큰을 **내 영어 정규형으로 맞춘 뒤** 합집합에 넣는다.

    ⛔2026-09-13 실측: sunomusic v3는 한국어를 «찾기는» 하는데 **정규화를 안 하고**
      원형(`여성`·`남성`)을 그대로 싣는다. 그대로 합집합하면 `{'female','여성'}`이 되어
      **같은 사람이 두 낱말로 세어지고 「확장」으로 오판된다**(실측 gid 30573 = 가짜 확장,
      30536 = 가짜 쌍_갈림). ⇒ **합치기 전에 자를 맞춘다.**
    ★교훈: 합집합은 상대의 «못 봄»은 막아 주지만 **«표기 차이»는 못 막는다 — 맞춰서 합쳐야 한다.**
    """
    out = set()
    for w in (tokens or []):
        if not isinstance(w, str):
            continue
        key = w.strip()
        out.add(GEN_ALT.get(key, GEN_ALT.get(key.lower(), key.lower())))
    return out
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
        _clips = [sorted(_peer_tokens(r)[0] | set(gender_words(r.get('렌더입력SP') or '')))
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
    # ★2026-09-14 — kee §2 조건을 «규율이 아니라 도구»에 넣는다.
    #   ⛔「무수정 N/N」은 분모가 「렌더 성공 클립」처럼 읽히는데, 이 자가 실제로 센 것은
    #     **「결과통에 SP가 실려 온 클립」**이다(텍스트층). N057 `5fddf3da`는 `status=error`인데
    #     이 분모 «안에» 있었다(sunomusic·kee 2026-09-14 전수).
    #   ⇒ ★두 수를 «기계가» 같이 찍는다 — 내가 기억해서 병기하는 방식은 재사용 자리에서 샌다.
    _err, _pend = _known_failed_clips()
    print(f"★누적 {len(rec['batches'])}배치({n}곡): V0 무수정 {t0u}/{t0}"
          f"  ※단위=**텍스트층**(SP가 실려 온 클립)")
    if _err or _pend:
        print(f"   ⛔렌더 «성공» 분모는 **{t0 - len(_err) - len(_pend)}** ★두 수를 한 칸에 쓰지 말 것")
        if _err:
            print(f"      · 실패(error) {len(_err)}클립 제외: {', '.join(_err)}")
        if _pend:
            print(f"      · ⚠미완(submitted/streaming) {len(_pend)}클립 제외 — "
                  f"**실패가 아니다**(통 작성 시점에 진행 중): {', '.join(_pend)}")
    else:
        print("   ⚠렌더 실패 확인분 0 — ★「없다」가 아니라 «내가 아는 범위에 없다»"
              "(clip status는 sunomusic 칸·무료창 4일치만 전수됨)")
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
