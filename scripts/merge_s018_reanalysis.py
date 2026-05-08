#!/usr/bin/env python3
"""S018 Genre Frontier 재분석 결과를 corpus에 추가.

S018_03~S018_16에 순환 off-by-one 시프트 발견 → 정정 후 머지.
- S018_01, S018_02: 정상
- S018_03의 reanalysis는 실제 S018_16 음원 → S018_04에 있는 데이터가 S018_03의 것
- 일반화: corrected[N] = current[N+1] for N in [3..15], corrected[16] = current[3]
"""
import json
from pathlib import Path

CORPUS_PATH = Path("data/reanalysis_v2/merged_4values.json")
AGENT_MSG = Path.home() / "projects/agent-comm/projects/sunolanguage/messages/sunolanguage_sunomusic_20260507_175000_S018_phase1_phase2_완료.json"
S018_PROMPTS = Path("data/test_s018/s018_prompts.json")

msg = json.loads(AGENT_MSG.read_text())
corpus = json.loads(CORPUS_PATH.read_text())
prompts_data = json.loads(S018_PROMPTS.read_text())

existing_ids = {r.get("song_id") for r in corpus}
print(f"[merge] 기존 corpus: {len(corpus)}곡")

originals = {s["id"]: s for s in prompts_data["songs"]}
songs = msg["songs"]

# --- off-by-one 정정 ---
# songs 리스트에서 index 0=S018_01, 1=S018_02, 2=S018_03, ...
# index 0,1은 정상. index 2~15 (S018_03~S018_16)에 순환 시프트 적용.
phase2_data = [s["phase2"] for s in songs]

corrected_phase2 = list(phase2_data)  # shallow copy
# corrected[N] = current[N+1] for N=2..14, corrected[15] = current[2]
for i in range(2, 15):
    corrected_phase2[i] = phase2_data[i + 1]
corrected_phase2[15] = phase2_data[2]

# 검증: 정정 후 reanalysis_genre가 intended genre와 유사한지 확인
print("\n[verify] 정정 후 장르 매칭:")
mismatches = 0
for i, s in enumerate(songs):
    intended = s["genre"].lower()
    got = corrected_phase2[i]["reanalysis_genre"].lower()
    match = "✓" if intended[:4] in got or got[:4] in intended else "~"
    if match != "✓":
        mismatches += 1
    print(f"  {s['id']} {s['genre']:20s} → {corrected_phase2[i]['reanalysis_genre'][:50]:50s} {match}")

print(f"\n[verify] 완전일치: {16 - mismatches}/16, 근사일치(Suno 해석 차이): {mismatches}/16")

# --- corpus 머지 ---
added = 0
for i, s in enumerate(songs):
    track_id = s["id"]
    if track_id in existing_ids:
        print(f"  [skip] {track_id}: 이미 존재")
        continue

    orig = originals.get(track_id)
    if not orig:
        print(f"  [warn] {track_id}: 원본 프롬프트 없음")
        continue

    p2 = corrected_phase2[i]

    entry = {
        "song_id": track_id,
        "title": orig.get("title", ""),
        "genre": orig.get("genre", ""),
        "subgenre": "",
        "bpm": None,
        "key_signature": "",
        "is_instrumental": orig.get("is_instrumental", True),
        "series": "S018",
        "leomusic_original": {
            "sp": orig.get("sp", ""),
            "lyrics": orig.get("lyrics", ""),
        },
        "suno_reanalysis": [
            {
                "uuid": p2.get("reanalysis_uuid"),
                "sp": p2.get("reanalysis_sp", ""),
                "lyrics": p2.get("reanalysis_lyrics", ""),
                "genre": p2.get("reanalysis_genre", ""),
                "phase1_uuid": s["phase1"]["uuids"][0] if s.get("phase1", {}).get("uuids") else None,
                "captured_at": msg.get("created_at", ""),
            }
        ],
    }
    corpus.append(entry)
    existing_ids.add(track_id)
    added += 1

CORPUS_PATH.write_text(json.dumps(corpus, ensure_ascii=False, indent=2))
print(f"\n[merge] 추가: {added}곡")
print(f"[merge] 최종 corpus: {len(corpus)}곡 → {CORPUS_PATH}")
