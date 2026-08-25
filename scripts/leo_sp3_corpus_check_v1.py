#!/usr/bin/env python3
"""LEO 제시 SP 3건 ↔ 우리 코퍼스 대조 v1 (2026-08-25)

물음: 「기존 우리 것과 다른 점」.

★설계 원칙 — 기저 없이는 비율을 내지 않는다.
   어휘 접지율은 **같은 조회기로 우리 입력층 SP를 대조군**으로 돌려 견준다.
   (1차 시도에서 구 접지율 0.056을 보고 「낯설다」로 읽을 뻔했는데,
    우리 SP를 같은 조회기에 넣으니 중앙값 0.069였다 — 조회기 특성이지 SP 특성이 아니었다.)

★못 하는 것: 「이 SP가 잘 먹히나」는 못 잰다(생성 필요·B-2).
   여기서 나오는 것은 **「우리 540곡 코퍼스에 있는 말인가」**뿐이다.
"""
import json, re, sqlite3, random, statistics, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEX = ROOT / "data/reanalysis_v2/lexical_index.sqlite"
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "data/collection/leo_sp3_input_20260825.json")
OUT = ROOT / "data/collection/leo_sp3_corpus_check_v1.json"

STOP = set("a an the and or with in on of at to for as by is are be into then through "
           "yet strong throughout underneath end central".split())
NOISE = re.compile(r"^\d+$")

con = sqlite3.connect(LEX)
def pool(cond):
    return " || ".join(r[0].lower() for r in con.execute(
        f"SELECT coalesce(entity,'')||' '||coalesce(sentence,'')||' '||coalesce(modifiers,'') FROM entries WHERE {cond}"))
OUTP, INPP = pool("source!='leomusic_sp_full'"), pool("source='leomusic_sp_full'")
OW = set(re.findall(r"[a-z0-9][a-z0-9'\-]*", OUTP))
IW = set(re.findall(r"[a-z0-9][a-z0-9'\-]*", INPP))
ours = [r[0] for r in con.execute("SELECT DISTINCT sentence FROM entries WHERE source='leomusic_sp_full' AND sentence IS NOT NULL")]
suno = [r[0] for r in con.execute("SELECT DISTINCT sentence FROM entries WHERE source='suno_sp_full' AND sentence IS NOT NULL")]

words = lambda t: [w for w in re.findall(r"[a-z0-9][a-z0-9'\-]*", t.lower()) if w not in STOP]
phr = lambda t: [p.strip() for p in re.split(r"[,.]", t) if p.strip()]
tc = lambda t: (lambda w: round(sum(1 for x in w if x[0].isupper()) / len(w), 3) if w else None)(re.findall(r"[A-Za-z][a-z]+", t))

# ── 대조군: 우리 입력층 SP 120건을 같은 조회기로 ────────────────────────
random.seed(7)
samp = random.sample(ours, min(120, len(ours)))
bw = [sum(1 for x in set(words(s)) if x in OW) / len(set(words(s))) for s in samp if words(s)]
bp = [sum(1 for x in phr(s) if x.lower() in OUTP) / len(phr(s)) for s in samp if phr(s)]
q = lambda v, f: sorted(v)[int(len(v) * f)]

AXES = {
 "녹음환경·공간 서술": r"close-mic|close mic|room tone|bathroom|tile|miked|recorded in|phone-record|field record|live room|basement|garage|hallway|cassette|vinyl|tape hiss|tape warmth|lo-?fi record",
 "시간전개 서술": r"\b(opens? with|begins? with|starts? with|leading into|building into)\b",
 "종결 지시": r"(hard cut|cut to silence|abrupt (end|stop)|fades? out at the end|ends? (on|with))",
 "BPM 명시": r"\b\d{2,3}\s*bpm\b",
 "콜론 헤더": r"[A-Z][a-z]+:",
}
def rate(p, pat):
    c = re.compile(pat, re.I)
    n = sum(1 for x in p if c.search(x))
    return {"n": n, "모집단": len(p), "비율": round(n / len(p), 3)}

sps = json.loads(SRC.read_text())
per = {}
for k, v in sps.items():
    ws = sorted(set(words(v)))
    a = [w for w in ws if w not in OW and w in IW]
    b = [w for w in ws if w not in OW and w not in IW and not NOISE.match(w)]
    per[k] = {
      "자수": len(v), "구": len(phr(v)), "고유낱말": len(ws),
      "Title_Case_비율": tc(v), "콜론_헤더": bool(re.search(r"[A-Z][a-z]+:", v)),
      "출력층_낱말_접지율": round(sum(1 for x in ws if x in OW) / len(ws), 3),
      "출력층_구_접지": f"{sum(1 for x in phr(v) if x.lower() in OUTP)}/{len(phr(v))}",
      "★ⓐ우리는_쓰는데_Suno출력층엔_없음": a,
      "★ⓑ양쪽_다_없음(새것)": b,
      "축_적중": {n: bool(re.search(p, v, re.I)) for n, p in AXES.items()},
    }

out = {
 "무엇": "LEO 제시 SP 3건 ↔ 우리 코퍼스(540곡) 대조 — 어휘 접지·형태",
 "재현": "scripts/leo_sp3_corpus_check_v1.py", "원문": str(SRC.relative_to(ROOT)),
 "★생성": "0건 · 크레딧 0",
 "모집단": {"우리 입력층 SP": len(ours), "Suno 출력층 SP": len(suno),
          "Suno 출력층 총 문자수": sum(len(x) for x in suno)},
 "★대조군(같은 조회기·우리 SP 120건)": {
   "낱말_출력층_접지율_중앙값": round(statistics.median(bw), 3),
   "사분범위": [round(q(bw, .25), 3), round(q(bw, .75), 3)],
   "구_출력층_접지율_중앙값": round(statistics.median(bp), 3),
   "★읽는_법": "낱말 접지율이 사분범위 안이면 「우리 것과 다르지 않다」. 구 접지율은 조회기 특성상 원래 0에 가깝다 — 여기서 낮다고 낯선 게 아니다.",
 },
 "형태_기저": {n: {"우리_입력층": rate(ours, p), "Suno_출력층": rate(suno, p)} for n, p in AXES.items()},
 "Title_Case_기저": {"우리_입력층_중앙값": statistics.median([tc(x) or 0 for x in ours]),
                 "Suno_출력층_중앙값": statistics.median([tc(x) or 0 for x in suno]),
                 "≥0.9인 SP": {"우리": sum(1 for x in ours if (tc(x) or 0) >= .9),
                             "Suno": sum(1 for x in suno if (tc(x) or 0) >= .9)}},
 "SP별": per,
 "★합집합_새_낱말": sorted({w for v in per.values() for w in v["★ⓑ양쪽_다_없음(새것)"]}),
 "★이_대조가_못_하는_것": [
   "「이 SP가 잘 먹히나」는 못 잰다 — 생성 필요(B-2).",
   "미접지 = 「우리 540곡에서 안 나왔다」이지 「Suno가 모른다」가 아니다.",
   "문자열 대조라 어형 변화는 부분적으로만 잡힌다.",
   "ⓐ군이 큰 것은 이 SP들의 성질이 아니라 **Suno 출력층 전반의 성질**이다(구조강·감성약).",
 ],
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps({k: out[k] for k in ("모집단", "★대조군(같은 조회기·우리 SP 120건)", "Title_Case_기저")}, ensure_ascii=False, indent=1))
print("\n형태 축 (우리 / Suno출력 / SP1·2·3):")
for n in AXES:
    a, b = out["형태_기저"][n]["우리_입력층"], out["형태_기저"][n]["Suno_출력층"]
    leo = "".join("O" if per[k]["축_적중"][n] else "·" for k in sps)
    print(f"  {n:<16} {a['n']:>4}/{a['모집단']} ({a['비율']:.2f})   {b['n']:>4}/{b['모집단']} ({b['비율']:.2f})   {leo}")
print("\nSP별:")
for k, v in per.items():
    print(f"  {k} {v['자수']}자 · TitleCase {v['Title_Case_비율']} · 낱말접지 {v['출력층_낱말_접지율']} · 새것 {len(v['★ⓑ양쪽_다_없음(새것)'])}")
print("\n★합집합 새 낱말", len(out["★합집합_새_낱말"]), ":", ", ".join(out["★합집합_새_낱말"]))
print("→", OUT.relative_to(ROOT))
