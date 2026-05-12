# v5.5 Pump-Up Modulation 정밀 테스트 프로토콜

**시리즈**: S_PU (Pump-Up)
**설계일**: 2026-05-12
**목적**: v5.5 자동 pump-up modulation의 장르별 발생 빈도 · 네거티브 억제 · 명시 강화 효과 정량 측정

---

## 1. 배경

v5.5에서 마지막 코러스의 pump-up modulation(반음/온음 올림 전조)이 SP 지시 없이 자동 생성되는 현상 발견 (2026-05-09, Leo 실청취 확인).

- **확인**: K-Ballad, K-Rock (여러 곡에서 반복 관찰)
- **미확인**: K-Trot, K-Pop Dance, Western Pop, Jazz 등
- **DB 근거**: `key change` 키워드 = S018_16(Trance, v5.5) 1건만. W1(v5.0) 0건 → v5.5 신규 행동

## 2. 가설

| 코드 | 가설 | 검증 기준 |
|------|------|-----------|
| H1 | **문화 가설** — 자동 pump-up은 K-음악 학습량 증가에 기인. K-장르에서 빈도 높고, 서양 장르에서 낮음 | K-장르 Baseline > 서양 장르 Baseline |
| H2 | **네거티브 유효성** — "no key change" 지시가 자동 pump-up을 억제함 | Negative < Baseline (모든 장르) |
| H3 | **명시 강화** — 명시적 pump-up 지시가 빈도를 높임 | Explicit > Baseline (모든 장르) |

## 3. 실험 설계

### 독립변수
1. **장르** (6종): K-Ballad, K-Rock, K-Trot, K-Pop Dance, Western Pop Ballad, Jazz Ballad
2. **전조 지시** (3조건): Baseline / Negative / Explicit

### 종속변수
- 최종 코러스 pump-up 발생 여부 (이진: 0=없음, 1=발생)

### 반복
- 각 SP당 **3회 생성** (v5.5 출력 분산 고려)
- 18 SP × 3회 = **54곡**

### 장르 선정 근거

| # | 장르 | 문화권 | 선정 이유 |
|---|------|--------|-----------|
| 1 | K-Ballad | 한국 | 이미 pump-up 확인. 양성 대조군 |
| 2 | K-Rock | 한국 | 이미 pump-up 확인. 양성 대조군 |
| 3 | K-Trot | 한국 | 한국 트로트 pump-up은 필수 클리셰 |
| 4 | K-Pop Dance | 한국 | K-Pop 댄스에서도 pump-up 빈번 |
| 5 | Western Pop Ballad | 서양 | 서양 팝 발라드에서는 pump-up 드묾 → 문화 가설 핵심 |
| 6 | Jazz Ballad | 서양 | 재즈에서 pump-up은 관습 외 → 음성 대조군 |

### 조건별 SP 차이 (마지막 1문장만 상이)

| 조건 | 코드 | 추가 문장 |
|------|------|-----------|
| Baseline | A | (없음) |
| Negative | B | `No key change. The song maintains the same key throughout.` |
| Explicit | C | `A key change occurs in the final chorus, modulating up a half step.` |

---

## 4. SP 세트 (18개)

### 4.1 K-Ballad (PU_01 ~ PU_03)

**PU_01 — K-Ballad Baseline (A)**
```
K-Pop ballad featuring a male tenor vocal. A grand piano plays arpeggiated chords with sustain pedal, creating a warm, intimate foundation. Clean electric guitar adds gentle fills with light chorus and delay. Electric bass follows the kick drum pattern with a warm, rounded tone. The drums maintain a steady beat with brushed snare and soft kick. The male tenor vocal delivers with a breathy, emotional quality. The arrangement is sparse, focusing on the interplay between the piano and the vocal melody. 72 BPM in E Major, 4/4 time signature.
```

**PU_02 — K-Ballad Negative (B)**
```
K-Pop ballad featuring a male tenor vocal. A grand piano plays arpeggiated chords with sustain pedal, creating a warm, intimate foundation. Clean electric guitar adds gentle fills with light chorus and delay. Electric bass follows the kick drum pattern with a warm, rounded tone. The drums maintain a steady beat with brushed snare and soft kick. The male tenor vocal delivers with a breathy, emotional quality. The arrangement is sparse, focusing on the interplay between the piano and the vocal melody. 72 BPM in E Major, 4/4 time signature. No key change. The song maintains the same key throughout.
```

**PU_03 — K-Ballad Explicit (C)**
```
K-Pop ballad featuring a male tenor vocal. A grand piano plays arpeggiated chords with sustain pedal, creating a warm, intimate foundation. Clean electric guitar adds gentle fills with light chorus and delay. Electric bass follows the kick drum pattern with a warm, rounded tone. The drums maintain a steady beat with brushed snare and soft kick. The male tenor vocal delivers with a breathy, emotional quality. The arrangement is sparse, focusing on the interplay between the piano and the vocal melody. 72 BPM in E Major, 4/4 time signature. A key change occurs in the final chorus, modulating up a half step.
```

---

### 4.2 K-Rock (PU_04 ~ PU_06)

**PU_04 — K-Rock Baseline (A)**
```
K-Rock with driving energy and power chord progressions. Distorted electric guitar plays aggressive palm-muted riffs. A second electric guitar adds melodic lead lines with delay and reverb. Bass guitar follows the kick drum pattern with a thick, overdriven tone. The drums feature a driving beat with double kick and crash cymbals on downbeats. The male tenor vocal is powerful with slight grit. The arrangement builds from restrained verses to full-band chorus intensity. 138 BPM in A Minor, 4/4 time signature.
```

**PU_05 — K-Rock Negative (B)**
```
K-Rock with driving energy and power chord progressions. Distorted electric guitar plays aggressive palm-muted riffs. A second electric guitar adds melodic lead lines with delay and reverb. Bass guitar follows the kick drum pattern with a thick, overdriven tone. The drums feature a driving beat with double kick and crash cymbals on downbeats. The male tenor vocal is powerful with slight grit. The arrangement builds from restrained verses to full-band chorus intensity. 138 BPM in A Minor, 4/4 time signature. No key change. The song maintains the same key throughout.
```

**PU_06 — K-Rock Explicit (C)**
```
K-Rock with driving energy and power chord progressions. Distorted electric guitar plays aggressive palm-muted riffs. A second electric guitar adds melodic lead lines with delay and reverb. Bass guitar follows the kick drum pattern with a thick, overdriven tone. The drums feature a driving beat with double kick and crash cymbals on downbeats. The male tenor vocal is powerful with slight grit. The arrangement builds from restrained verses to full-band chorus intensity. 138 BPM in A Minor, 4/4 time signature. A key change occurs in the final chorus, modulating up a half step.
```

---

### 4.3 K-Trot (PU_07 ~ PU_09)

**PU_07 — K-Trot Baseline (A)**
```
K-Pop and disco fusion featuring a male baritone vocal. Accordion plays steady rhythmic staccato chords. Saxophone provides melodic fills between vocal phrases. Electric bass plays a disco-style pattern with bright, punchy tone. Clean electric guitar adds rhythmic strumming with light chorus. The drums feature a four-on-the-floor kick with open hi-hat on upbeats. The male baritone vocal delivers with vibrato and emotional projection. The arrangement is lush with full band instrumentation. 118 BPM in G Major, 4/4 time signature.
```

**PU_08 — K-Trot Negative (B)**
```
K-Pop and disco fusion featuring a male baritone vocal. Accordion plays steady rhythmic staccato chords. Saxophone provides melodic fills between vocal phrases. Electric bass plays a disco-style pattern with bright, punchy tone. Clean electric guitar adds rhythmic strumming with light chorus. The drums feature a four-on-the-floor kick with open hi-hat on upbeats. The male baritone vocal delivers with vibrato and emotional projection. The arrangement is lush with full band instrumentation. 118 BPM in G Major, 4/4 time signature. No key change. The song maintains the same key throughout.
```

**PU_09 — K-Trot Explicit (C)**
```
K-Pop and disco fusion featuring a male baritone vocal. Accordion plays steady rhythmic staccato chords. Saxophone provides melodic fills between vocal phrases. Electric bass plays a disco-style pattern with bright, punchy tone. Clean electric guitar adds rhythmic strumming with light chorus. The drums feature a four-on-the-floor kick with open hi-hat on upbeats. The male baritone vocal delivers with vibrato and emotional projection. The arrangement is lush with full band instrumentation. 118 BPM in G Major, 4/4 time signature. A key change occurs in the final chorus, modulating up a half step.
```

---

### 4.4 K-Pop Dance (PU_10 ~ PU_12)

**PU_10 — K-Pop Dance Baseline (A)**
```
K-Pop dance track with energetic synth production. A bright, arpeggiated synthesizer drives the melody. Sub-bass synth follows the kick pattern with deep, punchy tone. The drums feature punchy electronic kick, crisp snare, and rapid hi-hat patterns. The female vocal is bright with clean delivery. Background vocals provide stacked harmonies in the chorus. The arrangement alternates between sparse verses and dense, layered choruses with synth pad swells. 128 BPM in C Minor, 4/4 time signature.
```

**PU_11 — K-Pop Dance Negative (B)**
```
K-Pop dance track with energetic synth production. A bright, arpeggiated synthesizer drives the melody. Sub-bass synth follows the kick pattern with deep, punchy tone. The drums feature punchy electronic kick, crisp snare, and rapid hi-hat patterns. The female vocal is bright with clean delivery. Background vocals provide stacked harmonies in the chorus. The arrangement alternates between sparse verses and dense, layered choruses with synth pad swells. 128 BPM in C Minor, 4/4 time signature. No key change. The song maintains the same key throughout.
```

**PU_12 — K-Pop Dance Explicit (C)**
```
K-Pop dance track with energetic synth production. A bright, arpeggiated synthesizer drives the melody. Sub-bass synth follows the kick pattern with deep, punchy tone. The drums feature punchy electronic kick, crisp snare, and rapid hi-hat patterns. The female vocal is bright with clean delivery. Background vocals provide stacked harmonies in the chorus. The arrangement alternates between sparse verses and dense, layered choruses with synth pad swells. 128 BPM in C Minor, 4/4 time signature. A key change occurs in the final chorus, modulating up a half step.
```

---

### 4.5 Western Pop Ballad (PU_13 ~ PU_15)

**PU_13 — Western Pop Ballad Baseline (A)**
```
Pop ballad with piano and vocal focus. A grand piano plays sustained chords with gentle arpeggiated fills. Fingerpicked acoustic guitar provides a steady pattern. Electric bass enters in the chorus with a warm, clean tone. The drums are minimal with soft kick and brushed snare in verses, building to full kit in the chorus. The female vocal is clear and controlled with a slight breathy quality. Strings swell in the final section. The arrangement is intimate and builds gradually. 75 BPM in D Major, 4/4 time signature.
```

**PU_14 — Western Pop Ballad Negative (B)**
```
Pop ballad with piano and vocal focus. A grand piano plays sustained chords with gentle arpeggiated fills. Fingerpicked acoustic guitar provides a steady pattern. Electric bass enters in the chorus with a warm, clean tone. The drums are minimal with soft kick and brushed snare in verses, building to full kit in the chorus. The female vocal is clear and controlled with a slight breathy quality. Strings swell in the final section. The arrangement is intimate and builds gradually. 75 BPM in D Major, 4/4 time signature. No key change. The song maintains the same key throughout.
```

**PU_15 — Western Pop Ballad Explicit (C)**
```
Pop ballad with piano and vocal focus. A grand piano plays sustained chords with gentle arpeggiated fills. Fingerpicked acoustic guitar provides a steady pattern. Electric bass enters in the chorus with a warm, clean tone. The drums are minimal with soft kick and brushed snare in verses, building to full kit in the chorus. The female vocal is clear and controlled with a slight breathy quality. Strings swell in the final section. The arrangement is intimate and builds gradually. 75 BPM in D Major, 4/4 time signature. A key change occurs in the final chorus, modulating up a half step.
```

---

### 4.6 Jazz Ballad (PU_16 ~ PU_18)

**PU_16 — Jazz Ballad Baseline (A)**
```
Jazz ballad with intimate club atmosphere. Upright bass plays walking lines with warm, woody tone. Piano provides sparse jazz voicings with sustained chords and gentle melodic fills. Muted trumpet plays soft, lyrical phrases with plate reverb. The drums use brushes on snare with ride cymbal and gentle kick. The male baritone vocal is smooth and relaxed with natural vibrato. The arrangement is spacious, leaving room between instruments. 65 BPM in Bb Major, 4/4 time signature.
```

**PU_17 — Jazz Ballad Negative (B)**
```
Jazz ballad with intimate club atmosphere. Upright bass plays walking lines with warm, woody tone. Piano provides sparse jazz voicings with sustained chords and gentle melodic fills. Muted trumpet plays soft, lyrical phrases with plate reverb. The drums use brushes on snare with ride cymbal and gentle kick. The male baritone vocal is smooth and relaxed with natural vibrato. The arrangement is spacious, leaving room between instruments. 65 BPM in Bb Major, 4/4 time signature. No key change. The song maintains the same key throughout.
```

**PU_18 — Jazz Ballad Explicit (C)**
```
Jazz ballad with intimate club atmosphere. Upright bass plays walking lines with warm, woody tone. Piano provides sparse jazz voicings with sustained chords and gentle melodic fills. Muted trumpet plays soft, lyrical phrases with plate reverb. The drums use brushes on snare with ride cymbal and gentle kick. The male baritone vocal is smooth and relaxed with natural vibrato. The arrangement is spacious, leaving room between instruments. 65 BPM in Bb Major, 4/4 time signature. A key change occurs in the final chorus, modulating up a half step.
```

---

## 5. 가사

### 규칙
- 동일 장르 3조건은 **동일 가사** 사용 (SP만 변수)
- 반드시 **3개 코러스** 포함 (마지막 코러스에서 pump-up 여부 측정)
- Suno 자동 생성 허용 — 단, 섹션 태그 [Verse], [Chorus], [Bridge] 포함

### Korean 가사 (PU_01~PU_12)
```
[Verse 1]
어둠 속에 홀로 남은 밤
기억 속에 네가 스며들어

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어

[Verse 2]
시간이 멈춘 듯 흘러가고
이 자리에 여전히 남아

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어

[Bridge]
언젠가 다시 만날 수 있을까
그날을 기다리며

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어
```

### English 가사 (PU_13~PU_18)
```
[Verse 1]
Shadows fall across the empty room
Memories of you still linger here

[Chorus]
I'm standing where you left me
Waiting for the dawn

[Verse 2]
The clock has stopped but time keeps moving on
I'm frozen in this moment still

[Chorus]
I'm standing where you left me
Waiting for the dawn

[Bridge]
Maybe someday we'll find our way back home
Until then I'll hold on

[Chorus]
I'm standing where you left me
Waiting for the dawn
```

---

## 6. 평가 방법

### 6.1 주관 평가 (Leo 청취)
각 곡의 마지막 코러스를 앞 코러스와 비교 청취하여 pump-up 발생 여부를 판정.

| 코드 | 판정 | 기준 |
|------|------|------|
| 0 | 없음 | 같은 조성 유지 |
| 1 | 있음 | 반음 이상 올림 전조 확인 |
| ? | 불확실 | 미세한 변화, 판단 보류 |

### 6.2 객관 평가 (Suno 재분석)
생성된 곡을 Suno 앱에 재업로드하여 재분석 SP에서 키워드 검출.

검색어: `key change`, `modulation`, `modulates`, `modulating`, `transpose`

### 6.3 분석 항목

| 분석 | 수식 | 의미 |
|------|------|------|
| 장르별 Baseline 빈도 | count(pump_up=1) / total per genre | 자연 발생률 |
| Negative 억제율 | 1 - (Negative빈도 / Baseline빈도) | 억제 효과 |
| Explicit 강화율 | Explicit빈도 / Baseline빈도 | 강화 효과 |
| 주관-객관 일치율 | agree / total | 재분석 신뢰도 |

---

## 7. 기대 결과

| 장르 | Baseline (A) | Negative (B) | Explicit (C) |
|------|-------------|--------------|--------------|
| K-Ballad | 높음 (>60%) | 낮음 (<30%) | 매우 높음 (>80%) |
| K-Rock | 높음 (>60%) | 낮음 (<30%) | 매우 높음 (>80%) |
| K-Trot | 높음 (>60%) | 낮음 (<30%) | 매우 높음 (>80%) |
| K-Pop Dance | 중간 (30~60%) | 낮음 (<20%) | 높음 (>60%) |
| Western Pop | 낮음 (<30%) | 매우 낮음 (<10%) | 중간 (30~60%) |
| Jazz Ballad | 매우 낮음 (<10%) | 매우 낮음 (<5%) | 낮음 (<30%) |

---

## 8. 발주 요약

| 항목 | 값 |
|------|-----|
| 시리즈 | S_PU |
| SP 수 | 18 |
| 곡당 반복 | 3회 |
| 총 곡수 | 54 |
| 크레딧 (추정) | ~270 (5 × 54) |
| 재분석 | 54곡 전부 |
| 우선순위 | 높음 — v5.5 핵심 행동 규명 |
| 발주처 | sunomusic |
