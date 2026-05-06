# 사전 v3.0 확장 계획

**현행**: v2.0 (437곡 / 5,070 words / 189 genres / 13,501 entries)
**목표**: v3.0 — v5.5 정보 반영 + 장르갭 메우기 + 새 분류 축 추가

---

## 신규 분류 축 (v2.0에 없는 것)

### 1. negative_vocab (네거티브 프롬프팅 어휘)
v5.5에서 "no X" 형태로 Suno가 확실히 반응하는 배제 어휘.

```json
{
  "negative_vocab": {
    "vocal_processing": ["no autotune", "no vocal effects", "dry vocal"],
    "production": ["no reverb", "no compression", "no modern production"],
    "instruments": ["no synths", "no drums", "no percussion", "no electric"],
    "style": ["no backing vocals", "no harmony", "no choir"],
    "validated": true,
    "source": "community + S018 test"
  }
}
```

### 2. top_anchor_weights (SP 위치 가중치)
v5.5에서 확인된 SP 필드 내 위치별 영향력 순위.

```json
{
  "top_anchor_weights": {
    "position_1": {"role": "genre/subgenre", "weight": "highest"},
    "position_2": {"role": "mood/energy", "weight": "high"},
    "position_3": {"role": "core_instruments", "weight": "high"},
    "position_4": {"role": "vocal_identity", "weight": "medium"},
    "position_5": {"role": "production/harmony", "weight": "low"},
    "validated": false,
    "source": "community consensus + pending S018 A/B test"
  }
}
```

### 3. genre_frontier (장르별 정체성 키워드)
각 장르를 정의하는 최소 필수 어휘 세트.

```json
{
  "genre_frontier": {
    "Synthwave": {
      "must_have": ["analog synth", "arpeggio", "gated reverb"],
      "typical_bpm": "110-120",
      "typical_drums": "gated reverb snare, electronic",
      "corpus_count": 0,
      "external_confidence": "high"
    }
  }
}
```

### 4. output_variance (v5.5 출력 분산 정보)
동일 SP → 다른 결과 나올 때의 변동 패턴.

```json
{
  "output_variance": {
    "v5.0_stability": "high (같은 프롬프트 = 유사 결과)",
    "v5.5_stability": "lower (편차 증가, 특히 vocal grain/arrangement)",
    "high_variance_slots": ["vocal_character", "arrangement_detail", "drum_pattern"],
    "low_variance_slots": ["genre", "bpm", "key", "main_instrument"]
  }
}
```

### 5. studio_stem_map (Suno Studio 12트랙 매핑)
Suno Studio에서 내보내는 12개 스템 트랙 명칭 ↔ corpus 악기명 매핑.

```json
{
  "studio_stem_map": {
    "vocals": ["vocals", "male vocals", "female vocals"],
    "drums": ["drums", "kick drum", "snare drum", "hi-hat"],
    "bass": ["electric bass", "bass guitar", "808 bass"],
    "electric_guitar": ["electric guitar", "distorted guitar"],
    "acoustic_guitar": ["acoustic guitar", "fingerpicked guitar", "nylon string"],
    "synth": ["synthesizer", "synth pad", "analog synth"],
    "pad": ["pad", "ambient pad", "warm pad"],
    "strings": ["strings", "violin", "cello", "viola"],
    "brass": ["brass", "trumpet", "saxophone", "horn"],
    "keys_piano": ["piano", "Rhodes", "organ", "keyboard"],
    "percussion": ["percussion", "shaker", "tambourine", "congas"],
    "effects_ambience": ["ambient", "field recording", "noise", "sfx"]
  }
}
```

---

## 기존 섹션 업데이트 계획

| 섹션 | 현행 | v3.0 변경 |
|------|------|----------|
| corpus.tracks_count | 437 | S003+S004+S016-S017 재분석 합류 시 ~480+ |
| instrument_phrases | 42 악기 | S018 결과로 banjo/fiddle/bodhran/tumbi 등 추가 |
| drum_vocab | 85 패턴 | cajon(13회) 포함 확인, breakbeat/disco hi-hat 정식 추가 |
| genre_vocabulary_map | 190 장르 | S018 16개 장르 추가 → 206+ |
| suno_does_not_use | 5 카테고리 | 유지 (변경 없음) |
| dead_budget_findings | v2.0 | S005-S006 화성 테스트 결과 추가 |

---

## 빌드 파이프라인 변경

```
[기존]
build_dictionary_v2.py → rag/suno_dictionary.json

[v3.0]
build_dictionary_v3.py → rag/suno_dictionary_v3.json
  - 입력 추가: S003/S004/S016-S017/S018 재분석 결과
  - 신규 축: negative_vocab, top_anchor_weights, genre_frontier, output_variance, studio_stem_map
  - 외부 데이터 머지: genre_corpus_external_reference.md → genre_frontier 초기값
```

---

## 트리거 조건 (언제 v3.0 빌드?)

다음 조건 **2개 이상** 충족 시:
1. ✓ S003/S004 재분석 결과 수신 (생성 완료, 재분석 대기)
2. □ S016-S017 재분석 결과 수신
3. □ S018 결과 수신 (최소 8곡)
4. □ S007-S015 결과 수신 (최소 일부)

---

## 즉시 가능한 작업 (재분석 대기 무관)

1. **genre_frontier 초기값 작성** — 외부 레퍼런스 40개 장르 필수 키워드 세트
2. **negative_vocab 구조 확정** — 커뮤니티 검증 목록 기반
3. **studio_stem_map 확정** — Suno 공식 12트랙 기준
4. **build_dictionary_v3.py 스켈레톤** — 기존 v2 로직 + 신규 축 빈 슬롯
5. **S018 프롬프트 전문 작성** — 즉시 발주 가능 상태로
