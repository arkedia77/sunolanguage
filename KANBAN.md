# sunolang KANBAN

## IN PROGRESS
- [sunolanguage] S018 "Genre Frontier" 16곡 — sunomusic 전수 완료 확인 (agent-comm 커밋), 결과 수신 + corpus 머지 대기
- [sunolanguage] suno_reanalysis DB 적재 — sunomusic 적재 완료 추정 (커밋 확인), 다음 세션에서 SELECT 테스트
- [sunolanguage] 사전 v3.0 — 재빌드 완료 (480곡/5,405 words/203 genres), S018 수신 시 재빌드 예정

## TODO
### S018 결과 처리
- [sunolanguage] S018 agent-comm 메시지 수신 → corpus 머지 → genre_frontier validated 업데이트
- [sunolanguage] S018 echo 측정

### DB 직접 분석 (신규)
- [sunolanguage] suno_reanalysis 테이블 SELECT 테스트 — 장르별 네이티브 어휘 직접 비교
- [sunolanguage] 트롯/로파이/시네마틱 등 장르별 Suno 어휘 대조 분석

### v5.5 검증
- [sunolanguage] Top-Anchor A/B 테스트 (S018에 내장)
- [sunolanguage] 네거티브 프롬프팅 효과 측정 (S018 7곡에 배정)
- [sunolanguage] SP 길이별 테스트 200/500/900자 (S018_03/08/12)
- [sunolanguage] [] vs () 체계적 비교 테스트 — 같은 지시를 두 방식으로 대조

### 검증 대기
- [sunolanguage] S002 결과 대기 — sunomusic 관현악 15악기 12곡 (재분석 포함)
- [sunolanguage] W002 Wave 2 장르 균등화 60곡 — sunomusic 재분석 대기 (2026-04-27 발주)
- [sunolanguage] S007-S015 82곡 — sunomusic 생성+재분석 (2026-04-29 발주, 장기)
- [sunolanguage] 55 Best 출처 확인 대기 — sunomusic 회신 후 corpus 합류 여부 결정

### SP Builder
- [sunolanguage] Suno 29개 공식 대장르 카테고리 반영
- [sunolanguage] Top-Anchor 자동 배치 기능 추가 (v5.5 반영)

### 책 본문 (자료 준비 단계)
- [sunolanguage] 1·2·5장 자료 준비 — corpus_unmined_findings + 사전 v3.0 + SP 순서 분석이 핵심 자료
- [sunolanguage] 3·4장 — W002+S007-S015 결과 필요

## BLOCKED
- 없음

## DONE (최근)
- [sunolanguage] S003/S004/S016/S017 43곡 corpus 머지 + lexical index 재빌드 (15,005 entries) — 2026-05-07 ✅
- [sunolanguage] 사전 v3.0 재빌드 (480곡/5,405 words/203 genres/48 instruments/108 drums) — 2026-05-07 ✅
- [sunolanguage] echo 재측정 (평균 7.9%, ≥70% 0건, 네이티브 근거 유지) — 2026-05-07 ✅
- [sunolanguage] SP 출력 순서 분석 (Genre 97% 첫 문장 고정) — 2026-05-07 ✅
- [sunolanguage] 가사 브라켓 패턴 분석 + leomusic2 echo 분석 — 2026-05-07 ✅
- [sunolanguage] sunomusic 재분석 DB 적재 요청 (P1) 발송 — 2026-05-07 ✅
- [sunolanguage] 사전 v3.0 빌더 구현 + 첫 빌드 (5축 신규 + 437곡 기존 corpus) — 2026-05-06 ✅
- [sunolanguage] genre_frontier 40장르 초기값 JSON 생성 — 2026-05-06 ✅
- [sunolanguage] S018 16곡 sunomusic 발주 — 2026-05-06 ✅
- [sunolanguage] S003/S004/S016-S017 44곡 재분석 요청 발송 — 2026-05-06 ✅
