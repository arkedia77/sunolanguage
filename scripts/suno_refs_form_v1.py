#!/usr/bin/env python3
"""suno_refs_form_v1.py — Suno 홈 레퍼런스 재수집(11-16)의 스타일 문장 꼴 체크 (LEO 11-16 «최근 수노에서 레퍼런스로 나온 곡들 쭉 체크»).
재료 = agent-comm:projects/sunomusic/attachments/SUNO_HOME_REFS_20261116/{refs.json, artist_albums.json} · 문면만(들림 0).
칸 = LEO 문구 분석(exchange/leo_prompts_20261115/analysis.md)과 같은 정규식 꼴 + 앨범 안 일관성."""
import collections, itertools, json, re, statistics as st, sys
from pathlib import Path

P = Path.home() / "agent-comm-sunolanguage/projects/sunomusic/attachments/SUNO_HOME_REFS_20261116"
F = {
    "bpm": r"\b\d{2,3}\s?bpm\b", "meter": r"\b[2-9]/[48]\b",
    "scene": r"\b(about|feels? like|like a|as if|story of|singing about|song about)\b",
    "flow": r"\b(chorus|verse|verses|bridge|outro|intro|build|builds|drop)\b",
    "neg_body": r"\b(no|not|without|rather than|avoid)\b",
    "female_male": r"\b(female|male)\b",
    "time_directive": r"\b(within (the )?first|\d+\s?(seconds|sec|bars))\b",
}


def feats(t):
    tl = t.lower(); f = {k: bool(re.search(v, tl)) for k, v in F.items()}
    segs = [s for s in re.split(r"[,.;]", t) if s.strip()]
    f["sentence"] = sum(len(s.split()) for s in segs) / max(1, len(segs)) >= 5
    f["bpm_first"] = bool(re.search(F["bpm"], re.split(r"(?<=[.;])\s", tl)[0])) if f["bpm"] else False
    w = re.findall(r"[A-Za-z][\w'-]*", t); f["titlecase"] = len(w) > 5 and sum(x[0].isupper() for x in w) / len(w) > 0.8
    f["korean"] = bool(re.search(r"[가-힣]", t))
    return f


def q(a):
    return [round(x) for x in st.quantiles(a, n=4)] if len(a) > 3 else a


def summ(name, texts):
    texts = [t for t in texts if t and t.strip()]
    c = collections.Counter()
    for t in texts:
        for k, v in feats(t).items(): c[k] += v
    n = len(texts)
    return {"group": name, "n": n, "chars_q": q([len(t) for t in texts]), **{k: f"{c[k]} ({100 * c[k] // max(1, n)}%)" for k in list(F) + ["sentence", "bpm_first", "titlecase", "korean"]}}


def main():
    refs = json.loads((P / "refs.json").read_text())["songs"]
    alb = json.loads((P / "artist_albums.json").read_text())["albums"]
    new = [s.get("style") for s in refs if s.get("seen_20261111") is False]
    old = [s.get("style") for s in refs if s.get("seen_20261111") is True]
    trk = [t.get("style") for a in alb for t in a.get("tracks", [])]
    ver = [t.get("style") for a in alb if a.get("user_is_verified") for t in a.get("tracks", [])]
    rows = [summ("홈 새로 걸림(11-11에 없던)", new), summ("홈 11-11에도 있던", old), summ("앨범 112장 곡", trk), summ("인증 앨범 2장 곡", ver)]
    neg = sum(bool(s.get("negative_tags")) for s in refs)
    # 앨범 안 일관성 — 스타일 문장 낱말 자카드(곡 쌍) · 모두 같은 문장인 앨범 수
    W = lambda t: set(re.findall(r"[a-z][a-z'-]+", (t or "").lower()))
    cons = []
    for a in alb:
        ss = [t.get("style") for t in a.get("tracks", []) if t.get("style")]
        if len(ss) < 3: continue
        J = [len(W(x) & W(y)) / max(1, len(W(x) | W(y))) for x, y in itertools.combinations(ss, 2)]
        cons.append({"album_key": a["album_key"], "n": len(ss), "identical": len(set(ss)) == 1, "jaccard_med": round(st.median(J), 2),
                     "chars_med": st.median(len(x) for x in ss), "core": sorted(set.intersection(*map(W, ss)))[:12]})
    out = {"rows": rows, "refs_negative_tags": neg, "albums_with_3plus": len(cons),
           "albums_identical_style": sum(c["identical"] for c in cons),
           "album_jaccard_q": q([c["jaccard_med"] * 100 for c in cons]), "albums": cons}
    o = Path(__file__).resolve().parent.parent / "data/suno_refs_form_v1.json"
    o.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for r in rows: print(json.dumps(r, ensure_ascii=False))
    print("neg_tags", neg, "albums≥3", len(cons), "identical", out["albums_identical_style"], "jaccard×100 q", out["album_jaccard_q"])


if __name__ == "__main__":
    main()
