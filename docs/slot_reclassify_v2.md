# Suno 슬롯 재분류 v2 — 결과 요약

> 생성일: 2026-04-18 · SP 2291문장 · 브래킷 2282개

## 슬롯 구조

```
1.  장르 선언           — 첫 문장, 100% 일관
2.  악기 레이어 (동적)  — 곡에 등장하는 악기만큼 2-1, 2-2, ...
3.  드럼                — 킥/스네어/하이햇/퍼커션 보조 + 필인/패턴
4.  보컬
    4-1. 메인보컬       — 음역, 톤, 기법 (syncopated, laid-back 등)
    4-2. 코러스/백킹    — 더블링, 레이어드, 하모니, 애드립
5.  템포/조성/박자      — BPM, key, time signature
6.  믹싱                — 마이킹, 스테레오, 패닝, 컴프레션, EQ
    ※ 마스터링(limiter, LUFS, multiband 등)도 이 슬롯 하위.
      단, Suno SP에서 마스터링 수준 표현은 0건 — 믹싱 레벨까지만 묘사함.
7.  전자 이펙터         — 리버브, 딜레이, 코러스이펙트, 디스토션 등
8.  사운드 이펙트       — 바이닐크랙클, 기계음, 환경음 등
9.  편곡 총평           — 원문 리스팅 (악기값은 슬롯2에 복사)
10. 없음 선언           — 명시적 제외/퇴장 ('no percussion', 'drops out')
```

**원칙**: 하나의 표현이 복수 슬롯에 들어가는 것이 정상.
규칙이 아니라 '가능성 높은 패턴'으로 기술.

---

## SP 슬롯별 분포

| 슬롯 | 빈도 | 비율 |
|------|------|------|
| instruments | 971 | 42.4% |
| vocal_main | 853 | 37.2% |
| tempo_key_time | 447 | 19.5% |
| drums | 444 | 19.4% |
| arrangement | 390 | 17.0% |
| genre | 326 | 14.2% |
| effect_electronic | 271 | 11.8% |
| mixing | 100 | 4.4% |
| vocal_chorus | 72 | 3.1% |
| absence | 17 | 0.7% |
| effect_sound | 17 | 0.7% |
| unclassified | 1 | 0.0% |

### SP 슬롯별 예시

**genre**:
- `K-Pop Indie Pop ballad.`
- `K-Pop ballad with jazz-pop and soul influences.`
- `K-Indie folk ballad.`
- `K-Pop ballad with R&B influences.`
- `K-Hip Hop with a boom bap influence.`

**instruments**:
- `Clean electric guitar plays a repetitive arpeggiated pattern with light chorus and delay.`
- `A sub-bass synth provides low-end weight on the downbeats.`
- `A secondary electric guitar enters with sustained, ambient swells.`
- `The arrangement is sparse, focusing on the vocal performance and the rhythmic interplay between the guitar and the kick `
- `The arrangement features a prominent upright bass playing walking lines and syncopated rhythms, a grand piano providing `

**drums**:
- `The drums consist of a dry, tight kick and a crisp snare with a subtle electronic clap layer.`
- `The arrangement is sparse, focusing on the vocal performance and the rhythmic interplay between the guitar and the kick `
- `The arrangement features a prominent upright bass playing walking lines and syncopated rhythms, a grand piano providing `
- `A drum kit uses brushes on the snare with a light swing feel.`
- `Percussion is minimal, featuring a soft electronic kick and a crisp snare with a short decay.`

**vocal_main**:
- `Breathy, intimate female vocals are processed with moderate plate reverb and centered in the mix.`
- `The arrangement is sparse, focusing on the vocal performance and the rhythmic interplay between the guitar and the kick `
- `The arrangement features a prominent upright bass playing walking lines and syncopated rhythms, a grand piano providing `
- `The male lead vocal is a smooth tenor, utilizing a mix of chest voice and light vibrato.`
- `A soft, breathy baritone male vocal sits forward in the mix with light plate reverb.`

**vocal_chorus**:
- `Male vocals are delivered in a smooth, melodic tenor range with light doubling in the chorus.`
- `Male vocals are energetic and melodic, sitting forward in the mix with light doubling and short plate reverb.`
- `The production features clean, dry vocal processing in the verses with increased reverb and layering during the melodic `
- `Occasional vocal ad-libs and layered harmonies appear in the background.`
- `The arrangement transitions from a sparse, rhythmic verse to a dense, wall-of-sound chorus with layered vocal harmonies.`

**tempo_key_time**:
- `The tempo is 72 BPM in the key of C Major.`
- `The track is in the key of E Major at a tempo of 82 BPM in 4/4 time.`
- `Tempo is 78 BPM in 4/4 time, key of G Major.`
- `Tempo is 72 BPM in 4/4 time.`
- `The tempo is 92 BPM in the key of G minor.`

**mixing**:
- `Breathy, intimate female vocals are processed with moderate plate reverb and centered in the mix.`
- `A soft, breathy baritone male vocal sits forward in the mix with light plate reverb.`
- `Male vocals are delivered in a smooth, mid-range baritone with light compression.`
- `Male vocals are energetic and melodic, sitting forward in the mix with light doubling and short plate reverb.`
- `The arrangement is dense with a polished, high-fidelity production style.`

**effect_electronic**:
- `Clean electric guitar plays a repetitive arpeggiated pattern with light chorus and delay.`
- `Breathy, intimate female vocals are processed with moderate plate reverb and centered in the mix.`
- `Production is clean with natural room reverb on the acoustic instruments.`
- `A soft, breathy baritone male vocal sits forward in the mix with light plate reverb.`
- `Clean electric guitar plays arpeggiated chords with light chorus and reverb.`

**effect_sound**:
- `A subtle vinyl crackle texture persists throughout the arrangement.`
- `Subtle vinyl crackle and atmospheric city noise are layered in the background.`
- `Occasional record scratches and vinyl crackle textures are layered into the mix.`
- `A soft, muffled kick drum enters on beats 1 and 3, accompanied by a subtle shaker on eighth notes.`
- `Production includes subtle record scratch effects and vocal doubling on the hook.`

**arrangement**:
- `Breathy, intimate female vocals are processed with moderate plate reverb and centered in the mix.`
- `The arrangement is sparse, focusing on the vocal performance and the rhythmic interplay between the guitar and the kick `
- `The arrangement features a prominent upright bass playing walking lines and syncopated rhythms, a grand piano providing `
- `The arrangement is minimalist, focusing on the interplay between the rhythmic acoustic guitar and the intimate vocal del`
- `Male vocals are delivered in a breathy, intimate tenor range, transitioning to a powerful chest voice in the chorus.`

**absence**:
- `The bridge features a stripped-back section with filtered synth pads before returning to the full groove.`
- `The arrangement centers on a solo violin playing a lyrical melody over a grand piano.`
- `Minimalist arrangement with no percussion or bass.`
- `No percussion or bass is present in this segment.`
- `A solo cello plays a counter-melody in the lower register.`

**unclassified**:
- `The harmonic progression uses jazz-influenced extensions and secondary dominants common in contemporary Korean ballads.`

---

## 악기 빈도 (SP)

| # | 악기 | 빈도 |
|---|------|------|
| 1 | bass guitar | 284 |
| 2 | electric guitar | 235 |
| 3 | guitar | 183 |
| 4 | clean electric guitar | 148 |
| 5 | synthesizer | 142 |
| 6 | acoustic guitar | 126 |
| 7 | acoustic piano | 123 |
| 8 | pad | 113 |
| 9 | synth bass | 62 |
| 10 | slap bass | 37 |
| 11 | strings | 28 |
| 12 | brass | 23 |
| 13 | electric piano | 19 |
| 14 | cello | 11 |
| 15 | rhodes | 9 |
| 16 | violin | 8 |
| 17 | upright bass | 6 |
| 18 | trumpet | 6 |
| 19 | saxophone | 4 |
| 20 | harp | 3 |
| 21 | 808 | 3 |
| 22 | organ | 2 |
| 23 | harmonica | 1 |
| 24 | trombone | 1 |

---

## 코드/보이싱 표현 (악기 슬롯 내 수식어)

| 표현 | 빈도 |
|------|------|
| sustained chords | 32 |
| arpeggiated chords | 29 |
| power chords | 28 |
| harmonies | 27 |
| chord progression | 21 |
| harmonic support | 15 |
| harmonic depth | 11 |
| harmonic density | 9 |
| harmonic texture | 9 |
| harmonic padding | 7 |
| jazz chords | 6 |
| harmonic sustain | 4 |
| block chords | 3 |
| harmonic pads | 3 |
| voicings | 3 |
| harmonic warmth | 2 |
| harmonic backing | 2 |
| harmonic wash | 2 |
| harmonic fill | 2 |
| harmonic accompaniment | 1 |
| jazz voicings | 1 |
| harmonic thickening | 1 |
| harmonic structure | 1 |
| harmonic accents | 1 |
| harmonic filling | 1 |
| harmonic progression | 1 |
| power chord | 1 |
| harmonic element | 1 |
| harmonic layers | 1 |
| harmonic layering | 1 |
| sustained chord | 1 |
| open chord | 1 |
| harmonic layer | 1 |
| harmonic movement | 1 |

> 코드/보이싱은 독립 슬롯이 아닌 악기 레이어의 수식어로 등장.

---

## 가사 브래킷 슬롯별 분포

| 슬롯 | 빈도 | 비율 |
|------|------|------|
| section | 974 | 42.7% |
| instruments | 753 | 33.0% |
| vocal_main | 478 | 20.9% |
| transition | 464 | 20.3% |
| drums | 361 | 15.8% |
| pronunciation | 137 | 6.0% |
| effect_electronic | 96 | 4.2% |
| arrangement | 64 | 2.8% |
| vocal_chorus | 25 | 1.1% |
| effect_sound | 16 | 0.7% |
| absence | 10 | 0.4% |

### 브래킷 슬롯별 예시

**section**:
- `[Intro]`
- `[Verse 1]`
- `[Intro]`
- `[Verse 1]`
- `[Pre-Chorus]`

**instruments**:
- `[arpeggiated clean electric guitar with chorus]`
- `[upright bass, grand piano, brushed snare drum]`
- `[muted trumpet enters]`
- `[piano chords intensify]`
- `[muted trumpet melodic fill]`

**drums**:
- `[kick drum enters]`
- `[upright bass, grand piano, brushed snare drum]`
- `[muted trumpet melodic fill]`
- `[soft electronic kick enters]`
- `[sub-bass synth enters, snare hits on 2 and 4]`

**vocal_main**:
- `[breathy female vocals]`
- `[male tenor vocals]`
- `[breathy baritone male vocals]`
- `[breathy male vocals]`
- `[melodic male vocals]`

**vocal_chorus**:
- `[melodic vocal ad-libs with reverb]`
- `[vocal harmony on '삭제']`
- `[vocal harmonies enter]`
- `[synth pads enter, layered vocal harmonies]`
- `[melodic male vocals, layered harmonies]`

**transition**:
- `[kick drum enters]`
- `[muted trumpet enters]`
- `[piano chords intensify]`
- `[soft electronic kick enters]`
- `[sub-bass synth enters, snare hits on 2 and 4]`

**effect_electronic**:
- `[arpeggiated clean electric guitar with chorus]`
- `[clean electric guitar with chorus effect, synth bass, electronic drums]`
- `[clean electric guitar with chorus effect, soft shaker]`
- `[melodic vocal ad-libs with reverb]`
- `[clean electric guitar arpeggio with chorus effect]`

**effect_sound**:
- `[synth riser]`
- `[clean electric guitar riff, vinyl crackle]`
- `[jazzy piano loop, vinyl crackle, light percussion]`
- `[Rhodes electric piano, record scratch, vinyl crackle]`
- `[syncopated piano chords, vinyl crackle, melodic bass enters]`

**arrangement**:
- `[full band arrangement, driving bassline]`
- `[full band arrangement]`
- `[full band enters, strings swell, belted vocals]`
- `[full band intensity, open power chords]`
- `[full arrangement, energetic brass]`

**absence**:
- `[instrumental fade out]`
- `[guitar stops briefly]`
- `[solo violin melody, arpeggiated grand piano]`
- `[guitar continues, drums fade out]`
- `[solo cello enters]`

**pronunciation**:
- `[sub-bass synth enters, snare hits on 2 and 4]`
- `[palm-muted electric guitar riff]`
- `[clean electric guitar eighth-note rhythm, syncopated bass enters]`
- `[melodic vocal ad-libs with reverb]`
- `[sub-kick enters]`

---

## 가사 브래킷 실사용 가이드

### 기본 문법: `[...]`

Suno 가사에서 `[대괄호]`는 **비가사 지시문**을 의미합니다.
가사가 아닌 모든 음악적 지시는 대괄호 안에 넣습니다.

### 브래킷 용도별 패턴

#### 1. 섹션 구분
```
[Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Bridge]
[Outro]
[Instrumental]
[Breakdown]
```
- 대문자 시작이 관례
- 단독 한 줄에 배치

#### 2. 악기 큐 (진입/퇴장/변경)
```
[fingerpicked acoustic guitar]           ← 구간 시작 시 악기 지정
[clean electric guitar enters]            ← 진입 타이밍
[bass guitar enters with a slide]         ← 진입 + 주법
[synth pads swell]                        ← 변화
[guitar stops briefly]                    ← 일시 중단
[piano melodic fill]                      ← 필인
```

#### 3. 드럼 큐
```
[kick drum enters]                        ← 킥 진입
[shaker enters]                           ← 퍼커션 보조 진입
[drum fill]                               ← 필인
[drums fade out]                          ← 퇴장
[soft kick drum, brushed snare]           ← 드럼 편성 지정
```

#### 4. 보컬 지시
```
[breathy female vocals]                   ← 메인보컬 톤+성별
[male tenor vocals]                       ← 메인보컬 음역
[male vocals enter]                       ← 보컬 진입
[whispered vocals]                        ← 기법 전환
[vocal harmony on '사랑']                 ← 코러스/하모니
[layered vocals]                          ← 레이어드
[ad-lib]                                  ← 애드립
```

#### 5. 이펙트/전환
```
[guitar feedback swell]                   ← 사운드 이펙트
[vinyl crackle]                           ← 환경 이펙트
[piano chords intensify]                  ← 다이내믹 전환
[full band arrangement]                   ← 편곡 전환
[instrumental fade out]                   ← 페이드 아웃
```

#### 6. 가사 중간 삽입
```
서랍 깊은 곳에 누런 봉투 하나 [muted trumpet enters]
접힌 자국 사이로 번진 마음 [piano chords intensify]
```
- 가사 텍스트 사이에 브래킷을 넣으면 **해당 시점**에 이벤트 발생
- 줄 끝에 붙이는 것이 가장 흔한 패턴

### SP ↔ 가사 브래킷 관계

| SP (팔레트) | 가사 브래킷 (타임라인) |
|------------|----------------------|
| 곡 전체에 이런 악기가 있다 | 이 구간에서 이 악기가 들어온다 |
| 전체 톤/성격 선언 | 시점별 변화 지시 |
| 산문 텍스트 | `[대괄호]` 지시문 |

**SP에서 선언한 악기가 가사에서 진입하는 것이 가장 높은 확률의 패턴.**
SP에 없는 악기를 가사에서 직접 큐하는 것도 가능하지만 빈도가 낮음.

---

## 경계 단어 정리

### 복수 슬롯에 걸리는 단어

| 단어 | 의미 A | 의미 B | 판별 기준 |
|------|--------|--------|-----------|
| bass | 베이스 기타 (악기) | bass drum (드럼) | 'bass guitar/line/plays' → 악기, 'bass drum' → 드럼 |
| bass | 베이스 기타 | synth bass (별도 악기) | 'synth bass/sub-bass' → synth bass |
| chorus | 섹션 태그 | 코러스 이펙트 | 대문자 단독 `[Chorus]` → 섹션, 'light chorus' → 이펙터 |
| close-mic | 보컬 기법 | 믹싱 기법 | 양쪽 슬롯에 중복 등록 |
| pitch correction | 보컬 프로세싱 | 전자 이펙터 | 양쪽 슬롯에 중복 등록 |
| vibrato | 보컬 기법 | 이펙터 (tremolo와 혼용) | 보컬 문맥 → 보컬, 악기 문맥 → 이펙터 |
| reverb | 믹싱 요소 | 전자 이펙터 | 양쪽 슬롯에 중복 등록 |
| fills | 드럼 필인 | 악기 melodic fill | 'drum fill' → 드럼, 'melodic fill' → 악기 |
| groove | 드럼 패턴 | 템포/느낌 | 'drum groove' → 드럼, 'mid-tempo groove' → 템포 |
| solo | 없음 선언 (solo = 다른 건 없음) | 연주 기법 | 'solo vocal' → 없음선언, 'guitar solo' → 악기 |

### 별도 악기로 구분해야 하는 것

| 같은 카테고리 아님 | 이유 |
|-------------------|------|
| bass guitar ≠ synth bass | 음색·역할·주법 완전히 다름 |
| synthesizer ≠ keyboard | keyboard=물리악기(keys), synthesizer=소리합성 |
| acoustic piano ≠ electric piano | 음색·표현 범위 다름 |
| acoustic guitar ≠ electric guitar | 주법·이펙트 체인 다름 |
| clean electric guitar ≠ distorted electric guitar | 이펙트 유무로 캐릭터 분리 |

---

## 수치 요약

- SP 문장: 2291개
- 가사 브래킷: 2282개
- 고유 악기: 24종
- 코드/보이싱 표현: 34종 (총 230회)
- SP 미분류: 1개
- 브래킷 미분류: 0개