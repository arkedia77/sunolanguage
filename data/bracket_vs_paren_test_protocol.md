# [] 브래킷 vs () 괄호 체계적 비교 테스트 프로토콜

**시리즈**: S_BP (Bracket vs Parenthesis)
**설계일**: 2026-05-12
**목적**: 가사 채널에서 [] 브래킷과 () 괄호에 동일한 지시를 넣었을 때 Suno 반응 차이 정량 측정

---

## 1. 배경

ch2 분석에서 두 채널의 역할이 구분됨:
- **[] 브래킷**: 독립 행, 섹션 마커 + 악기 진입 큐 + 보컬 큐
- **() 괄호**: 인라인, 보컬 행위 디렉션 + 감탄사

Leo 실청취로 () 유효성 4/4 확인 (hums softly, melismatic runs, trills/scales, spoken).
그러나 동일 지시를 [] vs ()로 대조한 실험은 0건.

**핵심 질문**: 같은 지시어를 [] 에 넣는 것과 () 에 넣는 것이 다른 결과를 만드는가?

---

## 2. 가설

| 코드 | 가설 | 검증 기준 |
|------|------|-----------|
| H1 | **채널 특화** — 악기 큐는 []에서, 보컬 행위는 ()에서 더 잘 반영됨 | 각 지시 유형별 적합 채널 > 부적합 채널 |
| H2 | **채널 무관** — []와 ()는 형식적 차이일 뿐, Suno 반응은 동일 | [] ≈ () (모든 지시 유형에서) |
| H3 | **[] 우세** — 독립 행의 []가 인라인 ()보다 일관적으로 강한 반응 | [] > () (대부분 지시 유형에서) |
| H4 | **교차 간섭** — 부적합 채널 사용 시 의도와 다른 결과 발생 | 부적합 채널에서 왜곡/무시 비율 높음 |

---

## 3. 실험 설계

### 독립변수
1. **지시 유형** (3종): 악기 진입 큐 / 보컬 질감 큐 / 보컬 행위 디렉션
2. **채널** (3조건): [] 브래킷 / () 괄호 / Control (지시 없음)

### 종속변수
- 지시 반영 여부 (0=미반영, 1=반영, ?=불확실) — Leo 청취 판정
- Suno 재분석 SP에서 해당 지시어 출현 여부

### 반복
- 각 조건당 **3회 생성**
- 9조건 × 3회 = **27곡**

### SP 고정 원칙
- **모든 27곡은 동일한 SP** 사용 (SP는 변수가 아님)
- 변수는 **가사 안의 지시 방식**만

---

## 4. 지시어 세트 (3종)

### 지시 A: 악기 진입 큐 (Instrument Cue)
- 지시어: `fingerpicked acoustic guitar`
- corpus 근거: 브래킷 빈도 29회 (ch2 §2.4)
- 의미: Verse 2 진입 시점에 핑거피킹 어쿠스틱 기타 추가

### 지시 B: 보컬 질감 큐 (Vocal Timbre Cue)
- 지시어: `breathy female vocals`
- corpus 근거: 브래킷 빈도 28회 (ch2 §2.4)
- 의미: Chorus에서 보컬 질감을 breathy로 전환

### 지시 C: 보컬 행위 디렉션 (Vocal Action Directive)
- 지시어: `hums softly`
- corpus 근거: () 유효성 4/4 검증 완료
- 의미: Bridge에서 허밍으로 전환

---

## 5. 공통 SP

```
K-Pop ballad featuring a male tenor vocal. Clean electric guitar plays arpeggiated chords with light chorus and delay. Electric bass follows the kick drum pattern with a warm, rounded tone. The drums maintain a steady beat with soft kick and brushed snare. A subtle synthesizer pad provides atmospheric background. The male tenor vocal delivers with a soft, intimate quality. The arrangement is sparse, focusing on the interplay between the guitar and the vocal melody. Plate reverb on the vocal. 72 BPM in E Major, 4/4 time signature.
```

**SP 길이**: ~480자 (K-Ballad 적정 범위 내)

SP에 acoustic guitar, breathy, hums 등의 단어를 **의도적으로 미포함** — 가사 지시의 독립적 효과를 측정하기 위함.

---

## 6. 가사 세트 (9 변형)

### 6.0 기본 구조 (공통)

```
[Intro]

[Verse 1]
어둠 속에 홀로 남은 밤
기억 속에 네가 스며들어

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어

[Verse 2]
{--- 지시 A 삽입 위치 ---}
시간이 멈춘 듯 흘러가고
이 자리에 여전히 남아

[Chorus]
{--- 지시 B 삽입 위치 ---}
돌아올 수 없는 그 길 위에
나 홀로 서 있어

[Bridge]
{--- 지시 C 삽입 위치 ---}
언젠가 다시 만날 수 있을까
그날을 기다리며

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어
```

---

### 6.1 지시 A — 악기 진입 큐: 3 변형

**BP_A1 — [] 브래킷 (적합 채널)**
```
[Verse 2]
[fingerpicked acoustic guitar]
시간이 멈춘 듯 흘러가고
이 자리에 여전히 남아
```

**BP_A2 — () 괄호 (부적합 채널)**
```
[Verse 2]
(fingerpicked acoustic guitar)
시간이 멈춘 듯 흘러가고
이 자리에 여전히 남아
```

**BP_A0 — Control (지시 없음)**
```
[Verse 2]
시간이 멈춘 듯 흘러가고
이 자리에 여전히 남아
```

---

### 6.2 지시 B — 보컬 질감 큐: 3 변형

**BP_B1 — [] 브래킷 (적합 채널)**
```
[Chorus]
[breathy female vocals]
돌아올 수 없는 그 길 위에
나 홀로 서 있어
```

**BP_B2 — () 괄호 (부적합 채널)**
```
[Chorus]
돌아올 수 없는 그 길 위에 (breathy female vocals)
나 홀로 서 있어
```

**BP_B0 — Control (지시 없음)**
```
[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어
```

---

### 6.3 지시 C — 보컬 행위 디렉션: 3 변형

**BP_C1 — [] 브래킷 (부적합 채널)**
```
[Bridge]
[hums softly]
언젠가 다시 만날 수 있을까
그날을 기다리며
```

**BP_C2 — () 괄호 (적합 채널)**
```
[Bridge]
(hums softly)
언젠가 다시 만날 수 있을까
그날을 기다리며
```

**BP_C0 — Control (지시 없음)**
```
[Bridge]
언젠가 다시 만날 수 있을까
그날을 기다리며
```

---

## 7. 가사 조합 매트릭스

각 곡은 지시 A, B, C 위치 중 **하나만 변형**하고 나머지는 Control로 고정한다. 변수를 1개씩 격리하기 위함.

| # | 코드 | 지시 A (Verse 2) | 지시 B (Chorus 2) | 지시 C (Bridge) | 측정 대상 |
|---|------|-----------------|-------------------|-----------------|-----------|
| 1 | BP_A1 | [] 브래킷 | Control | Control | 악기 큐 @ [] |
| 2 | BP_A2 | () 괄호 | Control | Control | 악기 큐 @ () |
| 3 | BP_A0 | Control | Control | Control | 악기 큐 baseline |
| 4 | BP_B1 | Control | [] 브래킷 | Control | 보컬 질감 @ [] |
| 5 | BP_B2 | Control | () 괄호 | Control | 보컬 질감 @ () |
| 6 | BP_B0 | Control | Control | Control | 보컬 질감 baseline |
| 7 | BP_C1 | Control | Control | [] 브래킷 | 보컬 행위 @ [] |
| 8 | BP_C2 | Control | Control | () 괄호 | 보컬 행위 @ () |
| 9 | BP_C0 | Control | Control | Control | 보컬 행위 baseline |

> **참고**: BP_A0, BP_B0, BP_C0는 동일한 가사 (모두 Control). 실제로는 1세트만 생성하고 3회 반복을 baseline으로 공유.
> → 실제 고유 가사 세트: 7개. 총 곡수: 7 × 3 = **21곡** + baseline 3곡 = **24곡**.
> 또는 단순화: 9코드 × 3회 = **27곡** (baseline 중복 허용).

---

## 8. 완성 가사 (전문)

### BP_A1 — 악기 큐 @ [] 브래킷

```
[Intro]

[Verse 1]
어둠 속에 홀로 남은 밤
기억 속에 네가 스며들어

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어

[Verse 2]
[fingerpicked acoustic guitar]
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

### BP_A2 — 악기 큐 @ () 괄호

```
[Intro]

[Verse 1]
어둠 속에 홀로 남은 밤
기억 속에 네가 스며들어

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어

[Verse 2]
(fingerpicked acoustic guitar)
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

### BP_B1 — 보컬 질감 @ [] 브래킷

```
[Intro]

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
[breathy female vocals]
돌아올 수 없는 그 길 위에
나 홀로 서 있어

[Bridge]
언젠가 다시 만날 수 있을까
그날을 기다리며

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어
```

### BP_B2 — 보컬 질감 @ () 괄호

```
[Intro]

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
돌아올 수 없는 그 길 위에 (breathy female vocals)
나 홀로 서 있어

[Bridge]
언젠가 다시 만날 수 있을까
그날을 기다리며

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어
```

### BP_C1 — 보컬 행위 @ [] 브래킷

```
[Intro]

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
[hums softly]
언젠가 다시 만날 수 있을까
그날을 기다리며

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어
```

### BP_C2 — 보컬 행위 @ () 괄호

```
[Intro]

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
(hums softly)
언젠가 다시 만날 수 있을까
그날을 기다리며

[Chorus]
돌아올 수 없는 그 길 위에
나 홀로 서 있어
```

### BP_CTRL — Control (모든 지시 없음)

```
[Intro]

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

---

## 9. 평가 방법

### 9.1 주관 평가 (Leo 청취)

각 곡에서 해당 지시가 삽입된 섹션을 집중 청취.

**지시 A (악기 큐):**
| 코드 | 판정 | 기준 |
|------|------|------|
| 0 | 미반영 | Verse 2에서 핑거피킹 어쿠스틱 기타 인지 불가 |
| 1 | 반영 | Verse 2에서 핑거피킹 어쿠스틱 기타 명확히 인지 |
| ? | 불확실 | 유사한 사운드 있으나 확신 어려움 |

**지시 B (보컬 질감):**
| 코드 | 판정 | 기준 |
|------|------|------|
| 0 | 미반영 | Chorus 2에서 보컬이 male tenor 유지 (SP 기본값) |
| 1 | 반영 | Chorus 2에서 breathy female 보컬로 전환 |
| ? | 불확실 | 보컬 질감 변화 있으나 female/breathy 확신 어려움 |

**지시 C (보컬 행위):**
| 코드 | 판정 | 기준 |
|------|------|------|
| 0 | 미반영 | Bridge에서 가사를 정상 가창 |
| 1 | 반영 | Bridge에서 허밍 또는 비가사 보컬 |
| ? | 불확실 | 보컬 변화 있으나 허밍 아닌 다른 해석 |

### 9.2 객관 평가 (Suno 재분석)

생성된 곡을 Suno 앱에 재업로드하여 재분석 SP/가사에서 키워드 검출.

| 지시 | 검색어 |
|------|--------|
| A | `acoustic guitar`, `fingerpick`, `fingerstyle` |
| B | `breathy`, `female vocal` |
| C | `hum`, `humming` |

### 9.3 분석 항목

| 분석 | 수식 | 의미 |
|------|------|------|
| [] 반영률 | count(1) / total per [] | 브래킷 채널 효과 |
| () 반영률 | count(1) / total per () | 괄호 채널 효과 |
| Control 발생률 | count(1) / total per CTRL | 자연 발생 기저선 |
| 채널 차이 | \|[]반영률 - ()반영률\| | 채널 간 차이 크기 |
| 적합 우위 | 적합채널반영률 - 부적합채널반영률 | 채널 특화 효과 |

---

## 10. 기대 결과

| 지시 | 적합 채널 | [] 반영률 | () 반영률 | Control | 예상 패턴 |
|------|----------|----------|----------|---------|-----------|
| A (악기 큐) | [] | **높음 (>60%)** | 낮음~중간 | 낮음 (<20%) | [] >> () > CTRL |
| B (보컬 질감) | [] | **높음 (>60%)** | 중간 (30~50%) | 낮음 (<20%) | [] > () > CTRL |
| C (보컬 행위) | () | 중간 (30~50%) | **높음 (>60%)** | 낮음 (<10%) | () > [] > CTRL |

**예상 결론**: H1(채널 특화)과 H3([] 우세)의 혼합. 악기 큐는 []에서 강하고, 보컬 행위는 ()에서 강하되, 전반적으로 []가 ()보다 강력한 신호.

---

## 11. 발주 요약

| 항목 | 값 |
|------|-----|
| 시리즈 | S_BP |
| SP 수 | 1 (고정) |
| 가사 변형 | 7 (6 실험 + 1 Control) |
| 곡당 반복 | 3회 |
| 총 곡수 | 21 (7 × 3) |
| 크레딧 (추정) | ~105 (5 × 21) |
| 재분석 | 21곡 전부 |
| 우선순위 | 중간 — ch2 채널 이론 실증, S_PU 이후 발주 |
| 발주처 | sunomusic |

---

## 12. 시사점 (테스트 완료 후)

- H1 확인 시: ch2 "채널별 역할 분리" 이론 실증 → 매뉴얼에 "이 지시는 반드시 []로" 등 채널 처방 추가
- H2 확인 시: 채널 구분은 형식적 → SP 작성 가이드 단순화
- H3 확인 시: "모든 지시는 []로 넣어라" 통일 규칙
- H4 확인 시: 부적합 채널 사용 경고 추가 필요
