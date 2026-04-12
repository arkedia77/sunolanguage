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

    lines.extend([
        "",
        "---",
        "",
        "## 4. 자주 쓰는 형용사+명사 조합 (상위 50)",
        "",
        "SP에서 바로 쓸 수 있는 Suno 친화적 표현입니다.",
        "",
        "| 조합 | 빈도 |",
        "|------|------|",
    ])
    combos = dictionary.get("descriptor_combos", {})
    for combo, count in list(combos.items())[:50]:
        lines.append(f"| {combo} | x{count} |")

    lines.extend([
        "",
        "---",
        "",
        "## 5. 장르별 핵심 어휘 (상위 15 장르)",
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

    print("1/5 악기별 구문 추출...")
    inst_phrases = extract_instrument_phrases(tracks)
    print(f"  → {len(inst_phrases)}개 악기 표현")

    print("2/5 주법/기법 패턴 추출...")
    tech_patterns = extract_technique_patterns(tracks)
    print(f"  → {len(tech_patterns)}개 주법 표현")

    print("3/5 프로덕션 어휘 추출...")
    prod_vocab = extract_production_vocab(tracks)
    print(f"  → {len(prod_vocab)}개 프로덕션 표현")

    print("4/5 장르별 어휘 맵 생성...")
    genre_map = build_genre_vocabulary_map(genre_analysis)
    print(f"  → {len(genre_map)}개 장르 커버")

    print("5/5 형용사+명사 조합 추출...")
    combos = extract_descriptor_combos(tracks)
    print(f"  → {len(combos)}개 조합")

    # 사전 조립
    dictionary = {
        "version": "1.0",
        "created_at": "2026-04-12",
        "tracks_count": len(tracks),
        "genres_count": len(genre_analysis),
        "instrument_phrases": inst_phrases,
        "technique_patterns": tech_patterns,
        "production_vocab": prod_vocab,
        "genre_vocabulary_map": genre_map,
        "descriptor_combos": combos,
        "stats": {
            "total_instrument_phrases": len(inst_phrases),
            "total_technique_patterns": len(tech_patterns),
            "total_production_terms": len(prod_vocab),
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
    print(f"Suno 네이티브 어휘 사전 v1.0 완성")
    print(f"  악기 표현: {len(inst_phrases)}개")
    print(f"  주법 패턴: {len(tech_patterns)}개")
    print(f"  프로덕션: {len(prod_vocab)}개")
    print(f"  장르 커버: {len(genre_map)}개")
    print(f"  조합 표현: {len(combos)}개")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
