#!/usr/bin/env python3
"""
sunolang - Suno 프롬프트에서 구조화 어휘 추출

입력: collected_prompts.json (hymns/stems), phone_recording/*.json
출력: data/parsed/ 에 트랙별 JSON + 전체 어휘 인덱스
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PARSED_DIR = PROJECT_ROOT / "data" / "parsed"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

# ── Suno tags 문장 단위 분류 규칙 ──────────────────────────────

# 각 카테고리를 식별하는 키워드/패턴
CATEGORY_PATTERNS = {
    "genre": [
        r"\b(hymn|choral|classical|jazz|blues|rock|pop|trot|R&B|hip[- ]?hop|"
        r"trap|house|techno|ambient|folk|country|bossa\s*nova|metal|punk|"
        r"gospel|worship|liturgical|funk|soul|reggae|latin|world|"
        r"K-Pop|EDM|lo-?fi|synthwave|bluegrass|flamenco|afrobeat|amapiano|"
        r"raga|gamelan|bebop|modal\s+jazz|indie|alternative|electronic|"
        r"Christian|sacred|contemporary|traditional)\b",
    ],
    "instruments": [
        r"\b(piano|organ|pipe organ|guitar|bass|drum|violin|viola|cello|"
        r"flute|oboe|clarinet|trumpet|trombone|saxophone|harp|timpani|"
        r"glockenspiel|cymbal|hi-hat|snare|kick|synthesizer|synth|"
        r"choir|SATB|soprano|alto|tenor|bass voice|strings?|brass|"
        r"woodwind|percussion|ensemble|orchestra|accompaniment|"
        r"a\s+cappella)\b",
    ],
    "techniques": [
        r"\b(arpeggiat|staccato|legato|tremolo|vibrato|glissando|rubato|"
        r"pizzicato|fingerstyle|block\s+chord|homophonic|polyphonic|"
        r"counterpoint|unison|harmony|four-part|colla\s+parte|"
        r"walking\s+(bass|pattern)|fingerpick|strumm|hammer[- ]on|"
        r"pull[- ]off|double[- ]stroke|roll|trill|bend|slide|"
        r"palm[- ]mute|mute|sustained|pedal\s+(note|bass|tone))",
    ],
    "vocal": [
        r"\b(vocal|sing|voice|diction|phrasing|vowel|consonant|"
        r"operatic|falsetto|belt|breathy|raspy|vibrato|"
        r"clear\s+diction|controlled\s+vibrato|classical\s+choral|"
        r"formal\s+and|liturgical|reverent|delivery)\b",
    ],
    "production": [
        r"\b(reverb|delay|echo|compression|EQ|stereo|mono|panning|"
        r"mixing|mastering|clean|polished|warm|bright|dry|wet|"
        r"hall\s+reverb|plate\s+reverb|room\s+reverb|cathedral|"
        r"acoustic\s+space|natural\s+reverb|electronic\s+processing|"
        r"recording|production)\b",
    ],
    "rhythm_tempo": [
        r"\b(\d+\s*BPM|tempo|time\s+signature|[234]/[234]\s+time|"
        r"moderato|allegro|andante|adagio|presto|stately|steady|"
        r"syncopat|swing|shuffle|groove|beat|pulse|"
        r"ritardando|rallentando|accelerando|fermata|rubato)\b",
    ],
    "dynamics_structure": [
        r"\b(forte|piano|mezzo|crescendo|decrescendo|diminuendo|"
        r"sforzando|fortissimo|pianissimo|swell|build|"
        r"cadence|plagal|coda|strophic|verse|chorus|bridge|"
        r"intro|outro|interlude|modulation|key\s+change|"
        r"dynamic\s+range|section)\b",
    ],
    "key_harmony": [
        r"\b(key\s+of\s+[A-G][b#]?\s*(Major|Minor|major|minor)|"
        r"[A-G][b#]?\s+(Major|Minor)|tonic|dominant|subdominant|"
        r"harmonic\s+structure|tonal|chord|progression|cadence|"
        r"resolution|modulation)\b",
    ],
}

# 컴파일
COMPILED_PATTERNS = {
    cat: [re.compile(p, re.IGNORECASE) for p in patterns]
    for cat, patterns in CATEGORY_PATTERNS.items()
}


def classify_sentences(tags_text: str) -> dict[str, list[str]]:
    """tags 텍스트를 문장 단위로 분류하여 카테고리별 문장 목록 반환."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|(?<=\))\s+', tags_text) if s.strip()]
    result = {cat: [] for cat in COMPILED_PATTERNS}

    for sent in sentences:
        matched_cats = []
        for cat, patterns in COMPILED_PATTERNS.items():
            for p in patterns:
                if p.search(sent):
                    matched_cats.append(cat)
                    break
        if not matched_cats:
            matched_cats = ["genre"]  # 첫 문장은 보통 장르 선언
        for cat in matched_cats:
            if sent not in result[cat]:
                result[cat].append(sent)
    return result


def extract_vocab_from_tags(tags_text: str) -> dict[str, list[str]]:
    """tags 텍스트에서 구체적 어휘(표현) 추출."""
    vocab = {
        "genre_terms": [],
        "instruments": [],
        "techniques": [],
        "vocal_terms": [],
        "production_terms": [],
        "tempo_rhythm": [],
        "dynamics_structure": [],
        "key_harmony": [],
    }

    # 장르 추출
    genre_re = re.compile(
        r"(Traditional\s+Christian\s+hymn|Choral\s+hymn|Korean\s+choral\s+hymn|"
        r"K-Pop\s+Trot\s+fusion|liturgical\s+music|sacred\s+music|"
        r"[A-Z][a-z]+(?:\s+[a-z]+)*\s+(?:hymn|anthem|ballad|song))",
        re.IGNORECASE
    )
    vocab["genre_terms"] = list(set(m.group() for m in genre_re.finditer(tags_text)))

    # 악기 추출
    inst_re = re.compile(
        r"(grand\s+piano|pipe\s+organ|SATB\s+choir|mixed[- ]voice\s+choir|"
        r"mixed\s+SATB\s+choir|mixed\s+choir|string\s+section|"
        r"bass\s+guitar|acoustic\s+guitar|electric\s+guitar|"
        r"drum\s+kit|disco\s+drum\s+kit|snare\s+drum|kick\s+drum|"
        r"synthesized?\s+(?:brass|strings?)|"
        r"soprano|alto|tenor|bass\s+(?:voice|section)|"
        r"(?:pipe\s+)?organ|piano|flute|oboe|clarinet|trumpet|"
        r"trombone|saxophone|harp|timpani|glockenspiel|cymbal|hi-hat|"
        r"violin|viola|cello|orchestra)",
        re.IGNORECASE
    )
    vocab["instruments"] = list(set(m.group() for m in inst_re.finditer(tags_text)))

    # 주법/텍스처 추출
    tech_re = re.compile(
        r"(block\s+chords?|arpeggiated\s+(?:patterns?|figures?|chords?)|"
        r"four-part\s+(?:homophonic\s+)?harmony|homophonic\s+(?:harmony|texture)|"
        r"staccato\s+rhythmic\s+stabs|walking\s+(?:bass|pattern)|"
        r"legato\s+(?:phrasing|violins?)|sustained\s+(?:phrasing|chord|pedal|vowels?)|"
        r"melodic\s+counterpoint|colla\s+parte|unison\s+passages?|"
        r"flowing\s+eighth-note\s+patterns?|fingerstyle|"
        r"full\s+registration|bright\s+registrations?|"
        r"(?:principal|reed)\s+(?:and\s+reed\s+)?stops?|"
        r"prominent\s+pedal\s+notes?|strophic\s+(?:hymn\s+)?format|"
        r"plagal\s+cadence|classical\s+vibrato|controlled\s+vibrato|"
        r"(?:natural\s+)?hall\s+reverb|plate\s+reverb|"
        r"wide\s+stereo\s+field|natural\s+(?:acoustic|reverb|decay)|"
        r"ritardando|rallentando|rubato|fermata)",
        re.IGNORECASE
    )
    vocab["techniques"] = list(set(m.group() for m in tech_re.finditer(tags_text)))

    # 보컬 표현
    vocal_re = re.compile(
        r"(formal\s+and\s+(?:operatic|reverent|liturgical)|"
        r"clear\s+diction|controlled\s+vibrato|classical\s+(?:choral|vibrato)|"
        r"sustained\s+(?:legato\s+)?phrasing|precise\s+consonant\s+(?:articulation|cut-offs)|"
        r"elongated\s+vowels|wide\s+dynamic\s+range|"
        r"(?:male|female)\s+(?:tenor|soprano|alto|bass)|"
        r"traditional\s+Trot\s+vibrato|melodic\s+inflections|"
        r"breathy|raspy|falsetto|belt(?:ing)?|operatic)",
        re.IGNORECASE
    )
    vocab["vocal_terms"] = list(set(m.group() for m in vocal_re.finditer(tags_text)))

    # 프로덕션
    prod_re = re.compile(
        r"(natural\s+(?:cathedral-like\s+)?acoustic|significant\s+hall\s+reverb|"
        r"natural\s+hall\s+reverb|natural\s+(?:room\s+)?resonance|"
        r"large\s+(?:hall|acoustic\s+space)|church\s+or\s+cathedral\s+setting|"
        r"clean\s+(?:with\s+a\s+natural|compressed\s+tone)|polished|"
        r"light\s+plate\s+reverb|wide\s+stereo\s+field|"
        r"without\s+electronic\s+processing|a\s+cappella)",
        re.IGNORECASE
    )
    vocab["production_terms"] = list(set(m.group() for m in prod_re.finditer(tags_text)))

    # 템포/리듬
    tempo_re = re.compile(
        r"(\d+\s*BPM|4/4\s+time|3/4\s+time|6/8\s+time|"
        r"moderate[,\s]+stately\s+tempo|steady\s+(?:moderato|\d+\s*BPM|tempo)|"
        r"stately\s+tempo|moderate\s+tempo)",
        re.IGNORECASE
    )
    vocab["tempo_rhythm"] = list(set(m.group() for m in tempo_re.finditer(tags_text)))

    # 다이나믹스/구조
    dyn_re = re.compile(
        r"(mezzo-forte\s+to\s+forte|piano\s+to\s+(?:a\s+resonant\s+)?forte|"
        r"forte\s+throughout|gentle\s+piano|resonant\s+forte|"
        r"(?:dynamics?\s+)?swell|plagal\s+cadence|final\s+cadence|"
        r"strophic\s+(?:hymn\s+)?(?:format|structure)|"
        r"slight\s+ritardando)",
        re.IGNORECASE
    )
    vocab["dynamics_structure"] = list(set(m.group() for m in dyn_re.finditer(tags_text)))

    # 키/화성
    key_re = re.compile(
        r"((?:key\s+of\s+)?[A-G][b#]?\s+(?:Major|Minor)|"
        r"tonic\s+and\s+dominant|traditional\s+Western\s+tonal\s+progressions?|"
        r"clear\s+cadences|harmonic\s+(?:structure|support))",
        re.IGNORECASE
    )
    vocab["key_harmony"] = list(set(m.group() for m in key_re.finditer(tags_text)))

    return vocab


def extract_inline_cues(sp_text: str) -> dict[str, list[str]]:
    """suno_sp에서 섹션 태그와 인라인 큐 추출."""
    if not sp_text:
        return {"section_tags": [], "instrument_cues": [], "dynamics_cues": []}

    # 대괄호 내용 추출
    bracket_re = re.compile(r'\[([^\]]+)\]')
    all_cues = bracket_re.findall(sp_text)

    section_tags = []
    instrument_cues = []
    dynamics_cues = []

    section_re = re.compile(
        r'^(Intro|Verse\s*\d*|Pre-?Chorus|Chorus|Bridge|Interlude|Outro|'
        r'Hook|Drop|Breakdown|Build|Solo|Instrumental)$',
        re.IGNORECASE
    )
    dynamics_re = re.compile(
        r'(forte|piano|crescendo|decrescendo|swell|build|'
        r'slowing|rallentando|ritardando|key\s+change|fades?\s+out|'
        r'increases?\s+in\s+volume|softly|gently|natural\s+decay)',
        re.IGNORECASE
    )

    for cue in all_cues:
        cue_stripped = cue.strip()
        if section_re.match(cue_stripped):
            section_tags.append(cue_stripped)
        elif dynamics_re.search(cue_stripped):
            dynamics_cues.append(cue_stripped)
        else:
            instrument_cues.append(cue_stripped)

    return {
        "section_tags": list(dict.fromkeys(section_tags)),
        "instrument_cues": list(dict.fromkeys(instrument_cues)),
        "dynamics_cues": list(dict.fromkeys(dynamics_cues)),
    }


def parse_track(track: dict, source: str) -> dict:
    """단일 트랙 파싱."""
    tags = track.get("suno_tags", "") or track.get("suno_output", {}).get("style_prompt", "")
    sp = track.get("suno_sp", "") or track.get("suno_output", {}).get("lyrics_structure", "")

    result = {
        "source": source,
        "title": track.get("title", ""),
        "suno_uuid": track.get("suno_uuid", ""),
    }

    # 추가 메타 (hymn_no, key 등)
    for field in ("hymn_no", "key", "stem", "track_id"):
        if field in track:
            result[field] = track[field]

    result["classified_sentences"] = classify_sentences(tags)
    result["vocabulary"] = extract_vocab_from_tags(tags)
    result["inline_cues"] = extract_inline_cues(sp)
    result["raw_tags"] = tags
    result["raw_sp"] = sp

    return result


def build_vocab_index(parsed_tracks: list[dict]) -> dict:
    """전체 트랙에서 어휘 빈도 인덱스 생성."""
    index = {}
    for track in parsed_tracks:
        vocab = track.get("vocabulary", {})
        for category, terms in vocab.items():
            if category not in index:
                index[category] = {}
            for term in terms:
                normalized = term.strip().lower()
                if normalized not in index[category]:
                    index[category][normalized] = {"count": 0, "examples": []}
                index[category][normalized]["count"] += 1
                if len(index[category][normalized]["examples"]) < 3:
                    ref = track.get("title", track.get("hymn_no", "unknown"))
                    index[category][normalized]["examples"].append(str(ref))

    # 각 카테고리 내 빈도순 정렬
    for category in index:
        index[category] = dict(
            sorted(index[category].items(), key=lambda x: -x[1]["count"])
        )
    return index


def main():
    all_parsed = []

    # 1. collected_prompts.json (hymns)
    collected = PROJECT_ROOT / "projects" / "sunolanguage" / "messages"
    # agent-comm 경로에서 직접 읽기
    agent_comm_collected = Path.home() / "projects" / "agent-comm" / "projects" / "sunolanguage" / "messages" / "sunolanguage_sunolanguage_20260402_001000_collected_prompts.json"

    if agent_comm_collected.exists():
        data = json.loads(agent_comm_collected.read_text())
        hymns = data.get("hymns", {}).get("tracks", [])
        stems = data.get("stems", {}).get("tracks", [])
        print(f"[collected_prompts] 찬송가 {len(hymns)}곡, 스템 {len(stems)}개 로드")
        for track in hymns:
            all_parsed.append(parse_track(track, "hymn"))
        for track in stems:
            all_parsed.append(parse_track(track, "stem"))

    # 2. phone_recording/*.json
    phone_dir = RAW_DIR / "phone_recording"
    if phone_dir.exists():
        for jf in sorted(phone_dir.glob("*.json")):
            data = json.loads(jf.read_text())
            parsed = parse_track(data, "phone_recording")
            parsed["title"] = data.get("track", {}).get("title", jf.stem)
            all_parsed.append(parsed)
            print(f"[phone_recording] {jf.name} 파싱 완료")

    if not all_parsed:
        print("파싱할 데이터가 없습니다.")
        return

    # 트랙별 파싱 결과 저장
    tracks_out = PARSED_DIR / "parsed_tracks.json"
    tracks_out.write_text(json.dumps(all_parsed, ensure_ascii=False, indent=2))
    print(f"\n트랙별 파싱 → {tracks_out} ({len(all_parsed)}건)")

    # 어휘 빈도 인덱스 생성
    index = build_vocab_index(all_parsed)
    index_out = PARSED_DIR / "vocab_index.json"
    index_out.write_text(json.dumps(index, ensure_ascii=False, indent=2))
    print(f"어휘 인덱스 → {index_out}")

    # 요약 출력
    print("\n── 어휘 인덱스 요약 ──")
    for cat, terms in index.items():
        print(f"  {cat}: {len(terms)}개 고유 표현")
        top3 = list(terms.items())[:3]
        for term, info in top3:
            print(f"    - \"{term}\" (x{info['count']})")


if __name__ == "__main__":
    main()
