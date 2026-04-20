# Instrument 슬롯 3계 분할 설계안

**작성일**: 2026-04-20
**맥락**: Phase V3.1 R4 잔여 항목. SP instrument 슬롯 1,663건(39% 집중) 의미 세분화
**전제**: 슬롯명은 `.kit` / `.layer` / `.role` (Leo 네이밍)

---

## 1. 문제 정의

현재 `parse_slot_entities_v3.py`의 `instrument` 슬롯은 단일 분류다.
"acoustic guitar"(126건)과 "808 bass"(3건)가 같은 층위에 놓여 **책 3~4장의 어휘 해상도가 떨어진다**.

한 문장에 3개 정보가 섞여 있다:
- *어떤 악기인가* (family)
- *곡에서 어떤 텍스처 층인가* (lead/rhythm/bass…)
- *기능적으로 무엇을 하는가* (plays/follows/provides…)

---

## 2. 3계 분할안

| 계 | 의미 | 추출 단서 | 폐쇄형(closed)/개방형(open) |
|---|---|---|---|
| **`.kit`** | 악기 **family** (구조적 분류) | 엔티티 자체 사전 매핑 | 8 family (폐쇄형) |
| **`.layer`** | 곡 내 **텍스처 층** | 문장 구문 + 수식어 | 6 layer (폐쇄형) |
| **`.role`** | 기능 **동사** | sentence의 주동사 | 7 role (폐쇄형) |

### 2.1 `.kit` — 악기 family (8개)

현재 v3 데이터 기반 8-family 분류 (총 1,663건 전원 귀속):

| family | 건수 | 대표 엔티티 |
|---|---:|---|
| `guitar` | 702 | electric guitar, acoustic guitar, clean/distorted/palm-muted… |
| `bass` | 507 | electric bass, bass guitar, synth bass, slap bass, sub-bass, 808 bass |
| `synth` | 247 | synthesizer, pad, synth pad, string pad |
| `keys` | 132 | piano, grand piano, electric piano, rhodes |
| `strings` | 45 | strings, cello, violin, orchestral strings |
| `brass` | 29 | brass section, trumpet, saxophone, muted trumpet |
| `reeds` | 2 | saxophone, harmonica (재분류 가능) |
| `other` | — | 추후 신곡 수집 시 확장 |

→ **파서 변경 최소**: 엔티티 사전에 `"family": "guitar"` 필드만 추가.

### 2.2 `.layer` — 텍스처 층 (6개)

| layer | 판별 구문 | 우선순위 |
|---|---|---|
| `lead` | "plays a melody", "lead line", "melodic line" | 1 |
| `rhythm` | "plays rhythm", "strums chords", "comping", "chord progression" | 2 |
| `bass` | family=bass 자동 / "bassline", "low-end" | 3 |
| `pad` | family=synth 서브셋 + "sustained", "background texture" | 4 |
| `counter` | "counter-melody", "ornament", "answering phrase" | 5 |
| `fill` | "fills", "transitional", "brief lick" | 6 |

→ **개별 엔티티는 복수 layer 가능**: 같은 "electric guitar"가 한 문장에선 lead, 다른 문장에선 rhythm.
→ layer가 결정 불가인 경우는 `unspecified`로 두되, 비율 집계에서 제외.

### 2.3 `.role` — 기능 동사 (7개)

현 데이터에서 추출된 role-hint 동사 **1,026건**의 분포:

| role | 대표 동사 | 빈도 |
|---|---|---:|
| `execute` | plays, playing | 356 |
| `groove_lock` | follows (the kick pattern), locks (with) | 269 |
| `support` | provides, supports | 173 |
| `fill` | fills, filling | 109 |
| `layer_on` | layers, doubles, adds | 17 |
| `lead_out` | leads, carries, outlines | ~10 |
| `sustain` | holds, sustains, drones | (신규 추출) |

→ role은 **문장 주동사 기반**. 엔티티 사전에 들어가지 않음.

---

## 3. 구현 시나리오

### 3.1 데이터 구조

기존:
```json
{"slot": "instrument", "entity": "electric bass", "sentence": "..."}
```

변경 후:
```json
{
  "slot": "instrument",
  "kit": "bass",
  "layer": "bass",
  "role": "groove_lock",
  "entity": "electric bass",
  "sentence": "..."
}
```

→ **기존 `slot: instrument` 유지** (하위호환). 3개 필드 추가만.

### 3.2 파이프라인 영향

| 파일 | 변경 |
|---|---|
| `parse_slot_entities_v3.py` | `INSTRUMENT_ENTITIES`에 family 메타 추가 + `classify_layer()` / `classify_role()` 함수 신설 |
| `extract_templates.py` | 영향 없음 (엔티티 치환은 그대로) |
| `measure_echo.py` | 영향 없음 |
| `lexical_search_cli.py` | FTS5 컬럼 3개 추가 → 쿼리 예: `kit:bass layer:bass` |
| (신규) `slot_genre_matrix.py` | 3계 교차표로 4장 원자재 생성 |

### 3.3 작업 분량 추정

- `.kit` 매핑 사전: 30분 (39 엔티티 × 8 family)
- `.layer` 분류 규칙: 2~3시간 (구문 판별 + 검증)
- `.role` 동사 사전: 1시간
- 파서 개조 + 재파싱: 1시간
- **총 5~6시간**

---

## 4. Leo 결정 필요

1. **8-family 분류 체계 확정**
   - reeds는 brass에 흡수할지 / 신설 유지할지
   - "synth pad"는 `synth` vs `pad` layer — family=synth, layer=pad 이중 태그 OK?

2. **layer 6개 범주 확정**
   - `counter` 범주가 현 데이터에 거의 없음 — 제거하고 5개로 갈지

3. **role 7개 범주 확정**
   - `execute`(plays)가 34% 차지해 분별력 낮음 → 더 잘게 쪼갤지
   - 아니면 plays + 수식어(syncopated/melodic) 조합을 role로 재정의

4. **적용 시점**
   - V3.1 마무리로 지금 진행 / V3.2 Wave 1 수집 후 진행

---

## 5. 예상 산출물

- `data/reanalysis_v2/sp_entities_v3_split.json` — 3계 필드 추가된 엔티티
- `data/reanalysis_v2/instrument_kit_layer_role_matrix.json` — 교차표
- 책 4장 "장르별 슬롯 매트릭스"에 **kit × layer × genre** 히트맵 3종
