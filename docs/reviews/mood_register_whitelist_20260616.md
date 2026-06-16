# 무드 산문 화이트리스트 (SP 형식표준 v1 / C항) — 정본

**작성일**: 2026-06-16. 베이스: sunolang lexical_index v3.2 + 사전 v3.2 mood_emotion. native = leomusic 자작 SP 제외 Suno 재분석 출력 기준.
**상태**: ⚠️ HOLD — SP 형식표준 v1 전체가 미발효. 배포는 sunolanguage 자체 검토 완료 후 sunolanguage가 직접(LEO 지시 2026-06-16).
**용도**: C "무드 산문 1줄"에 쓸 어휘 통제. FORBIDDEN은 우리가 SP에 쓰지만 Suno 재분석이 echo하지 않는 어휘(native 0~2건).

## SAFE (native ≥3 — Suno가 실제 출력하는 무드 register)

bright(724) · intimate(465) · warm(461) · smooth(278) · punchy(214) · jazz-influenced(189) · atmospheric(187) · powerful(98) · high-energy(80) · aggressive(77) · lush(71) · gritty(68) · funky(65) · airy(50) · energetic(48) · cinematic(32) · dark(32) · soulful(31) · upbeat(29) · delicate(17) · groovy(16) · melancholic(15) · mellow(11) · dramatic(9) · playful(7) · emotional(5) · ethereal(5) · triumphant(5)

→ 경향: **구체·음향적 무드어**(bright/warm/smooth/punchy/atmospheric/gritty/airy)가 Suno-native register.

## FORBIDDEN (native <3 — 우리는 쓰나 Suno 재분석 거의/전무)

bittersweet(0) · breezy(0) · dreamy(0) · euphoric(0) · haunting(0) · hazy(0) · hopeful(0) · hypnotic(0) · longing(0) · moody(0) · nostalgic(0) · reflective(0) · serene(0) · somber(0) · sultry(0) · tender(0) · wistful(0) · yearning(0) · brooding(1) · cold(2) · sentimental(2) · uplifting(2)

→ 경향: **감정·시적 무드어**(dreamy/nostalgic/haunting/wistful/longing/sultry/serene)는 사람이 즐겨 쓰나 Suno 출력엔 없음 = 5장 "추상감정 데드존"의 무드판. 추상감정(happy/sad/angry/euphoric/joyful)도 동일 0건.

## 적용 규칙 (C 발효 시)
1. 무드 산문 1줄은 SAFE 목록에서만.
2. 빌더/검증 게이트에 FORBIDDEN 목록 reject 추가.
3. 신규 무드어는 `scripts/batch_sp_review.py` 또는 lexical_index native count ≥3 확인 후 SAFE 편입.

> 책 5장 보강 후보: "우리는 쓰나 Suno는 echo 안 하는 무드어" = 입력 layer-2(수동이해 가능) ≠ 출력 register. SAFE/FORBIDDEN 경계가 그 실증.
