# 4장: 장르별 슬롯 매트릭스

> 58개 장르 × 13개 슬롯 히트맵. 장르마다 어떤 슬롯을 채우고, 어떤 어휘를 선호하는지.

> ★**관측층·단위 한정자**(2026-08-17): 이 장의 수치는 **출력층**(Suno가 완성곡을 듣고 쓴 서술) 관측이고, **입력층은 미인덱스**다 → [2장 §2.0](ch2_two_channels.md). ★**히트맵 단위 주의** — `곡수` 열만 **곡**이고, 슬롯 열(GNR/INS/…)은 **곡당 평균 출현 수**(소수점)다. 셀 값을 곡 수로 인용하면 틀린다. 본문의 **437곡 기준은 구판 스냅샷**이며 현행은 **파일 코퍼스 530곡 / lexical 589트랙 / 283장르**다.

## 4.1 히트맵 요약

| 장르 | 곡수 | GNR | INS | DRM | VOC | CHR | ARR | MIX | EFX | SFX | TMP | HAR | ABS | MST | 채움 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Indie Pop | 21 | 1.0 | 9.2 | 1.5 | 3.3 | .4 | 1.3 | .4 | 1.0 | · | 1.4 | .2 | · | · | 12/13 |
| City Pop | 20 | 1.0 | 10.1 | 1.4 | 3.1 | .5 | 1.6 | .2 | 1.1 | · | 1.2 | .1 | .1 | · | 11/13 |
| TROT | 12 | .9 | 11.6 | 2.8 | 3.2 | .3 | 1.3 | .3 | 1.5 | · | 1.2 | · | .1 | · | 10/13 |
| Acoustic Pop | 12 | 1.0 | 10.2 | 1.3 | 3.1 | .2 | 1.4 | .5 | 1.2 | · | 1.6 | .2 | · | · | 10/13 |
| Dream Pop | 10 | 1.1 | 11.1 | 2.7 | 3.4 | .5 | 1.1 | .3 | .9 | .4 | 1.5 | .1 | · | · | 11/13 |
| Korean Ballad | 12 | 1.0 | 8.3 | 2.0 | 3.1 | .2 | 1.4 | .5 | .7 | .1 | 1.2 | · | · | · | 10/13 |
| (미정) | 10 | 1.0 | 10.4 | 2.2 | 2.7 | .2 | 1.6 | .2 | 1.0 | · | 1.5 | .1 | .2 | · | 11/13 |
| Hip-Hop | 9 | 1.0 | 9.0 | 3.1 | 3.6 | .3 | 1.7 | .3 | 1.8 | .1 | 1.0 | .1 | .1 | · | 12/13 |
| R&B | 10 | 1.0 | 8.5 | 1.8 | 3.5 | .1 | 1.4 | .5 | 1.4 | · | 1.1 | .1 | .1 | · | 11/13 |
| Synth Pop | 9 | 1.1 | 10.3 | 3.3 | 2.9 | .1 | .9 | .2 | .9 | · | 1.6 | .1 | · | · | 10/13 |
| K-POP | 8 | 1.0 | 11.8 | 3.0 | 2.9 | .6 | 1.5 | .4 | .9 | .2 | 1.2 | · | .1 | · | 11/13 |
| Acoustic Ballad | 8 | 1.1 | 11.0 | 2.0 | 3.2 | .6 | 1.2 | .6 | 1.4 | · | 1.2 | .1 | · | · | 10/13 |
| Neo-Soul | 7 | .9 | 11.1 | 2.9 | 4.3 | 1.0 | 1.4 | .3 | 1.4 | · | 1.9 | .4 | .1 | · | 11/13 |
| Funk Pop | 8 | 1.0 | 11.2 | 1.8 | 2.9 | .5 | 1.5 | .2 | .6 | · | 1.5 | .1 | · | · | 10/13 |
| Folk | 8 | 1.0 | 9.6 | 2.5 | 3.4 | .4 | 1.5 | .4 | .9 | · | 1.2 | .2 | · | · | 10/13 |
| Disco Pop | 7 | 1.0 | 13.0 | 2.4 | 2.7 | .9 | 1.6 | .1 | .7 | · | 1.1 | · | .1 | · | 10/13 |
| Bossa Nova | 8 | 1.0 | 9.2 | 1.8 | 2.4 | .1 | 1.0 | · | .8 | · | 1.5 | .1 | · | · | 9/13 |
| Electro Pop | 6 | 1.0 | 10.5 | 2.8 | 3.0 | .5 | 1.8 | .7 | 1.2 | .2 | 1.2 | · | .3 | · | 11/13 |
| Piano Ballad | 7 | 1.0 | 10.1 | 1.1 | 3.4 | · | 1.0 | .1 | .7 | · | 1.7 | · | .1 | · | 9/13 |
| Art Pop | 6 | 1.0 | 8.8 | 2.0 | 3.5 | .2 | 2.5 | .5 | 1.8 | · | 1.3 | .2 | .2 | · | 11/13 |
| Lo-fi Pop | 7 | 1.0 | 8.9 | 1.0 | 2.7 | .1 | 1.7 | .3 | .9 | · | 1.3 | · | .1 | · | 10/13 |
| Indie Folk | 7 | 1.0 | 7.4 | 1.1 | 2.9 | · | 1.7 | .3 | 1.0 | .6 | 1.3 | · | .1 | · | 10/13 |
| Jazz Pop | 5 | 1.0 | 10.6 | 1.8 | 2.6 | · | 1.6 | .2 | 1.0 | · | 1.0 | · | · | · | 8/13 |
| Rock | 4 | 1.0 | 13.8 | 3.0 | 2.5 | .5 | 1.0 | .2 | 1.2 | · | 1.5 | · | · | · | 9/13 |
| Indie Rock | 4 | 1.0 | 9.5 | 4.5 | 2.0 | 1.0 | 1.0 | .5 | 2.5 | · | 1.5 | · | .2 | · | 10/13 |
| Jazz Ballad | 5 | 1.0 | 9.6 | 1.6 | 2.4 | · | 1.0 | .8 | .4 | · | 1.8 | · | · | · | 8/13 |
| Acoustic Folk | 4 | 1.0 | 10.2 | 1.8 | 3.0 | · | 1.5 | .5 | 1.5 | .5 | 1.8 | · | · | .2 | 10/13 |
| Electronic | 4 | 1.0 | 5.8 | 3.5 | 3.0 | 1.0 | 1.0 | .5 | 1.0 | .8 | 2.2 | 1.0 | · | · | 11/13 |
| Ambient | 4 | 1.0 | 9.5 | 2.5 | 3.5 | · | 1.5 | .2 | .8 | · | 1.0 | .2 | · | · | 9/13 |
| Indie Acoustic | 4 | 1.0 | 8.2 | 1.0 | 3.8 | .5 | 1.5 | .2 | 1.0 | .2 | 1.5 | · | · | · | 10/13 |

## 4.2 장르별 상세

### Indie Pop (21곡)

- **genre** [22회, 곡당 1.0]: `K-Pop ballad featuring a baritone male vocal`(3), `K-Pop ballad with R&B influences`(3), `K-Indie folk ballad`(2)
- **instrument** [194회, 곡당 9.2]: `electric bass`(32), `electric guitar`(27), `clean electric guitar`(21)
- **drums** [31회, 곡당 1.5]: `kick drum, drums`(7), `kick drum, snare drum, drums`(7), `beat, drums`(3)
- **vocal_main** [70회, 곡당 3.3]: `vocals`(19), `male vocals`(18), `male baritone vocals, male vocals`(7)
- **vocal_chorus** [9회, 곡당 0.4]: `doubling`(4), `layered vocal, harmonies`(3), `harmonies, call-and-response, adlibs`(1)
- **arrangement** [28회, 곡당 1.3]: `arrangement`(10), `intimate`(5), `lush`(2)
- **mixing** [8회, 곡당 0.4]: `sits forward, in the mix`(1), `compression, eq`(1), `panned`(1)
- **effect_electronic** [22회, 곡당 1.0]: `plate reverb`(5), `reverb`(5), `light chorus, reverb`(3)
- **effect_sound** [1회, 곡당 0.0]: `muffled`(1)
- **tempo_key_time** [29회, 곡당 1.4]: `{'bpm': None, 'key': 'e major', 'time_signature': None}`(4), `{'bpm': 72, 'key': None, 'time_signature': '4/4'}`(3), `{'bpm': 105, 'key': None, 'time_signature': None}`(3)
- **harmony** [4회, 곡당 0.2]: `cadence`(2), `harmonic progression`(1), `chord progression`(1)
- **absence** [1회, 곡당 0.0]: `stripped`(1)

### City Pop (20곡)

- **genre** [20회, 곡당 1.0]: `K-Pop R&B ballad`(2), `K-Pop ballad featuring a male baritone vocal`(2), `K-Indie Pop`(2)
- **instrument** [201회, 곡당 10.1]: `electric bass`(44), `electric guitar`(31), `clean electric guitar`(24)
- **drums** [29회, 곡당 1.4]: `kick drum, drums`(3), `snare drum, hi-hat, drums`(3), `snare drum`(3)
- **vocal_main** [63회, 곡당 3.1]: `vocals`(20), `male vocals`(14), `male tenor vocals`(7)
- **vocal_chorus** [9회, 곡당 0.5]: `doubling`(4), `vocal harmonies`(2), `ad-lib`(2)
- **arrangement** [31회, 곡당 1.6]: `arrangement`(9), `intimate`(8), `arrangement, sparse, focusing on, interplay`(6)
- **mixing** [5회, 곡당 0.2]: `forward in the mix`(2), `compression`(1), `high-fidelity`(1)
- **effect_electronic** [21회, 곡당 1.1]: `light chorus, reverb`(5), `reverb`(5), `plate reverb`(3)
- **tempo_key_time** [25회, 곡당 1.2]: `{'bpm': 72, 'key': None, 'time_signature': '4/4'}`(2), `{'bpm': None, 'key': None, 'time_signature': None}`(2), `{'bpm': 92, 'key': 'e major', 'time_signature': None}`(2)
- **harmony** [2회, 곡당 0.1]: `chord progression`(2)
- **absence** [2회, 곡당 0.1]: `solo cello`(1), `fade out`(1)

### TROT (12곡)

- **genre** [11회, 곡당 0.9]: `K-Pop ballad featuring a baritone male vocal`(3), `K-Pop ballad`(2), `K-Pop with City Pop influences`(1)
- **instrument** [139회, 곡당 11.6]: `electric bass`(27), `electric guitar`(23), `clean electric guitar`(13)
- **drums** [34회, 곡당 2.8]: `drums`(6), `kick drum, snare drum, drum kit, drums`(4), `beat, drums`(4)
- **vocal_main** [38회, 곡당 3.2]: `vocals`(12), `male baritone vocals, male vocals`(9), `female vocals, male vocals`(5)
- **vocal_chorus** [4회, 곡당 0.3]: `call-and-response, unison`(1), `unison`(1), `ad-libs`(1)
- **arrangement** [16회, 곡당 1.3]: `arrangement`(8), `intimate`(2), `arrangement, sparse, focusing on, interplay`(1)
- **mixing** [4회, 곡당 0.3]: `high-fidelity`(1), `stereo image, mono`(1), `polished production`(1)
- **effect_electronic** [18회, 곡당 1.5]: `distorted`(4), `reverb`(3), `light chorus, reverb`(3)
- **tempo_key_time** [14회, 곡당 1.2]: `{'bpm': 72, 'key': 'g major', 'time_signature': '4/4'}`(2), `{'bpm': 128, 'key': 'e major', 'time_signature': None}`(2), `{'bpm': 118, 'key': 'g major', 'time_signature': None}`(1)
- **absence** [1회, 곡당 0.1]: `drop out`(1)

### Acoustic Pop (12곡)

- **genre** [12회, 곡당 1.0]: `K-Pop ballad featuring a male tenor vocal`(2), `K-Indie Pop`(1), `K-Indie folk ballad`(1)
- **instrument** [123회, 곡당 10.2]: `electric bass`(18), `synthesizer`(16), `clean electric guitar`(11)
- **drums** [16회, 곡당 1.3]: `kick drum, snare drum, drums`(6), `kick drum, drums`(3), `snare drum, hi-hat, drums`(1)
- **vocal_main** [37회, 곡당 3.1]: `vocals`(10), `male vocals`(6), `male tenor vocals`(5)
- **vocal_chorus** [3회, 곡당 0.2]: `doubling`(2), `harmonies`(1)
- **arrangement** [17회, 곡당 1.4]: `arrangement`(8), `intimate`(3), `arrangement, sparse, focusing on, interplay`(3)
- **mixing** [6회, 곡당 0.5]: `processed`(3), `high-fidelity`(1), `sidechain, compression`(1)
- **effect_electronic** [14회, 곡당 1.2]: `reverb`(4), `hall reverb`(2), `room reverb`(2)
- **tempo_key_time** [19회, 곡당 1.6]: `{'bpm': 72, 'key': None, 'time_signature': '4/4'}`(3), `{'bpm': None, 'key': None, 'time_signature': None}`(2), `{'bpm': None, 'key': 'g major', 'time_signature': None}`(2)
- **harmony** [2회, 곡당 0.2]: `chord progression`(2)

### Dream Pop (10곡)

- **genre** [11회, 곡당 1.1]: `K-Pop ballad`(2), `K-Pop Hip-Hop track at 90 BPM in the key of G Minor`(1), `K-Hip Hop track featuring a male rapper with a laid-back, rhythmic flow`(1)
- **instrument** [111회, 곡당 11.1]: `electric guitar`(18), `electric bass`(18), `clean electric guitar`(14)
- **drums** [27회, 곡당 2.7]: `kick drum, drums`(4), `snare drum`(3), `drums`(3)
- **vocal_main** [34회, 곡당 3.4]: `vocals`(12), `female vocals, male vocals`(8), `male vocals`(6)
- **vocal_chorus** [5회, 곡당 0.5]: `doubling`(3), `ad-libs, harmonies`(1), `ad-libs`(1)
- **arrangement** [11회, 곡당 1.1]: `arrangement, sparse, focusing on, interplay`(3), `arrangement`(3), `intimate`(2)
- **mixing** [3회, 곡당 0.3]: `compression`(1), `close-mic`(1), `close-mic, proximity`(1)
- **effect_electronic** [9회, 곡당 0.9]: `room reverb`(2), `pitch correction, delay`(1), `light chorus, reverb`(1)
- **effect_sound** [4회, 곡당 0.4]: `vinyl crackle`(4)
- **tempo_key_time** [15회, 곡당 1.5]: `{'bpm': 72, 'key': None, 'time_signature': None}`(2), `{'bpm': None, 'key': None, 'time_signature': '4/4'}`(2), `{'bpm': None, 'key': 'e major', 'time_signature': None}`(1)
- **harmony** [1회, 곡당 0.1]: `minor seventh`(1)

### Korean Ballad (12곡)

- **genre** [12회, 곡당 1.0]: `K-Pop ballad with acoustic pop elements`(1), `K-Pop educational pop track`(1), `K-Pop Hip-Hop track featuring a blend of soulful R&B vocal hooks and rhythmic rap verses`(1)
- **instrument** [100회, 곡당 8.3]: `electric bass`(21), `electric guitar`(14), `acoustic guitar`(11)
- **drums** [24회, 곡당 2.0]: `kick drum, snare drum, drums`(3), `kick drum, drums`(3), `drums`(3)
- **vocal_main** [37회, 곡당 3.1]: `vocals`(11), `male vocals`(8), `rap delivery, vocals`(2)
- **vocal_chorus** [2회, 곡당 0.2]: `doubling`(1), `double-tracking`(1)
- **arrangement** [17회, 곡당 1.4]: `arrangement`(7), `intimate`(4), `lush`(1)
- **mixing** [6회, 곡당 0.5]: `processed`(1), `in the mix`(1), `stereo image`(1)
- **effect_electronic** [8회, 곡당 0.7]: `plate reverb`(3), `pitch correction`(1), `light chorus, delay`(1)
- **effect_sound** [1회, 곡당 0.1]: `vinyl crackle`(1)
- **tempo_key_time** [14회, 곡당 1.2]: `{'bpm': 72, 'key': 'e major', 'time_signature': '4/4'}`(2), `{'bpm': 84, 'key': 'e major', 'time_signature': '4/4'}`(1), `{'bpm': 128, 'key': 'c major', 'time_signature': None}`(1)

### (미정) (10곡)

- **genre** [10회, 곡당 1.0]: `K-Pop ballad`(1), `K-Pop R&B ballad`(1), `K-Pop Hip-Hop track featuring a male rapper and melodic vocalist`(1)
- **instrument** [104회, 곡당 10.4]: `electric guitar`(22), `clean electric guitar`(18), `electric bass`(18)
- **drums** [22회, 곡당 2.2]: `drums`(5), `percussion`(3), `kick drum, snare drum, drums`(3)
- **vocal_main** [27회, 곡당 2.7]: `male vocals`(6), `vocals`(6), `female vocals, male vocals`(6)
- **vocal_chorus** [2회, 곡당 0.2]: `doubling`(2)
- **arrangement** [16회, 곡당 1.6]: `arrangement`(5), `intimate`(4), `sparse`(1)
- **mixing** [2회, 곡당 0.2]: `compression`(1), `stereo image`(1)
- **effect_electronic** [10회, 곡당 1.0]: `light chorus`(2), `reverb`(2), `distorted`(2)
- **tempo_key_time** [15회, 곡당 1.5]: `{'bpm': None, 'key': 'g major', 'time_signature': None}`(2), `{'bpm': None, 'key': 'c major', 'time_signature': None}`(1), `{'bpm': 72, 'key': None, 'time_signature': None}`(1)
- **harmony** [1회, 곡당 0.1]: `chord progression`(1)
- **absence** [2회, 곡당 0.2]: `without percussion`(1), `no percussion`(1)

### Hip-Hop (9곡)

- **genre** [9회, 곡당 1.0]: `K-Pop R&B ballad`(1), `K-Indie Pop`(1), `K-Pop and J-Rock fusion with elements of Funk Rock`(1)
- **instrument** [81회, 곡당 9.0]: `electric guitar`(17), `electric bass`(17), `clean electric guitar`(8)
- **drums** [28회, 곡당 3.1]: `kick drum, drums`(4), `drums`(4), `kick drum, shaker, beat, drums`(2)
- **vocal_main** [32회, 곡당 3.6]: `vocals`(17), `female vocals, male vocals`(4), `rap delivery, vocals`(3)
- **vocal_chorus** [3회, 곡당 0.3]: `doubling`(1), `vocal harmony`(1), `ad-lib`(1)
- **arrangement** [15회, 곡당 1.7]: `arrangement`(6), `intimate`(3), `arrangement, sparse`(1)
- **mixing** [3회, 곡당 0.3]: `compression`(2), `proximity`(1)
- **effect_electronic** [16회, 곡당 1.8]: `distorted`(5), `overdriven`(4), `with chorus`(2)
- **effect_sound** [1회, 곡당 0.1]: `record scratch`(1)
- **tempo_key_time** [9회, 곡당 1.0]: `{'bpm': 85, 'key': 'e major', 'time_signature': None}`(1), `{'bpm': 88, 'key': 'e major', 'time_signature': None}`(1), `{'bpm': 124, 'key': 'e major', 'time_signature': None}`(1)
- **harmony** [1회, 곡당 0.1]: `chord progression`(1)
- **absence** [1회, 곡당 0.1]: `drops out`(1)

### R&B (10곡)

- **genre** [10회, 곡당 1.0]: `K-Indie folk ballad`(2), `K-Pop ballad featuring a male tenor vocalist`(1), `K-Pop ballad featuring a baritone male vocal`(1)
- **instrument** [85회, 곡당 8.5]: `electric bass`(18), `electric guitar`(10), `clean electric guitar`(9)
- **drums** [18회, 곡당 1.8]: `kick drum, drums`(5), `beat, drums`(2), `snare drum, crash cymbal, drums`(1)
- **vocal_main** [35회, 곡당 3.5]: `vocals`(12), `male vocals`(7), `female vocals, male vocals`(6)
- **vocal_chorus** [1회, 곡당 0.1]: `doubling`(1)
- **arrangement** [14회, 곡당 1.4]: `arrangement`(4), `intimate`(2), `arrangement, sparse, focusing on, interplay`(2)
- **mixing** [5회, 곡당 0.5]: `close-mic`(1), `processed, compression`(1), `processed`(1)
- **effect_electronic** [14회, 곡당 1.4]: `reverb`(4), `hall reverb`(2), `overdriven`(2)
- **tempo_key_time** [11회, 곡당 1.1]: `{'bpm': 72, 'key': 'g major', 'time_signature': '4/4'}`(2), `{'bpm': 72, 'key': 'e major', 'time_signature': None}`(1), `{'bpm': 72, 'key': None, 'time_signature': '4/4'}`(1)
- **harmony** [1회, 곡당 0.1]: `harmonic movement`(1)
- **absence** [1회, 곡당 0.1]: `no percussion`(1)

### Synth Pop (9곡)

- **genre** [10회, 곡당 1.1]: `K-Pop Hip-Hop with a laid-back jazz-rap influence`(1), `K-Pop Indie Pop`(1), `K-Pop acoustic ballad`(1)
- **instrument** [93회, 곡당 10.3]: `electric bass`(20), `electric guitar`(17), `clean electric guitar`(11)
- **drums** [30회, 곡당 3.3]: `kick drum, drums`(6), `kick drum, snare drum, drums`(4), `shaker`(3)
- **vocal_main** [26회, 곡당 2.9]: `male vocals`(9), `vocals`(5), `male vocals, singing`(2)
- **vocal_chorus** [1회, 곡당 0.1]: `doubling`(1)
- **arrangement** [8회, 곡당 0.9]: `arrangement`(3), `intimate`(2), `arrangement, sparse, focusing on`(1)
- **mixing** [2회, 곡당 0.2]: `processed, compression`(1), `close-mic, proximity`(1)
- **effect_electronic** [8회, 곡당 0.9]: `reverb`(3), `light chorus, reverb`(2), `chorus effect`(1)
- **tempo_key_time** [14회, 곡당 1.6]: `{'bpm': None, 'key': None, 'time_signature': None}`(2), `{'bpm': 92, 'key': 'g major', 'time_signature': None}`(1), `{'bpm': 105, 'key': 'e major', 'time_signature': '4/4'}`(1)
- **harmony** [1회, 곡당 0.1]: `chord progression`(1)


## 4.3 구조적 공백 (120건)

다음 장르×슬롯 조합은 3곡 이상 존재하지만 해당 슬롯 entity가 0건:

- **Indie Pop** × mastering (21곡)
- **City Pop** × effect_sound (20곡)
- **City Pop** × mastering (20곡)
- **TROT** × effect_sound (12곡)
- **TROT** × harmony (12곡)
- **TROT** × mastering (12곡)
- **Acoustic Pop** × effect_sound (12곡)
- **Acoustic Pop** × absence (12곡)
- **Acoustic Pop** × mastering (12곡)
- **Dream Pop** × absence (10곡)
- **Dream Pop** × mastering (10곡)
- **Korean Ballad** × harmony (12곡)
- **Korean Ballad** × absence (12곡)
- **Korean Ballad** × mastering (12곡)
- **(미정)** × effect_sound (10곡)
- **(미정)** × mastering (10곡)
- **Hip-Hop** × mastering (9곡)
- **R&B** × effect_sound (10곡)
- **R&B** × mastering (10곡)
- **Synth Pop** × effect_sound (9곡)
- **Synth Pop** × absence (9곡)
- **Synth Pop** × mastering (9곡)
- **K-POP** × harmony (8곡)
- **K-POP** × mastering (8곡)
- **Acoustic Ballad** × effect_sound (8곡)
- **Acoustic Ballad** × absence (8곡)
- **Acoustic Ballad** × mastering (8곡)
- **Neo-Soul** × effect_sound (7곡)
- **Neo-Soul** × mastering (7곡)
- **Funk Pop** × effect_sound (8곡)


## 4.4 K-장르 간 슬롯 비교 (2026-05-12 추가)

DB 385행에서 K-Ballad(163행), K-Indie(76행), K-Funk(33행), K-Rock(40행)의 슬롯 사용 패턴을 비교한다. 같은 K-계열이지만 슬롯별로 완전히 다른 어휘 세계가 존재한다.

### 악기(INS) 슬롯 비교

| 악기 | K-Ballad | K-Indie | K-Funk | K-Rock |
|------|----------|---------|--------|--------|
| electric guitar | 40% | 58% | 85% | **100%** |
| acoustic guitar | **56%** | 49% | — | — |
| grand piano | **40%** | — | — | — |
| electric bass | 42% | 38% | 76% | 68% |
| slap bass | — | — | **85%** | — |
| bass guitar | 12% | 8% | — | **82%** |
| synthesizer | 18% | 13% | 52% | — |
| brass section | — | — | **52%** | — |
| string section | 15% | — | — | — |
| pad | 12% | 8% | 45% | 38% |

**핵심**:
- K-Ballad = piano+acoustic 중심의 미니멀 편성
- K-Indie = acoustic+electric 균형
- K-Funk = slap+brass+synth의 리듬 편성 (다른 K와 완전 분리)
- K-Rock = electric guitar+bass guitar의 밴드 편성

### 보컬(VOC) 슬롯 비교

| 보컬 | K-Ballad | K-Indie | K-Funk | K-Rock |
|------|----------|---------|--------|--------|
| breathy | **62%** | 48% | — | — |
| soft | **55%** | 58% | — | — |
| intimate | 48% | 42% | — | — |
| bright | — | — | **85%** | 38% |
| powerful | 8% | — | — | **42%** |
| tenor | 25% | 25% | 33% | **55%** |
| baritone | **35%** | 30% | — | 18% |

**핵심**:
- K-Ballad/K-Indie = breathy+soft+intimate 서정 계열
- K-Funk = bright 독점 (85%)
- K-Rock = powerful+tenor 에너지 계열

### 주법(EFX) 슬롯 비교

| 주법 | K-Ballad | K-Indie | K-Funk | K-Rock |
|------|----------|---------|--------|--------|
| arpeggiated | **52%** | 25% | — | 25% |
| clean | 38% | **62%** | 33% | 35% |
| staccato | — | — | **73%** | — |
| slap | — | — | **85%** | — |
| syncopated | 12% | 28% | 94% | 52% |
| distorted | — | — | — | **62%** |
| power chord | — | — | — | **65%** |
| driving | — | — | 15% | **65%** |
| palm-muted | — | — | — | **52%** |
| fingerstyle | 18% | 21% | — | — |

**핵심**: K-장르를 구분하는 가장 강력한 단서는 주법 슬롯이다:
- K-Ballad → arpeggiated+fingerstyle
- K-Indie → clean+syncopated
- K-Funk → slap+staccato (배타적)
- K-Rock → distorted+power chord+driving (배타적)

### 배타적 식별 어휘 (장르 전환 가이드)

| 원하는 장르 | 반드시 포함할 어휘 | 반드시 제외할 어휘 |
|------------|-------------------|-------------------|
| K-Ballad | breathy, arpeggiated, grand piano | slap, staccato, distorted, power chord |
| K-Indie | soft, clean, syncopated | slap, brass, power chord, driving |
| K-Funk | slap, staccato, bright, brass | breathy, arpeggiated, grand piano |
| K-Rock | distorted, power chord, driving | breathy, slap, staccato, grand piano |


## 4.5 SP 길이와 장르 (2026-05-12 추가)

DB 385행 재분석 SP 길이 분석. SP를 작성할 때 장르별 적정 길이를 참조한다.

### 전체 통계

| 항목 | 값 |
|------|-----|
| 평균 | 522자 |
| 중앙값 | 517자 |
| 표준 구간 (Q1~Q3) | 464~575자 |
| 최빈 구간 | 400~599자 (전체의 75%) |

> **생성 측 검증 (N시리즈 140곡, → 6장 6.5)**: 우리 SP 생성 엔진의 배치별 평균 길이 궤적이 이 표준을 실측으로 따라갔다 — N001 407자(정보 부족)→ N004 749자/최대 893자(과포화 부스트 INST5/MIN650)→ N006부터 510~566자 안정권 복귀. 즉 위 522자 표준은 생성 측에서도 자기수렴 지점이었고, N004의 893자 팽창은 위 과포화 경계(900자)를 직접 건드린 사례다. "길수록 좋다"가 아니라 표준 근방이 최적임이 양쪽(재분석 코퍼스 + 생성)에서 확인된다.

### 장르별 적정 길이

| 장르 | 행수 | 평균 SP 길이 | 적정 범위 | 해석 |
|------|------|-------------|----------|------|
| Classical | 6 | **697자** | 630~760 | 오케스트라 편성 = 가장 많은 묘사 |
| Folk | 9 | 586자 | 420~670 | 어쿠스틱 편성 변주 |
| Jazz | 14 | 586자 | 410~760 | 보이싱/화성 묘사 |
| Electronic | 15 | 572자 | 460~790 | 신스 파라미터 상세 |
| Hip-Hop | 18 | 551자 | 390~720 | 비트+효과 중심 |
| R&B/Soul | 16 | 550자 | 460~650 | 보컬+그루브 |
| Pop | 29 | 540자 | 360~880 | 범위 가장 넓음 (융합 장르) |
| Rock | 38 | 539자 | 340~680 | 밴드 편성 |
| Indie | 35 | 524자 | 410~660 | 중간 복잡도 |
| Funk | 31 | 517자 | 380~680 | 리듬 중심 |
| Ballad | 158 | **484자** | 230~670 | 미니멀 편성 → 가장 짧음 |

### Vocal vs Instrumental

| 유형 | 평균 SP | 차이 |
|------|---------|------|
| Vocal | 505자 | 기준 |
| Instrumental | 560자 | **+55자** |

보컬 묘사 자리를 악기 묘사가 대체하므로, Instrumental SP는 50~60자 더 길게 작성 가능.

### SP 길이 실용 가이드

1. **500자 = Suno 재분석 표준**: 이보다 짧으면 정보 부족, 길면 과밀
2. **장르별 조절**: Ballad ~480자 / Rock ~540자 / Classical ~700자
3. **과포화 경계**: B192 실패 곡(964~999자)은 재분석 평균의 ~2배 → 900자 이상은 위험 (→ **6장 6.5**에서 N시리즈로 실측 재현: N004가 평균 749·최대 893자까지 팽창했다가 안정권 복귀)
4. **편성 복잡도 ∝ SP 길이**: 악기 수가 많으면 자연스럽게 길어짐
5. **Instrumental +55자 규칙**: 보컬곡 대비 악기 묘사 여유

### 장르 단어수 vs SP 길이 (Pearson r = 0.33)

장르명이 복잡할수록 SP가 약간 길어지지만, 약한 상관에 불과. 장르명 9단어까지 SP 길이 단조증가, 이후 감소 — 지나치게 긴 장르명은 오히려 초점을 잃음.


## 4.6 장르 경계의 겹침 (2026-05-12 추가)

K-장르 서브타입 분석에서 장르 경계가 모호한 조합이 발견된다.

| 겹침 쌍 | 공유 시그니처 | 차이점 |
|---------|-------------|--------|
| K-Indie Ballad ≈ K-Ballad Folk | acoustic+breathy+arpeggiated | 장르 라벨만 다름 |
| K-Rock Soft ≈ K-Ballad Rock | arpeggiated+clean+delay | BPM 73 vs 72 (무의미) |
| K-Indie Rock ≈ K-Rock Indie | syncopated+clean+reverb | 템포 109 vs 107 (미미) |
| K-Funk J-Fusion ≈ 독립 | slap+bright+synth | 다른 K-장르와 겹침 최소 |

**시사점**: Suno의 장르 분류는 이산적 카테고리가 아니라 연속적 스펙트럼이다. SP 작성 시 장르명보다 **배타적 어휘**(§4.4)가 실제 사운드를 결정한다.

## 4.7 장르별 수식어 프로파일 (2026-05-14 추가)

445개 재분석 SP에서 25개 핵심 수식어의 장르별 사용률을 분석한다. `clean`은 모든 장르에서 64~92%로 보편적이므로, 장르를 감별하는 것은 **2~3위 수식어**다.

### 장르별 Top 3 수식어 (clean 제외)

| 장르 | 곡수 | 2위 | 3위 | 4위 |
|------|------|-----|-----|-----|
| Pop | 193 | subtle 45% | breathy 39% | crisp 36% |
| Electronic | 43 | subtle 65% | crisp 60% | bright 40% |
| Ballad | 43 | breathy 58% | subtle 56% | **warm 49%** |
| R&B | 38 | breathy 55% | **soft 50%** | subtle 50% |
| Folk | 36 | subtle 53% | soft 47% | breathy 47% |
| Rock | 25 | **distorted 36%** | subtle 32% | bright 32% |
| Jazz | 15 | subtle 47% | crisp 40% | smooth 33% |
| Funk | 13 | subtle 69% | breathy 62% | crisp 54% |
| Bossa Nova | 9 | **soft 78%** | subtle 67% | **sparse 56%** |
| Trot | 12 | subtle 50% | crisp 42% | soft 42% |

### 장르 감별 수식어

특정 장르에서 유의미하게 높고 타 장르에서 낮은 수식어:

| 수식어 | 감별 장르 | 해당 장르 | 타장르 평균 | 배율 |
|--------|----------|----------|-----------|------|
| **warm** | Ballad | 49% | 23% | ×2.1 |
| **distorted** | Rock | 36% | 7% | ×5.1 |
| **punchy** | Funk | 38% | 10% | ×3.8 |
| **sparse** | Bossa Nova | 56% | 18% | ×3.1 |
| **soft** | Bossa Nova | 78% | 33% | ×2.4 |

### SP 작성 실용 가이드

장르를 바꾸고 싶을 때, 수식어만 교체하면 된다:

| 목표 장르 | 추가할 수식어 | 제거할 수식어 |
|----------|-------------|-------------|
| → Ballad | warm, breathy, intimate | distorted, punchy, bright |
| → Rock | distorted, heavy, driving | soft, warm, breathy |
| → Funk | punchy, bright, crisp, tight | warm, soft, sparse |
| → Bossa Nova | soft, sparse, warm, mellow | distorted, punchy, heavy |
| → Electronic | crisp, bright, subtle, atmospheric | warm, soft, acoustic |

§4.4의 배타적 악기/주법 어휘와 이 수식어 프로파일을 결합하면, 장르명 없이도 원하는 장르의 사운드를 유도할 수 있다.