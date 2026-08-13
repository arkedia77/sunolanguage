# 나레이션 메타태그 격차 v1 — 오너 지적 실측

**작성**: sunolanguage · 2026-08-12
**계기**: ★오너 지적 — 「어제 유투브 통해서 보니, **나레이션 관련한 메타태그부터 우리꺼 빠진 게 많이 생겼어**」
**산출**: `data/metatag_external/narration_metatag_gap_v1.json` · 재현=`scripts/metatag_narration_gap_v1.py`
**상위 문서 정정 대상**: `docs/metatag_external_survey_v0.md` §0·§2의 「순증 0」

---

## 0. 한 줄

**오너 지적이 맞다. v0의 「외부 순증 0」은 틀렸다.**
나레이션 태그 **103개 중 85개가 우리에 없다**.
~~그중 19개는 외부에서 음원까지 공개된 시연분이다.~~ → ★**08-13 정정: 15개이고, 「음원 공개 시연」이 아니라 「외부 출처에 철자가 실재함을 내가 실물 대조한 것」까지다**(§2 정정 박스). 4건은 **미검증 강등**.

---

## 1. ★v0이 왜 못 봤나 — 원인 2개, 둘 다 내 방법 문제

### ⑴ 축 오류 — 못 보는 자로 재고 「없다」고 했다
v0은 288개를 **「Suno가 그 표기를 뱉었는가」** 축으로만 쟀다.
나레이션 태그는 대부분 **지시형**이라 Suno의 *서술* 브라켓에 나올 이유가 없다.
v0 §5에 「(b) 지시형은 판정 불가」라고 **내가 직접 써놓고도**, 그 ABSENT를
**「외부 출처가 부실하다」**로 읽었다. 올바른 독법은 정반대다 —
**우리 재고가 비어 있다는 신호**였다.

근거: 우리 나레이션 **브라켓 재고 = 2종, 각 1곡**(`spoken-word delivery`, `whispered vocals`). 사실상 공백.

### ⑵ 추출 오류 — 정규식이 대괄호를 요구했다
v0 수집기는 `\[...\]` 기반이었다. 그래서 **태그를 대괄호 없이 적는 출처가 통째로 안 보였다**:

| 출처 | 형태 | 놓친 것 |
|---|---|---|
| sunoaiwiki 메타태그 목록 | 무괄호 정의쌍 **81항목** | `Female narrator` · `Announcer` · `Reporter` · `Clears throat` · `Sighs` … |
| brunch(한국어) | 무괄호 **대문자** | `FEMALE NARRATOR:` · `WHISPERS:` · `ANNOUNCER:` |

★v0이 「브라켓 0건」이라 적은 sunoaiwiki가 **나레이션 밀도가 가장 높은 출처**였다.
`Female narrator`·`Reporter`는 **이 출처에만 있다**. 「없음」이 아니라 **「안 봄」**이었다.

---

## 2. 실측 — 나레이션 태그 103개

| 판정 | 건수 |
|---|---|
| OURS_BRACKET (우리 브라켓에 있음) | 3 |
| OURS_BRACKET_PARTIAL | 11 |
| OURS_SP_ONLY (서술축에만) | 4 |
| **★GAP (우리에 전무)** | **85** |

### ★그중 「외부 출처에 철자 확인 + 우리엔 전무」 = ~~19건~~ **15건** (★08-13 정정)

> ★★**정정 2건 (2026-08-13 자진)** — 이 절의 「19건」은 틀렸다.
>
> **⒜ A등급 4건 → `미검증` 강등.** 아래 A항의 출처 `suno.com/s/nrhqq4oreDlBEabw`는 **JS 게이트라 내가 못 읽는다**(직접 재확인). 제목만 새는데 그게 *"Righteous Report Ep 3" by **Jack Righteous*** — **내 「실패양식」 출처와 동일 인물인데 독립 출처로 셌다.** 「음원 공개·실물 가사」라 적은 verbatim의 **원본 캐시가 리포에 없다.** ⇒ **A_demo는 내가 확인한 적 없는 등급이다.**
>
> **⒝ 나머지 15건은 오늘 실물 검증했다.** B·C·D항의 유튜브 4출처를 `yt-dlp`로 **처음 실제 회수**(`data/metatag_external/yt/verify_v1/`)하고 태그 철자를 기계 대조 → **18/18 verbatim 적중.** 「안 보고 인용했다」는 내 의심은 **기각**됐다.
> ⚠**단 적중한 것은 「철자」이지 「시연」이 아니다** — 영상 본문은 HTTP 429로 미회수. **A_demo의 「A/B 시연」 근거는 아직 설명란 기재까지다.**
>
> 재현: `scripts/metatag_narration_gap_v1.py` → 등급 분포 `B_recited 81 / A_demo 18 / 미검증 4`.

**A. ~~공개 음원 실물~~ → ★미검증** (`suno.com/s/nrhqq4oreDlBEabw`, Suno v5 — 규칙블록형)
`[VOICEOVER — SPOKEN, NOT SUNG]` · `[READ NATURALLY • NO RHYMES • NO MELODY]` · `[BACKGROUND: minimal ambient underscore only]` · `[PERFORMANCE RULES]`
→ style 필드라고 내가 적었던 것: `"Make deep Spoken word voiceover, conversational narration, clear speech, no melody, no singing…"`
★**이 4건은 아래 15건 집계에서 빠진다.** 표기를 지우지는 않는다 — **등급만 내린다**(나중에 열리면 복원 가능하도록).

**B. 공개곡 가사 — 화자+어조를 브라켓 안에 서술**
`[Female spoken, vocaloid, gentle]` · `[Monster spoken, raspy, angry]` · `[Verse 1, Man]` · `[laugh]` · `[in Latin]`

**C. 스킷 — 캐릭터명이 브라켓 안으로**
`[AI Automated Voice, talking]` · `[Tay Chatbot, talking:]` · `[Outro, Tay Chatbot:]` · `[Deadpan]` · `[Tay laughs]` · `[Old Windows error pings. A dial-up modem scream.]`(자유문 SFX 지시)

**D. 영상 A/B 시연** `[Spoken Verse]` · `[Pause]` · `[Dramatic Pause]` · `[Deep Breath]`

---

## 3. ★가장 중요한 발견 — 「브라켓 채널 dead」 판정이 너무 넓었다

08-11 encore 회신에서 나는 3채널로 답했다: SP 산문 ✅ / `()` 괄호 ✅ / **`[]` 브라켓 ❌ 쓰지 마십시오**.
근거는 `[spoken]`·`[whispered vocals]` 브라켓 1건씩 = dead.

**이번 자료가 그 판정을 좁힌다.** 죽는 것은 **맨 명찰**이고,
**화자+어조를 서술한 브라켓**은 공개 음원 시연 사례가 있다:

| 죽음 | 삶(외부 시연) |
|---|---|
| `[spoken]` `[Male Vocal]` — 맨 명찰 | `[Monster spoken, raspy, angry]` `[Female spoken, vocaloid, gentle]` |

★이것은 **우리 `duet_bracket_grammar_v1.md` §0과 정확히 같은 원리**다 —
「Suno에게 화자는 **명찰(누가)이 아니라 음원 서술(무엇이 들리는가)**로만 전달된다」.
우리는 그 원리를 **찾아놓고 브라켓 채널에는 적용하지 않았다**. 채널 전체를 dead로 접었다.

**미검증이다**(우리가 재현한 것 아님). 그러나 **우리 자체 문법이 예측하는 방향과 일치**하므로 파일럿 1순위다.

---

## 4. 우리가 실제로 가진 것 — 격차에는 모양이 있다

| 축 | 우리 재고 |
|---|---|
| **SP 산문 서술** | ★**158개 표현**(`spoken-word` `conversational` `storytelling` `narrative`…) — **풍부** |
| **브라켓 지시** | **2종 각 1곡** — **공백** |

우리는 **「Suno가 낭독조를 어떻게 묘사하는가」는 잘 알고, 「낭독을 어떻게 시키는가」는 거의 모른다.**
관측축만 쌓고 지시축을 안 쌓은 결과다. 외부는 정확히 그 반대를 갖고 있었다.

---

## 5. 화자귀속 문법 8종 — 우리 4층 문법에 없는 형태 포함

| 문법 | 형태 | 등급 |
|---|---|---|
| ★괄호내 화자+어조 서술 | `[Monster spoken, raspy, angry]` | **A 시연** |
| ★캐릭터명·구조태그 병합 | `[Verse 1, Man]` `[Outro, Tay Chatbot:]` | **A 시연** |
| ★규칙블록형 | `[VOICEOVER…]` + `[PERFORMANCE RULES]` + 불릿 | **A 시연** |
| 콜론 파라미터 | `[narrator: voice: female, style: documentary]` | B(문법 내부 비일관) |
| 역할 인라인 큐 | `[announcer: horror show host, ominous, slow delivery]` | B |
| 파이프 표기 | `[spoken word \| intimate, close-mic]` | B |
| 성별 접두 콜론 | `[Male: gritty baritone]` | B |
| 괄호 화자힌트 | `(Voice A)` / `(Voice B)` | B(출처 스스로 「약한 힌트」) |

★**캐릭터명 병합형은 우리 정본에 없다.** CM-2026-0001 부녀 듀엣 화자분리에 직접 관련.

---

## 6. 외부가 준 실패 양식 — 우리 데드존 3계층에 붙일 후보

| 양식 | 출처 | 내용 |
|---|---|---|
| ★**브라켓이 노래로 불림** | jackrighteous | 「cue가 너무 장황하면 라벨이 그대로 불린다 → 브라켓을 짧게」 |
| 충돌태그 적층 | gh_stayen | `[whisper]`+`[shouted vocals]` 같은 줄 금지, 구간당 1개 |
| 페르소나 활성 시 무시 | gh_stayen | Persona 선택 시 `[Male Vocal]`은 중복·무시 가능 |

★첫 항목은 **우리가 이미 재는 축**이다 — VD 3곡 실측의 「브라켓 텍스트 가창 누출 **0/2**」가 같은 지표.
즉 외부의 실패 양식과 우리 측정축이 **맞물린다**. 파일럿 설계가 쉬운 자리.

---

## 7. 여전히 못 본 것

- **유튜브 자막 = 전량 0건.** 캡션 트랙 **존재는 확인**(`Uy2jV0fqTPk` 9개 언어 등)했으나 서명 URL이 IP 바인딩이라 0바이트 반환. 구술 태그목록은 **미독 상태 유지**.
- **Reddit 전면 403** (v0과 동일).
- `suno.wiki/faq/metatags/voice-tags/` 403 — 검색 스니펫은 `[Female Narrator]`를 이 페이지에 귀속시키나 **못 읽었으므로 출처로 안 씀**.
- `sunometatagcreator.com`(1000+ 주장)·`openmusicprompt`(500+ 주장) 미회수. ★단 stayen이 1,170→실제 184로 **6배 부풀려졌던 전례**가 있어 「1000+」는 산문 예시 인플레로 추정.

---

## 8. 방법 교훈 (승격 후보)

1. ★**「표기 형태」를 가정한 추출기는 그 형태를 안 쓰는 출처를 「없음」으로 만든다.** 대괄호 정규식 하나로 최고밀도 출처를 잃었다. → 수집기는 **형태 불문 후보 추출 + 사후 정규화**로.
2. ★**「A로 재서 안 나왔다」를 「B가 부실하다」로 옮겨 적지 말 것.** v0 §5에 한계를 적어놓고 §0 헤드라인에서 그 한계를 무시했다 — **한계를 각주에만 적는 3회차 형태**(08-04 kee 지적과 동형).
3. 시연(음원 공개) 출처와 암송 출처를 **등급으로 분리**하니 신호가 살았다. 19건의 A등급 격차는 등급 없이는 안 보였다.

---

## 9. 다음 (판단은 오너)

1. ★**encore 회신 정정 필요 여부** — 08-11에 「`[]` 브라켓 쓰지 마십시오」로 나갔다. §3이 그 판정을 좁힌다. CM-2026-0001은 **나레이션 구간이 요건 ⑶**이라 설계에 직접 영향. **재촉 아닌 정정**이므로 발신 가부 판단 요청.
2. **서술형 브라켓 파일럿** — `[spoken]`(맨 명찰) vs `[Male spoken, low register, intimate]`(서술형) 미니멀페어. 우리 자체 문법이 방향을 예측하므로 검정력 있음.
3. **지시축 재고 구축** — 85개 GAP을 후보 풀로. 단 **입력 반응은 한 건도 검증 안 됨**.
