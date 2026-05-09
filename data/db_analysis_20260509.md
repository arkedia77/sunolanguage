# suno_reanalysis DB 분석 보고서 (2026-05-09)

## 데이터 현황
- 총 385행: W1 326행 + S003 12 + S004 12 + S016 10 + S017 9 + S018 16
- W1: reanalysis_genre NULL → reanalysis_sp 첫 문장에서 추출 (162개 고유 장르)
- S시리즈: reanalysis_genre 전부 있음 (52개 고유 장르)

## 대장르 분포

| 대장르 | 행수 | 소스 |
|--------|------|------|
| K-Ballad | 162 | W1 전부 |
| K-Indie | 40 | W1 전부 |
| K-Pop (기타) | 27 | W1 24 + S016 3 |
| K-Funk Pop | 26 | W1 전부 |
| K-Rock | 25 | W1 전부 |
| K-Hip Hop | 19 | W1 전부 |
| Bossa Nova | 12 | S003/S004/S016/S017/S018 |
| K-R&B | 12 | W1 전부 |
| K-City Pop | 11 | W1 전부 |
| Classical/Orchestral | 10 | S003/S004/S016 |
| Jazz | 9 | 다수 S시리즈 |
| Electronic | 6 | S004/S018 |
| Folk/World | 5 | S004/S016/S018 |

## W1 특성: K-Pop 75.5% 편향
- Ballad 50%, Indie 23%, R&B 15%, Rock 12%, Funk 10%
- 한국 음악 원곡을 Suno가 재분석한 결과 → K-접두어 장르가 지배적

## 사전 v3.0 미등재 핵심 어휘 (DB에서 ≥10회)

### 연주 기법 / 음악 이론
| 어휘 | 빈도 | 최다 장르 |
|------|------|-----------|
| counterpoint | 40 | K-Ballad |
| strumming | 30 | K-Ballad |
| walking (bass) | 28 | Jazz |
| arpeggios | 19 | K-Ballad |
| polyphonic | 14 | K-City Pop |
| runs | 16 | Jazz |
| leaps | 14 | K-Ballad |
| hammer-ons | 12 | K-Ballad |
| rolls | 12 | K-Hip Hop |

### 음색 / 질감
| 어휘 | 빈도 | 최다 장르 |
|------|------|-----------|
| rounded | 34 | K-Ballad |
| mid-range | 24 | K-Indie |
| low-end | 13 | K-Ballad |
| sub-heavy | 18 | K-Ballad |
| resonance | 12 | K-Ballad |
| timbre | 13 | K-Ballad |

### 리듬 / 템포
| 어휘 | 빈도 | 최다 장르 |
|------|------|-----------|
| downbeats | 24 | K-Ballad |
| mid-tempo | 24 | K-Ballad |
| eighth (note) | 28 | K-Rock |
| four-bar | 13 | K-Ballad |

### 스타일 수식어
| 어휘 | 빈도 | 최다 장르 |
|------|------|-----------|
| jazz-influenced | 35 | K-Ballad |
| high-energy | 17 | K-Rock |
| powerful | 22 | K-Ballad |

## 장르별 고유 어휘 (사전 미등재)

### Bossa Nova
brushes, clave, nylon, improvisational, solos, triangle, comping, call-and-response

### Jazz
pompe, chromatic, vibrato-heavy, accompaniment

### Classical
ostinatos, passages, woodwinds, trills, ensemble, characterized

### Folk/World
fiddle, whistle, tin, bodhran, chordal

### Electronic
sweeps, supersaw, roland, four-on-the-floor

### K-Funk
funk-pop, pops, punctuate, ad-libs

### K-Hip Hop
rapper, rapping, boom-bap, rapid-fire, flow

## 가사 브라켓 태그 (상위)
- 섹션: Intro(376), Verse 1(342), Chorus(230), Outro(61), Pre-Chorus(59)
- 악기 큐: fingerpicked acoustic guitar(29), bass guitar enters(18), kick drum enters(15)
- 보컬 큐: breathy male vocals(58), breathy female vocals(28), male vocals(25)

## 괄호 () 태그
- 감탄사/허밍: Hmm-mm(10), Ooh-ooh(4), Humming(4), Woo-hoo!(4)
- 한국어: 우후(4), 음-(2)

## 인사이트

1. **사전 v3.0 확장 필요**: 50+ 미등재 어휘가 DB에서 10회 이상 등장 → 네이티브 확정
2. **K-장르 편향**: W1이 326/385행(85%)을 차지, 한국 음악 중심 → S시리즈로 다양성 보완 중
3. **counterpoint = Suno 핵심어**: 40회 등장, 사전 미등재 1위. Suno가 대위법적 배치를 자주 인지
4. **jazz-influenced**: K-Ballad에서 19회 — Suno가 한국 발라드에서 재즈 영향을 자주 감지
5. **rounded/sub-heavy/low-end**: 저음 관련 질감 어휘가 사전에 부재
6. **가사 브라켓**: Intro/Verse/Chorus 섹션 마커 + 악기 큐 + 보컬 질감 큐의 3가지 용도
