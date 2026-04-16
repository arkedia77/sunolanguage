# Suno 네이티브 어휘 — 전체 맵 (v2 초안)

- 곡(유니크 song_id): **318**
- Suno 재분석 clips: **326**
- 출처: leomusic 생성곡 1분 컷 → Suno 앱 재업로드 → 자체 분석 SP+가사 수집

## 1. 장르 그룹 × 곡수

| 그룹 | 곡수 |
|------|-----:|
| Pop 계열 | 147 |
| 기타 | 29 |
| Rock 계열 | 28 |
| Folk/Acoustic | 28 |
| R&B 계열 | 27 |
| Ballad | 17 |
| Electronic/Ambient | 16 |
| Hip-Hop 계열 | 11 |
| Jazz | 9 |
| 미정 | 4 |
| Orchestral/Cinematic | 2 |

## 2. 카테고리 전역 포화도 (Suno SP 내)

| 카테고리 | 총 출현 | 고유 표현 | 상위 예시 |
|----|---:|---:|---|
| 악기 | 2203 | 28 | guitar(529), bass(280), drum(236), kick(216), snare(188) |
| 주법/연주 | 431 | 19 | syncopated(159), arpeggiated(74), backbeat(48), palm-muted(47), fingerpicked(47) |
| 프로덕션 | 470 | 16 | chorus(187), reverb(170), compression(32), distorted(32), delay(14) |
| 무드/감정 | 932 | 22 | crisp(136), bright(110), intimate(105), tight(94), warm(91) |
| 템포/BPM | 327 | 27 | 72 bpm(97), 92 bpm(26), 105 bpm(21), 88 bpm(20), 115 bpm(19) |
| 조성/Key | 293 | 14 | key of e major(131), key of g major(73), key of c major(31), g major(19), key of g minor(9) |
| 보컬 | 614 | 13 | breathy(155), male vocals(126), tenor(93), baritone(82), male vocal(51) |
| 음색/텍스처 | 782 | 13 | clean(252), crisp(136), bright(110), warm(91), muted(83) |
| 하모니/화성 | 323 | 5 | major(270), minor(27), seventh(22), ninth(3), chromatic(1) |
| 구조/다이내믹스 | 231 | 9 | chorus(187), verse(17), intro(9), swells(5), swell(5) |
| 시간서명 | 161 | 1 | 4/4 time(161) |
| 장르 자칭 | 510 | 12 | k-pop(245), jazz(54), rock(52), r&b(50), electronic(41) |

## 3. 장르 그룹 × 카테고리 히트 매트릭스

| 장르 그룹 | 악기 | 주법/연주 | 프로덕션 | 무드/감정 | 템포/BPM | 조성/Key | 보컬 | 음색/텍스처 | 하모니/화성 | 구조/다이내믹스 | 시간서명 | 장르 자칭 |
|----|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pop 계열 | 1041 | 189 | 216 | 450 | 150 | 130 | 288 | 361 | 147 | 106 | 73 | 227 |
| 기타 | 203 | 45 | 44 | 97 | 30 | 26 | 54 | 79 | 27 | 22 | 15 | 46 |
| Rock 계열 | 203 | 40 | 49 | 68 | 29 | 28 | 45 | 78 | 29 | 27 | 11 | 45 |
| Folk/Acoustic | 195 | 42 | 31 | 78 | 30 | 28 | 56 | 73 | 31 | 14 | 19 | 49 |
| R&B 계열 | 192 | 46 | 41 | 75 | 29 | 26 | 55 | 58 | 28 | 15 | 17 | 43 |
| Ballad | 105 | 21 | 17 | 53 | 17 | 14 | 35 | 46 | 15 | 10 | 10 | 28 |
| Electronic/Ambient | 85 | 15 | 26 | 42 | 16 | 15 | 36 | 32 | 15 | 12 | 8 | 26 |
| Hip-Hop 계열 | 81 | 11 | 20 | 29 | 11 | 11 | 16 | 25 | 15 | 12 | 1 | 20 |
| Jazz | 55 | 13 | 14 | 25 | 9 | 9 | 17 | 18 | 10 | 8 | 4 | 17 |
| 미정 | 31 | 7 | 10 | 10 | 4 | 4 | 8 | 8 | 4 | 4 | 2 | 8 |
| Orchestral/Cinematic | 12 | 2 | 2 | 5 | 2 | 2 | 4 | 4 | 2 | 1 | 1 | 1 |

## 4. 가사 브래킷 시스템 (총 출현 / 고유)

| 추정 타입 | 출현 | 고유 | 상위 예시 |
|----|---:|---:|---|
| section | 1010 | 40 | [verse 1](326), [intro](317), [chorus](215), [pre-chorus](59), [verse 2](39) |
| instrument_or_arrangement | 244 | 40 | [fingerpicked acoustic guitar](29), [bass guitar enters](18), [kick drum enters](14), [fingerpicked acoustic guitar arpeggio](12), [shaker enters](11) |
| effect | 330 | 40 | [chorus](215), [pre-chorus](59), [synth pads swell](6), [clean electric guitar arpeggio with chorus effect](4), [guitar feedback swell](3) |
| vocal_direction | 285 | 40 | [breathy male vocals](58), [breathy female vocals](28), [male vocals](23), [male tenor vocals](21), [smooth male vocals](12) |
| transition_cue | 176 | 40 | [bass guitar enters](18), [kick drum enters](14), [shaker enters](11), [electric bass enters](11), [male vocals enter](10) |
| uncategorized | 61 | 40 | [brass stabs](5), [crash cymbal](4), [rimshot on backbeat](4), [cymbal crash](4), [unintelligible](3) |

## 5. 구멍 리스트 (우선 검토)

**장르 그룹별 얇은 영역**: 본 맵 §3에서 값이 0~5인 셀 — 해당 장르·카테고리는 현재 데이터로 매뉴얼 엔트리 생성 시 근거 부족. 추가 업로드 타겟 후보.

**주요 공백 관찰**:
- **Orchestral/Cinematic** (2곡): 얇은 카테고리 → 주법/연주, 프로덕션, 템포/BPM, 조성/Key, 보컬, 음색/텍스처, 하모니/화성, 구조/다이내믹스, 시간서명, 장르 자칭
- **Jazz** (9곡): 얇은 카테고리 → 시간서명