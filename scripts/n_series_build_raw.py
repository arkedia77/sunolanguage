#!/usr/bin/env python3
"""n_series_build_raw.py — N시리즈 설계 JSON → 적재용 raw JSON.

설계(사람이 쓰는 칸: pos/title/genre/genre_group/key/bpm/theme/sub_theme/terms/sp/lyrics)
→ raw(db_insert.py가 build_handoff.map_song으로 읽는 칸)로 기계 변환한다.
★손으로 raw를 만들지 않는다 — 같은 값을 두 번 적으면 갈린다.

사용: .venv/bin/python scripts/n_series_build_raw.py data/n041/N041_design.json
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build(design_path: Path) -> Path:
    d = json.loads(design_path.read_text(encoding="utf-8"))
    songs = []
    for s in d["songs"]:
        ly = s["lyrics"]
        songs.append({
            "index": s["pos"],
            "title": s["title"],
            "sp": s["sp"],
            "sp_length": len(s["sp"]),
            "lyrics": ly,
            "lyrics_length": len(ly),
            "genre_group": s["genre_group"],
            "song_form": "designed_v1",
            "song_form_type": "designed_v1",
            "bracket_sections": len(re.findall(r"^\s*\[[^\]]*\]\s*$", ly, re.M)),
            "theme": s["theme"],
            "sub_theme": s["sub_theme"],
            "bpm": s["bpm"],
            "key_signature": s["key"],
            "energy": s.get("energy", "Medium"),
            "sp_validation": "PASS",
            "lyrics_validation": "PASS",
            "coherence": None,
        })
    out = {"songs": songs,
           "metadata": {"batch": d["batch"], "designed_by": "sunolanguage",
                        "method": "설계 기반", "model_target": "v6",
                        "engine": "sunolanguage_design_v1"}}
    p = design_path.parent / f"{d['batch']}_raw.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {p} — {len(songs)}곡")
    return p


if __name__ == "__main__":
    build(Path(sys.argv[1]))
