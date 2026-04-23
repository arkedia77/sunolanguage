# sunolang KANBAN

## IN PROGRESS
- [sunolanguage] Wave 1 배치 구성 대기 — corpus-zero 장르 60곡 선별 예정 — 2026-04-23
- [leomusic2] yoonnest 40곡 장르+SP 확인 회신 대기 — 2026-04-23

## TODO
### Suno 네이티브 어휘 확장
- [sunolanguage] Wave 1 배치: TROT(20) + Bossa Nova(11) + Cinematic(8) + Neo-Soul(7) + Folk Pop(8) + 기타 6곡
- [sunolanguage] suspicion_tracker 자동 갱신 스크립트 — 신규 재분석 시 `suno_seen_in_reanalysis` 자동 업데이트

### Phase V3.2 — 장르 균등화 수집 (4-6주)
- [sunolanguage] Wave 1: 외부 레퍼런스 60곡 수집 (Leo 저작권 결정 대기)
- [sunolanguage] Wave 1 결과로 echo율 재측정 → leomusic 생성곡 대비 비교
- [sunolanguage] Wave 2: leomusic 생성곡 60곡 (Folk/R&B/Ballad/Rock +10씩, 신장르 +20)

### Phase V3.3 — 책 본문 빌드 파이프라인 (1-2주)
- [sunolanguage] `scripts/build_manual_v3.py` — v3 entity + templates → 매뉴얼 A/B 장별 초안
- [sunolanguage] `scripts/slot_genre_matrix.py` — 장르별 슬롯 채워짐 히트맵 (책 4장 원자재)

### 책 집필
- [sunolanguage] 1장 "Suno의 분류 체계" 본문
- [sunolanguage] 2장 "두 채널 시스템" 본문
- [sunolanguage] 5장 "Suno가 묘사하지 않는 것" 본문 (코드 진행 0건 + mastering 2건 + dynamic markings 0건)
- [sunolanguage] 3·4장 본문 (V3.2 Wave 1 완료 후)

### 외부 연동 대기
- [leomusic-base] 어휘 사전 v1.1 aliases 매핑 (68악기+64주법) — 도착 시 머지

## BLOCKED
- 없음

## DONE (최근)
- [sunolanguage] Suno 코드/조성 어휘 분석 — key 652회 vs 코드명 0회 확정 — 2026-04-23 ✅
- [sunolanguage] B193+K024 배치 SP/브래킷 Suno 어휘 대조 리뷰 — 2026-04-23 ✅
- [sunolanguage] stems 95곡 파싱 + lexical_index 확장 (11,911 entries, 4,725 words) — 2026-04-23 ✅
- [sunolanguage] words/phrases/word_phrase_map 테이블 추가 — 2026-04-23 ✅
- [sunolanguage] 장르 갭 분석 — 789곡 ~95 corpus-zero 장르 식별 — 2026-04-23 ✅
- [sunolanguage] 트로트→foxtrot 매핑 발견 + K-pop trot 유효 확인 — 2026-04-23 ✅
- [sunolanguage] agent-comm 6건 발신 (어휘DB 공유 3 + yoonnest 질의 1 + 코드분석 2) — 2026-04-23 ✅
- [sunolanguage] sunomusic 배치 36건 mp3 준비 + 작업지시서 — 2026-04-21 ✅
- [sunolanguage] B192 SP 교차검증 + novel-word 마이닝 — 2026-04-20 ✅
