# 코퍼스 커넥터 (Corpus Connector) 정본 설계 v0.1

**목적**: sunolang 코퍼스(Suno 네이티브 어휘)의 **외부 인터페이스를 하나의 시스템으로 통합**한다.
지금까지 방향별로 따로 만들어진 세 고리(표현 레이어 발신 / 레퍼런스 매칭 수신 / encore 소비 핸드오프)를
**공용 정본·공용 스키마·공용 파이프라인 골격** 위에 올려, 세션마다의 수작업을 표준 반복 시스템으로 바꾼다.

**작성일**: 2026-07-17 | **발주**: LEO('셋 다 시스템화', 07-17) | **설계 점검**: fableself(위임)
**전제 대조**: `docs/expression_layer_design.md` · `docs/matching_feature_redesign_v1.md` · `docs/corpus_update_reference_matching_design.md` · encore 3채널 합의(07-16)

**v0.1 개정(07-17, fableself 점검 반영)**: ①blocker 구조화(gate_owner·release_condition·on_release{transition,version_bump}·status enum) ②버전 규약에 `breaking_content` 플래그(삭제·재타깃=소비자 재검증 트리거) ③게이트 해제 시 소유 명기(피처 정의=도메인 오너 / 배선=커넥터) ④번들 파생=무손실만, 소비팀이 구독 레지스트리에 선언·커넥터는 기계 적용.
**v0.2 개정(07-17, fableself ①항 조건부 PASS 경미 2건)**: ⓐpathC handoff `crosswalk_ref`=버전드 경로+sha 고정(latest 포인터 계약 참조 금지 — breaking_content 게이트 우회 차단) ⓑ매니페스트 생성시각을 `manifest_generated_at`(최상위)로 분리, 스냅샷 객체엔 스냅샷 고유 시각(dict_created_at)만(R-P5 시각 실측 정합). → **설계 점검 4항 전건 종결(fableself, LEO 위임 완료).**

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
      "blocker": {                        // 구조화(v0.1 항1) — 문자열 아님
        "gate_owner": "leomusic3",
        "release_condition": "기계귀 협의 통과 → F1~F5 배선",
        "on_release": {"transition": "blocked→live", "version_bump": "minor (신 채널=additive)"},
        "ownership_on_release": "피처 정의·개정=leomusic3 / 소비·배선=커넥터" } },
    { "port": "consume", "direction": "outbound", "status": "blocked",
      "consumers": ["encore"],
      "blocker": { "gate_owner": "encore", "release_condition": "encore fresh run 신호",
        "on_release": {"transition": "blocked→live", "version_bump": "minor"},
        "ownership_on_release": "소비 스키마·요청=encore / serializer 실행=커넥터" } }
  ],
  "status_enum": ["live", "blocked", "deprecated", "scaffold"],
  "runs_log": "sunolang.db:connector_runs"
}
```

## 4. 버전 규약 (코퍼스 스냅샷 ↔ 인터페이스 버전)

- **corpus_snapshot**은 코어의 관측 상태(사전 버전·트랙수·개념수)를 고정한다. publish/ingest/handoff는 실행 시점의 스냅샷을 각인한다.
- **interface_version = {major}.{minor} + `breaking_content` 플래그** (v0.1 항2 — 버전은 2단 유지, 플래그 1개만 추가)
  - **major**: payload 스키마 하위호환 깨짐(필드 제거/구조 변경). 소비자 재계약 필요.
  - **minor + breaking_content=true**: 스키마 무손상이나 **삭제·별칭 재타깃**(매칭 결과 변동) → 소비자 **재검증 트리거**.
  - **minor + breaking_content=false**: additive(신규 원자·별칭·레지스터 추가). 소비자 무중단 pull, 재계약 불요.
  - 감지: 발행 시 직전 발행분 대비 개념/별칭 삭제·재타깃을 자동 검출(`detect_breaking`). 레지스터 텍스트 편집은 concept 해소 불변이라 breaking 아님(정직 명기).
- 모든 산출물은 `_manifest`(snapshot_id·interface_version·sha256·breaking_content·생성시각·소스)를 동봉 → 소비자가 **버전 드리프트를 감지**. sha256=콘텐츠 해시(벽시계 제외)로 스냅샷↔버전 앵커 무결.
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
- 산출: ① 버전드 crosswalk(전체) ② 팀별 번들 ③ `_manifest` 동봉.
- **번들 파생 경계(v0.1 항4)**: 커넥터 번들 = **무손실 파생만**(sort/filter/subset). 의미 변환은 소비 측 어댑터 몫.
  파생 로직 **소유 = 선언한 팀**(구독 레지스트리 `derivations`에 정렬 키 등 등록), **실행 = 커넥터**(기계 적용, `apply_derivation`). 비무손실 kind는 거부(`rejected_nonlossless`).
  예: leomusic3 taxonomy 정렬 = leomusic3가 `subscribers.json`에 선언한 sort 스펙을 커넥터가 적용. → R-P4 '둘 다 보유'가 실구조로 성립.
- 재빌드 훅: 사전 재빌드 감지(dict_version 변화) → `build_expression_db --coverage`로 신규 원자 워크리스트 → minor 증분.
- 구독 레지스트리: `data/connector/subscribers.json`(팀·포맷·선언 파생·마지막 수신 버전·last_breaking) — 재발행 시 드리프트 팀 자동 식별.
- 대체: 기존 4팀 수동 1회 발신(07-17) → 표준 반복 발행.

### 6.2 IN — 레퍼런스 매칭 (status: **blocked**, 스캐폴드+게이트)
- 소스: 외부 레퍼런스 곡/SP → `reference_matcher`(v0 텍스트공간, run1~15='검증전').
- 스캐폴드: `corpus_connector.py in match` = ingest_runner 헬스 → matcher → gap 등록 → recheck 루프를 **하나의 엔트리**로 배선.
- 게이트: v1(F1~F5 구조피처, `matching_feature_redesign_v1.md`)은 **leomusic3 기계귀 협의 통과 시에만** 활성. 그전까지 v0 산출은 매니페스트에 `status: blocked / 검증전` 각인, 90곡 일괄매칭 보류 유지.
- **해제 시 소유(v0.1 항3)**: 피처 정의·개정 = **leomusic3**(기계귀 도메인 오너) / 소비·배선 = **커넥터**. rag 오너십 판정과 동형(콘텐츠 오너 vs 배선 오너 분리) — 해제 후 소유 분쟁 예방.

### 6.3 CONSUME — encore 경로C handoff (status: **blocked**, 스캐폴드)
- 소스: 코퍼스 자산(레퍼자산·카탈로그·rag 외부트랙) → encore 소비 스키마(회신스키마 정본, 발신 07-16).
- 스캐폴드: `corpus_connector.py consume handoff` = 코퍼스 자산 → 경로C 스키마 serializer(재사용 가능, 기존 handoff serializer 관성 승계).
- 게이트: encore **fresh run 대기**. 스키마 정본화 + serializer 스텁까지 이번에 두고, 실주행은 encore 신호 시.

## 7. 갱신·수명주기

- 정본 = 이 문서 + `data/connector/manifest.json`. 포트 산출물은 파생(재생성 가능).
- 사전 재빌드(v3.3) → OUT minor 증분 자동. IN v1 승격 → 매니페스트 status live 전환(기계귀 게이트 해제 시). CONSUME → encore fresh run 신호 시 live.
- 세션 지식: 사건 1건은 KANBAN까지, 2회↑ 재발 시 룰 승격(G-K1).

## 8. 점검 결과 (fableself, 07-17 — ②③④ 판정·보강 반영 완료 / ①은 실물 사본 후 잔여 판정 1회)

1. **공용 매니페스트 스키마** — fableself 예고 기준(blocker의 ⓐ게이트 주체·해제조건 ⓑ해제 시 전이·버전 bump ⓒ소비자 상태 enum + sha 앵커) **선반영**: blocker 구조화·`status_enum`·`_manifest.sha256` 콘텐츠앵커. 실물 사본 도착 시 잔여 판정.
2. ✅**버전 규약** — `breaking_content` 플래그 도입(삭제·재타깃=재검증 트리거). 버전 2단 유지·플래그 1개 최소 개정.
3. ✅**경계 배치** — IN v1/CONSUME 해제 시 소유 명기(도메인 오너 vs 배선 오너). encore 3채널 정합.
4. ✅**번들 소유** — 무손실 파생만·소비팀 선언·커넥터 기계 적용으로 명문화(§6.1).
