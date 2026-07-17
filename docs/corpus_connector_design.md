# 코퍼스 커넥터 (Corpus Connector) 정본 설계 v0

**목적**: sunolang 코퍼스(Suno 네이티브 어휘)의 **외부 인터페이스를 하나의 시스템으로 통합**한다.
지금까지 방향별로 따로 만들어진 세 고리(표현 레이어 발신 / 레퍼런스 매칭 수신 / encore 소비 핸드오프)를
**공용 정본·공용 스키마·공용 파이프라인 골격** 위에 올려, 세션마다의 수작업을 표준 반복 시스템으로 바꾼다.

**작성일**: 2026-07-17 | **발주**: LEO('셋 다 시스템화', 07-17) | **설계 점검**: fableself(위임)
**전제 대조**: `docs/expression_layer_design.md` · `docs/matching_feature_redesign_v1.md` · `docs/corpus_update_reference_matching_design.md` · encore 3채널 합의(07-16)

---

## 1. 통합 관점 — 코퍼스 외부 인터페이스 = 3 포트

세 고리는 방향만 다른 **동일 추상**이다: 코퍼스와 외부 소비자/생산자 사이의 왕복 변환기.

```
                       ┌──────────────── OUT ────────────────►  타 LLM · 인간 · 4팀
        코퍼스          │   표현 레이어 → 버전드 crosswalk publish        (아웃바운드)
   (사전 v3.x +        │
    556트랙 +   ───────┤◄─────────────── IN ─────────────────  외부 레퍼런스 곡/SP
    expr_* +          │   reference_matcher: 매칭 → gap → 재해소       (인바운드)
    lexical_index)     │
                       └──────────────── CONSUME ─────────────►  encore(외부 커미션 프로듀서)
                           경로C handoff: 코퍼스 자산 → 소비 스키마    (소비 인터페이스)
```

encore 3채널 합의(07-16)에서 sunolang의 몫 = **text 어휘 번역 채널**. 커넥터는 그 채널의 실체 구현이며,
IN/CONSUME의 오디오 정밀부는 leomusic3 기계귀(CLAP)와의 하이브리드로 넘긴다(경계 명시, §5).

## 2. 공용 정본 (R-P4 코어+어댑터)

- **코어(불변)**: 사전 `rag/suno_dictionary_v3.json` + `sunolang.db`(코퍼스·expr_*·lexical_index). 포트가 코어를 변형하지 않는다.
- **어댑터(포트)**: 각 포트는 코어에서 **파생물**을 만들어 밖과 접한다. 파생물은 언제든 재생성 가능(정본은 코어).
- **단일 진입점**: `scripts/corpus_connector.py` — 세 포트의 공용 CLI. 각 포트는 서브커맨드.

## 3. 공용 스키마 — 커넥터 매니페스트

정본: `data/connector/manifest.json`. 세 포트의 상태·버전·산출물·소비자/생산자를 **한 곳에 선언**한다(G-K4 단일 기재).

```jsonc
{
  "corpus_snapshot": {                    // 코어 상태 스냅샷 (버전 바인딩의 기준)
    "snapshot_id": "cs-<dict_version>-<track_count>-<yyyymmdd>",
    "dict_version": "3.2",
    "corpus_tracks": 556,
    "expr_concepts": 437,
    "captured_at": "<iso8601>"
  },
  "interface_version": "0.1",             // {major}.{minor} — §4 규약
  "ports": [
    {
      "port": "out",                      // out | in | consume
      "direction": "outbound",
      "status": "live",                   // live | scaffold | blocked
      "payload_schema": "schemas/out_crosswalk.schema.json",
      "artifact": "data/connector/out/crosswalk_v<interface_version>.json",
      "artifact_sha256": "<hex>",
      "consumers": ["leomusic", "leomusic2", "leomusic3", "leomusic-trot"],
      "blocker": null
    },
    { "port": "in", "direction": "inbound", "status": "blocked",
      "producers": ["external_reference_songs"],
      "blocker": "v1 F1~F5 구조피처 재설계 = leomusic3 기계귀 협의 게이트(kee 순번 대기)" },
    { "port": "consume", "direction": "outbound", "status": "blocked",
      "consumers": ["encore"],
      "blocker": "경로C fresh run 대기(회신스키마 발신완료 07-16)" }
  ],
  "runs_log": "sunolang.db:connector_runs"
}
```

## 4. 버전 규약 (코퍼스 스냅샷 ↔ 인터페이스 버전)

- **corpus_snapshot**은 코어의 관측 상태(사전 버전·트랙수·개념수)를 고정한다. publish/ingest/handoff는 실행 시점의 스냅샷을 각인한다.
- **interface_version = {major}.{minor}**
  - **major**: payload 스키마 하위호환 깨짐(필드 제거/의미 변경). 소비자 재계약 필요.
  - **minor**: 내용 증분(신규 원자·별칭·레지스터 추가), 스키마 하위호환 유지. 소비자 무중단 pull.
- 모든 산출물은 `_manifest`(snapshot_id·interface_version·sha256·생성시각·소스 커밋)를 동봉 → 소비자가 **버전 드리프트를 감지**.
- 재빌드(v3.3 등) 시: 스냅샷 갱신 → OUT 재발행은 minor 증분(신규 원자만 저작 워크리스트), 스키마 불변이면 major 고정.

## 5. 파이프라인 골격 (공용 러너 패턴)

`corpus_ingest_runner`의 검증된 관성(원자 실행 + 자동 롤백 + 상태DB)을 커넥터 공용 규약으로 승격:

- **원자성**: 각 포트 실행은 임시 산출 → 검증 통과 후에만 정본 위치로 교체(부분 산출물 노출 금지).
- **상태 로그**: `sunolang.db:connector_runs`(port, snapshot_id, interface_version, artifact_sha256, status, started/ended, note) — 모든 실행 append.
- **헬스 게이트**: OUT publish 전 `corpus_health_check` 재사용(FAIL 시 발행 거부).
- **정직 경계**: 텍스트층에서 도달 가능한 최대치까지만. 오디오 정밀(에너지커브·믹싱질감·음색동일성)은 leomusic3 기계귀로 위임 — 매니페스트 `blocker`에 명기.

```sql
CREATE TABLE IF NOT EXISTS connector_runs (
  id INTEGER PRIMARY KEY,
  port TEXT NOT NULL,                    -- out | in | consume
  snapshot_id TEXT NOT NULL,
  interface_version TEXT NOT NULL,
  artifact_sha256 TEXT,
  status TEXT NOT NULL,                  -- ok | rejected | blocked | dry_run
  note TEXT,
  started_at TEXT DEFAULT (datetime('now','localtime')),
  ended_at TEXT
);
```

## 6. 포트별 명세

### 6.1 OUT — 표현 레이어 publish (status: **live**, 이번 구현)
- 소스: `expr_*` (빌드 `build_expression_db.py`). 발행: `corpus_connector.py out publish`.
- 산출: ① 버전드 crosswalk(전체) ② 팀별 번들(leomusic·2·3·trot 맞춤 — leomusic3엔 taxonomy 정렬 파생) ③ `_manifest` 동봉.
- 재빌드 훅: 사전 재빌드 감지(dict_version 변화) → `build_expression_db --coverage`로 신규 원자 워크리스트 → minor 증분.
- 구독 레지스트리: `data/connector/subscribers.json`(팀·포맷·마지막 수신 버전) — 재발행 시 드리프트 팀 자동 식별.
- 대체: 기존 4팀 수동 1회 발신(07-17) → 표준 반복 발행.

### 6.2 IN — 레퍼런스 매칭 (status: **blocked**, 스캐폴드+게이트)
- 소스: 외부 레퍼런스 곡/SP → `reference_matcher`(v0 텍스트공간, run1~15='검증전').
- 스캐폴드: `corpus_connector.py in match` = ingest_runner 헬스 → matcher → gap 등록 → recheck 루프를 **하나의 엔트리**로 배선.
- 게이트: v1(F1~F5 구조피처, `matching_feature_redesign_v1.md`)은 **leomusic3 기계귀 협의 통과 시에만** 활성. 그전까지 v0 산출은 매니페스트에 `status: blocked / 검증전` 각인, 90곡 일괄매칭 보류 유지.

### 6.3 CONSUME — encore 경로C handoff (status: **blocked**, 스캐폴드)
- 소스: 코퍼스 자산(레퍼자산·카탈로그·rag 외부트랙) → encore 소비 스키마(회신스키마 정본, 발신 07-16).
- 스캐폴드: `corpus_connector.py consume handoff` = 코퍼스 자산 → 경로C 스키마 serializer(재사용 가능, 기존 handoff serializer 관성 승계).
- 게이트: encore **fresh run 대기**. 스키마 정본화 + serializer 스텁까지 이번에 두고, 실주행은 encore 신호 시.

## 7. 갱신·수명주기

- 정본 = 이 문서 + `data/connector/manifest.json`. 포트 산출물은 파생(재생성 가능).
- 사전 재빌드(v3.3) → OUT minor 증분 자동. IN v1 승격 → 매니페스트 status live 전환(기계귀 게이트 해제 시). CONSUME → encore fresh run 신호 시 live.
- 세션 지식: 사건 1건은 KANBAN까지, 2회↑ 재발 시 룰 승격(G-K1).

## 8. 열린 결정 (fableself 점검 대상)

1. **공용 매니페스트 스키마**가 세 포트를 과부족 없이 표현하는가(특히 IN/CONSUME의 blocker·게이트 표현).
2. **버전 규약**의 major/minor 경계 — 소비자(4팀) 재계약 트리거로 충분·과하지 않은가.
3. **경계 배치** — 텍스트층/기계귀층 분담이 encore 3채널 합의와 정합하는가(IN v1·CONSUME 정밀부).
4. 팀별 번들 커스터마이즈를 커넥터가 소유할지, 소비 측 어댑터로 넘길지(R-P4: 기본은 코어+어댑터 양자보유).
