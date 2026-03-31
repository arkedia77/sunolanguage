# Cross-Axis Connections & sunolanguage의 고유 기여

> 2026-03-31 | 4개 축 리서치 종합

---

## 1. 축 간 교차점

### Axis 1 × Axis 2: 음색 언어 → AI 음악 생성
- Zacharakis의 LTM(Luminance-Texture-Mass) 모델이 제시한 음색 형용사들은 text-to-music 모델의 학습 데이터(MusicCaps, LP-MusicCaps)에서도 빈번히 등장
- 그러나 학술적 timbre 연구는 isolated tones 중심이고, AI 모델은 full mix 프롬프트를 처리 → 중간 다리 부재
- **교차 논문**: MuLan (Axis 2, 3) — 음악-텍스트 joint embedding이 음색 언어를 암묵적으로 학습하지만, 어떤 음색 형용사가 효과적인지는 불투명

### Axis 1 × Axis 3: 음색 언어 → 감각 접지
- Wallmark(2019)의 Stroop 실험은 timbre-language 매핑이 자동적(automatic)임을 입증 → Barsalou(1999)의 perceptual symbol theory와 직접 연결
- Spence(2011)의 crossmodal correspondence가 "bright=high frequency" 같은 보편적 매핑의 근거 제공
- **핵심 인사이트**: 음색 어휘가 임의적 관습이 아니라 인지적으로 접지(grounded)되어 있다는 것 = AI가 이 어휘를 통해 음색을 학습할 수 있다는 이론적 근거

### Axis 2 × Axis 3: AI 음악 생성 → 멀티모달 AI
- MusicLM은 MuLan 위에 구축 → CLIP의 vision-language 패러다임이 music-language로 직접 전이된 증거
- CLAP(Axis 2, 3)은 오디오-텍스트 contrastive learning의 실용적 구현
- **교차 논문**: ImageBind (Axis 3) — 6개 모달리티를 언어 앵커로 연결, 음악도 이 프레임워크에 포함

### Axis 2 × Axis 4: AI 음악 생성 → 음악 온톨로지
- Text-to-music 모델의 학습 데이터 메타데이터(장르, 악기, 무드 태그)는 사실상 비형식적 음악 온톨로지
- LP-MusicCaps가 태그→캡션 변환에 사용한 태그 체계는 MIR 택소노미에서 유래
- **교차 논문**: Oramas et al. (Axis 4) — 텍스트 설명 → 지식그래프 → 추천 파이프라인이 text-to-music 학습 데이터 구축과 구조적으로 유사

### Axis 3 × Axis 4: 감각 접지 → 음악 온톨로지
- Harnad의 symbol grounding 관점에서 음악 온톨로지의 형식적 기호(symbol)들은 감각 경험에 접지되어야 의미를 가짐
- MPEG-7 저수준 디스크립터(spectral centroid 등)는 신호 수준의 접지를 제공하지만, 언어 수준의 접지는 부재
- **핵심 인사이트**: 형식 온톨로지(Axis 4)와 감각 접지(Axis 3) 사이의 빈자리 = 인간 음악 언어(leomusic-base)의 역할

---

## 2. sunolanguage만의 White Space

4개 축의 기존 연구를 종합하면, 다음 영역이 **미개척지**임이 드러남:

### 2.1 폐쇄형 AI 엔진의 자체 어휘 역추출
- 기존 접근: 오픈소스 모델 내부 분석 (attention 시각화, ablation study) 또는 학습 데이터 분석
- **sunolanguage의 접근**: Suno에 실제 음악을 넣고, Suno가 스스로 생성한 프롬프트를 대량 수집
- 이 "reverse vocabulary extraction from a closed-source AI engine"은 선행 사례 없음
- Suno가 쓰는 말 = Suno가 확실히 이해하는 말 → ground-truth vocabulary

### 2.2 인간 음색 언어 vs AI 유효 어휘 갭의 실증 매핑
- Axis 1: 인간이 음색을 표현하는 언어 체계 (LTM 등)
- Axis 2: AI 모델이 텍스트를 처리하는 방식 (embedding opacity)
- **sunolanguage의 기여**: 이 둘 사이의 갭을 실증적으로 측정
  - 학술적 음색 어휘 중 Suno가 반응하는 것 vs 무시하는 것
  - Suno가 사용하지만 학술 코퍼스에 없는 프로덕션 용어 (e.g., "lo-fi", "crispy")
  - 같은 단어가 학술적 의미와 Suno 해석에서 차이나는 경우

### 2.3 Sensory→Language→AI 프레임워크의 음악 도메인 최초 적용
- CLIP(시각)이 증명한 "감각→언어→AI" 파이프라인을 음악에 적용
- 기존 음악-언어 모델(MuLan, CLAP)은 암묵적 embedding만 학습
- **sunolanguage는 명시적(explicit), 해석 가능한(interpretable) 어휘를 추출** → Harnad의 symbol grounding을 실현

### 2.4 형식 온톨로지 → 인간 언어 → AI 유효 어휘 3계층 스택
```
Axis 4: 형식 음악 온톨로지 (Music Ontology, MPEG-7, H-S)
  ↓ leomusic-base가 번역
Axis 1: 인간 음악 언어 (LTM 모델, TOR 프레임워크)
  ↓ sunolanguage가 필터링
Axis 2: AI 엔진 유효 어휘 (Suno SP, Inline Cues, Stem descriptors)
```
이 3계층 스택을 제안하고 실증한 선행 연구는 없음.

---

## 3. 논문화 시 포지셔닝

sunolanguage는 다음과 같이 포지셔닝 가능:

> **"Reverse Vocabulary Extraction from a Commercial AI Music Engine: Bridging Timbre Semantics, Music Ontology, and Generative AI through Empirical Language Mapping"**

- **Related Work**: 4개 축이 각각 하나의 Related Work 서브섹션
- **Contribution**: 2.1~2.4의 4가지 white space
- **Method**: Phase 1(TOR 분석) + Phase 2(Suno 프롬프트 수집) + 대조 분석
- **Evaluation**: 수집된 어휘로 SP 작성 → Suno 생성 → 의도 일치도 측정
