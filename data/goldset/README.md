# chaser_calib_goldset — leomusic3 chaser 임계값 캘리브레이션 goldset

**생성**: sunolanguage · **수요자**: leomusic3
- **v0**: 100 트리플 (2026-07-01) — `chaser_calib_goldset_v0.json`. 라벨 45/35/20, 20장르축, target_collection 미태깅.
- **v1**: 240 트리플 (2026-07-02) — `chaser_calib_goldset_v1.json`. 라벨 96/96/48(40/40/20), **KR 견고 8축 집중** + target_collection 태그. v0 sanity-check 피드백(ⓐ짧은구 정규화·ⓑno_match 정제) 반영.

## 목적
leomusic3 chaser normalize의 direct/blend/fallback 임계값(현 휴리스틱 direct 0.78 /
blend 0.62)을 경험적으로 재설정하기 위한 라벨드 goldset. proposal_text를 chaser
retrieve에 투입 → top1 candidate score를 측정 → label과 대조해 precision/recall
곡선으로 임계 재설정.

## 트리플 구조
```
{ "id", "proposal_text", "candidate_native_entity", "label", "genre_axis", "note" }
```
- **proposal_text** — LLM이 자유생성할 법한 영어 음향 묘사(합성). leomusic3 chaser의 입력 형태.
- **candidate_native_entity** — 대응(또는 오답) Suno 네이티브 토큰. **전건 lexical_index v3.2(496곡) attested**.
- **label** — match / partial / no_match (아래 기준).
- **note** — partial/경계 판정 근거(주관성 보정용).

## 라벨 기준
| label | 정의 | 기대 score | chaser 구간 |
|---|---|---|---|
| **match** | proposal 지배적 음향의도의 **정확한** 네이티브 대응 = candidate | HIGH | direct |
| **partial** | 의미 중첩하나 **비정확**(상위/하위개념·형제토큰·한 면만·thin 근사) | MEDIUM | blend |
| **no_match** | **무관**, 또는 네이티브 대응 없는 개념(dead-zone 컴파운드·foley·추상) | LOW | fallback |

no_match도 candidate는 attested 토큰(리트리버가 오검출할 법한 '오답 페어')이라,
실제 리트리버가 그 토큰을 top1로 뽑았을 때의 score까지 함께 관찰 가능.

## 구성 (v0)
- **라벨 분포**: match 45 / partial 35 / no_match 20 (blend·fallback 경계 표본 충분)
- **장르축 20종**: edm·hiphop·rnb·jazz·rock·ballad·cinematic·citypop·disco·trot·folk·
  bossa·amapiano·dreampop·latin·kpop·funk·ambient·lofi·pop
- **CN 미포함**(leomusic3 합의 — KR 우세 코퍼스 기준 v1)

## 한계 (합의됨)
1. proposal_text는 sunolang **합성**(실 프로덕션 로그 아님) — 1차 캘리 용도. 확정 전
   leomusic3 자체 chaser 로그(score 분포)로 **2차 검증** 권장.
2. partial 경계는 주관 개입 여지 — `note`에 판정근거 명시.
3. v0 sanity-check(형식·score 분포 확인) 통과 후 **v1(200~300)** 확장.

## v1 신규 (v0 대비)
- **candidate 짧은구 정규화**(ⓐ) — terse 단일토큰을 2~4단어 구로(예: `supersaw`→`detuned supersaw lead`), 구성어 attested 유지 + `atomic_token` 병기. proposal 문장과의 length asymmetry 완화.
- **no_match 정제**(ⓑ) — dead-zone 컴파운드/foley/추상만. v0의 실악기 중간유사도 오답페어는 partial로 재분류.
- **target_collection 태그** — KR 견고 8축만: ballad→music_kr_ballad, rnb→music_kr_rnb, hiphop→music_kr_hiphop, rock→music_kr_rock, pop·kpop→music_kr_pop, trot→music_kr_trot, folk→music_kr_acoustic. 무매핑 11축은 v2 이월.
- **attestation 기준 정정** — 현행 lexical_index distinct song 556(v3.2 사전 496곡에서 배치 적재로 성장). v0의 '496' 표기는 사전버전 기준이었음.

## 파일
- `chaser_calib_goldset_v0.json` — 트리플 100 + 메타
- `chaser_calib_goldset_v1.json` — 트리플 240 + 메타(+atomic_token/target_collection 필드)
