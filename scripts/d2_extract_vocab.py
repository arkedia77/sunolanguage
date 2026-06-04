#!/usr/bin/env python3
"""D2: Suno 재분석 SP에서 어휘 추출 → v1 카테고리 매칭 + 신규 후보 surface."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

MERGED = Path(__file__).resolve().parent.parent / "data/reanalysis_v2/merged_4values.json"
V1_DICT = Path(__file__).resolve().parent.parent / "rag/suno_dictionary.json"
OUT_COUNTS = Path(__file__).resolve().parent.parent / "data/reanalysis_v2/d2_category_counts.json"
OUT_NEW = Path(__file__).resolve().parent.parent / "data/reanalysis_v2/d2_new_candidates.json"
OUT_DIFF = Path(__file__).resolve().parent.parent / "data/reanalysis_v2/d2_song_diff.json"

merged = json.loads(MERGED.read_text())
v1 = json.loads(V1_DICT.read_text())

CATS = [
    "instrument_phrases", "technique_patterns", "production_vocab",
    "mood_emotion", "vocal_expressions", "timbre_texture",
    "harmony_vocab", "tempo_rhythm", "dynamics_structure",
]
v1_terms = {c: set(v1.get(c, {}).keys()) for c in CATS}
all_v1 = set()
for terms in v1_terms.values():
    all_v1.update(t.lower() for t in terms)

counts = {c: Counter() for c in CATS}
new_phrase_count = Counter()

INSTR_HEAD = re.compile(
    r"\b([\w\-/]+(?:\s+[\w\-/]+){0,3}\s+"
    r"(guitar|guitars|bass|drums?|drum\s+kit|synth|synths|piano|keys|"
    r"pads?|organ|rhodes|vocals?|vocal|saxophone|sax|trumpet|strings?|"
    r"violin|cello|flute|clarinet|harp|808s?|claps?|hats?|hi-hats?|kick|snare|shaker|tambourine))\b",
    re.IGNORECASE,
)
ADJ_MOOD = re.compile(r"\b(warm|cold|bright|dark|intimate|raw|gentle|aggressive|sparse|dense|gritty|smooth|lush|dry|wet|haunting|dreamy|ethereal|airy|punchy|tight|loose|crisp|resonant|muffled|shimmering|driving|groovy|soulful|hypnotic|melancholic|nostalgic|euphoric|tense|serene|playful)\b", re.IGNORECASE)
PROD_TERMS = re.compile(r"\b(reverb|delay|compression|compressed|saturation|distortion|tape\s+hiss|vinyl\s+crackle|side[- ]chain\w*|ducking|filter|low-?pass|high-?pass|band-?pass|eq|autotune|auto-tune|vocoder|chorus|flanger|phaser|tremolo|gated\s+reverb|plate\s+reverb|spring\s+reverb|room\s+reverb|hall\s+reverb|bit[- ]crush\w*|lo-?fi|wide\s+stereo)\b", re.IGNORECASE)

song_diffs = []

def extract_phrases(text):
    text = text.lower()
    phrases = set()
    for m in INSTR_HEAD.finditer(text):
        phrases.add(m.group(1).strip())
    for m in ADJ_MOOD.finditer(text):
        phrases.add(m.group(1).strip())
    for m in PROD_TERMS.finditer(text):
        phrases.add(m.group(1).strip())
    return phrases

for song in merged:
    leo_sp = (song["leomusic_original"].get("sp") or "").lower()
    for sr in song["suno_reanalysis"]:
        suno_sp = (sr.get("sp") or "").lower()
        if not suno_sp:
            continue
        # v1 매칭
        matched_by_cat = defaultdict(list)
        for cat, terms in v1_terms.items():
            for t in terms:
                tl = t.lower()
                if len(tl) < 3:
                    continue
                if tl in suno_sp:
                    counts[cat][t] += 1
                    matched_by_cat[cat].append(t)
        # 구문 추출
        phrases = extract_phrases(suno_sp)
        new_phrases = [p for p in phrases if p.lower() not in all_v1]
        for p in new_phrases:
            new_phrase_count[p] += 1
        # diff: Suno에만 있는 구/단어
        suno_words = set(re.findall(r"[a-z][a-z\-]+", suno_sp))
        leo_words = set(re.findall(r"[a-z][a-z\-]+", leo_sp))
        sp_new = sorted(suno_words - leo_words)[:60]
        sp_dropped = sorted(leo_words - suno_words)[:60]
        song_diffs.append({
            "song_id": song["song_id"],
            "title": song["title"],
            "suno_uuid": sr.get("uuid"),
            "v1_matched": {k: v for k, v in matched_by_cat.items() if v},
            "candidate_new_phrases": sorted(set(new_phrases)),
            "words_only_in_suno_sp": sp_new,
            "words_only_in_leomusic_sp": sp_dropped,
        })

cat_out = {c: dict(counts[c].most_common()) for c in CATS}
OUT_COUNTS.write_text(json.dumps(cat_out, ensure_ascii=False, indent=2))
OUT_NEW.write_text(json.dumps(dict(new_phrase_count.most_common(500)), ensure_ascii=False, indent=2))
OUT_DIFF.write_text(json.dumps(song_diffs, ensure_ascii=False, indent=2))

total = sum(sum(v.values()) for v in counts.values())
print(f"[D2] v1 매칭 총 히트: {total}")
for c in CATS:
    print(f"  {c}: {sum(counts[c].values())} hits / unique {len(counts[c])}")
print(f"[D2] 신규 후보 구문: {len(new_phrase_count)} unique (top500 저장)")
print(f"[D2] 곡별 diff: {len(song_diffs)}건")
print(f"[D2] out: {OUT_COUNTS.name}, {OUT_NEW.name}, {OUT_DIFF.name}")
