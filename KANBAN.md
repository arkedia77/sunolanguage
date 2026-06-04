# sunolang KANBAN

## IN PROGRESS
- [sunolanguage] **★D139 이사 reklcli→purple** — Phase 0 완료(경로전환12파일+requirements+checkpoint+체크리스트). 21:00 reklcli freeze 진입, purple go-live Leo 직접 챙김. 다음 세션은 purple에서 기동 확인 필수
- [sunolanguage] **Wave T entity 초안** — leomusic-trot 요청. 기존 코퍼스 trot entity 추출 + T5/T9 서브장르 BPM·리듬 매핑 (근거자료 노션 위치 수신 완료)
- [sunolanguage] **songs.sub_theme/coherence ALTER 대기** — Leo 결정 B, sunomusic→admin 중계. 완료 시 N008~N012 backfill+db_insert 2컬럼 추가
- [sunolanguage] **N001/N002 재분석** — sunomusic 재분석 요청 발송 (2026-05-29), 결과 수신 후 `measure_echo_n_series.py` 실행
- [sunolanguage] **Serendipity Engine (SP + Lyrics + Bracket)** — SP 3,707 + Lyrics 4,620 Qdrant 가동 중 (dedup 후), INST5+MIN650+3대패치 적용, **다음: Gate 4 성장 검증**
- [sunolanguage] **S_INST200 200곡 sunomusic 생성 대기** — 발주 완료 2026-05-26 (생성 보류 — Leo 지시 2026-05-29)
- [sunolanguage] S_BP 21곡 — sunomusic 생성 대기 (LEO 가동 승인 완료 2026-05-25)
- [sunolanguage] sunolang DDL 적재 대기 — admin DDL 실행 후 `json_to_db.py load` (4테이블, 437곡+11K엔티티)
- [sunolanguage] S_PU 54곡 pump-up 판정 — songs_test_lab INSERT 완료, sunomusic WF-3 재분석 대기
- [sunolanguage] S002 12곡 분석 — UUID/재분석 sunomusic에서 수령 필요
- [sunolanguage] 사전 v3.1 — S시리즈 추가 수신 시 재빌드

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
- [sunolanguage] 55 Best 출처 확인 대기 — sunomusic 회신 후 corpus 합류 여부 결정

### 책 본문
- [sunolanguage] 3·4장 W002+S007-S015 데이터 반영 (현재 K-장르+SP 길이까지 반영 완료)
- [sunolanguage] ch5 추가 보강 — W002/S007-S015 데이터 반영 시 업데이트 (현재 283행, BPM/구조/장르 데드존 추가 완료)

## BLOCKED
- 없음

## DONE (최근)
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
