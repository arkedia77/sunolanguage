#!/usr/bin/env python3
"""
S_INST200 Master Plan Generator v2
공백 타겟팅 설계 — 기존 코퍼스의 구멍을 정확히 노림
"""
import json
import random
from pathlib import Path
from collections import Counter

# ═══════════════════════════════════════════════════════════════
# GAP-TARGETING CONSTRAINTS
# ═══════════════════════════════════════════════════════════════
#
# KEY GAPS:   A, Bb, Ab, F#, Eb, C#, Db, D# = 0 songs each
# MODE GAPS:  Minor 16%, Modal 0% → push to 60%+ non-major
# BPM GAPS:   <60 = 0, 70-79 = 141(31.7%), 150+ = 25 → invert
# TIME GAPS:  4/4 = 98%, 3/4 = 3, 6/8 = 1, rest = 0
# INST GAPS:  90+ instruments with 0 corpus presence

# Key allocation: zero-coverage roots get heavy allocation
# A, Bb, Ab, F#, Eb, C#, Db = ~20 each = 140 songs
# Low-coverage D, F, B, G#, C = ~10 each = 50 songs
# Over-covered E, G = max 5 each = 10 songs

# Mode allocation: Major 40% / Minor 30% / Modal 30%
# Modal = Dorian, Phrygian, Lydian, Mixolydian, Pentatonic, Whole tone, Locrian, etc.

# BPM allocation: avoid 70-99, push extremes
# <50:     20 songs (10%)
# 50-69:   25 songs (12.5%)
# 70-99:   15 songs (7.5%)  ← DELIBERATELY LOW (corpus already 70%)
# 100-119: 20 songs (10%)
# 120-139: 25 songs (12.5%)
# 140-159: 30 songs (15%)
# 160-179: 30 songs (15%)
# 180-220: 25 songs (12.5%)
# 220+:    10 songs (5%)

# Time sig allocation: invert the gap
# 4/4:   80 songs (40%)  ← not 98%
# 3/4:   30 songs (15%)
# 6/8:   25 songs (12.5%)
# 12/8:  15 songs (7.5%)
# 7/8:   15 songs (7.5%)
# 5/4:   12 songs (6%)
# 2/4:   10 songs (5%)
# 9/8:    8 songs (4%)
# 11/8:   5 songs (2.5%)

songs = []

# ═══════════════════════════════════════════════════════════════
# SESSION 1: 001-040 — ZERO-KEY + EXTREME BPM + ODD METERS
# ═══════════════════════════════════════════════════════════════

songs += [
    # --- Zero-key: Ab ---
    {"id": "SI001", "genre": "Doom Metal", "instruments": ["down-tuned guitar", "bass guitar", "slow heavy drums"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 45, "key": "Ab Minor", "vocal": None},
    {"id": "SI002", "genre": "Dark Ambient", "instruments": ["dissonant synth pad", "sub-drone", "granular texture"],
     "form": "Free-form", "time": "4/4", "bpm": 35, "key": "Ab Minor", "vocal": None},
    {"id": "SI003", "genre": "Neo-Soul", "instruments": ["rhodes", "fretless bass", "finger snaps"],
     "form": "Verse-Chorus", "time": "6/8", "bpm": 65, "key": "Ab Major", "vocal": None},
    {"id": "SI004", "genre": "Film Score", "instruments": ["full orchestra", "french horn", "timpani"],
     "form": "Through-composed", "time": "3/4", "bpm": 55, "key": "Ab Major", "vocal": None},

    # --- Zero-key: Bb ---
    {"id": "SI005", "genre": "Big Band Swing", "instruments": ["brass section", "tenor saxophone", "drum kit"],
     "form": "AABA", "time": "4/4", "bpm": 185, "key": "Bb Major", "vocal": None},
    {"id": "SI006", "genre": "Reggae", "instruments": ["offbeat guitar", "deep bass", "one-drop drums"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 78, "key": "Bb Minor", "vocal": None},
    {"id": "SI007", "genre": "New Orleans Jazz", "instruments": ["trombone", "clarinet", "tuba"],
     "form": "Collective improvisation", "time": "4/4", "bpm": 118, "key": "Bb Major", "vocal": None},
    {"id": "SI008", "genre": "Polka", "instruments": ["accordion", "tuba", "clarinet"],
     "form": "AABB", "time": "2/4", "bpm": 135, "key": "Bb Major", "vocal": None},

    # --- Zero-key: F# ---
    {"id": "SI009", "genre": "Progressive Metal", "instruments": ["distorted guitar", "bass guitar", "double-kick drums"],
     "form": "Suite", "time": "7/8", "bpm": 155, "key": "F# Minor", "vocal": None},
    {"id": "SI010", "genre": "Impressionist", "instruments": ["piano", "flute", "harp"],
     "form": "Through-composed", "time": "6/8", "bpm": 48, "key": "F# Minor", "vocal": None},
    {"id": "SI011", "genre": "Shoegaze", "instruments": ["heavily distorted guitar", "bass with flanger", "crash washes"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 98, "key": "F# Minor", "vocal": None},
    {"id": "SI012", "genre": "Art Pop", "instruments": ["celesta", "synthesizer", "orchestral harp"],
     "form": "Through-composed", "time": "5/4", "bpm": 88, "key": "F# Major", "vocal": None},

    # --- Zero-key: Eb ---
    {"id": "SI013", "genre": "Gospel", "instruments": ["Hammond organ", "piano", "choir"],
     "form": "Call-and-Response", "time": "12/8", "bpm": 62, "key": "Eb Major", "vocal": None},
    {"id": "SI014", "genre": "Bebop", "instruments": ["alto saxophone", "piano", "ride cymbal"],
     "form": "AABA", "time": "4/4", "bpm": 210, "key": "Eb Major", "vocal": None},
    {"id": "SI015", "genre": "Disco", "instruments": ["strings", "four-on-the-floor kick", "electric bass"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 125, "key": "Eb Minor", "vocal": None},
    {"id": "SI016", "genre": "Waltz", "instruments": ["string orchestra", "grand piano", "harp"],
     "form": "Ternary (ABA)", "time": "3/4", "bpm": 170, "key": "Eb Major", "vocal": None},

    # --- Zero-key: C# ---
    {"id": "SI017", "genre": "Black Metal", "instruments": ["tremolo-picked guitar", "blast beats", "bass guitar"],
     "form": "Through-composed", "time": "4/4", "bpm": 195, "key": "C# Minor", "vocal": None},
    {"id": "SI018", "genre": "Drone Ambient", "instruments": ["sustained synth pad", "sub-drone", "overtone singing"],
     "form": "Free-form", "time": "4/4", "bpm": 30, "key": "C# Minor", "vocal": None},
    {"id": "SI019", "genre": "Trance", "instruments": ["supersaw lead", "sidechained bass", "snare roll builds"],
     "form": "Build-Drop", "time": "4/4", "bpm": 142, "key": "C# Minor", "vocal": None},

    # --- Zero-key: Db ---
    {"id": "SI020", "genre": "Romantic Period", "instruments": ["grand piano", "solo violin", "orchestral strings"],
     "form": "Ternary (ABA)", "time": "3/4", "bpm": 58, "key": "Db Major", "vocal": None},
    {"id": "SI021", "genre": "Stoner Metal", "instruments": ["fuzzy down-tuned guitar", "bass guitar", "heavy drums"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 55, "key": "Db Minor", "vocal": None},
    {"id": "SI022", "genre": "Trip-Hop", "instruments": ["scratched vinyl", "atmospheric strings", "deep bass"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 82, "key": "Db Minor", "vocal": None},

    # --- Zero-key: A (0 in corpus!) ---
    {"id": "SI023", "genre": "Bluegrass", "instruments": ["banjo", "mandolin", "upright bass"],
     "form": "AABB", "time": "4/4", "bpm": 160, "key": "A Major", "vocal": None},
    {"id": "SI024", "genre": "Flamenco", "instruments": ["nylon-string guitar", "cajón", "hand claps"],
     "form": "Through-composed", "time": "12/8", "bpm": 95, "key": "A Phrygian", "vocal": None},
    {"id": "SI025", "genre": "Surf Rock", "instruments": ["spring reverb guitar", "upright bass", "floor tom"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 165, "key": "A Minor", "vocal": None},
    {"id": "SI026", "genre": "Thrash Metal", "instruments": ["palm-muted riff", "bass guitar", "double-kick drums"],
     "form": "Verse-Chorus-Solo", "time": "4/4", "bpm": 200, "key": "A Minor", "vocal": None},

    # --- Extreme BPM (<50) ---
    {"id": "SI027", "genre": "Funeral Doom", "instruments": ["extremely slow guitar drone", "organ", "sparse timpani"],
     "form": "Through-composed", "time": "4/4", "bpm": 25, "key": "Db Minor", "vocal": None},
    {"id": "SI028", "genre": "Ambient Minimalist", "instruments": ["sustained piano notes", "tape loop", "silence"],
     "form": "Free-form", "time": "3/4", "bpm": 35, "key": "F# Minor", "vocal": None},

    # --- Extreme BPM (>200) ---
    {"id": "SI029", "genre": "Speedcore", "instruments": ["distorted kick drum", "noise synth", "gabber bass"],
     "form": "Loop-based", "time": "4/4", "bpm": 250, "key": "A Minor", "vocal": None},
    {"id": "SI030", "genre": "Fast Bebop", "instruments": ["tenor saxophone", "piano", "ride cymbal"],
     "form": "AABA", "time": "4/4", "bpm": 280, "key": "Bb Major", "vocal": None},

    # --- Odd meter focus (7/8, 5/4, 9/8, 11/8) ---
    {"id": "SI031", "genre": "Balkan Brass", "instruments": ["trumpet", "tuba", "snare drum"],
     "form": "Strophic", "time": "7/8", "bpm": 140, "key": "Ab Minor", "vocal": None},
    {"id": "SI032", "genre": "Progressive Rock", "instruments": ["12-string guitar", "mellotron", "bass guitar"],
     "form": "Suite", "time": "5/4", "bpm": 108, "key": "Eb Minor", "vocal": None},
    {"id": "SI033", "genre": "Carnatic Fusion", "instruments": ["mridangam", "violin", "veena"],
     "form": "Through-composed", "time": "7/8", "bpm": 90, "key": "A Minor", "vocal": None},
    {"id": "SI034", "genre": "Turkish Psychedelic", "instruments": ["electric saz", "organ", "fuzzy guitar"],
     "form": "Verse-Chorus", "time": "9/8", "bpm": 115, "key": "Bb Minor", "vocal": None},
    {"id": "SI035", "genre": "Math Rock", "instruments": ["tapping electric guitar", "bass guitar", "complex drums"],
     "form": "Through-composed", "time": "11/8", "bpm": 145, "key": "F# Minor", "vocal": None},

    # --- 3/4 waltz variations ---
    {"id": "SI036", "genre": "Viennese Waltz", "instruments": ["string orchestra", "flute", "timpani"],
     "form": "AABB", "time": "3/4", "bpm": 180, "key": "A Major", "vocal": None},
    {"id": "SI037", "genre": "Jazz Waltz", "instruments": ["piano", "upright bass", "brush drums"],
     "form": "AABA", "time": "3/4", "bpm": 155, "key": "Eb Major", "vocal": None},

    # --- 6/8 compound ---
    {"id": "SI038", "genre": "Celtic Folk", "instruments": ["tin whistle", "bodhrán", "fiddle"],
     "form": "Strophic", "time": "6/8", "bpm": 125, "key": "Ab Major", "vocal": None},
    {"id": "SI039", "genre": "Tarantella", "instruments": ["mandolin", "tambourine", "accordion"],
     "form": "Strophic", "time": "6/8", "bpm": 175, "key": "A Minor", "vocal": None},

    # --- 2/4 march ---
    {"id": "SI040", "genre": "Military March", "instruments": ["brass band", "snare drum", "piccolo"],
     "form": "March (trio)", "time": "2/4", "bpm": 120, "key": "Bb Major", "vocal": None},
]

# ═══════════════════════════════════════════════════════════════
# SESSION 2: 041-080 — MORE ZERO-KEYS + MODAL + RARE TIME SIGS
# ═══════════════════════════════════════════════════════════════

songs += [
    # --- Zero-key: A continued ---
    {"id": "SI041", "genre": "Country", "instruments": ["fiddle", "dobro", "acoustic guitar"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 115, "key": "A Major", "vocal": None},
    {"id": "SI042", "genre": "Raga", "instruments": ["sitar", "tabla", "tanpura"],
     "form": "Through-composed", "time": "7/8", "bpm": 70, "key": "A Mixolydian", "vocal": None},
    {"id": "SI043", "genre": "Death Metal", "instruments": ["heavily distorted guitar", "blast beats", "guttural bass"],
     "form": "Through-composed", "time": "4/4", "bpm": 205, "key": "A Minor", "vocal": None},

    # --- Modal keys (코퍼스 0건) ---
    {"id": "SI044", "genre": "Modal Jazz", "instruments": ["muted trumpet", "piano", "upright bass"],
     "form": "AABA", "time": "4/4", "bpm": 68, "key": "D Dorian", "vocal": None},
    {"id": "SI045", "genre": "Spanish Fusion", "instruments": ["nylon-string guitar", "cajón", "upright bass"],
     "form": "Through-composed", "time": "12/8", "bpm": 95, "key": "E Phrygian", "vocal": None},
    {"id": "SI046", "genre": "Medieval", "instruments": ["recorder", "lute", "hurdy-gurdy"],
     "form": "Binary (AB)", "time": "3/4", "bpm": 80, "key": "D Mixolydian", "vocal": None},
    {"id": "SI047", "genre": "Hindustani Classical", "instruments": ["bansuri", "tabla", "tanpura"],
     "form": "Through-composed", "time": "7/8", "bpm": 55, "key": "C Lydian", "vocal": None},
    {"id": "SI048", "genre": "Greek Rebetiko", "instruments": ["bouzouki", "guitar", "violin"],
     "form": "Strophic", "time": "9/8", "bpm": 90, "key": "D Phrygian", "vocal": None},
    {"id": "SI049", "genre": "Blues", "instruments": ["slide guitar", "harmonica", "stomp box"],
     "form": "12-bar blues", "time": "12/8", "bpm": 65, "key": "A Mixolydian", "vocal": None},
    {"id": "SI050", "genre": "Psychedelic Rock", "instruments": ["mellotron", "fuzz guitar", "wah-wah bass"],
     "form": "Through-composed", "time": "4/4", "bpm": 105, "key": "E Dorian", "vocal": None},
    {"id": "SI051", "genre": "Whole Tone Experiment", "instruments": ["piano", "vibraphone", "flute"],
     "form": "Free-form", "time": "5/4", "bpm": 72, "key": "C Whole Tone", "vocal": None},
    {"id": "SI052", "genre": "Locrian Drone", "instruments": ["synthesizer drone", "bass guitar", "sparse drums"],
     "form": "Free-form", "time": "4/4", "bpm": 42, "key": "B Locrian", "vocal": None},

    # --- Zero-key: D# / Eb minor ---
    {"id": "SI053", "genre": "Symphonic Metal", "instruments": ["orchestral strings", "distorted guitar", "double-kick"],
     "form": "Verse-Chorus-Bridge", "time": "4/4", "bpm": 158, "key": "Eb Minor", "vocal": None},
    {"id": "SI054", "genre": "Chamber Music", "instruments": ["string quartet", "clarinet", "piano"],
     "form": "Rondo (ABACA)", "time": "3/4", "bpm": 100, "key": "Eb Minor", "vocal": None},

    # --- Low-coverage F ---
    {"id": "SI055", "genre": "Funk", "instruments": ["clavinet", "slap bass", "wah-wah guitar"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 108, "key": "F Minor", "vocal": None},
    {"id": "SI056", "genre": "Baroque", "instruments": ["harpsichord", "violin", "cello"],
     "form": "Binary (AB)", "time": "3/4", "bpm": 80, "key": "F Major", "vocal": None},
    {"id": "SI057", "genre": "Progressive House", "instruments": ["supersaw synth", "sidechained sub-bass", "filtered sweep"],
     "form": "Build-Drop", "time": "4/4", "bpm": 128, "key": "F Minor", "vocal": None},
    {"id": "SI058", "genre": "Solo Piano Nocturne", "instruments": ["grand piano"],
     "form": "Through-composed", "time": "6/8", "bpm": 52, "key": "F Minor", "vocal": None},

    # --- More odd meters ---
    {"id": "SI059", "genre": "Dave Brubeck-style Jazz", "instruments": ["piano", "alto saxophone", "upright bass"],
     "form": "AABA", "time": "5/4", "bpm": 170, "key": "Eb Major", "vocal": None},
    {"id": "SI060", "genre": "Bulgarian Folk", "instruments": ["kaval", "gadulka", "tapan"],
     "form": "Strophic", "time": "11/8", "bpm": 130, "key": "A Minor", "vocal": None},
    {"id": "SI061", "genre": "Gamelan", "instruments": ["metalophone", "gong", "bamboo flute"],
     "form": "Cyclical", "time": "7/8", "bpm": 55, "key": "C Pentatonic", "vocal": None},
    {"id": "SI062", "genre": "Afro-Cuban 6/8", "instruments": ["congas", "tres guitar", "bass"],
     "form": "Verse-Montuno", "time": "6/8", "bpm": 100, "key": "F Minor", "vocal": None},

    # --- More 12/8 ---
    {"id": "SI063", "genre": "Slow Blues", "instruments": ["overdriven guitar", "hammond organ", "drums"],
     "form": "12-bar blues", "time": "12/8", "bpm": 58, "key": "Bb Minor", "vocal": None},
    {"id": "SI064", "genre": "West African Percussion", "instruments": ["djembe", "balafon", "shekere"],
     "form": "Call-and-Response", "time": "12/8", "bpm": 100, "key": "A Minor", "vocal": None},
    {"id": "SI065", "genre": "Gospel Slow", "instruments": ["organ", "piano", "bass guitar"],
     "form": "Strophic", "time": "12/8", "bpm": 50, "key": "Ab Major", "vocal": None},

    # --- More 2/4 ---
    {"id": "SI066", "genre": "Samba", "instruments": ["surdo", "pandeiro", "cavaquinho"],
     "form": "Strophic", "time": "2/4", "bpm": 105, "key": "A Major", "vocal": None},
    {"id": "SI067", "genre": "Quickstep", "instruments": ["brass section", "piano", "upright bass"],
     "form": "AABA", "time": "2/4", "bpm": 200, "key": "Bb Major", "vocal": None},

    # --- More 3/4 ---
    {"id": "SI068", "genre": "Mazurka", "instruments": ["piano", "violin", "cello"],
     "form": "AABB", "time": "3/4", "bpm": 145, "key": "F# Minor", "vocal": None},
    {"id": "SI069", "genre": "Minuet", "instruments": ["harpsichord", "flute", "violin"],
     "form": "Binary (AB)", "time": "3/4", "bpm": 112, "key": "Db Major", "vocal": None},

    # --- Extreme slow ---
    {"id": "SI070", "genre": "Glacial Ambient", "instruments": ["frozen pad", "ice texture", "distant bell"],
     "form": "Free-form", "time": "4/4", "bpm": 20, "key": "C# Minor", "vocal": None},
    {"id": "SI071", "genre": "Sufi Drone", "instruments": ["ney", "frame drum", "sustained chant"],
     "form": "Through-composed", "time": "4/4", "bpm": 38, "key": "Eb Minor", "vocal": None},

    # --- Extreme fast ---
    {"id": "SI072", "genre": "Drum and Bass", "instruments": ["reese bass", "breakbeat drums", "atmospheric pad"],
     "form": "Build-Drop", "time": "4/4", "bpm": 176, "key": "Ab Minor", "vocal": None},
    {"id": "SI073", "genre": "Grindcore", "instruments": ["blast beats", "distorted guitar", "screaming bass"],
     "form": "Through-composed", "time": "4/4", "bpm": 240, "key": "C# Minor", "vocal": None},

    # --- More rare keys ---
    {"id": "SI074", "genre": "Cumbia", "instruments": ["accordion", "guiro", "cowbell"],
     "form": "Strophic", "time": "4/4", "bpm": 92, "key": "Bb Major", "vocal": None},
    {"id": "SI075", "genre": "Acid House", "instruments": ["303 bassline", "TR-909 drums", "filter sweeps"],
     "form": "Loop-based", "time": "4/4", "bpm": 126, "key": "Db Minor", "vocal": None},
    {"id": "SI076", "genre": "Neoclassical", "instruments": ["piano", "cello", "violin"],
     "form": "Ternary (ABA)", "time": "3/4", "bpm": 75, "key": "C# Minor", "vocal": None},
    {"id": "SI077", "genre": "Electro Swing", "instruments": ["brass section", "electronic beats", "double bass"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 128, "key": "A Major", "vocal": None},
    {"id": "SI078", "genre": "Dub", "instruments": ["heavy bass", "spring reverb drums", "echo guitar"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 75, "key": "Eb Minor", "vocal": None},
    {"id": "SI079", "genre": "Tango", "instruments": ["bandoneón", "violin", "piano"],
     "form": "AABB", "time": "4/4", "bpm": 66, "key": "Ab Minor", "vocal": None},
    {"id": "SI080", "genre": "Power Metal", "instruments": ["fast arpeggiated guitar", "double-kick", "keyboard"],
     "form": "Verse-Chorus-Solo", "time": "4/4", "bpm": 168, "key": "F# Major", "vocal": None},
]

# ═══════════════════════════════════════════════════════════════
# SESSION 3: 081-120 — RARE INSTRUMENTS + REMAINING KEY GAPS
# ═══════════════════════════════════════════════════════════════

songs += [
    # --- East Asian instruments (corpus = 0) ---
    {"id": "SI081", "genre": "Chinese Traditional", "instruments": ["erhu", "guzheng", "dizi"],
     "form": "Through-composed", "time": "4/4", "bpm": 65, "key": "A Minor", "vocal": None},
    {"id": "SI082", "genre": "Japanese Koto", "instruments": ["koto", "shakuhachi", "taiko"],
     "form": "Through-composed", "time": "6/8", "bpm": 55, "key": "Db Minor", "vocal": None},
    {"id": "SI083", "genre": "Korean Traditional", "instruments": ["gayageum", "haegeum", "daegeum"],
     "form": "Through-composed", "time": "6/8", "bpm": 60, "key": "A Minor", "vocal": None},
    {"id": "SI084", "genre": "Chinese Pipa", "instruments": ["pipa", "erhu", "bamboo flute"],
     "form": "Through-composed", "time": "3/4", "bpm": 72, "key": "F# Minor", "vocal": None},
    {"id": "SI085", "genre": "Shamisen Rock", "instruments": ["shamisen", "taiko", "electric bass"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 148, "key": "A Minor", "vocal": None},

    # --- South Asian instruments (corpus = 0) ---
    {"id": "SI086", "genre": "Raga Evening", "instruments": ["sitar", "tabla", "tanpura"],
     "form": "Through-composed", "time": "7/8", "bpm": 48, "key": "Db Major", "vocal": None},
    {"id": "SI087", "genre": "Bhangra", "instruments": ["dhol drums", "tumbi", "synthesizer"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 142, "key": "Bb Major", "vocal": None},
    {"id": "SI088", "genre": "Qawwali", "instruments": ["harmonium", "tabla", "hand claps"],
     "form": "Through-composed", "time": "4/4", "bpm": 90, "key": "Bb Minor", "vocal": "Urdu"},

    # --- Middle Eastern instruments (corpus = 0) ---
    {"id": "SI089", "genre": "Arabian Maqam", "instruments": ["oud", "ney", "darbuka"],
     "form": "Through-composed", "time": "4/4", "bpm": 82, "key": "D Phrygian", "vocal": None},
    {"id": "SI090", "genre": "Persian Classical", "instruments": ["tar", "santur", "tombak"],
     "form": "Through-composed", "time": "6/8", "bpm": 75, "key": "Eb Minor", "vocal": None},

    # --- African instruments (corpus = 0) ---
    {"id": "SI091", "genre": "Afrobeats", "instruments": ["log drum", "shakers", "clean electric guitar"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 108, "key": "Bb Minor", "vocal": None},
    {"id": "SI092", "genre": "Highlife", "instruments": ["bright arpeggiated guitar", "brass section", "percussion"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 112, "key": "A Major", "vocal": None},
    {"id": "SI093", "genre": "Amapiano", "instruments": ["log drum", "piano chords", "shakers"],
     "form": "Loop-based", "time": "4/4", "bpm": 113, "key": "Eb Major", "vocal": None},
    {"id": "SI094", "genre": "Gqom", "instruments": ["minimal percussion", "deep bass synth", "chanted patterns"],
     "form": "Loop-based", "time": "4/4", "bpm": 152, "key": "Ab Minor", "vocal": None},
    {"id": "SI095", "genre": "Soukous", "instruments": ["bright arpeggiated guitar", "bass guitar", "sebene rhythm"],
     "form": "Verse-Sebene", "time": "4/4", "bpm": 135, "key": "A Major", "vocal": None},
    {"id": "SI096", "genre": "Mbaqanga", "instruments": ["accordion", "pennywhistle", "electric guitar"],
     "form": "Strophic", "time": "4/4", "bpm": 118, "key": "Bb Major", "vocal": None},
    {"id": "SI097", "genre": "Ethiopian Jazz", "instruments": ["masinko", "krar", "kebero"],
     "form": "Through-composed", "time": "6/8", "bpm": 95, "key": "Eb Minor", "vocal": None},

    # --- African percussion (corpus = 0) ---
    {"id": "SI098", "genre": "West African Drum Ensemble", "instruments": ["djembe", "balafon", "shekere"],
     "form": "Call-and-Response", "time": "12/8", "bpm": 110, "key": "Ab Major", "vocal": None},
    {"id": "SI099", "genre": "Kalimba Ambient", "instruments": ["kalimba", "atmospheric pad", "field recording"],
     "form": "Free-form", "time": "3/4", "bpm": 55, "key": "F# Major", "vocal": None},

    # --- Latin percussion (corpus near 0) ---
    {"id": "SI100", "genre": "Capoeira", "instruments": ["berimbau", "pandeiro", "atabaque"],
     "form": "Call-and-Response", "time": "4/4", "bpm": 120, "key": "Bb Minor", "vocal": None},
    {"id": "SI101", "genre": "Salsa", "instruments": ["timbales", "trumpet", "piano montuno"],
     "form": "Verse-Montuno", "time": "4/4", "bpm": 98, "key": "F Minor", "vocal": None},
    {"id": "SI102", "genre": "Bachata", "instruments": ["nylon-string guitar", "bongos", "güiro"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 130, "key": "A Minor", "vocal": None},

    # --- European rare (corpus = 0) ---
    {"id": "SI103", "genre": "Klezmer", "instruments": ["clarinet", "accordion", "violin"],
     "form": "AABB", "time": "4/4", "bpm": 130, "key": "Db Minor", "vocal": None},
    {"id": "SI104", "genre": "Russian Folk", "instruments": ["balalaika", "accordion", "domra"],
     "form": "Strophic", "time": "2/4", "bpm": 140, "key": "A Minor", "vocal": None},
    {"id": "SI105", "genre": "Andean Folk", "instruments": ["charango", "pan flute", "bombo drum"],
     "form": "Strophic", "time": "4/4", "bpm": 100, "key": "Bb Minor", "vocal": None},
    {"id": "SI106", "genre": "Scottish Highland", "instruments": ["bagpipe", "snare drum", "fiddle"],
     "form": "March", "time": "6/8", "bpm": 110, "key": "A Major", "vocal": None},

    # --- Rare keyboard instruments ---
    {"id": "SI107", "genre": "Harpsichord Concerto", "instruments": ["harpsichord", "string ensemble", "oboe"],
     "form": "Ritornello", "time": "3/4", "bpm": 105, "key": "Db Major", "vocal": None},
    {"id": "SI108", "genre": "Celesta Lullaby", "instruments": ["celesta", "harp", "soft strings"],
     "form": "Strophic", "time": "6/8", "bpm": 48, "key": "F# Major", "vocal": None},

    # --- Rare electronic ---
    {"id": "SI109", "genre": "Theremin Ambient", "instruments": ["theremin", "modular synth", "tape loops"],
     "form": "Free-form", "time": "5/4", "bpm": 40, "key": "Eb Minor", "vocal": None},
    {"id": "SI110", "genre": "Chiptune", "instruments": ["8-bit square wave", "triangle bass", "noise percussion"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 155, "key": "Bb Major", "vocal": None},

    # --- Underrepresented woodwinds ---
    {"id": "SI111", "genre": "Bassoon Quartet", "instruments": ["bassoon", "oboe", "clarinet"],
     "form": "Rondo (ABACA)", "time": "3/4", "bpm": 100, "key": "F Major", "vocal": None},
    {"id": "SI112", "genre": "Recorder Consort", "instruments": ["soprano recorder", "alto recorder", "bass recorder"],
     "form": "Binary (AB)", "time": "3/4", "bpm": 88, "key": "Db Major", "vocal": None},

    # --- Underrepresented tuned percussion ---
    {"id": "SI113", "genre": "Marimba Ensemble", "instruments": ["marimba", "vibraphone", "glockenspiel"],
     "form": "Theme-Variations", "time": "5/4", "bpm": 120, "key": "Bb Major", "vocal": None},
    {"id": "SI114", "genre": "Steel Drum Calypso", "instruments": ["steel drum", "bass guitar", "cowbell"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 118, "key": "F Major", "vocal": None},
    {"id": "SI115", "genre": "Hang Drum Meditation", "instruments": ["hang drum", "atmospheric pad", "field recording"],
     "form": "Free-form", "time": "4/4", "bpm": 60, "key": "Db Minor", "vocal": None},

    # --- Taiko focused ---
    {"id": "SI116", "genre": "Taiko Ensemble", "instruments": ["taiko drums", "shime-daiko", "kane"],
     "form": "Through-composed", "time": "4/4", "bpm": 92, "key": "Db Major", "vocal": None},

    # --- Mongolian ---
    {"id": "SI117", "genre": "Mongolian Throat Singing", "instruments": ["morin khuur", "throat singing drone", "frame drum"],
     "form": "Through-composed", "time": "4/4", "bpm": 62, "key": "Eb Minor", "vocal": "Mongolian"},

    # --- Remaining zero-keys (G#/Ab minor coverage) ---
    {"id": "SI118", "genre": "Dubstep", "instruments": ["wobble bass", "aggressive sub-bass", "half-time drums"],
     "form": "Build-Drop", "time": "4/4", "bpm": 140, "key": "Ab Minor", "vocal": None},
    {"id": "SI119", "genre": "Enka", "instruments": ["shamisen", "koto", "shakuhachi"],
     "form": "Strophic", "time": "4/4", "bpm": 70, "key": "C# Minor", "vocal": "Japanese"},
    {"id": "SI120", "genre": "Fado", "instruments": ["Portuguese guitar", "nylon-string guitar", "upright bass"],
     "form": "Strophic", "time": "3/4", "bpm": 65, "key": "F Minor", "vocal": "Portuguese"},
]

# ═══════════════════════════════════════════════════════════════
# SESSION 4: 121-160 — CROSS-GENRE + REMAINING HOLES
# ═══════════════════════════════════════════════════════════════

songs += [
    # --- Cross-genre (never tested combos) ---
    {"id": "SI121", "genre": "Sitar + Drum and Bass", "instruments": ["sitar", "fast breakbeat", "reese bass"],
     "form": "Build-Drop", "time": "4/4", "bpm": 174, "key": "A Minor", "vocal": None},
    {"id": "SI122", "genre": "Erhu + Ambient", "instruments": ["erhu", "synth pad", "distant percussion"],
     "form": "Free-form", "time": "3/4", "bpm": 45, "key": "C# Minor", "vocal": None},
    {"id": "SI123", "genre": "Banjo + Electronica", "instruments": ["banjo", "electronic beats", "synth bass"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 128, "key": "Bb Major", "vocal": None},
    {"id": "SI124", "genre": "Koto + Jazz", "instruments": ["koto", "upright bass", "brush drums"],
     "form": "AABA", "time": "4/4", "bpm": 95, "key": "F# Minor", "vocal": None},
    {"id": "SI125", "genre": "Accordion + Trance", "instruments": ["accordion", "supersaw synth", "four-on-the-floor kick"],
     "form": "Build-Drop", "time": "4/4", "bpm": 138, "key": "Db Minor", "vocal": None},
    {"id": "SI126", "genre": "Bagpipe + Metal", "instruments": ["bagpipe", "distorted guitar", "blast beats"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 165, "key": "Ab Minor", "vocal": None},
    {"id": "SI127", "genre": "Steel Drum + Hip-Hop", "instruments": ["steel drum", "808 bass", "hi-hat triplets"],
     "form": "Loop-based", "time": "4/4", "bpm": 88, "key": "Eb Major", "vocal": None},
    {"id": "SI128", "genre": "Oud + Dubstep", "instruments": ["oud", "wobble bass", "half-time drums"],
     "form": "Build-Drop", "time": "4/4", "bpm": 140, "key": "Bb Minor", "vocal": None},
    {"id": "SI129", "genre": "Guzheng + Lo-fi", "instruments": ["guzheng", "vinyl crackle", "soft electronic beat"],
     "form": "Loop-based", "time": "4/4", "bpm": 78, "key": "F# Minor", "vocal": None},
    {"id": "SI130", "genre": "Tango + Electronica", "instruments": ["bandoneón", "electronic beats", "synth strings"],
     "form": "AABB", "time": "4/4", "bpm": 78, "key": "Ab Minor", "vocal": None},
    {"id": "SI131", "genre": "Celtic + Drum and Bass", "instruments": ["tin whistle", "fast breakbeat", "reese bass"],
     "form": "Build-Drop", "time": "4/4", "bpm": 172, "key": "A Major", "vocal": None},
    {"id": "SI132", "genre": "Didgeridoo + Ambient", "instruments": ["didgeridoo", "drone pad", "rain stick"],
     "form": "Free-form", "time": "4/4", "bpm": 35, "key": "Db Minor", "vocal": None},

    # --- Remaining genre frontier (untested 25) ---
    {"id": "SI133", "genre": "Vaporwave", "instruments": ["lo-fi synthesizer", "pitch-shifted sample", "retro pad"],
     "form": "Loop-based", "time": "4/4", "bpm": 85, "key": "Ab Major", "vocal": None},
    {"id": "SI134", "genre": "Tech House", "instruments": ["punchy kick", "rolling bassline", "hi-hat pattern"],
     "form": "Loop-based", "time": "4/4", "bpm": 126, "key": "F Minor", "vocal": None},
    {"id": "SI135", "genre": "Deep House", "instruments": ["warm pad", "deep bass", "organic percussion"],
     "form": "Build-Drop", "time": "4/4", "bpm": 122, "key": "Bb Minor", "vocal": None},
    {"id": "SI136", "genre": "Grime", "instruments": ["aggressive synth stab", "deep sub-bass", "percussive hi-hat"],
     "form": "Loop-based", "time": "4/4", "bpm": 140, "key": "C# Minor", "vocal": None},
    {"id": "SI137", "genre": "Memphis Phonk", "instruments": ["lo-fi 808", "pitched vocal sample", "tape-saturated drums"],
     "form": "Loop-based", "time": "4/4", "bpm": 130, "key": "Ab Minor", "vocal": None},
    {"id": "SI138", "genre": "Dembow", "instruments": ["deep 808 bass", "dembow drum pattern", "synth stab"],
     "form": "Loop-based", "time": "4/4", "bpm": 100, "key": "Bb Minor", "vocal": None},
    {"id": "SI139", "genre": "Black Metal Ambient", "instruments": ["tremolo-picked guitar", "synth pad", "sparse drums"],
     "form": "Through-composed", "time": "4/4", "bpm": 160, "key": "Db Minor", "vocal": None},
    {"id": "SI140", "genre": "Metalcore", "instruments": ["down-tuned guitar", "screamed vocals tag", "breakdown drums"],
     "form": "Verse-Breakdown", "time": "4/4", "bpm": 150, "key": "C# Minor", "vocal": None},
    {"id": "SI141", "genre": "Slowcore", "instruments": ["sparse clean guitar", "brushed snare", "fretless bass"],
     "form": "Verse-Chorus", "time": "3/4", "bpm": 55, "key": "F# Minor", "vocal": None},
    {"id": "SI142", "genre": "Jangle Pop", "instruments": ["bright arpeggiated 12-string", "bass guitar", "upbeat drums"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 128, "key": "A Major", "vocal": None},
    {"id": "SI143", "genre": "Post-punk", "instruments": ["chorus delay guitar", "prominent bass guitar", "gated snare"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 142, "key": "Db Minor", "vocal": None},
    {"id": "SI144", "genre": "Neo-folk", "instruments": ["dark acoustic guitar", "drone cello", "frame drum"],
     "form": "Strophic", "time": "3/4", "bpm": 60, "key": "Eb Minor", "vocal": None},
    {"id": "SI145", "genre": "Outlaw Country", "instruments": ["acoustic guitar", "upright bass", "pedal steel"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 100, "key": "A Major", "vocal": None},
    {"id": "SI146", "genre": "Drift Phonk", "instruments": ["distorted cowbell", "aggressive 808", "dark synth"],
     "form": "Loop-based", "time": "4/4", "bpm": 134, "key": "Ab Minor", "vocal": None},

    # --- Solo/Duo showcases (low instrument count = different SP structure) ---
    {"id": "SI147", "genre": "Solo Cello", "instruments": ["cello"],
     "form": "Through-composed", "time": "3/4", "bpm": 48, "key": "Eb Minor", "vocal": None},
    {"id": "SI148", "genre": "Solo Acoustic Guitar", "instruments": ["fingerpicked acoustic guitar"],
     "form": "Through-composed", "time": "6/8", "bpm": 72, "key": "Db Major", "vocal": None},
    {"id": "SI149", "genre": "Saxophone + Piano", "instruments": ["tenor saxophone", "piano"],
     "form": "AABA", "time": "4/4", "bpm": 68, "key": "Bb Minor", "vocal": None},
    {"id": "SI150", "genre": "Violin + Harp", "instruments": ["violin", "harp"],
     "form": "Binary (AB)", "time": "3/4", "bpm": 85, "key": "F# Minor", "vocal": None},
    {"id": "SI151", "genre": "Solo Harp", "instruments": ["concert harp"],
     "form": "Through-composed", "time": "3/4", "bpm": 62, "key": "Ab Major", "vocal": None},
    {"id": "SI152", "genre": "Organ Fugue", "instruments": ["pipe organ"],
     "form": "Fugue", "time": "4/4", "bpm": 72, "key": "C# Minor", "vocal": None},

    # --- Remaining odd meters ---
    {"id": "SI153", "genre": "Aksak Folk", "instruments": ["zurna", "davul", "tambura"],
     "form": "Strophic", "time": "9/8", "bpm": 130, "key": "Bb Minor", "vocal": None},
    {"id": "SI154", "genre": "Prog Jazz", "instruments": ["piano", "upright bass", "drums"],
     "form": "Through-composed", "time": "11/8", "bpm": 130, "key": "Eb Minor", "vocal": None},
    {"id": "SI155", "genre": "Indian Tabla Solo", "instruments": ["tabla", "tanpura"],
     "form": "Through-composed", "time": "7/8", "bpm": 90, "key": "Db Major", "vocal": None},

    # --- Extreme BPM remaining ---
    {"id": "SI156", "genre": "Extratone", "instruments": ["hyper-speed kick", "noise texture", "dissonant synth"],
     "form": "Free-form", "time": "4/4", "bpm": 300, "key": "A Minor", "vocal": None},
    {"id": "SI157", "genre": "Noise Ambient", "instruments": ["white noise", "feedback drone", "reversed cymbal"],
     "form": "Free-form", "time": "4/4", "bpm": 30, "key": "C# Minor", "vocal": None},

    # --- Remaining 3 ---
    {"id": "SI158", "genre": "Zouk", "instruments": ["synthesizer", "electric guitar", "ka drum"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 108, "key": "F Minor", "vocal": None},
    {"id": "SI159", "genre": "Berlin School", "instruments": ["sequenced synth", "arpeggiated synth", "atmospheric pad"],
     "form": "Free-form", "time": "5/4", "bpm": 42, "key": "Db Minor", "vocal": None},
    {"id": "SI160", "genre": "Glitch", "instruments": ["granular synthesis", "detuned piano", "stuttered percussion"],
     "form": "Free-form", "time": "11/8", "bpm": 110, "key": "Eb Minor", "vocal": None},
]

# ═══════════════════════════════════════════════════════════════
# SESSION 5: 161-200 — VOCAL CONCENTRATION + FINAL GAPS
# ═══════════════════════════════════════════════════════════════

songs += [
    # --- Vocal tracks (14 languages) ---
    {"id": "SI161", "genre": "Italian Opera Aria", "instruments": ["full orchestra", "grand piano", "harp"],
     "form": "Through-composed", "time": "3/4", "bpm": 68, "key": "Ab Major", "vocal": "Italian"},
    {"id": "SI162", "genre": "Italian Art Song", "instruments": ["piano", "strings", "oboe"],
     "form": "Strophic", "time": "6/8", "bpm": 58, "key": "Db Major", "vocal": "Italian"},
    {"id": "SI163", "genre": "French Chanson", "instruments": ["accordion", "nylon-string guitar", "upright bass"],
     "form": "Strophic", "time": "3/4", "bpm": 90, "key": "F Minor", "vocal": "French"},
    {"id": "SI164", "genre": "Spanish Bolero", "instruments": ["nylon-string guitar", "congas", "upright bass"],
     "form": "Strophic", "time": "4/4", "bpm": 62, "key": "A Minor", "vocal": "Spanish"},
    {"id": "SI165", "genre": "Brazilian Bossa Nova", "instruments": ["nylon-string guitar", "electric piano", "soft percussion"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 72, "key": "Db Major", "vocal": "Portuguese"},
    {"id": "SI166", "genre": "German Lied", "instruments": ["grand piano"],
     "form": "Through-composed", "time": "3/4", "bpm": 55, "key": "Eb Major", "vocal": "German"},
    {"id": "SI167", "genre": "Hindi Film Song", "instruments": ["sitar", "tabla", "strings"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 95, "key": "Bb Minor", "vocal": "Hindi"},
    {"id": "SI168", "genre": "Swahili Pop", "instruments": ["electric guitar", "bass guitar", "percussion"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 110, "key": "Ab Major", "vocal": "Swahili"},
    {"id": "SI169", "genre": "Arabic Pop", "instruments": ["oud", "darbuka", "strings"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 95, "key": "Bb Phrygian", "vocal": "Arabic"},
    {"id": "SI170", "genre": "K-Ballad Vocal", "instruments": ["grand piano", "strings", "gentle drums"],
     "form": "Verse-Chorus-Bridge", "time": "4/4", "bpm": 68, "key": "Db Major", "vocal": "Korean"},
    {"id": "SI171", "genre": "K-Trot Vocal", "instruments": ["accordion", "saxophone", "electric bass"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 122, "key": "A Major", "vocal": "Korean"},
    {"id": "SI172", "genre": "Chinese Ballad", "instruments": ["erhu", "piano", "strings"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 70, "key": "F# Minor", "vocal": "Mandarin"},
    {"id": "SI173", "genre": "Irish Gaelic Folk", "instruments": ["tin whistle", "bodhrán", "acoustic guitar"],
     "form": "Strophic", "time": "6/8", "bpm": 100, "key": "A Major", "vocal": "Irish Gaelic"},
    {"id": "SI174", "genre": "Hawaiian Slack-key", "instruments": ["slack-key guitar", "ukulele", "steel guitar"],
     "form": "Strophic", "time": "4/4", "bpm": 85, "key": "Bb Major", "vocal": "Hawaiian"},
    {"id": "SI175", "genre": "Turkish Folk", "instruments": ["bağlama", "ney", "frame drum"],
     "form": "Strophic", "time": "9/8", "bpm": 88, "key": "Eb Phrygian", "vocal": "Turkish"},

    # --- Remaining instrumental gaps ---
    {"id": "SI176", "genre": "Reggaeton", "instruments": ["dembow rhythm", "staccato synth bass", "atmospheric pad"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 95, "key": "C# Minor", "vocal": None},
    {"id": "SI177", "genre": "Garage Rock", "instruments": ["overdriven guitar", "bass guitar", "lo-fi drums"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 150, "key": "A Minor", "vocal": None},
    {"id": "SI178", "genre": "New Wave", "instruments": ["sequenced synth", "fretless bass", "electronic drums"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 135, "key": "Bb Major", "vocal": None},
    {"id": "SI179", "genre": "Synth Punk", "instruments": ["distorted synth", "aggressive bass", "four-on-the-floor kick"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 162, "key": "C# Minor", "vocal": None},
    {"id": "SI180", "genre": "Space Rock", "instruments": ["reverb guitar", "synthesizer", "echo drums"],
     "form": "Through-composed", "time": "4/4", "bpm": 100, "key": "Eb Minor", "vocal": None},

    {"id": "SI181", "genre": "Boogie", "instruments": ["talk box guitar", "bass guitar", "electronic drums"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 112, "key": "Ab Minor", "vocal": None},
    {"id": "SI182", "genre": "City Pop", "instruments": ["slap bass", "clean electric guitar", "electric piano"],
     "form": "Verse-Chorus-Bridge", "time": "4/4", "bpm": 110, "key": "F# Major", "vocal": None},
    {"id": "SI183", "genre": "K-Pop Dance", "instruments": ["synthesizer", "sub-bass", "crisp snare"],
     "form": "Verse-Chorus-Bridge", "time": "4/4", "bpm": 125, "key": "Db Minor", "vocal": None},
    {"id": "SI184", "genre": "K-Indie", "instruments": ["clean electric guitar", "soft synth pad", "light drums"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 100, "key": "Bb Major", "vocal": None},
    {"id": "SI185", "genre": "K-Rock", "instruments": ["distorted guitar", "palm-muted riffs", "driving drums"],
     "form": "Verse-Chorus-Bridge", "time": "4/4", "bpm": 138, "key": "Ab Minor", "vocal": None},

    # --- Final extreme experiments ---
    {"id": "SI186", "genre": "Microtonal Experiment", "instruments": ["microtonal synthesizer", "detuned piano", "percussion"],
     "form": "Free-form", "time": "5/4", "bpm": 75, "key": "Quarter-tone D", "vocal": None},
    {"id": "SI187", "genre": "Polyrhythm Study", "instruments": ["marimba", "djembe", "shakers"],
     "form": "Through-composed", "time": "7/8", "bpm": 110, "key": "Ab Major", "vocal": None},
    {"id": "SI188", "genre": "Silence Study", "instruments": ["prepared piano", "long pauses", "single bell"],
     "form": "Free-form", "time": "4/4", "bpm": 25, "key": "Db Major", "vocal": None},
    {"id": "SI189", "genre": "Feedback Noise", "instruments": ["guitar feedback", "noise generator", "industrial drums"],
     "form": "Free-form", "time": "4/4", "bpm": 220, "key": "Atonal", "vocal": None},
    {"id": "SI190", "genre": "Binaural Drone", "instruments": ["binaural beat synth", "sub-bass oscillator", "wind texture"],
     "form": "Free-form", "time": "4/4", "bpm": 30, "key": "F Minor", "vocal": None},

    # --- Pentatonic/Chromatic keys ---
    {"id": "SI191", "genre": "Pentatonic Ambient", "instruments": ["crystal singing bowls", "synth pad", "wind chimes"],
     "form": "Free-form", "time": "4/4", "bpm": 40, "key": "A Pentatonic", "vocal": None},
    {"id": "SI192", "genre": "Chromatic Etude", "instruments": ["piano", "violin", "cello"],
     "form": "Through-composed", "time": "3/4", "bpm": 90, "key": "Chromatic", "vocal": None},
    {"id": "SI193", "genre": "Lydian Dream", "instruments": ["electric piano", "synth pad", "soft drums"],
     "form": "Verse-Chorus", "time": "6/8", "bpm": 82, "key": "F Lydian", "vocal": None},
    {"id": "SI194", "genre": "Aeolian Rock", "instruments": ["clean guitar", "bass guitar", "drums"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 112, "key": "A Aeolian", "vocal": None},

    # --- Final remaining instruments ---
    {"id": "SI195", "genre": "Dulcimer Folk", "instruments": ["hammered dulcimer", "fiddle", "acoustic guitar"],
     "form": "Strophic", "time": "3/4", "bpm": 98, "key": "Db Major", "vocal": None},
    {"id": "SI196", "genre": "Zither Classical", "instruments": ["zither", "violin", "cello"],
     "form": "Through-composed", "time": "3/4", "bpm": 65, "key": "F# Minor", "vocal": None},
    {"id": "SI197", "genre": "Ukulele Pop", "instruments": ["ukulele", "light percussion", "bass"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 118, "key": "Bb Major", "vocal": None},
    {"id": "SI198", "genre": "Melodica Reggae", "instruments": ["melodica", "heavy bass", "spring reverb snare"],
     "form": "Verse-Chorus", "time": "4/4", "bpm": 76, "key": "Eb Major", "vocal": None},
    {"id": "SI199", "genre": "Cimbalom Jazz", "instruments": ["cimbalom", "upright bass", "brush drums"],
     "form": "AABA", "time": "4/4", "bpm": 100, "key": "Db Minor", "vocal": None},
    {"id": "SI200", "genre": "Glass Harmonica", "instruments": ["glass harmonica", "harp", "sustained strings"],
     "form": "Through-composed", "time": "3/4", "bpm": 50, "key": "Ab Major", "vocal": None},
]


# ═══════════════════════════════════════════════════════════════
# STATISTICS & GAP ANALYSIS
# ═══════════════════════════════════════════════════════════════

from collections import Counter
import re

all_genres = Counter(s["genre"] for s in songs)
all_instruments = Counter()
for s in songs:
    for i in s["instruments"]:
        all_instruments[i] += 1
all_times = Counter(s["time"] for s in songs)
all_forms = Counter(s["form"] for s in songs)
vocal_songs = [s for s in songs if s["vocal"]]
vocal_langs = Counter(s["vocal"] for s in vocal_songs)

# Key root analysis
key_roots = Counter()
key_modes = Counter()
for s in songs:
    k = s["key"]
    root_match = re.match(r'([A-G][b#]?)', k)
    if root_match:
        key_roots[root_match.group(1)] += 1
    if "Major" in k: key_modes["Major"] += 1
    elif "Minor" in k or "minor" in k: key_modes["Minor"] += 1
    elif any(m in k for m in ["Dorian","Phrygian","Lydian","Mixolydian","Locrian","Aeolian","Pentatonic","Whole Tone","Chromatic"]):
        key_modes["Modal/Other"] += 1
    else: key_modes["Other"] += 1

bpm_buckets = Counter()
for s in songs:
    b = s["bpm"]
    if b < 40: bpm_buckets["<40"] += 1
    elif b < 60: bpm_buckets["40-59"] += 1
    elif b < 80: bpm_buckets["60-79"] += 1
    elif b < 100: bpm_buckets["80-99"] += 1
    elif b < 120: bpm_buckets["100-119"] += 1
    elif b < 140: bpm_buckets["120-139"] += 1
    elif b < 160: bpm_buckets["140-159"] += 1
    elif b < 180: bpm_buckets["160-179"] += 1
    elif b < 220: bpm_buckets["180-219"] += 1
    else: bpm_buckets["220+"] += 1

print(f"Total songs: {len(songs)}")
print(f"Unique genres: {len(all_genres)}")
print(f"Unique instrument combos: {len(all_instruments)}")
print(f"Unique time signatures: {len(all_times)}")
print(f"Unique forms: {len(all_forms)}")
print(f"Vocal tracks: {len(vocal_songs)} ({len(vocal_langs)} languages)")

print(f"\n{'='*60}")
print("GAP TARGETING RESULTS")
print(f"{'='*60}")

print("\n=== Key Root Distribution (corpus gaps = A, Bb, Ab, F#, Eb, C#, Db) ===")
corpus_zero = {'A','Bb','Ab','F#','Eb','C#','Db'}
for note in ['C','C#','Db','D','D#','Eb','E','F','F#','Gb','G','G#','Ab','A','A#','Bb','B']:
    c = key_roots.get(note, 0)
    tag = " ★ ZERO-KEY" if note in corpus_zero else ""
    bar = '█' * c
    print(f"  {note:3s}  {c:3d}  {bar}{tag}")

print(f"\n=== Mode Distribution (corpus: Major 84%, Minor 16%, Modal 0%) ===")
for m, c in key_modes.most_common():
    pct = c / len(songs) * 100
    print(f"  {m:15s}  {c:3d}  ({pct:.1f}%)")

print(f"\n=== BPM Distribution (corpus: 70-79=31.7%, <60=0%, 150+=5.6%) ===")
for bucket in ["<40","40-59","60-79","80-99","100-119","120-139","140-159","160-179","180-219","220+"]:
    c = bpm_buckets.get(bucket, 0)
    pct = c / len(songs) * 100
    bar = '█' * c
    print(f"  {bucket:8s}  {c:3d}  ({pct:4.1f}%)  {bar}")

print(f"\n=== Time Signature Distribution (corpus: 4/4=98%, 3/4=1.3%, 6/8=0.4%) ===")
for t, c in all_times.most_common():
    pct = c / len(songs) * 100
    print(f"  {t:6s}  {c:3d}  ({pct:4.1f}%)")

print(f"\n=== Song Form Distribution ===")
for f, c in all_forms.most_common():
    print(f"  {c:3d}  {f}")

print(f"\n=== Vocal Languages ({len(vocal_songs)} tracks) ===")
for l, c in vocal_langs.most_common():
    print(f"  {c:2d}  {l}")

print(f"\n=== Session Breakdown ===")
for sess in range(5):
    start = sess * 40
    batch = songs[start:start+40]
    v_count = len([s for s in batch if s["vocal"]])
    non44 = len([s for s in batch if s["time"] != "4/4"])
    genres_in_batch = len(set(s["genre"] for s in batch))
    print(f"  Session {sess+1}: SI{batch[0]['id'][2:]:>03s}–SI{batch[-1]['id'][2:]:>03s}  "
          f"({len(batch)} songs, {v_count} vocal, {non44} non-4/4, {genres_in_batch} genres)")

# Write JSON
output_path = Path("/Users/leo/sunolanguage/data/s_inst200/s_inst200_plan.json")
with open(output_path, "w") as f:
    json.dump({
        "series": "S_INST200",
        "version": "2.0",
        "description": "200-song gap-targeting batch — corpus blind spots only",
        "design_principle": "NOT good music. Fill every hole in key/BPM/time sig/instrument/genre.",
        "total_songs": len(songs),
        "sessions": 5,
        "songs_per_session": 40,
        "vocal_tracks": len(vocal_songs),
        "unique_genres": len(all_genres),
        "unique_instruments": len(all_instruments),
        "gap_targeting": {
            "zero_keys_covered": sorted(list(corpus_zero)),
            "modal_keys_introduced": True,
            "bpm_range": f"{min(s['bpm'] for s in songs)}-{max(s['bpm'] for s in songs)}",
            "non_44_count": len([s for s in songs if s["time"] != "4/4"]),
            "non_44_pct": round(len([s for s in songs if s["time"] != "4/4"]) / len(songs) * 100, 1),
        },
        "created_at": "2026-05-25",
        "songs": songs,
    }, f, ensure_ascii=False, indent=2)

print(f"\n✅ Plan v2 saved to {output_path}")
