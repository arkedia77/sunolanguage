#!/usr/bin/env python3
"""V_PILOT 하베스트 게이트 — 코사인(주)+lang가드+near-dup jaccard(보조)+dedup. 통과율 실측."""
import json,re
from sentence_transformers import SentenceTransformer
import numpy as np
m=SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
def cos(a,b):
    va,vb=m.encode([a,b]); return float(np.dot(va,vb)/(np.linalg.norm(va)*np.linalg.norm(vb)))
def toks(t): return set(re.findall(r"[가-힣a-zA-Z0-9]+",t.lower()))
def jac(a,b):
    A,B=toks(a),toks(b); return len(A&B)/len(A|B) if A|B else 0
def kr_ratio(t):
    kr=len(re.findall(r"[가-힣]",t)); alpha=len(re.findall(r"[a-zA-Z]",t))
    return kr/(kr+alpha) if (kr+alpha) else 0

d=json.load(open("data/lyric_variations/V_PILOT_harvest_results.json"))
res=d.get("results") or d.get("harvest") or d
rows=[]; seen_variants=set()
COS_LO,COS_HI=0.70,0.985
stats={"total":0,"accept":0,"rej_lang":0,"rej_cos_low":0,"rej_dup":0,"rej_jac":0,"rej_seen":0}
# 중복 시드 dedup: 동일 original은 1회만
seen_orig=set()
for r in res:
    orig=r.get("original","")
    variants=r.get("variants",[])
    if not variants: continue
    if orig in seen_orig:  # 발견2: 중복시드 스킵
        stats["rej_dup"]+=len(variants); continue
    seen_orig.add(orig)
    for rank,v in enumerate(variants,1):
        stats["total"]+=1
        gate="accept"; c=None
        if kr_ratio(v)<0.5:  # 발견1: 영어 드리프트 lang가드
            gate="rej_lang"
        elif v.strip()==orig.strip() or v in seen_variants:
            gate="rej_seen"
        elif jac(orig,v)>=0.9:  # near-dup 보조컷
            gate="rej_jac"
        else:
            c=cos(orig,v)
            if c<COS_LO: gate="rej_cos_low"
            elif c>=COS_HI: gate="rej_jac"  # near-dup(의미)
        stats[gate if gate in stats else "accept"]+=1
        if gate=="accept":
            seen_variants.add(v)
            rows.append({"seed_id":r.get("seed_id"),"source_song_id":r.get("source_song_id"),
                         "source_chunk_id":r.get("source_chunk_id"),"original":orig,"variant":v,
                         "variant_rank":rank,"lang":"ko","section_tag":r.get("section_tag"),
                         "cosine_to_src":round(c,3) if c else None,"gate_status":"accepted"})
print("=== V_PILOT 게이트 결과 ===")
print(f"  총 변형: {stats['total']}")
print(f"  ✅채택: {stats['accept']}")
print(f"  ❌영어드리프트(lang): {stats['rej_lang']}")
print(f"  ❌의미이탈(cos<0.70): {stats['rej_cos_low']}")
print(f"  ❌near-dup(jac≥0.9/cos≥0.985): {stats['rej_jac']}")
print(f"  ❌원문/중복: {stats['rej_seen']}")
print(f"  ⊘중복시드 스킵: {stats['rej_dup']}")
acc=stats['accept']; base=stats['total']-stats['rej_dup']
print(f"\n  통과율(중복시드 제외 분모): {acc}/{base} = {100*acc/base:.0f}%")
if rows:
    cs=[r['cosine_to_src'] for r in rows if r['cosine_to_src']]
    import statistics
    print(f"  채택분 코사인 평균 {statistics.mean(cs):.3f} / 범위 {min(cs):.3f}~{max(cs):.3f}")
json.dump({"batch":"V_PILOT","gate":"cosine0.70-0.985+lang가드+dedup","stats":stats,
           "accepted":rows},open("data/lyric_variations/V_PILOT_gated.json","w"),ensure_ascii=False,indent=2)
print(f"\n저장: data/lyric_variations/V_PILOT_gated.json ({len(rows)} accepted)")
