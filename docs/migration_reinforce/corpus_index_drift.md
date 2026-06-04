# Corpus Index Drift — Local Chunks vs Deployed Qdrant

Generated: 2026-06-05 (reinforce phase, read-only)
Qdrant: http://100.90.35.121:6333 (count/scroll only, no writes)

## Headline

| Collection | Local chunk file | Live Qdrant | Gap (local − live) |
|---|---|---|---|
| presets (`sunolang_presets`) | **10,646** (`data/chunks.json`) | **3,707** | **6,939 missing live** |
| lyrics (`sunolang_lyrics`) | **5,858** (`data/lyrics_chunks.json`) | **4,620** | **1,238 missing live** |

The deployed indexes are stale: the live presets index holds only ~35% of the
locally-built chunks, and live lyrics holds ~79%.

## Presets — per-slot drift

Local `data/chunks.json` carries two sources (`sp_*` = 5,690 chunks, `bracket_*` = 4,956 chunks).
Live `sunolang_presets` has NO bracket-derived chunks and is missing the entire `section` slot.

| Slot | Local (chunks.json) | Live Qdrant | Gap |
|---|---|---|---|
| instrument | 4,592 | 2,096 | 2,496 |
| section | 1,367 | **0** | 1,367 |
| vocal_main | 1,202 | 562 | 640 |
| drums | 1,017 | 481 | 536 |
| tempo_key_time | 599 | 270 | 329 |
| arrangement | 594 | 42 | 552 |
| effect_electronic | 495 | 19 | 476 |
| genre | 402 | 196 | 206 |
| vocal_chorus | 156 | 8 | 148 |
| mixing | 131 | 6 | 125 |
| effect_sound | 53 | 23 | 30 |
| harmony | 38 | 4 | 34 |
| **TOTAL** | **10,646** | **3,707** | **6,939** |

Key structural facts:
- The `section` slot (1,367 local chunks, all from `bracket_section_*`) is **entirely absent** live.
- Every slot is under-represented live; the live snapshot predates the current local build.

## Lyrics — per-granularity drift

| Granularity | Local (lyrics_chunks.json) | Live Qdrant | Gap |
|---|---|---|---|
| section | 2,452 | 2,451 | 1 |
| couplet | 3,406 | 2,169 | 1,237 |
| **TOTAL** | **5,858** | **4,620** | **1,238** |

The drift is almost entirely in the `couplet` granularity (section granularity is essentially in sync, −1).

Per section_tag (local → live), the deficit is spread across tags, e.g.:
verse 2,265→2,067, chorus 1,690→1,354, bridge 656→426, outro 400→263, pre_chorus 289→151.

## Positional-ID orphan risk — MUST use `rebuild`, not `build`

Both live collections use **integer positional point IDs** (sampled ids `0,1,2,3,4,…`),
NOT the stable string `chunk_id` (e.g. `sp_genre_1_000`, `lyrics_verse_1_000`).

Implication: point id = insertion ordinal. If a future authorized run does an
incremental `build` (append) rather than a full `rebuild`:
- New chunks would receive ids continuing from the live max, but the local build
  re-numbers from 0, so **the same ordinal id would map to a different chunk_id**
  between local and live → silent overwrite / orphaned vectors whose payload no
  longer matches their position.
- Because the local file already grew by +6,939 (presets) and +1,238 (lyrics)
  with re-ordered slots, an append cannot reconcile positions.

Therefore a future authorized sync **must drop-and-rebuild** both collections from
the current `data/chunks.json` / `data/lyrics_chunks.json` so that positional ids
are re-assigned consistently against the full local set.

## What an authorized rebuild would change

- `sunolang_presets`: 3,707 → **10,646** (+6,939), adding the missing `section`
  slot (1,367) and the full bracket-derived corpus, and topping up every existing slot.
- `sunolang_lyrics`: 4,620 → **5,858** (+1,238), almost all in `couplet` granularity.
- Re-assigns all positional ids → eliminates the orphan risk.

No writes were performed by this report.
