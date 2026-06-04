# Song-Forms Coverage — genre-slot entities vs `classify_genre_group`

Generated: 2026-06-05 (reinforce phase, read-only scroll)
Source: live `sunolang_presets`, slot=`genre`; classifier `scripts/song_forms.py`

## Headline

- **196 distinct genre-slot entities** live (matches the expected ~196).
- Group distribution: **BALLAD 50 / POP 45 / ROCK 34 / RNB 26 / ACOUSTIC 21 / HIPHOP 20**.
- **0 entities fall through to the pure POP default.** Every entity is classified by
  either an explicit `GENRE_GROUPS` keyword or the `genre_signals` heuristic.
- **5 entities are NOT matched by any explicit keyword** — they are rescued only by
  the weaker `genre_signals` heuristic. These are the dictionary-refresh candidates.

## Classification result (n = 196 distinct entities)

| genre_group | count |
|---|---|
| BALLAD | 50 |
| POP (incl. default) | 45 |
| ROCK | 34 |
| RNB | 26 |
| ACOUSTIC | 21 |
| HIPHOP | 20 |

`classify_genre_group` returns "POP" for 45 entities, but **all 45 matched a real POP
keyword** (`pop`, `dance`, `edm`, `disco`, `funk`, `synthwave`, etc.) — none reached
the `return "POP"` default at the end of the function. True default fall-through = **0**.

## Un-keyworded entities (dictionary-refresh candidates)

5 entities match **no** entry in `GENRE_GROUPS` and are only classified via the
secondary `genre_signals` map (matched on the word "orchestral"/"score" → BALLAD):

1. `Cinematic orchestral hybrid` → BALLAD (via signal "orchestral")
2. `Cinematic orchestral score` → BALLAD (via signal "orchestral")
3. `Orchestral fanfare and march` → BALLAD (via signal "orchestral")
4. `Orchestral film score with a focus on dramatic, fast-paced …` → BALLAD (via signal)
5. `Orchestral soundtrack with a focus on woodwinds and strings` → BALLAD (via signal)

All five are **cinematic / orchestral / soundtrack** genres. The dictionary has no
keyword for this family; they only classify because "orchestral" happens to be a
BALLAD signal word. This is fragile:
- A cinematic cue with **no** "orchestral"/"piano"/"strings" token would hit the pure
  POP default and get a POP song form, which is musically wrong for a film score.

### Refresh recommendation

Add a dedicated keyword cluster to `GENRE_GROUPS` (and likely a matching `GENRE_FORMS`
group or an explicit mapping to BALLAD) for the cinematic family, e.g.:
`cinematic, soundtrack, film score, score, orchestral, fanfare, march, trailer`.
This converts the 5 signal-only matches into explicit, intentional classifications and
guards against POP-default fall-through for future cinematic genre entities.

## Method note

Scrolled all `slot=genre` points (read-only), de-duplicated on payload `entity`,
ran each through `song_forms.classify_genre_group`, then re-checked each result against
the explicit `GENRE_GROUPS` keyword set to separate keyword-matches from
signal-only / default matches. No writes performed.
