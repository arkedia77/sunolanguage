# 매칭 리포트 — run 15 (2026-07-11T11:48:25)

- 입력(track): Screaming Ibanez electric guitar with whammy bar divebombs and legato technique, saturated high-gain distortion, tight rhythm section with synth pads creating sci-fi rock atmosphere. 외계인과 서핑 — 기타 한 대로 은하계를 여행하는 스릴. virtuosic. surfing. alien. energetic. shredding. bright. fun. sci-fi. guitar-hero. ex…
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬+M3사전 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| C_1720 | 인데요, | K-Pop City Pop with elements of Funk and Jazz Fusion | 0.5384 |
| 10464 | Horizon Step | Cinematic | 0.3917 |
| 10469 | Crack of Light | Cinematic | 0.3543 |
| 1433 | 거울 속 아버지 | Neo-Soul | 0.3148 |
| C_1393 | 쿨한 척 삼 분 | K-Pop ballad with acoustic folk influences | 0.2856 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| Screaming Ibanez electric guitar with whammy bar divebombs and legato technique | Distorted electric guitars play palm-muted chugging riffs and power chords. | effect_electronic | 10469 |
| saturated high-gain distortion | lead electric guitar enters with high-gain distortion | effect_electronic | 10469 |
| tight rhythm section with synth pads creating sci-fi rock atmosphere | clean funk electric guitar, slap bass, tight drum kit, bright synth pads | instrument | 1675 |
| virtuosic | The vocal delivery is intimate and breathy, utilizing a narrow dynamic range and subtle vibrato. | vocal_main | 944 |
| surfing | Bridge | section | C_1721 |
| energetic | full band, energetic slap bass | arrangement | 1573 |
| shredding | vocalizing | vocal_main | C_1373 |
| bright | full band energy, bright synth pads | instrument | C_1511 |
| fun | Bridge | section | C_1393 |
| guitar-hero | palm-muted guitar | instrument | 126 |
| Electric Guitar Legato runs | The bass guitar enters with melodic, legato lines. | instrument | 1651 |
| whammy bar dives | Bridge | section | C_1764 |
| tapping | Bridge | section | C_1732 |
| harmonics | During the chorus, distorted electric guitar power chords provide harmonic density. | instrument | C_1712 |
| sustained singing lead Spectral: bright | The vocal performance is intimate and breathy, utilizing a close-mic technique with light plate reverb. | arrangement | 122 |
| singing | Chorus | section | 1759 |
| sustained | Instrumental | section | S003_06 |
| Temporal: fluid legato | The bass guitar enters with melodic, legato lines. | instrument | 1651 |
| rapid | Pre-Chorus | section | C_1725 |
| Character: virtuosic | A soft, breathy female vocal performs a melodic line with gentle vibrato and intimate proximity. | mixing | 1662 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **?**: Funk Pop, Retro Dance, BPM 118, Male Vocal, Groovy bass, Bright synth, Fun and energetic, Verse → Chorus → Verse → Chorus → Bridge → Final Chorus · Bright and playful Modern Acoustic Pop with energetic strummed guitar and lively percussion at mid tempo, featuring cheerful ukulele accents and warm piano melodies that create a lighthearted atmosphere of playful togetherness and genuine fun, the production emphasizes organic joy through handclap patterns and whistling hooks that invite participation, incorporating warm bass guitar grooves and occasional glockenspiel that add sparkle to the upbeat arrangement, the track captures the pure delight of playing together as adults through infectious rhythms and feel-good acoustic textures · repetitive two-bar melodic hook · single snare hits, rhythmic tapping on drum rims
- **arrangement**: The vocal delivery is intimate and close-mic'd, utilizing subtle vibrato on sustained notes. · full band, energetic slap bass · full band, layered group vocals, energetic brass riff · full band, bright guitar chords · full band, energetic
- **drums**: fast slap bass, driving drum beat, distorted surf guitar riff · light hi-hat taps · rapid hi-hat rolls · feedback swell, rapid drum fill
- **effect_electronic**: Distorted electric guitars play palm-muted chugging riffs and power chords. · lead electric guitar enters with high-gain distortion · full band, high-energy distorted guitars, crash cymbals · A high-energy female vocal lead features a clear, polished tone with light reverb.
- **instrument**: Distorted electric guitar enters with sustained power chords and feedback swells. · Distorted electric guitars play palm-muted power chords and syncopated rhythmic riffs. · A distorted 808 bassline follows the root notes with heavy saturation. · clean funk electric guitar, slap bass, tight drum kit, bright synth pads · Atmospheric synth pads provide harmonic texture in the background.
- **mixing**: A soft, breathy female vocal performs a melodic line with gentle vibrato and intimate proximity.
- **section**: Intro · Bridge · Outro · Chorus · Instrumental
- **tempo_key_time**: Key of G Major. · Key of G Major, 95 BPM.
- **unclassified**: sustained power chords
- **vocal_chorus**: full band energy, vocal ad-libs
- **vocal_main**: The vocal delivery is intimate and breathy, utilizing a narrow dynamic range and subtle vibrato. · vocalizing · melodic singing, guitar arpeggios

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- `외계인과 서핑 — 기타 한 대로 은하계를 여행하는 스릴` (best vector 0.430) → gap_candidates 등록
- `alien` (best vector 0.341) → gap_candidates 등록
- `sci-fi` (best vector 0.433) → gap_candidates 등록
- `exhilarating` (best vector 0.381) → gap_candidates 등록
- `sci-fi` (best vector 0.433) → gap_candidates 등록
- `exhilarating` (best vector 0.381) → gap_candidates 등록

## (e) 음수필터 경고 (suno_does_not_use — SP에 넣지 말 것)

- 없음