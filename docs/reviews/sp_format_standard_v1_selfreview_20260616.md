# SP 형식표준 v1 — sunolanguage 자체 최종검토 (Leo 평가 요청용)

**작성일**: 2026-06-16. 베이스: lexical_index v3.2 (Suno 재분석 SP 505곡 등). 절차: 자체검토 → ★Leo 평가 → (통과) 정식 업데이트 시그널 → 각 라인 DB pull.
**대상**: explore 차용안 A(압축산문)/B(꼬리 장르태그)/C(무드 화이트리스트). 현 상태 = 전체 HOLD.

---

## A. 압축 산문 길이 — ✅ PASS (저위험)

- **근거**: Suno 재분석 SP 505곡 길이 = median **521** · avg **525** · 75%가 400~600자. explore 최상위 Você ~480. 우리 N006+ 안정권 510~566. → ~500자 타깃은 강하게 실증됨.
- **정제 권고**: 평평한 500 대신 **장르 조정**(ch4.5): Ballad ~480 / Rock ~540 / Classical·Orchestral ~700. 상한 1000 유지, 과장황만 지양.
- **리스크**: 낮음. 복잡 편성곡을 500으로 강제하면 악기 디테일 손실 — '타깃'이지 '상한' 아님으로 명시하면 해소.

## B. 꼬리 장르태그 시딩 — ⚠️ CAUTION (최고 불확실, 형식 비-native)

- **어휘 게이트**: 건전 — attested만(glitch 22/phonk 2 OK, reverse swell·riddim·doubled·autotuned 0 reject).
- **★형식 리스크(핵심)**: Suno 재분석 SP **505곡 중 꼬리 CSV태그 형식 = 0건**. 즉 단어는 attested여도 '산문 뒤 콤마 태그나열'이라는 **형식 자체가 우리 코퍼스에 없는 비-native**. explore Lucid에서 작동했으나 Suno 자체 출력엔 부재 — 형식 효과 미검증.
- **권고**: 3안 중 Leo 택일 — ①채택 보류(순수 산문 유지, 장르는 산문 내 서술) ②실험-only(Leo 청음 A/B: 꼬리태그 有 vs 無 비교 후 판정) ③다장르 곡 한정 옵션. **자체검토 의견: ②실험-only 권고**(형식 비-native라 청음 검증 선행).

## C. 무드 화이트리스트 — ✅ PASS (프레이밍 단서)

- **SAFE 28** (native≥3, Suno 실제 출력): bright(724)·intimate(465)·warm(461)·smooth(278)·atmospheric(187)·gritty(68)·funky(65)·airy(50)·cinematic(32)·soulful(31)·melancholic(15)·mellow(11)·ethereal(5) 등. → 구체·음향적 무드어.
- **FORBIDDEN 22** (native 0~2): dreamy·nostalgic·tender·bittersweet·moody·wistful·sultry·haunting·longing·serene·euphoric 등. → 감정·시적 무드어.
- **★프레이밍 단서**: FORBIDDEN은 '우리 코퍼스(556곡) 출력에 없음'이지 'Suno가 입력에서 무시함' 확정 아님(layer-2 가능 — 입력은 이해하나 출력 echo 안 함). 즉 **하드밴 vs 소프트주의** 선택 필요.
- **권고**: SAFE는 양성 register로 적용. FORBIDDEN은 '하드밴'보다 **'Leo 청음 확인 대기'**(dreamy/nostalgic 1~2개를 청음으로 실효 검증) 권고 — 2단 게이트 정합.

---

## Leo 평가 요청 사항 (3건 결정)

| 항목 | 자체검토 | Leo 결정 필요 |
|---|---|---|
| **A** | ✅ PASS | 장르 조정 길이(ch4.5 테이블)를 타깃으로 확정? |
| **B** | ⚠️ 형식 비-native(0/505) | ①보류 / ②실험-only(청음 A/B) / ③다장르 옵션 — 택일 (자체검토=②권고) |
| **C** | ✅ PASS | FORBIDDEN을 하드밴 vs 소프트주의(청음 확인)? (자체검토=소프트주의 권고) |

**자체검토 종합**: A 즉시 적용 가능(장르조정 단서). C 적용 가능(SAFE 적용+FORBIDDEN은 청음 확인). B는 형식이 비-native라 청음 A/B 선행 권고. → **A·C는 Leo 평가 통과 시 시그널, B는 실험 트랙으로 분리** 제안.
