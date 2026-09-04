# antisuno · 엔진 통제면 대장 v0

> Phase 0 산출물 ①. 작성 2026-08-31 · sunolanguage
> 자료: `codex exec`+웹검색 5클러스터(`data/antisuno/survey/parsed_*.json`) + 세션 직접 원문도달분(`claude_firsthand_v0.json`)
> 병합본 `data/antisuno/survey/merged_v0.json` · **엔진 36종**
> ⛔**전건 문서층(E)이다. 렌더 실측(M)은 이 문서에 하나도 없다** — 유일한 예외는 §4의 leomusic3 M4 1건이고 출처를 값 옆에 붙였다.

---

## §0. 이 대장의 한 줄

**「대괄호」는 하나의 문법이 아니었다.** 36엔진을 늘어놓으니 같은 `[ ]` 안에 **여섯 가지 서로 다른 의미**가 들어 있다(§4).
우리가 3년간 잰 건 그중 **한 칸(Suno)의 성질**이고, 그걸 「음악 LLM은 대괄호를 지시로 읽는다」로 일반화한 적이 있다면 그건 틀렸다.

## §1. 축 대조표 (○=있음 ✗=없음 ?=문서 미확인)

| 엔진 | 가사칸 | 구조태그 | 길이지정 | 참조오디오 | 네거티브 | seed | 스템 | 편집 | 실시간 | API 파라미터수 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|--:|
| **Suno** *(우리 기준선)* | ○ | ○ | ✗ | ○ | ✗ | ✗ | ○ | ○ | ✗ | 비공개 |
| Lyria 2 (Vertex) | ✗ | ? | ✗ | ✗ | ○ | ○ | ? | ✗ | ✗ | 4 |
| **Lyria 3** (Gemini API) | ✗* | ○ | ○ | ✗ | ✗ | ✗ | ? | ✗ | ✗ | 7 |
| **Lyria RealTime** | ✗ | ✗ | ✗ | ✗ | ○ | ○ | ✗ | ○ | **○** | 15 |
| Google Flow Music | ○ | ? | ○ | ○ | ? | ? | ? | ○ | ✗ | — |
| **MiniMax Music 3.0** | ○ | ○ | ✗ | ○ | ✗ | ✗ | ? | ○ | ✗ | 14 |
| **Mureka** | ○ | ○ | ✗ | ○ | ✗ | ✗ | ○ | ○ | ? | 20 |
| 天工 SkyMusic 2.0 | ○ | ? | ? | ○ | ? | ? | ? | ? | ○ | — |
| **Udio** | ○ | ○ | ○ | ○ | ? | ? | ? | ○ | ✗ | — |
| **Eleven Music (music_v2)** | ○ | ○ | ○ | ○ | ○ | ○ | ? | ○ | ✗ | 17 |
| Riffusion / FUZZ | ○ | ? | ? | ○ | ? | ? | ○ | ○ | ? | — |
| Stable Audio 2.5 | ✗ | ✗ | ○ | ○ | ✗ | ○ | ? | ○ | ✗ | 11 |
| **Sonauto Melodia** | ○ | ? | ○ | ○ | ○ | ○ | ? | ○ | ✗ | 26 |
| Soundverse | ○ | ? | ○ | ○ | ✗ | ✗ | ○ | ○ | ✗ | 21 |
| Beatoven.ai | ✗ | ✗ | ○ | ? | ✗ | ✗ | ○ | ? | ✗ | 4 |
| **YuE** (OSS) | ○ | ○ | ○ | ○ | ? | ○ | ○ | ○ | ✗ | 21 |
| **ACE-Step** (OSS) | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ✗ | **44** |
| **DiffRhythm** (OSS) | ○ | ✗† | ○ | ○ | ✗ | ○ | ✗ | ○ | ✗ | 11 |
| **SongBloom** (OSS) | ○ | ○ | ○ | ○ | ? | ? | ✗ | ✗ | ✗ | 9 |
| **LeVo / SongGeneration** (OSS) | ○ | ○ | ○ | ○ | ? | ? | ○ | ✗ | ✗ | 12 |
| MusicGen / AudioCraft | ✗ | ✗ | ○ | ○ | ✗ | ? | ✗ | ○ | ✗ | 18 |
| JASCO | ✗ | ✗ | ✗ | ○ | ✗ | ? | ✗ | ✗ | ✗ | 7 |
| MusicGen-Stem | ✗ | ✗ | ? | ○ | ? | ? | ○ | ○ | ✗ | — |
| Stable Audio Open | ✗ | ✗ | ○ | ○ | ○ | ○ | ✗ | ○ | ✗ | 20 |
| InspireMusic | ✗ | ✗ | ○ | ○ | ? | ? | ✗ | ○ | ✗ | 15 |
| Seed-Music (ByteDance) | ○ | ? | ? | ○ | ? | ? | ? | ○ | ? | — |
| ACE Studio 2.0 ‡ | ○ | ✗ | ○ | ○ | ✗ | ✗ | ○ | ○ | ? | — |
| Synthesizer V Studio 2 Pro ‡ | ○ | ✗ | ○ | ○ | ✗ | ? | ? | ○ | ? | 8 |
| VOCALOID6 ‡ | ○ | ✗ | ○ | ○ | ✗ | ✗ | ? | ○ | ○ | — |
| CeVIO AI Song ‡ | ○ | ✗ | ○ | ✗ | ✗ | ✗ | ? | ○ | ✗ | — |
| UTAU / OpenUtau ‡ | ○ | ✗§ | ○ | ✗ | ✗ | ✗ | ○ | ○ | ✗ | 16 |

\* Lyria 3는 **가사 칸이 따로 없고** 가사·태그·BPM·조성·타임스탬프를 **자연어 `input` 한 칸에 함께** 넣는다 — 「칸이 없다」가 아니라 「칸이 하나다」.
† DiffRhythm은 의미 구조 태그 대신 **timed LRC**(`[00:10.00]가사행`)를 쓴다 — §4 Type D.
‡ 가창 합성 계열. 통제면이 **자연어가 아니라 MIDI 노트+음소+엔벨로프**다. 「길이지정」은 노트 길이를 뜻한다.
§ OpenUtau의 대괄호는 **음소 힌트**(`read[r iy d]`)다 — §4 Type E.

## §2. Suno에 **없는** 통제면 — 발견 순으로

| # | 통제면 | 실물 | 우리에게 뜻하는 것 |
|---|--------|------|--------------------|
| 1 | **가중 프롬프트** | Lyria RealTime `WeightedPrompt{text, weight}` 배열 | 프롬프트가 문자열이 아니라 **벡터**. 「A를 0.8, B를 0.2」가 문법으로 존재 |
| 2 | **구간별 길이 계약** | Eleven `chunks[].duration_ms`(3~120초) + `respect_sections_durations` | 우리 D015가 「전달조차 안 됐다」로 끝난 축이 여기선 **필드 이름을 갖고 있다** |
| 3 | **응집 강도 3단** | Eleven `context_adherence: low\|medium\|high` | 「앞뒤 구간과 얼마나 붙일지」를 사람이 고른다 |
| 4 | **seed 재현성** | Lyria2/RT · Eleven · Sonauto · Stable Audio · ACE-Step · YuE · DiffRhythm | ★**우리는 같은 SP를 두 번 돌린 결과를 고정할 수 없다.** 통제쌍 설계의 근본 제약이 여기서 풀린다 |
| 5 | **네거티브 프롬프트** | Lyria2 `negative_prompt` · Eleven `negative_styles` · Sonauto `negative_tags` · ACE-Step | 「하지 마라」를 별도 채널로. Suno는 SP 문장 안에서 부정문으로 싸울 수밖에 없다 |
| 6 | **화성·조성·박자 별도 경로** | ACE-Step `bpm`·`keyscale`·`timesignature`·`duration`이 **각각 독립 조건 경로로 DiT에 전달** | ★우리 사전 v3.3 `suno_does_not_use`가 「코드명 0회·다이나믹 마킹 0회」인 이유의 유력 후보 — **Suno엔 그 경로가 없어서 텍스트로 넣으면 죽는 것** |
| 7 | **구간 국소 편집** | Mureka `/v1/song/region-edit`(시간구간+가사) · Stable Audio `mask_start`/`mask_end` · Eleven `store_for_inpainting` | 「그 마디만 고친다」 |
| 8 | **멜로디/MIDI 조건화** | Mureka `melody_id`(5~60초 오디오 **또는 MIDI**) · Soundverse `midi`·`melody` · MusicGen `melody_wavs` · JASCO `chords`+`drums_wav` | ★**JASCO는 코드 진행을 조건으로 직접 받는다** |
| 9 | **재사용 보이스 ID** | Mureka `vocal_id`(15~30초 샘플로 생성) · Soundverse `vocal_id` | 「같은 가수로 앨범 열 곡」 |
| 10 | **실시간 스티어링** | Lyria RealTime(WebSocket 중 config 갱신·`reset_context`) · MusicFX DJ · SkyMusic/Melodio | 생성 **도중** 지시 변경 |
| 11 | **타임스탬프 지시** | Lyria 3 `[0:00 - 0:10] Intro: …` · DiffRhythm LRC `[00:10.00]` | 초 단위 좌표 |
| 12 | **음소 단위 편집** | CeVIO(직접 입력 음소가 가사 계산 음소보다 **우선**) · OpenUtau `phoneticHint` · Synth V `pitchDelta`·`tension`·`breathiness` | 발음을 문자가 아니라 **음소로** |

## §3. Suno에 **있고** 다른 데 드문 것 — 공정하게

- **가사 칸 + 구조 태그 + 스타일 프롬프트 3채널을 동시에**, 그리고 **엔진이 스스로 만든 태그 어휘가 대량 존재**한다(우리 코퍼스 560곡의 근거).
- Lyria 계열은 **가사 자체가 없다**(Lyria 2/RealTime = instrumental only, 문서 명시). MusicGen·JASCO·Stable Audio·InspireMusic·Beatoven도 가사 경로 없음.
  ⇒ **36엔진 중 사용자 가사로 노래를 만드는 건 절반가량이다.** 「Suno 대체」를 말할 때 이 절반은 애초에 후보가 아니다.

## §4. ★대괄호 의미론 6종 — 이 대장의 핵심 산출

| 형 | 의미 | 불리나 | 실물 |
|---|------|:-:|---|
| **A. 구조 제어 토큰** | 섹션 경계를 모델에 알림 | 안 불림 | Suno(M1 4,166건) · YuE `[verse]` · ACE-Step · SongBloom · LeVo |
| **A′. 길이가 정의된 구조 토큰** | 토큰 자체에 **기대 길이가 문서화** | 안 불림 | **SongBloom**: `[intro]`·`[outro]`·`[inst]` 하나가 150초 모델에서 **약 1초**, 240초 모델에서 **약 5초**(E1) · **LeVo**: `[intro-short]`/`[intro-medium]`/`[inst-short]`/`[inst-medium]`처럼 **길이를 태그 이름에 넣음**(E1) |
| **B. 라벨과 지시의 분리** | `[ ]`=섹션 라벨, `{ }`=연주 지시 | `{}`안 안 불림 | **Eleven Music**: `[Verse 1]` + `{guitar solo}` + `(hmmm)` 3층(E1) |
| **C. 공인된 지시 태그** | 공식이 'guidance tag'라 부름 | 확률적 | **Udio**: `[Scream]`·`[Guitar Solo]`·`[Announcer]`. 공식 헬프가 **「hard-coded command가 아니고 adherence가 확률적」**이라 명시(E2) |
| **D. 시간 좌표** | 대괄호가 초 단위 위치 | 해당없음 | **DiffRhythm** `[00:10.00]가사` · **Lyria 3** `[0:00 - 0:10] Intro:` |
| **E. 음소 힌트** | 발음 지정 | 안 불림 | **OpenUtau** `read[r iy d]`(E1) |
| **F. ★그냥 불림** | 지시로 안 읽힘 | **불림** | **MiniMax Music 3.0** — 곡 중간 긴 브라켓 2건 bigram recall 0.92·1.00, 합 24.5초=트랙의 13.9%. **M4** · 출처 leomusic3 08-29 통제쌍 n=1 |

★**F가 존재한다는 것만으로 「음악 LLM은 대괄호를 지시로 읽는다」는 일반화가 깨진다.** 다만 A~E는 전부 **문서층(E)**이고 F만 **렌더층(M4)**이다 — 층이 달라서 정면 비교가 아니다. 이 비대칭을 Phase 2 통제쌍이 메꿔야 한다.

## §5. 사전등록 채점 (헌장 §6, 조사 전 기재분)

| 예측 | 판정 | 근거 |
|---|---|---|
| **P1** 대부분 엔진은 가사 칸이 프롬프트와 분리 | **지지** | 사용자 가사로 노래를 만드는 상용 10종 중 **9종이 분리**. 유일한 단일칸이 Lyria 3 |
| **P2** 구조 태그 문법을 공식 공표한 엔진은 소수 | ⛔**기각** | 구조 태그를 가진 9엔진 중 **6종(66.7%)이 공식 목록·예시를 공표**(Lyria3·MiniMax·YuE·SongBloom·LeVo·Udio). ★**공표 안 하는 쪽이 소수파다** |
| **P3** 「대괄호 안은 안 불린다」는 엔진 조건부 | **판정 유보** | §4대로 의미론이 6갈래로 갈렸다. 「조건부/일반」의 이분법 자체가 틀린 질문이었다 |
| **P4** Suno에 없는 통제면 최소 3종 | **지지(초과)** | §2에 **12종** |

★**P2 기각의 파장**: 우리 대장 D008·D026·D036은 「Suno는 공식 문법을 공표하지 않는다」류다. 이 조사는 그 주장을 **반박하지 않는다**(Suno가 공표 안 하는 건 그대로다). 대신 **「업계가 원래 안 한다」는 암묵 전제를 깬다** — Suno의 미공표는 관행이 아니라 **선택**이다.
★**P3의 자기 정정**: 예측 문장을 잘못 세웠다. 「조건부인가 일반인가」는 대괄호가 한 가지 문법일 때만 성립하는 질문인데, 실제로는 6종이었다. 예측은 고치지 않고 **틀린 채로 남긴다**(헌장 §6).

## §6. 자료 한계 — 먼저 밝힌다

1. **전건 문서층.** 「문서에 있다」는 「그렇게 동작한다」가 아니다. §2의 12종 중 우리가 렌더로 확인한 건 **0종**이다.
2. **외부 검색자 1종.** 이번 라운드는 `codex exec` 단독이다. ~~gemini CLI 미인증으로 독립 교차검증자가 없었다~~ ⇒ ⛔**09-04 정정**: 원인 기재가 틀렸다 — 구글 CLI는 **`agy`(antigravity-cli)**로 교체됐고 인증도 살아 있다(`agy --print`→PONG·rc=0). **없어서 못 부른 게 아니라 내가 안 불렀다.** 세션이 직접 원문 도달해 재확인한 건 Eleven·Lyria RealTime·Lyria 3·MiniMax·Udio **5건뿐**이고 나머지는 미검증이다.
3. **`?` 칸이 많다.** §1 표의 물음표는 「없다」가 아니라 **「문서에서 못 찾았다」**다. 부재로 읽으면 안 된다.
4. **Suno 행은 우리 실측이 아니라 우리 관행 요약**이다. Suno는 공식 API 문서가 없어 같은 자로 못 잰다 — 그 비대칭이 이 표의 구조적 결함이다.
