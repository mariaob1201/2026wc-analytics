# ⚽ World Cup 2026 — End-to-End Goal Forecasting

**The core outcome of this project: forecast the goals in every World Cup match,
score those forecasts against the real results as they come in, and keep a live,
honest track record of how good the forecasts are.** Everything else — win
probabilities, title odds, tactics — is derived from the goal forecast.

```
 forecast goals  ──▶  match is played  ──▶  compare to ground truth  ──▶  roll forward
 (Bayesian model)     (live results)        (hit-rate, goals MAE, RPS)     (refit daily)
```

A hierarchical Bayesian model gives each team an attack and a defence, turning any
fixture into a full **scoreline distribution**. Predicted goals are logged
*before* kickoff and checked against the actual score afterward — so accuracy
accumulates over the tournament instead of being asserted once.

## 🎯 The headline: forecasts vs ground truth → [docs/FORECAST_LOG.md](docs/FORECAST_LOG.md)

Every goal forecast and how it turned out, with the running scoreboard:

| | Predicted (xG) | Predicted | **Actual** | ✓ |
|---|---|---|---|:--:|
| Mexico v South Africa | 1.6–0.8 | 1-0 | **2-0** | ✅ |
| France v Senegal | 1.6–0.8 | 1-0 | **3-1** | ✅ |
| Spain v Cape Verde | 2.0–0.6 | 1-0 | **0-0** | — |

**Running accuracy (out-of-sample, live):** 54% outcome hit-rate · 1.54 goals MAE ·
RPS 0.166. The model **beats Elo and a naive baseline on RPS across the 2018, 2022
and 2026 World Cups** — see the benchmark in [docs/EVALUATION.md](docs/EVALUATION.md).

```bash
make daily            # pull latest results → refit → forecast → score vs truth
```

This whole loop runs **automatically every day** via GitHub Actions
([`.github/workflows/track.yml`](.github/workflows/track.yml)): it pulls the day's
results, refits, forecasts the next games, fills in ground truth for matches just
played, and commits the refreshed reports.

### What's in the repo

| Output | What it is |
|---|---|
| **[docs/FORECAST_LOG.md](docs/FORECAST_LOG.md)** | **Goal forecasts vs ground truth + running accuracy (the main outcome)** |
| [docs/EVALUATION.md](docs/EVALUATION.md) | Backtest vs Elo + naive baselines (2018/2022/2026), RPS/log-loss |
| [docs/match_predictions.md](docs/match_predictions.md) | Per-match predicted goals vs actual + next-slate forecasts |
| [docs/CHAMPION_TRACKER.md](docs/CHAMPION_TRACKER.md) | Goals rolled up → title odds, conditioned on current results |
| [docs/WINNERS.md](docs/WINNERS.md) | Next-day match picks + Elo champion scorecard + predicted-vs-true track record |
| [docs/analytics.md](docs/analytics.md) | Calibration chart, match sentiment & tactics |
| [docs/METHODOLOGY.md](docs/METHODOLOGY.md) · [docs/LIVE_PIPELINE.md](docs/LIVE_PIPELINE.md) | Methodology + the live/agent automation guide |

### Title odds over the tournament

How each contender's championship probability moved as matches were played
(x = games played, conditioned only on results known by then — `make timeline`):

![Title odds timeline](artifacts/champion_timeline.png)

> **For researchers:** a reference implementation of a Baio–Blangiardo-style
> hierarchical Poisson goals model — partial pooling for the 48-team field,
> recency-weighted likelihood, an Elo cross-check, an LLM judge/extractor, and a
> proper out-of-sample backtest (RPS/log-loss vs baselines).

---

## How it works (one model, three layers)

**1. Goals.** Each team has a latent **attack** and **defence**. For a fixture,
`log λ = intercept (+ home_adv) + attack[i] − defence[j]` gives each side a Poisson
goal rate → a full scoreline distribution. Rating *teams* (not matchups) is what
lets it predict pairings that have never been played.

**2. Learning, with the newcomer problem handled.** Abilities are fit on **real
international results** (Bayesian, MCMC). **Partial pooling** shrinks thin-record
teams toward the mean and a **squad-strength prior** built from player ratings — so
debutants get sensible, *uncertain* estimates instead of overconfident extrapolation
(the principled alternative to Bradley-Terry in an expanded field).

**3. Tournament.** Monte-Carlo simulation over the **real 12-group / knockout
structure**, holding completed games fixed and simulating the rest. Current **form +
sentiment** enter as a small, capped goal-rate nudge.

Cross-checks: a recency-weighted **Elo** (who's hot now) and an **LLM-as-a-Judge**
(OpenAI or Claude — auto-detected from your API key) that fuses ratings with
scouting for a single fixture.

---

## Quick start

```bash
make setup     # .venv + deps (PyMC, ArviZ, pandas, matplotlib)
make daily     # ⭐ the full loop: pull results → refit → forecast → score vs truth
make evaluate  # backtest vs Elo + naive baselines (the scoreboard)
make test      # fast test suite
```

Single match on demand:

```bash
.venv/bin/python scripts/12_predict_match.py --home Mexico --away Czechia
# → expected goals, most-likely score, P(win/draw/win), over-2.5, both-teams-score
```

---

## Pipeline (stages map to `scripts/`)

| Stage | Does | Key output |
|---|---|---|
| 05 | Build real squads + features + semantic profiles | per-team prior, `team_profiles.md` |
| 06 | Fit Bayesian goals model on real results (to today) | `posterior_real.nc` |
| 10 | Elo over real results + Elo-vs-Bayesian comparison | `elo_ratings.csv` |
| 12 | Predict goals for one fixture | console |
| 13 | Pre-tournament **backtest** + forecast | `match_predictions.md` |
| 14 | Tracking analytics, **sentiment**, **tactics** | `analytics.md`, charts |
| 15 | Momentum-aware full simulation | `simulation_real.csv` |
| 16 | **Champion Tracker** (state-conditioned) | `CHAMPION_TRACKER.md` |
| 07 | Mexico deep-dive (quant + tactics + media/X sentiment) | `mexico_assessment.md` |
| 11 | LLM-as-a-Judge for a fixture (Claude + Elo fallback) | console |

A synthetic demo pipeline (`make all`, stages 01–04) runs offline without any
real data, for learning the mechanics.

---

## Data

| Source | Role |
|---|---|
| **martj42 international results** | Likelihood — fits attack/defence + Elo (real, live-updated) |
| **FIFA player dataset** (sofifa schema) | Squad-strength **prior** (skills, age/seniority, value) |
| **ESPN / SI / NPR / Wikipedia** | Scouted form, tactics, knockout projections, sentiment |
| **X API** (optional, pay-per-use) | Fan sentiment via a budget-capped collector |

Player and result data are reconciled across sources with explicit name aliases.

---

## Validation & honesty

The model is **backtested out-of-sample**: trained only on pre-tournament data, it
predicted the played matches at a **~54% outcome hit-rate** and is **well-calibrated**
(see the calibration chart). Known limitations, each with a mitigation, are documented
in [METHODOLOGY.md §10–11](docs/METHODOLOGY.md) — most importantly **strength-of-schedule**
(newcomers' qualifying opposition), the **independence-Poisson** assumption (Dixon-Coles
upgrade), and the FIFA-vintage player prior.

Reproducible: seeded throughout, fits in seconds, `pytest` covers data, features, a
tiny end-to-end fit, Elo, momentum, tactics, and the judge fallback.

---

## References

martj42/international_results · FIFA complete player dataset · Maher (1982);
Dixon & Coles (1997); Baio & Blangiardo (2010); World Football Elo Ratings.
Scouting/sentiment citations are inline in `data/scouting.py`.

_Numbers here are an analytical exercise, not betting advice._
