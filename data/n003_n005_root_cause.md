# N003~N005 이슈 근본 원인 정밀 분석

**분석일**: 2026-05-30

---

## 분류 기준

- **확정적 수정**: 코드/데이터 변경으로 이슈를 근본적으로 제거 가능
- **효과 제한적 수정**: 개선은 되지만 구조적 한계로 완전 해결 불가
- **운**: 랜덤 프로세스 또는 코퍼스 한계로 통제 불가

---

## 확정적 수정 가능 (4건)

### 1. 배치 내 크로스곡 오염 — `batch_used_song_ids` 미추적

**증상**: N005 곡1과 곡7이 6행 공유 ("추락 직전에 눈을 떠" 등)

**발생 경로 (코드 추적)**:
```
코퍼스 원곡 song_id=51 (1곡)
  → Qdrant에 9포인트로 분할 저장 (section 4 + couplet 5)
  → verse P140, chorus P146, chorus couplet P147, bridge P149 등

lyrics_engine.py:322  batch_used_ids = set()     ← point_id만 추적
lyrics_engine.py:323  batch_used_texts = set()   ← section 전체 텍스트만 추적

생성곡1 → match_sp_differentiated() → P146(chorus) 사용 → batch_used_ids에 146 추가
생성곡7 → match_sp_differentiated() → P142(verse couplet) 사용
          P142 ≠ P146 이므로 통과 ✅
          텍스트도 section vs couplet이라 다름 ✅
          BUT 같은 원곡(song_id=51)의 다른 섹션 → 개별 행 공유 ❌
```

**근본 원인**: `batch_used_ids`가 Qdrant point_id만 추적. 같은 원곡의 다른 포인트(section/couplet 이중 저장 포함)는 다른 point_id이므로 제외되지 않음.

**수정 방법**: `lyrics_engine.py`에 `batch_used_song_ids = set()` 추가. `lyrics_retriever.py`의 `make_filter`에 `exclude_song_ids` 파라미터로 전달.

**추가 발견**: N005는 실제로 6개 서브배치(2~3곡씩)로 분할 생성됨. 서브배치마다 `batch_used_*`가 리셋. → N005 10곡을 단일 배치로 생성해야 배치 추적이 유효.

---

### 2. SP 문장 과다 → 코히어런스 하락

**증상**: N003 coh 0.570 vs N004 coh 0.507 (SP 550c→750c)

**발생 경로**:
```
serendipity.py:37  INSTRUMENT_COUNT = 5    ← 3→5 변경 (5/30)
serendipity.py:38  MIN_SP_LENGTH = 650      ← 450→650 변경 (5/30)

controlled_drift():
  1. genre(1문장) + instrument(5문장) + drums(1) + vocal(1) + arrangement(1) + tempo(1) = 10문장
  2. len(trial) < 650 → BOOST: instrument/arrangement/vocal 추가 = 12~13문장
  3. slot_assembler.assemble_sp() → dedup → 10~13문장 → 650~900c

lyrics_retriever.py:174  genre = extract_sp_genre(sp_text)  ← 첫 문장만
lyrics_retriever.py:175  moods = extract_sp_mood(sp_text)   ← 전체 SP에서 mood 추출
  → SP가 길수록 mood 단어 다양 → 검색 쿼리 희석 → 코히어런스 하락
```

**근본 원인**: INSTRUMENT_COUNT=5와 MIN_SP_LENGTH=650이 SP를 불필요하게 팽창. SP의 mood 단어가 가사 검색 쿼리에 전부 포함되면서 검색 초점 분산.

**수정 방법**:
- `INSTRUMENT_COUNT = 4`, `MIN_SP_LENGTH = 550` (N003 설정 복귀)
- `slot_assembler.py`에 `MAX_SENTENCES = 9` 게이트 추가

---

### 3. 코퍼스 SP 디렉티브 혼입 ("Layered leads, maximum energy")

**증상**: N004 곡5/곡8, N005 곡3에 가사로 등장

**발생 경로**:
```
코퍼스 원곡 S018_01 장르 = "Synthwave with a focus on instructional vocal cues"
  → 코러스 텍스트 = "Layered leads, maximum energy" (실제 가사가 아닌 악기 지시)
  → lyrics_chunk_builder.py → Qdrant sunolang_lyrics에 정상 인제스트
  → corpus_quality_gate.py: 영어 디렉티브 패턴 미필터링

검색 시: theme_search() → 이 포인트가 score 0.37로 상위 반환
  → _pick_novel: 텍스트 중복 아님 → 통과 → 가사에 포함
```

**근본 원인**: 품질 게이트가 한국어 노이즈만 필터링. 영어 SP 디렉티브("Layered", "maximum energy", "builds to" 등)는 미탐지.

**수정 방법**: `corpus_quality_gate.py` 또는 `lyrics_chunk_builder.py`에 영어 디렉티브 패턴 필터 추가. S018 계열 중 instructional/technical 텍스트 제거.

---

### 4. 송폼 단조 (N004 5곡 동일, N005 6곡 동일)

**증상**: N005의 6/10곡이 `verse → chorus → verse → chorus → bridge → verse → outro`

**발생 경로**:
```
song_forms.py:114-118  select_form():
  forms = GENRE_FORMS[genre_group]     ← BALLAD: 3변형, ACOUSTIC: 3변형
  return random.choice(list(forms.values()))  ← 이전 선택 기억 없음

lyrics_engine.py:332  form = select_form(genre_group)  ← 매 곡 독립 호출
  → 배치 내 이전 선택 정보 미전달

N005 genre_group 분포: BALLAD(8) + ACOUSTIC(1) + ROCK(1)
  → 8곡이 BALLAD 3변형 중 랜덤 → 확률적으로 3~4곡 동일 폼 필연
```

**근본 원인**: `select_form()`이 stateless. 배치 내 이전 선택 정보 없이 매번 독립 `random.choice()`. 장르 편중과 결합되어 송폼이 3개 이내로 수렴.

**수정 방법**: `lyrics_engine.py`에서 `form_used_counts` 딕셔너리를 유지. `select_form()`에 `avoid_forms` 파라미터 전달하여 미사용 변형 우선 선택.

---

## 효과 제한적 수정 (3건)

### 5. 장르 편중 (N005 BALLAD 80%)

**발생 경로**:
```
serendipity.py:63-89  controlled_drift():
  seed_vec = model.encode("K-Ballad piano emotional strings")
  noise = np.random.normal(0, drift_factor=0.6, dim=384)
  perturbed = normalize(seed_vec + noise)
  → genre 슬롯 검색: 벡터 공간에서 seed 인근 → BALLAD 클러스터 집중

song_forms.py:87-111  classify_genre_group():
  if "ballad" in text → BALLAD  (우선 매칭)
  if "piano" in text → BALLAD  (signal 매칭)
  if "emotional" in text → BALLAD
  → Ballad 계열 seed는 장르 분류에서도 BALLAD로 수렴
```

**근본 원인**: 벡터 공간 구조상 seed 인근 noise는 같은 클러스터(BALLAD) 내에 착지. drift_factor=0.6은 클러스터 탈출에 불충분.

**수정 가능 부분**:
- 장르그룹 쿼터: 배치 내 동일 그룹 최대 50% → 초과 시 장르 슬롯 재검색 (drift ↑)
- 장르 슬롯에만 drift 1.5배 적용

**한계**: drift를 키우면 장르는 분산되지만:
- 네이티브 적합성 하락 (코퍼스에서 먼 조합)
- SP 내부 coherence 하락 (장르와 악기 불일치)
- N003이 다양했던 건 noise가 우연히 다양한 방향으로 갔기 때문 (재현 불확실)

---

### 6. 서브테마 비효과 (키워드 히트율 19%)

**발생 경로**:
```
lyrics_themes.py:120-138  get_theme_query():
  sub_kr = random.sample(["처음","떨리","두근"], 3)   ← 서브테마 키워드 3개
  base = "처음 떨리 두근"                              ← 3토큰
       + "flutter first meeting excitement spring"    ← 5토큰
       + "이별 떠나 잊어"                              ← 메인테마 3토큰
       + "farewell goodbye separation pain..."        ← 6토큰
  → 총 ~17토큰 중 서브테마 = 3토큰 (18%)

lyrics_retriever.py:186-187
  base_query = f"{theme_query} {base_query}"
  → theme_query(17토큰) + genre+moods(10토큰) = 27토큰
  → 서브테마 비중: 3/27 = 11%

model.encode(27토큰 쿼리) → 384차원 벡터
  → 임베딩 모델은 전체 토큰의 가중 평균 → 서브테마 방향성 11%로 희석
```

**근본 원인**: 임베딩 검색은 토큰 수로 가중. 서브테마 3토큰이 전체 27토큰의 11%에 불과하여 벡터 방향에 미미한 영향.

**수정 가능 부분**:
- 서브테마 키워드 3회 반복 (3→9토큰, 9/33=27%)
- 2단계 검색: 1차 theme+genre 검색 → 2차 서브테마 키워드 포함 여부로 rerank

**한계**:
- 코퍼스에 "도시" 관련 가사가 10섹션 미만이면 rerank해도 무의미
- 임베딩은 의미적 유사성 기반 → 키워드 존재를 보장하지 않음 (구조적 한계)

---

### 7. 브래킷-SP 악기 불일치 (N005에서도 46% 불일치)

**발생 경로**:
```
lyrics_retriever.py:209-237  NON_LYRIC_TAGS (intro/outro/interlude):
  → bracket_presets.py가 SP 악기 기반 브래킷 생성 ← SP 일치 O

lyrics_retriever.py:238+  LYRIC_TAGS (verse/chorus/bridge):
  → Qdrant sunolang_lyrics에서 section 검색 → 원곡 가사 그대로 반환
  → 원곡 가사 내 [Electric Guitar Solo], [Strings Swell] 등은 원곡 SP의 악기
  → 현재 생성 SP에 strings가 없어도 원곡 브래킷의 [Strings Swell]이 그대로 출력

bracket_presets.py:169-183  SP 악기 추출 → 브래킷 후보 악기 일치도 우선:
  → 이 로직은 intro/outro에만 적용. verse/chorus 내부 브래킷에는 미적용
```

**근본 원인**: 가사 섹션(verse/chorus/bridge) 내부의 브래킷 디렉티브는 원곡에서 그대로 가져옴. 현재 SP와의 악기 일치 검증/치환 단계 없음.

**수정 가능 부분**:
- 검색 후 악기 일치도 점수 반영 (rerank): 브래킷 악기가 SP에 있는 섹션 우선
- 동의어 매핑: strings↔string orchestra, guitar↔electric guitar

**한계**:
- 원곡 브래킷을 그대로 사용하는 설계 — 브래킷 자체를 재작성하면 코퍼스 기반 원칙 위반
- 코퍼스에 현재 SP 악기 조합과 일치하는 가사 섹션이 없을 수 있음

---

## 운에 맡기는 부분 (3건)

### 8. 배치 간 크로스곡 유사성 (N003↔N004 37행 공유)

각 배치는 독립 실행. `batch_used_*`가 배치 간 공유되지 않음.
같은 코퍼스 + 같은 5테마(이별/사랑/밤/성장/자유) → 코퍼스 내 "attractor" 섹션(높은 점수의 인기 구절)이 매번 상위 반환.

```
코퍼스 내 song_id=148 verse (point 726):
  "더 이상 볼 수 없는 나를 / 왜 지켜야 하는지 몰라..."
  → "이별" 테마 검색 시 score 0.554로 최상위
  → N003, N004, N005 모두에서 선택
```

**통제 불가 이유**: 독립 배치는 독립 창작. 코퍼스의 상위 섹션이 반복 선택되는 것은 자연스러움. 실제 작곡가도 자기 앨범 내 곡 간 유사 표현 사용.

→ 단, **P0 수정(batch_used_song_ids)** 이 적용되면 배치 내 오염은 제거되고, 배치 간 유사성만 남게 됨. 배치 간 유사성은 Leo 판단(수용 가능).

### 9. 벡터 노이즈 방향

```
serendipity.py:75  noise = np.random.normal(0, drift_factor, 384)
  → 384차원 가우시안 노이즈의 방향은 매 실행 다름
  → N003 실행 시: noise가 RNB/ACOUSTIC/ROCK 방향으로 분산 (운 좋음)
  → N005 실행 시: noise가 BALLAD 클러스터 내부에 집중 (운 나쁨)
```

파라미터(seed, drift)가 같아도 결과 분포가 다름. 이는 numpy.random의 본질적 속성.

→ **확정적 수정으로 편차 감소 가능** (장르 쿼터), **완전 통제는 불가**.

### 10. 코퍼스 커버리지 한계

현재 코퍼스: 437곡, 4,620 lyrics 섹션.
- "도시" 서브테마 관련 섹션: 추정 20~30개
- "방랑" 서브테마 관련 섹션: 추정 5~10개
- 희귀 서브테마일수록 매칭 품질 하락

W002 60곡 + S시리즈 추가 인제스트 시 개선 예상이나, 현재 규모에서는 서브테마/장르 조합에 따라 품질 편차 불가피.

---

## 수정 우선순위 요약

| 순위 | 이슈 | 분류 | 예상 효과 |
|------|------|------|-----------|
| P0-A | batch_used_song_ids 추가 | 확정적 수정 | 배치 내 오염 ~90% 제거 |
| P0-B | 서브배치 → 단일배치 통합 | 확정적 수정 | 배치 추적 유효화 |
| P0-C | 코퍼스 SP 디렉티브 필터 | 확정적 수정 | "Layered leads" 류 완전 제거 |
| P1-A | SP 파라미터 복귀 (4/550) | 확정적 수정 | coh 0.50→0.57 회복 |
| P1-B | MAX_SENTENCES=9 게이트 | 확정적 수정 | SP 12문장→9문장 이내 |
| P1-C | 송폼 배치 내 분산 | 확정적 수정 | 동일 폼 최대 2회 |
| P2-A | 장르그룹 쿼터 (50%) | 효과 제한적 | BALLAD 80%→50% |
| P2-B | 서브테마 가중치 강화 | 효과 제한적 | 히트율 19%→30~40% |
| P2-C | 브래킷 악기 rerank | 효과 제한적 | 일치율 54%→65~70% |
| — | 배치 간 유사성 | 운 | 수용 (독립 창작) |
| — | 벡터 노이즈 방향 | 운 | 쿼터로 편차 감소 |
| — | 코퍼스 커버리지 | 운 | W002 인제스트 시 개선 |
