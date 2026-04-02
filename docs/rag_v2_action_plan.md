# RAG v2 Deepdive → sunolanguage 활용 방향

**작성일**: 2026-04-02
**기반**: mukl deepdive v2 (47 레퍼런스, 12 gaps, 실험 프로토콜)

---

## 즉시 적용 (Phase 2-3 진행 중 병행)

### 1. Audiocards 템플릿 차용 (G5)
- Suno tags 파싱 시 Audiocards의 구조화 메타데이터 필드를 참조
- 현재 파싱 스크립트 8개 카테고리 → Audiocards 체계와 매핑 검증
- **적용 시점**: 파싱 스크립트 고도화 시

### 2. SunoCaps 비교 데이터 (G6)
- 256개 Suno 샘플 + 감정/프롬프트 정렬 주석
- 우리 데이터와 직접 비교 가능 (같은 플랫폼, 다른 시기)
- **적용 시점**: Phase 2H 완료 후 어휘 비교 시

### 3. Casini INPUT vs sunolanguage OUTPUT 프레임 (G7)
- 101,953곡 INPUT 어휘 ↔ 우리 OUTPUT 어휘 비교
- H1~H5 가설 검증 구조 그대로 사용
- **적용 시점**: 충분한 데이터 확보 후 (최소 200곡+)

---

## 중기 적용 (데이터 500곡+ 이후)

### 4. MusicSem 32k 자연어 설명 비교 (G4)
- Reddit 기반 자연어 vs Suno 기술적 어휘 차이 정량화
- Type-token ratio, Zipf's law 비교

### 5. ConceptCaps 200속성 분류 체계 (G3)
- 우리 어휘를 ConceptCaps 분류에 매핑
- 빠진 속성 식별 → 추가 수집 대상 도출

---

## 장기/연구용 (논문화 단계)

### 6. SAE 기반 해석성 (G1) — 참조만
- Suno 내부 모델 접근 불가 → 직접 적용 어려움
- 논문 포지셔닝 시 "complementary approach" 언급

### 7. 프롬프트 인버전 (G2) — 프레임 차용
- EDITOR/VGD의 "audio→text inversion" 프레임으로 포지셔닝
- 우리 방법: 인버전이 아닌 "AI self-description extraction"

### 8. 논문 타겟: ISMIR 2026 Option A ("AI Music Vocabulary Inversion")

---

## 보류

- G8 (CLAP 변종): 임베딩 비교는 데이터 충분 시 검토
- G9 (SongEval): 평가 프레임워크, 현 단계 불필요
- G10 (CLaMP 3): 다국어 MIR, Phase 3 다장르 완료 후 검토
- G11 (TADA!): Suno 모델 접근 필요, 현 단계 불가
- G12 (Suno v5.5): 이미 v5.5 사용 중, 반영 완료
