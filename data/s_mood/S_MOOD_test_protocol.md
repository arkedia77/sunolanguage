# S_MOOD — 감정어휘 dead-zone 렌더·Echo 테스트 프로토콜

**시리즈**: S_MOOD · **설계일**: 2026-07-03 · **곡수**: 12 (6쌍 A/B) · **test_id**: 258~269
**계기**: 패션필름 D&G SP의 `suspense`(2곡) 관찰 → 심리·분위기 어휘 전수채굴(`docs/suno_mood_vocabulary_map.md`) → dead-zone 감정형용사 실증 실험

---

## 1. 배경

Suno 분석출력에 **감정의 결을 나타내는 형용사가 거의 없음**(실측): 기능어 `tension`(84곡)·`dark`(55)·`bright`(336)는 CORE인데, `suspenseful`·`sinister`·`sensual`·`foreboding`·`desolate`는 **0곡(dead-zone)**. `euphoric`은 5곡(thin).

단 "분석출력에 없음 ≠ 생성입력으로 못 알아들음". 두 질문을 분리해야 함.

## 2. 가설

| 코드 | 가설 | 검증 기준 |
|---|---|---|
| **H1 (렌더 이해)** | dead-word를 SP에 넣어도 Suno가 의도한 무드를 렌더한다 (입력 이해 ≠ 출력어휘) | Leo 청취: A(dead)와 B(attested) 무드 동등성 |
| **H2 (Echo 비대칭)** | 재분석 시 dead-word는 **되돌아오지 않고 대체어로 치환**된다 | A곡 재분석 SP에 probe_word 미출현 / 대체 무드어 출현 |
| **H3 (등가성)** | dead-word A와 attested B가 **청취상 구분 불가**하면, SP에서 대체어 사용이 정보손실 없이 안전 | A≈B 청취 → 치환규칙(vocab_map C절) 타당성 입증 |

## 3. 설계 (A/B 매칭쌍, 통제실험)

- **독립변수**: 무드어휘 표현 (A=dead-word 직접 / B=attested 대체어). **그 외 전부 통제** — 동일 장르·악기·템포·조성·믹스, `{MOOD}` 슬롯만 교체.
- **무가사 인스트루멘탈** — 가사 정서 교란 배제, 순수 SP 무드어 효과 격리.
- **6쌍**:

| pair | probe (A, dead) | 대체 (B, attested) | 장르 프레임 | 조성/BPM |
|---|---|---|---|---|
| P1 | suspenseful (0) | tension and dissonant motifs (84/25) | cinematic orchestral | Dm/100 |
| P2 | sinister (0) | dark and menacing (45/2) | dark electronic | Cm/90 |
| P3 | sensual (0) | smoky and sultry (3/1) | neo-soul | A/72 |
| P4 | foreboding (0) | ominous (2) | ambient cinematic | Em/60 |
| P5 | desolate (0) | bleak and lonely (0/2) | sparse acoustic | Am/66 |
| P6 | euphoric (5, thin) | bright and energetic (223/65) | dance-pop | F/126 |

*(괄호=lexical_index v3.2 attestation 곡수)*

## 4. 측정

1. **생성** (sunomusic): 12곡 무가사 생성. SP 그대로.
2. **청취** (Leo, H1·H3): 각 쌍 A vs B 블라인드 — 무드 동등한가? A가 의도 무드를 내는가?
3. **재분석** (Suno 앱 업로드→4값, H2): A곡 재분석 SP에 probe_word가 되돌아오나? 대체어로 바뀌나? → `measure_echo` 방법론.

## 5. 판정

- **H1 성립** (A도 무드 렌더): dead-word도 생성입력으론 유효 → SP에 써도 됨(단 출력엔 안 나옴).
- **H1 기각** (A 무드 붕괴/무시): dead-word는 생성서도 무효 → **반드시 대체어 사용**. vocab_map C절 치환규칙 필수화.
- **H2 성립**: dead-word는 Echo 0 확정 → 코퍼스가 영원히 안 배움(자기강화 갭). suspicion_tracker 확정 등재.
- **H3 성립** (A≈B): 치환 무손실 → SP 작성매뉴얼에 "감정형용사→attested 치환" 규칙 확정.

## 6. 산출물 반영

- 결과 → `docs/suno_mood_vocabulary_map.md` D절 갱신 + 책 5장(감성어휘 전략) 실증 근거
- probe_word 6종 → suspicion_tracker 등재(Echo 추적)

## 7. 진행 로그

- **2026-07-03 생성 완료** (sunomusic) — 12/12 success, test_id 259~270 DB writeback(suno_generated=true·uuid1/2 채움 12/12 검증). 제출SP==생성tags **무변형 확인**(어휘효과 측정 조건 무결). 곡당 2테이크 uuid 확보. A/B 무드어 전건 tags 반영.
  - **1차 관찰(생성 tags = 제출SP 왕복)**: SP 무변형이라 A곡 dead-word가 tags에 그대로 존속 → 이는 '제출SP 보존'이지 H2(재분석 Echo)가 아님. H2는 **오디오 재분석 필요**.
  - **다음 대기**: ①Leo 청취(H1·H3 — A vs B 무드 동등성/구분가능성) ②Suno 앱 오디오 재분석(H2 — dead-word가 Suno 분석출력으로 되돌아오나 vs 대체어 치환). 재분석 대상 uuid는 batch json에 반영됨.

## 파일
- `data/s_mood/S_MOOD_batch.json` — 12곡 SP 전문 + 생성 uuid/url (A/B 프레임 통제 PASS, 무변형 검증)
- 빌더: `/tmp/build_smood.py`
