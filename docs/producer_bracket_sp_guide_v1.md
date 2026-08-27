# 프로듀서용 브라켓·SP 가이드 v1 — 코퍼스 실측만

**날짜** 2026-08-27 · **작성** sunolanguage · **근거** 우리 코퍼스 540곡 · **입력↔출력 짝 411**
**재현** `scripts/bracket_leak_corpus_wide_v1.py` · 팔레트 원본 `data/reanalysis_v2/producer_bracket_palette_v1.json`
**★이 문서에 추측은 없습니다.** 전부 「우리가 넣은 것 ↔ Suno가 되돌려준 것」을 대조한 값입니다.

---

## §1. 오늘 확정된 것 세 줄

1. ★**브라켓 안에 쓴 말은 노래되지 않습니다.** 브라켓 전용 낱말 **4,166개 중 출현 0**(0.00%).
2. ★**브라켓 밖에 쓴 말은 노래됩니다.** 같은 가사 필드의 브라켓 밖 낱말 **536개 중 395개(73.69%) 출현**.
3. ★**길어도 안 새어나갑니다.** 6어 이상 브라켓 **50건**(최장 **16어 완전 문장형**)도 **누출 0**.

같은 곡·같은 필드에서 갈렸습니다. 가장 선명한 단건 — `S004_11`: 브라켓 45낱말 **0 출현**, 본문 32낱말 **32 출현(100%)**.

> ⇒ **브라켓은 안전합니다. 길게, 서술적으로 쓰셔도 됩니다.**
> 「메타태그는 1~3어로 짧게」라는 외부 가이드는 **우리 실측과 맞지 않습니다.**

---

## §2. ★사고 1순위 — 브라켓 **밖** 지시문

가장 흔한 실사고입니다. 실물:

```
입력 가사 (S018_01)          →   Suno가 되돌려준 가사
[Verse 1 - 16 bars]              [Verse 1]
Full kit enters, bass synth      [kick drum enters]
  joins                          Full kit enters      ← ★노래됐습니다
                                 [synth bass enters]
                                 Bass joins           ← ★노래됐습니다
```

같은 배치의 다른 곡에서는 이렇게 났습니다 —
`Enters, enters, enters, enters, enters, enters, enters, enters`

★**편곡 지시를 가사 필드에 맨 텍스트로 쓰면 그대로 불립니다.** 대괄호를 씌우면 안 불립니다.
**가사 필드에는 부를 것만.** 지시는 전부 `[ ]` 안으로.

---

## §3. ★어휘 격차 — 우리는 구조를 말하고, Suno는 음색을 말합니다

| | 서술 브라켓 상위 | 성격 |
|---|---|---|
| **우리 입력** (1,055회) | `[Climax Chorus]` 36 · `[Long Outro]` 25 · `[Double Chorus]` 16 · `[B Section]` 7 | **구조 명칭** |
| **Suno 출력** (3,154회) | `[breathy male vocals]` 85 · `[fingerpicked acoustic guitar]` 38 · `[bass guitar enters]` 24 · `[kick drum enters]` 18 | **음색 · 악기 진입** |

★**Suno는 「무슨 구간인가」가 아니라 「지금 무엇이 어떤 음색으로 들어오는가」를 말합니다.**
그리고 §1에 따라 **그렇게 길게 써도 대가가 없습니다.**

---

## §4. 바로 복사해 쓰는 팔레트 — **Suno 자신이 쓰는 문면**

수치 = `회수 / 곡수` (우리 코퍼스 출력층 실측)

**보컬 음색·성부**
`[breathy male vocals]` 85/83 · `[male vocals]` 38/36 · `[breathy female vocals]` 34/34 ·
`[male tenor vocals]` 31/31 · `[smooth male vocals]` 17/17 · `[baritone male vocals]` 16/16 ·
`[soft male vocals]` 16/16 · `[female vocals]` 14/13 · `[falsetto]` 14/14 · `[falsetto ad-lib]` 8/8 ·
`[male rap vocals]` 8/8 · `[vocalizing]` 11/8

**악기 진입·퇴장** ← ★우리가 거의 안 쓰는 축입니다
`[bass guitar enters]` 24/24 · `[bass enters]` 19/19 · `[kick drum enters]` 18/18 ·
`[electric bass enters]` 15/15 · `[soft kick drum enters]` 14/14 · `[shaker enters]` 14/14 ·
`[synth bass enters]` 10/10 · `[bass and drums enter]` 9/9 · `[drums and bass drop out]` 9/9 ·
`[acoustic guitar fades out]` 8/8 · `[clean electric guitar enters]` 6/6 · `[strings enter]` 6/6

**악기 음색·주법**
`[fingerpicked acoustic guitar]` 38/37 · `[fingerpicked acoustic guitar arpeggio]` 12/12 ·
`[brass stabs]` 12/11 · `[fingerstyle acoustic guitar]` 11/11 · `[piano melodic fill]` 8/8 ·
`[palm-muted guitar]` 7/7 · `[synth pads swell]` 7/7 · `[clean electric guitar fills]` 7/7 ·
`[upright bass enters]` 5/5 · `[bass slides]` 5/5

**다이내믹**
`[Climax]` 6/6 · `[strings enter softly]` 5/5 · `[full band arrangement]` 3/3 ·
`[full band, high energy]` 3/3 · `[snare roll build-up]` 2/2

---

## §5. 그 밖에 실측으로 나온 것 셋

### ⓐ 섹션 라벨은 힘을 빼셔도 됩니다
입력에 `[Intro]`를 **넣은 곡** → 출력에 `[Intro]` **97.9%**.
입력에 **안 넣은 곡** → 출력에 `[Intro]` **97.7%**.
★차이가 없습니다. **Suno가 알아서 붙입니다.** 구조 라벨에 쓰던 힘을 §4 음색·진입 축으로 옮기십시오.

### ⓑ ★여성 보컬은 명시해도 샙니다
| 입력 SP | → 출력이 female로 묘사 | → **male로 묘사** |
|---|---:|---:|
| 성별 미명시 (349곡) | 15% | **72%** |
| **female 명시 (49곡)** | 31% | **★67%** |
| male 명시 (57곡) | 12% | 84% |

female을 명시하면 female 묘사가 **2배**(15%→31%)로 오릅니다. **그래도 3분의 2가 male로 묘사됩니다.**
⇒ 여성 보컬은 **SP와 브라켓 양쪽에 명시**하고, **결과를 반드시 귀로 확인**하십시오.
⚠단, 이 자(Suno 재분석) 자체가 male 편중입니다(출력 전체 M 333 vs F 71). **방향은 믿되 크기는 믿지 마십시오.**

### ⓒ Styles Box에 대괄호를 써도 됩니다
우리 입력 SP 435곡 중 **31곡이 브라켓을 포함**했고 전부 정상적으로 나왔습니다.
「Styles Box의 대괄호는 illegal」이라는 외부 주장에는 **반례가 31곡** 있습니다.

---

## §6. ★이 가이드가 못 하는 말

1. **「브라켓이 먹힌다」고는 말하지 않았습니다.** 잰 것은 「**안 불린다**」뿐입니다.
   지시가 **반영됐는지**(uptake)는 아직 안 쟀습니다.
2. 출력은 Suno의 **재분석**이지 전사가 아닙니다. 「불렸다/안 불렸다」의 최종 판정이 아닙니다.
3. 누출 **대조군은 25곡**뿐이고 대부분 영문 편곡 시트 계열입니다. 나머지 386짝의 「0」은 **자의 감도가 미확인**입니다.
4. §4 팔레트는 **Suno가 쓰는 말**입니다 — 「넣으면 지켜진다」의 실증이 **아닙니다**. 통할 확률이 높다는 것까지입니다.
5. 코퍼스가 **한쪽으로 쏠려 있습니다** — 대장 2,966곡 중 재분석된 것은 155곡이고 대부분 leomusic 4월분입니다.
   **트로트·국악·CN·yoonnest는 0곡**입니다. 그 장르에서는 이 팔레트가 얇습니다.
   (확장 요청 발신 완료 — 1차 8배치 80곡, 0cr)

---

**질문·반례 환영합니다.** 「이렇게 썼는데 안 되더라」가 제일 값진 자료입니다 — 그 곡의 **입력 SP·가사와 uuid**를 주시면 코퍼스에 넣고 재겠습니다.
