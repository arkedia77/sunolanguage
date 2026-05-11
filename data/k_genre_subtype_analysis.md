# 비-Ballad K-장르 서브타입 심층 분석 (2026-05-11)

DB 385행 중 K-Indie(76행), K-Funk(33행), K-Rock(40행) 서브타입별 악기·보컬·주법 시그니처 비교.
K-Ballad(163행) 분석 결과와 교차 비교 포함.

---

## 1. K-Indie (76행, 36개 고유 장르)

### 서브타입 분포

| 서브타입 | 행수 | 핵심 정체성 |
|----------|------|-----------|
| Pop | 29 | 인디팝 — 일렉+어쿠스틱 균형 |
| Folk | 22 | 포크 — 어쿠스틱 100%, 미니멀 |
| Rock | 6 | 인디록 — 일렉+드럼 풀셋 |
| Ballad | 6 | 인디발라드 — 아르페지오+breathy |
| Acoustic | 6 | 어쿠스틱 — Folk와 유사하나 더 단순 |
| Jazz | 4 | 재즈팝 — 클린+스윙 |

### 악기 시그니처

| 악기 | Pop | Folk | Rock | Ballad | Acoustic | Jazz |
|------|-----|------|------|--------|----------|------|
| electric guitar | **97%** | 27% | **100%** | — | — | **100%** |
| acoustic guitar | — | **100%** | — | **83%** | **100%** | — |
| electric bass | 48% | 32% | — | **67%** | 33% | **100%** |
| drums | 45% | — | **100%** | — | — | 75% |
| kick | 76% | 27% | 67% | 33% | — | **100%** |
| snare | 66% | — | **100%** | — | — | **100%** |
| pad | 17% | — | — | — | — | — |

#### 인사이트
- **Pop vs Folk**: Pop은 일렉 97% + kick 76%로 밴드 편성, Folk는 어쿠스틱 100% + 리듬 섹션 최소
- **Rock**: K-Ballad Rock과 동일하게 일렉 100% + 풀 리듬 섹션. K-Indie Rock은 더 빠름(109 BPM vs 72 BPM)
- **Ballad**: K-Ballad Folk와 거의 동일 시그니처 (acoustic 83%, breathy 100%, arpeggiated 83%)
- **Jazz**: 일렉 + 일렉 베이스 조합. K-Ballad Jazz(grand piano 60%)와 달리 피아노 없음

### 보컬 시그니처

| 보컬 | Pop | Folk | Rock | Ballad | Acoustic | Jazz |
|------|-----|------|------|--------|----------|------|
| breathy | 52% | 68% | — | **100%** | 50% | — |
| soft | 62% | **86%** | — | **83%** | **83%** | **100%** |
| intimate | 48% | 64% | — | **100%** | **83%** | — |
| warm | 31% | 32% | — | **100%** | — | **75%** |
| tenor | 48% | — | **67%** | — | — | — |
| baritone | 10% | **64%** | 33% | — | **50%** | **75%** |

#### 인사이트
- **Folk/Ballad/Acoustic**: breathy+soft+intimate 삼중주 = K-Indie 서정 계열 핵심
- **Pop**: tenor 48%로 상대적으로 밝은 음색
- **Jazz**: soft 100% + baritone 75% + warm 75% → 저음역 따뜻한 보컬
- **Rock**: tenor 67%, breathy/soft 없음 → K-Indie 중 유일하게 "서정" 탈피

### 주법 시그니처

| 주법 | Pop | Folk | Rock | Ballad | Acoustic | Jazz |
|------|-----|------|------|--------|----------|------|
| clean | **100%** | 32% | **100%** | **83%** | 50% | **100%** |
| syncopated | **76%** | — | **83%** | — | 33% | 75% |
| steady | 55% | **95%** | 83% | — | **100%** | — |
| reverb | 69% | **77%** | **100%** | 67% | **83%** | — |
| fingerstyle | — | **55%** | — | 33% | — | — |
| arpeggiated | 21% | — | — | **83%** | — | — |
| eighth-note | 17% | 55% | — | — | 50% | — |

#### 인사이트
- **Pop**: clean 100% + syncopated 76% = 깔끔하지만 리듬감 있음
- **Folk**: steady 95% + fingerstyle 55% = 리듬 변화 최소, 핑거 주법
- **Ballad**: arpeggiated 83% = K-Ballad 계열과 동일한 핵심 주법
- **Rock**: clean 100% + syncopated 83% + reverb 100% = 인디 록 특유의 공간감

### 통계

| 항목 | Pop | Folk | Rock | Ballad | Acoustic | Jazz |
|------|-----|------|------|--------|----------|------|
| 평균 BPM | 93 | 75 | 109 | 72 | 82 | 88 |
| 평균 SP 길이 | 527자 | 476자 | 594자 | 451자 | 477자 | 480자 |

---

## 2. K-Funk (33행, 22개 고유 장르)

### 서브타입 분포

| 서브타입 | 행수 | 핵심 정체성 |
|----------|------|-----------|
| Pure Funk-Pop | 14 | K-Pop + 펑크 = 브라스+슬랩 |
| J-Fusion | 5 | J-Pop/J-Rock + Funk |
| Disco-Funk | 5 | 디스코+펑크 퓨전 |
| Synth-Funk | 3 | 신스 중심 펑크 |
| Indie-Funk | 2 | 인디 + 펑크 |

### 악기 시그니처

| 악기 | Pure Funk-Pop | J-Fusion | Disco-Funk | Synth-Funk |
|------|--------------|----------|------------|-----------|
| electric guitar | **93%** | **100%** | **100%** | 67% |
| brass | **71%** | — | **60%** | — |
| synth/synthesizer | 64% | **80%** | **100%** | **100%** |
| pad | 50% | — | **80%** | **100%** |
| kick | **93%** | 60% | — | — |
| snare | **93%** | **100%** | 80% | **100%** |
| bass guitar | — | **80%** | — | — |

#### 인사이트
- **Pure Funk-Pop**: 브라스 71%가 핵심 차별점. K-Indie/K-Rock에 브라스 거의 0%
- **Disco-Funk**: 신스+패드 조합 = 전자음 기반 펑크. 브라스도 60%로 하이브리드
- **Synth-Funk**: 신스+패드 100%, 일렉 기타 67%로 가장 전자음 비중 높음
- **J-Fusion**: 일렉 기타+베이스 기타 조합, 브라스 없음 → 밴드 편성 펑크

### 보컬 시그니처

| 보컬 | Pure Funk-Pop | J-Fusion | Disco-Funk | Synth-Funk |
|------|--------------|----------|------------|-----------|
| bright | **100%** | **80%** | **100%** | **100%** |
| breathy | 36% | — | — | — |
| falsetto | **29%** | — | — | — |
| rap | **29%** | — | — | — |
| tenor | — | **60%** | — | — |
| smooth | — | 40% | — | — |

#### 인사이트
- **bright = K-Funk 전체 기본값** (85%): K-Ballad의 breathy(70~90%)에 대응
- **falsetto + rap**: Pure Funk-Pop만의 특징. 다른 K-장르에서 매우 드묾
- **K-Ballad와 정반대**: K-Ballad=breathy+soft+intimate, K-Funk=bright+energetic

### 주법 시그니처

| 주법 | Pure Funk-Pop | J-Fusion | Disco-Funk | Synth-Funk |
|------|--------------|----------|------------|-----------|
| syncopated | **100%** | **100%** | **100%** | — |
| slap | **100%** | **100%** | **80%** | **100%** |
| staccato | **100%** | — | 60% | 67% |
| clean | **100%** | 80% | 80% | 67% |
| muted | 71% | 60% | — | — |
| sixteenth-note | 43% | — | **60%** | — |
| driving | — | — | — | **67%** |

#### 인사이트
- **slap = K-Funk DNA**: 전 서브타입에서 80~100%. 다른 K-장르에서 0%
- **syncopated**: K-Funk 94%로 가장 높음 (K-Indie 45%, K-Rock 45%)
- **staccato**: K-Funk 73%로 독점적 (K-Indie 0%, K-Rock 0%)
- **sixteenth-note**: 52% — 16분음표 그루브가 펑크 리듬 핵심

### 통계

| 항목 | Pure Funk-Pop | J-Fusion | Disco-Funk | Synth-Funk |
|------|--------------|----------|------------|-----------|
| 평균 BPM | 116 | 121 | 118 | 122 |
| 평균 SP 길이 | 497자 | 561자 | 488자 | 491자 |

---

## 3. K-Rock (40행, 32개 고유 장르)

### 서브타입 분포

| 서브타입 | 행수 | 핵심 정체성 |
|----------|------|-----------|
| Punk/Pop-Punk | 11 | 고속+파워코드+디스토션 |
| J-Rock Fusion | 8 | J-Rock + K-Pop 혼성 |
| Pop-Rock | 6 | 팝 기반 록 |
| Indie Rock | 5 | 인디 감성 록 |
| Soft Rock/Ballad | 5 | 느린 록 발라드 |
| K-Rock Pure | 3 | 순수 K-Rock |

### 악기 시그니처

| 악기 | Punk | J-Rock | Pop-Rock | Indie Rock | Soft Rock | K-Rock Pure |
|------|------|--------|----------|------------|-----------|-------------|
| electric guitar | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** |
| bass guitar | **82%** | **75%** | **83%** | 60% | 60% | **100%** |
| drums | **73%** | 62% | 50% | **100%** | 80% | **100%** |
| snare | 82% | **88%** | 83% | **100%** | 80% | 67% |
| hi-hat | 64% | **75%** | **83%** | **100%** | — | — |
| kick | 45% | 75% | **100%** | 80% | **100%** | **100%** |
| pad | — | — | — | — | **80%** | — |

#### 인사이트
- **electric guitar 100% = K-Rock 전체 필수**: 서브타입 불문
- **Soft Rock**: pad 80%가 유일한 차별점 — 공간감/앰비언스 강조
- **Punk**: bass guitar 82% + drums 73% = 전형적 3피스 밴드
- **Indie Rock**: hi-hat 100% + snare 100% = 가장 완전한 드럼 세트

### 보컬 시그니처

| 보컬 | Punk | J-Rock | Pop-Rock | Indie Rock | Soft Rock |
|------|------|--------|----------|------------|-----------|
| bright | 36% | **88%** | **100%** | — | — |
| tenor | — | **75%** | **67%** | **80%** | 80% |
| powerful | — | 38% | — | — | **60%** |
| breathy | — | — | — | — | **80%** |
| soft | — | — | — | — | **80%** |
| rap | 27% | 38% | — | — | — |
| counterpoint | — | — | — | — | — |

#### 인사이트
- **Punk**: 보컬 묘사 최소 — Suno가 펑크 보컬을 구체적으로 묘사하지 않음
- **J-Rock**: bright 88% + tenor 75% = 가장 밝고 높은 보컬
- **Soft Rock**: breathy 80% + soft 80% = K-Ballad와 겹침 (장르 경계)
- **rap 출현**: Punk 27%, J-Rock 38% — K-Rock에서도 랩 보컬 감지

### 주법 시그니처

| 주법 | Punk | J-Rock | Pop-Rock | Indie Rock | Soft Rock |
|------|------|--------|----------|------------|-----------|
| distorted | **91%** | **75%** | — | — | — |
| power chord | **91%** | — | **83%** | — | — |
| palm-muted | **91%** | **75%** | — | — | — |
| driving | **100%** | **75%** | 67% | — | — |
| overdriven | — | — | — | **80%** | — |
| clean | — | — | **83%** | **100%** | **100%** |
| arpeggiated | — | — | — | — | **100%** |
| syncopated | — | — | **83%** | **100%** | — |
| delay | — | — | — | — | **100%** |

#### 인사이트
- **Punk**: distorted+power chord+palm-muted+driving = 4대 주법 모두 90%+
- **J-Rock**: Punk과 유사하나 power chord 없음, palm-muted 비중 약간 낮음
- **Indie Rock**: clean 100% + overdriven 80% = 클린/오버드라이브 전환 스타일
- **Soft Rock**: arpeggiated 100% + clean 100% + delay 100% = K-Ballad 주법과 동일
- **Pop-Rock**: syncopated 83% + power chord 83% = 리듬감+파워 겸비

### 통계

| 항목 | Punk | J-Rock | Pop-Rock | Indie Rock | Soft Rock | K-Rock Pure |
|------|------|--------|----------|------------|-----------|-------------|
| 평균 BPM | **154** | **151** | 132 | 107 | **73** | **148** |
| 평균 SP 길이 | 534자 | 527자 | 531자 | 576자 | 514자 | 562자 |

---

## 4. 3개 장르 교차 비교 + K-Ballad

### 4.1 장르 DNA 핵심 어휘

| 속성 | K-Ballad | K-Indie | K-Funk | K-Rock |
|------|----------|---------|--------|--------|
| 핵심 악기 | piano/acoustic | acoustic/electric | electric+brass | electric 100% |
| 보컬 기본값 | breathy(80%) | soft(70%) | **bright(85%)** | tenor(50%) |
| 핵심 주법 | arpeggiated | steady/clean | **slap+syncopated** | **distorted+driving** |
| 평균 BPM | 72 | 86 | **118** | **135** |
| SP 평균 길이 | 489자 | 502자 | 515자 | **539자** |

### 4.2 장르 구분 키워드 (Suno 네이티브)

K-장르 간 **배타적** 출현 어휘:

| 어휘 | K-Ballad | K-Indie | K-Funk | K-Rock |
|------|----------|---------|--------|--------|
| slap | — | — | **85%** | — |
| staccato | — | — | **73%** | — |
| brass | — | — | **52%** | — |
| sixteenth-note | — | — | **52%** | — |
| power chord | — | — | — | **65%** |
| distorted | — | — | — | **62%** |
| palm-muted | — | — | — | **52%** |
| overdriven | — | — | — | **42%** |
| driving | — | — | — | **65%** |
| fingerstyle | — | 21% | — | — |
| grand piano | 40% | — | — | — |
| string section | 15% | — | — | — |

### 4.3 장르 경계 겹침

1. **K-Indie Ballad ≈ K-Ballad Folk**: acoustic+breathy+arpeggiated. 구분 어려움.
2. **K-Rock Soft Rock ≈ K-Ballad Rock**: arpeggiated+clean+delay. BPM만 다름(73 vs 72).
3. **K-Indie Rock ≈ K-Rock Indie Rock**: syncopated+clean+reverb. 템포 차이(109 vs 107 BPM)도 미미.
4. **K-Funk J-Fusion**: 다른 K-장르와 겹침 없음 — 가장 독립적.

### 4.4 SP 길이 인사이트

- 복잡 편성 = 긴 SP: K-Rock(539자) > K-Funk(515자) > K-Indie(502자) > K-Ballad(489자)
- 서브타입 최대: K-Indie Rock(594자), K-Indie Rock(576자), K-Rock Pure(562자)
- 서브타입 최소: K-Indie Ballad(451자), K-Indie Folk(476자)
- 미니멀 편성(어쿠스틱+보컬) → SP 짧음, 풀밴드+이펙트 → SP 김

### 4.5 v5.5 관련

- key change(pump-up modulation): K-Ballad/K-Rock에서 발견, K-Funk/K-Indie에서 미발견
- K-Funk의 brass+slap 조합은 v5.0에서도 v5.5에서도 동일 → 버전 불변 어휘
