# scripts/archive/ — 폐기 스크립트

v3 entity 구조(parse_slot_entities_v3.py)에 의해 대체된 스크립트들.
혹시 참조가 필요할 수 있으므로 보관.

아카이브일: 2026-04-18

---

## 각 스크립트 설명

### extract_slot_grammar.py
- **역할**: SP 문장을 7슬롯(장르/악기/드럼/보컬/템포/프로덕션/편곡)으로 분류, 슬롯별 문법 패턴 추출
- **출력**: `data/reanalysis_v2/suno_sp_slot_grammar.json`
- **대체**: `parse_slot_entities_v3.py` — 10슬롯 + entity/modifier/pattern/effect 구조로 확장

### build_suno_dictionary.py
- **역할**: v1 어휘 사전 구축 (카테고리별 단어 매칭)
- **출력**: `rag/suno_dictionary.json`
- **대체**: v3 entity 데이터(`sp_entities_v3.json`, `instrument_details_v3.json` 등)가 단어 단위가 아닌 entity+modifier 단위로 수집

### parse_suno_vocab.py
- **역할**: v1 Suno 분석 텍스트에서 어휘 추출 (정규식 기반 카테고리 매칭)
- **출력**: `data/parsed/vocab_index.json`
- **대체**: 동일하게 v3 entity 구조

### build_rag_index.py
- **역할**: v1 RAG 인덱스 구축 (genre/instrument/technique/production 인덱스)
- **출력**: `rag/*.json`
- **대체**: v3 entity 데이터 기반 RAG로 재구축 예정 (벡터DB 포함)
- **참고**: 현재 `rag/` 디렉토리의 인덱스는 v1 기반이므로 구식

### reclassify_slots_v2.py
- **역할**: SP+브래킷을 10슬롯으로 분류 (슬롯 타입만, entity 미분해)
- **출력**: `sp_slots_v2.json`, `bracket_slots_v2.json`, `docs/slot_reclassify_v2.md`
- **대체**: `parse_slot_entities_v3.py` — 동일 슬롯 + entity/modifier 분해 추가
- **참고**: v3 만드는 중간 과정. 슬롯 구조 설계 논의에 유용했음

### build_20song_templates.py
- **역할**: 20곡을 7슬롯으로 분해한 템플릿 해석서 생성
- **출력**: `docs/slot_template_20songs.md`
- **대체**: v3 entity 구조로 리빌드 필요
- **참고**: Leo 피드백 — 드럼/퍼커션 슬롯 이름, 베이스 분류, 비교표 불명확 등 지적

---

## 현재 유효한 파이프라인

```
d1_merge_original_sp.py          → merged_4values.json
parse_slot_entities_v3.py        → sp_entities_v3.json + bracket_entities_v3.json + 상세 통계 JSON 7개
```

보조 스크립트 (아직 유효):
```
d2_extract_vocab.py              → v1 카테고리별 어휘 (참고용)
d3_coverage.py                   → 커버리지 측정 (참고용)
recon_all.py                     → SP/가사 전수 정찰 (참고용)
build_map_and_manuals.py         → 커버리지 맵 (v3 기반 리빌드 대상)
build_manual_samples.py          → 매뉴얼 샘플 (v3 기반 리빌드 대상)
```
