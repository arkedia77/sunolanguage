# 매칭 리포트 — run 4 (2026-07-10T17:45:54)

- 입력(track): Single repeating melody passed through the entire orchestra in a crescendo lasting 15+ minutes, beginning with solo snare drum and flute, layering oboe, clarinet, bassoon, brass, and full strings into an overwhelming orchestral tsunami. 최면적 반복 위의 거대한 크레센도 — 끝없이 커지는 파도. hypnotic. building. relentless…
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| S003_06 | Horn Calls and Whispers | ? | 0.5452 |
| S003_07 | Three Mutes of the Trumpet | ? | 0.5310 |
| C_1725 | 같은 책이었다 | K-Pop power ballad featuring male tenor vocals and a rock-influenced arrangement | 0.4790 |
| S018_16 | UpliftingArcs | Trance | 0.4505 |
| S003_05 | Clarinet Chameleon | ? | 0.4365 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| Single repeating melody passed through the entire orchestra in a crescendo lasting 15+ minutes | The arrangement features a gradual crescendo in vocal intensity. | vocal_main | 72 |
| beginning with solo snare drum and flute | flute solo over guitar and bass | instrument | C_1491 |
| layering oboe | The arrangement features a solo oboe and flute playing a playful, staccato melody in 3/4 time. | instrument | S003_05 |
| clarinet | The arrangement features a solo clarinet, acoustic guitar, and upright bass. | arrangement | S003_06 |
| bassoon | bass enters | instrument | C_1455 |
| brass | brass stabs | instrument | C_1481 |
| and full strings into an overwhelming orchestral tsunami | orchestral strings enter, vocal intensity increases | instrument | 222 |
| hypnotic | Intro | section | S018_16 |
| building | Bridge | section | C_1723 |
| relentless | full band, aggressive vocals | vocal_main | C_1722 |
| crescendo | Distorted electric guitars enter during the crescendo with sustained power chords. | arrangement | 189 |
| obsessive | Intro | section | C_1392 |
| triumphant | vocalizing | vocal_main | C_1373 |
| overwhelming | Intro | section | 1756 |
| Snare Drum Continuous bolero rhythm pattern (3+3+2 subdivision) | The arrangement centers on a syncopated boom-bap drum pattern with a crisp snare and a deep, rounded sub-bass. | drums | 1070 |
| pp to mf crescendo over 15 min | The arrangement features a gradual crescendo in vocal intensity. | vocal_main | 72 |
| wire snares on Spectral: dry | clean electric guitar, melodic bass, dry drums | drums | 52 |
| crisp | clean electric guitar loop, punchy kick drum, crisp snare | drums | 1535 |
| Temporal: precise attack | 4/4 time signature. | tempo_key_time | 160 |
| short decay | A digital reverb with a short decay is applied to the vocals and guitar. | instrument | 154 |
| Character: hypnotic | Intro | section | S018_16 |
| mechanical | Bridge | section | C_1710 |
| relentless | full band, aggressive vocals | vocal_main | C_1722 |
| Flute Solo melody A | flute solo over guitar and bass | instrument | C_1491 |
| legato | The bass guitar enters with melodic, legato lines. | instrument | 1651 |
| middle register | high-register vocals, full band | arrangement | C_1370 |
| solo opening Spectral: pure | pure silence | ? | 26 |
| clear | Intro | section | 1756 |
| slightly breathy | breathy male vocals | vocal_main | C_1458 |
| Temporal: soft onset | soft male vocals | vocal_main | 190 |
| Character: intimate | The arrangement is sparse and intimate. | arrangement | 1612 |
| delicate | Bridge | section | C_1714 |
| Clarinet Solo melody B | The arrangement features a solo clarinet, acoustic guitar, and upright bass. | arrangement | S003_06 |
| legato | The bass guitar enters with melodic, legato lines. | instrument | 1651 |
| chalumeau to clarion register Spectral: warm | high-register vocals, full band | arrangement | C_1370 |
| woody | Intro | section | C_1370 |
| round | Bridge | section | C_1727 |
| Temporal: smooth attack | smooth male vocals | vocal_main | C_1524 |
| Character: singing | vocalizing | vocal_main | C_1373 |
| expressive | vocalizing | vocal_main | C_1481 |
| Full Orchestra Layered doubling of melody at octaves | full band, layered vocal harmonies | vocal_chorus | C_10019 |
| massive crescendo | Distorted electric guitars enter during the crescendo with sustained power chords. | arrangement | 189 |
| tutti fff climax Spectral: increasingly bright and full | Outro | section | 10466 |
| Temporal: sustained | sustained guitar feedback | ? | 40 |
| massive | Bridge | section | C_1368 |
| Character: overwhelming | Intro | section | 10472 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **?**: Electro-Pop, hypnotic energetic atmosphere, Korean lyrics with primal attraction theme, energetic vocals with dynamic urgency and power, pulsing synthesizers creating hypnotic groove, driving electronic drums with glitchy character, energetic bass line driving forward with momentum, varied textural elements adding complexity, BPM 124, chorus establishing infectious hook immediately, verse one building energy with vocal expression, chorus reinforcing consistent theme and hook, verse two intensifying emotional expression, chorus with elevation and additional elements, bridge creating variation and contrast, outro fading with synth elements and decay, three minutes plus mandatory, capturing primal attraction through hypnotic electro-pop production · Dynamic hyperpop with obsessive beat repetition and distorted vocal layers. Glitchy production emphasizing tactile, sensory overload through instrumental repetition. Vocal delivery ranges from measured to frenetic, mirroring psychological state. Heavy use of vocal processing and layering creating polyphonic texture. Rhythmic hypnosis through looped elements (button presses, swallowing, breathing sampled as percussion). Pharmacy ambiance mixed with electronic chaos. Energy building through accumulation rather than traditional dynamics. Neurotic, obsessive atmosphere. Clean, balanced production emphasizing instrumental clarity and emotional resonance. Mid-range focus with supportive low-end. Dynamic range allows peaks and valleys. The mix balances vocal presence with atmospheric support, maintaining clarity throughout shifts. · Smooth and intimate Chill R&B with warm Rhodes piano chords and gentle programmed beats at low energy tempo, featuring silky bass lines and atmospheric vocal layers that create a contemplative wedding reception atmosphere of solitary reflection, the production emphasizes space and emotional vulnerability through minimal instrumentation and careful dynamic control, incorporating subtle string arrangements and reverb-processed textures that add depth without overwhelming the intimate core, the track captures the complex emotions of celebrating others happiness while processing personal loneliness through masterful restraint and carefully placed harmonic surprises · snare on beats 2 and 4, steady kick drum pattern · mechanical sound effects
- **absence**: solo cello enters with legato melody
- **arrangement**: Distorted electric guitars enter during the crescendo with sustained power chords. · The structure is characterized by call-and-response between brass and woodwinds, building to a full orchestral crescendo with sustained brass chords and rapid percussion flourishes. · The arrangement features a solo clarinet, acoustic guitar, and upright bass. · The arrangement maintains a minimalist, intimate texture without percussion. · full band, high-energy distorted guitars
- **drums**: triumphant brass fanfare, snare drum rolls, cymbal crashes · The arrangement centers on a syncopated boom-bap drum pattern with a crisp snare and a deep, rounded sub-bass. · The drum kit features a crisp snare on the backbeat and a syncopated kick pattern. · clean electric guitar, melodic bass, dry drums · snare roll
- **effect_sound**: muffled kick drum, crisp snare, eighth-note hi-hats
- **genre**: Orchestral fanfare and march. · Bossa Nova.
- **instrument**: flute solo over guitar and bass · A flute enters for a melodic solo section. · A flute enters to play melodic flourishes and a solo. · The arrangement features a solo oboe and flute playing a playful, staccato melody in 3/4 time. · The structure involves call-and-response between the clarinet and guitar, with the bass maintaining a steady pulse.
- **mixing**: The production is intimate with a close-mic vocal technique and a wide stereo field for the instrumental elements.
- **section**: Intro · Outro · Bridge · Pre-Chorus · Breakdown
- **tempo_key_time**: 4/4 time signature. · A steady, mechanical metronome-like click or woodblock sound provides a rhythmic pulse at 72 BPM in 4/4 time. · Tempo is 72 BPM in 4/4 time. · Tempo is 105 BPM in the key of G Major.
- **unclassified**: Solo Section · Climax · sustained power chords
- **vocal_chorus**: The structure involves call-and-response between the clarinet and guitar, with the bass maintaining a steady pulse. · vocal ad-lib: '전부거든' · vocal harmony · full band, layered vocal harmonies
- **vocal_main**: The arrangement features a gradual crescendo in vocal intensity. · full band, aggressive vocals · vocalizing · falsetto · A deep, processed male voice provides spoken-word cues throughout the arrangement.

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- `최면적 반복 위의 거대한 크레센도 — 끝없이 커지는 파도` (best vector 0.398) → gap_candidates 등록
- `mesmerizing` (best vector 0.368) → gap_candidates 등록
- `ritualistic` (best vector 0.389) → gap_candidates 등록
- `monumental` (best vector 0.308) → gap_candidates 등록
- `tidal` (best vector 0.404) → gap_candidates 등록