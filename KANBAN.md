# sunolang KANBAN

## IN PROGRESS
- [reklcli] 핑거프린팅 우회 방안 검토 — 2026-03-29
- [reklcli+Leo] Demucs 스템 분리 테스트 (개별 스템 Suno 앱 업로드) — 2026-03-29

## TODO
- [reklcli] Demucs stem separation 테스트 (핑거프린팅 우회용) — Phase 2 선행
- [Leo] Phase 2: stem 분리 후 Suno 앱 업로드 → 프롬프트 수집
- [reklcli] Phase 2: Suno 프롬프트 vs predicted_keywords 대조 분석
- [reklcli] Phase 3: 보컬 대중음악 200-300곡 선곡 + 분석
- [reklcli] Phase 5: 통합 RAG 구축

## BLOCKED
- [Leo] Phase 2 MP3 업로드: Audible Magic 핑거프린팅 차단 — stem separation 테스트 필요

## DONE (최근)
- [mukl] 100곡 DB INSERT 완료 — 2026-03-29 ✅ (tracks 100건, instrument_textures 193건)
- [reklcli] Phase 1: 100곡 TOR 상세 분석 완료 — 2026-03-28 ✅
  - 100곡 tracks 테이블 상세 필드 전부 채움 (key, bpm, form, harmony, recording, mood, imagery, listening_points, predicted_keywords)
  - 193개 instrument_textures 레코드 (악기별 player, technique, tone_character, role, equipment)
  - 장르: Classical(12) + Film Score(14) + Hybrid/New Age(13) + Jazz(15) + Electronic/Post-Rock(17) + Guitar/World/Lofi/Funk/Contemporary(29)
- [reklcli] Phase 0: 기반 세팅 — 2026-03-28 ✅
  - agent-comm/sunolang/ 채널 + COMM_RULES.md
  - 100곡 선곡 완료, DB 생성, TOR 프레임워크 채택
  - mukl에게 프로젝트 시작 + DB 확장 요청 전송
