#!/usr/bin/env python3
"""
lyrics_chunk_builder.py — Parse lyrics into hybrid chunks for Qdrant.

Two granularity levels (single collection, granularity field):
  - section:  full [SectionTag] block (existing)
  - couplet:  2-line pairs within each section (new)

Features:
  - Couplet: 2-line sliding pairs, merge lines under 20 chars
  - Section dedup: identical repeated sections collapsed (tag,text), repeat_count metadata
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


def dedup_repeated_sections(sections: list[dict]) -> list[dict]:
    """Collapse identical repeated sections within a song, adding repeat_count.

    ★2026-08-22 일반화 — 종전 이름은 dedup_chorus였고 `tag == "chorus"`만 접었다.
    그 결과 hook·pre_chorus 반복은 안 접혀서 두 가지가 동시에 생겼다:
      ⑴ 같은 곡 안에 텍스트가 완전히 같은 청크 — 품질게이트 exact_duplicate 26건(section)
      ⑵ ★더 큰 쪽 = **비대칭**. chorus 반복 64회는 repeat_count로 기록되는데
         hook은 전부 repeat_count=1이었다(n=103). 「어느 섹션이 얼마나 반복되나」를
         태그별로 비교하면 구조적으로 편향된 답이 나온다.
    키를 (tag, text)로 잡아 태그를 가로지르지 않는다 — chorus↔drop처럼 라벨이 다른 동일
    텍스트는 그 라벨 차이가 정보라서 남긴다(실측 1쌍).
    드라이런 실측: 청크 6,093→6,045(-48) · 중복 초과 70→22 · verse 영향 0.
    잔여 22 = couplet 층에서 서로 다른 chorus 섹션이 2행짜리 일부를 공유하는 건(18+2)
    + chorus↔drop 1쌍(2). 이쪽은 실제로 다른 섹션이라 접지 않는다.
    """
    seen: dict[tuple, int] = {}
    deduped = []
    for sec in sections:
        key = (sec["tag"], sec["text"].strip())
        if key in seen:
            seen[key] += 1
            continue
        seen[key] = 1
        deduped.append({**sec, "_repeat_key": key})
    for sec in deduped:
        sec["repeat_count"] = seen[sec.pop("_repeat_key")]
    return deduped


# 구명 별칭 — 외부 호출자 보호(현재 저장소 내 호출자는 build_chunks 1곳뿐)
dedup_chorus = dedup_repeated_sections


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

        sections = dedup_repeated_sections(sections)
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

    repeated = [c for c in chunks
                if c["payload"]["granularity"] == "section"
                and c["payload"].get("repeat_count", 1) > 1]
    if repeated:
        total_saved = sum(c["payload"]["repeat_count"] - 1 for c in repeated)
        by_tag = Counter(c["payload"]["section_tag"] for c in repeated)
        print(f"\nSection dedup: {len(repeated)} unique sections with repeats, {total_saved} duplicates collapsed")
        print(f"  by tag: {dict(by_tag.most_common())}")

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
