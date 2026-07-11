# 매칭 리포트 — run 10 (2026-07-11T11:47:39)

- 입력(track): Impressionistic piano with extensive use of sustain pedal creating harmonic halos, wide dynamic range from pppp to forte, overtone-rich voicings exploiting sympathetic string resonance. 달빛 아래의 고요한 몽환 — 꿈결 같은 아름다움과 깊은 내면의 평화. moonlit. dreamlike. serene. ethereal. contemplative. nocturnal. intimate. t…
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬+M3사전 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| S004_03 | Flauta na Praia | ? | 0.3481 |
| 188 | 지하철 | Ethereal Ambient | 0.2808 |
| C_1480 | 하늘색 우산 | K-Pop track with a blend of funk and disco elements | 0.2671 |
| C_1725 | 같은 책이었다 | K-Pop power ballad featuring male tenor vocals and a rock-influenced arrangement | 0.2642 |
| C_1727 | 사실은 | K-Pop R&B track with a mid-tempo groove | 0.2531 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| Impressionistic piano with extensive use of sustain pedal creating harmonic halos | A Rhodes-style electric piano provides sustained harmonic pads in the background. | instrument | 1426 |
| wide dynamic range from pppp to forte | grand piano playing sustained chords, soft synth pad | instrument | 1046 |
| overtone-rich voicings exploiting sympathetic string resonance | Soft, breathy female vocals are processed with high-frequency air and moderate hall reverb. | vocal_main | 1145 |
| dreamlike | Intro | section | 1160 |
| serene | The production features high-fidelity clarity with a moderate hall reverb on the vocals and piano. | effect_electronic | 188 |
| ethereal | The production features high-fidelity clarity with a moderate hall reverb on the vocals and piano. | effect_electronic | 188 |
| contemplative | Pre-Chorus | section | C_1480 |
| nocturnal | Soft, breathy female vocals are processed with high-frequency air and moderate hall reverb. | vocal_main | 1135 |
| intimate | The arrangement is sparse and intimate. | arrangement | 1571 |
| tender | Bridge | section | C_1725 |
| luminous | full band energy, bright synth pads | instrument | C_1511 |
| Piano Wide arpeggios | grand piano arpeggios, legato strings | instrument | 1756 |
| extensive sustain pedal | A warm synth pad provides harmonic sustain. | instrument | 20003 |
| rubato | The arrangement centers on a grand piano playing rubato chords in the intro before settling into a steady 4/4 rhythm. | instrument | 1071 |
| pp-ppp dynamics | Acoustic rhythm guitar plays percussive la pompe style chords in 4/4 time. | tempo_key_time | S003_11 |
| legato touch with floating top notes Spectral: warm | Orchestral strings provide legato pads in the background. | instrument | 10046 |
| round | Bridge | section | C_1727 |
| overtone-rich from sustained pedal | overdriven electric guitar power chords, steady drum beat | drums | 171 |
| Temporal: soft attack | 4/4 time signature. | tempo_key_time | 160 |
| long resonant decay | A digital reverb with a short decay is applied to the vocals and guitar. | instrument | 154 |
| Character: luminous | The arrangement features a prominent slap bass line with syncopated sixteenth-note patterns and a bright, percussive character. | arrangement | 183 |
| liquid | Instrumental | section | S004_03 |
| shimmering | full synth arrangement, shimmering pads | arrangement | 1606 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **?**: Contemplative Korean Folk with gentle fingerpicked guitar and minimal percussion at mid tempo, featuring warm cello melodies and subtle string arrangements that create a profoundly peaceful atmosphere where silence speaks louder than words, the production emphasizes organic warmth and space through carefully miked acoustic instruments and natural room ambiance, incorporating gentle bass notes and occasional piano phrases that add depth without disturbing the meditative quality, the arrangement builds through gradual textural expansion while maintaining the contemplative core that captures the deep value of comfortable shared silence · The track features a distorted, overdriven kick drum with a long decay that creates a rhythmic rumble · single resonant drum hits with long decay · Drum and Bass, liquid rolling energy, fast breakbeat drums and deep rolling sub-bass, no vocals. 174 BPM in E minor. No four-on-the-floor — syncopated breakbeat pattern with snare on offbeats, rapid hi-hat variations, ghost notes on kick. Rolling sub-bass with long sustained notes following the chord progression. Atmospheric warm pads in minor key with occasional major chord lifts. Rhodes piano melodic phrase repeating over the breaks. Reverb on the pads, dry and punchy on the drums. Intro builds from pad and single snare hits into full breakbeat drop.
- **arrangement**: The arrangement is sparse and intimate. · The arrangement centers on a grand piano playing rubato block chords and arpeggios. · The dynamics utilize gradual crescendos and decrescendos throughout the arrangement. · The arrangement features a clean, funk-influenced electric guitar playing syncopated 16th-note rhythms and a melodic electric bass with a bright, round tone. · The arrangement features a clean, palm-muted electric guitar playing a rhythmic eighth-note pattern and a warm synth bass with a soft attack.
- **drums**: rimshot on backbeat · drums and bass continue, guitar chords sustain · overdriven electric guitar power chords, steady drum beat
- **effect_electronic**: The production features high-fidelity clarity with a moderate hall reverb on the vocals and piano. · The production is clean and dry with minimal reverb, emphasizing the acoustic transients of the plucked and bowed strings.
- **genre**: Bossa Nova.
- **instrument**: A Rhodes-style electric piano provides sustained harmonic pads in the background. · Electric piano and shimmering synth pads fill the harmonic space. · Bright polyphonic synth pads provide harmonic sustain. · grand piano playing sustained chords, soft synth pad · A subtle synth pad fills the mid-range frequency spectrum.
- **mixing**: The production uses high-fidelity reverb on the vocals and strings to create a large acoustic space.
- **section**: Intro · Outro · Chorus · Pre-Chorus · Bridge
- **tempo_key_time**: Acoustic rhythm guitar plays percussive la pompe style chords in 4/4 time. · 4/4 time signature. · Key of E Major.
- **vocal_chorus**: melodic singing, layered vocal harmonies
- **vocal_main**: Soft, breathy female vocals are processed with high-frequency air and moderate hall reverb. · The vocal performance is intimate and breathy, utilizing a close-mic technique with light plate reverb. · The production is minimalist, focusing on the clarity of the vocal and the resonance of the acoustic strings. · A bright, percussive synth pluck enters during the chorus, doubling the vocal melody. · vocal harmony

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- `달빛 아래의 고요한 몽환 — 꿈결 같은 아름다움과 깊은 내면의 평화` (best vector 0.323) → gap_candidates 등록
- `moonlit` (best vector 0.349) → gap_candidates 등록
- `impressionistic` (best vector 0.339) → gap_candidates 등록

## (e) 음수필터 경고 (suno_does_not_use — SP에 넣지 말 것)

- ⚠️ `pp` → 다이나믹 마킹(p/mf/ff…) — Suno 0회