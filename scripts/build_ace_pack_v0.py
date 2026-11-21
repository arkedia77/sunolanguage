#!/usr/bin/env python3
"""build_ace_pack_v0.py — ACE Music 언어 팩 v0 어휘 칸 (encore 210427 · LEO 11-21 «에이스뮤직랭귀지 팩»).
재료 = ACE 가 직접 쓴 글만(✦ 출력): 시범 30 · 수집 v2 40 · v3 우리 SP 24 · v4 45 · 빈칸 매직 100 (생성 0 · 0cr).
셈 = 출력마다 2~3낱말 구(B.grams) 문서 빈도 · ≥5 출력 · 숫자 든 구 뺌 · 칸 = 구 자체의 단서 낱말(acelang_frame_v1.SLOT · 같으면 SLOT 순서) · 단서 없으면 그 구가 든 문장의 칸 최빈 · Suno 사전 v2.2 대조(있으면 HS·V+).
쓰기 = data/acelang/ace_pack_v0.json 만. 이름 검사 = 대문자 낱말 빈도(capitalized_top)를 적어 손 확인(11-21: 실가수·그룹 이름 0 · 악기 상표 Roland·Juno·Hammond·Fender·Telecaster 만).
"""
import collections, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import acelang_frame_v1 as F
import acelang_frame_v2 as V2
import build_suno_phrase_dict_v2 as B

AT = Path.home() / "agent-comm-sunolanguage/projects/sunomusic/attachments"
V3 = AT / "acelang_collect_v3_우리SP_20261114.jsonl"
MAGIC = AT / "ACE_MAGIC_PROMPTS_20261119/prompts.jsonl"
DICT = REPO / "data/suno_phrase_dict_v2/dict.json"
OUT = REPO / "data/acelang/ace_pack_v0.json"


def load_all():
    rows = [{"set": r["set"], "out": r["out"]} for r in F.load() + V2.load_v4()]
    rows += [{"set": "v3", "out": json.loads(l)["out"]} for l in V3.read_text().splitlines()]
    rows += [{"set": "magic", "out": json.loads(l)["prompt"]} for l in MAGIC.read_text().splitlines()]
    return rows


def main():
    rows = load_all()
    D = {r["phrase"]: r for r in json.loads(DICT.read_text())["rows"]}
    df, slot_of = collections.Counter(), collections.defaultdict(collections.Counter)
    for r in rows:
        seen = set()
        for i, s in enumerate(F.sents(r["out"])):
            k = F.slot(s, i)
            for g in B.grams(s):
                if 2 <= len(g.split()) <= 3:
                    slot_of[g][k] += 1
                    seen.add(g)
        df.update(seen)
    keep = [(g, n) for g, n in df.most_common() if n >= 5]
    # 겹친 구 줄이기: 3낱말 구가 같은 수로 2낱말 구를 품으면 2낱말 구 뺌
    drop = {g2 for g3, n3 in keep if len(g3.split()) == 3 for g2, n2 in keep
            if len(g2.split()) == 2 and g2 in g3 and n2 - n3 <= 1}
    vocab = []
    for g, n in keep:
        if g in drop:
            continue
        if re.search(r"\d", g):
            continue  # BPM·연대 숫자 구는 꼴 칸(§틀)에서 셈
        d = D.get(g)
        hits = {k: len(rx.findall(g)) for k, rx in F.SLOT}
        own = max(hits, key=lambda k: (hits[k], -[x for x, _ in F.SLOT].index(k))) if max(hits.values()) else None
        vocab.append({"phrase": g, "ace_outputs": n, "slot": own or slot_of[g].most_common(1)[0][0], "slot_by": "구 자체" if own else "든 문장",
                      "suno_dict": bool(d), "suno_category": d["category"] if d else None,
                      "suno_HS": d["HS"] if d else 0, "suno_Vplus": d["V+"] if d else 0})
    caps = collections.Counter(w for r in rows for w in re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", r["out"]))
    by_slot = collections.defaultdict(list)
    for v in vocab:
        by_slot[v["slot"]].append(v)
    out = {"meta": {"script": "repo:sunolanguage scripts/build_ace_pack_v0.py", "n_outputs": len(rows),
                    "by_set": collections.Counter(r["set"] for r in rows), "min_outputs": 5,
                    "dict": "repo:sunolanguage data/suno_phrase_dict_v2/dict.json (v2.2)"},
           "vocab_n": len(vocab), "vocab_in_suno_dict": sum(v["suno_dict"] for v in vocab),
           "by_slot_n": {k: len(v) for k, v in by_slot.items()},
           "by_slot": {k: v for k, v in by_slot.items()},
           "capitalized_top": caps.most_common(80)}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=list))
    print(json.dumps({k: out[k] for k in ("meta", "vocab_n", "vocab_in_suno_dict", "by_slot_n")}, ensure_ascii=False, default=list))
    for k, v in by_slot.items():
        print("==", k, [(x["phrase"], x["ace_outputs"], "S" if x["suno_dict"] else "-") for x in v[:30]])
    print("CAPS", caps.most_common(80))


if __name__ == "__main__":
    main()
