#!/usr/bin/env python3
"""n_series_gate.py — N시리즈 설계 배치 게이트(발주 전 hard fail 판정).

★게이트 PASS는 곡의 품질을 보증하지 않는다. 여기서 보는 것은 규격 위반과
「내가 코퍼스 밖으로 나갔는가」뿐이다.

판정 항목:
  G1 SP 길이 ≤ 1000자                     — 오너 규칙(SP 1000자)
  G2 선언 어휘가 출력층 코퍼스에 관측되는가 — ⛔사전은 화이트리스트가 아니다. 미관측은
                                             「금지」가 아니라 **발주 전에 내가 알아야 하는 사실**.
  G3 SP 기재 BPM/키가 필드와 일치          — 적재 메타와 처방문 불일치 차단
  G4 가사 브래킷 = 섹션 태그 ∪ 사운드 큐    — 명찰형(화자 이름) 0 · 한글 브래킷 0
  G5 제목 중복 0                           — 배치 내 ∪ PG songs 전건
  G6 가사 jaccard 최대치                   — 대조군 = PG 내 우리 곡 전건 ∪ 같은 배치 앞 곡

사용: .venv/bin/python scripts/n_series_gate.py data/n041/N041_design.json [--no-db]
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB = ROOT / "data/n_series_attested_vocab.json"

SP_MAX = 1000
JACCARD_MAX = 0.35
SECTION = re.compile(
    r"^\[(Intro|Verse|Chorus|Pre-Chorus|Post-Chorus|Final Chorus|Bridge|Hook|Outro|"
    r"Interlude|Instrumental|Instrumental Break|Build|Climax|Refrain|Break|Drop|Solo)"
    r"\s*\d*\]$", re.I)
HANGUL = re.compile(r"[가-힣]")


def tok(s: str) -> set[str]:
    return set(re.findall(r"[가-힣]{2,}|[a-zA-Z]{3,}", s))


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_vocab():
    if not VOCAB.exists():
        sys.exit(f"❌ 어휘 자료 없음 — 먼저 scripts/n_series_vocab.py 실행: {VOCAB}")
    v = json.loads(VOCAB.read_text(encoding="utf-8"))
    return (set(v["entities"]) | set(v["phrases"]), set(v["words_output_layer"]),
            set(g.lower() for g in v["genres"]))


def check_term(t: str, att: set, words: set) -> bool:
    t = t.lower().strip()
    if t in att:
        return True
    parts = t.split()
    # 수식어 + 관측 엔티티 조합은 허용(코퍼스가 modifier를 따로 싣는다)
    for i in range(1, len(parts)):
        head = " ".join(parts[i:])
        if head in att and all(p in words or p in att for p in parts[:i]):
            return True
    return len(parts) == 1 and t in words


def gate(design_path: Path, use_db=True):
    d = json.loads(design_path.read_text(encoding="utf-8"))
    batch = d["batch"]
    songs = d["songs"]
    att, words, genres = load_vocab()

    prior = []      # (title, tokens)
    if use_db:
        sys.path.insert(0, str(ROOT / "scripts"))
        from json_to_db import get_conn
        con = get_conn(); cur = con.cursor()
        cur.execute("SELECT title FROM songs")
        db_titles = {r[0] for r in cur.fetchall()}
        cur.execute("SELECT title, lyrics FROM songs WHERE source_project='sunolanguage'")
        prior = [(t, tok(l or "")) for t, l in cur.fetchall()]
        con.close()
    else:
        db_titles = set()

    fails, warns = [], []
    max_j_all = 0.0
    seen_titles, seen_tokens = set(), []
    rows = []

    for s in songs:
        line = f"{batch}_{s['pos']:02d}"
        sp, ly, title = s["sp"], s["lyrics"], s["title"]

        # G1
        if len(sp) > SP_MAX:
            fails.append(f"{line} G1 SP {len(sp)}자 > {SP_MAX}")
        # G2
        terms = s.get("terms") or []
        if not terms:
            fails.append(f"{line} G2 terms 미선언 — 어휘 점검 불가")
        unatt = [t for t in terms if not check_term(t, att, words)]
        native = (len(terms) - len(unatt)) / len(terms) if terms else 0.0
        if unatt:
            warns.append(f"{line} G2 미관측 {unatt}")
        g = s.get("genre", "").lower()
        g_core = re.sub(r"^korean\s+", "", g)   # 「Korean X」는 우리 입력층 관례(관측 라벨 아님)
        if g not in genres and g_core not in genres:
            warns.append(f"{line} G2 장르 라벨 미관측(핵 '{g_core}'도 0건): {s.get('genre')}")
        # G3
        if f"{s['bpm']} BPM" not in sp:
            fails.append(f"{line} G3 SP에 BPM {s['bpm']} 없음")
        if s["key"] not in sp:
            fails.append(f"{line} G3 SP에 키 {s['key']} 없음")
        # G4
        brackets = re.findall(r"^\s*\[[^\]]*\]\s*$", ly, re.M)
        n_sec = 0
        for b in brackets:
            b = b.strip()
            if SECTION.match(b):
                n_sec += 1
                continue
            inner = b[1:-1]
            if HANGUL.search(inner):
                fails.append(f"{line} G4 한글 브래킷: {b}")
            elif inner and inner[0].isupper():
                fails.append(f"{line} G4 명찰형 의심 브래킷: {b}")
        if HANGUL.search(" ".join(re.findall(r"\[[^\]]*\]", ly))):
            pass
        # G5
        if title in seen_titles:
            fails.append(f"{line} G5 배치 내 제목 중복: {title}")
        if title in db_titles:
            fails.append(f"{line} G5 PG 제목 중복: {title}")
        seen_titles.add(title)
        # G6
        t_now = tok(ly)
        cands = [(t, jaccard(t_now, tk)) for t, tk in prior] + \
                [(t, jaccard(t_now, tk)) for t, tk in seen_tokens]
        mj, mt = (max(cands, key=lambda x: x[1]) if cands else ("", 0.0))[::-1]
        max_j_all = max(max_j_all, mj)
        if mj >= JACCARD_MAX:
            fails.append(f"{line} G6 jaccard {mj:.3f} ≥ {JACCARD_MAX} vs 「{mt}」")
        seen_tokens.append((title, t_now))

        rows.append((line, title, len(sp), native, n_sec, mj, mt))

    print(f"■ {batch} 게이트 — {len(songs)}곡 · 대조군 {len(prior)}곡(PG 우리 곡 전건)")
    print(f"{'line':10} {'제목':22} {'SP자':>5} {'native':>7} {'섹션':>4} {'maxJ':>6}  최근접")
    for line, title, spn, nat, nsec, mj, mt in rows:
        print(f"{line:10} {title[:20]:22} {spn:5} {nat:7.4f} {nsec:4} {mj:6.3f}  {mt[:18]}")
    print(f"\n최대 jaccard(배치) = {max_j_all:.3f}")
    if warns:
        print("\n⚠ 경고(발주 차단 아님 — ★단 「미관측」은 내가 코퍼스 밖으로 나갔다는 사실이다):")
        for w in warns:
            print("   ", w)
    if fails:
        print("\n❌ HARD FAIL:")
        for f in fails:
            print("   ", f)
        return 1
    print("\n✅ 전건 PASS (hard fail 0)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--no-db", action="store_true")
    a = ap.parse_args()
    sys.exit(gate(Path(a.design), use_db=not a.no_db))
