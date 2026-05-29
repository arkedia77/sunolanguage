#!/usr/bin/env python3
"""
lyrics_chunk_builder.py — Parse lyrics into hybrid chunks for Qdrant.

Two granularity levels (single collection, granularity field):
  - section:  full [SectionTag] block (existing)
  - couplet:  2-line pairs within each section (new)

Features:
  - Couplet: 2-line sliding pairs, merge lines under 20 chars
  - Chorus dedup: identical chorus text collapsed, repeat_count metadata
  - Genre augmentation in embed_text

Usage:
    python scripts/lyrics_chunk_builder.py build           # build hybrid chunks
    python scripts/lyrics_chunk_builder.py build --augment  # include genre in embed text
    python scripts/lyrics_chunk_builder.py stats            # show chunk statistics
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MERGED_FILE = PROJECT_ROOT / "data" / "reanalysis_v2" / "merged_4values.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "lyrics_chunks.json"

TAG_NORMALIZE = {
    "verse": "verse",
    "verse 1": "verse", "verse 2": "verse", "verse 3": "verse", "verse 4": "verse",
    "verse 1-a": "verse", "verse 1-b": "verse", "verse 2-a": "verse", "verse 2-b": "verse",
    "chorus": "chorus",
    "chorus 1": "chorus", "chorus 2": "chorus", "chorus 3": "chorus",
    "final chorus": "chorus", "climax chorus": "chorus", "double chorus": "chorus",
    "drop/chorus": "chorus", "last chorus": "chorus",
    "pre-chorus": "pre_chorus", "pre-chorus 1": "pre_chorus", "pre-chorus 2": "pre_chorus",
    "bridge": "bridge", "bridge 2": "bridge",
    "hook": "hook",
    "intro": "intro",
    "outro": "outro", "long outro": "outro", "final outro": "outro",
    "interlude": "interlude",
    "tag": "tag",
    "drop": "drop", "drop 2": "drop", "final drop": "drop",
    "instrumental": "instrumental",
    "instrumental intro": "intro",
    "coda": "coda",
    "ad-lib": "outro",
    "breakdown": "bridge",
}

VALID_TAGS = {
    "verse", "chorus", "pre_chorus", "bridge", "hook",
    "intro", "outro", "interlude", "tag", "drop",
    "instrumental", "coda",
}

MIN_SECTION_CHARS = 10
MIN_COUPLET_CHARS = 20


def normalize_tag(raw_tag: str) -> str | None:
    lower = raw_tag.strip().lower()
    if lower in TAG_NORMALIZE:
        return TAG_NORMALIZE[lower]
    for prefix in ("verse", "chorus", "pre-chorus", "bridge", "hook",
                   "intro", "outro", "interlude", "drop", "instrumental"):
        if lower.startswith(prefix):
            normalized = prefix.replace("-", "_")
            if normalized in VALID_TAGS:
                return normalized
    return None


def detect_language(text: str) -> str:
    has_kr = bool(re.search(r"[가-힣]", text))
    has_en = bool(re.search(r"[a-zA-Z]{3,}", text))
    if has_kr and has_en:
        return "mixed"
    if has_kr:
        return "ko"
    if has_en:
        return "en"
    return "ko"


def extract_genre_from_sp(song: dict) -> str:
    for clip in (song.get("suno_reanalysis") or []):
        sp = clip.get("sp", "")
        if sp:
            return sp.split(".")[0].strip()
    return ""


def parse_lyrics_sections(lyrics: str) -> list[dict]:
    parts = re.split(r"\[([^\]]+)\]", lyrics)
    sections = []
    for i in range(1, len(parts), 2):
        raw_tag = parts[i].strip()
        text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if not text or len(text) < MIN_SECTION_CHARS:
            continue
        normalized = normalize_tag(raw_tag)
        if normalized is None:
            continue
        sections.append({
            "tag": normalized,
            "tag_raw": raw_tag,
            "text": text,
            "index": len(sections),
        })
    return sections


def dedup_chorus(sections: list[dict]) -> list[dict]:
    """Collapse identical chorus sections, adding repeat_count."""
    seen_chorus: dict[str, int] = {}
    deduped = []
    for sec in sections:
        if sec["tag"] == "chorus":
            normalized_text = sec["text"].strip()
            if normalized_text in seen_chorus:
                seen_chorus[normalized_text] += 1
                continue
            seen_chorus[normalized_text] = 1
            sec = {**sec, "_chorus_key": normalized_text}
        deduped.append(sec)
    for sec in deduped:
        if "_chorus_key" in sec:
            sec["repeat_count"] = seen_chorus[sec.pop("_chorus_key")]
        else:
            sec["repeat_count"] = 1
    return deduped


def split_couplets(text: str) -> list[str]:
    """Split section text into 2-line couplet pairs, merging short lines."""
    raw_lines = [l for l in text.split("\n") if l.strip()]
    if len(raw_lines) < 2:
        return []
    merged = []
    buf = ""
    for line in raw_lines:
        if buf:
            buf = buf + "\n" + line
            merged.append(buf)
            buf = ""
        elif len(line.strip()) < MIN_COUPLET_CHARS:
            buf = line
        else:
            merged.append(line)
    if buf:
        if merged:
            merged[-1] = merged[-1] + "\n" + buf
        else:
            merged.append(buf)

    couplets = []
    for i in range(0, len(merged), 2):
        pair = merged[i:i + 2]
        couplets.append("\n".join(pair))
    return couplets


def build_structure_string(sections: list[dict]) -> str:
    return "|".join(s["tag"] for s in sections)


def build_embed_text(text: str, tag: str, genre: str, augment: bool) -> str:
    if not augment:
        return text
    parts = [text]
    parts.append(f"section: {tag}")
    if genre:
        parts.append(f"genre: {genre}")
    return " | ".join(parts)


def build_chunk_id(song_id, tag: str, seq: int) -> str:
    sid = str(song_id).replace("/", "_").replace(" ", "_")
    return f"lyrics_{tag}_{sid}_{seq:03d}"


def build_chunks(augment: bool = True) -> list[dict]:
    with open(MERGED_FILE) as f:
        songs = json.load(f)

    chunks = []
    sec_counter: dict[tuple, int] = {}
    coup_counter: dict[tuple, int] = {}

    for song in songs:
        lyrics = song.get("leomusic_original", {}).get("lyrics", "")
        if not lyrics:
            continue

        song_id = song.get("song_id", 0)
        genre = extract_genre_from_sp(song)
        sections = parse_lyrics_sections(lyrics)
        if not sections:
            continue

        sections = dedup_chorus(sections)
        structure = build_structure_string(sections)
        language = detect_language(lyrics)

        for sec in sections:
            # --- section-level chunk ---
            key = (song_id, sec["tag"])
            seq = sec_counter.get(key, 0)
            sec_counter[key] = seq + 1

            chunk_id = build_chunk_id(song_id, sec["tag"], seq)
            embed_text = build_embed_text(sec["text"], sec["tag"], genre, augment)

            chunks.append({
                "chunk_id": chunk_id,
                "text": sec["text"],
                "embed_text": embed_text,
                "payload": {
                    "chunk_id": chunk_id,
                    "song_id": song_id,
                    "section_tag": sec["tag"],
                    "section_tag_raw": sec["tag_raw"],
                    "section_index": sec["index"],
                    "text": sec["text"],
                    "embed_text": embed_text,
                    "genre": genre,
                    "language": language,
                    "line_count": len(sec["text"].strip().split("\n")),
                    "char_count": len(sec["text"]),
                    "structure": structure,
                    "granularity": "section",
                    "repeat_count": sec.get("repeat_count", 1),
                },
            })

            # --- couplet-level chunks ---
            couplets = split_couplets(sec["text"])
            for ci, couplet_text in enumerate(couplets):
                ckey = (song_id, sec["tag"], "couplet")
                cseq = coup_counter.get(ckey, 0)
                coup_counter[ckey] = cseq + 1

                c_id = f"lyrics_couplet_{song_id}_{sec['tag']}_{cseq:03d}"
                c_embed = build_embed_text(couplet_text, sec["tag"], genre, augment)

                chunks.append({
                    "chunk_id": c_id,
                    "text": couplet_text,
                    "embed_text": c_embed,
                    "payload": {
                        "chunk_id": c_id,
                        "song_id": song_id,
                        "section_tag": sec["tag"],
                        "section_tag_raw": sec["tag_raw"],
                        "section_index": sec["index"],
                        "couplet_index": ci,
                        "parent_chunk_id": chunk_id,
                        "text": couplet_text,
                        "embed_text": c_embed,
                        "genre": genre,
                        "language": language,
                        "line_count": len(couplet_text.strip().split("\n")),
                        "char_count": len(couplet_text),
                        "structure": structure,
                        "granularity": "couplet",
                        "repeat_count": sec.get("repeat_count", 1),
                    },
                })

    return chunks


def cmd_build(augment: bool = True):
    chunks = build_chunks(augment=augment)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Built {len(chunks)} lyrics chunks -> {OUTPUT_FILE}")
    print_stats(chunks)


def cmd_stats():
    if not OUTPUT_FILE.exists():
        print(f"No chunks file. Run: python {__file__} build")
        return
    with open(OUTPUT_FILE) as f:
        chunks = json.load(f)
    print_stats(chunks)


def print_stats(chunks: list[dict]):
    print(f"\nTotal chunks: {len(chunks)}")

    by_gran = Counter(c["payload"]["granularity"] for c in chunks)
    print(f"\nBy granularity:")
    for g, count in by_gran.most_common():
        print(f"  {g}: {count}")

    for gran in ["section", "couplet"]:
        subset = [c for c in chunks if c["payload"]["granularity"] == gran]
        if not subset:
            continue
        print(f"\n--- {gran} ---")
        by_tag = Counter(c["payload"]["section_tag"] for c in subset)
        print(f"  By section tag:")
        for tag, count in by_tag.most_common():
            print(f"    {tag}: {count}")
        text_lens = [c["payload"]["char_count"] for c in subset]
        print(f"  Length: min={min(text_lens)}, max={max(text_lens)}, avg={sum(text_lens) // len(text_lens)}")

    deduped_chorus = [c for c in chunks
                      if c["payload"]["granularity"] == "section"
                      and c["payload"]["section_tag"] == "chorus"
                      and c["payload"].get("repeat_count", 1) > 1]
    if deduped_chorus:
        total_saved = sum(c["payload"]["repeat_count"] - 1 for c in deduped_chorus)
        print(f"\nChorus dedup: {len(deduped_chorus)} unique chorus with repeats, {total_saved} duplicates removed")

    by_lang = Counter(c["payload"]["language"] for c in chunks)
    print(f"\nBy language: {dict(by_lang)}")
    songs = set(c["payload"]["song_id"] for c in chunks)
    print(f"Unique songs: {len(songs)}")
    genres = set(c["payload"]["genre"] for c in chunks if c["payload"]["genre"])
    print(f"Unique genres: {len(genres)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "build":
        augment = "--augment" in args or "--no-augment" not in args
        cmd_build(augment=augment)
    elif args[0] == "stats":
        cmd_stats()
    else:
        print(f"Usage: python {__file__} [build [--no-augment] | stats]")
