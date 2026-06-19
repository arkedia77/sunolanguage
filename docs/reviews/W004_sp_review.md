# W004 SP 검토 (leomusic-trot, 2026-06-19)

**베이스**: lexical_index v3.2 (556트랙 / 17,822 entries) · 네이티브 GT만 판정
**검토 의뢰**: 동아시아 전통색을 "서술형 근사 음색"으로만 구현(명명태그 0)한 실험축 B의 GT정합
**회신 원칙**: findings(attestation 사실) 채택, recommendation(치환 권고)은 LM-Trot 재분석

---

## 종합 평결: 실험축 B(서술형 전통색) = **GT-SOUND PASS** (수식어 2종만 정정 권고)

핵심 결론 — 동아시아 전통색을 명명태그 대신 **서술형 근사 음색**으로 구현한 접근은 GT에 근거가 있습니다. 직전 회신(명명태그 전멸 → 서술형만 attested)을 정확히 적용했고, 골격 어휘가 전부 attested입니다.

---

## ① 전통색 서술형 음색 GT정합 (핵심)

| 구성요소 | GT hits | 판정 |
|---|---|---|
| `resembling` | 7 | ✅ attested |
| `resembling a gayageum` | 3 | ✅ attested (C_1710 패턴) |
| `plucked string` | 3 | ✅ attested |
| `bowed string` | 3 | ✅ attested |
| `glissando` | 25 | ✅ 강하게 attested |
| `zither` / `zither-like` / `plucked zither` | 0 | ⚠️ 미검증 |
| `vocal-like glissando` (구) | 0 | ⚠️ 구 단위 미검증(단 glissando 단독 25) |

**판정**: 골격("plucked string resembling a gayageum" / "bowed string ... glissando")은 전부 GT-attested → Suno가 전통색 음색으로 렌더할 근거 있음. 실험축 B 타당.

**정정 권고(2종, recommendation)**:
- `a plucked zither-like string resembling a gayageum` → **`a plucked string resembling a gayageum`** (zither-like 제거 = C_1710 축자형). "zither" 0건이라 노이즈 위험.
- `a bowed string with vocal-like glissando` → **`a bowed string with glissando`** (vocal-like 제거 권고, 단 glissando 25로 강해 현행도 저위험).

## ② 명명 단독태그 0 확인 — 부분 통과, 1건 플래그

- 악기 명명 단독태그: gayageum/haegeum/erhu **단독 사용 0 확인** ✅ (haegeum 0·erhu 0, gayageum 7건은 전부 "resembling" 서술형).
- ⚠️ **`Gukak Trot` 서브장르 라벨**(song 05/06/07 오프닝): `gukak` 0건 / `gukak trot` 0건 — **장르 라벨 'Gukak'은 GT-unattested**. Suno가 'Gukak'을 인식 못 해 무시·드롭하고 앵커("Trot, Korean adult contemporary" 3건 attested)로 폴백할 가능성 높음. 색채는 ①의 서술형이 carry하므로 실해는 낮으나, **'Gukak'이라는 명칭 자체는 렌더 안 됨**. (LM-Trot의 descriptive_timbre_only 슬롯 정책과 라벨이 다소 불일치 — 사적 명칭으로 둘지/앵커 서술로 바꿀지 재분석 영역.)

## ③ 서브장르 라벨 — 기지(旣知) 패턴, 앵커가 carry

`City Pop Trot`·`Synth Trot`·`Funk Trot`·`R&B Trot`·`Trap Trot`·`Modern Korean Trot` = **전부 0건**. W001/W002에서 확인된 트로트 패턴(컴파운드 서브장르명은 비-native, Suno는 트로트를 K-Pop으로 라벨). **앵커 `Korean adult contemporary`(3) + 식별3종(accordion 35·heavy vibrato 8·traditional phrasing 2)이 보정** — 전부 attested. 정합.

## ④ 악기 어휘 — 양호 (1건 플래그)

| 악기 | GT | | 악기 | GT |
|---|---|---|---|---|
| four-on-the-floor | 74 ✅ | | tenor saxophone | 7 ✅ |
| slap bass | 608 ✅ | | wah guitar | 17 ✅ |
| upright bass | 235 ✅ | | 808 sub-bass | 8 ✅ |
| brushed snare | 51 ✅ | | handclaps | 20 ✅ |
| glockenspiel | 33 ✅ | | accordion | 35 ✅ |

- ⚠️ `octave disco bass`(song01) = 0건(구 단위). "disco"/"octave bass" 분해 가능성 있으나 구 자체는 미검증 → 점검 권고.

## ⑤ SP 예산
698~894자, 전곡 ≤900 — 과포화 회피 정책 준수 ✅ (W001-09 930자 컷 교훈 반영 확인).

---

## 정정 요약 (recommendation — LM-Trot 재분석)
1. `zither-like` 제거 → `a plucked string resembling a gayageum` (필수 권고, zither 0건)
2. `vocal-like` 제거 → `a bowed string with glissando` (권고, 현행 저위험)
3. `Gukak Trot` 라벨: 'gukak' 0건 인지 — 사적 명칭/앵커 폴백 전제로 사용하거나 서술 대체 (판단 위임)
4. `octave disco bass`(song01) 점검

**ledger #5 핵심 답**: 전통색 서술형은 dead-zone(명명태그)을 회피하면서 attested 골격으로 색채를 살림 → **GT 사전판정 통과**. Leo 청음으로 실렌더 확인 단계 권함.
