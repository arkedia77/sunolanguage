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
        ask = sorted(set(w.lower() for w in GEN.findall(om[s['title']])))
        got = pc['rendered_sp'][0].get('성별어') or []
        # ★2026-09-12 수리(자적발) — 옛 사다리엔 «확장» 칸이 없어서 발주 ['male'] →
        #   렌더 ['male','tenor'](=발주어 유지 + 음역어 추가)가 **'축소'**로 찍혔다
        #   (N041 gid 30419 실측). 늘어난 걸 줄었다고 적는 라벨이다. ⛔깨짐 수(소실+역전)는
        #   영향 없으나 라벨은 틀렸다 ⇒ 발주어가 전부 남아 있고 더 붙은 경우는 '확장'.
        verdict = ('유지' if sorted(got) == ask else
                   '소실' if not got else
                   '역전' if not set(got) & set(ask) else
                   '확장' if set(ask) <= set(got) else '축소')
        gen.append({"gid": s['id'], "발주": ask, "v4": got, "판정": verdict})
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
    print(f"   성별어 {cnt} ⇒ 깨짐 {broke}/{n} ({broke/n*100:.1f}%) "
          f"※성별어는 대조본 판정이라 버킷이 섞여 있다 — 경계 후 재분리 필요")

if __name__ == '__main__':
    main(sys.argv[1])
