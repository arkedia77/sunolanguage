# leomusic-trot/W005 SP 정밀검토 — '장마,도시' 10곡 (실험축 E: 떼창 인라인 브라켓)

- **검토자**: sunolanguage
- **수신**: 2026-06-19 (06-27 재촉) / **회신**: 2026-06-30
- **배치**: `~/leomusic-trot/batches/trot/W005/` (song01~song10)
- **방법**: 가사 브라켓 코퍼스 + `data/reanalysis_v2/lexical_index.sqlite` (v3.2, 496곡) phrases/entries LIKE, distinct-song 카운트
- **종합 평결**: **조건부 PASS** — 골격·악기·서브장르 앵커 GT 정합. 단 ★떼창 브라켓 3종이 컴파운드 dead-zone(곡 01·04·10 국한), SP 전곡 과포화 근접대(910~950자, 5곡 ≥943). 어휘 분리/트림 권고.

---

## 관점① 떼창 브라켓 attestation (leomusic-trot/W007 교차검증과 겹침 → 상당부분 완료)

W005 축E와 leomusic-trot/W007 축G가 `[call-and-response shouts]` 브래킷을 공유 → call-and-response는 W007 검토에서 이미 attested 확정(v3.2 **29곡**). 추가 검증:

| 브래킷 어휘 | v3.2 | 판정 |
|---|---|---|
| call-and-response (shouts) | 29곡 / shouts 4곡 | ✅ attested |
| chant / chanting | 12곡 / 2곡 | ✅ (단독) |
| gang vocals | 1곡 | ✅ (thin) |
| **gang vocals chant / chanting** (컴파운드) | **0곡** | ⚠️ **DEAD-ZONE** |
| **crowd singalong / singalong** | **0곡 / 0곡** | ⚠️ **DEAD-ZONE** |
| sing-along (하이픈) | 2곡 | ✅ (thin) |
| group vocal / vocal shout | 1곡 / 1곡 | ✅ (thin) |
| falsetto (ad-lib) | 94곡 / 5곡 | ✅ |

→ **권고**: `[gang vocals chant]`→`[gang vocals]`+`[chanting]` 분리, `[crowd singalong]`→`[crowd sing-along]`(하이픈, thin) 또는 `[group vocal sing-along]`로 대체. call-and-response·belted·breathy·vibrato·falsetto 계열은 전부 GT-safe.

## 관점② W001 산문 → W005 브라켓 이식 정합

leomusic-trot/W001은 떼창을 **SP 산문**으로 기술("a gang singalong chorus and call-and-response shouts", "crowd singalong feel", "Crowd handclaps and gang vocals chanting build a plaza"). W005는 이를 **인라인 가사 브라켓**으로 이식.

- **call-and-response shouts** — 산문·브라켓 양형 모두 attested(29곡). ✅ **클린 이식**.
- **gang vocals chant(ing)** — 산문에선 주변 문맥이 carry했으나, 고립된 브라켓 컴파운드는 0건. → 이식이 dead-zone을 노출.
- **gang/crowd singalong** — ★**산문 원형(W001)부터 이미 0건**(gang singalong 0 / crowd singalong 0). 브라켓 이식이 미렌더 어휘를 그대로 옮긴 것 — 이식 자체 결함이 아니라 **원천 어휘가 미attested**. 컴파운드 분해(crowd + sing-along + gang vocals)로 해소 필요.

→ **결론**: 이식 메커니즘은 건전(call-and-response 실증). 단 W001 산문에 잠재했던 미attested 떼창 어휘가 브라켓화로 **가시화**됨. 수정은 이식방식이 아닌 어휘층에서.

## 관점③ 서브장르 어휘

- 서브장르 컴파운드 **City Pop / R&B / Synth / Funk / Modern Korean / Trap Trot** = literal 0건이나 **기지 패턴**(leomusic-trot/W004 검토 결론 재확인). 전곡 `Trot, Korean adult contemporary.` 선행 앵커 → 'Korean adult contemporary'가 렌더 carry(W004 실증과 일치). ✅ 앵커 전략 정합.
- 악기 어휘 전건 attested: accordion / octave electric bass / city pop synth pad / analog synth arpeggio / slap bass·thumb-pop / wah guitar / 808 bass / trap hi-hat rolls / upright(walking) bass / tenor saxophone / brushed snare / brass stabs.
- ⚠️ **song06 `City Pop Trot, Gen4`** — 'Gen4'는 leomusic-trot 내부 세대 마커, GT 어휘 아님(미렌더 토큰). SP에서 제거 권고.
- song06 한국어 의성어 SP/브라켓 삽입('룰루랄라'·'반짝반짝'·'신난다', `[falsetto ad-libs: 우우~ 신난다!]`) — 가사 ad-lib 내용이라 무해(falsetto ad-lib attested 5곡).

## 관점④ SP 과포화

전 10곡 **910~950자**. 분포: 910·941·922·943·945·936·943·948·938·950. **5곡(04·05·07·08·10) ≥943**.

- 과포화 가설([[project_sp_saturation_hypothesis]]): B192 964~999자 구간 폐기 다발. W005 최대 950 → **실패 임계(964) 직하, 여유 ~14자**.
- 구조적 중복: 전곡 `Trot, Korean adult contemporary.`(≈31자) + 서브장르 재기술 + 장문 씬묘사(01·06·08·09 말미). 트림 여지.
- **판정**: 하드 실패 아님(전곡 <964). 단 균질 고밀도 패킹이라 헤드룸 얇음. **권고: ≥945자 3곡(05·08·10) 씬묘사·중복앵커 ~20-30자 트림으로 안전마진 확보**.

---

## 곡별 요약 (song01~song10)

| # | 서브장르 | SP자 | 떼창브라켓 | dead-zone | 곡평결 |
|---|---|---:|---|---|---|
| 01 | City pop/disco Trot | 910 | gang vocals chant×2, call-and-response shouts, belted, ad-lib | gang vocals chant | ⚠️ 어휘분리 |
| 02 | R&B Trot ballad | 941 | breathy/vibrato 표준 | — | ✅ |
| 03 | Synth Trot | 922 | belted+vibrato 표준 | — | ✅ |
| 04 | Funk Trot | 943 | gang vocals chanting×2, crowd singalong, call-and-response | chanting 컴파운드 + crowd singalong (★최다 떼창) | ⚠️ 어휘분리 |
| 05 | Modern Korean Trot | 945 | breathy/vibrato 표준 | — | ✅(트림권고) |
| 06 | City Pop Trot "Gen4" | 936 | falsetto ad-libs, belted 복합 | 'Gen4' 비GT토큰 / handclaps on every beat 0 | ⚠️ Gen4 제거 |
| 07 | R&B Trot ballad | 943 | breathy/baritone vibrato 표준 | — | ✅ |
| 08 | Trap Trot (half-time) | 948 | belted/vibrato/ad-lib 표준 | — | ✅(트림권고) |
| 09 | Synth Trot | 938 | breathy/vibrato 표준 | — | ✅ |
| 10 | Modern Korean Trot | 950 | crowd singalong | crowd singalong (★최장 SP) | ⚠️ 어휘대체+트림 |

## 권고 요약 (findings — 자동승격 금지, leomusic-trot 재분석)
1. **떼창 어휘 dead-zone 해소**(곡 01·04·10): `[gang vocals chant(ing)]`→`[gang vocals]`+`[chanting]`, `[crowd singalong]`→`[crowd sing-along]` 또는 `[group vocal sing-along]`.
2. **song06 'Gen4' 제거**(비GT 내부 마커), `handclaps on every beat`→`handclaps`(attested).
3. **SP 트림**(곡 05·08·10, ≥945자): 중복 앵커/씬묘사 ~20-30자 절감으로 964 임계 마진 확보.
4. 골격(male lead·heavy vibrato·traditional phrasing·call-and-response·서브장르 앵커·악기) 전건 GT-safe — 재생성 불요, 위 3건만 핀포인트 수정.
