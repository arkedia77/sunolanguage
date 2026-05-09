# sunolang KANBAN

## IN PROGRESS
- [sunolanguage] W1 reanalysis_genre UPDATE — SQL 생성 완료, sunomusic 실행 대기 중
- [sunolanguage] 사전 v3.1 — DB 교차분석 27개 어휘 추가 완료, S시리즈 추가 수신 시 재빌드

## TODO
### DB 분석 (진행 중)
- [sunolanguage] W1 326행 장르별 심층 비교 — 같은 K-Ballad 내 서브장르별 어휘 차이 분석
- [sunolanguage] SP 길이 vs 장르 상관관계 — DB에서 SP 길이 분포 조회

### genre_frontier 후속
- [sunolanguage] 미검증 25개 장르 must_have도 Suno 네이티브 기반으로 작성 (S019+ 데이터 필요)

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

### 책 본문
- [sunolanguage] 1·2·5장 완성도 향상 — 초안 재작성 완료, 검토 후 교정 필요
- [sunolanguage] 3·4장 — W002+S007-S015 결과 필요

## BLOCKED
- 없음

## DONE (최근)
- [sunolanguage] DB 385행 교차분석 + 장르별 네이티브 어휘 대조 — 2026-05-09 ✅
- [sunolanguage] W1 326행 장르 추출 (162 고유 장르) + UPDATE SQL 생성 — 2026-05-09 ✅
- [sunolanguage] 사전 v3.0→v3.1 업데이트 (미등재 27개 어휘 추가) — 2026-05-09 ✅
- [sunolanguage] genre_frontier v1.1→v1.2 (15개 장르 must_have 네이티브 재작성) — 2026-05-09 ✅
- [sunolanguage] 책 1·2·5장 재작성 (곡 인용 제거, DB 데이터 반영) — 2026-05-09 ✅
- [sunolanguage] sunomusic에 W1 genre UPDATE 실행 요청 발송 — 2026-05-09 ✅
- [sunolanguage] S018 16곡 corpus 머지 (off-by-one 정정 포함, 437곡) — 2026-05-08 ✅
- [sunolanguage] genre_frontier v1.1 validated 업데이트 (16개 장르) — 2026-05-08 ✅
- [sunolanguage] suno_reanalysis DB 385행 적재 완료 — 2026-05-08 ✅
