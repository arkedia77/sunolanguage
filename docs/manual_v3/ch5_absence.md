# 5장: Suno가 묘사하지 않는 것

> 437곡의 corpus와 385행의 DB 교차분석에서 체계적으로 빠진 것들. 구조적 공백은 Suno의 한계이자 SP 작성의 핵심 가이드다.

## 5.1 완전 데드존 — 0건 카테고리

### 코드명과 코드 진행

- `key of X` 패턴: **652회** 출현 (Suno의 화성 인식 상한)
- 구체적 코드명 (Am7, Cmaj7, Dm): **0건**
- 로마 숫자 진행 (I-IV-V-I, ii-V-I): **0건**
- 코드 진행 표기 (Am → F → C → G): **0건**

Suno의 화성 인식은 **조성(key)** 수준에서 멈춘다. S005 "Harmony: The Chord Frontier" 10곡 테스트에서도 코드명이나 진행을 입력한 SP에 대해 Suno는 이를 무시하거나 자체 해석으로 대체했다(검증 대기 중).

### 다이내믹 마킹

- pp, mf, ff, crescendo, diminuendo: **0건**
- sforzando, fortepiano, al niente: **0건** (S003 스트레스 테스트 입력에도 불구)

Suno는 클래식 다이내믹 기호를 인식하지 않는다. 대신 자연어 동사를 사용한다:
- `builds` (점점 강해짐)
- `swells` (부풀어오름)  
- `drops` (갑자기 줄어듦)
- `fades` (서서히 사라짐)
- `stripped-back` (편성 축소)

### 마스터링 용어

- limiter: **0건**
- compressor (마스터링 맥락): **0건**
- loudness: **0건**
- master bus: **2건** (437곡 중 극히 예외적)

Suno의 프로덕션 인식은 **트랙 레벨**(reverb, distortion, chorus, delay)에서 끝난다. 마스터 버스 이후의 프로세싱은 묘사 영역 밖이다.

### 감정 형용사 (추상적)

- happy, sad, angry, excited: **0건** (SP에서)
- melancholic, nostalgic, euphoric: **0건** (SP에서)

Suno는 추상적 감정어를 사용하지 않는다. 대신 물리적 질감 어휘로 분위기를 전달한다:
- `warm`(109), `intimate`(120), `dreamy`, `gritty`
- `bright`(126), `crisp`(160), `soft`(107), `dark`

"슬프다"가 아니라 "따뜻하고 친밀한" — 이것이 Suno의 감정 표현법이다.

## 5.2 사실상 데드존 — 극히 드문 카테고리

### 감정 어휘의 빈곤

437곡에서 감정 관련 어휘가 등장하는 패턴:

| 어휘 | 빈도 | 비고 |
|------|------|------|
| intimate | 120 | 유일하게 높은 빈도의 감정어 |
| warm | 109 | 물리적 질감에 가까움 |
| dreamy | 18 | 이펙트 설정 맥락에서 주로 |
| gritty | 15 | 디스토션 묘사 맥락 |
| mellow | 12 | 템포/어레인지먼트 맥락 |

`intimate`를 제외하면 Suno의 "감정 어휘"는 사실상 물리적 속성 묘사다. `warm`은 EQ의 저역 특성을, `dreamy`는 리버브/딜레이 설정을, `gritty`는 디스토션 양을 지칭한다.

### 보컬 의인화 표현

- `voice cracks`, `raspy`, `nasal`, `husky`: 각 5건 미만
- `passionate`, `emotional delivery`: **0건**

Suno는 보컬을 물리적으로 묘사한다 — `breathy`(125), `soft`(107), `falsetto`(18), `baritone`/`tenor`/`soprano` (음역). "감정을 담아서"가 아니라 "부드러운 호흡으로, 낮은 음역에서."

## 5.3 absence 슬롯 — 명시적 부재 지시

Suno가 "없음"을 적극적으로 표현하는 8가지 패턴:

| 표현 | SP 빈도 | 브래킷 빈도 |
|------|--------:|----------:|
| solo cello | 5 | 5 |
| no percussion | 4 | — |
| without percussion | 4 | — |
| solo male | 3 | — |
| stripped(-back) | 2 | — |
| solo violin | 1 | 1 |
| without additional | 1 | — |
| is absent | 1 | — |

총 21회(SP) + 18회(브래킷). Suno는 "퍼커션 없음"을 `no percussion` 또는 `without percussion`으로 명시하며, 악기 솔로를 `solo cello`, `solo violin` 형식으로 표현한다.

브래킷에서는 추가로:
- `[drop out]` (4회) — 악기 퇴장
- `[fade out]` / `[fades out]` (각 3회) — 페이드 아웃

## 5.4 Suno Dead Zone 실험 결과

Dead Budget 실험(10곡 라운드트립 테스트)에서 확인된 데드존 표현:

### 입력해도 무시되는 것

- **구체적 코드명**: `Am7 → Dm7 → G7 → Cmaj7` 같은 코드 진행을 SP에 입력해도 Suno는 이를 무시하고 자체 화성을 생성
- **이탈리아어 다이내믹**: `pianissimo`, `fortissimo`, `sforzando` — Suno가 이해하지 못함
- **마스터링 지시**: `compress the master bus`, `limit at -14 LUFS` — 반영되지 않음
- **감정 형용사**: `make it emotional`, `with sadness` — Suno의 SP에 이런 표현이 없으므로 의미 없음

### 입력하면 번역되는 것 (수동적 이해)

- **클래식 주법 일부**: `spiccato`, `pizzicato` → Suno가 알지만 자체 SP에서는 드물게 사용 (각 2~5회)
- **재즈 전문 용어**: `comping`, `walking bass` → Suno가 이해하고 반영하지만 자체 어휘로 번역하기도 함
- **프로덕션 전문어**: `sidechain`, `bitcrushing` → 일부 인식하지만 출력 SP에서는 자연어로 풀어씀

## 5.5 3계층 어휘 모델

DB 교차분석으로 확인된 Suno 어휘의 3계층 구조:

### 1층: 네이티브 어휘 (Suno가 자발적으로 사용)

Suno가 재분석 SP에서 외부 입력 없이 자체적으로 사용하는 어휘. 437곡에서 반복 출현하며 장르별 분포가 안정적.

```
악기: electric bass(345), electric guitar(279), acoustic guitar(144), synthesizer(89)
질감: crisp(160), bright(126), warm(109), tight(104), dry(95), soft(107)
기법: arpeggiated(92), fingerstyle(78), palm-muted(45), slap(23), strumming(30)
구조: arrangement(453), counterpoint(40), walking(28), syncopated(87)
```

### 2층: 수동 이해 어휘 (입력하면 반영, 자발적 사용 드묾)

SP에 입력하면 Suno가 이해하고 반영하지만, 재분석 SP에서 자체적으로 사용하지는 않는 어휘. Echo 분석에서 확인 — 평균 Jaccard 유사도 7.6%.

```
주법: spiccato(2), col legno(1), sul ponticello(1), flutter tonguing(0)
화성: minor seventh(2), suspended chord(0), pedal point(0)
프로덕션: bitcrushing(0), granular synthesis(0)
```

### 3층: 데드존 (입력해도 무시)

Suno가 인식하지 못하거나 의도적으로 무시하는 표현:

```
코드: Am7, Cmaj7, I-IV-V-I, ii-V-I
다이내믹: pp, mf, ff, crescendo, diminuendo
마스터링: limiter, loudness, LUFS
감정: sad, happy, emotional, passionate
```

## 5.6 DB 교차분석 신규 발견

385행 DB 분석에서 기존 사전에 없었지만 Suno가 빈번하게 사용하는 어휘 27개를 신규 등록했다 (사전 v3.1). 이들은 "사전에 빠졌던 1층 어휘"로, 데드존이 아니라 누락이었다:

| 분류 | 신규 어휘 | 빈도 |
|------|----------|------|
| 기법 | counterpoint(40), strumming(30), walking(28), arpeggios(19), leaps(14), hammer-ons(12), runs(16), rolls(12), comping(3), call-and-response(8), ostinatos(5) | 11개 |
| 질감 | rounded(34), sub-heavy(18), low-end(13) | 3개 |
| 리듬 | mid-tempo(24), downbeats(24), four-bar(13), four-on-the-floor(3) | 4개 |
| 분위기 | jazz-influenced(35), high-energy(17), powerful(22) | 3개 |
| 악기 | fiddle(6), bodhrán(2), guiro(1), log drum(5), reese bass(1), whistle(3) | 6개 |

## 5.7 SP 작성을 위한 시사점

1. **코드명 넣지 마라** — 0건. `key of F minor`까지가 Suno의 화성 인식 한계
2. **다이내믹 마킹 넣지 마라** — 0건. `builds`, `swells`, `drops`로 대체
3. **감정 형용사 넣지 마라** — 0건. `warm`, `intimate`, `bright` 같은 물리적 질감으로 대체
4. **마스터링 지시 넣지 마라** — 2건. Suno는 트랙 레벨 프로덕션까지만 인식
5. **absence를 활용하라** — `no percussion`, `solo cello` 같은 명시적 부재 지시는 유효 (총 21회)
6. **1층 어휘를 우선 사용하라** — 이 장의 3계층 모델에서 1층 어휘가 가장 확실한 Suno 반응을 보장
