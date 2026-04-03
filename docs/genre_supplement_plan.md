# 데이터 부족 장르 보강 계획

**작성일**: 2026-04-03
**현황**: 342곡 / 59장르 파싱 완료

---

## 보강 우선순위

### Tier 1: 최우선 보강 (용어 10개 미만, 6장르)

| 장르 | 현재 용어 수 | 보강 목표 | 비고 |
|------|------------|----------|------|
| alt rock | 2 | 30+ | 대중적 장르인데 데이터 극소 |
| amapiano | 2 | 20+ | 아프리카 신흥 장르, 고유 어휘 확보 가치 높음 |
| drum and bass | 6 | 30+ | 전자음악 핵심 장르 |
| flamenco | 6 | 30+ | 고유 주법/악기 어휘 풍부할 것으로 예상 |
| math rock | 6 | 30+ | 복잡한 박자/주법 어휘 기대 |
| chillout | 7 | 20+ | lo-fi 계열과 겹칠 수 있으나 독립 확보 필요 |

### Tier 2: 보강 권장 (용어 10-19개, 13장르)

| 장르 | 현재 용어 수 | 비고 |
|------|------------|------|
| country | 10 | 미국 전통, 악기 어휘 중요 |
| lofi hip-hop | 10 | lo-fi hip hop(18)과 통합 검토 |
| psychedelic pop-rock | 10 | psychedelia(17)와 통합 검토 |
| sacred | 10 | liturgical(35), worship(49)과 관계 정리 필요 |
| darkwave | 14 | 독자적 신스/분위기 어휘 |
| pop-rock | 14 | pop rock(17)과 통합 필요 |
| new wave | 16 | 80s 특유 프로덕션 어휘 |
| post-rock | 17 | 구조적 어휘 기대 (crescendo, layering) |
| stoner rock | 17 | 퍼즈/리버브 프로덕션 어휘 |
| dubstep | 18 | 베이스 디자인 어휘 |
| tech house | 18 | 전자음악 프로덕션 |
| afrobeat | 19 | 리듬 패턴 어휘 풍부할 것 |
| synthwave | 24 | 80s 신스 프로덕션 |

### 장르명 통합 필요 (중복 해소)

- `lo-fi hip hop` (18) + `lo-fi hip-hop` (17) + `lofi hip-hop` (10) → 통합
- `hip hop` (70) + `hip-hop` (57) → 통합
- `pop rock` (17) + `pop-rock` (14) → 통합
- `boom bap` (54) + `boom-bap` (22) → 통합
- `psychedelia` (17) + `psychedelic pop-rock` (10) + `neo-psychedelia` (25) → 관계 정리

---

## 수집 방법

1. **Suno 앱 녹음**: 해당 장르 대표곡을 Suno에 녹음 → 프롬프트 수집
   - Tier 1 장르당 최소 10곡 목표
   - sunomusic에 장르별 녹음 요청 가능

2. **기존 데이터 장르 재분류**: 342곡 중 잘못 분류된 곡 재검토

3. **장르명 정규화 스크립트**: 중복 장르명 통합 처리

---

## 예상 효과

- 현재 59장르 → 통합 후 약 50장르 (정규화)
- Tier 1 보강 시: 빈약 장르 0개 달성
- 총 어휘 커버리지 향상 → RAG 검색 품질 개선
