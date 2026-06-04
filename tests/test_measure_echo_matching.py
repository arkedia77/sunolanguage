"""Regression locks for measure_echo_n_series robust handoff/reanalysis matching.

Covers the hardening (2026-06-05):
  - reanalysis SP read from any of reanalysis_sp / sp / style_prompt
  - handoff index keyed by batch_line AND numeric gid/global_id/id
  - reanalysis records resolvable by batch_line OR numeric id
No DB connection, no file writes — exercises pure helpers + build_original_index.
"""
import measure_echo_n_series as m


def test_reanalysis_sp_field_fallback():
    assert m.reanalysis_sp_of({"reanalysis_sp": "A"}) == "A"
    assert m.reanalysis_sp_of({"sp": "B"}) == "B"
    assert m.reanalysis_sp_of({"style_prompt": "C"}) == "C"
    # precedence: reanalysis_sp first
    assert m.reanalysis_sp_of({"reanalysis_sp": "A", "sp": "B"}) == "A"
    assert m.reanalysis_sp_of({}) == ""


def test_reanalysis_keys_collected_as_strings():
    keys = m.reanalysis_keys_of({"batch_line": "N001_01", "gid": 20311})
    assert "N001_01" in keys
    assert "20311" in keys
    # empty/None values are not emitted as keys
    assert m.reanalysis_keys_of({"gid": None, "id": ""}) == []


def test_build_original_index_keys_by_batch_line():
    handoff = {
        "batches": {
            "N001": [
                {"batch_line": "N001_01", "style_prompt": "pop sp",
                 "genre": "pop", "title": "T1"},
            ],
            "N002": [
                {"batch_line": "N002_01", "gid": 20500, "style_prompt": "rock sp",
                 "genre": "rock", "title": "T2"},
            ],
        }
    }
    idx = m.build_original_index(handoff)
    # batch_line key resolves
    assert idx["N001_01"]["sp"] == "pop sp"
    # numeric gid key ALSO resolves to the same song (dual keying)
    assert idx["20500"]["title"] == "T2"
    assert idx["N002_01"]["title"] == "T2"


def test_real_handoff_index_nonempty():
    handoff = m_json(m.HANDOFF)
    idx = m.build_original_index(handoff)
    assert idx, "real handoff produced empty index"
    # every entry exposes the four fields downstream code relies on
    for entry in idx.values():
        assert set(entry) == {"batch_line", "sp", "genre", "title"}


def m_json(path):
    import json
    return json.loads(path.read_text())
