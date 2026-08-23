#!/usr/bin/env python3
"""X1 「충돌」 검산 v1 — 지시축 대장 §3 X1의 판정 자체를 검산한다.

두 갈래:
 A) 축 정합: 우리 주장/외부 주장이 같은 대상·같은 종류의 근거인가 (대장 JSON에서 원문 인용)
 B) 실측 보강: A_demo 근거곡(dxG9qPPpRnI)의 **입력 가사** ↔ **자막(실제 렌더 ASR)** 대조로
    「긴 서술 브라켓이 가사로 새는가」를 잰다. 생성 0·크레딧 0.

★자막의 한계: 자막은 **낱말**만 준다. 「낭독이었나·쉰 목소리였나」는 자막으로 못 잰다.
   ⇒ 잴 수 있는 것은 **누출(브라켓 문자열이 불렸는가)** 하나뿐이다.
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
YT = ROOT / "data/metatag_external/yt/verify_v1"
DESC = YT / "dxG9qPPpRnI.description"
VTT = YT / "dxG9qPPpRnI.en-orig.vtt"
REG = ROOT / "data/metatag_external/directive_register_v1.json"
OUT = ROOT / "data/metatag_external/x1_conflict_audit_v1.json"

def norm(t):
    return re.sub(r"[^a-z0-9 ]", " ", t.lower())

def caption_text(p):
    lines = []
    for ln in p.read_text().splitlines():
        if ln.startswith(("WEBVTT", "Kind:", "Language:")) or "-->" in ln or not ln.strip():
            continue
        t = re.sub(r"<[^>]+>", "", ln).strip()
        if t and (not lines or lines[-1] != t):
            lines.append(t)
    return re.sub(r"\s+", " ", " ".join(lines))

# ── 입력 가사 ──────────────────────────────────────────────────────────
desc = DESC.read_text()
body = desc.split("// Lyrics (as input)", 1)[1]
body = body.split("// Credits", 1)[0] if "// Credits" in body else body
brackets = re.findall(r"\[([^\]]+)\]", body)
uniq = sorted(set(brackets))

def wc(s):  # 브라켓 안 낱말 수 (외부 「1~3단어」 규칙의 단위)
    return len([w for w in norm(s).split() if w])

bracket_rows = [{"표기": f"[{b}]", "낱말수": wc(b), "출현": brackets.count(b)} for b in uniq]
bracket_rows.sort(key=lambda r: (-r["낱말수"], r["표기"]))

# 브라켓 안에만 있고 가사 본문에는 없는 낱말 = 누출 판정에 쓸 수 있는 낱말
lyric_body = re.sub(r"\[[^\]]*\]", " ", body)
body_words = set(norm(lyric_body).split())
bracket_words = set()
for b in brackets:
    bracket_words |= set(norm(b).split())
probe = sorted(w for w in bracket_words if w and w not in body_words)
shared = sorted(w for w in bracket_words if w in body_words)

# ── 자막(실제 렌더) ────────────────────────────────────────────────────
cap = caption_text(VTT)
cap_words = norm(cap).split()
cap_set = set(cap_words)

leak = {w: cap_words.count(w) for w in probe}
leaked = {w: n for w, n in leak.items() if n}

# ★적중 낱말은 문맥 실사 후에만 「누출」로 센다 (자동 적중 ≠ 누출)
ADJUDICATED = {
 "by": {"판정": "누출 아님", "근거": "자막 문맥 'ins I by skull' = 입력 가사 'inside my skull'의 "
        "자동자막 오인식. [Lyrics by Josh Powlison]과 무관.", "확인": "문자열 실사 08-23"},
}
real_leak = {w: n for w, n in leaked.items() if ADJUDICATED.get(w, {}).get("판정") != "누출 아님"}

# 브라켓이 지배한 대사 줄이 실제로 렌더됐는가 (내용어 적중률)
gov = []
for ln in body.splitlines():
    m = re.match(r"\s*\[(Female spoken[^\]]*|Monster spoken[^\]]*)\]\s*(.+)", ln)
    if m and m.group(2).strip():
        gov.append((m.group(1), m.group(2).strip()))
STOP = set("the a an of to in on my it is that and or if so you your they i be do".split())
gov_rows = []
for tag, line in gov:
    ws = [w for w in norm(line).split() if w and w not in STOP]
    hit = [w for w in ws if w in cap_set]
    gov_rows.append({"태그": f"[{tag}]", "대사_앞30자": line[:30],
                     "내용어": len(ws), "자막적중": len(hit),
                     "적중률": round(len(hit) / len(ws), 3) if ws else None})

# ── 외부 주장 원문 (대장에서 인용) ─────────────────────────────────────
reg = json.load(open(REG))
want = {"D001", "D002", "D006", "D013", "D016", "D051", "D053"}
ext = [{"id": c["id"], "host": c["출처host"], "주장": c["주장"],
        "★검증가능성": c["★검증가능성"]} for c in reg["주장"] if c["id"] in want]

out = {
 "무엇": "X1 「충돌」 검산 v1 — 대장 §3 X1의 「정면 반대」 판정 자체를 검산",
 "재현": "scripts/x1_bracket_conflict_audit_v1.py",
 "★생성": "0건 · 크레딧 0 · 새 수집 0 (리포 내 기존 자료만)",
 "A_축정합_외부주장_원문": ext,
 "B_실측": {
   "근거곡": "https://www.youtube.com/watch?v=dxG9qPPpRnI",
   "입력가사_출처": "영상 설명란 '// Lyrics (as input)'",
   "자막_출처": str(VTT.relative_to(ROOT)) + " (유튜브 자동자막 = 실제 렌더 ASR)",
   "브라켓_고유": len(uniq), "브라켓_총출현": len(brackets),
   "브라켓_낱말수_분포": bracket_rows,
   "누출_판정낱말(브라켓에만 있고 가사본문엔 없음)": probe,
   "판정불가_낱말(가사본문과 공유 → 누출 판정에 못 씀)": shared,
   "자막_적중_원값": leaked,
   "★적중_문맥실사": ADJUDICATED,
   "★누출_확정": real_leak,
   "★누출_건수": len(real_leak),
   "★분모": {"서술브라켓_출현": sum(r["출현"] for r in bracket_rows
                                if r["표기"] in ("[Female spoken, vocaloid, gentle]",
                                                 "[Monster spoken, raspy, angry]")),
            "판정가능_낱말종수": len(probe)},
   "지배대사_렌더_확인": gov_rows,
   "자막_문자수": len(cap),
 },
 "★이_실측이_못_하는_것": [
   "낭독이었는지·쉰 목소리였는지·화났는지 = 자막은 낱말만 준다. 못 잰다.",
   "대조군 없음 — 맨 명찰 [spoken]로 같은 가사를 돌린 판이 없다. 「서술이 더 낫다」는 못 나온다.",
   "자동자막은 오인식이 있다(실측: 'array dot join'→'a rap B join'). 낱말 부재는 약한 증거다.",
   "N=1곡. 한 곡의 한 판이다.",
 ],
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps({k: v for k, v in out["B_실측"].items() if k != "브라켓_낱말수_분포"}, ensure_ascii=False, indent=1))
print("\n브라켓 낱말수:")
for r in bracket_rows:
    print(f"  {r['낱말수']}어 ×{r['출현']:2d}  {r['표기']}")
print("\n→", OUT.relative_to(ROOT))
