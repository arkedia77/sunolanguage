#!/usr/bin/env python3
"""build_directive_register_v1.py — ★지시축 대장 v1 신설.

왜 필요한가(2026-08-22):
  후보 선반(`candidate_shelf_v1.json` 236행)은 **표기** 대장이다. 「이런 표기가 외부에 있다」를 담는다.
  그런데 외부에는 **행동 주장**이 따로 있다 — 「짧게 써라」「인트로에선 안 먹는다」「이건 placebo다」.
  이건 표기가 아니라 **지시의 효과에 대한 주장**이고, 선반에도 4레인 집계에도 **들어갈 자리가 없어서**
  `metatag_lane_recount_v1`이 `failure_modes`·`advice`·`precedence_statements`·`rule_block_prompting`을
  **「안 센 것」으로 제외**했다. ⇒ 이미 수집돼 있는데 **대장이 없어 안 세어진 64건**이 있었다.
  ★08-12에 「관측축만 쌓고 지시축을 안 쌓았다」고 진단했는데, 그 공백이 **자료 구조에도 그대로** 있었다.

★단위 = 주장 1건(표기 아님). ★출력이 아니라 **입력의 효과**에 대한 남의 말이다.

등급:
  A_demo    출처가 자기 생성물을 틀어 보임이 원문으로 확인
  B_recited 주장만 있고 시연 없음
  ★수치·준수율은 시연이 있어도 N·측정법 미기재면 B.

검증가능성(★이 대장의 존재 이유):
  already_measured   우리가 이미 잰 자리가 있다 → 지금 대조 가능
  corpus_now         우리 코퍼스(출력층)로 지금 잴 수 있다 — ★단 「Suno가 뱉나」이지 「입력이 먹히나」가 아니다
  impossible_by_design 우리 코퍼스는 출력만 담아 **원리상 못 잰다**(준수율·무시·실패율)
  needs_generation   생성이 필요 → B-2 「설계까지만」에 걸려 있다

사용: .venv/bin/python scripts/build_directive_register_v1.py
산출: data/metatag_external/directive_register_v1.json
"""
import json, re, sqlite3, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANES = ROOT / "data/metatag_external/v2_lanes"
HARVEST = ROOT / "data/metatag_external/reopen_harvest_v1.json"
OUT = ROOT / "data/metatag_external/directive_register_v1.json"

# ★필드명만 보고 넣지 않는다 — 2026-08-22 1차판에서 두 필드를 잘못 넣었다.
#   `target_attempts` = **회수 로그**(「403이었다」)이지 지시의 효과에 대한 주장이 아니다 → reopen 쪽 소관.
#   `instances`       = **실물 SP 예문**이지 주장이 아니다 → 표기·예문 자산.
#   둘을 넣으면 「지시축 주장 71건」이 부풀고, 그중 10건은 주장이 아닌 것이 된다.
FIELD_MAP = {"failure_modes": "실패양식", "advice": "조언", "precedence_statements": "우선순위",
             "rule_block_prompting": "규칙블록"}
EXCLUDED_FIELDS = {"target_attempts": "회수 로그 — 지시의 효과 주장 아님(reopen_v1 소관)",
                   "instances": "실물 SP 예문 — 주장 아님(표기·예문 자산)",
                   "tags": "표기 — 후보 선반 소관", "speaker_syntax": "표기 — 후보 선반 소관",
                   "not_accessed": "미회수 목록 — reopen_v1 소관", "notes": "수집자 메모"}

# ── 축 분류: 키워드 보조 + 자동 표시 ─────────────────────────────────────
# ★한국어 주장(B-4 자막 회수분)이 영어 정규식에 안 걸려 1차판에서 6건이 통째로 「미분류」였다. 병기한다.
AXES = [
    ("우선순위·필드충돌", r"conflict|override|overrule|precedence|both fields|competing|exclude|contradic"
                    r"|repeat.{0,30}(instruction|styles)|not neutral|stronger|보완|부작용|결합"),
    ("형태효과(길이·형식)", r"short|long|1-3 words|verbose|sentence|tokenizer|stuff|concise"
                     r"|bracket.{0,20}(length|noise)|guidance, not command|labels as guidance"),
    ("준수율·무시", r"tier|complian|ignore[sd]?|honou?red|placebo|reliab|%|guarant|성공률|보장|급락"),
    ("위치효과", r"before|placement|mid-line|own line|opening line|top|intro|인트로|배치|앞 30초"),
    ("실패양식", r"sung as|sung aloud|collapse|smear|rushed|random|swap|실패|노래처럼|단절"),
    ("범위(스타일↔가사)", r"style field|styles box|entire song|only that section|scope|전곡|스타일에"),
    ("표기법(괄호·대문자)", r"parenthes|all caps|capital|quotation|quotes|bracket.{0,10}are"),
    ("기능차이·장르의존", r"장르 의존|chillwave|bossa nova|death metal|음악을 무시|음악에 맞춰"),
    ("교습출처_부재", r"NO source that teaches|idiosyncratic|does not publish|no official|못 찾았"),
]


def axis_of(text: str):
    hits = [name for name, pat in AXES if re.search(pat, text, re.I)]
    return hits or ["미분류"]


# ── 검증가능성 규칙 ────────────────────────────────────────────────────
def norm_grade(g: str):
    """★등급 문자열이 출처마다 달라 집계가 깨졌다(1차판 5종). A_demo/B_recited 둘로 정규화하고
    수치 주장 여부는 따로 깃발로 든다 — 시연이 있어도 N·측정법 없는 수치는 B다."""
    g = (g or "").strip()
    return "A_demo" if g.startswith("A_demo") else "B_recited"


NUMERIC = re.compile(r"\d+\s*%|\bTier\s*\d|성공률|약 \d+")


def testability(text: str):
    t = text.lower()
    if re.search(r"placebo|ignore[sd]? (them|it) completely|colon", t):
        return "corpus_now", "형식이 Suno 출력층에 존재하는지는 지금 잴 수 있다(단 존재≠입력준수)"
    if re.search(r"tier|complian|%|reliab|guarant|honou?red|skipped entirely", t):
        return "impossible_by_design", "준수율·무시 축 — 우리 코퍼스는 Suno가 뱉은 것만 담아 원리상 못 잰다"
    if re.search(r"parenthes|\(whisper|sung as the word", t):
        return "already_measured", "우리 `(spoken)` 실측이 있다(LEO 실청취 4/4 · 기계 판정가능 2 중 1 견고)"
    if re.search(r"sung as|sung aloud|bracket.{0,20}sung", t):
        return "already_measured", "우리 VD 실측 「브라켓 텍스트 가창 누출 0/2」와 같은 축"
    return "needs_generation", "생성 필요 — B-2 「설계까지만」에 걸림"


def load_lane_claims():
    out = []
    for f in sorted(LANES.glob("*.json")):
        d = json.loads(f.read_text())
        lane = f.stem
        for k, ko in FIELD_MAP.items():
            for it in d.get(k, []):
                txt = (it.get("claim") or it.get("claim_verbatim") or it.get("statement")
                       or it.get("observation") or it.get("reason")
                       or it.get("style_prompt_verbatim") or "")
                if not txt:
                    continue
                url = it.get("source_url", "") or it.get("target", "")
                host = url.split("/")[2] if url.startswith("http") else url
                ax, why = testability(txt)
                out.append({
                    "주장": txt, "레인": lane, "필드": ko,
                    "grade": norm_grade(it.get("grade", "B_recited")),
                    "★수치주장": bool(NUMERIC.search(txt)),
                    "출처url": url, "출처host": host,
                    "출처label": it.get("source_label", ""),
                    "축": axis_of(txt), "★축_판정": "자동(키워드) — 사람 검토분은 아래 curated_conflicts",
                    "★검증가능성": ax, "★검증가능성_근거": why,
                })
    return out


def load_video_claims():
    if not HARVEST.exists():
        return []
    h = json.loads(HARVEST.read_text())
    c = h.get("지시축_주장", {})
    out = []
    for it in c.get("주장", []):
        txt = it["주장"]
        ax, why = testability(txt)
        out.append({
            "주장": txt, "레인": "reopen_v1(B-4 자막)", "필드": "시연영상",
            "grade": norm_grade(it.get("등급", "")),
            "★수치주장": bool(NUMERIC.search(txt)),
            "출처url": "https://www.youtube.com/watch?v=Uy2jV0fqTPk",
            "출처host": "www.youtube.com",
            "출처label": "SunoAI Lab Notes — [Spoken Word]と[Spoken Verse]",
            "축": axis_of(txt), "★축_판정": "자동(키워드)",
            "★검증가능성": ax, "★검증가능성_근거": why,
            "★우리축": it.get("★우리축", ""),
        })
    return out


# ── ★사람이 읽고 세운 모순 목록 (자동 아님) ─────────────────────────────
CURATED = {
    "★왜_따로_적나": "아래는 키워드가 아니라 **내가 64건을 읽고** 세운 것이다. 자동 분류로는 안 나온다.",
    "외부↔우리_충돌": [
        {"id": "X1", "★중요도": "최상",
         "우리_주장": "「맨 명찰(`[spoken]`)은 죽고 **화자+어조 서술 브라켓**(`[Monster spoken, raspy, angry]`)은 공개 음원 시연이 존재한다」 — 08-12 최대 발견. 우리 `duet_bracket_grammar_v1` §0(화자는 명찰 아닌 음원 서술로 전달)과 같은 원리.",
         "외부_주장": "「브라켓은 1~3단어로 짧게. 긴 브라켓 문장은 토크나이저가 노이즈로 압축한다」(hookgenius) / 「문장형 어투를 빼고 짧은 큐 하나를 사건 직전에」(tagasong) / 「태그를 헤더로 쓰고 가사는 아래에 — 브라켓 안에 문장을 넣으면 명령문이 불린다」(tagasong)",
         "★판정": "**정면 반대 방향**이다. 우리는 「서술을 얹으면 강해진다」, 외부는 「길면 죽는다」.",
         "★이미_설계돼_있다": "우리 `docs/field_attribution_2x2_preregistration.md`의 브라켓 축이 **없음/짧은태그/긴규칙문 3수준**이다 — 이 충돌을 재게 이미 설계돼 있다.",
         "검증가능성": "needs_generation (B-2)",
         "★주의": "두 주장이 같은 것을 안 재고 있을 수 있다 — 우리 근거는 **공개 음원 실물 존재**(존재 증명)이고 외부는 **평균 성공률**(빈도 주장)이다. 존재와 빈도는 양립한다. ⇒ 「충돌」로 확정하기 전에 축부터 맞출 것."},
        {"id": "X2", "★중요도": "상",
         "우리_관측": "오늘(08-22) miraheze에서 회수한 `Vocal Style: soulful`·`Vocal Emotion: energetic`·`Vocalist: Female` 등 **key:value 브라켓** 가족이 우리 **출력층 0**.",
         "외부_주장": "「`[Reverb: 30%]`·`[Bass: 80%]` 류 콜론+숫자 파라미터 태그는 **placebo**다. Suno는 완전히 무시한다. 문법이 공식처럼 보여서(대괄호·콜론·숫자) 처음 지어낸 가이드가 다음 가이드로 복제됐을 뿐」(hookgenius)",
         "우리_독립근거": "`duet_bracket_grammar_v1`이 **다른 방법(GLOB)**으로 `[Male Vocal]` exact **0곡** — 명찰형이 안 산다.",
         "★판정": "★**3경로가 같은 방향(음성)으로 수렴**한다: ⑴우리 출력층 0 ⑵우리 듀엣문법 명찰형 0곡 ⑶외부의 명시적 placebo 주장. **그래도 생성 없이는 미검증**이고, 부재는 여전히 「우리가 못 봤다」다.",
         "검증가능성": "corpus_now(형식 존재 여부) + needs_generation(입력 준수)"},
        {"id": "X3", "★중요도": "상",
         "외부_충돌": "songsmith「소괄호는 **항상 불린다**. `(whispered)`는 '휘스퍼드'라는 **단어로 불린다**」 ↔ sunoaiwiki「소괄호를 spoken 전달에 쓰라」 — **외부끼리 정면 모순**.",
         "★우리_자산": "우리는 이 자리에 **실측이 있다** — `(spoken)` LEO 실청취 **4/4** + 기계는 **판정 가능 2클립 중 1클립만 견고**.",
         "★판정": "★**64건 중 우리가 지금 판정에 기여할 수 있는 거의 유일한 자리**다. 우리 실측은 songsmith의 「항상 불린다」를 **약화**시킨다(적어도 우리 4클립에선 안 불렸다). 단 **N=4·우리 편성**이라 일반화 못 한다.",
         "검증가능성": "already_measured(부분)"},
    ],
    "외부↔외부_충돌": [
        {"id": "C1", "쟁점": "소괄호가 불리는가", "A": "songsmith: 항상 불린다", "B": "sunoaiwiki: spoken에 쓰라", "비고": "X3와 같은 쟁점"},
        {"id": "C2", "쟁점": "긴 브라켓/규칙블록이 되는가",
         "A": "hookgenius·tagasong: 짧게(1-3단어), 문장형 금지",
         "B": "공개곡 실물에 `[VOICEOVER — SPOKEN, NOT SUNG]`+`[PERFORMANCE RULES]` 블록형이 존재(우리 08-12 수집)",
         "★비고": "★수집자 자신이 적어 둔 음성 소견이 있다 — 「이 레인에서 닿은 **모든 가이드 중 이 패턴을 가르치거나 시연하는 출처를 하나도 못 찾았다**. 곡 저자 개인 습관으로 보인다」. ⇒ **실물은 있는데 교습 출처가 0**."},
        {"id": "C3", "쟁점": "`[Intro]` 준수율", "A": "hookgenius: notoriously skipped entirely / titanxt: less reliable",
         "★우리_대조": "우리 **출력층** `Intro` 770히트/581곡(브라켓 711). ★단 이건 **Suno가 뱉은 라벨**이지 **우리가 넣은 `[Intro]`를 지켰나**가 아니다 — **다른 축이라 반박이 아니다.**"},
    ],
    "★독립_수렴(양성)": [
        {"쟁점": "`[Spoken Word]`는 잘 먹힌다",
         "출처A": "hookgenius — 「Tier 1, Suno에서 가장 깨끗하게 준수되는 태그 중 하나」(자칭 400+ 생성 시험)",
         "출처B": "youtube Uy2jV0fqTPk — 「성공률 약 80%」(A_demo 시연 있음)",
         "★비고": "독립 2출처가 같은 방향. 둘 다 N·측정법 미기재라 **수치는 B_recited**이나, **방향은 두 번 나왔다.**"},
    ],
}


def main():
    claims = load_lane_claims() + load_video_claims()
    for i, c in enumerate(claims, 1):
        c["id"] = f"D{i:03d}"

    host = collections.Counter(c["출처host"] for c in claims)
    top_host, top_n = host.most_common(1)[0]
    ax = collections.Counter(a for c in claims for a in c["축"])
    test = collections.Counter(c["★검증가능성"] for c in claims)
    grade = collections.Counter(c["grade"] for c in claims)
    numeric = sum(1 for c in claims if c.get("★수치주장"))

    out = {
        "무엇": "지시축 대장 v1 — 「지시의 효과」에 대한 외부 주장 대장(표기 대장 아님)",
        "재현": ".venv/bin/python scripts/build_directive_register_v1.py",
        "원자료": ["data/metatag_external/v2_lanes/*.json (failure_modes·advice·precedence_statements·rule_block_prompting·target_attempts·instances)",
                "data/metatag_external/reopen_harvest_v1.json (B-4 자막 회수분)"],
        "★왜_지금_생겼나": ("이 64건은 **새로 모은 게 아니라 이미 수집돼 있던 것**이다. 담을 대장이 없어서 "
                      "`metatag_lane_recount_v1`이 「안 센 것」으로 제외했고, 그래서 **집계에도 인용에도 한 번도 안 나왔다.** "
                      "★08-12에 「관측축만 쌓고 지시축을 안 쌓았다」고 진단했는데 그 공백이 자료 구조에도 그대로 있었다."),
        "★단위": "주장 1건. 표기가 아니라 **입력의 효과에 대한 남의 말**이다.",
        "★대장에서_뺀_필드": {**EXCLUDED_FIELDS,
            "★경위": "1차판에서 `target_attempts`·`instances`를 넣어 71건으로 셌다. 그중 10건은 주장이 아니었다 "
                   "— 회수 로그와 SP 예문이다. **필드명만 보고 넣은 내 오류**이고, 「지시축 주장 N건」을 부풀렸다."},
        "집계": {
            "총_주장": len(claims),
            "등급": dict(grade),
            "★수치_주장": {"수": numeric,
                       "★주": "수치는 시연이 있어도 N·측정법 미기재면 B_recited다. 인용 시 반드시 출처 자기신고임을 병기할 것."},
            "축": dict(ax.most_common()),
            "★검증가능성": dict(test),
            "출처_호스트": dict(host.most_common()),
        },
        "★★단일저자_집중": {
            "최다": top_host, "건수": top_n, "비율": f"{top_n/len(claims)*100:.0f}%",
            "★뜻": ("이 대장의 절반이 **한 저자**에게서 나온다. 출처 수가 늘어도 **독립 확인은 안 늘어난다.** "
                  "선반의 `derivative_cluster` 경고와 같은 문제이고, 여기서는 더 심하다 — "
                  "★**「여러 가이드가 그렇게 말한다」를 근거로 쓰지 말 것.**"),
        },
        "★이_대장이_못_하는_것": [
            "★어느 주장도 우리가 검증하지 않았다. 전부 **남의 말**이다.",
            f"준수율·무시 축 {test.get('impossible_by_design',0)}건은 우리 코퍼스로 **원리상 못 잰다** — 출력만 담기 때문.",
            f"{test.get('needs_generation',0)}건은 생성이 필요하고 **B-2 「설계까지만」**에 걸려 있다. 내가 안 연다.",
            "축 분류는 키워드 자동이다(`★축_판정` 참조). 사람이 읽고 세운 것은 `curated_conflicts`뿐이다.",
        ],
        "curated_conflicts": CURATED,
        "주장": claims,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {OUT}")
    print(f"총 주장 {len(claims)} / 등급 {dict(grade)} / 수치주장 {numeric}")
    print(f"검증가능성 {dict(test)}")
    print(f"★단일저자 집중 {top_host} {top_n}건 ({top_n/len(claims)*100:.0f}%)")
    print(f"축 {dict(ax.most_common())}")


if __name__ == "__main__":
    main()
