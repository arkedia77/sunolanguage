# sunolang KANBAN

## IN PROGRESS
- [sunolanguage] suno_reanalysis DB 분석 시작 — psql 설치 후 385행 직접 조회 (W1:326 + S시리즈:59)
- [sunolanguage] 사전 v3.0 — 최신 빌드 완료 (496곡/5,496 words/216 genres), S시리즈 추가 수신 시 재빌드

## TODO
### DB 분석 (신규)
- [sunolanguage] psql 설치 (`brew install libpq`) → suno_reanalysis SELECT 테스트
- [sunolanguage] W1 326행 reanalysis_genre NULL → SP 첫 문장에서 장르 추출 UPDATE
- [sunolanguage] 장르별 Suno 네이티브 어휘 대조 분석 (트롯/로파이/시네마틱 등)

### genre_frontier 정제
- [sunolanguage] must_have 키워드를 Suno 네이티브 어휘 기반으로 재작성 (현재 히트율 0~67%)

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
- [sunolanguage] S018 16곡 corpus 머지 (off-by-one 정정 포함, 437곡) — 2026-05-08 ✅
- [sunolanguage] genre_frontier v1.1 validated 업데이트 (16개 장르) — 2026-05-08 ✅
- [sunolanguage] suno_reanalysis DB 385행 적재 완료 (S018 정정 + W1 326곡 소급) — 2026-05-08 ✅
- [sunolanguage] sunomusic phase2 off-by-one 버그 통보 + DB 수정 완료 — 2026-05-08 ✅
- [sunolanguage] S003/S004/S016/S017 43곡 corpus 머지 + lexical index 재빌드 (15,005 entries) — 2026-05-07 ✅
- [sunolanguage] 사전 v3.0 재빌드 (480곡/5,405 words/203 genres/48 instruments/108 drums) — 2026-05-07 ✅
- [sunolanguage] echo 재측정 (평균 7.9%, ≥70% 0건, 네이티브 근거 유지) — 2026-05-07 ✅
- [sunolanguage] SP 출력 순서 분석 (Genre 97% 첫 문장 고정) — 2026-05-07 ✅
