#!/usr/bin/env python3
"""코퍼스 확장 대장 v1 — 「무엇을 더 재분석하면 코퍼스가 실제로 커지는가」.

★주 임무(코퍼스셋 관리)로 복귀해 만든 첫 산출.
전제: 재분석 = **0cr 실측 확정**(sunomusic 08-03 AWARE05 회신 — upload_audio 전후
      monthly_remaining 6070→6070 Δ0, 9클립 전량 처리 후도 Δ0. 신규생성·커버·리믹스 아님).

모집단 = `agent-comm:projects/sunomusic/exchange/aware_clip_index_20260803.jsonl.gz`
        (gid·source_project·batch·title·genre_design·bpm·status·uuid·take·**cdn_mp3**)
★이 대장은 **08-03 기준**이라 이후 생산분은 안 들어 있다 — 최신본 재발급이 필요하다.

⚠키 주의: 대장의 `uuid` = **생성 클립**, 코퍼스의 `suno_reanalysis[].uuid` = **재분석 클립**.
   둘은 다른 값이라 uuid로 대조하면 교집합이 0으로 나온다. **대조는 gid로 한다.**
"""
import json, gzip, re
from collections import Counter, defaultdict

REG='/Users/purple/projects/agent-comm/projects/sunomusic/exchange/aware_clip_index_20260803.jsonl.gz'
COR='data/reanalysis_v2/merged_4values.json'
OUT='data/reanalysis_v2/corpus_expansion_ledger_v1.json'

FAMS=['trot','트로트','pansori','국악','gukak','cn_','guofeng','boom bap','trip-hop','rap','hip',
      'house','techno','edm','metal','classic','orchestr','ambient','jazz','funk','disco','soul',
      'r&b','folk','rock','ballad','lo-fi','lofi','bossa','country','pop']
def fam(g):
    g=(g or '').lower()
    for k in FAMS:
        if k in g: return {'트로트':'trot','국악':'gukak','lofi':'lo-fi','guofeng':'cn_'}.get(k,k)
    return (g.split('/')[0].strip()[:22] or '미정')

def main():
    rows=[json.loads(l) for l in gzip.open(REG,'rt')]
    reg={}
    for r in rows: reg.setdefault(r['gid'],r)
    takes=Counter(r['gid'] for r in rows)
    cor=json.load(open(COR))
    have={int(s['song_id']) for s in cor if str(s['song_id']).isdigit()}
    cor_fam=Counter(fam(s.get('genre')) for s in cor)
    cor_inputs=sum(1 for s in cor if (s.get('leomusic_original') or {}).get('lyrics'))

    miss=[g for g in reg if g not in have]
    by_proj=Counter(reg[g]['source_project'] for g in miss)
    by_fam=Counter(fam(reg[g].get('genre_design')) for g in miss)

    # 우선순위: ⑴코퍼스 0~소수인 장르族 ⑵코퍼스 미진입 프로젝트 ⑶배치 단위 묶음
    prio=[]
    for f,n in by_fam.most_common():
        c=cor_fam.get(f,0)
        if n>=10:
            ratio = n/(c+1)
            prio.append({'장르族':f,'코퍼스_보유':c,'미재분석':n,'배수':round(ratio,1)})
    prio.sort(key=lambda x:-x['배수'])

    tranche=defaultdict(list)
    for g in miss:
        r=reg[g]; f=fam(r.get('genre_design'))
        c=cor_fam.get(f,0)
        if c==0 or (f=='trot' and c<20):
            tranche[f].append({'gid':g,'project':r['source_project'],'batch':r.get('batch'),
                               'title':r.get('title'),'genre_design':r.get('genre_design'),
                               'takes':takes[g],'cdn_mp3':bool(r.get('cdn_mp3'))})
    t1=sorted([x for f in tranche for x in tranche[f]], key=lambda x:(x['project'],x['batch'] or '',x['gid']))

    out={
     '무엇':'코퍼스 확장 대장 v1 — 재분석하면 실제로 코퍼스가 커지는 곡의 목록과 우선순위',
     '날짜':'2026-08-27','작성':'sunolanguage','재현':'scripts/corpus_expansion_ledger_v1.py',
     '★비용':'재분석 = 0cr 실측 확정(sunomusic 08-03 AWARE05 회신: upload_audio 전후 monthly_remaining Δ0, 9클립 전량 후도 Δ0). '
             '생성 아님 — 업로드+Describe Your Audio 자동 서술.',
     '★모집단':{'대장':REG,'기준일':'2026-08-03(★스테일 — 이후 생산분 미포함)',
                '고유_gid':len(reg),'클립':len(rows),'cdn_mp3_보유':sum(1 for r in rows if r.get('cdn_mp3'))},
     '★현재_코퍼스':{'곡':len(cor),'그중_입력가사_보유':cor_inputs,
                     '★입력_결손':len(cor)-cor_inputs,
                     '대장과_gid_교집합':len(have & set(reg))},
     '★격차':{'미재분석_곡':len(miss),'상한':len(cor)+len(miss),
              '프로젝트별':dict(by_proj.most_common()),
              '★코퍼스_진입_프로젝트':'leomusic 148 · leomusic2 7 — **나머지 전 프로젝트 0곡**'},
     '★장르_우선순위(배수=미재분석/(보유+1))':prio[:20],
     '★1차_묶음(코퍼스 0곡 장르 + 트로트)':{'곡수':len(t1),'목록':t1},
     '★반입_규격':{'경로':'data/reanalysis_v2/incoming/{배치}_reanalysis_{YYYYMMDD}.json',
                   '필드':'gid · suno_uuid(재분석 클립) · suno_sp · suno_lyrics · suno_genre · suno_title',
                   '★입력층_동봉_필수':'`leomusic_sp`/`leomusic_lyrics` — 이걸 비우면 **짝 대조군에서 빠진다**. '
                                      '종전 BATCH_C 60건이 그렇게 빠졌다(V33X01 반입서 자인).',
                   '병합기':'scripts/merge_batch_reanalysis.py <회신.json> --batch C [--execute]'},
     '★이_대장이_못_하는_것':[
       '대장이 **08-03 기준**이라 8월 하순 생산분이 안 들어 있다 — 최신본을 받아야 격차가 확정된다.',
       '`genre_design`은 **설계 라벨**이지 관측이 아니다. 장르 공백 판정은 설계 기준이고, 렌더 실물과 다를 수 있다.',
       '입력층(`leomusic_sp`/`leomusic_lyrics`)은 **각 프로듀서 프로젝트**가 갖고 있다 — 우리 손에 없는 것이 다수.',
       '재분석 0cr은 sunomusic 실측이지 **내가 잰 값이 아니다**. 대량 처리 시 재확인이 필요하다.',
       '★병목은 크레딧이 아니라 **sunomusic의 앱 작업량**이다. 2,811곡을 한 번에 요청하지 않는다.',
     ],
    }
    json.dump(out,open(OUT,'w'),ensure_ascii=False,indent=1)
    print('WROTE',OUT)
    print('미재분석',len(miss),'· 상한',len(cor)+len(miss),'· 1차 묶음',len(t1),'곡')
    print('장르 우선순위 상위 8:')
    for p in prio[:8]: print('  ',p)
    print('1차 묶음 프로젝트별:',Counter(x['project'] for x in t1).most_common())

if __name__=='__main__': main()
