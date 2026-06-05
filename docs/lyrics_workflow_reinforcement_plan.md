# 가사 맞추는 워크플로우 보강 방안 (Lyrics-Matching Reinforcement Plan)

**작성**: 2026-06-05 (Opus 4.8, 퍼플)
**대상**: N시리즈 가사 생성 파이프라인 (`lyrics_engine.py` → `match_sp_differentiated` → `assemble_lyrics` → `validate_lyrics`)
**근거**: 코드 실독 검증 (Explore 맵 + 직접 확인)

---

## 0. 핵심 진단

현재 `match_sp_differentiated`(`lyrics_retriever.py:158-350`)는 **각 섹션을 독립적으로 최적 검색**한다.
곡 전체의 서사·정서 정합을 만드는 장치가 구조적으로 거의 없다.

- `_pick_novel`은 retrieval score 1등만 채택(`:273`) — 이미 고른 섹션과의 정합 미고려
- coherence는 측정만 되고(`compute_coherence :139-151`, 순수 pairwise cosine) **게이트가 무력**(PASS `>0.3`, 실분포 ~0.54 → 항상 통과, `:118`)
- coherence는 "벡터유사도"이지 "서사전개"가 아님 — 브릿지의 좋은 대비를 오히려 감점, 단조 반복을 고득점
- 연속성 장치는 verse2 `prev_verse_text[:60]` 1개뿐(`:250-252`), 나머지 섹션은 story-so-far를 모름
- 크로스곡 중복은 song_id만 차단 — 다른 song_id의 동일 코러스 텍스트는 통과 (Jaccard는 `measure_echo`에 있으나 오프라인 전용)
- couplet 3,447청크가 코퍼스에 있으나 본선 파이프라인에서 미사용

→ 누적 피드백("다른 가사 ≠ 이야기 전개", "N시리즈 단조로움", "비문법")의 근원이 전부 이 구조에 있다.

### ★설계 전제 갱신 (2026-06-05, Leo 통찰)
**Suno는 가사를 읽고 음악을 바꾼다.** SP=음악 프레임, 가사=섹션별 변조 신호.
Leo 가설: 가사 맥락이 섹션마다 튀면(서사 단절) Suno가 각 섹션에 반응해야 하므로 **의외로 창의적 음악**이 나옴.
→ **coherence는 최대화 대상이 아니라 통제 밴드**다. 저정합을 무조건 제거하면 음악적 창의성을 평탄화시킨다.
제거 대상은 *무작위* 단절이지, *의도된 대비* 자체가 아니다. (검증: N013/N014 저-coh 4곡 Suno 출력 실청취/Echo 분석 — `project_suno_lyrics_drive_music` 메모리)
N013/N014 자가점검 실증: coherence 지표는 품질을 유의미하게 추적(고0.68 정합 / 저0.44~0.49 단절). 단 "단절=결함" 판정은 보류, "단절=레버" 가능성 우선 검증.

---

## Tier 1 — Quick Wins (소규모 코드, 즉시 효과, 회귀위험 낮음)

### T1-1. coherence-aware 재랭킹 (★최우선)
**위치**: `lyrics_retriever.py:262-290` (`_pick_novel` + 채택부)
**현재**: top-K 중 첫 유효 후보를 그대로 채택 (retrieval score 단독)
**보강**: 이미 선택된 섹션 임베딩(`anchor_embeddings`)을 누적 보유 →
top-K novel 후보를 `α·retrieval_score + β·mean_cos_to_anchors`로 재점수 → 최적 1개 채택.
- 임베딩 모델은 validator의 `paraphrase-multilingual-MiniLM-L12-v2` 재사용(중복 로드 회피)
- α=0.6, β=0.4 시작값. β를 너무 키우면 단조해지므로 상한 가드
- **효과**: coherence 직접 상승 + 섹션 선택이 "곡 맥락"을 반영하기 시작

### T1-2. coherence 게이트 재설계 (상·하한 밴드)
**위치**: `lyrics_validator.py:116-126`
**현재**: `<0.2 FAIL / <0.3 WARN / else PASS` — 0.54도 0.80도 다 PASS
**보강**: 코퍼스 실분포 기준 밴드 도입
- `< 0.40` → WARN(저정합), `< 0.30` → FAIL
- `> 0.80` → WARN(**단조/자기반복**) — "N시리즈 단조로움" 피드백 직격
- WARN 시 worst-pair 섹션 1개 re-roll 트리거(엔진 측 재검색)
- 임계값은 N001~N012 실분포로 캘리브레이션 후 확정

### T1-3. Jaccard 단편중복 인루프 가드
**위치**: `lyrics_retriever.py:_pick_novel`
**현재**: 크로스곡 중복은 song_id로만 차단
**보강**: `measure_echo_n_series.py:104`의 토큰 Jaccard를 `_pick_novel`로 승격 →
후보 텍스트 vs 이미 선택된 섹션 Jaccard `> 0.5`면 reject.
- song_id가 달라도 동일/유사 코러스 텍스트를 잡아냄 (현 dedup 사각지대)
- 임계 0.5는 echo 측정 평균(7.6%) 대비 충분히 보수적

---

## Tier 2 — Structural (중간 규모, 서사 품질의 본질 개선)

### T2-1. 의도된 대비(contrast) 아크 — ※재프레이밍 (구: 서사 정합 강제)
**위치**: `match_sp_differentiated` 쿼리 구성부(`:175-252`) + 신규 arc 어휘
**현재**: 섹션마다 `genre + mood + role_hint` 평면 쿼리. verse2만 직전 텍스트 주입 → 결과는 *무작위* 단절
**보강(설계 전제 갱신 반영)**: 목표는 정합 최대화가 **아니라** 단절의 *통제*다.
- 곡 단위 아크 플랜 도출(예 발라드: setup→longing→climax→resolution) → 각 섹션 쿼리에 아크-스테이지 키워드 블렌딩
- **섹션 내부**는 국소 정합 유지(라인끼리 따로 놀지 않게), **섹션 간** 맥락 전환은 musically meaningful 지점(bridge/drop)에서 *의도적* 허용
- `prev_verse_text` 주입을 일반화하되, 대비 지점에서는 의도적으로 앵커 약화 → "무작위 단절"은 줄이고 "의도된 대비"는 보존
- **효과**: 무작위→의도된 대비. Suno 음악 변조를 *유발*하는 단절은 살리고, 짜깁기 단절만 제거
- **선행 검증 필수**: 저-coh가 실제로 Suno 창의성을 높이는지 N013/N014 실데이터로 확인 후 파라미터 확정

### T2-2. couplet granularity 활성화 (폴리시 패스)
**위치**: `lyrics_retriever.py` + `lyrics_engine.cmd_batch`
**현재**: couplet 3,447청크 미사용 (granularity 항상 section)
**보강**: 조립 후 폴리시 패스에서 couplet 단위로
- 저연속성 라인쌍을 couplet 교체로 보수
- role+arc 둘 다 맞는 단일 섹션이 없을 때 서로 다른 아크 스테이지의 couplet 2개로 verse 합성
- **효과**: 사장된 코퍼스 자산 활용 + 라인 수준 정밀 블렌딩

### T2-3. refiner 문법보존화
**위치**: `lyrics_refiner.py:105-159`
**현재**: 같은길이 한국어 content word 단순치환 → NNG↔VV 무차별 → 비문법
**보강 (택1 또는 병행)**:
- (a) **POS 보존 치환**: kiwipiepy(이미 의존성) 형태소 분석으로 NNG→NNG, VV→VV 활용형 보존 치환만 허용 → 문법파괴 차단
- (b) **opt-in LLM 리라이트 경로**: off-theme/비문법 라인만 엄격 제약(구조·브래킷·행수·언어 보존)하에 재작성. `--refine-llm` 플래그로 분리
- **효과**: "비문법" 피드백 종결, 테마 정합 유지

---

## Tier 3 — 측정·검증 루프 (자가점검의 자동화)

### T3-1. 배치 감사 하니스 표준화
**신규**: `scripts/lyrics_batch_audit.py`
**현재**: 크로스곡오염/비문법/hook반복/SP디렉티브 점검을 세션마다 수동 수행
**보강**: 배치 출력에 자동 실행되는 게이트로 코드화
- 크로스곡 Jaccard 매트릭스 / 곡내 라인반복 / 브래킷-SP 악기일치율 / coherence 밴드 분포 / 문법 휴리스틱
- per-batch 리포트 + re-roll 대상 fail-list 출력
- `corpus_quality_gate.py` 철학 계승, 책 출판수준 정확도 요구에 정합

### T3-2. Echo 그라운딩 루프
**위치**: `measure_echo_n_series.py` 연동
**보강**: Suno 재분석 도착 시 Jaccard 피드백을 검색에 환류 —
Suno 출력에 실제 "echo"되는 코퍼스 섹션을 upweight. 생성↔Suno 네이티브 어휘 폐루프.
(N001/N002 재분석 결과 수신 대기 항목과 합류)

---

## 권장 실행 순서

1. **T1-1 (재랭킹) + T1-2 (게이트) 동시** — 가장 큰 품질 레버, 회귀위험 낮음. N013에서 A/B 측정
2. **T1-3 (Jaccard 가드)** — dedup 사각지대 즉시 봉합
3. **T3-1 (감사 하니스)** — 이후 모든 보강의 측정 기반 확보
4. **T2-1 (서사 아크)** — 본질 개선, T3-1 측정 위에서 진행
5. **T2-3 (refiner) / T2-2 (couplet)** — 정밀 폴리시
6. **T3-2 (Echo 환류)** — 재분석 수신 후

## 측정 프로토콜
- 베이스라인: N001~N012 기존 출력의 coherence 분포 + 크로스곡 Jaccard 매트릭스 기록
- 각 보강 적용 시 N013 A/B: coherence 밴드 / 크로스곡 중복 / 라인반복 / 폼다양성 / 제목고유율
- 회귀 테스트(`tests/`, 현 52개) 통과 유지
