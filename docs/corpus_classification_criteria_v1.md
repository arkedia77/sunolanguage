# 코퍼스 분류 기준 — 현행판 v1.0

**작성일**: 2026-07-31 (3시간 재검토 세션 산출물)
**지위**: 분산돼 있던 분류 기준의 **통합 현행판 정본**. 개별 설계문서(expression_layer_design.md·slot_reclassify_v2.md 등)는 사료로 보존하되, 기준 충돌 시 이 문서가 우선. 차기 개정 시 이 파일을 v1.1로 갱신(파일 분리 금지).
**근거 표기 원칙**: 모든 수치는 실측 정본 파일 병기(R-P1).

---

## §0. 정본 지도 (어디에 무엇이 있나)

| 층 | 정본 | 내용 |
|---|---|---|
| 사전(코어) | `rag/suno_dictionary_v3.json` | v3.2 (2026-06-12), 556트랙·17,822엔트리·263장르 |
| 표현층(어댑터) | `sunolang.db` `expr_*` 4테이블 | 개념 437·표현 2,622·별칭 72 (2026-07-31 기준) |
| 슬롯 문법 | `docs/slot_reclassify_v2.md` | 10슬롯, SP 2,291문장 기준 (2026-04-18) |
| 장르 구문 유형 | `docs/manual_v3/ch1_classification.md` | Type A~D, 슬롯 출현 순서 |
| 전파 정책 | `docs/corpus_propagation_policy.md` | v3.2, A(원자)/B(재빌드)/C(이벤트) |
| 가사 코퍼스 밴드 | `data/n_series_coherence_retro.json` | coherence 실측 140행 |
| 트랙 원장 | `sunolang.db` `tracks` | 153행, phase1/phase4_tier1/phase5 |

## §1. 코퍼스 셋 구분

1. **원천 코퍼스** — Suno 앱 재분석 SP 원문. 사전 v3.2 기준 556트랙(leomusic 318 + Wave1 외부 60 + stems 95 + Dead Budget 10 + S시리즈 등). *유일한 attestation 원천* — 여기 등장한 어휘만 native 판정 가능.
2. **사전(코어)** — 원천에서 추출한 카테고리별 어휘 사전. 코어는 불변(재발명 금지), 갱신은 재빌드(B1)로만.
3. **표현층(어댑터)** — 사전 원자 437개념 × 6레지스터. 번역이 정본을 대체하지 않음(코어+어댑터, R-P4).
4. **가사 코퍼스** — N시리즈 등 가사 자산. 어휘 코퍼스와 별도 축(§7).
5. **트랙 원장(tracks)** — 수집·분석 진행상태 관리(phase1 100·phase4_tier1 30·phase5 23). 어휘 판정과 무관한 공정 관리층.

## §2. 어휘 계층 모델 — 3층→**4층** 개정 ★07-31

Dead Budget(2026-04-24)의 3층 모델에 **프라이어층 조건부 유효**를 신설한다.

| 층 | 정의 | 판정 근거 |
|---|---|---|
| L1 native | Suno가 자발적으로 출력하는 어휘 | 원천 코퍼스 attestation ≥1 |
| L2 passive | 입력하면 이해하나 자기 말로 번역해 출력 | 라운드트립·생성검증(§6) |
| L3 dead-zone | 입력해도 무반응 | 라운드트립 0반응, `expr_inbound_aliases kind='dead_zone'` |
| **L4 prior-bound** ★신설 | **어휘는 native이나 효력이 프라이어층(가사 정서·에너지·구조)에 종속** | 07-11 K3016 실측: 저에너지 소프트발라드+독백 조합서 baritone 지시 5회 전부 무효 — dead-zone 0건 네이티브 정형+브래킷 이중결합으로도 실패. 어휘·표기·구조(프라이어) 3층 분리 실증 |

**함의**: attested_count가 높아도 무조건 유효가 아니다. 성부·성별 지시가 대표 사례(현재 vocal 성부 3개념 notes에 caveat 등재). 어휘 유효성 판정 시 "어느 프라이어 조건에서 실측됐나"를 병기할 것.

## §3. 카테고리 — 11 원자 + 1 예외 (계 12)

DB 실측 분포(2026-07-31, `expr_concepts`): technique 120 · mood 63 · production 61 · instrument 55 · dynamics 34 · timbre 25 · tempo_rhythm 20 · drums 19 · vocal 17 · vocal_chorus 13 · harmony 8 = **원자 11종**.

**genre 예외(2건: jazz·blues)**: 설계상 genre는 원자화 제외(장르명은 시스템 간 공용어, `genre_vocabulary_map` 264로 별도 관리)이나, **인바운드 별칭 타깃용 시드**(origin='alias_seed')로만 2건 존재. 신규 genre 개념 추가 금지 — 장르는 사전의 genre_vocabulary_map이 정본.

**origin 구분**: dictionary 405(사전 v3.2 원자 추출) + alias_seed 32(별칭 타깃용 시드 = mood 30 + genre 2, 실측 2026-07-31). 설계문서의 카테고리 수치(mood 33 등)와 DB 실측(mood 63)의 차이는 alias_seed 시드분 — attestation 판정 시 origin='dictionary'만 원천 코퍼스 근거로 취급.

**장르 분류의 알려진 한계 (기준에 편입)**:
- **드리프트**: Suno는 사운드앵커>장르명 — UK Drill→Industrial techno/EBM 드리프트, native 'Trot' 라벨 1/12(W001 GT 재분석 06-13), Gukak 0건. 비서양 장르는 편성·질감 어휘로 우회(별칭 테이블 등재).
- **크로스오버 유효**: 'Classical-X Crossover' 계열 10종 생성 10/10 성공(JIOBD01 07-27) — 복합 구문형 장르 라벨(manual_v3 Type B~D)은 생성 방향으로도 유효.

## §4. 레지스터 6종 + 엔진별 uptake 편차 ★07-31

`expr_registers` 6종: suno_native(정본·canonical) / music_theory_en / plain_ko / plain_en / llm_prompt / tags.

**llm_prompt 개정**: 대상을 "MusicGen/Stable Audio/**Lyria**류"로 확장. ★엔진별 uptake 편차를 notes에 기록하는 것이 기준 — 첫 등재: **Lyria 절대조성=약한 시민권**(07-24 key-uptake 3세션 실측: restatement echo돼도 렌더는 전조/드롭, C major 지시→E♭ 렌더. BPM·groove·화성어휘·편성·다이내믹은 강한 echo). Lyria엔 상대화성·리듬·편성으로 유도. 정본: `data/lyria_probe/lyria_probe_set_v0.json` ★structure_finding_20260724_key_uptake.

## §5. 판정 기준 (attested / confidence / 별칭)

- **attested_count**: 해당 원자를 포함한 사전 엔트리 수 합산 — *salience 순서용 근사치*(컴파운드 중복 합산, 정확 빈도 아님).
- **confidence**: authored 표현의 자기평가(high/medium/low). 낮으면 정직 표기 — 상향은 실측으로만.
- **표면지표 상한 원칙**: 문자열 지표(CER/WER류)는 confidence med 상한 — 렌더 청취(가청) 확인 전 attested 승격 금지(layer2_fidelity_spec_v0 §핵심원칙, 07-19).
- **inbound_aliases 3종**(계 72): `dead_zone` 32(외부어→attested 우회 안내) / `ko_glossary` 33(ko→en attested) / `blocked` **7**(차단 규칙).

**blocked 규칙 현행 7종** (5→7, ★07-31 신설 2):
1. 구체 코드명(Am, Dm7 등) — 0회, 'key of X'만 유효(652회)
2. 코드 진행 표기(II-V-I 등) — 0회
3. 다이나믹 마킹(p/mf/ff) — 0회
4. mastering 용어 — corpus 2건
5. 감정 브래킷([기분] 등) — 브래킷은 악기/보컬/섹션만
6. ★negative 성별 지시('no female vocals' 등) — 0건(featuring a male... 95 vs no female 0, 07-11 실측)
7. ★용도성 명칭(OST, BGM) — 실질 0건. 용도는 메타로, 콘셉트는 mood 어휘로(07-11 실측)

## §6. passive(생성검증) 승격 경로 ★07-31 신설

**문제**: 원천 코퍼스는 Suno의 *출력*만 수집 → 입력 유효성(L2 passive)은 attestation으로 못 잡는다.
**기준**: 생성 배치에서 저빈도/무빈도 어휘가 유효 실증되면 — ①attested_count는 절대 오염하지 않는다(원천=재분석 SP만) ②해당 개념 suno_native 표현의 notes에 `[날짜 배치명 생성검증]` 형식으로 등재 ③개념이 아예 없으면(attested 0) DB 신설 금지 — 본 문서 아래 대장에만 기록.

**passive 검증 대장 (현행)**:
| 어휘 | 실증 | 근거 |
|---|---|---|
| choir (attested 4) | 콰이어 배분 3곡 포함 10/10 성공·LEO GO | JIOBD01 07-27~30 |
| a cappella (attested 0) | 동일 배치 생성 유효 | JIOBD01 07-27 |
| () 괄호 보컬 디렉션 | 입력 효과 4/4 실현(hums/melisma/trills/spoken) | Dead Budget 04-25 Leo 청취 |
| K-pop trot | SP에서 유효 확인 | 04-23 Leo 확인 |

## §7. 가사 코퍼스 — coherence 통제밴드

- **coherence는 최대화 대상이 아니라 통제 밴드** — 저-coh 섹션 단절은 창의성 레버일 수 있음(Leo 가설 06-05), 고-coh(>0.80)는 단조 위험.
- **밴드 현행 [0.45, 0.7]** — N시리즈 14배치 140행 실측: 평균 0.5562, low 14 / band 116 / high 10 (83% 밴드 내). 정본: `data/n_series_coherence_retro.json`.
- 제거 대상은 *무작위* 단절이지 *대비(contrast)* 아님 — 섹션 간 전환은 musically meaningful 지점(bridge/drop)에서 의도적 허용.

## §8. 슬롯 문법 (포인터)

SP 구조 분류는 `docs/slot_reclassify_v2.md` 10슬롯 체계 현행 유지(장르선언→악기→드럼→보컬(메인/코러스)→템포·조성→믹싱→이펙터→사운드FX→편곡총평→없음선언). 하나의 표현이 복수 슬롯에 들어가는 것이 정상 — 규칙이 아닌 '가능성 높은 패턴'. 슬롯 출현 순서 실측은 manual_v3 ch1 §1.1.

**버전 종속 행동 (슬롯 5 관련)**: v5.5부터 마지막 코러스 pump-up modulation 자동 생성(발라드+록 확인, 05-09 Leo 실청취·DB검증 S018_16 1건). SP 전조 지시 불요할 수 있음 — 서양 팝 타깃은 'no key change' 네거티브 테스트 필요.

## §9. 갱신 트리거·버전 이력

- **사전 재빌드(B1)**: 신규 ≥30곡 누적 / 시간 상한 90일+≥10곡 등 셋 중 하나(전파 정책 §B1). 재빌드 시 표현층은 `build_expression_db.py` 재실행→신규 원자만 증분 저작(기존 저작분 suno_term 키 보존).
- **이 문서**: 분류 *기준 자체*의 변경(층 모델·카테고리·레지스터·blocked)이 있을 때만 버전업. 개별 어휘 추가는 버전업 사유 아님.

| 버전 | 일자 | 변경 |
|---|---|---|
| v1.0 | 2026-07-31 | 최초 통합판. ★4층 모델(L4 prior-bound 신설) / blocked 5→7 / llm_prompt 엔진편차 기준(Lyria) / passive 승격 경로 신설 / coherence 밴드 실측 편입 / 장르 드리프트·크로스오버 한계 편입 |

## §10. 07-31 재검토 반영 요약 (DB 변경분)

| 변경 | 대상 | 근거 |
|---|---|---|
| vocal 성부 3개념 suno_native notes에 프라이어 caveat | male_baritone/male_tenor/female_soprano_vocals | 07-11 K3016 |
| dead_zone 별칭 +4 (저음 형용사 en/ko·트로트 ko/en) | expr_inbound_aliases | 07-11·06-13 W001 |
| blocked +2 (negative 성별·용도명 OST/BGM) | expr_inbound_aliases | 07-11 |
| llm_prompt 2건 notes Lyria caveat + 레지스터 정의 확장 | harmony:key_change·modulation / expr_registers | 07-24 key-uptake |
| choir 생성검증 note | vocal_chorus:choir | 07-27 JIOBD01 |
