# 매칭 리포트 — run 5 (2026-07-10T17:49:52)

- 입력(nuance_text): warm fingerpicked acoustic guitar enters, mellow Cmaj7 arpeggios, II-V-I turnaround, mf dynamics, cello swells
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬+M3사전 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| C_1458 | 이름 없는 불안 | K-Indie folk ballad | 0.2382 |
| C_1764 | 실밥 | K-Pop ballad | 0.0856 |
| 1273 | 크레딧이 올라가는 동안 | R&B Soul | 0.0843 |
| C_1393 | 쿨한 척 삼 분 | K-Pop ballad with acoustic folk influences | 0.0842 |
| S004_05 | Klezmer Clarinet | ? | 0.0697 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| warm fingerpicked acoustic guitar enters | fingerpicked acoustic guitar | instrument | C_1458 |
| mellow Cmaj7 arpeggios | grand piano arpeggios | instrument | C_1764 |
| II-V-I turnaround | snare enters with reverb | effect_electronic | 928 |
| mf dynamics | The dynamics utilize gradual crescendos and decrescendos throughout the arrangement. | arrangement | 10472 |
| cello swells | synth pad swells | instrument | 1150 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **arrangement**: The dynamics utilize gradual crescendos and decrescendos throughout the arrangement. · The arrangement uses frequent stop-start dynamics and rhythmic breaks.
- **effect_electronic**: snare enters with reverb · final cello note decays into reverb
- **instrument**: fingerpicked acoustic guitar · Fingerpicked acoustic guitar with a warm, resonant tone. · acoustic guitar enters, fingerpicked · grand piano arpeggios · melodic singing, guitar arpeggios
- **vocal_main**: Subtle vocal doubling and harmony stacks appear on key phrases.

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- 없음

## (e) 음수필터 경고 (suno_does_not_use — SP에 넣지 말 것)

- ⚠️ `Cmaj7` → 구체적 코드명(Am, Dm7, Cmaj7…) — Suno 0회. 'key of X'만 유효
- ⚠️ `II-V-I` → 코드 진행 표기(II-V-I…) — Suno 0회
- ⚠️ `mf` → 다이나믹 마킹(p/mf/ff…) — Suno 0회