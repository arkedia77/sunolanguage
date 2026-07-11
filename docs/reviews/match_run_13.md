# 매칭 리포트 — run 13 (2026-07-11T11:48:07)

- 입력(track): Head Hunters version with Bill Summers's hindewhu (African pygmy flute) bottle-blowing intro, thick Clavinet and Fender Rhodes electronic-funk texture, and Bennie Maupin's nasal soprano sax over polyrhythmic percussion.. 수박 장수의 흥 — 길거리 블루스의 순수한 펑키함. funky. bouncy. bluesy. street-smart. groovy. playf…
- 코퍼스 버전: 497songs/v3.2 · 채널: M1벡터+M2렉시컬+M3사전 RRF(k=60)
- τ(잠정): vector<0.45 & lexical hit<1 → gap

## (a) 최근접 코퍼스 곡 top-5

| song_id | 제목 | 장르 | RRF합 |
|---|---|---|---:|
| C_1392 | 빨간 점 | K-Pop ballad with acoustic pop elements | 0.6496 |
| C_1725 | 같은 책이었다 | K-Pop power ballad featuring male tenor vocals and a rock-influenced arrangement | 0.3958 |
| C_1034 | 별다줄 | K-Pop ballad with soul and blues influences | 0.3583 |
| C_1456 | 먼지 낀 날개 | K-Indie pop track with a laid-back | 0.2856 |
| C_1522 | 액자 자리 | K-Pop City Pop with elements of Funk and Jazz Fusion | 0.2856 |

## (b) Suno 네이티브 치환표 (외부 표현 → 코퍼스 실존 표현)

| 외부 표현 | → 코퍼스 표현 | slot | 근거곡 |
|---|---|---|---|
| Head Hunters version with Bill Summers's hindewhu (African pygmy flute) bottle-blowing intro | Intro | section | 1745 |
| thick Clavinet and Fender Rhodes electronic-funk texture | A clean electric guitar provides subtle arpeggiated textures in the background. | instrument | 1209 |
| and Bennie Maupin's nasal soprano sax over polyrhythmic percussion | crescendo of polyrhythmic drumming | ? | 74 |
| funky | funky electric guitar enters, upbeat drums | instrument | 62 |
| bouncy | Outro | section | C_1392 |
| bluesy | The arrangement features a clean electric guitar playing bluesy licks and rhythmic chords, a warm electric bass, and a standard drum kit with a crisp snare and prominent hi-hats. | arrangement | C_1034 |
| street-smart | Intro | section | 162 |
| groovy | The bass guitar follows the kick drum with a groovy, staccato feel. | drums | 1160 |
| playful | vocalizing | vocal_main | C_1494 |
| rhythmic | A syncopated hip-hop beat drives the rhythm, consisting of a tight, dry kick drum, a crisp snare with a short reverb tail, and sixteenth-note closed hi-hat patterns. | drums | 150 |
| infectious | Intro | section | C_1392 |
| debut | Intro | section | C_1456 |
| simple-brilliant | Intro | section | C_1522 |
| Piano Iconic funk riff (watermelon man call) | Intro | section | 1573 |
| bluesy comping | acoustic guitar continues rhythmic comping | instrument | S004_04 |
| rhythmic drive Spectral: bright | slap bass, rhythmic electric guitar, bright synth stabs | instrument | C_1480 |
| punchy | slap bass, clean electric guitar, punchy drums | instrument | C_1713 |
| mid-range | A subtle synthesizer pad fills the mid-range. | instrument | C_1481 |
| Temporal: staccato riff | staccato synth riff, slap bass enters | instrument | 31 |
| rhythmic | A syncopated hip-hop beat drives the rhythm, consisting of a tight, dry kick drum, a crisp snare with a short reverb tail, and sixteenth-note closed hi-hat patterns. | drums | 150 |
| Character: funky | Intro | section | 189 |
| street-smart | Intro | section | 162 |
| infectious | Intro | section | C_1392 |
| Trumpet Bright | Bright, staccato brass stabs from a trumpet and saxophone section punctuate the transitions. | instrument | 173 |
| bluesy phrasing | Intro | section | S017_09 |
| powerful high register Spectral: bright | high-register vocals, full band | vocal_main | C_1370 |
| cutting | Bridge | section | C_1729 |
| powerful | Bridge | section | C_1725 |
| Temporal: confident attack | 4/4 time signature. | tempo_key_time | C_1764 |
| Character: energetic | full band, energetic slap bass | arrangement | 1573 |
| joyful | Bridge | section | C_1725 |

## (c) SP 초안 재료 (슬롯별 검증 표현 — SP 1000자 이내 확인 필수)

- **?**: crescendo of polyrhythmic drumming · complex polyrhythmic tom fills · Bright and playful Modern Acoustic Pop with energetic strummed guitar and lively percussion at mid tempo, featuring cheerful ukulele accents and warm piano melodies that create a lighthearted atmosphere of playful togetherness and genuine fun, the production emphasizes organic joy through handclap patterns and whistling hooks that invite participation, incorporating warm bass guitar grooves and occasional glockenspiel that add sparkle to the upbeat arrangement, the track captures the pure delight of playing together as adults through infectious rhythms and feel-good acoustic textures · The drum kit features a prominent double-kick pedal pattern and a bright, cutting snare
- **arrangement**: The production is clean with minimal reverb, emphasizing the intimate, live-band feel. · The arrangement features a clean electric guitar playing bluesy licks and rhythmic chords, a warm electric bass, and a standard drum kit with a crisp snare and prominent hi-hats. · full band, driving rhythm · full band enters, driving rhythm · full band energy, bright synth pads
- **drums**: clean funk electric guitar, synth bass, electronic drums · climax, heavy drums, layered harmonies · funky clean electric guitar, slap bass, tight drums · The bass guitar follows the kick drum with a groovy, staccato feel. · A syncopated hip-hop beat drives the rhythm, consisting of a tight, dry kick drum, a crisp snare with a short reverb tail, and sixteenth-note closed hi-hat patterns.
- **effect_electronic**: clean electric guitar with light overdrive plays melodic bluesy riff · driving overdriven bass line, steady drum beat, clean electric guitar staccato riff
- **genre**: K-Pop Funk-Pop. · K-Pop, City Pop.
- **instrument**: flute motif enters, echoing cello phrases · flute fades out · A clean electric guitar provides subtle arpeggiated textures in the background. · slap bass, funk guitar, electronic drums · clean electric guitar fills
- **section**: Intro · Outro · Bridge · Main Riff
- **tempo_key_time**: 4/4 time signature.
- **vocal_chorus**: falsetto ad-lib · The arrangement features a call-and-response dynamic between the guitar and piano over a steady, syncopated groove.
- **vocal_main**: vocalizing · high-register vocals, full band · vocal chops · climax, powerful vocals · vocal harmony

## (d) 커버리지 gap (코퍼스가 못 받아낸 표현)

- `수박 장수의 흥 — 길거리 블루스의 순수한 펑키함` (best vector 0.295) → gap_candidates 등록

## (e) 음수필터 경고 (suno_does_not_use — SP에 넣지 말 것)

- 없음