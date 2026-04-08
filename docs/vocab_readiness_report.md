# Sunolanguage 어휘 활용 준비도 보고서

**작성일**: 2026-04-08
**데이터**: 82곡 → 241 스템 성공 (73%), 11장르

---

## 1. 판정 기준 (3단계)

| 등급 | 기준 | 의미 |
|------|------|------|
| A ★ | tags≥20 & vocab≥60 | **즉시 적용** — leomusic2 SP 생성에 바로 투입 |
| B ◆ | tags≥10 & vocab≥40 | **보강 후 적용** — Base 매칭 보강 후 사용 |
| C △ | tags<10 | **추가 수집** — 곡 수집 더 필요 |

- tags = 수집된 Suno tags 수 (스템별 1개)
- vocab = 고유 악기 + 주법 종류 수

---

## 2. 장르별 판정 결과

| 장르 | tags | 악기 | 주법 | vocab | 등급 |
|------|------|------|------|-------|------|
| Jazz | 39 | 38 | 40 | 78 | A ★ |
| Electronic / Ambient | 39 | 34 | 31 | 65 | A ★ |
| Hybrid / Cinematic | 29 | 40 | 25 | 65 | A ★ |
| Lo-fi / Neo-classical / Piano | 24 | 33 | 33 | 66 | A ★ |
| Contemporary Instrumental | 22 | 34 | 26 | 60 | A ★ |
| Post-Rock | 18 | 29 | 24 | 53 | B ◆ |
| Film Score / OST | 17 | 34 | 25 | 59 | B ◆ |
| World Music | 16 | 32 | 27 | 59 | B ◆ |
| Guitar Instrumental | 14 | 25 | 26 | 51 | B ◆ |
| Funk / Soul / Blues Instrumental | 14 | 31 | 26 | 57 | B ◆ |
| New Age | 9 | 26 | 17 | 43 | C △ |

**A등급 5개, B등급 5개, C등급 1개**

---

## 3. 어휘 총량

| 카테고리 | sunolang | Base | 매칭률 |
|---------|---------|------|--------|
| 악기 | 68종 | 372종 | 47% (32/68) |
| 주법 | 64종 | 57종 | 17% (11/64) |
| 프로덕션 | 34종 | 63종 | 23% (8/34) |

### 매칭률이 낮은 이유
- Suno는 **복합 표현** 사용: "arpeggiated guitar", "syncopated kick", "distorted bass"
- Base는 **정규화된 canonical name** 사용: "guitar", "bass guitar"
- → **aliases 테이블**로 매핑하면 70%+ 가능 (leomusic-base F 로드맵)

### Suno 고유 표현 (Base에 없는 것, 가치 높음)
- 악기: distorted bass, distorted kick, acoustic drum kit, distorted synth, slap bass 등
- 주법: arpeggiated, fingerpicking, chromatic run, double-stop, call-and-response 등
- 프로덕션: crisp, punchy, atmospheric, analog, lo-fi, bright, dry 등

---

## 4. 활용 전략

### Phase 1: A등급 5장르 즉시 적용 (→ leomusic2)
- Jazz, Electronic/Ambient, Hybrid/Cinematic, Lo-fi/Neo-classical, Contemporary Instrumental
- sunolang 어휘 → leomusic2 SP 생성 시 참조 데이터로 제공
- 방식: exports/JSON 또는 API 엔드포인트

### Phase 2: Base aliases 구축 (→ leomusic-base)
- sunolang 68악기 + 64주법 → Base element_id 매핑
- 매칭률 47% → 70%+ 목표
- B등급 5장르도 이 단계 후 투입 가능

### Phase 3: 추가 수집
- C등급 New Age: 곡 수집 5~10곡 추가 필요
- 실패 스템 재시도 (50MB 잔여 41스템 + 기타 46스템)

---

## 5. leomusic-base 인터페이스 현황

이미 구축 완료:
- `~/leomusic-base/exports/` — instruments/articulations/genres/vocals/production JSON
- `~/leomusic-base/scripts/sunolang_interface.py` — Python 클래스
- `sunolang_gap_analysis.json` — 갭 분석 결과

sunolanguage가 해야 할 것:
- A등급 장르 어휘를 **leomusic2가 참조 가능한 형태**로 내보내기
- leomusic-base aliases 반영 요청
