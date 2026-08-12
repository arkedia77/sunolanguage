#!/usr/bin/env python3
"""메타태그 외부 탐색 v0 — 외부 공개출처 태그 원장 + 코퍼스 대조

배경: 지금까지의 브라켓/메타태그 지식은 전부 자체 코퍼스 리버스 산출물이었다.
오너 지시(08-11) = 「유튜브·외부에서, 공개된 것만」 탐색.

★대조축의 정의 (오독 방지 — 이 주석이 판정의 전부다)
  코퍼스 브라켓 = `parse_slot_entities_v3.py` 가 merged_4values.json 의
  song["suno_reanalysis"][*]["lyrics"] 에서 뽑은 것 = **Suno가 스스로 출력한 브라켓**.
  따라서 본 대조가 답하는 질문은 오직 하나:
      "Suno 자신이 그 표기를 뱉은 적이 있는가?"
  답하지 '않는' 질문:
      "그 태그를 입력하면 Suno가 반응하는가?"  ← 출력어휘 ≠ 입력제어. 별도 실험 필요.
  그러므로 ABSENT = 「Suno가 안 뱉었다」이지 「안 먹힌다」가 아니다.

검산: 양성대조군(verse/chorus 등)이 0이면 질의 철자가 틀린 것이지 코퍼스가 빈 게 아니다.
      음성대조군이 0이 아니면 매칭이 헐거운 것이다. 둘 다 실패 시 즉시 abort.
"""
import json
import re
import sqlite3
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
OUT_DIR = ROOT / "data" / "metatag_external"

BRACKET_SOURCES = ("bracket_entity", "stems_bracket")
SP_SOURCES = ("sp_entity", "stems_sp", "suno_sp_full")

# ─────────────────────────────────────────────────────────────
# 외부 출처 원장 — 전부 에이전트가 실제 fetch 한 URL 기반.
# 기억/추측으로 채운 태그는 한 건도 넣지 않는다(각 보고서의 "unsourced" 절은 제외함).
# ─────────────────────────────────────────────────────────────
SOURCES = OrderedDict([
    ("official_hub", {
        "grade": "A_official",
        "url": "https://suno.com/hub/how-to-make-a-song",
        "note": "suno.com 도메인이나 헬프센터 아닌 마케팅/SEO 문서(저자 바이라인 있음). 갱신 2026-08-11",
        "provenance": "first_party",
    }),
    ("official_release_notes", {
        "grade": "A_official",
        "url": "https://about.suno.com/release-notes",
        "note": "제품 체인지로그(진성 1차). 2024-09-19 / 2024-10-10 항목",
        "provenance": "first_party",
    }),
    ("yt_master_ai_fast", {
        "grade": "B_youtube",
        "url": "https://www.youtube.com/watch?v=40Pg2iNnWR4",
        "note": "설명란에 'Meta Tags Used:' 블록 + 태그별 데모 챕터. 유튜브 채널 중 유일하게 시연 구조",
        "provenance": "creator_demo",
    }),
    ("yt_ai_controversy", {
        "grade": "B_youtube",
        "url": "https://www.youtube.com/watch?v=D5FBP-vv72c",
        "note": "커리큘럼 나열(암송). 검증 주장 없음",
        "provenance": "recited",
    }),
    ("yt_ai_tune_craft", {
        "grade": "B_youtube",
        "url": "https://www.youtube.com/watch?v=JHd6yae77fY",
        "note": "영상 내 시연 주장",
        "provenance": "creator_demo",
    }),
    ("gh_stayen", {
        "grade": "C_community",
        "url": "https://github.com/stayen/suno-reference",
        "note": "184개. 공개 게시글 취합 + 자체 400회 생성 교차시험 주장. ★유일하게 반증(무효 태그) 목록을 가진 출처",
        "provenance": "compiled_plus_self_tested",
    }),
    ("blog_blakecrosley", {
        "grade": "C_community",
        "url": "https://blakecrosley.com/guides/suno",
        "note": "본인 수천 트랙 테스트 주장. 요약기 경유 수집이라 누락 가능",
        "provenance": "claims_self_tested",
    }),
    ("blog_hookgenius", {
        "grade": "C_community",
        "url": "https://hookgenius.app/learn/suno-metatags-complete-list/",
        "note": "'v5의 모든 작동 태그' 주장하나 방법론 무기재. 상업 블로그",
        "provenance": "asserted_no_method",
    }),
    ("blog_jackrighteous", {
        "grade": "C_community",
        "url": "https://jackrighteous.com/en-us/pages/suno-ai-meta-tags-guide",
        "note": "★자체 헤지: '생성 관례이지 보장된 소프트웨어 명령이 아님'",
        "provenance": "hedged",
    }),
])

# tag literal -> [source keys]
EXTERNAL_TAGS = OrderedDict()


def add(source_key, tags):
    for t in tags:
        EXTERNAL_TAGS.setdefault(t, []).append(source_key)


add("official_hub", ["[Verse]", "[Verse 1]", "[Chorus]", "[Bridge]", "[Intro]"])
add("official_release_notes", ["[drum break]", "[female vocals]"])

add("yt_master_ai_fast", [
    "[Angry verse]", "[Crowd sings]", "[Crowd yells]",
    "[Chorus, modulate up a key]", "[Chorus, modulate down a key]",
    "[Interlude]", "[Guitar solo]",
])
add("yt_ai_controversy", [
    "[Verse]", "[Chorus]", "[Bridge]", "[Intro]", "[Hook]", "[Interlude]", "[Outro]",
])
add("yt_ai_tune_craft", ["[Primal Scream]"])

add("gh_stayen", [
    "[track]", "[accelerando]", "[ad-lib]", "[ambient]", "[announcer]", "[aria-rise]",
    "[arpeggio]", "[arrangement]", "[articulation]", "[attack]", "[background-vocals]",
    "[bass]", "[bass-slide]", "[beat-switch]", "[big finish]", "[bleep]", "[break]",
    "[breakdown]", "[bridge]", "[build]", "[cadence]", "[cadential]",
    "[call-and-response]", "[chant]", "[chant-loop]", "[choir]", "[chorus]",
    "[chromatic]", "[climax]", "[cluster]", "[coda]", "[compression]", "[control]",
    "[consonance]", "[content]", "[counterpoint]", "[crescendo]", "[development]",
    "[diminuendo]", "[dissonance]", "[distorted vocals]", "[distortion]", "[drop]",
    "[drum-fill]", "[duet]", "[dynamics]", "[echo]", "[effects]", "[element]",
    "[emotional]", "[end]", "[ensemble]", "[epic]", "[episode]", "[eq]", "[era]",
    "[exposition]", "[extend-style]", "[fade]", "[female]", "[fermata]",
    "[field-recording]", "[finale]", "[focus]", "[fragmentation]", "[fugue]", "[gain]",
    "[genre]", "[glissando]", "[glitch]", "[grind]", "[happy]", "[harmonics]",
    "[harmonies]", "[harmony]", "[hook]", "[improvisation]", "[inflection]",
    "[instrument]", "[instruments]", "[instrumental]", "[intensity]", "[interlude]",
    "[intermezzo]", "[intro]", "[inversion]", "[lament]", "[language]", "[laughter]",
    "[layering]", "[legato]", "[length]", "[loop-friendly]", "[male]", "[male vocal]",
    "[female vocal]", "[marcato]", "[minuet]", "[modulation]", "[mood]", "[mutation]",
    "[narrator]", "[no]", "[no-repeat]", "[orchestra]", "[orchestration]", "[outro]",
    "[pad]", "[pedal-point]", "[personae]", "[pizzicato]", "[polyphony]",
    "[power-off drop]", "[pre-chorus]", "[prelude]", "[pronunciation]", "[pulse]",
    "[quiet arrangement]", "[rapped verse]", "[recapitulation]", "[refrain]",
    "[register]", "[resolution]", "[retrograde]", "[reverb]", "[reverberate]",
    "[rhythm]", "[rhythmic-motif]", "[ritardando]", "[riff]", "[rise]", "[rondo]",
    "[sad]", "[scale]", "[scat break]", "[scherzo]", "[secondary theme]", "[sequence]",
    "[sforzando]", "[sfx]", "[shout]", "[signal-processing]", "[silence]",
    "[sincopation]", "[siren]", "[solo]", "[sonority]", "[spoken word]", "[staccato]",
    "[start]", "[stereo]", "[stretto]", "[structure]", "[style]", "[subject]",
    "[subharmonic]", "[sustain]", "[swell]", "[syncopation]", "[technique]", "[tempo]",
    "[tension-release]", "[tenuto]", "[tessitura]", "[texture]", "[theme]", "[timbre]",
    "[tone]", "[tone-cluster]", "[transition]", "[tremolo]", "[trio]", "[variation]",
    "[verse]", "[vibe]", "[vocalist]", "[vocal-style]", "[vocals]", "[vocoder]",
    "[voicing]", "[vulnerable vocals]", "[whisper]", "[whispers]", "[whispering]",
])

add("blog_blakecrosley", [
    "[Intro]", "[Verse]", "[Verse 1]", "[Verse 2]", "[Pre-Chorus]", "[Chorus]",
    "[Post-Chorus]", "[Bridge]", "[Breakdown]", "[Build]", "[Build-Up]", "[Drop]",
    "[Hook]", "[Interlude]", "[Outro]", "[End]", "[Instrumental]",
    "[Instrumental Intro]", "[Instrumental Break]", "[Guitar Solo]", "[Piano Solo]",
    "[Drum Solo]", "[Bass Solo]", "[Saxophone Solo]", "[Strings Rise]",
    "[Percussion Break]", "[Synth Solo]", "[Male Vocal]", "[Female Vocal]", "[Duet]",
    "[Choir]", "[Harmony]", "[Rap]", "[Spoken Word]", "[Whisper]", "[Scream]",
    "[Ad-lib]", "[Humming]", "[Backing Vocals]", "[Fade In]", "[Fade Out]",
    "[Silence]", "[Crescendo]", "[Decrescendo]", "[Key Change]",
])

add("blog_hookgenius", [
    "[Whispered]", "[Soft]", "[Gentle]", "[Quiet]", "[Spoken]", "[Powerful]",
    "[Belted]", "[Shouted]", "[Screamed]", "[Growled]", "[Intense]", "[Falsetto]",
    "[Head Voice]", "[Chest Voice]", "[Breathy]", "[Raspy]", "[Smooth]", "[Soulful]",
    "[Operatic]", "[Nasal]", "[Airy]", "[Harmonies]", "[Ad-libs]", "[Vocal Run]",
    "[Melisma]", "[Vibrato]", "[Staccato]", "[Legato]", "[Call and Response]",
    "[Chant]", "[Rapped]", "[Fast Rap]", "[Slow Flow]", "[Melodic Rap]",
    "[Trap Flow]", "[Boom Bap Flow]", "[Mumble Rap]", "[Double Time]", "[Swell]",
])

add("blog_jackrighteous", [
    "[Refrain]", "[Violin Solo]", "[Drum Break]", "[A Cappella]", "[Group Vocal]",
    "[Half-Time]", "[Double-Time]", "[Sparse Instrumentation]", "[Full Band]",
    "[Theme]", "[Final Chorus]",
])

# 외부가 스스로 '작동 안 함'이라 밝힌 것 — 수집 대상이자 별도 취급(무효 주장 원장)
EXTERNAL_NEGATIVE_CLAIMS = {
    "[autotune: ...]": "unsupported (gh_stayen)",
    "[filter: ...]": "inefficient (gh_stayen)",
    "[loop: ...]": "unsupported (gh_stayen)",
    "[mix, mixing: ...]": "inefficient (gh_stayen)",
    "[master: ...]": "inefficient (gh_stayen)",
    "[pan, panning: ...]": "inefficient (gh_stayen)",
    "[style: none]": "invalid (gh_stayen)",
    "[end]": "빈번히 무시됨 — '[5 second fade out][end] 조차 정지 못시킴' (gh_stayen 인용)",
    "[personae]": "사용자 시도일 뿐 공식 미지원 (gh_stayen)",
}

# 수집했으나 전량 회수 실패한 출처(표본만 확보) — 「없음」 아니라 「안 봄」으로 남긴다
PARTIAL_SOURCES = {
    "musci.io": "브라켓문자열 336건 존재 확인, 전량 미회수(표본만). https://musci.io/blog/suno-tags",
    "entrepeneur4lyf/suno_ai_meta_tags_guide": "313건 존재 확인, 전량 미회수(표본만). 출처주장 0건(grep 검증)",
    "reddit r/SunoAI": "★전면 접근 불가(403). 태그 실효성 논쟁의 주무대인데 표본 0",
    "youtube 자막": "전 영상 0건 회수(봇차단). 구술 태그목록 전량 미독",
}

NORM_RE = re.compile(r"[\s\-_]+")


def norm(s):
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    s = s.lower().strip()
    s = NORM_RE.sub(" ", s)
    return s.strip(" .,!?")


def load_corpus(con):
    """(sentence, song_id) 쌍으로 받는다 — 곡 수가 attestation 강도의 단위."""
    q = ("SELECT DISTINCT sentence, song_id FROM entries "
         "WHERE source IN (%s) AND sentence IS NOT NULL")
    brackets = list(con.execute(q % ",".join("?" * len(BRACKET_SOURCES)), BRACKET_SOURCES))
    sps = list(con.execute(q % ",".join("?" * len(SP_SOURCES)), SP_SOURCES))
    return brackets, sps


def build_index(brackets, sps):
    """정규화 문자열 -> {원문 표기 집합, 곡 집합}"""
    exact = {}
    for text, sid in brackets:
        e = exact.setdefault(norm(text), {"raw": set(), "songs": set()})
        e["raw"].add(text)
        e["songs"].add(sid)
    bracket_pairs = [(norm(t), sid) for t, sid in brackets]
    sp_pairs = [(norm(t), sid) for t, sid in sps]
    return exact, bracket_pairs, sp_pairs


def probe(tag, exact, bracket_pairs, sp_pairs):
    """★부분일치는 반드시 단어경계로. 부분문자열이면 [no]가 'piano'에, [end]가 'bend'에 걸린다."""
    n = norm(tag)
    if not n:
        return {"normalized": n, "verdict": "ABSENT", "bracket_exact": 0,
                "bracket_exact_songs": 0, "bracket_exact_samples": [],
                "bracket_contains": 0, "bracket_contains_songs": 0,
                "sp_contains": 0, "sp_contains_songs": 0}

    hit = exact.get(n)
    pat = re.compile(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])")

    c_forms, c_songs = set(), set()
    for text, sid in bracket_pairs:
        if text != n and pat.search(text):
            c_forms.add(text)
            c_songs.add(sid)

    s_forms, s_songs = set(), set()
    for text, sid in sp_pairs:
        if pat.search(text):
            s_forms.add(text)
            s_songs.add(sid)

    if hit:
        verdict = "EMITTED_EXACT"
    elif c_forms:
        verdict = "EMITTED_PARTIAL"
    elif s_forms:
        verdict = "SP_ONLY"
    else:
        verdict = "ABSENT"

    return {
        "normalized": n,
        "verdict": verdict,
        "bracket_exact": len(hit["raw"]) if hit else 0,
        "bracket_exact_songs": len(hit["songs"]) if hit else 0,
        "bracket_exact_samples": sorted(hit["raw"])[:3] if hit else [],
        "bracket_contains": len(c_forms),
        "bracket_contains_songs": len(c_songs),
        "bracket_contains_samples": sorted(c_forms)[:3],
        "sp_contains": len(s_forms),
        "sp_contains_songs": len(s_songs),
    }


POSITIVE_CONTROLS = ["[Verse]", "[Chorus]", "[Intro]", "[Instrumental]"]
NEGATIVE_CONTROLS = ["[zzqqxx not a real tag]", "[qwertyuiop asdfgh]"]


def main():
    if not DB.exists():
        sys.exit(f"코퍼스 없음: {DB}")
    con = sqlite3.connect(DB)
    brackets, sps = load_corpus(con)
    exact, bracket_pairs, sp_pairs = build_index(brackets, sps)

    print(f"코퍼스: 고유 브라켓 {len(exact)}종 / 브라켓-곡쌍 {len(bracket_pairs)} / SP문장-곡쌍 {len(sp_pairs)}")

    # ── 검산 먼저. 실패하면 결과를 내지 않는다 ──
    ctrl = {"positive": {}, "negative": {}}
    ok = True
    for t in POSITIVE_CONTROLS:
        r = probe(t, exact, bracket_pairs, sp_pairs)
        ctrl["positive"][t] = r
        if r["bracket_exact"] == 0:
            ok = False
            print(f"  ✗ 양성대조 실패 {t} → 0건. 질의 철자/정규화가 틀렸다(코퍼스가 빈 게 아님)")
        else:
            print(f"  ✓ 양성대조 {t} = {r['bracket_exact_songs']}곡")
    for t in NEGATIVE_CONTROLS:
        r = probe(t, exact, bracket_pairs, sp_pairs)
        ctrl["negative"][t] = r
        if r["bracket_exact"] or r["bracket_contains"] or r["sp_contains"]:
            ok = False
            print(f"  ✗ 음성대조 실패 {t} → 매칭이 헐겁다")
        else:
            print(f"  ✓ 음성대조 {t} = 0건")
    if not ok:
        sys.exit("검산 실패 — 판정 중단(거짓 0 방지)")

    results = {}
    for tag, srcs in EXTERNAL_TAGS.items():
        r = probe(tag, exact, bracket_pairs, sp_pairs)
        r["sources"] = srcs
        r["best_grade"] = min(SOURCES[s]["grade"] for s in srcs)
        results[tag] = r

    counts = {}
    for r in results.values():
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    # ── 역방향 격차: Suno가 자주 뱉는데 외부 어느 목록에도 없는 표기 ──
    # (외부 탐색의 소득만 세면 절반만 보는 것 — 외부가 '놓친 것'이 대칭축)
    ext_norms = {norm(t) for t in EXTERNAL_TAGS}
    corpus_only = []
    for n, e in exact.items():
        if n in ext_norms:
            continue
        corpus_only.append({
            "bracket": sorted(e["raw"])[0],
            "normalized": n,
            "songs": len(e["songs"]),
        })
    corpus_only.sort(key=lambda x: -x["songs"])

    print("\n역방향 격차 — Suno가 뱉지만 외부 목록에 없는 상위 표기")
    for row in corpus_only[:12]:
        print(f"  {row['songs']:4d}곡  {row['bracket']!r}")

    print("\n판정 분포 (질문='Suno가 그 표기를 뱉은 적 있는가')")
    for k in ("EMITTED_EXACT", "EMITTED_PARTIAL", "SP_ONLY", "ABSENT"):
        print(f"  {k:16s} {counts.get(k, 0):4d}")
    print(f"  {'합계':16s} {len(results):4d}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_by": "scripts/metatag_external_crosscheck.py",
        "corpus": {
            "db": str(DB.relative_to(ROOT)),
            "bracket_sources": list(BRACKET_SOURCES),
            "sp_sources": list(SP_SOURCES),
            "distinct_brackets": len(exact),
            "distinct_sp_sentence_song_pairs": len(sp_pairs),
            "provenance": "merged_4values.json -> suno_reanalysis[*].lyrics = Suno 자신의 출력 브라켓",
        },
        "question_answered": "Suno가 이 표기를 스스로 뱉은 적이 있는가",
        "question_NOT_answered": "이 태그를 입력하면 Suno가 반응하는가 (출력어휘 != 입력제어)",
        "controls": ctrl,
        "sources": SOURCES,
        "counts": counts,
        "tags": results,
        "external_negative_claims": EXTERNAL_NEGATIVE_CLAIMS,
        "partial_or_unreached_sources": PARTIAL_SOURCES,
        "corpus_only_top100": corpus_only[:100],
        "corpus_only_total": len(corpus_only),
    }
    out = OUT_DIR / "external_metatag_crosscheck_v0.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"\n저장: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
