# World Cup 2026 Analytics — Methodology Report

**Predicting the 2026 FIFA World Cup from a hierarchical Bayesian goals model, complemented by Elo and an LLM judge.**

_Technical report. Compiled 2026-06-19. This is a living document — sections marked **[Open]** are active research directions._

---

## 1. Summary

We forecast the 2026 World Cup by **modelling goals, not winners**. Each team is given a latent *attack* and *defence* ability; the number of goals each side scores in a match is a Poisson draw whose rate combines the two teams' abilities. Winners, draws, qualification, and the eventual champion are all *derived* by simulating scorelines through the real tournament structure.

Three design choices drive the methodology:

1. **Teams are rated individually, not as matchups.** A fixture is predicted by combining two teams' abilities, so the model handles pairings that have never been played — essential for a 48-team field with debutants and a results-driven knockout bracket.
2. **Hierarchical partial pooling** regularizes teams with thin match records toward the population mean and a squad-strength prior, producing honest, wide uncertainty instead of overconfident extrapolation. This is the principled alternative to paired-comparison models (Bradley-Terry), which over-state established-vs-newcomer gaps when data is sparse.
3. **Uncertainty propagates end-to-end.** Inference is Bayesian (MCMC), so every ability is a posterior *distribution*. The tournament simulation draws fresh parameters each run, so headline probabilities reflect how unsure we are, not a single point estimate.

Two complementary views sit alongside the core model: a **recency-weighted Elo** (sequential, emphasises current form and high-stakes games) and an **LLM-as-a-Judge** (fuses ratings with qualitative scouting for a single fixture). Where the Bayesian and Elo views disagree is a useful flag for teams the data is least certain about.

---

## 2. Problem statement and scope

- **Target:** the full scoreline distribution for any fixture among the 48 finalists, and tournament-level outcome probabilities (advance, reach each round, win the title).
- **Unit of prediction:** a single match between two named teams. Not a per-team "goals per game" average and not an all-play-all league table.
- **Structure:** the real 2026 format — 12 groups of 4, top 2 of each group plus the 8 best third-placed teams advancing to a Round of 32, then single-elimination to the final.
- **Non-goals:** player-level event modelling (xG from shot data), live in-play prediction, or betting-market arbitrage. The model consumes *match results* and *squad ratings*, not event streams.

---

## 3. Data

| Source | What it provides | Use |
|---|---|---|
| **martj42 international results** (open, GitHub) | Every men's international since 1872, live-updated incl. WC 2026 matches | Likelihood — fits attack/defence and Elo |
| **FIFA player dataset** (sofifa schema, ~19k players) | Per-player position, age, six skill ratings, market value, international reputation | Squad-strength **prior** |
| **Scouted intelligence** (ESPN, SI, NPR, Wikipedia) | Coach, formation, form, key players, fan/expert sentiment, knockout projections | Qualitative layer + LLM-judge context |
| **X / social (optional)** | Fan sentiment via the X API (pay-per-use) | Sentiment layer (budget-capped collector) |

**Filtering.** For the live model we use international results from **2022-01-01 to the present cutoff (2026-06-19)**, restricted to the 48 finalists — **586 matches**. The window balances recency (current squads) against sample size. Team names are reconciled across datasets with explicit alias maps (e.g. `Czechia → Czech Republic`, `Ivory Coast → Côte d'Ivoire`, `South Korea → Korea Republic`).

**Squads.** From the player dataset we take each nation's **top 26 by overall** as a proxy squad (47 of 48 teams resolve; one has no players in the source and falls back to a neutral prior). Vintage caveat: the player snapshot predates 2026, so squad composition is approximate — see §10.

---

## 4. Feature engineering → the squad-strength prior

Per-player features are rolled up to one number per team that seeds the model's prior:

- **Skill index** — weighted blend of the six skill ratings (attack-leaning weights).
- **Longevity** — standardized blend of career length and caps (experience proxy).
- **Social/reputation** — international reputation as a soft star-power signal.

These combine (skill 0.70, longevity 0.15, log squad market value 0.10, star power 0.05), standardized, and scaled to roughly the log-goal-rate range, giving each team a `prior_strength` covariate. **Interpretation:** before any match is observed, a squad with better players is *a priori* expected to attack better — but the data is allowed to override this (§5).

---

## 5. Core model — hierarchical Bayesian Poisson scoreline

For a match between home team `h` and away team `a`:

```
home_goals ~ Poisson(λ_home)
away_goals ~ Poisson(λ_away)

log λ_home = intercept + home_adv + att_eff[h] − def[a]
log λ_away = intercept           + att_eff[a] − def[h]
```

**Abilities and the player prior.** Effective attack is a covariate term plus a residual:

```
att_eff[t] = beta_prior · prior_strength[t]  +  att[t]
```

`prior_strength` is the player-feature covariate (§4); `beta_prior` is *estimated*, so the model learns how much to trust the squad ratings. On the live fit `beta_prior ≈ 0.53` — it leans on player ratings, but less than it would with no match data, exactly as it should.

**Partial pooling (the newcomer fix).** Residual abilities are drawn from a shared distribution whose spread is itself estimated:

```
att[t] = sigma_att · att_raw[t]      att_raw ~ ZeroSumNormal(1)
def[t] = sigma_def · def_raw[t]      def_raw ~ ZeroSumNormal(1)
```

Teams with few matches are shrunk toward the mean (and toward their prior); teams with many matches keep their own signal. This is the regularization that prevents a debutant's handful of lopsided qualifiers from producing an extreme rating.

**Priors.** `intercept ~ Normal(0,1)`, `home_adv ~ Normal(0.25, 0.25)`, `beta_prior ~ Normal(0,1)`, `sigma_att, sigma_def ~ HalfNormal(0.5)`.

**Identifiability.** Attack/defence are defined only up to a constant, so the `ZeroSumNormal` parameterization forces abilities to average to zero and lets `intercept` absorb the overall scoring level.

**Why not Bradley-Terry / Elo-only as the core?** A paired-comparison model rates win propensity, discarding margins, and gives each team a free parameter that overfits sparse records. The hierarchical Poisson keeps goal margins (a 4-0 says more than a 1-0) and pools sparse teams — both matter more in an expanded field.

---

## 6. Inference

Sampled with **NUTS** (PyMC), 4 chains. Diagnostics on the live fit are clean: **R-hat ≈ 1.00**, healthy effective sample sizes, no divergences.

**A reproducibility note worth recording.** The first parameterization (centered abilities centered on the covariate) produced a **funnel** — `sigma_att` near zero, R-hat 1.6, ESS in single digits — and raising `target_accept` made it *worse*. The fix was the **non-centered** parameterization above (sample standardized offsets, scale by σ separately), which restored R-hat 1.0 and lifted ESS by ~100×. This is the canonical hierarchical-model pathology and its canonical cure.

---

## 7. Prediction — from parameters to goals

For a fixture, `predict_match` forms each side's rate `λ = exp(intercept [+ home_adv] + att_eff − def)` **for every posterior draw**, builds the Poisson scoreline matrix, and averages over draws (a **posterior-predictive** distribution that carries parameter uncertainty). From that single matrix:

- expected goals per side,
- most-likely scoreline,
- 1X2 probabilities (win/draw/win = sums over the matrix),
- markets: over/under 2.5, both-teams-to-score.

Example (live fit, neutral venue): *Mexico vs Senegal* → xG 1.20–1.09, most likely **1-1**, Mexico 38% / draw 28% / Senegal 33%. **Winners are sums over the goals matrix** — there is no separate "winner model."

---

## 8. Tournament simulation

Outcome probabilities can't be read off arithmetic because the bracket branches, so we run **Monte Carlo** over the real 2026 structure:

1. Play each group's actual fixtures by drawing scorelines from the model.
2. Rank within group by points → goal difference → goals for → random tie-break.
3. Advance the **top 2 per group + 8 best third-placed teams** to the Round of 32.
4. Single-elimination through the bracket; knockout draws resolved by a near-coin-flip shootout slightly favouring the stronger side.
5. Repeat thousands of times, drawing **fresh posterior parameters each tournament**, and tabulate how often each team reaches each round.

Because matchups are scored from team-level abilities, the simulation **generates each knockout round's fixtures from the previous round's results** — fixtures that don't exist yet are no obstacle.

---

## 9. Complementary methods

**Elo (recency-weighted).** A sequential rating walked over the same real results in date order: `R' = R + K·G·(W − E)`, with `K` larger for World Cup games than friendlies and a goal-difference multiplier `G`. It answers "who is hot *now*", weighting current and high-stakes results. On the live data Elo ranks Mexico **7th** vs the Bayesian model's **20th** — the pooled view says "solid", the momentum view says "surging". Their disagreement localizes uncertainty.

**LLM-as-a-Judge.** For a single fixture, an LLM (OpenAI or Claude — provider auto-detected from the configured API key, structured output) is handed both ratings, recent form, the squad/tactics profile, sentiment, and venue, and returns calibrated 1X2 probabilities + rationale. It fuses signals a formula can't and serves as a qualitative cross-check; an Elo-only fallback runs when no API key is configured.

---

## 10. Key assumptions and limitations

| Assumption / limitation | Impact | Mitigation / status |
|---|---|---|
| **Goals are independent Poisson** | Understates correlation at 0-0/1-1 | **[Open]** Dixon-Coles low-score correction or bivariate Poisson |
| **Ratings transitive on a common scale** | Cross-confederation matchups (rare opponents) least reliable | **[Open]** confederation/opponent-strength random effect |
| **No strength-of-schedule adjustment** | Newcomers' qualifying results vs weaker opposition inflate ratings; pooling tames variance, not this bias | **[Open]** — the most important next step |
| **Player prior is FIFA-vintage** | Squad composition predates 2026 (some dated names) | Swap in a current FC24/FC25 dataset (one-line source change) |
| **Elo cold-start at 1500** | Teams with few games under-converge | Seed initial ratings, or down-weight early; or defer to Bayesian for sparse teams |
| **Knockout bracket seeded by strength** | Approximates, not reproduces, the official R32 crossing table | Swap in the official crossing map once finalized |
| **One nation lacks player data** | Neutral prior for that team | Acceptable; flagged at runtime |

---

## 11. Validation and future work **[Open]**

The current evidence for the model is internal coherence (sensible rankings, clean diagnostics) and face validity. The defensible next steps:

0. **xG-based model** *(machinery built, stage 21)* — `build_xg_model` fits
   attack/defence on **expected goals** (Gamma likelihood) instead of goals, since
   xG is a less-noisy measure of chance quality. `scripts/21_xg_backtest.py`
   compares it to the goals model by RPS and keeps it only if it wins. **Status:**
   verified on synthetic data; the real comparison needs an xG-labelled match table
   (`data/raw/xg_matches.csv` from FBref match reports or StatsBomb open data) —
   bulk xG for training matches isn't cheaply scrapeable, so this is supplied, not
   auto-harvested. xG + shots are the highest-expected-value upgrade.
1. **Calibration on held-out matches** — posterior-predictive checks; reliability diagrams for 1X2 and over/under; are 40%-favourites right ~40% of the time? This is how to *measure* (not assume) whether favourites are over-rated in the expanded field.
2. **Strength-of-schedule / confederation effects** — add a confederation random effect or opponent-strength term; the single biggest lever for the newcomer-bias concern.
3. **Recency weighting / in-tournament updating** — weight recent matches up, or refit as 2026 results arrive. In-tournament games are played against the *actual* field, sidestepping qualifying-schedule bias — the strongest signal once the sample grows.
4. **Dixon-Coles / bivariate Poisson** — correct the low-score independence assumption.
5. **Backtesting** — replay 2018/2022 World Cups to benchmark log-loss/Brier against bookmaker odds and simpler baselines.

---

## 12. Reproducibility

Pipeline (each stage is a thin script over `src/wc2026/`):

| Stage | Command | Output |
|---|---|---|
| Real squads + features | `scripts/05_extract_real_players.py` | per-team prior, semantic profiles |
| Fit on real results | `scripts/06_fit_real.py` | posterior, strength table |
| Elo | `scripts/10_elo.py` | Elo ratings + Bayesian comparison |
| Predict a match (goals) | `scripts/12_predict_match.py --home X --away Y` | scoreline forecast |
| LLM judge a fixture | `scripts/11_llm_judge.py --a X --b Y` | judged verdict (or Elo fallback) |
| Simulate tournament | `scripts/04_simulate_tournament.py` | round-by-round probabilities |

All stochastic steps are seeded; the model fits in seconds (586 matches, 48 teams). Tests (`pytest`) cover data shapes, features, a tiny end-to-end fit, Elo, and the judge fallback.

---

## 13. References

- Match data: martj42/international_results (GitHub).
- Player data: FIFA complete player dataset (sofifa schema).
- Modelling lineage: Maher (1982) independent-Poisson; Dixon & Coles (1997) low-score correction; Baio & Blangiardo (2010) hierarchical Bayesian football model; World Football Elo Ratings.
- Scouting/sentiment: ESPN, Sports Illustrated, NPR, Wikipedia (see `data/scouting.py` for per-claim citations).
