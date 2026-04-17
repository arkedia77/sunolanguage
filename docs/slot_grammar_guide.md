# Suno SP 7-Slot Grammar — leomusic2 참조 가이드

> 출처: sunolanguage v2 (326 clips / 318곡 / 2,291문장 분석)
> 생성일: 2026-04-17
> 전체 데이터: `data/reanalysis_v2/suno_sp_slot_grammar.json`

## 슬롯(Slot)이란?

NLP frame semantics의 slot: 구조화된 템플릿 내 채워야 할 빈칸.
Suno SP는 자유 산문처럼 보이지만, 7개 슬롯이 일관되게 출현하며
각 슬롯마다 고정된 구문 패턴과 어휘 풀이 존재.

## 7-Slot 프레임 (출현 순서)

| # | 슬롯 | 위치 | 필수 | 문장수 | 핵심 포맷 |
|---|------|------|------|-----:|------|
| 1 | **장르 선언** | 첫 문장 | Y | 323 | `{장르 라벨}. / {장르} with {영향} influences.` |
| 2 | **악기 레이어** | 본문 (복수) | Y | 580 | `{악기} plays/performs {패턴} with {이펙트}.` |
| 3 | **드럼/퍼커션** | 본문 | N | 290 | `The drums consist of {킥} and {스네어} with {레이어}.` |
| 4 | **보컬** | 본문 | N | 280 | `{보컬타입} vocals delivered in {음역} with {프로세싱}.` |
| 5 | **템포/조성/박자** | 후반부 | Y | 406 | `The tempo is <BPM> in the key of <KEY>.` |
| 6 | **프로덕션/믹스** | 본문~후반 | N | 163 | `Production is {특성} with {리버브} on {대상}.` |
| 7 | **어레인지먼트 총평** | 마지막 | N | 249 | `The arrangement is {밀도}, focusing on {상호작용}.` |

---

## genre_declaration: 장르 선언

**설명**: 장르 선언. Suno가 첫 문장에서 장르 라벨을 제시하는 슬롯.

### 장르 라벨 TOP 15
| 라벨 | 빈도 |
|------|-----:|
| k-pop ballad + [featuring] modifier | 34 |
| k-pop ballad + [with] modifier | 28 |
| k-pop ballad | 25 |
| k-pop r&b ballad | 19 |
| k-indie folk ballad | 18 |
| k-pop acoustic ballad | 11 |
| k-indie pop | 9 |
| k-pop + [with] modifier | 9 |
| k-pop funk-pop | 9 |
| k-pop hip-hop track + [featuring] modifier | 8 |
| k-indie ballad | 6 |
| k-indie pop + [with] modifier | 5 |
| k-rock + [with] modifier | 5 |
| k-pop indie pop | 5 |
| k-pop r&b + [with] modifier | 5 |

### 구문 템플릿 TOP 5
- (25) `k-pop ballad.`
- (19) `k-pop r&b ballad.`
- (18) `k-indie folk ballad.`
- (17) `k-pop ballad featuring a baritone male vocal.`
- (11) `k-pop ballad with r&b influences.`

### 실제 예제
- K-Pop Indie Pop ballad.
- K-Pop ballad with jazz-pop and soul influences.
- K-Indie folk ballad.

---

## instrument_layers: 악기 레이어

**설명**: 악기/어레인지먼트 레이어. 각 악기의 연주 패턴·이펙트·역할 기술.

### 악기 TOP 15
| 악기 | 빈도 |
|------|-----:|
| clean electric guitar | 130 |
| acoustic guitar | 60 |
| electric guitar | 56 |
| bass guitar | 43 |
| synth pads | 20 |
| slap bass | 16 |
| electric piano | 14 |
| string section | 14 |
| sub-bass synth | 12 |
| grand piano | 11 |
| synth bass | 11 |
| synth pad | 11 |
| cello | 8 |
| synthesizer pads | 6 |
| violin | 6 |

### 구문 템플릿 TOP 5
- (7) `fingerpicked acoustic guitar in a steady eighth-note pattern.`
- (4) `acoustic guitar plays a steady fingerstyle pattern with alternating bass notes and arpeggiated chords.`
- (4) `clean electric guitar plays arpeggiated chords with light chorus and reverb.`
- (4) `a clean electric guitar provides subtle arpeggiated textures in the background.`
- (4) `clean electric guitar plays arpeggiated chords with light chorus and delay.`

### 실제 예제
- Clean electric guitar plays a repetitive arpeggiated pattern with light chorus and delay.
- A sub-bass synth provides low-end weight on the downbeats.
- A secondary electric guitar enters with sustained, ambient swells.

---

## drums: 드럼/퍼커션

**설명**: 드럼/퍼커션 전용 기술. 킥·스네어·하이햇·셰이커 등 타격음 구성.

### 드럼 요소 TOP 10
| 요소 | 빈도 |
|------|-----:|
| crisp snare | 81 |
| shaker | 32 |
| soft kick drum | 24 |
| tight snare | 16 |
| dry kick drum | 15 |
| cymbal | 15 |
| electronic snare | 14 |
| tight kick drum | 12 |
| soft kick | 12 |
| rimshot | 12 |

### 구문 템플릿 TOP 5
- (4) `a sub-heavy synth bass follows the kick drum pattern.`
- (3) `percussion consists of a crisp electronic snare on the backbeat and a tight, dry kick drum.`
- (3) `the bass guitar follows the kick drum with a thick, overdriven tone.`
- (3) `a warm synth bass follows the kick drum pattern.`
- (3) `the bass guitar follows the kick drum with a consistent eighth-note pulse.`

### 실제 예제
- The drums consist of a dry, tight kick and a crisp snare with a subtle electronic clap layer.
- A drum kit uses brushes on the snare with a light swing feel.
- Percussion is minimal, featuring a soft electronic kick and a crisp snare with a short decay.

---

## vocals: 보컬

**설명**: 보컬 타입·딜리버리·프로세싱. 음역·발성법·이펙트 기술.

### 보컬 타입 TOP 10
| 타입 | 빈도 |
|------|-----:|
| baritone male vocal | 12 |
| smooth male | 8 |
| male tenor vocal | 6 |
| male tenor vocals | 5 |
| breathy female vocal | 5 |
| breathy male | 4 |
| breathy male vocals | 4 |
| male baritone vocal | 4 |
| breathy male vocal | 3 |
| male baritone vocals | 2 |

### 딜리버리 스타일
| 스타일 | 빈도 |
|------|-----:|
| breathy | 114 |
| melodic | 110 |
| intimate | 63 |
| conversational | 56 |
| rhythmic | 55 |
| smooth | 49 |
| soft | 42 |
| powerful | 20 |
| emotive | 8 |
| percussive | 6 |

### 보컬 프로세싱
| 프로세싱 | 빈도 |
|------|-----:|
| vibrato | 44 |
| doubling | 15 |
| minimal vibrato | 13 |
| light reverb | 7 |
| plate reverb | 7 |
| pitch correction | 3 |
| room reverb | 2 |
| delay | 1 |

### 구문 템플릿 TOP 5
- (3) `female vocals are delivered in a breathy, intimate head voice with minimal vibrato.`
- (3) `a male vocalist sings in a soft, conversational baritone with light breathiness and minimal vibrato.`
- (2) `male tenor vocals.`
- (2) `the vocal performance is intimate with breathy delivery in the lower register, transitioning to a resonant chest voice.`
- (2) `male vocals are delivered in a breathy, intimate baritone register with minimal vibrato.`

### 실제 예제
- Male vocals are delivered in a breathy, intimate tenor range, transitioning to a powerful chest voice in the chorus.
- Male vocals transition from a melodic, sung intro to a rhythmic, percussive rap delivery.
- The vocals transition between rhythmic rapping and melodic singing with light pitch correction and reverb.

---

## tempo_key_time: 템포/조성/박자

**설명**: 템포(BPM)·조성(Key)·박자(Time signature). 구문 템플릿이 고정적.

### 구문 템플릿 TOP 5
- (59) `key of <KEY>.`
- (55) `the tempo is <BPM> in the key of <KEY>.`
- (40) `tempo is <BPM>.`
- (32) `the tempo is <BPM> in <TIME> time.`
- (27) `key of <KEY>, <BPM>.`

### 실제 예제
- The tempo is 72 BPM in the key of C Major.
- The track is in the key of E Major at a tempo of 82 BPM in 4/4 time.
- Tempo is 78 BPM in 4/4 time, key of G Major.

---

## production: 프로덕션/믹스

**설명**: 프로덕션/믹스 특성. 리버브 타입, 마이크 배치, 전체 공간감 기술.

### 구문 템플릿 TOP 5
- (3) `male vocals are processed with light pitch correction and doubling.`
- (3) `the mix is intimate with close-mic proximity and light room reverb on the vocals.`
- (2) `the vocal performance is intimate and breathy, utilizing a close-mic technique with light plate reverb.`
- (2) `the vocal performance uses a mix of chest voice and breathy delivery, with subtle vibrato on sustained notes.`
- (2) `the production is clean with light plate reverb on the vocals and guitar.`

### 실제 예제
- Breathy, intimate female vocals are processed with moderate plate reverb and centered in the mix.
- The male lead vocal is a smooth tenor, utilizing a mix of chest voice and light vibrato.
- Production is clean with natural room reverb on the acoustic instruments.

---

## arrangement_summary: 어레인지먼트 총평

**설명**: 어레인지먼트 총평. 'The arrangement is sparse/dense, focusing on...' 패턴.

### 구문 템플릿 TOP 5
- (17) `the arrangement centers on a grand piano playing sustained chords and melodic fills.`
- (6) `the arrangement is sparse, focusing on the interplay between the vocal melody and the rhythmic guitar strumming.`
- (4) `the arrangement is sparse, focusing on the interplay between the rhythmic acoustic guitar and the vocal melody.`
- (4) `the arrangement is sparse, focusing on the interplay between the acoustic guitar and the vocal melody.`
- (4) `the arrangement is sparse, focusing on the interplay between the vocal melody and the acoustic guitar.`

### 실제 예제
- The arrangement is sparse, focusing on the vocal performance and the rhythmic interplay between the guitar and the kick drum.
- The arrangement features a prominent upright bass playing walking lines and syncopated rhythms, a grand piano providing harmonic accompaniment with jazz voicings, and a muted trumpet performing melodic fills and a solo.
- The arrangement is minimalist, focusing on the interplay between the rhythmic acoustic guitar and the intimate vocal delivery.

---

## 가사 브래킷 시스템 (leomusic2 가사 생성용)

총 출현: **2282**

### 타입별 분포
| 타입 | 출현 | 고유 |
|------|-----:|-----:|
| section | 1015 | 45 |
| instrument_or_arrangement | 869 | 600 |
| effect | 381 | 91 |
| vocal_direction | 400 | 152 |
| transition_cue | 408 | 258 |
| uncategorized | 77 | 56 |

### 브래킷 TOP 20
| 브래킷 | 빈도 |
|------|-----:|
| [verse 1] | 326 |
| [intro] | 317 |
| [chorus] | 215 |
| [pre-chorus] | 59 |
| [breathy male vocals] | 58 |
| [verse 2] | 39 |
| [fingerpicked acoustic guitar] | 29 |
| [breathy female vocals] | 28 |
| [male vocals] | 23 |
| [male tenor vocals] | 21 |
| [bass guitar enters] | 18 |
| [kick drum enters] | 14 |
| [fingerpicked acoustic guitar arpeggio] | 12 |
| [smooth male vocals] | 12 |
| [female vocals] | 11 |
| [shaker enters] | 11 |
| [electric bass enters] | 11 |
| [male vocals enter] | 10 |
| [bass enters] | 10 |
| [baritone male vocals] | 9 |

## SP 조합 예제 (7슬롯 완전체)

실제 Suno SP를 7슬롯으로 분해한 것. leomusic2가 SP를 생성할 때 이 구조를 따르면 Suno가 인식하는 포맷에 부합.

### 예제 1: #0001 소음의 끝 (Lo-fi Indie Pop)
```
[1-genre]      K-Pop Indie Pop ballad.
[2-instrument] Clean electric guitar plays a repetitive arpeggiated pattern
               with light chorus and delay.
[2-instrument] A sub-bass synth provides low-end weight on the downbeats.
[3-drums]      The drums consist of a dry, tight kick and a crisp snare
               with a subtle electronic clap layer.
[4-vocals]     Breathy, intimate female vocals are processed with moderate
               plate reverb and centered in the mix.
[2-instrument] A secondary electric guitar enters with sustained, ambient swells.
[5-tempo]      The tempo is 72 BPM in the key of C Major.
[7-arrange]    The arrangement is sparse, focusing on the vocal performance
               and the rhythmic interplay between the guitar and the kick drum.
```

### 예제 2: #0041 첫 발자국 (City Pop / Future Funk)
```
[1-genre]      K-Pop and J-Pop fusion with elements of City Pop and Funk.
[2-instrument] Slap bass line performing syncopated sixteenth-note patterns,
               bright acoustic piano playing jazz-influenced chord extensions,
               and clean electric guitar with rhythmic palm-muted scratching.
[3-drums]      The drum kit uses a crisp, high-tuned snare and a tight kick drum.
[4-vocals]     Male tenor vocal performs with smooth, melodic delivery,
               transitioning into rhythmic, rap-influenced phrasing in the verses.
[5-tempo]      The tempo is 118 BPM in the key of E Major.
[2-instrument] Synthesizer pads provide sustained harmonic support in the background,
               while occasional brass stabs accent the transitions.
```

### 예제 3: #0091 새 안경 (Britpop / Mod Revival) — 간결형
```
[1-genre]      K-Pop, J-Rock, Pop Rock.
[4-vocals]     Male tenor vocals.
[2-instrument] Clean electric guitar plays syncopated eighth-note riffs
               with light overdrive.
[2-instrument] Bass guitar follows the kick drum in a driving 4/4 pattern.
[3-drums]      Acoustic drums feature a prominent snare on 2 and 4
               with consistent hi-hat eighth notes.
[2-instrument] Bright piano chords accent the downbeats.
[5-tempo]      Key of E Major. Tempo 128 BPM.
```