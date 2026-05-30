#!/usr/bin/env python3
"""
corpus_quality_gate.py — Ingest validation gate for lyrics corpus.

Validates new lyrics chunks before they enter the Qdrant corpus.
Ensures quality, deduplicates, and flags noise.

Usage:
    python scripts/corpus_quality_gate.py validate data/lyrics_chunks.json
    python scripts/corpus_quality_gate.py scan                    # scan existing corpus
    python scripts/corpus_quality_gate.py dedup data/lyrics_chunks.json --write
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MIN_TEXT_CHARS = 10
MIN_LINES = 1
MAX_CHARS_PER_SECTION = 1500
VALID_SECTION_TAGS = {
    "verse", "chorus", "bridge", "pre_chorus", "hook",
    "intro", "outro", "interlude", "instrumental", "drop", "tag", "coda",
}
VALID_GRANULARITIES = {"section", "couplet"}

SP_DIRECTIVE_KEYWORDS = {
    "layered leads", "maximum energy", "builds to", "crescendo to",
    "palm muted", "power chords", "instrumental break", "solo section",
    "key change", "double time feel", "half time feel", "tempo change",
    "stacked synths", "stacked pads", "full intensity", "heavy distortion",
    "fade in", "fade out slowly", "drop section", "breakdown section",
}


def is_sp_directive(text: str) -> bool:
    clean_lines = [l.strip() for l in text.strip().split("\n")
                   if l.strip() and not l.strip().startswith("[")]
    if not clean_lines:
        return False
    combined = " ".join(clean_lines).lower()
    has_korean = bool(re.search(r"[가-힯]", combined))
    if not has_korean and len(combined) < 80:
        for kw in SP_DIRECTIVE_KEYWORDS:
            if kw in combined:
                return True
    return False


def validate_chunk(chunk: dict) -> list[str]:
    issues = []
    payload = chunk.get("payload", {})
    text = payload.get("text", "")
    tag = payload.get("section_tag", "")
    gran = payload.get("granularity", "")
    sid = payload.get("song_id", 0)

    if not text or not text.strip():
        issues.append("empty_text")
        return issues

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    if len(text.strip()) < MIN_TEXT_CHARS:
        issues.append(f"too_short({len(text.strip())}c)")

    if len(text) > MAX_CHARS_PER_SECTION:
        issues.append(f"too_long({len(text)}c)")

    if tag and tag not in VALID_SECTION_TAGS:
        issues.append(f"invalid_tag({tag})")

    if gran and gran not in VALID_GRANULARITIES:
        issues.append(f"invalid_granularity({gran})")

    if not sid:
        issues.append("missing_song_id")

    bracket_lines = [l for l in lines if l.startswith("[") and l.endswith("]")]
    if bracket_lines and tag in ("verse", "chorus", "bridge", "pre_chorus"):
        issues.append(f"bracket_in_lyric_section({len(bracket_lines)})")

    if len(lines) >= 3:
        unique = set(lines)
        if len(unique) == 1:
            issues.append("repetitive_single_line")

    if is_sp_directive(text):
        issues.append("sp_directive")

    return issues


def find_duplicates(chunks: list[dict]) -> dict:
    text_to_chunks = defaultdict(list)
    for i, c in enumerate(chunks):
        text = c.get("payload", {}).get("text", "")
        sid = c.get("payload", {}).get("song_id", 0)
        gran = c.get("payload", {}).get("granularity", "")
        text_to_chunks[(text, sid, gran)].append(i)

    dupes = {}
    for key, indices in text_to_chunks.items():
        if len(indices) > 1:
            dupes[key] = indices
    return dupes


def scan_corpus(chunks: list[dict]) -> dict:
    results = {
        "total": len(chunks),
        "issues": defaultdict(int),
        "flagged_indices": [],
        "duplicates": {},
        "by_granularity": Counter(),
        "by_tag": Counter(),
    }

    for i, chunk in enumerate(chunks):
        payload = chunk.get("payload", {})
        results["by_granularity"][payload.get("granularity", "?")] += 1
        results["by_tag"][payload.get("section_tag", "?")] += 1

        issues = validate_chunk(chunk)
        if issues:
            results["flagged_indices"].append((i, issues))
            for issue in issues:
                issue_type = issue.split("(")[0]
                results["issues"][issue_type] += 1

    dupes = find_duplicates(chunks)
    results["duplicates"] = dupes
    dup_extra = sum(len(idxs) - 1 for idxs in dupes.values())
    results["issues"]["exact_duplicate"] = dup_extra

    return results


def dedup_chunks(chunks: list[dict]) -> tuple[list[dict], int]:
    seen = set()
    cleaned = []
    removed = 0
    for chunk in chunks:
        payload = chunk.get("payload", {})
        key = (payload.get("text", ""),
               payload.get("song_id", 0),
               payload.get("granularity", ""))
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        cleaned.append(chunk)
    return cleaned, removed


def print_scan_results(results: dict):
    print(f"=== Corpus Quality Scan ===")
    print(f"  Total chunks: {results['total']}")
    print(f"  Unique chunks: {results['total'] - results['issues'].get('exact_duplicate', 0)}")
    print()
    print(f"  By granularity: {dict(results['by_granularity'])}")
    print(f"  By tag (top 10):")
    for tag, cnt in results["by_tag"].most_common(10):
        print(f"    {tag}: {cnt}")
    print()
    print(f"  Issues found:")
    if not results["issues"]:
        print("    (none)")
    else:
        for issue, cnt in sorted(results["issues"].items(), key=lambda x: -x[1]):
            print(f"    {issue}: {cnt}")
    print()
    if results["flagged_indices"]:
        print(f"  Flagged chunks (first 10):")
        for idx, issues in results["flagged_indices"][:10]:
            print(f"    [{idx}] {issues}")


def cmd_validate(args: list[str]):
    path = args[0] if args else str(PROJECT_ROOT / "data" / "lyrics_chunks.json")
    with open(path) as f:
        chunks = json.load(f)

    results = scan_corpus(chunks)
    print_scan_results(results)

    total_issues = sum(results["issues"].values())
    if total_issues == 0:
        print("\n  VERDICT: CLEAN")
    else:
        pct = total_issues / results["total"] * 100
        if pct < 1:
            print(f"\n  VERDICT: PASS ({pct:.2f}% issues)")
        elif pct < 5:
            print(f"\n  VERDICT: WARN ({pct:.1f}% issues)")
        else:
            print(f"\n  VERDICT: FAIL ({pct:.1f}% issues)")


def cmd_scan(args: list[str]):
    cmd_validate(args)


def cmd_dedup(args: list[str]):
    path = args[0] if args else str(PROJECT_ROOT / "data" / "lyrics_chunks.json")
    do_write = "--write" in args

    with open(path) as f:
        chunks = json.load(f)

    cleaned, removed = dedup_chunks(chunks)
    print(f"Dedup: {len(chunks)} → {len(cleaned)} ({removed} removed)")

    if do_write and removed > 0:
        with open(path, "w") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        print(f"  Written to {path}")
    elif removed > 0:
        print(f"  (dry run — use --write to save)")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    rest = args[1:]

    commands = {
        "validate": cmd_validate,
        "scan": cmd_scan,
        "dedup": cmd_dedup,
    }

    if cmd in commands:
        commands[cmd](rest)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
