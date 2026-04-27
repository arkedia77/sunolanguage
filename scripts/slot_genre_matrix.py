#!/usr/bin/env python3
"""장르별 슬롯 채워짐 히트맵 생성 — 책 4장 원자재"""

import json, sys
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SP_ENTITIES = BASE / "data/reanalysis_v2/sp_entities_v3.json"
BR_ENTITIES = BASE / "data/reanalysis_v2/bracket_entities_v3.json"
MERGED = BASE / "data/reanalysis_v2/merged_4values.json"
OUTPUT = BASE / "data/reanalysis_v2/slot_genre_matrix.json"

SLOTS = [
    "genre", "instrument", "drums", "vocal_main", "vocal_chorus",
    "arrangement", "mixing", "effect_electronic", "effect_sound",
    "tempo_key_time", "harmony", "absence", "mastering"
]

def normalize_genre(g):
    g = g.strip()
    if "/" in g:
        g = g.split("/")[0].strip()
    if "," in g:
        g = g.split(",")[0].strip()
    return g

def load_entities():
    with open(SP_ENTITIES) as f:
        sp = json.load(f)
    with open(BR_ENTITIES) as f:
        br = json.load(f)
    return sp, br

def load_song_genres():
    with open(MERGED) as f:
        merged = json.load(f)
    return {s["song_id"]: s["genre"] for s in merged}

def build_matrix(sp_ents, br_ents, song_genres):
    genre_slot = defaultdict(lambda: defaultdict(int))
    genre_songs = defaultdict(set)
    genre_entities = defaultdict(lambda: defaultdict(list))

    all_ents = [(e, "sp") for e in sp_ents] + [(e, "br") for e in br_ents]

    for ent, source in all_ents:
        slot = ent.get("slot", "")
        if slot == "unclassified" or slot == "section":
            continue
        raw_genre = ent.get("genre", "")
        if not raw_genre:
            continue
        genre = normalize_genre(raw_genre)
        song_id = ent.get("song_id")

        genre_slot[genre][slot] += 1
        if song_id:
            genre_songs[genre].add(song_id)
        raw_entity = ent.get("entity", "")
        if raw_entity:
            if isinstance(raw_entity, str):
                entity_text = raw_entity
            elif isinstance(raw_entity, list):
                entity_text = ", ".join(str(x) for x in raw_entity)
            else:
                entity_text = str(raw_entity)
            genre_entities[genre][slot].append(entity_text)

    top_genres = sorted(genre_slot.keys(),
                        key=lambda g: sum(genre_slot[g].values()), reverse=True)

    matrix = []
    for genre in top_genres:
        n_songs = len(genre_songs[genre])
        if n_songs < 2:
            continue
        row = {
            "genre": genre,
            "song_count": n_songs,
            "total_entities": sum(genre_slot[genre].values()),
            "slots_filled": sum(1 for s in SLOTS if genre_slot[genre].get(s, 0) > 0),
            "slots_total": len(SLOTS),
        }
        slot_detail = {}
        for slot in SLOTS:
            count = genre_slot[genre].get(slot, 0)
            ents_list = genre_entities[genre].get(slot, [])
            top_ents = Counter(ents_list).most_common(5)
            slot_detail[slot] = {
                "count": count,
                "per_song": round(count / n_songs, 1) if n_songs else 0,
                "top_entities": [{"entity": e, "freq": f} for e, f in top_ents]
            }
        row["slots"] = slot_detail
        matrix.append(row)

    return matrix

def print_heatmap(matrix):
    short = {
        "genre": "GNR", "instrument": "INS", "drums": "DRM",
        "vocal_main": "VOC", "vocal_chorus": "CHR", "arrangement": "ARR",
        "mixing": "MIX", "effect_electronic": "EFX", "effect_sound": "SFX",
        "tempo_key_time": "TMP", "harmony": "HAR", "absence": "ABS",
        "mastering": "MST"
    }
    header = f"{'Genre':<25} {'#':>3} │" + "".join(f"{short[s]:>4}" for s in SLOTS) + " │Fill"
    print(header)
    print("─" * len(header))

    for row in matrix[:40]:
        g = row["genre"][:24]
        n = row["song_count"]
        cells = []
        for s in SLOTS:
            v = row["slots"][s]["per_song"]
            if v == 0:
                cells.append("   ·")
            elif v < 1:
                cells.append(f"  .{int(v*10)}")
            elif v < 10:
                cells.append(f" {v:3.1f}")
            else:
                cells.append(f"{v:4.0f}")
        fill = row["slots_filled"]
        print(f"{g:<25} {n:>3} │{''.join(cells)} │{fill:>2}/{row['slots_total']}")

def find_gaps(matrix):
    gaps = []
    for row in matrix:
        if row["song_count"] < 3:
            continue
        for slot in SLOTS:
            if slot == "genre":
                continue
            if row["slots"][slot]["count"] == 0:
                gaps.append({
                    "genre": row["genre"],
                    "missing_slot": slot,
                    "song_count": row["song_count"]
                })
    return gaps

def main():
    print("Loading data...")
    sp_ents, br_ents = load_entities()
    song_genres = load_song_genres()
    print(f"  SP: {len(sp_ents)} entities, BR: {len(br_ents)} entities")

    print("Building matrix...")
    matrix = build_matrix(sp_ents, br_ents, song_genres)
    print(f"  {len(matrix)} genres (≥2 songs)")

    print("\n" + "=" * 100)
    print("SLOT-GENRE MATRIX (entities per song)")
    print("=" * 100)
    print_heatmap(matrix)

    gaps = find_gaps(matrix)
    if gaps:
        print(f"\n=== GAPS: {len(gaps)} genre×slot combinations with 0 entities (≥3 songs) ===")
        for g in gaps[:20]:
            print(f"  {g['genre']} × {g['missing_slot']} ({g['song_count']} songs)")

    output = {
        "version": "3.3",
        "created_at": "2026-04-27",
        "corpus": {
            "sp_entities": len(sp_ents),
            "br_entities": len(br_ents),
            "genres_with_2plus_songs": len(matrix)
        },
        "slots": SLOTS,
        "matrix": matrix,
        "gaps": gaps
    }
    with open(OUTPUT, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {OUTPUT}")

if __name__ == "__main__":
    main()
