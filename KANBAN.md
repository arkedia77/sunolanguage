# sunolang KANBAN

## IN PROGRESS
- [sunolanguage] **브래킷 코퍼스 설계** — bracket_entities_v3.json 4,956청크 → 장르별 브래킷 프리셋 + Intro/Interlude/Outro 자동 배치 (Leo 지시 2026-05-29, 다음 세션 즉시 착수)
- [sunolanguage] **코퍼스 노이즈 정리** — 5,925 가사 청크 노이즈 스캔 + 인제스트 밸리데이션 게이트 (Leo 지시 2026-05-29)
- [sunolanguage] **N001/N002 재분석** — sunomusic 재분석 요청 발송 (2026-05-29), 결과 수신 후 `measure_echo_n_series.py` 실행
- [sunolanguage] **Serendipity Engine (SP + Lyrics)** — SP 10,646 + Lyrics 5,925 하이브리드 Qdrant 완료, **다음: Gate 4 성장 검증 (S_INST200 수신 후)**
- [sunolanguage] **S_INST200 200곡 sunomusic 생성 대기** — 발주 완료 2026-05-26, 200곡 SP+가사 전문 전송 완료, 결과 회신 대기
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
- [sunolanguage] **N시리즈 파이프라인 v2 구현** — song_forms.py + title_generator.py 신규, lyrics_retriever/assembler/engine 개선, V1≠V2 100%, 7종폼/10곡, 제목 자동 생성 — 2026-05-29 ✅
- [sunolanguage] N001/N002 코퍼스 어휘 충실도 분석 — 커버리지 98.3%, Novel 12/320 — 2026-05-29 ✅
- [sunolanguage] N001+N002 20/20 Suno 생성 전곡 완료 — gid 20311~20330, 40클립, 통합DB UPDATE — 2026-05-29 ✅
- [sunolanguage] 가사 커플릿 하이브리드 청킹 구현 — section 2,478 + couplet 3,447 = 5,925, 코러스 dedup 61건, 3모드 E2E PASS — 2026-05-28 ✅
- [sunolanguage] Lyrics Corpus 시스템 E2E 완주 — 2,539 섹션 다국어 임베딩, pair 5/5 PASS, coherence 0.55 — 2026-05-28 ✅
- [sunolanguage] Serendipity Engine E2E 완주 — Qdrant 10,646 청크 임베딩, 20/20 PASS (drift 0.5+0.8 네이티브 100%), Gate 1~3 통과 — 2026-05-28 ✅
- [sunolanguage] Serendipity Engine 6개 스크립트 작성 — chunk_builder/embed_pipeline/serendipity/slot_assembler/preset_validator/preset_engine — 2026-05-28 ✅
- [sunolanguage] chunks.json 10,646건 빌드 — SP 5,690 + Bracket 4,956, 437곡 192장르 — 2026-05-27 ✅
- [sunolanguage] Notion 설계 문서 게시 — 아키텍처+Gate 워크플로우+기술스택+CLI — 2026-05-27 ✅
- [sunolanguage] W002 균등화 프로토콜+녹음목록 설계 — 7장르 60곡 비례 배분 — 2026-05-25 ✅
- [sunolanguage] sunolang DDL 설계 + json_to_db.py — 4테이블 스키마 + 적재 스크립트 + admin 요청 — 2026-05-25 ✅
- [sunolanguage] sunolang 코퍼스 DB 독립 테이블 결정 ACK — leomusic2 경유 Leo 결정 수신 — 2026-05-25 ✅
- [sunolanguage] ch5 보강 — §5.7 BPM 재해석 + §5.8 구조 제어 데드존 + §5.9 장르 데드존 (164→283행) — 2026-05-25 ✅
- [sunolanguage] S_BP 21곡 sunomusic 발주 — [] vs () 비교 테스트, SP+가사 7종 전문 포함 — 2026-05-25 ✅
- [sunolanguage] Moonlit Sleep 자문 회신 — 코퍼스 385행 기반 Q1~Q6 답변 (BPM 하한/lo-fi 패턴/ambient/instrumental/장르토큰/loop) — 2026-05-25 ✅
- [sunolanguage] S_PU 54곡 songs_test_lab INSERT — 6장르×3조건×3rep, test_id 1~54 — 2026-05-24 ✅
- [sunolanguage] songs_test_lab 신설 + role_sunolanguage LOGIN 활성화 — LEO 결정, admin 구현 — 2026-05-24 ✅
- [sunolanguage] sp_builder.py §1.10/§1.11 준수 수정 — 오프닝/7문장/drums/보컬 5건 수정 — 2026-05-24 ✅
- [sunolanguage] lexical_index.sqlite 재빌드 — 15,509 entries, 5,496 unique words — 2026-05-24 ✅
- [sunolanguage] 디스크 오프로드 43GB → /Volumes/LEO + symlink — admin 요청 — 2026-05-24 ✅
- [sunolanguage] SP 구조 심층 분석 — 7문장 공식, 동사 체계, 수식어 클러스터, 악기 기본 수식어, 장르 프로파일 — 2026-05-14 ✅
- [sunolanguage] ch1 §1.11 추가 — SP 7문장 공식 + 핵심 동사 6개 + 문장 시작 패턴 — 2026-05-14 ✅
- [sunolanguage] ch3 §3.15~3.16 추가 — 수식어 공기 클러스터 (서정/선명/범용) + 악기별 기본 수식어 — 2026-05-14 ✅
- [sunolanguage] ch4 §4.7 추가 — 장르별 수식어 프로파일 + 감별 수식어 5종 — 2026-05-14 ✅
- [sunolanguage] [] vs () 비교 테스트 설계 — S_BP 시리즈 7가사×3회=21곡 프로토콜 완성 — 2026-05-12 ✅
- [sunolanguage] ch1 §1.10 추가 — SP 오프닝 문법 (445곡 분석: 55.7% Genre only, 83.4% K-접두어) — 2026-05-12 ✅
- [sunolanguage] ch2 §2.6~2.7 추가 — 브래킷 시퀀스 문법 + () 사용 빈도·위치 분석 — 2026-05-12 ✅
- [sunolanguage] v5.5 pump-up modulation 테스트 설계 — S_PU 시리즈 18 SP, 54곡 프로토콜 완성 — 2026-05-12 ✅
- [sunolanguage] genre_frontier v1.3 — 25개 미검증 장르 must_have Suno 네이티브 재작성 — 2026-05-12 ✅
- [sunolanguage] SP Builder 신규 — 29개 대장르, 121개 서브장르, Top-Anchor 자동 배치 — 2026-05-12 ✅
- [sunolanguage] ch3 업데이트 — §3.14 K-장르별 악기 수식어 패턴 추가 — 2026-05-12 ✅
- [sunolanguage] ch4 업데이트 — §4.4 K-장르 슬롯 비교, §4.5 SP 길이, §4.6 장르 경계 추가 — 2026-05-12 ✅
- [sunolanguage] 비-Ballad K-장르 심층 분석 (K-Indie 76행, K-Funk 33행, K-Rock 40행) — 2026-05-11 ✅
- [sunolanguage] SP 길이 vs 장르 상관관계 분석 (385행, Pearson r=0.33) — 2026-05-11 ✅
- [sunolanguage] ch1 업데이트 (서브타입 비교, SP 길이, 장르 경계, 배타적 어휘) — 2026-05-11 ✅
- [sunolanguage] W1 reanalysis_genre UPDATE 326행 sunomusic 실행 확인 — 2026-05-11 ✅
- [sunolanguage] K-Ballad 10개 서브타입 심층 분석 (163행, 악기·보컬·주법 시그니처) — 2026-05-10 ✅
- [sunolanguage] v5.5 key change (pump-up modulation) 발견 + 사전 등록 + leomusic/2 알림 — 2026-05-09 ✅
- [sunolanguage] DB 385행 교차분석 + 장르별 네이티브 어휘 대조 — 2026-05-09 ✅
- [sunolanguage] W1 326행 장르 추출 + UPDATE SQL 생성 + sunomusic 전달 — 2026-05-09~10 ✅
- [sunolanguage] 사전 v3.0→v3.1 업데이트 (미등재 27개 + key change) — 2026-05-09 ✅
- [sunolanguage] genre_frontier v1.1→v1.2 (15개 장르 must_have 네이티브 재작성) — 2026-05-09 ✅
- [sunolanguage] 책 1·2·5장 재작성 (곡 인용 제거, DB 데이터 반영) — 2026-05-09 ✅
