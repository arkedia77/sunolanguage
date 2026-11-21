#!/usr/bin/env python3
"""magic_prompts_v1.py — 매직 버튼이 빈칸에 쓴 프롬프트 Suno 100 · ACE 100 (sunomusic 163732 · 180158 · LEO «새로운 것·바뀐 것·지속할지»).
재료 = agent-comm:projects/sunomusic/attachments/{SUNO_MAGIC_PROMPTS_20261118,ACE_MAGIC_PROMPTS_20261119}/prompts.jsonl (화면 버튼이 부르는 길 · 0cr · 생성 0)
견줌 = ACE: acelang_frame_v1 셈 그대로(씨앗 든 ✦ 115 = frame_v2_all.json) · Suno: suno_refs_form_v1 셈 그대로(홈 새 곡 · 앞 곡)
낱말 셈 = 정규식 휴리스틱(아래 RX) · 들림 0 · 판단 = «글 쪽 꼴»만.
"""
import json, re, sys
from collections import Counter
from pathlib import Path
from statistics import median

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import acelang_frame_v1 as F

AC = Path.home() / "agent-comm-sunolanguage/projects/sunomusic/attachments"
SUNO = AC / "SUNO_MAGIC_PROMPTS_20261118/prompts.jsonl"
ACE = AC / "ACE_MAGIC_PROMPTS_20261119/prompts.jsonl"
OUT = REPO / "data/magic_prompts_v1.json"

RX = {
    "bpm": r"\b\d{2,3} ?BPM\b",
    "key": r"\b[A-G][#b]?(?:-flat|-sharp)? (?:major|minor)\b|\bkey of\b",
    "meter": r"\b\d/\d\b|\bhalf-time\b|\bswung\b|\bshuffle\b",
    "decade": r"\b(?:early|mid|late)?[- ]?(?:19|20)?\d0s\b",
    "vocal": r"\bvocals?\b|\bvoice\b|\bsinger\b|\brap\b|\bharmonies\b|\bchoir\b|\bfalsetto\b",
    "gender": r"\b(?:male|female|boy|girl|women|men)\b",
    "flow": r"\bintro\b|\bopens?\b|\bopening\b|\bbuilds?\b|\bbridge\b|\bchorus(?:es)?\b|\bfade|\bfinale\b|\boutro\b|\bdrop\b|\bbreakdown\b|\bending\b|\bconclud|\bclos(?:e|es|ing)\b|\bfinal\b",
    "mix": r"\bmix\b|\bmaster|\bproduction\b|\bcompress|\bsidechain|\breverb\b|\btape\b|\bsaturat|\blo-fi\b|\bstereo\b|\bwide\b",
    "region": r"\b(?:Korean|K-pop|Japanese|Latin|Brazilian|African|Afro|UK|British|American|Nordic|Pacific Northwest|Detroit|Chicago|Memphis|Jamaican|French|Indian|Arabic|Spanish|Irish|Balkan|West Coast|East Coast|Southern|Nashville|Berlin|Atlanta)\b",
    "scene": r"\blike (?:a|an|the)\b|\bas if\b|\bimagine\b|\bnight drive\b|\brain\b|\bcity lights\b",
    "neg": r"\bno \w+|\bwithout\b|\bavoid\b|\bdon't\b",
    "kpop": r"\bk-?pop\b|\bkorean\b",
}


def feats(t):
    f = {k: bool(re.search(v, t, re.I)) for k, v in RX.items()}
    f["chars"] = len(t)
    f["commas"] = t.count(",")
    f["sentences"] = len(F.sents(t))
    f["is_prose"] = f["sentences"] >= 2
    return f


def first_chunk(t, kind):
    return (t.split(",")[0] if kind == "suno" else F.sents(t)[0]).strip().lower()


def genre_head(t, kind):
    """장르 머리: Suno = 첫 쉼표 칸 · ACE = 첫 문장 앞 6낱말(연대·지역 포함)."""
    if kind == "suno":
        return t.split(",")[0].strip().lower()
    return " ".join(re.findall(r"[a-z0-9&'-]+", F.sents(t)[0].lower())[:6])


GENRE_WORDS = ["rock", "pop", "jazz", "hip-hop", "hip hop", "r&b", "soul", "funk", "house", "techno", "trap", "phonk", "ambient", "folk",
               "country", "metal", "punk", "grunge", "blues", "reggae", "disco", "orchestral", "cinematic", "drill", "afrobeats", "bossa",
               "city pop", "lo-fi", "edm", "dubstep", "drum and bass", "synthwave", "shoegaze", "gospel", "k-pop", "latin", "classical", "bop"]


def genre_tags(t, kind):
    h = genre_head(t, kind) if kind == "ace" else ", ".join(t.lower().split(",")[:3])
    return [g for g in GENRE_WORDS if re.search(rf"\b{re.escape(g)}\b", h)]


def summ(rows, kind):
    fs = [feats(r["prompt"]) for r in rows]
    n = len(fs)
    s = {"n": n, "chars_med": median(f["chars"] for f in fs), "chars_min": min(f["chars"] for f in fs), "chars_max": max(f["chars"] for f in fs),
         "commas_med": median(f["commas"] for f in fs), "sent_med": median(f["sentences"] for f in fs), "prose": sum(f["is_prose"] for f in fs)}
    for k in RX:
        s[k] = sum(f[k] for f in fs)
    heads = Counter(genre_head(r["prompt"], kind) for r in rows)
    s["genre_head_top"] = heads.most_common(8)
    s["genre_head_distinct"] = len(heads)
    gt = Counter(g for r in rows for g in genre_tags(r["prompt"], kind))
    s["genre_word_top"] = gt.most_common(12)
    if kind == "suno":  # BPM 자리: 몇째 칸 / 끝 칸
        pos = []
        for r in rows:
            cs = [c.strip() for c in r["prompt"].split(",")]
            i = next((j for j, c in enumerate(cs) if re.search(RX["bpm"], c, re.I)), None)
            if i is not None:
                pos.append("last" if i == len(cs) - 1 else ("last2" if i == len(cs) - 2 else ("first3" if i < 3 else "mid")))
        s["bpm_pos"] = Counter(pos).most_common()
        s["bpm_first_chunk"] = sum(bool(re.search(RX["bpm"], r["prompt"].split(",")[0], re.I)) for r in rows)
    else:
        s["bpm_first_sentence"] = sum(bool(re.search(RX["bpm"], F.sents(r["prompt"])[0], re.I)) for r in rows)
        s["decade_first_sentence"] = sum(bool(re.search(RX["decade"], F.sents(r["prompt"])[0], re.I)) for r in rows)
        last = [F.slot(F.sents(r["prompt"])[-1], len(F.sents(r["prompt"])) - 1) for r in rows]
        s["last_slot"] = Counter(last).most_common()
        s["has_mix_sentence"] = sum(any(F.slot(x, i) == "믹스" for i, x in enumerate(F.sents(r["prompt"]))) for r in rows)
    return s, fs


def ace_seeded():
    """견줌: 씨앗 든 ✦ 115 (frame_v2_all 재료) 같은 RX 로."""
    import acelang_frame_v2 as V2
    rows = [{"prompt": r["out"], "seed": r["seed"]} for r in F.load() + V2.load_v4()]
    s, _ = summ(rows, "ace")
    s["seed_has_bpm"] = sum(bool(re.search(RX["bpm"], r["seed"], re.I)) for r in rows)
    return s


def main():
    suno = [json.loads(l) for l in SUNO.read_text().splitlines()]
    ace = [json.loads(l) for l in ACE.read_text().splitlines()]
    ss, _ = summ(suno, "suno")
    sa, _ = summ(ace, "ace")
    out = {"meta": {"script": "repo:sunolanguage scripts/magic_prompts_v1.py", "rx": RX,
                    "src": {"suno": "agent-comm:projects/sunomusic/attachments/SUNO_MAGIC_PROMPTS_20261118/prompts.jsonl",
                            "ace": "agent-comm:projects/sunomusic/attachments/ACE_MAGIC_PROMPTS_20261119/prompts.jsonl"}},
           "suno_magic": ss, "ace_magic": sa, "ace_seeded_115": ace_seeded(),
           "uniq_all": {"suno": len({r["prompt"] for r in suno}), "ace": len({r["prompt"] for r in ace})}}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False, indent=1, default=list)[:9000])


if __name__ == "__main__":
    main()
