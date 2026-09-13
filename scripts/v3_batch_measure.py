#!/usr/bin/env python3
"""v3_batch_measure.py — 대조본 V3 배치의 «자체 값»과 두 대조를 잰다 (N059부터).

왜 스크립트인가: N059(첫 V3)를 **손으로** 쟀다. 같은 칸을 매 배치 손으로 다시 재면
  ⑴칸이 흔들리고 ⑵어느 칸을 빠뜨렸는지 나중에 못 안다. 오늘 H6에서 배운 것과 같은 형태 —
  ★**반복 점검은 조심이 아니라 도구로 내린다.**

⛔이 도구가 지키는 경계:
  · **V3 값만 낸다.** V2 종료값(클립 358·무수정 14·ko 11)과 **합산·차이 계산을 안 한다**.
    사전등록(KANBAN ①-23)대로 **V3 3배치(클립 60) 전에는 V2와 비교하지 않는다** —
    그래서 이 도구는 V2 수를 아예 읽지 않는다(읽으면 쓰게 된다).
  · 버킷은 **클립에 적힌 실제값**(`aug_creativity`)으로 건다. 의도(`pair_variety`)와
    어긋나면 클립 기록이 이긴다(v6_ingest_result와 동일 규칙 — 단일 진실원 재사용).
  · **단위를 셋 다 싣는다**(첫 클립 / 둘 다 / 하나라도 + 쌍 갈림). N059에서 곡 단위로만
    보면 gid 30605의 클립 역전이 가려졌다(실물).

사용: .venv/bin/python scripts/v3_batch_measure.py N059 N060 ...
      (인자 없으면 원장에서 대조본_칸=='V3'인 배치 전건)
"""
import json, glob, math, re, statistics, sys
sys.path.insert(0, 'scripts')
from v6_ingest_result import (  # noqa: E402 — 자(정규식·사상·중첩해제·상대칸)는 하나만 쓴다
    LEDGER, INBOX, gender_words, _peer_tokens, _norm_tokens, _drop_nested,
)

HANGUL = re.compile(r'[가-힣]')


def wilson(k, n, z=1.96):
    """Wilson 95% CI(%) — ★자를 바꾸지 않는다: 기존 기재(1/20 → 0.9~23.6)가 Wilson 값이다.
    Clopper-Pearson으로 갈아타면 같은 분자·분모에서 다른 구간이 나와 시계열이 끊긴다."""
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round(100 * max(0.0, c - m), 1), round(100 * min(1.0, c + m), 1)


def _phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def power_at(n, p0, p1, alpha=0.05):
    """단일비율 검정의 검정력(양측). ★2026-09-14 신설 — 이 칸이 없어서 사고가 났다.

    ⛔경위: 나는 판정선을 **클립 60**으로 박고 거기서 「내 예측 반증」을 선언했는데,
      **바로 다음 배치(N062)가 그 판정을 뒤집었다**(1/60=1.67% → 4/80=5.00%).
      뒤집힌 이유는 데이터가 아니라 **내 설계**다: 60클립의 검정력은 **31%**였다.
      ⇒ ★**내 판정선은 「가를 수 있는 표본」이 아니라 「내가 기다릴 수 있는 표본」으로
        정해졌다.** 그래서 판정을 찍을 때마다 검정력을 **같이** 찍는다 —
        숫자가 낮으면 「판정」이라 부르지 못하게.
    """
    if n <= 0:
        return 0.0
    za = 1.959963985
    z = (abs(p1 - p0) * math.sqrt(n) - za * math.sqrt(p0 * (1 - p0))) / math.sqrt(p1 * (1 - p1))
    return _phi(z)


def n_for(p0, p1, power=0.8):
    """검정력 `power`를 내는 표본수(단일비율·양측 α=.05)."""
    za, zb = 1.959963985, 0.8416212336
    return (za * math.sqrt(p0 * (1 - p0)) + zb * math.sqrt(p1 * (1 - p1))) ** 2 / (p1 - p0) ** 2


def clip_level(tags):
    """클립 단위 깨짐 + 길이비 층별. ★원장의 `클립별_판정` 순서는 통의 `rendered_sp` 순서와
    같다(적재기가 그 순서로 만든다) ⇒ 같은 첨자로 길이비와 짝지을 수 있다."""
    rec = json.load(open(LEDGER))['batches']
    rows = []
    for t in tags:
        byg = {g['gid']: g for g in rec[t]['성별어']}
        for _s, _pc, r in clips_of(t):
            g = byg.get(_s['id'])
            if not g:
                continue
            cj = g.get('클립별_판정') or []
            idx = [i for i, rr in enumerate(_pc['rendered_sp']) if rr is r]
            if not idx or idx[0] >= len(cj):
                continue
            rows.append({"gid": _s['id'], "판정": cj[idx[0]],
                         "길이비": r.get('길이비'), "batch": t})
    return rows


def clips_of(tag):
    fs = sorted(glob.glob(f'{INBOX}/**/sunolanguage_sunomusic_*_{tag}_생성결과.json',
                          recursive=True))
    if not fs:
        sys.exit(f'⛔{tag} 결과통 없음 — 미측정(「없다」가 아님)')
    b = json.load(open(fs[-1])); b = b.get('body', b)
    out = []
    for s in b['songs']:
        pcs = s.get('pair_clips')
        pc = pcs[0] if isinstance(pcs, list) else pcs
        if not pc:
            continue
        for r in pc['rendered_sp']:
            if r.get('aug_creativity') != 3:      # ★실제값으로만 건다
                continue
            out.append((s, pc, r))
    return out


def measure(tag):
    cl = clips_of(tag)
    if not cl:
        return None
    sp = [r for _, _, r in cl]
    ratios = [r.get('길이비') for r in sp if isinstance(r.get('길이비'), (int, float))]
    intact = sum(1 for r in sp if r.get('무수정'))
    ko = [r for r in sp if HANGUL.search(r.get('렌더입력SP') or '')]
    normed = sum(1 for r in sp if r.get('성별어_정규화') is not None)
    # 대조 ⑴ 사상: 그쪽 정규화 칸 ↔ 내 사상(같은 원형을 각자 접었을 때)
    map_bad = [(_s['id'], m) for _s, _pc, r in cl for m in [_peer_tokens(r)[1]] if m]
    # 대조 ⑵ 탐지: 그쪽 토큰 ↔ 내가 «SP 원문에서 직접» 찾은 토큰
    #   ★N059에서 처음 가동한 검사다 — 사상 대조는 「같은 원형을 어떻게 접었나」만 보므로
    #     상대가 **애초에 못 본/잘못 본** 토큰은 20/20 「일치」로 조용히 통과한다.
    det_bad = []
    for _s, _pc, r in cl:
        spx = r.get('렌더입력SP') or ''
        theirs = r.get('성별어_정규화')
        theirs = _drop_nested(_norm_tokens(theirs), spx) if theirs is not None \
            else _drop_nested(_norm_tokens(r.get('성별어')), spx)
        mine = set(gender_words(spx))
        if theirs != mine:
            det_bad.append((_s['id'], sorted(theirs), sorted(mine)))
    return {"tag": tag, "clips": len(sp), "무수정": intact, "길이비": ratios,
            "ko": [(_s['id'], len(r.get('렌더입력SP') or ''))
                   for _s, _pc, r in cl if HANGUL.search(r.get('렌더입력SP') or '')],
            "정규화칸": normed, "사상_불일치": map_bad, "탐지_불일치": det_bad,
            "songs": {_s['id'] for _s, _pc, _r in cl}}


def unit_counts(tags):
    """단위 3종 — 원장의 클립별 판정에서 읽는다(적재기가 이미 낸 값을 다시 세지 않는다)."""
    rec = json.load(open(LEDGER))['batches']
    first = both = any_ = split = pairs = 0
    for t in tags:
        for g in rec[t]['성별어']:
            pairs += 1
            cj = g.get('클립별_판정') or []
            if cj and cj[0] != '유지':
                first += 1
            if cj and all(x != '유지' for x in cj):
                both += 1
            if any(x != '유지' for x in cj):
                any_ += 1
            if g.get('쌍_갈림'):
                split += 1
    return pairs, first, both, any_, split


def main(tags):
    rec = json.load(open(LEDGER))['batches']
    if not tags:
        tags = [t for t, b in rec.items() if b.get('대조본_칸') == 'V3']
    print(f"=== 대조본 V3 자체 측정 (배치 {len(tags)}: {', '.join(tags)}) ===")
    print("⛔V2와 비교하지 않는다 — 사전등록대로 V3 3배치(클립 60) 전엔 판정 유보")
    acc = []
    for t in tags:
        m = measure(t)
        if not m:
            print(f"  ⚠{t}: V3 클립 0 — 이 배치는 V3가 아니다"); continue
        acc.append(m)
        rs = m['길이비']
        med = round(statistics.median(rs), 4) if rs else None
        over = sum(1 for x in rs if x > 1.0)
        print(f"\n  [{t}] 클립 {m['clips']} · 무수정 {m['무수정']}/{m['clips']}"
              f" · 길이비 중앙값 {med} (최소 {min(rs):.4f} / 최대 {max(rs):.4f}"
              f" · >1.0 이 {over}/{len(rs)})")
        print(f"       한글 재작성 {len(m['ko'])}클립 {m['ko'] or ''}"
              f" · 정규화 칸 {m['정규화칸']}/{m['clips']}")
        print(f"       대조⑴ 사상  불일치 {len(m['사상_불일치'])}/{m['clips']}"
              + (f" ⛔{m['사상_불일치']}" if m['사상_불일치'] else " ✅"))
        print(f"       대조⑵ 탐지  불일치 {len(m['탐지_불일치'])}/{m['clips']}"
              + (f" ⛔{m['탐지_불일치']}" if m['탐지_불일치'] else " ✅ (SP 원문 기준)"))
    if not acc:
        return
    tot = sum(m['clips'] for m in acc)
    rs = [x for m in acc for x in m['길이비']]
    pairs, first, both, any_, split = unit_counts([m['tag'] for m in acc])
    print(f"\n  ★V3 누적 — 클립 {tot} · 무수정 {sum(m['무수정'] for m in acc)}/{tot}"
          f" · 길이비 중앙값 {round(statistics.median(rs),4)} · >1.0 이 "
          f"{sum(1 for x in rs if x>1.0)}/{len(rs)} · 한글 {sum(len(m['ko']) for m in acc)}")
    print(f"     단위 3종(분모 {pairs}쌍): ⒜첫 클립 {first} · ⒝둘 다 {both} · "
          f"⒞하나라도 {any_} · 쌍 갈림 {split}")
    need = 60 - tot
    print(f"     사전등록 판정선 = V3 클립 60 ⇒ {'도달' if need <= 0 else f'{need}클립 부족(배치 {-(-need//20)}건)'}"
          f" · 그 전엔 V2와 비교 안 함")

    rows = clip_level([m['tag'] for m in acc])
    broke = [r for r in rows if r['판정'] != '유지']
    up = [r for r in rows if isinstance(r['길이비'], (int, float)) and r['길이비'] > 1.0]
    dn = [r for r in rows if isinstance(r['길이비'], (int, float)) and r['길이비'] <= 1.0]
    bu = sum(1 for r in up if r['판정'] != '유지')
    bd = sum(1 for r in dn if r['판정'] != '유지')
    lo, hi = wilson(len(broke), len(rows))
    print(f"\n  ★클립 단위 깨짐 = {len(broke)}/{len(rows)} = {100*len(broke)/len(rows):.2f}%"
          f" (Wilson CI {lo}~{hi}) {[(r['gid'], r['판정'], r['길이비']) for r in broke]}")
    print(f"     층별 — 늘어남(>1.0) {bu}/{len(up)} · 안 늘어남(≤1.0) {bd}/{len(dn)}"
          f" · 늘어난 비율 {len(up)}/{len(rows)} = {100*len(up)/len(rows):.1f}%")
    if need <= 0:
        print("\n  ■ 사전등록 판정 (KANBAN ①-23 — 판정선 도달했으므로 여기서만 V2 기저를 쓴다)")
        # ★2026-09-14 개정 — 「실측 비율판」을 **판정에서 뺀다**(참고로만 찍는다).
        #   ⛔경위: 두 판(등록 25% / 실측 비율)이 N063에서 **처음 갈렸다**
        #     — 등록판은 검정력 43%로 「부르지 않음」, 실측판은 67%로 「반증」.
        #   ⇒ 갈리는 순간 **내가 유리한 판을 고를 수 있는 구조**가 된다. 그게 창 옮기기다.
        #   ★더 근본: 실측 비율판의 예상값은 **데이터가 커질 때마다 바뀐다**(움직이는 표적).
        #     같은 데이터로 예측을 만들고 그 데이터로 판정하면 순환이다.
        #   ⇒ 판정은 **등록값 하나로만** 한다. 실측 비율은 「등록 가정이 얼마나 빗나갔나」를
        #     보는 참고 칸으로 남긴다(지우지 않는다 — 지우면 빗나간 것을 못 본다).
        for name, share in (("등록 가정 25%[판정]", 0.25),
                            ("실측 비율[참고·비판정]", len(up) / len(rows))):
            exp = share * 21.7 + (1 - share) * 5.7        # V2 층별 기저(등록값)
            pw = power_at(len(rows), 0.057, exp / 100)
            need_n = n_for(0.057, exp / 100)
            out = not (lo <= exp <= hi)
            # ★2026-09-14 재개정 — 검정력이 모자라면 **「반증/유지」 낱말을 아예 찍지 않는다.**
            #   ⛔직전 판은 「예상은 CI 밖 → 반증」과 「⛔「판정」이라 부르지 않는다」를
            #     **같은 화면에 나란히** 찍었다. 읽는 사람(나 포함)은 앞 낱말을 집는다.
            #   ★이게 내 메모리에 적힌 「도구가 대신 단정한다(고정 문구)」의 실물이다 —
            #     경고를 덧붙이는 것으로는 안 되고, **낱말 자체를 안 내야** 한다.
            if "참고" in name:
                verdict = ""
            elif pw < 0.5:
                verdict = f" → ⛔미판정(검정력 {100*pw:.0f}% < 50%)"
            else:
                verdict = f" → {'반증' if out else '유지'}"
            print(f"     {name}: 예상 {exp:.1f}% = {exp*len(rows)/100:.1f}건"
                  f" ↔ 귀무 5.7% = {5.7*len(rows)/100:.1f}건"
                  f" ↔ 실측 {100*len(broke)/len(rows):.2f}% = {len(broke)}건"
                  f" ⇒ 예상은 CI {'밖' if out else '안'}{verdict}"
                  + f" · 귀무는 CI {'밖' if not (lo <= 5.7 <= hi) else '안'}")
            print(f"       ★검정력 = {100*pw:.0f}% (n={len(rows)}) · 검정력 80%에 필요한 클립"
                  f" = {need_n:.0f}(배치 {need_n/20:.0f}건)"
                  + ("  ⛔CI 밖이어도 「반증」이라 쓰지 않는다 — 등록선(클립 309)까지 수만 적는다"
                     if pw < 0.5 and "참고" not in name and out else ""))
        print("     ⛔예상·귀무 둘 다 CI 밖이면 「예측이 틀렸다」와 「기저 자체가 다르다」가 같이 참이다"
              " — 하나만 적지 않는다.")


if __name__ == '__main__':
    main(sys.argv[1:])
