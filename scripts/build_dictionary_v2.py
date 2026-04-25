#!/usr/bin/env python3
"""
Suno Native Vocabulary Dictionary v2.0 빌더
- v1.1 (665곡/70장르) → v2.0 (437곡+stems/189장르/5,070단어)
- lexical_index.sqlite + v3.2 standard + Dead Budget 발견 통합
"""

import json
import sqlite3
import collections
from pathlib import Path
from datetime import date

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "data/reanalysis_v2/lexical_index.sqlite"
V32_PATH = BASE / "data/reanalysis_v2/suno_native_standard_v3.2.json"
V32_EXP_PATH = BASE / "data/reanalysis_v2/vocab_expansion_v3.2.json"
OUT_PATH = BASE / "rag/suno_dictionary.json"

def query_all(cur, sql):
    cur.execute(sql)
    return cur.fetchall()

def build():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    with open(V32_PATH) as f:
        v32 = json.load(f)
    with open(V32_EXP_PATH) as f:
        v32_exp = json.load(f)

    # --- 기본 통계 ---
    total_entries = query_all(cur, "SELECT COUNT(*) FROM entries")[0][0]
    unique_words = query_all(cur, "SELECT COUNT(*) FROM words")[0][0]
    total_songs = query_all(cur, "SELECT COUNT(DISTINCT song_id) FROM entries")[0][0]
    total_genres = query_all(cur, "SELECT COUNT(DISTINCT genre) FROM entries")[0][0]

    # --- instrument_phrases ---
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt, COUNT(DISTINCT genre) as gs
        FROM entries WHERE slot='instrument'
        GROUP BY entity ORDER BY cnt DESC
    """)
    instrument_phrases = {}
    for entity, cnt, gs in rows:
        patterns = query_all(cur, f"""
            SELECT pattern, COUNT(*) as pc FROM entries
            WHERE slot='instrument' AND entity=? AND pattern != ''
            GROUP BY pattern ORDER BY pc DESC LIMIT 5
        """.replace("?", f"'{entity.replace(chr(39), chr(39)*2)}'"))
        modifiers = query_all(cur, f"""
            SELECT modifiers, COUNT(*) as mc FROM entries
            WHERE slot='instrument' AND entity=? AND modifiers != '[]' AND modifiers != ''
            GROUP BY modifiers ORDER BY mc DESC LIMIT 5
        """.replace("?", f"'{entity.replace(chr(39), chr(39)*2)}'"))
        instrument_phrases[entity] = {
            "count": cnt,
            "genre_spread": gs,
            "top_patterns": [{"pattern": p, "freq": f} for p, f in patterns],
            "top_modifiers": [{"modifier": m, "freq": f} for m, f in modifiers]
        }

    # --- technique_patterns ---
    rows = query_all(cur, """
        SELECT pattern, COUNT(*) as cnt FROM entries
        WHERE pattern != '' AND pattern IS NOT NULL AND slot='instrument'
        GROUP BY pattern ORDER BY cnt DESC LIMIT 100
    """)
    technique_patterns = {p: {"count": c} for p, c in rows}

    # --- production_vocab ---
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot IN ('mixing', 'effect_electronic', 'effect_sound', 'mastering')
        GROUP BY entity ORDER BY cnt DESC
    """)
    production_vocab = {e: {"count": c} for e, c in rows}

    # --- key_signatures (entity는 JSON: {"bpm":..,"key":..,"time_signature":..}) ---
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
    key_signatures = {
        "keys": {k: c for k, c in key_counts.most_common(30)},
        "bpm": {str(k): c for k, c in bpm_counts.most_common(20)},
        "time_signatures": {k: c for k, c in ts_counts.most_common(10)}
    }

    # --- harmony_vocab ---
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot='harmony'
        GROUP BY entity ORDER BY cnt DESC
    """)
    harmony_vocab = {e: {"count": c} for e, c in rows}

    # --- mood/timbre (from words table) ---
    mood_words = [
        'warm', 'gritty', 'cinematic', 'dreamy', 'mellow', 'ethereal',
        'intimate', 'melancholic', 'atmospheric', 'lush', 'dark', 'bright',
        'emotional', 'soulful', 'upbeat', 'nostalgic', 'haunting', 'moody',
        'punchy', 'aggressive', 'smooth', 'delicate', 'dramatic', 'playful',
        'somber', 'energetic', 'sultry', 'euphoric', 'brooding', 'serene'
    ]
    mood_emotion = {}
    for w in mood_words:
        row = query_all(cur, f"SELECT freq_total, freq_sp, freq_bracket FROM words WHERE word='{w}'")
        if row:
            mood_emotion[w] = {"count": row[0][0], "sp": row[0][1], "bracket": row[0][2]}

    timbre_words = [
        'distorted', 'soft', 'resonant', 'compressed', 'saturated', 'crisp',
        'muddy', 'clean', 'heavy', 'airy', 'thick', 'thin', 'fuzzy',
        'metallic', 'glassy', 'woody', 'breathy', 'nasal', 'hollow',
        'punchy', 'boomy', 'shimmering', 'lo-fi', 'hi-fi', 'analog'
    ]
    timbre_texture = {}
    for w in timbre_words:
        row = query_all(cur, f"SELECT freq_total, freq_sp, freq_bracket FROM words WHERE word='{w}'")
        if row:
            timbre_texture[w] = {"count": row[0][0], "sp": row[0][1], "bracket": row[0][2]}

    # --- tempo_rhythm ---
    tempo_words = [
        'syncopated', 'steady', 'driving', 'swung', 'shuffle', 'rubato',
        'staccato', 'legato', 'arpeggiated', 'fingerpicked', 'strummed',
        'palm-muted', 'spiccato', 'pizzicato', 'tremolo', 'trill'
    ]
    tempo_rhythm = {}
    for w in tempo_words:
        row = query_all(cur, f"SELECT freq_total, freq_sp, freq_bracket FROM words WHERE word='{w}'")
        if row:
            tempo_rhythm[w] = {"count": row[0][0], "sp": row[0][1], "bracket": row[0][2]}
    # time signatures
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot='tempo_key_time' AND (entity LIKE '%time%' OR entity LIKE '%BPM%')
        GROUP BY entity ORDER BY cnt DESC LIMIT 20
    """)
    for e, c in rows:
        tempo_rhythm[e] = {"count": c}

    # --- dynamics_structure ---
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot='arrangement'
        GROUP BY entity ORDER BY cnt DESC LIMIT 40
    """)
    dynamics_structure = {e: {"count": c} for e, c in rows}

    # --- vocal_expressions ---
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot='vocal_main'
        GROUP BY entity ORDER BY cnt DESC LIMIT 60
    """)
    vocal_expressions = {e: {"count": c} for e, c in rows}

    # --- vocal_chorus ---
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt FROM entries
        WHERE slot='vocal_chorus'
        GROUP BY entity ORDER BY cnt DESC
    """)
    vocal_chorus = {e: {"count": c} for e, c in rows}

    # --- drums ---
    rows = query_all(cur, """
        SELECT entity, COUNT(*) as cnt, COUNT(DISTINCT genre) as gs FROM entries
        WHERE slot='drums'
        GROUP BY entity ORDER BY cnt DESC
    """)
    drum_vocab = {}
    for entity, cnt, gs in rows:
        drum_vocab[entity] = {"count": cnt, "genre_spread": gs}

    # --- genre_vocabulary_map (189 genres) ---
    genre_vocabulary_map = {}
    rows = query_all(cur, """
        SELECT genre, COUNT(*) as cnt, COUNT(DISTINCT entity) as unique_entities
        FROM entries GROUP BY genre ORDER BY cnt DESC
    """)
    for genre, cnt, ue in rows:
        if genre is None:
            genre = "(none)"
        top_instruments = query_all(cur, f"""
            SELECT entity, COUNT(*) as ic FROM entries
            WHERE genre=? AND slot='instrument'
            GROUP BY entity ORDER BY ic DESC LIMIT 5
        """.replace("?", f"'{genre.replace(chr(39), chr(39)*2)}'"))
        genre_vocabulary_map[genre] = {
            "total_entries": cnt,
            "unique_entities": ue,
            "top_instruments": [{"entity": e, "freq": f} for e, f in top_instruments]
        }

    # --- descriptor_combos (2-word phrases) ---
    rows = query_all(cur, """
        SELECT word, freq_total FROM words
        WHERE freq_total >= 10
        ORDER BY freq_total DESC LIMIT 300
    """)
    descriptor_combos = {w: c for w, c in rows}

    # --- Dead Budget 발견사항 ---
    dead_budget_findings = {
        "test_date": "2026-04-24",
        "tracks_tested": 10,
        "three_layer_vocabulary": {
            "layer_1_native": "Suno가 자발적으로 사용하는 어휘 (corpus에서 발견됨)",
            "layer_2_passive": "Suno가 입력받으면 이해하지만 자기 말로 번역하여 출력 (전공용어 → 네이티브 표현)",
            "layer_3_dead_zone": "Suno가 완전히 무시하는 어휘 (입력해도 반응 없음)"
        },
        "new_genres_discovered": [
            {"genre": "Cinematic orchestral folk", "trigger": "Classical orchestral sonata form → Suno 재분류"},
            {"genre": "Classical crossover and operatic pop", "trigger": "Bel canto + Italian lyrics"},
            {"genre": "Chamber pop and baroque pop", "trigger": "Contemporary chamber music + string extended techniques"},
            {"genre": "Symphonic power metal", "trigger": "Operatic soprano coloratura → Power metal로 분류"},
            {"genre": "Classical orchestral waltz", "trigger": "Romantic orchestral rit/fermata/sfz"},
            {"genre": "Baroque chamber music", "trigger": "Fugue/counterpoint → 정상 분류"},
            {"genre": "Orchestral film score", "trigger": "Motivic development → 정상 분류"}
        ],
        "genre_classification_bias": {
            "korean_lyrics": "한국어 가사 → K-Pop 자동 분류 (DB10: Sprechgesang art song → K-Pop Ballad)",
            "operatic_soprano": "오페라 소프라노 기교 → Power Metal 분류 (DB08: Coloratura → Symphonic power metal)",
            "string_quartet": "현악 4중주 → Folk-Pop 분류 (DB05: Contrary motion → Folk-pop instrumental)",
            "romantic_piano": "로맨틱 피아노 독주 → Folk-Pop 전환 (DB04: bII6 → Classical piano → contemporary folk-pop)"
        },
        "paren_directive_effective": {
            "description": "() 괄호 안 보컬 디렉션이 Suno에서 유효함 — Leo 실청취 4/4 확인",
            "confirmed": [
                {"input": "(hums softly)", "output": "허밍 아아~~아아~ 실현", "track": "DB03"},
                {"input": "(melismatic runs, two octaves)", "output": "Ah-ah-ah 멜리스마 실현", "track": "DB08"},
                {"input": "(trills, turns, ascending scales)", "output": "트릴, 어센딩 스케일 실현", "track": "DB08"},
                {"input": "(spoken)", "output": "스포큰 워드 실현", "track": "DB10"}
            ]
        },
        "copyright_filter": {
            "trigger": "가사/타이틀에 지역명(Italian, Neapolitan, French) → copyrighted material 차단",
            "workaround": "가사/타이틀에서 지역명 제거 (SP에는 유지 가능)",
            "scope": "가사+타이틀에만 적용, SP(tags)에는 미적용"
        }
    }

    # --- suno_does_not_use ---
    suno_does_not_use = v32.get("suno_does_not_use", {})

    # --- inferred_vocab_status ---
    inferred_vocab_status = v32.get("inferred_vocab_status", {})

    # --- 최종 조립 ---
    dictionary = {
        "version": "2.0",
        "created_at": str(date.today()),
        "previous_version": "1.1 (2026-04-12, 665곡/70장르)",
        "corpus": {
            "tracks_count": total_songs,
            "unique_words": unique_words,
            "total_entries": total_entries,
            "genres_count": total_genres,
            "sources": [
                "leomusic 생성곡 318곡",
                "Wave 1 외부곡 60곡 (19개 장르: TROT/Bossa Nova/K-POP 등)",
                "stems 분리 분석 95곡",
                "Dead Budget 라운드트립 10곡"
            ]
        },
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
        "dead_budget_findings": dead_budget_findings,
        "suno_does_not_use": suno_does_not_use,
        "inferred_vocab_status": inferred_vocab_status,
        "sp_slot_vocab": v32.get("sp_slot_vocab", {}),
        "stats": {
            "total_instrument_phrases": len(instrument_phrases),
            "total_drum_entities": len(drum_vocab),
            "total_technique_patterns": len(technique_patterns),
            "total_production_terms": len(production_vocab),
            "total_key_signatures": len(key_signatures),
            "total_harmony_terms": len(harmony_vocab),
            "total_mood_terms": len(mood_emotion),
            "total_timbre_terms": len(timbre_texture),
            "total_vocal_expressions": len(vocal_expressions),
            "total_genres_mapped": len(genre_vocabulary_map),
            "total_descriptor_combos": len(descriptor_combos)
        }
    }

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)

    print(f"✅ Suno Dictionary v2.0 → {OUT_PATH}")
    print(f"   corpus: {total_songs}곡 / {unique_words} words / {total_genres} genres")
    print(f"   instruments: {len(instrument_phrases)} / drums: {len(drum_vocab)}")
    print(f"   techniques: {len(technique_patterns)} / production: {len(production_vocab)}")
    print(f"   genres mapped: {len(genre_vocabulary_map)}")
    print(f"   Dead Budget 신규 장르: {len(dead_budget_findings['new_genres_discovered'])}")

    conn.close()

if __name__ == "__main__":
    build()
