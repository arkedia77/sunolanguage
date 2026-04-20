#!/usr/bin/env python3
"""
Suno 네이티브 어휘 사전 빌더

665트랙 파싱 데이터에서 Suno가 실제로 사용하는 어휘를 추출하여
SP 작성에 바로 쓸 수 있는 사전을 생성.

출력:
  - rag/suno_dictionary.json — 전체 어휘 사전 (기계용)
  - docs/suno_dictionary_report.md — 읽기 쉬운 보고서 (사람용)
"""

import json
import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARSED_DIR = PROJECT_ROOT / "data" / "parsed"
RAG_DIR = PROJECT_ROOT / "rag"
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def load_all():
    tracks = json.load(open(PARSED_DIR / "parsed_tracks.json"))
    genre_analysis = json.load(open(PARSED_DIR / "genre_analysis_normalized.json"))
    ac_mapped = json.load(open(PARSED_DIR / "audiocards_mapped.json"))
    return tracks, genre_analysis, ac_mapped


def extract_instrument_phrases(tracks):
    """트랙별 raw_tags에서 악기+수식어 구문 추출."""
    # "a [adjective] [instrument] [playing/performing] [technique]" 패턴
    patterns = [
        # "distorted electric guitar playing palm-muted power chords"
        re.compile(
            r'(?:a\s+|the\s+)?'
            r'((?:[\w-]+\s+){0,3})'  # 수식어 0~3개
            r'(piano|guitar|bass(?:\s+guitar)?|drums?|drum\s+kit|violin|viola|cello|'
            r'flute|oboe|clarinet|trumpet|trombone|saxophone|harp|organ|'
            r'synthesizer|synth(?:\s+(?:pad|lead|bass))?|808|'
            r'hi-hat|snare(?:\s+drum)?|kick(?:\s+drum)?|cymbal|timpani|'
            r'choir|orchestra|strings?|brass|woodwinds?|percussion|'
            r'sitar|tabla|banjo|mandolin|ukulele|marimba|vibraphone|'
            r'Rhodes|Wurlitzer|Moog|mellotron|vocoder|'
            r'horn\s+section|string\s+section)'
            r'\s+'
            r'((?:playing|performing|providing|executing|delivering|featuring|utilizing|'
            r'with|using|in\s+a)\s+'
            r'[\w\s,\-]{5,80})',
            re.IGNORECASE
        ),
        # "[instrument] provides/plays/performs ..."
        re.compile(
            r'(?:the\s+|a\s+)?'
            r'((?:[\w-]+\s+){0,3})'
            r'(piano|guitar|bass(?:\s+guitar)?|drums?|drum\s+kit|violin|viola|cello|'
            r'flute|oboe|clarinet|trumpet|trombone|saxophone|harp|organ|'
            r'synthesizer|synth(?:\s+(?:pad|lead|bass))?|808|'
            r'hi-hat|snare(?:\s+drum)?|kick(?:\s+drum)?|cymbal|'
            r'choir|orchestra|strings?|brass|woodwinds?|percussion|'
            r'sitar|tabla|banjo|mandolin|ukulele|marimba|vibraphone|'
            r'Rhodes|Wurlitzer|Moog|mellotron|vocoder|'
            r'horn\s+section|string\s+section)'
            r'\s+'
            r'((?:provides?|plays?|performs?|creates?|adds?|delivers?|maintains?|follows?|drives?)\s+'
            r'[\w\s,\-]{5,80})',
            re.IGNORECASE
        ),
    ]

    phrases = defaultdict(lambda: {"count": 0, "examples": []})
    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        for pat in patterns:
            for m in pat.finditer(tags):
                modifier = m.group(1).strip().lower()
                instrument = m.group(2).strip().lower()
                action = m.group(3).strip()
                # 너무 짧거나 긴 것 필터
                if len(action) < 10 or len(action) > 120:
                    continue
                key = f"{modifier + ' ' if modifier else ''}{instrument}"
                key = re.sub(r'\s+', ' ', key).strip()
                phrases[key]["count"] += 1
                if len(phrases[key]["examples"]) < 3:
                    # 전체 구문 저장
                    full = f"{key} {action}"
                    full = re.sub(r'\s+', ' ', full).strip()
                    phrases[key]["examples"].append({
                        "phrase": full,
                        "title": track.get("title", "?"),
                        "genre": track.get("genre_label", track.get("source", "?")),
                    })
    return dict(sorted(phrases.items(), key=lambda x: -x[1]["count"]))


def extract_technique_patterns(tracks):
    """주법/연주 기법 구문 추출 — Suno가 실제 쓰는 표현."""
    tech_re = re.compile(
        r'((?:[\w-]+\s+){0,2}'
        r'(?:arpeggiat\w+|staccato|legato|tremolo|vibrato|glissando|pizzicato|'
        r'fingerstyle|fingerpick\w+|palm[- ]mut\w+|sweep\s+pick\w+|tapping|'
        r'slap(?:ping)?|pop(?:ping)?|strumm\w+|hammer[- ]on|pull[- ]off|'
        r'syncopat\w+|walking\s+bass\w*|power\s+chords?|block\s+chords?|'
        r'four-on-the-floor|backbeat|triplet|shuffle|swing|'
        r'double[- ]stroke|roll|trill|bend|slide|'
        r'polyrhythm\w*|cross[- ]rhythm|blast\s+beat|'
        r'sidechain\w*|compression|gated\s+reverb|'
        r'call[- ]and[- ]response|melisma\w*|portamento|'
        r'ostinato|pedal\s+(?:note|point|tone))'
        r'(?:\s+[\w\s,\-]{3,40})?)',
        re.IGNORECASE
    )

    techniques = defaultdict(lambda: {"count": 0, "contexts": []})
    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        for m in tech_re.finditer(tags):
            phrase = m.group(0).strip()
            # 핵심 기법명 추출
            key = re.sub(r'\s+', ' ', phrase).strip().lower()
            if len(key) < 4:
                continue
            # 너무 긴 것 트리밍
            if len(key) > 60:
                key = key[:60].rsplit(' ', 1)[0]
            techniques[key]["count"] += 1
            if len(techniques[key]["contexts"]) < 2:
                techniques[key]["contexts"].append({
                    "title": track.get("title", "?"),
                    "genre": track.get("genre_label", track.get("source", "?")),
                })
    return dict(sorted(techniques.items(), key=lambda x: -x[1]["count"]))


def extract_production_vocab(tracks):
    """프로덕션/사운드 디자인 어휘 추출."""
    prod_re = re.compile(
        r'((?:heavy|light|subtle|natural|significant|prominent|thick|thin|wide|narrow|'
        r'deep|high|low|warm|bright|dark|crisp|clean|dry|wet)\s+)?'
        r'((?:hall|plate|room|spring|cathedral|tape|analog|digital|slapback)[- ]?'
        r'(?:reverb|delay|echo|saturation)|'
        r'vinyl\s+(?:crackle|noise|hiss)|tape\s+(?:saturation|hiss)|'
        r'(?:high|low|band)[- ]pass\s+filter|'
        r'sidechain(?:ed)?\s+compression|gated\s+reverb|'
        r'stereo\s+(?:field|width|spread|imaging)|'
        r'(?:wide|narrow)\s+stereo|'
        r'bit[- ]?crush(?:ed|ing)?|'
        r'(?:lo-?fi|atmospheric|ambient)\s+(?:texture|production|aesthetic|quality)|'
        r'(?:clean|warm|bright|polished|raw)\s+(?:mix|production|sound|tone))',
        re.IGNORECASE
    )

    production = defaultdict(lambda: {"count": 0, "genres": set()})
    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        for m in prod_re.finditer(tags):
            phrase = m.group(0).strip().lower()
            phrase = re.sub(r'\s+', ' ', phrase)
            production[phrase]["count"] += 1
            genre = track.get("genre_label", track.get("source", "?"))
            production[phrase]["genres"].add(genre)

    # set → list
    result = {}
    for k, v in sorted(production.items(), key=lambda x: -x[1]["count"]):
        result[k] = {"count": v["count"], "genres": sorted(v["genres"])}
    return result


def build_genre_vocabulary_map(genre_analysis):
    """장르별 핵심 어휘 맵 — SP 작성 시 장르 선택하면 바로 쓸 수 있는 표현 목록."""
    genre_map = {}
    for genre, data in sorted(genre_analysis.items()):
        fields = data.get("fields", {})
        if data.get("total_unique_terms", 0) < 5:
            continue
        genre_map[genre] = {
            "instruments": fields.get("ac_instruments", []),
            "techniques": fields.get("ac_techniques", []),
            "production": fields.get("ac_production", []),
            "mood": fields.get("ac_mood_emotion", []),
            "timbre": fields.get("ac_timbre", []),
            "tempo_structure": fields.get("ac_temporal_structure", []),
        }
    return genre_map


def extract_key_harmony(tracks):
    """조성/화성 어휘 추출 — Suno가 인식하는 키와 화성 표현."""
    key_re = re.compile(
        r'((?:key\s+of\s+)?[A-G][b#]?\s*(?:Major|Minor|major|minor))',
        re.IGNORECASE
    )
    harmony_re = re.compile(
        r'(modal|dorian|mixolydian|lydian|phrygian|aeolian|locrian|'
        r'pentatonic|blues\s+scale|chromatic|whole[- ]tone|'
        r'diminished|augmented|suspended|'
        r'seventh|ninth|eleventh|thirteenth|'
        r'ii-V-I|I-IV-V|twelve[- ]bar|turnaround|'
        r'tonic\s+and\s+dominant|tonal\s+progression|'
        r'(?:plagal|authentic|deceptive|half)\s+cadence|'
        r'drone|pedal\s+point|ostinato|'
        r'chord\s+progression|harmonic\s+(?:structure|support|movement)|'
        r'key\s+change|modulation|resolution)',
        re.IGNORECASE
    )

    keys = defaultdict(lambda: {"count": 0, "genres": set()})
    harmony = defaultdict(lambda: {"count": 0, "genres": set()})

    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        genre = track.get("genre_label", track.get("source", "?"))
        for m in key_re.finditer(tags):
            k = m.group(1).strip()
            keys[k]["count"] += 1
            keys[k]["genres"].add(genre)
        for m in harmony_re.finditer(tags):
            h = m.group(0).strip().lower()
            harmony[h]["count"] += 1
            harmony[h]["genres"].add(genre)

    result_keys = {k: {"count": v["count"], "genres": sorted(v["genres"])}
                   for k, v in sorted(keys.items(), key=lambda x: -x[1]["count"])}
    result_harmony = {k: {"count": v["count"], "genres": sorted(v["genres"])}
                      for k, v in sorted(harmony.items(), key=lambda x: -x[1]["count"])}
    return result_keys, result_harmony


def extract_mood_emotion(tracks):
    """무드/감정 어휘 추출."""
    mood_re = re.compile(
        r'\b(melanchol(?:ic|y)|euphori[ca]|energetic|calm|serene|'
        r'aggressive|intense|dark|bright|warm|cold|'
        r'dreamy|ethereal|nostalgic|hopeful|triumphant|'
        r'haunting|eerie|mysterious|playful|joyful|'
        r'somber|mournful|passionate|tender|gentle|'
        r'epic|majestic|powerful|anthemic|uplifting|'
        r'groovy|funky|chill|relaxed|mellow|'
        r'hypnotic|meditative|contemplative|introspective|'
        r'raw|visceral|gritty|smooth|lush|sparse|'
        r'dramatic|cinematic|suspenseful|ominous|foreboding|'
        r'bittersweet|wistful|longing|yearning|'
        r'celebratory|festive|exuberant|jubilant|'
        r'subdued|restrained|understated|intimate|'
        r'chaotic|frenzied|turbulent|volatile|'
        r'soothing|tranquil|peaceful|placid)\b',
        re.IGNORECASE
    )

    moods = defaultdict(lambda: {"count": 0, "genres": set()})
    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        genre = track.get("genre_label", track.get("source", "?"))
        for m in mood_re.finditer(tags):
            mood = m.group(0).strip().lower()
            moods[mood]["count"] += 1
            moods[mood]["genres"].add(genre)

    return {k: {"count": v["count"], "genres": sorted(v["genres"])}
            for k, v in sorted(moods.items(), key=lambda x: -x[1]["count"])}


def extract_tempo_rhythm(tracks):
    """템포/리듬 어휘 추출."""
    tempo_re = re.compile(
        r'(\d+\s*BPM|'
        r'[234678]/[2348]\s*(?:time)?|'
        r'(?:slow|mid|up)[- ]?tempo|'
        r'moderato|allegro|andante|adagio|presto|largo|vivace|'
        r'stately|steady|driving|laid[- ]?back|'
        r'syncopat\w+|swing|shuffle|groove|backbeat|'
        r'four[- ]on[- ]the[- ]floor|off[- ]?beat|'
        r'triplet|dotted|straight|'
        r'half[- ]time|double[- ]time|'
        r'polymetr\w+|odd\s+(?:time|meter)|mixed\s+meter|'
        r'ritardando|rallentando|accelerando|fermata|rubato)',
        re.IGNORECASE
    )

    rhythms = defaultdict(lambda: {"count": 0, "genres": set()})
    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        genre = track.get("genre_label", track.get("source", "?"))
        for m in tempo_re.finditer(tags):
            r = m.group(0).strip().lower()
            rhythms[r]["count"] += 1
            rhythms[r]["genres"].add(genre)

    return {k: {"count": v["count"], "genres": sorted(v["genres"])}
            for k, v in sorted(rhythms.items(), key=lambda x: -x[1]["count"])}


def extract_dynamics_structure(tracks):
    """다이나믹스/곡 구조 어휘 추출."""
    dyn_re = re.compile(
        r'\b(forte|piano|mezzo[- ]?forte|mezzo[- ]?piano|'
        r'fortissimo|pianissimo|sforzando|'
        r'crescendo|decrescendo|diminuendo|'
        r'swell|build(?:up)?|drop|breakdown|riser|'
        r'intro|verse|pre[- ]?chorus|chorus|bridge|'
        r'interlude|outro|hook|solo|coda|'
        r'A[- ]?section|B[- ]?section|head|vamp|'
        r'strophic|through[- ]composed|rondo|AABA|ABAB|'
        r'fade\s+(?:in|out)|cut|silence|'
        r'layering|textural\s+shift|'
        r'dynamic\s+range|dynamic\s+contrast|'
        r'sparse\s+to\s+dense|builds?\s+in\s+intensity)\b',
        re.IGNORECASE
    )

    dynamics = defaultdict(lambda: {"count": 0, "genres": set()})
    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        genre = track.get("genre_label", track.get("source", "?"))
        for m in dyn_re.finditer(tags):
            d = m.group(0).strip().lower()
            dynamics[d]["count"] += 1
            dynamics[d]["genres"].add(genre)

    return {k: {"count": v["count"], "genres": sorted(v["genres"])}
            for k, v in sorted(dynamics.items(), key=lambda x: -x[1]["count"])}


def extract_timbre_texture(tracks):
    """음색/텍스처 어휘 추출."""
    timbre_re = re.compile(
        r'\b(bright|dark|warm|cold|thin|thick|rich|full|hollow|'
        r'metallic|woody|glassy|breathy|airy|nasal|'
        r'crisp|muddy|punchy|boomy|tinny|shimmering|'
        r'fuzzy|distorted|overdriven|clean|saturated|'
        r'resonant|muffled|sharp|soft|harsh|smooth|'
        r'bell[- ]?like|silky|gritty|raspy|husky|'
        r'crystalline|ethereal|lush|dense|sparse|'
        r'brittle|crunchy|sizzling|rumbling|thunderous)\b',
        re.IGNORECASE
    )

    timbres = defaultdict(lambda: {"count": 0, "genres": set()})
    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        genre = track.get("genre_label", track.get("source", "?"))
        for m in timbre_re.finditer(tags):
            t = m.group(0).strip().lower()
            timbres[t]["count"] += 1
            timbres[t]["genres"].add(genre)

    return {k: {"count": v["count"], "genres": sorted(v["genres"])}
            for k, v in sorted(timbres.items(), key=lambda x: -x[1]["count"])}


def extract_vocal_expressions(tracks):
    """보컬/보이싱 어휘 추출."""
    vocal_re = re.compile(
        r'((?:male|female)\s+(?:tenor|soprano|alto|bass|vocal)|'
        r'(?:operatic|falsetto|belt(?:ing)?|breathy|raspy|gritty|smooth|silky|airy)\s+vocal|'
        r'formal\s+and\s+(?:operatic|reverent|liturgical)|'
        r'clear\s+diction|controlled\s+vibrato|classical\s+vibrato|'
        r'wide\s+vibrato|minimal\s+vibrato|heavy\s+vibrato|'
        r'head\s+voice|chest\s+voice|mixed\s+voice|'
        r'vocal\s+(?:chop|sample|fry|run|harmony|layering|stack)|'
        r'backing\s+vocal|harmony\s+vocal|layered\s+vocal|'
        r'auto[- ]?tune|pitch\s+correction|'
        r'rap|spoken\s+word|chant|'
        r'melismatic\s+\w+|vocal\s+(?:delivery|style|technique|performance)|'
        r'(?:nasal|throaty|gritty|smooth|breathy|airy|husky)\s+(?:delivery|tone|quality)|'
        r'a\s+cappella|unison\s+(?:vocal|singing)|'
        r'four-part\s+harmony|homophonic\s+(?:harmony|texture)|'
        r'SATB|soprano|alto|tenor|baritone|'
        r'vibrato|legato\s+phrasing|sustained\s+phrasing|'
        r'precise\s+(?:diction|articulation|consonant)|'
        r'elongated\s+vowels)',
        re.IGNORECASE
    )

    vocals = defaultdict(lambda: {"count": 0, "genres": set()})
    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        genre = track.get("genre_label", track.get("source", "?"))
        for m in vocal_re.finditer(tags):
            v = m.group(0).strip().lower()
            v = re.sub(r'\s+', ' ', v)
            vocals[v]["count"] += 1
            vocals[v]["genres"].add(genre)

    return {k: {"count": v["count"], "genres": sorted(v["genres"])}
            for k, v in sorted(vocals.items(), key=lambda x: -x[1]["count"])}


def extract_descriptor_combos(tracks):
    """Suno가 자주 쓰는 형용사+명사 조합 추출."""
    combo_re = re.compile(
        r'\b([\w-]+)\s+'
        r'(guitar|bass|piano|drums?|snare|kick|hi-hat|cymbal|'
        r'synth|pad|lead|strings?|vocal|voice|choir|'
        r'reverb|delay|tone|sound|groove|beat|rhythm|'
        r'melody|chord|progression|pattern|texture)\b',
        re.IGNORECASE
    )

    combos = defaultdict(int)
    for track in tracks:
        tags = track.get("raw_tags", "")
        if not tags:
            continue
        for m in combo_re.finditer(tags):
            adj = m.group(1).lower()
            noun = m.group(2).lower()
            # 관사/전치사 필터
            if adj in ('a', 'an', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'of', 'with', 'for', 'is', 'are'):
                continue
            combos[f"{adj} {noun}"] += 1

    return dict(sorted(combos.items(), key=lambda x: -x[1])[:200])


def generate_report(dictionary, tracks_count, genre_count):
    """읽기 쉬운 마크다운 보고서 생성."""
    lines = [
        "# Suno 네이티브 어휘 사전",
        f"\n**생성일**: 2026-04-12",
        f"**데이터**: {tracks_count}트랙 / {genre_count}장르",
        f"**목적**: Suno가 실제로 사용하는 어휘와 표현 패턴 → SP 작성 참고",
        "",
        "---",
        "",
        "## 1. 악기별 Suno 표현 (상위 30)",
        "",
        "Suno가 악기를 묘사할 때 실제로 쓰는 구문입니다.",
        "",
    ]

    inst_phrases = dictionary.get("instrument_phrases", {})
    for i, (inst, info) in enumerate(list(inst_phrases.items())[:30]):
        lines.append(f"### {i+1}. {inst} (x{info['count']})")
        for ex in info.get("examples", []):
            lines.append(f"- *\"{ex['phrase']}\"* — {ex['title']} ({ex['genre']})")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 2. 주법/연주 기법 (상위 40)",
        "",
        "| 표현 | 빈도 | 장르 예시 |",
        "|------|------|----------|",
    ])
    tech = dictionary.get("technique_patterns", {})
    for phrase, info in list(tech.items())[:40]:
        genres = ", ".join(c["genre"] for c in info.get("contexts", []))
        lines.append(f"| {phrase} | x{info['count']} | {genres} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. 프로덕션/사운드 (상위 30)",
        "",
        "| 표현 | 빈도 | 장르 |",
        "|------|------|------|",
    ])
    prod = dictionary.get("production_vocab", {})
    for phrase, info in list(prod.items())[:30]:
        genres = ", ".join(info.get("genres", [])[:3])
        lines.append(f"| {phrase} | x{info['count']} | {genres} |")

    # 조성/화성
    lines.extend([
        "",
        "---",
        "",
        "## 4. 조성 (Key Signatures)",
        "",
        "Suno가 인식하고 명시하는 조성입니다. SP에서 `in the key of X`로 지정 가능.",
        "",
        "| 조성 | 빈도 | 장르 |",
        "|------|------|------|",
    ])
    key_sigs = dictionary.get("key_signatures", {})
    for key, info in list(key_sigs.items())[:25]:
        genres = ", ".join(info.get("genres", [])[:3])
        lines.append(f"| {key} | x{info['count']} | {genres} |")

    lines.extend([
        "",
        "### 화성 어휘",
        "",
        "| 표현 | 빈도 | 장르 |",
        "|------|------|------|",
    ])
    harmony = dictionary.get("harmony_vocab", {})
    for term, info in list(harmony.items())[:20]:
        genres = ", ".join(info.get("genres", [])[:3])
        lines.append(f"| {term} | x{info['count']} | {genres} |")

    # 무드/감정
    lines.extend([
        "",
        "---",
        "",
        "## 5. 무드/감정",
        "",
        "| 표현 | 빈도 | 장르 |",
        "|------|------|------|",
    ])
    mood = dictionary.get("mood_emotion", {})
    for term, info in list(mood.items())[:30]:
        genres = ", ".join(info.get("genres", [])[:3])
        lines.append(f"| {term} | x{info['count']} | {genres} |")

    # 템포/리듬
    lines.extend([
        "",
        "---",
        "",
        "## 6. 템포/리듬",
        "",
        "| 표현 | 빈도 | 장르 |",
        "|------|------|------|",
    ])
    tempo = dictionary.get("tempo_rhythm", {})
    for term, info in list(tempo.items())[:30]:
        genres = ", ".join(info.get("genres", [])[:3])
        lines.append(f"| {term} | x{info['count']} | {genres} |")

    # 다이나믹스/구조
    lines.extend([
        "",
        "---",
        "",
        "## 7. 다이나믹스/곡 구조",
        "",
        "| 표현 | 빈도 | 장르 |",
        "|------|------|------|",
    ])
    dynamics = dictionary.get("dynamics_structure", {})
    for term, info in list(dynamics.items())[:30]:
        genres = ", ".join(info.get("genres", [])[:3])
        lines.append(f"| {term} | x{info['count']} | {genres} |")

    # 음색/텍스처
    lines.extend([
        "",
        "---",
        "",
        "## 8. 음색/텍스처",
        "",
        "| 표현 | 빈도 | 장르 |",
        "|------|------|------|",
    ])
    timbre = dictionary.get("timbre_texture", {})
    for term, info in list(timbre.items())[:30]:
        genres = ", ".join(info.get("genres", [])[:3])
        lines.append(f"| {term} | x{info['count']} | {genres} |")

    # 보컬
    lines.extend([
        "",
        "---",
        "",
        "## 9. 보컬/보이싱 ⚠️ 데이터 부족",
        "",
        "스템 기반 수집 특성상 보컬 데이터가 제한적입니다. 전곡 업로드로 보강 필요.",
        "",
        "| 표현 | 빈도 | 장르 |",
        "|------|------|------|",
    ])
    vocal = dictionary.get("vocal_expressions", {})
    for term, info in list(vocal.items())[:30]:
        genres = ", ".join(info.get("genres", [])[:3])
        lines.append(f"| {term} | x{info['count']} | {genres} |")

    # 형용사+명사 조합
    lines.extend([
        "",
        "---",
        "",
        "## 10. 자주 쓰는 형용사+명사 조합 (상위 50)",
        "",
        "SP에서 바로 쓸 수 있는 Suno 친화적 표현입니다.",
        "",
        "| 조합 | 빈도 |",
        "|------|------|",
    ])
    combos = dictionary.get("descriptor_combos", {})
    for combo, count in list(combos.items())[:50]:
        lines.append(f"| {combo} | x{count} |")

    # 커버리지 요약
    stats = dictionary.get("stats", {})
    lines.extend([
        "",
        "---",
        "",
        "## 11. 커버리지 요약 — 부족한 영역",
        "",
        "| 카테고리 | 추출 수 | 평가 |",
        "|---------|--------|------|",
        f"| 악기 표현 | {stats.get('total_instrument_phrases', 0)} | ✅ 충분 |",
        f"| 주법 패턴 | {stats.get('total_technique_patterns', 0)} | ✅ 충분 |",
        f"| 프로덕션 | {stats.get('total_production_terms', 0)} | ✅ 양호 |",
        f"| 조성 | {stats.get('total_key_signatures', 0)} | ✅ Suno가 인식함 확인 |",
        f"| 화성 | {stats.get('total_harmony_terms', 0)} | {'⚠️ 보강 필요' if stats.get('total_harmony_terms', 0) < 20 else '✅ 양호'} |",
        f"| 무드/감정 | {stats.get('total_mood_terms', 0)} | {'⚠️ 보강 필요' if stats.get('total_mood_terms', 0) < 30 else '✅ 양호'} |",
        f"| 템포/리듬 | {stats.get('total_tempo_rhythm', 0)} | ✅ 양호 |",
        f"| 다이나믹스/구조 | {stats.get('total_dynamics_structure', 0)} | {'⚠️ 보강 필요' if stats.get('total_dynamics_structure', 0) < 20 else '✅ 양호'} |",
        f"| 음색 | {stats.get('total_timbre_terms', 0)} | ✅ 양호 |",
        f"| 보컬 | {stats.get('total_vocal_terms', 0)} | {'❌ 매우 부족' if stats.get('total_vocal_terms', 0) < 30 else '⚠️ 보강 필요'} |",
        f"| 장르 | {stats.get('total_genres_covered', 0)} | ⚠️ 226개 중 일부만 커버 |",
        "",
        "### 보강 계획",
        "1. **보컬**: 전곡 업로드(스템X) → 보컬 디렉션 어휘 수집",
        "2. **무드**: suno_moods 데이터 외 추가 감성 표현 수집",
        "3. **장르**: 미커버 장르 추가 수집 (현재 62/226)",
        "4. **화성**: 코드 진행, 모드 등 고급 화성 어휘 보강",
    ])

    lines.extend([
        "",
        "---",
        "",
        "## 12. 장르별 핵심 어휘 (상위 15 장르)",
        "",
    ])
    genre_map = dictionary.get("genre_vocabulary_map", {})
    ranked_genres = sorted(genre_map.items(),
                          key=lambda x: sum(len(v) for v in x[1].values()),
                          reverse=True)
    for genre, fields in ranked_genres[:15]:
        total = sum(len(v) for v in fields.values())
        lines.append(f"### {genre} ({total}개 표현)")
        for field_name, field_label in [
            ("instruments", "악기"), ("techniques", "주법"),
            ("production", "프로덕션"), ("mood", "무드"),
            ("timbre", "음색")
        ]:
            terms = fields.get(field_name, [])
            if terms:
                lines.append(f"- **{field_label}**: {', '.join(terms[:10])}")
        lines.append("")

    return "\n".join(lines)


def main():
    tracks, genre_analysis, ac_mapped = load_all()
    print(f"Loaded {len(tracks)} tracks, {len(genre_analysis)} genres")

    print("1/10 악기별 구문 추출...")
    inst_phrases = extract_instrument_phrases(tracks)
    print(f"  → {len(inst_phrases)}개 악기 표현")

    print("2/10 주법/기법 패턴 추출...")
    tech_patterns = extract_technique_patterns(tracks)
    print(f"  → {len(tech_patterns)}개 주법 표현")

    print("3/10 프로덕션 어휘 추출...")
    prod_vocab = extract_production_vocab(tracks)
    print(f"  → {len(prod_vocab)}개 프로덕션 표현")

    print("4/10 장르별 어휘 맵 생성...")
    genre_map = build_genre_vocabulary_map(genre_analysis)
    print(f"  → {len(genre_map)}개 장르 커버")

    print("5/10 형용사+명사 조합 추출...")
    combos = extract_descriptor_combos(tracks)
    print(f"  → {len(combos)}개 조합")

    print("6/10 조성/화성 추출...")
    key_sigs, harmony_vocab = extract_key_harmony(tracks)
    print(f"  → 조성 {len(key_sigs)}개, 화성 {len(harmony_vocab)}개")

    print("7/10 무드/감정 추출...")
    mood_vocab = extract_mood_emotion(tracks)
    print(f"  → {len(mood_vocab)}개 무드 표현")

    print("8/10 템포/리듬 추출...")
    tempo_vocab = extract_tempo_rhythm(tracks)
    print(f"  → {len(tempo_vocab)}개 템포/리듬 표현")

    print("9/10 다이나믹스/구조 추출...")
    dynamics_vocab = extract_dynamics_structure(tracks)
    print(f"  → {len(dynamics_vocab)}개 다이나믹스/구조 표현")

    print("10/10 음색/텍스처 + 보컬 추출...")
    timbre_vocab = extract_timbre_texture(tracks)
    vocal_vocab = extract_vocal_expressions(tracks)
    print(f"  → 음색 {len(timbre_vocab)}개, 보컬 {len(vocal_vocab)}개")

    # 사전 조립
    dictionary = {
        "version": "1.1",
        "created_at": "2026-04-12",
        "tracks_count": len(tracks),
        "genres_count": len(genre_analysis),
        "instrument_phrases": inst_phrases,
        "technique_patterns": tech_patterns,
        "production_vocab": prod_vocab,
        "key_signatures": key_sigs,
        "harmony_vocab": harmony_vocab,
        "mood_emotion": mood_vocab,
        "tempo_rhythm": tempo_vocab,
        "dynamics_structure": dynamics_vocab,
        "timbre_texture": timbre_vocab,
        "vocal_expressions": vocal_vocab,
        "genre_vocabulary_map": genre_map,
        "descriptor_combos": combos,
        "stats": {
            "total_instrument_phrases": len(inst_phrases),
            "total_technique_patterns": len(tech_patterns),
            "total_production_terms": len(prod_vocab),
            "total_key_signatures": len(key_sigs),
            "total_harmony_terms": len(harmony_vocab),
            "total_mood_terms": len(mood_vocab),
            "total_tempo_rhythm": len(tempo_vocab),
            "total_dynamics_structure": len(dynamics_vocab),
            "total_timbre_terms": len(timbre_vocab),
            "total_vocal_terms": len(vocal_vocab),
            "total_genres_covered": len(genre_map),
            "total_descriptor_combos": len(combos),
        }
    }

    # JSON 사전 저장
    dict_path = RAG_DIR / "suno_dictionary.json"
    with open(dict_path, "w") as f:
        json.dump(dictionary, f, indent=2, ensure_ascii=False)
    print(f"\n사전 저장 → {dict_path}")

    # 보고서 생성
    report = generate_report(dictionary, len(tracks), len(genre_analysis))
    report_path = DOCS_DIR / "suno_dictionary_report.md"
    report_path.write_text(report)
    print(f"보고서 → {report_path}")

    # 요약
    print(f"\n{'='*50}")
    print(f"Suno 네이티브 어휘 사전 v1.1 완성")
    print(f"  악기 표현: {len(inst_phrases)}개")
    print(f"  주법 패턴: {len(tech_patterns)}개")
    print(f"  프로덕션: {len(prod_vocab)}개")
    print(f"  조성: {len(key_sigs)}개 / 화성: {len(harmony_vocab)}개")
    print(f"  무드: {len(mood_vocab)}개")
    print(f"  템포/리듬: {len(tempo_vocab)}개")
    print(f"  다이나믹스/구조: {len(dynamics_vocab)}개")
    print(f"  음색: {len(timbre_vocab)}개 / 보컬: {len(vocal_vocab)}개")
    print(f"  장르 커버: {len(genre_map)}개")
    print(f"  조합 표현: {len(combos)}개")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
