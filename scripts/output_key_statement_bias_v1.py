#!/usr/bin/env python3
"""출력층 키 서술 편향 실측 v1 — 「Suno 자기분석의 조성 서술을 근거로 쓸 수 있나」

계기: leomusic-trot 축H 실측(08-23)의 ★평탄화 발견
      (「modulating to Y」를 쓰면 전곡이 Y로 렌더된다 — 무시가 아니라 도착조성으로 이동).
      오디오 없이 텍스트 층으로 가를 수 있다고 봤다 —
        「무시」 가설  ⇒ 출력 조성 = **출발조성**
        「평탄화」가설 ⇒ 출력 조성 = **도착조성**
      우리 출력층(Suno 자기분석 SP)이 조성을 말하므로 대조가 선다.

★결과: 못 쓴다. **기저를 먼저 재서 막혔다.** 아래 분포 참조.
   ⇒ 이 스크립트의 산출은 「전조 판정」이 아니라 **「판정 도구가 못 쓴다는 증거」**다.

생성 0 · 크레딧 0.
"""
import json, re, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MERGED = ROOT / "data/reanalysis_v2/merged_4values.json"
OUT = ROOT / "data/reanalysis_v2/output_key_statement_bias_v1.json"

# 지시군 = w030_harmony_probe.py PRESCRIBED 전수와 동일(육안 감사 확정본)
PRESCRIBED = {"1135","1146","1386","1396","1427","1445","1446","1507","1508","1535","1539","1547",
 "1553","1558","1580","1630","1644","1660","1733","1766","10021","10464","10466","10472","1100",
 "1107","1149","1399","1432","1433","1451","S018_16","123","133","1126","1485","1405","1414","1415","10469"}

KEYSTATE = re.compile(r"\bkey (?:of |is |signature is )?([A-G](?:#|b|♯|♭)?)\s*[- ]?\s*(major|minor|maj|min)\b", re.I)

def norm(k, q): return f"{k[0].upper()}{k[1:]} {q.lower()[:5]}"

data = json.loads(MERGED.read_text())
dist, per_song = collections.Counter(), {}
n_with = 0
for m in data:
    sid = str(m["song_id"])
    sp = " ".join((r.get("sp") or "") for r in m["suno_reanalysis"])
    hits = KEYSTATE.findall(sp)
    if hits:
        n_with += 1
        v = norm(*hits[0]); dist[v] += 1; per_song[sid] = v

top3 = dist.most_common(3)
share3 = sum(v for _, v in top3) / n_with if n_with else None

# 지시군에서 계획이 서로 다른데 출력 서술이 같은 실물 예시
examples = []
for m in data:
    sid = str(m["song_id"])
    if sid not in PRESCRIBED or sid not in per_song: continue
    ins = m["leomusic_original"].get("sp") or ""
    seg = [s for s in re.split(r"(?<=[.])\s+", ins) if re.search(r"modulat\w*", s, re.I)]
    if seg:
        examples.append({"song_id": sid, "입력_지시문": seg[0].strip()[:160], "출력층_키_서술": per_song[sid]})

out = {
 "무엇": "Suno 자기분석 SP의 조성 서술이 조성 근거로 쓸 수 있는지 — 기저 분포로 판정",
 "계기": "leomusic-trot 축H(08-23) 평탄화 발견을 우리 코퍼스 텍스트 층으로 검산하려던 시도",
 "재현": "scripts/output_key_statement_bias_v1.py",
 "모집단": {"곡": len(data), "출력층에_키_서술_있는_곡": n_with,
          "비율": round(n_with / len(data), 3) if data else None},
 "★분포": {"고유_조성_종수": len(dist), "전체": dist.most_common(),
         "상위3": top3, "상위3_점유": round(share3, 3) if share3 else None},
 "★판정": ("**조성 근거로 쓸 수 없다.** 24조성 중 %d종만 나오고 상위 3종이 %.0f%%다. "
         "음악 분포가 아니라 추정기 쏠림이다. ⇒ 텍스트 층으로는 「무시 ↔ 평탄화」를 못 가른다 — 오디오가 필요하다."
         % (len(dist), (share3 or 0) * 100)),
 "★실물_예시(계획은 서로 다른데 출력 서술이 같다)": examples[:12],
 "★이_산출이_못_하는_것": [
   "Suno가 조성을 **틀리게 들었다**는 뜻이 아니다 — 우리가 **그 서술로 판정할 수 없다**는 뜻이다.",
   "렌더의 실제 조성은 이 자료로 전혀 모른다. 오디오 크로마 실측이 있어야 한다.",
   "우리 대량 오디오는 현재 `/Volumes/LEO` 미마운트로 심링크 4개가 댕글링이라 못 돌린다.",
 ],
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "★실물_예시(계획은 서로 다른데 출력 서술이 같다)"},
                 ensure_ascii=False, indent=1))
print("\n예시:")
for e in out["★실물_예시(계획은 서로 다른데 출력 서술이 같다)"][:6]:
    print(f"  {e['song_id']:>7}  출력={e['출력층_키_서술']:<9} | {e['입력_지시문'][:90]}")
print("→", OUT.relative_to(ROOT))
