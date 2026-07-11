# 매칭 리포트 — run 11 (2026-07-11T11:47:49)

- 입력(track): Melancholic jazz piano loop with tape wobble, soft side-chained pads, muted hi-hats and vinyl rain noise creating a late-night contemplative atmosphere. 고독 — 비 오는 밤 혼자만의 시간의 따뜻한 위안. lonely. warm. lo-fi. rainy. intimate. bedroom. vinyl-warm. contemplative. headphone. solitary. Lo-fi Production Sample…
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬+M3사전 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| C_1505 | 거울 앞의 유전자 | K-Pop Ballad | 0.5384 |
| 1175 | 별점 2.3 | Lo-fi Pop | 0.4150 |
| C_1477 | 두 번째 좌표 | K-Rock track with pop-punk and alternative rock influences | 0.2827 |
| S004_03 | Flauta na Praia | ? | 0.2824 |
| 1571 | 서른두 번째 도장 | Bossa Nova | 0.2590 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| Melancholic jazz piano loop with tape wobble | piano loop fades out with increasing reverb | effect_electronic | 10466 |
| soft side-chained pads | strings enter, soft legato pads | instrument | 1103 |
| muted hi-hats and vinyl rain noise creating a late-night contemplative atmosphere | Atmospheric vinyl crackle and ambient city street noise are layered throughout the arrangement. | effect_sound | 10466 |
| 고독 — 비 오는 밤 혼자만의 시간의 따뜻한 위안 | Verse 1 | section | 1259 |
| lonely | Chorus | section | C_1509 |
| warm | warm electric bass enters | instrument | 127 |
| lo-fi | Intro | section | 1175 |
| intimate | The arrangement is sparse and intimate. | arrangement | 1571 |
| bedroom | Intro | section | 169 |
| vinyl-warm | A subtle vinyl crackle layer persists throughout the track. | effect_sound | S004_03 |
| contemplative | Pre-Chorus | section | C_1480 |
| headphone | slap bass, electronic drums, bright synth pads | instrument | 1539 |
| solitary | Intro | section | C_1477 |
| Lo-fi Production Sampled melody | The production is clean with minimal reverb, emphasizing the interplay between the rhythmic guitar and the vocal melody. | instrument | 1636 |
| dusty drums | drums enter | drums | C_1367 |
| vinyl crackle | vinyl crackle, clean electric guitar chords | instrument | S004_03 |
| tape saturation | A distorted 808 bassline follows the root notes with heavy saturation. | effect_electronic | S018_11 |
| lo-fi processing Spectral: warm | Shimmering polyphonic synth pads and a subtle brass section provide harmonic depth during the transitions. | instrument | 1486 |
| muffled | soft muffled kick drum enters | effect_sound | 1046 |
| lo-fi | Intro | section | 1175 |
| Temporal: slow | 4/4 time signature. | tempo_key_time | 20006 |
| laid-back | Outro | section | C_1392 |
| Character: lonely-warm | Intro | section | 162 |
| intimate | The arrangement is sparse and intimate. | arrangement | 1571 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **?**: Folk, Acoustic Folk in G Major. 68 BPM. Low energy with rubato fingerpicking and old inn wooden warmth. Soft vocals lonely peaceful, past-tense narrative delivery, tactile descriptive phrasing, voice close as if speaking to oneself in an empty room. Steel string acoustic guitar Travis picking warm, harmonica single note melody on chorus breathy, no drums foot tap on wood floor, guitar bass notes provide bottom. Wooden stair creak on verse transitions, key turning in lock metallic on bridge. Simple folk progressions, G to C to D, Travis picking providing bass and melody. A metal key with a wooden tag marked 301 — the warmth it holds from your palm and the cold it returns by morning. Single mic guitar and voice, room tone preserved, wood resonance, no processing. Korean lyrics throughout. · Contemplative Korean Folk with gentle fingerpicked guitar and minimal percussion at mid tempo, featuring warm cello melodies and subtle string arrangements that create a profoundly peaceful atmosphere where silence speaks louder than words, the production emphasizes organic warmth and space through carefully miked acoustic instruments and natural room ambiance, incorporating gentle bass notes and occasional piano phrases that add depth without disturbing the meditative quality, the arrangement builds through gradual textural expansion while maintaining the contemplative core that captures the deep value of comfortable shared silence · Warm mid-low energy vocal with standard form structure, intimate portrayal of solitary moment in empty classroom after school, reflective narrative capturing relational nostalgia and fleeting moments with classmates, acoustic arrangement with subtle string accompaniment, school ambience implied through minimal sound design, 90-100 BPM, contemplative yet accessible tone, theme of temporary solitude and relationships captured through spatial emptiness and lingering memories, tender and understated emotional delivery · dusty drum break enters
- **arrangement**: The arrangement is sparse and intimate. · A subtle vinyl crackle texture persists throughout the arrangement. · The arrangement features a prominent slap bass line with syncopated sixteenth-note patterns and a bright, percussive character.
- **drums**: A warm synth bass enters on the first beat of the verse. · drums enter · bass and drums enter · A soft, muffled kick drum enters on the downbeats. · distorted electric guitar feedback, slow heavy drum fill
- **effect_electronic**: piano loop fades out with increasing reverb · The recording has a dry, intimate room acoustic with minimal reverb on the vocals. · A distorted 808 bassline follows the root notes with heavy saturation.
- **effect_sound**: jazzy piano loop, vinyl crackle, light percussion · Atmospheric vinyl crackle and ambient city street noise are layered throughout the arrangement. · water droplet sound · A subtle vinyl crackle layer persists throughout the track. · clean electric guitar arpeggio, vinyl crackle
- **genre**: K-Pop Hip-Hop track featuring a rhythmic piano loop playing syncopated jazz chords. · K-Pop ballad. · Indie pop with a laid-back, mid-tempo groove.
- **instrument**: strings enter, soft legato pads · The arrangement uses side-chain compression on the pads and occasional vocal doubling. · Rhodes piano enters with soft pads · Atmospheric elements include shimmering synth pads and a recurring, high-pitched flute or woodwind motif that echoes the cello's phrases. · Guitar Solo
- **mixing**: The production features high-fidelity vocal processing with moderate plate reverb.
- **section**: Verse 1 · Chorus · Intro · Outro · Pre-Chorus
- **tempo_key_time**: 4/4 time signature.
- **vocal_chorus**: Production is polished with high-frequency clarity and wide stereo imaging on the vocal harmonies.
- **vocal_main**: Occasional synth pads and filtered vocal samples provide atmospheric texture. · The vocal performance is intimate and breathy, utilizing a mix of chest voice and light falsetto transitions. · intimate male vocals · Male and female vocals alternate and harmonize in a breathy, intimate delivery. · The production is polished with modern compression and slight saturation on the vocals.

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- `rainy` (best vector 0.345) → gap_candidates 등록
- `rainy` (best vector 0.345) → gap_candidates 등록

## (e) 음수필터 경고 (suno_does_not_use — SP에 넣지 말 것)

- 없음