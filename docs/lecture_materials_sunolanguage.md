# SunoLanguage 강의 자료 — 관현악·작곡 전공자 대상

> sunolanguage → rag 회신 (2026-04-24)
> 378곡 / 13,501 entries / 5,070 unique words / 189 genres 기반

---

## 1. 프로젝트 소개 (1분 버전)

### 한 단락

Suno라는 AI 음악 생성 서비스에 실제 음악을 들려주면 Suno가 그 음악을 자기 말로 묘사합니다. 우리는 이 과정을 378곡에 대해 반복하면서 "Suno가 실제로 사용하는 어휘 사전"을 만들었습니다. 마치 외국인이 어떤 단어를 알고 어떤 단어를 모르는지 테스트하듯, AI 음악 엔진의 '언어 능력'을 역분석한 프로젝트입니다.

### 핵심 3줄

1. **Suno는 5,070개의 고유 단어로 음악을 묘사한다** — 인간 음악 어휘의 극히 일부
2. **코드 진행(II-V-I), 다이나믹 마킹(pp, mf), 성악 용어(passaggio)를 전혀 모른다** — 0회 사용
3. **대신 프로덕션 언어(vinyl crackle, sidechain compression, plate reverb)에는 능숙하다** — DAW 엔지니어의 언어

---

## 2. 실제 예제 모음

### (a) Suno가 실제로 쓰는 문장 10개

악기·주법·무드·프로덕션 각 영역에서 Suno SP 원문 그대로:

**악기**
1. > "Grand piano plays arpeggiated chords in the lower register with a legato melody in the right hand."
2. > "Orchestral strings enter with sustained legato pads, primarily cellos and violins providing harmonic thickening."
3. > "A muted trumpet performing melodic fills and a solo."
4. > "Solo cello performs a melancholic, legato melody in the tenor register."

**주법**
5. > "Fingerpicked acoustic guitar in a steady eighth-note pattern."
6. > "Distorted electric guitars play palm-muted chugging riffs and power chords."
7. > "The upright bass plays a walking line in a relaxed swing feel."

**무드/프로덕션**
8. > "The production is intimate with close-mic positioning on both the vocals and the guitar, featuring a short room reverb."
9. > "Atmospheric vinyl crackle and tape hiss provide a lo-fi texture."
10. > "A prominent sidechain compression effect creates a pumping sensation on the synth pads."

---

### (b) 장르별 Suno 방언 — SP 전문 4곡

#### Cinematic (gid=10464, "Horizon Step")
```
Cinematic orchestral score. Solo cello performs a melancholic, legato melody
in the tenor register. Sustained string pads in the violins and violas provide
harmonic support with slow, gradual volume swells. A secondary cello or double
bass enters later to provide low-frequency root notes. The arrangement is
sparse and minimalist, focusing on the interplay between the solo cello and
the ensemble textures. 65 BPM. D minor. 4/4 time signature.
```
→ **특징**: 악기명(cello, violins, violas) + 주법(legato, sustained) + 배치(sparse, minimalist). 화성 분석 없음.

#### Jazz (gid=1642, "브러시의 호박빛")
```
Jazz trio ballad featuring a baritone male vocalist. The arrangement consists
of a grand piano, upright bass, and a drum kit played with brushes. The piano
performs sparse, jazz-chord voicings and melodic fills between vocal phrases.
The upright bass plays a walking line in a relaxed swing feel. The drummer
uses brushes on the snare drum to create a continuous, soft swishing texture.
The vocals are delivered in a low-register, intimate, spoken-word style that
transitions into melodic singing.
```
→ **특징**: 편성(trio) + 주법(brushes, walking line) + 보컬 스타일(spoken-word → melodic singing). 코드명 없음.

#### Rock (gid=10469, "Crack of Light")
```
Hard rock with heavy metal influences. Distorted electric guitars play
palm-muted chugging riffs and power chords. A high-gain lead guitar performs
fast alternate-picked runs and wide vibrato. The bass guitar follows the root
notes of the guitar riffs with a gritty, overdriven tone. Acoustic drums
feature a punchy kick, a high-tuned snare, and frequent double-bass pedal
patterns. The tempo is 140 BPM in 4/4 time.
```
→ **특징**: 이펙트(distorted, high-gain, overdriven) + 주법(palm-muted, alternate-picked) + 드럼 상세. 감정/분위기 묘사 거의 없음.

#### K-Pop TROT (gid=20001, "사랑인가 봐") — Wave 1 신규 수집
```
K-Pop with City Pop influences. Features a bright, slap-style electric bass,
clean funk-rhythm electric guitar, and a digital synthesizer playing staccato
brass-like stabs. The drum kit uses a crisp snare and a steady kick. Male
vocals are delivered in a smooth, melodic tenor. The arrangement includes a
prominent synth-brass lead melody during the intro and transitions. Tempo is
118 BPM in the key of G Major.
```
→ **특징**: 트로트를 "K-Pop with City Pop influences"로 분류. 뽕짝 리듬을 "slap-style bass + funk-rhythm guitar"로 묘사. 장르 인식의 한계와 재해석이 동시에 드러남.

---

### (c) Dead Budget — Suno가 한 번도 안 쓴 음악 전문용어

#### (c1) 클래식·음악학 용어

| 용어 | Suno 사용 횟수 | 비고 |
|------|:---:|------|
| contrary motion | 0 | 대위법 기본 |
| motivic development | 0 | 동기 발전 |
| Neapolitan sixth | 0 | 변화 화음 |
| augmented sixth | 0 | 변화 화음 |
| fugue | 0 | 대위법 형식 |
| sonata | 0 | 소나타 형식 |
| appoggiatura | 0 | 비화성음 |
| cadenza | 0 | 독주 즉흥 |
| fermata | 0 | 늘임표 |
| sforzando | 0 | 강세 |

#### (c2) 전공자가 당연히 쓸 법한데 Suno는 모르는 용어

| 용어 | Suno 사용 횟수 | 비고 |
|------|:---:|------|
| passaggio | 0 | 성악 음역 전환점 |
| chiaroscuro | 0 | 성악 음색 기법 |
| tessitura | 0 | 주 음역대 |
| coloratura | 0 | 장식적 기교 |
| bel canto | 0 | 벨칸토 창법 |
| col legno | 0 | 활대 나무로 연주 |
| con sordino | 0 | 약음기 사용 |
| sul ponticello | 1 | 브릿지 근처 연주 (거의 0) |
| voice leading | 2 | 성부 진행 (거의 0) |

**대비**: Suno가 아는 것 — legato(71회), staccato(154회), vibrato(115회), tremolo(49회), rubato(59회), pizzicato(19회)

---

### (d) Suno만의 어휘 — 전공자에겐 낯선 프로덕션 언어

| Suno 어휘 | 빈도 | 뜻 |
|-----------|:---:|------|
| plate reverb | 223회 | 금속판 울림 잔향 (하드웨어 리버브) |
| sub-bass | 150회 | 40Hz 이하 초저음 베이스 |
| room reverb | 141회 | 방 크기 잔향 시뮬레이션 |
| palm-muted | 134회 | 손바닥으로 현 뮤트한 주법 |
| vinyl crackle | 87회 | LP 레코드 잡음 (로파이 텍스처) |
| close-mic | 89회 | 마이크 근접 배치 |
| sidechain compression | 33회 | 킥에 맞춰 다른 악기 볼륨을 줄이는 기법 |
| 808 | 32회 | Roland TR-808 드럼머신 사운드 |
| high-pass filter | 32회 | 저음 차단 필터 |
| tape saturation | 19회 | 테이프 녹음 특유의 따뜻한 왜곡 |

---

### (e) Stems 분리에서만 드러난 어휘 — 왜 중요한가

Suno에게 완성곡을 통째로 들려주면 "pop ballad with piano and strings" 수준으로 묘사합니다. 그런데 같은 곡의 **드럼만 따로** 들려주면 이야기가 달라집니다:

| 어휘 | stems에서만 발견 | 뜻 |
|------|:---:|------|
| dissonant | 51회 | 불협화음적 (전체 곡에선 숨겨져 있던 판단) |
| polyrhythmic | 9회 | 복합 리듬 (드럼 단독 분석에서만 감지) |
| taiko | 10회 | 일본 전통 북 (다른 악기에 묻혀 인식 못 하던 것) |
| d-beat | 12회 | 펑크/하드코어 특유의 드럼 패턴 |
| clangs | 37회 | 금속성 충돌음 |

**의미**: AI도 음악을 '덩어리'로 들으면 세부를 놓칩니다. 악기별로 분리해서 들려줘야 비로소 자기가 아는 단어를 꺼냅니다. 이것은 인간 청취와 놀랍도록 유사합니다 — 오케스트라 총주에서 오보에 파트를 분리해서 듣지 않으면 그 뉘앙스를 설명하기 어려운 것과 같습니다.

---

### (f) 7-Slot 문법 해설 — "당겨 당겨" (B193 gid=1783)

실제 Suno가 생성한 곡의 SP를 슬롯별로 분해한 것입니다:

| 슬롯 | 내용 |
|------|------|
| **genre** | K-Alt Rock, grungy. |
| **tempo_key_time** | Tempo is 128 BPM in 4/4 time, key of E minor. |
| **vocal_main** | A gritty, raspy female vocal with rhythmic, emotive delivery. Chesty open-throated shout on the final chorus. |
| **vocal_chorus** | Layered gang vocals doubled in unison on the chorus. |
| **instrument** | Gritty distorted electric guitar plays palm-muted power-chord stabs with tube-amp crunch, opening into wide overdrive on the chorus. Clean electric guitar layers arpeggiated tritone intervals with light chorus. Fuzzy electric bass follows the kick with overdriven mid-range bite. White-noise sweeps rise before each chorus. |
| **drums** | Snappy kick drum on a syncopated pattern. Cracking snare with room tone on 2 and 4. Crash punctuation on the peaks. |
| **arrangement** | The arrangement starts with solo clean guitar, builds through distorted layers, and explodes with gang vocals on the final chorus. |
| **mixing** | Vocals sit gritty and forward with heavy bus compression. |
| **effect** | Parallel distortion on the master bus, side-chain compression on the chorus, light plate reverb. |

**읽는 법**: Suno에게 "이런 음악 만들어"라고 할 때, 이 7개 슬롯을 채우는 것이 Suno가 이해하는 '악보'입니다. 전통 악보의 오선지 대신, 텍스트 슬롯이 Suno의 기보법입니다.

---

### (g) 보컬 묘사 — Suno vs 성악 전공 용어

| 영역 | Suno가 쓰는 표현 | 성악 전공 용어 |
|------|-----------------|--------------|
| 음역 전환 | "transitions into light head voice" | passaggio |
| 음색 | "warm, resonant" | chiaroscuro |
| 주 음역 | "mid-range baritone" | tessitura |
| 기교 | "melodic runs" | coloratura / melisma |
| 창법 | "breathy, intimate delivery" | bel canto |
| 떨림 | "wide vibrato on sustained notes" (115회) | vibrato (동일 용어 공유) |
| 끊어 부르기 | "staccato vocal delivery" (154회) | staccato (동일 용어 공유) |
| 힘주기 | "powerful belt" | appoggio / sforzando |
| 말하듯 | "spoken-word style" / "conversational" (107회) | sprechgesang / parlando |
| 감정 | "emotive", "gritty", "raspy" | 전공 용어 없음 (감정은 해석의 영역) |

**핵심 관찰**: Suno와 성악은 vibrato, staccato, legato 같은 **이탈리아어 기본 용어**만 공유합니다. 그 위의 전문 체계(passaggio, tessitura, chiaroscuro)는 Suno의 어휘에 존재하지 않습니다. 반면 Suno는 "breathy", "gritty", "raspy" 같은 **감각적·물리적 묘사**에 능숙합니다.

---

## 3. 강의 활용 가이드

| 자료 | 추천 타이밍 | 효과 |
|------|-----------|------|
| 프로젝트 소개 | 오프닝 직후 (5분) | "이런 연구가 존재한다"는 경이감 |
| 장르별 SP 비교 (b) | 본론 초반 (15분) | "읽어보세요" → 학생이 직접 장르 차이 체감 |
| Dead Budget (c) | **본론 중반 (25분)** | 가장 강력. "여러분이 아는 이 용어를, AI는 모릅니다" → 전공자 존재 이유 |
| Suno-only 어휘 (d) | Dead Budget 직후 | "반대로 AI만 아는 언어도 있습니다" → 균형 |
| 보컬 대비표 (g) | 관현악과: 현악 비교로 변형 / 작곡과: 그대로 사용 | 전공 지식과 직접 연결 |
| Stems 스토리 (e) | **심화 후반 (50분)** | "이 연구는 아직 진행 중" → 연구의 살아있는 느낌 |
| 7-Slot 해설 (f) | 마무리 전 (60분) | "AI의 악보는 이렇게 생겼습니다" → 인상적 클로징 |

---

## 4. 시각 자료 후보

- **어휘 히트맵**: `data/reanalysis_v2/vocab_expansion_v3.2.json` → genre_slot_matrix를 히트맵으로 시각화 가능
- **Dead Budget 대비표**: (c) 섹션을 슬라이드 1장으로 — 왼쪽 빨간색(0회), 오른쪽 초록색(고빈도)
- **7-Slot 도식**: (f) 섹션을 색깔 블록으로 — 각 슬롯을 다른 색으로 칠한 SP 전문
- **Suno SP 원문 타이포**: (b) 장르별 SP를 모노스페이스 폰트로 슬라이드에 배치
