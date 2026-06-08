# 뮤직메이커2 업그레이드 제안서

**작성**: sunolanguage (Opus 4.8, 퍼플)
**일자**: 2026-06-07
**의뢰**: rag→sunolanguage (LEO 지시 2026-06-05) — "뮤직메이커는 계속 디벨롭할 활성 툴. 업그레이드 방안을 제안형으로 고민해달라."
**대상**: 레오뮤직프롬프트 생성기 = Suno Style Prompt Generator (`webapp/`, 패키지명 `suno-sp-builder` v0.1.0)
**배포**: musicmaker.arkedia.work:8113 (정적 nginx + cloudflared)

---

## 0. 요약 (TL;DR)

현 뮤직메이커는 **수동 슬롯 빌더**다. 잘 만들어졌으나 두 가지 구조적 한계가 있다:

1. **코퍼스가 고정·구버전**: 빌드타임에 `suno_dictionary.json` **v2.0(437곡/5,070단어, 2026-04-25)** 을 임포트. 그 사이 사전은 **v3.1(496곡/5,496단어/216장르)** 로, Qdrant 코퍼스는 **presets 10,646 / lyrics 5,858** 로 성장했다. 툴이 이 성장을 전혀 못 따라간다.
2. **본 엔진과 단절**: webapp의 SP 조립은 고정순서 룰베이스인데, sunolanguage 본 엔진(Serendipity = Qdrant 시맨틱 검색 + 품질게이트)은 별도로 존재한다. 사용자가 본 엔진의 품질·창발성을 누리지 못한다.

제안은 **3-Tier**로 나눈다:
- **Tier 1 (즉시, 저노력·고효과)**: 사전 v3.1 드롭인 교체 + 코퍼스 빌드 자동화 + SP 7문장 공식·트로트 Y016·부정프롬프팅 반영. 현 아키텍처 유지.
- **Tier 2 (중기)**: 작업 영속화(localStorage 히스토리)·품질게이트 인라인·다국어 가사 힌트 등 UX 강화.
- **Tier 3 (= "뮤직메이커2")**: 본 Serendipity 엔진을 백엔드로 연결한 **시맨틱 생성 모드**. 수동 빌더 → "코퍼스가 제안하는" 하이브리드 툴로 진화.

---

## 1. 현 구현 스냅샷

| 항목 | 현황 |
|------|------|
| 스택 | Vanilla JS + Vite 6 + sortablejs. ~1,500 LOC. 의존성 최소. |
| 레이아웃 | 3패널: global-settings / song-form-editor / preview-panel + 상단 template-bar |
| 상태 | `state/store.js` 단일 스토어 + pub/sub. 영속화 없음(Reset=`location.reload`) |
| 생성 | `sp-generator.js` 룰베이스 문장 조립 + 브래킷 구조 생성 |
| 데이터 | 빌드타임 정적 JSON 임포트 (vite alias `@rag`, `@reanalysis`) |
| 템플릿 | 20종 장르 프리셋(City Pop/K-POP/Ballad/Trot/EDM…) + 12종 송폼 |
| 이미 잘 됨 ✓ | 장르·악기 **검색 필터**, Copy SP/Lyrics/Both, **글자수 가드**(900자 danger — 1000자 한계 반영), () 보컬 디렉션, 섹션 드래그 재정렬, 장르 선택 시 슬롯 자동완성(autoFill) |

### 데이터 소스 실태

| 임포트 경로 | 파일 | 버전·코퍼스 | 상태 |
|---|---|---|---|
| `@rag/suno_dictionary.json` | suno_dictionary.json | **v2.0** · 437곡 / 5,070단어 / 189장르 (2026-04-25) | ⚠️ **구버전** |
| (미사용) | suno_dictionary_v3.json | **v3.1** · 496곡 / 5,496단어 / 216장르 (2026-05-09) | ✅ 존재, 미연결 |
| `@reanalysis/slot_genre_matrix.json` | slot_genre_matrix.json | v3.3 · 58장르(2+곡) / sp_entities 5,053 (2026-04-27) | △ 부분집계(311곡) |
| `@rag/genre_index.json`, `instrument_index.json` | — | meta v1.0 / 665곡 기준 | △ 혼재 |
| (Qdrant, 미연결) | sunolang_presets / sunolang_lyrics | **10,646 / 5,858** (2026-06-05 rebuild) | ❌ webapp 미사용 |

> **핵심 발견**: `suno_dictionary_v3.json`은 현 로더(`loader.js`)가 쓰는 6개 키(instrument_phrases / drum_vocab / production_vocab / key_signatures / mood_emotion / vocal_expressions)와 내부 구조까지 **스키마 동일** → **import 한 줄만 바꾸면 드롭인 교체 가능**. (검증 완료 2026-06-07)

---

## 2. 갭 분석

### G1. 코퍼스 최신화 (의뢰 1순위)
- 사전 v2.0→v3.1 미반영: 곡 437→496(+59), 단어 5,070→5,496(+426), 장르 189→216(+27).
- 헤더 문구 "437 tracks, 5,070 words" 하드코딩 → 실제와 불일치.
- 더 큰 문제는 **갱신 경로가 수동**이다: 사전 재빌드 후에도 webapp에 자동 반영 안 됨. rebuild→rsync 수동 워크플로(2026-05-02 admin 확인). 코퍼스가 주 단위로 자라는데 툴은 멈춰 있음.
- "Qdrant 10,646 미반영 의심"(의뢰)은 두 갈래로 분리해야 정확하다:
  - (a) **dictionary 단어사전**: v2→v3.1 갱신이면 해결 (Tier 1).
  - (b) **Qdrant 시맨틱 코퍼스**: 애초에 webapp 설계에 없음(정적 사전 기반). 이건 Tier 3 과제(엔진 연결).

### G2. SP 최신 문법
- 현 문장 순서: genre→mainInstrument→sectionInstrument→drums→vocal→effect→tempo→mood→arrangement.
- 확정된 **SP 7문장 공식**: GENRE→주악기(91%)→보조→드럼→보컬→**어레인지→템포(50.1%)**. 현재는 tempo가 arrangement·mood보다 앞 → 코퍼스 실제 순서와 어긋남.
- **부정 프롬프팅(absence 슬롯) 미지원**: matrix에 `absence` 슬롯 존재하나 UI 비노출. (단 트로트 Y016 검토결과 — not-Enka 부정문은 priming 역효과 → 부정문은 신중히. 부정 슬롯은 "no drums / no reverb"류 구조적 부재에 한정 권고.)
- **트로트 템플릿 Y016 미반영**: 현 trot 템플릿은 accordion+sax(✓)이나, kkeokk-ki→native vibrato·slides, traditional Korean bass→electric bass root-fifth, 12/8→shuffle 권고 미적용.
- "Key of X" 표기는 코퍼스 정합(652회) — 유지 OK. 구체 코드명/진행표기 0회이므로 추가 금지(현 구현 부합).

### G3. UX
- **작업 영속화 없음**: 새로고침/Reset 시 전부 소실. localStorage 자동저장·복원·세션 히스토리 부재(의뢰 예시 "히스토리" 언급).
- 검색·복사·글자수가드는 이미 양호 ✓ (의뢰 예시 일부는 이미 충족).
- 216장르 평면 스크롤 → 카테고리 접힘은 있으나(genreCategories) 즐겨찾기/최근사용 없음.
- 다국어: 가사 언어 힌트·다국어 보컬 디렉션 가이드 없음(S_INST200에서 16개 언어 코퍼스 확보했으나 툴 미활용).

### G4. 아키텍처 (가장 큰 기회)
- webapp = 룰베이스 수동조립 / 본 엔진 = Qdrant 시맨틱 + 게이트. **두 시스템이 완전 분리**.
- 사용자는 본 엔진의 강점(드리프트 기반 cross-genre 창발, 코퍼스 게이트 품질보증, 가사-SP coherence)을 못 누림.
- 정적 빌드라 코퍼스 갱신 = 매번 수동 rebuild+rsync.

---

## 3. 업그레이드 제안

### ★ Tier 1 — 즉시 (1세션, 저노력·고효과)

| # | 항목 | 내용 | 효과 |
|---|---|---|---|
| T1-1 | **사전 v3.1 드롭인** | `loader.js` import를 `suno_dictionary_v3.json`으로 교체(스키마 호환 검증됨). 헤더 문구를 빌드시 코퍼스 메타에서 자동 주입(하드코딩 제거). | 코퍼스 +59곡/+426단어/+27장르 즉시 반영 |
| T1-2 | **코퍼스 빌드 자동화** | `npm run sync-corpus` 스크립트: rag/ 최신 JSON·slot_matrix 검증→복사→버전배지 갱신. CI 한 번으로 rebuild까지. 수동 rsync 의존 축소. | 갱신 경로 1-커맨드화, 드리프트 방지 |
| T1-3 | **SP 7문장 순서 정정** | sp-generator 문장 순서를 공식대로 재배열(arrangement→tempo가 마지막). | 출력이 코퍼스 실제 SP 분포에 정합 |
| T1-4 | **트로트 Y016 반영** | trot 템플릿/추천에 native vibrato·slides, electric bass root-fifth, shuffle 반영. 부정문(not-Enka류) 금지 가드. | 트로트 SP 실측 품질 ↑ |
| T1-5 | **부정/부재 슬롯(선택)** | global에 "구조적 부재"(no drums, sparse, a cappella 등 absence 슬롯 어휘) 토글 노출. 정서부정문은 제외. | absence 슬롯 활용, 미니멀 표현 |

### Tier 2 — 중기 (UX·품질, 2~3세션)

| # | 항목 | 내용 |
|---|---|---|
| T2-1 | **작업 영속화** | store에 localStorage 자동저장/복원. 새로고침에도 유지. |
| T2-2 | **세션 히스토리** | 생성 SP/가사 스냅샷 N개 보관·복원·비교(의뢰 예시). |
| T2-3 | **인라인 품질게이트** | 본 엔진 `corpus_quality_gate` 룰(SP 디렉티브 누출 경고, INST/MIN 길이, 1행섹션) 경량 포팅 → 프리뷰에 실시간 경고 배지. |
| T2-4 | **다국어 가사 가이드** | 보컬 언어 선택 + 언어별 () 디렉션 예시(코퍼스 16개 언어 기반). |
| T2-5 | **즐겨찾기·최근사용** | 장르/악기/이펙트 빈도 학습 + 핀. |
| T2-6 | **장르 추천 근거 표시** | autoFill 슬롯에 "이 장르 N곡 중 빈도" 근거 툴팁(코퍼스 신뢰도 가시화). |

### ★★ Tier 3 — "뮤직메이커2" (엔진 연결, 별도 결정 필요)

핵심: **수동 빌더 → 시맨틱 생성 하이브리드**. 두 옵션.

- **옵션 A (정적 강화, 저위험)**: Qdrant를 빌드타임에 1회 질의해 장르별 top-k 시맨틱 추천을 정적 JSON으로 굽고, webapp이 이를 "추천" 패널로 노출. 백엔드 서버 불필요(현 nginx 정적 유지). 코퍼스 10,646 반영하되 인프라 변화 최소.
- **옵션 B (라이브 백엔드, 고기능)**: sunolanguage 엔진을 경량 API(FastAPI)로 래핑 → webapp에 "Auto-generate (Serendipity)" 버튼. seed+drift 입력→실시간 시맨틱 SP+가사+coherence 반환→사용자가 슬롯으로 받아 미세조정. 본 엔진 품질을 사용자 손에. 단 서버·DB·Qdrant 상시가동 필요(인프라 결정).

> 권고: **A를 먼저** (정적, 10,646 코퍼스 가치를 위험 없이 흡수) → 수요 확인 후 B.

---

## 4. 권고 로드맵

1. **이번/다음 세션**: Tier 1 전체 실행(드롭인+자동화+문법정정+트로트). 1000자 가드 유지([[feedback_sp_char_limit]]). 빌드 검증 후 LEO 시연.
2. **+1~2세션**: Tier 2 영속화·히스토리·인라인게이트.
3. **별도 결정**: Tier 3 옵션 A/B는 인프라(상시 백엔드 가동 여부)가 LEO/admin 결정사항 → 본 제안서로 의사결정 요청.

## 5. LEO 결정 요청 사항

- **Q1.** Tier 1 즉시 착수 승인? (현 아키텍처 무변경, 저위험)
- **Q2.** 뮤직메이커2(Tier 3) 방향 — 정적 강화(A) vs 라이브 엔진 백엔드(B)? 인프라 상시가동 가능 여부.
- **Q3.** 회신 경로 — LEO 직접 보고 vs rag 경유 (의뢰는 택일 허용).

---

## 부록. 검증 메모 (2026-06-07)
- v3.1 사전 6개 로더키 스키마 동일 확인 → T1-1 드롭인 안전.
- slot_genre_matrix v3.3은 311곡 부분집계(58장르). 전체 코퍼스 대비 보강 여지 → 재빌드 시 갱신 권고.
- 장르/악기 검색·Copy 3종·글자수 danger 가드는 **이미 구현됨** → 의뢰 UX 예시 중 일부는 충족 상태(중복 작업 회피).
