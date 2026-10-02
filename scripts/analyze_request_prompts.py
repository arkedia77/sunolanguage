"""요청층 프롬프트 ↔ 우리 코퍼스 대조 (2026-10-02 LEO 지시분으로 신설).

무엇을 재나
  주어진 Suno 프롬프트를 구(phrase)로 쪼개, 각 구가 **우리 코퍼스에 관측된 말인가**를 본다.
    ⑴`expr_concepts` 구 단위 완전일치(= 우리가 저작까지 한 원자) — attested_count 동반
    ⑵`suno_dictionary_v3` 낱말 단위(출력층 freq_total · 입력층 freq_input 분리 표기)
  ★장르 라벨·BPM·구조 지시는 **요청층**이라 「관측 0」이어도 결함이 아니다 — 층을 나눠 센다.
  ⛔「미관측」 = 「쓰면 안 된다」가 아니다. 우리 코퍼스(레퍼런스 619트랙)가 그 말을 본 적 없다는 뜻뿐이다.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "sunolang.db"
DICT = ROOT / "rag" / "suno_dictionary_v3.json"
# 요청층으로 분류할 패턴 — 관측 대상이 아니다(우리가 Suno 에 '달라고' 쓰는 말)
REQUEST_PAT = re.compile(r"\b(\d{2,3}\s*-?\s*\d{0,3}\s*bpm|tempo|vibe|verse|chorus|bridge|structure|"
                         r"radio-ready|mix|9:16|vertical|reel|instagram)\b", re.I)


def split_phrases(text):
    parts = re.split(r"[;,.\n]| and (?=[a-z])", text)
    return [re.sub(r"\s+", " ", p).strip().lower() for p in parts if p and p.strip()]


def load_dict_words():
    d = json.loads(DICT.read_text())
    words = {}
    for sec in ("mood_emotion", "timbre_texture", "tempo_rhythm", "instrument_phrases", "drum_vocab",
                "technique_patterns", "production_vocab", "vocal_expressions", "vocal_chorus",
                "dynamics_structure", "harmony_vocab"):
        for k, v in (d.get(sec) or {}).items():
            if isinstance(v, dict):
                words[k.lower()] = {"sec": sec, "total": v.get("freq_total") or v.get("count"),
                                    "input": v.get("input") or v.get("freq_input")}
            else:
                words.setdefault(k.lower(), {"sec": sec, "total": v, "input": None})
    return words


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not src:
        sys.exit("사용: analyze_request_prompts.py <prompts.json>")
    prompts = json.loads(src.read_text())
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    atoms = {r[0].lower(): (r[1], r[2], r[3]) for r in
             con.execute("select suno_term, attested_count, category, is_dead_zone from expr_concepts")}
    words = load_dict_words()

    print("=== 요청층 프롬프트 ↔ 코퍼스 대조 ===")
    print(f"대조 기준: expr_concepts {len(atoms)}원자 · 사전 v{json.loads(DICT.read_text())['version']} 낱말 {len(words)}\n")
    rows = []
    for p in prompts:
        ph = split_phrases(p["text"])
        hit_atom, hit_word, req, miss = [], [], [], []
        for x in ph:
            if REQUEST_PAT.search(x):
                req.append(x)
            elif x in atoms:
                hit_atom.append((x, atoms[x][0]))
            else:
                w = [t for t in re.findall(r"[a-z0-9\-]+", x) if t in words]
                (hit_word if w else miss).append((x, w))
        rows.append((p, ph, hit_atom, hit_word, req, miss))
        n = len(ph)
        print(f"[{p['id']}] {p['label']}  — 구 {n}개")
        print(f"   원자 완전일치 {len(hit_atom)} · 낱말 일치 {len(hit_word)} · 요청층 {len(req)} · ★미관측 {len(miss)}")
        if hit_atom:
            top = sorted(hit_atom, key=lambda t: -t[1])[:6]
            print("   관측 상위: " + ", ".join(f"{t}({c})" for t, c in top))
        if miss:
            print("   ★미관측: " + ", ".join(x for x, _ in miss[:8]) + ("" if len(miss) <= 8 else f" … +{len(miss)-8}"))
        print()

    tot_miss = sum(len(r[5]) for r in rows)
    tot_ph = sum(len(r[1]) for r in rows)
    print(f"합계: 구 {tot_ph} · 미관측 {tot_miss} ({tot_miss/tot_ph:.0%})")
    print("⛔「미관측」=「틀렸다」가 아니다 — 우리 레퍼런스 코퍼스가 그 말을 본 적 없다는 뜻이다.")


if __name__ == "__main__":
    main()
