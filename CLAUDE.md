# SunoLanguage (sunolang) 프로젝트 가이드

**목적**: Suno 앱의 음악 인식 결과(프롬프트)를 수집/분석하여 Suno 네이티브 어휘 RAG 구축
**생성일**: 2026-03-28
**약칭**: sunolang

---

## 핵심 개념

Suno 앱에 실제 음악을 녹음(~10초)하면 Suno가 자동 분석하여 프롬프트를 생성함.
이 프롬프트 = **Suno가 스스로 사용하는 언어로 음악을 묘사한 것**.
→ 대량 수집 시 Suno가 실제로 이해/반응하는 어휘 사전 구축 가능.

## 활용 목표

1. **Suno 네이티브 어휘 사전** — 장르별 악기, 주법, 보이싱, 환경 표현
2. **악기 + 주법 RAG** — SP 작성 시 Suno가 확실히 반응하는 표현 검색
3. **LeoMusic2 SP 품질 향상** — 추정이 아닌 Suno 자체 어휘 기반 SP 생성

## 데이터 구조

### 수집 원본 (data/raw/)
- Leo가 Suno 앱으로 녹음 → 생성된 프롬프트를 텍스트로 저장
- 파일명: `{번호}_{장르}_{간단설명}.txt` (예: `001_bossanova_cafe.txt`)

### 파싱 결과 (data/parsed/)
- 원본에서 구조화된 JSON 추출
- 필드: genre, instruments[], voicings[], techniques[], tempo, time_signature, recording_env, section_tags[]

### RAG 인덱스 (rag/)
- 장르별, 악기별, 주법별 인덱스
- 검색: "bossa nova + guitar" → 관련 표현 목록

## 폴더 구조

```
~/sunolanguage/
├── CLAUDE.md          — 이 파일
├── KANBAN.md          — 작업 현황
├── data/
│   ├── raw/           — Suno 앱 분석 원본 텍스트
│   └── parsed/        — 구조화된 JSON
├── scripts/           — 파싱/분석 스크립트
├── rag/               — RAG 인덱스 및 검색
└── docs/              — 분석 문서
```

## LeoMusic2 연동

- sunolang RAG → LeoMusic2 SP 작성 시 참조
- 단, sunolang은 독립 프로젝트 (leomusic2 코드 직접 수정 X)
- 데이터 흐름: sunolang(어휘 사전) → leomusic2(SP 생성)
