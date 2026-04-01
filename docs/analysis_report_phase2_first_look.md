# Suno 프롬프트 1차 분석 리포트

**날짜**: 2026-04-02
**분석 대상**: Phase 2H 찬송가 30곡 + Phase 2A 스템 4곡 (10스템)
**분석자**: reklcli (sunolanguage)

---

## 1. 데이터 개요

| 소스 | 곡수 | 비고 |
|------|------|------|
| Phase 2H 찬송가 | 30곡 (31곡 중 #27 빈값) | 전체곡 업로드, 저작권 차단 0건 |
| Phase 2A 스템 | 4곡 × 2~3스템 = 10스템 | Clair de Lune, Bumblebee, Schindler's List, Take Five |

- SP 잘림 이슈 발견 → 피드 API가 원인 → 클립 API로 재수집 완료 (tags 평균 100자→600~700자)
- suno_tags (SP) + suno_sp (Inline Cues + 가사) 2개 레이어 수집

---

## 2. Suno의 tags(SP) 서술 구조

찬송가 30곡의 tags를 전수 확인한 결과, Suno는 일관된 서술 템플릿을 따름:

**서술 순서:**
1. 장르/스타일 선언 — `Traditional Christian hymn`, `Contemporary Christian choral anthem`
2. 편성 + 역할 — `for SATB choir and pipe organ`, `with orchestral accompaniment`
3. 악기별 상세 — `grand piano playing block chords and arpeggiated patterns in a supportive role`
4. 박자/BPM/키 — `4/4 time at 72 BPM in the key of G Major`
5. 보컬/연주 특성 — `formal and operatic with clear diction and controlled vibrato`
6. 녹음 환경 — `natural cathedral-like acoustic with significant hall reverb`
7. 다이나믹스/구조 — `dynamics swell from mezzo-forte to forte during the final cadence`

이 순서가 거의 모든 곡에서 반복됨.

---

## 3. 악기 표현 — 3층 구조

Suno는 악기를 3개 층위로 묘사:

### Layer 1: 악기명 (What)
- `grand piano`, `pipe organ`, `SATB choir`, `string section`, `flute`, `oboe`, `timpani`, `glockenspiel`

### Layer 2: 역할 (Function)
- `in a supportive role`, `provides harmonic support`, `melodic counterpoint`
- `provides a rhythmic pulse`, `melodic interludes`, `accentuating the downbeats`

### Layer 3: 음색/주법 (How)
- 피아노: `arpeggiated chords`, `block chords`, `flowing eighth-note patterns`, `bright concert hall timbre`
- 오르간: `full registration`, `principal and reed stops`, `prominent pedal notes`, `bright registrations`
- 합창: `homophonic harmony`, `four-part harmony`, `unison passages`, `classical vibrato`
- 현악: `legato violins`, `staccato violins`, `sustained harmonic support`
- 드럼: `crisp, high-tuned snare`, `punchy kick drum`, `dry hi-hats`, `rapid double-stroke rolls`

### 편성 지정 구문 패턴
- `for + [편성]` — `for SATB choir and pipe organ`
- `featuring + [편성]` — `featuring a mixed SATB choir and grand piano`
- `with + [편성]` — `with orchestral accompaniment`

---

## 4. 무드/캐릭터 표현 — 우리 예측과의 차이

### Suno가 쓴 무드 관련 표현 (찬송가 30곡에서 추출)
- `majestic and processional character`
- `reverent`
- `stately tempo`
- `formal and liturgical`
- `spacious, liturgical quality`
- `bright, resonant choral tone`

### Phase 1 우리 예측 (mood_keywords)
- `hypnotic`, `mesmerizing`, `ritualistic`, `monumental`, `jubilant`, `cosmic`, `heroic`, `frantic`, `buzzing`...

### 차이의 본질
- **Suno**: "이 음악이 어떻게 연주/녹음되는지" 묘사 (제작 사양에 가까움)
- **우리 예측**: "이 음악을 들으면 어떤 느낌인지" 묘사 (감상 반응)
- Suno에게 무드가 없는 것이 아니라, **악기+공간+다이나믹스 조합으로 무드를 암시**하는 방식
- 같은 범주로 1:1 비교하면 안 됨 — 서로 다른 것을 묘사하고 있음

---

## 5. suno_sp (Inline Cues) 레이어

tags(SP)와 별개로 suno_sp에는 구간별 연주 지시가 포함:

### 구조 태그
- `[Intro]`, `[Verse 1]`, `[Chorus]`, `[Interlude]`, `[Bridge]`, `[Outro]`

### 악기 동작 큐
- `[pipe organ enters with full registration]`
- `[choir transitions to four-part harmony]`
- `[piano arpeggios intensify]`
- `[timpani roll]`, `[cymbal swell]`
- `[drums drop out]`

### 다이나믹스/연출 큐
- `[choir increases in volume, forte]`
- `[slowing tempo, rallentando]`
- `[sustained final chord, natural decay]`
- `[key change to D major]`

### tags vs suno_sp 비교
| | tags (SP) | suno_sp (Inline Cues) |
|--|-----------|----------------------|
| 범위 | 곡 전체 | 구간별 |
| 내용 | 전체 사양서 | 실시간 연주 지시 |
| 어휘 | 겹치지만 용도 다름 | 동작 동사 + 악기 결합 |

---

## 6. 스템 분석 — mismatch의 의미

### Clair de Lune — 같은 곡의 3스템을 Suno가 다르게 인식

| 스템 | Suno 인식 | 원곡과 match? |
|------|----------|--------------|
| drums | Romantic-era nocturne, concert grand piano, rubato | 가까움 |
| bass | Contemporary worship ballad, electric guitar, male vocal, 영어 가사 생성 | 완전히 다름 |
| other | Contemporary classical, concert grand piano, rubato | 가까움 |

### Schindler's List — 3스템 전부 mismatch

| 스템 | Suno 인식 |
|------|----------|
| drums | Indie folk, acoustic guitar fingerstyle, breathy male vocals |
| bass | Ambient drone, granular synthesizer, experimental soundscape |
| other | Classical chamber music for violin and piano (원곡에 가까움) |

### 의미
- 스템 분리 시 Suno는 원곡을 인식하지 못하고, **그 소리 조각에서 가장 가까운 음악적 맥락을 추론**
- mismatch도 Suno 어휘 사전에는 유효 — Suno가 특정 음향 패턴을 어떤 언어로 매핑하는지 보여줌
- bass 스템 → worship ballad로 인식: Suno에게 저음역 아르페지오 패턴 = worship 장르와 연결되는 것일 수 있음

---

## 7. 다음 단계 (미확정)

- Suno tags의 서술 구조를 기준으로 어휘를 분류 (장르, 편성, 주법, 음색, BPM/키, 녹음환경, 다이나믹스)
- 찬송가 잔여 ~900곡 + 스템 잔여 ~95곡 수집 계속
- Phase 1 예측과의 비교는 "같은 것을 다르게 말한다"가 아니라 "다른 것을 말하고 있다"는 전제에서 접근
- 방법론 확정 후 진행

---

## 참고
- 데이터 원본: `agent-comm/projects/sunolanguage/messages/reklcli_mukl_sunolanguage_20260402_001000_collected_prompts.json`
- Phase 1 DB: `sunolang.db` tracks 테이블 (100곡)
- SP 잘림 이슈: 피드 API → 클립 API 전환으로 해결 (2026-04-02)
