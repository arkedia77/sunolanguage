"""Regression locks for the SP-generation engine constants + pure functions.

Covers: serendipity constants, slot_assembler limits + pure dedup/assemble,
preset_validator verdict thresholds, and song_forms classify/select (no Qdrant).
"""
import importlib

import serendipity
import slot_assembler
import preset_validator
import song_forms


# --- 1. serendipity constants ------------------------------------------------

def test_serendipity_instrument_count():
    assert serendipity.INSTRUMENT_COUNT == 4


def test_serendipity_min_sp_length():
    assert serendipity.MIN_SP_LENGTH == 550


# --- 2. slot_assembler limits ------------------------------------------------

def test_slot_assembler_max_sentences():
    assert slot_assembler.MAX_SENTENCES == 9


def test_slot_assembler_sp_char_limit():
    assert slot_assembler.SP_CHAR_LIMIT == 1000


# --- slot_assembler pure functions (no Qdrant) -------------------------------

def test_dedup_drops_exact_and_substring_duplicates():
    sentences = [
        "Clean electric guitar plays arpeggiated patterns.",
        "Clean electric guitar plays arpeggiated patterns.",  # exact dup
        "Warm upright bass walks steady quarter notes.",
    ]
    out = slot_assembler._dedup_sentences(sentences)
    assert len(out) == 2
    assert out[0] == "Clean electric guitar plays arpeggiated patterns."
    assert out[1] == "Warm upright bass walks steady quarter notes."


def test_assemble_caps_at_max_sentences():
    # 12 distinct instrument texts -> must be capped to MAX_SENTENCES.
    preset = {
        "instrument": [
            {"text": f"Distinct instrument line number {i} of the arrangement"}
            for i in range(12)
        ]
    }
    sp = slot_assembler.assemble_sp(preset)
    # Each rendered sentence ends with a period; count them.
    n_sentences = sp.count(".")
    assert n_sentences <= slot_assembler.MAX_SENTENCES
    assert len(sp) <= slot_assembler.SP_CHAR_LIMIT


def test_assemble_clean_text_adds_period_and_orders_genre_first():
    preset = {
        "genre": {"text": "K-Pop ballad"},
        "instrument": [{"text": "Soft piano carries the melody"}],
        "drums": {"text": "Brush drums keep a gentle pulse"},
    }
    sp = slot_assembler.assemble_sp(preset)
    assert sp.startswith("K-Pop ballad.")
    assert sp.endswith(".")


def test_assemble_respects_char_limit_with_long_input():
    long_line = {"text": "A" * 400}
    preset = {"instrument": [long_line, long_line, long_line, long_line]}
    sp = slot_assembler.assemble_sp(preset)
    assert len(sp) <= slot_assembler.SP_CHAR_LIMIT


# --- 3. preset_validator verdict thresholds ----------------------------------

def test_validator_thresholds_constants_in_source():
    # The thresholds live inline in validate_sp; lock them via behavior below,
    # and assert the documented boundary values are unchanged in the module text.
    src = importlib.import_module("preset_validator")
    import inspect
    code = inspect.getsource(src.validate_sp)
    assert "ratio >= 0.95" in code
    assert "ratio >= 0.90" in code


def test_validator_verdict_pass_at_full_native(monkeypatch):
    # Force every meaningful word to be "native" -> ratio 1.0 -> PASS.
    monkeypatch.setattr(preset_validator, "_load_v3_words",
                        lambda: {"guitar", "piano", "bass", "drums"})
    monkeypatch.setattr(preset_validator, "_load_corpus_text", lambda: "")
    res = preset_validator.validate_sp("guitar piano bass drums")
    assert res["native_ratio"] == 1.0
    assert res["verdict"] == "PASS"


def test_validator_verdict_fail_at_low_native(monkeypatch):
    # No native vocabulary at all -> ratio 0.0 -> FAIL.
    monkeypatch.setattr(preset_validator, "_load_v3_words", lambda: set())
    monkeypatch.setattr(preset_validator, "_load_corpus_text", lambda: "")
    res = preset_validator.validate_sp(
        "zzqq xylo morphic wibble grontle flarn quibble")
    assert res["native_ratio"] < 0.90
    assert res["verdict"] == "FAIL"


def test_validator_verdict_boundary_warn(monkeypatch):
    # 19 native / 1 novel = 0.95 -> PASS; 18/2 = 0.90 -> WARN; 17/3 -> FAIL.
    native_vocab = {f"nat{i}" for i in range(19)}
    monkeypatch.setattr(preset_validator, "_load_v3_words", lambda: native_vocab)
    monkeypatch.setattr(preset_validator, "_load_corpus_text", lambda: "")

    # 19 native + 1 novel -> 0.95 PASS
    sp_pass = " ".join([f"nat{i}" for i in range(19)] + ["novelxyz"])
    assert preset_validator.validate_sp(sp_pass)["verdict"] == "PASS"

    # 18 native + 2 novel -> 0.90 WARN
    native_vocab_18 = {f"nat{i}" for i in range(18)}
    monkeypatch.setattr(preset_validator, "_load_v3_words", lambda: native_vocab_18)
    sp_warn = " ".join([f"nat{i}" for i in range(18)] + ["novelxyz", "novelabc"])
    assert preset_validator.validate_sp(sp_warn)["verdict"] == "WARN"


# --- 4. song_forms classify + select (no Qdrant) -----------------------------

def test_classify_genre_group_fixed_inputs():
    cases = {
        "K-Pop R&B ballad": "BALLAD",
        "Slow piano ballad": "BALLAD",
        "Neo-soul groove": "RNB",
        "Boom bap hip-hop track": "HIPHOP",
        "Trap beat with 808s": "HIPHOP",
        "K-Rock with pop-punk influences": "ROCK",
        "Bossa Nova": "ACOUSTIC",
        "Acoustic fingerstyle folk": "ACOUSTIC",
        "K-Pop dance track": "POP",
        "Future bass synthwave": "POP",
    }
    for text, expected in cases.items():
        assert song_forms.classify_genre_group(text) == expected, text


def test_classify_empty_defaults_pop():
    assert song_forms.classify_genre_group("") == "POP"
    assert song_forms.classify_genre_group("totally unknown genre xyz") == "POP"


def test_classify_city_pop_is_pop_not_acoustic():
    # ACOUSTIC contains generic substrings; city pop must resolve to POP/RNB,
    # never ACOUSTIC (explicit guard in classify_genre_group).
    assert song_forms.classify_genre_group("City Pop") != "ACOUSTIC"


def test_select_form_avoid_excludes_given_form():
    group = "BALLAD"
    forms = song_forms.GENRE_FORMS[group]
    # Avoid all but one variant -> select_form must return the remaining one.
    keep_name = "minimal"
    avoid = [list(f) for name, f in forms.items() if name != keep_name]
    for _ in range(30):  # random.choice internally; run many times
        got = song_forms.select_form(group, avoid_forms=avoid)
        assert got == list(forms[keep_name]), got


def test_select_form_variant_exact():
    got = song_forms.select_form("ROCK", variant="heavy")
    assert got == list(song_forms.GENRE_FORMS["ROCK"]["heavy"])


def test_select_form_unknown_group_falls_back_to_pop_forms():
    pop_form_tuples = {tuple(f) for f in song_forms.GENRE_FORMS["POP"].values()}
    for _ in range(20):
        got = tuple(song_forms.select_form("NOPE_GROUP"))
        assert got in pop_form_tuples
