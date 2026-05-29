#!/usr/bin/env python3
"""
lyrics_validator.py — Validate assembled lyrics for structural integrity.

Checks:
  1. Structure completeness (verse + chorus required)
  2. Character limit (3000 chars)
  3. Language consistency
  4. Thematic coherence (cosine similarity between sections)
  5. Self-plagiarism (all sections from same song)

Usage:
    python scripts/lyrics_validator.py "assembled lyrics text"
    python scripts/lyrics_validator.py --sections-json '{"verse": {...}, "chorus": {...}}'
"""

import json
import os
import re
import sys

import numpy as np

LYRICS_CHAR_LIMIT = 3000

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

_model_cache = None


def _get_model():
    global _model_cache
    if _model_cache is None:
        from sentence_transformers import SentenceTransformer
        _model_cache = SentenceTransformer(EMBEDDING_MODEL)
    return _model_cache


def validate_lyrics(lyrics_text: str, sections_meta: list[dict] = None,
                    song_form: list[str] = None) -> dict:
    issues = []

    parsed_sections = re.findall(r"\[([^\]]+)\]\s*\n(.*?)(?=\n\[|\Z)", lyrics_text, re.DOTALL)

    has_verse = any("verse" in tag.lower() for tag, _ in parsed_sections)
    has_chorus = any("chorus" in tag.lower() or "hook" in tag.lower() for tag, _ in parsed_sections)

    form_requires_chorus = True
    if song_form:
        form_requires_chorus = any(t in ("chorus", "hook") for t in song_form)

    if not has_verse:
        issues.append("missing verse section")
    if not has_chorus and form_requires_chorus:
        issues.append("missing chorus/hook section")

    total_chars = len(lyrics_text)
    if total_chars > LYRICS_CHAR_LIMIT:
        issues.append(f"exceeds {LYRICS_CHAR_LIMIT} char limit ({total_chars})")

    NON_LYRIC_TAGS = {"intro", "outro", "interlude", "instrumental"}
    section_texts = []
    for tag, text in parsed_sections:
        text = text.strip()
        if not text:
            continue
        if tag.lower().split()[0] in NON_LYRIC_TAGS:
            continue
        section_texts.append(text)

    coherence = compute_coherence(section_texts) if len(section_texts) >= 2 else 1.0

    if sections_meta:
        song_ids = set(m.get("song_id") for m in sections_meta if m.get("song_id"))
        if len(song_ids) == 1 and len(sections_meta) > 1:
            issues.append("all sections from same song (self-plagiarism)")

        languages = set(m.get("language") for m in sections_meta if m.get("language"))
        if len(languages) > 1 and "mixed" not in languages:
            issues.append(f"mixed languages across sections: {languages}")

    if coherence < 0.2:
        verdict = "FAIL"
    elif coherence < 0.3 or issues:
        verdict = "WARN"
    else:
        verdict = "PASS"

    if not has_verse or not has_chorus:
        verdict = "FAIL"

    return {
        "lyrics_length": total_chars,
        "section_count": len(parsed_sections),
        "has_verse": has_verse,
        "has_chorus": has_chorus,
        "coherence_score": round(coherence, 4),
        "verdict": verdict,
        "issues": issues,
    }


def compute_coherence(section_texts: list[str]) -> float:
    model = _get_model()
    embeddings = model.encode(section_texts)

    sims = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            cos = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
            sims.append(cos)

    return float(np.mean(sims)) if sims else 1.0


def print_validation(result: dict) -> None:
    v = result["verdict"]
    print(f"  [{v}] coherence={result['coherence_score']:.2f} "
          f"| {result['section_count']} sections "
          f"| {result['lyrics_length']} chars")
    if result["issues"]:
        for issue in result["issues"]:
            print(f"         ! {issue}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: lyrics_validator.py 'lyrics text' | --sections-json '{...}'")
        sys.exit(1)

    if sys.argv[1] == "--sections-json":
        sections = json.loads(sys.argv[2])
        section_texts = []
        metas = []
        for tag, payload in sections.items():
            if isinstance(payload, dict):
                section_texts.append(f"[{tag}]\n{payload.get('text', '')}")
                metas.append(payload)
            else:
                section_texts.append(f"[{tag}]\n{payload}")
        lyrics_text = "\n\n".join(section_texts)
        result = validate_lyrics(lyrics_text, sections_meta=metas)
    else:
        lyrics_text = sys.argv[1]
        result = validate_lyrics(lyrics_text)

    print_validation(result)
