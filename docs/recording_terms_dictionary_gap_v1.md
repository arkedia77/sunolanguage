# attested 사전이 «녹음 상황어»를 잘랐나 — 판정 v1 (2026-10-24 16:0x · 0cr · 읽기 전용)

**발제**: plan.md 2판 ▶착수(10-24 15:5x) · 출처 = 10-16 ①-65 「tracks 79 중 51 에 녹음 상황어 ⇒ attested 사전 0 = 추출이 못 담음」.
**자(사전 고정)**: `scripts/build_suno_emitted_v1.py` 의 `REC` 정규식(10-16 작성 · 이번에 고르지 않음) · 관측층 = `tracks.suno_prompt` 79곡(v6 이전 Suno 녹음 인식) · 사전 = `expr_concepts` 453.

## 결과
- REC 걸린 곡 **77/79**. 사전 개념 중 REC 일치 **25개** — reverb 170 · plate reverb 58 · compression 42 · close-mic 34 · room reverb 32 · lo-fi 30 · processed 25 · compressed 20 … (+ 인접 `saturated` 30 · `clean` 1,028).
- ⇒ ⛔**10-16 「attested 사전 0」은 틀렸다(내 기재 · 자진 정정)** — 녹음 상황어 대부분은 이미 사전에 있다. 「0」이 나온 자리는 suno_emitted 층의 그 낱말 행 `attested_count` 였고, 그걸 사전 전체로 일반화했다.

| 낱말(출현/곡) | 문맥 | 판정 |
|---|---|---|
| **dry** 115/52 | «production is dry with minimal» 12 · «dry snare» 19+ | **놓침(결함)** — 사전 0 |
| **saturation** 23/20 | «high-gain/heavy saturation» | **부분 놓침** — 형용사 `saturated` 30 은 있음, 명사형 없음 |
| room ambience 3/3 · wet 1 · ambience 1 | «minimal room ambience» | 놓침(소량) |
| recording 23/19 | «the recording has a…» 틀 문장 | **규칙상 제외(정당)** — 소리 개념 아님 |
| mixed 5/4 · dynamics 6/6 | «mixed choir» · 음악적 셈여림 | **REC 오탐** — 녹음어 아님 |

## 기전
`build_dictionary_v3.build_mood_and_timbre` 의 음색 낱말이 **손으로 고른 닫힌 목록 25개**다(`saturated`·`clean`·`compressed`·`lo-fi` 있음 · **`dry`·`wet` 없음**). 제작 어휘(`build_production_vocab`)는 슬롯 파서 entity(mixing·effect·mastering)만 받아 «dry snare» 같은 수식 형용사는 안 들어온다.

## 처분 (집행 0 · 다음 재빌드 때)
- ⑴사전 재빌드(B 임계) 때 음색 닫힌 목록에 `dry`·`wet` 추가 + `saturation` 명사형을 `saturated` 와 묶을지 판단 — 재빌드 전 이 표를 대조군으로.
- ⑵`sunolang.db:suno_emitted_meta.recording_category` 문구의 «attested 사전 0» 은 틀린 문장 — ⛔단일 Writer(`build_suno_emitted_v1.py`)만 쓴다 ⇒ 빌더 문자열을 고쳐 두고 **다음 적재 때 반영**(지금 재적재는 PG 새 클립이 섞여 표 전체가 바뀌므로 안 함).
