# Suno explore 4곡 SP 형식 비교 — 우리(leomusic family) 형식 대조

**의뢰**: sunomusic (LEO 지시). explore 첫페이지 산문형 4곡 vs 우리 형식.
**작성일**: 2026-06-16. 검증: sunolang lexical_index v3.2.

## 형식 스펙트럼 (4곡이 한 축을 이룸)

| 곡 / 창작자 | 형식 | BPM·키 표기 | SP길이 | 우리와 유사도 |
|---|---|---|---|---|
| **Você quis brincar** / PACO | ★순수 산문 | "Tempo is 130 BPM in the key of G minor." (문장) | ~480자 | **최고 — 사실상 동일** |
| Lucid Dreaming / Varletine | 산문 + 꼬리 CSV 장르태그 | "128 BPM half-time pulse" (인라인) | ~520자 | 중 (하이브리드) |
| stay with me / melø | 산문 + 꼬리 불릿 강조(`* "..."`)| 없음 | ~430자 | 중 |
| **float.** / WorriedChart | ★라벨형 필드(Genre:/BPM:/Mood:/Vocals:/Production:/Structure:/Imagery:) | "BPM: 150 \| Key: A Minor" (라벨) | ~720자 | 하 (가장 다름) |
| **우리 B249** (gid2326/7) | 순수 산문 문단분리 + 가사 instrument-cue 브래킷 | "118 BPM, 4/4, key of A minor." (자체 행) | ~480~560자 | (기준) |

## ① 구조 유사/상이
- **Você = 우리와 동일축**: 순수 산문, ~500자, 장르→비트→악기→보컬→arrangement→tempo/키. sunomusic 관찰 정확. 우리 형식이 explore 상위곡과 일치함을 외부 검증.
- **float. = 반대축(라벨형)**: 필드 분리. Suno 출력은 항상 산문이라 라벨형은 *입력 작성 편의*형이지 native 출력형 아님 — 단 작동(layer-2 수동이해 가능성). Imagery 필드("wet streets, chrome reflections…")는 무드보드형으로 우리 코퍼스에 없는 표현 다수.
- **Lucid = 장르 시딩**: 산문 뒤 CSV("jazz, techno, synthetic, electric, soul, glitch, edm, world, violin, noise") — 장르/질감 폭을 태그로 추가.
- **stay = 강조 레이어**: 산문 뒤 불릿으로 핵심 디렉티브("heavy vocal harmonies", "soft vocal adlibs") 강조 = Top-Anchor 발상.

## ② 차용/벤치마크
- **Você 압축 산문(~480자)**: 우리 ~500자 표준의 외부 검증 — "짧고 밀도 높은 산문이 정답". (4장 4.5)
- **Lucid 꼬리 장르태그**: 장르 폭 시딩에 유용. ★단 attested 어휘만 — reverse swell(0)/riddim(0)/doubled(0)/autotuned(0) 등은 dead, glitch(22)/phonk(2 희귀)는 살아있음.
- **float. 라벨형**: 복잡 멀티필드 SP를 *사람이 관리*하기 편함(Mood/Structure 분리). 차용 시 "작성 보조 템플릿"으로만, 최종은 산문 변환 권장.
- **stay 불릿 강조**: 핵심 디렉티브 강조 = 우리 Top-Anchor로 이미 일부 커버.

## ③ 가사 브래킷 (Suno-native 태그)
- explore: 소문자 `[verse 1]`/`[chorus]`/`[pre-chorus]`/`[drop]`/`[bridge]` + 일부 fx큐(`[glitch & echo]`/`[catchy synth beatdrop]`/`[heavy synth fadeout]`).
- Você: 브래킷 거의 없음(순수 가사 + 끝 `[Sharp electric guitar solo]` 1개).
- float.: 구조 태그만(`[Intro]`~`[Final Drop]`).
- ★**우리 B249**: 구조 태그 + **instrument-cue 브래킷 풍부**(`[color organ shuffle]`/`[muted trumpet cry]`/`[accordion bellows swell]`/`[walking upright bass tag]`) — explore 4곡보다 **시간축 악기 통제가 정밀**. 2장 브래킷 문법 + W003 검증분과 일치(우리 고유 강점).

## ④ 우리 형식 강점/약점 + 개선
**강점**: ①순수 Suno-native 산문(Você와 동급, 가장 깨끗) ②instrument-cue 브래킷 시간축 통제(explore 우위) ③문단 구조 일관성.
**약점/개선**:
1. **장르 폭 시딩 부재** → Lucid식 꼬리 장르태그를 *선택적* 도입(attested 장르만). 단일 장르 곡엔 불필요.
2. **무드/이미지 레이어 약함** → float.의 Mood 발상을 *산문 무드문장 1줄*로 흡수(라벨 아닌 산문으로).
3. **강조 메커니즘** → stay 불릿 = 우리 Top-Anchor 첫줄 배치로 대체 가능, 추가 불요.

## 종합
우리 형식은 explore 최상위 산문곡(Você)과 동일축이며, instrument-cue 브래킷에서 오히려 더 정밀하다. 외부 4곡은 "순수산문(Você)↔라벨형(float.)" 스펙트럼을 보여주고, 차용 가치는 Você의 압축도 + Lucid의 장르 시딩(attested 한정). 형식 변경보다 **현 산문+브래킷 강점 유지 + 장르 시딩 선택 도입**이 결론.
