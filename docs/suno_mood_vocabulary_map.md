# Suno 네이티브 심리·분위기 어휘 예상확장 지도

**작성**: 2026-07-03 · **소스**: lexical_index (현행 556곡, distinct song 기준) · **계기**: 패션필름 D&G SP의 `suspense` 관찰 → 심리상태/환경분위기 어휘 전수 채굴

> **전제**: 여기 실린 단어는 전부 **Suno가 오디오 분석으로 스스로 생성한** 어휘(=Suno 네이티브). 우리가 추정한 게 아니라 Suno가 실제 음악을 묘사할 때 쓴 말. [[project_suno_vocabulary_insight]] "구조적 어휘 강·감성적 어휘 약" 가설의 실측 근거.

---

## 밀도 계층 (distinct song 수)

| 계층 | 기준 | 성격 |
|---|---|---|
| **CORE** | ≥30곡 | Suno가 확실히 반응. SP 1순위 사용 |
| **SOLID** | 10~29곡 | 안정적. 사용 권장 |
| **THIN** | 2~9곡 | 렌더되나 약함. 단독보다 보강어와 |
| **TRACE** | 1곡 | 극약. 대체어 권장 |
| **DEAD** | 0곡 | 미렌더. 회피 + 대체 |

---

## A. 심리 상태 (Psychological States)

### A1. 따뜻함·친밀 (CORE — Suno 최강 감성축)
`warm`(527) · `intimate`(471) · `soft`(411) · `gentle`(183) · `tender`(48) · `delicate`(21)
→ **Suno 감성어휘의 심장부.** 따뜻/부드러움 계열은 구조어급 밀도. K-ballad/R&B/acoustic SP의 기본 팔레트.

### A2. 우수·그리움 (SOLID~THIN — 한국 정서 핵심이나 밀도 급락)
`nostalgic`(48) · `bittersweet`(43) · `melancholic`(20) · `vulnerable`(19) · `longing`(13) · `melancholy`(7) · `wistful`(4) · `aching`(3) · `yearning`(3)
→ ★한국 음악의 '한(恨)' 정서인데 `melancholic` 20 / `longing` 13으로 **의외로 thin**. `wistful`·`aching`·`yearning`은 거의 안 씀. **함의**: 그리움을 SP에 넣을 땐 `nostalgic`(48)·`bittersweet`(43)을 앵커로, 미세결(`wistful`/`yearning`)은 보강용.

### A3. 내성·사색 (SOLID)
`contemplative`(68) · `introspective`(38) · `reflective`(22) · `meditative`(24)
→ 사색축은 견고. lo-fi/ambient/발라드 인트로에 안정적.

### A4. 고양·환희 (THIN — 뜻밖의 약점)
`joyful`(10) · `triumphant`(10) · `uplifting`(9) · `euphoric`(6) · `cheerful`(6) · `hopeful`(6)
→ ★긍정·고양 감정이 **전부 THIN**. Suno는 밝음을 감정어(`joyful`)보다 음향어(`bright` 336)로 표현하는 경향. **함의**: 신나는 곡도 `euphoric`보다 `bright`+`energetic`+템포/악기로.

### A5. 긴장·불안·공포 (tension만 CORE, 나머지 붕괴)
`tension`(84, CORE) · `anxious`(13) · `urgent`(7) · `nervous`(6) · `tense`(3) · `restless`(2) · `frantic`(2) · **`suspense`(2, ← 패션필름 계기어)** · `uneasy`(1)
DEAD: `suspenseful`(0) · `foreboding`(0) · `desperate`(0) · `hopeless`(0)
→ ★★**가장 뚜렷한 갭.** 긴장의 기능어 `tension`은 84곡인데, 그 감정의 결(`suspenseful`/`foreboding`/`desperate`)은 **0곡**. **함의**: 공포·서스펜스는 `tension`+렌더수단(`dissonant`/minor key/`ominous` drone)으로. 형용사 확장(`suspenseful`)은 회피.

### A6. 어둠·위협 (THIN~TRACE)
`dark`(55, SOLID) · `brooding`(2) · `menacing`(2) · `ominous`(2) · `moody`(2) · `haunting`(1) · `eerie`(1) · `dread`(1)
DEAD: `sinister`(0) · `grim`(0) · `bleak`(0)
→ `dark`(55)만 CORE급, 나머지 어둠 형용사는 전부 THIN/TRACE/DEAD. 어둠 표현도 `dark`+음향(`dissonant`/`industrial`/minor)으로 수렴.

### A7. 저항·힘 (THIN)
`defiant`(17, SOLID) · `confident`(10) · `bold`(5) · `rebellious`(3) · `fierce`(2) · `heroic`(2) · `angry`(1)
DEAD: `empowering`(0)
→ `defiant`(17)이 저항축 대표. 나머지 thin.

### A8. 관능·낭만 (THIN — 대부분 음향어로 우회)
`romantic`(14) · `passionate`(3) · `smoky`(3) · `sultry`(1)
DEAD: `sensual`(0) · `seductive`(0)
→ ★관능 형용사 `sensual`·`seductive`가 **0곡**. Suno는 관능을 `smoky`(음색)·`sultry`로 우회. **함의**: 섹시한 무드는 `smoky vocals`·`sultry`로.

### A9. 슬픔·상실 (TRACE~DEAD)
`grief`(8) · `somber`(3) · `mournful`(2) · `despairing`(2)
DEAD: `sorrowful`(0) · `heartbroken`(0) · `desolate`(0) · `lonesome`(0)
→ 직접적 슬픔 형용사는 거의 dead. `grief`(8)·`mournful`(2)이 그나마. 슬픔도 `melancholic`+`aching`+minor로.

---

## B. 환경·공간 분위기 (Environmental Atmosphere)

### B1. 공간·질감 (CORE~SOLID)
`atmospheric`(143, CORE) · `ambient`(134, CORE) · `spacious`(29) · `ethereal`(35) · `dreamy`(33) · `hazy`(5) · `cavernous`(4) · `expansive`(6)
DEAD: `misty`(0) · `foggy`(0) · `immersive`(1)
→ 공간감은 `atmospheric`/`ambient`가 CORE. 안개류(`misty`/`foggy`)는 0 — `hazy`(5)로 대체.

### B2. 시대·질감 미학 (SOLID)
`retro`(34) · `urban`(34) · `vintage`(23) · `gritty`(54) · `raw`(47) · `nocturnal`(12) · `neon`(5)
DEAD: `dystopian`(0) · `futuristic`(0)
→ 레트로·도시·거친질감 견고. 미래/디스토피아 형용사는 0 → `industrial`+`dark electronic`으로 우회.

### B3. 평온·냉기 (THIN)
`serene`(14) · `calm`(7) · `peaceful`(6) · `cold`(11) · `cozy`(3) · `fragile`(3)
DEAD: `tranquil`(0) · `icy`(0) · `soothing`(1)
→ `serene`(14) 대표. `tranquil`·`icy` dead → `serene`/`cold`로.

### B4. 씬 명사 (분위기 앵커로 유효)
`rain`(68, CORE) · `chamber`(17) · `dawn`(7) · `midnight`(6) · `neon`(6) · `shadow`(4) · `cavern`(4) · `cathedral`(3) · `mist`(3) · `dusk`(2)
DEAD: `cosmic`(0) · `dreamscape`(0)
→ ★`rain`(68)은 씬어휘 중 최강(장마·비 정서 곡 다수). 분위기 앵커로 씬명사가 형용사보다 강한 경우 있음.

---

## C. 예상확장 원칙 (dead-zone → attested 대체 규칙)

Suno가 **아직 안 쓴 심리/분위기 형용사를 SP에 쓰려 할 때**의 치환 규칙:

| 쓰고 싶은 (DEAD) | Suno 네이티브 대체 |
|---|---|
| suspenseful / foreboding | `tension` + `dissonant` / `ominous` drone |
| sinister / grim / bleak | `dark` + `menacing`(2) / minor key |
| desperate / hopeless | `aching` + `urgent` / `despairing`(2) |
| sorrowful / heartbroken | `melancholic` + `grief`(8) / `mournful`(2) |
| sensual / seductive | `smoky` (음색) + `sultry`(1) |
| misty / foggy | `hazy`(5) + `atmospheric` |
| tranquil / icy | `serene`(14) / `cold`(11) |
| dystopian / futuristic | `industrial` + `dark electronic` |
| ecstatic / euphoric(강) | `bright` + `energetic` + 템포 |

---

## D. 종합 인사이트 (SP 전략·책 반영)

1. **Suno의 감성축은 "따뜻함"에 편중** — `warm`(527)/`intimate`(471)/`soft`(411)이 구조어급. K-ballad/R&B가 코퍼스 주류인 결과.
2. **기능어는 CORE, 감정의 결은 THIN/DEAD** — `tension`(84) vs `suspenseful`(0), `dark`(55) vs `sinister`(0), `bright`(336) vs `euphoric`(6). Suno는 감정을 **형용사보다 음향·구조로** 표현. → 이것이 "감성적 어휘 약"의 정체.
3. **SP 작성 규칙**: 심리/분위기는 ①CORE 앵커(`warm`/`tension`/`atmospheric`/`dark`/`nostalgic`) 1개 + ②렌더 수단(악기·음색·조성·템포)으로 결을 냄. **미세 감정형용사 단독 의존 금지**(0곡 다수).
4. **한국 정서 갭**: 그리움/한(`longing` 13·`yearning` 3)이 정서 중요도 대비 thin. `nostalgic`+`bittersweet` 앵커 + `aching` 보강이 현실적.

## 다음
- dead-zone 감정형용사 후보를 suspicion_tracker 등재 검토 → 향후 배치 재분석에서 등장 여부 추적
- 이 지도를 책 5장(감성어휘 전략) 원자재로 편입
