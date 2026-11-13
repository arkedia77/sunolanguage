#!/usr/bin/env python3
"""acelang_ourSP_rewrite_v1.py — 우리 판 SP 원문 → ACE ✦ 출력(수집 v3 · 8곡 × 3) 변환 규칙 셈 (encore 235637 · sunomusic 002311). 쓰기 = data/acelang/ourSP_rewrite_v1.json 만."""
import collections, itertools, json, re, statistics as st, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import build_suno_phrase_dict_v2 as B
from acelang_frame_v1 import sents, slot, words, SLOT

F = Path.home() / "agent-comm-sunolanguage/projects/sunomusic/attachments/acelang_collect_v3_우리SP_20261114.jsonl"
KEY = re.compile(r"\b([A-G](?:♭|♯|b|#|-flat|-sharp)?) ?(major|minor)\b|\bkey of ([A-G][#b]?)( (major|minor))?", re.I)


def keyof(t):
    m = KEY.search(t)
    return None if not m else (m.group(1) or m.group(3)).upper() + " " + (m.group(2) or m.group(5) or "").lower()


def main():
    rows = [json.loads(l) for l in F.read_text().splitlines()]
    by = collections.defaultdict(list)
    for r in rows:
        by[r["gid"]].append(r)
    res, agg = [], collections.Counter()
    slot_keep = collections.defaultdict(list)
    added_all = collections.Counter()
    for gid, rs in sorted(by.items()):
        seed = rs[0]["seed_text"]
        ss = sents(seed.replace("\n", " "))
        sw = words(seed)
        bpm = re.search(r"(\d{2,3}) ?BPM", seed, re.I)
        per = []
        for r in rs:
            o = r["out"]; ow = words(o); os_ = sents(o)
            # 씨앗 문장 칸별 낱말이 출력에 남은 몫
            for i, s in enumerate(ss):
                k = slot(s, i); w = words(s)
                if w:
                    slot_keep[k].append(len(w & ow) / len(w))
            new = ow - sw
            added_all.update(new)
            per.append({"chars": len(o), "n_sent": len(os_), "keep": round(len(sw & ow) / len(sw), 2), "new_share": round(len(new) / len(ow), 2),
                        "bpm_kept": bool(bpm and re.search(rf"\b{bpm.group(1)} ?BPM", o, re.I)), "key_seed": keyof(seed), "key_out": keyof(o),
                        "first": slot(os_[0], 0), "last": slot(os_[-1], len(os_) - 1), "mix_sentence": any(slot(s, i) == "믹스" for i, s in enumerate(os_)),
                        "bpm_in_first_sentence": bool(bpm and re.search(rf"\b{bpm.group(1)} ?BPM", os_[0], re.I))})
        J = [len(words(a["out"]) & words(b["out"])) / len(words(a["out"]) | words(b["out"])) for a, b in itertools.combinations(rs, 2)]
        res.append({"gid": gid, "seed_chars": len(seed), "seed_sent": len(ss), "seed_slots": [slot(s, i) for i, s in enumerate(ss)], "outs": per, "jaccard_med": round(st.median(J), 2)})
    flat = [p for r in res for p in r["outs"]]
    summ = {
        "n": len(flat), "songs": len(res),
        "chars": f"씨앗 중앙 {st.median(r['seed_chars'] for r in res)} → 출력 중앙 {st.median(p['chars'] for p in flat)}",
        "sent": f"씨앗 중앙 {st.median(r['seed_sent'] for r in res)} → 출력 {dict(collections.Counter(p['n_sent'] for p in flat))}",
        "word_keep_med": st.median(p["keep"] for p in flat), "new_word_share_med": st.median(p["new_share"] for p in flat),
        "bpm_kept": f"{sum(p['bpm_kept'] for p in flat)}/{len(flat)}", "bpm_in_first_sentence": f"{sum(p['bpm_in_first_sentence'] for p in flat)}/{len(flat)}",
        "key_seed_has": sum(1 for p in flat if p["key_seed"]), "key_kept_same": sum(1 for p in flat if p["key_seed"] and p["key_seed"] == p["key_out"]),
        "key_dropped": sum(1 for p in flat if p["key_seed"] and not p["key_out"]), "key_changed": sum(1 for p in flat if p["key_seed"] and p["key_out"] and p["key_seed"] != p["key_out"]),
        "first_genre": sum(p["first"] == "장르" for p in flat), "last_structure": sum(p["last"] == "구조" for p in flat), "mix_sentence": sum(p["mix_sentence"] for p in flat),
        "slot_word_keep_med": {k: round(st.median(v), 2) for k, v in slot_keep.items()},
        "jaccard_med_by_song": {r["gid"]: r["jaccard_med"] for r in res},
        "added_words_top": [w for w, n in added_all.most_common(40)],
    }
    o = REPO / "data/acelang"; o.mkdir(exist_ok=True)
    (o / "ourSP_rewrite_v1.json").write_text(json.dumps({"summary": summ, "songs": res}, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    for r in res:
        print(r["gid"], r["seed_chars"], r["seed_slots"], [(p["chars"], p["n_sent"], p["keep"], p["key_seed"], p["key_out"]) for p in r["outs"]])


if __name__ == "__main__":
    main()
