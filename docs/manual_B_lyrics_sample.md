# 매뉴얼 B — Suno가 가사에서 하는 것 (샘플 엔트리)

- 데이터 범위: 318곡 / 326 Suno 재분석 clips / **2,282개 가사 브래킷**
- Suno는 가사 내부 `[...]` 브래킷으로 **구간별 연출 지시**를 남김 — SP 산문과 별개의 언어 시스템
- 본 문서는 전체 매뉴얼의 **샘플 10 엔트리** + 자동 1차 타입 분류

## 추정 타입 체계 (1차 초안)

| 타입 | 정의 |
|------|------|
| section | 곡 구조 구분 태그 (Intro/Verse/Chorus/Bridge 등). Suno 재분석 가사에서 가장 안정된 브래킷 체계. |
| vocal_direction | 보컬 퍼포먼스 지시 (톤/발성/숨결/강도). 구간 시작 부분 또는 특정 라인 위치에 삽입. |
| instrument_or_arrangement | 악기 진입/레이어/어레인지먼트 큐. 'X enters', 'X comes in', 'layered with Y' 형태 다수. |
| transition_cue | 구간 전환 큐 (enter/drop/fade/build/swell). 레이어 추가·제거 타이밍 명시. |
| effect | 이펙트/프로세싱 큐 (reverb/delay/filter sweep 등). 순간적 처리 강조 용도. |

## 타입별 출현/고유 분포 (자동 분류)

| 타입 | 출현 | 고유 | 비고 |
|----|---:|---:|----|
| section | 1010 | 40 | 가장 안정 |
| instrument_or_arrangement | 244 | 40 | 가장 다양 (600 고유) |
| effect | 330 | 40 |  |
| vocal_direction | 285 | 40 |  |
| transition_cue | 176 | 40 | 순간 큐 위주 |
| uncategorized | 61 | 40 | 타입 규칙 보완 필요 |

## 샘플 엔트리

### [intro]
- **타입**: section — 곡 구조 구분 태그 (Intro/Verse/Chorus/Bridge 등). Suno 재분석 가사에서 가장 안정된 브래킷 체계.
- **총 출현**: 317회 (고유 311곡)
- **장르 분포(상위5)**: Indie Pop(19), City Pop(16), (미정)(10), Acoustic Pop(10), R&B(10)
- **검증 상태**: confirmed
- **인용 문맥** (앞뒤 40자 포함):
  - #0001 *소음의 끝* · `38270b87`
    > ...[Intro] [arpeggiated clean electric guitar with...
  - #0002 *누런 봉투* · `43957982`
    > ...[Intro] [upright bass, grand piano, brushed sna...
  - #0011 *화면 속 타인* · `61efe721`
    > ...[Intro] [fingerstyle acoustic guitar]  [Verse 1...

### [verse 1]
- **타입**: section — 곡 구조 구분 태그 (Intro/Verse/Chorus/Bridge 등). Suno 재분석 가사에서 가장 안정된 브래킷 체계.
- **총 출현**: 326회 (고유 318곡)
- **장르 분포(상위5)**: Indie Pop(19), City Pop(16), Korean Ballad(11), (미정)(10), Acoustic Pop(10)
- **검증 상태**: confirmed
- **인용 문맥** (앞뒤 40자 포함):
  - #0001 *소음의 끝* · `38270b87`
    > ...ted clean electric guitar with chorus]  [Verse 1] [breathy female vocals] 화면을 끄자 천장이 보였어...
  - #0002 *누런 봉투* · `43957982`
    > ...bass, grand piano, brushed snare drum]  [Verse 1] [male tenor vocals] 서랍 깊은 곳에 누런 봉투 하나 바...
  - #0011 *화면 속 타인* · `61efe721`
    > ...[Intro] [fingerstyle acoustic guitar]  [Verse 1] [breathy baritone male vocals] 가로등에 비친...

### [chorus]
- **타입**: section — 곡 구조 구분 태그 (Intro/Verse/Chorus/Bridge 등). Suno 재분석 가사에서 가장 안정된 브래킷 체계.
- **총 출현**: 215회 (고유 205곡)
- **장르 분포(상위5)**: Indie Pop(11), Korean Ballad(9), (미정)(8), Acoustic Pop(7), Funk Pop(7)
- **검증 상태**: confirmed
- **인용 문맥** (앞뒤 40자 포함):
  - #0002 *누런 봉투* · `43957982`
    > ...한 번도 다정한 적 없던 그 사람이 별이 밝다고 당신 생각이 난다고  [Chorus] [piano chords intensify] 이 낡은 잉크가 말하고 있...
  - #0012 *빈 밥상* · `7ff0271c`
    > ...줄었다 자유라고 했는데 왜 이렇게 무거운지 밥그릇 가장자리가 차갑다  [Chorus] [sub-bass synth enters, snare hits on 2...
  - #0021 *새벽 다섯 시* · `36bc3e2d`
    > ...점 중독인지 구원인지 모를 이 반복 거울이 천천히 내 모습을 갈아낸다  [Chorus] [melodic rap vocals] 새벽 다섯 시 나는 유령이 된다...

### [pre-chorus]
- **타입**: section — 곡 구조 구분 태그 (Intro/Verse/Chorus/Bridge 등). Suno 재분석 가사에서 가장 안정된 브래킷 체계.
- **총 출현**: 59회 (고유 58곡)
- **장르 분포(상위5)**: (미정)(5), City Pop(3), Rock(3), Alternative R&B / Indie Electronic(2), Synth-Punk(2)
- **검증 상태**: confirmed
- **인용 문맥** (앞뒤 40자 포함):
  - #0002 *누런 봉투* · `43957982`
    > ...et enters] 군번 옆에 적힌 날짜는 내가 태어나기 훨씬 전이야  [Pre-Chorus] 한 번도 다정한 적 없던 그 사람이 별이 밝다고 당신 생각이 난다고...
  - #0061 *건조기 자장가* · `2e7995e0`
    > ...건조기 세 대 중 하나만 돌고 있어 내 빨래가 둥글게 춤을 추고 있다  [Pre-Chorus] 유리 너머로 보이는 양말과 티셔츠 원심력 속에서 팔을 벌리고 날아간다...
  - #0091 *새 안경* · `e2ab461b`
    > ...나뭇잎 한 장 한 장이 따로 보이고 건물 모서리의 윤곽선이 살아 있다  [Pre-Chorus] 횡단보도 신호등 색이 또렷하고 멀리 있는 사람 표정까지 읽힌다 버스 번...

### [bridge]
- **타입**: section — 곡 구조 구분 태그 (Intro/Verse/Chorus/Bridge 등). Suno 재분석 가사에서 가장 안정된 브래킷 체계.
- **총 출현**: 3회 (고유 3곡)
- **장르 분포(상위5)**: Indie Rock(1), Rock(1), Acoustic Folk(1)
- **검증 상태**: plausible
- **인용 문맥** (앞뒤 40자 포함):
  - #0168 *늦둥이 아빠* · `9c0b82d8`
    > ...져와 마이크에서 열기가 올라와 가슴에서 불이 나 참았던 게 다 쏟아져  [Bridge] [drums drop out, clean guitar arpeggio]...
  - #1682 *혼자 서 있는 플랫폼* · `f03db071`
    > ...중국집이 있어요 짬뽕은 오후에 졸려요 새로 생긴 태국 음식점이 있어요  [Bridge] [clean electric guitar counterpoint] 메뉴...
  - #1745 *한 꼬집* · `87dd7d7d`
    > ...가 먼저 웃었는데 [bass enters] 지금은 끝나고 나서야 웃어  [Bridge] 핸드폰에 볼 것도 없으면서 고개를 숙여 너도 그래 화장실 다녀올게 혼자...

### [breathy female vocals]
- **타입**: vocal_direction — 보컬 퍼포먼스 지시 (톤/발성/숨결/강도). 구간 시작 부분 또는 특정 라인 위치에 삽입.
- **총 출현**: 28회 (고유 28곡)
- **장르 분포(상위5)**: (미정)(3), Hip-Hop(2), City Pop(2), Electronic(2), Lo-fi Indie Pop / Dream Pop(1)
- **검증 상태**: confirmed
- **인용 문맥** (앞뒤 40자 포함):
  - #0001 *소음의 끝* · `38270b87`
    > ...electric guitar with chorus]  [Verse 1] [breathy female vocals] 화면을 끄자 천장이 보였어 [kick drum enters] 헤드라이트...
  - #0125 *보풀* · `42974592`
    > ...ing acoustic guitar, shaker]  [Verse 1] [breathy female vocals] 숟가락이 그릇에 닿아 [upright bass enters] 달칵 소리...
  - #0134 *투잡* · `beb47eb5`
    > ...light chorus, soft sub-bass]  [Verse 1] [breathy female vocals] 커튼 사이로 비친 들어 [kick drum and rimshot ent...

### [kick drum enters]
- **타입**: instrument_or_arrangement — 악기 진입/레이어/어레인지먼트 큐. 'X enters', 'X comes in', 'layered with Y' 형태 다수.
- **총 출현**: 14회 (고유 14곡)
- **장르 분포(상위5)**: Electronic(2), Lo-fi Indie Pop / Dream Pop(1), Neo-Soul / Jazzy Pop(1), Dream Pop / Shoegaze(1), Synth-Punk(1)
- **검증 상태**: confirmed
- **인용 문맥** (앞뒤 40자 포함):
  - #0001 *소음의 끝* · `38270b87`
    > ...[breathy female vocals] 화면을 끄자 천장이 보였어 [kick drum enters] 헤드라이트가 벽을 스치며 지나가 옆집 기타 소리 한 줄이 이불 위로 천...
  - #0121 *발밑 무지개* · `da51155f`
    > ...발밑에 있었어 [finger snap] 고개 숙인 나에게만 보이는 걸 [kick drum enters] 퇴근길 빨간불 앞에 멈춰 서서 [snare hit] 웅덩이에 번진 기름...
  - #0140 *거울 속 거울* · `3d3824c8`
    > ...an electric guitar riff, vinyl crackle] [kick drum enters] (Let's go) [snare and bass enter] (Um,...

### [arpeggiated clean electric guitar with chorus]
- **타입**: instrument_or_arrangement — 악기 진입/레이어/어레인지먼트 큐. 'X enters', 'X comes in', 'layered with Y' 형태 다수.
- **총 출현**: 2회 (고유 2곡)
- **장르 분포(상위5)**: Lo-fi Indie Pop / Dream Pop(1), Hip-Hop(1)
- **검증 상태**: single_occurrence
- **인용 문맥** (앞뒤 40자 포함):
  - #0001 *소음의 끝* · `38270b87`
    > ...[Intro] [arpeggiated clean electric guitar with chorus]  [Verse 1] [breathy female vocals] 화면을...
  - #1223 *단골* · `fbd3cb1d`
    > ...[Intro] [arpeggiated clean electric guitar with chorus]  [Verse 1] [breathy female vocals] 붓을 씻...

### [plate reverb]
- **타입**: effect — 이펙트/프로세싱 큐 (reverb/delay/filter sweep 등). 순간적 처리 강조 용도.
- **총 출현**: 0회 (고유 0곡)
- **검증 상태**: single_occurrence
- **인용 문맥** (앞뒤 40자 포함):

### [drum kit enters]
- **타입**: instrument_or_arrangement — 악기 진입/레이어/어레인지먼트 큐. 'X enters', 'X comes in', 'layered with Y' 형태 다수.
- **총 출현**: 0회 (고유 0곡)
- **검증 상태**: single_occurrence
- **인용 문맥** (앞뒤 40자 포함):
