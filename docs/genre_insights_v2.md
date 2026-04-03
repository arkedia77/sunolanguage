# Suno 네이티브 어휘 — 장르별 인사이트 v2

**기준 데이터**: 파싱 v2 (342곡 / 59장르 / Audiocards 7필드)
**생성일**: 2026-04-03

---

## 1. 데이터 개요

| 항목 | 수치 |
|------|------|
| 총 파싱 곡 수 | 342곡 |
| 총 장르 수 | 59개 |
| 7/7 풀커버리지 장르 | 28개 |
| 데이터 부족 장르 (≤2필드) | 2개 (alt rock, amapiano) |

### Audiocards 필드별 어휘 규모

| 필드 | 고유 용어 수 | Top 3 |
|------|-------------|-------|
| ac_instruments | 66개 | bass(120), drums(95), piano(81) |
| ac_temporal_structure | 64개 | chorus(73), bridge(30), hook(29) |
| ac_techniques | 62개 | vibrato(21), block chords(13), arpeggiated chords(6) |
| ac_genre_style | 58개 | rock(50), jazz(48), ambient(36) |
| ac_mood_emotion | 41개 | warm(76), raw(46), gentle(45) |
| ac_timbre | 31개 | soft(82), warm(76), clean(44) |
| ac_production | 28개 | vinyl crackle(21), wide stereo(10), hall reverb(9) |

---

## 2. 장르별 어휘 풍부도 TOP 10

Suno가 해당 장르를 묘사할 때 사용하는 고유 용어가 많을수록 = Suno가 그 장르를 더 세밀하게 구분함.

| 순위 | 장르 | 고유 용어 수 | 의미 |
|------|------|-------------|------|
| 1 | jazz | 158개 | Suno가 가장 풍부하게 묘사하는 장르 |
| 2 | rock | 148개 | 악기·주법·무드 모두 다양 |
| 3 | ambient | 138개 | production/timbre 표현 특히 풍부 |
| 4 | cinematic | 132개 | 영화음악 특화 어휘 다수 |
| 5 | r&b | 110개 | vocal timbre 묘사 세밀 |
| 6 | choral | 96개 | 찬송가 데이터 반영 |
| 7 | indie pop | 96개 | 현대 팝 표현 풍부 |
| 8 | swing | 95개 | 재즈 파생 장르 중 가장 풍부 |
| 9 | dream pop | 91개 | atmospheric 표현 특화 |
| 10 | indie rock | 89개 | rock 파생 중 높은 커버리지 |

---

## 3. SP 작성에 핵심: 장르별 Technique 사전

Suno가 실제 인식/사용하는 주법 표현. SP에 그대로 사용 가능.

### Jazz
`call and response` · `chopping` · `double bass` · `polyrhythm` · `sampling` · `scratching` · `syncopated comping` · `syncopated slap` · `vibrato` · `walking bass`

### Rock
`arpeggiated chords` · `power chords` · `shredding` · `staccato electric` · `syncopated rhythm` · `vibrato`

### Ambient
`arpeggiated bells` · `arpeggiated guitar` · `call-and-response` · `looping` · `power chords` · `sampling` · `syncopated hammond`

### Cinematic
`arpeggiated bells` · `arpeggiated synths` · `four-on-the-floor` · `scratching` · `vibrato`

### R&B
`call-and-response` · `syncopated percussion` · `walking bass`

### Choral / Classical
`arpeggiated eighth` · `arpeggiated flourishes` · `arpeggiated octaves` · `arpeggiated patterns` · `block chords` · `legato bass` · `legato counter` · `legato pads` · `legato phrasing` · `legato violins` · `rubato` · `syncopated piano` · `vibrato`

### Fusion
`four-on-the-floor` · `glissando` · `staccato rhythmic` · `vibrato` · `walking bass`

### Hip Hop / Trap
`sampling` · `scratching` · `sidechain` · `syncopated kick` · `syncopated slap`

### Dream Pop / Shoegaze
`arpeggiated bells` · `scratching` · `sidechain` · `syncopated kick` · `vibrato`

---

## 4. 장르별 고유 악기 — Suno가 구분하는 것들

"공통 악기"(bass, drums, piano, guitar 등)를 제외하고, 특정 장르에서만 등장하는 악기.

### Jazz 전용
`saxophone` · `trumpet` · `trombone` · `upright bass` · `vibraphone` · `rhodes piano` · `clarinet` · `flute` · `marimba` · `kora` · `oud` · `sitar`

### Rock 전용
`clean guitar` · `distortion guitar` · `overdriven guitar` · `wurlitzer` · `xylophone`

### Choral/Classical 전용
`pipe organ` · `grand piano` · `oboe` · `timpani` · `string section` · `woodwinds`

### Hip Hop 전용
`mpc` · `sampler` · `turntable`

### Dream Pop 전용
`synth lead`

---

## 5. Mood/Emotion 지도 — 장르별 감정 DNA

Suno가 각 장르에 부여하는 감정 형용사. SP의 tone 설정에 직접 활용.

| 장르 | 핵심 무드 | 차별화 키워드 |
|------|----------|-------------|
| jazz | warm, smooth, dreamy | euphoric, introspective, serene |
| rock | raw, gritty, powerful | anthemic, energetic, epic |
| ambient | ethereal, dreamy, calm | cold, hypnotic, tender |
| cinematic | epic, powerful, dark | intense, cold, haunting |
| r&b | smooth, warm, groovy | tender, funky, hypnotic |
| dream pop | dreamy, ethereal, warm | contemplative, tender, haunting |
| folk | warm, nostalgic, gentle | meditative, sparse, anthemic |
| soul | warm, groovy, gritty | funky, anthemic, meditative |
| classical | majestic, powerful, lush | (감정 어휘 적음 — 구조적 묘사 위주) |
| shoegaze | (mood 필드 없음) | timbre로 대체: fuzzy, distorted, thick |

---

## 6. Production 시그니처 — 장르별 사운드 질감

SP에서 production 스타일을 지정할 때 Suno가 반응하는 표현.

| 장르 | Production 키워드 |
|------|-----------------|
| jazz | vinyl crackle, tape saturation, room reverb, wide stereo |
| rock | heavy distortion, analog saturation, plate reverb, raw production |
| ambient | atmospheric production, clean mix, subtle reverb, lo-fi aesthetic |
| cinematic | raw production, room reverb, vinyl crackle, wide stereo |
| r&b | atmospheric production, light reverb, warm tone, vinyl hiss |
| dream pop | atmospheric production, heavy reverb, vinyl crackle |
| hip hop | vinyl crackle, wide stereo |
| shoegaze | heavy reverb, tape saturation |
| choral | hall reverb, vinyl crackle, wide stereo |

---

## 7. Timbre 팔레트 — 장르별 음색 어휘

| 장르 | 고유 Timbre | 공통 제외 차별화 |
|------|-----------|----------------|
| jazz | husky, muffled, harsh, breathy | 보컬 질감 묘사 풍부 |
| rock | fuzzy, overdriven, nasal, raspy | 기타 톤 묘사 특화 |
| r&b | silky, husky, raspy | 보컬 부드러움 강조 |
| shoegaze | fuzzy, distorted, thick | 노이즈/왜곡 중심 |
| cinematic | glassy, thin, cold | 차가운 질감 표현 |
| soul | raspy, thick, full | 따뜻한 아날로그 톤 |
| classical | resonant, full, rich | 홀 울림 중심 |
| folk | raspy, breathy | 자연스러운 보컬 |

---

## 8. 핵심 발견 & SP 활용 가이드

### 발견 1: Suno는 "감정 + 질감" 조합으로 장르를 구분한다
- 같은 악기(guitar, bass)라도 timbre + mood 조합이 장르를 결정
- 예: `warm smooth guitar` → jazz / `gritty distorted guitar` → rock

### 발견 2: Production 키워드가 시대감을 결정한다
- `vinyl crackle` + `tape saturation` → 빈티지/아날로그
- `atmospheric production` + `wide stereo` → 현대적/공간감
- `heavy reverb` → dreamy/shoegaze 계열

### 발견 3: Technique 용어가 가장 강력한 SP 무기
- `walking bass` 하나로 jazz feel 확정
- `power chords` → 즉시 rock
- `arpeggiated` 계열 → 클래식/앰비언트 텍스처

### 발견 4: 데이터 부족 장르는 추가 수집 필요
- alt rock(2), amapiano(2), flamenco(3), math rock(3) → Phase 4에서 보강

---

## 9. 다음 단계

1. **500곡+ 확보 후**: Casini INPUT(사용자가 넣은 프롬프트) vs Suno OUTPUT(Suno 자체 묘사) 비교
2. **MusicSem/ConceptCaps 매핑**: 학술 음악 온톨로지와 Suno 어휘 대응표
3. **데이터 부족 장르 보강**: flamenco, math rock, darkwave 등 타겟 수집
4. **LeoMusic2 연동**: 이 인사이트를 SP 생성 파이프라인에 반영
