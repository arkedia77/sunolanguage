# LEO 제공 프롬프트 8개 — 분석·재작성 (2026-10-02)

LEO 직지시: 「준 프롬프트 분석해보고, 코퍼스도 분석해보고, 우리 스타일로 다시 만들어서 곡 만들어봐」

- `prompts.json` — 원문 8개(전사). ⚠P7 은 첫 전사에서 한 구절을 중복시켰다가 교정했다(원문 우선).
- `rewrite_specs.json` → `rewritten_sp.json` — 재작성 입력/산출.
- 분석기 `repo:scripts/analyze_request_prompts.py` · 재작성기 `repo:scripts/rewrite_sp_our_style.py`

## 실측 (2026-10-02)
- 8개를 구 단위로 쪼개 **137구 중 71구(52%)가 우리 코퍼스 미관측**.
- 미관측은 네 갈래다 — ⑴**요청층**(장르 라벨·BPM·구조 지시: 관측 0이 당연) ⑵**평가어**(`luxurious`·`impeccable`·`radio-ready`·`instantly captivating` = 오디오 서술이 아니라 평가) ⑶**표기 변종**(`sub bass`→`sub-bass`(61) · `kick`→`kick drum`(496) · `snare`→`snare drum`(453) · `arpeggio`→`arpeggiated`(147) · `four on the floor`→`four-on-the-floor`(3)) ⑷**진짜 미관측**(`glitch`·`detuned`·`drum machine`·`whispered`·`swing` — 레퍼런스 619트랙에서 관측 0).
- ★`P8`은 **음악 프롬프트가 아니라 릴 영상 프롬프트**다(9:16·film grain·bokeh). 음악 생성에 넣지 않았다.
- ★`P3`은 사람에게 말하듯 쓴 **명령문**이 섞였다(`put some rap`·`then put some heavy sexy drum`)·같은 말 중복(`rap`2·`female vocals`2·`hip-hop`3).
- 코퍼스 쪽 비대칭: **`male vocals` 721 ↔ `female vocals` 150**(4.8배). 요청은 여성 보컬이 많은데 우리 관측 기반은 남성 쪽이 두텁다.
- `emotional` 관측 **1**(09-02 층 분리 후). 「emotional and empowering」류는 우리 기준으로 근거가 거의 없다.

## 우리 스타일 5규칙 (기계가 검사한다 — 말로만 두지 않는다)
R1 평가어·마케팅어 금지 · R2 표기를 관측형으로 정규화 · R3 서술어는 전부 `attested≥30`·데드존 아님(미달이면 **거절**하고 대체어 제시) · R4 장르·BPM·구조는 **요청층으로 분리 기재** · R5 1000자 이내·중복 0·명령문 0.

## 산출 SP 4개 (전부 검사 통과)
| | 출처 | 길이 | 관측 어휘 | 최저 attested |
|---|---|---|---|---|
| R1 | P1 (394자) | **131자** | 9 | 30 |
| R2 | P6 (949자) | **171자** | 15 | 42 |
| R3 | P5 (185자) | **120자** | 9 | 50 |
| R4 | P7 (291자) | **130자** | 10 | 64 |

★**대조군을 같이 돌렸다**: 일부러 못 쓸 말(`glitch`·`detuned`·`drum machine`·`nocturnal`)을 섞은 R5 는 **거절**됐고, `clap`(13)이 든 R2 초안도 문턱 미만으로 막혀 `kick drum`(496)으로 바꿨다 — 게이트가 장식이 아님을 확인.

## 곡
생성은 sunomusic 칸이라 **A/B 발주**로 보냈다(`sunomusic_sunolanguage_20261002_144023`):
①야간 R&B = P6 원본(949자) ↔ R2 재작성(171자) · ②올드스쿨 소울 = P7 원본 ↔ R4 재작성.
가사 없음(instrumental)·모델/설정/take 수를 쌍 안에서 고정 — 재작성본만 돌리면 좋았는지 나빴는지 알 수 없다(대조군 없음).
⛔**청음 판정은 하지 않는다**(A&R 칸). 나는 어휘·길이·층 분리만 기록한다.
