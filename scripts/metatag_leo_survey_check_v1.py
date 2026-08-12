#!/usr/bin/env python3
"""LEO 조사분(텔레그램 6262, 08-12 02:05) 주장 실측 검증

중계=kimsecretary. ★출처는 LEO 측 조사(도구 미상)이고 kimsecretary는 검증 안 함 —
사실 판정이 내 몫이라 명시됨. 본 스크립트가 그 판정의 근거다.

검증 대상 주장 4개:
  C1. 「Suno 공식 Music Glossary에 Verse/Chorus/Bridge/Pre-Chorus/Intro/Outro/Hook/Break
      **구조를 명시**」 → 공식이 그것을 '브라켓 태그'로 문서화했는가?
  C2. 「가장 안정적인 건 구조 태그」 → 그 목록이 Suno 자체 출력에 실재하는가?
  C3. ★「복합 메타태그」(`[Verse 1 - Intimate Male Vocal]` / `[Chorus | soaring vocal | wide]`)
      → Suno 자신이 복합 브라켓을 쓰는가? 쓴다면 어떤 구분자로?
  C4. 「BPM/Key 태그는 conditioning이지 lock 아님」 → 코퍼스에 흔적이 있는가?
"""
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
OUT = ROOT / "data" / "metatag_external" / "leo_survey_check_v1.json"

BRACKET_SOURCES = ("bracket_entity", "stems_bracket")
SP_SOURCES = ("sp_entity", "stems_sp", "suno_sp_full")

# LEO 조사분이 제시한 목록 (원문 순서 보존)
LEO_STRUCTURE = ["[Intro]", "[Verse 1]", "[Pre-Chorus]", "[Chorus]", "[Verse 2]",
                 "[Bridge]", "[Final Chorus]", "[Outro]", "[End]"]
LEO_ARRANGE = ["[Instrumental]", "[Instrumental Break]", "[Break]", "[Breakdown]",
               "[Build]", "[Build-Up]", "[Drop]", "[Guitar Solo]", "[Piano Solo]",
               "[Saxophone Solo]", "[Hook]", "[Interlude]"]
LEO_VOCAL = ["[Male Vocal]", "[Female Vocal]", "[Whispered]", "[Spoken]", "[Belted]",
             "[Breathy Vocal]", "[Raspy Vocal]", "[Soft Vocal]", "[Harmony]",
             "[Harmonies]", "[Stacked Harmonies]", "[Backing Vocals]", "[Ad-libs]"]
LEO_DYNAMICS = ["crescendo", "diminuendo", "forte", "fortissimo", "pianissimo",
                "staccato", "legato", "vibrato", "tremolo"]
LEO_PARAM = ["[BPM: 82]", "[Key: F# minor]", "[Time Signature: 6/8]",
             "[BPM:120]", "[Key:Am]"]
# 원문이 「공식 용어집에 명시」라 주장한 것
LEO_CLAIMED_OFFICIAL = ["[Verse]", "[Chorus]", "[Bridge]", "[Intro]", "[Outro]",
                        "[Pre-Chorus]", "[Break]", "[Hook]"]

# 우리가 08-12 실측으로 확인한 '공식 출처에서 실제 브라켓으로 확인된' 전부
# (에이전트가 help.suno.com·about.suno.com·suno.com/hub 직접 fetch·raw 추출)
VERIFIED_OFFICIAL_BRACKETED = {"[Verse]", "[Verse 1]", "[Chorus]", "[Bridge]",
                               "[Intro]", "[drum break]", "[female vocals]"}

NORM_RE = re.compile(r"[\s\-_]+")


def norm(s):
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    s = s.lower().strip()
    return NORM_RE.sub(" ", s).strip(" .,!?:")


def main():
    con = sqlite3.connect(DB)
    q = ("SELECT DISTINCT sentence, song_id FROM entries "
         "WHERE source IN (%s) AND sentence IS NOT NULL")
    brackets = list(con.execute(q % ",".join("?" * len(BRACKET_SOURCES)), BRACKET_SOURCES))
    sps = list(con.execute(q % ",".join("?" * len(SP_SOURCES)), SP_SOURCES))

    exact = {}
    for t, sid in brackets:
        exact.setdefault(norm(t), {"raw": set(), "songs": set()})
        exact[norm(t)]["raw"].add(t)
        exact[norm(t)]["songs"].add(sid)
    sp_pairs = [(norm(t), sid) for t, sid in sps]

    if norm("[Intro]") not in exact or norm("[zzqq nope]") in exact:
        sys.exit("검산 실패 — 중단")
    print("검산 통과\n")

    def probe(tag):
        n = norm(tag)
        hit = exact.get(n)
        pat = re.compile(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])")
        sp_songs = {sid for t, sid in sp_pairs if pat.search(t)}
        return {"bracket_songs": len(hit["songs"]) if hit else 0,
                "sp_songs": len(sp_songs)}

    report = {}

    # ── C2: LEO 목록이 Suno 자체 출력에 실재하는가 ──
    print("■ C2 — LEO 제시 목록이 Suno 자체 출력 브라켓에 있는가 (곡수)")
    for label, group in (("구조", LEO_STRUCTURE), ("편곡", LEO_ARRANGE), ("보컬", LEO_VOCAL)):
        print(f"  [{label}]")
        g = {}
        for t in group:
            r = probe(t)
            g[t] = r
            mark = "✅" if r["bracket_songs"] else ("△SP" if r["sp_songs"] else "❌")
            print(f"    {mark} {t:24s} bracket={r['bracket_songs']:4d}곡  sp={r['sp_songs']:4d}곡")
        report[label] = g

    print("\n■ C4 — BPM/Key/박자 파라미터 태그")
    report["파라미터"] = {}
    for t in LEO_PARAM:
        r = probe(t)
        report["파라미터"][t] = r
        print(f"    {'✅' if r['bracket_songs'] else '❌'} {t:22s} bracket={r['bracket_songs']}곡")
    # 형태 자체(BPM: 숫자)가 브라켓에 등장하는지
    param_forms = [t for t, _ in brackets if re.search(r"(?i)\b(bpm|key|time signature)\b", t)]
    print(f"    ★브라켓에 BPM/Key/Time Signature 문자열 포함 = {len(param_forms)}종")
    report["파라미터_형태_출현"] = param_forms[:20]

    print("\n■ 다이내믹 용어 (LEO: 공식이 프롬프트 사용 권장)")
    report["다이내믹"] = {}
    for w in LEO_DYNAMICS:
        r = probe(w)
        report["다이내믹"][w] = r
        print(f"    {w:14s} bracket={r['bracket_songs']:3d}곡  sp={r['sp_songs']:4d}곡")

    # ── C3: ★복합 브라켓 — Suno 자신이 쓰는가, 구분자는? ──
    print("\n■ ★C3 — 복합 브라켓(섹션+서술)을 Suno 자신이 쓰는가")
    SECTION = re.compile(r"(?i)^(intro|verse|chorus|pre-?chorus|bridge|outro|hook|break|"
                         r"breakdown|interlude|instrumental|drop|build|section|refrain|coda)")
    # ★거짓양성 주의: 'Pre-Chorus'의 하이픈은 구분자가 아니라 단어의 일부다.
    #   맨 하이픈을 구분자로 잡으면 78/79가 Pre-Chorus로 채워진다(1차판이 그랬음).
    #   ⇒ 구분자는 `,` `|` `:` `(` 또는 **공백으로 둘러싸인 하이픈**만 인정.
    COMPOUND = re.compile(r"[,|:(]|\s-\s|\s–\s|\s—\s")
    sep_counter = Counter()
    compound_examples = []
    section_simple = 0
    seen_text = set()
    for t, sid in brackets:
        rest = t.strip()
        if rest in seen_text:
            continue
        seen_text.add(rest)
        if not SECTION.match(rest):
            continue
        m = COMPOUND.search(rest)
        if m:
            sep_counter[m.group(0).strip() or "-"] += 1
            compound_examples.append(rest)
        else:
            section_simple += 1
    print(f"    섹션 브라켓 중 단순형(섹션명만) = {section_simple}종")
    print(f"    ★복합형(섹션+구분자+서술) = {sum(sep_counter.values())}종")
    for sep, n in sep_counter.most_common():
        print(f"       구분자 {sep!r} : {n}종")
    for ex in compound_examples[:12]:
        print(f"       예: {ex!r}")
    report["복합브라켓"] = {"단순형": section_simple,
                        "복합형": sum(sep_counter.values()),
                        "구분자": dict(sep_counter),
                        "예시": compound_examples}

    # ── C1: 공식 문서가 실제로 브라켓으로 문서화했는가 ──
    print("\n■ ★C1 — 「공식 용어집에 명시」 주장 대조 (08-12 실측 대조군)")
    c1 = {}
    for t in LEO_CLAIMED_OFFICIAL:
        ok = t in VERIFIED_OFFICIAL_BRACKETED
        c1[t] = ok
        print(f"    {'✅ 공식 브라켓 확인' if ok else '❌ 공식에서 브라켓으로 확인 안 됨'}  {t}")
    report["C1_공식주장_대조"] = c1

    OUT.write_text(json.dumps({
        "source": "LEO 조사분 텔레그램 6262 (2026-08-12 02:05), 중계=kimsecretary",
        "caveat": "★LEO 조사분은 도구 미상 LLM 산출로 보이며 kimsecretary 미검증. 본 파일이 실측 대조.",
        "axis_note": "bracket_songs = Suno 자체 출력에 그 표기가 나온 곡 수. "
                     "0이라고 '입력 시 안 먹힌다'는 뜻이 아님(출력어휘≠입력제어).",
        "report": report,
    }, ensure_ascii=False, indent=2))
    print(f"\n저장: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
