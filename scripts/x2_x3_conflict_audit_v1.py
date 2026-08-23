#!/usr/bin/env python3
"""X2·X3 검산 v1 — X1과 같은 두 축으로 대장 §3의 나머지 2건을 검산한다.

축 ⓐ **대상 일치**: 양쪽이 같은 물건을 말하고 있나
축 ⓑ **근거 종류·층 일치**: 존재/빈도 · 출력층/입력준수 가 같나

X2 = 「key:value 브라켓 — 3경로 수렴」
X3 = 「소괄호 — 외부끼리 정면 모순, 우리 실측이 기여」

생성 0 · 크레딧 0 · 새 수집 0 (리포 내 기존 자료만).
"""
import json, re, sqlite3, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEX = ROOT / "data/reanalysis_v2/lexical_index.sqlite"
OUT = ROOT / "data/metatag_external/x2_x3_conflict_audit_v1.json"

KV = re.compile(r"([A-Za-z][A-Za-z ]{1,24}):\s*([^,;\)\]]{1,30})")
NUMV = re.compile(r"^\s*\d+\s*%?\s*$")

con = sqlite3.connect(LEX)
rows = con.execute("SELECT source,song_id,sentence,entity,modifiers FROM entries").fetchall()
def blob(r): return " ".join(x for x in (r[3], r[2], r[4]) if x)
brk = [r for r in rows if r[0] in ("bracket_entity", "stems_bracket")]   # Suno 출력층 브라켓
inp = [r for r in rows if r[0] == "leomusic_sp_full"]                   # 우리 입력층 SP

# ── X2-⑴ 출력층 key:value 를 「콜론+숫자」와 「콜론+낱말」로 갈라 센다 ──────
def split_kv(rs):
    num, word, keys_num, keys_word = 0, 0, collections.Counter(), collections.Counter()
    for r in rs:
        for m in KV.finditer(blob(r)):
            k = m.group(1).strip().lower(); v = m.group(2).strip()
            if k in ("http", "https"): continue
            if NUMV.match(v): num += 1; keys_num[k] += 1
            else:             word += 1; keys_word[k] += 1
    return {"콜론+숫자": num, "콜론+낱말": word,
            "숫자형_키": keys_num.most_common(10), "낱말형_키": keys_word.most_common(10)}

x2_out, x2_in = split_kv(brk), split_kv(inp)

# ── X2-⑵ 경로2가 정말 다른 대상인가 — 맨 명찰 [Male Vocal] 계열 실측 ────────
def count_exact(rs, needle):
    n = re.compile(r"(?<![a-z])" + re.escape(needle) + r"(?![a-z])", re.I)
    songs = {r[1] for r in rs if n.search(blob(r))}
    return {"엔트리": sum(1 for r in rs if n.search(blob(r))), "곡": len(songs)}

labels = ["male vocal", "female vocal", "spoken", "male", "female"]
x2_label = {L: {"출력층_브라켓": count_exact(brk, L), "입력층_SP": count_exact(inp, L)} for L in labels}

# ── X3 소괄호 누출 — 우리 4클립 ASR 전수에 지시어가 남았나 ────────────────
asr_files = ["data/vd_duet3/VD_final_asr.json", "data/vd_duet3/VD3_v11_asr.json",
             "data/vd_duet3/VD3_v11_asr_musical.json"]
def texts(o):
    if isinstance(o, dict):
        for v in o.values(): yield from texts(v)
    elif isinstance(o, list):
        for v in o: yield from texts(v)
    elif isinstance(o, str): yield o
x3_leak = {}
for f in asr_files:
    p = ROOT / f
    if not p.exists(): continue
    d = json.loads(p.read_text())
    t = " ".join(texts(d))
    x3_leak[f] = {
        "클립키": list(d) if isinstance(d, dict) else None,
        "전사_문자수": len(t),
        "라틴문자_토큰": sorted(set(re.findall(r"[A-Za-z]{2,}", t)))[:20],
        "spoken_음차_적중": re.findall(r"스포[가-힣]*|포큰|spoken", t, re.I),
    }

out = {
 "무엇": "X2·X3 검산 v1 — 대장 §3의 나머지 2건을 X1과 같은 두 축(대상 일치·근거 종류/층 일치)으로 검산",
 "재현": "scripts/x2_x3_conflict_audit_v1.py",
 "★생성": "0건 · 크레딧 0 · 새 수집 0",
 "모집단": {"출력층_브라켓_엔트리": len(brk), "입력층_SP_엔트리": len(inp),
          "출력층_브라켓_곡": len({r[1] for r in brk}), "입력층_SP_곡": len({r[1] for r in inp})},
 "X2": {
   "★쟁점": "hookgenius 「콜론+숫자 파라미터 태그는 placebo」에 대해 우리가 「3경로 수렴」이라 적었다.",
   "⑴출력층_key:value_형태분해": x2_out,
   "⑵입력층_key:value_형태분해": x2_in,
   "⑶맨명찰_실측(경로2가 같은 대상인지)": x2_label,
 },
 "X3": {
   "★쟁점": "songsmith 「소괄호는 항상 불린다」 ↔ sunoaiwiki 「소괄호를 spoken에 쓰라」 = 외부끼리 정면 모순이라 적었다.",
   "★우리가_전에_잰_축": "말/노래 **음향 분리**(F0 sustain·delta·voiced) — `spoken_delivery_probe_n4_report.py`. "
                    "판정가능 2클립 중 RM2=말하기·RM1=보류, M23 2클립=게이트 기각.",
   "★오늘_처음_잰_축": "**누출** — 괄호 안 지시어 `spoken`이 낱말로 불렸는가. ASR 전사 전수 스캔.",
   "누출_스캔": x3_leak,
 },
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out["X2"], ensure_ascii=False, indent=1))
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "클립키"} for k, v in x3_leak.items()},
                 ensure_ascii=False, indent=1))
print("→", OUT.relative_to(ROOT))
