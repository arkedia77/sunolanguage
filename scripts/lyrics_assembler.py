#!/usr/bin/env python3
"""
lyrics_assembler.py — Assemble selected lyrics sections into a Suno-format sheet.

Takes section payloads and produces a complete lyrics sheet with
proper [SectionTag] bracket formatting.

Usage:
    python scripts/lyrics_assembler.py --json '{"verse": {...}, "chorus": {...}}'
"""

import json
import sys

DEFAULT_STRUCTURE = ["verse", "pre_chorus", "chorus", "verse", "bridge", "chorus", "outro"]

TAG_DISPLAY = {
    "verse": "Verse",
    "chorus": "Chorus",
    "pre_chorus": "Pre-Chorus",
    "bridge": "Bridge",
    "hook": "Hook",
    "intro": "Intro",
    "outro": "Outro",
    "interlude": "Interlude",
    "tag": "Tag",
    "drop": "Drop",
    "instrumental": "Instrumental",
    "coda": "Coda",
}

LYRICS_CHAR_LIMIT = 3000


def _is_bracket_section(payload: dict) -> bool:
    if isinstance(payload, dict):
        return payload.get("source") == "bracket_preset"
    return False


def assemble_lyrics(sections: dict[str, dict],
                    structure: list[str] = None) -> str:
    if structure is None:
        structure = DEFAULT_STRUCTURE

    lines = []
    tag_counts = {}
    chorus_first = {}

    for tag in structure:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        occurrence = tag_counts[tag]
        indexed_key = f"{tag}_{occurrence}"

        if tag == "chorus" and occurrence > 1 and "chorus" in chorus_first:
            payload = chorus_first["chorus"]
        else:
            payload = sections.get(indexed_key) or sections.get(tag)

        if payload is None:
            continue

        text = payload.get("text", "") if isinstance(payload, dict) else str(payload)
        if not text.strip():
            continue

        if tag == "chorus" and occurrence == 1:
            chorus_first["chorus"] = payload

        is_bracket = _is_bracket_section(payload)

        display_tag = TAG_DISPLAY.get(tag, tag.replace("_", " ").title())
        if tag == "verse":
            display_tag = f"Verse {occurrence}"
        elif tag == "hook":
            display_tag = f"Hook"

        lines.append(f"[{display_tag}]")
        lines.append(text.strip())
        lines.append("")

    result = "\n".join(lines).strip()

    if len(result) > LYRICS_CHAR_LIMIT:
        result = truncate_lyrics(result, LYRICS_CHAR_LIMIT)

    return result


def truncate_lyrics(lyrics: str, limit: int) -> str:
    sections = lyrics.split("\n\n")
    result = []
    length = 0
    for section in sections:
        added = len(section) + (2 if result else 0)
        if length + added > limit:
            break
        result.append(section)
        length += added
    return "\n\n".join(result)


def lyrics_summary(sections: dict[str, dict]) -> str:
    lines = []
    for tag, payload in sections.items():
        if isinstance(payload, dict):
            text = payload.get("text", "")
            genre = payload.get("genre", "")
            song_id = payload.get("song_id", "?")
            first_line = text.split("\n")[0][:60] if text else ""
            lines.append(f"  [{tag}] song={song_id} | {first_line} [{genre[:30]}]")
        else:
            lines.append(f"  [{tag}] {str(payload)[:60]}")
    return "\n".join(lines)


def extract_source_info(sections: dict[str, dict]) -> dict:
    songs = set()
    genres = set()
    languages = set()
    for payload in sections.values():
        if isinstance(payload, dict):
            songs.add(payload.get("song_id", 0))
            if payload.get("genre"):
                genres.add(payload["genre"])
            if payload.get("language"):
                languages.add(payload["language"])
    return {
        "song_count": len(songs),
        "songs": sorted(songs),
        "genres": sorted(genres),
        "languages": sorted(languages),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: lyrics_assembler.py --json '{...}'")
        sys.exit(1)

    if sys.argv[1] == "--json":
        sections = json.loads(sys.argv[2])
    else:
        sections = json.loads(sys.argv[1])

    print("=== Section Summary ===")
    print(lyrics_summary(sections))
    print()

    lyrics = assemble_lyrics(sections)
    print("=== Assembled Lyrics ===")
    print(lyrics)
    print(f"\nLength: {len(lyrics)} chars")

    info = extract_source_info(sections)
    print(f"Sources: {info['song_count']} songs, genres: {info['genres'][:3]}")
