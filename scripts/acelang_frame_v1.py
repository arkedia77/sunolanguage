#!/usr/bin/env python3
"""acelang_frame_v1.py — ACE ✦(마법사) 출력 수집본 → 틀·흔들림·낱말 층 셈 (encore 223102·224045 · sunomusic 235201). 쓰기 = data/acelang/frame_v1.json 만.
문장 칸 판정은 낱말 단서(휴리스틱) — 표본 손 확인은 보고서에."""
import collections, itertools, json, re, statistics as st, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import build_suno_phrase_dict_v2 as B

AT = Path.home() / "agent-comm-sunolanguage/projects/sunomusic/attachments"
SLOT = [  # (칸, 단서) — 한 문장의 칸 = 단서 수가 가장 많은 칸 · 같으면 위 순서
    ("구조", r"\b(intro|verses?|choruses|chorus|pre-chorus|bridge|outro|break|breakdown|drop|opens?|opening|closes?|closing|ends?|ending|final|fades?|builds?|swell\w*|section|arrangement|hook)\b"),
    ("믹스", r"\b(mix|mixed|production|produced|master\w*|reverb|compression|compressed|saturat\w*|stereo|polished|tape|lo-fi|analog|warmth|sidechain\w*|side-chain\w*|low-end|headroom|clarity)\b"),
    ("보컬", r"\b(vocals?|voices?|singer|sung|sings|rap\w*|harmon\w*|chants?|croon\w*|falsetto|delivery|ad-libs?|belt\w*|whisper\w*|duet|crooner)\b"),
    ("리듬·저역", r"\b(kick|drums?|beats?|groove|bass\w*|808s?|hi-hats?|snares?|claps?|percussion|rhythm\w*|shuffle|swing|four-on-the-floor|backbeat|rimshots?|toms?|cymbals?)\b"),
    ("리드·화성", r"\b(guitars?|piano|synths?|strings|sax\w*|accordion|melod\w*|leads?|keys|organ|brass|horns?|violin|cello|pads?|chords?|arpeggi\w*|plucks?|stabs?|rhodes|flute|trumpet|riffs?)\b"),
]
SLOT = [(k, re.compile(v, re.I)) for k, v in SLOT]
ORDER = ["장르", "리듬·저역", "리드·화성", "보컬", "믹스", "구조"]


def sents(t):
    return [s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s]


def slot(s, i):
    hits = {k: len(rx.findall(s)) for k, rx in SLOT}
    best = max(hits.values())
    if i == 0 and (re.search(r"\b\d{2,3} ?bpm\b", s, re.I) or best < 3):
        return "장르"
    return next(k for k, _ in SLOT if hits[k] == best) if best else "그 밖"


def words(t):
    return {w for w in re.findall(r"[a-z][a-z\-']+", t.lower()) if w not in B.STOP and len(w) > 2}


def load():
    rows = []
    for l in (AT / "acelang_collect_v2_20261113.jsonl").read_text().splitlines():
        d = json.loads(l); rows.append({"set": "v2", "seed": d["seed_id"] + " " + d["seed_text"], "n": d["press_n"], "out": d["out"]})
    for l in (AT / "acelang_pilot_20261113.jsonl").read_text().splitlines():
        d = json.loads(l); rows.append({"set": "pilot", "seed": d["seed"], "n": d["round"], "out": d["out"]})
    return rows


def main():
    rows = load()
    D = {r["phrase"]: r for r in json.loads((REPO / "data/suno_phrase_dict_v2/dict.json").read_text())["rows"]}
    sk = lambda r: r["V+"] >= 5 or r["HS"] >= 3 or r["AG"] >= 2
    out = {"n": len(rows), "by_set": collections.Counter(r["set"] for r in rows)}
    for r in rows:
        ss = sents(r["out"])
        r["chars"] = len(r["out"]); r["n_sent"] = len(ss); r["sent_len"] = [len(s) for s in ss]
        r["slots"] = [slot(s, i) for i, s in enumerate(ss)]
        r["last_is_structure"] = r["slots"][-1] == "구조"
        r["last_share"] = round(len(ss[-1]) / len(r["out"]), 2)
        seed_bpm = re.search(r"(\d{2,3}) BPM", r["seed"])
        r["bpm_kept"] = bool(seed_bpm and re.search(rf"\b{seed_bpm.group(1)} ?BPM", r["out"], re.I)) if seed_bpm else None
        r["bpm_any"] = bool(re.search(r"\b\d{2,3} ?BPM\b", r["out"], re.I))
        r["key"] = bool(re.search(r"\b[A-G](♭|♯|b|#|-flat|-sharp)? (major|minor)\b", r["out"]))
        segs = [s.strip() for s in re.split(r"[,.;]", r["out"]) if s.strip()]
        hit = 0
        for s in segs:
            gs = [g for g in B.grams(s) if g in D and len(g.split()) >= 2 and sk(D[g])]
            hit += bool(gs)
        r["chunks"] = len(segs); r["chunks_suno"] = hit
    seq = lambda r: [s for i, s in enumerate(r["slots"]) if i == 0 or s != r["slots"][i - 1]]
    def mono(r):  # 칸 순서가 ORDER 를 거스르지 않나(그 밖 빼고)
        idx = [ORDER.index(s) for s in seq(r) if s in ORDER]
        return all(a <= b for a, b in zip(idx, idx[1:]))
    out["chars"] = {"med": st.median(r["chars"] for r in rows), "min": min(r["chars"] for r in rows), "max": max(r["chars"] for r in rows)}
    out["n_sent"] = dict(collections.Counter(r["n_sent"] for r in rows))
    out["first_slot_genre"] = sum(r["slots"][0] == "장르" for r in rows)
    out["last_is_structure"] = sum(r["last_is_structure"] for r in rows)
    out["last_longest"] = sum(r["sent_len"][-1] == max(r["sent_len"]) for r in rows)
    out["last_share_med"] = st.median(r["last_share"] for r in rows)
    out["order_monotone"] = sum(mono(r) for r in rows)
    out["has_mix_sentence"] = sum("믹스" in r["slots"] for r in rows)
    out["slot_seq_top"] = collections.Counter(" → ".join(seq(r)) for r in rows).most_common(8)
    out["bpm_kept"] = f"{sum(r['bpm_kept'] for r in rows if r['bpm_kept'] is not None)}/{sum(r['bpm_kept'] is not None for r in rows)}"
    out["bpm_any_when_seed_no_bpm"] = f"{sum(r['bpm_any'] for r in rows if r['bpm_kept'] is None)}/{sum(r['bpm_kept'] is None for r in rows)}"
    out["key_added"] = sum(r["key"] for r in rows)
    out["chunks_suno_share_med"] = st.median(r["chunks_suno"] / r["chunks"] for r in rows)
    # 씨앗별 흔들림 — 같은 씨앗 출력끼리 낱말 자카드
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["set"], r["seed"])].append(r)
    seeds = []
    for (sset, sd), rs in sorted(by.items()):
        J = [len(words(a["out"]) & words(b["out"])) / len(words(a["out"]) | words(b["out"])) for a, b in itertools.combinations(rs, 2)]
        core = set.intersection(*(words(r["out"]) for r in rs)) if rs else set()
        seeds.append({"set": sset, "seed": sd, "n": len(rs), "chars": [r["chars"] for r in rs], "n_sent": [r["n_sent"] for r in rs],
                      "jaccard_med": round(st.median(J), 2) if J else None, "core_all": sorted(core)[:25],
                      "seq": collections.Counter(" → ".join(seq(r)) for r in rs).most_common(2),
                      "key_added": sum(r["key"] for r in rs), "bpm_kept": [r["bpm_kept"] for r in rs]})
    out["seeds"] = seeds
    # 낱말: ACE 가 자주 쓰는 구(출력 ≥5) ↔ Suno 사전
    df = collections.Counter()
    for r in rows:
        df.update(g for g in B.grams(r["out"]) if len(g.split()) >= 2)
    top = [(g, n) for g, n in df.most_common() if n >= 5][:80]
    out["ace_top_phrases"] = [{"phrase": g, "ace_outputs": n, **({k: D[g][k] for k in ("V+", "V-", "HS", "HU", "AG")} if g in D else {"in_dict": False})} for g, n in top]
    # Suno 가 지우는 꼴이 ACE 에 얼마나
    DEL = {"자리 낱말(in the background/midground/foreground)": r"\bin the (back|mid|fore)ground\b", "weave(s)": r"\bweaves?\b", "embrace(s)": r"\bembrac", "«The mix/production …» 문장 머리": r"(^|\.\s+)The (mix|production)\b"}
    out["suno_deleted_forms_in_ace"] = {k: sum(bool(re.search(v, r["out"], re.I)) for r in rows) for k, v in DEL.items()}
    o = REPO / "data/acelang"; o.mkdir(exist_ok=True)
    (o / "frame_v1.json").write_text(json.dumps({"summary": out, "rows": rows}, ensure_ascii=False, indent=1, default=list))
    print(json.dumps({k: v for k, v in out.items() if k not in ("seeds", "ace_top_phrases")}, ensure_ascii=False, indent=1, default=list))
    for s in seeds:
        print(s["set"], s["seed"][:40], "n", s["n"], "자", s["chars"], "문장", s["n_sent"], "J", s["jaccard_med"], "조", s["key_added"], "BPM", s["bpm_kept"], s["seq"][0])
    for p in out["ace_top_phrases"][:45]:
        print(p)


if __name__ == "__main__":
    main()
