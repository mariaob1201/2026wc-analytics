# Data Pipeline — collection → players → features → per group

How raw public data becomes the two tabular datasets and the model's prior. The
whole chain is keyless and reproducible; the daily GitHub Action re-runs it end
to end (see [LIVE_PIPELINE.md](LIVE_PIPELINE.md)).

```
PUBLIC SOURCES                 EXTRACTION                 FEATURES                  STRUCTURE
─────────────                  ──────────                 ────────                  ─────────
martj42 results feed ─┐        wc2026_matches()           per-player:               48 teams,
FIFA attributes  ─────┼──►     build_real_matches()   ─►  longevity, skill_index,   12 groups
Wikipedia squads ─────┤        fetch_squads()             social_score, age-role    (teams.py)
worldcup2026 repo ────┘        + FIFA join (surname)      per-team: prior_strength      │
                                     │                          │                       ▼
                                     ▼                          ▼                  by_group() drives
                               wc2026_players.csv        team_features_*.csv       group → knockout
                                                          → model prior             simulation
```

## 1. Data collection — `data/sources.py`

Four keyless public sources, each cached under `data/raw/`:

| Source | Function | Provides |
|---|---|---|
| martj42/international-results | `download_intl_results()` | every international match + score (training data) |
| FIFA player attributes (sofifa dump) | `download_fifa()` | pace / shooting / passing / dribbling / defending / physical |
| Wikipedia 2026 squads | `fetch_squads()` | the real called-up players (name, age, caps, position) |
| rezarahiminia/worldcup2026 | `fetch_team_metadata()` | official FIFA codes, flags, group letters |

- **Freshness:** the results feed re-downloads when the cache is older than
  `max_age_hours` (default 6h), with a graceful fallback to the cache if the
  network is down — so live forecasts don't lag reality.
- **Windowing / naming:** `build_real_matches(start, end)` filters to a recent
  window and maps name aliases to our canonical 48 teams; `wc2026_matches()`
  returns just the 2026 fixtures (scored rows + not-yet-played rows).

## 2. Individual player extraction — `scripts/27_build_player_dataset.py`

Builds the **player table** `data/processed/wc2026_players.csv` in three moves:

1. **Real roster** — `fetch_squads()` parses each nation's Wikipedia squad
   wikitext (`live_squads.parse_squads`) into rows of *name, position, age,
   caps*. Using the live squad is what keeps retired players out of the tables.
2. **Attribute join** — each real player is matched to the FIFA dataset **by
   surname**, taking the highest-rated namesake. Matched rows are tagged
   `rating_source = "fifa-match"`; unmatched players are back-filled with their
   team's median (`rating_source = "team-median"`) so no row is empty.
3. **Schema:** `team, fifa_code, group, name, position, age, caps, overall,
   pace, shooting, passing, dribbling, defending, physical, rating_source`.

**Honest limits** (encoded in `rating_source`): the surname join covers ~70% of
players, and the FIFA dump is 2022-vintage. An exact per-player feed
(api-football) would replace both — plug it in behind the same schema.

## 3. Feature engineering — `features/player_features.py` + `data/live_squads.py`

**Per player** (`add_player_features`):

| Feature | Meaning |
|---|---|
| `longevity` | z(career years) + z(caps) — experience |
| `skill_index` | weighted blend of the six skill ratings |
| `social_score` | log(followers) × engagement — a reach proxy |

**Age × role weighting** (`live_team_features`): youth is weighted for *pace in
attack* (`_youth_pace_weight`), seniority for *ball-retention / solidity in
defence* (`_experience_weight`), yielding `young_pace`, `senior_solidity`, and a
combined `age_role`.

**Per team → the prior** (`build_team_features` / `live_team_features`):
aggregate to one row per team and collapse into a single standardized
`prior_strength`:

```
prior_strength ∝ 0.80·z(squad_overall) + 0.06·z(log caps)
               + 0.04·z(avg_age)       + 0.10·z(age_role)
```

This number is the Bayesian model's prior mean for each team, so squad quality
shapes the goal forecasts before any 2026 result is observed.

## 4. Per-group organization — `data/teams.py`

The 48 teams are declared with their real 2026 draw. `by_group()` returns
`{group_letter: [4 teams]}` and assertions enforce **12 groups × 4 teams**. The
`group` column rides through both output tables, and `by_group()` is what the
tournament simulators iterate to run the group stage (top-2 of each group + the
8 best third-placed teams → knockout) in both the Bayesian
`models/simulate.py` and the Elo `models/elo_sim.py`.

## The two outputs

| File | Grain | Key columns |
|---|---|---|
| `data/processed/wc2026_players.csv` | one row per player | identity + position/age/caps + 6 FIFA attributes + `rating_source` |
| `data/processed/wc2026_team_assessment.csv` | one row per team | 2026 results, model + Elo ratings, aggregated squad strength, `young_pace` / `senior_solidity`, tier / style / talisman |

## How the daily job chains it

`make daily` runs the stages in dependency order:

```
real-players → live-squads → live-features → real-fit → elo
  → dataset(27) → winners(28) → track/champion → timeline → prediction-log
```

Each day: fresh squads + results → recompute features / prior → refit the model
→ rebuild the player & team tables → regenerate every forecast.
