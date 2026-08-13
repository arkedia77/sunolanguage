#!/usr/bin/env python3
"""나레이션 메타태그 격차 v1 — 오너 지적(08-12) 「나레이션 관련 우리꺼 빠진 게 많다」 실측

★v0의 오류를 고친다:
  v0은 288개를 「Suno가 뱉었는가」축으로만 재고 순증 0이라 보고했다. 두 가지가 틀렸다.
  ⑴ 축 오류 — 나레이션 태그는 대부분 **지시형**이라 Suno의 서술 브라켓에 나올 이유가 없다.
     그 축의 ABSENT는 외부 불신의 근거가 아니라 **우리 커버리지 공백의 신호**다.
  ⑵ 추출 오류 — v0 수집기는 `[...]` 정규식이라 **태그를 대괄호 없이 적는 출처**(sunoaiwiki
     81항목: Female narrator / Announcer / Reporter …)를 통째로 못 봤다. 「없음」이 아니라 「안 봄」.

본 스크립트가 답하는 것:
  ⓐ 외부 나레이션 태그 각각이 우리 코퍼스에 있는가 (없으면 = 우리 공백)
  ⓑ 우리가 실제로 가진 나레이션 자산은 무엇인가 (= SP 서술축. encore Q1-a/Q1-c 답변용)
"""
import json
import re
import sqlite3
import sys
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
OUT_DIR = ROOT / "data" / "metatag_external"

BRACKET_SOURCES = ("bracket_entity", "stems_bracket")
SP_SOURCES = ("sp_entity", "stems_sp", "suno_sp_full")

# ─────────────────────────────────────────────────────────────
# 외부 나레이션 태그 원장 — 전부 에이전트가 실제 fetch·raw 추출한 것.
# grade: A_demo = 음원·A/B로 시연됨 / B_recited = 목록에 적혀만 있음
# bracketed=False = 출처가 대괄호 없이 적음(★v0이 놓친 형태)
# ─────────────────────────────────────────────────────────────
NARRATION_TAGS = OrderedDict()


def add(tags, source, grade, bracketed=True, note=""):
    for t in tags:
        e = NARRATION_TAGS.setdefault(t, {"sources": [], "grade": grade,
                                          "bracketed": bracketed, "notes": []})
        e["sources"].append(source)
        if grade == "A_demo":
            e["grade"] = "A_demo"
        if note:
            e["notes"].append(note)


# ── A등급: 실제 시연(음원 공개 또는 영상 A/B) ──
# ★2026-08-13 실물 검증: 아래 유튜브 4출처를 `yt-dlp`로 **처음 실제 회수**하고
#   주장 태그 철자를 기계 대조했다 → **18/18 verbatim 적중**(회수분 = data/metatag_external/yt/verify_v1/).
#   ⇒ 「안 보고 인용했다」는 내 의심은 **기각**됐다.
#   ⚠단 적중한 것은 **철자**이지 **「시연」이 아니다** — 영상 본문은 HTTP 429로 미회수.
#     A_demo의 「A/B 시연」 근거는 아직 **설명란 기재까지**다. 이 한정을 등급 옆에 달고 다닐 것.
add(["[Spoken Word]", "[Spoken Verse]"], "yt_Uy2jV0fqTPk(JP)", "A_demo",
    note="영상이 장르별 A/B 시연. 「指定範囲の歌詞をセリフにする」")
add(["[Spoken]", "[Whispered]", "[Pause]", "[Dramatic Pause]", "[Deep Breath]"],
    "yt_zu7fhHtVAwU(PT)", "A_demo", note="설명란에 전체 나레이션 대본 수록")
add(["[Female spoken, vocaloid, gentle]", "[Monster spoken, raspy, angry]",
     "[Verse 1, Man]", "[laugh]", "[in Latin]"],
    "yt_dxG9qPPpRnI", "A_demo", note="★괄호 안 화자+어조 서술형 — 공개곡 가사 실물")
add(["[AI Automated Voice, talking]", "[Tay Chatbot, talking:]",
     "[Outro, Tay Chatbot:]", "[Deadpan]", "[Tay laughs]",
     "[Old Windows error pings. A dial-up modem scream.]"],
    "yt_sJnkHygvp6g", "A_demo", note="★캐릭터명이 브라켓 안으로 들어간 형태·자유문 SFX 지시")
# ★2026-08-13 강등 — A_demo → 미검증. 자진 신고분.
#   ⑴ suno.com/s/nrhqq4oreDlBEabw 는 **JS 게이트라 내가 못 읽는다**(직접 재확인). 제목만 샌다.
#   ⑵ 그 제목이 "Righteous Report Ep 3" by **Jack Righteous** — 내 「실패양식」 출처와 **동일 인물**인데
#      독립 출처로 셌다. 저자 수렴을 교차확인으로 계상한 것.
#   ⑶ 내가 「음원 공개·실물 가사」라 적은 verbatim의 **원본 캐시가 리포에 없다.**
#   ⇒ 「A_demo」는 내가 확인한 적 없는 등급이다. 등급을 내리는 것이지 표기를 지우는 것이 아니다.
add(["[VOICEOVER — SPOKEN, NOT SUNG]", "[READ NATURALLY • NO RHYMES • NO MELODY]",
     "[BACKGROUND: minimal ambient underscore only]", "[PERFORMANCE RULES]"],
    "suno.com/s/nrhqq4oreDlBEabw", "미검증",
    note="★08-13 A_demo→미검증 강등. JS게이트로 미열람·원본 캐시 없음·동일 저자(Jack Righteous) 중복 계상")

# ── B등급: 목록에 기재(시연 없음) ──
add(["[Narration]", "[Sprechgesang]"], "sunoaiwiki_spokenword", "B_recited")
add(["[Whispering vocals]", "[Screaming vocals]"], "sunoaiwiki_production", "B_recited")
add(["[narrator]", "[announcer]", "[whispers]", "[whispering]", "[whisper]",
     "[laughter]", "[shout]", "[vocalist]", "[vocal-style]", "[personae]",
     "[spoken word]", "[rapped verse]", "[sfx]", "[siren]", "[field-recording]"],
    "gh_stayen", "B_recited", note="파라미터 문법 보유(단 LLM 생성 흔적 있어 '제안'으로 취급)")
add(["[Vocal Style: Whisper]", "[Vocal Style: Monotone]", "[Vocal Style: Shouting]",
     "[Vocal Style: Breathless]", "[Voice: Auto-tune]", "[Vocal Ad-libs]",
     "[Effect: Radio Filter]", "[Persona: Pop Star]"],
    "openmusicprompt", "B_recited")
add(["[Whispered lyrics]"], "howtopromptsuno", "B_recited")
add(["[Spoken Word Narration]", "[Staticky Spoken Pre-Chorus]", "[Telephone Call]",
     "[Swanky Crooning Male]", "[Ethereal Female Whisper]"],
    "gh_daveshap", "B_recited", note="훈련데이터에 등장하는 형태라 주장")
add(["[Man]", "[Woman]", "[Boy]", "[Girl]", "[Telephone Effect]", "[Clears Throat]",
     "[Sighs]", "[Chuckles]", "[Giggles]", "[Groaning]", "[Cough]", "[Whistling]",
     "[Audience laughing]", "[Applause]", "[Cheering]", "[Phone Ringing]",
     "[Static]", "[Record Scratch]", "[Silence]", "[Censored]", "[Screams]"],
    "musci.io", "B_recited")

# ★★v0이 통째로 못 본 형태 — 출처가 대괄호 없이 적는다
add(["Female narrator", "Announcer", "Reporter", "Man", "Woman", "Boy", "Girl",
     "Whispers", "Sighs", "Chuckles", "Giggling", "Screams", "Clears throat",
     "Audience laughing", "Applause", "Censored", "Silence", "Barking",
     "Squawking", "Phone ringing", "Beeping"],
    "sunoaiwiki_metataglist", "B_recited", bracketed=False,
    note="★출처가 대괄호 없이 기재 — v0 정규식이 구조적으로 못 봄")
add(["FEMALE NARRATOR", "WHISPERS", "ANNOUNCER", "AUDIENCE LAUGHING",
     "APPLAUSE", "PHONE RINGING"],
    "brunch_botongmarketer_599(KR)", "B_recited", bracketed=False,
    note="한국어 출처. 대문자 무괄호 표기")

# 화자귀속 문법 — 태그가 아니라 '문법'이라 별도 보관
SPEAKER_SYNTAX = OrderedDict([
    ("괄호내_화자+어조_서술", {
        "form": "[Monster spoken, raspy, angry] / [Female spoken, vocaloid, gentle]",
        "source": "yt_dxG9qPPpRnI (공개곡 가사)",
        "grade": "A_demo",
        "note": "★화자를 명찰이 아니라 '어떻게 들리는가'로 적음 — duet_bracket_grammar_v1 §0과 동형",
    }),
    ("캐릭터명_구조태그_병합", {
        "form": "[Verse 1, Man] / [Outro, Tay Chatbot:] / [Chorus, Man]",
        "source": "yt_dxG9qPPpRnI, yt_sJnkHygvp6g",
        "grade": "A_demo",
        "note": "★구조태그 뒤에 화자를 콤마로 붙임. 우리 4층 문법에 없는 형태",
    }),
    ("콜론_파라미터", {
        "form": "[narrator: voice: female, style: documentary]",
        "source": "gh_stayen",
        "grade": "B_recited",
        "note": "문법이 내부 비일관(voice: 는 콜론, volume= 는 등호)",
    }),
    ("역할_인라인_큐", {
        "form": "[announcer: horror show host, ominous, slow delivery]",
        "source": "gh_stayen",
        "grade": "B_recited",
        "note": "",
    }),
    ("파이프_표기", {
        "form": "[spoken word | intimate, close-mic, almost whispered]",
        "source": "gh_stayen, entrepeneur4lyf",
        "grade": "B_recited",
        "note": "",
    }),
    ("성별_접두_콜론", {
        "form": "[Male: gritty baritone] / [female:]",
        "source": "gh_stayen",
        "grade": "B_recited",
        "note": "",
    }),
    ("규칙블록형_프롬프트", {
        "form": "[VOICEOVER — SPOKEN, NOT SUNG] + [PERFORMANCE RULES] + 불릿 규칙",
        "source": "suno.com/s/nrhqq4oreDlBEabw",
        "grade": "A_demo",
        "note": "★태그 1개가 아니라 '규칙 블록'으로 낭독을 강제한 실물 — 가장 완성된 형태",
    }),
    ("괄호_화자힌트", {
        "form": "(Voice A) / (Voice B)",
        "source": "gh_stayen",
        "grade": "B_recited",
        "note": "★출처 스스로 '약한 힌트(soft hint)'라 명시",
    }),
])

# 외부가 밝힌 실패 양식 — 우리 데드존 3계층에 붙일 후보
FAILURE_MODES = {
    "브라켓이_노래로_불림": {
        "source": "jackrighteous",
        "quote": "The label is sung aloud → 원인: cue가 너무 장황/서정적 → 조치: 브라켓을 짧게",
        "note": "★긴 나레이션 태그([announcer: horror show host, ominous, slow delivery])의 실제 실패 양식",
    },
    "충돌태그_적층": {
        "source": "gh_stayen",
        "quote": "[whisper] + [shouted vocals]를 같은 줄에 쌓지 말 것. 구간당 주 전달방식 1개",
        "note": "",
    },
    "페르소나_활성시_무시": {
        "source": "gh_stayen",
        "quote": "Persona 선택 시 [Male Vocal]/[Female Vocal]은 중복이거나 무시될 수 있음",
        "note": "musci는 무조건 유효하다고 적어 정면 충돌",
    },
}

NORM_RE = re.compile(r"[\s\-_]+")


def norm(s):
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    s = s.lower().strip()
    s = NORM_RE.sub(" ", s)
    return s.strip(" .,!?:•—")


def main():
    if not DB.exists():
        sys.exit(f"코퍼스 없음: {DB}")
    con = sqlite3.connect(DB)
    q = ("SELECT DISTINCT sentence, song_id FROM entries "
         "WHERE source IN (%s) AND sentence IS NOT NULL")
    brackets = list(con.execute(q % ",".join("?" * len(BRACKET_SOURCES)), BRACKET_SOURCES))
    sps = list(con.execute(q % ",".join("?" * len(SP_SOURCES)), SP_SOURCES))

    exact = {}
    for text, sid in brackets:
        e = exact.setdefault(norm(text), {"raw": set(), "songs": set()})
        e["raw"].add(text)
        e["songs"].add(sid)
    bracket_pairs = [(norm(t), sid) for t, sid in brackets]
    sp_pairs = [(norm(t), sid) for t, sid in sps]

    # 검산 (v0과 동일 — 실패 시 중단)
    for probe_t, want in (("[Intro]", True), ("[zzqqxx nope]", False)):
        hit = norm(probe_t) in exact
        if hit != want:
            sys.exit(f"검산 실패: {probe_t} → {hit}. 판정 중단")
    print("검산 통과 (양성 [Intro] 적중 / 음성 무의미문자열 0)")

    results = {}
    for tag, meta in NARRATION_TAGS.items():
        n = norm(tag)
        pat = re.compile(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])")
        hit = exact.get(n)
        c_songs = {sid for t, sid in bracket_pairs if t != n and pat.search(t)}
        s_songs = {sid for t, sid in sp_pairs if pat.search(t)}
        if hit:
            verdict = "OURS_BRACKET"
        elif c_songs:
            verdict = "OURS_BRACKET_PARTIAL"
        elif s_songs:
            verdict = "OURS_SP_ONLY"
        else:
            verdict = "★GAP"
        results[tag] = {
            **meta,
            "verdict": verdict,
            "bracket_songs": len(hit["songs"]) if hit else 0,
            "bracket_partial_songs": len(c_songs),
            "sp_songs": len(s_songs),
        }

    c = Counter(r["verdict"] for r in results.values())
    print("\n나레이션 태그 {}개 대조".format(len(results)))
    for k in ("OURS_BRACKET", "OURS_BRACKET_PARTIAL", "OURS_SP_ONLY", "★GAP"):
        print(f"  {k:22s} {c.get(k, 0):4d}")

    grades = Counter(r["grade"] for r in results.values())
    print("\n등급 분포 (★08-13 강등 반영)")
    for k, v in grades.most_common():
        print(f"  {k:22s} {v:4d}")

    gaps_demo = [t for t, r in results.items() if r["verdict"] == "★GAP" and r["grade"] == "A_demo"]
    gaps_unver = [t for t, r in results.items() if r["verdict"] == "★GAP" and r["grade"] == "미검증"]
    # ★한정자를 건수 옆에 붙인다 — 이 줄만 떼어 인용돼도 등급이 따라가도록(08-11·06-15 실피해 2회).
    print(f"\n★'외부 출처에 철자 확인 + 우리엔 전무' = {len(gaps_demo)}건"
          f"  ※철자는 실물 대조(18/18), 「A/B 시연」 자체는 미확인(영상 본문 429)")
    for t in gaps_demo:
        print(f"    {t}")
    print(f"\n★미검증으로 강등 = {len(gaps_unver)}건  ※JS게이트 미열람·동일 저자 중복 계상(08-13 자진)")
    for t in gaps_unver:
        print(f"    {t}")

    # ── 우리가 실제로 가진 자산 = SP 서술축 (encore Q1-a/Q1-c 답변용) ──
    narr_pat = re.compile(
        r"(?i)spoken[- ]word|conversational|storytelling|narrat|whisper|recit|monolog|declaim")
    asset = Counter()
    for text, sid in sps:
        for m in narr_pat.finditer(text):
            frag = text[max(0, m.start() - 45):m.end() + 45]
            asset[frag.strip()] += 1
    print(f"\n우리 SP 서술축 나레이션 자산 = {len(asset)}개 표현 (상위 8)")
    for frag, n in asset.most_common(8):
        print(f"  {n:3d}  …{frag}…")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "narration_metatag_gap_v1.json"
    out.write_text(json.dumps({
        "generated_by": "scripts/metatag_narration_gap_v1.py",
        "context": "오너 지적(08-12) — v0의 '순증 0'은 축 오류 + 대괄호 정규식 추출 오류의 산물",
        "axis_note": "★GAP = 우리 코퍼스에 없다. Suno가 안 뱉는다는 뜻이며, 지시형 태그의 경우 "
                     "'입력하면 반응하는가'는 여전히 미검증. 단 나레이션 족은 우리 재고가 "
                     "브라켓 2종뿐이라 GAP=우리 공백으로 읽는 것이 맞다.",
        "counts": dict(c),
        "tags": results,
        "speaker_syntax": SPEAKER_SYNTAX,
        "failure_modes": FAILURE_MODES,
        "our_sp_assets_top50": asset.most_common(50),
    }, ensure_ascii=False, indent=2))
    print(f"\n저장: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
