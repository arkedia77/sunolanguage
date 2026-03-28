# Timbre Description Guide (TOR 프레임워크 기반)

**채택일**: 2026-03-28
**출처**: McGill ACTOR Project — Timbre and Orchestration Resource (TOR)
**용도**: sunolang 100곡 분석 + LeoMusic2 SP 작성 시 악기 질감 묘사 표준

---

## 1. 팀브르 묘사 3축

| 축 | 설명 | 묘사 예시 |
|----|------|-----------|
| **Spectral** | 주파수 분포, 배음 구조 | bright/dark, nasal/round, thin/full |
| **Temporal** | 어택·디케이·서스테인 패턴 | sharp attack/soft onset, sustained/percussive |
| **Spectrotemporal** | 시간에 따른 스펙트럼 변화 | shimmering, evolving, static, swelling |

## 2. 핵심 디스크립터 10개 (Timbre Toolbox, Peeters 2011)

| 디스크립터 | 측정 대상 | 인간 언어 매핑 |
|-----------|----------|---------------|
| Spectral Centroid | 주파수 에너지 무게중심 | **bright ↔ dark** |
| Attack Time | 소리 시작~피크 시간 | **sharp/percussive ↔ soft/gradual** |
| Spectral Flux | 스펙트럼 변화량 | **shimmering/evolving ↔ static/steady** |
| Roughness | 인접 주파수 간 비팅 | **rough/gritty ↔ smooth/clean** |
| Spectral Spread | 주파수 분포 폭 | **full/rich ↔ thin/narrow** |
| Harmonic Ratio | 정수배 배음 비율 | **tonal/clear ↔ noisy/breathy** |
| Temporal Centroid | 에너지 시간 무게중심 | **front-loaded ↔ sustained** |
| Spectral Irregularity | 배음 간 진폭 불규칙도 | **hollow/woody ↔ dense/metallic** |
| RMS Energy Envelope | 음량 변화 곡선 | **dynamic/expressive ↔ compressed/flat** |
| Spectral Rolloff | 에너지 90% 지점 주파수 | **airy/open ↔ muffled/closed** |

## 3. tone_character 작성 템플릿

```
Spectral: [bright/dark/nasal/round/thin/full 등]
Temporal: [attack 특성, sustain 특성]
Character: [감각적 형용사 2-3개]
Comparable: [유사한 다른 악기/연주자 레퍼런스]
```

### 예시 (Take Five — Paul Desmond Alto Sax)
```
Spectral: dark centroid, low harmonic energy above 3kHz, round tone
Temporal: soft attack, long sustain with gentle decay
Character: silky, dry, airy — "dry martini" quality
Comparable: Lester Young tenor aesthetic but in alto register
```

## 4. Timbrarium — 악기별 소리 팔레트

하나의 악기가 낼 수 있는 모든 가능한 소리를 카탈로그화:

### 현악기 (Strings)
- 전통: arco (활), pizzicato (뜯기), tremolo, vibrato
- 확장: col legno (활 나무), sul ponticello (브릿지), sul tasto (지판), harmonics
- 특수: spiccato (바운스), ricochet, bartók pizz (스냅)

### 건반 (Keys)
- 전통: key strike, sustain pedal bloom
- 내부: string plucking, muting, prepared piano
- 특수: half-pedal, una corda (소프트 페달), celeste pedal

### 관악기 (Winds)
- 전통: legato, staccato, tonguing variations
- 확장: flutter-tonguing, multiphonics, slap tongue, overblowing
- 특수: subtone (서브톤), growl, false fingering

### 타악기 (Percussion)
- 전통: stick, mallet, brush
- 확장: rim shot, cross-stick, dead stroke
- 특수: prepared, bowed cymbal, friction techniques

## 5. 참고 자료

- [TOR](https://timbreandorchestration.org) — 분석/도구/교육 자료
- [OrchARD](https://timbreandorchestration.org/tools) — 검색 가능한 오케스트레이션 DB
- [Timbre Toolbox](https://www.mcgill.ca/mpcl/files/mpcl/peeters_2011_jasa.pdf) — 음향 디스크립터
- [Sound on Sound Classic Tracks](https://www.soundonsound.com/series/classic-tracks) — 녹음 분석
- [Song Exploder](https://songexploder.net) — 트랙별 분해 분석
