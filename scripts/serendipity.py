#!/usr/bin/env python3
"""
serendipity.py — Serendipitous SP preset discovery engine.

Three retrieval modes that break genre conventions:
  1. Controlled Drift  — seed + per-slot noise → cross-genre combos
  2. Cross-Genre Neighbor — find closest match in genre B for a genre A chunk
  3. Random Walk — chain: pick random chunk → nearest in next slot → chain

Usage (standalone test):
    python scripts/serendipity.py drift "acoustic guitar" --factor=0.5
    python scripts/serendipity.py cross --from-genre=Jazz --to-genre=Metal --slot=instrument
    python scripts/serendipity.py walk --steps=7
"""

import json
import os
import sys
import random
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

COLLECTION_NAME = "sunolang_presets"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_DIM = 384

QDRANT_HOST = os.environ.get("QDRANT_HOST", "100.90.35.121")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", None)

SP_SLOTS = ["genre", "instrument", "drums", "vocal_main", "arrangement", "tempo_key_time"]
INSTRUMENT_COUNT = 4
BOOST_SLOTS = ["instrument", "arrangement", "vocal_main"]
MIN_SP_LENGTH = 550


def get_client():
    from qdrant_client import QdrantClient
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY)


def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def make_filter(slot: str, genre: str = None):
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    conditions = [FieldCondition(key="slot", match=MatchValue(value=slot))]
    if genre:
        conditions.append(FieldCondition(key="genre", match=MatchValue(value=genre)))
    return Filter(must=conditions)


def normalize(vec):
    n = np.linalg.norm(vec)
    return vec / n if n > 0 else vec


def controlled_drift(seed_text: str, drift_factor: float = 0.5,
                     n_instruments: int = INSTRUMENT_COUNT,
                     client=None, model=None) -> dict:
    if client is None:
        client = get_client()
    if model is None:
        model = get_model()

    seed_vec = model.encode(seed_text)
    preset = {}

    for slot in SP_SLOTS:
        noise = np.random.normal(0, drift_factor, VECTOR_DIM)
        perturbed = normalize(seed_vec + noise)

        n = n_instruments if slot == "instrument" else 1
        # tempo_key_time는 후보를 넉넉히 받아 key+BPM 둘 다 든 청크를 우선 선택
        # (코퍼스 tempo 청크의 ~47%만 둘 다 명시 — Leo 지적 키/BPM 누락 보정). 2026-06-19.
        limit = 12 if slot == "tempo_key_time" else n
        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=perturbed.tolist(),
            query_filter=make_filter(slot),
            limit=limit,
        )
        if response.points:
            if slot == "instrument":
                preset[slot] = [hit.payload for hit in response.points]
            elif slot == "tempo_key_time":
                def _score(p):
                    t = (p.payload.get("text", "") or "").lower()
                    return ("key of" in t) + ("bpm" in t)
                best = max(response.points, key=_score)
                preset[slot] = best.payload
            else:
                preset[slot] = response.points[0].payload

    from slot_assembler import assemble_sp
    trial = assemble_sp(preset)
    if len(trial) < MIN_SP_LENGTH:
        used_texts = {p.get("text", "") for p in (
            preset.get("instrument", []) if isinstance(preset.get("instrument"), list)
            else [preset.get("instrument", {})]
        )}
        for slot in BOOST_SLOTS:
            noise = np.random.normal(0, drift_factor * 1.2, VECTOR_DIM)
            perturbed = normalize(seed_vec + noise)
            response = client.query_points(
                collection_name=COLLECTION_NAME,
                query=perturbed.tolist(),
                query_filter=make_filter(slot),
                limit=3,
            )
            for hit in response.points:
                t = hit.payload.get("text", "")
                if t not in used_texts:
                    used_texts.add(t)
                    if slot == "instrument":
                        if not isinstance(preset.get(slot), list):
                            preset[slot] = [preset[slot]] if slot in preset else []
                        preset[slot].append(hit.payload)
                    else:
                        key = f"{slot}_boost"
                        preset[key] = hit.payload
                    break

    return preset


def cross_genre_neighbor(from_genre: str, to_genre: str, slot: str = "instrument",
                         client=None, model=None, limit: int = 5) -> list[dict]:
    if client is None:
        client = get_client()

    from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchText

    source_results = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(must=[
            FieldCondition(key="slot", match=MatchValue(value=slot)),
            FieldCondition(key="genre", match=MatchText(text=from_genre)),
        ]),
        limit=20,
        with_vectors=True,
    )[0]

    if not source_results:
        print(f"No chunks found for slot={slot}, genre={from_genre}")
        return []

    source = random.choice(source_results)
    source_vector = source.vector

    target_response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=source_vector,
        query_filter=Filter(must=[
            FieldCondition(key="slot", match=MatchValue(value=slot)),
            FieldCondition(key="genre", match=MatchText(text=to_genre)),
        ]),
        limit=limit,
    )

    return [{
        "source": source.payload,
        "target": hit.payload,
        "score": hit.score,
    } for hit in target_response.points]


def random_walk(steps: int = 7, client=None, model=None) -> dict:
    if client is None:
        client = get_client()

    slot_order = list(SP_SLOTS)
    random.shuffle(slot_order)
    if len(slot_order) < steps:
        slot_order = (slot_order * ((steps // len(slot_order)) + 1))[:steps]

    preset = {}
    current_vector = None

    for slot in slot_order:
        if current_vector is None:
            all_in_slot = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=make_filter(slot),
                limit=100,
                with_vectors=True,
            )[0]
            if not all_in_slot:
                continue
            pick = random.choice(all_in_slot)
            preset[slot] = pick.payload
            current_vector = pick.vector
        else:
            response = client.query_points(
                collection_name=COLLECTION_NAME,
                query=current_vector,
                query_filter=make_filter(slot),
                limit=1,
            )
            if response.points:
                hit = response.points[0]
                if slot == "instrument" and slot in preset:
                    if not isinstance(preset[slot], list):
                        preset[slot] = [preset[slot]]
                    preset[slot].append(hit.payload)
                else:
                    preset[slot] = hit.payload
                result_with_vec = client.scroll(
                    collection_name=COLLECTION_NAME,
                    scroll_filter=make_filter(slot),
                    limit=1,
                    with_vectors=True,
                )[0]
                if result_with_vec:
                    current_vector = result_with_vec[0].vector

    return preset


def format_preset(preset: dict) -> str:
    lines = []
    for slot in SP_SLOTS:
        if slot not in preset:
            continue
        val = preset[slot]
        if isinstance(val, list):
            for v in val:
                lines.append(f"  [{slot}] {v.get('text', '')}")
        else:
            lines.append(f"  [{slot}] {val.get('text', '')}")
    return "\n".join(lines)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: serendipity.py drift|cross|walk [options]")
        sys.exit(1)

    mode = args[0]

    if mode == "drift":
        seed = args[1] if len(args) > 1 else "acoustic guitar"
        factor = 0.5
        for a in args:
            if a.startswith("--factor="):
                factor = float(a.split("=")[1])
        print(f"Controlled Drift: seed='{seed}', drift={factor}")
        preset = controlled_drift(seed, drift_factor=factor)
        print(format_preset(preset))

    elif mode == "cross":
        fg, tg, sl = "Jazz", "Metal", "instrument"
        for a in args:
            if a.startswith("--from-genre="):
                fg = a.split("=")[1]
            elif a.startswith("--to-genre="):
                tg = a.split("=")[1]
            elif a.startswith("--slot="):
                sl = a.split("=")[1]
        print(f"Cross-Genre: {fg} → {tg}, slot={sl}")
        results = cross_genre_neighbor(fg, tg, slot=sl)
        for r in results:
            print(f"  score={r['score']:.4f}")
            print(f"    source: {r['source'].get('text', '')[:80]}")
            print(f"    target: {r['target'].get('text', '')[:80]}")

    elif mode == "walk":
        steps = 7
        for a in args:
            if a.startswith("--steps="):
                steps = int(a.split("=")[1])
        print(f"Random Walk: {steps} steps")
        preset = random_walk(steps=steps)
        print(format_preset(preset))
