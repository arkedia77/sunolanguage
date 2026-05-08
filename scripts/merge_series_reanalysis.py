#!/usr/bin/env python3
"""S-시리즈 재분석 결과를 merged_4values.json corpus에 추가."""
import json
from pathlib import Path

CORPUS_PATH = Path("data/reanalysis_v2/merged_4values.json")
REANALYSIS_MSG = Path.home() / "projects/agent-comm/projects/sunolanguage/messages/sunolanguage_sunomusic_20260507_005000_S016_S017_S003_S004_재분석회신.json"

SERIES_PROMPTS = {
    "S003": Path("data/test_s003/s003_prompts.json"),
    "S004": Path("data/test_s004/s004_prompts.json"),
    "S016": Path("data/test_s016/s016_prompts.json"),
    "S017": Path("data/test_s017/s017_prompts.json"),
}

reanalysis = json.loads(REANALYSIS_MSG.read_text())
corpus = json.loads(CORPUS_PATH.read_text())

existing_ids = {r.get("song_id") for r in corpus}
print(f"[merge] 기존 corpus: {len(corpus)}곡")

originals = {}
for series, path in SERIES_PROMPTS.items():
    d = json.loads(path.read_text())
    for t in d["test_prompts"]:
        originals[t["id"]] = t

added = 0
skipped_dup = 0
skipped_fail = 0

for series_key in ["S003", "S004", "S016", "S017"]:
    items = reanalysis[series_key]
    for item in items:
        track_id = item["id"]

        if track_id in existing_ids:
            skipped_dup += 1
            continue

        if item["status"] != "ok":
            skipped_fail += 1
            print(f"  [skip] {track_id}: status={item['status']}")
            continue

        orig = originals.get(track_id)
        if not orig:
            print(f"  [warn] {track_id}: 원본 프롬프트 없음")
            continue

        entry = {
            "song_id": track_id,
            "title": orig.get("title", item.get("title", "")),
            "genre": orig.get("genre", ""),
            "subgenre": "",
            "bpm": orig.get("bpm"),
            "key_signature": orig.get("key", ""),
            "is_instrumental": orig.get("is_instrumental", item.get("is_instrumental", True)),
            "series": series_key,
            "leomusic_original": {
                "sp": orig.get("sp", ""),
                "lyrics": orig.get("lyrics", ""),
            },
            "suno_reanalysis": [
                {
                    "uuid": item.get("reanalysis_uuid"),
                    "sp": item.get("reanalysis_sp", ""),
                    "lyrics": item.get("reanalysis_lyrics", ""),
                    "genre": item.get("reanalysis_genre", ""),
                    "phase1_uuid": item.get("phase1_uuid"),
                    "captured_at": reanalysis.get("created_at", ""),
                }
            ],
        }
        corpus.append(entry)
        existing_ids.add(track_id)
        added += 1

CORPUS_PATH.write_text(json.dumps(corpus, ensure_ascii=False, indent=2))
print(f"[merge] 추가: {added}곡, 중복 스킵: {skipped_dup}, 실패 스킵: {skipped_fail}")
print(f"[merge] 최종 corpus: {len(corpus)}곡 → {CORPUS_PATH}")
