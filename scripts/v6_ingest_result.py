#!/usr/bin/env python3
"""v6 생성결과 수령 → 입력층 대장 갱신 (N0xx 배치 공통).

왜 스크립트인가: 배치 20개를 손으로 같은 집계를 반복하면 자가 흔들린다.
                 ★09-11 leomusic2 적발분(파이프가 실패를 삼킴)과 같은 계열 —
                 반복 절차는 규율이 아니라 도구로 고정한다.
사용: .venv/bin/python scripts/v6_ingest_result.py N027
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
    v4, gen = [], []
    for s in songs:
        pc = s['pair_clips'][0] if isinstance(s.get('pair_clips'), list) else s.get('pair_clips')
        if not pc: continue
        v4 += pc['rendered_sp']
        ask = sorted(set(w.lower() for w in GEN.findall(om[s['title']])))
        got = pc['rendered_sp'][0].get('성별어') or []
        verdict = ('유지' if sorted(got) == ask else
                   '소실' if not got else
                   '역전' if not set(got) & set(ask) else '축소')
        gen.append({"gid": s['id'], "발주": ask, "v4": got, "판정": verdict})
    rec['batches'][tag] = {
        "n_songs": len(songs),
        "V0": {"무수정": f"{sum(1 for r in v0 if r['무수정'])}/{len(v0)}",
               "길이비": sorted({r['길이비'] for r in v0})},
        "V4": {"무수정": f"{sum(1 for r in v4 if r['무수정'])}/{len(v4)}" if v4 else "0/0",
               "길이비_최소": min((r['길이비'] for r in v4), default=None),
               "길이비_최대": max((r['길이비'] for r in v4), default=None)},
        "성별어": gen}
    json.dump(rec, open(LEDGER, 'w'), ensure_ascii=False, indent=2)
    t0 = t0u = t4 = t4u = 0; cnt = {'유지': 0, '소실': 0, '역전': 0, '축소': 0}
    for bb in rec['batches'].values():
        a, x = bb['V0']['무수정'].split('/'); t0u += int(a); t0 += int(x)
        a, x = bb['V4']['무수정'].split('/'); t4u += int(a); t4 += int(x)
        for g in bb['성별어']: cnt[g['판정']] += 1
    n = sum(x['n_songs'] for x in rec['batches'].values())
    broke = cnt['소실'] + cnt['역전']
    print(f"★누적 {len(rec['batches'])}배치({n}곡): V0 무수정 {t0u}/{t0} · V4 {t4u}/{t4} · "
          f"성별어 {cnt} ⇒ 깨짐 {broke}/{n} ({broke/n*100:.1f}%)")

if __name__ == '__main__':
    main(sys.argv[1])
