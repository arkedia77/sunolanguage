#!/usr/bin/env python3
"""
slot_assembler.py — Assemble retrieved chunks into a valid SP preset.

Takes slot payloads from serendipity.py retrieval and assembles them
into a coherent SP following Top-Anchor ordering:
  1. Genre          (highest weight)
  2. Instruments    (high — up to 2 sentences)
  3. Drums          (high)
  4. Vocal          (medium)
  5. Arrangement    (low)
  6. Tempo/Key/Time (lowest)

Bracket patterns can be overlaid as section-level directives.

Usage:
    # Typically called from preset_engine.py, not standalone
    python scripts/slot_assembler.py --json '{"genre": {...}, "instrument": [...], ...}'
"""

import json
import re
import sys
from pathlib import Path

TOP_ANCHOR_SLOTS = [
    "genre",
    "instrument",
    "drums",
    "vocal_main",
    "arrangement",
    "tempo_key_time",
]

SP_CHAR_LIMIT = 1000


def clean_text(text: str) -> str:
    text = text.strip()
    if text and not text.endswith("."):
        text += "."
    text = re.sub(r"\.{2,}", ".", text)
    return text


def assemble_sp(preset: dict, bracket_overlay: list[dict] | None = None) -> str:
    sentences = []

    for slot in TOP_ANCHOR_SLOTS:
        if slot not in preset:
            continue
        val = preset[slot]

        if isinstance(val, list):
            for item in val:
                text = item.get("text", "") if isinstance(item, dict) else str(item)
                text = clean_text(text)
                if text and text != ".":
                    sentences.append(text)
        else:
            text = val.get("text", "") if isinstance(val, dict) else str(val)
            text = clean_text(text)
            if text and text != ".":
                sentences.append(text)

    if bracket_overlay:
        for br in bracket_overlay:
            text = br.get("text", "")
            if text:
                bracket_text = f"[{text.strip()}]"
                sentences.append(bracket_text)

    sp = " ".join(sentences)

    if len(sp) > SP_CHAR_LIMIT:
        sp = truncate_to_limit(sp, SP_CHAR_LIMIT)

    return sp


def truncate_to_limit(sp: str, limit: int) -> str:
    parts = re.split(r'(?<=[.\]])\s+', sp)
    result = []
    length = 0
    for part in parts:
        added_len = len(part) + (1 if result else 0)
        if length + added_len > limit:
            break
        result.append(part)
        length += added_len
    return " ".join(result)


def extract_metadata(preset: dict) -> dict:
    meta = {}
    genre_val = preset.get("genre")
    if isinstance(genre_val, dict):
        meta["genre"] = genre_val.get("genre", "")
    instruments = preset.get("instrument", [])
    if isinstance(instruments, list):
        meta["instruments"] = [
            i.get("entity", i.get("text", ""))
            for i in instruments if isinstance(i, dict)
        ]
    elif isinstance(instruments, dict):
        meta["instruments"] = [instruments.get("entity", instruments.get("text", ""))]
    return meta


def preset_summary(preset: dict) -> str:
    lines = []
    for slot in TOP_ANCHOR_SLOTS:
        if slot not in preset:
            lines.append(f"  [{slot}] (empty)")
            continue
        val = preset[slot]
        if isinstance(val, list):
            for v in val:
                text = v.get("text", "") if isinstance(v, dict) else str(v)
                genre = v.get("genre", "") if isinstance(v, dict) else ""
                suffix = f" [{genre}]" if genre else ""
                lines.append(f"  [{slot}] {text[:80]}{suffix}")
        else:
            text = val.get("text", "") if isinstance(val, dict) else str(val)
            genre = val.get("genre", "") if isinstance(val, dict) else ""
            suffix = f" [{genre}]" if genre else ""
            lines.append(f"  [{slot}] {text[:80]}{suffix}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: slot_assembler.py --json '{...}'")
        sys.exit(1)

    if sys.argv[1] == "--json":
        preset = json.loads(sys.argv[2])
    else:
        preset = json.loads(sys.argv[1])

    print("=== Slot Summary ===")
    print(preset_summary(preset))
    print()

    sp = assemble_sp(preset)
    print("=== Assembled SP ===")
    print(sp)
    print(f"\nLength: {len(sp)} chars")
