#!/usr/bin/env python3
"""
Suno Native Vocabulary Dictionary v3.0 빌더
- v2.0 기반 + 5개 신규 축: negative_vocab, top_anchor_weights, genre_frontier, output_variance, studio_stem_map
- 외부 레퍼런스 기반 genre_frontier 초기값 포함
- S003/S004/S016-S017/S018 재분석 결과 수신 시 corpus 자동 확장
"""

# ============================================================
# ⚠️  WARNING — BORYU (보류 / DO NOT RUN AS-IS) — LEO decision
# ============================================================
# This builder is RETIRED. Running it now REGRESSES the curated dictionary.
# rag/suno_dictionary_v3.json is currently the hand-curated **v3.1**, NOT the
# v3.0 this script emits. Re-running build() will OVERWRITE v3.1 with v3.0 and:
#
#   (a) Stamp the output back to "version": "3.0" (see line ~540), dropping
#       the v3.1 designation entirely.
#   (b) DELETE the v3.1 hand-curation: update_notes, the DB cross-reference,
#       and the ~25 manually enriched entries — none of these are reproduced
#       by build() and all are lost on overwrite of OUT_PATH.
#   (c) NOT actually produce a v3.2. vocab_expansion_v3.2.json is DEAD-LOADED:
#       V32_EXP_PATH is read into `v32_exp` inside build() (the
#       `with open(V32_EXP_PATH) ...` line) but that variable is never consumed
#       anywhere in build() — it has zero effect on the assembled dictionary.
#
# A genuine v3.2 build would require CODE CHANGES, not just a re-run:
#   - consume `v32_exp` (vocab_expansion) into the assembled dictionary, and
#   - merge/preserve the existing v3.1 enrichments (update_notes, db-crossref,
#     the ~25 enriched entries) instead of overwriting them.
#
# Until that work is done: DO NOT execute build(). Importing this module is safe
# (no writes happen at import time — writing only occurs inside build()).
# ============================================================

import json
import sqlite3
import collections
from pathlib import Path
from datetime import date

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "data/reanalysis_v2/lexical_index.sqlite"
V32_PATH = BASE / "data/reanalysis_v2/suno_native_standard_v3.2.json"
V32_EXP_PATH = BASE / "data/reanalysis_v2/vocab_expansion_v3.2.json"
GENRE_FRONTIER_PATH = BASE / "rag/genre_frontier.json"
OUT_PATH = BASE / "rag/suno_dictionary_v3.json"

# 추가 corpus 소스 (수신 시 활성화)
EXTRA_CORPUS_DIRS = [
    BASE / "data/test_s003",
    BASE / "data/test_s004",
    BASE / "data/test_s016",
    BASE / "data/test_s017",
    BASE / "data/test_s018",
]


def query_all(cur, sql, params=None):
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    return cur.fetchall()


def build_corpus_stats(cur):
    total_entries = query_all(cur, "SELECT COUNT(*) FROM entries")[0][0]
    unique_words = query_all(cur, "SELECT COUNT(*) FROM words")[0][0]
    total_songs = query_all(cur, "SELECT COUNT(DISTINCT song_id) FROM entries")[0][0]
    total_genres = query_all(cur, "SELECT COUNT(DISTINCT genre) FROM entries")[0][0]
    return {
        "tracks_count": total_songs,
        "unique_words": unique_words,
        "total_entries": total_entries,
        "genres_count": total_genres,
        "sources": [
            "leomusic 생성곡 318곡",
            "Wave 1 외부곡 60곡 (19개 장르)",
            "stems 분리 분석 95곡",
            "Dead Budget 라운드트립 10곡",
            # 아래는 수신 시 추가
            # "S003 주법·기법 심화 12곡",
            # "S004 장르 교차 12곡",
            # "S016-S017 레스토랑 BGM 20곡",
            # "S018 Genre Frontier 16곡",
        ]
    }


def build_instrument_phrases(cur):
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt, COUNT(DISTINCT genre) as gs
        FROM entries WHERE slot='instrument'
        GROUP BY entity ORDER BY cnt DESC
    """)
    result = {}
    for entity, cnt, gs in rows:
        esc = entity.replace("'", "''")
        patterns = query_all(cur, f"""
            SELECT pattern, COUNT(*) as pc FROM entries
            WHERE slot='instrument' AND entity='{esc}' AND pattern != ''
            GROUP BY pattern ORDER BY pc DESC LIMIT 5
        """)
        modifiers = query_all(cur, f"""
            SELECT modifiers, COUNT(*) as mc FROM entries
            WHERE slot='instrument' AND entity='{esc}' AND modifiers != '[]' AND modifiers != ''
            GROUP BY modifiers ORDER BY mc DESC LIMIT 5
        """)
        result[entity] = {
            "count": cnt,
            "genre_spread": gs,
            "top_patterns": [{"pattern": p, "freq": f} for p, f in patterns],
            "top_modifiers": [{"modifier": m, "freq": f} for m, f in modifiers]
        }
    return result


def build_technique_patterns(cur):
    rows = query_all(cur, """
        SELECT pattern, COUNT(*) as cnt FROM entries
        WHERE pattern != '' AND pattern IS NOT NULL AND slot='instrument'
        GROUP BY pattern ORDER BY cnt DESC LIMIT 100
    """)
    return {p: {"count": c} for p, c in rows}


def build_production_vocab(cur):
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot IN ('mixing', 'effect_electronic', 'effect_sound', 'mastering')
        GROUP BY entity ORDER BY cnt DESC
    """)
    return {e: {"count": c} for e, c in rows}


def build_key_signatures(cur):
    rows = query_all(cur, "SELECT entity FROM entries WHERE slot='tempo_key_time'")
    key_counts = collections.Counter()
    bpm_counts = collections.Counter()
    ts_counts = collections.Counter()
    for (entity_str,) in rows:
        try:
            obj = json.loads(entity_str)
            if obj.get("key"):
                key_counts[obj["key"]] += 1
            if obj.get("bpm"):
                bpm_counts[obj["bpm"]] += 1
            if obj.get("time_signature"):
                ts_counts[obj["time_signature"]] += 1
        except (json.JSONDecodeError, TypeError):
            pass
    return {
        "keys": {k: c for k, c in key_counts.most_common(30)},
        "bpm": {str(k): c for k, c in bpm_counts.most_common(20)},
        "time_signatures": {k: c for k, c in ts_counts.most_common(10)}
    }


def build_harmony_vocab(cur):
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot='harmony'
        GROUP BY entity ORDER BY cnt DESC
    """)
    return {e: {"count": c} for e, c in rows}


def build_mood_and_timbre(cur):
    mood_words = [
        'warm', 'gritty', 'cinematic', 'dreamy', 'mellow', 'ethereal',
        'intimate', 'melancholic', 'atmospheric', 'lush', 'dark', 'bright',
        'emotional', 'soulful', 'upbeat', 'nostalgic', 'haunting', 'moody',
        'punchy', 'aggressive', 'smooth', 'delicate', 'dramatic', 'playful',
        'somber', 'energetic', 'sultry', 'euphoric', 'brooding', 'serene'
    ]
    mood_emotion = {}
    for w in mood_words:
        row = query_all(cur, "SELECT freq_total, freq_sp, freq_bracket, freq_input "
                             "FROM words WHERE word=?", (w,))
        if row:
            # ★층은 값 옆에 — count/sp/bracket 은 **Suno 출력층**, input 은 우리가 써넣은 입력층.
            #   input 만 있고 count==0 이면 「우리는 썼는데 Suno 관측 0」이다(키는 지우지 않는다:
            #   지우면 증분 병합기가 큐레이션으로 보고 옛 오염값을 되살린다).
            mood_emotion[w] = {"count": row[0][0], "sp": row[0][1],
                               "bracket": row[0][2], "input": row[0][3]}

    timbre_words = [
        'distorted', 'soft', 'resonant', 'compressed', 'saturated', 'crisp',
        'muddy', 'clean', 'heavy', 'airy', 'thick', 'thin', 'fuzzy',
        'metallic', 'glassy', 'woody', 'breathy', 'nasal', 'hollow',
        'punchy', 'boomy', 'shimmering', 'lo-fi', 'hi-fi', 'analog'
    ]
    timbre_texture = {}
    for w in timbre_words:
        row = query_all(cur, "SELECT freq_total, freq_sp, freq_bracket, freq_input "
                             "FROM words WHERE word=?", (w,))
        if row:
            timbre_texture[w] = {"count": row[0][0], "sp": row[0][1],
                                 "bracket": row[0][2], "input": row[0][3]}

    return mood_emotion, timbre_texture


def build_tempo_rhythm(cur):
    tempo_words = [
        'syncopated', 'steady', 'driving', 'swung', 'shuffle', 'rubato',
        'staccato', 'legato', 'arpeggiated', 'fingerpicked', 'strummed',
        'palm-muted', 'spiccato', 'pizzicato', 'tremolo', 'trill'
    ]
    result = {}
    for w in tempo_words:
        row = query_all(cur, "SELECT freq_total, freq_sp, freq_bracket, freq_input "
                             "FROM words WHERE word=?", (w,))
        if row:
            result[w] = {"count": row[0][0], "sp": row[0][1],
                         "bracket": row[0][2], "input": row[0][3]}
    return result


def build_dynamics_structure(cur):
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot='arrangement'
        GROUP BY entity ORDER BY cnt DESC LIMIT 40
    """)
    return {e: {"count": c} for e, c in rows}


def build_vocal(cur):
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot='vocal_main'
        GROUP BY entity ORDER BY cnt DESC LIMIT 60
    """)
    vocal_expressions = {e: {"count": c} for e, c in rows}

    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot='vocal_chorus'
        GROUP BY entity ORDER BY cnt DESC
    """)
    vocal_chorus = {e: {"count": c} for e, c in rows}
    return vocal_expressions, vocal_chorus


def build_drum_vocab(cur):
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt, COUNT(DISTINCT genre) as gs FROM entries
        WHERE slot='drums'
        GROUP BY entity ORDER BY cnt DESC
    """)
    return {entity: {"count": cnt, "genre_spread": gs} for entity, cnt, gs in rows}


def build_genre_vocabulary_map(cur):
    genre_vocabulary_map = {}
    rows = query_all(cur, """
        SELECT genre, COUNT(*) as cnt, COUNT(DISTINCT entity) as unique_entities
        FROM entries GROUP BY genre ORDER BY cnt DESC
    """)
    for genre, cnt, ue in rows:
        if genre is None:
            genre = "(none)"
        esc = genre.replace("'", "''")
        top_instruments = query_all(cur, f"""
            SELECT entity, COUNT(*) as ic FROM entries
            WHERE genre='{esc}' AND slot='instrument'
            GROUP BY entity ORDER BY ic DESC LIMIT 5
        """)
        genre_vocabulary_map[genre] = {
            "total_entries": cnt,
            "unique_entities": ue,
            "top_instruments": [{"entity": e, "freq": f} for e, f in top_instruments]
        }
    return genre_vocabulary_map


def build_descriptor_combos(cur):
    rows = query_all(cur, """
        SELECT word, freq_total FROM words
        WHERE freq_total >= 10
        ORDER BY freq_total DESC LIMIT 300
    """)
    return {w: c for w, c in rows}


# ============================================================
# v3.0 신규 축
# ============================================================

def build_negative_vocab():
    """v5.5에서 확인된 네거티브 프롬프팅 어휘"""
    return {
        "vocal_processing": {
            "terms": ["no autotune", "no vocal effects", "dry vocal", "no pitch correction"],
            "confidence": "high",
            "source": "community + v5.5 반응 확인"
        },
        "production": {
            "terms": ["no reverb", "no compression", "no modern production", "no effects processing"],
            "confidence": "high",
            "source": "community + Blake Crosley reference"
        },
        "instruments": {
            "terms": ["no synths", "no drums", "no percussion", "no electric", "no electric instruments"],
            "confidence": "high",
            "source": "community verified"
        },
        "style": {
            "terms": ["no backing vocals", "no harmony", "no choir", "no clean vocals"],
            "confidence": "medium",
            "source": "S018 테스트 배정 (검증 대기)"
        },
        "mix": {
            "terms": ["no dry mix", "no four-on-the-floor"],
            "confidence": "medium",
            "source": "S018 테스트 배정 (검증 대기)"
        },
        "usage_note": "SP 내에서 'no X' 형태로 배치. v5.5에서 반응 향상 확인. v5.0에서도 일부 유효하나 불안정.",
        "validated_by_s018": False
    }


def build_top_anchor_weights():
    """v5.5 SP 위치별 영향력 가중치"""
    return {
        "formula": "[Genre/Subgenre], [Mood/Energy], [Core Instruments ×2], [Vocal Identity/grain]",
        "positions": {
            "position_1": {
                "role": "genre/subgenre",
                "weight": "highest",
                "description": "SP 첫 단어가 전체 곡 방향 결정"
            },
            "position_2": {
                "role": "mood/energy",
                "weight": "high",
                "description": "에너지 레벨 및 감성 톤"
            },
            "position_3": {
                "role": "core_instruments",
                "weight": "high",
                "description": "주요 악기 2개 (쉼표 구분)"
            },
            "position_4": {
                "role": "vocal_identity",
                "weight": "medium",
                "description": "보컬 특성 또는 'no vocals'"
            },
            "position_5_onwards": {
                "role": "production/details",
                "weight": "low",
                "description": "후반부 디테일은 영향력 감소"
            }
        },
        "effect": "첫 줄 배치 시 global lock — 이후 섹션에서 override 어려움",
        "validated": False,
        "pending_test": "S018 Top-Anchor A/B (16곡 전체 적용, 효과 비교는 기존 corpus와)"
    }


def load_genre_frontier():
    """genre_frontier.json에서 로드 (별도 파일로 관리)"""
    if GENRE_FRONTIER_PATH.exists():
        with open(GENRE_FRONTIER_PATH) as f:
            return json.load(f)
    return {"error": "genre_frontier.json not found — run genre frontier builder first"}


def build_output_variance():
    """v5.5 출력 분산 정보"""
    return {
        "v5_0": {
            "stability": "high",
            "description": "같은 프롬프트 → 유사 결과 (구조/악기 고정, 멜로디만 변화)"
        },
        "v5_5": {
            "stability": "lower",
            "description": "편차 증가, 특히 vocal grain / arrangement detail / drum pattern 변동",
            "high_variance_slots": [
                "vocal_character",
                "arrangement_detail",
                "drum_pattern",
                "harmonic_color"
            ],
            "low_variance_slots": [
                "genre",
                "bpm",
                "key",
                "main_instrument",
                "overall_mood"
            ]
        },
        "implication": "v5.5에서는 핵심 요소를 Top-Anchor로 고정하고, 변동 허용 요소는 하위 배치",
        "validated": False,
        "pending_test": "S018 동일 SP 2회 생성 비교 (추후)"
    }


def build_studio_stem_map():
    """Suno Studio 12트랙 스템 ↔ corpus 악기 매핑"""
    return {
        "vocals": {
            "stem_name": "vocals",
            "corpus_entities": ["vocals", "male vocals", "female vocals", "backing vocals", "choir"],
            "notes": "메인+백킹 합쳐서 1트랙"
        },
        "drums": {
            "stem_name": "drums",
            "corpus_entities": ["drums", "kick drum", "snare drum", "hi-hat", "drum kit", "drum machine"],
            "notes": "킥/스네어/하이햇 통합"
        },
        "bass": {
            "stem_name": "bass",
            "corpus_entities": ["electric bass", "bass guitar", "upright bass", "808 bass", "sub-bass", "synth bass"],
            "notes": "신디/일렉/어쿠스틱 베이스 통합"
        },
        "electric_guitar": {
            "stem_name": "electric_guitar",
            "corpus_entities": ["electric guitar", "distorted guitar", "overdriven guitar", "clean electric guitar"],
            "notes": "일렉기타 전체"
        },
        "acoustic_guitar": {
            "stem_name": "acoustic_guitar",
            "corpus_entities": ["acoustic guitar", "fingerpicked guitar", "nylon string guitar", "classical guitar"],
            "notes": "어쿠스틱/클래식 기타"
        },
        "synth": {
            "stem_name": "synth",
            "corpus_entities": ["synthesizer", "synth pad", "analog synth", "synth lead", "arpeggiator"],
            "notes": "리드/패드/아르페지오 통합"
        },
        "pad": {
            "stem_name": "pad",
            "corpus_entities": ["pad", "ambient pad", "warm pad", "atmospheric pad", "string pad"],
            "notes": "지속형 배경 사운드"
        },
        "strings": {
            "stem_name": "strings",
            "corpus_entities": ["strings", "violin", "cello", "viola", "string ensemble", "orchestral strings"],
            "notes": "현악기 전체"
        },
        "brass": {
            "stem_name": "brass",
            "corpus_entities": ["brass", "trumpet", "saxophone", "horn", "trombone", "french horn"],
            "notes": "관악기 + 색소폰 포함"
        },
        "keys_piano": {
            "stem_name": "keys_piano",
            "corpus_entities": ["piano", "Rhodes", "organ", "keyboard", "electric piano", "Wurlitzer"],
            "notes": "건반류 전체"
        },
        "percussion": {
            "stem_name": "percussion",
            "corpus_entities": ["percussion", "shaker", "tambourine", "congas", "bongos", "cowbell", "clap"],
            "notes": "드럼킷 외 타악기"
        },
        "effects_ambience": {
            "stem_name": "effects_ambience",
            "corpus_entities": ["ambient", "field recording", "noise", "sfx", "vinyl crackle", "tape hiss"],
            "notes": "환경음/이펙트/노이즈"
        }
    }


# ============================================================
# v2.0 Dead Budget 발견 (그대로 유지)
# ============================================================

def build_dead_budget_findings():
    return {
        "test_date": "2026-04-24",
        "tracks_tested": 10,
        "three_layer_vocabulary": {
            "layer_1_native": "Suno가 자발적으로 사용하는 어휘 (corpus에서 발견됨)",
            "layer_2_passive": "Suno가 입력받으면 이해하지만 자기 말로 번역하여 출력",
            "layer_3_dead_zone": "Suno가 완전히 무시하는 어휘 (입력해도 반응 없음)"
        },
        "new_genres_discovered": [
            {"genre": "Cinematic orchestral folk", "trigger": "Classical orchestral sonata form"},
            {"genre": "Classical crossover and operatic pop", "trigger": "Bel canto + Italian lyrics"},
            {"genre": "Chamber pop and baroque pop", "trigger": "chamber music + extended techniques"},
            {"genre": "Symphonic power metal", "trigger": "Operatic soprano coloratura"},
            {"genre": "Classical orchestral waltz", "trigger": "Romantic orchestral rit/fermata/sfz"},
            {"genre": "Baroque chamber music", "trigger": "Fugue/counterpoint"},
            {"genre": "Orchestral film score", "trigger": "Motivic development"}
        ],
        "genre_classification_bias": {
            "korean_lyrics": "한국어 가사 → K-Pop 자동 분류",
            "operatic_soprano": "오페라 소프라노 기교 → Power Metal 분류",
            "string_quartet": "현악 4중주 → Folk-Pop 분류",
            "romantic_piano": "로맨틱 피아노 독주 → Folk-Pop 전환"
        },
        "paren_directive_effective": True,
        "copyright_filter": {
            "trigger": "가사/타이틀에 지역명 → copyrighted material 차단",
            "workaround": "가사/타이틀에서 지역명 제거 (SP에는 유지 가능)"
        }
    }


# ============================================================
# 메인 빌드
# ============================================================

def build(allow_regress: bool = False):
    # 하드 가드 — 보류(LEO 결정) 상태에서 실수 실행 차단. 상단 WARNING 참조.
    # 재실행 시 hand-curated v3.1(rag/suno_dictionary_v3.json)을 v3.0으로 REGRESS.
    if not allow_regress:
        raise RuntimeError(
            "build_dictionary_v3.build() is RETIRED (BORYU/보류 — LEO decision). "
            "Running it OVERWRITES hand-curated v3.1 with v3.0 (REGRESS). "
            "Dictionary updates must go through incremental curated merge instead. "
            "If you truly intend to regress, call build(allow_regress=True) "
            "or run with --force-regress. See the WARNING block at the top of this file."
        )

    if not DB_PATH.exists():
        print(f"❌ DB not found: {DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    with open(V32_PATH) as f:
        v32 = json.load(f)
    with open(V32_EXP_PATH) as f:
        v32_exp = json.load(f)

    print("📦 Building corpus stats...")
    corpus = build_corpus_stats(cur)

    print("🎸 Building instrument phrases...")
    instrument_phrases = build_instrument_phrases(cur)

    print("🥁 Building drum vocab...")
    drum_vocab = build_drum_vocab(cur)

    print("🎼 Building technique patterns...")
    technique_patterns = build_technique_patterns(cur)

    print("🎛️ Building production vocab...")
    production_vocab = build_production_vocab(cur)

    print("🎵 Building key signatures...")
    key_signatures = build_key_signatures(cur)

    print("🎶 Building harmony vocab...")
    harmony_vocab = build_harmony_vocab(cur)

    print("😊 Building mood & timbre...")
    mood_emotion, timbre_texture = build_mood_and_timbre(cur)

    print("⏱️ Building tempo/rhythm...")
    tempo_rhythm = build_tempo_rhythm(cur)

    print("📐 Building dynamics/structure...")
    dynamics_structure = build_dynamics_structure(cur)

    print("🎤 Building vocal data...")
    vocal_expressions, vocal_chorus = build_vocal(cur)

    print("🗺️ Building genre vocabulary map...")
    genre_vocabulary_map = build_genre_vocabulary_map(cur)

    print("📝 Building descriptor combos...")
    descriptor_combos = build_descriptor_combos(cur)

    # --- v3.0 신규 축 ---
    print("🚫 Building negative vocab (v3.0)...")
    negative_vocab = build_negative_vocab()

    print("⚓ Building top anchor weights (v3.0)...")
    top_anchor_weights = build_top_anchor_weights()

    print("🌍 Loading genre frontier (v3.0)...")
    genre_frontier = load_genre_frontier()

    print("📊 Building output variance (v3.0)...")
    output_variance = build_output_variance()

    print("🎚️ Building studio stem map (v3.0)...")
    studio_stem_map = build_studio_stem_map()

    # --- 최종 조립 ---
    dictionary = {
        "version": "3.0",
        "created_at": str(date.today()),
        "previous_version": "2.0 (2026-04-25, 437곡/5,070단어/189장르)",
        "corpus": corpus,
        # v2.0 기존 섹션
        "instrument_phrases": instrument_phrases,
        "drum_vocab": drum_vocab,
        "technique_patterns": technique_patterns,
        "production_vocab": production_vocab,
        "key_signatures": key_signatures,
        "harmony_vocab": harmony_vocab,
        "mood_emotion": mood_emotion,
        "tempo_rhythm": tempo_rhythm,
        "dynamics_structure": dynamics_structure,
        "timbre_texture": timbre_texture,
        "vocal_expressions": vocal_expressions,
        "vocal_chorus": vocal_chorus,
        "genre_vocabulary_map": genre_vocabulary_map,
        "descriptor_combos": descriptor_combos,
        "dead_budget_findings": build_dead_budget_findings(),
        "suno_does_not_use": v32.get("suno_does_not_use", {}),
        "inferred_vocab_status": v32.get("inferred_vocab_status", {}),
        "sp_slot_vocab": v32.get("sp_slot_vocab", {}),
        # v3.0 신규 축
        "negative_vocab": negative_vocab,
        "top_anchor_weights": top_anchor_weights,
        "genre_frontier": genre_frontier,
        "output_variance": output_variance,
        "studio_stem_map": studio_stem_map,
        # 통계
        "stats": {
            "total_instrument_phrases": len(instrument_phrases),
            "total_drum_entities": len(drum_vocab),
            "total_technique_patterns": len(technique_patterns),
            "total_production_terms": len(production_vocab),
            "total_harmony_terms": len(harmony_vocab),
            "total_mood_terms": len(mood_emotion),
            "total_timbre_terms": len(timbre_texture),
            "total_vocal_expressions": len(vocal_expressions),
            "total_genres_mapped": len(genre_vocabulary_map),
            "total_descriptor_combos": len(descriptor_combos),
            "genre_frontier_count": len(genre_frontier) if isinstance(genre_frontier, dict) and "genres" in genre_frontier else 0,
            "negative_vocab_categories": len(negative_vocab) - 2,
            "studio_stem_tracks": len(studio_stem_map),
        }
    }

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Suno Dictionary v3.0 → {OUT_PATH}")
    print(f"   corpus: {corpus['tracks_count']}곡 / {corpus['unique_words']} words / {corpus['genres_count']} genres")
    print(f"   instruments: {len(instrument_phrases)} / drums: {len(drum_vocab)}")
    print(f"   techniques: {len(technique_patterns)} / production: {len(production_vocab)}")
    print(f"   genres mapped: {len(genre_vocabulary_map)}")
    print(f"   [v3.0 신규]")
    print(f"   negative_vocab: {len(negative_vocab) - 2} categories")
    print(f"   top_anchor_weights: 5 positions")
    print(f"   genre_frontier: {len(genre_frontier.get('genres', {}))} genres")
    print(f"   output_variance: v5.0 vs v5.5 비교")
    print(f"   studio_stem_map: {len(studio_stem_map)} stems")

    conn.close()


if __name__ == "__main__":
    import sys
    build(allow_regress="--force-regress" in sys.argv[1:])
