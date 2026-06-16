# UK Garage SP — 원본(태그식) vs 우리 문법·코퍼스 재작성 A/B

**목적**: Leo 제시 UK Garage House SP가 "너무 좋은 음악"을 냈다 → 동일 의도를 **우리 문법(Suno-native 산문) + GT 코퍼스 어휘**로 재작성해 생성·청취 비교. 우리 방식이 동등/우위인지 검증.
**작성일**: 2026-06-16. 검증 베이스: sunolang lexical_index v3.2.
**주의**: 작동 이유(layer-2 수동이해 등)는 가설이며, 본 A/B 청취가 검증 수단(확정 아님).

---

## A. 원본 (Leo 제시 — 태그식)

> Uk Garage House At 124 Bpm, Crisp Two-Step Groove, Swung Shuffle Hats, Tight Clipped Claps, Punchy Sidechained Kick, Elastic Bassline, Low Piano Stabs, Funky Acid-Jazz Guitar Accents, Polished Female Lead Vocal, Soulful But Controlled Delivery, Short Diva Hook Phrases, Clear Transient Attack, Open Upper Mids, Airy Top End, Wide Stereo Percussion, Clean Low-Mid Separation, Tight Sub Bass, Bright Club Mix, Glossy But Not Harsh, Early-2000S London Nightlife Energy, Elegant Fashion-Forward Attitude, Gradual Build, Strong Drop, Rhythmic Post-Drop, No Muddy Reverb, No Boomy Bass, No Dense Layering

- 형식: 콤마 태그나열 + 전 단어 Title Case
- 길이: ~1,050자 (태그 27개)
- 단어단위 코퍼스 커버리지: 81% / 구절단위 dead-zone ~60%(uk garage·two-step·믹스자갈)

## B. 재작성 (우리 문법 — Suno-native 산문)

> UK garage at 124 BPM, 4/4 time. A swung two-step groove with shuffled hi-hats, tight handclaps, and a punchy sidechained kick. A deep elastic bassline and tight sub-bass anchor the low end while low piano stabs and funky jazz-influenced electric guitar accents land on the off-beats. A polished female lead delivers soulful, controlled vocals with short, powerful hook phrases and light ad-libs. Bright, glossy production with airy highs and wide stereo percussion. The arrangement builds gradually into a strong drop, then settles into a rhythmic post-drop breakdown. Early-2000s London dancefloor energy, clean and uncluttered.

- 형식: 완전한 산문 + sentence case (1~3장 슬롯문법 순서: 장르/BPM → 그루브/드럼 → 베이스 → 악기 → 보컬 → 프로덕션 → 구조)
- 길이: **629자** (native 표준 500~700, 과포화 회피)
- 단어단위 커버리지: **84%**

## 변환 매핑 (무엇을 바꿨나)

| 원본(태그) | 재작성(native) | 이유 |
|---|---|---|
| Title Case 태그나열 | sentence-case 산문 | Suno 재분석 출력 형식(1~3장) |
| Crisp Two-Step Groove | swung two-step groove (swung 21·shuffle 13 attested) | 형용사 자갈 정리 |
| Tight Clipped Claps | tight handclaps (clipped 0건) | dead 형용사 제거 |
| Funky Acid-Jazz Guitar | funky jazz-influenced electric guitar (acid-jazz 0 → jazz-influenced 189) | 치환 |
| Short Diva Hook Phrases | short, powerful hook phrases (diva 0 → powerful 98) | 치환 |
| Clear Transient Attack / Open Upper Mids / Clean Low-Mid Separation | (삭제) | 5장 믹스엔지니어링 데드존 |
| Bright Club Mix / Glossy But Not Harsh | bright, glossy production | 트랙레벨로 |
| No Muddy Reverb / No Boomy Bass / No Dense Layering | "clean and uncluttered"(긍정 치환) | 네거티브 용어가 dead → 긍정 native 표현 |
| 유지(이미 native) | sidechained kick·piano stabs·sub-bass·funky·soulful·polished·wide stereo·build·drop·ad-lib·breakdown | attested |

## 의도적 보존 (미존재지만 캐릭터 유지)
two-step / elastic / glossy / london / dancefloor / early-2000s — 장르·씬 정체성 어휘라 음악의도 보존 위해 유지(layer-2 후보).

## A/B 청취 가설 (검증 대상, 미확정)
- H1: B(산문·629자)가 A(태그·1050자)와 **동등 이상** 품질 → "우리 문법이 더 짧고 안정적으로 같은 결과" 시사 가능성
- H2: A가 더 좋으면 → 태그식·과포화·믹스자갈이 이 장르에서 기여했을 가능성(재검토)
- 어느 쪽이든 **양쪽 곡을 Suno 재분석**해 term별 반영을 보면 layer-2/3 판정 입증 가능

→ 다음: 두 SP 동일 시드/세대로 생성 후 청취. (sunomusic 발주 또는 Leo 직접 생성)
