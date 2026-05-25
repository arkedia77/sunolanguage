#!/usr/bin/env python3
"""sunolang 코퍼스 JSON → PostgreSQL 독립 테이블 적재 스크립트.

사용법:
    python scripts/json_to_db.py load          # 전체 적재 (tracks + clips + entities)
    python scripts/json_to_db.py load-tracks   # 트랙 + 클립만
    python scripts/json_to_db.py load-entities # SP/브래킷 엔티티만
    python scripts/json_to_db.py status        # 적재 현황 확인
    python scripts/json_to_db.py reset         # 전체 삭제 후 재적재 (주의)

데이터 소스:
    data/reanalysis_v2/merged_4values.json     → sunolang_tracks + sunolang_clips
    data/reanalysis_v2/sp_entities_v3.json     → sunolang_sp_entities
    data/reanalysis_v2/bracket_entities_v3.json → sunolang_bracket_entities

DDL: scripts/sunolang_corpus_ddl.sql (admin 실행 필요)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "reanalysis_v2"


def get_conn():
    conf = {}
    conf_path = os.path.expanduser("~/.config/leofamily_music/db_sunolanguage.conf")
    with open(conf_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                conf[k.strip()] = v.strip().strip('"')
    return psycopg2.connect(
        host=conf["DB_HOST"],
        port=conf["DB_PORT"],
        dbname=conf["DB_NAME"],
        user=conf["DB_USER"],
        password=conf["DB_PASSWORD"],
    )


def load_tracks(conn):
    with open(DATA / "merged_4values.json") as f:
        songs = json.load(f)

    cur = conn.cursor()

    cur.execute("SELECT song_id FROM sunolang_tracks")
    existing = {r[0] for r in cur.fetchall()}

    track_rows = []
    clip_rows = []

    for s in songs:
        sid = s["song_id"]
        if sid in existing:
            continue

        orig = s.get("leomusic_original", {})
        orig_sp = orig.get("sp", "") if isinstance(orig, dict) else ""
        orig_lyrics = orig.get("lyrics", "") if isinstance(orig, dict) else ""

        ra_list = s.get("suno_reanalysis", [])
        is_instrumental = None
        if isinstance(ra_list, list) and ra_list:
            first_sp = ra_list[0].get("sp", "").lower()
            is_instrumental = "instrumental" in first_sp and "vocal" not in first_sp

        track_rows.append((
            sid,
            s.get("title", ""),
            s.get("genre", ""),
            s.get("subgenre", ""),
            s.get("bpm"),
            s.get("key_signature", ""),
            orig_sp,
            orig_lyrics,
            is_instrumental,
        ))

        if isinstance(ra_list, list):
            for clip in ra_list:
                captured = clip.get("captured_at")
                if captured:
                    try:
                        captured = datetime.fromisoformat(captured)
                    except (ValueError, TypeError):
                        captured = None
                clip_rows.append((
                    sid,
                    clip.get("uuid"),
                    clip.get("sp", ""),
                    clip.get("lyrics", ""),
                    None,
                    clip.get("file", ""),
                    captured,
                ))

    if track_rows:
        execute_values(
            cur,
            """INSERT INTO sunolang_tracks
               (song_id, title, genre, subgenre, bpm, key_signature,
                original_sp, original_lyrics, is_instrumental)
               VALUES %s""",
            track_rows,
        )
        print(f"sunolang_tracks: {len(track_rows)} rows inserted")

    if clip_rows:
        execute_values(
            cur,
            """INSERT INTO sunolang_clips
               (track_id, suno_uuid, reanalysis_sp, reanalysis_lyrics,
                reanalysis_genre, source_file, captured_at)
               SELECT t.track_id, v.uuid::uuid, v.sp, v.lyrics, v.genre, v.file, v.cap
               FROM (VALUES %s) AS v(song_id, uuid, sp, lyrics, genre, file, cap)
               JOIN sunolang_tracks t ON t.song_id = v.song_id::int""",
            clip_rows,
        )
        print(f"sunolang_clips: {len(clip_rows)} rows inserted")

    conn.commit()


def load_sp_entities(conn):
    with open(DATA / "sp_entities_v3.json") as f:
        entities = json.load(f)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sunolang_sp_entities")
    if cur.fetchone()[0] > 0:
        print("sunolang_sp_entities: already populated, skipping (use 'reset' to reload)")
        return

    rows = []
    for e in entities:
        rows.append((
            e.get("song_id"),
            e.get("slot", ""),
            e.get("entity", ""),
            e.get("modifiers", []),
            e.get("pattern", ""),
            e.get("effects", []),
            e.get("chords", []),
            e.get("sentence", ""),
            e.get("source", ""),
        ))

    if rows:
        execute_values(
            cur,
            """INSERT INTO sunolang_sp_entities
               (track_id, slot, entity, modifiers, pattern, effects, chords, sentence, source)
               SELECT t.track_id, v.slot, v.entity, v.mods::text[], v.pat, v.eff::text[], v.ch::text[], v.sent, v.src
               FROM (VALUES %s) AS v(song_id, slot, entity, mods, pat, eff, ch, sent, src)
               JOIN sunolang_tracks t ON t.song_id = v.song_id::int""",
            rows,
        )
        print(f"sunolang_sp_entities: {len(rows)} rows inserted")

    conn.commit()


def load_bracket_entities(conn):
    with open(DATA / "bracket_entities_v3.json") as f:
        entities = json.load(f)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sunolang_bracket_entities")
    if cur.fetchone()[0] > 0:
        print("sunolang_bracket_entities: already populated, skipping (use 'reset' to reload)")
        return

    rows = []
    for e in entities:
        rows.append((
            e.get("song_id"),
            e.get("slot", ""),
            e.get("entity", ""),
            e.get("modifiers", []),
            e.get("bracket", ""),
            e.get("source", ""),
        ))

    if rows:
        execute_values(
            cur,
            """INSERT INTO sunolang_bracket_entities
               (track_id, slot, entity, modifiers, bracket, source)
               SELECT t.track_id, v.slot, v.entity, v.mods::text[], v.brk, v.src
               FROM (VALUES %s) AS v(song_id, slot, entity, mods, brk, src)
               JOIN sunolang_tracks t ON t.song_id = v.song_id::int""",
            rows,
        )
        print(f"sunolang_bracket_entities: {len(rows)} rows inserted")

    conn.commit()


def show_status(conn):
    cur = conn.cursor()
    tables = [
        "sunolang_tracks",
        "sunolang_clips",
        "sunolang_sp_entities",
        "sunolang_bracket_entities",
    ]
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"{t}: {cnt} rows")
        except psycopg2.errors.UndefinedTable:
            conn.rollback()
            print(f"{t}: TABLE NOT FOUND (admin DDL 실행 필요)")


def reset_all(conn):
    cur = conn.cursor()
    for t in [
        "sunolang_bracket_entities",
        "sunolang_sp_entities",
        "sunolang_clips",
        "sunolang_tracks",
    ]:
        try:
            cur.execute(f"DELETE FROM {t}")
            print(f"{t}: cleared")
        except psycopg2.errors.UndefinedTable:
            conn.rollback()
            print(f"{t}: not found")
    conn.commit()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    conn = get_conn()

    try:
        if cmd == "status":
            show_status(conn)
        elif cmd == "load":
            load_tracks(conn)
            load_sp_entities(conn)
            load_bracket_entities(conn)
            show_status(conn)
        elif cmd == "load-tracks":
            load_tracks(conn)
        elif cmd == "load-entities":
            load_sp_entities(conn)
            load_bracket_entities(conn)
        elif cmd == "reset":
            confirm = input("전체 삭제 후 재적재합니다. 계속? (yes/no): ")
            if confirm == "yes":
                reset_all(conn)
                load_tracks(conn)
                load_sp_entities(conn)
                load_bracket_entities(conn)
                show_status(conn)
            else:
                print("취소됨")
        else:
            print(f"Unknown command: {cmd}")
            print(__doc__)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
