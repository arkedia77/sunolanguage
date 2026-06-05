#!/usr/bin/env python3
"""D1: Suno 재분석 결과 × leomusic 원본 SP/가사 머지 → 4값 세트 JSON 생성.

데이터 소스: legion PostgreSQL (read-only). 구머신(mushin@172.30.1.77)
sqlite3 leomusic.db 직읽기에서 전환 — LEO 결정 'legion PG 직접읽기로 전환'.
"""
import configparser
import json
from pathlib import Path

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data/reanalysis_v2/upload_results"
OUT_PATH = Path(__file__).resolve().parent.parent / "data/reanalysis_v2/merged_4values.json"
DB_CONF = Path.home() / ".config" / "leofamily_music" / "db.conf"
# 구 leomusic.db 는 leomusic 프로젝트 곡만 보유 → 통합 songs 테이블에서 동일 범위로 스코프.
CREATOR_SCOPE = "leomusic"


def fetch_leomusic_rows(ids):
    """legion PG에서 leomusic-origin 곡의 원본 메타/SP/가사 조회 (read-only)."""
    import psycopg2
    c = configparser.ConfigParser()
    c.read(DB_CONF)
    cfg = dict(c["postgresql"])
    conn = psycopg2.connect(host=cfg["host"], port=int(cfg["port"]),
                            dbname=cfg["dbname"], user=cfg["user"], password=cfg["password"])
    cur = conn.cursor()
    cur.execute(
        "SELECT global_id, title, genre, subgenre, bpm, key_signature, style_prompt, lyrics "
        "FROM songs WHERE creator = %s AND global_id = ANY(%s);",
        (CREATOR_SCOPE, list(ids)),
    )
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

files = sorted(UPLOAD_DIR.glob("*.json"))
print(f"[D1] found {len(files)} Suno 재분석 JSON")

records = {}
for fp in files:
    d = json.loads(fp.read_text())
    sid = d.get("song_id")
    if sid is None:
        continue
    records.setdefault(sid, []).append(d)

ids = sorted(records.keys())
print(f"[D1] unique song_id: {len(ids)}")

rows = fetch_leomusic_rows(ids)
print(f"[D1] leomusic DB rows: {len(rows)}")

by_id = {r["global_id"]: r for r in rows}

merged = []
missing = []
for sid in ids:
    leo = by_id.get(sid)
    suno_entries = records[sid]
    if not leo:
        missing.append(sid)
        continue
    merged.append({
        "song_id": sid,
        "title": leo["title"],
        "genre": leo.get("genre"),
        "subgenre": leo.get("subgenre"),
        "bpm": leo.get("bpm"),
        "key_signature": leo.get("key_signature"),
        "leomusic_original": {
            "sp": leo.get("style_prompt"),
            "lyrics": leo.get("lyrics"),
        },
        "suno_reanalysis": [
            {
                "uuid": s.get("suno_uuid"),
                "sp": s.get("suno_analysis_sp"),
                "lyrics": s.get("suno_analysis_lyrics"),
                "file": s.get("file"),
                "captured_at": s.get("captured_at"),
            }
            for s in suno_entries
        ],
    })

OUT_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2))
print(f"[D1] 머지 완료: {len(merged)}곡 → {OUT_PATH}")
if missing:
    print(f"[D1] leomusic DB 누락 song_id: {missing}")
