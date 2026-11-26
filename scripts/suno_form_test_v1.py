#!/usr/bin/env python3
"""suno_form_test_v1.py — Suno 자기 꼴(쉼표 태그 한 줄) SP vs 우리 카드 SP (encore 143538 ① · 매직 버튼 analysis_v1·v2).
결정적 변환(난수·모델 0). 입력 = DB songs.style_prompt 축자 · 가사 = DB songs.lyrics 축자(두 팔 같음).
  A 카드 그대로(문장형)
  B 태그 줄: 문장 머리 틀 낱말만 지움(Instrumentation features · Harmonic texture built on · Mood captures · Production with · Include · Voice)
     + 마지막 항목 앞 «and» 지움 · 마침표 → 쉼표 · 칸 순서 = Suno 매직 버튼 꼴(장르·조 → BPM → 에너지 → 악기 → 화성 → 프로덕션 → 구조(Include) → 보컬 → 무드)
     ⇒ **낱말은 카드 그대로**(덧붙임 0 · 지운 것 = 틀 낱말뿐 · 실행 때 검사) · 길이는 거의 같음(꼴만 바꿈 · 길이 시험 아님)
쓰기 = agent-comm:projects/sunolanguage/exchange/suno_form_test_v1/inputs/{run_id}.json + manifest.json
"""
import hashlib, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

OUT = Path.home() / "agent-comm-sunolanguage/projects/sunolanguage/exchange/suno_form_test_v1/inputs"
GIDS = [11339, 11344, 11346]  # 카드 꼴 같은 판(1134x) · 68 · 88 · 124 BPM · 발라드·재즈 힙합·팝 록
HEADS = [("instr", "Instrumentation features "), ("harm", "Harmonic texture built on "), ("mood", "Mood captures "),
         ("prod", "Production with "), ("incl", "Include "), ("voice", "Voice ")]
ORDER = ["genre", "bpm", "energy", "instr", "harm", "prod", "incl", "vocal", "voice", "lone", "mood"]
FRAME = {"instrumentation", "features", "harmonic", "texture", "built", "on", "mood", "captures", "production", "with", "include", "voice", "and"}


def sents(sp):
    return [p.strip().rstrip(".") for p in re.split(r"(?<=\.)\s+", sp.strip()) if p.strip()]


def items(t):
    t = re.sub(r",?\s+and\s+(?=[^,]*$)", ", ", t)
    return [x.strip() for x in t.split(",") if x.strip()]


def tagline(sp):
    slots = {k: [] for k in ORDER}
    ps = sents(sp)
    slots["genre"] = items(ps[0])
    for p in ps[1:]:
        head = next((k for k, h in HEADS if p.startswith(h)), None)
        if head:
            slots[head] += items(p[len(dict(HEADS)[head]):])
        elif re.fullmatch(r"\d{2,3} BPM", p):
            slots["bpm"].append(p)
        elif re.search(r"\benergy\b", p, re.I):
            slots["energy"].append(p)
        elif re.fullmatch(r"[A-Z][a-z-]+", p):
            slots["lone"].append(p.lower())
        else:
            slots["vocal"] += items(p)
    return ", ".join(x for k in ORDER for x in slots[k])


def words(t):
    return re.findall(r"[a-z0-9&'#-]+", t.lower())


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def main():
    from json_to_db import get_conn
    cur = get_conn().cursor()
    cur.execute("select global_id, style_prompt, lyrics, bpm, title from songs where global_id = any(%s)", (GIDS,))
    S = {r[0]: dict(zip(("sp", "ly", "bpm", "title"), r[1:])) for r in cur.fetchall()}
    runs = []
    for g in GIDS:
        a, b = S[g]["sp"], tagline(S[g]["sp"])
        added = set(words(b)) - set(words(a))
        lost = set(words(a)) - set(words(b)) - FRAME
        if added or lost:
            raise SystemExit(f"{g} 낱말 어긋남 · 덧붙음 {sorted(added)} · 빠짐 {sorted(lost)}")
        for arm, sp in (("A 카드 그대로", a), ("B 태그 줄(같은 낱말)", b)):
            rid = f"SF{arm[0]}_{g}"
            assert len(sp) <= 1000, rid
            runs.append({"run_id": rid, "arm": arm, "gid": g, "design_bpm": S[g]["bpm"], "requests": 1, "engine": "Suno · 두 팔 같은 모델(sunomusic 고름 · 판 안 고정)",
                         "account": "asiloveu", "variety_enhance": "끔(넣은 글 그대로)", "SP": sp, "SP_chars": len(sp), "SP_sha256": sha(sp),
                         "commas": sp.count(","), "sentences": len(sents(sp)) if arm[0] == "A" else 1,
                         "lyrics": S[g]["ly"], "lyrics_sha256": sha(S[g]["ly"]), "sp_is_db_verbatim": sp == a, "lyrics_is_db_verbatim": True})
    OUT.mkdir(parents=True, exist_ok=True)
    for r in runs:
        (OUT / f"{r['run_id']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
    man = {"script": "repo:sunolanguage scripts/suno_form_test_v1.py", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "generations": len(runs), "clips": 2 * len(runs), "runs": [{k: r[k] for k in r if k not in ("SP", "lyrics")} for r in runs]}
    (OUT.parent / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
    for r in runs:
        print(r["run_id"], r["SP_chars"], r["commas"], r["sp_is_db_verbatim"])
    for g in GIDS:
        print("\n", g, "B:", tagline(S[g]["sp"]))


if __name__ == "__main__":
    main()
