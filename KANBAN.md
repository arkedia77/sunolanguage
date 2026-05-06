# sunolang KANBAN

## IN PROGRESS
- [sunolanguage] S018 "Genre Frontier" 16곡 — sunomusic 발주 완료 (2026-05-06), 생성 대기
- [sunolanguage] S003/S004/S016-S017 44곡 — 재분석(Phase 2) 요청 발송 완료 (2026-05-06), 결과 대기
- [sunolanguage] 사전 v3.0 — 빌더 구현 완료 + 첫 빌드 완료, 재분석 결과 수신 시 corpus 확장 후 재빌드

## TODO
### S018 장르 프론티어 (corpus ZERO 해소)
- [sunolanguage] 결과 수신 → 재분석 → corpus 머지 → 40개 장르갭 중 16개 해소

### 사전 v3.0 빌드
- [sunolanguage] S003+S004+S016-S017 재분석 수신 시 corpus 머지 → v3.0 재빌드
- [sunolanguage] S018 결과 수신 시 genre_frontier validated 업데이트

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

### 책 본문 (1달 후 집필, 지금은 자료 준비)
- [sunolanguage] 1·2·5장 자료 준비 — corpus_unmined_findings + 사전 v3.0이 핵심 자료
- [sunolanguage] 3·4장 — W002+S007-S015 결과 필요

## BLOCKED
- 없음

## DONE (최근)
- [sunolanguage] 사전 v3.0 빌더 구현 + 첫 빌드 (5축 신규 + 437곡 기존 corpus) — 2026-05-06 ✅
- [sunolanguage] genre_frontier 40장르 초기값 JSON 생성 — 2026-05-06 ✅
- [sunolanguage] S018 16곡 sunomusic 발주 (작업지시서+프롬프트전문) — 2026-05-06 ✅
- [sunolanguage] S003/S004/S016-S017 44곡 재분석 요청 발송 — 2026-05-06 ✅
- [sunolanguage] Suno v5.5 vs v5.0 업그레이드 종합 정리 + Notion 업로드 — 2026-05-06 ✅
- [sunolanguage] corpus 미발굴 패턴 분석 (텍스처 순위/동사 문법/감정어 빈약 확정) — 2026-05-06 ✅
- [sunolanguage] S018 "Genre Frontier" 16곡 설계 (corpus ZERO 해소 + v5.5 검증) — 2026-05-06 ✅
- [sunolanguage] 사전 v3.0 확장 계획 (5축 신규: negative/anchor/frontier/variance/stem) — 2026-05-06 ✅
- [sunolanguage] 장르별 외부 코퍼스 레퍼런스 60+장르 수집 — 2026-05-06 ✅
- [sunolanguage] leomusic2 vocab gap R1+R2 전수 대조 회신 (12/17 네이티브 + 6/14 표준형) — 2026-05-06 ✅
- [sunolanguage] S016-S017 점심 레스토랑 BGM 20곡 설계 + sunomusic 우선 발주 — 2026-05-02 ✅
- [sunolanguage] S007–S015 9개 시리즈 82곡 설계 + sunomusic 일괄 발주 — 2026-04-29 ✅
- [sunolanguage] SP Builder 메인악기 패널 + Phase 3/4 완료 — 2026-04-28 ✅
