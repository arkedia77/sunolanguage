#!/usr/bin/env python3
"""acelang_reframe_v1.py — 우리 판 SP → «우리 낱말 그대로 + ace_frame 재배열» (encore 002628 · 3팔 시험 셋째 팔).
결정적 변환(난수·모델 0). 입력 = sunomusic 수집 v3 jsonl 의 seed_text(= DB songs.style_prompt 축자) · 출력 = data/acelang/arm3_reframe_v1.json
규칙(our_sp_rewrite_v1.md ①②③ 중 ①② 만 — ③ 길이 맞춤은 낱말을 더하거나 빼야 해서 안 함):
  ① BPM·조를 장르 문장 안으로: «<장르 머리> at NNN BPM in <조>» · 따로 선 BPM·4/4·조 토막과 «The tempo is …» 문장은 지움 · 조 «Cm»→«C minor»
  ② 믹스 문장 지움: mix·production·compression 낱말이 든 문장
  + 재배열: 장르 → 리듬·저역 → 리드·화성 → 보컬 → 그 밖 → 구조 (같은 칸 안은 원래 순서)
덧붙이는 낱말 = «at · BPM · in · minor/major» 뿐 — 실행 때 검사(어기면 멈춤).
"""
import hashlib, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

SRC = Path.home() / "agent-comm-sunolanguage/projects/sunomusic/attachments/acelang_collect_v3_우리SP_20261114.jsonl"
OUT = REPO / "data/acelang/arm3_reframe_v1.json"
ORDER = ["장르", "리듬·저역", "리드·화성", "보컬", "그 밖", "구조"]
LABEL = {"vocal": "보컬", "lead": "리드·화성", "harmony": "리드·화성", "color": "그 밖", "rhythm": "리듬·저역", "bass": "리듬·저역", "drums": "리듬·저역"}
BPM = re.compile(r"\b(\d{2,3}) ?BPM\b", re.I)
KEY = re.compile(r"\b(?:in the key of|key of)\s+([A-G][#b]?m?(?: (?:major|minor))?)|\b([A-G][#b]?) (major|minor)\b")
# 칸 판정(이 변환 전용 · 결정적): 구조 = 문장 머리·끝맺음 말 · 그 밖은 문장에서 «먼저 나오는» 단서 낱말의 칸
STRUCT = re.compile(r"^(The arrangement|The song|Bridge|The ending)\b|\bto close\b|\bthe ending\b|\boutro\b", re.I)
CUE = [("보컬", r"vocals?|voices?|singing|singer"),
       ("리듬·저역", r"drums?|kit|kick|snares?|hi-hats?|claps?|percussion|cabasa|beat|groove|bass|808s?"),
       ("리드·화성", r"lead|guitars?|piano|synths?|strings?|string|brass|saxophone|accordion|bells|glockenspiel|cello|chords|pads?|organ|keys")]
CUE_RX = re.compile(r"\b(" + "|".join(f"(?P<g{i}>{rx})" for i, (_, rx) in enumerate(CUE)) + r")\b", re.I)


def kind(u):
    if STRUCT.search(u):
        return "구조"
    m = CUE_RX.search(u)
    if not m:
        return "그 밖"
    return next(CUE[i][0] for i in range(len(CUE)) if m.group(f"g{i}"))


MIX = re.compile(r"\b(mix|production|compression)\b", re.I)
ALLOWED_NEW = {"at", "bpm", "in", "minor", "major", "a", "b", "c", "d", "e", "f", "g"}  # 음이름 = 조 풀어 씀(Cm→C minor)


def spell(k):
    k = k.strip()
    if re.fullmatch(r"[A-G][#b]?m", k):
        return k[:-1] + " minor"
    return k


def units(t):
    out = []
    for para in re.split(r"\n\s*\n|\n", t.strip()):
        for s in re.split(r"(?<=\.)\s+", para.strip()):
            if s.strip():
                out.append(s.strip())
    return out


def strip_tempo(u):
    """BPM·4/4·조 토막 지움 — 남은 쉼표 정리. «The tempo is …» 문장은 통째로 빈 것이 됨."""
    if re.match(r"^The tempo is\b", u):
        return ""
    u = BPM.sub("", u)
    u = re.sub(r"\b\d/\d\b", "", u)
    u = re.sub(r"\bkey of [A-G][#b]?m?(?: (?:major|minor))?", "", u)
    u = re.sub(r"\b[A-G][#b]? (?:major|minor)\b", "", u)
    u = re.sub(r"\s*,\s*(?=[,.]|$)", "", u)          # 빈 쉼표 칸
    u = re.sub(r"(,\s*){2,}", ", ", u)
    u = re.sub(r"\s{2,}", " ", u).strip(" ,")
    return "" if re.fullmatch(r"[\W_]*", u) else u


def reframe(sp):
    bpm = BPM.search(sp)
    km = KEY.search(sp)
    key = spell(km.group(1)) if km and km.group(1) else (f"{km.group(2)} {km.group(3)}" if km else None)
    us = units(sp)
    genre = strip_tempo(us[0]).rstrip(".")
    tag = " at " + bpm.group(1) + " BPM" + (f" in {key}" if key else "") if bpm else ""
    cut = min([i for i in (genre.find(" — "), genre.find(",")) if i >= 0], default=len(genre))
    genre = genre[:cut] + tag + genre[cut:] + "."
    rest = []
    for i, u in enumerate(us[1:], 1):
        u2 = strip_tempo(u)
        if not u2 or MIX.search(u2):
            continue
        if not u2.endswith("."):
            u2 += "."
        m = re.match(r"^(\w+):", u2)
        k = LABEL.get(m.group(1).lower()) if m else None
        k = k or kind(u2)
        rest.append((ORDER.index(k) if k in ORDER else ORDER.index("그 밖"), i, u2))
    rest.sort()
    out = " ".join([genre] + [u for _, _, u in rest])
    w = lambda t: set(re.findall(r"[a-z]+", t.lower()))
    extra = w(out) - w(sp) - ALLOWED_NEW
    if extra:
        raise SystemExit(f"덧붙인 낱말 있음: {sorted(extra)}")
    return out, {"bpm": bpm.group(1) if bpm else None, "key": key, "dropped_mix": sum(bool(MIX.search(strip_tempo(u))) for u in us[1:])}


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    seeds = {}
    for l in SRC.read_text().splitlines():
        d = json.loads(l)
        seeds.setdefault(d["gid"], d["seed_text"])
    res = []
    for gid, sp in sorted(seeds.items()):
        out, info = reframe(sp)
        res.append({"gid": gid, "in_chars": len(sp), "out_chars": len(out), "in_sha256": sha(sp), "out_sha256": sha(out), **info, "sp_in": sp, "sp_out": out})
    meta = {"script": "scripts/acelang_reframe_v1.py", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source": str(SRC).replace(str(Path.home()) + "/agent-comm-sunolanguage/", "agent-comm:"), "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
            "rules": "① BPM·조 장르 문장 안 · ② 믹스 문장 지움 · 재배열 장르→리듬→리드→보컬→그 밖→구조 · ③ 길이 맞춤 안 함 · 덧붙인 낱말 = at·BPM·in·minor/major 뿐(검사)"}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"meta": meta, "arms": res}, ensure_ascii=False, indent=1))
    for r in res:
        print(r["gid"], r["in_chars"], "→", r["out_chars"], "· 믹스 지움", r["dropped_mix"], "· sha", r["out_sha256"][:16])
        print("   ", r["sp_out"][:300])
    print("script", meta["script_sha256"][:16])


if __name__ == "__main__":
    main()
