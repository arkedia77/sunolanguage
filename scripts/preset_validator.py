#!/usr/bin/env python3
"""
preset_validator.py — Validate generated presets against Suno native vocabulary.

Wraps batch_sp_review.py's native-word checking logic for serendipity presets.
Checks each word in the assembled SP against:
  1. V3 entity vocabulary (sp_entities_v3 + bracket_entities_v3 tokens)
  2. Suno reanalysis corpus (326 clips — actual Suno output)

Returns a validation result with native ratio, novel words, and verdict.

Usage:
    python scripts/preset_validator.py "assembled SP text here"
    python scripts/preset_validator.py --file presets.json
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V3_PATH = ROOT / "data" / "reanalysis_v2"
SP_ENT = V3_PATH / "sp_entities_v3.json"
BR_ENT = V3_PATH / "bracket_entities_v3.json"
MERGED = V3_PATH / "merged_4values.json"

STOP = set("""
a an the and with of in on at into from to that as is are has have be been was
were it its their them this these those there here for by or but no not any each
all some every more most less very quite throughout before after during while
against between through plays play played playing enter enters entering entered
builds building built sustains sustained follows followed following rises rising
doubled layered provides provided adds added layers walks punches plucks moving
delivering maintaining centered lifts alternates alternating creates creating
shifts shifting transitions transitioning rolls rolling drives driving hits
hitting breathes breathing resonates resonating pulses pulsing one two three
four five six seven eight nine ten zero first second third fourth bar bars note
notes beat beats section sections line lines part parts phrase phrases verse
verses chorus choruses bridge intro outro interlude pre hook hooks song songs
track tracks music musical bpm tempo time key major minor korean lyrics minutes
long must sit wide forward close low high mid full downbeat upbeat backbeat
rhythm style tone pattern delivery chord chords sustain register articulation
phrasing male female vocal vocals voice voices harmonies harmony bright warm
soft light dry clean sparse minimal deep rich quiet loud thick thin heavy tight
punchy smooth crisp melodic rhythmic steady c d e f g b ab bb eb db gb cm dm
em fm gm am bm featuring instrumental
""".split())

_v3_cache = None
_corpus_cache = None


def _load_v3_words() -> set[str]:
    global _v3_cache
    if _v3_cache is not None:
        return _v3_cache

    words = set()
    for path in (SP_ENT, BR_ENT):
        if not path.exists():
            continue
        for rec in json.loads(path.read_text()):
            for field in ("entity", "pattern"):
                v = rec.get(field, "") or ""
                if isinstance(v, str):
                    for tok in re.split(r"[^\w\-]+", v.lower()):
                        tok = tok.strip("-")
                        if tok:
                            words.add(tok)
            for field in ("modifiers", "effects", "chords"):
                for item in (rec.get(field) or []):
                    if isinstance(item, str):
                        for tok in re.split(r"[^\w\-]+", item.lower()):
                            tok = tok.strip("-")
                            if tok:
                                words.add(tok)
    _v3_cache = words
    return words


def _load_corpus_text() -> str:
    global _corpus_cache
    if _corpus_cache is not None:
        return _corpus_cache

    if not MERGED.exists():
        _corpus_cache = ""
        return ""

    songs = json.loads(MERGED.read_text())
    texts = []
    for song in songs:
        for clip in (song.get("suno_reanalysis") or []):
            if isinstance(clip, dict):
                texts.append((clip.get("sp") or "") + "\n" + (clip.get("lyrics") or ""))
    _corpus_cache = "\n\n".join(texts).lower()
    return _corpus_cache


def tokenize(sp: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s\-']", " ", sp.lower())
    return [t.strip("'-") for t in cleaned.split() if t.strip("'-")]


def count_in_corpus(word: str, corpus: str) -> int:
    return len(re.findall(r"(?:^|\W)" + re.escape(word.lower()) + r"(?:\W|$)", corpus))


def validate_sp(sp_text: str) -> dict:
    v3_words = _load_v3_words()
    corpus = _load_corpus_text()

    tokens = tokenize(sp_text)
    meaningful = [t for t in tokens if len(t) >= 3 and not t.isdigit() and t not in STOP]

    native = []
    novel = []

    for word in meaningful:
        if word in v3_words:
            native.append(word)
        elif count_in_corpus(word, corpus) > 0:
            native.append(word)
        else:
            novel.append(word)

    total = len(native) + len(novel)
    ratio = len(native) / total if total > 0 else 1.0

    if ratio >= 0.95:
        verdict = "PASS"
    elif ratio >= 0.90:
        verdict = "WARN"
    else:
        verdict = "FAIL"

    return {
        "sp_length": len(sp_text),
        "total_words": len(tokens),
        "meaningful_words": total,
        "native_count": len(native),
        "novel_count": len(novel),
        "native_ratio": round(ratio, 4),
        "verdict": verdict,
        "novel_words": sorted(set(novel)),
    }


def validate_preset_batch(presets: list[dict]) -> list[dict]:
    results = []
    for i, p in enumerate(presets):
        sp = p.get("sp", "")
        result = validate_sp(sp)
        result["preset_index"] = i
        result["drift"] = p.get("drift", None)
        results.append(result)
    return results


def print_validation(result: dict) -> None:
    v = result["verdict"]
    icon = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}[v]
    print(f"  [{icon}] native={result['native_ratio']:.1%} "
          f"({result['native_count']}/{result['meaningful_words']}) "
          f"| SP={result['sp_length']}chars")
    if result["novel_words"]:
        print(f"         novel: {', '.join(result['novel_words'][:10])}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: preset_validator.py 'SP text' | --file presets.json")
        sys.exit(1)

    if sys.argv[1] == "--file":
        with open(sys.argv[2]) as f:
            presets = json.load(f)
        results = validate_preset_batch(presets)
        pass_count = sum(1 for r in results if r["verdict"] == "PASS")
        warn_count = sum(1 for r in results if r["verdict"] == "WARN")
        fail_count = sum(1 for r in results if r["verdict"] == "FAIL")

        print(f"Validated {len(results)} presets:")
        for r in results:
            print_validation(r)

        print(f"\nSummary: {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL")
        avg_ratio = sum(r["native_ratio"] for r in results) / len(results) if results else 0
        print(f"Average native ratio: {avg_ratio:.1%}")
    else:
        sp_text = sys.argv[1]
        result = validate_sp(sp_text)
        print_validation(result)
