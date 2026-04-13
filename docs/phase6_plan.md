# Phase 6 기획 — 보컬/보이싱 데이터 보강

**기획일**: 2026-04-13
**목적**: 스템 기반 수집의 보컬 한계(vocals 68% 성공률, 54개 어휘) 극복
**전략**: **전곡 업로드**로 Suno가 뱉는 보컬 디렉션 어휘 수집

---

## 배경 — 왜 전곡 업로드인가

| 항목 | 기존 (Phase 1-5) | Phase 6 |
|------|------------------|---------|
| 입력 | Demucs 스템 분리 (drums/bass/vocals/other) | 전곡 (mix 그대로) |
| 보컬 성공률 | 68% (낮음) | 100% (분리 X) |
| 수집 대상 | 악기별 주법/음색 중심 | **보컬 디렉션/그레인/테크닉** 중심 |
| 장르 | 기존 70개 + 신규 확장 | 1순위 장르 집중 |

**leomusic-base 리뷰 반영**: vocal grain 15종 + voice tag 47종 + falsetto/belt/head voice 테크닉 표현 — base export + Phase 6 자체 수집 병행.

---

## 수집 목표

### 어휘 카테고리
- **보컬 그레인**: breathy, raspy, silky, gritty, airy, nasal, smoky, husky, whispered
- **보컬 테크닉**: falsetto, belt, head voice, chest voice, mixed voice, vibrato variants, melisma, riffs, runs
- **보컬 딜리버리**: spoken, sung, rapped, chanted, narrated, whispered
- **보컬 레이어**: doubled, harmonized, stacked, call-response
- **보컬 이펙트**: autotuned, vocoded, pitched-down, pitched-up, reversed, chopped

### 수치 목표
- 보컬 어휘 54개 → **200개 이상** (약 4배)
- 신규 장르 10개 이상 커버 (1순위 장르 기준)

---

## 대상 장르 (leomusic-base Q4 우선순위 1순위)

| 장르 | 목표 곡수 | 이유 |
|------|----------|------|
| K-Pop (메인스트림) | 30곡 | 한국 시장 최상위, base 데이터 완비 |
| K-Pop 서브장르 (발라드, 댄스, 힙합) | 20곡 | 서브장르 보컬 스타일 차이 |
| R&B / Neo-Soul | 25곡 | 보컬 그레인/멜리스마 핵심 장르 |
| Lo-fi Hip-Hop (보컬 포함) | 15곡 | 필터드 보컬, 샘플 보컬 표현 |
| **소계** | **90곡** | |

---

## 수집 프로세스

1. **곡 선정** — 각 장르 대표곡 + 보컬 스타일 다양성 확보 (상업곡, 인디, 레퍼런스)
2. **Suno 앱 업로드** — 전곡(스템 분리 X) → Suno 네이티브 분석
3. **프롬프트 수집** — 생성된 tags + prompt를 JSON으로 저장
4. **파싱** — `parse_suno_vocab.py` (기존 파이프라인 재사용, `genre_label` 정상 동작 확인됨)
5. **RAG 재빌드** — `build_rag_index.py` + `build_suno_dictionary.py`
6. **커버리지 검증** — 보컬 어휘 54 → 200+ 달성 여부 측정

---

## 산출물

- `data/raw/phase6/` — 원본 Suno 응답 90곡
- `data/prompts/phase6_*.json` — 파싱용 구조화 데이터
- `data/parsed/` — 전체 vocab_index 재생성
- `rag/vocal_index.json` — **신규**: 보컬 전용 검색 인덱스
- `docs/phase6_vocabulary_report.md` — 수집 결과 보고서
- 노션 업데이트 — 어휘 사전 v1.2 (보컬 대폭 확장)

---

## 의존성 & 전제

- **sunomusic**: Suno 앱 업로드 담당 (역할 정리 2026-04-12 기준)
- **90곡 업로드 일정**: sunomusic 가용성 확인 필요 → 별도 협의 메시지 발송
- **leomusic-base export**: 화성/보컬/다이나믹스 데이터 (2026-04-13 요청) 수신 후 병합

---

## 마일스톤 (잠정)

| 단계 | 내용 | 예상 시기 |
|------|------|-----------|
| M1 | 곡 리스트 확정 (90곡) + sunomusic 일정 협의 | Phase 5 정리 마무리 후 |
| M2 | K-Pop 30곡 업로드 + 파싱 | M1 후 3-5일 |
| M3 | R&B/Neo-Soul 25곡 + Lo-fi 15곡 | M2 후 3-5일 |
| M4 | 파싱 + RAG 재빌드 + 보고서 | M3 후 1일 |
| M5 | 어휘 사전 v1.2 노션 업데이트 + 각 프로젝트 전달 | M4 후 |

---

## 리스크

1. **Suno 앱이 전곡에 대해 보컬 디렉션을 일관되게 뱉는가** — 소수 샘플로 사전 검증 필요 (M1 단계에 3-5곡 파일럿)
2. **상업곡 업로드 저작권** — Leo 판단 필요 (개인 분석 용도로 수집, 재배포 X)
3. **장르 라벨링 편차** — Suno가 K-Pop을 "pop / dance pop / electropop" 등으로 분산 라벨링할 수 있음 → normalize_genres.py 확장 필요

---

## 다음 액션

1. Leo 승인 후 M1 착수
2. sunomusic에 Phase 6 일정 협의 메시지 발송
3. 파일럿 5곡 선정 (K-Pop 3 + R&B 2) — Suno 보컬 디렉션 품질 확인
