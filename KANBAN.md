# sunolang KANBAN

## IN PROGRESS
- [sunolanguage] Phase V3.1 방법론 보강 마무리 단계 — 2026-04-20

## TODO
### Phase V3.1 잔여
- [sunolanguage] `parse_slot_entities_v3.py` instrument 3계 분할 (.kit / .layer / .role) — 설계 논의 필요
- [sunolanguage] extract_templates 엔티티 사전 정리 — "male vocals" 패턴 끝경계 버그 수정 (`<VOCAL>ist` 잔존)

### Phase V3.2 — 장르 균등화 수집 (4-6주)
- [sunolanguage] Wave 1: 외부 레퍼런스 60곡 수집 (Orchestral×18, Jazz×16, Hip-Hop×14, Electronic×12)
- [sunolanguage] Wave 1 결과로 echo율 재측정 → leomusic 생성곡 대비 비교
- [sunolanguage] Wave 2: leomusic 생성곡 60곡 (Folk/R&B/Ballad/Rock +10씩, 신장르 +20)

### Phase V3.3 — 책 본문 빌드 파이프라인 (1-2주, V3.1 완료 후)
- [sunolanguage] `scripts/build_manual_v3.py` — v3 entity + templates → 매뉴얼 A/B 장별 초안
- [sunolanguage] `scripts/slot_genre_matrix.py` — 장르별 슬롯 채워짐 히트맵 (책 4장 원자재)
- [sunolanguage] 20곡 템플릿 해석서 → 책 부록 형식 재구성

### 책 집필
- [sunolanguage] 1장 "Suno의 분류 체계" 본문 (V3.1 완료 후 즉시 가능)
- [sunolanguage] 2장 "두 채널 시스템" 본문
- [sunolanguage] 5장 "Suno가 묘사하지 않는 것" 본문 (mastering 2건/limiter 0건 근거 확보)
- [sunolanguage] 3·4장 본문 (V3.2 Wave 1 완료 후)

### 외부 연동 대기
- [leomusic-base] 어휘 사전 v1.1 aliases 매핑 (68악기+64주법) — 도착 시 머지

## BLOCKED
- 없음

## DONE (최근)
- [sunolanguage] 전면 방법론 재검토 + 로드맵 수립 (플랜 `tender-wishing-lynx.md` 승인) — 2026-04-20 ✅
- [sunolanguage] R1 `scripts/extract_templates.py` — 슬롯별 구문 템플릿 추출 (tempo_key_time: 40x "The tempo is <BPM> in the key of <KEY>.") — 2026-04-20 ✅
- [sunolanguage] R2 `scripts/measure_echo.py` — echo 평균 7.6%, ≥70% 0건 → Suno 네이티브 어휘 근거 확보 — 2026-04-20 ✅
- [sunolanguage] R4 부분 `parse_slot_entities_v3.py` — mastering 분리(2건), harmony 신설(28건) — 2026-04-20 ✅
- [sunolanguage] `scripts/lexical_search_cli.py` — sqlite FTS5 검색기 (8,268 rows, "limiter" 0건 즉시 확인) — 2026-04-20 ✅
- [sunolanguage] v3 entity 데이터 leomusic+leomusic2 배포 + 차이 분석 + 파일럿 지시 (agent-comm `36abcb3`) — 2026-04-18 ✅
- [sunolanguage] v3 10슬롯 entity+modifier 파이프라인 완성 (`parse_slot_entities_v3.py`) — SP 4,250 / 브래킷 3,342 엔트리, 분류율 99.84%/99.88% — 2026-04-18 ✅
- [sunolanguage] v3 최종보고서 Notion 업로드 완료 — 2026-04-18 ✅
- [sunolanguage] 폐기 스크립트 6개 `scripts/archive/`로 이동 + README.md 작성 — 2026-04-18 ✅
- [sunolanguage] `docs/slot_reclassify_v2.md` 슬롯 구조 문서 작성 — 2026-04-18 ✅
- [sunolanguage] 20곡 7-Slot 템플릿 해석서 Leo 검토 완료 → v3 재설계로 전환 — 2026-04-18 ✅
