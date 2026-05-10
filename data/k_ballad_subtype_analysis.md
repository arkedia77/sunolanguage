# K-Ballad 서브타입별 어휘 심층 분석 (2026-05-10)

DB 385행 중 K-Ballad 163행을 10개 서브타입으로 분류하여 악기·보컬·주법·프로덕션 비교.

## 서브타입 분포

| 서브타입 | 행수 | 핵심 정체성 |
|----------|------|-----------|
| R&B | 33 | 리듬+전자음 발라드 |
| Baritone | 29 | 피아노+성악적 발라드 |
| Plain | 30 | 무표지 K-Pop 발라드 |
| Folk | 22 | 어쿠스틱 미니멀 |
| Acoustic | 20 | 기타 중심 발라드 |
| Indie | 10 | 인디 감성 |
| Jazz | 5 | 재즈 영향 발라드 |
| Rock | 5 | 록 발라드 |
| Tenor | 5 | 테너 보컬 중심 |
| Synth | 4 | 신스팝 발라드 |

## 악기 시그니처

| 악기 | R&B | Folk | Acoustic | Baritone | Plain | Rock | Jazz |
|------|-----|------|----------|----------|-------|------|------|
| electric guitar | **85%** | 23% | 20% | 24% | 33% | **100%** | 60% |
| acoustic guitar | 12% | **100%** | **100%** | 41% | 50% | 0% | 0% |
| piano/grand | 15% | 0% | 0% | **72%/69%** | 50%/37% | 20% | 60%/40% |
| synth | **61%** | 5% | 0% | 14% | 13% | 20% | 0% |
| sub-bass | 21% | 0% | 0% | 0% | 10% | 0% | 0% |
| string section | 0% | 0% | 0% | **41%** | 10% | 40% | 0% |
| electric bass | 30% | 41% | 40% | 17% | 13% | 0% | 40% |

### 인사이트
- **R&B**: 일렉 기타 + 신스 조합이 핵심. 서브베이스 존재.
- **Folk/Acoustic**: 어쿠스틱 기타 100%. 신스/서브베이스 0%.
- **Baritone**: 그랜드 피아노 69% + 스트링 섹션 41% → 클래시컬 편성
- **Rock**: 일렉 기타 100% + 베이스 기타 60%. 어쿠스틱 0%.

## 보컬 시그니처

| 보컬 묘사 | R&B | Folk | Acoustic | Baritone | Plain | Rock | Jazz |
|-----------|-----|------|----------|----------|-------|------|------|
| breathy | 76% | 68% | 75% | **90%** | **90%** | 80% | 20% |
| soft | 64% | **82%** | 65% | 28% | 63% | 80% | 40% |
| intimate | 36% | 64% | 65% | **72%** | 53% | 20% | 20% |
| falsetto | **36%** | 0% | 0% | 7% | 7% | 0% | **40%** |
| tenor | **42%** | 0% | 35% | 0% | 23% | **80%** | 40% |
| baritone | 15% | **64%** | 45% | **100%** | 23% | 20% | 60% |
| smooth | **39%** | 9% | 5% | 0% | 3% | 40% | **80%** |
| powerful | 6% | 0% | 0% | 7% | 20% | **60%** | 0% |
| conversational | 18% | 23% | 20% | 3% | 10% | 0% | **40%** |

### 인사이트
- **breathy는 K-Ballad 전체의 기본값** (대부분 70~90%)
- **R&B**: falsetto(36%) + smooth(39%) + tenor(42%) — 기교적 보컬
- **Folk**: soft(82%) + baritone(64%) — 편안한 저음 보컬
- **Rock**: powerful(60%) + belted(40%) — 강한 보컬
- **Jazz**: smooth(80%) + conversational(40%) — 재즈 보컬 특유의 톤

## 주법 시그니처

| 주법 | R&B | Folk | Acoustic | Baritone | Plain | Rock | Jazz |
|------|-----|------|----------|----------|-------|------|------|
| syncopated | **52%** | 0% | 15% | 7% | 7% | 0% | **60%** |
| steady | 21% | **95%** | **75%** | 31% | 33% | 20% | 0% |
| fingerstyle | 6% | **55%** | 40% | 7% | 3% | 0% | 0% |
| fingerpicked | 12% | **45%** | **55%** | 24% | 23% | 0% | 0% |
| arpeggiated | 24% | 23% | 30% | 21% | **53%** | **100%** | 0% |
| swing | 0% | 0% | 0% | 0% | 0% | 0% | **80%** |
| walking | 0% | 0% | 0% | 0% | 0% | 20% | **40%** |

### 인사이트
- **R&B = syncopated**(52%), **Folk = steady**(95%) — 리듬 대비가 가장 극명
- **Folk/Acoustic**: fingerstyle/fingerpicked가 핵심 기법
- **Jazz**: swing(80%) + syncopated(60%) — 재즈 고유 리듬
- **Rock의 arpeggiated 100%**: 예상 외. 록 발라드에서 Suno가 아르페지오를 필수로 인식

## SP 길이

| 서브타입 | 평균 길이 |
|----------|----------|
| Jazz | 527자 |
| Rock | 514자 |
| R&B | 508자 |
| Baritone | 508자 |
| Indie | 476자 |
| Folk | 466자 |
| Acoustic | 459자 |
| Plain | 454자 |
| Synth | 430자 |

복잡한 편성(Jazz/Rock/R&B)일수록 SP가 길고, 미니멀 편성(Acoustic/Plain/Synth)일수록 짧다.

## 가사 브래킷 패턴

- **R&B**: `[falsetto]`, `[smooth male vocals]`, `[sub-bass enters]` — 보컬 기교 큐
- **Folk**: `[fingerpicked acoustic guitar]`, `[shaker enters]` — 어쿠스틱 악기 진입
- **Baritone**: `[grand piano playing sustained chords]`, `[legato strings enter]` — 오케스트라적
- **Plain**: `[breathy male vocals]`가 17회로 압도적 — 무표지 발라드의 기본 보컬 큐

## SP 작성 시사점

1. **R&B 발라드**: electric guitar + synth + sub-bass, syncopated, falsetto/smooth vocal
2. **Folk 발라드**: acoustic guitar + fingerstyle, steady rhythm, soft/intimate/baritone vocal  
3. **Acoustic 발라드**: acoustic guitar + fingerpicked, steady, breathy/intimate vocal
4. **Baritone 발라드**: grand piano + string section, legato, breathy/intimate/baritone vocal
5. **Rock 발라드**: electric guitar + arpeggiated, powerful/belted/tenor vocal, delay
6. **Jazz 발라드**: piano + upright bass, swing/syncopated, smooth/conversational vocal
