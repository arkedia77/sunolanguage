# antisuno · 이식성 규칙 v0 — 무엇이 엔진 중립 정본인가

> Phase 1 산출물 ③. 2026-08-31 · sunolanguage
> 근거: `docs/antisuno/control_surface_register_v0.md`(엔진 36종·E급) + leomusic3 08-29 이식 실측(M4)
> 기계판 = `data/antisuno/portability_rules_v0.json`

---

## §0. 이 문서가 답하는 것

leomusic3 `pipeline/stage_6b_brackets/runner.py` 독스트링에 이렇게 적혀 있었다:

> 「엔진 중립 정본은 `song_form`·`style_prompt`」

★**적어 두기만 하고 잰 적이 없었다.** 08-29에 처음 쟀고, **절반만 맞았다.**

---

## §1. 이식성 등급 `T0~T4`

| 등급 | 뜻 | 우리 자산 |
|---|---|---|
| **T0 중립** | 그대로 옮겨도 뜻이 보존된다 | `song_form`(섹션 순서·역할) · **가사 본문 텍스트** · 정서·서사 설계 · 장르/무드 개념 |
| **T1 변환 필요** | 뜻은 옮겨지나 **그릇이 다르다** | `style_prompt` 본문 · 악기·주법 어휘(사전 v3.3 437원자) |
| **T2 ⛔파손** | 그대로 옮기면 **곡이 망가진다** | **브라켓 문면 전체**(§3) |
| **T3 재설계** | 대응 개념이 없어 다시 짜야 한다 | spoken/narration 태그 계열(D005·D025~D028·D055~D061) · 콜론+숫자 태그 |
| **T4 ★역이식 기회** | **타 엔진에만 있는 칸** — 우리 설계를 더 정밀하게 적을 수 있는 자리 | seed · `duration_ms` · `keyscale`/`timesignature` · 네거티브 · `vocal_id` · MIDI/코드 조건화 |

★**독스트링 채점**: `song_form` **T0 — 맞다.** `style_prompt` **T1 — 「중립」이 아니라 「변환 가능」이다.**
그리고 독스트링이 말하지 않은 게 진짜 문제였다 — **`suno_lyrics`는 T2다.**

---

## §2. T2의 실측 — 무변경 이식의 대가

> 같은 곡·같은 SP로 `suno_lyrics`를 **MiniMax Music 3.0**에 무변경 이식:
> 곡 중간의 긴 브라켓 2건이 **그대로 가창**(bigram recall 0.92·1.00) → **24.5초 = 트랙의 13.9% 파손**.
> 짧은 브라켓 2~5어 8건은 전건 0.00 · 인트로·아웃트로 자리의 긴 브라켓(12어·11어)도 0.00.
> **M4** · leomusic3 08-29 · **통제쌍 n=1 · 엔진 1종 · 영어 1곡 · ASR 1종**

⚠**13.9%는 「이식 파손율」이 아니라 「이 1곡의 파손율」이다.** 모집단 추정치로 쓰지 않는다.

---

## §3. ★브라켓 변환 규칙 — 목표 엔진별

우리 브라켓은 두 종류가 섞여 있다. **이식할 때 먼저 이 둘을 가른다.**

| 종 | 예 | 정체 |
|---|---|---|
| **S. 섹션 라벨** | `[Verse 1]` `[Chorus]` `[Bridge]` | 구조 좌표 |
| **D. 연주 지시** | `[breathy male vocals]` `[the whole band drops out and leaves only a low sustained organ drone]` | 큐 |

| 목표 | S 섹션 라벨 | D 연주 지시 | 근거 |
|---|---|---|---|
| **Suno**(기준) | 그대로 | 그대로 | — |
| **MiniMax 3.0** | ✅**공식 14태그로 매핑**(`[Intro][Verse][Pre Chorus][Chorus][Interlude][Bridge][Outro][Post Chorus][Transition][Break][Hook][Build Up][Inst][Solo]`) | ⛔**가사에서 제거하고 `prompt`로 이동.** 특히 **곡 중간의 긴 지시는 불린다**(M4) | E1 + M4 |
| **Eleven Music** | ✅`chunks[].text` 안에 `[Verse 1]` 유지 | ✅**중괄호로 변환** `{guitar solo}` · 화성적 음성은 `(hmmm)` | E1 |
| **Lyria 3** | ✅자연어 `input` 한 칸에 `[Verse]` 포함 | ⚠**타임스탬프 서술로 재작성** 권장 `[0:00 - 0:10] Intro: …` | E1 |
| **Lyria RealTime** | ⛔**해당 없음 — 가사 자체가 불가**(instrumental only) | ⛔`WeightedPrompt{text,weight}` 배열로 **전면 재설계** | E1 |
| **Udio** | ✅그대로 | ⚠그대로 두되 **adherence는 확률적**(공식 명시). `( )`는 **백보컬로 불린다** | E2 |
| **ACE-Step** | ✅`[verse]`·`[chorus]` 소문자 계열 | ⚠텍스트 지시는 `caption`으로. **bpm·keyscale·timesignature·duration은 브라켓에서 빼서 파라미터로** | E1 |
| **SongBloom / LeVo** | ⚠**폐쇄 어휘로 강제 매핑**(`[intro]`·`[inst]`·`[outro]`, LeVo는 `-short`/`-medium` 접미) | ⛔**자유 문면 불가** — 어휘 밖은 버린다 | E1 |
| **DiffRhythm** | ⛔의미 태그 없음 — **timed LRC로 재작성** `[00:10.00]가사행` | ⛔불가 | E1 |
| **가창 합성**(ACE Studio·Synth V·VOCALOID) | ⛔**SP·브라켓 전면 폐기.** MIDI 노트 + 음절 배치 + 엔벨로프로 **재설계** | ⛔ | E1 |

★**한 줄 규칙**: **「D형 브라켓은 엔진을 건널 때 살아남지 못한다.」** 옮기려면 그 엔진의 **전용 채널**(prompt·`{}`·`caption`·파라미터)로 **이사**시켜야 한다.

---

## §4. `style_prompt`(T1) 변환 — 그릇이 다르다

| 축 | Suno | 타 엔진 | 조치 |
|---|---|---|---|
| **형** | 자유 문장 1개(≤1000자) | Eleven `positive_styles[]`(≤50) · Sonauto `tags`/`negative_tags` · ACE-Step `caption` | **문장 → 서술자 배열로 분해**. 우리 사전 437원자가 그대로 그 단위다 |
| **부정** | 문장 안에서 싸움 | `negative_styles[]`·`negative_prompt`·`negative_tags` | ★**부정 서술을 별도 배열로 뽑아낸다** — 우리 `suno_does_not_use`·dead-zone 25어가 여기 후보 |
| **언어** | 한국어 혼용 관행 있음 | **Eleven: 스타일 서술자 영어 필수**(가사는 임의 언어) · MiniMax 영어·중국어 | **스타일층만 영어 정화.** 우리 `ko_en_mood_glossary` 33어가 그 경로 |
| **숫자** | 텍스트로 밀어 넣음(→ 죽음) | ACE-Step `bpm`·`keyscale`·`timesignature`·`duration` · Eleven `duration_ms` | ★**텍스트에서 빼서 파라미터로 이사** |

---

## §5. ★T4 — 역이식 기회 (antisuno가 우리에게 되돌려주는 것)

| 칸 | 우리가 못 하던 것 | 열리는 것 |
|---|---|---|
| **seed** | 같은 SP를 두 번 돌린 결과를 고정 못 함 | ★**통제쌍에서 「한 글자만 다른 두 곡」이 성립.** 3년간의 근본 제약 |
| `duration_ms` | 길이 지시가 전달조차 안 됨(D015) | 구간 길이를 **계약**으로 |
| `keyscale`·`timesignature` | 코드명 0회·다이나믹 마킹 0회(dead zone) | 화성·박자를 **텍스트 밖**에서 |
| 네거티브 배열 | dead-zone 어휘를 「안 쓴다」로만 관리 | **「쓰지 마라」를 엔진에 직접** |
| `vocal_id` | 앨범 내 가수 동일성 보장 불가 | 15~30초 샘플로 **재사용 보이스** |
| MIDI·코드 조건화 | 멜로디 통제 불가 | Mureka `melody_id` · JASCO `chords` |

---

## §6. 이식 전 체크리스트 5문항

1. **가사 칸이 있는 엔진인가?** — 없으면(Lyria·MusicGen·Stable Audio·JASCO·Beatoven) 애초에 후보가 아니다.
2. **D형 브라켓을 어디로 이사시킬 것인가?** — 그대로 두면 §2의 대가를 치른다.
3. **스타일 서술자를 배열로 분해했는가? 영어인가?**
4. **텍스트 안의 숫자를 파라미터로 뺐는가?**
5. **seed를 고정했는가?** — 고정 안 하면 그 실험은 통제쌍이 아니다.

---

## §7. ⛔이 문서의 한계

1. **§3 변환표는 문서층(E)에서 유도한 처방이다.** 「이렇게 옮기면 보존된다」를 **잰 적이 없다**. 유일한 실측은 §2의 「무변경 이식은 깨진다」 1건(n=1)뿐이다.
2. **역방향을 안 봤다** — 타 엔진 자산을 Suno로 가져올 때의 규칙은 이 문서에 없다.
3. **T0을 실측한 적 없다.** `song_form`이 정말 중립인지는 **가정**이다. Phase 2 D안(이식 파손율)이 그걸 같이 잰다.
4. 가창 합성 계열(§3 맨 아래)은 **통제면의 종류 자체가 달라** 「변환」이 아니라 「다른 일」이다. 규칙표에 한 줄로 넣은 건 편의이고, 실제로는 별도 설계가 필요하다.
