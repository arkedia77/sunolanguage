# SP 구조 심층 분석 (445곡)

**분석일**: 2026-05-14
**데이터**: merged_4values.json 437곡 → 445 reanalysis SP

---

## 1. SP 문장 구조

### 문장 수 분포
- 평균: 7.1문장, 중앙값: 7, 범위: 5~11
- 6~8문장이 87.9% (391/445)

| 문장수 | 곡수 | 비율 |
|--------|------|------|
| 5 | 11 | 2.5% |
| 6 | 115 | 25.8% |
| **7** | **183** | **41.1%** |
| 8 | 93 | 20.9% |
| 9 | 37 | 8.3% |
| 10~11 | 6 | 1.3% |

### 문장 위치별 주제 (Suno SP 문법)

| 위치 | 1위 | 2위 | 3위 |
|------|-----|-----|-----|
| #1 | GENRE 63% | VOCAL 16% | INSTRUMENT 8% |
| #2 | **INSTRUMENT 91%** | VOCAL 5% | DRUMS 2% |
| #3 | INSTRUMENT 66% | VOCAL 14% | DRUMS 13% |
| #4 | INSTRUMENT 35% | DRUMS 30% | VOCAL 21% |
| #5 | VOCAL 32% | INSTRUMENT 22% | DRUMS 17% |
| #6 | TEMPO/KEY 34% | INSTRUMENT 22% | VOCAL 22% |

### 마지막 문장 주제

| 유형 | 비율 |
|------|------|
| TEMPO/KEY | 50.1% |
| VOCAL | 16.4% |
| ARRANGEMENT | 13.5% |
| INSTRUMENT | 11.9% |

### SP 7문장 공식

```
#1  {장르 선언}                    ← "K-Pop ballad with R&B influences."
#2  {주요 악기 묘사}               ← "Clean electric guitar plays arpeggiated chords..."
#3  {보조 악기 또는 베이스}        ← "Electric bass follows the kick drum pattern..."
#4  {드럼/퍼커션 또는 추가 악기}   ← "The drums consist of a dry, tight kick..."
#5  {보컬 묘사}                    ← "Breathy, intimate male vocals..."
#6  {어레인지먼트 또는 프로덕션}   ← "The arrangement is sparse..."
#7  {템포/조성}                    ← "72 BPM in E Major, 4/4 time signature."
```

---

## 2. SP 동사 체계

| 동사 | 빈도 | 역할 |
|------|------|------|
| plays | 264 | 악기 연주 묘사 |
| features | 205 | 편성 소개 |
| provides | 176 | 보조적 역할 부여 |
| follows | 162 | 다른 파트 추종 |
| fills | 107 | 빈 공간 채우기 |
| enters | 95 | 시간적 진입 |
| transitions | 64 | 전환 |
| accents | 56 | 강세 |
| maintains | 23 | 유지 |
| alternates | 19 | 교대 |

핵심 동사 6개(plays/features/provides/follows/fills/enters)가 전체의 85%+.

---

## 3. 수식어 공기 클러스터

### 서정 클러스터 (Lyrical)
breathy+intimate(1.87), intimate+soft(1.86), soft+warm(1.80), breathy+soft(1.72)
→ K-Ballad/R&B 장르의 핵심 수식어 조합

### 선명 클러스터 (Crisp)
bright+crisp(1.65), crisp+tight(1.68)
→ Funk/Electronic/K-Pop Dance 장르

### 기본 클러스터 (Neutral)
clean+subtle(1.15), clean+crisp(1.23), clean+warm(1.16)
→ 장르 불문 범용 조합

### 해석
lift > 1.5인 쌍은 특정 장르에서 "함께 나타나도록 설계된" 표현. SP 작성 시 이 쌍을 유지하면 Suno의 학습 패턴에 부합.

---

## 4. 악기별 기본 수식어 (Default Modifier)

| 악기 | 1위 (비율) | 2위 | 3위 |
|------|-----------|-----|-----|
| electric guitar | clean (64%) | distorted (11%) | rhythmic (3%) |
| acoustic guitar | fingerpicked (42%) | nylon-string (12%) | steel-string (7%) |
| electric bass | melodic (35%) | warm (20%) | clean (11%) |
| kick drum | soft (24%) | dry (14%) | tight (11%) |
| bass guitar | slap (35%) | melodic (25%) | electric (17%) |
| hi-hat | eighth-note (20%) | tight (19%) | closed (10%) |
| grand piano | resonant (75%) | — | — |
| cello | solo (50%) | legato (11%) | — |
| trumpet | muted (50%) | — | — |

수식어 미지정 시 Suno가 부여하는 "기본값":
- electric guitar = **clean**
- acoustic guitar = **fingerpicked**
- bass guitar = **slap** (K-Funk 영향)
- kick drum = **soft** (K-Ballad 우세 영향)

---

## 5. 장르별 수식어 프로파일

| 장르 | 1위 | 2위 | 3위 | 배타적 수식어 |
|------|-----|-----|-----|--------------|
| Pop (193) | clean 65% | subtle 45% | breathy 39% | — |
| Electronic (43) | clean 77% | subtle 65% | crisp 60% | — |
| Ballad (43) | clean 72% | breathy 58% | subtle 56% | **warm 49%** |
| R&B (38) | clean 66% | breathy 55% | soft 50% | — |
| Folk (36) | clean 75% | subtle 53% | soft 47% | — |
| Rock (25) | clean 64% | distorted 36% | subtle 32% | **distorted 36%** |
| Funk (13) | clean 92% | subtle 69% | breathy 62% | **punchy 38%** |
| Bossa Nova (9) | clean 78% | soft 78% | subtle 67% | **sparse 56%** |

### 장르 감별 수식어
- **warm** → Ballad 신호 (49% vs 타장르 23%)
- **distorted** → Rock 신호 (36% vs 7%)
- **punchy** → Funk 신호 (38% vs 10%)
- **sparse + soft** → Bossa Nova 신호 (56%+78%)

---

## 6. 문장 시작 패턴 (The X ...)

| 패턴 | 빈도 | 역할 |
|------|------|------|
| The tempo is | 164 | 마지막 문장 |
| The arrangement is | 106 | 편곡 설명 |
| The arrangement features | 104 | 편곡 소개 |
| A clean electric | 73 | 일렉기타 묘사 |
| The bass guitar | 61 | 베이스 묘사 |
| The arrangement centers | 58 | 편곡 초점 |
| The production is | 43 | 프로덕션 |
| The drum kit | 41 | 드럼 묘사 |
| The vocal performance | 35 | 보컬 묘사 |
| The track is | 29 | 전체 묘사 |
