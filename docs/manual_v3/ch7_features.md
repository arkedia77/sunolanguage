# 7장: Suno의 기능 — 언어 밖의 조작면

> 1~6장이 Suno의 **언어**(어휘·SP 문법·데드존)를 다뤘다면, 이 장은 Suno의 **기능** — 앱에서 실제로 만질 수 있는 조작면이다.
> 출처: sunomusic 실측 정본(`SUNO_CAPABILITIES.md` §S 2026-07-10 단일기준 + 07-22 신기능 실측), 1차 회신 v1(2026-07-31). 판정 태그: [실측]/[부분확인]/[미사용]/[미확인] — 추측 서술 없음.

## 7.1 생성 파라미터 — 곡을 만들 때 만지는 것

### 모델 선택 [실측]

Create 화면 드롭다운에서 6종 선택 가능 (2026-07-07 billing 실측):

| 표기 | 내부명 | 비고 |
|---|---|---|
| v5.5 | chirp-fenix | **default·최신** |
| v5 | chirp-crow | |
| v4.5+ | chirp-bluejay | |
| v4.5-all | chirp-auk-turbo | 무료. mashup/sample/remix capability 보유 |
| v4.5 | chirp-auk | |
| v4 | chirp-v4 | |

리마스터 전용 모델 3종이 별도 존재하나 전부 `can_use:false`(실행 불가). **07-07 이후 신모델 없음** — 이후 변화는 전부 워크플로/UI다.

### Style(SP) 필드 [실측]

- **UI 한도 1000자.** 초과 시 잘리지만 곡 생성 자체는 됨 — 우리 "SP 1000자 + 글자수 확인" 규칙의 실측 근거.
- ★**SP는 저작권 필터 무관** — 지역·민족명 등이 차단되는 것은 가사/제목 필드뿐. SP에는 걸리지 않는다.
- 폼 상태가 곡 간 persist됨(라디오그룹·소스 잔류) — 연속 생성 시 이전 설정 확인 필요.

### Lyrics 필드 [실측, 2026-07-09 개편]

- textarea → **contenteditable DIV(Lexical 에디터)** 전환. Lyricist(AI 작사 어시스턴트)·전체화면 에디터·장르 제안칩 동반 신설.
- **송폼([Verse]·[Chorus] 등)은 가사 안에서 정의** — SP와 무관 (2장 채널 분리와 일치).

### Instrumental 토글 [실측]

토글 ON = lyrics칸 소멸 → **브라켓 송폼과 상호배타**. 무가사 2방식(6장·CS01 선례): ①순수 무가사=토글 ON+빈 가사 ②무가사+구조 제어=토글 **OFF**+브라켓만 lyrics에.

### Vocal Gender [실측]

Write 모드 More Options에 `[Male|Female]` 토글 등장. 단 **소프트큐 드리프트 선례 있음** — 토글+SP 하드 명시를 병행하는 것이 실운영 관행이다. 그래도 못 잡는 경우가 5장 4층(프라이어 종속): 가사 정서·에너지가 만드는 프라이어는 토글로도 못 뚫는다.

→ 화자·듀엣 지시의 표기 문법과 실패 기전(코퍼스 편중 4.3:1·명찰형 데드존)은 **`docs/duet_bracket_grammar_v1.md` 정본** 참조. 위 `Exclude styles`가 이 붕괴의 파라미터층 대응 후보이나 **성별 A/B 미실시**.

### Duration 슬라이더 [실측 2026-07-23, 24클립]

07-20 신설. More Options → `Duration [Custom|Auto]` → 범위 **10~360초**, 기본 180초.

★핵심 실측 모델: **실측 길이 = min/max(슬라이더 타깃, 채울 수 있는 소재량)**
- 무가사 ≤3분: 거의 정확한 하드컷(−1~3초). 4분 초과는 못 늘림(Extend 필요).
- 보컬 곡: 슬라이더가 실제 길이 다이얼로 작동하되 **가사량이 목표 길이만큼 있어야** 한다. 6줄 가사에 180초를 걸어도 30~41초에서 끝난다 — 빈약한 가사를 패딩하지 않는다.

이것도 구조적으로 5장 4층과 같다: **파라미터(표기)가 소재(프라이어)를 이기지 못한다.** 길이를 원하면 슬라이더가 아니라 가사량을 설계하라.

### 나머지

- **Weirdness / Style Influence 슬라이더** [실측 2026-08-03, 10클립] — 둘 다 `aria-label`·0~100·기본 50, More Options 내. 세팅은 JS focus + CDP ArrowRight/Left(스텝 1) — **Home/End 무효**로 Duration 슬라이더와 동일 조작 규약. Weirdness 0/25/50/75/100 스윕(Style Influence 50 고정) 5점×2클립 전건 확보. **어휘 델타(귀측) 판정은 미실시.**
- **Persona** [실측] — persona_id 지정, 5개 페르소나 운용 중.
- **Exclude styles** [실측 2026-08-03] ★**정정** — 종전 "[미사용]·SP 양성 서술로 제어" 판단을 뒤집는다. 필드는 `INPUT[type=text]`(placeholder `Exclude styles`, More Options)이고, **입력값이 clip metadata `negative_tags`로 전달·저장**된다(`accessible_features`에 활성).
  → ★**5장 negative 데드존의 경계가 좁혀졌다**: 데드존인 것은 **SP 산문 안의 부정 서술**(`no female vocals` 0건 비네이티브)이지, **부정 그 자체가 아니다.** 부정에는 **전용 채널**이 따로 있다.
  A/B 대조 확보(동일 SP `saxophone solo` 명시·동일 가사, exclude만 차등 / OFF 2클립 · ON `saxophone, brass, horn` 2클립, negative_tags 저장 확인). **음향 억제 실효는 귀측 청취 판정 대기.**

## 7.2 생성 후 기능

| 기능 | 동작 | 판정 |
|---|---|---|
| **Extend** | 곡 뒤 이어붙이기. 무가사 4분 초과 확보 경로 | [실측] |
| **Cover** | 오디오 앵커 유지 + SP로 편곡 변경. **v5.0→v5.5 리메이크도 이 경로** | [실측] |
| **Stems 분리** | Advanced Split — 128악기 선택, 20cr/곡. 응답에 분리본+MR(complement) 둘 다 오므로 title로 구분 필수. 레거시 2-stem은 품질 미달로 폐기 | [실측·표준] |
| **MIDI export** | 5악기 note별 | [실측] |
| **곡 분석** | downbeats·waveform·novelty-sections·aligned_lyrics — 무료 | [실측] |
| **가사 인라인 AI** | 가사 선택→Variations/Rhymes/Reference, 크레딧 0. 코퍼스 증량에 활용(V_BATCH1 1,027행) | [실측] |
| **곡 관리** | 공개/비공개·삭제(20개 배치)·플레이리스트 | [실측] |
| **메타 수정** | 제목·태그·표시 프롬프트. 단 **표시 수정일 뿐 재가창 아님**(재가창=infill/cover) | [실측] |
| **Replace section(infill)** | 구간 교체 (Studio) | [미확인, 실전 미사용] |
| **Remaster** | 3개 모델(chirp-flounder v5.5 / carp v5 / bass v4.5+) 전부 `can_use:false`. ★사유 확정: `free_remasters_remaining=0` — **티어 조건이 아니라 카운트 조건**(Premier도 무료분 소진 시 불가). 규명 종결 | [실측·종결] |
| **비디오** | `POST /api/video/generate/{clip_id}/` →204 → `GET .../status/` processing→complete(~10~20초) → `cdn1.suno.ai/{clip}.mp4`. **기존 곡에 영상 부착**(신규 생성 아님)·크레딧 ≤10 | [실측 08-03] |
| **Mashup/Voices** | 진입점 확인, 실생성 미실행 (Voices는 `free_vox_gens_remaining=0` 관측 — Remaster와 같은 카운트 게이트 가능성) | [부분확인] |

## 7.3 운영 제약

- **2-take 관행의 근거**: 곡당 dual 클립 생성이 **기본 거동**이다 — 우리 배치의 "곡별 2take"는 옵션이 아니라 앱의 기본값.
- **크레딧**: 수치는 실시간 조회 원칙(하드코딩 금지). Stems Advanced Split 20cr/곡이 대표 비용.
- **산출물 접근**: `cdn1.suno.ai/{uuid}.mp3`(청음 공유 표준 — suno.com 페이지 링크는 `<audio>` 재생 불가). wav 변환 트리거 후 폴링. MP3 ID3 코멘트에 UUID 내장(역매칭 가능).
- **처리 속도**: 곡당 ~130초(렌더 대기 포함), 직렬 처리.
- **알려진 리스크**: 공식 셀프서브 API 부재(비공개 파트너 프로그램만) / WMG 다운로드 캡 예고(07-22까지 미시행 — 다운로드 급감 시 원인 1순위 후보).
- **특수문자 제목 no-submit 의심 = [기각] 2026-08-03** — `ā/ē/ō` 포함 제목(`Tēst Ā Bōa`) 정상 Create·2클립·제목 그대로 저장. K3012 70037의 silent no-submit은 **diacritics 원인이 아니다**(다른 요인·전이적 이슈). 안전 문자셋 = 라틴 확장 diacritics 포함 정상. 이모지·CJK 확장은 미검증.

## 7.4 버전 변화 (v5.0 → v5.5, 기능 관점)

- **신모델 없음** — v5.5(chirp-fenix)가 최신이고, "v5.0 곡의 v5.5 리메이크"는 별도 마이그레이션 기능이 아니라 **Cover 경로**로 수행한다.
- 기능 변화는 전부 UI/워크플로: 07-09 Lyrics 에디터 개편, 07-20 Duration 슬라이더 신설.
- 언어(어휘) 변화는 별개 축 — v5.5 자동 pump-up modulation(1장), `key change` 신규 어휘 등은 기존 장 참조.

## 7.5 업로드 → 분석 (코퍼스 수집 경로) — v2 보류분

sunomusic v2 회신에서 정합 대조 예정. 현재 우리 측 기보유 실측만 요약:
- 재분석 파이프라인: **1분 컷 → Suno 앱 업로드 → 분석 프롬프트 수집**(4값 세트).
- **저작권 차단**: 유명 원곡은 사전 차단. ★자기 생성곡 재업로드도 content-ID 유사배치로 차단됨 — 원본데이터 판정으로 우회.

## 7.6 기능과 언어의 경계 — 이 장의 위치

기능은 언어를 대체하지 않는다. 실측이 반복해서 보여주는 패턴은 하나다:

> **토글·슬라이더(기능)는 표기층이고, 곡의 실체는 소재(가사량·정서·에너지)가 결정한다.**

- Duration 슬라이더는 가사량을 못 이긴다 (7.1)
- Vocal Gender 토글은 가사 정서의 프라이어를 못 이긴다 (7.1 ↔ 5장 4층)
- Exclude 필드보다 SP 양성 서술이 실운영 표준이다 (7.1 ↔ 5장 negative 데드존)

기능 장이 마지막에 오는 이유가 이것이다 — 조작면을 아무리 잘 다뤄도, 결과를 결정하는 것은 1~6장의 언어 설계다.
