# leomusic-trot 전체 SP 검수 — 19배치 164곡 (2026-06-15)

**검수 베이스**: sunolang lexical_index v3.2 (556트랙/17,822 entries), leomusic 자작 SP 제외 Suno 네이티브 소스만으로 attestation. 전 SP 통합 `/tmp/lmtrot_all_sp.json`, novel 리포트 `docs/reviews/lmtrot_all_sp_review.md`.
**대상**: Y001~Y016 + W001 + W002 + DNE = 19배치 164곡

---

## 요약 — 두 갈래의 코퍼스

검수 결과 leomusic-trot SP는 **명확히 두 그룹**으로 갈린다:

- **GT-정합 그룹 (W001·W002·Y016·DNE, 24곡)**: 앵커 'Trot, Korean adult contemporary' 보유, GT 치환룰 적용됨, dead-zone 거의 없음. (W001/W002는 직전 개별 검수에서 종결)
- **레거시 Y그룹 (Y001~Y015, 135곡)**: Wave T 앵커 규약 이전 산출물로 추정. **앵커 0·식별3종 0 + 광범위 과포화 + dead-zone 어휘 다발.**

→ 본 검수의 신규 발견은 사실상 **레거시 Y그룹**에 집중된다.

---

## ① ★SP 과포화 — 최대 시스템 이슈

전체 평균 **845자**, **70/164곡(43%)이 900자 이상** 위험대. 4장 4.5 / 6장 6.5 기준 B192 폐기곡(964~999자)·재분석 평균(~500자)의 2배 = 과포화 위험.

| 배치 | 평균 | 최대 | ≥900 | 상태 |
|---|---|---|---|---|
| Y007 | 968 | 982 | 5/5 | 🚨 최악 |
| Y003 | 949 | 976 | 10/10 | 🚨 |
| Y006 | 924 | 943 | 8/10 | 🚨 |
| Y005 | 920 | 945 | 9/10 | 🚨 |
| Y015 | 918 | 947 | 8/10 | 🚨 |
| Y004 | 911 | 946 | 7/10 | 🚨 |
| Y014 | 908 | 950 | 7/10 | 🚨 |
| Y001 | 900 | **999** | 5/10 | 🚨 |
| Y002 | 880 | 979 | 3/10 | ⚠️ |
| W002 | 877 | 929 | 4/10 | (검수완료) |
| Y013 | 876 | 920 | 2/10 | ⚠️ |
| Y012 | 858 | 920 | 1/10 | ⚠️ |
| W001 | 828 | 931 | 1/10 | (검수완료) |
| DNE | 788 | 788 | 0/1 | OK |
| Y011 | 766 | 823 | 0/10 | OK |
| Y010 | 773 | 802 | 0/5 | OK |
| Y009 | 643 | 715 | 0/10 | ✅ |
| Y008 | 575 | 711 | 0/10 | ✅ |
| Y016 | 574 | 619 | 0/3 | ✅ |

- Y001-04는 **999자** = 1000자 천장 직격. Y003은 10곡 전부 ≥900.
- 흥미롭게 Y008/Y009/Y016은 575~643자로 건강 — 같은 팀 산출인데 배치별 길이 정책이 크게 흔들림.
- **권고**: ≥900자 70곡 우선 축약(목표 550~700자). 후반부 디테일은 영향력이 낮으므로(Top-Anchor) 뒤쪽 문장부터 컷.

## ② ★Dead-zone 어휘 — Y그룹 전반

raw 코퍼스 0건(Suno 미렌더) 어휘가 Y시리즈 거의 전 배치에 박혀 있다:

| 어휘 | 출현 | GT | 실제 용례 | 권고 치환 |
|---|---|---|---|---|
| `bounce` | **74곡** | 0건 | "disco bass with octave bounce pattern" | "disco bass" / "bouncing bass" (disco bass 50건) |
| `progressions` | 25곡 | 0건 | "disco-influenced chord progressions" | 삭제 — **Suno는 코드진행 미렌더(5장 데드존 재확인)** |
| `vintage` | 19곡 | 0건 | vintage 음색 수식 | 구체 음색어(warm/analog/lo-fi) |
| `modal` | 17곡 | 0건 | "modal color" | 조성 직접명시(key of X) 또는 삭제 |
| `arco` | 16곡 | 0건 | "strings arco interlude" | "bowed strings" / "legato strings" |
| `suspended` | 15곡 | 0건 | suspended chord | 삭제(코드명 데드존) 또는 "open/airy" |
| `programmed` | 11곡 | 0건 | "programmed drums" | "drum machine" (attested) |
| `timbales` | 1곡(Y012) | 0건 | 라틴 타악 | "congas"/"shaker" (W001 Latin 교훈과 동일) |

배치 분포: Y001~Y007은 arco/progressions/suspended/modal 집중(현악·재즈화성 계열), Y008~Y015는 bounce/vintage/programmed 집중(디스코·신스 계열). **거의 전 Y배치 오염.**

- `octave`(31건)·`organ`(25건)·`semitone`(1건 희귀)은 OK — batch_sp_review의 0건 표기는 좁은 코퍼스(505) 한계, 본 검수는 권위 index(17,822) 기준.

## ③ 앵커 / 식별3종 부재 (Y001~Y015)

| 그룹 | 앵커 'Trot, Korean adult contemporary' | 식별3종 |
|---|---|---|
| W001 | 10/10 | 8/10 |
| W002 | 10/10 | 10/10 |
| Y016 | 3/3 | 1/3 |
| DNE | 1/1 | 0/1 |
| **Y001~Y015 (135곡)** | **0** | **0** |

- Y001~Y015는 앵커·식별3종이 전무. GT 실증상 앵커 없는 트로트는 Suno가 'Trot' 아닌 K-Pop으로 라벨(12곡 중 1곡만 native 'Trot', gid20010). **이 135곡이 트로트로 의도된 라인이라면 드리프트 위험 큼.**
- 단 이는 Wave T 앵커 규약(2026-06-10) 이전 산출물일 가능성 — **재생성 여부는 leomusic-trot 판단 영역**. 신곡부터 앵커 적용이 최소 비용. (확인 요청)

## ④ 하이픈 / 폐기어 (경미)

- 폐기어(pitch bend/triplet shuffle/intimate grand): **164곡 전건 클린** ✅
- `major-pentatonic`(DNE 1곡, 0건)→pentatonic / `jazz-tinged`(W001 2곡, 0건)→jazz / `counter-line`(16곡, 2건 희귀 — borderline, 급하지 않음)

---

## 권고 우선순위

1. **과포화 일괄 축약** — ≥900자 70곡(특히 Y003·Y007·Y005·Y006 전부) 550~700자로. 가장 영향 큼.
2. **dead-zone 치환** — bounce/progressions/arco/modal/suspended/vintage/programmed/timbales 8종. 위 표대로. progressions·suspended는 코드 데드존이라 삭제가 정답.
3. **앵커 적용 검토** — Y001~Y015가 트로트 의도라면 (재생성 or 신곡부터). leomusic-trot 확인 필요.

회신원칙: finding(코퍼스 0건 실측) 채택 · recommendation(치환·축약) 재분석 검증 후 반영. 치환표 공동관리 일환.
