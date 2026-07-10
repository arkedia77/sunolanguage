# 매칭 리포트 — run 3 (2026-07-10T17:45:44)

- 입력(nuance_text): distorted cowbell drift phonk, Memphis chant, gqom log-drum darkness
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| S018_11 | MidnightDrift | Drift Phonk | 0.3531 |
| C_1509 | 건배사가 끝나면 | K-Hip Hop track featuring male rap vocals and melodic R&B-style hooks | 0.2692 |
| S018_15 | CallAndResponse | Afrobeats | 0.1491 |
| S018_03 | LagosToJohannesburg | Amapiano | 0.1210 |
| 108 | ? | ? | 0.0772 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| distorted cowbell drift phonk | distorted cowbell melody, 808 bass enters | drums | S018_11 |
| Memphis chant | Chorus | section | C_1509 |
| gqom log-drum darkness | log drum pattern intensifies | drums | S018_03 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **?**: log drum drops out
- **arrangement**: The arrangement features a prominent cowbell melody playing a syncopated, repetitive riff.
- **drums**: distorted cowbell melody, 808 bass enters · log drum pattern intensifies
- **effect_electronic**: A distorted 808 bassline follows the root notes with heavy saturation.
- **instrument**: Features a deep, percussive log drum bassline playing syncopated patterns.
- **section**: Chorus
- **vocal_chorus**: choir staccato chants
- **vocal_main**: Male vocals are delivered in a rhythmic, chant-like style with call-and-response elements.

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- 없음