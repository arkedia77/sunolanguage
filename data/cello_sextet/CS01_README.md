# CS01 — 첼로 6중주 결혼식/행사장 BGM 5곡

**설계**: 2026-07-03 · **용도**: 결혼식 등 행사장 BGM 연주곡 (무가사 인스트루멘탈) · **test_id**: 271~275

## 예식 흐름 매핑
| # | 곡 | 예식 순간 | 조성/BPM/박자 | 곡길이 |
|---|---|---|---|---|
| 1 | 프렐류드 | 하객 착석 | D / 64 / 4/4 | ~2:00 순환형(절정 없음) |
| 2 | 입장 | 신부 입장 | D / 72 / 4/4 | ~2:30 빌드→합주 절정 |
| 3 | 서약 | 서약 | G / 58 / 4/4 | ~2:00 절제(con sordino) |
| 4 | 축하 | 축하 | G / 118 / 6/8 | ~2:15 경쾌·합주 후렴 |
| 5 | 새 출발 | 퇴장·배웅 | E♭ / 76 / 4/4 | ~2:30 따뜻한 합주 절정 |

## 설계 2축
1. **성부분화 대위** — Cello 1(최고 선율) ~ Cello 6(최저 베이스) 음역별 역할, 순차 진입·교대
2. **★6대 합주(tutti)** — 블록화음/옥타브 유니즌으로 6대가 한 몸처럼 (곡마다 다른 방식: 잔잔한 지속화음/массed 블록화음/뮤트해제 스웰/후렴 유니즌/풀 화음)

## 브라켓 송폼 = 곡길이 + 연주구분 제어
lyrics 필드에 인스트루멘탈 송폼 브라켓 적재:
- **섹션태그**(구조/곡길이): `[Intro]`/`[Build]`/`[Theme]`/`[Refrain]`/`[Interlude]`/`[Climax]`/`[Outro]` — attested
- **연주지시**(연주구분): 각 섹션 `[소문자 지시]`가 어느 첼로가 무슨 주법을 하는지 명시

## GT 근거
- 편성명명 dead-zone 회피: `cello sextet`·`six cellos`·`tutti`·`homophonic` = 0곡 → 명명 대신 `for six cellos only` 서술 + 음역역할분화
- attested: cello(90)·legato(83)·vibrato(126)·pizzicato(20)·spiccato(3)·tremolo(42)·double stops(6)·con sordino(1)·arco(6)·harmonics(15)·counterpoint(62)·pedal tone(20) / 합주: unison(28)·ensemble(36)·octaves(9)·block chords(6)
- 방법론: BS01 첼로4중주(gid 30121~30130) 확장 + 어제 sunomusic 패션필름 브라켓 모델

## 파일
- `CS01_batch.json` — 5곡 SP + 브라켓 송폼 (SP 593~678자, 전곡 ≤1000, 합주구간 5/5)
