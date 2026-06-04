# Title Strategy Distribution — production lyrics batches

Generated: 2026-06-05 (reinforce phase, read-only file analysis)
Source: 48 files `data/lyrics_history/lyrics_batch_*.json`

## Headline

- 315 total items across 48 batch files; **288 carry `title` + `title_strategy`**
  (27 early items, from `lyrics_batch_20260528_*`, predate the title feature).
- Strategy mix: **verse_noun 41.7% / chorus_phrase 40.3% / rebalanced 10.1% / short_punch 8.0%**.
- **Single-noun titles dominate: 257/288 = 89.2%** are single-token;
  only **31/288 = 10.8%** are full-line / multi-token (contain a space).

## Strategy mix (n = 288)

| title_strategy | count | share |
|---|---|---|
| verse_noun | 120 | 41.7% |
| chorus_phrase | 116 | 40.3% |
| rebalanced | 29 | 10.1% |
| short_punch | 23 | 8.0% |

Note: `title_strategy` is a flat string in the data; **`rebalanced` is itself a
strategy value**, not a separate boolean flag (no nested `rebalanced` boolean was
found on any item → "rebalanced flag present: 0"). The "rebalanced rate" is therefore
the 10.1% share above — the share of titles the rebalancer reassigned.

## Single-noun vs full-line ratio

| Title shape | count | share |
|---|---|---|
| single-token (single-noun) | 257 | 89.2% |
| multi-token (full-line, has space) | 31 | 10.8% |

This validates the **kiwipiepy noun-extraction fix**: production titles are
overwhelmingly clean single-noun Korean tokens (e.g. `마비`, `고백`, `움직임`, `전부`),
which is the intended output of the morphological-analyzer path.

## Residual noise (caveat)

A small number of titles are still SP/English fragments rather than extracted nouns,
e.g. `Full kit enters,` and `Caliente, caliente`. These appear in the multi-token
bucket and indicate the noun extractor occasionally falls back to raw line text when
no Korean noun is recoverable (typically English-genre or instrumental-direction
lines). They are the residual after the kiwipiepy fix — minority, not majority.

## Timeline (kiwipiepy fix in production)

The title feature is present from `lyrics_batch_20260529_123828` onward; all 41
title-bearing batches (2026-05-29 → 2026-06-04) show the same high single-noun rate
(typically 8–10 of 10 per batch single-token), confirming the fix is stable in
sustained production, not a one-off.
