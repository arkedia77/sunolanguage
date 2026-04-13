# leomusic-base 어휘사전 v1.1 리뷰 반영

**리뷰 수신**: 2026-04-12 20:00 (`leomusic-base_sunolanguage_20260412_200000_어휘사전리뷰.json`)
**반영일**: 2026-04-13

---

## Q1. Aliases 매핑 (68악기 + 64주법) 상태

- **base 답변**: 미착수. 신디사이저 Deep Knowledge Phase 완료 후 착수 예정.
- **sunolang 반영**: 대기. KANBAN `IN PROGRESS` 유지, 별도 재촉 없음.

## Q2. 부족 카테고리 — 보강 적용

| 영역 | 심각도 | 기존 | base 제안 | 반영 방침 |
|------|--------|------|-----------|----------|
| 화성 | 높음 | 23개 | chord progression / voicing / modal interchange / secondary dominant / tritone substitution / pedal tone / HARMONIC_DEFAULT 38장르 | **base export 요청** |
| 다이나믹스_구조 | 중간 | 35개 | section dynamics / build-drop / tension-release / dynamic range + ENERGY_RANGE 엣지 | **base export 요청** |
| 보컬 | 높음 | 54개 | vocal grain 15종 + voice tag 47종 + falsetto/belt/head voice | **Phase 6 전곡 업로드로 자체 수집 + base export 병행** |

## Q3. SP 작성 시 빠진 4개 영역 — 신규 서브카테고리

1. **공간감/리버브** — dry room, cathedral reverb, intimate close-mic, wide stereo field 등
   - → 기존 `프로덕션(74)`에서 분리, 별도 `spatial/reverb` 서브카테고리 신설
2. **레이어링/텍스처** — layered pads, sparse arrangement, dense orchestration 등
   - → 신규 카테고리 `texture_relation` 추가
3. **에너지 곡선** — gradual build, sudden drop, climax peak 등
   - → 다이나믹스 확장 항목으로 흡수 (시간축 관점)
4. **악기 관계** — call-response, rhythmic lock, counterpoint, unison doubling 등
   - → base의 `PAIRS_WITH / ENSEMBLE_SLOT` 엣지 참조, 신규 카테고리 `instrument_relation`

## Q4. 장르 확장 우선순위

| 순위 | 장르 | 일정 |
|------|------|------|
| 1 | K-Pop (서브장르), R&B/Neo-Soul, Lo-fi Hip-Hop | Phase 6 기획에 포함 |
| 2 | Jazz 서브장르 (Smooth/Bebop/Modal/Fusion), Ambient/Chillout, Cinematic/Orchestral | Phase 7 |
| 3 | Latin (Bossa/Reggaeton/Salsa), African (Afrobeat/Highlife), World Fusion | Phase 8+ |

현재 커버: 70/226장르 (phase1_stem 오분류 정리 후, 2026-04-13).

---

## 후속 액션

1. **base에 JSON export 요청** — 화성 / 보컬 / 다이나믹스 3개 카테고리 (base 제안 수락)
2. **신규 서브카테고리 스키마 설계** — spatial, texture_relation, instrument_relation
3. **Phase 6 기획서 작성** — 전곡 업로드 + 1순위 장르 수집
