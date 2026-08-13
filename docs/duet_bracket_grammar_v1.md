# 듀엣 화자 지시 문법 v1 — 코퍼스 실측 정본

**작성**: sunolanguage · 2026-08-03
**계기**: LEO 지적 — "브라켓에 (여)인데 남자 목소리 나옴. 노래는 만들어짐"
**근거**: `data/reanalysis_v2/lexical_index.sqlite` (bracket_entity 6,635 + stems_bracket 2,343 + sp_entity 6,614 + suno_sp_full 505)
**전 세션 오판 정정**: VD 재제작 시 `[Male Vocal]` 명찰형 단일 토큰만 조회하여 "듀엣 코퍼스 0건"으로 보고 → **곡 단위 듀엣 문법 3곡이 실재**. 본 문서가 정본.

---

## 0. 한 줄

Suno에게 화자는 **명찰(누가)이 아니라 음원 서술(무엇이 들리는가)**로만 전달된다.
`(여)`가 남자로 나오는 것은 거부도 버그도 아니고, **명찰 채널이 데드존**이기 때문이다.

---

## 1. 증상의 정체 — 거부 아님, 데드존

| 관측 | 판정 |
|---|---|
| 곡은 정상 생성됨 | Suno가 입력을 **수용**함 (거부·모더레이션 아님) |
| `(여)` 구간에 남성 보컬 | 지시가 **무시**됨 = ch5 3계층의 **3층 데드존** |

`docs/manual_v3/ch5_absence.md` 3계층(렌더 / 부분반응 / 데드존)의 데드존 사례에 **화자 명찰**을 추가한다.

### 실측 데드존 (브라켓+SP 전 채널)

| 표기 | 코퍼스 건수 | 판정 |
|---|---|---|
| `[Male Vocal]` / `[Female Vocal]` (Title Case 명찰) | **0** (GLOB 대소문자 정밀) | dead |
| `(Male)` / `[Male]` | **0** | dead |
| 한글 화자 명찰 `(남)` `(여)` `[남]` `[여]` | **0** | dead |
| `singer 1` / `voice 1` / `duet part` / `narrator` | **0** | dead |
| `man` / `woman` | **0** | dead |

> 한글이 브라켓에 들어간 attested 사례는 **4건뿐이며 전부 "부를 한국어 가사 지정"**이다 —
> `[vocal ad-lib: '전부거든']`, `[vocal harmony on '삭제']`, `[drummer counts in: 하나, 둘, 셋, 넷]`.
> 즉 브라켓 속 한글 = **가창 내용**이지 **화자 신원**이 아니다. 이 용법만 유효.

### 선행 실증 — 명찰형 실패는 2026-07-11에 이미 계측됐다

leomusic3 K3016 OST 8번(73BPM Low 소프트 발라드, 한국어 독백)에서 남성 저음 지시 **4회 전부 미준수**, 스템 F0 실측:

| 시도 | 표기 | F0 median |
|---|---|---|
| ② | SP `low steady male vocal` | 309.3Hz |
| ③ | SP 헤드 `deep baritone male singer` + `no female vocals` | 247.6Hz |
| ④ | 가사 인라인 **`[Male Vocal — deep low baritone]`** + 섹션 `[male vocal]` | **247.8Hz (무변화 포화)** |

근거: `agent-comm/projects/sunolanguage/messages/sunolanguage_leomusic3_20260711_213206_보컬성별지시_준수율협의.json`
→ ④가 바로 **명찰형**이며, 이중결합에도 F0가 꿈쩍하지 않았다. VD 08-03 관측은 **재발**이지 신규가 아니다.

---

## 2. 왜 하필 남자로 떨어지는가 — 코퍼스 편중 (기전)

| 채널 | 남성만 지정 | 여성 포함 | 비 |
|---|---|---|---|
| 브라켓 | 395건 | 92건 | **4.29 : 1** |
| SP | 1,039건 | 237건 | **4.38 : 1** |

두 채널이 독립적으로 같은 4.3:1을 보인다. **Suno의 기본 사전확률이 남성 쪽에 강하게 쏠려 있다.**
→ 지시가 약하거나(명찰형) 모호하면 **남성으로 붕괴한다.** 여성 지시는 남성 지시보다 **더 강하고 더 자주** 박아야 한다.

### 2.1 어휘로 못 고치는 층 — 프라이어 (★한계선)

K3016 실측(§1)의 결론은 **어휘·표기·구조(프라이어) 3층 분리**였다
([[project_vocal_gender_register_drift]], `docs/manual_v3/ch5_absence.md` 3계층과 정합).

- **저에너지 소프트 발라드 + 1인칭 독백 가사** 조합에서는 성부 지시가 **어떤 표기로도** 교정되지 않았다(네이티브 정형 이중결합도 실패).
- 같은 배치의 **duet(male-female trading) 10번은 정상 성립** → 성별 지시 자체가 죽은 게 아니라 **특정 정서·에너지 조합에서만 붕괴**한다.

★ VD 미정합 3클립 중 **BL1(발라드, SP=whisper·저에너지·친밀)**이 정확히 이 조건이다.
→ **R1~R6을 다 지켜도 저에너지 발라드 듀엣은 화자가 무너질 수 있다.** 이건 문법이 아니라 기획 단계 리스크다.

---

## 3. attested 듀엣 문법 — 실증 3곡

전 코퍼스에서 남녀 듀엣이 곡 단위로 확인되는 것은 다음 3곡뿐이며, **세 곡이 같은 문법**을 쓴다.

### 3.1 song_id **20009** (TROT · 트로트 GT 앵커 세트 gid20001~20012 소속)

Suno 원문 SP: *"Male and female vocalists perform in a **call-and-response and unison format**, characterized by powerful **chest-voice** delivery and occasional vibrato."*

```
[Intro]
[distorted electric guitar riff, driving drum beat, slap bass]
[Verse 1]
[male vocals]
[palm-muted guitar]
[Verse 2]
[female vocals]
[bass slides]
[Chorus]
[unison male and female vocals, full band energy]
[electric guitar power chords, cymbal crashes]
[Outro]
[guitar solo, fading drum beat]
[vocal ad-libs]
```

★ **SP에 음색 대비 서술이 전혀 없다.** 브라켓 교대만으로 남녀가 갈렸다.

### 3.2 song_id **C_1484** (K-Indie pop, soft acoustic)

Suno 원문 SP: *"Male and female vocals **alternate and harmonize** in a breathy, intimate delivery."*

```
[Verse 1]
[male vocals, breathy]
[Chorus]
[female vocals enter, harmonizing with male vocals]
[Verse 2]
[male vocals]
[male and female duet]
[Bridge]
[instrumental break, acoustic guitar and electric guitar interplay]
```

### 3.3 song_id **1633** (Folk / K-Pop acoustic ballad)

Suno 원문 SP: *"featuring a **male and female vocal duet**… The male vocal is a warm **baritone**, while the female vocal is a clear, **airy soprano**. Both voices utilize breathy delivery and gentle vibrato."*

```
[Verse 1]
[male vocals]
[Chorus]
[female vocals enter]
[clean electric guitar melody enters]
```

---

### 3.4 형제 실증 — leomusic3 K3016 #10

코퍼스 밖 **우리 생성 실증**: leomusic3 K3016 배치 10번 **duet(male-female trading) 정상 성립**
(근거: `agent-comm/.../sunolanguage_leomusic3_20260711_213206_보컬성별지시_준수율협의.json`)
→ 듀엣 화자 분리는 **이미 성공한 적 있다**. 실패한 건 듀엣이 아니라 **단일 화자 저에너지 발라드의 성부 고정**(§2.1)이었다.

---

## 4. 규칙 (attested만)

### R1 — 화자는 vocal_main 브라켓 **독립 행**으로, 섹션 브라켓 **바로 다음 줄**에

```
[Verse 2]
[female vocals]
가사 첫 행…
```
❌ 가사 행 안에 인라인 금지, ❌ 명찰형 금지, ❌ 한글 금지.

### R2 — 교대 진입은 **`enter` 동사형**

attested: `[male vocals enter]` **18**(08-11 DB 재계수 — 종전 17은 오차 1) · `[female vocals enter]` 4 · `[male tenor vocals enter]` 5
`enter`는 "지금 이 사람이 새로 들어온다"는 **전환 신호**다. 첫 등장과 화자 교체 지점에 쓴다.

### R3 — 동시발성은 `unison` + **에너지 동반 서술**

attested 정본: **`[unison male and female vocals, full band energy]`** (3건)
보조: `[layered vocal harmonies]` · `[male and female duet]`(1건) · `[female vocals enter, harmonizing with male vocals]`(1건)
※ `[both]` `[together]` = **0건, 쓰지 말 것**.

### R4 — 여성 지시는 남성보다 **강하게·반복해서**

§2 편중(4.3:1) 대응. 여성 구간은 매 섹션마다 재지시하고, 수식어를 붙여 신호를 키운다.
attested female 수식어(빈도순): `breathy`(33) · `soft`(4) · `with light reverb`(4) · `rhythmic`(2) · `bright`(1) · `airy`(1) · `ethereal … soprano`(1)

### R5 — 음역·음색 수식은 **성별 토큰에 붙여 쓴다** (별도 행 금지)

attested 어순: `[breathy male vocals]`(77) · `[male tenor vocals]`(30) · `[baritone male vocals]`(14) · `[smooth male tenor vocals]`(8)
→ 어순 = `[<질감> <성별> <음역> vocals]`. `[breathy]`만 단독으로 두면 화자 정보가 사라진다.

### R6 — SP 채널은 **관계**를 쓴다 (개별 음색이 아니라)

attested SP 원문형 3종:
- `Male and female vocalists perform in a call-and-response and unison format` (20009)
- `Male and female vocals alternate and harmonize in a breathy, intimate delivery` (C_1484)
- `featuring a male and female vocal duet` + `The male vocal is a warm baritone, while the female vocal is a clear, airy soprano` (1633)

→ SP는 **① 듀엣 선언 ② 교대/합창 관계 ③ (선택) 남녀 각 1구절 음역** 순.

---

## 5. spoken vs narration — 채널별 실측

**결론: `narration`은 Suno 어휘가 아니다. 말하기는 `spoken-word`이며, 채널마다 유효성이 다르다.**

> ★**계수 단위 주의 (2026-08-11 정정)** — 아래 표의 SP 숫자는 **엔트리 행수**다. **곡 수가 아니다.**
> `spoken-word`의 경우 23행 / 16문장형 / **관측 9곡(497곡 중)**. 22를 곡 수로 읽으면 **2.4배 과대**가 된다.
> 계기: encore CM-2026-0001 회신(08-11) 준비 중 자기적발. 이 표를 인용할 땐 **곡 수로 환산해서** 쓸 것.

> ★**dead 판정에는 채널 한정자를 반드시 붙인다 (08-11 실피해 1건)** —
> 내가 06-15 leomusic-trot에 보낸 GT 회신은 표에 `spoken … dead`만 적고 채널 한정자를 안 붙였다.
> 본문에 「SP/() 채널에선 다를 수 있음」 주의를 달았으나 **표만 인용되면 caveat이 안 따라간다.**
> 2개월 뒤 encore가 그 표를 근거로 **「나레이션은 생성 불가」로 커미션 설계를 닫을 뻔했다.**
> → **채널을 안 적은 dead는 dead가 아니라 「어느 채널에서 dead인지 안 적은 것」이다.**

> ★★★**층 한정 — 위 경고를 내가 한 층 위에서 똑같이 어겼다 (2026-08-13 철회)** —
> **이 절의 모든 건수는 `Suno 출력 SP·브라켓`(관측층) 계수다.** 즉 **「Suno가 곡을 분석해서 그렇게 뱉는가」**를 센 것이고,
> **「사람이 입력에 그렇게 쓰면 먹는가」(입력층)를 잰 적이 없다.** 둘은 다른 층이다.
> ⇒ ★**「브라켓 dead」는 「Suno가 출력에 안 뱉는다」까지만이고 「입력에서 무효」가 아니다.**
> **철회분**: 내가 §5.1에 적었던 「**고립된 `[spoken]`이 죽는 이유가 이것**」(인과)과,
> 그걸 근거로 08-11 encore에 보낸 「**나레이션을 독립 블록으로 쓰지 마십시오**」(입력층 처방)를 **철회한다.**
> 그 분포에서 그 인과도 그 처방도 나오지 않는다.
> **반증 실물**: 오너 제공 1차 출처(`repo:sunolanguage/data/metatag_external/yt/OTDqev8aW0A_screen_read.json`)가
> **전이 서술 0건으로 고립 말하기 상태**를 쓴다(`Single male spoken narration` / `[Monologue: dramatic cinematic narration, low restrained male voice]`).
> 8기법 **8/8 전건이 브라켓을 쓰고**, ASR 교차검산에서 말하기/가창이 갈렸다(말하기 4기법 `[노래]` 0/0/0/0 vs 가창 6/6/1).
> ⚠**단 그 출처는 단일·대조군 없음**이라 **「브라켓을 쓰라」로 뒤집지도 않는다.** 정확한 상태는 **「입력층 미측정」**이다.
> ⇒ ★**`()` 괄호 채널 판정은 반대로 강화됐다** — 같은 출처가 말하기 가사를 **4/4 소괄호**, 가창 **0/3**으로 무예외 분리했다(§5.3).

| 표현 | 브라켓 | SP(행수) | 판정 ※전부 **관측층**(출력) 계수 — 입력층 아님 |
|---|---|---|---|
| `spoken-word` | 1건 (`[spoken-word delivery]`) | **23행 / 16형 / 관측 9곡** | 브라켓 dead · **SP live** |
| `narrative` | 0건 | 2건 | 희소 — 뜻이 다름(§5.2) |
| `narration` / `narrator` / `voiceover` / `monologue` / `dialogue` / `recitative` / `sprechgesang` / `talk` / `speak` | **0** | **0** | **전 채널 dead** |
| `whisper` | 1건 | 4건 | 브라켓 dead · SP 한정 live |
| `chant` | 3건 | 9건 | 양 채널 live |
| `shout` | 17건 | 11건 | 양 채널 live |

### 5.1 spoken-word = **말하기 자체**

SP attested 원문:
- *"The vocals are delivered in a low-register, intimate, **spoken-word style that transitions into melodic singing**."*
- *"A solo male vocalist performs with a soft, breathy delivery, **transitioning into a spoken-word style**."*
- *"A deep, processed male voice provides **spoken-word cues** throughout the arrangement."*

★ **패턴: spoken-word는 거의 항상 `transitions into / transitioning` 전이 서술과 함께 온다.**
Suno는 "말하기 구간"을 독립 상태가 아니라 **노래와의 전이**로 표상한다.

> ~~고립된 `[spoken]`이 죽는 이유.~~ ★**2026-08-13 철회.** 위 패턴은 **출력층 분포**로 참이지만,
> 거기서 **입력층 인과**(「그래서 고립 태그가 죽는다」)는 나오지 않는다. **「Suno가 그런 곡을 그렇게 묘사한다」는
> 「그렇게 안 쓰면 안 된다」를 함의하지 않는다.** 근거·반증은 §5 머리 철회 박스 참조.

### 5.2 narrative = **말하기가 아니라 서사적 창법**

SP attested 2건 중 명확한 것:
- *"A male baritone vocal delivers a **narrative performance, transitioning into a powerful, belted chest voice** during the chorus."*

→ 여기서 narrative는 **여전히 노래**다. 벌스의 담담한 서사조 → 후렴 벨팅으로 가는 **대비 축**을 가리킨다.
**말하게 하고 싶으면 `narrative`가 아니라 `spoken-word`.**

### 5.3 괄호 `()` 채널의 `(spoken)`

코퍼스 0건이나 **LEO 실청취 4/4 유효** (`data/bracket_vs_paren_test_protocol.md` §1, ch2 () 채널 검증분: hums softly / melismatic runs / trills / spoken).
→ **`(spoken)`은 괄호 채널에서만 살아 있다.** VD 재제작(RM)이 `(spoken)`을 쓴 것은 채널 선택이 옳았다.

### 5.4 말하기 3채널 요약

> ★**이 표만 떼어 인용될 것을 전제로 한정을 표 안에 박는다** — 08-11에 「표만 인용되면 caveat이 안 따라간다」로
> 실피해 1건이 났는데, 그 교훈을 **표 밖 박스에만 적어서** 08-13에 같은 자리에서 또 샜다.

| 채널 | 표기 | 유효 | 용도 |
|---|---|---|---|
| SP | `spoken-word style transitioning into melodic singing` | ✅ 23행 / **관측 9곡**(출력층) | 곡·구간 성격 선언 |
| `()` 괄호 | `(spoken)` | ✅ **실청취 4/4**(Dead Budget 04-25·별개 재료) + ASR 재현 — ★**입력층 실측이라 이 표에서 등급이 가장 높다** ⚠**단 기계 판별은 판정 가능 2클립 중 1클립만 견고**(RM2 대조군 15조합 중 14가 「말하기」 / RM1은 대조군 종속이라 판정 불가). ★**08-13 N=4 확장 결과: 시도 4클립 중 2클립을 게이트가 기각**했다 — 뮤지컬 편곡은 가창부 sustain이 낮아 **자가 먼저 무너진다**(A 0.45/0.44 vs RM 0.53/0.55). ⇒ **표본을 2배로 늘렸는데 판정 가능 표본은 안 늘었다.** ★**곡 수준 일반화 금지.** 근거=`scripts/spoken_probe_sensitivity.py`·`scripts/spoken_delivery_probe_n4_report.py` | 해당 행을 말로 |
| `[]` 브라켓 | `[spoken]` | ⚠**입력층 미측정** (출력층 1건뿐 ≠ 입력 무효. ~~쓰지 말 것~~ **08-13 철회**) | 판정 보류 — 쓰려면 대조군을 붙일 것 |

---

## 6. VD 실측과의 정합 (교차검증)

`data/vd_duet3/VD_FINAL_judgment.json` 8클립:

| 버전 | 화자 표기 | 정합 |
|---|---|---|
| RM (영어 서술형 브라켓 + `(spoken)`) | R1·R2·R3 준수 | **2/2** |
| v2.3 3곡 (한글 `(남)/(여)`) | 명찰형 = 데드존 | 4/6 |

미정합 3클립(BL1 코어2 남성 지속 · G1 코어1부터 여성 리드 · M23a 혼합) = **전부 `(여)` 지시가 남성으로 붕괴한 사례**로, §2 편중과 §1 데드존으로 설명된다.
단 RM은 브라켓과 SP가 동시에 바뀌어 기여 분리는 미완(N=2, confidence med) — **20009가 SP 대비 없이 브라켓만으로 성공**한 것이 브라켓 채널 단독 충분성의 실증이다.

---

## 7. 미결 — 이 문서로 못 닫는 것

1. **S_BP 2단계 미완**: `data/s_bp/s_bp_stage1_results.json` 21곡 생성·UUID 확보(2026-05-26) 후 `reanalysis_*` 전 필드 null. `[]` vs `()` 정량 대조가 70일째 미종결.
   - 참고 관측(교란 있음): take2 산출률이 `[breathy female vocals]` 브라켓 조건(BP_B1)만 **0/3**, 괄호 조건 2/3, 악기 브라켓 3/3. 단 CTRL도 1/3이라 캡처 누락 가능성 배제 못 함 — **단정 금지**.
2. **듀엣 실증 N=3**: 코퍼스 확장 시 남녀 듀엣곡 수집 우선순위 상향 필요.
3. **여성 편중 대응 R4의 효과 미검증**: 반복 지시가 실제로 붕괴를 막는지 A/B 미실시.

4. ★**미검증 대응 후보 — `Exclude styles`(negative_tags 전용 채널)**
   sunomusic ch7 실측(2026-08-03)으로 **`Exclude styles` 입력이 clip metadata `negative_tags`로 저장되는 실채널**임이 확인됐다(ch7 §7.1 정정분).
   → §1에서 실패한 K3016 ③ `no female vocals`는 **SP 산문 안의 부정 서술**이었다. 데드존인 것은 *부정 서술의 위치*이지 **부정 자체가 아닐 수 있다.**
   **가설**: 남성 붕괴 구간에 `Exclude styles = male vocals`를 걸면 §2 편중(4.3:1)을 프롬프트가 아닌 **파라미터 층에서** 눌러줄 가능성.
   **미검증** — ch7 A/B는 `saxophone, brass, horn`(악기) 대조뿐이고 **성별 대조는 미실시**, 음향 억제 실효도 귀측 판정 전. 채택 전 반드시 성별 A/B 필요.

---

## 8. 근거 등급 — ★대장은 여기 없다 (포인터)

이 문서의 규칙들이 **어느 등급의 근거 위에 서 있는지**는 전부
**`docs/corpus_classification_criteria_v1.md` §11 「외부 근거 등급 대장」**에 있다.

**이 문서 소관 행** (등급·한정자는 §11에서 읽을 것):
`(spoken)` 괄호 채널 · 듀엣 화자 R1~R6 · `narration`류→`spoken-word` 계수 ·
`spoken-word` SP 유효 · `[]` 브라켓 맨 명찰(판정 보류) · Styles의 브라켓 선행 서술.

> ★**왜 표를 여기 복사하지 않는가** — 두 가지가 겹친다.
> ⒜ **G-K4 단일 기재**(룰 전문은 1곳만).
> ⒝ ★**더 실질적인 이유: 오늘 복사본 때문에 사고가 났다.** 08-13 leomusic2 ACK가
>   **내 정본의 스테일**을 드러냈고, 같은 날 `metatag_narration_gap_v1`의 등급도 **스크립트 쪽만 안 고쳐져 19/15로 갈렸다.**
>   표를 복사하면 **한쪽만 늙는다.** 그래서 등급은 **한 곳에서만** 기른다.
>
> ★단 **§5.4의 한정자는 그 표 안에 그대로 둔다** — 그 표는 「말하기 3채널 요약」이라
> **떼어서 인용되는 것이 용도**이고, 등급이 아니라 **채널 선택**을 가리키기 때문이다.
> (등급이 바뀌면 §5.4도 같이 고친다. ★이 문단이 그 의무를 적어 두는 자리다.)
