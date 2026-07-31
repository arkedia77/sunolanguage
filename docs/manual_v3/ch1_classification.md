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
| 평균 SP 길이 | 522자 (Q1 464 ~ Q3 575) |

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

**전조(key change) — v5.5 버전 종속 행동**: `key change`는 코퍼스에서 v5.5 곡 1건뿐(S018_16 Trance, v5.0 Wave1은 0건)인 v5.5 신규 어휘다. 동시에 v5.5부터 **마지막 코러스의 pump-up modulation이 자동 생성**된다(2026-05-09 Leo 실청취, 발라드+록 확인 — 지시 없이도 발생). 한국 음악 클리셰(마지막 코러스 반음/온음 상승)와 부합하므로 한국 타깃은 그대로 활용하고, 서양 팝 타깃은 `no key change` 네거티브 지시 테스트가 필요하다. Suno 표현형: SP `"A key change occurs in the final section"`, 가사 `[key change]`.

### 박자 선언

`{N}/{N} time` 형식으로 박자를 명시한다. 4/4가 압도적이며, 3/4(왈츠), 6/8(셀틱/바로크) 등이 장르별로 고정적이다.

## 1.6 SP 길이와 장르의 관계

Suno 재분석 SP의 길이는 장르에 따라 체계적으로 달라진다.

### 전체 분포

75%의 SP가 400~599자 구간에 집중되어 있다. "표준 SP"는 약 500자다.

```
200-299    3행  █
300-399   20행  ██████████
400-499  142행  ████████████████████████████████████████████████ ← 최빈
500-599  149행  █████████████████████████████████████████████████ ← 최빈
600-699   60행  ████████████████████
700-799    9행  ███
800-899    2행  █
```

### 장르별 SP 길이

| 장르 | 행수 | 평균 | 범위 |
|------|------|------|------|
| Classical | 6 | **697자** | 634~756 |
| Jazz | 14 | **586자** | 409~761 |
| Folk | 9 | **586자** | 419~672 |
| Electronic | 15 | 572자 | 459~789 |
| Hip-Hop | 18 | 551자 | 394~721 |
| Rock | 38 | 539자 | 344~682 |
| Funk | 31 | 517자 | 378~676 |
| Indie | 35 | 524자 | 408~656 |
| Ballad | 158 | **484자** | 230~673 |

편성 복잡도가 SP 길이를 결정한다: 오케스트라 편성의 Classical(697자)이 가장 길고, 미니멀 편성의 Ballad(484자)가 가장 짧다. 장르 설명의 단어수와 SP 길이 사이에 약한 양의 상관이 있다(Pearson r=0.33).

Instrumental 트랙(560자)이 Vocal 트랙(505자)보다 평균 55자 더 길다 — 보컬 묘사가 빠진 대신 악기 묘사가 더 상세해진다.

## 1.7 장르와 어휘의 상관관계

DB 385행 교차분석에서 발견된 장르별 고유 어휘 패턴:

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

K-Ballad(163행)에서 가장 자주 등장하는 어휘:

```
breathy(125), soft(107), intimate(87), reverb(121),
light(119), subtle(110), warm(92), acoustic(144),
counterpoint(15), jazz-influenced(19), rounded(10)
```

K-Ballad의 어휘는 부드러움(soft/breathy/intimate)과 공간감(reverb/light/subtle) 중심이다. 주목할 점은 `counterpoint`(15회)와 `jazz-influenced`(19회)가 발라드에서 빈번하게 등장한다는 것이다 — Suno는 한국 발라드의 편곡을 대위법적이고 재즈 영향을 받은 것으로 인식한다.

#### K-Ballad 10개 서브타입

163행을 서브타입별로 분류하면 각각 고유한 악기·보컬·주법 시그니처를 갖는다:

| 서브타입 | 행수 | 핵심 악기 | 보컬 | 주법 |
|----------|------|----------|------|------|
| R&B | 33 | electric guitar 85% + synth 61% | falsetto + smooth | syncopated 52% |
| Baritone | 29 | grand piano 69% + strings 41% | baritone + rich | arpeggiated |
| Plain | 30 | piano 50% + acoustic 50% | breathy + soft | steady |
| Folk | 22 | acoustic guitar 100% | breathy 68% + intimate 64% | fingerstyle 55%, steady 95% |
| Acoustic | 20 | acoustic guitar 100% | breathy + warm | arpeggiated |
| Indie | 10 | electric guitar + bass | soft + intimate | clean + reverb |
| Jazz | 5 | electric guitar + grand piano | smooth + warm | swing 80% |
| Rock | 5 | electric guitar 100% | powerful + belted | arpeggiated 100% |
| Synth | 4 | synth + pad | breathy | steady |

R&B 서브타입은 일렉 기타+신스 조합과 팔세토가 핵심이고, Folk/Acoustic은 어쿠스틱 기타 100%와 핑거스타일/스테디 리듬이 특징이다. Baritone 서브타입은 그랜드 피아노+스트링 섹션의 클래시컬 편성이 다른 서브타입과 확연히 구분된다.

### K-Indie의 어휘 세계 (76행)

K-Indie는 K-Ballad와 부분적으로 겹치면서도 독자적 시그니처를 갖는다:

| 서브타입 | 행수 | 핵심 악기 | 보컬 | 주법 |
|----------|------|----------|------|------|
| Pop | 29 | electric guitar 97% + kick 76% | soft 62%, tenor 48% | clean 100% + syncopated 76% |
| Folk | 22 | acoustic 100%, 리듬 최소 | soft 86% + baritone 64% | steady 95% + fingerstyle 55% |
| Rock | 6 | 일렉+풀 드럼셋 | tenor 67% | syncopated 83% + overdriven 83% |
| Ballad | 6 | acoustic 83% | breathy+warm+intimate 100% | arpeggiated 83% |

**K-Indie Pop**(29행)이 가장 큰 서브타입으로, clean 100% + syncopated 76%의 "깔끔하지만 리듬감 있는" 사운드가 핵심이다. K-Indie Folk는 K-Ballad Folk와 시그니처가 거의 동일(acoustic 100%, steady 95%, fingerstyle 55%)하여 장르 경계가 모호하다.

### K-Funk의 어휘 세계 (33행)

K-Funk는 K-Ballad/K-Indie와 전혀 다른 어휘 세계를 형성한다:

| 서브타입 | 행수 | 핵심 악기 | 보컬 | 주법 |
|----------|------|----------|------|------|
| Pure Funk-Pop | 14 | electric guitar 93% + **brass 71%** | **bright 100%** | **slap 100% + staccato 100%** |
| J-Fusion | 5 | 일렉+synth 80% + bass 80% | bright 80% + tenor 60% | slap 100% + syncopated 100% |
| Disco-Funk | 5 | 일렉+**synth 100%**+pad 80% | bright 100% | slap 80% + sixteenth-note 60% |
| Synth-Funk | 3 | **synth+pad 100%** | bright 100% | slap 100% + driving 67% |

K-Funk의 DNA는 **slap(85%)**과 **staccato(73%)**와 **bright(85%)**다. 이 세 어휘는 K-Ballad(0%)와 K-Indie(0%)에서 거의 등장하지 않아 강력한 장르 식별자다. brass(52%)도 K-Funk에서만 유의미하게 출현한다.

### K-Rock의 어휘 세계 (40행)

| 서브타입 | 행수 | 핵심 악기 | 보컬 | 주법 |
|----------|------|----------|------|------|
| Punk/Pop-Punk | 11 | 일렉 100% + bass 82% | (묘사 최소) | **driving 100% + distorted 91% + power chord 91%** |
| J-Rock Fusion | 8 | 일렉 100% + snare 88% | bright 88% + tenor 75% | distorted 75% + palm-muted 75% |
| Pop-Rock | 6 | 일렉+풀 리듬 섹션 | bright 100% + tenor 67% | syncopated 83% + power chord 83% |
| Indie Rock | 5 | 풀 드럼셋 100% | tenor 80% | clean 100% + overdriven 80% |
| Soft Rock | 5 | 일렉+pad 80% | breathy 80% + soft 80% | **arpeggiated 100% + delay 100%** |

K-Rock의 DNA는 **distorted(62%)**와 **driving(65%)**과 **power chord(65%)**다. electric guitar는 전 서브타입에서 100%로, K-Rock에서 일렉 기타는 필수다. Soft Rock 서브타입은 arpeggiated+clean+delay로 K-Ballad와 거의 동일하여 장르 경계가 모호하다.

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

### K-장르 간 배타적 식별 어휘

같은 K-계열이라도 장르 간에 거의 겹치지 않는 배타적 어휘가 존재한다:

| 어휘 | K-Ballad | K-Indie | K-Funk | K-Rock |
|------|----------|---------|--------|--------|
| slap | — | — | **85%** | — |
| staccato | — | — | **73%** | — |
| brass | — | — | **52%** | — |
| sixteenth-note | — | — | **52%** | — |
| power chord | — | — | — | **65%** |
| distorted | — | — | — | **62%** |
| palm-muted | — | — | — | **52%** |
| driving | — | — | — | **65%** |
| fingerstyle | — | 21% | — | — |
| grand piano | 40% | — | — | — |
| string section | 15% | — | — | — |

이 표는 SP에서 장르를 전환할 때 핵심적이다. K-Funk를 원하면 slap+staccato를, K-Rock을 원하면 power chord+distorted를 포함시키면 된다.

## 1.8 K-장르 경계의 겹침

서브타입 분석에서 장르 경계가 모호한 조합이 발견된다:

1. **K-Indie Ballad ≈ K-Ballad Folk**: acoustic+breathy+arpeggiated. 악기·보컬·주법 시그니처가 거의 동일.
2. **K-Rock Soft Rock ≈ K-Ballad Rock**: arpeggiated+clean+delay. BPM만 차이(73 vs 72).
3. **K-Indie Rock ≈ K-Rock Indie Rock**: syncopated+clean+reverb. 템포 차이(109 vs 107 BPM)도 미미.
4. **K-Funk**: 다른 K-장르와 겹침 최소 — slap/staccato/brass로 가장 독립적인 어휘 세계.

이는 Suno의 장르 분류가 이산적(discrete) 카테고리가 아니라 연속적 스펙트럼임을 보여준다. K-Indie Folk와 K-Ballad Folk를 구분하는 것은 장르명의 차이이지, 실제 어휘 세계의 차이가 아니다.

## 1.9 Suno의 장르 인식 편향

### 관찰된 편향

1. **K-Pop 흡수**: 원곡이 트로트, 인디 포크, 힙합이어도 Suno는 상당수를 K-Pop으로 분류
2. **Ballad 과대 대표**: W1의 50%가 Ballad 태그를 포함 — 한국 음악 = 발라드라는 Suno의 편향
3. **Bebop → Bossa Nova 드리프트**: S018에서 Bebop으로 의도한 곡을 Suno가 "Bossa Nova jazz"로 재분류 — 재즈 하위 장르 구분 약함
4. **Afrobeats → Amapiano 혼동**: S018에서 Afrobeats로 의도한 곡을 "Amapiano"로 분류 — 아프리카 장르 구분 불명확

### 장르 경계의 유동성

동일한 음악을 두 번 재분석하면 장르 라벨이 달라질 수 있다(echo 분석에서 평균 Jaccard 유사도 7.6%). 이는 Suno의 장르 분류가 확정적 룩업이 아니라 확률적 생성임을 의미한다.

## 1.10 SP 오프닝 문법 — 첫 문장이 장르를 결정한다

445개 재분석 SP의 첫 문장(마침표 전)을 분석하면, Suno가 장르를 선언하는 공식(formula)이 있다.

### 오프닝 구문 템플릿

| 템플릿 | 비율 | 예시 |
|--------|------|------|
| **Genre.** | 55.7% | `K-Pop ballad.` |
| **Genre with Influence.** | 25.4% | `K-Pop ballad with R&B influences.` |
| **Genre featuring Vocal.** | 17.5% | `K-Pop ballad featuring a baritone male vocal.` |
| **Genre featuring Vocal with Influence.** | 1.3% | `K-Indie ballad featuring a male tenor vocal with jazz-pop influences.` |

절반 이상이 장르명만으로 첫 문장을 마치며, 복합 형식일 때도 `featuring` (보컬) + `with` (서브장르 영향)의 정형화된 구문을 사용한다.

### 첫 단어 분포

| 첫 단어 | 빈도 | 비율 |
|---------|------|------|
| K-Pop | 274 | 61.6% |
| K-Indie | 66 | 14.8% |
| Bossa | 10 | 2.2% |
| K-Rock | 7 | 1.6% |
| Cinematic | 5 | 1.1% |
| 기타 (83종) | 83 | 18.7% |

**83.4%가 K- 접두어로 시작한다.** Suno의 기본 장르 인식 프레임워크가 K-접두어 기반임을 보여준다.

### `featuring` 뒤에 오는 것

| 패턴 | 빈도 |
|------|------|
| a baritone male vocal | 25 |
| a male baritone vocal | 7 |
| a male tenor vocal | 6 |
| a male tenor vocalist | 4 |
| a female vocalist | 2 |

`featuring`은 거의 전적으로 **보컬 유형 선언**에 사용된다. 음역(baritone/tenor) + 성별(male/female) 조합이 핵심.

### `with` 뒤에 오는 것

| 패턴 | 빈도 |
|------|------|
| R&B influences | 14 |
| a mid-tempo groove | 6 |
| jazz-pop influences | 5 |
| soft rock influences | 4 |
| synth-pop elements | 4 |
| bossa nova influences | 4 |

`with`는 **서브장르 영향(influences)** 또는 **요소(elements)** 선언에 사용된다.

### 오프닝 길이

- 평균 5.3단어, 중앙값 5, 최대 17단어
- 5단어 이내가 대다수 — 간결한 장르 선언이 Suno의 표준

### SP 작성 규칙: 첫 문장 공식

Suno의 네이티브 패턴을 따르는 SP의 첫 문장은 이렇게 작성한다:

```
{K-접두어 장르} [featuring a {음역} {성별} vocal] [with {서브장르} influences].
```

예시:
- `K-Pop ballad.` (최소형)
- `K-Pop R&B ballad featuring a male tenor vocal.` (보컬 선언형)
- `K-Indie folk ballad with jazz-pop influences.` (영향 선언형)
- `K-Rock featuring a powerful male vocal with heavy metal influences.` (완전형)

**주의**: 첫 문장에 악기, 템포, 프로덕션을 넣지 않는다 — 이것은 Suno가 두 번째 문장 이후에 기술하는 영역이다.

## 1.11 SP 7문장 공식 — Suno가 음악을 묘사하는 순서

445개 재분석 SP의 문장 수와 위치별 주제를 분석하면, Suno가 음악을 기술하는 정형화된 7문장 구조가 있다.

### 문장 수

| 문장수 | 곡수 | 비율 |
|--------|------|------|
| 6 | 115 | 25.8% |
| **7** | **183** | **41.1%** |
| 8 | 93 | 20.9% |

평균 7.1문장, 중앙값 7. **6~8문장이 87.9%** — Suno의 SP 출력은 거의 항상 7문장 전후다.

### 문장 위치별 주제

| 위치 | 지배적 주제 | 비율 | 해석 |
|------|-----------|------|------|
| #1 | GENRE | 63% | 장르 선언 (§1.10) |
| #2 | **INSTRUMENT** | **91%** | 주요 악기 묘사 |
| #3 | INSTRUMENT | 66% | 보조 악기 / 베이스 |
| #4 | INSTRUMENT(35%) / DRUMS(30%) | 혼합 | 리듬 섹션 진입 |
| #5 | VOCAL | 32% | 보컬 묘사 |
| #6 | TEMPO/KEY(34%) / ARRANGEMENT(22%) | 혼합 | 구조·템포 마무리 |

2번째 문장이 악기인 비율 91% — 장르 선언 직후 반드시 악기 묘사가 온다.

### SP 7문장 템플릿

```
#1  {장르 선언}                    ← "K-Pop ballad with R&B influences."
#2  {주요 악기 묘사}               ← "Clean electric guitar plays arpeggiated chords..."
#3  {보조 악기 / 베이스}           ← "Electric bass follows the kick drum pattern..."
#4  {드럼 / 추가 악기}            ← "The drums consist of a dry, tight kick..."
#5  {보컬 묘사}                    ← "Breathy, intimate male vocals..."
#6  {어레인지먼트 / 프로덕션}     ← "The arrangement is sparse..."
#7  {템포 / 조성}                  ← "72 BPM in E Major, 4/4 time signature."
```

### 마지막 문장의 주제

| 유형 | 비율 |
|------|------|
| **TEMPO/KEY** | **50.1%** |
| VOCAL | 16.4% |
| ARRANGEMENT | 13.5% |
| INSTRUMENT | 11.9% |

절반이 템포/조성으로 끝난다. **"첫 문장 = 장르, 마지막 문장 = 템포"** — SP의 양 끝이 프레임을 형성한다.

### SP 핵심 동사 6개

Suno가 악기를 묘사할 때 사용하는 동사는 6개에 집중:

| 동사 | 빈도 | 용법 |
|------|------|------|
| plays | 264 | `Guitar plays arpeggiated chords` — 직접 연주 |
| features | 205 | `The arrangement features a...` — 편성 소개 |
| provides | 176 | `Bass provides low-end weight` — 역할 부여 |
| follows | 162 | `Bass follows the kick drum pattern` — 추종 |
| fills | 107 | `Piano fills the harmonic space` — 공간 채우기 |
| enters | 95 | `Strings enter in the chorus` — 시간적 진입 |

이 6개 동사가 SP 전체 동사 사용의 85%+. SP를 쓸 때 이 동사를 사용하면 Suno의 네이티브 문법에 부합한다.

### 문장 시작 패턴

| 패턴 | 빈도 | 위치 |
|------|------|------|
| The tempo is | 164 | 마지막 문장 |
| The arrangement is | 106 | 5~6번째 |
| The arrangement features | 104 | 5~6번째 |
| A clean electric | 73 | 2번째 |
| The bass guitar | 61 | 3~4번째 |
| The drum kit | 41 | 4번째 |
| The vocal performance | 35 | 5번째 |

각 문장의 시작어만으로도 위치를 예측할 수 있다 — 그만큼 Suno의 SP 문법은 고정적이다.

## 1.12 SP 작성을 위한 시사점

1. **7문장 구조를 따르라** — 장르 → 주악기 → 보조악기 → 드럼 → 보컬 → 어레인지먼트 → 템포/조성 (§1.11)
2. **첫 문장은 장르 선언 공식** — `{장르} [featuring {보컬}] [with {영향}].` 5단어 이내 (§1.10)
3. **마지막 문장은 템포/조성** — `72 BPM in E Major, 4/4 time signature.` (50.1%)
4. **K-접두어를 활용하라** — 한국 음악을 원할 때 K-Pop/K-Indie/K-Rock 접두어가 효과적 (83.4%)
5. **핵심 동사 6개** — plays/features/provides/follows/fills/enters만으로 충분 (§1.11)
6. **조성은 `key of X`로** — 코드명이나 진행 표기는 데드존
7. **장르별 핵심 마커를 포함하라** — Bossa Nova면 "nylon-string guitar, brushes", Trance면 "supersaw, four-on-the-floor"
8. **SP 길이를 장르에 맞춰라** — Ballad ~480자, Rock ~540자, Classical ~700자. 900자 이상 위험
9. **K-장르 전환은 배타적 어휘로** — K-Funk는 slap+staccato, K-Rock은 power chord+distorted
10. **Instrumental은 더 길게 써도 된다** — 보컬 묘사 대신 악기 묘사에 50~60자 여유
