# 코퍼스 전파 정책 (Corpus Propagation Policy)

**제정일**: 2026-06-12
**근거**: Batch C 인제스트 E2E(`8b3d2ad`) 경험 + 핸드오프 스키마 드리프트 교훈(N006)
**원칙**: 전파는 3등급으로 나뉜다 — 인제스트와 분리 불가능한 것(A), 비용이 커서 임계치로 묶는 것(B), 곡수와 무관하게 조건 발생 시 도는 것(C).

---

## Class A — 원자 전파 (매 인제스트, 곡수 무관)

**트리거: 신규 코퍼스 1곡이라도 인제스트되면 아래 전부를 같은 세션·같은 커밋에서 종결한다. 부분 전파 금지.**
(근거: 부분 전파가 곧 스키마 드리프트의 원인. Qdrant가 실서빙 레이어이므로 파일만 갱신하고 Qdrant를 미루면 생성 품질에 미반영 상태가 지속됨)

| # | 단계 | 수단 |
|---|---|---|
| A1 | 파일 코퍼스 병합 | `merge_batch_reanalysis.py` → `data/reanalysis_v2/merged_4values.json` |
| A2 | 엔티티 재파싱 | `parse_slot_entities_v3.py` |
| A3 | 청크 재빌드 + Qdrant 증분 | `chunk_builder.py` → `qdrant_incremental_upsert.py` (presets 필수, lyrics는 원곡 가사 보유 시만) |
| A4 | coverage_map 갱신 | `docs/coverage_map.md` |
| A5 | DB 증분 적재 | `json_to_db.py load` — **단, admin DDL 실행 전까지는 보류** (DDL 풀리면 merged_4values를 읽으므로 자동으로 최신분 적재됨) |
| A6 | 회귀 테스트 + KANBAN/메모리 기록 | 전파 수행 즉시 |

## Class B — 임계 전파 (누적 카운터 기반)

### B1. 사전 v3.x 재빌드 (`dictionary_incremental_merge.py` — ★`build_dictionary_v3.py`는 RETIRED, 절차는 아래 §사전 갱신 정식 경로)

아래 **셋 중 하나**라도 충족하면 재빌드:

1. **누적 신규 ≥ 30곡** (마지막 사전 빌드 기준 대비)
   - 근거: 전체 ~500곡의 6%. 정규 배치(60곡)는 단독 충족, S시리즈 소배치(12~21곡)는 2건 누적 시 충족
2. **thin 장르 임계 돌파**: coverage_map에서 표본 <5였던 장르가 ≥5로 진입한 경우
   - 근거: 곡수가 적어도 어휘 분포가 실질적으로 변동 (예: Orch 2→6)
3. **시간 상한**: 마지막 재빌드 후 90일 경과 + 누적 ≥10곡

단, **회신 대기 중인 배치가 2주 내 합류 예상이면 묶어서 1회 재빌드** (재빌드 비용 + 회귀 비용 절약). 대기 상한 2주 초과 시 보유분만으로 선행 재빌드.

### B2. webapp(뮤직메이커2) 사전 드롭인

사전 재빌드에 **종속** — 사전 버전업 시마다 동반 갱신. (T1 드롭인 체계 확립 전까지는 LEO 결정 대기 항목으로 유지)

## Class C — 이벤트 전파 (곡수 무관, 조건 발생 시)

| 대상 | 트리거 |
|---|---|
| Wave T 치환표 diff 발신 | 트로트/GT 관련 신규 엔티티 발생 시 **즉시** (공동관리 의무, 곡수 무관) |
| 책 본문 3·4장 | 장 집필/개정 착수 시점에 최신 코퍼스 스냅샷 반영 (인제스트마다 갱신 안 함) |
| 사전 메이저 버전(v4) | 스키마/슬롯 문법 자체가 바뀔 때만 |

---

## 사전 갱신 정식 경로 (B1 실행 절차)

`build_dictionary_v3.py`는 RETIRED (재실행 = v3.1 큐레이션 퇴행). 정식 절차:

1. `python3 scripts/lexical_search_cli.py build` — lexical_index.sqlite 풀 재빌드 (소스: sp/bracket_entities_v3 + merged_4values + prompts/, 사전 백업 권장)
2. `python3 scripts/dictionary_incremental_merge.py` — dry-run으로 큐레이션 보존 확인
3. `--apply --version X.Y --note "..."` — 적용 (사전 자동 백업 + 축소 가드 내장)
4. `.venv/bin/pytest tests/ -q` 회귀 + 검색기 스모크

## 현재 카운터 (전파 수행 시마다 갱신)

**최종 실측 2026-08-15** — ★값에 단위·층을 붙여 쓴다(곡/트랙/entries는 서로 다른 층). 괄호 안은 **측정법**(재현 가능한 것만 적는다).

| 항목 | 값 |
|---|---|
| 파일 코퍼스 | **530곡** (측정: `merged_4values.json` 배열 길이 = 530. `docs/coverage_map.md` 유니크 song_id 530과 일치) |
| lexical_index | **589트랙 / 19,084 entries / 283장르** (2026-08-14 23:39 재빌드, 백업 `lexical_index.sqlite.bak_v32_556_20260814`. 측정: `entries` 테이블 distinct song_id / count(*) / distinct genre) |
| Qdrant presets | **13,950 points** (측정: `GET {QDRANT_HOST}/collections/sunolang_presets` → `points_count`. ★호스트=`100.90.35.121:6333`. `localhost:6333`은 **다른 인스턴스**라 `sunolang_presets`가 없다 — 여기서 재면 오측) |
| 사전 최신 | **v3.3 (2026-08-15, 589트랙 기준)** — 코퍼스 +33곡 증분 반영. 병합=합집합 의미라 **현행 전용 키 69건 보존**(v3.1 수작업 큐레이션 27건은 그 부분집합) · 큐레이션 전용 9축 무변경 · 키 소실 0 (백업 `rag/suno_dictionary_v3.json.bak_v3.2`) |
| 사전 재빌드 카운터 | **0곡** (v3.3 기준 리셋) — 다음 트리거: 누적 ≥30곡 / thin 장르 ≥5 진입 / 마지막 재빌드 후 90일+누적 ≥10곡 |
| 표현 레이어 | **446개념 / 2,676표현 / 인바운드 별칭 72** (측정: `sunolang.db` `expr_concepts`·`expr_expressions`·`expr_inbound_aliases` 각 count(*). 08-15 v3.3 신규 원자 9건 증분 저작 = +54표현) — ★**정본은 DB가 아니라 `data/expressions/authored/*.json` + `inbound_aliases_seed.json`**. DB는 파생물이라 **DB에만 쓴 값은 재빌드로 조용히 소실된다**(08-15 별칭 6건이 실제로 그렇게 사라졌다가 정본 복원됨) |
| 커넥터 OUT | **interface v0.2 / snapshot `cs-3.3-589-20260815` / 구독 5팀** (측정: `python3 scripts/corpus_connector.py status`. 산출 `data/connector/out/crosswalk_v0.2.json` sha256 `d1c4e9ad48b4fcfb…` · `breaking_content=false`=additive) — 소비자=leomusic·leomusic2·leomusic3·leomusic-trot·**encore**(08-15 편입) |
| DB 테이블 | 0 (admin DDL 대기, A5 보류 중) — ★2026-06-12 기재분, 08-15 **미재확인** |
| webapp 사전 | v2.0 (B2 종속 — LEO Q1 결정 후 **v3.3** 드롭인) |

> ⚠ **이 표는 「전파 수행 시마다 갱신」이라 적어 놓고 06-12~08-15 두 달간 안 고쳤다**(문서 497곡 / 실제 530곡). A4 coverage_map은 갱신돼 있었으므로 **데이터가 아니라 문서만 늙은 것**. 실피해는 아직 없으나 **오인용 위험**이다 — 이 표를 남이 읽고 인용하면 두 달 전 수치가 현재값으로 전파된다.
