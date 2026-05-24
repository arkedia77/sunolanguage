#!/usr/bin/env python3
"""
SP Builder — Suno 네이티브 어휘 기반 SP 템플릿 생성기 (Top-Anchor 자동 배치).

사용:
  python3 scripts/sp_builder.py list                          # 29개 대장르 + 서브장르 목록
  python3 scripts/sp_builder.py build "K-Ballad"              # 기본 템플릿 생성
  python3 scripts/sp_builder.py build "K-Rock" --vocal=female  # 보컬 지정
  python3 scripts/sp_builder.py build "Jazz" --bpm=120 --key="Bb Major" --mood=smooth
  python3 scripts/sp_builder.py build "EDM" --sub=Trance --instrumental
  python3 scripts/sp_builder.py anchor "raw SP text here"     # 기존 SP를 Top-Anchor 순서로 재배치
"""
import argparse
import json
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DICT_PATH = REPO / "rag" / "suno_dictionary_v3.json"
FRONTIER_PATH = REPO / "rag" / "genre_frontier.json"

MAJOR_GENRES = {
    "K-Ballad": {
        "sub_genres": ["Korean Ballad", "Piano Ballad", "Acoustic Ballad", "Orchestral Ballad"],
        "instruments": ["grand piano", "clean electric guitar", "electric bass", "strings"],
        "drums": "steady beat with brushed snare and soft kick",
        "vocal": {"male": "breathy male tenor vocals", "female": "breathy female vocals"},
        "bpm": "68-76", "key": "E Major", "time_sig": "4/4",
        "moods": ["intimate", "emotional", "warm", "melancholic"],
        "arrangement": "sparse, focusing on the interplay between the piano and the vocal melody",
    },
    "K-Rock": {
        "sub_genres": ["Pop-Rock", "Punk", "J-Rock", "Indie Rock", "Soft Rock"],
        "instruments": ["distorted electric guitar", "bass guitar", "palm-muted electric guitar"],
        "drums": "driving beat with double kick and crash cymbals on downbeats",
        "vocal": {"male": "powerful male tenor vocals with grit", "female": "powerful female vocals"},
        "bpm": "130-145", "key": "A Minor", "time_sig": "4/4",
        "moods": ["driving", "energetic", "raw", "intense"],
        "arrangement": "builds from restrained verses to full-band chorus intensity",
    },
    "K-Trot": {
        "sub_genres": ["TROT", "K-Pop Trot", "Disco Trot"],
        "instruments": ["accordion", "saxophone", "electric bass", "clean electric guitar"],
        "drums": "four-on-the-floor kick with open hi-hat on upbeats",
        "vocal": {"male": "male baritone vocals with vibrato", "female": "female vocals with vibrato"},
        "bpm": "115-128", "key": "G Major", "time_sig": "4/4",
        "moods": ["energetic", "lush", "emotional"],
        "arrangement": "lush with full band instrumentation",
    },
    "K-Pop": {
        "sub_genres": ["K-POP", "K-Pop Dance", "K-R&B", "K-Hip-Hop"],
        "instruments": ["synthesizer", "sub-bass", "synth pad", "clean electric guitar"],
        "drums": "punchy electronic kick, crisp snare, and rapid hi-hat patterns",
        "vocal": {"male": "bright male tenor vocals", "female": "bright female vocals"},
        "bpm": "120-132", "key": "C Minor", "time_sig": "4/4",
        "moods": ["energetic", "bright", "polished"],
        "arrangement": "alternates between sparse verses and dense, layered choruses",
    },
    "Indie Pop": {
        "sub_genres": ["Bedroom Pop", "Dream Pop", "Lo-fi Pop", "Art Pop", "Soft Indie"],
        "instruments": ["clean electric guitar", "electric bass", "synthesizer", "acoustic guitar"],
        "drums": "steady kick and snare pattern with light hi-hat",
        "vocal": {"male": "soft male tenor vocals", "female": "soft female vocals"},
        "bpm": "95-115", "key": "E Major", "time_sig": "4/4",
        "moods": ["dreamy", "intimate", "warm", "nostalgic"],
        "arrangement": "intimate, with layered textures building gradually",
    },
    "City Pop": {
        "sub_genres": ["Neo City Pop", "City Pop / Funk", "City Pop / Future Funk"],
        "instruments": ["slap bass", "clean electric guitar", "electric piano", "synthesizer"],
        "drums": "syncopated groove with crisp snare and open hi-hat",
        "vocal": {"male": "smooth male tenor vocals", "female": "smooth female vocals"},
        "bpm": "105-118", "key": "E Major", "time_sig": "4/4",
        "moods": ["groovy", "smooth", "bright", "nostalgic"],
        "arrangement": "lush, with prominent bass and keyboard interplay",
    },
    "Pop": {
        "sub_genres": ["Pop", "Dance Pop", "Electro Pop", "Synth Pop", "Pop Rock"],
        "instruments": ["synthesizer", "electric bass", "clean electric guitar", "synth pad"],
        "drums": "four-on-the-floor kick with clap on 2 and 4",
        "vocal": {"male": "clear male vocals", "female": "clear female vocals"},
        "bpm": "110-130", "key": "C Major", "time_sig": "4/4",
        "moods": ["upbeat", "bright", "catchy"],
        "arrangement": "polished production with layered chorus",
    },
    "Rock": {
        "sub_genres": ["Hard Rock", "Alternative Rock", "Pop Rock", "Blues Rock", "Surf Rock"],
        "instruments": ["distorted electric guitar", "bass guitar", "electric guitar"],
        "drums": "driving rock beat with crash cymbals and fills",
        "vocal": {"male": "powerful male vocals with rasp", "female": "powerful female vocals"},
        "bpm": "120-145", "key": "E Minor", "time_sig": "4/4",
        "moods": ["driving", "powerful", "raw"],
        "arrangement": "full-band with guitar-driven energy",
    },
    "Metal": {
        "sub_genres": ["Doom Metal", "Black Metal", "Thrash Metal", "Metalcore"],
        "instruments": ["down-tuned guitar", "bass guitar", "distorted electric guitar"],
        "drums": "aggressive double-kick with blast beats",
        "vocal": {"male": "screamed vocals", "female": "screamed vocals"},
        "bpm": "60-200", "key": "D Minor", "time_sig": "4/4",
        "moods": ["aggressive", "dark", "heavy", "crushing"],
        "arrangement": "dense, wall-of-distortion with dynamic breakdowns",
    },
    "Punk": {
        "sub_genres": ["Pop Punk", "Synth-Punk", "Post-Punk", "Emo Pop"],
        "instruments": ["distorted electric guitar", "bass guitar", "clean electric guitar"],
        "drums": "fast driving beat with snare on every beat",
        "vocal": {"male": "shouted male vocals", "female": "shouted female vocals"},
        "bpm": "150-180", "key": "G Major", "time_sig": "4/4",
        "moods": ["urgent", "energetic", "raw", "rebellious"],
        "arrangement": "fast-paced with minimal production",
    },
    "Hip-Hop": {
        "sub_genres": ["Lo-fi Hip-Hop", "Trap", "Boom Bap", "K-Hip-Hop"],
        "instruments": ["808 bass", "synthesizer", "electric guitar", "synth pad"],
        "drums": "hi-hat triplets, deep kick, snappy snare",
        "vocal": {"male": "rhythmic male rap vocals", "female": "rhythmic female rap vocals"},
        "bpm": "80-95", "key": "G Minor", "time_sig": "4/4",
        "moods": ["dark", "confident", "atmospheric"],
        "arrangement": "loop-based with layered percussion and vocal focus",
    },
    "R&B": {
        "sub_genres": ["Neo-Soul", "Contemporary R&B", "Alt R&B", "Indie R&B", "Soft R&B"],
        "instruments": ["electric bass", "synthesizer", "clean electric guitar", "rhodes"],
        "drums": "laid-back groove with rim clicks and soft kick",
        "vocal": {"male": "smooth male vocals with falsetto", "female": "smooth female vocals"},
        "bpm": "70-90", "key": "Ab Major", "time_sig": "4/4",
        "moods": ["smooth", "warm", "intimate", "sensual"],
        "arrangement": "warm, with prominent vocals and groove-focused rhythm section",
    },
    "Soul": {
        "sub_genres": ["Indie Soul", "Soul Ballad", "Pop Soul"],
        "instruments": ["electric bass", "rhodes", "brass section", "electric guitar"],
        "drums": "tight groove with ghost notes on snare",
        "vocal": {"male": "soulful male vocals with vibrato", "female": "soulful female vocals"},
        "bpm": "75-95", "key": "F Major", "time_sig": "4/4",
        "moods": ["soulful", "warm", "groovy"],
        "arrangement": "warm, with call-and-response between vocals and brass",
    },
    "Funk": {
        "sub_genres": ["Funk Pop", "Electronic Funk", "Disco Funk", "City Pop / Funk"],
        "instruments": ["slap bass", "clean electric guitar", "brass section", "synthesizer"],
        "drums": "syncopated funk groove with ghost notes and open hi-hat",
        "vocal": {"male": "bright male vocals", "female": "bright female vocals"},
        "bpm": "105-120", "key": "E Minor", "time_sig": "4/4",
        "moods": ["groovy", "bright", "energetic"],
        "arrangement": "rhythm-driven with prominent bass and rhythmic guitar",
    },
    "Disco": {
        "sub_genres": ["Disco Pop", "Electro Swing", "Funk-Disco Soul"],
        "instruments": ["electric bass", "synthesizer", "clean electric guitar", "strings"],
        "drums": "four-on-the-floor kick with open hi-hat on every upbeat",
        "vocal": {"male": "bright male tenor vocals", "female": "bright female vocals"},
        "bpm": "115-130", "key": "A Minor", "time_sig": "4/4",
        "moods": ["groovy", "celebratory", "energetic"],
        "arrangement": "lush orchestration with driving four-on-the-floor rhythm",
    },
    "Jazz": {
        "sub_genres": ["Jazz Ballad", "Jazz Pop", "Bebop", "Modal Jazz", "Latin Jazz", "Gypsy Jazz"],
        "instruments": ["upright bass", "piano", "muted trumpet", "saxophone"],
        "drums": "brush pattern on snare with ride cymbal and gentle kick",
        "vocal": {"male": "smooth male baritone vocals", "female": "smooth female vocals"},
        "bpm": "60-180", "key": "Bb Major", "time_sig": "4/4",
        "moods": ["smooth", "intimate", "spacious", "swinging"],
        "arrangement": "spacious, leaving room between instruments for improvisation",
    },
    "Blues": {
        "sub_genres": ["Acoustic Blues", "Blues Rock", "Electric Blues"],
        "instruments": ["electric guitar", "harmonica", "electric bass", "acoustic guitar"],
        "drums": "shuffle beat with ride cymbal",
        "vocal": {"male": "gravelly male vocals", "female": "gravelly female vocals"},
        "bpm": "70-120", "key": "E Minor", "time_sig": "4/4",
        "moods": ["raw", "gritty", "soulful"],
        "arrangement": "stripped-back with guitar and vocal leading",
    },
    "Folk": {
        "sub_genres": ["Indie Folk", "Acoustic Folk", "Folk Rock", "Celtic Folk", "Neo-folk"],
        "instruments": ["fingerpicked acoustic guitar", "acoustic guitar", "violin", "mandolin"],
        "drums": "minimal with brushed snare or no drums",
        "vocal": {"male": "warm male vocals", "female": "warm female vocals"},
        "bpm": "90-120", "key": "G Major", "time_sig": "4/4",
        "moods": ["warm", "pastoral", "intimate", "storytelling"],
        "arrangement": "acoustic-focused with natural, organic textures",
    },
    "Country": {
        "sub_genres": ["Country", "Country Pop", "Outlaw Country", "Bluegrass"],
        "instruments": ["acoustic guitar", "banjo", "fiddle", "electric bass"],
        "drums": "steady two-step with brushed snare",
        "vocal": {"male": "warm baritone vocals", "female": "warm female vocals"},
        "bpm": "100-140", "key": "G Major", "time_sig": "4/4",
        "moods": ["warm", "storytelling", "dusty"],
        "arrangement": "acoustic instrumentation with string harmonies",
    },
    "Latin": {
        "sub_genres": ["Bossa Nova", "Salsa", "Cumbia", "Reggaeton", "Bachata", "Dembow"],
        "instruments": ["nylon-string acoustic guitar", "electric bass", "brass section", "acoustic piano"],
        "drums": "syncopated Latin percussion with clave pattern",
        "vocal": {"male": "warm male vocals", "female": "warm female vocals"},
        "bpm": "80-130", "key": "D Minor", "time_sig": "4/4",
        "moods": ["warm", "rhythmic", "celebratory"],
        "arrangement": "percussion-driven with melodic interplay",
    },
    "Reggae": {
        "sub_genres": ["Reggae", "Dub"],
        "instruments": ["electric bass", "clean electric guitar", "organ", "synthesizer"],
        "drums": "one-drop rhythm with rimshot on 3",
        "vocal": {"male": "relaxed male vocals", "female": "relaxed female vocals"},
        "bpm": "70-90", "key": "Bb Major", "time_sig": "4/4",
        "moods": ["laid-back", "warm", "groovy"],
        "arrangement": "bass-heavy with offbeat guitar stabs and spacious mix",
    },
    "World": {
        "sub_genres": ["Afrobeats", "Highlife", "Gamelan", "Raga", "Bhangra", "Qawwali"],
        "instruments": ["percussion", "acoustic guitar", "brass section", "synthesizer"],
        "drums": "complex polyrhythmic percussion pattern",
        "vocal": {"male": "expressive male vocals", "female": "expressive female vocals"},
        "bpm": "90-130", "key": "D Major", "time_sig": "4/4",
        "moods": ["energetic", "vibrant", "rhythmic"],
        "arrangement": "percussion-forward with layered rhythmic textures",
    },
    "EDM": {
        "sub_genres": ["Trance", "Progressive House", "Tech House", "Dubstep", "Drum and Bass",
                       "Acid House", "Future Bass"],
        "instruments": ["synthesizer", "sub-bass", "synth pad", "arpeggiated synthesizer"],
        "drums": "four-on-the-floor kick with sidechained bass",
        "vocal": {"male": "processed male vocals", "female": "processed female vocals"},
        "bpm": "125-140", "key": "F Minor", "time_sig": "4/4",
        "moods": ["euphoric", "driving", "building"],
        "arrangement": "build-up and drop structure with filtered transitions",
    },
    "Phonk": {
        "sub_genres": ["Drift Phonk", "Memphis Phonk"],
        "instruments": ["808 bass", "distorted electric guitar", "synthesizer"],
        "drums": "lo-fi 808 pattern with hi-hat triplets and distorted cowbell",
        "vocal": {"male": "pitched vocal sample", "female": "pitched vocal sample"},
        "bpm": "126-140", "key": "G Minor", "time_sig": "4/4",
        "moods": ["aggressive", "dark", "driving"],
        "arrangement": "loop-based with heavy bass and distorted textures",
    },
    "Ambient": {
        "sub_genres": ["Dark Ambient", "Drone Ambient", "Ethereal Ambient", "Ambient Electronic"],
        "instruments": ["synth pad", "sustained synthesizer pad", "pad", "strings"],
        "drums": "no percussion",
        "vocal": {"male": "no vocals", "female": "no vocals"},
        "bpm": "60-80", "key": "D Minor", "time_sig": "4/4",
        "moods": ["atmospheric", "meditative", "expansive"],
        "arrangement": "spacious, with slowly evolving textures and no rhythm",
    },
    "Lo-fi": {
        "sub_genres": ["Lo-fi Pop", "Lo-fi Hip-Hop", "Chillhop", "Lo-fi R&B"],
        "instruments": ["clean electric guitar", "electric bass", "rhodes", "acoustic guitar"],
        "drums": "soft lo-fi beat with vinyl crackle texture",
        "vocal": {"male": "soft male vocals", "female": "soft female vocals"},
        "bpm": "75-90", "key": "F Major", "time_sig": "4/4",
        "moods": ["chill", "warm", "nostalgic"],
        "arrangement": "lo-fi production with warm, analog-style textures",
    },
    "Shoegaze": {
        "sub_genres": ["Shoegaze", "Dream Pop / Shoegaze", "Slowcore"],
        "instruments": ["distorted electric guitar", "bass guitar", "clean electric guitar"],
        "drums": "simple beat with crash washes and reverb",
        "vocal": {"male": "hushed male vocals with heavy reverb", "female": "hushed female vocals"},
        "bpm": "90-110", "key": "E Minor", "time_sig": "4/4",
        "moods": ["dreamy", "swirling", "immersive"],
        "arrangement": "layered guitar walls with chorus and delay effects",
    },
    "Synthwave": {
        "sub_genres": ["Synthwave", "Vaporwave", "Berlin School"],
        "instruments": ["arpeggiated synthesizer", "synth bass", "synth pad", "electric piano"],
        "drums": "gated snare on 2 and 4 with electronic kick",
        "vocal": {"male": "processed male vocals", "female": "processed female vocals"},
        "bpm": "110-125", "key": "A Minor", "time_sig": "4/4",
        "moods": ["nostalgic", "retro", "atmospheric"],
        "arrangement": "synth-driven with arpeggiated sequences and gated reverb",
    },
    "Classical": {
        "sub_genres": ["Cinematic", "Film Score", "Neoclassical", "Chamber", "Orchestral"],
        "instruments": ["strings", "cello", "violin", "piano", "orchestral strings"],
        "drums": "no drums",
        "vocal": {"male": "no vocals", "female": "no vocals"},
        "bpm": "60-100", "key": "D Minor", "time_sig": "4/4",
        "moods": ["cinematic", "emotional", "grand", "intimate"],
        "arrangement": "orchestral with dynamic contrast between sections",
    },
}

TOP_ANCHOR_ORDER = [
    "genre",           # position 1: highest weight
    "mood",            # position 2: high
    "core_instruments", # position 3: high (2 instruments)
    "vocal",           # position 4: medium
    "details",         # position 5+: low (arrangement, drums, effects, tempo)
]


def load_dictionary():
    if DICT_PATH.exists():
        with open(DICT_PATH) as f:
            return json.load(f)
    return None


def load_frontier():
    if FRONTIER_PATH.exists():
        with open(FRONTIER_PATH) as f:
            return json.load(f)
    return None


def list_genres():
    print("═══ Suno SP Builder — 29개 대장르 카테고리 ═══\n")
    for i, (genre, info) in enumerate(MAJOR_GENRES.items(), 1):
        subs = ", ".join(info["sub_genres"])
        bpm = info["bpm"]
        print(f"  {i:2d}. {genre:<14s}  BPM {bpm:<10s}  └ {subs}")
    print(f"\n총 {len(MAJOR_GENRES)}개 대장르, "
          f"{sum(len(v['sub_genres']) for v in MAJOR_GENRES.values())}개 서브장르")
    print("\n사용: python3 sp_builder.py build <장르명>")


def find_genre(query):
    q = query.lower().strip()
    for name, info in MAJOR_GENRES.items():
        if q == name.lower():
            return name, info
    for name, info in MAJOR_GENRES.items():
        if q in name.lower():
            return name, info
        for sub in info["sub_genres"]:
            if q == sub.lower() or q in sub.lower():
                return name, info
    return None, None


def build_sp(genre_name, genre_info, args):
    vocal_gender = getattr(args, "vocal", "male") or "male"
    mood = getattr(args, "mood", None) or genre_info["moods"][0]
    bpm_input = getattr(args, "bpm", None)
    key_input = getattr(args, "key", None)
    sub = getattr(args, "sub", None)
    instrumental = getattr(args, "instrumental", False)

    bpm_range = genre_info["bpm"]
    if bpm_input:
        bpm = str(bpm_input)
    else:
        parts = bpm_range.split("-")
        bpm = parts[0] if len(parts) == 1 else str((int(parts[0]) + int(parts[1])) // 2)

    key = key_input or genre_info["key"]
    time_sig = genre_info["time_sig"]

    genre_label = sub if sub else genre_name
    vocal_desc = genre_info["vocal"].get(vocal_gender, genre_info["vocal"]["male"])

    instruments = genre_info["instruments"]

    lines = []

    # §1.10: Genre [featuring Vocal]. — genre first, no mood lead
    if not instrumental:
        lines.append(f"{genre_label} featuring {vocal_desc}.")
    else:
        lines.append(f"{genre_label} instrumental.")

    # §1.11: 주악기(pos 2)→보조악기(pos 3)→드럼(pos 4) — max 3 instrument sentences
    inst_sentences = []
    for inst in instruments:
        inst_sentences.append(_get_instrument_pattern(inst, genre_name))
    lines.extend(inst_sentences[:3])

    # Drums
    drums = genre_info["drums"]
    if drums.startswith("no "):
        lines.append(f"The drums feature {drums}.")
    else:
        article = "an " if drums[0] in "aeiou" else "a " if drums[0].islower() else ""
        lines.append(f"The drums feature {article}{drums}.")

    # §1.11: 보컬(pos 5) — mood integrated, skip if mood already in vocal_desc
    if not instrumental:
        if mood.lower() in vocal_desc.lower():
            lines.append(f"The {vocal_desc} deliver with expressive phrasing.")
        else:
            article = "an" if mood[0] in "aeiou" else "a"
            lines.append(f"The {vocal_desc} deliver with {article} {mood} quality.")

    # §1.11: 어레인지(pos 6)→템포(pos 7)
    arr = genre_info["arrangement"]
    if arr[0].islower() and not arr.startswith(("builds", "alternates", "loop")):
        lines.append(f"The arrangement is {arr}.")
    else:
        lines.append(f"The arrangement {arr}.")
    lines.append(f"{bpm} BPM in {key}, {time_sig} time signature.")

    sp = " ".join(lines)
    return sp


def _get_instrument_pattern(instrument, genre):
    patterns = {
        "grand piano": "A grand piano plays arpeggiated chords with sustain pedal",
        "piano": "Piano provides chord voicings with sustained chords and gentle fills",
        "acoustic piano": "Acoustic piano plays rhythmic chord patterns",
        "clean electric guitar": "Clean electric guitar plays arpeggiated patterns with light chorus and delay",
        "electric guitar": "Electric guitar provides rhythmic patterns with clean tone",
        "distorted electric guitar": "Distorted electric guitar plays aggressive riffs with heavy overdrive",
        "palm-muted electric guitar": "Palm-muted electric guitar drives the rhythm with tight, percussive strokes",
        "arpeggiated electric guitar": "Arpeggiated electric guitar creates shimmering melodic patterns",
        "fingerpicked acoustic guitar": "Fingerpicked acoustic guitar provides a steady pattern with alternating bass notes",
        "acoustic guitar": "Acoustic guitar plays a steady fingerstyle pattern",
        "nylon-string acoustic guitar": "Nylon-string acoustic guitar plays gentle arpeggiated patterns",
        "electric bass": "Electric bass follows the kick drum pattern with a warm, rounded tone",
        "bass guitar": "Bass guitar follows the kick drum pattern with a thick, overdriven tone",
        "slap bass": "Slap bass drives the groove with syncopated sixteenth-note patterns",
        "fretless bass": "Fretless bass provides smooth, sliding melodic lines",
        "sub-bass": "Sub-bass synth follows the kick pattern with deep, punchy tone",
        "808 bass": "808 bass provides deep, sustained low-end hits",
        "synth bass": "Synth bass drives the low-end with a warm, analog tone",
        "synthesizer": "A bright synthesizer provides melodic patterns",
        "arpeggiated synthesizer": "Arpeggiated synthesizer creates rhythmic melodic sequences",
        "synth pad": "Synth pad provides atmospheric harmonic depth in the background",
        "pad": "Atmospheric pad provides sustained harmonic backing",
        "sustained synthesizer pad": "Sustained synthesizer pad creates a slow-evolving sonic landscape",
        "strings": "String ensemble provides harmonic backing with sustained bowing",
        "orchestral strings": "Orchestral strings swell with dynamic expression",
        "violin": "Violin plays lyrical melodic phrases",
        "cello": "Cello provides warm, rich low-register melodies",
        "brass section": "Brass section punctuates with staccato stabs and melodic fills",
        "muted trumpet": "Muted trumpet plays soft, lyrical phrases with plate reverb",
        "trumpet": "Trumpet provides bright, melodic phrases",
        "saxophone": "Saxophone provides melodic fills between vocal phrases",
        "accordion": "Accordion plays steady rhythmic staccato chords",
        "harmonica": "Harmonica adds bluesy melodic fills",
        "rhodes": "Rhodes electric piano provides warm, bell-like chord patterns",
        "electric piano": "Electric piano provides warm chord voicings with tremolo",
        "upright bass": "Upright bass plays walking lines with warm, woody tone",
        "banjo": "Banjo plays rapid Scruggs-style rolls",
        "fiddle": "Fiddle provides energetic melodic lines",
        "mandolin": "Mandolin adds rhythmic chop on the backbeat",
        "vibraphone": "Vibraphone adds shimmering melodic accents",
        "flute": "Flute plays gentle, breathy melodic lines",
        "clarinet": "Clarinet provides warm, woody melodic phrases",
        "harp": "Harp plays gentle arpeggiated patterns",
        "glockenspiel": "Glockenspiel adds bright, bell-like melodic accents",
        "down-tuned guitar": "Down-tuned guitar plays heavy, crushing power chords",
        "log drum": "Log drum provides deep, resonant bass pattern",
    }
    return patterns.get(instrument, f"{instrument.capitalize()} enters") + "."


def reorder_top_anchor(raw_sp):
    """기존 SP 텍스트를 Top-Anchor 순서로 재배치 (휴리스틱)."""
    import re
    sentences = [s.strip() for s in re.split(r'(?<=[.!])\s+', raw_sp) if s.strip()]

    genre_s, mood_s, inst_s, vocal_s, detail_s = [], [], [], [], []

    genre_kw = ['pop', 'rock', 'jazz', 'ballad', 'folk', 'metal', 'punk', 'hip-hop',
                'r&b', 'electronic', 'ambient', 'funk', 'soul', 'disco', 'trance',
                'house', 'drill', 'phonk', 'blues', 'country', 'latin', 'reggae',
                'classical', 'cinematic', 'trot', 'k-pop', 'shoegaze', 'synthwave',
                'bossa', 'cumbia', 'salsa', 'dubstep', 'drum and bass', 'indie']
    vocal_kw = ['vocal', 'singer', 'voice', 'baritone', 'tenor', 'soprano', 'falsetto',
                'rap', 'singing', 'breathy', 'soulful', 'screamed', 'hushed']
    tempo_kw = ['bpm', 'tempo', 'key of', 'time signature', 'major', 'minor']
    arrangement_kw = ['arrangement', 'production', 'mix', 'build', 'structure']

    for s in sentences:
        sl = s.lower()
        if any(k in sl for k in genre_kw) and len(genre_s) == 0:
            genre_s.append(s)
        elif any(k in sl for k in vocal_kw):
            vocal_s.append(s)
        elif any(k in sl for k in tempo_kw):
            detail_s.append(s)
        elif any(k in sl for k in arrangement_kw):
            detail_s.append(s)
        else:
            inst_s.append(s)

    result = genre_s + inst_s[:2] + vocal_s + inst_s[2:] + detail_s
    return " ".join(result)


def main():
    parser = argparse.ArgumentParser(description="Suno SP Builder")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="29개 대장르 목록 표시")

    build_p = sub.add_parser("build", help="SP 템플릿 생성")
    build_p.add_argument("genre", help="장르명 (대장르 또는 서브장르)")
    build_p.add_argument("--vocal", choices=["male", "female"], default="male")
    build_p.add_argument("--mood", help="분위기 키워드")
    build_p.add_argument("--bpm", type=int, help="BPM")
    build_p.add_argument("--key", help="조성 (예: 'E Major')")
    build_p.add_argument("--sub", help="서브장르 지정")
    build_p.add_argument("--instrumental", action="store_true", help="인스트루멘탈")

    anchor_p = sub.add_parser("anchor", help="기존 SP를 Top-Anchor 순서로 재배치")
    anchor_p.add_argument("sp", help="원본 SP 텍스트")

    args = parser.parse_args()

    if args.command == "list":
        list_genres()
    elif args.command == "build":
        genre_name, genre_info = find_genre(args.genre)
        if not genre_info:
            print(f"❌ '{args.genre}' 장르를 찾을 수 없습니다.")
            print("  사용 가능한 장르: " + ", ".join(MAJOR_GENRES.keys()))
            sys.exit(1)

        sp = build_sp(genre_name, genre_info, args)

        print(f"═══ SP Builder: {genre_name} ═══\n")
        print(f"장르: {genre_name}")
        if args.sub:
            print(f"서브장르: {args.sub}")
        print(f"보컬: {'Instrumental' if args.instrumental else args.vocal}")
        print(f"분위기: {args.mood or genre_info['moods'][0]}")
        print(f"길이: {len(sp)}자\n")
        print("─── SP (Top-Anchor 순서) ───\n")
        print(textwrap.fill(sp, width=80))
        print(f"\n─── Top-Anchor 배치 순서 ───")
        print("  1. Genre/Subgenre  [highest]  → 첫 문장")
        print("  2. Core Instruments [high]    → 2~3번째 문장")
        print("  3. Drums           [high]     → 중간")
        print("  4. Vocal Identity  [medium]   → 후반")
        print("  5. Arrangement     [low]      → 끝부분")
        print("  6. Tempo/Key/Time  [lowest]   → 마지막 문장")

        frontier = load_frontier()
        if frontier:
            for fname, fdata in frontier.get("genres", {}).items():
                if fname.lower() in genre_name.lower() or genre_name.lower() in fname.lower():
                    if fdata.get("validated"):
                        print(f"\n⚠ 참고: {fname} → S018 검증 완료")
                        print(f"  must_have: {fdata['must_have']}")
                        if fdata.get("suno_native_notes"):
                            print(f"  notes: {fdata['suno_native_notes']}")

    elif args.command == "anchor":
        result = reorder_top_anchor(args.sp)
        print("═══ Top-Anchor 재배치 결과 ═══\n")
        print(textwrap.fill(result, width=80))
        print(f"\n길이: {len(result)}자")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
