# 커넥터 OUT v0.3 재발행 고지 — 초안 v1 (2026-09-19 · ⛔미발신)

- **수신**: leomusic · leomusic2 · leomusic3 · leomusic-trot · encore (구독 5팀)
- **발신**: sunolanguage
- **수치 출처**: `scripts/connector_out_delta_v1.py` 출력 `data/connector/out/delta_pub_v0.2_to_current.json`
  (발행분 `crosswalk_latest.json` ↔ 현행 정본 재수출 · ★손 전사 0)
- **발행 예정**(dry-run 실측): interface **v0.2 → v0.3** · snapshot `cs-3.3-589-20260815` → **`cs-3.5-619-20260902`**
  · 개념 453 · 별칭 72 · sha256 `36cd7c889296e2cf…`

---

## 1. 무엇을 보내는가

크로스워크를 **33일 만에** 재발행합니다(마지막 발행 2026-08-17). 그동안 코어가 두 번 움직였습니다 —
09-02 **층 분리 처방**(v3.3→v3.5), 09-14 **표현 저작 42건**(개념 446→453).

## 2. ★먼저 읽으실 것 — 「Suno 관측 수」가 «줄어든» 이유

`attested_count` **181개 개념에서 값이 바뀝니다**(증가 116 · 감소 65 · 그중 **0으로 12**).

⛔**이건 「Suno가 그 말을 덜 쓰게 됐다」가 아닙니다.** 09-02 이전 값은 **우리가 쓴 입력층과 Suno가 낸
출력층을 한 통에 세고 있었습니다.** 처방으로 둘을 갈랐고, 이제 `attested_count` = **출력층 관측만**입니다.
⇒ **줄어든 것이 아니라, 전에 부풀려져 있던 것입니다.**

- 감소 상위: `warm` 531→143 · `emotional` 361→1 · `intimate` 609→416 · `soft` 422→237 ·
  `bright` 338→205 · `punchy` 280→160 · `lo-fi` 112→30 · `atmospheric` 143→68 ·
  `fingerpicked` 267→201 · `energetic` 81→22
- 증가 상위: `drums` 935→1018 · `electric bass` 1065→1148 · `vocals` 586→660 ·
  `electric guitar` 824→889 · `distorted` 658→711 (코퍼스 589→619트랙 증가분)

## 3. ★★가장 실무에 닿는 칸 — 「Suno 관측 0」이 되는 12단어 (전건)

`dreamy` 33→0 · `nostalgic` 48→0 · `serene` 14→0 · `glassy` 8→0 · `hollow` 4→0 · `somber` 3→0 ·
`moody` 2→0 · `euphoric` 6→0 · `haunting` 1→0 · `sultry` 1→0 · `hi-fi` 1→0 · `trill` 1→0

**뜻**: 이 12단어는 **우리가 SP에 써 온 말**이고, **Suno가 완성곡을 듣고 되돌려 쓴 적은 한 번도 없습니다.**
⛔「쓰지 마십시오」가 아닙니다 — **「Suno 어휘로 통한다는 근거가 없다」**까지가 우리가 말할 수 있는 전부입니다.
판단은 그쪽 칸입니다. 대체어가 필요하시면 인바운드 별칭 72건(`dead_zone` 포함)을 그대로 쓰실 수 있습니다.

⚠**자 두 벌 주의**: 저희 정책표에는 같은 단어가 `nostalgic 0/49`로 적혀 있습니다. 그 **49는 사전의
`freq_input`**(v3.5·619트랙 기준)이고, 위 **48은 크로스워크 `attested_count`**(발행분 v3.3·589트랙 기준)입니다.
**다른 자입니다 — 두 수를 같은 줄에 놓고 빼지 마십시오.**

## 4. 그 밖의 변동

- **개념 446 → 453** (신규 7 · **소실 0**): `ring out` · `return` · `builds from` ·
  `half-time feel, filtered synth` · `full band, brass section enters` ·
  `full band, energetic delivery` · `a prominent brass section with trumpets and saxophones, a slap bass guitar`
  - ⚠`builds from`은 전치사로 끝나는 조각이라 단독으로 뜻이 안 닫힙니다 — `confidence=low`로 정직 표기.
  - ⚠`ring out`·`return`은 기존 `rings out`·`returns`의 **어형 변종**이며 **중복이 아닙니다**(별개 원자).
- **인바운드 별칭 72 → 72** (신규 0 · 소실 0)

## 5. ⛔`breaking_content=false`를 믿지 마십시오

이번 발행도 플래그는 **false**(additive)로 찍힙니다. 그런데 **내용은 위와 같이 바뀝니다.**
`detect_breaking`은 **삭제·별칭 재타깃만** 보고 **`attested_count` 하락은 «안 봅니다»**.
⇒ 그래서 이 고지를 **플래그가 아니라 델타 실물로** 씁니다. 자동 감지에 기대신 라인이 있으면 알려 주십시오.

## 6. ★판본 한정자 — 이 크로스워크는 «Suno 6.0 이전» 관측입니다

- 이 발행분의 관측은 **전부 6.0 이전 코퍼스**에서 나왔습니다. 우리 **6.0 관측은 현재 0건**입니다.
- ⛔**코퍼스 560레코드에 판본 칸이 없습니다**(`merged_4values.json` 전수 실측 09-10 — `model`·`version` 등장 0건).
  ⇒ 6.0 산출이 들어오기 시작하면 **구판과 한 통에 섞여 조용히 오염됩니다.** 판본 칸 신설이 선행 과제(P0)입니다.
- ⇒ **당장 하실 일은 없습니다.** 다만 위 수치를 6.0 결과에 그대로 적용하지 마시고, **6.0에서 다르게 보이는 게
  있으면 저희에게 실물로 주십시오** — 그게 저희가 판본을 가르는 첫 재료가 됩니다.

## 7. 수령 후

- 번들은 팀별로 갈라 나갑니다(`data/connector/out/bundle_{팀}.json`).
- 회신 **불요**입니다. 다만 ⑴2·3절이 그쪽 프롬프트에 실제로 영향이 있거나 ⑵5절 자동 감지에 기대고
  계셨다면, 그 두 가지만 알려 주십시오.
