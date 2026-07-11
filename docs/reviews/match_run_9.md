# 매칭 리포트 — run 9 (2026-07-11T11:47:29)

- 입력(track): Layered full orchestra with soaring brass fanfares, driving string ostinato, massive timpani and epic percussion hits, choir pads building to a triumphant climax with cinematic risers and sub-bass reinforcement. 용기의 불꽃 — 최후의 전투 직전의 각오. epic. heroic. powerful. cinematic. battle-ready. soaring. triump…
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬+M3사전 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| S004_07 | Trompeta Caliente | ? | 0.5540 |
| C_1725 | 같은 책이었다 | K-Pop power ballad featuring male tenor vocals and a rock-influenced arrangement | 0.5146 |
| C_1368 | 자동문이 열릴 때마다 | K-Pop ballad featuring a tenor male vocal | 0.5106 |
| C_1369 | 세 시간째 빨간 불 | K-Pop ballad | 0.3775 |
| C_1481 | 창문이 처음이야 | K-Pop | 0.3328 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| Layered full orchestra with soaring brass fanfares | full band, driving drums, soaring strings | arrangement | C_1328 |
| driving string ostinato | staccato string ostinato enters | ? | 30 |
| massive timpani and epic percussion hits | brass hits, driving percussion | instrument | C_1480 |
| choir pads building to a triumphant climax with cinematic risers and sub-bass reinforcement | choir sustained pads | instrument | S004_07 |
| epic | Intro | section | C_1477 |
| heroic | Chorus | section | C_10018 |
| powerful | Bridge | section | C_1725 |
| cinematic | Cinematic orchestral score. | genre | 10464 |
| battle-ready | Pre-Chorus | section | C_1271 |
| soaring | full band, driving drums, soaring strings | instrument | C_1368 |
| triumphant | vocalizing | vocal_main | C_1373 |
| courageous | Intro | section | C_1369 |
| massive | Bridge | section | C_1368 |
| Brass Section Heroic fanfares | brass stabs | instrument | C_1481 |
| power sustain | A warm synth pad provides harmonic sustain. | instrument | 20003 |
| unison melody at climax Spectral: brilliant | Climax | unclassified | S004_01 |
| massive | Bridge | section | C_1368 |
| cutting | Bridge | section | C_1729 |
| Temporal: broad attack | 4/4 time signature. | tempo_key_time | 160 |
| sustained fff | sustained guitar feedback | instrument | 10469 |
| Character: heroic | Verse 1 | section | 208 |
| triumphant | vocalizing | vocal_main | C_1373 |
| Epic Choir Latin-esque syllables | Choral vocalizations consist of operatic staccato chants and sustained pads. | vocal_chorus | S004_07 |
| sustained power chords | distorted electric guitar power chords | effect_electronic | 189 |
| building from pp to fff Spectral: massive | Key of G Major. | tempo_key_time | 1662 |
| full harmonic spectrum | full band, layered vocal harmonies | arrangement | C_10019 |
| Temporal: sustained | sustained guitar feedback | ? | 40 |
| swelling | full band enters, strings swell, belted vocals | arrangement | C_1505 |
| Character: divine | Verse 3 | section | C_1764 |
| overwhelming | Intro | section | 1756 |
| Taiko/Percussion Massive hits | brass hits, driving percussion | instrument | C_1480 |
| accelerating patterns | Slap bass performs syncopated sixteenth-note patterns. | instrument | 196 |
| sub-bass impacts Spectral: deep sub-bass | sub-bass enters | instrument | 182 |
| physical impact | full band, high-energy distorted guitars, crash cymbals | arrangement | 1759 |
| Temporal: explosive transient | A steady, mechanical metronome-like click or woodblock sound provides a rhythmic pulse at 72 BPM in 4/4 time. | effect_sound | 1671 |
| Character: war drums | bass and drums enter | drums | 1556 |
| primal | Intro | section | 1111 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **?**: staccato string ostinato enters · Epic cinematic trailer music built around a french horn ensemble. Eight french horns in unison perform a heroic, ascending theme over thundering taiko drum hits. Timpani provides a militaristic rhythmic ostinato. A deep synthesizer bass drone creates tension beneath the horns. A wordless choir joins during the climax with sustained vowel sounds. The piece follows trailer music structure: quiet atmospheric opening, rising tension, a false climax, silence, then the final massive impact. The horn melody is simple and anthem-like, designed for maximum emotional impact. 90 BPM. 4/4 time. Massive reverb with cinematic compression. · High-energy EDM Future Bass with powerful synthesizer drops and pulsing sidechain bass at 160 BPM. Driving four-on-the-floor kick drum with crisp hi-hats and snappy claps. Bright supersaw lead synths layered with vocal chops and pitched vocal samples. Build-ups with rising white noise sweeps into massive drops with heavy sub-bass. Energetic male vocals with anthemic delivery, singing in Korean. Festival-ready production with wide stereo imaging, heavy compression, and stadium-filling reverb tails. Perfect workout and running motivation track. Fully mixed and mastered. · Pop Punk, School Pop Punk in C Major. 142 BPM. Mid-high energy with push beat and youthful urgency building to drum solo bridge explosion. Bright vocals excited nervous, chest voice youthful bright, breathless on crush moments, mixed voice on final chorus with courageous lift. Electric guitar bright distorted power pop, second guitar clean arpeggios verse power chords chorus, live drum kit energetic pop punk with extended drum solo on bridge, electric bass pick bright punchy driving. Auditorium empty room reverb on drum solo, school bell processed on intro. Bright major punk progressions with innocent energy. A high schooler sneaking into rehearsal to watch their crush play a drum solo — heartbeat racing the kick drum. Auditorium natural reverb, guitar amp close mic, youthful raw energy. Korean lyrics throughout. · The drum kit features a prominent double-kick pedal pattern and a bright, cutting snare
- **arrangement**: full band, driving drums, soaring strings · The structure is characterized by call-and-response between brass and woodwinds, building to a full orchestral crescendo with sustained brass chords and rapid percussion flourishes. · The production is minimalist, focusing on the clarity of the vocal and the resonance of the acoustic strings. · The production is clean with minimal reverb, emphasizing the intimate, live-band feel. · full arrangement
- **drums**: full orchestra, heavy brass, thunderous percussion · Orchestral percussion includes timpani rolls and concert bass drum hits. · Orchestral percussion includes timpani rolls, snare drum rolls, and crash cymbals. · triumphant brass fanfare, snare drum rolls, cymbal crashes · A cinematic percussion ensemble includes taiko drums, orchestral snares, and metallic hits.
- **effect_electronic**: distorted electric guitar power chords · Distorted electric guitars provide power chords during the chorus.
- **effect_sound**: A steady, mechanical metronome-like click or woodblock sound provides a rhythmic pulse at 72 BPM in 4/4 time.
- **genre**: Cinematic orchestral score.
- **instrument**: The arrangement features staccato violin and viola patterns playing rhythmic ostinatos in 4/4 time. · Orchestral strings play staccato rhythmic patterns alongside a driving rock drum kit and a prominent electric bass. · brass hits, driving percussion · choir sustained pads · The arrangement builds from a sparse guitar-driven intro to a full band climax with layered vocal harmonies.
- **section**: Intro · Chorus · Bridge · Outro · Pre-Chorus
- **tempo_key_time**: 4/4 time signature. · Key of E Major. · Key of G Major. · The harmonic structure follows a diatonic progression in the key of C Major. · Tempo is 72 BPM in 4/4 time.
- **unclassified**: Climax · sustained power chords
- **vocal_chorus**: full ensemble unison melody · Choral vocalizations consist of operatic staccato chants and sustained pads. · The arrangement transitions from a sparse, rhythmic verse to a dense, wall-of-sound chorus with layered vocal harmonies. · operatic choir chants · vocal harmony
- **vocal_main**: vocalizing · falsetto · climax, powerful vocals · The arrangement builds from a sparse guitar-driven intro to a full band climax with layered vocal harmonies. · vocal chops

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- `용기의 불꽃 — 최후의 전투 직전의 각오` (best vector 0.368) → gap_candidates 등록
- `adrenaline` (best vector 0.354) → gap_candidates 등록

## (e) 음수필터 경고 (suno_does_not_use — SP에 넣지 말 것)

- ⚠️ `fff` → 다이나믹 마킹(p/mf/ff…) — Suno 0회