# 매뉴얼 A — Suno가 SP에서 하는 것 (샘플 엔트리)

- 데이터 범위: 318곡 / 326 Suno 재분석 clips
- 본 문서는 전체 매뉴얼의 **샘플 15 엔트리**. 전문가 3분 리뷰용 파일럿.
- 각 엔트리는 정의·빈도·장르분포·변이형·leomusic 대응 관계·원문 인용 3건 포함

## 엔트리 형식
```
### {term}
- 카테고리
- 정의
- Suno SP 출현 / leomusic 원 SP 출현
- 장르 분포(상위5)
- 변이형
- leomusic↔Suno 관계
- 검증 상태 (confirmed ≥10 / plausible ≥3 / single_occurrence)
- 인용문 3건 (song_id · UUID · 장르)
```

## 샘플 엔트리

### clean electric guitar
- **카테고리**: 악기/Instrument
- **정의**: 왜곡 없이 맑은 음색의 일렉트릭 기타. Suno가 연주 묘사 시 가장 자주 사용하는 기타 디스크립터로, 주로 아르페지오·코드 연주와 함께 등장.
- **Suno SP 출현**: 147회 / **leomusic 원 SP 출현**: 15회
- **장르 분포(상위5)**: Indie Pop(10), (미정)(9), City Pop(9), Korean Ballad(6), Folk(6)
- **변이형**: `clean electric guitar`(147) / `a clean electric guitar`(58)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0001 *소음의 끝* · `38270b87` · [Lo-fi Indie Pop / Dream Pop]
    > Clean electric guitar plays a repetitive arpeggiated pattern with light chorus and delay.
  - #0012 *빈 밥상* · `7ff0271c` · [Contemporary R&B]
    > Clean electric guitar plays arpeggiated chords with light chorus and reverb.
  - #0041 *첫 발자국* · `dfef369e` · [City Pop / Future Funk]
    > The arrangement features a slap bass line performing syncopated sixteenth-note patterns, a bright acoustic piano playing jazz-influenced chord extensions, and a clean electric guitar with rhythmic palm-muted scratching.

### sub-bass synth
- **카테고리**: 악기/Instrument
- **정의**: 20~60Hz 대역을 담당하는 저음 전용 신스. Suno는 'provides low-end weight', 'holds the foundation' 같은 기능 기술과 함께 사용.
- **Suno SP 출현**: 13회 / **leomusic 원 SP 출현**: 0회
- **장르 분포(상위5)**: Indie Pop(2), Lo-fi Indie Pop / Dream Pop(1), Contemporary R&B(1), Hip-Hop / Lo-fi Boom Bap(1), Acoustic Folk / Ambient(1)
- **변이형**: `sub-bass synth`(13) / `a sub-bass synth`(12)
- **leomusic↔Suno 관계**: Suno 고유 (leomusic 원 SP 미출현)
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0001 *소음의 끝* · `38270b87` · [Lo-fi Indie Pop / Dream Pop]
    > A sub-bass synth provides low-end weight on the downbeats.
  - #0012 *빈 밥상* · `7ff0271c` · [Contemporary R&B]
    > Sub-bass synth enters during the chorus.
  - #0134 *투잡* · `beb47eb5` · [Hip-Hop / Lo-fi Boom Bap]
    > A sub-bass synth follows the root notes of the guitar.

### fingerpicked acoustic guitar
- **카테고리**: 악기/Instrument
- **정의**: 손가락으로 현을 튕기는 어쿠스틱 기타 연주. Suno는 이 표현을 intimate/folk/ballad 계열에서 일관되게 사용, 악기+주법을 한 토큰으로 결합.
- **Suno SP 출현**: 46회 / **leomusic 원 SP 출현**: 30회
- **장르 분포(상위5)**: Korean Ballad(4), Indie Pop(3), City Pop(3), Lo-fi Pop(3), Folk(3)
- **변이형**: `fingerpicked acoustic guitar`(46) / `a fingerpicked acoustic guitar`(12)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0121 *발밑 무지개* · `366d1eaf` · [Neo-Soul / Jazzy Pop]
    > Fingerpicked acoustic guitar in a steady eighth-note pattern.
  - #0122 *갈라진 지도* · `4a4d2238` · [Acoustic Ballad / Folk Pop]
    > The arrangement centers on a fingerpicked acoustic guitar with a warm, resonant tone.
  - #0127 *반 톤* · `effa0b22` · [Future Bass / Electro Pop]
    > Fingerpicked acoustic guitar in a steady eighth-note pattern.

### arpeggiated
- **카테고리**: 주법/Playing technique
- **정의**: 코드를 동시에 울리지 않고 음을 하나씩 순차로 퍼뜨리는 연주. 기타/신스/피아노에 모두 적용. 'a repetitive arpeggiated pattern' 형태 자주 출현.
- **Suno SP 출현**: 74회 / **leomusic 원 SP 출현**: 18회
- **장르 분포(상위5)**: Acoustic Pop(4), Folk(4), Lo-fi Pop(3), Korean Ballad(3), (미정)(2)
- **변이형**: `arpeggiated`(74) / `arpeggio`(4)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0001 *소음의 끝* · `38270b87` · [Lo-fi Indie Pop / Dream Pop]
    > Clean electric guitar plays a repetitive arpeggiated pattern with light chorus and delay.
  - #0011 *화면 속 타인* · `61efe721` · [Indie Pop / Dream Pop]
    > Acoustic guitar plays a steady fingerstyle pattern with alternating bass notes and arpeggiated chords.
  - #0012 *빈 밥상* · `7ff0271c` · [Contemporary R&B]
    > Clean electric guitar plays arpeggiated chords with light chorus and reverb.

### syncopated
- **카테고리**: 주법/Playing technique
- **정의**: 강박 대신 약박을 강조하여 리듬을 당김. Suno의 주법 어휘 중 최상위 빈도. 드럼/베이스/기타 모두에서 사용.
- **Suno SP 출현**: 159회 / **leomusic 원 SP 출현**: 18회
- **장르 분포(상위5)**: Indie Pop(10), City Pop(8), (미정)(6), Funk Pop(6), Hip-Hop(5)
- **변이형**: `syncopated`(159) / `syncopation`(1)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0002 *누런 봉투* · `43957982` · [Contemporary R&B / Neo-Soul]
    > The arrangement features a prominent upright bass playing walking lines and syncopated rhythms, a grand piano providing harmonic accompaniment with jazz voicings, and a muted trumpet performing melodic fills and a solo.
  - #0022 *뜯지 않은 상자* · `44623873` · [Synth-Pop / Bedroom Pop]
    > The arrangement centers on a clean, palm-muted electric guitar playing a syncopated rhythmic riff.
  - #0031 *99+* · `f2ce400e` · [Hyperpop / Digital Noise]
    > The track utilizes a prominent, syncopated slap bass line that interacts with a crisp electronic drum kit.

### plate reverb
- **카테고리**: 프로덕션/Production
- **정의**: 금속판 진동을 이용한 리버브. Suno는 보컬 처리 기술어로 반복 사용 — 특히 'moderate plate reverb', 'plate reverb on the vocals' 구문으로 정형화됨.
- **Suno SP 출현**: 44회 / **leomusic 원 SP 출현**: 10회
- **장르 분포(상위5)**: City Pop(4), Indie Pop(3), Korean Ballad(3), Lo-fi Indie Pop / Dream Pop(1), Indie Pop / Dream Pop(1)
- **변이형**: `plate reverb`(44) / `moderate plate reverb`(5)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0001 *소음의 끝* · `38270b87` · [Lo-fi Indie Pop / Dream Pop]
    > Breathy, intimate female vocals are processed with moderate plate reverb and centered in the mix.
  - #0011 *화면 속 타인* · `61efe721` · [Indie Pop / Dream Pop]
    > A soft, breathy baritone male vocal sits forward in the mix with light plate reverb.
  - #0081 *김밥 냄새* · `d2dbc0dc` · [Country Pop / Americana]
    > The vocal is clean with light plate reverb, delivered in a conversational, storytelling tone.

### sidechain compression
- **카테고리**: 프로덕션/Production
- **정의**: 외부 신호(보통 킥드럼) 레벨에 반응해 다른 트랙 볼륨을 자동 감쇠시키는 기법. Suno는 'sidechain compression from the kick' 형태로 사용.
- **Suno SP 출현**: 4회 / **leomusic 원 SP 출현**: 5회
- **장르 분포(상위5)**: Future Bass / Electro Pop(1), Jazz Ballad / Bossa Nova(1), Acoustic Pop(1), R&B(1)
- **변이형**: `sidechain compression`(4) / `side-chain compression`(1)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: plausible
- **인용문** (song_id · UUID · 장르):
  - #0137 *플레이리스트* · `8e182cd3` · [Future Bass / Electro Pop]
    > The production uses sidechain compression on the pads and bass to create a pumping effect against the kick.
  - #0147 *아침 약* · `deda2bbf` · [Jazz Ballad / Bossa Nova]
    > A prominent sidechain compression effect creates a pumping sensation on the synth pads.
  - #1466 *첫 번째 물* · `f04099ce` · [Acoustic Pop]
    > The arrangement uses sidechain compression on the pads to create a pumping effect against the kick.

### breathy female vocals
- **카테고리**: 보컬/Vocal
- **정의**: 숨소리 결이 섞인 여성 보컬. Suno는 이 표현을 Pop/R&B/Indie의 intimate 계열에서 안정적으로 사용, 'intimate'·'centered in the mix' 등과 공기(共起).
- **Suno SP 출현**: 5회 / **leomusic 원 SP 출현**: 0회
- **장르 분포(상위5)**: Acoustic Folk / Midnight Folk(1), Acoustic Indie Folk(1), City Pop(1), Dream Pop(1), R&B(1)
- **변이형**: `breathy female vocals`(5)
- **leomusic↔Suno 관계**: Suno 고유 (leomusic 원 SP 미출현)
- **검증 상태**: plausible
- **인용문** (song_id · UUID · 장르):
  - #1135 *4시 반의 출발* · `44a6103b` · [Acoustic Folk / Midnight Folk]
    > Soft, breathy female vocals are processed with high-frequency air and moderate hall reverb.
  - #1145 *헬멧 안의 새벽* · `f3e65dac` · [Acoustic Indie Folk]
    > Soft, breathy female vocals are processed with high-frequency air and moderate hall reverb.
  - #1177 *디지털 디톡스 실패기* · `ffa3d3d3` · [City Pop]
    > Soft, breathy female vocals with light doubling and subtle reverb.

### baritone male vocal
- **카테고리**: 보컬/Vocal
- **정의**: 중저음역 남성 보컬. Suno는 'baritone male vocal'을 팝·R&B·발라드에서 고정 어휘로 사용 (단수/복수 혼용).
- **Suno SP 출현**: 33회 / **leomusic 원 SP 출현**: 0회
- **장르 분포(상위5)**: Indie Pop(2), City Pop(2), Indie Pop / Dream Pop(1), Chillwave / Synthpop(1), Piano Ballad / Cinematic(1)
- **변이형**: `baritone male vocal`(33) / `a baritone male vocal`(31) / `baritone male vocals`(1)
- **leomusic↔Suno 관계**: Suno 고유 (leomusic 원 SP 미출현)
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0011 *화면 속 타인* · `61efe721` · [Indie Pop / Dream Pop]
    > A soft, breathy baritone male vocal sits forward in the mix with light plate reverb.
  - #0061 *건조기 자장가* · `2e7995e0` · [Chillwave / Synthpop]
    > A baritone male vocal delivers a rhythmic, almost conversational melody in Korean.
  - #0072 *빈손* · `207c187e` · [Piano Ballad / Cinematic]
    > A baritone male vocal performs with a breathy, emotive delivery, utilizing wide vibrato on sustained notes.

### intimate
- **카테고리**: 무드/Mood
- **정의**: 작은 공간/가까운 거리에서 속삭이듯 전달되는 질감을 가리키는 Suno의 핵심 무드 형용사. 보컬·편곡 양쪽에 동시 적용.
- **Suno SP 출현**: 105회 / **leomusic 원 SP 출현**: 179회
- **장르 분포(상위5)**: Indie Pop(8), City Pop(6), (미정)(5), Korean Ballad(5), Lo-fi Pop(4)
- **변이형**: `intimate`(105)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0001 *소음의 끝* · `38270b87` · [Lo-fi Indie Pop / Dream Pop]
    > Breathy, intimate female vocals are processed with moderate plate reverb and centered in the mix.
  - #0011 *화면 속 타인* · `61efe721` · [Indie Pop / Dream Pop]
    > The arrangement is minimalist, focusing on the interplay between the rhythmic acoustic guitar and the intimate vocal delivery.
  - #0012 *빈 밥상* · `7ff0271c` · [Contemporary R&B]
    > Male vocals are delivered in a breathy, intimate tenor range, transitioning to a powerful chest voice in the chorus.

### crisp
- **카테고리**: 음색/Timbre
- **정의**: 선명하고 에지가 살아있는 타격음·스네어·하이햇 묘사 시 Suno가 고정적으로 쓰는 형용사. 'crisp snare', 'crisp hi-hat' 형태.
- **Suno SP 출현**: 136회 / **leomusic 원 SP 출현**: 40회
- **장르 분포(상위5)**: Indie Pop(6), Synth Pop(6), City Pop(6), Korean Ballad(6), (미정)(5)
- **변이형**: `crisp`(136) / `crisp snare`(91) / `crisp hi-hats`(3)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0001 *소음의 끝* · `38270b87` · [Lo-fi Indie Pop / Dream Pop]
    > The drums consist of a dry, tight kick and a crisp snare with a subtle electronic clap layer.
  - #0012 *빈 밥상* · `7ff0271c` · [Contemporary R&B]
    > Percussion is minimal, featuring a soft electronic kick and a crisp snare with a short decay.
  - #0021 *새벽 다섯 시* · `36bc3e2d` · [Electro Hip-Hop / Synth-Trap]
    > The drum kit consists of a punchy kick, a crisp snare, and consistent eighth-note hi-hats.

### 72 BPM
- **카테고리**: 템포/Tempo
- **정의**: Suno 재분석에서 가장 자주 등장하는 BPM값. K-발라드·Indie Pop 샘플에서 집중 출현 — leomusic 생성곡 템포 분포 반영.
- **Suno SP 출현**: 97회 / **leomusic 원 SP 출현**: 11회
- **장르 분포(상위5)**: Indie Pop(6), Acoustic Pop(6), City Pop(6), R&B(5), Lo-fi Pop(5)
- **변이형**: `72 bpm`(97) / `at 72 bpm`(13)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0001 *소음의 끝* · `38270b87` · [Lo-fi Indie Pop / Dream Pop]
    > The tempo is 72 BPM in the key of C Major.
  - #0012 *빈 밥상* · `7ff0271c` · [Contemporary R&B]
    > Tempo is 72 BPM in 4/4 time.
  - #0072 *빈손* · `207c187e` · [Piano Ballad / Cinematic]
    > Tempo is 72 BPM in 4/4 time.

### key of E Major
- **카테고리**: 조성/Key
- **정의**: Suno 재분석에서 최빈출 조성. 샘플 곡의 실제 key 분포를 반영하며 'The tempo is X BPM in the key of E Major' 구문에 고정 위치.
- **Suno SP 출현**: 131회 / **leomusic 원 SP 출현**: 0회
- **장르 분포(상위5)**: Indie Pop(10), City Pop(7), R&B(4), Acoustic Ballad(4), Jazz Pop(4)
- **변이형**: `key of e major`(131) / `in the key of e major`(58)
- **leomusic↔Suno 관계**: Suno 고유 (leomusic 원 SP 미출현)
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0002 *누런 봉투* · `43957982` · [Contemporary R&B / Neo-Soul]
    > The track is in the key of E Major at a tempo of 82 BPM in 4/4 time.
  - #0041 *첫 발자국* · `dfef369e` · [City Pop / Future Funk]
    > The tempo is 118 BPM in the key of E Major.
  - #0051 *추락 직전* · `485897b1` · [Garage Rock / Indie Rock]
    > Key of E Major, 85 BPM.

### 4/4 time
- **카테고리**: 박자/Time signature
- **정의**: 네박자. 원 기획 parsed schema에는 있었으나 v1 사전엔 빠져있던 필드. Suno SP에서 161회 출현, 전체 샘플 거의 전수가 4/4.
- **Suno SP 출현**: 161회 / **leomusic 원 SP 출현**: 0회
- **장르 분포(상위5)**: Indie Pop(8), Korean Ballad(7), City Pop(7), R&B(7), Acoustic Pop(6)
- **변이형**: `4/4`(174) / `4/4 time`(161)
- **leomusic↔Suno 관계**: Suno 고유 (leomusic 원 SP 미출현)
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0002 *누런 봉투* · `43957982` · [Contemporary R&B / Neo-Soul]
    > The track is in the key of E Major at a tempo of 82 BPM in 4/4 time.
  - #0011 *화면 속 타인* · `61efe721` · [Indie Pop / Dream Pop]
    > Tempo is 78 BPM in 4/4 time, key of G Major.
  - #0012 *빈 밥상* · `7ff0271c` · [Contemporary R&B]
    > Tempo is 72 BPM in 4/4 time.

### K-Pop
- **카테고리**: 장르/Genre self-label
- **정의**: Suno가 첫 문장에서 장르 선언 시 가장 자주 내세우는 라벨. 'K-Pop ballad', 'K-Pop R&B ballad' 복합 형태로도 사용.
- **Suno SP 출현**: 245회 / **leomusic 원 SP 출현**: 17회
- **장르 분포(상위5)**: Indie Pop(15), City Pop(11), Korean Ballad(9), Acoustic Pop(8), (미정)(7)
- **변이형**: `k-pop`(245) / `k-pop ballad`(87) / `k-pop r&b`(33)
- **leomusic↔Suno 관계**: 공통 어휘
- **검증 상태**: confirmed
- **인용문** (song_id · UUID · 장르):
  - #0001 *소음의 끝* · `38270b87` · [Lo-fi Indie Pop / Dream Pop]
    > K-Pop Indie Pop ballad.
  - #0002 *누런 봉투* · `43957982` · [Contemporary R&B / Neo-Soul]
    > K-Pop ballad with jazz-pop and soul influences.
  - #0012 *빈 밥상* · `7ff0271c` · [Contemporary R&B]
    > K-Pop ballad with R&B influences.

---

## SP 작성 형식 표준 v1 (2026-06-16, explore 벤치마크 반영) — ⚠️ LEO 검증 대기(HOLD)

> **⚠️ HOLD (2026-06-16)**: 본 표준은 아직 **발효 전**이다. 절차 = [sunolanguage 코퍼스 체크 → sunomusic 검증 → LEO 게이트 → 그 후 전파/발효]. 현재 코퍼스 체크 완료·검증 대기 단계이며, leomusic/2/3 전파는 회수됨. **게이트 통과 전 적용 금지.** 코퍼스 체크 결과: A PASS · B PASS · C 조건부(무드 register 제한 — dreamy/nostalgic/tender/bittersweet/moody는 Suno 재분석 0건이라 제외, warm/intimate/atmospheric/smooth/lush/soulful/mellow/melancholic만 사용).
>
> **근거**: Suno explore 산문형 4곡 비교(`reviews/explore4_sp_format_comparison_20260616.md`) + UK Garage 태그식 분석. LEO 채택 지시(sunomusic 경유, 2026-06-16) → 절차 정정으로 검증 게이트 선행. 발효 시 leomusic/leomusic2/leomusic3 SP 빌더 라인 공통 적용 예정.

**전제 — 우리 형식 정체성(불변)**: Suno-native 영어 **산문 멀티문장**(콤마 태그나열·라벨형 아님). 순서: 장르·무드 → 악기 → 보컬 → 프로덕션 → BPM/키. 가사필드는 구조 브래킷 + **instrument-cue 브래킷**(`[muted trumpet cry]` 등)으로 시간축 통제 — ★우리 고유 강점, 유지가 표준의 대전제.

### A. 압축 산문 길이 타깃 (Você/PACO 벤치마크)
- 목표 **~500자 밀도 산문** (현 700자대에서 압축). 상한 1000자 유지하되 과장황 지양.
- BPM/키는 `Tempo is X BPM in the key of Y.` 식 **1문장 마감** 유지(또는 `X BPM, 4/4, key of Y.` 자체 행).
- 근거: explore 최상위 산문곡 Você가 ~480자로 우리와 동일 구조 — 짧고 밀도 높은 산문이 최적(4장 4.5 SP 길이, 6장 6.5 과포화 회피와 일치).

### B. 꼬리 장르태그 시딩 (Lucid/Varletine, 선택적)
- **다(多)장르·퓨전 곡에 한해** SP 말미에 CSV 장르태그 시딩 허용. 단일 장르 곡엔 불요.
- ★**attested 어휘만**(lexical_index v3.2 검증 의무): glitch(22)·phonk(2) 등 OK / `reverse swell`·`riddim`·`doubled`·`autotuned` 등 **0건 어휘 금지**.
- 검증 경로: `scripts/batch_sp_review.py --json` 또는 lexical_index 직접 조회로 0건 태그 reject.

### C. 무드 산문 흡수 (float/WorriedChart 발상, 라벨형 미채택)
- float.의 Mood 필드 발상을 **라벨이 아닌 '무드 산문 1줄'**로 흡수. 라벨형(`Genre:`/`Mood:`) 구조 자체는 미채택(작성 보조 템플릿으로만, 최종 출력은 산문 변환).

### 미채택
- stay(melø) 불릿 강조 → 우리 Top-Anchor 첫줄 배치로 이미 커버.
- float 라벨 구조 → 작성 보조용만, 산출 SP는 산문.
