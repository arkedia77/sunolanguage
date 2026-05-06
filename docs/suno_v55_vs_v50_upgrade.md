# Suno v5.5 vs v5.0 업그레이드 종합 정리

**작성일**: 2026-05-06  
**소스**: 웹 리서치 + Notion 오븐 에이전트 연구 + leomusic2 조사 + sunolang RAG 현황

---

## 1. 핵심 철학 전환

| 구분 | v5.0 | v5.5 |
|------|------|------|
| **방향** | 더 강한 생성 모델 | 더 개인화된 창작 모델 |
| **핵심 가치** | 음질·프롬프트 반응성 | 목소리·스타일·취향 개인화 |
| **워크플로우** | 프롬프트 → 원샷 생성 | 프롬프트 + 후처리 + 리파인먼트 |

> v5.5는 "프롬프팅이 더 이상 핵심 기술이 아닌" 시대로의 전환.  
> 진짜 기술은 **시스템이 나에게 반응하도록 조형하는 것**.

---

## 2. 신기능 3종 (2026-03-26 출시)

### A. Voices (보이스 클로닝)
- **대상**: Pro/Premier 구독자
- **방식**: 10초+ 가창/랩 녹음 업로드 또는 라이브 캡처 → 본인 확인(랜덤 문구)
- **효과**: 음색(timbre), 텍스처, 음역대 캡처 → 생성 음악에 반영
- **제한**: 본인만 사용 가능 (공유/마켓플레이스 미제공)
- **sunolang 시사점**: 일관된 보컬 톤 확보 → 배치 내 보컬 일관성 향상 가능

### B. Custom Models (커스텀 모델)
- **대상**: Pro/Premier 구독자, 최대 **3개**
- **방식**: 본인 오리지널 곡 6곡 이상 업로드 (권장 10~60곡, 스타일 일관성 중요)
- **효과**: v5.5가 해당 스타일 학습 → "나의 사운드"에 가까운 출력
- **Voices와 차이**: Voices = 보컬 특성만 / Custom Models = 전체 음악 스타일
- **sunolang 시사점**: 장르별 1개씩 3개 활용 가능 (예: BALLAD/R&B/ACOUSTIC)

### C. My Taste (취향 학습)
- **대상**: 모든 사용자 (무료 포함)
- **방식**: 별도 업로드 불필요, 사용 패턴 자동 학습 (장르·무드 축적)
- **효과**: 시간 경과에 따라 생성 결과 자동 개인화
- **sunolang 시사점**: 계정 사용 패턴 축적 시 자연 최적화

---

## 3. 음질·오디오 특성 변화

| 항목 | v5.0 | v5.5 | 변화 정도 |
|------|------|------|-----------|
| **라우드니스** | 높음 (라디오 레디) | **1.5~2dB 낮음** (스튜디오 레디) | 큰 차이 |
| **크레스트 팩터** | 낮음 (과압축) | **높아짐** → 트랜지언트 보존 | 큰 차이 |
| **고역 에너지 비중** | 17~22% | **34~36%** (거의 2배) | 큰 차이 |
| **메탈릭 보컬** | 존재 | **크게 개선** | 큰 차이 |
| **출력 분산** | 안정적 | **분산 증가** (동일 프롬프트 편차 큼) | 주의 |
| **스펙 (SR/비트레이트)** | 44.1kHz, 128/320kbps | 동일 (변경 없음) | 변화 없음 |
| **최대 생성 길이** | 4분 | **8분** | 2배 |
| **악기 분리도** | 보통 | **더 명확** | 개선 |
| **보컬 표현력** | 보통 | **비브라토/호흡음/자음** 자연스러움 | 개선 |

### v5.5에서 개선된 것 (후처리 부담 감소)
- ~~메탈릭 보컬 보정~~ → 경미한 경우만
- ~~트랜지언트 복구~~ → 크레스트 팩터 향상
- ~~과도한 컴프레션 해제~~ → 헤드룸 확보
- ~~고역 에너지 부족~~ → 고역 2배 증가 (Pro 기준)

### v5.5에서도 여전한 문제
| 아티팩트 | 설명 | 심각도 |
|----------|------|--------|
| **리버브 포그** | Suno 시그니처 앰비언스, 전체 탁함 | 높음 |
| **스테레오 이미징** | 비정상 위상, 과도하게 좁/넓음 | 높음 |
| **Low-mid 블리딩** | 킥/베이스 200-400Hz 탁함 | 중간 |
| **AI 스펙트럼 시그니처** | 보코더 아티팩트, smeared highs | 중간 |
| **16kHz 컷오프** | Free 플랜 MP3 한계 (버전 무관) | Free만 |

---

## 4. 프롬프트 엔지니어링 변화

### SP Top-Anchor 원리 (v5.5 강화)
v5.5에서 SP 필드 **앞부분 가중치**가 더 명확해짐.

**권장 배치 순서**:
```
1. Genre/Subgenre     — 가중치 최고
2. Mood/Energy        — 높음
3. Instruments (핵심 2개) — 높음
4. Vocals (grain, delivery) — 중간
5. Production/Harmony — 낮음
```

### 새로운 프롬프트 기법
- **네거티브 프롬프팅**: "no autotune", "no synths", "dry vocal" 등 → v5.5에서 반응성 향상
- **세밀한 보컬 제어**: "breathy", "raspy", "falsetto" 등 보컬 디렉션 더 잘 반응
- **스타일 벡터 스태킹**: 여러 형용사 조합으로 교차 스타일 가능
- **감정 아크 제어**: 섹션별 에너지 변화 지시 반응 개선

### SP 길이 이슈
- 커뮤니티 권장: 200자 이내
- sunolang/KR2 현실: 연주 디렉션 포함 800~1000자
- **과포화 가설과 연관**: v5.5에서도 SP 상한 근접 시 반응성 저하 가능 → A/B 테스트 필요

---

## 5. Studio 기능 (v5.5 신규)

| 기능 | 설명 |
|------|------|
| **스템 익스포트** | 최대 12개 time-aligned WAV (보컬/드럼/베이스/기타/신스/패드/스트링/브라스/키보드/퍼커션/이펙트) |
| **스템 품질** | 내부 표현 접근 → 외부 Demucs보다 크로스토크 적음 |
| **출력 포맷** | MP3, WAV, Tempo-Locked WAV, MIDI, WAV+MIDI |
| **Remove FX** | 리버브/이펙트 제거 (풀 믹스 디리버브보다 깨끗) |
| **편집 모드** | 개별 스템 편집 + 리믹싱 |

---

## 6. sunolang에 대한 시사점

### 긍정적 영향
1. **SP 반응성 향상**: 우리 corpus 어휘가 v5.5에서도 유효할 가능성 높음 (네이티브 어휘 기반)
2. **네거티브 프롬프팅 활용**: "no autotune", "dry" 등 배제 지시로 정밀도 향상 가능
3. **8분 생성**: 긴 곡 테스트 가능 (클래식/앰비언트)
4. **악기 분리도 향상**: 멀티 악기 SP 지시가 더 잘 반영될 가능성

### 주의 사항
1. **출력 분산 증가**: 동일 SP로도 결과 편차 큼 → 테스트 시 반복 생성 필요
2. **현 corpus는 v5 기반**: 437곡 모두 v5(chirp-crow) 재분석 결과. v5.5 재분석 결과와 차이 있을 수 있음
3. **Top-Anchor 미적용**: 현재 S001~S017 SP는 Top-Anchor 구조 미반영 → 다음 시리즈에서 적용 검토
4. **Custom Model 기회**: S001~S017 결과물 중 우수작으로 Custom Model 학습 가능

### 즉시 실행 가능 TODO
- [ ] S001~S004 결과 수신 후 v5.5 재분석 비교 (동일 곡 v5 vs v5.5 출력 차이)
- [ ] 네거티브 프롬프팅 테스트 배치 설계 ("no reverb", "no autotune" 효과 측정)
- [ ] Top-Anchor 구조 A/B 테스트 (현행 SP vs Top-Anchor 적용 SP)
- [ ] SP 길이별 테스트 (200자 vs 500자 vs 900자) — 과포화 가설 검증

---

## 7. 오븐 에이전트 연구 핵심 (후처리 파이프라인)

오븐 에이전트(2026-05-05)가 정리한 v5.5 맞춤 후처리:

### 권장 풀 믹스 파이프라인 (무료/Python)
```
Suno WAV → AudioSR/Apollo(대역폭 확장) → pedalboard(EQ/압축) → matchering(레퍼런스 매칭) → pyloudnorm(-14 LUFS)
```

### v5.5에서 특히 효과적인 도구
| 도구 | 용도 |
|------|------|
| **Apollo** | MP3→Lossless 복원, 풀 믹스 최적 |
| **matchering** | 프로 레퍼런스 트랙과 주파수/라우드니스 매칭 |
| **DENOISE-AI** | Suno/Udio 전용 AI 아티팩트 제거 |
| **Suno Studio 스템** | 내장 12트랙 분리 (외부 Demucs보다 우수) |

---

## Sources
- [Suno v5.5 공식 블로그](https://suno.com/blog/v5-5)
- [Suno Help: What's New in v5.5](https://help.suno.com/en/articles/11362305)
- [Suno v5.5 vs v5: What Actually Changed](https://suno-v5.com/blog/suno-v5-5-vs-v5-what-actually-changed)
- [7 Suno v5.5 Behaviors Every Creator Needs to Know](https://www.jgbeatslab.com/ai-music-lab-blog/suno-v5-5-behaviors-every-creator-needs-to-know)
- [Suno V5.5 Full Rollout: Core Differences](https://suno.hk/blog/suno-v55-comprehensive-comparison/)
- [MindStudio: What Is Suno 5.5](https://www.mindstudio.ai/blog/what-is-suno-5-5-voice-cloning-studio-features)
- [Suno V5.5 Advanced Prompt Engineering 2026](https://suno.bi/blog/suno-v5-5-prompt-engineering-advanced-techniques-2026-en)
- [The End of Prompt-and-Pray](https://jackrighteous.com/en-us/blogs/guides-using-suno-ai-music-creation/end-of-prompt-and-pray-suno-v5-5)
- [Prompting Is Not the Skill Anymore](https://medium.com/@J.S.Matkowski/prompting-is-not-the-skill-anymore-1e446c937c0f)
- [Suno v5.5 Complete Guide: Voices, Custom Models & My Taste](https://suno.bi/blog/suno-v5-5-voices-custom-models-my-taste-guide-2026-en)
- Notion: 오븐 에이전트 "Suno 후처리 음질 향상 연구" (2026-05-06)
- Notion: "Suno v5.5 신기능 조사 + SP Top-Anchor 전략" (2026-03-27)
