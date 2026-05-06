# S018 "Genre Frontier + v5.5 Validation" 시리즈 설계

**목적**: corpus ZERO 장르 40개 중 상위 우선순위 16개를 선정, v5.5 신기법(Top-Anchor + 네거티브 프롬프팅)으로 생성 → 재분석 시 새 장르 어휘 대량 수집
**곡 수**: 16곡 (장르당 1곡)
**Axis**: H+ (장르 프론티어 확장)

---

## 설계 원칙

1. **Top-Anchor 구조 적용**: 모든 SP를 v5.5 권장 배치 순서로 작성
2. **네거티브 프롬프팅 포함**: 각 곡에 1~2개 "no X" 배제 지시
3. **SP 길이 500~600자**: 과포화 방지 + 충분한 디렉션
4. **인스트루멘탈 12곡 + 보컬 4곡**: 악기/프로덕션 어휘 수집 극대화
5. **BPM 명시**: 장르 정체성 고정

---

## 16곡 선정 기준

corpus ZERO 40개 중 아래 기준으로 우선 선정:
- Suno 고반응 가능성 (대중적 장르)
- sunolang에 기여도 (독특한 어휘 기대)
- LeoMusic2 SP 작성에 활용 가능성

---

## S018 곡 목록

| # | 장르 | 제목 | Vocal | 핵심 검증 포인트 |
|---|------|------|-------|-----------------|
| 01 | Synthwave | NeonDriveRetro | Inst | gated reverb, analog arpeggios, DX7 |
| 02 | UK Drill | SouthLondonNights | Vocal(M) | sliding 808, rolling hi-hats, plate reverb |
| 03 | Amapiano | LagosToJohannesburg | Inst | log-drum bassline, rolling shaker |
| 04 | Reggaeton | DembowCaliente | Vocal(F) | dembow rhythm, booming bass |
| 05 | Doom Metal | CrushingSludge | Vocal(M) | downtuned sludge riffs, crushing tempo |
| 06 | Drum and Bass | LiquidRoller | Inst | fast breakbeat, rolling sub-bass, 174 BPM |
| 07 | Bebop | BirdFliesAgain | Inst | virtuosic saxophone, walking bass, fast swing |
| 08 | Bluegrass | MountainPickin | Inst | banjo lead, fiddle, high-lonesome |
| 09 | Celtic Folk | TinWhistleDawn | Inst | tin whistle, bodhran, fiddle |
| 10 | Gypsy Jazz | DjangoAfterDark | Inst | hot acoustic guitar, violin, swing |
| 11 | Phonk/Drift | MidnightDrift | Inst | distorted cowbell, aggressive 808 |
| 12 | Acid House | Squelch303 | Inst | 303 bassline, raw rave energy |
| 13 | Cumbia | AccordionFiesta | Vocal(F) | accordion lead, guira, rolling groove |
| 14 | Shoegaze | WallOfSound | Vocal(M) | wall-of-sound guitars, buried vocals, swirling |
| 15 | Afrobeats | CallAndResponse | Inst | call-and-response, log drum, brass stabs |
| 16 | Trance | UpliftingArcs | Inst | supersaw leads, euphoric breakdown, building |

---

## v5.5 검증 요소 (모든 곡에 적용)

### Top-Anchor 테스트
- SP 첫 줄 = "[장르], [무드], [핵심 악기 2개], [보컬/grain]"
- 2줄부터 = 상세 디렉션

### 네거티브 프롬프팅 (곡별 배정)
| 곡 | 네거티브 | 검증 목적 |
|----|----------|----------|
| S018_01 | "no modern production" | 빈티지 강제 여부 |
| S018_02 | "no autotune" | 보컬 처리 배제 |
| S018_05 | "no clean vocals" | 스크림/그라울 강제 |
| S018_06 | "no four-on-the-floor" | 브레이크비트 강제 |
| S018_07 | "no electric instruments" | 어쿠스틱 재즈 강제 |
| S018_10 | "no drums, no percussion kit" | 리듬기타만으로 스윙 |
| S018_14 | "no dry mix" | 리버브/이펙트 강제 |

### SP 길이 테스트 (3곡 변형)
- S018_03: 200자 (초단축)
- S018_08: 500자 (중간)
- S018_12: 900자 (장문)
→ 동일 수준 장르 정체성 유지 여부 비교

---

## 예상 수집 어휘 (장르당)

재분석 시 수집 기대 어휘 예시:
- **Synthwave**: arpeggio, analog synth, gated reverb, 80s, pulsing, neon
- **UK Drill**: sliding 808, triplet hi-hat, minor key, plate reverb, aggressive
- **Amapiano**: log drum, piano chords, shaker, soft vocal, deep bass
- **Bebop**: walking bass, comping, swing, virtuosic, saxophone, uptempo
- **Bluegrass**: banjo, fiddle, picking, high-lonesome, upright bass

---

## 다음 단계

1. 16곡 전체 SP+가사 전문 작성 → `s018_prompts.json`
2. sunomusic 발주 (S007~S015 결과 수신 후 또는 병렬)
3. 생성 결과 → Suno 앱 재업로드 → 재분석 수집
4. 새 어휘를 사전 v3.0에 머지
