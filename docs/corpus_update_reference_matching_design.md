# 코퍼스 지속 업데이트 + 외부 레퍼런스 매칭 시스템 — 전체 워크플로우 설계

**작성일**: 2026-07-10 · **상태**: 설계 v1.0 (Leo 승인 대기)
**목표**: ① Suno 코퍼스셋을 지속적·안정적으로 업데이트하는 시스템 ② 외부 레퍼런스곡/뉘앙스가 들어왔을 때 기존 코퍼스셋과 매칭하는 시스템 — DB 포함 전체 워크플로우

---

## 0. 설계 원칙과 현황 실측

### 원칙
1. **기존 자산 재사용 우선** — 새로 만드는 것은 "잇는 층(오케스트레이션·상태·매칭)"뿐. 파싱/임베딩/게이트/머지는 기존 스크립트 그대로 호출.
2. **자유도=코퍼스 프리셋 원칙 준수** — 매칭 결과는 항상 "코퍼스에 실존하는 표현"만 반환. 추정 어휘 생성 금지.
3. **부분 전파 금지(전파정책 v3.2 Class A)** — 업데이트는 원자 단위. 실패 시 전체 롤백.
4. **코어+어댑터(R-P4)** — 매칭 DB는 로컬 SQLite 코어로 시작, PostgreSQL(Legion) 이관 어댑터 경로를 열어둠(admin DDL 대기와 독립적으로 즉시 가동 가능).

### 현황 실측 (2026-07-10)

| 레이어 | 자산 | 규모 | 근거 |
|---|---|---|---|
| 파일 코퍼스 | `data/reanalysis_v2/merged_4values.json` | 497곡 (4값 세트) | docs/corpus_propagation_policy.md 카운터 |
| 렉시컬 인덱스 | `data/reanalysis_v2/lexical_index.sqlite` (FTS5) | 17,822 entries / 556트랙 / 263장르 | sqlite 실측 |
| 벡터 인덱스 | Qdrant `sunolang_presets` / `sunolang_lyrics` | 12,818 / 5,858 포인트, all-MiniLM-L6-v2 384dim Cosine | scripts/embed_pipeline.py:30-32 |
| 사전 | `rag/suno_dictionary_v3.json` v3.2 + 6개 인덱스 | 20 카테고리(instrument_phrases~suno_does_not_use) | rag/ 실측 |
| 외부곡 분석 | `sunolang.db` tracks (source=reklcli) | 153곡 + instrument_textures 193 + vocal_textures | sqlite 실측 |
| 전파 정책 | Class A(원자)/B(임계)/C(이벤트) | v3.2, 카운터 수기 관리 | docs/corpus_propagation_policy.md |
| 품질 게이트 | `corpus_quality_gate.py` validate/scan/dedup | 5,858 청크 CLEAN | memory corpus-quality-gate |

### 결손부 (이 설계가 채우는 것)
- **U-갭**: Class A A1~A6이 **수동 개별 실행** → 사람이 빠뜨리면 부분 전파(=스키마 드리프트 재발 위험). 카운터가 문서 수기 표 → B1 임계 판정이 기억 의존.
- **M-갭**: 외부 레퍼런스(곡/뉘앙스) → 코퍼스 매칭의 **정식 워크플로우·기록 DB 부재**. reklcli 153곡 분석과 코퍼스 검색기가 서로 연결 안 됨. 매칭 실패(=코퍼스 공백)가 수집 큐로 되돌아가는 루프 없음.

---

## 1. 전체 아키텍처

```
                    ┌─────────────────────────────────────────────┐
                    │              유입 소스 (3종)                  │
                    │ ① sunomusic 재분석 회신 배치 (4값 JSON)       │
                    │ ② 외부 음원 업로드 결과 (external_source)     │
                    │ ③ 매칭 시스템 gap 후보 → 녹음/업로드 큐 ──┐   │
                    └───────────────┬───────────────────────│───┘
                                    ▼                       │
              ┌─────────────────────────────────────┐       │
              │  [시스템 U] corpus_ingest_runner.py  │       │
              │  A0 품질게이트 → A1 병합 → A2 파싱    │       │
              │  → A3 청크+Qdrant → A4 coverage      │       │
              │  → A5 DB적재 → A6 회귀 → 상태DB 기록  │       │
              │  (원자 실행·체크포인트·자동 롤백)       │       │
              └──────────────┬──────────────────────┘       │
                             ▼                              │
              ┌─────────────────────────────────────┐       │
              │  pipeline_state / ingest_log (DB)    │       │
              │  → B1 임계 자동판정 (≥30곡/thin/90일) │       │
              │  → corpus_health_check.py (4레이어    │       │
              │     곡수·버전 동기 검증)               │       │
              └──────────────┬──────────────────────┘       │
                             ▼                              │
     ┌────────────────────────────────────────────┐         │
     │        코퍼스 서빙 레이어 (기존)              │         │
     │  Qdrant(벡터) + lexical_index(FTS)          │         │
     │  + suno_dictionary_v3(사전) + merged_4values │         │
     └──────────────┬─────────────────────────────┘         │
                    ▼                                       │
   ┌────────────────────────────────────────────────┐      │
   │  [시스템 M] reference_matcher.py                │      │
   │  인테이크(곡/뉘앙스) → 정규화(슬롯 추출)          │      │
   │  → 3중 매칭(M1벡터+M2렉시컬+M3사전) → RRF 융합    │      │
   │  → 매칭 리포트 + Suno네이티브 치환표 + SP재료     │      │
   │  → gap 후보 등록 ───────────────────────────────┘
   │  기록: reference_items/match_runs/match_results │
   └────────────────────────────────────────────────┘
```

두 시스템은 **gap 피드백 루프**로 닫힌다: 매칭에서 코퍼스가 못 받아낸 표현 = 다음 수집 배치의 우선 대상.

---

## 2. 시스템 U — 코퍼스 지속·안정 업데이트

### 2.1 신규 스크립트: `scripts/corpus_ingest_runner.py`

전파정책 v3.2 Class A를 **한 커맨드로 원자 실행**하는 오케스트레이터. 기존 스크립트를 subprocess/모듈 호출로 재사용.

```
python3 scripts/corpus_ingest_runner.py ingest --batch data/incoming/batch_X.json
python3 scripts/corpus_ingest_runner.py status        # 카운터·임계 판정 표시
python3 scripts/corpus_ingest_runner.py rollback --run 17
```

| 단계 | 동작 | 재사용 스크립트 | 실패 시 |
|---|---|---|---|
| A0 | 인제스트 전 검증: 스키마(4값 세트), UUID 중복, 품질게이트 | `corpus_quality_gate.py validate` | **전체 중단** (원본 무변경) |
| A0.5 | 스냅샷: merged_4values·lexical_index·사전 백업 (`data/backups/run_{id}/`) | 신규 (cp) | — |
| A1 | 파일 코퍼스 병합 | `merge_batch_reanalysis.py` | 롤백 |
| A2 | 엔티티 재파싱 | `parse_slot_entities_v3.py` | 롤백 |
| A3 | 청크 재빌드 + Qdrant 증분 | `chunk_builder.py` → `qdrant_incremental_upsert.py` (presets 필수, lyrics는 원곡 가사 보유 시) | 롤백 |
| A4 | coverage_map 갱신 | `d3_coverage.py` → docs/coverage_map.md | 롤백 |
| A5 | DB 증분 적재 | `json_to_db.py load` (admin DDL 전까지 `--skip-db` 플래그로 보류, 상태DB에 `db_pending` 표기) | 경고+계속 |
| A6 | 회귀 테스트 | `.venv/bin/pytest tests/ -q` | 롤백 |
| A7 | 상태DB 기록 + B임계 판정 출력 + KANBAN 갱신 안내 | 신규 | — |

**안정성 장치**:
- **체크포인트**: 각 단계 완료를 `ingest_log.steps_done`에 기록. 중단 시 `--resume`으로 이어가되, A3(Qdrant)은 idempotent upsert라 재실행 안전.
- **롤백**: A0.5 스냅샷 복원 + Qdrant는 upsert된 point id 목록으로 delete. "부분 전파된 채 방치" 상태를 구조적으로 차단.
- **락파일**: `data/.ingest.lock` — 동시 인제스트 방지.

### 2.2 상태 DB (수기 카운터의 자동화)

현재 `docs/corpus_propagation_policy.md`의 수기 카운터 표를 DB로 이전. **문서는 정책(규칙)만 남기고, 상태(숫자)는 DB가 단일 진실원.**

```sql
-- sunolang.db에 추가 (로컬 코어; PG 이관 시 동일 DDL)
CREATE TABLE ingest_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_name TEXT NOT NULL,            -- 예: 'S_MOOD_reanalysis_12'
  source_kind TEXT NOT NULL CHECK(source_kind IN ('reanalysis','external_upload','gap_queue')),
  songs_added INTEGER NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL DEFAULT 'running'
    CHECK(status IN ('running','done','rolled_back','failed','db_pending')),
  steps_done TEXT,                     -- JSON: ["A0","A1",...]
  backup_path TEXT,
  qdrant_point_ids TEXT,               -- JSON: 롤백용
  notes TEXT
);

CREATE TABLE pipeline_state (          -- 단일행 키-값 (카운터)
  key TEXT PRIMARY KEY,                -- 'corpus_songs','lexical_tracks','qdrant_presets',
  value TEXT NOT NULL,                 -- 'dict_version','rebuild_counter','last_rebuild_at' 등
  updated_at TEXT NOT NULL
);
```

**B1 임계 자동 판정** (`status` 커맨드 및 매 인제스트 종료 시):
- `rebuild_counter ≥ 30` OR thin 장르(<5) 신규 ≥5 진입(coverage diff로 검출) OR (경과 ≥90일 AND counter ≥10) → **"사전 재빌드 필요" 신호 + 정식 경로 4단계 안내 출력** (lexical build → incremental_merge dry-run → --apply → pytest). 자동 실행은 안 함 — 재빌드는 큐레이션 보존 확인이 필요한 반자동 절차이므로 사람 개시 유지.

### 2.3 신규 스크립트: `scripts/corpus_health_check.py`

4개 레이어 동기 검증 — "안정적"의 핵심. 인제스트 후행 + 주기(세션 시작 시) 실행.

| 검사 | 기준 |
|---|---|
| H1 곡수 정합 | merged_4values 곡수 == pipeline_state.corpus_songs == ingest_runs 합산 |
| H2 인덱스 정합 | lexical_index 트랙수·Qdrant 포인트수가 상태DB와 일치 (±0) |
| H3 사전 신선도 | rebuild_counter, 마지막 재빌드 경과일 → B1 임계 근접 경고 |
| H4 백업 존재 | 최근 run의 backup_path 실존 |
| H5 게이트 재검 | 무작위 표본 N곡 quality_gate 재통과 |

출력: PASS/WARN/FAIL 요약 1화면. FAIL 시 인제스트 러너가 다음 실행을 거부(`--force`로만 해제).

---

## 3. 시스템 M — 외부 레퍼런스 → 코퍼스 매칭

### 3.1 입력 3형태

| 형태 | 예 | 인테이크 |
|---|---|---|
| **곡 (음원 파일/링크)** | Leo가 준 레퍼런스 mp3, 유튜브 링크 | (권장) **Suno 앱 1분컷 업로드** → Suno 자체 SP 확보 = *Suno 자기 언어라서 매칭 신호 최강* (기존 재분석 파이프라인 그대로). (차선) reklcli-형 텍스트 분석(texture_description·mood·instruments)만으로 매칭 |
| **뉘앙스 텍스트** | "새벽 강가의 안개 같은 첼로, 절제된" | 텍스트 그대로 정규화 단계로 |
| **기존 분석 자산** | sunolang.db tracks 153곡 (reklcli) | texture_description + mood_keywords + instrument_textures를 쿼리로 변환 (일괄 배치 매칭 가능) |

### 3.2 매칭 파이프라인: `scripts/reference_matcher.py`

```
python3 scripts/reference_matcher.py match --text "misty riverside cello, restrained" [--genre cello]
python3 scripts/reference_matcher.py match --suno-sp data/incoming/ref_analysis.json   # Suno 앱 분석 결과
python3 scripts/reference_matcher.py match --track-id 42                               # sunolang.db 기존 분석
python3 scripts/reference_matcher.py report --run 5                                    # 리포트 재출력
```

**단계**:

1. **정규화** — 입력 텍스트에서 슬롯 후보 추출(instrument/technique/mood/production/tempo/vocal). 기존 슬롯 문법(`suno_sp_slot_grammar.json`) 재사용. 한국어 뉘앙스는 영어 병기 변환(간단 사전 + 곡 분석 시 mood_keywords 활용).
2. **3중 매칭** (전 채널 기존 인프라 직결):
   - **M1 벡터**: 쿼리 임베딩(all-MiniLM-L6-v2, 서빙과 동일 모델) → Qdrant `sunolang_presets` top-k(기본 20) — *의미 유사* 채널. 뉘앙스처럼 어휘가 코퍼스와 다를 때 주력.
   - **M2 렉시컬**: `lexical_index.sqlite` entries_fts(FTS5) 슬롯별 질의 — *표현 실존* 채널. 곡 분석처럼 구체어가 있을 때 주력.
   - **M3 사전**: `suno_dictionary_v3.json` genre_vocabulary_map·instrument_phrases·mood_emotion 직조회 + `genre_aliases.json` 정규화 — *검증 어휘* 채널. `suno_does_not_use`·dead_budget_findings로 **음수 필터**(Suno가 안 쓰는 표현은 추천에서 제외).
3. **융합**: RRF(Reciprocal Rank Fusion, k=60)로 3채널 랭킹 통합. 채널 가중은 입력 형태별 프리셋(뉘앙스=M1 우세, Suno SP=M2 우세).
4. **산출 (매칭 리포트, `docs/reviews/match_run_{id}.md`)**:
   - **(a) 최근접 코퍼스 곡 top-5** — song_id, 장르, 매칭 슬롯별 근거 문장
   - **(b) Suno 네이티브 치환표** — `외부 표현 → 코퍼스 실존 표현` 쌍 (SP 작성 시 바로 사용; 예제 중심)
   - **(c) SP 초안 재료** — 슬롯별 검증 표현 모음 (1000자 제한 고려 표기)
   - **(d) 커버리지 gap** — 매칭 스코어가 임계(τ) 미달인 슬롯 = *코퍼스가 이 뉘앙스를 표현 못함* → `gap_candidates` 등록
5. **기록** — 아래 DB에 run·결과 영속화. 같은 레퍼런스 재문의 시 이력 조회.

**임계 τ 캘리브레이션**: goldset 방법론 재사용(direct 0.76/blend 0.59 확정 전례) — 매칭 확정/기각 판정선은 파일럿 10건 Leo 청음·검토로 캘리브레이션 후 고정.

### 3.3 매칭 DB 스키마 (sunolang.db 확장)

기존 `tracks`(153곡)를 레퍼런스 마스터로 **그대로 승격**하고, 매칭 계층만 신설:

```sql
-- 곡 아닌 입력(뉘앙스 텍스트)도 수용하는 인테이크 테이블
CREATE TABLE reference_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL CHECK(kind IN ('track','nuance_text','suno_analysis')),
  track_id INTEGER REFERENCES tracks(id),      -- kind='track'일 때
  input_text TEXT,                             -- 뉘앙스 원문 / Suno 분석 SP
  suno_uuid TEXT,                              -- Suno 앱 업로드 분석 시
  requested_by TEXT DEFAULT 'leo',
  created_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE match_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reference_item_id INTEGER NOT NULL REFERENCES reference_items(id),
  corpus_version TEXT NOT NULL,      -- pipeline_state 스냅샷 (dict v3.2 / 497곡 등)
  channel_weights TEXT,              -- JSON: {"m1":..,"m2":..,"m3":..}
  status TEXT NOT NULL DEFAULT 'done' CHECK(status IN ('done','failed')),
  report_path TEXT,
  created_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE match_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL REFERENCES match_runs(id),
  slot TEXT NOT NULL,                -- instrument/technique/mood/production/...
  query_expr TEXT NOT NULL,          -- 정규화된 쿼리 표현
  matched_expr TEXT,                 -- 코퍼스 실존 표현 (치환표의 우변)
  corpus_song_id INTEGER,            -- 근거 곡
  channel TEXT NOT NULL CHECK(channel IN ('m1_vector','m2_lexical','m3_dict','fused')),
  score REAL NOT NULL,
  is_gap INTEGER NOT NULL DEFAULT 0  -- 1 = τ 미달 (코퍼스 공백)
);
CREATE INDEX idx_mr_run ON match_results(run_id);
CREATE INDEX idx_mr_gap ON match_results(is_gap);

-- gap 피드백 루프: 매칭 실패 표현 → 수집 후보
CREATE TABLE gap_candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  expr TEXT NOT NULL,                -- 코퍼스에 없는 표현/뉘앙스
  slot TEXT,
  first_seen_run INTEGER REFERENCES match_runs(id),
  hit_count INTEGER DEFAULT 1,       -- 재출현 횟수 (우선순위 근거)
  status TEXT NOT NULL DEFAULT 'open'
    CHECK(status IN ('open','queued','recorded','ingested','wontfix')),
  resolution_note TEXT,              -- 어느 배치로 해소됐는지
  updated_at TEXT DEFAULT (datetime('now','localtime'))
);
CREATE UNIQUE INDEX idx_gap_expr ON gap_candidates(expr, slot);
```

**gap 루프 운영**: `gap_candidates`에서 `hit_count` 상위 → W-규약 배치ID로 녹음/외부음원 업로드 큐 편성(기존 `mine_novel_songs.py`·`external_source_leads.md` 흐름 합류) → 재분석 회신이 시스템 U로 인제스트되면 러너가 해당 gap을 `ingested`로 자동 마킹(표현 재매칭 검사).

### 3.4 PostgreSQL 이관 경로 (코어+어댑터)

- 코어: 위 DDL은 SQLite로 즉시 가동 (admin DDL 비대기).
- 어댑터: Leo 결정(05-25) "같은 PG 내 독립 테이블" 기조 유지 — `json_to_db.py`와 동일 패턴으로 `matching_to_pg.py` 이관 스크립트 1개면 됨(DDL은 위와 동일, AUTOINCREMENT→SERIAL 치환). 이관 트리거 = admin DDL 개통 + 타 라인(leomusic2 등)이 매칭 이력 조회를 필요로 할 때.

---

## 4. 운영 시나리오 (E2E 예시)

**시나리오 A — 신규 재분석 배치 도착 (지속 업데이트)**
1. sunomusic 회신 JSON 수신 → `corpus_ingest_runner.py ingest --batch ...`
2. A0 게이트 통과 → A1~A6 원자 실행 → 카운터 자동 증가
3. 종료 메시지: "497→509곡. 재빌드 카운터 12/30. thin 장르 진입 없음. B1 미도달."
4. `corpus_health_check.py` PASS → 끝. (사람 개입: 커맨드 1회)

**시나리오 B — Leo가 레퍼런스곡 전달 (매칭)**
1. 1분컷 → Suno 앱 업로드(sunomusic 경유) → 분석 SP 회수
2. `reference_matcher.py match --suno-sp ...` → 리포트: 최근접 코퍼스 5곡 + 치환표 + SP 재료
3. 치환표 기반 SP 작성(1000자 확인) → 생성 발주
4. gap 2건 검출 → `gap_candidates` 등록 (open)

**시나리오 C — 뉘앙스만 전달**
1. "새벽 강가 안개 같은 첼로" → `match --text ...` → M1 벡터 우세 매칭
2. 코퍼스 근접: CS01 첼로 계열 muted/restrained 표현군 반환 (원곡273 교훈과 정합)
3. 매칭 약한 슬롯(예: 'fog-like texture') → gap 등록 → 다음 수집 배치 후보

**시나리오 D — gap 루프 닫힘**
1. gap `hit_count` 상위 5건 → W-배치 편성 → 녹음/외부음원 → 재분석
2. 시스템 U 인제스트 → 러너가 gap 표현 재매칭 → τ 통과 시 `ingested` 마킹
3. 코퍼스가 "요청됐지만 없던 뉘앙스" 방향으로 성장 — **수요 주도 확장**

---

## 5. 구현 로드맵

| 단계 | 내용 | 신규 코드 | 규모 |
|---|---|---|---|
| **P1** | 상태DB DDL + `corpus_ingest_runner.py`(A0~A7, 롤백) + 카운터 이전 | 러너 1본 + DDL | 중 |
| **P2** | `corpus_health_check.py` H1~H5 | 1본 | 소 |
| **P3** | 매칭 DDL + `reference_matcher.py` MVP(M1+M2, 텍스트 입력) + 리포트 | 1본 + DDL | 중 |
| **P4** | M3 사전 채널 + 음수필터 + RRF + τ 캘리브레이션(파일럿 10건, Leo 검토) | 확장 | 소 |
| **P5** | gap 루프(gap_candidates ↔ 러너 연동) + tracks 153곡 일괄 배치 매칭 | 확장 | 소 |
| P6(후순위) | PG 어댑터 이관 | 1본 | 소 |

**열린 결정 (Leo, 하나씩)**:
1. τ 캘리브레이션 파일럿 10건의 소재 — 기존 reklcli 153곡 중 선정 vs 신규 레퍼런스 대기
2. gap→녹음 큐 편성 주기 — 매칭 run마다 즉시 vs 월 1회 묶음

---

## 6. 정합성 체크 (기존 정책과의 관계)

- 전파정책 v3.2: **대체 아님, 자동화** — Class A/B/C 규칙 그대로, 실행·카운팅만 러너/DB로 이동. 정책 문서의 수기 카운터 표는 P1 완료 시 "상태DB 참조" 1줄로 대체.
- 품질게이트: A0로 편입 (기존 validate 재사용).
- 사전 재빌드: 정식 4단계 경로 유지, 러너는 **신호만** (자동 실행 금지 — 큐레이션 보존 확인 필요).
- DB-pull-on-signal 배포 모델: 매칭 리포트는 산출물, 타 라인 push 안 함. PG 이관 후 타 라인이 SELECT.
- instrumental/브라켓 제약, SP 1000자: 리포트 (c) SP 재료 출력 시 명기.
