#!/usr/bin/env python3
"""
db_insert.py — sunolanguage DB-direct INSERT (핸드오프 대체)

엔진 raw 배치 → songs 테이블 직접 INSERT (creator=sunolanguage, status=pending_suno).
leomusic/leomusic2와 동일한 DB-direct 구조로 통일 → 핸드오프 변환단계/스키마 드리프트 소멸.
(2026-05-31, Leo 승인 DB-direct 전환. [[project_handoff_schema_drift]])

전제:
  - role_sunolanguage 에 songs INSERT/SELECT/UPDATE GRANT 완료 (라이브 DB 확인,
    감사(audit) 트리거도 존재). 더 이상 GRANT 대기 아님.
  - gid는 자동채번 아님 → admin이 배치별 gid 범위 사전배정 → --gid-start 로 전달
  - songs 컬럼셋/값패턴은 leomusic2 insert_k030_to_pg.py 정본을 미러링

매핑은 build_handoff.map_song(Option A) 재사용 → 단일 진실원 유지.

사용법:
  # 검증 (기본, DB 연결 없음):
  python3 scripts/db_insert.py data/lyrics_history/lyrics_batch_*.json --batch N008 --gid-start 20391
  # 실제 적재 (GRANT 완료 상태 — --execute 로 실적재):
  python3 scripts/db_insert.py <raw> --batch N008 --gid-start 20391 --execute
"""
import argparse
import sys
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_handoff import load_raw, map_song, REQUIRED_NONEMPTY  # 매핑 단일 진실원

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_PROJECT = "sunolanguage"
CREATOR = "sunolanguage"
CREATED_BY = "sunolanguage"
MUSIC_ENGINE = "suno_v5"
DEFAULT_MARKET = "KR2"
STATUS = "pending_suno"

# leomusic2 insert_k030_to_pg.py 정본 컬럼셋 (40)
SONGS_COLUMNS = [
    "global_id", "source_project", "batch", "batch_position", "market",
    "title", "lyrics", "style_prompt", "status",
    "theme", "episode", "category", "lyricist", "genre", "genre_mode",
    "energy", "song_form", "song_form_name", "voicing", "char_count",
    "voice_perspective_type", "bpm", "genre_group", "sub_theme", "coherence",
    "intro_bars", "interlude_bars", "outro_bars",
    "mood", "instrumentation", "production_direction",
    "key_signature", "scale_type", "modulation",
    "subgenre", "creator", "label", "music_engine",
    "created_date", "theme_id", "created_by", "created_at",
]


def song_to_row(opt_a: dict, gid: int, now) -> dict:
    """Option A 곡 dict → songs 테이블 컬럼 dict (40컬럼)."""
    genre = opt_a.get("genre") or ""
    return {
        "global_id": gid,
        "source_project": SOURCE_PROJECT,
        "batch": opt_a["batch"],
        "batch_position": opt_a["batch_position"],
        "market": opt_a.get("market") or DEFAULT_MARKET,
        "title": opt_a["title"],
        "lyrics": opt_a["lyrics"],
        "style_prompt": opt_a["style_prompt"],
        "status": STATUS,
        "theme": opt_a.get("theme") or "",
        "episode": "",                       # sunolang 미생산
        "category": "",
        "lyricist": opt_a.get("lyricist") or "lyrics_rag_v2",
        "genre": genre,
        "genre_mode": opt_a.get("genre_mode") or "vocal",
        "energy": opt_a.get("energy") or "Medium",
        "song_form": opt_a.get("song_form") or "",
        "song_form_name": "",
        "voicing": "",
        "char_count": opt_a.get("char_count") or 0,
        "voice_perspective_type": "",
        "bpm": opt_a.get("bpm") or 0,
        "genre_group": opt_a.get("genre_group") or "",
        "sub_theme": opt_a.get("sub_theme") or "",      # live songs 컬럼 존재(2026-06-05 확인)
        "coherence": opt_a.get("coherence"),            # float, 없으면 NULL
        "intro_bars": 0, "interlude_bars": 0, "outro_bars": 0,
        "mood": "",
        "instrumentation": "",
        "production_direction": "",
        "key_signature": opt_a.get("key_signature") or "",
        "scale_type": "",
        "modulation": "",
        "subgenre": genre,
        "creator": CREATOR,
        "label": SOURCE_PROJECT,             # leomusic2는 "KR2"였으나 의미상 프로젝트명 사용
        "music_engine": MUSIC_ENGINE,
        "created_date": now.strftime("%Y-%m-%d %H:%M:%S"),  # varchar(20) — 19자 문자열
        "theme_id": 0,                       # self_generated (themebank 미사용)
        "created_by": CREATED_BY,
        "created_at": now,
    }


def build_rows(raw_path: Path, batch: str, gid_start: int, *, seed, drift,
               engine, market, energy, now):
    items, raw_meta = load_raw(raw_path)
    seed = seed or raw_meta.get("seed", "")
    drift = drift if drift is not None else raw_meta.get("drift")
    engine = engine or raw_meta.get("engine", "serendipity_engine_v2")

    rows = []
    for i, item in enumerate(items):
        opt_a = map_song(item, batch, i + 1, market=market, energy=energy,
                         engine=engine, seed=seed, drift=drift)
        rows.append((opt_a, song_to_row(opt_a, gid_start + i, now)))
    return rows


def validate(rows):
    problems = []
    for opt_a, _ in rows:
        missing = [k for k in REQUIRED_NONEMPTY if not opt_a.get(k)]
        if missing:
            problems.append((opt_a.get("batch_line", "?"), missing))
    return problems


def insert_sql():
    cols = ", ".join(SONGS_COLUMNS)
    ph = ", ".join(["%s"] * len(SONGS_COLUMNS))
    return f"INSERT INTO songs ({cols}) VALUES ({ph})"


def main():
    ap = argparse.ArgumentParser(description="sunolanguage DB-direct songs INSERT")
    ap.add_argument("raw", help="엔진 raw batch json")
    ap.add_argument("--batch", required=True)
    ap.add_argument("--gid-start", type=int, required=True,
                    help="admin 사전배정 gid 시작값 (자동채번 아님)")
    ap.add_argument("--seed", default="")
    ap.add_argument("--drift", type=float, default=None)
    ap.add_argument("--engine", default="")
    ap.add_argument("--market", default=DEFAULT_MARKET)
    ap.add_argument("--energy", default="Medium")
    ap.add_argument("--execute", action="store_true",
                    help="실제 INSERT (미지정 시 dry-run: 연결 없이 검증/출력만)")
    args = ap.parse_args()

    raw_path = Path(args.raw)
    if not raw_path.is_absolute():
        raw_path = PROJECT_ROOT / raw_path
    if not raw_path.exists():
        sys.exit(f"❌ raw 파일 없음: {raw_path}")

    # dry-run은 시간 고정값으로 결정적 출력
    now = datetime.now() if args.execute else datetime(2026, 1, 1)
    rows = build_rows(raw_path, args.batch, args.gid_start,
                      seed=args.seed, drift=args.drift, engine=args.engine,
                      market=args.market, energy=args.energy, now=now)

    problems = validate(rows)
    if problems:
        print("❌ 필수 키 누락 — INSERT 차단:", file=sys.stderr)
        for line, missing in problems:
            print(f"   {line}: {missing}", file=sys.stderr)
        sys.exit(1)

    gid_end = args.gid_start + len(rows) - 1
    print(f"배치 {args.batch} | {len(rows)}곡 | gid {args.gid_start}~{gid_end} | 컬럼 {len(SONGS_COLUMNS)}")
    print(f"필수키 검증 PASS | INSERT SQL 컬럼수={len(SONGS_COLUMNS)} 플레이스홀더={insert_sql().count('%s')}")

    if not args.execute:
        print("\n[DRY-RUN] DB 연결/INSERT 없음. 샘플 곡1 매핑:")
        _, row = rows[0]
        for c in SONGS_COLUMNS:
            v = str(row[c])
            print(f"  {c:24} = {v[:60]}")
        print(f"\ngenre_group 분포:",
              {g: sum(1 for _, r in rows if r['genre_group'] == g)
               for g in sorted({r['genre_group'] for _, r in rows})})
        print("→ --execute 로 실적재 (GRANT 완료). (gid 범위는 admin 사전배정값 사용)")
        return

    # 실제 적재
    from json_to_db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    sql = insert_sql()
    inserted = 0
    try:
        for opt_a, row in rows:
            cur.execute(sql, tuple(row[c] for c in SONGS_COLUMNS))
            inserted += 1
            print(f"  INSERT gid={row['global_id']} | {row['title']} | {row['genre']} | {row['char_count']}자")
        conn.commit()
        print(f"\n✅ {inserted}곡 songs INSERT 완료 (gid {args.gid_start}~{gid_end}, creator=sunolanguage)")
    except Exception as e:
        conn.rollback()
        sys.exit(f"❌ INSERT 실패 (롤백됨): {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
