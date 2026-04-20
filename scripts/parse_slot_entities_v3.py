#!/usr/bin/env python3
"""
Suno SP + 가사 브래킷 → 슬롯별 entity + modifier + pattern 파싱 v3

각 슬롯 항목을:
  - entity: 핵심 대상 (snare, electric guitar, male vocals 등)
  - modifiers: 수식어 (crisp, tight, warm 등)
  - pattern: 연주/동작 패턴 (on the backbeat, arpeggiated chords 등)
  - effects: 적용된 이펙트 (light chorus, plate reverb 등)
  - sentence: 원문
으로 분해
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path

DATA = json.loads(Path("data/reanalysis_v2/merged_4values.json").read_text())

# ─────────────────────────────────────────
# 엔티티 사전
# ─────────────────────────────────────────

# 악기 엔티티 (구체적 → 포괄적 순서로 매칭)
INSTRUMENT_ENTITIES = [
    ("fingerpicked acoustic guitar", re.compile(r"fingerpicked acoustic guitar", re.I)),
    ("fingerstyle acoustic guitar", re.compile(r"fingerstyle acoustic guitar", re.I)),
    ("nylon-string acoustic guitar", re.compile(r"nylon[- ]string acoustic guitar", re.I)),
    ("12-string acoustic guitar", re.compile(r"12-string acoustic guitar", re.I)),
    ("strummed acoustic guitar", re.compile(r"strummed acoustic guitar", re.I)),
    ("steel-string acoustic guitar", re.compile(r"steel[- ]string acoustic guitar", re.I)),
    ("acoustic guitar", re.compile(r"acoustic guitar", re.I)),
    ("clean electric guitar", re.compile(r"clean electric guitar", re.I)),
    ("distorted electric guitar", re.compile(r"distorted electric guitar", re.I)),
    ("overdriven electric guitar", re.compile(r"overdriven electric guitar", re.I)),
    ("palm-muted electric guitar", re.compile(r"palm[- ]muted electric guitar", re.I)),
    ("arpeggiated electric guitar", re.compile(r"arpeggiated electric guitar", re.I)),
    ("electric guitar", re.compile(r"electric guitar", re.I)),
    ("guitar", re.compile(r"\bguitar\b", re.I)),
    ("slap bass", re.compile(r"slap bass", re.I)),
    ("upright bass", re.compile(r"upright bass", re.I)),
    ("fretless bass", re.compile(r"fretless bass", re.I)),
    ("synth bass", re.compile(r"(?:synth[- ]?bass|bass synth)", re.I)),
    ("sub-bass", re.compile(r"sub[- ]?bass(?:\s+synth)?", re.I)),
    ("808 bass", re.compile(r"808(?:\s+(?:sub[- ]?)?bass)?", re.I)),
    ("electric bass", re.compile(r"(?:electric |clean electric )?bass(?:\s+guitar)?(?!\s*(?:synth|drum))", re.I)),
    ("bass guitar", re.compile(r"bass\s+guitar", re.I)),
    ("grand piano", re.compile(r"grand piano", re.I)),
    ("acoustic piano", re.compile(r"acoustic piano", re.I)),
    ("electric piano", re.compile(r"electric piano", re.I)),
    ("piano", re.compile(r"\bpiano\b", re.I)),
    ("rhodes", re.compile(r"\brhodes\b", re.I)),
    ("hammond organ", re.compile(r"hammond organ", re.I)),
    ("organ", re.compile(r"\borgan\b", re.I)),
    ("synthesizer", re.compile(r"\bsynth(?:esizer)?s?\b(?!\s*bass)", re.I)),
    ("synth pad", re.compile(r"synth\s+pads?", re.I)),
    ("string pad", re.compile(r"string\s+pads?", re.I)),
    ("pad", re.compile(r"\bpads?\b", re.I)),
    ("keyboard", re.compile(r"\bkeyboard\b", re.I)),
    ("keys", re.compile(r"\bkeys\b(?!\s+of)", re.I)),
    ("orchestral strings", re.compile(r"orchestral strings", re.I)),
    ("strings", re.compile(r"\bstrings\b", re.I)),
    ("violin", re.compile(r"\bviolin\b", re.I)),
    ("cello", re.compile(r"\bcello\b", re.I)),
    ("harp", re.compile(r"\bharp\b", re.I)),
    ("flute", re.compile(r"\bflute\b", re.I)),
    ("muted trumpet", re.compile(r"muted trumpet", re.I)),
    ("trumpet", re.compile(r"\btrumpet\b", re.I)),
    ("saxophone", re.compile(r"(?:alto |tenor |soprano )?(?:saxophone|sax)\b", re.I)),
    ("trombone", re.compile(r"\btrombone\b", re.I)),
    ("clarinet", re.compile(r"\bclarinet\b", re.I)),
    ("brass section", re.compile(r"brass\s+(?:section|stabs?|accents?|hits?)", re.I)),
    ("brass", re.compile(r"\bbrass\b", re.I)),
    ("harmonica", re.compile(r"\bharmonica\b", re.I)),
    ("accordion", re.compile(r"\baccordion\b", re.I)),
    ("ukulele", re.compile(r"\bukulele\b", re.I)),
    ("mandolin", re.compile(r"\bmandolin\b", re.I)),
    ("banjo", re.compile(r"\bbanjo\b", re.I)),
    ("vibraphone", re.compile(r"\bvibraphone\b", re.I)),
    ("glockenspiel", re.compile(r"\bglockenspiel\b", re.I)),
]

DRUM_ENTITIES = [
    ("kick drum", re.compile(r"(?:soft |muted |punchy |heavy |tight |electronic )?kick(?:\s+drum)?", re.I)),
    ("snare drum", re.compile(r"(?:crisp |tight |dry |electronic |brushed )?snare(?:\s+drum)?", re.I)),
    ("hi-hat", re.compile(r"(?:open |closed |sixteenth-note )?hi-hats?", re.I)),
    ("ride cymbal", re.compile(r"ride\s+cymbal", re.I)),
    ("crash cymbal", re.compile(r"crash\s+cymbals?", re.I)),
    ("cymbal", re.compile(r"\bcymbals?\b", re.I)),
    ("tom", re.compile(r"\btoms?\b", re.I)),
    ("shaker", re.compile(r"\bshakers?\b", re.I)),
    ("tambourine", re.compile(r"\btambourine\b", re.I)),
    ("cowbell", re.compile(r"\bcowbell\b", re.I)),
    ("woodblock", re.compile(r"\bwoodblock\b", re.I)),
    ("clap", re.compile(r"\b(?:hand)?claps?\b", re.I)),
    ("finger snap", re.compile(r"finger\s*snaps?\b", re.I)),
    ("rimshot", re.compile(r"\brimshot\b", re.I)),
    ("cross-stick", re.compile(r"cross[- ]?stick", re.I)),
    ("congas", re.compile(r"\bcongas?\b", re.I)),
    ("bongos", re.compile(r"\bbongos?\b", re.I)),
    ("cajon", re.compile(r"\bcajon\b", re.I)),
    ("drum kit", re.compile(r"(?:acoustic |electronic )?drum\s+(?:kit|machine|set)", re.I)),
    ("drums", re.compile(r"\bdrums?\b", re.I)),
    ("percussion", re.compile(r"\bpercussion\b", re.I)),
    ("beat", re.compile(r"\b(?:pop |rock |driving |trap )?beat\b", re.I)),
]

# ─────────────────────────────────────────
# Instrument 3계 분할: kit / layer / role (2026-04-20)
# ─────────────────────────────────────────
INSTRUMENT_FAMILY = {
    # guitar
    "fingerpicked acoustic guitar": "guitar",
    "fingerstyle acoustic guitar": "guitar",
    "nylon-string acoustic guitar": "guitar",
    "12-string acoustic guitar": "guitar",
    "strummed acoustic guitar": "guitar",
    "steel-string acoustic guitar": "guitar",
    "acoustic guitar": "guitar",
    "clean electric guitar": "guitar",
    "distorted electric guitar": "guitar",
    "overdriven electric guitar": "guitar",
    "palm-muted electric guitar": "guitar",
    "arpeggiated electric guitar": "guitar",
    "electric guitar": "guitar",
    "guitar": "guitar",
    "ukulele": "guitar",
    "mandolin": "guitar",
    "banjo": "guitar",
    # bass
    "slap bass": "bass",
    "upright bass": "bass",
    "fretless bass": "bass",
    "synth bass": "bass",
    "sub-bass": "bass",
    "808 bass": "bass",
    "electric bass": "bass",
    "bass guitar": "bass",
    # keys
    "grand piano": "keys",
    "acoustic piano": "keys",
    "electric piano": "keys",
    "piano": "keys",
    "rhodes": "keys",
    "hammond organ": "keys",
    "organ": "keys",
    "keyboard": "keys",
    "keys": "keys",
    # synth
    "synthesizer": "synth",
    "synth pad": "synth",
    "string pad": "synth",
    "pad": "synth",
    # strings
    "orchestral strings": "strings",
    "strings": "strings",
    "violin": "strings",
    "cello": "strings",
    "harp": "strings",
    # brass (+ reeds/woodwinds 흡수)
    "muted trumpet": "brass",
    "trumpet": "brass",
    "saxophone": "brass",
    "trombone": "brass",
    "clarinet": "brass",
    "brass section": "brass",
    "brass": "brass",
    "flute": "brass",
    # other
    "harmonica": "other",
    "accordion": "other",
    "vibraphone": "other",
    "glockenspiel": "other",
}

# Layer 판별: lead / rhythm / bass / pad / fill (counter 제거)
LAYER_LEAD_RE = re.compile(
    r"\b(lead\s+(?:line|melody|guitar|synth|riff)|melodic\s+lead|"
    r"plays?\s+(?:a|the)\s+(?:main\s+)?melody|"
    r"melodic\s+line|carries?\s+the\s+melody|lead\b)", re.I)
LAYER_RHYTHM_RE = re.compile(
    r"\b(rhythm\s+(?:guitar|part)|strums?\b|strumm\w+|"
    r"comps?\b|comping|chord\s+progression|"
    r"plays?\s+(?:jazz\s+|open\s+|power\s+|block\s+)?chords?|"
    r"rhythmic\s+(?:strumming|comp\w*))", re.I)
LAYER_PAD_RE = re.compile(
    r"\b(pads?\b|sustained\s+(?:chord|texture|note|string)|"
    r"background\s+(?:texture|pad)|atmospheric\s+(?:texture|layer|pad)|"
    r"legato\s+(?:string|pad)|harmonic\s+padding|"
    r"ambient\s+(?:texture|layer|pad))", re.I)
LAYER_FILL_RE = re.compile(
    r"\b(fills?\b|filling|transitional\s+(?:lick|run|fill)|"
    r"brief\s+lick|ornamentation|ornamental\s+(?:run|line))", re.I)

# Role 판별 (7 role + role_detail)
ROLE_PATTERNS = [
    ("groove_lock", re.compile(
        r"\b(?:follows?|following|locks?\s+(?:with|in)|locked\s+(?:to|with)|"
        r"syncs?\s+with|grooves?\s+with)\b", re.I)),
    ("support", re.compile(
        r"\b(?:provides?|providing|supports?|supporting|"
        r"underpins?|anchors?|accompanies)\b", re.I)),
    ("fill", re.compile(
        r"\b(?:fills?|filling)\b(?!\s+the\s+mix)", re.I)),
    ("layer_on", re.compile(
        r"\b(?:layers?|layering|doubles?|doubled|"
        r"adds?\s+(?:a|an|some|additional)|stacks?)\b", re.I)),
    ("lead_out", re.compile(
        r"\b(?:leads?\s+(?:the|with)|carries?\s+(?:the|a)|"
        r"outlines?\s+(?:the|a)|drives?\s+(?:the|a))\b", re.I)),
    ("sustain", re.compile(
        r"\b(?:holds?|holding|sustains?|sustained|drones?|droning)\b", re.I)),
    ("execute", re.compile(
        r"\b(?:plays?|playing|delivers?|delivering|performs?|performing)\b", re.I)),
]

# role_detail: execute의 수식어·패턴 보조 태그
ROLE_DETAIL_PATTERNS = [
    (w, re.compile(rf"\b{re.escape(w)}\b", re.I))
    for w in (
        "syncopated", "melodic", "rhythmic", "percussive",
        "jazz", "funk", "rock", "folk",
        "eighth-note", "sixteenth-note", "quarter-note",
        "four-to-the-floor", "driving", "laid-back", "steady",
        "palm-muted", "strummed", "fingerpicked", "arpeggiated",
    )
]


def classify_family(entity: str) -> str:
    """악기 엔티티 → family (8개, 미매핑은 'other')."""
    return INSTRUMENT_FAMILY.get(entity.lower(), "other")


def classify_layer(sent: str, family: str) -> str:
    """문장 + family → layer (lead/rhythm/bass/pad/fill/unspecified)."""
    s = sent or ""
    if LAYER_LEAD_RE.search(s):
        return "lead"
    if LAYER_PAD_RE.search(s):
        return "pad"
    if LAYER_FILL_RE.search(s):
        return "fill"
    if family == "bass":
        return "bass"
    if LAYER_RHYTHM_RE.search(s):
        return "rhythm"
    return "unspecified"


def classify_role(sent: str):
    """문장 주동사 → (role, role_details)."""
    s = sent or ""
    role = "unspecified"
    for r, pat in ROLE_PATTERNS:
        if pat.search(s):
            role = r
            break
    details = []
    if role == "execute":
        for name, pat in ROLE_DETAIL_PATTERNS:
            if pat.search(s):
                details.append(name)
    return role, details


VOCAL_ENTITIES = [
    ("male tenor vocals", re.compile(r"male\s+tenor\s+vocals?\b", re.I)),
    ("male baritone vocals", re.compile(r"(?:male\s+)?baritone\s+(?:male\s+)?vocals?\b", re.I)),
    ("female soprano vocals", re.compile(r"female\s+soprano\s+vocals?\b", re.I)),
    ("female vocals", re.compile(r"female\s+vocals?\b", re.I)),
    ("male vocals", re.compile(r"male\s+vocals?\b", re.I)),
    ("male rapper", re.compile(r"male\s+rapper", re.I)),
    ("female vocalist", re.compile(r"female\s+vocalist", re.I)),
    ("male vocalist", re.compile(r"male\s+vocalist", re.I)),
    ("vocalist", re.compile(r"\bvocalist\b", re.I)),
    ("vocals", re.compile(r"\bvocals?\b", re.I)),
    ("voice", re.compile(r"\bvoice\b", re.I)),
    ("rapper", re.compile(r"\brapper\b", re.I)),
    ("singer", re.compile(r"\bsinger\b", re.I)),
    ("falsetto", re.compile(r"\bfalsetto\b", re.I)),
    ("vocalizing", re.compile(r"\bvocaliz\w+\b", re.I)),
    ("rap delivery", re.compile(r"\b(?:rhythmic\s+)?(?:male\s+)?rap(?:\s+delivery)?\b", re.I)),
    ("singing", re.compile(r"\b(?:melodic\s+)?singing\b", re.I)),
]

# ─────────────────────────────────────────
# 수식어 사전
# ─────────────────────────────────────────
TONE_MODIFIERS = {
    "warm", "bright", "dark", "mellow", "crisp", "punchy", "round", "rounded",
    "sharp", "thick", "thin", "rich", "full", "deep", "airy", "silky",
    "gritty", "raw", "organic", "clean", "dirty", "muddy", "boomy",
    "shimmering", "glitchy", "lo-fi", "hi-fi", "vintage", "modern",
    "classic", "analog", "digital", "synthetic", "natural",
    "soft", "hard", "heavy", "light", "gentle",
    "smooth", "rough", "coarse", "delicate",
    "funky", "jazzy", "soulful", "bluesy",
    "atmospheric", "ethereal", "dreamy", "spacious",
    "intimate", "close", "distant",
    "dry", "wet",
    "polished", "refined", "processed", "unprocessed",
    "compressed", "saturated",
    "resonant", "muted",
    "clean-toned", "high-pitched", "low-pitched",
    "sub-heavy",
}

INTENSITY_MODIFIERS = {
    "subtle", "slight", "light", "moderate", "heavy", "prominent", "dominant",
    "minimal", "maximal", "aggressive", "gentle", "soft", "loud",
    "energetic", "driving", "relaxed", "laid-back", "upbeat",
    "powerful", "delicate", "fierce", "calm",
    "high-energy", "low-energy",
}

TEMPORAL_MODIFIERS = {
    "steady", "consistent", "repetitive", "occasional", "frequent",
    "constant", "intermittent", "sporadic", "continuous",
    "rapid", "rapid-fire", "slow", "fast",
    "gradual", "sudden", "brief",
}

SPATIAL_MODIFIERS = {
    "wide", "narrow", "centered", "panned", "forward", "back",
    "stereo", "mono",
    "high", "low", "mid", "mid-range",
    "sparse", "dense", "lush", "tight", "loose",
}

ALL_MODIFIERS = TONE_MODIFIERS | INTENSITY_MODIFIERS | TEMPORAL_MODIFIERS | SPATIAL_MODIFIERS

# ─────────────────────────────────────────
# 패턴 추출
# ─────────────────────────────────────────
PLAYING_PATTERNS = re.compile(
    r"(plays?|performs?|provides?|delivers?|follows?|drives?|maintains?|creates?|"
    r"utiliz\w+|featur\w+|consist\w+|enters?|hits?|locks?\s+with)\s+"
    r"(.{5,80}?)(?:\.|,\s+(?:with|and|featuring|creating|locking)|\s*$)",
    re.I
)

EFFECT_PHRASES = re.compile(
    r"(?:with|and|featuring|using|processed with|applied)\s+"
    r"((?:light |subtle |moderate |heavy |short |long |wide )?"
    r"(?:chorus|reverb|delay|distortion|overdrive|phaser|flanger|"
    r"compression|plate reverb|room reverb|hall reverb|spring reverb|"
    r"pitch correction|auto-?tune|feedback|echo|vibrato|tremolo|"
    r"chorus effect|doubling|EQ|sidechain)"
    r"(?:\s+and\s+(?:light |subtle |moderate )?"
    r"(?:chorus|reverb|delay|distortion|compression|EQ))?)",
    re.I
)

CHORD_PHRASES = re.compile(
    r"(arpeggiated chords?|sustained chords?|power chords?|"
    r"jazz chords?|block chords?|open chords?|"
    r"chord progressions?|seventh chords?|ninth chords?|"
    r"minor seventh|major seventh|"
    r"jazz voicings?|voicings?|"
    r"harmonic (?:support|depth|density|texture|padding|sustain|fill\w*|"
    r"accompaniment|structure|movement|backing|wash|warmth|thickening|accents))",
    re.I
)

DELIVERY_PHRASES = re.compile(
    r"((?:breathy|smooth|conversational|intimate|rhythmic|melodic|"
    r"percussive|energetic|aggressive|gentle|relaxed|"
    r"soulful|emotive|emotional|storytelling|"
    r"laid-back|syncopated|staccato|legato|"
    r"powerful|soft|warm|airy|raspy|gritty|husky|nasal)"
    r"(?:,?\s+(?:and\s+)?(?:breathy|smooth|conversational|intimate|"
    r"rhythmic|melodic|percussive|emotional|soulful))*"
    r"\s+(?:delivery|vocal|vocals|singing|style|tone|performance))",
    re.I
)

# ─────────────────────────────────────────
# 문장 파싱
# ─────────────────────────────────────────
def extract_modifiers(sentence):
    words = re.findall(r"[a-z][\w\-]*", sentence.lower())
    return [w for w in words if w in ALL_MODIFIERS]

def extract_effects(sentence):
    found = []
    for m in EFFECT_PHRASES.finditer(sentence):
        found.append(m.group(1).strip())
    return found

def extract_chords(sentence):
    found = []
    for m in CHORD_PHRASES.finditer(sentence):
        found.append(m.group(1).strip().lower())
    return found

def extract_pattern(sentence):
    m = PLAYING_PATTERNS.search(sentence)
    if m:
        return m.group(2).strip().rstrip(".,")
    return ""

def find_entities(sentence, entity_list):
    found = []
    sl = sentence
    for name, pat in entity_list:
        if pat.search(sl):
            found.append(name)
    # 구체적 엔티티가 있으면 포괄적 제거
    if len(found) > 1:
        generic = {"guitar", "drums", "percussion", "cymbal", "pad",
                   "piano", "vocals", "voice", "brass", "keys"}
        specifics = [f for f in found if f not in generic]
        if specifics:
            found = specifics + [f for f in found if f in generic and
                                 not any(f in s for s in specifics)]
    return found


# ─────────────────────────────────────────
# 슬롯 분류 (v2 기반 + entity 파싱)
# ─────────────────────────────────────────
GENRE_RE = re.compile(
    r"^(k-pop|k-indie|k-hip\s*hop|k-ballad|k-rock|k-r&b|"
    r"korean|j-rock|j-pop|"
    r"pop|rock|jazz|r&b|hip[- ]?hop|electronic|ambient|folk|"
    r"indie|ballad|soul|funk|disco|synth|city\s*pop|bossa|"
    r"punk|metal|blues|country|reggae|lo-?fi|boom\s*bap|"
    r"cinematic|orchestral|dream\s*pop|shoegaze|chillwave|"
    r"future\s*bass|trap|EDM|house|techno|dnb|drill)", re.I)

TEMPO_RE = re.compile(
    r"\b(tempo\b|bpm|\d+\s*bpm|key of|key is|key:|key\s*[A-G]|"
    r"time signature|\d+/\d+\s*time|in\s+\d+/\d+)\b", re.I)

MIXING_RE = re.compile(
    r"\b(close-mic\w*|mic\s+position\w*|stereo\s+imag\w*|"
    r"panning|panned|compression|compressor|"
    r"EQ\b|equali[sz]\w+|sidechain|"
    r"forward\s+in\s+the\s+mix|centered\s+in\s+the\s+mix|"
    r"sits?\s+forward|sits?\s+back\b|"
    r"in\s+the\s+mix|"
    r"high-?fidelity|lo-?fi\s+production|"
    r"analog\s+warmth|tape\s+saturation|"
    r"clean\s+production|polished\s+production|"
    r"processed|processing|"
    r"stereo\s+width|mono\b|proximity|"
    r"gain\s+stag\w*|headroom)\b", re.I)

# 마스터링: mixing과 분리. Suno의 "빈 슬롯" 발견 자체가 책 5장 근거.
MASTERING_RE = re.compile(
    r"\b(limiter|limiting|LUFS|loudness|"
    r"multiband\s+compress\w*|brickwall|brick-wall|"
    r"maximizer|mastering\s+chain|master\s+bus|"
    r"loudness\s+war|peak\s+normalization|"
    r"RMS\b|K-weighting|true\s*peak|"
    r"mastering\b|mastered\b)\b", re.I)

# 화성: chord progression, voicing, 화성 분석 어휘
HARMONY_RE = re.compile(
    r"\b(chord\s+progression|secondary\s+dominant|modal\s+interchange|"
    r"tonicization|jazz\s+chord\s+progression|"
    r"I-IV-V|ii-V-I|ii\s*-\s*V\s*-\s*I|"
    r"diatonic|neapolitan|tritone\s+substitut\w+|"
    r"modulation|modulates?\s+to|borrowed\s+chord|passing\s+chord|"
    r"suspended\s+chord|sus\s*chord|"
    r"major\s+seventh|minor\s+seventh|dominant\s+seventh|"
    r"ninth\s+chord|eleventh\s+chord|thirteenth\s+chord|"
    r"extension\s+chord|"
    r"harmonic\s+progression|harmonic\s+movement|"
    r"circle\s+of\s+fifths|"
    r"relative\s+(?:major|minor)|"
    r"cadence|plagal\s+cadence|authentic\s+cadence|deceptive\s+cadence)\b",
    re.I)

EFFECT_RE = re.compile(
    r"\b(reverb|delay|echo|chorus\s+effect|chorus\s+pedal|"
    r"light\s+chorus|with\s+chorus|and\s+chorus|subtle\s+chorus|"
    r"distort\w+|overdrive|overdriven|fuzz|"
    r"phaser|flanger|wah|tremolo\s+(?:effect|pedal)|"
    r"filter\s+sweep|high-?pass\s+filter|low-?pass\s+filter|"
    r"pitch\s+correction|auto[- ]?tune|"
    r"plate\s+reverb|room\s+reverb|hall\s+reverb|spring\s+reverb|"
    r"short\s+reverb|long\s+reverb|"
    r"slap-?back\s+delay|ping-?pong\s+delay|"
    r"feedback\s+(?:loop|swell))\b", re.I)

SOUND_FX_RE = re.compile(
    r"\b(vinyl\s+crackle|record\s+scratch|static|noise\s+layer|"
    r"clock[- ]?tick\w*|machine\s+sound|mechanical|"
    r"ambient\s+(?:noise|sound|texture)|"
    r"sound\s+effect|swoosh|riser|sweep|shutter|"
    r"tape\s+hiss|white\s+noise|"
    r"foley|water\s+drop\w*|dripping|hum\b|muffled)\b", re.I)

ARRANGEMENT_RE = re.compile(
    r"\b(arrangement\b|focusing\s+on|interplay\b|"
    r"sparse\b|dense\b|minimalist\b|lush\b|intimate\b|"
    r"wall[- ]of[- ]sound|full\s+band|stripped[- ]?back|"
    r"builds?\s+(?:from|to|into|toward)|crescendo|"
    r"transitions?\s+(?:from|to|into))\b", re.I)

ABSENCE_RE = re.compile(
    r"\b(no\s+percussion|no\s+drums?|no\s+bass|"
    r"without\s+(?:percussion|drum|bass|additional)|"
    r"(?:is\s+)?absent|stripped|drops?\s+out|"
    r"cuts?\s+out|fades?\s+out|stops?\s+briefly|"
    r"solo\s+(?:male|female|vocal|piano|guitar|violin|cello))\b", re.I)

VOCAL_CHORUS_RE = re.compile(
    r"\b(doubling|doubled|double[- ]?track\w*|"
    r"layered\s+vocal|vocal\s+layer|vocal\s+stack|"
    r"backing\s+vocal|background\s+vocal|"
    r"vocal\s+harmon\w+|harmonies|"
    r"choir|choral|unison|call[- ]and[- ]response|"
    r"ad[- ]?libs?|adlib)\b", re.I)


def parse_sp_sentence(sent, idx, total):
    """SP 문장 → 슬롯 엔트리 목록 반환."""
    sl = sent.lower()
    entries = []
    modifiers = extract_modifiers(sent)
    effects = extract_effects(sent)
    chords = extract_chords(sent)
    pattern = extract_pattern(sent)

    # 장르
    if idx == 0 and GENRE_RE.search(sl):
        entries.append({
            "slot": "genre",
            "entity": sent.rstrip(".").strip(),
            "modifiers": [],
            "pattern": "",
            "effects": [],
            "chords": [],
            "sentence": sent,
        })

    # 악기 (+ 3계 분할: kit / layer / role)
    instruments = find_entities(sent, INSTRUMENT_ENTITIES)
    for inst in instruments:
        kit = classify_family(inst)
        layer = classify_layer(sent, kit)
        role, role_details = classify_role(sent)
        entries.append({
            "slot": "instrument",
            "entity": inst,
            "kit": kit,
            "layer": layer,
            "role": role,
            "role_details": role_details,
            "modifiers": modifiers,
            "pattern": pattern,
            "effects": effects,
            "chords": chords,
            "sentence": sent,
        })

    # 드럼
    drum_parts = find_entities(sent, DRUM_ENTITIES)
    if drum_parts:
        entries.append({
            "slot": "drums",
            "entity": drum_parts,
            "modifiers": modifiers,
            "pattern": pattern,
            "effects": effects,
            "chords": [],
            "sentence": sent,
        })

    # 보컬 메인
    vocal_ents = find_entities(sent, VOCAL_ENTITIES)
    if vocal_ents:
        delivery = DELIVERY_PHRASES.findall(sent)
        entries.append({
            "slot": "vocal_main",
            "entity": vocal_ents,
            "modifiers": modifiers,
            "pattern": pattern,
            "effects": effects,
            "chords": [],
            "delivery": [d.strip() for d in delivery] if delivery else [],
            "sentence": sent,
        })

    # 보컬 코러스
    if VOCAL_CHORUS_RE.search(sl):
        entries.append({
            "slot": "vocal_chorus",
            "entity": VOCAL_CHORUS_RE.findall(sl),
            "modifiers": modifiers,
            "sentence": sent,
        })

    # 템포/조성
    if TEMPO_RE.search(sl):
        bpm = re.search(r"(\d+)\s*bpm", sl, re.I)
        key = re.search(r"key\s+(?:of\s+|is\s+|:\s*)?([a-g][#b]?\s*(?:major|minor))", sl, re.I)
        time_sig = re.search(r"(\d+/\d+)\s*time", sl, re.I)
        entries.append({
            "slot": "tempo_key_time",
            "entity": {
                "bpm": int(bpm.group(1)) if bpm else None,
                "key": key.group(1).strip() if key else None,
                "time_signature": time_sig.group(1) if time_sig else None,
            },
            "modifiers": modifiers,
            "sentence": sent,
        })

    # 마스터링 (mixing 전에 체크 — 더 구체적 슬롯)
    if MASTERING_RE.search(sl):
        entries.append({
            "slot": "mastering",
            "entity": MASTERING_RE.findall(sl),
            "modifiers": modifiers,
            "sentence": sent,
        })

    # 화성
    if HARMONY_RE.search(sl):
        entries.append({
            "slot": "harmony",
            "entity": HARMONY_RE.findall(sl),
            "modifiers": modifiers,
            "chords": chords,
            "sentence": sent,
        })

    # 믹싱
    if MIXING_RE.search(sl):
        entries.append({
            "slot": "mixing",
            "entity": MIXING_RE.findall(sl),
            "modifiers": modifiers,
            "sentence": sent,
        })

    # 이펙터
    if EFFECT_RE.search(sl):
        entries.append({
            "slot": "effect_electronic",
            "entity": EFFECT_RE.findall(sl),
            "modifiers": modifiers,
            "sentence": sent,
        })

    # 사운드 이펙트
    if SOUND_FX_RE.search(sl):
        entries.append({
            "slot": "effect_sound",
            "entity": SOUND_FX_RE.findall(sl),
            "modifiers": modifiers,
            "sentence": sent,
        })

    # 편곡
    if ARRANGEMENT_RE.search(sl):
        arr_instruments = find_entities(sent, INSTRUMENT_ENTITIES)
        entries.append({
            "slot": "arrangement",
            "entity": ARRANGEMENT_RE.findall(sl),
            "modifiers": modifiers,
            "instruments_mentioned": arr_instruments,
            "sentence": sent,
        })

    # 없음
    if ABSENCE_RE.search(sl):
        entries.append({
            "slot": "absence",
            "entity": ABSENCE_RE.findall(sl),
            "modifiers": [],
            "sentence": sent,
        })

    # 미분류
    if not entries:
        entries.append({
            "slot": "unclassified",
            "entity": "",
            "modifiers": modifiers,
            "pattern": pattern,
            "effects": effects,
            "chords": chords,
            "sentence": sent,
        })

    return entries


# ─────────────────────────────────────────
# 가사 브래킷 파싱
# ─────────────────────────────────────────
SECTION_RE_B = re.compile(
    r"^(intro|verse|pre-?chorus|chorus|bridge|outro|hook|drop|"
    r"breakdown|interlude|instrumental|refrain|coda|end)"
    r"(?:\s*\d*|\s+(?:break|outro|intro|solo))?$", re.I)

TRANSITION_RE_B = re.compile(
    r"\b(enters?|drops?\s|fades?|builds?|swells?|cuts?|returns?|"
    r"intensif\w*|crescendo|strip\w*|resumes?|continues?|"
    r"opens?\s+up|increases?|rings?\s+out|counts?\s+in|"
    r"stops?|slides?|flourish\w*|scratche?s?)\b", re.I)

PRONUNCIATION_RE = re.compile(r"[a-z]+-[a-z]+", re.I)


def parse_bracket(text):
    """가사 브래킷 → 슬롯 엔트리 목록 반환."""
    bt = text.strip()
    bl = bt.lower()
    entries = []

    # 섹션 태그 (정확 매칭)
    if SECTION_RE_B.match(bl) or bl in ("chorus", "pre-chorus"):
        return [{"slot": "section", "entity": bt, "modifiers": [], "bracket": bt}]

    modifiers = extract_modifiers(bt)
    effects = extract_effects(bt)

    # 악기 (+ 3계 분할: kit / layer / role)
    instruments = find_entities(bt, INSTRUMENT_ENTITIES)
    for inst in instruments:
        kit = classify_family(inst)
        layer = classify_layer(bt, kit)
        role, role_details = classify_role(bt)
        entries.append({
            "slot": "instrument",
            "entity": inst,
            "kit": kit,
            "layer": layer,
            "role": role,
            "role_details": role_details,
            "modifiers": modifiers,
            "effects": effects,
            "action": "",
            "bracket": bt,
        })

    # 드럼
    drum_parts = find_entities(bt, DRUM_ENTITIES)
    if drum_parts:
        entries.append({
            "slot": "drums",
            "entity": drum_parts,
            "modifiers": modifiers,
            "bracket": bt,
        })

    # 보컬 메인
    vocal_ents = find_entities(bt, VOCAL_ENTITIES)
    if vocal_ents:
        entries.append({
            "slot": "vocal_main",
            "entity": vocal_ents,
            "modifiers": modifiers,
            "bracket": bt,
        })

    # 보컬 코러스
    if VOCAL_CHORUS_RE.search(bl):
        entries.append({
            "slot": "vocal_chorus",
            "entity": VOCAL_CHORUS_RE.findall(bl),
            "modifiers": modifiers,
            "bracket": bt,
        })

    # 전환 큐
    trans_match = TRANSITION_RE_B.findall(bl)
    if trans_match:
        for e in entries:
            e["action"] = trans_match[0].lower()
        if not entries:
            entries.append({
                "slot": "transition",
                "entity": trans_match,
                "modifiers": modifiers,
                "bracket": bt,
            })

    # 마스터링 (브래킷도 동일 체크)
    if MASTERING_RE.search(bl):
        entries.append({
            "slot": "mastering",
            "entity": MASTERING_RE.findall(bl),
            "modifiers": modifiers,
            "bracket": bt,
        })

    # 화성
    if HARMONY_RE.search(bl):
        entries.append({
            "slot": "harmony",
            "entity": HARMONY_RE.findall(bl),
            "modifiers": modifiers,
            "bracket": bt,
        })

    # 전자 이펙터
    if EFFECT_RE.search(bl):
        entries.append({
            "slot": "effect_electronic",
            "entity": EFFECT_RE.findall(bl),
            "modifiers": modifiers,
            "bracket": bt,
        })

    # 사운드 이펙트
    if SOUND_FX_RE.search(bl):
        entries.append({
            "slot": "effect_sound",
            "entity": SOUND_FX_RE.findall(bl),
            "modifiers": modifiers,
            "bracket": bt,
        })

    # 편곡
    if re.search(r"(full\s+band|full\s+arrangement|full\s+electronic|half-time|arrangement)", bl):
        entries.append({
            "slot": "arrangement",
            "entity": bt,
            "modifiers": modifiers,
            "bracket": bt,
        })

    # 없음/퇴장
    if ABSENCE_RE.search(bl):
        entries.append({
            "slot": "absence",
            "entity": ABSENCE_RE.findall(bl),
            "modifiers": [],
            "bracket": bt,
        })

    # 발음 지시
    if PRONUNCIATION_RE.search(bl) and not entries:
        entries.append({
            "slot": "pronunciation",
            "entity": bt,
            "modifiers": [],
            "bracket": bt,
        })

    # 미분류
    if not entries:
        entries.append({
            "slot": "unclassified",
            "entity": bt,
            "modifiers": modifiers,
            "bracket": bt,
        })

    return entries


# ─────────────────────────────────────────
# 전체 실행
# ─────────────────────────────────────────
all_sp_entries = []
all_bracket_entries = []
sp_slot_counts = Counter()
br_slot_counts = Counter()
instrument_details = defaultdict(lambda: {
    "count": 0, "modifiers": Counter(), "patterns": Counter(),
    "effects": Counter(), "chords": Counter()
})
drum_details = defaultdict(lambda: {"count": 0, "modifiers": Counter()})
vocal_details = {"modifiers": Counter(), "delivery": Counter(), "effects": Counter()}

# 브래킷용 통계
br_instrument_details = defaultdict(lambda: {
    "count": 0, "modifiers": Counter(), "actions": Counter()
})
br_drum_details = defaultdict(lambda: {"count": 0, "modifiers": Counter()})

for song in DATA:
    sid = song.get("song_id", 0)
    genre = song.get("genre", "")

    for sr in song.get("suno_reanalysis", []):
        # ── SP 파싱 ──
        sp = sr.get("sp", "")
        if sp:
            sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+", sp.strip()) if x.strip()]
            for i, sent in enumerate(sents):
                entries = parse_sp_sentence(sent, i, len(sents))
                for e in entries:
                    e["song_id"] = sid
                    e["genre"] = genre
                    e["source"] = "sp"
                    all_sp_entries.append(e)
                    sp_slot_counts[e["slot"]] += 1

                    if e["slot"] == "instrument":
                        inst = e["entity"]
                        d = instrument_details[inst]
                        d["count"] += 1
                        for m in e.get("modifiers", []):
                            d["modifiers"][m] += 1
                        if e.get("pattern"):
                            d["patterns"][e["pattern"][:60]] += 1
                        for ef in e.get("effects", []):
                            d["effects"][ef] += 1
                        for ch in e.get("chords", []):
                            d["chords"][ch] += 1
                    elif e["slot"] == "drums":
                        for dp in e.get("entity", []):
                            drum_details[dp]["count"] += 1
                            for m in e.get("modifiers", []):
                                drum_details[dp]["modifiers"][m] += 1
                    elif e["slot"] == "vocal_main":
                        for m in e.get("modifiers", []):
                            vocal_details["modifiers"][m] += 1
                        for dl in e.get("delivery", []):
                            vocal_details["delivery"][dl] += 1
                        for ef in e.get("effects", []):
                            vocal_details["effects"][ef] += 1

        # ── 가사 브래킷 파싱 ──
        lyr = sr.get("lyrics", "")
        if lyr:
            for m in re.finditer(r"\[([^\]]{1,200})\]", lyr):
                bt = m.group(1).strip()
                entries = parse_bracket(bt)
                for e in entries:
                    e["song_id"] = sid
                    e["genre"] = genre
                    e["source"] = "lyrics"
                    all_bracket_entries.append(e)
                    br_slot_counts[e["slot"]] += 1

                    if e["slot"] == "instrument":
                        inst = e["entity"]
                        bd = br_instrument_details[inst]
                        bd["count"] += 1
                        for mod in e.get("modifiers", []):
                            bd["modifiers"][mod] += 1
                        if e.get("action"):
                            bd["actions"][e["action"]] += 1
                    elif e["slot"] == "drums":
                        for dp in e.get("entity", []):
                            br_drum_details[dp]["count"] += 1
                            for mod in e.get("modifiers", []):
                                br_drum_details[dp]["modifiers"][mod] += 1

# ─────────────────────────────────────────
# 출력
# ─────────────────────────────────────────
OUT = Path("data/reanalysis_v2")

# 1. SP 엔트리
(OUT / "sp_entities_v3.json").write_text(
    json.dumps(all_sp_entries, ensure_ascii=False, indent=2))

# 2. 브래킷 엔트리
(OUT / "bracket_entities_v3.json").write_text(
    json.dumps(all_bracket_entries, ensure_ascii=False, indent=2))

# 3. 악기별 상세 (SP)
inst_summary = {}
for inst, d in sorted(instrument_details.items(), key=lambda x: -x[1]["count"]):
    inst_summary[inst] = {
        "count": d["count"],
        "top_modifiers": d["modifiers"].most_common(10),
        "top_patterns": d["patterns"].most_common(5),
        "top_effects": d["effects"].most_common(5),
        "top_chords": d["chords"].most_common(5),
    }
(OUT / "instrument_details_v3.json").write_text(
    json.dumps(inst_summary, ensure_ascii=False, indent=2))

# 4. 악기별 상세 (브래킷)
br_inst_summary = {}
for inst, d in sorted(br_instrument_details.items(), key=lambda x: -x[1]["count"]):
    br_inst_summary[inst] = {
        "count": d["count"],
        "top_modifiers": d["modifiers"].most_common(10),
        "top_actions": d["actions"].most_common(10),
    }
(OUT / "bracket_instrument_details_v3.json").write_text(
    json.dumps(br_inst_summary, ensure_ascii=False, indent=2))

# 5. 드럼 상세 (SP)
drum_summary = {}
for dp, d in sorted(drum_details.items(), key=lambda x: -x[1]["count"]):
    drum_summary[dp] = {
        "count": d["count"],
        "top_modifiers": d["modifiers"].most_common(10),
    }
(OUT / "drum_details_v3.json").write_text(
    json.dumps(drum_summary, ensure_ascii=False, indent=2))

# 6. 드럼 상세 (브래킷)
br_drum_summary = {}
for dp, d in sorted(br_drum_details.items(), key=lambda x: -x[1]["count"]):
    br_drum_summary[dp] = {
        "count": d["count"],
        "top_modifiers": d["modifiers"].most_common(10),
    }
(OUT / "bracket_drum_details_v3.json").write_text(
    json.dumps(br_drum_summary, ensure_ascii=False, indent=2))

# 7. 보컬 상세 (SP)
vocal_summary = {
    "top_modifiers": vocal_details["modifiers"].most_common(20),
    "top_delivery": vocal_details["delivery"].most_common(20),
    "top_effects": vocal_details["effects"].most_common(10),
}
(OUT / "vocal_details_v3.json").write_text(
    json.dumps(vocal_summary, ensure_ascii=False, indent=2))

# 콘솔 출력
print(f"SP 엔트리: {len(all_sp_entries)} / 브래킷 엔트리: {len(all_bracket_entries)}")
print()
print("=== SP 슬롯 분포 ===")
for s, c in sp_slot_counts.most_common():
    print(f"  {c:4d}  {s}")
print()
print("=== 브래킷 슬롯 분포 ===")
for s, c in br_slot_counts.most_common():
    print(f"  {c:4d}  {s}")

print()
print("=== SP 악기 entity + modifier TOP 10 ===")
for inst, d in sorted(instrument_details.items(), key=lambda x: -x[1]["count"])[:10]:
    mods = ", ".join(f"{m}({c})" for m, c in d["modifiers"].most_common(5))
    effs = ", ".join(f"{e}({c})" for e, c in d["effects"].most_common(3))
    print(f"  {d['count']:3d}x {inst}")
    if mods: print(f"       mod: {mods}")
    if effs: print(f"       eff: {effs}")

print()
print("=== 브래킷 악기 entity + action TOP 10 ===")
for inst, d in sorted(br_instrument_details.items(), key=lambda x: -x[1]["count"])[:10]:
    mods = ", ".join(f"{m}({c})" for m, c in d["modifiers"].most_common(3))
    acts = ", ".join(f"{a}({c})" for a, c in d["actions"].most_common(3))
    print(f"  {d['count']:3d}x {inst}")
    if mods: print(f"       mod: {mods}")
    if acts: print(f"       act: {acts}")

print()
print("=== SP 드럼 modifier ===")
for dp, d in sorted(drum_details.items(), key=lambda x: -x[1]["count"])[:8]:
    mods = ", ".join(f"{m}({c})" for m, c in d["modifiers"].most_common(5))
    print(f"  {d['count']:3d}x {dp}: {mods}")

print()
print("=== 브래킷 드럼 modifier ===")
for dp, d in sorted(br_drum_details.items(), key=lambda x: -x[1]["count"])[:8]:
    mods = ", ".join(f"{m}({c})" for m, c in d["modifiers"].most_common(3))
    print(f"  {d['count']:3d}x {dp}: {mods}")

print()
print("=== 보컬 delivery TOP 10 ===")
for d, c in vocal_details["delivery"].most_common(10):
    print(f"  {c:3d}x {d}")

print()
print("=== 미분류 ===")
for e in all_sp_entries:
    if e["slot"] == "unclassified":
        print(f"  [SP] [{e['song_id']:04d}] {e['sentence'][:100]}")
for e in all_bracket_entries:
    if e["slot"] == "unclassified":
        print(f"  [BR] [{e['song_id']:04d}] [{e['bracket'][:80]}]")
