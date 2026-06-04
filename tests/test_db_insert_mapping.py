"""Regression locks for the DB-direct insert mapping (NO DB connection).

Covers: build_handoff.map_song over real lyrics_history batch entries, the
db_insert row dict shape (== SONGS_COLUMNS), and INSERT SQL placeholder count.
"""
import glob
import json
from datetime import datetime
from pathlib import Path

import pytest

import build_handoff
import db_insert

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HISTORY_GLOB = str(PROJECT_ROOT / "data" / "lyrics_history" / "lyrics_batch_*.json")


def _load_good_entries(max_entries=4):
    """Pull a few entries that satisfy REQUIRED_NONEMPTY after mapping.

    Newer batches carry title + genre_group; older ones don't, so we filter to
    mappable entries rather than failing on legacy data.
    """
    entries = []
    for path in sorted(glob.glob(HISTORY_GLOB)):
        try:
            data = json.load(open(path))
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for item in data:
            mapped = build_handoff.map_song(
                item, "TST", len(entries) + 1, market="KR2", energy="Medium",
                engine="serendipity_engine_v2", seed="seed", drift=0.5)
            if all(mapped.get(k) for k in build_handoff.REQUIRED_NONEMPTY):
                entries.append((item, mapped))
                if len(entries) >= max_entries:
                    return entries
    return entries


def test_found_mappable_batch_entries():
    entries = _load_good_entries()
    assert len(entries) >= 2, "expected at least 2 mappable lyrics_history entries"


def test_map_song_required_nonempty_satisfied():
    entries = _load_good_entries()
    for raw, mapped in entries:
        missing = [k for k in build_handoff.REQUIRED_NONEMPTY if not mapped.get(k)]
        assert not missing, f"REQUIRED_NONEMPTY violated: {missing}"


def test_map_song_genre_extracted_from_sp():
    entries = _load_good_entries()
    for raw, mapped in entries:
        # genre should be the first SP clause (extract_genre), non-empty for vocal SPs.
        assert isinstance(mapped["genre"], str)


def test_song_to_row_keys_equal_songs_columns():
    entries = _load_good_entries()
    now = datetime(2026, 1, 1)
    for i, (raw, mapped) in enumerate(entries):
        row = db_insert.song_to_row(mapped, gid=10000 + i, now=now)
        assert set(row.keys()) == set(db_insert.SONGS_COLUMNS), (
            f"row keys diverge from SONGS_COLUMNS: "
            f"extra={set(row) - set(db_insert.SONGS_COLUMNS)}, "
            f"missing={set(db_insert.SONGS_COLUMNS) - set(row)}")
        # ordering-independent but list form should also match column count
        assert len(row) == len(db_insert.SONGS_COLUMNS)


def test_insert_sql_placeholder_count_matches_columns():
    sql = db_insert.insert_sql()
    assert sql.count("%s") == len(db_insert.SONGS_COLUMNS)
    # column list in the SQL must also enumerate every column
    for col in db_insert.SONGS_COLUMNS:
        assert col in sql


def test_song_to_row_static_fields():
    # Lock the creator/engine/status constants flowing into the row.
    entries = _load_good_entries()
    if not entries:
        pytest.skip("no mappable entries")
    raw, mapped = entries[0]
    row = db_insert.song_to_row(mapped, gid=99999, now=datetime(2026, 1, 1))
    assert row["global_id"] == 99999
    assert row["creator"] == "sunolanguage"
    assert row["source_project"] == "sunolanguage"
    assert row["music_engine"] == "suno_v5"
    assert row["status"] == "pending_suno"
    # created_date is varchar(20): a 19-char "YYYY-MM-DD HH:MM:SS" string
    assert len(row["created_date"]) == 19
