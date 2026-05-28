#!/usr/bin/env python3
"""
preset_engine.py — Serendipity Preset Engine CLI.

End-to-end CLI that ties together chunk retrieval (serendipity.py),
SP assembly (slot_assembler.py), and native validation (preset_validator.py).

Commands:
    discover   Generate presets via Controlled Drift
    cross      Cross-genre neighbor discovery
    walk       Random walk preset generation
    batch      Generate N presets with validation stats
    ingest     Incremental ingest of new corpus data
    stats      Show Qdrant collection and corpus stats

Usage:
    python scripts/preset_engine.py discover "acoustic guitar" --drift=0.5
    python scripts/preset_engine.py discover "edm synth" --drift=0.8 --validate
    python scripts/preset_engine.py cross --from=Jazz --to=Metal
    python scripts/preset_engine.py walk --steps=7
    python scripts/preset_engine.py batch --count=10 --drift=0.5 --validate
    python scripts/preset_engine.py ingest --source=data/reanalysis_v2
    python scripts/preset_engine.py stats
"""

import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

QDRANT_HOST = os.environ.get("QDRANT_HOST", "100.90.35.121")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", None)
COLLECTION_NAME = "sunolang_presets"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

HISTORY_DIR = PROJECT_ROOT / "data" / "preset_history"


def cmd_discover(args: list[str]):
    from serendipity import controlled_drift, get_client, get_model
    from slot_assembler import assemble_sp, preset_summary
    from preset_validator import validate_sp, print_validation

    seed = "acoustic guitar"
    drift = 0.5
    do_validate = False
    n_presets = 1

    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--drift="):
            drift = float(a.split("=")[1])
        elif a.startswith("--count="):
            n_presets = int(a.split("=")[1])
        elif a == "--validate":
            do_validate = True
        elif not a.startswith("--"):
            seed = a
        i += 1

    print(f"Discover: seed='{seed}', drift={drift}, count={n_presets}")
    print()

    client = get_client()
    model = get_model()

    for n in range(n_presets):
        if n_presets > 1:
            print(f"--- Preset {n+1}/{n_presets} ---")

        preset = controlled_drift(seed, drift_factor=drift, client=client, model=model)
        print(preset_summary(preset))
        print()

        sp = assemble_sp(preset)
        print(f"SP ({len(sp)} chars):")
        print(f"  {sp}")
        print()

        if do_validate:
            result = validate_sp(sp)
            print_validation(result)
            print()

        if n_presets > 1 and n < n_presets - 1:
            print()


def cmd_cross(args: list[str]):
    from serendipity import cross_genre_neighbor, get_client

    fg, tg, sl = "Jazz", "Metal", "instrument"
    for a in args:
        if a.startswith("--from="):
            fg = a.split("=")[1]
        elif a.startswith("--to="):
            tg = a.split("=")[1]
        elif a.startswith("--slot="):
            sl = a.split("=")[1]

    print(f"Cross-Genre: {fg} -> {tg}, slot={sl}")
    print()

    client = get_client()
    results = cross_genre_neighbor(fg, tg, slot=sl, client=client)

    for r in results:
        print(f"  score={r['score']:.4f}")
        src = r["source"].get("text", "")[:80]
        tgt = r["target"].get("text", "")[:80]
        print(f"    source [{fg}]: {src}")
        print(f"    target [{tg}]: {tgt}")
        print()


def cmd_walk(args: list[str]):
    from serendipity import random_walk, get_client
    from slot_assembler import assemble_sp, preset_summary
    from preset_validator import validate_sp, print_validation

    steps = 7
    do_validate = False
    for a in args:
        if a.startswith("--steps="):
            steps = int(a.split("=")[1])
        elif a == "--validate":
            do_validate = True

    print(f"Random Walk: {steps} steps")
    print()

    client = get_client()
    preset = random_walk(steps=steps, client=client)
    print(preset_summary(preset))
    print()

    sp = assemble_sp(preset)
    print(f"SP ({len(sp)} chars):")
    print(f"  {sp}")

    if do_validate:
        print()
        result = validate_sp(sp)
        print_validation(result)


def cmd_batch(args: list[str]):
    from serendipity import controlled_drift, random_walk, get_client, get_model
    from slot_assembler import assemble_sp
    from preset_validator import validate_sp, print_validation

    count = 10
    drift = 0.5
    mode = "drift"
    seed = "acoustic guitar"
    do_validate = True
    save = False

    for a in args:
        if a.startswith("--count="):
            count = int(a.split("=")[1])
        elif a.startswith("--drift="):
            drift = float(a.split("=")[1])
        elif a.startswith("--mode="):
            mode = a.split("=")[1]
        elif a.startswith("--seed="):
            seed = a.split("=")[1]
        elif a == "--save":
            save = True
        elif a == "--no-validate":
            do_validate = False

    print(f"Batch: {count} presets, mode={mode}, drift={drift}")
    if mode == "drift":
        print(f"  seed='{seed}'")
    print()

    client = get_client()
    model = get_model() if mode == "drift" else None

    results = []
    t0 = time.time()

    for i in range(count):
        if mode == "drift":
            preset = controlled_drift(seed, drift_factor=drift, client=client, model=model)
        else:
            preset = random_walk(steps=7, client=client)

        sp = assemble_sp(preset)
        entry = {"index": i, "sp": sp, "drift": drift, "mode": mode}

        if do_validate:
            val = validate_sp(sp)
            entry["validation"] = val
            print(f"  [{i+1:3d}/{count}] ", end="")
            print_validation(val)
        else:
            print(f"  [{i+1:3d}/{count}] SP={len(sp)}chars")

        results.append(entry)

    elapsed = time.time() - t0
    print(f"\nGenerated {count} presets in {elapsed:.1f}s")

    if do_validate:
        verdicts = [r["validation"]["verdict"] for r in results]
        pass_n = verdicts.count("PASS")
        warn_n = verdicts.count("WARN")
        fail_n = verdicts.count("FAIL")
        avg_ratio = sum(r["validation"]["native_ratio"] for r in results) / len(results)
        print(f"  PASS={pass_n}  WARN={warn_n}  FAIL={fail_n}")
        print(f"  Avg native ratio: {avg_ratio:.1%}")

    if save:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_path = HISTORY_DIR / f"batch_{ts}.json"
        with open(out_path, "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"  Saved to {out_path}")


def cmd_ingest(args: list[str]):
    from chunk_builder import build_chunks
    from embed_pipeline import cmd_build

    augment = True
    for a in args:
        if a == "--no-augment":
            augment = False

    print("Incremental ingest: rebuilding chunks and re-embedding...")
    print()
    cmd_build(batch_size=500)


def cmd_stats(args: list[str]):
    from embed_pipeline import cmd_stats as qdrant_stats

    chunks_file = PROJECT_ROOT / "data" / "chunks.json"
    if chunks_file.exists():
        with open(chunks_file) as f:
            chunks = json.load(f)
        print(f"Local chunks: {len(chunks)}")
        by_slot = {}
        for c in chunks:
            slot = c["payload"]["slot"]
            by_slot[slot] = by_slot.get(slot, 0) + 1
        for slot, count in sorted(by_slot.items(), key=lambda x: -x[1]):
            print(f"  {slot}: {count}")
        print()

    print("Qdrant collection:")
    try:
        qdrant_stats()
    except Exception as e:
        print(f"  (unavailable: {e})")

    if HISTORY_DIR.exists():
        history_files = sorted(HISTORY_DIR.glob("batch_*.json"))
        if history_files:
            print(f"\nPreset history: {len(history_files)} batches")
            for hf in history_files[-3:]:
                print(f"  {hf.name}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    rest = args[1:]

    commands = {
        "discover": cmd_discover,
        "cross": cmd_cross,
        "walk": cmd_walk,
        "batch": cmd_batch,
        "ingest": cmd_ingest,
        "stats": cmd_stats,
    }

    if cmd in commands:
        commands[cmd](rest)
    elif cmd in ("--help", "-h"):
        print(__doc__)
    else:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(commands.keys())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
