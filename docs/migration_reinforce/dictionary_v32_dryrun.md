# build_dictionary_v3.py — v3.2 dry-run findings

Date: 2026-06-05 (post-migration reinforce phase, purple machine)
Run: `build_dictionary_v3.build()` with `OUT_PATH` overridden to a TEMP path
(`/tmp/reinforce/suno_dictionary_v3_temp.json`). The committed
`rag/suno_dictionary_v3.json` was NOT modified.

## Inputs

- DB: `data/reanalysis_v2/lexical_index.sqlite` (committed, 15509 entries / 5496 words)
- `data/reanalysis_v2/suno_native_standard_v3.2.json` (v3.2 staged standard)
- `data/reanalysis_v2/vocab_expansion_v3.2.json` (v3.2 staged expansion)
- `rag/genre_frontier.json`

## How the script consumes the v3.2 inputs

The script reads `suno_native_standard_v3.2.json` (`V32_PATH`) and pulls exactly three
sections into the dictionary:

- `suno_does_not_use`   (5 categories)
- `inferred_vocab_status` (4 entries)
- `sp_slot_vocab`        (12 slots)

It also opens `vocab_expansion_v3.2.json` (`V32_EXP_PATH`) into a local variable
`v32_exp`, **but that variable is never referenced again** anywhere in `build()`.
So `vocab_expansion_v3.2.json` (which carries `instrument_details` x41,
`drum_details` x82, `genre_slot_matrix` x189, `slot_vocab_pool` x12) contributes
**nothing** to the output as the script stands today. Wiring it in is a code change
and is out of scope for this workstream (scripts are read-only here).

## What v3.2 would change vs the committed v3.1

Result: for the three sections the script actually wires, the v3.2 file is
**byte-identical to what is already committed in v3.1**:

| section | committed v3.1 | v3.2 file | identical? |
|---|---|---|---|
| suno_does_not_use | 5 | 5 | yes |
| inferred_vocab_status | 4 | 4 | yes |
| sp_slot_vocab | 12 | 12 | yes |

So the v3.2 standard inputs introduce **0 added / 0 changed entries** in the parts
of the dictionary the script touches — the committed v3.1 already absorbed them.
A re-run does not "advance" the dictionary to v3.2; the dry-run output is still
stamped `"version": "3.0"` by the script.

## Re-running today would REGRESS the committed v3.1 (do not overwrite)

Diffing the fresh temp build (version "3.0", created 2026-06-05) against the
committed `rag/suno_dictionary_v3.json` (version "3.1", created 2026-05-09):

Keys only in committed: `update_notes` (lost on re-run).

Section size deltas (committed -> fresh re-run):

| section | committed v3.1 | fresh re-run | delta |
|---|---|---|---|
| genre_frontier | 6 | 8 | +2 |
| harmony_vocab | 9 | 8 | -1 |
| instrument_phrases | 55 | 49 | -6 |
| mood_emotion | 33 | 30 | -3 |
| technique_patterns | 111 | 100 | -11 |
| tempo_rhythm | 20 | 16 | -4 |
| timbre_texture | 26 | 23 | -3 |
| stats | 15 | 13 | -2 |

Stats deltas:

- `stats.db_crossref_date`: `2026-05-09` -> absent
- `stats.db_rows_analyzed`: `385` -> absent
- `stats.genre_frontier_count`: `6` -> `8`
- `stats.total_technique_patterns`: `111` -> `100`

## Interpretation

The committed v3.1 is a **post-processed / hand-finished** artifact: it has the
`update_notes` key, a `"3.1"` version stamp, a `2026-05-09` `db_crossref_date`, a
`db_rows_analyzed: 385` stat, and several sections (instrument_phrases,
technique_patterns, mood/tempo/timbre, harmony) that are LARGER than what the script
regenerates from the current committed sqlite. None of those enrichments are
reproducible from `build_dictionary_v3.py` against the current DB — they were added
after the script ran (likely a DB cross-reference pass that is not part of this
script's corpus, plus manual curation).

Therefore:

1. The v3.2 staged standard file changes nothing the script wires (already in v3.1).
2. The v3.2 expansion file is dead-loaded and would need a code change to take effect.
3. Re-running the script as-is would OVERWRITE v3.1 with a smaller v3.0-stamped dict
   and drop curated content. **Do not overwrite the committed dictionary.**

Temp output deleted after measurement.
