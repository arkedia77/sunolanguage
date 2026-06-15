# sunolang KANBAN

## IN PROGRESS
- [sunolanguage] **★뮤직메이커2 업그레이드 제안서** (rag→sunolanguage, LEO 지시 2026-06-05) — **제안서 초안 작성완료** `docs/musicmaker2_upgrade_proposal.md`(2026-06-07). 원소스=repo `webapp/`(suno-sp-builder Vite SPA) 확정. 진단: 사전 v2.0(437)→v3.1(496) 미반영·엔진 단절. 3-Tier 제안(T1 드롭인+자동화+문법정정 / T2 영속화·게이트 / T3 시맨틱 엔진연결=뮤직메이커2). **대기: LEO 결정 Q1(T1 착수)·Q2(T3 A/B)·Q3(회신경로)**
- [sunolanguage] **가사 워크플로우 보강** — `docs/lyrics_workflow_reinforcement_plan.md` (3-tier). **T3-1 배치감사 하니스 완료(06-11)** + 베이스라인(N001~N014 coh분포) 소급 측정 완료 → **다음: T1-3 Jaccard가드 → T1-1 재랭킹 → T1-2 게이트밴드** (T1/T2 파라미터 확정은 Leo 저-coh 청취검증 결과 반영)
- [sunolanguage] **★D139 이사 reklcli→purple** — **purple 기동 확인 완료(2026-06-10)**: venv import OK / PG legion 접속 OK(songs 3,227) / Qdrant 원격(100.90.35.121) sunolang_presets+lyrics 정상. go-live 검증 종결
- [sunolanguage] **Wave T entity** — 1차분(06-10) + 2차분 발송·**전건 채택 완료(2026-06-15)**: 신규 Trot 서브장르 시그니처 5종(`data/wave_t/wave_t_2_subgenre_signatures.json`) + 공유 canon `kkeokk_ki` 치환 diff(0건 false-negative 발견). leomusic-trot 회신(`...160349_적용완료`): ①canon kkeokk_ki 치환 채택(Traditional/Disco/Blues 적용, Modern은 미보유 제외) ②신규 4종(City Pop/R&B/Synth/Trap) 활성등재·`_future_genres` 스텁 제거 ③Latin provisional 동의. **잔여: Latin/Funk Trot은 W001-08/W002-08 생성→재분석 실증 후 등재**
- [sunolanguage] **N001/N002 재분석 — 막힘 확정(LEO 대기)** — sunomusic 06-10 회신: 재분석DB 미적재=미생성, 큐 미등재, LEO 우선순위 지시 대기(sunomusic이 에스컬레이션). 수신 즉시 `measure_echo_n_series.py` 실행
- [sunolanguage] **★상태확인 배치 6건 — 전건 회신 수신(06-10 20:38)** — ①S_INST200 보류유지(LEO 해제 확인 요청됨) ②S_BP 2단계 막힘 ③S_PU 막힘 ④**S002 생성완료, UUID 재송부 요청 발송(06-10)** ⑤N001/N002 막힘 ⑥55Best LEO만 확정가능. **②③⑤⑥ 전부 LEO 우선순위 지시로 수렴 — sunomusic이 LEO 에스컬레이션 완료, 중복 에스컬레이션 생략. 06-17 재점검**
- [sunolanguage] **Serendipity Engine (SP + Lyrics + Bracket)** — SP 3,707 + Lyrics 4,620 Qdrant 가동 중 (dedup 후), INST5+MIN650+3대패치 적용, **다음: Gate 4 성장 검증**
- [sunolanguage] **S_INST200 200곡** — 보류 유지 확인(06-10). LEO 해제 시 batch_data 153MB 무결성 재검증 후 착수 (sunomusic이 LEO에 해제 확인 요청)
- [sunolanguage] S_BP 21곡 2단계 재분석 — **막힘 확정(06-10)**: 재분석 큐 미등재, LEO 우선순위 지시 대기 (1단계 UUID 21/21 보유)
- [sunolanguage] sunolang DDL 적재 대기 — admin DDL 실행 후 `json_to_db.py load` (4테이블, merged_4values 현행 497곡 자동 반영)
- [sunolanguage] S_PU 54곡 pump-up 판정 — **막힘 확정(06-10)**: 재분석DB 미적재, LEO 우선순위 지시 대기 (skiplist 정책 반영 예정 확인)
- [sunolanguage] S002 12곡 — **UUID 24개 수령·검증·적재 완료(06-10)** `data/test_s002/s002_uuid_list.json`. 재분석은 LEO 우선순위 지시 시 본 목록으로 즉시 발주
- [sunolanguage] 사전 v3.2 완료(06-12) — 다음 재빌드는 전파정책 B1 트리거(누적 ≥30곡, Batch A 합류 등) 충족 시 `dictionary_incremental_merge.py`로

- [sunolanguage] **★코퍼스셋 확장 2026Q2** — 계획 `docs/corpus_expansion_plan_2026Q2.md`. 목표 +100곡(496→~600). **Phase 0 단독수행분 완료(2026-06-09)**: D1 장르정규화(`rag/genre_aliases.json`) + D2 갭재선별(`scripts/rank_gap_candidates.py`→`upload_queue_gap.json`, 갭적중72/100) + D3 외부수집배치(`data/collection/batch_A_external.json`, 40샘플). **Batch B(W002) 60곡 목록 v2 완성(2026-06-11)**: `data/w002_recording_list_v2.md` — thin 장르 직격 재배분(Orch/Cine 14·Jazz 10·Tier-1 18·Tier-2 16·Trot 2), Leo 가용 시 전달. **★Batch C 60/60 수신·인제스트 완료(2026-06-11, `8b3d2ad`)**: corpus 437→497 + Qdrant presets 10,646→12,818 증분 + coverage_map Jazz 9→14·Orch 2→6. 단 C곡 재분석은 Suno가 원곡 성격(K-ballad)대로 라벨링 — 장르 갭 직격은 Batch A(외부)·B(녹음) 몫 실증. **Batch A 회신 대기 / ★Batch B 목록 v2 LEO 전달 발송(2026-06-12, kimsecretary 경유 `kimsecretary_sunolanguage_20260612_202308_BatchB_녹음목록v2_LEO전달.json`, 60곡 전문 포함) — Leo 녹음 착수 대기**

- [sunolanguage] **★자가점검+보강안 (2026-06-10)** — `docs/self_audit_reinforcement_20260610.md`. 통합 우선순위 9건: ①✅상태확인 배치(06-10) ②✅backfill 종결판정(06-10) ③✅dict_v3 가드(06-11) ④✅T3-1 배치감사 하니스(06-11) ⑤✅Batch B 목록 v2(06-11) ⑥✅Wave T 1차분(06-10, 2차분 대기) ⑦가사 T1: ✅T1-3 Jaccard가드(06-11) / T1-1·T1-2는 Leo 청취검증 대기 ⑧✅Phase2 선행 3스크립트(06-11) ⑨저-coh 청취검증(Leo)

## TODO
### v5.5 검증
- [sunolanguage] S_PU 시리즈 sunomusic 발주 — `data/v55_pumpup_test_protocol.md` 참조
- [sunolanguage] Top-Anchor A/B 테스트 (S018에 내장)
- [sunolanguage] 네거티브 프롬프팅 효과 측정 (S018 7곡에 배정)
- [sunolanguage] SP 길이별 테스트 200/500/900자 (S018_03/08/12)
- [sunolanguage] S_BP 21곡 sunomusic 생성 대기 — 발주 완료 2026-05-25, 결과 회신 대기

### genre_frontier 후속
- [sunolanguage] 미검증 25개 S019+ 데이터로 hit_rate 실측 (v1.3 네이티브 재작성은 완료)

### 검증 대기
- [sunolanguage] W002 Wave 2 장르 균등화 60곡 — 프로토콜+녹음목록 완성 (2026-05-25), Leo 녹음 착수 필요
- [sunolanguage] S007-S015 82곡 — sunomusic 미착수, Leo 우선순위 결정 필요
- [sunolanguage] 55 Best 출처 확인 — sunomusic 미보유 정보 확인(06-10), **LEO만 확정 가능** (sunomusic이 LEO에 확인 요청). 회신 후 corpus 합류 여부 결정

### 책 본문
- [sunolanguage] 3·4장 W002+S007-S015 데이터 반영 (현재 K-장르+SP 길이까지 반영 완료)
- [sunolanguage] ch5 추가 보강 — W002/S007-S015 데이터 반영 시 업데이트 (현재 283행, BPM/구조/장르 데드존 추가 완료)

## BLOCKED
- 없음

## DONE (최근)
- [sunolanguage] **W002 10곡 SP 검토회신 (leomusic-trot '한여름 새풍', 06-15)** — corpus 556 v3.2 베이스. W001 v2 치환룰 9/10 상속(폐기어 대폭 감소). 잔존 2건만: ★Funk Trot(W002-08) `clavinet` 0건 dead-zone(Latin tumbao 동일 패턴)→치환필수 / W002-02 `city-pop`·`major-pentatonic` 하이픈→치환권고. 공통정책 10/10·폐기어 클린·BPM 데드존 회피·글자수 807~945 전곡 통과. funk/wah guitar/slap bass/brass stabs는 attested(Latin 교훈 적용 확인). `docs/reviews/W002_sp_review.md`. 회신+admin ACK(`e5d028e0`) — 2026-06-15 ✅
- [sunolanguage] **★Wave T 2차분 발송 (W001 검토 후속·`_future_genres` 대기분 해소)** — leomusic-trot에 신규 Trot 서브장르 시그니처 5종 발송(`data/wave_t/wave_t_2_subgenre_signatures.json`, corpus 556트랙 v3.2 GT-attested): City Pop/R&B/Synth/Trap=ready, Latin=provisional(tumbao/montuno/timbales 0건 dead-zone→보류). canon key는 leomusic-trot 소유 유지·match_patterns/fallback_prose만 GT값 제공(layer_model_trot 준수). ★핵심: 공유 canon `kkeokk_ki` match_patterns 전건 0건 발견(검출기 false-negative)→치환 diff 발신. 발송 `ba7ab144`, admin ACK — 2026-06-15 ✅
- [sunolanguage] **W001 10곡 SP 검토회신 (leomusic-trot, 06-12 요청→06-13 회신)** — corpus 556트랙 v3.2 베이스, 네이티브 소스만(자작 SP 제외)으로 판정. 핵심: ①공통정책(앵커 오프닝+식별3종)=gid20010 원문 축자일치 → OK ②**GT 12곡 중 Suno native 'Trot' 라벨 1/12**(나머지 K-Pop 드리프트) — 식별3종만으론 부족, 앵커 오프닝 고정이 최강 보정 실증 ③Latin 전문어(tumbao/montuno/timbales) 0건 dead zone → 치환필수 ④bass 5종 중 slap/analog/808 OK, fingerstyle 치환권고, tumbao 치환필수 ⑤BPM 전곡 타당(앵커=115) ⑥폐기어 클린, W001-09 930자 컷 권장. novel 리포트 `docs/reviews/W001_sp_review.md`(0건 단어 100개 추적 등재). 회신+admin ACK 발송(`c20f51e7`). **Latin 어휘세트는 W001-08 생성 후 재분석 실증으로 Wave T 2차분 등재 판단** — 2026-06-13 ✅
- [sunolanguage] **★사전 v3.2 — Batch C 전파 완료 (Leo 지시로 B1 선행 실행)** — ①lexical_index 풀 재빌드 496→556트랙/17,822entries/263장르(`lexical_search_cli.py build`, 백업 `.bak_v31_496`) ②**`dictionary_incremental_merge.py` 신규** = RETIRED 빌더(WARNING: 재실행 시 v3.1 퇴행)가 요구한 incremental curated merge 구현(재계산 베이스+큐레이션 보존+축소 가드+dry-run 기본) ③v3.1→v3.2: 코퍼스 496→556, 수작업 큐레이션 27건 전량 보존 검증(instrument 6·technique 11·mood 3·timbre 3·tempo 4 외), genre_map 217→264(Korean Ballad 계열 등 Batch C 유입) ④회귀 57/57 + 검색기 스모크 PASS. 04-24 vocab_expansion 스냅샷은 재빌드 인덱스로 대체. webapp 드롭인은 B2 종속(LEO Q1 대기) — 2026-06-12 ✅
- [sunolanguage] **코퍼스 전파 정책 제정** — `docs/corpus_propagation_policy.md`. A=매 인제스트 원자전파(병합→파싱→Qdrant→coverage→DB→회귀, 부분전파 금지) / B=임계전파(사전 재빌드: 누적≥30곡 OR thin장르 ≥5 돌파 OR 90일+10곡; webapp은 사전에 종속) / C=이벤트전파(Wave T diff 즉시, 책=집필 시점). 현행 카운터: 코퍼스 497·사전 v3.1(496) 대비 +60 임계 초과 → Batch A 합류 대기(상한 06-26) — 2026-06-12 ✅
- [sunolanguage] **★Batch C 60곡 인제스트 E2E (Phase2 파이프라인 첫 실전)** — sunomusic 60/60 회신(발주 gid 완전일치) → merge(437→497, gap_areas 조인 60/60) → parse_slot_entities_v3 → 청크 재빌드 → **qdrant_incremental_upsert 집합 diff 재설계 후 presets +2,172 증분(12,818)** → 회귀 57/57 → coverage_map(Jazz 9→14·Orch 2→6). 가사 컬렉션 무변경=설계 정상(가사 코퍼스는 원곡 가사, C곡 원곡가사 미보유). admin·sunomusic ACK 발송. **sunomusic 노트: Suno Describe UI 카피변경이 백로그 4건(S_BP/S_PU/N001·N002) 막힘의 근본원인이었을 가능성 — 패치 완료, LEO 지시 시 즉시 발주** — 2026-06-11 ✅
- [sunolanguage] **T1-3 Jaccard 인루프 가드 + Phase2 선행 3스크립트** — ①`lyrics_retriever._pick_novel`에 토큰 Jaccard>0.5 reject(한국어 호환 토큰화, 테스트 5종, 라이브 스모크 PASS) ②`lyrics_sanitizer.py`(NFC·zero-width·전각·스마트쿼트·공백 정규화 + 외국어혼입/기호 검수 리포트, 멱등) ③`merge_batch_reanalysis.py`(Batch A/C 회신→merged_4values 병합, 별칭 키 허용·sanitizer 인라인·dry-run 기본, 모의회신 검증) ④`qdrant_incremental_upsert.py`(point_id 연속성 전제 증분 적재, 정렬 표본검증·축소 가드, 라이브 양 컬렉션 동기 확인). 회귀 57/57 — 2026-06-11 ✅
- [sunolanguage] **자체작업 3건 (보강안 ③④⑤)** — ①build_dictionary_v3 RuntimeError 하드가드(--force-regress 명시 없이는 실행 차단, v3.1 무손상 확인) ②**T3-1 배치감사 하니스 `scripts/lyrics_batch_audit.py` 신규**: audit(coh밴드/크로스곡·크로스배치 Jaccard/SP디렉티브/V1=V2/1행섹션/폼·제목·브래킷일치, fail-list+exit code) + retro(DB 소급) — N012~N014 출고분 PASS로 수동 자가점검과 캘리브레이션 일치, **N001~N014 coh분포 소급 완료**(140행, 전체 avg 0.5562, `data/n_series_coherence_retro.json`) ③Batch B(W002) 60곡 목록 v2 `data/w002_recording_list_v2.md`(thin 직격: Orch14/Jazz10/T1 18/T2 16/Trot2). 회귀 52/52 — 2026-06-11 ✅
- [sunolanguage] **sub_theme/coherence backfill 종결 판정** — DB 직접 검증(2026-06-10): N005~N014 + S_PU 등 150행 중 채울 수 있는 행 전부 채워짐(06-05 backfill이 커버). 잔여 NULL 60행은 **원본 데이터 부재**(N001/N002 theme키 자체 없음, N003/N004 sub_theme 미도입, N007 공란버그 Leo 수용, S001 클래식 가사 없음) — 의도된 공백, 조작 backfill 금지 — 2026-06-10 ✅
- [sunolanguage] **N013+N014 실전배치 20곡 DB-direct E2E 완주** — N013(gid 30051~30060, coh0.56, 8폼) + N014(gid 30061~30070, coh0.57, 10폼). 크로스배치 오염0, 자가점검 완료(정량 PASS·저-coh 4곡 서사단절 식별), **sunomusic 생성 20/20 generated**. 가설검증 청취세트 준비(저-coh vs 고-coh) — 2026-06-05 ✅
- [sunolanguage] **N012 10곡 생성 + 가사 일관성 검사 + 전곡 성공** — seed "warm Rhodes piano" drift 0.7, 3곡 교체(coh↑), coh avg 0.56, gid 30041~30050, sunomusic 10/10 — 2026-06-04 ✅
- [sunolanguage] **D139 이사 Phase 0 완료** — requirements 54줄 일치, SQLite checkpoint, 절대경로→상대경로 12파일, 체크리스트+5건 확인→admin 전부 OK, reklcli freeze 진입 — 2026-06-04 ✅
- [sunolanguage] **N009~N011 최종 전곡 성공 확인** — sunomusic 재생성으로 30/30 (자가점검 24/30→전곡 성공). 자가점검 기준 보수적 확인 — 2026-06-04 ✅
- [sunolanguage] **lyrics_engine.py 버그 수정** — song_source_ids str/int 혼합 TypeError 수정 — 2026-06-04 ✅
- [sunolanguage] **leomusic-base 가사붙임조직 거시 51종 수신** — KN-MACRO-TEXT-SETTING, text-setting 조직축 — 2026-06-04 ✅
- [sunolanguage] **N009~N011 30곡 생성 완료 24/30(→30/30)** — 크로스배치 오염 방지 `--exclude-history` 패치 적용 — 2026-06-03 ✅
- [sunolanguage] **흥이야 윤스ver 2종 작업 (LEO 지시)** — ①형태·글자수 고정 변주 10곡+제목 10개 ②맥락유지 변주 10곡. 생성기 2종, sunomusic 회신 — 2026-06-01 ✅
- [sunolanguage] **★N008 DB-direct E2E 완주** — INSERT→트리거→생성→uuid UPDATE 전구간 검증. gid 30001~30010 — 2026-06-01 ✅
- [sunolanguage] **제목 짤림 근본수정 (kiwipiepy)** — 형태소분석 NNG/NNP만 추출, 짤림 0 — 2026-06-01 ✅
- [sunolanguage] **P0/P1 6건 패치 + N006 10곡 생성** — 10/10 PASS, coh 0.54, 8종폼 — 2026-05-30 ✅
