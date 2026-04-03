#!/usr/bin/env python3
"""
sunolang - Suno 프롬프트에서 구조화 어휘 추출 (v2)

입력:
  - collected_prompts.json (hymns/stems)
  - phone_recording/*.json
  - suno_moods.jsonl (306곡 다장르)
출력:
  - data/parsed/parsed_tracks.json — 트랙별 파싱
  - data/parsed/vocab_index.json — 어휘 빈도 인덱스
  - data/parsed/genre_analysis.json — 장르별 어휘 차이 분석
  - data/parsed/audiocards_mapped.json — Audiocards 7필드 매핑
"""

import json
import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PARSED_DIR = PROJECT_ROOT / "data" / "parsed"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

# ── Audiocards 7필드 정의 (arXiv:2602.13835 기반) ──────────
AUDIOCARDS_FIELDS = {
    "ac_instruments": "악기 명사 (nouns)",
    "ac_techniques": "연주 기법 (noun-verb pairs)",
    "ac_genre_style": "장르/스타일 레이블",
    "ac_mood_emotion": "무드/감정 형용사",
    "ac_production": "녹음/프로덕션 설명",
    "ac_temporal_structure": "시간/구조적 마커",
    "ac_timbre": "음색 형용사 (Reymore 20-dim)",
}

# ── Suno tags 문장 단위 분류 규칙 (v2: 다장르 대응) ─────────

CATEGORY_PATTERNS = {
    "genre": [
        r"\b(hymn|choral|classical|jazz|blues|rock|pop|trot|R&B|hip[- ]?hop|"
        r"trap|house|techno|ambient|folk|country|bossa\s*nova|metal|punk|"
        r"gospel|worship|liturgical|funk|soul|reggae|latin|world|"
        r"K-Pop|EDM|lo-?fi|synthwave|bluegrass|flamenco|afrobeat|amapiano|"
        r"raga|gamelan|bebop|modal\s+jazz|indie|alternative|electronic|"
        r"Christian|sacred|contemporary|traditional|"
        # v2 다장르 추가
        r"progressive\s+(?:house|metal|rock)|thrash\s+metal|neo[- ]?soul|"
        r"IDM|breakbeat|post[- ]?rock|shoegaze|dream\s+pop|"
        r"psychedeli[ca]|grunge|dubstep|drum\s+and\s+bass|dnb|"
        r"new\s+wave|darkwave|industrial|noise|glitch|"
        r"downtempo|chillout|trip[- ]?hop|boom\s+bap|"
        r"lo-?fi\s+hip[- ]?hop|neo[- ]?psychedelia|"
        r"alt\s+rock|math\s+rock|stoner|doom|black\s+metal|"
        r"death\s+metal|power\s+metal|symphonic\s+metal)\b",
    ],
    "instruments": [
        r"\b(piano|organ|pipe\s+organ|guitar|bass|drum|violin|viola|cello|"
        r"flute|oboe|clarinet|trumpet|trombone|saxophone|harp|timpani|"
        r"glockenspiel|cymbal|hi-hat|snare|kick|synthesizer|synth|"
        r"choir|SATB|soprano|alto|tenor|bass\s+voice|strings?|brass|"
        r"woodwind|percussion|ensemble|orchestra|accompaniment|"
        r"a\s+cappella|"
        # v2 다장르 악기
        r"808|sub\s+bass|Rhodes|Fender\s+Rhodes|Wurlitzer|Moog|"
        r"theremin|mellotron|vocoder|sampler|drum\s+machine|"
        r"sitar|tabla|tanpura|oud|kora|djembe|cajón|cajon|"
        r"banjo|fiddle|mandolin|ukulele|dobro|pedal\s+steel|"
        r"marimba|vibraphone|xylophone|glockenspiel|celesta|"
        r"gamelan|metallophones?|gong|bamboo|jegog|"
        r"turntable|MPC|SP-?\d+|TR-?\d+|"
        r"distortion\s+guitar|overdriven\s+guitar|clean\s+guitar|"
        r"acoustic\s+guitar|electric\s+guitar|nylon\s+guitar|"
        r"upright\s+bass|fretless\s+bass|slap\s+bass|"
        r"horn\s+section|string\s+section)\b",
    ],
    "techniques": [
        r"\b(arpeggiat|staccato|legato|tremolo|vibrato|glissando|rubato|"
        r"pizzicato|fingerstyle|block\s+chord|homophonic|polyphonic|"
        r"counterpoint|unison|harmony|four-part|colla\s+parte|"
        r"walking\s+(?:bass|pattern)|fingerpick|strumm|hammer[- ]on|"
        r"pull[- ]off|double[- ]stroke|roll|trill|bend|slide|"
        r"palm[- ]mute|mute|sustained|pedal\s+(?:note|bass|tone)|"
        # v2 다장르 주법
        r"sidechain|compression|gated\s+reverb|"
        r"rasgueado|picado|golpe|alzapua|"
        r"sweep\s+pick|tapping|shred|tremolo\s+pick|"
        r"slap(?:ping)?|pop(?:ping)?|thumb|"
        r"polyrhythm|cross[- ]rhythm|interlocking|"
        r"call[- ]and[- ]response|"
        r"pitch\s+bend|portamento|melisma|"
        r"power\s+chord|drop\s+(?:D|tuning)|down[- ]tun|"
        r"blast\s+beat|double\s+(?:bass|kick|pedal)|"
        r"breakbeat|syncopat|shuffle|swing|"
        r"chopping|sampling|looping|scratching|"
        r"granular|glitch|stutter|chop)\b",
    ],
    "vocal": [
        r"\b(vocal|sing|voice|diction|phrasing|vowel|consonant|"
        r"operatic|falsetto|belt|breathy|raspy|vibrato|"
        r"clear\s+diction|controlled\s+vibrato|classical\s+choral|"
        r"formal\s+and|liturgical|reverent|delivery|"
        # v2 다장르 보컬
        r"auto[- ]?tune|rap|flow|scream|growl|grunt|"
        r"whisper|spoken\s+word|chant|yodel|"
        r"melismatic|riff|ad[- ]?lib|"
        r"harmony\s+vocal|backing\s+vocal|layered\s+vocal|"
        r"vocal\s+(?:chop|sample|fry|run)|"
        r"nasal|throaty|gritty|smooth|silky|airy|"
        r"head\s+voice|chest\s+voice|mixed\s+voice)\b",
    ],
    "production": [
        r"\b(reverb|delay|echo|compression|EQ|stereo|mono|panning|"
        r"mixing|mastering|clean|polished|warm|bright|dry|wet|"
        r"hall\s+reverb|plate\s+reverb|room\s+reverb|cathedral|"
        r"acoustic\s+space|natural\s+reverb|electronic\s+processing|"
        r"recording|production|"
        # v2 다장르 프로덕션
        r"lo-?fi|vinyl\s+(?:crackle|noise|hiss)|tape\s+(?:saturation|hiss)|"
        r"distort|overdrive|fuzz|saturation|"
        r"sidechain|pumping|ducking|"
        r"filtered|high[- ]pass|low[- ]pass|band[- ]pass|"
        r"bit[- ]?crush|downsample|"
        r"spacey|atmospheric|lush|dense|sparse|minimal|"
        r"ambient\s+(?:pad|texture|wash)|"
        r"808\s+(?:sub|bass)|sub\s+(?:bass|low)|"
        r"clipping|limiting|brick[- ]?wall)\b",
    ],
    "rhythm_tempo": [
        r"\b(\d+\s*BPM|tempo|time\s+signature|[234678]/[2348]\s+time|"
        r"moderato|allegro|andante|adagio|presto|stately|steady|"
        r"syncopat|swing|shuffle|groove|beat|pulse|"
        r"ritardando|rallentando|accelerando|fermata|rubato|"
        # v2 다장르 리듬
        r"four[- ]on[- ]the[- ]floor|off[- ]?beat|backbeat|"
        r"triplet|hi-hat\s+(?:roll|pattern)|trap\s+(?:beat|pattern)|"
        r"boom[- ]?bap|breakbeat|half[- ]time|double[- ]time|"
        r"polymetr|odd\s+(?:time|meter)|mixed\s+meter|"
        r"(?:5|7|9|11|13)/(?:4|8)\s*(?:time)?|"
        r"mid[- ]?tempo|up[- ]?tempo|slow|fast|laid[- ]?back|driving)\b",
    ],
    "dynamics_structure": [
        r"\b(forte|piano|mezzo|crescendo|decrescendo|diminuendo|"
        r"sforzando|fortissimo|pianissimo|swell|build|"
        r"cadence|plagal|coda|strophic|verse|chorus|bridge|"
        r"intro|outro|interlude|modulation|key\s+change|"
        r"dynamic\s+range|section|"
        # v2 다장르 구조
        r"drop|breakdown|buildup|riser|"
        r"hook|pre[- ]?chorus|post[- ]?chorus|"
        r"A[- ]?section|B[- ]?section|head|solo|"
        r"vamp|loop|turnaround|tag|"
        r"fade\s+(?:in|out)|cut|stop|silence|"
        r"layering|textural)\b",
    ],
    "key_harmony": [
        r"\b(key\s+of\s+[A-G][b#]?\s*(?:Major|Minor|major|minor)|"
        r"[A-G][b#]?\s+(?:Major|Minor)|tonic|dominant|subdominant|"
        r"harmonic\s+structure|tonal|chord|progression|cadence|"
        r"resolution|modulation|"
        # v2 다장르 화성
        r"modal|dorian|mixolydian|lydian|phrygian|aeolian|locrian|"
        r"pentatonic|blues\s+scale|chromatic|whole[- ]tone|"
        r"diminished|augmented|suspended|add\d|"
        r"seventh|ninth|eleventh|thirteenth|"
        r"ii-V-I|I-IV-V|twelve[- ]bar|turnaround|"
        r"atonal|microtonal|quarter[- ]tone|"
        r"drone|pedal\s+point|ostinato)\b",
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


# ── Audiocards 7필드 매핑 패턴 ──────────────────────────────

AC_PATTERNS = {
    "ac_instruments": re.compile(
        r"\b(grand\s+piano|upright\s+piano|electric\s+piano|acoustic\s+piano|"
        r"Rhodes\s+piano|Fender\s+Rhodes|Wurlitzer|Moog|"
        r"electric\s+guitar|acoustic\s+guitar|nylon\s+guitar|clean\s+guitar|"
        r"distortion\s+guitar|overdriven\s+guitar|bass\s+guitar|"
        r"upright\s+bass|fretless\s+bass|slap\s+bass|"
        r"pipe\s+organ|Hammond\s+organ|"
        r"drum\s+kit|drum\s+machine|snare\s+drum|kick\s+drum|bass\s+drum|"
        r"horn\s+section|string\s+section|"
        r"synth\s+(?:pad|lead|bass)|analog\s+synth|"
        r"piano|organ|guitar|bass|drums?|violin|viola|cello|"
        r"flute|oboe|clarinet|trumpet|trombone|saxophone|harp|"
        r"synthesizer|synth|808|sub\s+bass|"
        r"sitar|tabla|tanpura|oud|kora|djembe|cajón|cajon|banjo|fiddle|mandolin|"
        r"marimba|vibraphone|xylophone|celesta|gamelan|gong|"
        r"hi-hat|snare|kick|cymbal|timpani|"
        r"turntable|MPC|sampler|vocoder|"
        r"choir|orchestra|strings|brass|woodwinds?|percussion)\b",
        re.IGNORECASE
    ),
    "ac_techniques": re.compile(
        r"\b(fingerpicked\s+arpeggios?|tremolo\s+picking|palm[- ]muting|"
        r"sweep\s+picking|tapping|shredding|slapping|popping|"
        r"rasgueado|picado|walking\s+bass(?:line)?|"
        r"arpeggiated\s+\w+|staccato\s+\w+|legato\s+\w+|"
        r"pizzicato|glissando|vibrato|rubato|"
        r"sidechain(?:ed|ing)?(?:\s+compression)?|"
        r"polyrhythm(?:ic)?|cross[- ]rhythm|interlocking\s+\w+|"
        r"call[- ]and[- ]response|blast\s+beat|double\s+(?:bass|kick|pedal)|"
        r"syncopated\s+\w+|four[- ]on[- ]the[- ]floor|"
        r"chopping|sampling|looping|scratching|"
        r"block\s+chords?|power\s+chords?)\b",
        re.IGNORECASE
    ),
    "ac_genre_style": re.compile(
        r"\b((?:progressive|thrash|death|black|power|symphonic|doom|stoner)\s+(?:metal|rock)|"
        r"(?:neo[- ]?)?(?:soul|psychedelia)|"
        r"(?:lo-?fi\s+)?hip[- ]?hop|boom[- ]?bap|trap|"
        r"(?:progressive|deep|tech)\s+house|dubstep|drum\s+and\s+bass|"
        r"(?:post[- ]?)?rock|shoegaze|dream\s+pop|"
        r"jazz|bebop|modal\s+jazz|fusion|swing|"
        r"bossa\s*nova|flamenco|afrobeat|amapiano|raga|"
        r"bluegrass|country|folk|blues|funk|soul|R&B|gospel|"
        r"ambient|downtempo|chillout|trip[- ]?hop|"
        r"synthwave|darkwave|new\s+wave|industrial|"
        r"classical|orchestral|cinematic|"
        r"indie\s+(?:pop|rock|folk)|alt\s+rock|math\s+rock|"
        r"hymn|choral|worship|liturgical|sacred|"
        r"pop[- ]?rock|psychedelic\s+pop[- ]?rock)\b",
        re.IGNORECASE
    ),
    "ac_mood_emotion": re.compile(
        r"\b(melanchol(?:ic|y)|euphori[ca]|energetic|calm|serene|"
        r"aggressive|intense|dark|bright|warm|cold|"
        r"dreamy|ethereal|nostalgic|hopeful|triumphant|"
        r"haunting|eerie|mysterious|playful|joyful|"
        r"somber|mournful|passionate|tender|gentle|"
        r"epic|majestic|powerful|anthemic|uplifting|"
        r"groovy|funky|chill|relaxed|mellow|"
        r"hypnotic|meditative|contemplative|introspective|"
        r"raw|visceral|gritty|smooth|lush|sparse)\b",
        re.IGNORECASE
    ),
    "ac_production": re.compile(
        r"\b((?:hall|plate|room|spring|cathedral)[- ]?reverb|"
        r"(?:tape|analog|digital)\s+(?:delay|echo|saturation)|"
        r"sidechain(?:ed)?\s+compression|gated\s+reverb|"
        r"vinyl\s+(?:crackle|noise|hiss)|tape\s+hiss|"
        r"lo-?fi\s+(?:production|aesthetic|quality)|"
        r"(?:high|low|band)[- ]pass\s+filter|"
        r"bit[- ]?crush(?:ed|ing)?|"
        r"stereo\s+(?:field|width|spread|imaging)|"
        r"(?:wide|narrow)\s+stereo|"
        r"(?:clean|warm|bright|dark|polished|raw)\s+(?:mix|production|sound|tone)|"
        r"atmospheric\s+(?:texture|pad|wash|production)|"
        r"(?:heavy|light|subtle)\s+(?:compression|distortion|reverb))\b",
        re.IGNORECASE
    ),
    "ac_temporal_structure": re.compile(
        r"\b(\d+\s*BPM|[234678]/[2348]\s*(?:time)?|"
        r"(?:slow|mid|up)[- ]?tempo|"
        r"(?:intro|verse|pre[- ]?chorus|chorus|bridge|solo|"
        r"interlude|breakdown|buildup|drop|outro|hook|coda|vamp)|"
        r"fade\s+(?:in|out)|ritardando|rallentando|accelerando|fermata|"
        r"strophic|through[- ]composed|rondo|sonata|AABA|ABAB)\b",
        re.IGNORECASE
    ),
    "ac_timbre": re.compile(
        r"\b(bright|dark|warm|cold|thin|thick|rich|full|hollow|"
        r"metallic|woody|glassy|breathy|airy|nasal|"
        r"crisp|muddy|punchy|boomy|tinny|shimmering|"
        r"fuzzy|distorted|overdriven|clean|saturated|"
        r"resonant|muffled|sharp|soft|harsh|smooth|"
        r"bell[- ]?like|silky|gritty|raspy|husky)\b",
        re.IGNORECASE
    ),
}


def map_to_audiocards(tags_text: str) -> dict[str, list[str]]:
    """tags 텍스트를 Audiocards 7필드에 매핑."""
    result = {}
    for field, pattern in AC_PATTERNS.items():
        matches = pattern.findall(tags_text)
        cleaned = list(dict.fromkeys(m.strip().lower() for m in matches if m.strip()))
        result[field] = cleaned
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
    result["audiocards"] = map_to_audiocards(tags)
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


def analyze_genres(parsed_tracks: list[dict]) -> dict:
    """장르별 어휘 차이 분석."""
    genre_vocab = defaultdict(lambda: defaultdict(set))

    for track in parsed_tracks:
        # 장르 결정: ac_genre_style 또는 source
        genres = track.get("audiocards", {}).get("ac_genre_style", [])
        if not genres:
            genres = [track.get("source", "unknown")]

        for genre in genres:
            genre = genre.lower().strip()
            # Audiocards 필드별 어휘 수집
            ac = track.get("audiocards", {})
            for field, terms in ac.items():
                for term in terms:
                    genre_vocab[genre][field].add(term)

    # set → sorted list 변환 + 통계
    result = {}
    for genre, fields in sorted(genre_vocab.items()):
        result[genre] = {
            "total_unique_terms": sum(len(v) for v in fields.values()),
            "fields": {
                field: sorted(terms) for field, terms in fields.items()
            }
        }
    return result


def build_audiocards_summary(parsed_tracks: list[dict]) -> dict:
    """Audiocards 7필드별 전체 어휘 빈도 집계."""
    summary = {}
    for field in AC_PATTERNS:
        counter = defaultdict(lambda: {"count": 0, "sources": set()})
        for track in parsed_tracks:
            ac = track.get("audiocards", {})
            for term in ac.get(field, []):
                counter[term]["count"] += 1
                counter[term]["sources"].add(track.get("source", "?"))
        # set → list, 빈도순 정렬
        summary[field] = {
            term: {"count": info["count"], "sources": sorted(info["sources"])}
            for term, info in sorted(counter.items(), key=lambda x: -x[1]["count"])
        }
    return summary


def main():
    all_parsed = []

    # 1. collected_prompts.json (hymns)
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

    # 3. suno_moods.jsonl (306곡 다장르)
    moods_file = Path.home() / "projects" / "agent-comm" / "shared" / "suno_moods.jsonl"
    if moods_file.exists():
        moods_count = 0
        with moods_file.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                track = {
                    "suno_tags": data.get("tags", ""),
                    "suno_sp": data.get("lyrics", ""),
                    "title": data.get("title", ""),
                    "suno_uuid": data.get("song_id", ""),
                    "display_tags": data.get("display_tags", ""),
                    "moods": data.get("moods", []),
                }
                all_parsed.append(parse_track(track, "suno_moods"))
                moods_count += 1
        print(f"[suno_moods] {moods_count}곡 로드")

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

    # Audiocards 7필드 매핑 결과
    ac_summary = build_audiocards_summary(all_parsed)
    ac_out = PARSED_DIR / "audiocards_mapped.json"
    ac_out.write_text(json.dumps(ac_summary, ensure_ascii=False, indent=2))
    print(f"Audiocards 매핑 → {ac_out}")

    # 장르별 어휘 차이 분석
    genre_analysis = analyze_genres(all_parsed)
    genre_out = PARSED_DIR / "genre_analysis.json"
    genre_out.write_text(json.dumps(genre_analysis, ensure_ascii=False, indent=2))
    print(f"장르별 분석 → {genre_out}")

    # 요약 출력
    print(f"\n── 전체 요약 ({len(all_parsed)}곡) ──")
    sources = defaultdict(int)
    for t in all_parsed:
        sources[t.get("source", "?")] += 1
    print(f"  소스별: {dict(sources)}")

    print("\n── 어휘 인덱스 (기존 8카테고리) ──")
    for cat, terms in index.items():
        print(f"  {cat}: {len(terms)}개 고유 표현")
        top3 = list(terms.items())[:3]
        for term, info in top3:
            print(f"    - \"{term}\" (x{info['count']})")

    print("\n── Audiocards 7필드 요약 ──")
    for field, terms in ac_summary.items():
        print(f"  {field}: {len(terms)}개 고유 표현")
        top3 = list(terms.items())[:3]
        for term, info in top3:
            print(f"    - \"{term}\" (x{info['count']}, {info['sources']})")

    print(f"\n── 장르별 어휘 ({len(genre_analysis)}개 장르) ──")
    for genre, info in sorted(genre_analysis.items(), key=lambda x: -x[1]["total_unique_terms"])[:10]:
        print(f"  {genre}: {info['total_unique_terms']}개 고유 표현")


if __name__ == "__main__":
    main()
