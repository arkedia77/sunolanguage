# Corpus 미발굴 패턴 분석 (2026-05-06)

**소스**: 378곡 Suno 재분석 SP 386건 (196,016 chars)

---

## 1. Suno 음색/텍스처 어휘 순위 (자발적 사용)

| 순위 | 단어 | 빈도 | 용도 |
|------|------|------|------|
| 1 | crisp | 160 | 드럼/하이햇/스네어 수식 |
| 2 | bright | 126 | 전반적 음색 |
| 3 | warm | 109 | 베이스/패드/아날로그 |
| 4 | tight | 104 | 리듬/그루브 |
| 5 | dry | 95 | 프로덕션/믹스 |
| 6 | smooth | 78 | 보컬/재즈 |
| 7 | punchy | 41 | 킥/베이스 |
| 8 | shimmering | 21 | 기타/신스 |
| 9 | airy | 14 | 보컬/공간 |
| 10 | clear | 13 | 믹스/보컬 |
| 11 | lush | 12 | 패드/편곡 |
| 12 | gritty | 8 | 디스토션/보컬 |
| 13 | thick | 8 | 베이스/기타 |

**주의**: dark(1), metallic(1), mellow(2) = Suno가 거의 사용하지 않는 텍스처어.
→ "dark"는 장르명에서만 (dark ambient 등), 음색 묘사로는 미사용.

---

## 2. Suno 악기 역할 동사 패턴

Suno가 악기를 묘사할 때 사용하는 동사 문법:

| 악기 | 1순위 동사 | 2순위 | 3순위 |
|------|-----------|-------|-------|
| guitar | plays (193) | follows (65) | provides (43) |
| bass | follows (62) | enters (37) | provides (10) |
| piano | provides (23) | plays (14) | enters (6) |
| drums | feature (59) | consist (37) | play (8) |
| vocal | perform (88) | deliver (49) | - |

**문법 패턴**:
- `[instrument] plays [technique/pattern]` — 가장 일반적
- `[instrument] follows [other instrument]` — 베이스/기타가 다른 악기를 따르는 관계
- `drums feature [description]` — 드럼은 구성을 나열
- `vocals perform/deliver [quality]` — 보컬은 수행/전달

---

## 3. 악기 수식어 빈도

SP에서 Suno가 악기 앞에 붙이는 형용사:

| 수식어 | 빈도 | 적용 대상 |
|--------|------|----------|
| electric | 401 | guitar, bass, piano |
| acoustic | 182 | guitar, bass |
| grand | 47 | piano |
| slap | 47 | bass |
| tenor | 47 | vocals, saxophone |
| melodic | 27 | fills, lines |
| subtle | 27 | drums, effects |
| rhythmic | 25 | guitar, pattern |
| baritone | 23 | vocals |
| fretless | 14 | bass |
| polyphonic | 14 | synth |
| syncopated | 12 | pattern, rhythm |
| staccato | 11 | notes, guitar |
| upright | 10 | bass |
| atmospheric | 9 | synth, pad |

---

## 4. 감정/무드 어휘 — Suno 극도로 빈약 확인

Suno가 자발적으로 사용하는 감정 형용사:
- intimate: **120회** (압도적 1위)
- aggressive: 11회
- cinematic: 3회
- melancholic: 2회

**나머지 0회**: euphoric, nostalgic, wistful, triumphant, vulnerable, uplifting, anthemic, brooding, sultry, ethereal, haunting, playful, bittersweet, yearning, defiant, contemplative, whimsical, serene, somber, exuberant

→ **확정**: Suno는 감정을 형용사로 묘사하지 않음. 대신 음색(crisp/warm/bright)과 편곡(sparse/layered/intimate)으로 감정을 암시.
→ SP에서 mood 단어를 쓰면 Suno가 이해는 하지만(수동 어휘), 자기가 쓰지는 않음(비네이티브).

---

## 5. 전환/다이내믹스 어휘

| 표현 | 빈도 | 용도 |
|------|------|------|
| transitions from/to/into | 18 | 섹션 전환 |
| shifts into | 3 | 장르/무드 변화 |
| opens with | 3 | 곡 시작 |
| sudden | 10 | 급격한 변화 |
| crescendo | 4 | 점증 |
| rubato | 6 | 템포 유연성 |
| interplay between | 79 | 악기 간 상호작용 |
| minimalist | 46 | 편곡 밀도 |
| layered | 44 | 편곡 밀도 |

---

## 6. 사전 v3.0 반영 대상

### 신규 추가 필요
- texture_hierarchy: crisp > bright > warm > tight > dry > smooth > punchy (빈도순)
- verb_grammar: 각 악기별 동사 패턴 (Suno 문법 규칙)
- modifier_map: 악기별 허용 수식어 목록
- mood_gap: Suno가 사용하지 않는 감정어 목록 (suno_does_not_use 확장)

### 기존 업데이트
- timbre_texture: 현 23개 → 빈도 데이터 보강
- dynamics_structure: interplay(79)를 핵심 어휘로 승격
- mood_emotion: "Suno 자발 감정어 4개만" 명시

---

## 7. sunolang 핵심 인사이트 강화

### 기존 발견 재확인
- **Suno 3계층**: 이 분석으로 더 선명해짐
  - 네이티브: crisp(160), warm(109), tight(104) — 자발 사용
  - 수동이해: dark, euphoric, nostalgic — 지시하면 반응하지만 자발 0회
  - 데드존: 코드명, 다이내믹 마킹 — 무시

### 신규 발견
- **Suno 문법 규칙**: 악기별로 정해진 동사 패턴이 있음 (guitar plays / bass follows / drums feature)
- **감정 전달 방식**: 형용사가 아닌 음색+편곡 조합으로 감정 암시
- **"intimate" 독점**: 감정어 중 유일하게 고빈도 = Suno의 기본 무드 설정
