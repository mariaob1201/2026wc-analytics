# ⚽ World Cup 2026 — Bayesian Champion Tracker

A **living, state-aware forecast** of the 2026 FIFA World Cup. It models **goals**
with a hierarchical Bayesian model, conditions on the **matches already played**,
and answers two linked questions with one model:

1. **Next games** — how many goals each side scores in the upcoming fixtures.
2. **The trophy** — each team's probability of winning the World Cup, given
   everything that has happened so far.

Goals are the primitive; winners are a simulation over goals. Squad **skill**, the
**current results**, and **form + X/ESPN sentiment** all feed the prediction.

> **For researchers:** this is a reference implementation of a Baio–Blangiardo-style
> hierarchical Poisson football model, extended with partial pooling for a 48-team
> field, a recency Elo cross-check, an LLM-as-a-Judge, and an honest backtest. The
> full write-up — assumptions, diagnostics, and open problems — is in
> **[docs/METHODOLOGY.md](docs/METHODOLOGY.md)**.

---

## The headline view → [docs/CHAMPION_TRACKER.md](docs/CHAMPION_TRACKER.md)

Conditioned on the matches played so far, the model simulates the rest of the
tournament. Re-run after each matchday:

```bash
make track-champion     # refit on current results → tracker (odds + next games)
```

| Output | What it is |
|---|---|
| [docs/CHAMPION_TRACKER.md](docs/CHAMPION_TRACKER.md) | Title odds (conditioned on current state) + next-game goal forecasts + standings |
| [docs/match_predictions.md](docs/match_predictions.md) | Pre-tournament **backtest**: predicted goals vs actual, match by match |
| [docs/analytics.md](docs/analytics.md) | Tracking charts (calibration), match **sentiment** & **tactics** |
| [docs/METHODOLOGY.md](docs/METHODOLOGY.md) | Full technical methodology, assumptions, and research agenda |
| `artifacts/*.png` | Charts (champion odds, calibration, goals scatter, forecast bars) — regenerable |

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
(Claude) that fuses ratings with scouting for a single fixture.

---

## Quick start

```bash
make setup          # .venv + deps (PyMC, ArviZ, pandas, matplotlib)
make real-all       # full real-data pipeline (squads → fit → elo → backtest → sim)
make track-champion # the living champion tracker (re-run each matchday)
make test           # fast test suite
```

Single match on demand:

```bash
.venv/bin/python scripts/12_predict_match.py --home Mexico --away Czechia
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
