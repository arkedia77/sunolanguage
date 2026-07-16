# 표현 레이어 (Expression Layer) v0 설계

**목적**: sunolang 코퍼스(Suno 네이티브 어휘)를 **타 음악 LLM·인간과 연결**하기 위한 다중 표현 DB.
**작성일**: 2026-07-16 | **소스 정본**: `rag/suno_dictionary_v3.json` (v3.2, 코퍼스 556트랙 기준)
**위치**: `sunolang.db` `expr_*` 4테이블 + FTS5 (기존 테이블 불변, 독립 네임스페이스)

---

## 1. 문제와 구조 (코어+어댑터, R-P4)

sunolang의 어휘는 **Suno가 자기 말로 쓰는 언어**다. 이 정본은 그대로 두고(코어),
청중별 **어댑터(레지스터)**를 병렬 보유한다. 번역이 정본을 대체하지 않는다.

encore 3채널 합의(2026-07-16)에서 sunolang의 역할 = **text 어휘 번역 채널**.
이 레이어가 그 채널의 실체다: Suno 어휘 ↔ 타 시스템/인간 어휘의 왕복 변환기.

```
                    ┌─ music_theory_en  (음악가·전문가)
                    ├─ plain_ko         (Leo·한국어 일반인)
suno_native (코어) ─┼─ plain_en         (영어 일반인)
  attested 근거     ├─ llm_prompt       (타 음악생성 AI: MusicGen/Stable Audio류)
                    └─ tags             (기계 교환용 파셋)
        ▲
        └─ inbound_aliases (역방향: dead-zone어·한국어 → attested 대체)
```

## 2. 개념(코어) 추출

- 단위 = **원자 어휘**: 사전 v3.2의 11개 카테고리에서 컴파운드 키(JSON-배열)를 원자로 분해, 합산.
  - instrument 55 · drums 19 · technique 121 · production 62 · mood 33 · tempo_rhythm 20 · dynamics 36 · timbre 26 · vocal 17 · vocal_chorus 14 · harmony 8 = **총 411 원자**
- `attested_count` = 해당 원자를 포함한 사전 엔트리 count 합산 (**salience 순서용 근사치**, 정확 빈도 아님 — 컴파운드 중복 합산 명기)
- v0 제외(v0.1 이월): `genre_vocabulary_map`(264 — 장르명은 시스템 간 이미 공용어), `descriptor_combos`(306 — 컴파운드는 원자 조합으로 재구성 가능)

## 3. 레지스터 정의

| register | audience | 내용 | 생성 방법 |
|---|---|---|---|
| `suno_native` | Suno SP | 정본 그대로 | canonical (사전 추출) |
| `music_theory_en` | 음악가/전문가 | 이론·실무 정식 용어 | authored_llm |
| `plain_ko` | 한국어 인간 | 일상어 설명 1문장 이내 | authored_llm (+무드는 ko_en_mood_glossary 교차참조) |
| `plain_en` | 영어 인간 | 일상어 설명 | authored_llm |
| `llm_prompt` | 타 음악생성 AI | 프롬프트 토큰(짧은 구) | authored_llm |
| `tags` | 기계 | 파셋 태그 배열(JSON) | authored_llm |

저작 원칙: ①Suno 용어를 재발명하지 않는다(코어는 불변) ②plain_ko는 음악 비전공자가 소리를 떠올릴 수 있는 표현 ③확신 낮으면 `confidence: low` 정직 표기.

## 4. 인바운드 별칭 (역방향 연결)

외부(인간/타LLM)가 쓰는 말 → attested Suno 어휘로 안내. **dead-zone 통과 방지가 핵심**.

- 소스 A: `docs/suno_mood_vocabulary_map.md` C절 치환 규칙 (suspenseful→tension+dissonant 등 8쌍)
- 소스 B: `data/ko_en_mood_glossary.json` (ko→en attested, 2026-07-12, attested≥2만)
- 소스 C: `suno_does_not_use` 5규칙 (코드명/진행표기/다이나믹마킹 등) — 별칭이 아닌 **차단 규칙**으로 등재(`kind='blocked'`)

## 5. 스키마

```sql
expr_registers(register PK, audience, description)
expr_concepts(concept_id PK,          -- '{category}:{slug}'
  category, suno_term, attested_count, source_categories,  -- 원자가 나온 사전 카테고리들
  dict_version, is_dead_zone INTEGER DEFAULT 0, created_at)
expr_expressions(id PK, concept_id FK, register FK, text, method, confidence, notes,
  UNIQUE(concept_id, register))
expr_inbound_aliases(id PK, alias_text, alias_lang,       -- 외부어 (ko/en)
  kind,                                -- 'dead_zone' | 'ko_glossary' | 'blocked'
  target_concept_id FK NULL,           -- blocked는 NULL 가능
  replacement_note, source, UNIQUE(alias_text, kind))
expr_fts(FTS5: concept_id UNINDEXED, register, text)      -- 전 레지스터 통합 검색
```

## 6. 사용 시나리오

1. **아웃바운드**: 코퍼스/SP 재료를 타 LLM에 전달 — `suno_term` → `llm_prompt`/`plain_en`
2. **인바운드**: Leo가 "찰랑거리는 기타" → FTS(plain_ko) → concept → `suno_native` attested 표현
3. **dead-zone 가드**: 외부 표현이 별칭 테이블 적중 시 대체어 제시 (reference_matcher 음수필터와 상보)
4. **인간 열람**: 카테고리별 411 원자 대조표 export (`expression_search.py --export`)

## 7. 갱신 정책

- 사전 재빌드(v3.3, B1 트리거) 시 `build_expression_db.py` 재실행 → 신규 원자만 `authored 누락` 리포트 → 증분 저작. 기존 저작분은 suno_term 키로 보존.
- 저작분 정본 = `data/expressions/authored/*.json` (DB는 파생물, 재적재 가능)

## 8. v0.1 이후 후보

- 장르명 크로스맵(Suno 장르판정 드리프트 반영: 'UK Drill'→'Industrial techno' 같은 매핑 등재)
- descriptor_combos 컴파운드 표현
- 타 LLM별 전용 레지스터 분화(MusicGen vs Stable Audio 문법 차이 실증 후)
