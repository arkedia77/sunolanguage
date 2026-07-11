# 매칭 리포트 — run 14 (2026-07-11T11:48:16)

- 입력(track): Dreamy sequenced analog synthesizers with gentle arpeggiated patterns, warm pad layers building with slow modulation, classic Berlin school electronic textures with romantic cinematic atmosphere. 기차 안의 사랑 — 달리는 풍경 속 떨리는 첫 만남. romantic. electronic-train. Berlin-school. sequencer. forward-motion. cine…
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬+M3사전 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| C_1491 | 아직 거기 있어? | K-Pop ballad with jazz-pop influences | 0.5712 |
| 10464 | Horizon Step | Cinematic | 0.4649 |
| 82 | 공유 목록 | Indie Synth Pop / New Romantic | 0.4595 |
| C_1720 | 인데요, | K-Pop City Pop with elements of Funk and Jazz Fusion | 0.2692 |
| C_1732 | 같은 노래 다른 계절 | K-Pop and Funk-Pop fusion | 0.2692 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| Dreamy sequenced analog synthesizers with gentle arpeggiated patterns | A synth bass performs a melodic, walking line with a rounded, analog tone. | instrument | 197 |
| warm pad layers building with slow modulation | layered vocal harmonies, subtle synth pad | vocal_main | C_1374 |
| classic Berlin school electronic textures with romantic cinematic atmosphere | Intro | section | 180 |
| 기차 안의 사랑 — 달리는 풍경 속 떨리는 첫 만남 | Intro | section | 196 |
| romantic | Intro | section | 82 |
| electronic-train | Intro | section | 1696 |
| Berlin-school | Intro | section | S018_15 |
| forward-motion | Bridge | section | S018_11 |
| cinematic | Cinematic orchestral score. | genre | 10464 |
| 80s | Intro | section | C_1370 |
| dreamy | Intro | section | 1057 |
| flowing | Bridge | section | C_1491 |
| Sequenced Synths Arpeggiated sequences | clean arpeggiated electric guitar | instrument | 12 |
| sustained pads | choir sustained pads | vocal_chorus | S004_07 |
| warm analog lead | The production is intimate with minimal reverb on the vocals and a warm, analog-style saturation on the master bus. | vocal_main | 178 |
| evolving textures Spectral: warm | Atmospheric synth pads provide harmonic texture in the background. | instrument | 1167 |
| rich | Bridge | section | C_1732 |
| analog | A synth bass performs a melodic, walking line with a rounded, analog tone. | instrument | 197 |
| Temporal: forward-driving sequences | Soft, dry male vocals are positioned forward in the mix with minimal reverb. | mixing | 1626 |
| sustained pads | choir sustained pads | vocal_chorus | S004_07 |
| Character: romantic | Intro | section | 82 |
| cinematic | Cinematic orchestral score. | genre | 10464 |
| flowing | Bridge | section | C_1491 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **?**: The harmonic language is Romantic, utilizing chromatic passing tones and expressive modulations · Elegant acoustic waltz for guitar, violin, and cello. The acoustic guitar provides a gentle waltz accompaniment with bass notes on beat one and soft chords on beats two and three. The violin plays a lyrical melody with a warm, singing tone, using legato bowing. The cello adds a low melodic counterpoint, occasionally doubling the guitar bass line. The three instruments create a small chamber ensemble feel, intimate and refined. The energy is consistent throughout — graceful and flowing, never intense. Like string musicians playing softly at a special lunch occasion. Acoustic guitar, violin, cello. 88 BPM in D major. 3/4 time. Natural room acoustic. · Latin jazz instrumental with a warm, syncopated groove. Nylon-string acoustic guitar plays rhythmic montuno patterns with percussive muting and syncopated accents. Trumpet plays a bright, clean melody over the groove, staying in the middle register with a confident but not loud tone. Upright bass walks a Latin-flavored line with occasional syncopated fills. Congas provide the rhythmic foundation with a steady tumbao pattern. A shaker keeps sixteenth notes flowing. The energy is lively but controlled — perfect for a lunch with good company, not a nightclub. Nylon guitar, trumpet, upright bass, congas, shaker. 115 BPM in D minor. 4/4 time. Live room recording feel. · rapid hammer-on and pull-off sequences · The production is raw and aggressive, with the bass guitar occupying the center of the mix and utilizing a high-gain fuzz or overdrive pedal to create a thick, harmonically rich texture
- **arrangement**: The vocal delivery is intimate and breathy, utilizing a mix of chest voice and light head voice. · A soft, breathy female vocal performs a melodic line with gentle vibrato and intimate proximity. · The vocal delivery is intimate and close-mic'd, utilizing subtle vibrato on sustained notes. · full band energy, bright synth pads · The arrangement features a prominent slap bass line with syncopated sixteenth-note patterns and a bright, percussive character.
- **drums**: distorted synth bass, electronic percussion
- **genre**: Cinematic orchestral score. · Cinematic orchestral fusion with electronic elements. · K-Pop educational pop track. · K-Pop, City Pop. · Lo-fi hip hop track at 85 BPM in G minor.
- **harmony**: The 303 sequence uses a 16-step pattern with slides and accents, gradually increasing in brightness through filter modulation.
- **instrument**: A synth bass performs a melodic, walking line with a rounded, analog tone. · Minimalist arrangement with subtle, atmospheric synth pads providing a low-frequency bed. · The arrangement features bright, layered synthesizers including a sawtooth lead and shimmering pads. · full band energy, bright synth pads · A legato string section provides harmonic support with slow-moving pads.
- **mixing**: The male lead vocal is breathy and intimate, sitting forward in the mix with subtle plate reverb. · Soft, dry male vocals are positioned forward in the mix with minimal reverb. · A soft, melodic male vocal sits forward in the mix with light plate reverb.
- **section**: Intro · Verse 1 · Chorus · Bridge · Outro
- **vocal_chorus**: choir sustained pads
- **vocal_main**: layered vocal harmonies, subtle synth pad · intimate male vocals · The production is intimate with minimal reverb on the vocals and a warm, analog-style saturation on the master bus.

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- `sequencer` (best vector 0.407) → gap_candidates 등록
- `sensual` (best vector 0.438) → gap_candidates 등록

## (e) 음수필터 경고 (suno_does_not_use — SP에 넣지 말 것)

- 없음