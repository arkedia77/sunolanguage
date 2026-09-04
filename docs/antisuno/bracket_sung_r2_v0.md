# antisuno · R2 — 대괄호 가창 1차 관측 + 프롬프트 문법 대장

> Phase 1 산출물 ④. 2026-08-31 16:4x · sunolanguage
> 원자료 `data/antisuno/survey2/{raw_*.txt, parsed_bracket_sung.json, parsed_prompt_grammar.json}`
> 방법: `codex exec`+web_search 2클러스터(1차 라운드 한도 소진 후 재실행). ★**이 라운드는 E4를 일부러 수집했다** — 대신 전건 등급을 붙였다.

---

## §1. ★이 라운드 최대 발견 — **「태그는 안 불린다」를 공식으로 보증한 엔진이 하나도 없다**

`official_statements` 수집 결과: **0건.**

| 엔진 | 공식 문서가 말하는 것 | 말하지 **않는** 것 |
|---|---|---|
| Suno | (해당 문장 자체를 못 찾음 — `help.suno.com`) | 태그 비가창 |
| Udio | 「'hard-coded' commands의 목록이 **아니다**」·「AI가 최종 결정한다」 | 태그 비가창 |
| MiniMax | structure tags **14종 열거** | 태그 비가창 |
| Eleven | `[ ]`=section · `{ }`=inline direction · `( )`=phonetic sound **로 역할 구분** | 「절대 발음되지 않는다」 |
| ACE-Step | section/meta tags 문법 | 태그 비가창 |

⇒ ★**「대괄호 안은 지시다」는 어느 벤더도 보증한 적이 없다.** 우리 D004의 출처(songsmith)는 **제3자 블로그**다.
⇒ 우리가 3년간 「Suno는 대괄호를 지시로 읽는다」를 **관행으로** 다뤄 온 근거는 **벤더 보증이 아니라 우리 관측**이었다. 그건 문제가 아니다 — **문제는 그걸 벤더 규약처럼 인용해 온 것**이다.

---

## §2. ⛔★우리 자에 사각이 있을 가능성 — 이 라운드가 연 것

우리 값: **브라켓 전용 낱말 4,166건 → 가창 0건**(M1 전수).
**그 자는 Suno의 재분석 텍스트다.** 오디오가 아니다. (가이드 §6-2에 이미 「재분석 텍스트로 못 재는 축이 있다」고 적어 두었다.)

R2가 **오디오층 1차 관측**을 가져왔다 — 전건 **E4**이고, 전건 Suno에서다:

| 관측 | 문면 |
|---|---|
| `[big finish]` | 가수가 **"Big Finisssssshhhh!"** 를 속삭임 (v3) |
| `[echo indication for alive]` 등 | **"Feel alive…HEY ECHO…alive alive"** 로 가창 |
| 빈도 자가추정 | **「at least 1 out of 20 will sing what is in the brackets」** |
| 반대 관측 | 「I've about never had it sing instructions inside `[ ]` hard brackets.」 |

⇒ ★**두 값은 모순이 아니다. 층이 다르다.** 우리는 「재분석 텍스트에 안 나온다」를 쟀고, 저들은 「소리에서 들린다」를 말한다.
⇒ ⛔**그러나 이건 「우리 0/4,166이 부재를 잰 게 아니라 자의 사각일 수 있다」를 뜻한다.**

★**대장 칸은 안 움직인다** — v1.4 §4의 내 규칙대로 **E급은 대장 칸을 못 움직인다**. 움직이는 건 **한계 기재**이고, 이 축이 **Phase 2 최우선 표적**이 된다.

---

## §3. ★갈린 조건 — leomusic3 가설과 같은 축이 밖에서도 나왔다

전건 E4(Reddit). **조건 문면 그대로**:

| 축 | 문면 | 엔진 |
|---|---|---|
| **길이** | 「after a certain description length you're more likely to have things read out」·「keep the content in those brackets concise otherwise it'll misinterpret this content for lyrics」 | Suno |
| **길이** | 「if there's too much, Udio tends to ignore it or treat it like lyrics」 | Udio |
| **자기 줄·줄바꿈** | 「one or a few statements separated by periods and all on one line. I don't put line breaks here」 | Suno |
| ★**괄호 중첩·구두점** | 「`[verse: Guitar (drop D tuning), energetic]` where the `),` inside of that breaks the instructions」·「if you have something like `()`, followed by a comma, this causes it to break out of instructions」 | Suno |
| **버전** | 「In v4.5+, the part in parentheses would play as a nice chorus layer. **In v5, it just disappears.**」 | Suno |
| **위치**(공식) | 「We find that `[intro]` label is **less stable**, so we recommend starting with `[verse]` or `[chorus]`」 | **YuE · E1** |

★**leomusic3가 n=1에서 세운 「길이와 위치가 둘 다 걸린다」가 밖에서 독립으로 같은 방향으로 나왔다.** 등급은 낮지만(E4) **가설의 독립 지지**다.
★**새 축 1개 발견 — 구두점.** 「`),` 가 지시에서 튀어나오게 만든다」는 우리 축 목록에 **없던 것**이다. 우리 코퍼스에서 **바로 셀 수 있다**(브라켓 안 `),` 패턴 빈도 × 누출).

---

## §4. 모순 6건 — 지우지 않고 남긴다

| 엔진 | 충돌 |
|---|---|
| Suno `[ ]` | 「거의 안 불린다」 ↔ 「20곡 중 1곡은 불린다」 |
| Suno `( )` v5 | 「완전히 무시된다」 ↔ 같은 스레드에서 「Sings em for me」 |
| Udio `[ ]` | 같은 스레드에 「(usually) isn't sung」 ↔ 「sometimes it just says what is in the brackets」 |
| Riffusion | 「Riffusion will sing the brackets」 ↔ 전 가사를 대괄호로 감쌌더니 「no words are actually sung」 |
| MiniMax | 공식은 태그를 가사와 **구분**하되 비가창은 **보증 안 함** ↔ leomusic3 n=1에서 장문 태그 2건 **가창** |
| ACE-Step | `[chorus 1]`/`[chorus 2]`가 「no effect whatsoever」 — **가창도 비가창도 아닌 보고** |

⇒ ★**E4 층은 통제되지 않은 관측의 집합이다.** 방향이 갈리는 게 정상이고, **갈리는 그 자체가 「조건부다」의 증거**다.

---

## §5. 프롬프트 문법 대장 (E1 · 실무 직결)

### ⑴ 프롬프트 문자 상한 — 우리 1000자는 중간이다

| 엔진 | prompt 상한 |
|---|---:|
| Stable Audio 2.5 | **10,000** |
| Eleven Music | 4,100 |
| MiniMax Music | 2,000 |
| Mureka · Soundverse | 1,024 |
| **Suno**(우리 관행) | **1,000** |
| **ACE-Step 1.5 `caption`** | ★**512** |

★lyrics 상한과 혼동 금지(MiniMax lyrics는 3,500). ACE-Step은 우리의 **절반**이라 SP를 그대로 못 옮긴다.

### ⑵ ★한국어 — 우리에게 가장 중요한 칸

| 엔진 | 한국어 |
|---|---|
| **Mureka** | ✅**공식 명시** — 「supporting 10 languages: Chinese, English, Japanese, **Korean**, …」 |
| ACE-Step | ✅50+ 언어 목록에 포함 |
| **Eleven Music** | ⚠**Music 기준 unknown** — 「Korean (kor)」 목록은 **v3 음성 모델**용이지 Music 근거가 아니다 |
| **MiniMax Music** | ⚠**Music 기준 unknown** — 40개 언어 목록은 **speech synthesis** 문서 |
| **Stable Audio 2.5** | ⛔「Using foreign languages in your text prompt may result in mixed outcomes and **is not recommended**」 |
| Lyria 3 | 「generates lyrics in the language of your prompt」(한국어 개별 명시 없음) |

⇒ ★**한국어 가사가 주력인 우리에게 후보는 Mureka·ACE-Step이 앞선다.** Eleven·MiniMax는 **speech 문서를 Music 근거로 쓰면 안 된다**(이 라운드가 그 혼동을 걸러냈다).

### ⑶ 아티스트명 정책
- **Eleven Music·Lyria 3**: musician/band name·특정 아티스트 목소리 요청 **차단 명시**
- **Udio**: 스타일 참조는 허용, voice 복제는 안 함
- ★**ACE-Step**: 공식 가이드가 `reminiscent of Bon Iver`를 **작성 원칙의 예로 든다**

### ⑷ 공식 negative guidance — 방향이 하나로 모인다
「Too many instructions confuse the model」(ACE-Step) · 「Overloaded Prompts: Too many conflicting details confuse the model」(Soundverse) · 「Avoid repeating the same adjectives」(Stable Audio) · 「Don't try to control everything on your first attempt」(ACE-Step)
⇒ ★**우리 D002·D039·D050(「태그 쌓지 마라」·「반복이 강화가 아니다」)와 같은 방향이고, 저쪽은 공식 문서다.** 우리 축에서 **미측정**인 자리를 남의 E1이 채운다 — **일반 후보**.

---

## §6. ⛔한계

1. §2·§3·§4는 **전건 E4**(Reddit 개인 관측). **재현 조건·표본·오디오 원본이 없다.** 방향만 읽는다.
2. 「1 out of 20」은 **한 사용자의 자가추정**이다. 빈도로 인용하면 안 된다.
3. §5⑵의 `unknown`은 **「지원 안 한다」가 아니라 「Music 문서에서 근거를 못 찾았다」**다.
4. Riffusion 공식 prompting 문서는 **현재 404**(제품이 Flow Music으로 이전) — 그 엔진 문법은 복원 못 했다.
5. ~~gemini 미인증으로 독립 교차검증자가 여전히 없다~~ ⇒ ⛔**09-04 정정(LEO 지적)**: 이 라운드가 codex 단독인 것은 맞지만, **그 원인을 「gemini 미인증」으로 적은 것은 자를 잘못 댄 오판**이다. 이 머신의 구글 CLI는 **`agy`(antigravity-cli 1.1.3, 07-16 설치)**로 교체됐고 그 도구는 `~/.gemini/settings.json`도 `GEMINI_API_KEY`도 쓰지 않는다. 실측 `agy --print`→**PONG·rc=0**. ⇒ **교차검증자는 있었다.** 남은 실장애는 헤드리스 `read_url` 권한 자동거부 1건뿐(allow-rule로 해소 가능).

---

## §7. ★Phase 2 표적이 바뀐다

| 순위 | 안 | 왜 올라갔나 |
|---|---|---|
| **1** | ★**우리 자의 사각 검증** — 우리 코퍼스에서 **오디오로** 브라켓 가창 여부를 직접 잰다 | §2. 0/4,166이 부재인지 사각인지가 **대장에서 제일 두꺼운 값의 근거**다 |
| ~~2~~ ⇒ **강등** | ~~구두점 축 — 브라켓 안 `),` 패턴 × 누출~~ | ⛔**같은 날 세었고 못 잽니다** — 아래 §8 |
| 3 | 소괄호 축(D003) | 기존 1순위. Suno v4.5→v5 거동 변화 보고까지 붙었다 |
| 4 | 브라켓 어절수 × 위치 | leomusic3 n=1 확장 |

---

## §8. ★§7 순위2를 같은 날 내가 내렸다 — 세어 봤더니 조건이 없다

§7에 「구두점 축은 코퍼스에서 **지금 바로 셀 수 있다**」고 적고 **실제로 셌다**(`scripts/antisuno_punct_axis_v1.py` · 생성 0 · 크레딧 0).
★**재기 전에 사전등록부터 했다**: 기존 전수에서 판정가능 낱말 5,968 중 **누출 0건**이라 **종속변수의 분산이 0**이다 ⇒ 「구두점 있는 브라켓이 더 샌다」는 **이 자로는 원리상 못 잰다**. 그러니 잰 것은 **효과가 아니라 기저**다.

| 패턴 | 입력 브라켓 4,154 중 | |
|---|---:|---|
| ★**`),` (R2 문면 그대로)** | **0건 (0.00%)** | ⛔조건 자체가 우리 코퍼스에 **없다** |
| 중첩 소괄호 `(…)` | **0건 (0.00%)** | ⛔없다 |
| 쉼표 | 217건 (5.22%) | 있다 — 그런데 누출 0 |
| 콜론 | 3건 (0.07%) | `[last sound: solo violin harmonic]` 등 |
| 마침표·세미콜론 | 0건 | 없다 |

*(모집단 423곡 · 입력 브라켓 4,154. 08-27 전수의 3,863과 다른 것은 코퍼스가 540→560곡으로 늘어서다.)*

⇒ ★**판정: 구두점 축은 우리 코퍼스로 검증 불가.** 「효과가 없다」가 아니라 **「그 조건이 한 번도 발생하지 않았다」**다. 재려면 **그 문면을 일부러 넣어 생성**해야 한다 ⇒ Phase 2 생성 항목으로 **강등**.
⇒ ✅**대신 남는 값 하나**: **쉼표는 217건 있는데 누출은 0**이다. 「구두점이 지시를 깨뜨린다」의 **약한 음성 증거**다 — 단 쉼표는 R2가 지목한 그 패턴(`),`)이 **아니므로** 반박이 아니라 **다른 축의 값**이다.

★**교훈**: 「지금 바로 셀 수 있다」와 「세면 답이 나온다」는 다르다. **기저를 먼저 안 보고 순위를 매겼다.**
