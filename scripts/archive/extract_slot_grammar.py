#!/usr/bin/env python3
"""Suno SP 슬롯 문법 추출 → leomusic2 테스트 배치용 JSON 출력.

Suno SP의 7-슬롯 프레임:
  1. genre_declaration — 장르 선언 (첫 문장)
  2. instrument_layers — 악기/어레인지먼트 레이어 (복수 문장)
  3. drums — 드럼/퍼커션 전용 기술
  4. vocals — 보컬 타입/딜리버리/프로세싱
  5. tempo_key_time — 템포/조성/박자
  6. production — 프로덕션/믹스 특성
  7. arrangement_summary — 어레인지먼트 총평 (마지막 문장)
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

MERGED = Path("/Users/leo/sunolanguage/data/reanalysis_v2/merged_4values.json")
OUT = Path("/Users/leo/sunolanguage/data/reanalysis_v2/suno_sp_slot_grammar.json")
merged = json.loads(MERGED.read_text())

# --- 문장 분리 ---
def split_sentences(txt):
    if not txt:
        return []
    t = re.sub(r"\s+", " ", txt.strip())
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]

# --- 슬롯 분류 규칙 ---
GENRE_INDICATORS = re.compile(
    r"^(k-pop|k-indie|k-hip\s*hop|k-ballad|k-rock|k-r&b|"
    r"pop|rock|jazz|r&b|hip[- ]?hop|electronic|ambient|folk|"
    r"indie|ballad|soul|funk|disco|synth|city\s*pop|bossa|"
    r"punk|metal|blues|country|reggae|lo-?fi|boom\s*bap|"
    r"cinematic|orchestral|dream\s*pop|shoegaze|chillwave)", re.I)

DRUM_WORDS = {"drum", "drums", "kick", "snare", "hi-hat", "hi-hats",
              "percussion", "cymbal", "shaker", "tambourine", "rimshot",
              "backbeat", "beat", "beats"}

VOCAL_WORDS = {"vocal", "vocals", "singer", "singing", "voice",
               "baritone", "tenor", "soprano", "alto", "falsetto",
               "rap", "rapping", "melodic rap"}

TEMPO_RE = re.compile(r"\b(tempo|bpm|key of|time signature|\d+/\d+\s*time)\b", re.I)

PRODUCTION_WORDS = {"production", "mix", "mixing", "mastering", "processed",
                    "mic", "close-mic", "room reverb", "stereo", "panning",
                    "compression", "eq", "sidechain"}

ARRANGEMENT_RE = re.compile(r"(arrangement|arrangement is|focusing on|interplay)", re.I)

def classify_sentence(sent, idx, total):
    sl = sent.lower()
    words_set = set(re.findall(r"[a-z\-\']+", sl))

    # 첫 문장이고 장르 키워드로 시작 → genre_declaration
    if idx == 0 and GENRE_INDICATORS.search(sl):
        return "genre_declaration"

    # 템포/키/박자
    if TEMPO_RE.search(sl) and not words_set & DRUM_WORDS:
        return "tempo_key_time"

    # 어레인지먼트 총평 (마지막 근처 + "arrangement" 키워드)
    if ARRANGEMENT_RE.search(sl):
        return "arrangement_summary"

    # 프로덕션
    if words_set & PRODUCTION_WORDS:
        return "production"

    # 보컬
    if words_set & VOCAL_WORDS:
        return "vocals"

    # 드럼
    if words_set & DRUM_WORDS:
        return "drums"

    # 나머지 = 악기 레이어
    return "instrument_layers"


# --- 추출 ---
slot_sentences = defaultdict(list)   # slot -> [sentence, ...]
slot_by_genre = defaultdict(lambda: defaultdict(list))
first_sentences = []

for song in merged:
    genre = song.get("genre") or "미정"
    for sr in song.get("suno_reanalysis", []):
        sp = sr.get("sp") or ""
        sents = split_sentences(sp)
        if not sents:
            continue
        first_sentences.append(sents[0])
        for i, s in enumerate(sents):
            slot = classify_sentence(s, i, len(sents))
            slot_sentences[slot].append(s)
            slot_by_genre[slot][genre].append(s)

# --- 각 슬롯별 패턴/필러 추출 ---
def extract_templates(sentences, max_templates=30):
    """문장을 정규화해 반복 템플릿 추출."""
    tpls = Counter()
    for s in sentences:
        t = s.lower()
        t = re.sub(r"\b\d+\.?\d*\s*bpm\b", "<BPM>", t)
        t = re.sub(r"\b(in\s+the\s+key\s+of\s+)[a-g][#b♯♭]?\s*(major|minor)\b",
                    r"\1<KEY>", t)
        t = re.sub(r"\b[a-g][#b♯♭]?\s+(major|minor)\b", "<KEY>", t)
        t = re.sub(r"\b\d+/\d+\b", "<TIME>", t)
        t = re.sub(r"\b\d+\b", "<NUM>", t)
        tpls[t.strip()[:200]] += 1
    return dict(tpls.most_common(max_templates))

def extract_vocab(sentences, min_freq=2):
    """슬롯 내 주요 어휘(2-gram 이상 포함) 추출."""
    unigrams = Counter()
    bigrams = Counter()
    for s in sentences:
        toks = re.findall(r"[a-zA-Z][a-zA-Z\-']+", s.lower())
        for w in toks:
            if len(w) > 2:
                unigrams[w] += 1
        for i in range(len(toks) - 1):
            bigrams[f"{toks[i]} {toks[i+1]}"] += 1
    vocab = {}
    for w, c in unigrams.most_common(50):
        if c >= min_freq:
            vocab[w] = c
    for bg, c in bigrams.most_common(50):
        if c >= min_freq:
            vocab[bg] = c
    return dict(sorted(vocab.items(), key=lambda x: -x[1])[:60])

def pick_examples(sentences, n=5):
    """다양한 예문 선택."""
    seen = set()
    examples = []
    for s in sentences:
        key = s[:60].lower()
        if key not in seen:
            seen.add(key)
            examples.append(s)
        if len(examples) >= n:
            break
    return examples


# --- 장르 선언 서브분석 ---
genre_label_patterns = Counter()
for s in slot_sentences.get("genre_declaration", []):
    sl = s.lower().rstrip(".")
    # "K-Pop ballad with R&B influences" → base = "K-Pop ballad", modifier = "with R&B influences"
    m = re.match(r"(.+?)\s+(with|featuring)\s+(.+)", sl)
    if m:
        genre_label_patterns[f"{m.group(1).strip()} + [{m.group(2)}] modifier"] += 1
    else:
        genre_label_patterns[sl] += 1

# --- 보컬 서브슬롯 추출 ---
voice_types = Counter()
vocal_deliveries = Counter()
vocal_processing = Counter()

VOICE_TYPE_RE = re.compile(
    r"(breathy\s+(?:female|male|intimate)\s+(?:vocals?)?|"
    r"(?:male|female)\s+(?:tenor|baritone|soprano|alto)\s+(?:vocals?)?|"
    r"(?:baritone|tenor|soprano|alto)\s+(?:male|female)\s+(?:vocals?)?|"
    r"(?:smooth|soft|warm)\s+(?:male|female)\s+(?:vocals?)?)", re.I)

for s in slot_sentences.get("vocals", []):
    for m in VOICE_TYPE_RE.finditer(s):
        voice_types[m.group().lower().strip()] += 1
    # delivery words
    for d in ["breathy", "intimate", "conversational", "melodic", "smooth",
              "rhythmic", "percussive", "emotive", "soft", "powerful"]:
        if d in s.lower():
            vocal_deliveries[d] += 1
    # processing
    for p in ["plate reverb", "room reverb", "delay", "doubling", "pitch correction",
              "vibrato", "centered in the mix", "minimal vibrato", "light reverb"]:
        if p in s.lower():
            vocal_processing[p] += 1

# --- 악기 추출 ---
instruments = Counter()
INSTRUMENT_PATTERNS = [
    r"(clean electric guitar|acoustic guitar|electric guitar|bass guitar|"
    r"grand piano|electric piano|synth bass|sub-bass synth|"
    r"slap bass|upright bass|muted trumpet|string section|"
    r"synth(?:esizer)? pads?|organ|rhodes|saxophone|clarinet|"
    r"cello|violin|harp|flute)"
]
INST_RE = re.compile("|".join(INSTRUMENT_PATTERNS), re.I)

for s in slot_sentences.get("instrument_layers", []):
    for m in INST_RE.finditer(s):
        instruments[m.group().lower()] += 1

# --- 드럼 요소 추출 ---
drum_elements = Counter()
DRUM_EL_RE = re.compile(
    r"((?:dry|tight|punchy|soft|crisp|muted|electronic)\s+kick(?:\s+drum)?|"
    r"(?:crisp|tight|electronic|acoustic)\s+snare|"
    r"(?:crisp|bright|closed|open)\s+hi-hats?|"
    r"(?:subtle|light)?\s*(?:electronic\s+)?clap(?:\s+layer)?|"
    r"shaker|tambourine|rimshot|cymbal|brushes)", re.I)

for s in slot_sentences.get("drums", []):
    for m in DRUM_EL_RE.finditer(s):
        drum_elements[m.group().lower().strip()] += 1

# --- 결과 조립 ---
SLOT_ORDER = [
    "genre_declaration",
    "instrument_layers",
    "drums",
    "vocals",
    "tempo_key_time",
    "production",
    "arrangement_summary",
]

SLOT_DEFS = {
    "genre_declaration": {
        "position": "first_sentence",
        "required": True,
        "description": "장르 선언. Suno가 첫 문장에서 장르 라벨을 제시하는 슬롯.",
    },
    "instrument_layers": {
        "position": "body (복수 문장, 순서 비고정)",
        "required": True,
        "description": "악기/어레인지먼트 레이어. 각 악기의 연주 패턴·이펙트·역할 기술.",
    },
    "drums": {
        "position": "body",
        "required": False,
        "description": "드럼/퍼커션 전용 기술. 킥·스네어·하이햇·셰이커 등 타격음 구성.",
    },
    "vocals": {
        "position": "body",
        "required": False,
        "description": "보컬 타입·딜리버리·프로세싱. 음역·발성법·이펙트 기술.",
    },
    "tempo_key_time": {
        "position": "late (보통 후반부)",
        "required": True,
        "description": "템포(BPM)·조성(Key)·박자(Time signature). 구문 템플릿이 고정적.",
    },
    "production": {
        "position": "body or late",
        "required": False,
        "description": "프로덕션/믹스 특성. 리버브 타입, 마이크 배치, 전체 공간감 기술.",
    },
    "arrangement_summary": {
        "position": "last_sentence (주로)",
        "required": False,
        "description": "어레인지먼트 총평. 'The arrangement is sparse/dense, focusing on...' 패턴.",
    },
}

result = {
    "version": "v2.0",
    "source": "sunolanguage 326 clips (318 unique songs)",
    "description": "Suno SP 7-슬롯 묘사 문법. leomusic2 SP 생성기 참조용.",
    "slot_order": SLOT_ORDER,
    "total_sentences_analyzed": sum(len(v) for v in slot_sentences.values()),
    "slots": {},
}

for slot in SLOT_ORDER:
    sents = slot_sentences.get(slot, [])
    d = {
        **SLOT_DEFS[slot],
        "sentence_count": len(sents),
        "templates": extract_templates(sents),
        "vocabulary": extract_vocab(sents),
        "examples": pick_examples(sents, n=5),
    }

    # 슬롯별 서브데이터
    if slot == "genre_declaration":
        d["top_genre_labels"] = dict(genre_label_patterns.most_common(30))
    elif slot == "instrument_layers":
        d["instruments_detected"] = dict(instruments.most_common(30))
    elif slot == "drums":
        d["drum_elements"] = dict(drum_elements.most_common(20))
    elif slot == "vocals":
        d["voice_types"] = dict(voice_types.most_common(20))
        d["delivery_styles"] = dict(vocal_deliveries.most_common(15))
        d["processing"] = dict(vocal_processing.most_common(15))

    result["slots"][slot] = d

# --- 가사 브래킷도 포함 (leomusic2 가사 생성 시 참조) ---
brackets_file = Path("/Users/leo/sunolanguage/data/reanalysis_v2/recon_lyrics_brackets.json")
if brackets_file.exists():
    bdata = json.loads(brackets_file.read_text())
    bracket_summary = {
        "total_occurrences": bdata["entries_total"],
        "top_brackets": dict(list(bdata["top_frequencies"].items())[:50]),
        "by_type": {},
    }
    for t, counts in bdata["by_type_guess_counts"].items():
        top_items = dict(list(counts.items())[:30])
        bracket_summary["by_type"][t] = {
            "unique_count": len(counts),
            "total_occurrences": sum(counts.values()),
            "top_entries": top_items,
        }
    result["lyrics_bracket_system"] = bracket_summary

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(f"출력: {OUT}")
print(f"총 분석 문장: {result['total_sentences_analyzed']}")
print()
for slot in SLOT_ORDER:
    s = result["slots"][slot]
    print(f"  {slot}: {s['sentence_count']}문장 / 템플릿 {len(s['templates'])}개 / 어휘 {len(s['vocabulary'])}개")
