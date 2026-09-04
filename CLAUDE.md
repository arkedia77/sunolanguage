# SunoLanguage (sunolang) 프로젝트 가이드

**목적**: Suno 앱의 음악 인식 결과(프롬프트)를 수집/분석하여 Suno 네이티브 어휘 RAG 구축
**생성일**: 2026-03-28
**약칭**: sunolang

---

## 핵심 개념 (불변)

Suno 앱에 실제 음악을 녹음(~10초)하면 Suno가 **자기 언어로** 프롬프트를 생성함 = 관측층.
⇒ 대량 수집 시 **Suno가 실제로 반응하는 어휘 사전**이 나온다. ★단 그 프롬프트는 **오디오가 아니라 서술문**이다.
목표 = ⑴Suno 네이티브 어휘 사전 ⑵악기·주법 RAG ⑶프로듀서 SP 품질(leomusic2·3·trot — 코드 직접 수정 X, 데이터만 전달).

## 실물 위치 (★아래 트리는 스테일이 잦다 — 항상 `ls`로 확인)

- **대장·서사**=`KANBAN.md`(L2·무제한) / **분류 기준 정본**=`docs/corpus_classification_criteria_v1.md` / 교본=`docs/manual_v3/`
- **DB**=`sunolang.db`(tracks=레퍼런스 153곡 / `expr_*`=표현 코퍼스 / `match_*`·`ingest_runs`) — ★단일 Writer
- **스크립트**=`scripts/`(발신 `send_msg.py` · 인박스 `inbox_scan.py` — ★`.venv/bin/python`으로 실행)
- **데이터**=`data/`(배치·프로브·재분석 산출). ⛔`data/{raw,mp3_phase5,stems_phase5*,upload_batch_*}` **6건은 `/Volumes/LEO/sunolanguage_archive/` 심링크인데 그 볼륨이 미마운트**(09-02 실측) ⇒ 「없음」이 아니라 **끊긴 링크**. `data/parsed`·`rag/`는 실재.

---

## 컨텍스트·메모리 구조

**킷 정본**=`agent-comm:projects/fableself/exchange/context-memory-kit-v01.md` §2·§3 (판版=문서 제목 줄. 로컬 사본은 스테일 실적).

**3층 상한제**: L0 항시로드(이 파일 + memory/MEMORY.md, **합계 ≤6KB**) = 트리거+포인터만 / L1 진입 / L2 온디맨드(_HUB_INDEX_L2·memory·KANBAN — 무제한). 초과 시 병합·L2 강등으로만 해소.

### 추론 수칙 — 트리거만 (전문=킷 §2. 문면 복제 금지=G-K4)
**R-P1** 전제 감사(쓰기 전 grep·`근거:{파일}`) · **R-P2** 부분 Read · **R-P3** 결정 하나씩 · **R-P4** 양자택일 금지(기본=둘 다) · ★**R-P6 경계 밖 참조엔 `repo:경로` 한정자**(해시 포함 — 없으면 읽는 쪽에서 **에러 아닌 「없음」**)

### agent-comm 동기화 (ari D237 09-02)
★**내 통신용 클론 = 공유(`~/projects/agent-comm`) — 4분기 규율 적용**(⛔raw rebase 금지·`admin/scripts/sync_shared_clone.sh` 경유). ★**공유 트리는 커밋 전에도 남이 읽는다** ⇒ ⑴읽힘≠배달(인수는 `origin/main` 실물 조회로) ⑵읽힌 통은 폐기 말고 **철회통** 발신.

### 세션 종료 루틴 (지식 수명주기 §3)
- **G-K1 승격**: 사건 1건=session_log까지. 2회↑ 재발/타도메인 재사용만 룰 승격(단발 룰화 금지).
- **G-K2 은퇴**: 월1회/허브 15건↑ 시 병합·archive. 통합판 생성 = 같은 턴에 구판 은퇴.
- **G-K3 활성 태스크**: 링크는 KANBAN. MEMORY.md엔 "활성=칸반참조" 1줄만.
- **G-K4 단일 기재**: 룰 전문 1곳만. CLAUDE.md·MEMORY.md엔 트리거+포인터 1줄(3중 기재 금지).
- **G-K5 push 후 origin 실물 검증**: 변경은 push 후 `git show origin/main:{파일}` 대조까지 done. ⛔`HEAD:`는 push 증거가 아님. write→add→commit 최소창.
- **G-K6 author 병기**(ari 07-27): `AGENT_ID=sunolanguage git -c user.name=sunolanguage -c user.email=sunolanguage@leomusic.os commit`. AGENT_ID는 훅 트리거일 뿐 author 미변경 — 미병기 시 전역config(arkedia77)로 찍혀 활동판정 오독. ★전역 `git config user.*` 변경 금지. 후 `%an` 확인.
- 종료 시 push 자동(확인 없이).
