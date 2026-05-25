# W002 Wave 2 장르 균등화 60곡 프로토콜

**설계일**: 2026-05-25
**목적**: W1 326곡의 장르 편중(Ballad 25.5% vs Dance 0.6%) 완화
**담당**: sunolanguage 자체 영역 (sunomusic 5/17 확인)

---

## 1. W1 장르 불균형 현황

| 대장르 | W1 곡수 | 비율 | 상태 |
|--------|--------:|-----:|------|
| K-Pop Ballad | 83 | 25.5% | 과다 |
| K-Indie | 68 | 20.9% | 과다 |
| K-Pop R&B | 44 | 13.5% | 적정 |
| K-Rock | 39 | 12.0% | 적정 |
| K-Funk | 31 | 9.5% | 소폭 부족 |
| Other | 22 | 6.7% | 부족 |
| K-Hip Hop | 20 | 6.1% | 부족 |
| K-Synth Pop | 14 | 4.3% | 부족 |
| K-Ballad | 3 | 0.9% | 심각 부족 |
| K-Pop Dance | 2 | 0.6% | 심각 부족 |
| K-Trot | 0 | 0.0% | 전무 |

균등 기준: (326+60)/11 = **35곡/장르**
불균형 비율: 41.5x (Ballad 83 vs Dance 2)

---

## 2. W002 60곡 배분안

| 대장르 | 추가 | W1→W1+W2 | 목표 비율 |
|--------|-----:|--------:|-------:|
| K-Trot | **13** | 0→13 | 3.4% |
| K-Pop Dance | **13** | 2→15 | 3.9% |
| K-Ballad | **13** | 3→16 | 4.1% |
| K-Synth Pop | **8** | 14→22 | 5.7% |
| K-Hip Hop | **6** | 20→26 | 6.7% |
| Other (Western) | **5** | 22→27 | 7.0% |
| K-Funk | **2** | 31→33 | 8.5% |
| **합계** | **60** | 326→386 | |

> K-Rock(39), K-Pop R&B(44), K-Indie(68), K-Pop Ballad(83)은 이미 충분 → 추가 없음.

---

## 3. 장르별 곡 선정 기준

### K-Trot (+13곡)
- **서브장르 분산**: 전통 트로트(5) / 뽕짝(3) / 모던 트로트(3) / K-Pop Trot(2)
- **핵심 악기**: accordion, saxophone, disco bass, foxtrot rhythm
- **코퍼스 매핑**: TROT → foxtrot + disco bass + accordion + sax (메모리 확인)
- **선곡 원칙**: 남녀 비율 6:7, 다양한 BPM (100~140)

### K-Pop Dance (+13곡)
- **서브장르 분산**: EDM Dance(5) / Tropical House(3) / Future Bass(3) / Moombahton(2)
- **핵심 악기**: synth bass, four-on-the-floor kick, sidechain compression
- **BPM 범위**: 120~135
- **선곡 원칙**: 아이돌 스타일 포함, 고에너지 편성

### K-Ballad (+13곡)
- **K-Ballad vs K-Pop Ballad 구분**: K-Ballad은 전통적 한국 발라드 (오케스트라+피아노 중심)
- **서브장르 분산**: Orchestra Ballad(5) / Piano Ballad(4) / Rock Ballad(4)
- **핵심 악기**: grand piano, string section, solo cello
- **BPM 범위**: 60~80
- **선곡 원칙**: W1의 K-Pop Ballad과 차별화 — 더 전통적·클래식한 편성

### K-Synth Pop (+8곡)
- **서브장르 분산**: Synthwave(3) / Electro Pop(3) / City Pop Revival(2)
- **핵심 악기**: analog synth, sawtooth bass, gated reverb
- **BPM 범위**: 110~130

### K-Hip Hop (+6곡)
- **서브장르 분산**: Boom Bap(2) / Trap(2) / Jazz Rap(2)
- **핵심 악기**: 808 bass, hi-hat rolls, sample chops
- **BPM 범위**: 80~145 (Boom Bap 85~95, Trap 130~145)

### Other/Western (+5곡)
- **미확보 장르 우선**: Latin(2) / Classical(1) / Reggae(1) / Blues(1)
- **목적**: S018 genre_frontier 테스트에서 확인된 장르 보강

### K-Funk (+2곡)
- **부족 서브장르**: Disco-Funk(1) / Synth-Funk(1)
- **핵심 악기**: slap bass, staccato rhythm, bright horns

---

## 4. 수집 파이프라인

```
1. 곡 선정 → Leo 녹음 목록 작성 (60곡)
2. Leo → Suno 앱 녹음 (~10초 × 60곡)
3. Suno 재분석 → SP/가사/장르 4값 수집
4. sunolanguage → merged_4values.json 병합 + DB 적재
5. 장르 분포 재검증
```

---

## 5. 예상 일정

| 단계 | 소요 | 비고 |
|------|------|------|
| 곡 선정 | 1일 | sunolanguage 자체 |
| Leo 녹음 | 2~3일 | Leo 가용성 의존 |
| Suno 재분석 수집 | 1일 | sunolanguage 자체 (Suno 앱) |
| DB 적재 + 분석 | 0.5일 | json_to_db.py 활용 |

---

## 6. 성공 기준

- W1+W2 합산 시 **최대/최소 장르 비율 < 10x** (현재 41.5x)
- 11개 대장르 전부 **10곡 이상**
- K-Trot 코퍼스 **0→13곡** 확보
