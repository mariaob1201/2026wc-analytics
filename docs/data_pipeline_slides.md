% The 2026 World Cup Analytics Data Pipeline
% Collection, organization, and aggregation — a developer walkthrough
% github.com/mariaob1201/2026-world-cup-analytics

# Overview

## Pipeline at a glance

```
SOURCES                EXTRACTION            FEATURES            STRUCTURE
-------                ----------            --------            ---------
martj42 results  --\   wc2026_matches()      per-player:        48 teams
FIFA-22 attrs    ---+->build_real_matches()->longevity,        12 groups
Wikipedia squads --/   fetch_squads()         skill_index,      (teams.py)
worldcup2026 repo      + FIFA surname join    social, age×role       |
                            |                       |                 v
                            v                       v            by_group() ->
                   wc2026_players.csv     team_features_live.csv  group ->
                                          -> Bayesian prior       knockout sim
```

Keyless · cached to `data/raw/` · re-run daily by CI.

## Design principles

- **Keyless & public** — every source is a raw GitHub URL or public API; no credentials to reproduce.
- **Cache-first** — downloads land in `data/raw/`; the live results feed refreshes on a TTL, statics cached forever.
- **Canonicalized** — one naming convention for 48 teams; every source is aliased into it on ingest.
- **Schema-stable** — each stage emits a fixed, documented schema, so a source can be swapped without touching downstream code.
- **Reproducible** — `make daily` runs the full chain; the CI bot commits the diff.

# Collection

## Transport & formats

| Source | Transport | Format | Loader (`data/sources.py`) |
|---|---|---|---|
| martj42 results | HTTPS GET | CSV | `download_intl_results()` |
| FIFA-22 attributes | HTTPS GET | CSV | `download_fifa()` |
| Wikipedia squads | MediaWiki API | wikitext | `fetch_squads()` |
| worldcup2026 repo | HTTPS GET | JSON | `fetch_team_metadata()` |

All fetched with the standard library (`urllib.request`) — no scraping frameworks. Each loader is idempotent and offline-safe once cached.

## (1) Live match results

**Source:** `martj42/international_results` — every men's international since 1872, updated within days of each match.

- **Method:** `urllib.urlretrieve(URL, data/raw/intl_results.csv)`.
- **Freshness (TTL):** re-download when the cache mtime is older than `max_age_hours = 6` — so during the tournament the feed never lags reality by more than a few hours.
- **Resilience:** on a network error, fall back to the cached copy instead of raising.

```
if cache exists and age <= max_age_hours: return read(cache)
try:    urlretrieve(URL, cache)
except: if cache exists: return read(cache)   # offline fallback
        else: raise
```

## (2) Player attributes

**Source:** FIFA-22 complete player dataset (sofifa dump).

- **Method:** one-time HTTPS GET of the CSV to `data/raw/fifa_players_22.csv`; **static cache** (attributes don't change), refreshed only with `force=True`.
- **Columns used:** `short_name, overall` + the six skills `pace, shooting, passing, dribbling, defending, physic`.
- **Role:** the quantitative skill layer the real roster is joined against (Stage 2).

*Vintage caveat:* FIFA-22 is a fixed snapshot; swap `FIFA_CSV_URL` for an FC24/25 dump or an exact per-player API — the schema contract stays the same.

## (3) Real 2026 squads

**Source:** Wikipedia "2026 FIFA World Cup squads" (per nation).

- **Method:** MediaWiki API request for page *wikitext* (not rendered HTML), with an explicit `User-Agent` header (Wikipedia rejects blank UAs with HTTP 403).
- **Parse:** `parse_squads()` reads the `{{National football squad}}` template rows into `name, position, age, caps` per player; team names normalized via `WIKI_TEAM_ALIASES`.
- **Why:** this is the *ground-truth roster* — it keeps retired / uncalled players out of every table.

## (4) Official metadata

**Source:** `rezarahiminia/worldcup2026` (open JSON).

- **Method:** HTTPS GET of `football.teams.json`, parsed to a DataFrame of `name, fifa_code, group, flag`.
- **Role:** authoritative FIFA codes, group letters, and flag emoji for presentation — decoupled from our hard-coded draw so the two can be cross-checked.
- **Degrades gracefully:** if unreachable, the build falls back to local metadata and logs a warning.

# Organization

## Canonicalization

Different sources spell teams differently; all are mapped to one canon on ingest.

| Alias map | Scope | Example |
|---|---|---|
| `INTL_NAME_ALIASES` | results feed | Czechia → Czech Republic |
| `FIFA_NATION_ALIASES` | FIFA nationality | South Korea → Korea Republic |
| `WIKI_TEAM_ALIASES` | Wikipedia pages | Ivory Coast → Côte d'Ivoire |

Mapping is applied *to* the source name on read and *back* to canon on emit, so joins across sources are exact.

## Derived match frames

**`build_real_matches(start, end)`** — the training frame. Drops unscored rows, filters to [start, end] (`end` defaults to *today*) and to the 48 teams. Schema:

`match_id, date, home_team, away_team, home_goals, away_goals, tournament, neutral`

**`wc2026_matches()`** — all 2026 fixtures; adds canonical `home`/`away`. **Rows with null score = not yet played.**

That scored-vs-null split is exactly what separates *backtest* (played) from *forecast* (upcoming) downstream.

## On-disk layout

| Directory | Contents |
|---|---|
| `data/raw/` | cached source downloads (git-ignored) |
| `data/interim/` | scratch / intermediate frames |
| `data/processed/` | published CSVs (committed) |
| `artifacts/` | posteriors (.nc, ignored) + charts (.png, committed) |
| `docs/` | generated reports & this deck |

Two published tables live in `data/processed/`: `wc2026_players.csv` (per player) and `wc2026_team_assessment.csv` (per team).

# Extraction & Features

## Player extraction — the surname join

Real roster × FIFA attributes (`scripts/27_build_player_dataset.py`):

```python
key = lambda name: name.split()[-1].lower()          # surname
fifa = fifa.sort_values("overall", desc).drop_duplicates(key)  # best namesake
players = live.merge(fifa, on=key, how="left")        # keep every real player
rating_source = "fifa-match" if overall not null else "team-median"
# back-fill unmatched skills: team median, then global median
```

- **Left join** ⇒ no real player is ever dropped.
- **Provenance flag** `rating_source` marks matched vs. filled rows (~70% exact coverage).
- GKs (no pace/defending in FIFA) get the same median fill.

## Per-player features

On each player row (`features/player_features.py`):

| Feature | Definition |
|---|---|
| `longevity` | ½·(z(career_years) + z(caps)) |
| `skill_index` | Σ wₐ·ratingₐ  (shoot .25, pass/drib .20, pace .15, def/phys .10) |
| `social_score` | z( log₁₀(followers) · (1 + engagement) ) |

z(·) = population standardization (mean 0, sd 1). Position is also one-hot encoded for per-line analysis.

## Age × role weighting

Youth boosts attacking pace; seniority boosts defensive solidity (`data/live_squads.py`):

- **pace weight** = clip( 1.20 − 0.03·max(0, age−23), 0.75, 1.20 )  → ~1.2 at 20, 0.85 at 35
- **experience weight** = clip( 0.80 + 0.025·max(0, age−22), 0.80, 1.25 )  → ~0.8 at 22, 1.25 at 35

Then `pace_w = pace · pace_weight(age)` and `def_w = defending · experience_weight(age)`, aggregated over attackers / defenders.

# Aggregation

## Player → team prior

Per team, over the strongest 16 by `overall` (`live_team_features`):

- `age_role = ½·z(young_pace) + ½·z(senior_solidity)`
- `composite = 0.80·z(squad_overall) + 0.06·z(log(1+caps)) + 0.04·z(age) + 0.10·z(age_role)`
- **`prior_strength = z(composite) · 0.5`**  → the model's prior mean on attack

Skill dominates; caps/age/role add small, auditable nudges. Match data can still override the prior — `beta_prior` learns how much to trust it.

## Published team assessment

A separate roll-up for presentation (`scripts/27`), assembled by a left-join chain keyed on `team`:

```python
team = DataFrame(48 teams)
   .merge(results)   # 2026 W/D/L, GF/GA, points   (from wc2026_matches)
   .merge(strength)  # attack/defence/net/model_rank (posterior_strength_real.csv)
   .merge(elo)       # elo, elo_rank               (elo_ratings.csv)
   .merge(agg)       # squad_overall, attack/defence_strength,
                     # young_pace, senior_solidity, tier, style, star_player
form_momentum = combined_shifts(...)   # recency form + sentiment nudge
flag = fifa_code -> flag               # worldcup_repo metadata
```

`tier` from `squad_overall`; `style` from sign(attack − defence); `star_player` = top outfield by `overall`.

## Per-group structure

- `data/teams.py`: 48 `Team(name, code, confederation, group, latent_strength)` records encode the real draw.
- `by_group()` → `{letter: [4 teams]}`; asserts enforce **12 groups × 4**.
- The `group` column rides through both published tables.
- `by_group()` drives the group stage in *both* simulators (top-2 + 8 best thirds → knockout): `models/simulate.py` (Bayesian) and `models/elo_sim.py` (Elo).

# Presentation

## Presentation & the daily chain

**Surfaces:** `wc2026_players.csv`, `wc2026_team_assessment.csv`; `docs/WINNERS.md`, `CHAMPION_TRACKER.md`, `FORECAST_LOG.md`; `artifacts/*.png` (calibration, champion timeline).

```
make daily:
  real-players -> live-squads -> live-features -> real-fit -> elo
    -> dataset(27) -> winners(28) -> track/champion -> timeline -> log
```

Each run: fresh squads + results → recompute features/prior → refit → rebuild both tables → regenerate every forecast → the CI bot commits the diff.

## Extending it & honest limits

- **Better attributes:** replace the surname join with an exact-ID feed; the PLAYER schema (and everything downstream) is unchanged.
- **New prior signal:** add a column in `live_team_features`, fold it into `composite` with a small weight, then **validate on the RPS scoreboard** — a feature stays only if it lowers RPS.
- **New source:** add a loader returning a documented schema; wire aliases if names differ.
- **Limits:** ~70% surname-join coverage (flagged), FIFA-22 vintage, results feed lags real time by hours.

## Thank you

`docs/DATA_PIPELINE.md` — the written reference
`docs/data_pipeline_slides.tex` — the Beamer/LaTeX source (compile for PDF)

github.com/mariaob1201/2026-world-cup-analytics
