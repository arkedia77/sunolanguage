# DB Mirror Gap — `songs` schema vs `db_insert.SONGS_COLUMNS`

Generated: 2026-06-05 (reinforce phase, read-only SELECT)
DB: leofamily_music @ leo-legion-y540-15irh:5432, role_sunolanguage (SELECT only)

## Headline

- Live `songs` table: **74 columns** (`information_schema.columns`).
- `scripts/db_insert.py` `SONGS_COLUMNS`: **40 columns** (the sunolang mirror writes a 40-col subset).
- `sub_theme` and `coherence` **both EXIST live** → the "pending ALTER" note is **stale**.
- `build_handoff.map_song` already computes both, but `db_insert.song_to_row` drops them.
- Among sunolang rows: **coherence populated on 10/130**, **sub_theme populated on 0/130** → backfill needed.

## Schema confirmation

`information_schema.columns` for table `songs` returns 74 columns. Direct existence check:

- `sub_theme` exists: **True**
- `coherence` exists: **True**

There is therefore no schema migration ("pending ALTER") blocking the mirror.
The DDL is already in place; only the insert path lags.

## Producer/consumer mismatch

`scripts/build_handoff.py` (`map_song`, lines ~95–128) already emits both fields:

- `map_song` sets `"sub_theme": item.get("sub_theme")` (line ~123)
- `map_song` sets `"coherence": coherence_of(item)` (line ~128), where `coherence_of`
  (lines ~85–91) pulls `lyrics_validation.coherence_score` (rounded to 4 dp).
- `build_handoff.SONGS_COLUMNS` (lines ~43–44) lists `theme, sub_theme, … coherence`.

But `scripts/db_insert.py`:
- `SONGS_COLUMNS` (lines 40–51, 40 entries) contains **neither** `sub_theme` **nor** `coherence`.
- `song_to_row` (lines 54–96) never populates them.

So the Option-A handoff dict carries `sub_theme`/`coherence` all the way to `db_insert`,
which then silently drops them on INSERT.

## Live population state (source_project = 'sunolanguage')

Note: the live label is **`sunolanguage`** (130 rows), not `sunolang`.
`source_project` distribution: leomusic 2244, leomusic2 771, **sunolanguage 130**, yoonnest 40.

| Field | Populated sunolanguage rows | of total |
|---|---|---|
| coherence (NOT NULL) | **10** | 130 |
| sub_theme (NOT NULL & non-empty) | **0** | 130 |

Existing coherence values: min 0.4616, max 0.7276, avg 0.5404 (the 10 populated rows
were written by `build_handoff`/`json_to_db`, not by `db_insert`).

## Exact fix to extend the mirror (2-line addition)

In `scripts/db_insert.py`:

1. Add the two columns to `SONGS_COLUMNS` (line ~43, alongside `theme`):
   ```python
   "theme", "sub_theme", "episode", "category", ...   # add "sub_theme"
   ```
   and append `"coherence"` to the list.

2. In `song_to_row` (after the `"theme": ...` entry, ~line 67), add:
   ```python
   "sub_theme": opt_a.get("sub_theme") or "",
   "coherence": opt_a.get("coherence"),
   ```

`opt_a` already carries both keys from `build_handoff.map_song`, so no upstream change
is needed; the INSERT placeholder count derives from `len(SONGS_COLUMNS)` automatically.

## Backfill unblock

The DDL is present and the values are computable from existing handoff JSON, so the
backfill task (populate `coherence` on the remaining 120 rows, `sub_theme` on all 130)
is unblocked from a schema standpoint. It only requires (a) the 2-line db_insert
extension above and/or (b) an authorized UPDATE pass from the handoff files —
neither performed here (read-only workstream).
