# 매칭 리포트 — run 2 (2026-07-10T17:45:17)

- 입력(nuance_text): misty riverside cello at dawn, restrained and muted, like fog over water
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| 1146 | 안경을 닦는 손 | Piano Ballad | 0.0862 |
| C_1481 | 창문이 처음이야 | K-Pop | 0.0747 |
| C_1519 | 이유 없는 꽃다발 | K-Pop with elements of funk and disco | 0.0640 |
| 10464 | Horizon Step | Cinematic | 0.0555 |
| 210 | 선택하지 않은 것 | Ambient Indie | 0.0550 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| misty riverside cello at dawn | solo cello enters | instrument | 136 |
| restrained and muted | Clean electric guitar plays rhythmic muted scratches and staccato chords. | instrument | 1146 |
| like fog over water | Atmospheric synth pads and vocal harmonies add depth to the background. | instrument | C_1479 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **instrument**: solo cello enters · violin and cello enter · cello swells · Clean electric guitar plays rhythmic muted scratches and staccato chords. · muted syncopated electric guitar, melodic bass guitar, steady drum beat
- **vocal_main**: vocalizing

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- 없음