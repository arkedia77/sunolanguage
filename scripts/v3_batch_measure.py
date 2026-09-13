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
import json, glob, re, statistics, sys
sys.path.insert(0, 'scripts')
from v6_ingest_result import (  # noqa: E402 — 자(정규식·사상·중첩해제·상대칸)는 하나만 쓴다
    LEDGER, INBOX, gender_words, _peer_tokens, _norm_tokens, _drop_nested,
)

HANGUL = re.compile(r'[가-힣]')


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


if __name__ == '__main__':
    main(sys.argv[1:])
