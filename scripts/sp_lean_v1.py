#!/usr/bin/env python3
"""sp_lean_v1.py — 우리 카드 SP → LEO 문장형 꼴 시험판 (encore 112725 · 11342·11341 × ⑴⑵⑶).
결정적 변환(난수·모델 0). 입력 = DB songs.style_prompt 축자 · 출력 = agent-comm sunolanguage/exchange/leo_prompts_20261115/sp_test/
⑴ 원문 그대로
⑵ 같은 낱말 · 5문장 · 악기마다 꾸밈말 ≤1 · 끝 = 코러스 열림(장면 0):
   S1 «<장르> at NNN BPM in <조>, <무드 전부>.»
   S2 보컬 «<보컬 꾸밈말>, <홀로 선 꾸밈말> vocals, <프레이징 절>, <Voice 절>.»
   S3 악기 = «Instrumentation features» 항목 중 악기 낱말 든 것만 · 악기 낱말 앞 꾸밈말 ≤1 · 뒤 ≤2낱말 · chorus·bridge 항목 뺌
   S4 «Harmonic texture built on <화성 전부>, with <프로덕션 끝 2항목>.»
   S5 «The chorus opens with <chorus 항목에서 'on chorus'·'entering' 뺀 것>.»
   지우는 칸 = 에너지 문장 · 감정 «delivering … emotion» · 떨어진 꾸밈말 조각 · bridge 항목 · 프로덕션 나머지 · Include 인트로·아웃트로(구조 = 가사 브래킷 채널)
⑶ ⑵ + 장면 1문장 «A song about <TITLE_EN>.» — ★유일한 손 입력 = 아래 TITLE_EN(카드 제목 직역 2개 · DB 영어 주제 칸 비어 있음)
덧붙인 낱말 = FRAME 뿐(⑵) · ⑶ 은 FRAME + TITLE_EN 낱말 — 실행 때 검사(어기면 멈춤).
"""
import hashlib, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
OUT = Path.home() / "agent-comm-sunolanguage/projects/sunolanguage/exchange/leo_prompts_20261115/sp_test"
GIDS = [11342, 11341]
TITLE_EN = {11342: "the night the ice melts", 11341: "spring at twenty-three"}  # 얼음이 녹는 밤 · 스물셋의 봄 (직역)
FRAME = {"at", "bpm", "in", "and", "with", "the", "chorus", "opens", "vocals", "a", "song", "about", "harmonic", "texture", "built", "on"}
INSTR = re.compile(r"\b(rhodes|wurlitzer|piano|organ|moog|synth|pad|guitar|bass|kick|rimshot|snare|brushes|shaker|vibraphone|strings?|cello|drums?|hi-hats?)\b", re.I)


def seg(sp):
    """«Head. Rest.» 꼴 템플릿 SP → 칸 사전(문장 머리 낱말로 가름)."""
    s = {}
    parts = [p.strip() for p in re.split(r"(?<=\.)\s+", sp.strip()) if p.strip()]
    s["genre"], s["key"] = re.match(r"^([^,]+), .* in ([A-G][#b]? (?:major|minor))", parts[0]).groups()
    lone = []
    for p in parts[1:]:
        b = p.rstrip(".")
        if re.fullmatch(r"\d{2,3} BPM", b): s["bpm"] = b.split()[0]
        elif b.endswith("vocal phrasing") or " vocals with " in b: s["vocal"] = b
        elif b.startswith("Voice "): s["voice"] = b[len("Voice "):]
        elif b.startswith("Instrumentation features "): s["instr"] = b[len("Instrumentation features "):]
        elif b.startswith("Harmonic texture built on "): s["harm"] = b[len("Harmonic texture built on "):]
        elif b.startswith("Mood captures "): s["mood"] = b[len("Mood captures "):]
        elif b.startswith("Production"): s["prod"] = re.sub(r"^Production(?: with|:)\s*", "", b)
        elif re.fullmatch(r"[A-Z][a-z-]+", b): lone.append(b.lower())
    s["lone"] = lone
    return s


def items(t):
    t = re.sub(r",?\s+and\s+(?=[^,]*$)", ", ", t)
    return [x.strip() for x in t.split(",") if x.strip()]


def lean(sp):
    s = seg(sp)
    mood = items(s["mood"])
    s1 = f"{s['genre']} at {s['bpm']} BPM in {s['key']}, {', '.join(mood[:-1])} and {mood[-1]}."
    vadj = s["vocal"].split()[0]
    phr = [x for x in items(s["vocal"]) if "phrasing" in x][0]
    s2 = f"{vadj}{', ' + ', '.join(s['lone']) if s['lone'] else ''} vocals, {phr}, {s['voice']}."
    keep, chorus = [], []
    for it in items(s["instr"]):
        m = INSTR.search(it)
        if not m:
            continue
        if re.search(r"\bon chorus\b", it):
            chorus.append(re.sub(r"\s*(entering\s+)?on chorus\b", "", it)); continue
        if re.search(r"\bon bridge\b", it):
            continue
        w = it.split(); i = len(it[:m.start()].split())
        j = len(it[:m.end()].split())
        keep.append(" ".join(w[max(0, i - 1):j + 2]))
    s3 = keep[0][0].upper() + keep[0][1:] + ", " + ", ".join(keep[1:-1]) + ", and " + keep[-1] + "."
    h = items(s["harm"])
    pr = items(s["prod"])[-2:]
    s4 = f"Harmonic texture built on {', '.join(h[:-1])} and {h[-1]}, with {' and '.join(pr)}."
    s5 = f"The chorus opens with {' and '.join(chorus)}." if chorus else ""
    return " ".join(x for x in (s1, s2, s3, s4, s5) if x)


def words(t):
    return set(re.findall(r"[a-z]+", t.lower()))


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def main():
    from json_to_db import get_conn
    cur = get_conn().cursor()
    cur.execute("select global_id, style_prompt from songs where global_id = any(%s)", (GIDS,))
    src = dict(cur.fetchall())
    OUT.mkdir(parents=True, exist_ok=True)
    res = []
    for g in GIDS:
        sp = src[g]
        a2 = lean(sp)
        a3 = a2 + f" A song about {TITLE_EN[g]}."
        extra2 = words(a2) - words(sp) - FRAME
        extra3 = words(a3) - words(sp) - FRAME - words(TITLE_EN[g])
        if extra2 or extra3:
            raise SystemExit(f"{g} 덧붙인 낱말: {sorted(extra2 | extra3)}")
        for arm, t in (("1", sp), ("2", a2), ("3", a3)):
            (OUT / f"{g}_arm{arm}.txt").write_text(t)
            res.append({"gid": g, "arm": arm, "chars": len(t), "sentences": len(re.findall(r"\.(?:\s|$)", t)), "sha256": sha(t),
                        "new_words": sorted(words(t) - words(sp))})
    meta = {"script": "repo:sunolanguage scripts/sp_lean_v1.py", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source": "DB songs.style_prompt 축자", "title_en_hand_input": TITLE_EN}
    (OUT / "manifest.json").write_text(json.dumps({"meta": meta, "arms": res}, ensure_ascii=False, indent=1))
    for r in res:
        print(r["gid"], "⑴⑵⑶"[int(r["arm"]) - 1], r["chars"], "자", r["sentences"], "문장", r["sha256"][:16], "새 낱말", r["new_words"])
    for g in GIDS:
        print("\n", g, "⑶:", (OUT / f"{g}_arm3.txt").read_text())
    print("script", meta["script_sha256"][:16])


if __name__ == "__main__":
    main()
