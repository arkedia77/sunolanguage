# 사연 노래 카드 MVP (songcard)

LEO 직지시(2026-09-25, solself 중계) — 참고 서비스 흐름을 분석해 **우리 시스템 기반 카드형 MVP**로 만든 것.
분석 1쪽 = `docs/songcard_mvp_analysis_v1.md` · 화면 = `docs/songcard_mvp_shots/`.

## 실행
```bash
cd ~/sunolanguage
.venv/bin/python mvp/songcard/seed_samples.py              # 샘플 카드 3종(다시 돌려도 중복 없음)
.venv/bin/python mvp/songcard/server.py --port 8787         # http://127.0.0.1:8787/
.venv/bin/python mvp/songcard/e2e_test.py                   # 종단 점검(서버 떠 있는 상태에서)
```
외부에서 열려면 `--host 0.0.0.0`. 추측 불가 하위 경로에 올릴 땐 `--base /<접두>`(프록시가 접두를 떼든 안 떼든 둘 다 받음).
모든 응답에 `X-Robots-Tag: noindex`, `/robots.txt` = 전체 Disallow. 오디오 자산 경로는 리포 루트 기준 상대경로로 저장.

## 카드 1장 공개 = 정적 묶음 (LEO 09-26 「링크 아는 사람만 · leomusic.arkedia.work」)
```bash
.venv/bin/python mvp/songcard/export_card.py <request_id>    # → var/export/<무작위 16자>/
```
index.html · app.css · card.js · card.json · audio.mp3(납품본 1개) — 서버 불필요, 전부 상대경로.
⛔ 사연·장면 원문·SP·토큰·request_id·다른 take·WAV는 넣지 않고, 내보낸 뒤 폴더를 뒤져 누출 0건을 확인한다(누출 시 묶음 삭제).
카드에 원래 보이는 받는 분·보내는 분 이름과 헌사 한 줄은 들어간다.
의존성은 표준 라이브러리뿐이다(SP 조립이 `sunolang.db`를 읽기 전용으로 연다).

## 흐름
목적 카드 6종 → 사연·장르·목소리 입력 → **제작 상태 카드**(7단계, 5초마다 자동 갱신) → **음악 카드**(표지·헌사·재생기·가사·공유·재요청)

## 샘플 카드와 실제 제작 카드
| | 샘플(`source=sample`) | 실제 제작(`source=live`) |
|---|---|---|
| 음원 | 내부 제작곡 AWARE05 #30201·30202·30206 로컬 mp3를 빌려 씀 — **이 사연으로 만든 곡이 아님**(카드에 표시) | sunomusic 생성 결과 파일 |
| 사연 | 가상 | 고객 입력 |
| 파이프라인 | 올리지 못함(차단) | `pipeline.py` 단계 진행 |

## 실제 제작 경로 (운영자 CLI)
```
received ─lyrics-order→ lyrics_pending ─lyrics-in→ lyrics_ready ─gen-order→ generation_queued
         ─gen-ack→ generating ─audio-in→ audio_ready ─publish→ ready
```
- 가사는 **LM 라인**이 쓴다(sunolanguage는 가사를 쓰지 않는다). 담당 슬롯은 kee가 지정한다.
- 발주서는 `var/outbox/`에 떨어지고, agent-comm 발신은 사람이 확인한 뒤 `scripts/send_msg.py`로 따로 한다.
  고객 사연이 공유 저장소에 실리므로 자동으로 보내지 않는다.
- ⛔ `cdn1.suno.ai/{uuid}.mp3`는 403이다(09-25 실측). 오디오는 **파일로** 받아 `audio-in`으로 붙인다.

## 중복 생성 방지
- 접수: 브라우저가 폼마다 `client_key`를 만들어 새로고침해도 유지한다. 서버는 같은 키면 **기존 요청을 돌려준다**.
- 생성 발주: 발주서 파일명이 `{request_id}_gen_L{가사판}_V{보컬판}`이라 같은 판은 두 번 낼 수 없다.
- 재요청: 같은 `redo_key`이거나 **열린 재요청이 이미 있으면** 새로 만들지 않는다. `redo-close`를 두 번 실행해도 판은 한 번만 오른다.
- 오디오: sha256 자산 id라 같은 파일은 take로 두 번 붙지 않는다.

## 재요청과 납품본 (09-25 solself 독립검증 수리)
- 목소리·장르 재요청은 **바꿀 값(`to`)**을 받는다. 닫을 때 그 값으로 보컬판(`vocal_version`)과 SP를 다시 만들고,
  고객 메모는 다음 생성 발주서의 `change_requests`에 실린다.
- take는 만들어질 때의 **가사판·보컬판**(`lyrics_v`·`vocal_v`)에 묶인다. 카드는 **납품본**(`delivered` = take·가사판·보컬판 한 묶음)만 보여 준다.
  새 판을 만드는 동안에도 이전 납품본이 그대로 보이고(`updating`), 현재 판으로 만든 take가 없으면 `publish`가 거절한다.
- 서버와 CLI는 서로 다른 프로세스라서, 저장소 읽기-수정-쓰기를 **파일 잠금**(`var/.store.lock`, flock)으로 보호한다.

## 비공개와 공유
기본은 `private`(요청자 토큰이 있어야 카드·오디오가 열린다). 「공유하기」를 누르면 `link`로 바뀌고, 그때부터는 링크만 있으면 열린다.
공유 카드 응답에는 사연·SP·토큰이 들어가지 않는다(e2e 점검 항목).

## 저장
`var/songcard_store.json`(**git 밖**). 필드는 LM4로 옮기기 쉽게 이름을 맞췄다:
request_id · legacy_gid · takes[suno_uuid, asset_id, selected] · lyrics_versions · vocal_version · asset_manifest · redos.
