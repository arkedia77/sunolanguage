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

---

## 컨텍스트·메모리 구조 (킷 v0.2 — 전문: agent-comm/projects/fableself/exchange/context-memory-kit-v01.md)

**3층 상한제**: L0 항시로드(이 파일 + memory/MEMORY.md, **합계 ≤6KB**) = 트리거+포인터만 / L1 진입 다이제스트 / L2 온디맨드(memory/_HUB_INDEX_L2·개별 memory·notes·KANBAN — 무제한 성장). L0 초과 시 병합·L2 강등으로만 해소.

### 추론 수칙 (§2)
- **R-P1 전제 감사**: 사실 전제(수치·담당·상태)는 **작성 전** 정본 grep 1회 대조, 본문에 `근거:{파일}` 표기. 미확인은 명기.
- **R-P2 부분 Read**: 전체 재독 금지 — grep 위치확인 후 해당 절만 Read.
- **R-P3 결정 하나씩 닫기**: 열린 결정 병렬 금지. 닫히면 같은 턴에 정본 기록(Action-then-Record).
- **R-P4 양자택일 금지**: 배타 아니면 "둘 다 보유(코어+어댑터)"가 기본값. 진짜 배타일 때만 택일.

### 세션 종료 루틴 (지식 수명주기 §3)
- **G-K1 승격**: 사건 1건=session_log까지. 2회↑ 재발/타도메인 재사용만 룰 승격(단발 룰화 금지).
- **G-K2 은퇴**: 월1회/허브 15건↑ 시 병합·archive. 통합판 생성 = 같은 턴에 구판 은퇴.
- **G-K3 활성 태스크**: 링크는 KANBAN. MEMORY.md엔 "활성=칸반참조" 1줄만.
- **G-K4 단일 기재**: 룰 전문 1곳만. CLAUDE.md·MEMORY.md엔 트리거+포인터 1줄(3중 기재 금지).
- **G-K5 커밋 후 HEAD 검증**: repo 정본 변경은 push 후 `git show HEAD:{파일}` 실물 대조까지 done(공유클론 race 방지). write→add→commit 최소창.
- **G-K6 커밋 author 병기**(ari 07-27): 커밋=`AGENT_ID=sunolanguage git -c user.name=sunolanguage -c user.email=sunolanguage@leomusic.os commit`. AGENT_ID는 훅 트리거일 뿐 author 미변경 — 미병기 시 전역config(arkedia77)로 찍혀 활동판정 오독. ★전역 `git config user.*` 변경 금지(타 슬롯 공용). 후 `%an`=sunolanguage 확인.
- 종료 시 push 자동(확인 없이).
