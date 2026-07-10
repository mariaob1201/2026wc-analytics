# Data Pipeline — a developer's reference

How raw public data becomes per-player rows, per-team covariates, and the two
published tables. Everything here is keyless and reproducible; the daily GitHub
Action re-runs the whole chain ([LIVE_PIPELINE.md](LIVE_PIPELINE.md)).

> **Slides:** a presentation version of this doc —
> [`data_pipeline_slides.pptx`](data_pipeline_slides.pptx) (PowerPoint) and
> [`data_pipeline_slides.tex`](data_pipeline_slides.tex) (Beamer/LaTeX source;
> compile with `pdflatex` or Overleaf, or regenerate the pptx with
> `pandoc data_pipeline_slides.md -o data_pipeline_slides.pptx --slide-level=2`).

```
PUBLIC SOURCES                 EXTRACTION                 FEATURES                  STRUCTURE
─────────────                  ──────────                 ────────                  ─────────
martj42 results feed ─┐        wc2026_matches()           per-player:               48 teams,
FIFA-22 attributes ───┼──►     build_real_matches()   ─►  longevity, skill_index,   12 groups
Wikipedia squads ─────┤        fetch_squads()             social_score, age×role    (teams.py)
worldcup2026 repo ────┘        + FIFA join (surname)      per-team: prior_strength      │
                                     │                          │                       ▼
                                     ▼                          ▼                  by_group() drives
                               wc2026_players.csv        team_features_live.csv    group → knockout
                                                          → model prior             simulation
```

**Module map**

| Concern | Module |
|---|---|
| Source download + caching, name aliasing | `data/sources.py` |
| Live roster scrape + real prior (age×role) | `data/live_squads.py` |
| Synthetic-demo feature engineering | `features/player_features.py` |
| 48-team draw + grouping | `data/teams.py` |
| Open metadata (codes/flags) | `data/worldcup_repo.py` |
| Published tables (players + team assessment) | `scripts/27_build_player_dataset.py` |

---

## Stage 1 — Collection (`data/sources.py`)

All sources are raw GitHub URLs cached under `data/raw/`.

| Source | URL constant | Loader | Cache file |
|---|---|---|---|
| martj42 international results | `INTL_RESULTS_URL` | `download_intl_results(force=False, max_age_hours=6.0)` | `intl_results.csv` |
| FIFA-22 player attributes | `FIFA_CSV_URL` | `download_fifa(force=False)` | `fifa_players_22.csv` |
| Wikipedia 2026 squads | (per-nation) | `fetch_squads(force=False)` | `live_squads.csv` |
| rezarahiminia/worldcup2026 | `worldcup_repo.REPO` | `fetch_team_metadata()` | (in-memory) |

**Caching semantics.** `download_intl_results` re-fetches when the cached file's
mtime is older than `max_age_hours` (the feed updates during the tournament),
and on a network error falls back to the stale cache rather than raising. The
FIFA dump is static, so it's cached indefinitely after first fetch.

**Name aliasing.** Team names differ across sources, so two dicts normalize to
our canon: `INTL_NAME_ALIASES` (results feed) and `FIFA_NATION_ALIASES` (FIFA
nationalities). Wikipedia has its own `WIKI_TEAM_ALIASES` in `live_squads.py`.

**Derived match frames.**

`build_real_matches(start="2022-01-01", end=None) -> DataFrame` — the training
frame. Drops unscored rows, filters to `[start, end]` (end defaults to
`config.today()` so we never train on the future) and to our 48 teams, then
emits a fixed schema:

| col | dtype | notes |
|---|---|---|
| `match_id` | int | row index |
| `date` | str (ISO) | |
| `home_team`, `away_team` | str | canonical names |
| `home_goals`, `away_goals` | int | |
| `tournament` | str | drives Elo's K-factor |
| `neutral` | bool | host-nation exception |

`wc2026_matches() -> DataFrame` — every 2026 WC row (`tournament == "FIFA World
Cup"`, `date >= 2026-06-01`) with canonical `home`/`away` columns added. **Rows
with null `home_score`/`away_score` are fixtures not yet played** — that split
(scored vs. null) is what separates backtest from forecast downstream.

---

## Stage 2 — Individual player extraction (`scripts/27_build_player_dataset.py`)

Produces `data/processed/wc2026_players.csv`, one row per called-up player.

```python
live = fetch_squads()                       # real roster: name, position, age, caps, team
fifa = download_fifa()                       # attributes pool
rt   = fifa[["short_name","overall",*SKILLS]]
rt["_last"] = rt["short_name"].map(last)     # last() = surname, lowercased
rt = rt.sort_values("overall", ascending=False).drop_duplicates("_last")  # best namesake wins
pl = live.merge(rt, on="_last", how="left")  # left join keeps every real player
pl["rating_source"] = np.where(pl["overall"].notna(), "fifa-match", "team-median")
# back-fill unmatched skills with the team median, then the global median:
for c in ["overall", *SKILLS]:
    pl[c] = pl.groupby("team")[c].transform(lambda s: s.fillna(s.median()))
    pl[c] = pl[c].fillna(pl[c].median()).round(0)
```

**Join algorithm:** surname match (`name.split()[-1].lower()`), de-duplicated to
the highest-`overall` namesake, left-joined so no real player is dropped;
unmatched players inherit their squad's median attributes and are flagged
`rating_source="team-median"`. GKs (no pace/defending in FIFA) get the same
fill.

**PLAYER schema** (`wc2026_players.csv`):
`team, fifa_code, group, name, position, age, caps, overall, pace, shooting,
passing, dribbling, defending, physical, rating_source`.

> **Known limits (encoded, not hidden):** surname join ≈70% exact coverage
> (`rating_source` tells you which rows); FIFA-22 is a fixed vintage. Swap in an
> exact per-player feed (api-football) behind the same schema — the join is the
> only thing that changes.

---

## Stage 3 — Per-player features

Two feature paths exist for two purposes.

### 3a. Analytics features (`features/player_features.py`)

`add_player_features(players)` adds, per player:

| Feature | Definition |
|---|---|
| `longevity` | `(z(career_years) + z(caps)) / 2` |
| `skill_index` | `Σ rating_c · w_c` over the 6 skills, weights in `SKILL_WEIGHTS` (shooting .25, passing/dribbling .20, pace .15, defending/physical .10) |
| `social_score` | `z(log10(followers) · (1 + engagement_rate))` |
| `pos_*` | one-hot of position |

`_z` is population standardization (mean 0, sd 1, zero-variance-safe).

### 3b. Age × role weighting (`data/live_squads.py`)

The role-aware signal you asked for: youth boosts *attacking pace*, seniority
boosts *defensive solidity*, via age curves (clipped):

```python
_youth_pace_weight(age)  = clip(1.20 - max(0, age-23)·0.03, 0.75, 1.20)  # ~1.2@20 → 0.85@35
_experience_weight(age)  = clip(0.80 + max(0, age-22)·0.025, 0.80, 1.25) # ~0.8@22 → 1.25@35
pace_w = pace * _youth_pace_weight(age)         # per attacker
def_w  = defending * _experience_weight(age)    # per defender
```

---

## Stage 4 — Aggregation: player → team

### 4a. The model prior (`live_team_features(live, fifa)` → `team_features_live.csv`)

Per team, using the strongest 16 by `overall` and position splits:

| Team column | From |
|---|---|
| `squad_overall` | mean `overall` of top-16 |
| `avg_caps`, `avg_age` | squad means |
| `young_pace` | mean `pace_w` over FW/MF |
| `senior_solidity` | mean `def_w` over DF |
| `age_role` | `0.5·z(young_pace) + 0.5·z(senior_solidity)` |

collapsed into one standardized covariate:

```
composite      = 0.80·z(squad_overall) + 0.06·z(log1p(avg_caps))
               + 0.04·z(avg_age)       + 0.10·z(age_role)
prior_strength = z(composite) · 0.5      # ~[-1, 1], the model's prior mean
```

(The synthetic-demo analogue is `build_team_features` in `player_features.py`:
top-16 `skill_index` at 0.70, longevity 0.15, market value 0.10, star power
0.05.) `prior_strength` becomes the **mean of the prior on each team's attack**
in the Bayesian model — the match data can still override it, with `beta_prior`
learning how much to trust it.

### 4b. The published assessment (`scripts/27` → `wc2026_team_assessment.csv`)

A separate aggregation for presentation. `players.groupby("team")` computes
`squad_overall, avg_age, total_caps, attack_strength` (mean of pace/shooting/
dribbling), `defence_strength` (mean DF `defending`), `young_pace`,
`senior_solidity`; then derived semantics: `tier` (from `squad_overall`), `style`
(sign of attack−defence), `star_player` (top outfield by `overall`). Finally a
left-join chain assembles the row:

```python
team = DataFrame(teams)
    .merge(results)    # 2026 W/D/L, GF/GA, points  (_team_results)
    .merge(strength)   # attack/defence/net_strength/model_rank  (posterior_strength_real.csv)
    .merge(elo)        # elo/elo_rank                (elo_ratings.csv)
    .merge(agg)        # aggregated player characteristics + semantics
team["form_momentum"] = combined_shifts(...)   # recency form + sentiment nudge
team["flag"] = fifa_code -> flag               # worldcup_repo metadata
```

**TEAM schema** (`wc2026_team_assessment.csv`): `team, fifa_code, group, flag,
played, wins, draws, losses, goals_for, goals_against, goal_diff, points,
attack, defence, net_strength, model_rank, elo, elo_rank, squad_overall,
avg_age, total_caps, attack_strength, defence_strength, young_pace,
senior_solidity, form_momentum, tier, style, star_player`.

---

## Stage 5 — Structure & presentation

**Per group (`data/teams.py`).** 48 `Team(name, code, confederation, group,
latent_strength)` records encode the real draw; `by_group() -> {letter: [4
teams]}` with asserts enforcing 12×4. The `group` column rides through both
tables, and `by_group()` is what both simulators iterate for the group stage
(top-2 + 8 best thirds → knockout): `models/simulate.py` (Bayesian) and
`models/elo_sim.py` (Elo).

**Presentation surfaces:**

| Surface | Artifact |
|---|---|
| Tabular datasets | `data/processed/wc2026_players.csv`, `wc2026_team_assessment.csv` |
| Forecasts / trackers | `docs/WINNERS.md`, `CHAMPION_TRACKER.md`, `match_predictions.md`, `FORECAST_LOG.md` |
| Charts | `artifacts/*.png` (calibration, champion timeline, …) |

**Daily chain (`make daily`):**

```
real-players → live-squads → live-features → real-fit → elo
  → dataset(27) → winners(28) → track/champion → timeline → prediction-log
```

Each run: fresh squads + results → recompute features/prior → refit → rebuild
both tables → regenerate every forecast, then tracker-bot commits the diff.

---

## Extending it

- **Better player attributes:** replace the surname join in Stage 2 with an
  exact-ID feed; keep the PLAYER schema and everything downstream is unchanged.
- **New prior signal:** add a column in `live_team_features`, fold it into
  `composite` with a small weight, then **validate on the RPS scoreboard**
  ([EVALUATION.md](EVALUATION.md)) — a feature stays only if it lowers RPS.
- **New source:** add a loader in `data/sources.py` (or a sibling adapter like
  `worldcup_repo.py`) returning a documented schema; wire aliases if names differ.
