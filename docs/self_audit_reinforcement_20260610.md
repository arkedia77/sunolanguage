# 전체 태스크 자가점검 + 워크플로우 보강안 (2026-06-10)

점검 방법: KANBAN 9개 진행 트랙 전수 점검 — (1) purple 인프라 직접 검증, (2) agent-comm 메시지 로그 대조로 차단 상태 실증, (3) 워크플로우 3축(가사/코퍼스/뮤직메이커2) 코드·문서 심층 점검(병렬 4에이전트).

---

## 1. 인프라 자가점검 — D139 이사 go-live 검증 ✅ 전 항목 통과

| 항목 | 결과 | 증거 |
|---|---|---|
| venv | ✅ `.venv` kiwipiepy/qdrant_client/psycopg2 import OK | 직접 실행 |
| PostgreSQL | ✅ legion(`leo-legion-y540-15irh`) 접속 OK, songs=3,227 | `~/.config/leofamily_music/db_sunolanguage.conf` |
| ALTER 컬럼 | ✅ `songs.sub_theme`(text) + `songs.coherence`(real) 실존 확인 | information_schema 직접 조회 |
| Qdrant | ✅ 원격(100.90.35.121:6333) 정상, `sunolang_presets`+`sunolang_lyrics` 컬렉션 확인 | curl 직접 조회 |

→ **KANBAN의 "purple 기동 확인 필수" 항목은 본 점검으로 종결.**

---

## 2. 태스크 실태 검증 — KANBAN 드리프트 3건 + 방치 1건

### 2-1. KANBAN 표기 ≠ 실제 (정정 완료)

| 태스크 | KANBAN 표기 | 실제 (메시지 증거) |
|---|---|---|
| songs ALTER | "중계 대기" | **2026-05-31 admin 실행 완료** (`sunomusic_admin_20260531_203459_songs_ALTER완료.json`) → **N008~N014 backfill 즉시 가능 (차단 해제)** |
| 코퍼스확장 Batch A/C | "다음: 발주" | **2026-06-09 14:38 발주 완료** (`sunomusic_sunolanguage_20260609_143800_batchAC_발주.json`) → 회신 대기 |
| D139 purple 기동확인 | "확인 필수" | 본 점검으로 전 항목 PASS → 종결 |

### 2-2. N001/N002 재분석 — 표기 정확, 회신 미수신 (주의: 혼동 위험)
- 재분석 **요청은 05-29 12:11 발송** (`sunomusic_sunolanguage_20260529_121159_N시리즈_재분석요청.json`). 05-29 00시대의 "N001/N002 생성결과"는 **생성** 결과이지 재분석 결과가 아님. 재분석 회신은 inbox에 없음 → **12일 경과, 독촉 대상**.

### 2-3. 자체 착수 가능한데 방치된 태스크
- **Wave T entity 초안** — 근거자료 06-03 완전 수신(Notion 허브 + `~/projects/rag/research/trot_empire/`), Qdrant 접근 확보. 외부 의존 0인데 7일째 미착수. **우선순위 상향 필요.**

### 2-4. 독촉/재발송 필요 (sunomusic 무응답 누적)

| 대상 | 발주일 | 경과 | 조치 |
|---|---|---|---|
| S_INST200 200곡 | 05-26 | 15일 | 상태 확인 독촉 (Leo 보류 지시 05-29 여부 포함 확인) |
| S_BP 21곡 2단계 재분석 | 05-26 (1단계 21/21 완료) | 15일 | 2단계 진행 확인 |
| S_PU 54곡 WF-3 재분석 | 05-17 UUID 수령 후 | 24일 | 독촉 |
| S002 12곡 UUID/재분석 | — | — | 독촉 |
| N001/N002 재분석 | 05-29 | 12일 | 독촉 |
| 55 Best 출처 확인 | **요청 메시지 미발견** | — | **재발송** (기록 누락 가능성) |

→ **보강안: 위 6건을 단일 "상태 확인 배치" 메시지 1통으로 묶어 발송** (개별 독촉 6통보다 sunomusic 처리 효율↑).

---

## 3. 워크플로우별 품질 보강안

### W1. 가사 워크플로우 (lyrics_engine) — 보강안 `docs/lyrics_workflow_reinforcement_plan.md` 보완

**확정 약점** (코드 검증):
- `lyrics_retriever.py:262-290` `_pick_novel`이 retrieval score 1등 맹신 — 기선택 섹션과의 정합 미고려 (T1-1 대상)
- `lyrics_validator.py:116-126` 게이트가 0.3↑ 전부 PASS — 실분포(0.44~0.68)에서 무력 (T1-2 대상)
- coherence가 순수 벡터 유사도 → 단조 반복이 고득점, 의도된 대비가 감점되는 **지표 왜곡**
- `lyrics_refiner.py:140-143` POS 미보존 치환 → 비문법 피드백의 근원 (T2-3)
- couplet 3,447청크 사장, verse2만 연속성 주입

**보강안 누락분 (이번 점검에서 추가)**:
1. **평가지표 4종 신설**: 폼 다양성(배치당 동일 폼 ≤2), 제목 고유율, worst-pair coherence 추적, 크로스곡 Jaccard 매트릭스
2. **재현성**: 임베딩 모델 버전 핀 고정 + 임계값(α/β/Jaccard) 상수 문서화
3. **회귀테스트**: 현 11개 → T1-1/T1-2/T1-3 각각 전용 테스트 추가

**실행 순서 (확정)**:
```
① T3-1 배치감사 하니스(scripts/lyrics_batch_audit.py 신규)
   → N001~N014 소급 실행 → coherence 분포표 = T1-2 임계값 캘리브레이션 베이스라인
② T1-3 Jaccard 인루프 가드 (1일, 저위험)
③ T1-1 coherence-aware 재랭킹 (α0.6/β0.4 시작)
④ T1-2 게이트밴드 (<0.30 FAIL / <0.40 WARN / >0.80 WARN, ①결과로 확정)
⑤ N015 A/B 배치: T1 적용 vs 미적용 정량 비교
⑥ (병렬) N013/N014 저-coh 4곡 청취검증 → 저-coh=창의성 가설 판정 → T2-1 아크 설계 게이트
⑦ T2-3 refiner POS 보존(kiwipiepy) / T3-2 Echo 그라운딩(N001/N002 재분석 수신 후)
```

### W2. 코퍼스 확장 2026Q2 + 품질 게이트

**Phase 0 산출물 평가**: D1/D2/D3 완성도 양호. 단 D2 갭매칭이 부분문자열 기반 — 오매칭 실례 확인("cloud"→mellotron, "louder"→gayageum). **Phase 2 인제스트 전 단어경계 매칭으로 정정 필요.**

**Phase 2(L5) 선행 갭 — 회신 대기 중 지금 만들어둘 것**:
| 갭 | 신규 산출물 | 비고 |
|---|---|---|
| 가사 노이즈 정리 (Leo 지시) | `scripts/lyrics_sanitizer.py` | 유니코드 정규화·특수문자·공백·외국어혼입 — `corpus_quality_gate.py`엔 전무 |
| Batch A/C 회신 병합 | `scripts/merge_batch_reanalysis.py` | 현 merge는 S시리즈 전용 81줄 |
| Qdrant 증분 적재 | `scripts/qdrant_incremental_upsert.py` | rebuild만 존재 |
| 비서구악기/이펙트 엔티티 | `parse_slot_entities_v3.py` 사전 확장 | gayageum·erhu·sitar·riser·bitcrush |
| Entity 밸리데이션 | 게이트에 SP↔가사 cross-check + entity/modifier 정합 추가 | |
| **Batch B(W002 Wave2) 60곡 목록** | `docs/w002_wave2_genre_distribution.md` | **유일하게 Leo 녹음을 막고 있는 미작성물** |

### W3. 뮤직메이커2 / 사전 인프라

**LEO 결정(Q1~Q3) 대기와 무관한 비파괴 선작업**:
1. **`build_dictionary_v3.py` 가드 강화** — v3.1은 손큐레이션본, 재실행=역행+큐레이션 소실. `__main__`에서 RuntimeError로 차단 (최우선 안전조치)
2. T1 드롭인 준비 검증 완료: `webapp/src/data/loader.js:1` 한 줄 + `index.html:13` 메타 — 승인 즉시 1시간 내 배포 가능
3. `sync-corpus` 스크립트 초안 + 회귀 체크리스트(5장르×3템플릿) 작성
4. **제안서 보완 3건**: v3.2는 incremental merge 경로만(재빌드 금지) 명시 / 사전 v3.1 vs slot_matrix v3.3 버전 불일치 관리 방안 / Tier 3 옵션 A/B 인프라 설계서 분리

---

## 4. 프로세스 보강 (메타 — 이번 점검에서 드러난 구조 문제)

1. **KANBAN-실제 드리프트**: ALTER(10일), Batch 발주(1일) 등 완료 사실이 KANBAN에 미반영. → **세션 시작 루틴: inbox 최신 메시지 ↔ KANBAN IN PROGRESS 대조를 의무화** (이번처럼 차단 해제를 놓치면 backfill류 무비용 작업이 방치됨)
2. **발주 후 무응답 방치**: S_INST200 15일, S_PU 24일. → **규칙: 발주 후 7일 무응답 시 자동 독촉 대상으로 KANBAN에 날짜 명기**
3. **요청 발송 기록 누락**: 55 Best는 메시지 자체가 미발견. → 발주·요청은 반드시 agent-comm 파일로 남기고 KANBAN에 파일명 기재
4. **자체작업 vs 대기작업 분리**: KANBAN IN PROGRESS에 차단형/자체형이 혼재 → Wave T 같은 자체형이 매몰. **"ACTIONABLE NOW" 섹션 분리** 권장

---

## 5. 통합 실행 우선순위 (다음 세션 착수 순)

| 순위 | 작업 | 근거 |
|---|---|---|
| 1 | sunomusic 상태확인 배치 1통 발송 (6건 통합) | 24일 묵은 대기 해소, 5분 작업 |
| 2 | **N008~N014 sub_theme/coherence backfill** | ALTER 완료로 차단 해제됨, 데이터 준비 완료 |
| 3 | `build_dictionary_v3.py` RuntimeError 가드 | 사고 1회로 손큐레이션 소실 — 안전조치 |
| 4 | T3-1 배치감사 하니스 + N001~N014 소급 | 가사 T1 전체의 캘리브레이션 베이스라인 |
| 5 | Batch B(W002) 60곡 목록 작성 → Leo 전달 | Leo 녹음 착수의 유일한 차단물 |
| 6 | Wave T entity 초안 (leomusic-trot) | 7일 방치, 자료 완비 |
| 7 | T1-3 Jaccard 가드 → T1-1 재랭킹 → T1-2 게이트 | W1 실행 순서 |
| 8 | lyrics_sanitizer + merge_batch_reanalysis + qdrant_incremental | Batch A/C 회신 도착 전 완비 |
| 9 | N013/N014 저-coh 청취검증 (Leo) | T2-1 아크 설계 게이트 |
