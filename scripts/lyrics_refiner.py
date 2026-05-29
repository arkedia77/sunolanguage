#!/usr/bin/env python3
"""
lyrics_refiner.py — Post-assembly lyrics word refinement.

Takes assembled lyrics (corpus patchwork) and refines words to create
thematic coherence while preserving character count and poetic rhythm.

Principle: 가사는 시 기반 → 뼈대 유지 + 단어 교체 = 새로운 곡

Steps:
  1. Parse lyrics into lines
  2. Build theme vocabulary from corpus
  3. Identify off-theme words (nouns/verbs not in theme vocabulary)
  4. Replace with thematically coherent alternatives (same char count ±1)
  5. Preserve bracket directives, section tags, and structure

Usage:
    python scripts/lyrics_refiner.py "assembled lyrics" --theme=이별
    python scripts/lyrics_refiner.py --file lyrics.txt --theme=사랑
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "data" / "lyrics_chunks.json"

_corpus_cache = None
_theme_vocab_cache = {}


def _load_corpus() -> list[dict]:
    global _corpus_cache
    if _corpus_cache is None:
        with open(CHUNKS_FILE) as f:
            _corpus_cache = json.load(f)
    return _corpus_cache


def build_theme_vocabulary(theme: str) -> dict[str, list[str]]:
    if theme in _theme_vocab_cache:
        return _theme_vocab_cache[theme]

    from lyrics_themes import get_theme

    theme_def = get_theme(theme)
    if not theme_def:
        return {"nouns": [], "verbs": [], "all_words": set()}

    keywords = set(theme_def["keywords_kr"])
    chunks = _load_corpus()

    theme_chunks = []
    for c in chunks:
        text = c["payload"].get("text", "")
        if any(kw in text for kw in keywords):
            theme_chunks.append(text)

    all_words = []
    for text in theme_chunks:
        words = re.findall(r"[가-힣]{2,}", text)
        all_words.extend(words)

    word_freq = Counter(all_words)

    by_length = defaultdict(list)
    for word, freq in word_freq.most_common(500):
        by_length[len(word)].append((word, freq))

    result = {
        "by_length": dict(by_length),
        "all_words": set(word_freq.keys()),
        "top_words": set(w for w, _ in word_freq.most_common(200)),
        "keywords": keywords,
    }
    _theme_vocab_cache[theme] = result
    return result


def _is_content_word(word: str) -> bool:
    STOP_SUFFIXES = {"거야", "있어", "없어", "같은", "이게", "그게", "그냥", "근데",
                     "내가", "나는", "나를", "네가", "너를", "우리", "있다", "없는",
                     "있는", "했어", "됐어", "건지", "않아", "않는", "아닌", "되는",
                     "해도", "해서", "하고", "에서", "까지", "처럼", "보다", "위에"}
    return word not in STOP_SUFFIXES and len(word) >= 2


def _find_replacement(word: str, theme_vocab: dict, used: set) -> str | None:
    wlen = len(word)
    candidates = []

    for target_len in [wlen, wlen - 1, wlen + 1]:
        if target_len in theme_vocab["by_length"]:
            for cand, freq in theme_vocab["by_length"][target_len]:
                if cand != word and cand not in used and cand in theme_vocab["top_words"]:
                    candidates.append((cand, freq, abs(target_len - wlen)))

    candidates.sort(key=lambda x: (x[2], -x[1]))
    return candidates[0][0] if candidates else None


def refine_lyrics(lyrics: str, theme: str, max_replacements_per_section: int = 3) -> str:
    theme_vocab = build_theme_vocabulary(theme)
    if not theme_vocab.get("all_words"):
        return lyrics

    sections = re.split(r"(\[[^\]]+\]\n)", lyrics)
    refined_parts = []
    used_replacements = set()

    for part in sections:
        if part.startswith("[") and part.strip().endswith("]"):
            refined_parts.append(part)
            continue

        if not part.strip():
            refined_parts.append(part)
            continue

        lines = part.split("\n")
        refined_lines = []
        replacements_in_section = 0

        for line in lines:
            if not line.strip():
                refined_lines.append(line)
                continue

            if line.strip().startswith("[") and line.strip().endswith("]"):
                refined_lines.append(line)
                continue

            if line.strip().startswith("(") and line.strip().endswith(")"):
                refined_lines.append(line)
                continue

            words = re.findall(r"[가-힣]{2,}", line)
            content_words = [w for w in words if _is_content_word(w)]

            off_theme = [w for w in content_words if w not in theme_vocab["all_words"]]

            new_line = line
            for word in off_theme:
                if replacements_in_section >= max_replacements_per_section:
                    break
                replacement = _find_replacement(word, theme_vocab, used_replacements)
                if replacement:
                    new_line = new_line.replace(word, replacement, 1)
                    used_replacements.add(replacement)
                    replacements_in_section += 1

            refined_lines.append(new_line)

        refined_parts.append("\n".join(refined_lines))

    return "".join(refined_parts)


def compare_lyrics(original: str, refined: str) -> dict:
    orig_lines = [l for l in original.split("\n") if l.strip() and not l.startswith("[")]
    ref_lines = [l for l in refined.split("\n") if l.strip() and not l.startswith("[")]

    changed = 0
    total = max(len(orig_lines), 1)
    for o, r in zip(orig_lines, ref_lines):
        if o != r:
            changed += 1

    return {
        "original_chars": len(original),
        "refined_chars": len(refined),
        "char_diff": len(refined) - len(original),
        "lines_changed": changed,
        "total_lines": total,
        "change_rate": changed / total,
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    theme = "이별"
    lyrics_text = ""
    show_diff = False

    for a in args:
        if a.startswith("--theme="):
            theme = a.split("=")[1]
        elif a.startswith("--file="):
            with open(a.split("=")[1]) as f:
                lyrics_text = f.read()
        elif a == "--diff":
            show_diff = True
        elif not a.startswith("--"):
            lyrics_text = a

    if not lyrics_text:
        print("Need lyrics text or --file")
        sys.exit(1)

    print(f"Refining with theme: {theme}")
    print()

    refined = refine_lyrics(lyrics_text, theme=theme)
    stats = compare_lyrics(lyrics_text, refined)

    if show_diff:
        orig_lines = lyrics_text.split("\n")
        ref_lines = refined.split("\n")
        for o, r in zip(orig_lines, ref_lines):
            if o != r:
                print(f"  - {o}")
                print(f"  + {r}")
            else:
                print(f"    {o}")
    else:
        print(refined)

    print(f"\n--- Stats ---")
    print(f"  Chars: {stats['original_chars']} → {stats['refined_chars']} ({stats['char_diff']:+d})")
    print(f"  Lines changed: {stats['lines_changed']}/{stats['total_lines']} ({stats['change_rate']:.0%})")
