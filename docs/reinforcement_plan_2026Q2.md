# 수노랭귀지 보강 로드맵 (2026Q2 울트라플랜)

**작성**: 2026-06-19 (Opus 4.8, 퍼플) · 플랜 승인 완료, 구현은 차기 세션
**원천**: 플랜파일 `precious-cooking-hare.md` 정식화

## Context — 왜 지금 보강인가

200곡 생성(gid~30120)·사전 v3.2(556트랙)·풀 파이프라인(SP serendipity + 가사 engine + 코퍼스/Qdrant)·책 매뉴얼 ch1~6까지 성숙했다. 이 성숙 단계에서 드러난 **구조적 약점 3종**이 보강 대상이다:

1. **엔진 엣지케이스가 라이브 배치를 오염** — KANBAN '미해결 후보 3건'(title 폴백/genre-filter 무매칭/genre-lock 변주저하)이 N018·N019에서 실제 결함곡을 만들었다. 전수 회귀 57/57은 통과하나 이 엣지케이스들은 **전용 테스트가 없어** 매 배치 수동 점검에 의존.
2. **핵심 과학가설이 수개월째 미검증** — "저-coherence=가사가 음악을 변조하는 창의성 레버"([[project_suno_lyrics_drive_music]])는 가사 워크플로우 튜닝(T1/T2) 전체의 전제인데, Suno 재분석(N001/N002 등)이 막혀 **Echo 정량화 불가**, Leo 청취검증도 미실시. 즉 코퍼런스 통제밴드 철학이 미검증 가정 위에 서 있다.
3. **코퍼스 K-pop 편중이 비-팝 생성을 구조적으로 막음** — genre-filter는 band-aid다. 비-팝 어휘 thin → 앵커 불가·변주저하. 근본해결은 코퍼스 재균형(Batch A/B).

목표: (A) 자가실행 가능한 엔진/데이터 경화를 즉시 끝내고, (B) Leo 결정 1건으로 풀리는 검증·코퍼스·배포 차단을 **결정하기 쉬운 형태로 정리**해 올린다.

---

## Theme 1 — 엔진 강건성 (★자가실행, 최우선)

### R1. title_generator 폴백 — 장르명이 제목 되는 버그
- **위치**: `scripts/title_generator.py:211-216` (`generate_title`의 no-candidate 폴백)
- **현재**: 후보 0개 시 `sp_text.split(".")[0][:20]` → 장르명("K-Pop R&B ballad")이 제목. gid30120 실사례.
- **보강**: 폴백 체인 재설계 —
  1. 모든 섹션에서 한국어 명사 재추출(길이 가드 2→1자 완화, `_extract_korean_nouns` 재사용)
  2. 그래도 없으면 코어섹션 첫 유효행을 트리밍해 제목화
  3. 최종에도 없으면 장르명 금지 → `"제목미정"` 명시 플래그(리뷰 대상으로 audit가 잡도록), **절대 SP 장르 프리픽스를 제목으로 쓰지 않음**
- **테스트**: 가사빈약/영어-only/완전공백 3케이스 → 장르명이 title에 안 들어감을 assert (`tests/test_title_generator.py` 신규)

### R2. genre-filter 무매칭 강건성 — 앵커 조용한 소실
- **위치**: `scripts/serendipity.py:50-59`(`make_filter`), `:88-95`(genre 슬롯 query)
- **현재**: `genre_filter`가 0매칭이면(예: 'r&b'의 "&" 토큰화) genre 슬롯 `response.points` 빈값 → 슬롯 누락, 앵커 소실이 **조용히** 발생. N019에서 'soul'로 우회한 그 케이스.
- **보강**:
  1. genre 슬롯 query 직후 0매칭 감지 → `stderr` 경고(`genre-filter '{gt}' matched 0 — anchor dropped`) 출력
  2. 입력 정규화: 특수문자(`&`등) 분해·소문자화 후 재시도(예 'r&b'→'r b' OR 'soul'/'neo' 동의어 힌트). 동의어 맵은 `rag/genre_aliases.json` 재사용
  3. 그래도 0이면 **무필터 폴백 아님** — 명시적 실패로 CLI exit nonzero(비-팝 의도가 조용히 K-pop으로 되돌아가는 것 방지)
- **테스트**: 0매칭 토큰 입력 시 경고+nonzero exit assert

### R3. genre-lock 변주저하 — 엔진측 완화 + 근본은 Theme 3
- **현재**: 장르 락 시 코퍼스 비-팝 thin → 폼 3종·고coherence. 코드만으론 한계.
- **엔진측 보강(가능분)**: genre 슬롯만 고정하고 나머지 슬롯 drift는 유지(현 구현 OK)되, **drift_factor 자동 상향**(genre-locked 모드에서 비-genre 슬롯 노이즈↑)으로 thin 코퍼스 내 가용 변주 최대화. audit에 "genre-lock 배치=변주 기대치 하향" 노트 자동 기록.
- **근본**: Theme 3(코퍼스 재균형)에 의존 — 본 항목은 완화이지 해결 아님을 명시.

### R4. 엣지케이스 회귀 테스트 군 신설
- 현 테스트 5파일(`test_serendipity_invariants`·`test_lyrics_engine` 등)에 R1/R2 케이스 부재가 버그 누출 원인. R1/R2/R3 각 전용 테스트 추가 → 회귀 스위트에 합류.

---

## Theme 2 — 검증 루프 폐쇄 (★최대 전략가치, Leo 결정 1건이 게이트)

### V1. 재분석 차단 단일 에스컬레이션
- **현황**: S_BP·S_PU·S_INST200·N001/N002 재분석이 전부 "LEO 우선순위 지시 대기"로 수개월 정체. sunomusic은 "Suno Describe UI 카피변경 패치 완료, 지시 시 즉시 발주" 상태.
- **보강**: 개별 독촉이 아니라 **Leo 결정 1건으로 전부 푸는 단일 결정안**을 작성해 올림 — "재분석 우선순위: ①N001/N002(가사→음악 가설 검증 직결) ②S_PU(pump-up) ③S_BP ④S_INST200" 순서 제안 + 각 건이 무엇을 unblock하는지 1줄. Leo는 순서만 승인하면 됨.

### V2. 저-coh A/B 청취세트 (T1/T2 게이트)
- **현황**: T1-1(coherence-aware 재랭킹)·T1-2(게이트밴드)는 **코드 준비 완료, Leo 저-coh 청취검증 대기**. 가설 미판정이면 파라미터 확정 불가.
- **보강**: N013/N014 저-coh 4곡 vs 고-coh 대조곡을 묶은 **타이트한 청취세트 + 판정 질문지 1장**(저-coh가 실제로 음악적 창의성↑인가 Y/N) 준비 → Leo가 5분에 판정. 판정 결과로 T1-2 밴드(>0.80 WARN 등) 확정.

### V3. Echo 그라운딩 (재분석 수신 후 자동)
- V1으로 재분석 도착 시 `measure_echo_n_series.py` 실행 → SP↔재분석 Jaccard로 가사→음악 변조 정량화(T3-2). V1·V2 결과에 종속.

---

## Theme 3 — 코퍼스 재균형 (genre-lock 근본해결)

### C1. Batch A 외부수집 40샘플 — 회신 대기(sunomusic)
### C2. Batch B 녹음 60곡 — Leo 녹음 착수 대기 (목록 v2 전달완료)
- thin 장르 직격(Orch14/Jazz10/T1 18/T2 16/Trot2). **비-팝 thin의 진짜 해결책.** R3는 이게 들어와야 닫힘.
- 보강: V1 단일 결정안에 "Batch B 녹음 = 비-팝 생성 차단 해제의 유일 경로"를 함께 상기.

### C3. 인제스트 밸리데이션 강화 (★자가실행)
- **현황**: `lyrics_sanitizer.py`·`merge_batch_reanalysis.py`는 완료. 단 Leo 05-29 지시의 "인제스트 밸리데이션"은 SP↔가사 cross-check·entity/modifier 정합이 `corpus_quality_gate.py`에 미통합.
- **보강**: 게이트에 ①SP 슬롯 엔티티 ↔ 가사 브래킷 악기 정합 ②parse_slot_entities_v3 미등록 엔티티 리포트 추가. Batch A/C 회신 도착 전 완비.

---

## Theme 4 — 데이터 위생·완전성 (★자가실행)

### D1. N001/N002 정리
- TEMP 제목 20곡 → R1 수정 후 title_generator 재생성. 완전중복 1쌍(gid20313≡20326, Jaccard 1.0) 중 1곡 재생성. **책 원자재 오염 제거.**

### D2. 백필
- N001~N007 70곡 `genre_group` NULL + `song_form_name` NULL → genre/SP 기반 백필. (의도된 공백 아님, 자체분석 §6 확인분만)

### D3. 감사 하니스 경화
- `scripts/lyrics_batch_audit.py`에 ①title∈SP장르프리픽스 체크(R1 회귀 가드) ②**summary 분모=전체곡수**(N016에서 sunomusic 분모버그가 verify-fail을 '9/9'로 은폐 → 분모 정정 약속분 코드화).

---

## Theme 5 — 최종 산출물 (Leo 책 + 뮤직메이커2)

### B1. 뮤직메이커2 Tier 1 드롭인 — Leo Q1 대기
- **현황**: 배포 툴이 v2.0 사전(437곡) 구동 중인데 코퍼스는 556. `loader.js` import 1줄 교체로 즉시 최신화 가능(스키마 동일 검증완료 06-07). 06-07부터 Q1 승인 대기.
- **보강**: 제안서 Q1/Q2/Q3를 재상신(특히 Q1=저위험 즉시착수). 승인 시 1세션 내 배포.

### B2. 책 매뉴얼 데이터 반영 (★자가실행, 데이터 종속)
- `docs/manual_v3/ch3·ch4·ch5` + manual A/B에 W002/S007-S015·N시리즈 200곡 자체분석 반영. N시리즈 자체분석(06-15)의 "패치효과 데이터 실증 3종"은 즉시 ch6 반영 가능.

---

## 권장 실행 순서

| 순위 | 작업 | 성격 |
|---|---|---|
| 1 | **R1 title 폴백 + R4 테스트** | 자가실행, 매 배치 영향 |
| 2 | **R2 genre-filter 강건성 + R3 완화** | 자가실행, 비-팝 배치 영향 |
| 3 | **D1 N001/N002 정리 + D2 백필 + D3 감사경화** | 자가실행(R1 종속), 책 원자재 |
| 4 | **C3 인제스트 밸리데이션** | 자가실행, 회신 전 완비 |
| 5 | **V1 재분석 단일결정안 + V2 청취세트** | Leo 결정 준비물(5분 판정 가능하게) |
| 6 | **B2 책 매뉴얼 반영** | 자가실행, 데이터 종속 |
| 7 | (Leo 승인 후) **B1 뮤직메이커2 드롭인** / **V3 Echo** / **C1·C2 코퍼스** | 차단 해제 시 |

→ 1~4·6은 차기 세션부터 착수 가능. 5는 Leo 앞 결정을 1건으로 압축. 7은 차단 해제 트리거 대기.

---

## 산출물 & 검증

- **신규/수정 코드**: `title_generator.py`(R1), `serendipity.py`(R2/R3), `corpus_quality_gate.py`(C3), `lyrics_batch_audit.py`(D3), `tests/test_title_generator.py`·기존 테스트 확장(R4)
- **신규 문서**: `docs/reanalysis_priority_decision.md`(V1 결정안), 청취세트 질문지(V2)
- **데이터 작업**: N001/N002 DB 정정(D1), 70곡 백필(D2)
- **검증**:
  1. `python -m pytest tests/` 전건 PASS (신규 R1/R2/R3 테스트 포함, 현 베이스라인 57/57)
  2. R1: 가사빈약 입력으로 `title_generator` 실행 → 제목에 장르명 부재 확인
  3. R2: 'r&b' genre-filter로 `serendipity drift` 실행 → 경고+nonzero exit 확인
  4. D1/D2: DB 직접조회로 TEMP 제목 0건·중복 0건·N001~N007 genre_group 채움 확인
  5. 1회 N020 드라이런 배치 → `lyrics_batch_audit.py`로 title-not-genre·분모 정정 동작 확인
