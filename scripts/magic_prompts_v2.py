#!/usr/bin/env python3
"""magic_prompts_v2.py — Suno 매직 버튼 2판 150 (sunomusic 214100) · 1판 셈(magic_prompts_v1.summ) 그대로 · 무리만 나눔.
무리: L1 = 1판 leoarkedia 빈칸 보컬 100 · A = asiloveu 빈칸 보컬 100 · I = leoarkedia 빈칸 반주 20 · S = leoarkedia 장르 씨앗 10×3
더 셈: 두 계정 장르 머리 겹침 · 씨앗 낱말이 첫 칸/어딘가에 남나 · 씨앗에 없던 장르 낱말 덧붙임.
쓰기 = data/magic_prompts_v2.json 만."""
import collections, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import magic_prompts_v1 as M

V2 = M.AC / "SUNO_MAGIC_PROMPTS_20261121/prompts.jsonl"
OUT = REPO / "data/magic_prompts_v2.json"


def words(t):
    return set(re.findall(r"[a-z&]+", t.lower()))


def main():
    r1 = [json.loads(l) for l in M.SUNO.read_text().splitlines()]
    r2 = [json.loads(l) for l in V2.read_text().splitlines()]
    G = {"L1": r1,
         "A": [r for r in r2 if r["account"] == "asiloveu" and not r["seed"] and not r["is_instrumental"]],
         "I": [r for r in r2 if r["account"] == "leoarkedia" and not r["seed"] and r["is_instrumental"]],
         "S": [r for r in r2 if r["seed"]]}
    out = {"meta": {"script": "repo:sunolanguage scripts/magic_prompts_v2.py", "src_v2": "agent-comm:projects/sunomusic/attachments/SUNO_MAGIC_PROMPTS_20261121/prompts.jsonl"},
           "groups": {k: M.summ(v, "suno")[0] for k, v in G.items()}}
    hl = collections.Counter(M.genre_head(r["prompt"], "suno") for r in G["L1"])
    ha = collections.Counter(M.genre_head(r["prompt"], "suno") for r in G["A"])
    out["head_overlap_L1_A"] = sorted(set(hl) & set(ha))
    # 두 계정 모든 쉼표 칸 겹침(자카드)
    cl = {c.strip().lower() for r in G["L1"] for c in r["prompt"].split(",")}
    ca = {c.strip().lower() for r in G["A"] for c in r["prompt"].split(",")}
    out["chunk_jaccard_L1_A"] = round(len(cl & ca) / len(cl | ca), 3)
    seeds = []
    for sd in sorted({r["seed"] for r in G["S"]}):
        rs = [r for r in G["S"] if r["seed"] == sd]
        sw = words(sd)
        seeds.append({"seed": sd, "n": len(rs),
                      "first_chunk": [r["prompt"].split(",")[0].strip() for r in rs],
                      "seed_words_all_kept": sum(sw <= words(r["prompt"]) for r in rs),
                      "seed_in_first_chunk": sum(sw <= words(r["prompt"].split(",")[0]) for r in rs),
                      "added_genre_words": sorted({g for r in rs for g in M.genre_tags(r["prompt"], "suno")} - {g for g in M.GENRE_WORDS if re.search(rf"\b{re.escape(g)}\b", sd.lower())}),
                      "bpm": [re.search(M.RX["bpm"], r["prompt"], re.I).group(0) if re.search(M.RX["bpm"], r["prompt"], re.I) else None for r in rs]})
    out["seeds"] = seeds
    # 반주: 보컬 낱말 남나
    out["instrumental_vocal_word"] = sum(bool(re.search(M.RX["vocal"], r["prompt"], re.I)) for r in G["I"])
    out["instrumental_has_instrumental_word"] = sum(bool(re.search(r"\binstrumental\b", r["prompt"], re.I)) for r in G["I"])
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=list))
    for k, s in out["groups"].items():
        print(k, {x: s[x] for x in ("n", "chars_med", "chars_min", "chars_max", "commas_med", "bpm", "key", "vocal", "gender", "flow", "mix", "decade", "region", "kpop", "genre_head_distinct")})
        print("   heads", s["genre_head_top"][:6]); print("   genre", s["genre_word_top"][:8]); print("   bpm_pos", s.get("bpm_pos"))
    print("overlap heads", out["head_overlap_L1_A"], "chunk J", out["chunk_jaccard_L1_A"])
    for s in seeds:
        print(s["seed"], s["seed_words_all_kept"], s["seed_in_first_chunk"], s["first_chunk"], s["added_genre_words"], s["bpm"])
    print("instr vocal", out["instrumental_vocal_word"], "instr word", out["instrumental_has_instrumental_word"])


if __name__ == "__main__":
    main()
