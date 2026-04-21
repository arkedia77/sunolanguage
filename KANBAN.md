# sunolang KANBAN

## IN PROGRESS
- [sunomusic] 업로드 배치 36건 실행 대기 — 파일 준비 완료, 9시 실행 예정 — 2026-04-21

## TODO
### Suno 네이티브 어휘 확장
- [sunolanguage] sunomusic 배치 결과 수집 → suspicion_tracker 업데이트 + v3 확장 후보 판정
- [sunolanguage] suspicion_tracker 자동 갱신 스크립트 — 신규 재분석 시 `suno_seen_in_reanalysis` 자동 업데이트

### Phase V3.2 — 장르 균등화 수집 (4-6주)
- [sunolanguage] Wave 1: 외부 레퍼런스 60곡 수집 (Orchestral×18, Jazz×16, Hip-Hop×14, Electronic×12)
- [sunolanguage] Wave 1 결과로 echo율 재측정 → leomusic 생성곡 대비 비교
- [sunolanguage] Wave 2: leomusic 생성곡 60곡 (Folk/R&B/Ballad/Rock +10씩, 신장르 +20)

### Phase V3.3 — 책 본문 빌드 파이프라인 (1-2주)
- [sunolanguage] `scripts/build_manual_v3.py` — v3 entity + templates → 매뉴얼 A/B 장별 초안
- [sunolanguage] `scripts/slot_genre_matrix.py` — 장르별 슬롯 채워짐 히트맵 (책 4장 원자재)

### 책 집필
- [sunolanguage] 1장 "Suno의 분류 체계" 본문
- [sunolanguage] 2장 "두 채널 시스템" 본문
- [sunolanguage] 5장 "Suno가 묘사하지 않는 것" 본문 (mastering 2건/limiter 0건 + novel-word 근거)
- [sunolanguage] 3·4장 본문 (V3.2 Wave 1 완료 후)

### 외부 연동 대기
- [leomusic-base] 어휘 사전 v1.1 aliases 매핑 (68악기+64주법) — 도착 시 머지

## BLOCKED
- 없음

## DONE (최근)
- [sunolanguage] sunomusic 업로드 배치 mp3 36건 다운로드 + 작업지시서 — 2026-04-21 ✅
- [sunolanguage] 노션 4페이지 생성 (리서치2 + 참고자료1 + 작업지시1) — 2026-04-21 ✅
- [sunolanguage] 외부 악기·이펙트 소스 리드 수집 (freesound/mixkit/pixabay) — 2026-04-20 ✅
- [sunolanguage] leomusic 생성곡 novel-word 마이닝 (1033곡 → 100곡 큐) — 2026-04-20 ✅
- [sunolanguage] B192 SP 교차검증 — Suno 0건 84단어 추적, batch_sp_review.py 확립 — 2026-04-20 ✅
- [sunolanguage] B192 10곡 v3 문법 준수도 검토 — 성공/폐기 차이 = novel 단어 품질 — 2026-04-20 ✅
- [sunolanguage] instrument 3계 분할 + VOCAL 버그 수정 + V3.1 완결 — 2026-04-20 ✅
- [sunolanguage] 전면 방법론 재검토 + 로드맵 수립 — 2026-04-20 ✅
