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
5. ★**`python3 scripts/corpus_ingest_runner.py record-rebuild --apply`** — 재빌드 **마감**(상태DB에 `dict_version`/`last_rebuild_at`/`rebuild_counter`/`lexical_entries` 기록)

> ⚠ **⑤는 2026-08-16 신설이다 — 그전엔 마감 단계가 아예 없었다.** `rebuild_counter`는 인제스트에서 증가만 하고
> 어떤 재빌드 경로도 되돌리지 않아, 08-15 v3.3 재빌드 후에도 상태DB는 `v3.2 / 06-12 / 33`에 멈춰 있었다.
> ★**이 표 「카운터 0곡(v3.3 기준 리셋)」은 문서만의 선언이었고 기계는 리셋된 적이 없었다** — 08-16 5줄 점검이 잡았다.
> ⑤의 값은 **인자가 아니라 산출물 실측**이다(카운터 = `merged − lexical` 미포함 곡수). 손으로 「0」이라 쓸 수 없게 막았다.

## 현재 카운터 (전파 수행 시마다 갱신)

**최종 실측 2026-08-15** — ★값에 단위·층을 붙여 쓴다(곡/트랙/entries는 서로 다른 층). 괄호 안은 **측정법**(재현 가능한 것만 적는다).

| 항목 | 값 |
|---|---|
| 파일 코퍼스 | **560곡** (측정 2026-09-02: `merged_4values.json` 배열 길이 = 560. 그중 입력층 보유=짝 **455**) / ★별도 **입력 표본 30곡·짝 0**(`data/input_samples/REGISTRY.json` — ⛔코퍼스 곡수와 합산 금지) |
| lexical_index | **619트랙 / 20,456 entries / 293장르** (2026-09-02 재빌드, 백업 `lexical_index.sqlite.bak_v33_pre_v34_20260902_191447`. 측정: `entries` distinct song_id / count(*) / distinct genre) |
| Qdrant presets | **13,950 points** (측정: `GET {QDRANT_HOST}/collections/sunolang_presets` → `points_count`. ★호스트=`100.90.35.121:6333`. `localhost:6333`은 **다른 인스턴스**라 `sunolang_presets`가 없다 — 여기서 재면 오측) |
| 사전 최신 | **v3.5 (2026-09-02, 619트랙 기준)** — ★**층 오염 처방 반영**. `lexical_search_cli.py:SOURCE_COL` 에서 `leomusic_sp_full`(**우리 입력층**)을 `'sp'` 에서 분리해 **`freq_input` 신설**, ★**`freq_total` 을 출력층 합계만으로 재정의**. 사전 3섹션(`mood_emotion`·`timbre_texture`·`tempo_rhythm`) 항목에 **`input` 칸 병기**(층을 값 옆에) · `descriptor_combos` 값 58건을 출력층 실측으로 통일. **실측**: 전체 단어 출현 중 입력층 **34.3%**(`freq_total` 86,737 ↔ `freq_input` 45,283) · 3섹션 count 합계 **9,581 → 6,459**(−3,122 = 신설 `input` 칸 합계와 정확히 일치·손실 0). ★**Suno 관측 0으로 확정된 12단어**(앞=Suno 관측 / 뒤=우리 입력): `nostalgic` 0/49 · `dreamy` 0/33 · `serene` 0/14 · `glassy` 0/9 · `euphoric` 0/6 · `hollow` 0/4 · `somber` 0/3 · `moody` 0/2 · `haunting`·`sultry`·`hi-fi`·`trill` 각 0/1. `descriptor_combos` 최대 낙차: `emotional` **361→1** · `lyrics` **319→0** · `korean` 425→36 · `energy` 345→27. ⛔**키는 하나도 지우지 않았다** — 지우면 증분 병합기가 「큐레이션」으로 보고 **옛 오염값을 되살린다**(설계상 그렇게 동작). 대신 값이 0으로 보이게 두어 **읽는 쪽이 판단**하게 했다. 사전등록 `data/layer_fix_preregistration_v1.json` **12/12 적중·예측 밖 0단어 없음** · `pytest` 88 passed · 백업 `.bak_v3.4_pre_layerfix_20260902_202756`. ⚠**커넥터 OUT 재발행(5팀)은 미집행** — 프로듀서가 쓰던 어휘가 「Suno 관측 0」으로 바뀌는 건이라 전파 전 고지 필요. |
| 사전 재빌드 카운터 | **0곡** (측정 2026-09-02: `corpus_ingest_runner.py record-rebuild --apply` = merged 560곡 − lexical 619트랙 차집합 → 미포함 **0곡**. 상태DB `dict_version` v3.3→v3.4→**v3.5** · `last_rebuild_at` 08-15→09-02 · `rebuild_counter` 30→0 · `lexical_entries` 19,084→20,456 기록 완료. `corpus_health_check --no-net` = **PASS 6/6·WARN 0**(v3.5 후 재실행도 동일)) — 다음 트리거: 누적 ≥30곡 / thin 장르 ≥5 진입 / 마지막 재빌드 후 90일+누적 ≥10곡 |
| 표현 레이어 | **446개념 / 2,676표현 / 인바운드 별칭 72** (측정: `sunolang.db` `expr_concepts`·`expr_expressions`·`expr_inbound_aliases` 각 count(*). 08-15 v3.3 신규 원자 9건 증분 저작 = +54표현) — ★**정본은 DB가 아니라 `data/expressions/authored/*.json` + `inbound_aliases_seed.json`**. DB는 파생물이라 **DB에만 쓴 값은 재빌드로 조용히 소실된다**(08-15 별칭 6건이 실제로 그렇게 사라졌다가 정본 복원됨) |
| 표현 레이어 정본 키 | **개념 키 = `slugify(suno_term)`**(`build_expression_db.slugify`: 소문자화 후 비영숫자→`_`). concept_id=`{category}:{slug}`. 08-15 실측 **카테고리 교차 슬러그 충돌 0건/446**. ⇒ 표기 변종(하이픈/공백/대소문자)은 **다른 개념이 아니라 같은 개념**이며, `expression_search.py --term`이 이 규칙으로 접어서 조회한다(08-15 수정 전에는 원문 완전일치만 봐서 `call and response`가 「개념 없음」이었다) |
| 커넥터 OUT | **interface v0.2 / snapshot `cs-3.3-589-20260815` / 구독 5팀** (측정: `python3 scripts/corpus_connector.py status`. 산출 `data/connector/out/crosswalk_v0.2.json` sha256 `d1c4e9ad48b4fcfb…` · `breaking_content=false`=additive) — 소비자=leomusic·leomusic2·leomusic3·leomusic-trot·**encore**(08-15 편입) |
| DB 테이블 | **0개** (A5 보류 유지) — 2026-08-15 **실측 재확인**. 측정: `.venv/bin/python scripts/json_to_db.py status` → 4/4 `TABLE NOT FOUND` + 권한무관 카탈로그 `pg_class ⋈ pg_namespace where relname like 'sunolang%'` → **0행**(`information_schema`는 권한 있는 것만 보이므로 그것만으로는 「없음」을 못 세운다). 접속=`leofamily_music` @ `100.90.35.121` / role `role_sunolanguage`(role은 존재). ⚠**DDL 요청은 05-25 발신 후 82일째 무회신**(`agent-comm:projects/admin/messages/processed/admin_sunolanguage_20260525_201000_sunolang_corpus_DDL요청.json` — admin `processed/`에 있어 「처리됨」으로 보이나 실집행 0·회신 0) |
| webapp 사전 | v2.0 (B2 종속 — LEO Q1 결정 후 **v3.3** 드롭인) |

> ⚠ **이 표는 「전파 수행 시마다 갱신」이라 적어 놓고 06-12~08-15 두 달간 안 고쳤다**(문서 497곡 / 실제 530곡). A4 coverage_map은 갱신돼 있었으므로 **데이터가 아니라 문서만 늙은 것**. 실피해는 아직 없으나 **오인용 위험**이다 — 이 표를 남이 읽고 인용하면 두 달 전 수치가 현재값으로 전파된다.
