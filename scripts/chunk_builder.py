#!/usr/bin/env python3
"""
chunk_builder.py — Corpus entities → embeddable chunks for Qdrant.

Reads sp_entities_v3.json and bracket_entities_v3.json,
produces a unified chunk list with IDs, text, and metadata payload.

Usage:
    python scripts/chunk_builder.py build          # build chunks JSON
    python scripts/chunk_builder.py build --augment # include genre/kit in embed text
    python scripts/chunk_builder.py stats           # show chunk statistics
"""

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SP_ENTITIES = PROJECT_ROOT / "data" / "reanalysis_v2" / "sp_entities_v3.json"
BR_ENTITIES = PROJECT_ROOT / "data" / "reanalysis_v2" / "bracket_entities_v3.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "chunks.json"

PRESET_SLOTS = {
    "genre", "instrument", "drums", "vocal_main", "vocal_chorus",
    "arrangement", "tempo_key_time", "effect_electronic",
    "harmony", "mixing", "effect_sound",
}

SKIP_SLOTS = {"unclassified", "mastering", "absence", "pronunciation", "transition"}


def build_chunk_id(source: str, slot: str, song_id, seq: int) -> str:
    sid = str(song_id).replace("/", "_").replace(" ", "_")
    return f"{source}_{slot}_{sid}_{seq:03d}"


def extract_text(entity: dict, source_type: str) -> str:
    if source_type == "sp":
        return entity.get("sentence", "").strip()
    else:
        return entity.get("bracket", "").strip()


def augment_text(text: str, entity: dict) -> str:
    parts = [text]
    if entity.get("genre"):
        parts.append(f"genre: {entity['genre']}")
    if entity.get("kit"):
        parts.append(f"kit: {entity['kit']}")
    return " | ".join(parts)


def build_payload(entity: dict, source_type: str) -> dict:
    payload = {
        "slot": entity.get("slot", ""),
        "entity": entity.get("entity", ""),
        "genre": entity.get("genre", ""),
        "song_id": entity.get("song_id", 0),
        "source": source_type,
        "modifiers": json.dumps(entity.get("modifiers", []), ensure_ascii=False),
    }
    # ★관측층(입력/출력)은 **전달만** 한다 — 여기서 만들어내지 않는다.
    #   파서(`parse_slot_entities_v3.py`)가 `suno_reanalysis`를 도는 지점에서 찍은 값이고,
    #   없으면 **"unstamped"(=아직 안 봄)**로 둔다. ★"output"으로 기본값을 주면 안 된다 —
    #   그 순간 「안 찍힌 것」이 「출력층으로 확인된 것」으로 승격되고, 이건 08-15에 층이 8주간
    #   뒤집혀 있던 사고와 정확히 같은 형태다(라벨이 근거를 앞지름).
    payload["observation_layer"] = entity.get("observation_layer") or "unstamped"
    if entity.get("kit"):
        payload["kit"] = entity["kit"]
    if entity.get("layer"):
        # ★`layer`=편성 역할층(lead/rhythm/bass/pad/fill). `observation_layer`(입력/출력)와
        #   **다른 축**이다. 이름이 비슷해 섞이기 쉬우니 소비처는 둘을 구분해 읽을 것.
        payload["layer"] = entity["layer"]
    if entity.get("role"):
        payload["role"] = entity["role"]
    if entity.get("pattern"):
        payload["pattern"] = entity["pattern"]
    if entity.get("effects"):
        payload["effects"] = json.dumps(entity["effects"], ensure_ascii=False)
    if entity.get("chords"):
        payload["chords"] = json.dumps(entity["chords"], ensure_ascii=False)
    if source_type == "bracket" and entity.get("action"):
        payload["action"] = entity["action"]
    return payload


def build_chunks(augment: bool = False) -> list[dict]:
    with open(SP_ENTITIES) as f:
        sp_data = json.load(f)
    with open(BR_ENTITIES) as f:
        br_data = json.load(f)

    chunks = []
    seq_counter: dict[tuple, int] = {}

    for source_type, entities in [("sp", sp_data), ("bracket", br_data)]:
        for ent in entities:
            slot = ent.get("slot", "unclassified")
            if slot in SKIP_SLOTS:
                continue

            text = extract_text(ent, source_type)
            if not text or len(text) < 3:
                continue

            song_id = ent.get("song_id", 0)
            key = (source_type, slot, song_id)
            seq = seq_counter.get(key, 0)
            seq_counter[key] = seq + 1

            chunk_id = build_chunk_id(source_type, slot, song_id, seq)
            embed_text = augment_text(text, ent) if augment else text
            payload = build_payload(ent, source_type)

            chunks.append({
                "chunk_id": chunk_id,
                "text": text,
                "embed_text": embed_text,
                "payload": payload,
            })

    return chunks


def cmd_build(augment: bool = False):
    chunks = build_chunks(augment=augment)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Built {len(chunks)} chunks → {OUTPUT_FILE}")
    print_stats(chunks)


def cmd_stats():
    if not OUTPUT_FILE.exists():
        print(f"No chunks file found. Run: python {__file__} build")
        return
    with open(OUTPUT_FILE) as f:
        chunks = json.load(f)
    print_stats(chunks)


def print_stats(chunks: list[dict]):
    print(f"\nTotal chunks: {len(chunks)}")
    by_source = Counter(c["payload"]["source"] for c in chunks)
    print(f"By source: {dict(by_source)}")
    # ★관측층을 **항상** 낸다 — 프리셋 소비처가 「이게 Suno가 들은 결과(출력층)인지,
    #   우리가 써넣은 지시(입력층)인지」를 모르고 쓰면 프리셋의 의미가 뒤바뀐다.
    by_obs = Counter(c["payload"].get("observation_layer", "(필드없음)") for c in chunks)
    print(f"By observation_layer: {dict(by_obs)}  ★출력층=Suno가 완성곡을 듣고 서술한 것")
    if by_obs.get("unstamped"):
        print(f"  ⚠️ unstamped {by_obs['unstamped']}건 — 파서 재실행 전 산출분. "
              f"「출력층으로 확인됨」이 아니라 **아직 안 봄**이다.")
    by_slot = Counter(c["payload"]["slot"] for c in chunks)
    print(f"\nBy slot:")
    for slot, count in by_slot.most_common():
        print(f"  {slot}: {count}")
    text_lens = [len(c["text"]) for c in chunks]
    print(f"\nText length: min={min(text_lens)}, max={max(text_lens)}, avg={sum(text_lens)//len(text_lens)}")
    songs = set(c["payload"]["song_id"] for c in chunks)
    print(f"Unique songs: {len(songs)}")
    genres = set(c["payload"]["genre"] for c in chunks if c["payload"]["genre"])
    print(f"Unique genres: {len(genres)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "build":
        augment = "--augment" in args
        cmd_build(augment=augment)
    elif args[0] == "stats":
        cmd_stats()
    else:
        print(f"Usage: python {__file__} [build [--augment] | stats]")
