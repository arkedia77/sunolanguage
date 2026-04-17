# Suno SP+가사 7-Slot 템플릿 해석서 (20곡)

> leomusic2 참조용 · 2026-04-17 · sunolanguage v2 (326 clips)

## Part 1: Suno의 두 채널 시스템

Suno에게 곡을 만들라고 할 때, 두 가지 입력 채널이 있다:

### 채널 A: SP (Style Prompt) — "이 곡은 전체적으로 이런 곡이다"

산문 텍스트로 곡의 **전체 성격**을 기술. 7개 슬롯으로 구성:

| # | 슬롯 | 위치 | 역할 |
|---|------|------|------|
| 1 | **장르 선언** | 첫 문장 | Suno가 곡의 장르를 한 문장으로 선언. 첫 문장 고정 위치. |
| 2 | **악기 레이어** | 본문(복수) | 악기별 연주 패턴·이펙트·역할을 기술. 복수 문장, 순서 자유. |
| 3 | **드럼/퍼커션** | 본문 | 킥·스네어·하이햇·셰이커 등 타격음 구성을 기술. |
| 4 | **보컬** | 본문 | 보컬 타입(음역·성별)·딜리버리(발성법)·프로세싱(이펙트)을 기술. |
| 5 | **템포/조성/박자** | 후반부 | BPM·조성·박자를 기술. 고정 구문 패턴. |
| 6 | **프로덕션/믹스** | 본문~후반 | 전체 믹스 특성·리버브 타입·마이크 배치 등 프로덕션 기술. |
| 7 | **어레인지먼트 총평** | 마지막 | 어레인지먼트의 밀도·핵심 상호작용을 총평. |

**SP가 답하는 질문**: "어떤 장르? 어떤 악기? 어떤 드럼? 어떤 보컬? 얼마나 빠르게? 어떤 키? 어떤 믹스?"

### 채널 B: 가사 브래킷 — "시간 순서대로 뭐가 들어오고 빠지는가"

가사 텍스트 안에 `[...]` 브래킷을 삽입하여 **시간축 레이어링**을 컨트롤:

| 브래킷 타입 | 역할 | 예시 |
|------------|------|------|
| **섹션 태그** | 곡 구간 선언 | `[Intro]`, `[Verse 1]`, `[Chorus]`, `[Bridge]` |
| **악기/어레인지먼트 큐** | 해당 구간의 악기 편성 지정 | `[fingerpicked acoustic guitar]`, `[full band arrangement]` |
| **보컬 지시** | 보컬 타입 전환 | `[breathy female vocals]`, `[male tenor vocals]` |
| **전환 큐** | 악기 진입/퇴장 타이밍 | `[kick drum enters]`, `[bass drops out]` |
| **이펙트 큐** | 순간적 프로세싱 | `[vocal harmony on '삭제']`, `[guitar feedback swell]` |

**가사 브래킷이 답하는 질문**: "Intro에서 뭐가 먼저 나와? Verse 1에서 보컬은? Chorus에서 뭐가 추가로 들어와?"

### 두 채널의 관계

```
SP:   "이 곡에는 clean electric guitar, sub-bass synth, crisp snare가 있다"
       → 전체 팔레트 선언 (무엇이 있는가)

가사:  [Intro] [arpeggiated clean electric guitar with chorus]
       [Verse 1] [breathy female vocals] 가사... [kick drum enters]
       [Chorus] [sub-bass synth enters, snare hits on 2 and 4]
       → 시간축 시퀀싱 (언제 들어오는가)
```

**SP = 팔레트 / 가사 브래킷 = 타임라인.** 둘이 합쳐져야 완전한 곡 기술.

---

## Part 2: 20곡 실제 템플릿

### [1/20] #0168 늦둥이 아빠 — Indie Rock

#### SP 원문
> K-Pop Punk with a high-energy pop-rock arrangement. Distorted electric guitars play driving eighth-note power chords and palm-muted riffs. The bass guitar follows the kick drum with a thick, overdriven tone. Drums feature a standard rock beat with heavy crash cymbal accents and rapid snare fills. Male vocals are delivered with a melodic, slightly strained punk-rock belt. The tempo is 165 BPM in the key of E Major. The production is polished with modern compression and bright EQ on the guitars.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop Punk with a high-energy pop-rock arrangement. |
| | *장르: K-Pop Punk with a high-energy pop-rock arrangement* |
| **악기 레이어** | Distorted electric guitars play driving eighth-note power chords and palm-muted riffs. |
| | *악기: Distorted electric guitars play driving eighth-note power chords and palm-muted riffs* |
| **드럼/퍼커션** | The bass guitar follows the kick drum with a thick, overdriven tone. |
| | *드럼: The bass guitar follows the kick drum with a thick, overdriven tone* |
| **드럼/퍼커션** | Drums feature a standard rock beat with heavy crash cymbal accents and rapid snare fills. |
| | *드럼: Drums feature a standard rock beat with heavy crash cymbal accents and rapid snare fills* |
| **보컬** | Male vocals are delivered with a melodic, slightly strained punk-rock belt. |
| | *보컬: Male vocals are delivered with a melodic, slightly strained punk-rock belt* |
| **템포/조성/박자** | The tempo is 165 BPM in the key of E Major. |
| | *템포 165 BPM, 조성 e major* |
| **프로덕션/믹스** | The production is polished with modern compression and bright EQ on the guitars. |
| | *프로덕션: The production is polished with modern compression and bright EQ on the guitars* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[distorted electric guitar riff, driving drums]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[palm-muted guitar]` ← 악기/어레인지먼트 큐
  _참지 않아도 돼 웃어야 했어 계속_
  _부장님 개그에도 손뼉을 쳐야 해_
  _맥주 세 잔 제 속이 타는 건 술이_
  _아니야 목구멍에 걸린 말 때문이야_
`[Chorus]` ← 섹션 태그
`[full band, open power chords]` ← 악기/어레인지먼트 큐
  _노래방 마이크를 잡아 노래 대신 말이 나와_
  _형진 씨 힘들었어요 이 한마디가 터져와_
  _마이크에서 열기가 올라와 가슴에서 불이 나_
  _참았던 게 다 쏟아져_
`[Bridge]` ← 섹션 태그
`[drums drop out, clean guitar arpeggio]` ← 섹션 태그
  _한 번은 치던 손이 멈추고 조용해져_
  _에코가 울려_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): drum, electric guitar, guitar
- **SP에만** (전체 톤, 진입 큐 없음): bass
- **가사에만** (SP 미언급, 가사에서 직접 큐): clean guitar

---

### [2/20] #0171 이명 — Indie Pop

#### SP 원문
> K-Pop rock track featuring a male tenor vocalist. The arrangement centers on a bright, overdriven electric guitar playing syncopated eighth-note power chords and a clean electric guitar playing arpeggiated figures. A picked electric bass follows the kick drum pattern. The drums feature a crisp snare and a steady eighth-note hi-hat pattern. A subtle digital synth pad provides harmonic filling in the background. The tempo is 128 BPM in the key of E Major.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop rock track featuring a male tenor vocalist. |
| | *장르: K-Pop rock track featuring a male tenor vocalist* |
| **어레인지먼트 총평** | The arrangement centers on a bright, overdriven electric guitar playing syncopated eighth-note power chords and a clean electric guitar playing arpeggiated figures. |
| | *편곡: The arrangement centers on a bright, overdriven electric guitar playing syncopated eighth-note power chords and a clean electric guitar playing arpeggiated figures* |
| **드럼/퍼커션** | A picked electric bass follows the kick drum pattern. |
| | *드럼: A picked electric bass follows the kick drum pattern* |
| **드럼/퍼커션** | The drums feature a crisp snare and a steady eighth-note hi-hat pattern. |
| | *드럼: The drums feature a crisp snare and a steady eighth-note hi-hat pattern* |
| **악기 레이어** | A subtle digital synth pad provides harmonic filling in the background. |
| | *악기: A subtle digital synth pad provides harmonic filling in the background* |
| **템포/조성/박자** | The tempo is 128 BPM in the key of E Major. |
| | *템포 128 BPM, 조성 e major* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[overdriven electric guitar power chords, steady drum beat]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[male tenor vocals]` ← 보컬 지시
`[clean arpeggiated guitar enters]` ← 전환 큐
  _에너지바_
  _할 수 있다_
  _세 글자를 적어_
  _손끝이 떨려_
  _글씨가 삐뚤해_
  _옆방 코 고는 밤_
  _새벽이 깊어져_
  _문제집 위에_
  _식은 커피 한 잔_
`[bass guitar slides up]` ← 악기/어레인지먼트 큐

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): drum, electric guitar
- **SP에만** (전체 톤, 진입 큐 없음): clean electric guitar, electric bass, pad, synth
- **가사에만** (SP 미언급, 가사에서 직접 큐): bass, guitar

---

### [3/20] #0185 레시피 — Indie Pop

#### SP 원문
> K-Pop Ballad. A grand piano plays a rubato introduction before settling into a steady 4/4 rhythm. A male baritone vocal performs with a breathy, intimate delivery in the lower register, transitioning to a powerful, resonant chest voice in the higher register. A lush string section provides legato counter-melodies and sustained harmonic pads. An acoustic guitar enters with light strumming. The arrangement features a prominent orchestral swell. Key of E Major. Tempo is 72 BPM.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop Ballad. |
| | *장르: K-Pop Ballad* |
| **악기 레이어** | A grand piano plays a rubato introduction before settling into a steady 4/4 rhythm. |
| | *악기: A grand piano plays a rubato introduction before settling into a steady 4/4 rhythm* |
| **보컬** | A male baritone vocal performs with a breathy, intimate delivery in the lower register, transitioning to a powerful, resonant chest voice in the higher register. |
| | *보컬: A male baritone vocal performs with a breathy, intimate delivery in the lower register, transitioning to a powerful, resonant chest voice in the higher register* |
| **악기 레이어** | A lush string section provides legato counter-melodies and sustained harmonic pads. |
| | *악기: A lush string section provides legato counter-melodies and sustained harmonic pads* |
| **악기 레이어** | An acoustic guitar enters with light strumming. |
| | *악기: An acoustic guitar enters with light strumming* |
| **어레인지먼트 총평** | The arrangement features a prominent orchestral swell. |
| | *편곡: The arrangement features a prominent orchestral swell* |
| **템포/조성/박자** | Key of E Major. |
| | *조성 e major* |
| **템포/조성/박자** | Tempo is 72 BPM. |
| | *템포 72 BPM* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[rubato grand piano arpeggios]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[breathy male vocals]` ← 보컬 지시
`[piano settles into 4/4 rhythm]` ← 악기/어레인지먼트 큐
  _무릎이 소리를 내_
  _처음 듣는 소리야_
  _아닌 척 걸었어_
`[strings enter with soft legato pads]` ← 전환 큐
  _몸이 무거워_
  _일요일 아침이 길어_
  _발끝이 시려_
  _아무도 안 봤으면_
`[Chorus]` ← 섹션 태그
`[vocal intensity increases, strings swell]` ← 보컬 지시
  _예전 같지 않아_
`[acoustic guitar enters with light strumming]` ← 전환 큐

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): acoustic guitar, pads, piano
- **가사에만** (SP 미언급, 가사에서 직접 큐): strings

---

### [4/20] #0204 할 일 목록 — Hip-Hop

#### SP 원문
> K-Indie Pop. Clean electric guitar plays a syncopated, jazzy four-chord progression with light chorus and reverb. A soft, dry kick drum hits on every beat while a shaker provides a steady sixteenth-note pulse. A melodic bass guitar line follows the chord roots with occasional chromatic passing tones. Female vocals are delivered in a breathy, intimate head voice with minimal vibrato. The arrangement maintains a sparse, lounge-like texture. Tempo is 88 BPM in the key of E Major.

#### SP → 7슬롯 분해

| **장르 선언** | K-Indie Pop. |
| | *장르: K-Indie Pop* |
| **악기 레이어** | Clean electric guitar plays a syncopated, jazzy four-chord progression with light chorus and reverb. |
| | *악기: Clean electric guitar plays a syncopated, jazzy four-chord progression with light chorus and reverb* |
| **드럼/퍼커션** | A soft, dry kick drum hits on every beat while a shaker provides a steady sixteenth-note pulse. |
| | *드럼: A soft, dry kick drum hits on every beat while a shaker provides a steady sixteenth-note pulse* |
| **악기 레이어** | A melodic bass guitar line follows the chord roots with occasional chromatic passing tones. |
| | *악기: A melodic bass guitar line follows the chord roots with occasional chromatic passing tones* |
| **보컬** | Female vocals are delivered in a breathy, intimate head voice with minimal vibrato. |
| | *보컬: Female vocals are delivered in a breathy, intimate head voice with minimal vibrato* |
| **어레인지먼트 총평** | The arrangement maintains a sparse, lounge-like texture. |
| | *편곡: The arrangement maintains a sparse, lounge-like texture* |
| **템포/조성/박자** | Tempo is 88 BPM in the key of E Major. |
| | *템포 88 BPM, 조성 e major* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[clean electric guitar with chorus, syncopated jazz chords]` ← 섹션 태그
`[soft kick drum on every beat, shaker enters]` ← 전환 큐
`[Verse 1]` ← 섹션 태그
`[breathy female vocals]` ← 보컬 지시
  _아홉 시 칠 분 늘 같은 자리에 앉아_
  _이어폰 끼우기 전에 한번 이쪽을 봐_
  _고개를 살짝 끄덕여 그게 전부야 이름은 몰라_
  _물병 뚜껑 소리 여기 딴 걸 알아_
  _어느 나라 맛소 빈자리가 넓어_
  _하얗게 넓어_
  _자판기 앞에서_
  _말을 걸 수 있었어 하지 않았어_
  _다음 날 미소가 하나 더 붙어 있어_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): clean electric guitar, drum
- **SP에만** (전체 톤, 진입 큐 없음): bass, guitar

---

### [5/20] #0917 옛날 일기 — Acoustic Pop

#### SP 원문
> K-Pop ballad featuring a male tenor vocal. The arrangement centers on a grand piano playing sustained chords and melodic fills. A subtle synth pad provides harmonic depth in the background. The vocal performance uses a mix of chest voice and light vibrato, with increased dynamic intensity in the higher register. The tempo is 72 BPM in 4/4 time. The production features a clean, polished mix with moderate hall reverb on the vocals and piano.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop ballad featuring a male tenor vocal. |
| | *장르: K-Pop ballad featuring a male tenor vocal* |
| **어레인지먼트 총평** | The arrangement centers on a grand piano playing sustained chords and melodic fills. |
| | *편곡: The arrangement centers on a grand piano playing sustained chords and melodic fills* |
| **악기 레이어** | A subtle synth pad provides harmonic depth in the background. |
| | *악기: A subtle synth pad provides harmonic depth in the background* |
| **프로덕션/믹스** | The vocal performance uses a mix of chest voice and light vibrato, with increased dynamic intensity in the higher register. |
| | *프로덕션: The vocal performance uses a mix of chest voice and light vibrato, with increased dynamic intensity in the higher register* |
| **템포/조성/박자** | The tempo is 72 BPM in 4/4 time. |
| | *템포 72 BPM, 박자 4/4* |
| **프로덕션/믹스** | The production features a clean, polished mix with moderate hall reverb on the vocals and piano. |
| | *프로덕션: The production features a clean, polished mix with moderate hall reverb on the vocals and piano* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[grand piano playing melodic chords, soft synth pad]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[male tenor vocals]` ← 보컬 지시
`[piano continues]` ← 악기/어레인지먼트 큐
  _축가를 듣는다_
  _옆자리가 비어 있는 게 오늘따라 유독_
  _크게 느껴져_
`[Verse 2]` ← 섹션 태그
  _부케 토스 뒤로 물러서는 내가 쓸쓸하게 웃어_
  _친구의 행복 앞에서 내 외로움이 선명해_
`[Chorus]` ← 섹션 태그
  _축하하면서도 가슴 한쪽이 시리게 아려와_
  _비로연 속 커플들 사이에 혼자 앉아_
  _잔을 부딪칠 사람이 없는 테이블이 넓게 느껴져_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): pad, piano, synth

---

### [6/20] #0922 눈빛의 언어 — Korean Ballad

#### SP 원문
> K-Pop ballad with acoustic pop elements. A clean, fingerpicked acoustic guitar plays a steady eighth-note pattern. A warm, melodic electric bass enters to support the low end. Mid-tempo 4/4 time at 84 BPM in the key of E Major. Male vocals are delivered in a soft, breathy tenor register, transitioning into a more resonant chest voice during the chorus. Subtle percussion includes a soft kick drum and light shaker. The arrangement features a clean electric guitar playing melodic fills between vocal phrases.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop ballad with acoustic pop elements. |
| | *장르: K-Pop ballad with acoustic pop elements* |
| **악기 레이어** | A clean, fingerpicked acoustic guitar plays a steady eighth-note pattern. |
| | *악기: A clean, fingerpicked acoustic guitar plays a steady eighth-note pattern* |
| **악기 레이어** | A warm, melodic electric bass enters to support the low end. |
| | *악기: A warm, melodic electric bass enters to support the low end* |
| **템포/조성/박자** | Mid-tempo 4/4 time at 84 BPM in the key of E Major. |
| | *템포 84 BPM, 조성 e major, 박자 4/4* |
| **보컬** | Male vocals are delivered in a soft, breathy tenor register, transitioning into a more resonant chest voice during the chorus. |
| | *보컬: Male vocals are delivered in a soft, breathy tenor register, transitioning into a more resonant chest voice during the chorus* |
| **드럼/퍼커션** | Subtle percussion includes a soft kick drum and light shaker. |
| | *드럼: Subtle percussion includes a soft kick drum and light shaker* |
| **어레인지먼트 총평** | The arrangement features a clean electric guitar playing melodic fills between vocal phrases. |
| | *편곡: The arrangement features a clean electric guitar playing melodic fills between vocal phrases* |

#### 가사 브래킷 시퀀스

`[Verse 1]` ← 섹션 태그
`[fingerpicked acoustic guitar]` ← 악기/어레인지먼트 큐
  _낡은 일기장을 열면 그때의 내가 살아나_
  _서툴렀던 글씨 속에 순수한 사랑이 있었어_
`[bass enters, soft kick drum]` ← 전환 큐
  _이사 짐 정리하다 서랍 깊숙이서 찾은 일기장_
  _먼지를 불어내고 첫 페이지를 펼치면 네 이야기_
`[Verse 2]` ← 섹션 태그
  _하트 스티커가 붙은 날이 너를 처음 만난 날이야_
  _그때의 나는 모든 게 처음이라서 떨렸어_
  _첫 키스를 한 날 세 페이지나 쓴 내가 웃겨_
`[Chorus]` ← 섹션 태그
`[fuller arrangement, light percussion]` ← 악기/어레인지먼트 큐
  _옛날 일기를 읽으며 웃고 또 울어_
  _그때의 사랑이 지금의 나를 만들어줬어_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): drum, fingerpicked acoustic guitar
- **SP에만** (전체 톤, 진입 큐 없음): clean electric guitar, electric bass
- **가사에만** (SP 미언급, 가사에서 직접 큐): bass

---

### [7/20] #0928 서사 없는 사랑 — Synth Pop

#### SP 원문
> K-Pop ballad featuring a baritone male vocal. The arrangement centers on a grand piano playing sustained chords and melodic fills. A fretless bass enters with melodic slides, while a clean electric guitar provides subtle arpeggiated textures. The percussion consists of a soft kick drum and a crisp snare with moderate reverb. Orchestral string pads provide harmonic support in the background. The tempo is 72 BPM in 4/4 time, in the key of C Major.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop ballad featuring a baritone male vocal. |
| | *장르: K-Pop ballad featuring a baritone male vocal* |
| **어레인지먼트 총평** | The arrangement centers on a grand piano playing sustained chords and melodic fills. |
| | *편곡: The arrangement centers on a grand piano playing sustained chords and melodic fills* |
| **악기 레이어** | A fretless bass enters with melodic slides, while a clean electric guitar provides subtle arpeggiated textures. |
| | *악기: A fretless bass enters with melodic slides, while a clean electric guitar provides subtle arpeggiated textures* |
| **드럼/퍼커션** | The percussion consists of a soft kick drum and a crisp snare with moderate reverb. |
| | *드럼: The percussion consists of a soft kick drum and a crisp snare with moderate reverb* |
| **악기 레이어** | Orchestral string pads provide harmonic support in the background. |
| | *악기: Orchestral string pads provide harmonic support in the background* |
| **템포/조성/박자** | The tempo is 72 BPM in 4/4 time, in the key of C Major. |
| | *템포 72 BPM, 조성 c major, 박자 4/4* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[grand piano, soft kick drum]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[baritone male vocals]` ← 보컬 지시
`[fretless bass enters with slide]` ← 전환 큐
`[clean electric guitar arpeggios]` ← 악기/어레인지먼트 큐
  _식당에서 마주 앉아 메뉴판을 볼 때_
`[snare enters with reverb]` ← 전환 큐
  _입꼬리가 올라가면 그건 디저트가 먹고 싶다는 뜻_
  _오래 함께한 시간이 만들어준 언어_
  _세상에서 둘만 아는 침묵의 대화_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): bass, clean electric guitar, drum, piano
- **SP에만** (전체 톤, 진입 큐 없음): pads

---

### [8/20] #0936 침묵의 대화 — Folk

#### SP 원문
> K-Pop, J-Pop, Funk Pop. Bright, clean electric guitar plays syncopated funk rhythms with occasional 16th-note scratches. A slap bass guitar follows the kick drum with active, melodic fills. Acoustic piano provides rhythmic chord stabs. Electronic drums feature a crisp snare and a tight, punchy kick. Male vocals perform in a melodic, rhythmic style with frequent use of falsetto in the higher register. The arrangement includes layered vocal harmonies during the chorus. Key of E Major. Tempo is 118 BPM.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop, J-Pop, Funk Pop. |
| | *장르: K-Pop, J-Pop, Funk Pop* |
| **악기 레이어** | Bright, clean electric guitar plays syncopated funk rhythms with occasional 16th-note scratches. |
| | *악기: Bright, clean electric guitar plays syncopated funk rhythms with occasional 16th-note scratches* |
| **드럼/퍼커션** | A slap bass guitar follows the kick drum with active, melodic fills. |
| | *드럼: A slap bass guitar follows the kick drum with active, melodic fills* |
| **악기 레이어** | Acoustic piano provides rhythmic chord stabs. |
| | *악기: Acoustic piano provides rhythmic chord stabs* |
| **드럼/퍼커션** | Electronic drums feature a crisp snare and a tight, punchy kick. |
| | *드럼: Electronic drums feature a crisp snare and a tight, punchy kick* |
| **보컬** | Male vocals perform in a melodic, rhythmic style with frequent use of falsetto in the higher register. |
| | *보컬: Male vocals perform in a melodic, rhythmic style with frequent use of falsetto in the higher register* |
| **어레인지먼트 총평** | The arrangement includes layered vocal harmonies during the chorus. |
| | *편곡: The arrangement includes layered vocal harmonies during the chorus* |
| **템포/조성/박자** | Key of E Major. |
| | *조성 e major* |
| **템포/조성/박자** | Tempo is 118 BPM. |
| | *템포 118 BPM* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[clean funk electric guitar, slap bass, electronic drums]` ← 악기/어레인지먼트 큐
`[vocalizing]` ← 보컬 지시
`[Verse 1]` ← 섹션 태그
`[male vocals, piano stabs enter]` ← 보컬 지시
  _잊혀지기 전에 우리는 가장 좋은 친구_
`[bass fill]` ← 악기/어레인지먼트 큐
  _네가 이기면 좋아하는 표정이 보고 싶었을 뿐이야_
  _진지한 사랑만큼 함께 노는 시간도 소중해_
`[Verse 2]` ← 섹션 태그
`[snare roll]` ← 악기/어레인지먼트 큐
  _바닥에 나뒹굴며 웃다가 서로를 바라봤어_
  _이렇게 바보처럼 웃을 수 있는 사이가 최고야_
`[Chorus]` ← 섹션 태그
`[full band, layered vocal harmonies]` ← 보컬 지시
  _함께 노는 게 사랑의 가장 순수한 모습이야_
  _어른이 되어서도 아이처럼 웃을 수 있는 사이_
`[falsetto ad-lib]` ← 보컬 지시

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): drum, slap bass
- **SP에만** (전체 톤, 진입 큐 없음): acoustic piano, clean electric guitar, guitar
- **가사에만** (SP 미언급, 가사에서 직접 큐): bass, electric guitar, piano

---

### [9/20] #0945 어머니의 손길로 — City Pop

#### SP 원문
> K-Pop ballad featuring a male baritone vocal. The arrangement centers on a fingerpicked acoustic guitar playing a steady eighth-note pattern with occasional hammer-ons. A warm, melodic electric bass enters to provide counterpoint to the vocal melody. The tempo is 72 BPM in 4/4 time. The vocal delivery is intimate and breathy, utilizing a narrow dynamic range and subtle vibrato. The production is clean with light plate reverb on the vocals and guitar.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop ballad featuring a male baritone vocal. |
| | *장르: K-Pop ballad featuring a male baritone vocal* |
| **어레인지먼트 총평** | The arrangement centers on a fingerpicked acoustic guitar playing a steady eighth-note pattern with occasional hammer-ons. |
| | *편곡: The arrangement centers on a fingerpicked acoustic guitar playing a steady eighth-note pattern with occasional hammer-ons* |
| **보컬** | A warm, melodic electric bass enters to provide counterpoint to the vocal melody. |
| | *보컬: A warm, melodic electric bass enters to provide counterpoint to the vocal melody* |
| **템포/조성/박자** | The tempo is 72 BPM in 4/4 time. |
| | *템포 72 BPM, 박자 4/4* |
| **보컬** | The vocal delivery is intimate and breathy, utilizing a narrow dynamic range and subtle vibrato. |
| | *보컬: The vocal delivery is intimate and breathy, utilizing a narrow dynamic range and subtle vibrato* |
| **프로덕션/믹스** | The production is clean with light plate reverb on the vocals and guitar. |
| | *프로덕션: The production is clean with light plate reverb on the vocals and guitar* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[fingerpicked acoustic guitar]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[male baritone vocals enter]` ← 보컬 지시
  _말하지 않아도 되는 순간이_
  _있다는 걸_
`[electric bass enters]` ← 전환 큐
  _마음이 무거운 날 소파에 나란히 앉아_
  _아무 말 없이 찻잔을 건네는 것으로 충분해_
  _위로의 말보다 침묵이 더 깊이 닿는_
  _순간이 있어_
`[Verse 2]` ← 섹션 태그
  _장례식에서 돌아온 날_
  _네가 아무 말 하지 않았어_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): electric bass, fingerpicked acoustic guitar
- **SP에만** (전체 톤, 진입 큐 없음): guitar

---

### [10/20] #0967 블랙 카페 — Electro Pop

#### SP 원문
> K-Pop ballad featuring a male tenor vocal. The arrangement centers on a solo cello playing a melodic counterpoint and a fingerpicked acoustic guitar. A grand piano enters with sustained chords and melodic fills. The vocal performance uses a mix of chest voice and light vibrato. The tempo is 72 BPM in 4/4 time. The production features high-fidelity clarity with moderate hall reverb on the strings and vocals.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop ballad featuring a male tenor vocal. |
| | *장르: K-Pop ballad featuring a male tenor vocal* |
| **어레인지먼트 총평** | The arrangement centers on a solo cello playing a melodic counterpoint and a fingerpicked acoustic guitar. |
| | *편곡: The arrangement centers on a solo cello playing a melodic counterpoint and a fingerpicked acoustic guitar* |
| **악기 레이어** | A grand piano enters with sustained chords and melodic fills. |
| | *악기: A grand piano enters with sustained chords and melodic fills* |
| **프로덕션/믹스** | The vocal performance uses a mix of chest voice and light vibrato. |
| | *프로덕션: The vocal performance uses a mix of chest voice and light vibrato* |
| **템포/조성/박자** | The tempo is 72 BPM in 4/4 time. |
| | *템포 72 BPM, 박자 4/4* |
| **프로덕션/믹스** | The production features high-fidelity clarity with moderate hall reverb on the strings and vocals. |
| | *프로덕션: The production features high-fidelity clarity with moderate hall reverb on the strings and vocals* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[fingerpicked acoustic guitar, solo cello melody]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[male tenor vocals]` ← 보컬 지시
  _죽음 앞에서도 손을 놓지 않겠다고 맹세해_
  _이 약속이 우리 사랑의 가장 깊은 뿌리_
`[piano enters with soft chords]` ← 전환 큐
  _병원 복도를 함께 걸으며 생각했어_
  _이 사람의 마지막 순간에도 내가 옆에 있을 거라고_
`[Chorus]` ← 섹션 태그
  _그 각오가 두렵지 않은 건 사랑이 두려움보다 크니까_
`[cello plays sustained low notes]` ← 악기/어레인지먼트 큐
  _서약서에 쓴 건강할 때나 아플 때나_
`[piano melodic fill]` ← 악기/어레인지먼트 큐

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): fingerpicked acoustic guitar, piano
- **SP에만** (전체 톤, 진입 큐 없음): strings

---

### [11/20] #0973 빨간불의 시간 — City Pop

#### SP 원문
> K-Pop Indie Pop. Clean electric guitar plays a syncopated, palm-muted rhythmic pattern alongside a steady mid-tempo drum kit featuring a tight snare and crisp hi-hats. A melodic bass guitar follows the root notes of the guitar progression. Male vocals are delivered in a smooth, breathy tenor with light doubling and subtle reverb. The arrangement features atmospheric synth pads and occasional vocal harmonies. Tempo is 92 BPM in the key of E Major.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop Indie Pop. |
| | *장르: K-Pop Indie Pop* |
| **드럼/퍼커션** | Clean electric guitar plays a syncopated, palm-muted rhythmic pattern alongside a steady mid-tempo drum kit featuring a tight snare and crisp hi-hats. |
| | *드럼: Clean electric guitar plays a syncopated, palm-muted rhythmic pattern alongside a steady mid-tempo drum kit featuring a tight snare and crisp hi-hats* |
| **악기 레이어** | A melodic bass guitar follows the root notes of the guitar progression. |
| | *악기: A melodic bass guitar follows the root notes of the guitar progression* |
| **보컬** | Male vocals are delivered in a smooth, breathy tenor with light doubling and subtle reverb. |
| | *보컬: Male vocals are delivered in a smooth, breathy tenor with light doubling and subtle reverb* |
| **어레인지먼트 총평** | The arrangement features atmospheric synth pads and occasional vocal harmonies. |
| | *편곡: The arrangement features atmospheric synth pads and occasional vocal harmonies* |
| **템포/조성/박자** | Tempo is 92 BPM in the key of E Major. |
| | *템포 92 BPM, 조성 e major* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[clean electric guitar rhythmic pattern, soft synth pads]` ← 악기/어레인지먼트 큐
  _(Hoo-ooh-ooh)_
`[Verse 1]` ← 섹션 태그
`[breathy male vocals]` ← 보컬 지시
`[bass guitar enters]` ← 전환 큐
  _유리에 비친 네 모습이 두 개야 안쪽의 너와 바깥 세상이 반투명하게 포개져_
`[vocal harmonies enter]` ← 보컬 지시
`[snare hit]` ← 악기/어레인지먼트 큐
  _유리창_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): bass, clean electric guitar, guitar, pads, synth
- **SP에만** (전체 톤, 진입 큐 없음): drum

---

### [12/20] #1022 프사 바꾸는 밤 — R&B

#### SP 원문
> K-Pop ballad featuring a male tenor vocalist. The arrangement centers on a grand piano playing sustained chords and melodic fills. A clean electric guitar provides palm-muted rhythmic accents in the verses and arpeggiated textures in the chorus. The bass guitar follows the kick drum with a legato, melodic approach. Drums consist of a standard kit with a crisp snare and prominent crash cymbals during transitions. The tempo is 72 BPM in the key of E Major. The vocal performance uses a mix of chest voice and breathy head voice with light vibrato. Production features include hall reverb on the vocals and piano.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop ballad featuring a male tenor vocalist. |
| | *장르: K-Pop ballad featuring a male tenor vocalist* |
| **어레인지먼트 총평** | The arrangement centers on a grand piano playing sustained chords and melodic fills. |
| | *편곡: The arrangement centers on a grand piano playing sustained chords and melodic fills* |
| **악기 레이어** | A clean electric guitar provides palm-muted rhythmic accents in the verses and arpeggiated textures in the chorus. |
| | *악기: A clean electric guitar provides palm-muted rhythmic accents in the verses and arpeggiated textures in the chorus* |
| **드럼/퍼커션** | The bass guitar follows the kick drum with a legato, melodic approach. |
| | *드럼: The bass guitar follows the kick drum with a legato, melodic approach* |
| **드럼/퍼커션** | Drums consist of a standard kit with a crisp snare and prominent crash cymbals during transitions. |
| | *드럼: Drums consist of a standard kit with a crisp snare and prominent crash cymbals during transitions* |
| **템포/조성/박자** | The tempo is 72 BPM in the key of E Major. |
| | *템포 72 BPM, 조성 e major* |
| **프로덕션/믹스** | The vocal performance uses a mix of chest voice and breathy head voice with light vibrato. |
| | *프로덕션: The vocal performance uses a mix of chest voice and breathy head voice with light vibrato* |
| **프로덕션/믹스** | Production features include hall reverb on the vocals and piano. |
| | *프로덕션: Production features include hall reverb on the vocals and piano* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[sustained piano chords, light reverb]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[male tenor vocals, breathy delivery]` ← 보컬 지시
  _열다섯엔 나는 확신했어 스무 살이 되면_
`[clean electric guitar enters with palm-muted notes]` ← 전환 큐
  _서른이 되면 대답할 수 있을 거라고_
  _마흔이면 흔들리지 않을 거라고_
`[Verse 2]` ← 섹션 태그
`[bass guitar enters, legato phrasing]` ← 보컬 지시
  _지금 나이를 세어보면 그때 상상한_
`[kick drum enters]` ← 전환 큐
  _거울 속엔 여전히 질문만_
  _가득한 내가 서 있어_
`[Chorus]` ← 섹션 태그
`[full band enters, driving drum beat]` ← 전환 큐
  _어른이 되면 알 줄 알았어 사랑이 뭔지 인생이 뭔지_
`[crash cymbal]` ← 악기/어레인지먼트 큐

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): bass, clean electric guitar, drum, guitar, piano

---

### [13/20] #1032 숨은 시옷 찾기 — Disco Pop

#### SP 원문
> K-Pop educational pop track. Features bright, layered synthesizers, a punchy electronic kick drum, and a crisp snare. The bassline is a clean, melodic synth bass that follows the vocal melody closely. Male vocals are processed with light pitch correction and doubling. The arrangement includes rapid synth arpeggios and percussive accents. Key of G Major, 128 BPM.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop educational pop track. |
| | *장르: K-Pop educational pop track* |
| **드럼/퍼커션** | Features bright, layered synthesizers, a punchy electronic kick drum, and a crisp snare. |
| | *드럼: Features bright, layered synthesizers, a punchy electronic kick drum, and a crisp snare* |
| **보컬** | The bassline is a clean, melodic synth bass that follows the vocal melody closely. |
| | *보컬: The bassline is a clean, melodic synth bass that follows the vocal melody closely* |
| **프로덕션/믹스** | Male vocals are processed with light pitch correction and doubling. |
| | *프로덕션: Male vocals are processed with light pitch correction and doubling* |
| **어레인지먼트 총평** | The arrangement includes rapid synth arpeggios and percussive accents. |
| | *편곡: The arrangement includes rapid synth arpeggios and percussive accents* |
| **템포/조성/박자** | Key of G Major, 128 BPM. |
| | *템포 128 BPM, 조성 g major* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[bright synth melody, electronic drums]` ← 악기/어레인지먼트 큐
  _발음이 달라 달라 달라_
`[Chorus]` ← 섹션 태그
`[driving synth bass]` ← 악기/어레인지먼트 큐
  _발음이 달라 달라 달라_
  _선생님은 읽혀 달라_
  _아침이 너무 가며 소리가 바뀌어_
  _발음이 달라 달라 달라_
`[synth arpeggio]` ← 악기/어레인지먼트 큐
  _Yeah yeah yeah_
`[Verse 1]` ← 섹션 태그
`[percussive synth stabs]` ← 악기/어레인지먼트 큐
  _국물 시켜 배달해_
  _마치 미드 넘어가 자연스럽게_
  _학교 가는 길_
  _읽다가 멈추면 읽다 경험하라고 불러 매직_
  _약속했잖아 약속 맛있다 한 입_
  _글자는 그대로인데 소리가 달라져_
`[Pre-Chorus]` ← 섹션 태그
`[synth pads swell]` ← 전환 큐
  _왜 선대로 읽히냐고_
  _한국어가 원래 그래_
  _받침이 뒤를 만나면_
  _새로운 소리가 돼_
`[Chorus]` ← 섹션 태그
`[full electronic production]` ← 악기/어레인지먼트 큐
  _발음이 달라 달라 소리가 변해_
  _국물은 굿물 학교는 학굔_
  _알면 더 자연스러워지는 걸_
  _달라 달라 근데 다 규칙_
  _발음이 달라 달라 달라_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): bass, drum, synth
- **가사에만** (SP 미언급, 가사에서 직접 큐): pads

---

### [14/20] #1167 박스 제일 밑에서 — Acoustic Ballad

#### SP 원문
> K-Pop ballad with synth-pop elements. Female vocals in a mid-to-high range with light breathiness. Clean electric guitar plays a syncopated, palm-muted rhythmic pattern. A sub-bass synth provides low-end weight with sustained notes. Percussion consists of a crisp electronic snare on the backbeat and a tight, dry kick drum. Atmospheric synth pads provide harmonic texture in the background. Key of E Major, 105 BPM.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop ballad with synth-pop elements. |
| | *장르: K-Pop ballad with synth-pop elements* |
| **보컬** | Female vocals in a mid-to-high range with light breathiness. |
| | *보컬: Female vocals in a mid-to-high range with light breathiness* |
| **악기 레이어** | Clean electric guitar plays a syncopated, palm-muted rhythmic pattern. |
| | *악기: Clean electric guitar plays a syncopated, palm-muted rhythmic pattern* |
| **악기 레이어** | A sub-bass synth provides low-end weight with sustained notes. |
| | *악기: A sub-bass synth provides low-end weight with sustained notes* |
| **드럼/퍼커션** | Percussion consists of a crisp electronic snare on the backbeat and a tight, dry kick drum. |
| | *드럼: Percussion consists of a crisp electronic snare on the backbeat and a tight, dry kick drum* |
| **악기 레이어** | Atmospheric synth pads provide harmonic texture in the background. |
| | *악기: Atmospheric synth pads provide harmonic texture in the background* |
| **템포/조성/박자** | Key of E Major, 105 BPM. |
| | *템포 105 BPM, 조성 e major* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[clean electric guitar with palm muting, atmospheric synth pads]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[female vocals enter]` ← 보컬 지시
  _세상이 비어 있는 시간_
  _아무도 부르지 않았는데_
`[electronic snare and kick enter]` ← 전환 큐
  _빨간 불이 기다리라고 했는데_
  _나는 이미 달리고 있었어_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): clean electric guitar, pads, synth
- **SP에만** (전체 톤, 진입 큐 없음): bass, drum

---

### [15/20] #1175 별점 2.3 — Lo-fi Pop

#### SP 원문
> K-pop ballad featuring a female vocalist. The arrangement centers on a fingerpicked acoustic guitar playing arpeggiated patterns. A subtle bass guitar enters during the first verse, providing melodic counterpoint. The tempo is 72 BPM in 4/4 time, likely in the key of G Major. The female vocals are delivered in a soft, breathy, and intimate style with minimal processing, emphasizing natural vibrato and clear diction. The production is sparse and organic, focusing on the interplay between the vocal melody and the acoustic guitar's resonance.

#### SP → 7슬롯 분해

| **장르 선언** | K-pop ballad featuring a female vocalist. |
| | *장르: K-pop ballad featuring a female vocalist* |
| **어레인지먼트 총평** | The arrangement centers on a fingerpicked acoustic guitar playing arpeggiated patterns. |
| | *편곡: The arrangement centers on a fingerpicked acoustic guitar playing arpeggiated patterns* |
| **악기 레이어** | A subtle bass guitar enters during the first verse, providing melodic counterpoint. |
| | *악기: A subtle bass guitar enters during the first verse, providing melodic counterpoint* |
| **템포/조성/박자** | The tempo is 72 BPM in 4/4 time, likely in the key of G Major. |
| | *템포 72 BPM, 조성 g major, 박자 4/4* |
| **보컬** | The female vocals are delivered in a soft, breathy, and intimate style with minimal processing, emphasizing natural vibrato and clear diction. |
| | *보컬: The female vocals are delivered in a soft, breathy, and intimate style with minimal processing, emphasizing natural vibrato and clear diction* |
| **어레인지먼트 총평** | The production is sparse and organic, focusing on the interplay between the vocal melody and the acoustic guitar's resonance. |
| | *편곡: The production is sparse and organic, focusing on the interplay between the vocal melody and the acoustic guitar's resonance* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[fingerpicked acoustic guitar arpeggio]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[soft female vocals]` ← 보컬 지시
  _마지막 박스테이프를 봉하려다_
`[bass guitar enters]` ← 전환 큐
  _꺼내 보니 스무 살의 내 얼굴_
  _낯선 것도 아닌데 익숙한 것도 아닌_
  _오래된 앨범지 냄새가 번졌지_
  _이삿짐 다 싸놓은 텅 빈 방_
  _마루에 주저앉아 한참을 보았거든_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): bass, fingerpicked acoustic guitar, guitar
- **SP에만** (전체 톤, 진입 큐 없음): acoustic guitar, organ

---

### [16/20] #1232 10년 만에 — Indie Folk

#### SP 원문
> K-Pop ballad. A clean, resonant grand piano plays sustained chords and melodic fills. A warm, rounded electric bass enters with subtle slides. The male lead vocal is breathy and intimate, utilizing a mix of chest voice and light falsetto. A soft, synthesized pad provides a subtle harmonic wash in the background. The tempo is 72 BPM in 4/4 time. The arrangement is sparse, focusing on the vocal performance and piano resonance.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop ballad. |
| | *장르: K-Pop ballad* |
| **악기 레이어** | A clean, resonant grand piano plays sustained chords and melodic fills. |
| | *악기: A clean, resonant grand piano plays sustained chords and melodic fills* |
| **악기 레이어** | A warm, rounded electric bass enters with subtle slides. |
| | *악기: A warm, rounded electric bass enters with subtle slides* |
| **프로덕션/믹스** | The male lead vocal is breathy and intimate, utilizing a mix of chest voice and light falsetto. |
| | *프로덕션: The male lead vocal is breathy and intimate, utilizing a mix of chest voice and light falsetto* |
| **악기 레이어** | A soft, synthesized pad provides a subtle harmonic wash in the background. |
| | *악기: A soft, synthesized pad provides a subtle harmonic wash in the background* |
| **템포/조성/박자** | The tempo is 72 BPM in 4/4 time. |
| | *템포 72 BPM, 박자 4/4* |
| **어레인지먼트 총평** | The arrangement is sparse, focusing on the vocal performance and piano resonance. |
| | *편곡: The arrangement is sparse, focusing on the vocal performance and piano resonance* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[sustained grand piano chords]` ← 악기/어레인지먼트 큐
  _(Hmm-mm)_
`[Verse 1]` ← 섹션 태그
`[breathy male vocals]` ← 보컬 지시
`[piano melodic fill]` ← 악기/어레인지먼트 큐
  _생각했어_
  _마지막으로 본 게 언제야 6개월 됐어_
  _연락할까 생각해 봤어 뭐라고 쓰지_
  _그냥 잘 지내냐고 하면 되는데_
  _그게 안 돼_
`[Chorus]` ← 섹션 태그
`[electric bass enters with soft slides]` ← 전환 큐
  _잘 지내냐고 쓰면 잘 지내라는 답 올 거야_
  _그러면 어떡하지 그다음 뭐라고 해 또 어색해질 것 같아_
  _그래서_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): electric bass, piano
- **SP에만** (전체 톤, 진입 큐 없음): pad, synth

---

### [17/20] #1426 축의금 계산기 — Funk Pop

#### SP 원문
> K-Indie pop with a lo-fi aesthetic. Clean electric guitar plays a syncopated, jazzy chord progression with light chorus and reverb. A sub-heavy synth bass follows the kick drum pattern. Drums consist of a dry, tight snare and a muted kick drum in a steady 4/4 backbeat. Male vocals are delivered in a soft, breathy tenor with subtle double-tracking during the chorus. A Rhodes-style electric piano provides sustained harmonic pads in the background. The tempo is 85 BPM in the key of E Major.

#### SP → 7슬롯 분해

| **장르 선언** | K-Indie pop with a lo-fi aesthetic. |
| | *장르: K-Indie pop with a lo-fi aesthetic* |
| **악기 레이어** | Clean electric guitar plays a syncopated, jazzy chord progression with light chorus and reverb. |
| | *악기: Clean electric guitar plays a syncopated, jazzy chord progression with light chorus and reverb* |
| **드럼/퍼커션** | A sub-heavy synth bass follows the kick drum pattern. |
| | *드럼: A sub-heavy synth bass follows the kick drum pattern* |
| **드럼/퍼커션** | Drums consist of a dry, tight snare and a muted kick drum in a steady 4/4 backbeat. |
| | *드럼: Drums consist of a dry, tight snare and a muted kick drum in a steady 4/4 backbeat* |
| **보컬** | Male vocals are delivered in a soft, breathy tenor with subtle double-tracking during the chorus. |
| | *보컬: Male vocals are delivered in a soft, breathy tenor with subtle double-tracking during the chorus* |
| **악기 레이어** | A Rhodes-style electric piano provides sustained harmonic pads in the background. |
| | *악기: A Rhodes-style electric piano provides sustained harmonic pads in the background* |
| **템포/조성/박자** | The tempo is 85 BPM in the key of E Major. |
| | *템포 85 BPM, 조성 e major* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[clean electric guitar with chorus, soft synth bass]` ← 섹션 태그
`[Verse 1]` ← 섹션 태그
`[breathy male vocals]` ← 보컬 지시
  _이어폰에선 니가 들려와_
  _덜컹덜컹 레일 위를 달리는_
  _창밖에 뭐가 있는지 모르겠는데 어둠이 빠르게 지나가_
`[electric piano pads enter]` ← 전환 큐
  _내 얼굴이 갑자기 나와서 놀랐어_
  _그 얼굴 좀 피곤해 보여_
  _빈 커피 컵같이 떨려_
  _아무도 안 보는 밤이라 괜찮았어_
  _옆자리 비어 있는 게 오히려 좋았거든_
`[Chorus]` ← 섹션 태그
  _이 소리가 자장가였어_
  _몰랐어 이렇게 편한 건지_
  _덜컹거림이 멈추면 안 돼 아직도 착하고 싶지 않았어_
  _한 정거장만 더 가자_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): bass, clean electric guitar, electric piano, pads, synth
- **SP에만** (전체 톤, 진입 큐 없음): drum, rhodes

---

### [18/20] #1553 폐관 오 분 전 — Jazz Pop

#### SP 원문
> K-Indie pop with bossa nova influences. The arrangement features a nylon-string acoustic guitar playing syncopated jazz chords and a walking upright bass. A clean electric guitar provides melodic counterpoint with light chorus and reverb. Percussion consists of a shaker, a soft woodblock, and a drum kit played with brushes, emphasizing a swung eighth-note feel. The female vocals are delivered in a breathy, intimate head voice with minimal vibrato. The track is in the key of E Major at 105 BPM in 4/4 time. The production is dry and transparent, focusing on the natural timbre of the acoustic instruments.

#### SP → 7슬롯 분해

| **장르 선언** | K-Indie pop with bossa nova influences. |
| | *장르: K-Indie pop with bossa nova influences* |
| **어레인지먼트 총평** | The arrangement features a nylon-string acoustic guitar playing syncopated jazz chords and a walking upright bass. |
| | *편곡: The arrangement features a nylon-string acoustic guitar playing syncopated jazz chords and a walking upright bass* |
| **악기 레이어** | A clean electric guitar provides melodic counterpoint with light chorus and reverb. |
| | *악기: A clean electric guitar provides melodic counterpoint with light chorus and reverb* |
| **드럼/퍼커션** | Percussion consists of a shaker, a soft woodblock, and a drum kit played with brushes, emphasizing a swung eighth-note feel. |
| | *드럼: Percussion consists of a shaker, a soft woodblock, and a drum kit played with brushes, emphasizing a swung eighth-note feel* |
| **보컬** | The female vocals are delivered in a breathy, intimate head voice with minimal vibrato. |
| | *보컬: The female vocals are delivered in a breathy, intimate head voice with minimal vibrato* |
| **템포/조성/박자** | The track is in the key of E Major at 105 BPM in 4/4 time. |
| | *템포 105 BPM, 조성 e major, 박자 4/4* |
| **어레인지먼트 총평** | The production is dry and transparent, focusing on the natural timbre of the acoustic instruments. |
| | *편곡: The production is dry and transparent, focusing on the natural timbre of the acoustic instruments* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[nylon-string acoustic guitar, shaker, woodblock]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[breathy female vocals]` ← 보컬 지시
  _Te-te-re-te-te-re-te_
  _Te-te-re-te-te-re-te_
  _Te-te-re-te-te-re-te_
  _Te-te-re-te-te-re-te_
`[upright bass enters]` ← 전환 큐
  _Jomyeongi hanassi kkeojinda_
  _Dasotsi osibun_
`[clean electric guitar enters with melodic fills]` ← 전환 큐
  _Geurimsok nundongjaga gipeojineun geon eodum ttaemmaneun ani..._
  _Namu badage ullineun balsori gyeongbiwoni gakkai onda_
  _Kaenbeoseu apeseo itda_
  _Hanggeoreumdo tteulsuga eopda_
`[Chorus]` ← 섹션 태그
  _Nareul bogo isseo geu geurimi nareul bogo isseo hambaljjakdo..._

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): acoustic guitar, clean electric guitar, upright bass
- **SP에만** (전체 톤, 진입 큐 없음): drum

---

### [19/20] #1662 연기와 구름 사이 — Electronic

#### SP 원문
> K-Pop acoustic ballad. A nylon-string acoustic guitar plays a fingerstyle pattern with steady eighth-note movement and occasional hammer-ons. A soft, breathy female vocal performs a melodic line with gentle vibrato and intimate proximity. The arrangement is minimalist, focusing on the interplay between the vocal and the guitar. Key of G Major. Tempo is 84 BPM. Time signature is 4/4.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop acoustic ballad. |
| | *장르: K-Pop acoustic ballad* |
| **악기 레이어** | A nylon-string acoustic guitar plays a fingerstyle pattern with steady eighth-note movement and occasional hammer-ons. |
| | *악기: A nylon-string acoustic guitar plays a fingerstyle pattern with steady eighth-note movement and occasional hammer-ons* |
| **보컬** | A soft, breathy female vocal performs a melodic line with gentle vibrato and intimate proximity. |
| | *보컬: A soft, breathy female vocal performs a melodic line with gentle vibrato and intimate proximity* |
| **어레인지먼트 총평** | The arrangement is minimalist, focusing on the interplay between the vocal and the guitar. |
| | *편곡: The arrangement is minimalist, focusing on the interplay between the vocal and the guitar* |
| **템포/조성/박자** | Key of G Major. |
| | *조성 g major* |
| **템포/조성/박자** | Tempo is 84 BPM. |
| | *템포 84 BPM* |
| **템포/조성/박자** | Time signature is 4/4. |
| | *Time signature is 4/4.* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[fingerstyle nylon-string acoustic guitar]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[breathy female vocals]` ← 보컬 지시
  _다섯 살이었어 유치원에서 돌아왔어_
  _마당에 누워서 잔디가 등을 간지럽혔어_
  _풀냄새가 났어 하늘을 올려다봤어_
  _구름이 있었어 크고 하얗고 느렸어_
`[Chorus]` ← 섹션 태그
  _아빠에게 물었어 구름은 어디로 가_
  _아빠가 말했어 바람이 데려가는 대로 가_
  _그럼 구름은 길을 모르는 거야_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): acoustic guitar
- **SP에만** (전체 톤, 진입 큐 없음): guitar

---

### [20/20] #1669 서 있는 것 — Rock

#### SP 원문
> K-Pop City Pop fusion. Clean electric guitar plays syncopated funk-style muted strums and rhythmic chords. A slap bass guitar performs active, percussive lines with frequent slides. Acoustic drums feature a crisp snare and tight hi-hat patterns. Bright, staccato piano chords punctuate the arrangement. A smooth male tenor vocal delivers melodic lines with occasional rhythmic delivery. A brass section consisting of trumpets and saxophones provides punchy stabs and melodic fills. The track features a sudden tempo increase and shift to a swing-influenced big band jazz style with walking bass and rapid brass flourishes. Key of E Major. 115 BPM transitioning to 160 BPM.

#### SP → 7슬롯 분해

| **장르 선언** | K-Pop City Pop fusion. |
| | *장르: K-Pop City Pop fusion* |
| **악기 레이어** | Clean electric guitar plays syncopated funk-style muted strums and rhythmic chords. |
| | *악기: Clean electric guitar plays syncopated funk-style muted strums and rhythmic chords* |
| **악기 레이어** | A slap bass guitar performs active, percussive lines with frequent slides. |
| | *악기: A slap bass guitar performs active, percussive lines with frequent slides* |
| **드럼/퍼커션** | Acoustic drums feature a crisp snare and tight hi-hat patterns. |
| | *드럼: Acoustic drums feature a crisp snare and tight hi-hat patterns* |
| **어레인지먼트 총평** | Bright, staccato piano chords punctuate the arrangement. |
| | *편곡: Bright, staccato piano chords punctuate the arrangement* |
| **보컬** | A smooth male tenor vocal delivers melodic lines with occasional rhythmic delivery. |
| | *보컬: A smooth male tenor vocal delivers melodic lines with occasional rhythmic delivery* |
| **악기 레이어** | A brass section consisting of trumpets and saxophones provides punchy stabs and melodic fills. |
| | *악기: A brass section consisting of trumpets and saxophones provides punchy stabs and melodic fills* |
| **템포/조성/박자** | The track features a sudden tempo increase and shift to a swing-influenced big band jazz style with walking bass and rapid brass flourishes. |
| | *The track features a sudden tempo increase and shift to a swing-influenced big band jazz style with walking bass and rapid brass flourishes.* |
| **템포/조성/박자** | Key of E Major. |
| | *조성 e major* |
| **템포/조성/박자** | 115 BPM transitioning to 160 BPM. |
| | *템포 115 BPM* |

#### 가사 브래킷 시퀀스

`[Intro]` ← 섹션 태그
`[clean electric guitar funk strums, slap bass, tight drums]` ← 악기/어레인지먼트 큐
`[Verse 1]` ← 섹션 태그
`[male tenor vocals]` ← 보컬 지시
  _생방이야 빨간 불이 켜져 있어_
  _대본을 읽고 있어 카메라 세 대가 돌아_
  _이어피스 PD가 말해 잘하고 있어_
  _순조로워 웃으면서 진행해_
`[piano stabs]` ← 악기/어레인지먼트 큐
  _페이지를 넘겼어 다음 문장을 읽어_
  _잠깐 이어지지 않아_
`[Pre-Chorus]` ← 섹션 태그
`[brass section enters with punchy stabs]` ← 전환 큐
  _한 줄을 건너뛰었어_
  _1초 머릿속이 하얘졌어_
  _2초 수만 명이 보고 있어_
  _3초 입을 열어야 해 뭘 말해야 하지_
`[Chorus]` ← 섹션 태그
`[tempo increases, swing feel, walking bass, big band brass]` ← 악기/어레인지먼트 큐
  _2, 3초간 나에게는 30분이야_
  _카메라_

#### SP↔가사 악기 매칭
- **공통** (SP 기술 + 가사 큐): bass, clean electric guitar, piano, slap bass
- **SP에만** (전체 톤, 진입 큐 없음): acoustic drum, guitar, saxophone, trumpet
- **가사에만** (SP 미언급, 가사에서 직접 큐): drum

---

## Part 3: 공통 패턴 + leomusic2 체크리스트

### SP 작성 규칙
1. **첫 문장 = 장르 선언** (100% 일관). 'K-Pop/K-Indie/K-Hip Hop' + 하위장르 조합.
2. **각 악기 = 독립 문장**. `{악기} plays/performs/provides {패턴} with {이펙트}.`
3. **드럼 = 독립 문장**. 'The drums consist of {킥} and {스네어} with {레이어}.'
4. **보컬 = 독립 문장**. 음역(baritone/tenor) + 딜리버리(breathy/intimate) + 프로세싱(plate reverb).
5. **템포/조성 = 후반부**. 'The tempo is <BPM> in the key of <KEY>.' 변이형 한정.
6. **어레인지먼트 총평 = 마지막** (선택). 'The arrangement is sparse, focusing on...'

### 가사 작성 규칙
1. **[Intro]로 시작** + 메인 악기 큐. 예: `[Intro]\n[fingerpicked acoustic guitar]`
2. **각 섹션 = [섹션 태그] + [보컬/악기 큐]** 쌍으로 시작.
   - `[Verse 1]\n[breathy male vocals]` → 이 구간의 보컬 타입 지정
3. **가사 중간에 [전환 큐]** 삽입으로 레이어 추가.
   - `가사 텍스트 [kick drum enters] 가사 계속` → 킥드럼 진입 시점
4. **SP에서 언급한 악기가 가사에서도 진입** (교차 일관성).
5. **Chorus에서 악기 추가**, Bridge에서 악기 제거가 전형적 패턴.

### SP 생성 체크리스트
- [ ] 첫 문장에 장르 선언?
- [ ] 각 악기를 독립 문장으로? (패턴 + 이펙트)
- [ ] 드럼 구성 별도 문장?
- [ ] 보컬 타입·딜리버리·프로세싱?
- [ ] 후반부에 템포/조성/박자?
- [ ] 어레인지먼트 총평? (선택)

### 가사 생성 체크리스트
- [ ] [Intro]로 시작 + 악기 큐?
- [ ] 각 섹션 [태그] + [악기/보컬 큐] 쌍?
- [ ] 가사 중간 [X enters] 전환 큐?
- [ ] SP 악기와 가사 브래킷 교차 확인?
- [ ] Chorus 확장 / Bridge 축소 패턴?