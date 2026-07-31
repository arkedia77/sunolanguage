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

### negative 성별 지시

- `no female vocals`, `no male` 류: **0건** (2026-07-11 실측)

Suno는 보컬 성별을 **긍정형으로만** 지정한다 — `featuring a male` 95건 vs `featuring a female` 13건 vs negative 지시 0건. "여성 보컬 빼줘"가 아니라 "남성 바리톤 보컬로" — 원하는 것을 명시하는 문법이지, 원하지 않는 것을 배제하는 문법이 아니다.

### 용도성 명칭 (OST·BGM)

- `OST`: 실질 **0건** / `BGM`: **0건** (2026-07-11 실측)

"OST풍으로", "매장 BGM처럼" 같은 용도 지정은 Suno 어휘 밖이다. **용도는 메타데이터로, 콘셉트는 mood 어휘로** — OST의 실체가 'cinematic strings + sweeping dynamics'라면 그 물리적 실체를 쓴다.

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

### 저음 형용사

- `deep` (voice 맥락): **1건** / `low` (voice 맥락): **7건** (vocal_main, 2026-07-11 실측)

Suno는 보컬의 낮음을 형용사로 묘사하지 않는다 — **성부 명칭으로만** 기술한다(`baritone` 등 성부명이 표준). "깊고 낮은 목소리"가 아니라 "male baritone vocals". 단, 성부 명칭도 만능이 아니다 — §5.5의 4층(프라이어 종속) 참조.

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

### 4층: 프라이어 종속 (2026-07 개정)

3계층 모델의 맹점이 실측으로 드러났다: **어휘가 네이티브(1층)여도, 효력이 곡의 프라이어(가사 정서·에너지·구조)에 종속되는 경우가 있다.**

**사례 (2026-07-11, K3016 협업 실측)**: 저에너지 소프트 발라드 + 1인칭 독백 가사 조합에서 `male baritone vocals` 지시가 **5회 전부 무효**(스템 F0 median 247~309Hz, tenor 상단으로 표류). 5차 시도는 데드존 0건의 네이티브 정형('K-Pop ballad featuring a baritone male vocal' + 가사 브래킷 이중결합)으로도 실패했다. 같은 배치의 duet(male-female)은 정상 성립 — 어휘 문제가 아니라 **가사의 정서·에너지가 만드는 프라이어가 표기를 이긴 것**이다.

**함의**: attestation 빈도(baritone은 고빈도 네이티브)가 곧 효력 보장이 아니다. 어휘층·표기층·프라이어층은 분리된 세 겹이며, SP 표기는 마지막 겹을 뚫지 못한다. 성부·성별이 크리티컬한 곡은 **기획 단계에서 가사 정서·에너지 텍스처를 함께 설계**해야 한다 — 표기로는 못 잡는다.

> **생성 측 적용 (→ 6장 6.7)**: 이 3계층 구분은 곡 생성에서 자동 품질 게이트가 된다. 3층(데드존)·산문 채널 항목이 가창 가사 자리에 새어들면 그 곡의 coherence가 급락하므로(N시리즈 최저 coh 4곡 = 디렉티브 누출 결함곡과 일치), **coherence 점수가 계층 위반의 탐지기**로 기능한다. 또한 트로트 SP 작업에서 clavinet·tumbao(악기 데드존)·'sung in Korean'(0건 군더더기)을 raw 코퍼스 실측으로 걸러낸 것도 같은 3계층 판정의 응용이다.

## 5.6 DB 교차분석 신규 발견

385행 DB 분석에서 기존 사전에 없었지만 Suno가 빈번하게 사용하는 어휘 27개를 신규 등록했다 (사전 v3.1). 이들은 "사전에 빠졌던 1층 어휘"로, 데드존이 아니라 누락이었다:

| 분류 | 신규 어휘 | 빈도 |
|------|----------|------|
| 기법 | counterpoint(40), strumming(30), walking(28), arpeggios(19), leaps(14), hammer-ons(12), runs(16), rolls(12), comping(3), call-and-response(8), ostinatos(5) | 11개 |
| 질감 | rounded(34), sub-heavy(18), low-end(13) | 3개 |
| 리듬 | mid-tempo(24), downbeats(24), four-bar(13), four-on-the-floor(3) | 4개 |
| 분위기 | jazz-influenced(35), high-energy(17), powerful(22) | 3개 |
| 악기 | fiddle(6), bodhrán(2), guiro(1), log drum(5), reese bass(1), whistle(3) | 6개 |

## 5.7 BPM 재해석 — Suno가 템포를 자의적으로 바꾼다

385행 코퍼스에서 original_sp와 reanalysis_sp 양쪽에 BPM이 명시된 58쌍을 대조한 결과:

| 구분 | 수치 |
|------|------|
| BPM 일치 | 5/58 (8.6%) |
| BPM 변경 | 53/58 (**91.4%**) |

Suno는 SP에 명시된 BPM을 거의 그대로 따르지 않는다.

### 저BPM 더블링 패턴

BPM 80 이하에서 Suno의 재해석이 가장 극단적이다:

| 입력 BPM | 결과 BPM | 시프트 | 곡 |
|---------|---------|--------|-----|
| 60 | 210 | +150 | S003_09 Harp — 반박자 재해석 |
| 60 | 120 | +60 | S004_04 Oboe — 2배 더블링 |
| 66 | 124 | +58 | S003_04 Oboe — 2배 근사 |
| 68 | 105 | +37 | S016_07 Quiet Piano Room |
| 72 | 210 | +138 | S016_05 Cello+Piano — 3배 근사 |
| 80 | 130 | +50 | S016_09 Nylon Guitar |

해석: Suno가 BPM 60 이하 음원을 들으면 내부적으로 2~3배 더블링으로 재해석한다. SP에 50 BPM을 명시해도 100+ BPM으로 처리할 가능성이 높다.

### 코퍼스 BPM 분포

387건의 SP에서 추출한 BPM 분포:

| 구간 | 곡수 | 비율 |
|------|------|------|
| 60~69 | 10 | 2.6% |
| **70~79** | **119** | **30.7%** — 최빈 구간 |
| 80~89 | 52 | 13.4% |
| 90~99 | 43 | 11.1% |
| 100~109 | 26 | 6.7% |
| 110~119 | 47 | 12.1% |
| 120~129 | 43 | 11.1% |

코퍼스 최솟값은 65 BPM (Doom Metal 1건). 68 BPM이 10건(전부 K-Ballad)으로 Suno가 안정적으로 생성하는 실질적 하한이다. BPM 40~55 구간은 **0건**.

### SP 작성 시사점

- `72 BPM` — Suno가 가장 많이 생성하는 느린 템포 (K-Ballad 표준)
- `68 BPM` — 안정적 하한. 이 이하는 Suno가 자의적 재해석 위험
- BPM 50 이하를 원한다면 SP가 아닌 DAW 후처리(타임 스트레칭)로 접근

## 5.8 구조 제어 데드존 — Suno SP의 경계

385건 SP 전문에서 곡의 매크로 구조를 제어하려는 토큰 검색 결과:

| 토큰 | 출현 수 | 용법 |
|------|--------:|------|
| loop | 15 | **전부 묘사적** — "four-bar loop", "piano loop" (악기가 루프를 연주한다는 뜻) |
| seamless | 0 | — |
| fade in | 0 | — |
| fade out | 0 | — |
| no intro | 0 | — |
| no outro | 0 | — |
| crossfade | 0 | — |

Suno의 SP 언어는 **악기·편성·템포·조성**을 기술하는 체계다. 곡의 시작/종료/전환 같은 매크로 구조는 SP의 제어 범위 밖이다.

`loop`가 15회 등장하지만 이는 "반복 패턴을 연주한다"라는 악기 기법 묘사이지 "곡을 루프하라"는 구조 지시가 아니다. Suno는 `repetitive four-bar loop`, `consistent dynamic level`, `minimal structural variation` 같은 간접 묘사로 loop-friendly 특성을 유도할 수 있지만, 이는 보장이 아닌 경향성이다.

### 브래킷 구조 제어와의 비교

가사 채널 브래킷은 제한적 구조 제어가 가능하다:
- `[drop out]` (4회) — 악기 퇴장
- `[fade out]` / `[fades out]` (각 3회) — 페이드 아웃
- `[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` — 섹션 마커

즉, 구조 제어는 SP가 아닌 **가사 브래킷**의 영역이다. SP에서 구조를 제어하려는 시도는 데드존이다.

## 5.9 장르 데드존 — Suno가 모르는 장르 영역

385행 코퍼스의 reanalysis_genre 전수 조사에서 Suno가 자발적으로 사용한 장르 토큰과 **한 번도 등장하지 않은** 장르 영역:

### Suno 네이티브 장르 (코퍼스에서 확인)

| 영역 | 예시 | 코퍼스 건수 |
|------|------|----------:|
| K-Pop/K-Ballad 계열 | K-Pop ballad, K-Pop R&B, K-Indie folk ballad | 300+ |
| 월드뮤직 | Bossa Nova(4), Gypsy Jazz(4), Amapiano(2) | 15+ |
| 서양 록/팝 | Synthwave(1), Doom Metal(1), Acid House(1) | 10+ |
| Lo-fi | Lo-fi hip hop(1), Lofi hip hop(1), Korean Lo-fi Hip Hop(1) | 3 |
| 재즈 | Smooth jazz fusion(2), Bebop→Bossa nova 재해석(1) | 5+ |

### 코퍼스 0건 장르 (데드존)

| 장르 | 코퍼스 | SP 내 키워드 | 판정 |
|------|--------|------------|------|
| **ambient** (순수) | 0건 (장르 토큰) | 4건 (부차적 수식어: "ambient swells") | 장르로 미인식. 수식어로만 사용 |
| **drone** | 0건 (장르 토큰) | 2건 ("sustained drones" — 기법 묘사) | 장르 아닌 기법 |
| **Nordic dark ambient** | 0건 | 0건 | 완전 데드존 |
| **sleep / sleep music** | 0건 | 0건 | 완전 데드존 |
| **chill / chillhop** | 0건 | 0건 | 완전 데드존 |
| **meditation / healing** | 0건 | 0건 | 완전 데드존 |
| **ASMR** | 0건 | 0건 | 완전 데드존 |
| **new age** | 0건 | 0건 | 완전 데드존 |

### 해석

Suno의 학습 데이터와 생성 능력은 **구조적·리듬적 음악**에 집중되어 있다. 팝, 록, 발라드, 펑크, 재즈처럼 명확한 비트·멜로디·화성 구조가 있는 장르에서 강하고, ambient·drone·sleep처럼 무구조·무멜로디·무리듬 음악은 코퍼스에 거의 반영되지 않았다.

`ambient`라는 단어 자체는 Suno가 알지만(4건), 이는 "ambient pad"나 "ambient swells" 같은 **수식어**로서의 사용이지 **장르 정체성**이 아니다. SP에 `ambient` 장르를 명시해도 Suno가 순수 ambient 결과물을 안정적으로 생성한다는 코퍼스 근거는 없다.

### SP 작성 시사점

- 순수 ambient/drone이 필요하면 Suno 외 도구(AIVA, Mubert 등) 병행 권장
- Suno로 접근해야 한다면 `Downtempo electronic` + 구체적 악기 편성으로 최소한의 구조를 부여
- `sleep`, `meditation`, `healing`, `ASMR` 같은 기능적 장르 토큰은 Suno에 무의미
- Lo-fi hip hop은 네이티브 확인 (3건) — BPM 82~88, vinyl crackle + jazz chords 패턴

## 5.10 SP 작성을 위한 종합 시사점

1. **코드명 넣지 마라** — 0건. `key of F minor`까지가 Suno의 화성 인식 한계
2. **다이내믹 마킹 넣지 마라** — 0건. `builds`, `swells`, `drops`로 대체
3. **감정 형용사 넣지 마라** — 0건. `warm`, `intimate`, `bright` 같은 물리적 질감으로 대체
4. **마스터링 지시 넣지 마라** — 2건. Suno는 트랙 레벨 프로덕션까지만 인식
5. **absence를 활용하라** — `no percussion`, `solo cello` 같은 명시적 부재 지시는 유효 (총 21회)
6. **1층 어휘를 우선 사용하라** — 이 장의 3계층 모델에서 1층 어휘가 가장 확실한 Suno 반응을 보장
7. **BPM 68 이상을 유지하라** — 코퍼스 실질 하한. 이하는 Suno가 2~3배 더블링으로 재해석
8. **구조 제어는 가사 브래킷으로** — SP에서 fade/loop/intro 제어는 데드존. `[Outro]`, `[fade out]` 등 가사 채널 활용
9. **순수 ambient/drone은 Suno 약점** — 코퍼스 0건. 구조적 음악(비트·멜로디 있는)으로 접근하거나 외부 도구 병행
10. **BPM 시프트를 감안하라** — 91.4% 변경률. SP BPM은 목표가 아닌 힌트. 최종 BPM은 Suno 재량
