# 1장: Suno의 분류 체계

> Suno가 음악을 들으면 가장 먼저 하는 일: 장르 라벨을 붙이고, 템포와 조성을 선언한다.

## 1.1 장르 라벨링 — Suno의 첫 문장

Suno 재분석 SP의 첫 문장은 97.2%의 확률로 **장르 선언**이다. 437곡 corpus에서 장르가 SP의 첫 번째 문장 이외의 위치에 등장하는 경우는 2.8%에 불과하다.

```
평균 슬롯 출현 순서:
  Genre        → position 0.0  (97.2% 첫 문장)
  Instrument   → position 1.4
  Mood/Effect  → position 2.9
  Vocal        → position 3.7
  Tempo/Key    → position 4.8
```

이 순서는 Suno의 "묘사 문법"에서 가장 안정적인 규칙이다. Genre가 먼저 나오고, 악기 편성이 따르고, 분위기와 효과가 중간에 위치하며, 보컬 묘사가 뒤쪽에, 템포/조성 선언이 마지막에 온다.

## 1.2 장르 표현의 규모와 구조

| 지표 | 수치 |
|------|------|
| 분석 corpus | 437곡 (W1 378 + S시리즈 59) |
| 고유 장르 표현 | 216개 |
| DB 385행 기준 고유 장르 | 214개 (W1 162 + S시리즈 52) |

Suno의 장르 라벨은 단일 키워드가 아니라 **복합 구문**이다. 평균 5~8단어 길이의 문장형 라벨이 대부분이다.

### 장르 라벨의 구문 유형

**Type A: 단순 장르명** (전체의 약 15%)
- `K-Pop ballad`
- `Gypsy Jazz`
- `Acid House`
- `UK Drill`

**Type B: 장르 + 영향/융합** (전체의 약 45%)
- `K-Pop ballad with R&B influences`
- `Smooth jazz fusion with bossa nova influences`
- `K-Pop and Synth-pop fusion featuring male vocals`

**Type C: 장르 + 기술적 수식** (전체의 약 30%)
- `K-Pop ballad featuring a baritone male vocal`
- `Lo-fi hip hop track at 85 BPM in G minor`
- `Uplifting Trance at 138 BPM in F Major`

**Type D: 풀 문장형 묘사** (전체의 약 10%)
- `Classical orchestral piece with a focus on string ensemble and woodwinds`
- `Bluegrass and country instrumental with vocal cues`
- `Progressive Trance with heavy J-Pop and Eurobeat influences`

Type B와 C가 가장 흔하며, Suno는 순수 장르명보다 영향 관계나 보컬 특성을 장르 라벨에 포함시키는 것을 선호한다.

## 1.3 대장르 분포

DB 385행(W1 326 + S시리즈 59)을 키워드 기반으로 대장르 분류한 결과:

### K-계열 (W1 중심, 85%)

| 대장르 | 행수 | 비율 | 주요 소스 |
|--------|------|------|-----------|
| K-Ballad | 162 | 42.1% | W1 |
| K-Indie | 40 | 10.4% | W1 |
| K-Pop (기타) | 27 | 7.0% | W1+S016 |
| K-Funk Pop | 26 | 6.8% | W1 |
| K-Rock | 25 | 6.5% | W1 |
| K-Hip Hop | 19 | 4.9% | W1 |
| K-R&B | 12 | 3.1% | W1 |
| K-City Pop | 11 | 2.9% | W1 |

W1은 한국 음악 원곡을 Suno에 녹음한 재분석 데이터다. Suno는 한국 음악을 `K-` 접두어로 분류하며, 하위 장르를 세밀하게 구분한다. 특히 `K-Pop ballad`라는 라벨이 가장 빈번(42.1%)하며, 같은 한국 발라드도 `K-Indie folk ballad`, `K-Pop R&B ballad`, `K-Pop acoustic ballad` 등으로 세분화된다.

### 비K-계열 (S시리즈 중심)

| 대장르 | 행수 | 주요 소스 |
|--------|------|-----------|
| Bossa Nova | 12 | S003/S016/S017/S018 |
| Classical/Orchestral | 10 | S003/S004/S016 |
| Jazz | 9 | 다수 S시리즈 |
| Electronic | 6 | S004/S018 |
| Folk/World | 5 | S004/S018 |
| Rock | 5 | S004/W1 |
| Lo-fi | 3 | S004/S017 |

S시리즈는 의도적으로 다양한 장르를 테스트한 데이터로, 52개 고유 장르 / 59행(거의 모든 곡이 다른 장르)이다.

## 1.4 K-접두어 시스템

Suno가 한국 음악에 부여하는 `K-` 접두어는 단순 지역 태그가 아니라 **별도의 장르 분류 체계**이다.

| K-접두어 | 빈도 | 서양 대응 장르 |
|----------|------|---------------|
| K-Pop | 246/326 (75.5%) | Pop 전반 |
| K-Indie | 60 (18.4%) | Indie Pop/Folk |
| K-Rock | 7 (2.1%) | Rock/Punk |
| K-Hip Hop | 4 (1.2%) | Hip Hop |
| K-R&B | 12 (3.7%) | R&B/Soul |
| K-Ballad | 3 (0.9%) | Ballad |

`K-Pop`이 압도적이며, 원곡이 힙합이든 트로트든 Suno는 상당수를 K-Pop 계열로 분류한다. 이는 Suno의 한국 음악 인식이 K-Pop 중심으로 편향되어 있음을 보여준다.

## 1.5 장르 라벨의 부속 요소

### 템포 선언

Suno는 정확한 BPM을 SP에 명시한다. `at {BPM} BPM` 또는 `Tempo is {BPM}` 형식이 표준이며, `key of {조성}` 패턴이 652회 출현한다.

```
빈도 상위 BPM:
  120 BPM — 가장 빈번한 기본값
  100, 130, 140 — 장르에 따라 분포
  174 BPM — DnB 전용
  138 BPM — Trance 전용
```

### 조성 선언

`key of X` 패턴은 652회 출현하지만, 구체적 코드명(Am7, Cmaj7)은 **0건**, 코드 진행 표기(I-IV-V)도 **0건**이다. Suno의 화성 인식은 조성(key) 수준에서 멈춘다.

### 박자 선언

`{N}/{N} time` 형식으로 박자를 명시한다. 4/4가 압도적이며, 3/4(왈츠), 6/8(셀틱/바로크) 등이 장르별로 고정적이다.

## 1.6 장르와 어휘의 상관관계

DB 교차분석에서 발견된 장르별 고유 어휘 패턴:

### 장르가 어휘를 결정한다

같은 악기라도 장르에 따라 Suno의 묘사가 달라진다:

| 장르 | 기타 묘사 | 베이스 묘사 | 드럼 묘사 |
|------|----------|-----------|----------|
| K-Ballad | fingerstyle, arpeggiated, light chorus | sub-bass synth, low-end warmth | soft kick, brushed |
| K-Funk | palm-muted scratches, staccato | slap bass, sixteenth-note | tight, crisp snare |
| K-Rock | power chords, overdrive | follows kick drum | eighth-note, high-energy |
| Bossa Nova | nylon-string, comping | walking upright bass | brushes, woodblock |
| Jazz | chromatic runs, la pompe | walking, double bass | swing, call-and-response |
| Electronic | — | reese bass, sub-bass | four-on-the-floor, breakbeat |

### K-Ballad의 어휘 세계

K-Ballad(162행)에서 가장 자주 등장하는 어휘:

```
breathy(125), soft(107), intimate(87), reverb(121),
light(119), subtle(110), warm(92), acoustic(144),
counterpoint(15), jazz-influenced(19), rounded(10)
```

K-Ballad의 어휘는 부드러움(soft/breathy/intimate)과 공간감(reverb/light/subtle) 중심이다. 주목할 점은 `counterpoint`(15회)와 `jazz-influenced`(19회)가 발라드에서 빈번하게 등장한다는 것이다 — Suno는 한국 발라드의 편곡을 대위법적이고 재즈 영향을 받은 것으로 인식한다.

### 장르별 배타적 어휘

특정 장르에서만 등장하는 어휘:

| 어휘 | 배타적 장르 | 빈도 |
|------|-----------|------|
| la pompe | Gypsy Jazz | 5 |
| dembow | Reggaeton | 1 |
| reese bass | DnB | 1 |
| bodhrán | Celtic Folk | 2 |
| log drum | Amapiano/Afrobeats | 5 |
| Scruggs-style | Bluegrass | 1 |
| guiro | Cumbia | 1 |
| TR-909 | Acid House | 1 |
| supersaw | Trance | 2 |
| four-on-the-floor | Electronic 전반 | 3 |

이 어휘들은 해당 장르를 식별하는 핵심 마커이며, 다른 장르에서는 거의 나타나지 않는다.

## 1.7 Suno의 장르 인식 편향

### 관찰된 편향

1. **K-Pop 흡수**: 원곡이 트로트, 인디 포크, 힙합이어도 Suno는 상당수를 K-Pop으로 분류
2. **Ballad 과대 대표**: W1의 50%가 Ballad 태그를 포함 — 한국 음악 = 발라드라는 Suno의 편향
3. **Bebop → Bossa Nova 드리프트**: S018에서 Bebop으로 의도한 곡을 Suno가 "Bossa Nova jazz"로 재분류 — 재즈 하위 장르 구분 약함
4. **Afrobeats → Amapiano 혼동**: S018에서 Afrobeats로 의도한 곡을 "Amapiano"로 분류 — 아프리카 장르 구분 불명확

### 장르 경계의 유동성

동일한 음악을 두 번 재분석하면 장르 라벨이 달라질 수 있다(echo 분석에서 평균 Jaccard 유사도 7.6%). 이는 Suno의 장르 분류가 확정적 룩업이 아니라 확률적 생성임을 의미한다.

## 1.8 SP 작성을 위한 시사점

1. **장르를 첫 문장에 배치하라** — Suno의 97.2% 패턴을 따른다
2. **복합 장르 구문을 사용하라** — 단순 "Pop"보다 "K-Pop ballad with R&B influences" 형식이 Suno의 네이티브 패턴
3. **K-접두어를 활용하라** — 한국 음악을 원할 때 K-Pop/K-Indie/K-Rock 접두어가 효과적
4. **조성은 `key of X`로** — 코드명이나 진행 표기는 데드존
5. **장르별 핵심 마커를 포함하라** — Bossa Nova면 "nylon-string guitar, brushes", Trance면 "supersaw, four-on-the-floor"
6. **BPM을 명시하라** — `at {N} BPM` 형식으로, Suno가 장르에 따라 기대하는 BPM 범위가 있다
