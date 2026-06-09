# 코퍼스셋 확장 계획 (2026 Q2)

**작성**: sunolanguage (Opus 4.8, 퍼플) · 2026-06-09
**목표**: Suno 네이티브 어휘 코퍼스를 갭 직격 방식으로 성장 — 496 tracks → 목표 600+ tracks, thin 영역 0화

---

## 0. 현 코퍼스 스냅샷

| 레이어 | 규모 | 상태 |
|---|---|---|
| 네이티브 사전 (hand-curated) | **v3.1 · 496곡 / 5,496단어 / 217장르** | ✅ live. ⚠️ `build_dictionary_v3.py`는 **은퇴**(재실행 시 v3.0으로 REGRESS) → 갱신은 **incremental curated merge만** 허용 |
| Qdrant 시맨틱 | presets **10,646** / lyrics **5,858** | ✅ 2026-06-05 rebuild, live 동기 |
| upload_queue (재분석 후보) | 760 후보 / **100 큐잉** (novel_unique≥5) | △ 2026-04-20 생성, 갭장르 우선 재선별 필요 |
| 외부 소스 리드 | 악기 9계열 + 이펙트 3계열 | △ 큐레이션됨, **구체 파일 미선별** |

> **원칙**: 코퍼스는 Suno *자신의* 분석 출력이어야 함. 우리가 생성한 SP(N/S 시리즈)는 직접 코퍼스에 넣지 않음 — 그 곡을 Suno가 *재분석*한 결과만 네이티브 데이터. ([[project_corpus_quality_gate]], [[feedback_corpus_driven_freedom]])

---

## 1. 갭 진단 (어디를 늘릴 것인가)

### 장르 thin 영역 (coverage_map §3, 0~5 셀)
- **Orchestral/Cinematic — 단 2곡** (전 카테고리 빈약) ← 최우선
- **Jazz — 9곡** (시간서명 등 얇음)
- **Tier-1 빈약 장르** (용어 10개 미만): alt rock · amapiano · drum and bass · flamenco · math rock · chillout
- **Tier-2** (10~19개): country · darkwave · new wave · post-rock · synthwave · afrobeat · dubstep · tech house

### 어휘/악기 갭 (external_source_leads)
- 비서구 전통악기: 가야금·해금·거문고·장구 / 얼후·피파 / 코토·샤미센 / 시타르·타블라
- 특이 서구악기: theremin · hurdy gurdy · mellotron
- 이펙트: riser/sweep · vinyl/tape · bitcrush/granular

### 정합 부채 (수집 없이 즉시 개선 가능)
- 장르명 중복 5건(k pop / amapiano / synth pop / electro pop / drum and bass) + lo-fi·hip-hop 변형군 → 정규화 시 실효 어휘 즉시 확장

---

## 2. 확장 레버 (담당·노력별)

| 레버 | 내용 | 담당 | 노력 | 갭 타격 |
|---|---|---|---|---|
| **L1 정규화** | 장르명 dedup + 인덱스 클린 | sunolanguage 단독 | 저 | 정합부채 |
| **L2 외부 수집배치** | freesound 리드 → 구체 파일 3~5개/계열 선별 → 10초 슬라이스 → 업로드큐 | sunolanguage 선별 → sunomusic 업로드 | 중 | 악기/이펙트 갭 |
| **L3 W002 Wave2 60곡** | 장르균등 녹음(thin 장르 직격) | **Leo 녹음** → sunomusic 분석 | 중(프로토콜 완성) | thin 장르 |
| **L4 upload_queue 100곡** | leomusic novel-word 100곡 Suno 재분석 | sunomusic | 중 | 기존 카탈로그 미발굴 어휘 |
| **L5 인제스트 정비** | incremental curated merge 스크립트 + 밸리데이션 | sunolanguage 단독 | 중 | 갱신 파이프라인 |

---

## 3. 단계 계획

### Phase 0 — 정합·파이프라인 정비 (즉시, sunolanguage 단독)
1. **장르 정규화 스크립트**: dedup 5건 + lo-fi/hip-hop 변형 통합. 사전·genre_index·slot_matrix 동기. v3.1 정본 유지(REGRESS 회피, 수기 머지 방식).
2. **incremental ingest 경로 확정**: `merge_series_reanalysis.py` 계열을 기반으로 "신규 재분석 SP만 v3.1에 가산 + corpus_quality_gate 밸리데이션 + Qdrant 증분 upsert" 표준화. build_dictionary_v3 은퇴 상태 우회.
3. **upload_queue 갭 재선별**: 760 후보를 thin 장르(Orchestral/Jazz/Tier-1) 가중치로 재정렬 → 신규 100큐.

### Phase 1 — 수집 배치 설계 (sunolanguage 설계 → Leo/sunomusic 실행)
- **Batch A (외부 악기/이펙트)**: 12계열 × 3~5파일 선별 → 업로드큐 JSON + sunomusic 발주. **갭 직격, Leo 녹음 불필요**(외부 음원).
- **Batch B (W002 Wave2 60곡)**: thin 장르 비례배분 재확정(Orchestral/Cinematic·Jazz·Tier-1 6장르 가중) → Leo 녹음 목록 전달.
- **Batch C (upload_queue 100곡)**: sunomusic Suno 재분석 발주.

### Phase 2 — 인제스트·리빌드
- 재분석 결과 수신 → parse_slot_entities_v3 → curated merge(Phase0 경로) → Qdrant rebuild → 회귀테스트 52종 → coverage_map 갱신.

### Phase 3 — 검증
- Echo Jaccard로 네이티브성 확인 + coverage_map 재산출 + 갭 재평가(thin 셀 감소 측정).

---

## 3-bis. 실행 로그 (Phase 0, 2026-06-09 — 단독 수행분 완료)

착수 결정: **단독 수행분 먼저 / 목표 +100곡**.

| 산출물 | 파일 | 결과 |
|---|---|---|
| **D1 장르 정규화** | `rag/genre_aliases.json` | case/hyphen 충돌 5쌍(K-Pop/Amapiano/Synth Pop/Electro Pop/Drum and Bass) canonical 맵. 비파괴(v3.1 정본 보호). lo-fi 복합라벨 과병합 보류. |
| **D2 갭 재선별** | `scripts/rank_gap_candidates.py` → `data/reanalysis_v2/upload_queue_gap.json` | upload_queue 100건을 novel_words×갭키워드로 재가중. **갭적중 72건**. 영역커버: effects 58·orchestral 37·jazz 16·tier1 9·non-western 6. 상위=다른책/같은노래다른계절/알림999+ |
| **D3 외부 수집배치** | `data/collection/batch_A_external.json` | 비서구악기 6계열+이펙트 3계열, 구체 freesound/Mixkit URL, 10초 슬라이스 룰, **목표 40샘플**. sunomusic 발주 준비완료. |

**+100곡 구성**: D2 갭재선별 catalog ~60곡(Batch C) + D3 외부 40샘플(Batch A) ≈ 100 수집타깃.

**남은 단독 작업**: 인제스트 정비(L5) — 신규 재분석 SP만 v3.1에 가산하는 incremental curated merge 표준화(`merge_series_reanalysis.py` 확장). 재분석 결과 수신 후 실행하므로 Phase 2로.

**실행 필요(타 에이전트)**: Batch A·C sunomusic 발주 / Batch B(W002) Leo 녹음.

## 4. 권고 착수 순서
1. **지금 즉시(단독)**: Phase 0-1 장르 정규화 + Phase 0-3 upload_queue 갭 재선별 + Batch A 외부파일 선별 → 수집배치 준비 완료.
2. **Leo 가용 시**: Batch B 녹음 목록 전달(W002 thin 장르).
3. **sunomusic 큐**: Batch A·C 발주.

## 5. 결정 요청
- **Q1.** 이번 작업 우선 레버 — 외부 수집(L2, Leo 불필요) vs W002 녹음(L3, Leo 필요) 중 무엇부터?
- **Q2.** 목표 규모 — 이번 라운드 +50곡(가벼움) / +100곡 / +150곡(풀)?
