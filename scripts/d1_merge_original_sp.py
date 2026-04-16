#!/usr/bin/env python3
"""D1: Suno 재분석 결과 × leomusic 원본 SP/가사 머지 → 4값 세트 JSON 생성."""
import json
import subprocess
from pathlib import Path

UPLOAD_DIR = Path("/Users/leo/sunolanguage/data/reanalysis_v2/upload_results")
OUT_PATH = Path("/Users/leo/sunolanguage/data/reanalysis_v2/merged_4values.json")
SSH_HOST = "mushin@172.30.1.77"
DB_PATH = "~/projects/leomusic-cli/leomusic.db"

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

id_list = ",".join(str(i) for i in ids)
sql = (
    "SELECT global_id, title, genre, subgenre, bpm, key_signature, "
    "style_prompt, lyrics FROM songs WHERE global_id IN ({}) ".format(id_list)
)
cmd = ["ssh", SSH_HOST, f"sqlite3 -json {DB_PATH} \"{sql}\""]
out = subprocess.check_output(cmd, text=True)
rows = json.loads(out)
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
