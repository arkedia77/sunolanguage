# Suno 가사 AI 어시스트(Variations/Rhymes/Reference) 코퍼스 확장 설계

**작성**: 2026-07-04 · **요청**: sunomusic (LEO 지시) · **구동**: sunomusic CDP 하베스터 / **설계**: sunolanguage

---

## 0. 성격 규정 (설계 전제 — 중요)

Suno 가사에디터의 Variations/Rhymes/Reference는 ★**Suno의 오디오 분석 네이티브 어휘가 아니라 LLM 가사 리라이트 어시스트**다. 우리 본 코퍼스(실오디오 업로드→Suno 분석 SP/브라켓 = Suno 네이티브)와 **계보가 다르다**.

→ **원칙**: 본 코퍼스(`lyrics_chunks`/`sunolang_lyrics`)에 직접 섞지 않는다. **별도 계보**(`lyric_variations` 테이블 + 별도 Qdrant 컬렉션/네임스페이스)로 관리하고, 승격은 게이트 통과 시에만. [[feedback_corpus_driven_freedom]] "생성 후 게이트로 통제" 원칙 계승.

**가치**: (a) 가사 생성엔진의 **패러프레이즈 다양성 공급**(같은 의미 다른 표현 — N시리즈 단조로움 완화 [[feedback_n_series_diversity]]) (b) **운율 사전**(Rhymes) (c) Reference 기반 구절확장.

---

## 1. 3기능별 확장 방식

### A. Variations — 원문↔변형 패러프레이즈 페어 (주력)
- **방식**: 본 코퍼스 가사행 N개를 시드 → 각 행 드래그선택 → Variations 4후보 하베스트 → (원문, 변형[4], 소스행, 라벨) 로우 적재. 재생성(↻)으로 행당 최대 8~12후보까지 증량 가능.
- **용도**: lyrics_retriever의 패러프레이즈 풀. 현재 풀 고갈(97.7%, [[project_lyrics_pool_exhaustion]])의 **의미보존 증량책** — source song은 그대로지만 표현 variant를 늘려 exclude-history 압박 완화.
- **★게이트 (2026-07-04 한국어 파일럿으로 정정 — 중요)**: 애초 jaccard 0.4~0.85 밴드로 설계했으나 **한국어 파일럿 실측 결과 부적합**. 한국어는 교착어(조사·어미)라 좋은 패러프레이즈도 표면 토큰이 크게 달라 jaccard가 낮게 나옴(파일럿 11후보 중 jaccard 밴드내 2/11인데 육안·임베딩으론 10/11 양호). → **주 지표를 임베딩 코사인(의미보존)으로 교체**:
  - **채택 밴드: 임베딩 코사인 0.70 ≤ cos < 0.985** (paraphrase-multilingual 모델). cos≥0.985=near-dup(무가치), cos<0.70=의미이탈.
  - **jaccard는 보조**(near-dup 상단컷 백업, ≥0.9 즉시 reject)로만.
  - 파일럿 검증: 코사인 밴드로 10/11 채택(sunomusic 육안 HIGH와 일치), jaccard 밴드는 2/11(과폐기).
  - 누출검사(is_lyric_leak, 영어 악기서술 배제)·최소행·중복 검사는 유지.

### B. Rhymes — 운율 사전 코퍼스
- **방식**: 코퍼스 고빈도 행말 단어 시드 → Rhymes 세트 하베스트 → (단어, 운율단어[]) 적재. 한국어는 이 기능이 영어 위주라 **영어 가사/후렴 훅에 한정** 적용(한국어 운율은 kiwipiepy 음절 기반 별도).
- **용도**: 훅/후렴 운율 보강. 규모 작음(보조).

### C. Reference — 구절기준 생성 확장
- **방식**: 코퍼스 대표 구절을 reference 칩 투입 → 'Help me write lyrics'로 그 결기준 신규 가사 생성 → 신규 로우. 단 이건 **신규 창작**이라 variation보다 검증 부담 큼(누출/1행 게이트 필수).
- **용도**: 저커버리지 무드/테마 구절 확장. 파일럿 후 판단(우선순위 하).

---

## 2. 산출 스키마 (신규 테이블 `lyric_variations`)

```sql
CREATE TABLE lyric_variations (
  var_id        SERIAL PRIMARY KEY,
  source_type   TEXT NOT NULL,        -- 'variations' | 'rhymes' | 'reference'
  source_song_id INT,                 -- 원문이 온 본 코퍼스 곡(추적)
  source_chunk_id TEXT,               -- lyrics_chunks 시드 청크
  original_text TEXT NOT NULL,        -- 시드 원문(행/구절/단어)
  variant_text  TEXT NOT NULL,        -- 하베스트 결과 1건(4후보면 4로우)
  variant_rank  INT,                  -- 팝업 내 순번(1~4, 재생성분은 5+)
  lang          TEXT,                 -- 'ko' | 'en'
  section_tag   TEXT,                 -- verse/chorus/hook (시드 섹션)
  cosine_to_src REAL,                 -- ★원문 대비 임베딩 코사인(주 게이트, 0.70~0.985 채택)
  jaccard_to_src REAL,                -- 원문 대비 토큰 자카드(보조, near-dup ≥0.9 컷)
  gen_model     TEXT DEFAULT 'suno_lyrics_assist_v5.5',
  gate_status   TEXT DEFAULT 'pending', -- pending|accepted|rejected(과유사/이탈/누출)
  harvested_at  TIMESTAMPTZ DEFAULT now(),
  harvested_by  TEXT DEFAULT 'sunomusic'
);
```
- 4후보 = 4로우(variant_rank 1~4). 원문↔변형 페어는 (original_text, variant_text)로 자명.
- **게이트**(`gate_status`): jaccard 밴드(0.4~0.85) + is_lyric_leak(영어 악기서술 배제) + 최소행/중복 검사. corpus_quality_gate 로직 재사용.
- 승격: `gate_status='accepted'`만 별도 Qdrant 컬렉션(`sunolang_lyric_variants`)에 임베드 → retriever가 옵션으로 참조(본 코퍼스와 소스 구분 유지).

## 3. 규모·배치 형식 제안

- **파일럿(V-PILOT)**: 시드 30행(장르/섹션 다양: verse 12·chorus 12·hook 6), 행당 Variations 4후보(재생성 0) = 120 variant. 게이트 통과율·품질 실측 후 규모 확정.
- **본배치**: 시드 200~300행, 행당 4후보(+저수확행만 재생성 1회), 예상 ~1,000 variant. jaccard 게이트 후 유효분만.
- **라벨링 축**: source_song_id·section_tag·lang·genre(시드 상속) + jaccard_to_src(게이트). 무드/세대 라벨은 시드 곡 메타 상속(신규 판정 불요).
- **언어**: Variations는 영어 시드에서 품질 확인됨. 한국어 시드 하베스트 품질은 파일럿에서 검증(불확실 — Suno 어시스트 한국어 성능 미확인).

## 4. sunomusic 하베스트 스펙 (구동 인터페이스)

sunomusic이 CDP 하베스터로 돌릴 입력/출력 계약:

**입력** (sunolanguage → sunomusic, 시드 리스트):
```json
{ "batch":"V_PILOT", "command":"variations", "regenerate":0,
  "seeds":[ {"seed_id":"vp-001","source_song_id":123,"source_chunk_id":"lyrics_verse_1_000",
             "lang":"ko","section_tag":"verse","text":"화면을 끄자 천장이 보였어"}, ... ] }
```
**출력** (sunomusic → sunolanguage, 하베스트):
```json
{ "batch":"V_PILOT","results":[ {"seed_id":"vp-001","original":"...","variants":["..4개.."],
    "regenerated":false } ] }  // 우리가 jaccard 계산·게이트·적재
```
- sunomusic 역할: CDP 선택→툴바→팝업 하베스트→JSON 반환 (Apply·생성 불요 — 우리는 텍스트만 수확).
- sunolanguage 역할: 시드 선별(본 코퍼스에서)·jaccard 게이트·`lyric_variations` 적재·승격.

## 5. 리스크·미결

- ★**계보 오염 방지**: 절대 본 코퍼스에 직접 안 섞음. variant는 'Suno 네이티브'가 아님을 스키마·컬렉션 분리로 강제.
- 한국어 품질 미검증 → 파일럿 필수.
- Reference(신규창작)는 검증부담 커서 파일럿 후 판단.
- 크레딧 0(텍스트 어시스트) 확인됨 — 하베스트 규모 제약 없음(생성만 과금).

## 다음
- 본 설계 sunomusic 회신 → 합의 시 V_PILOT 시드 30행 선별(본 코퍼스에서)·전달 → sunomusic 하베스트 → 게이트·적재 → 품질 실측 → 본배치 규모 확정
- `lyric_variations` DDL admin 실행 요청(신규 테이블)
