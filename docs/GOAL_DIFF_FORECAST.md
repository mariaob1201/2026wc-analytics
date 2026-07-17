# Goal-difference forecast (Gaussian model)

_A simple Bayesian model of the **signed goal difference** (home - away): `goal_diff ~ Normal(mu, sigma)`, `mu = home_adv + strength[home] - strength[away]`, with a player-informed prior on strength. Refit daily on the latest results. Fit on **660 matches** through 2026-07-17._

_Player-data weight `beta_prior` = **0.70** (how much the model leans on squad ratings vs. results).

## Next games — predicted margin & outcome

_`E[margin]` = expected goal difference (sign = favourite). Probabilities are from the posterior-predictive margin._

| Date | Fixture | E[margin] | P(home) | P(draw) | P(away) |
|---|---|--:|--:|--:|--:|
| 2026-07-18 | France v England | +0.48 | 49% | 23% | 28% |
| 2026-07-19 | Spain v Argentina | +0.09 | 40% | 23% | 37% |

## Team strength (posterior mean, top 12)

| # | Team | strength |
|--:|---|--:|
| 1 | France | +1.35 |
| 2 | Portugal | +1.33 |
| 3 | Spain | +1.28 |
| 4 | Argentina | +1.16 |
| 5 | Brazil | +1.09 |
| 6 | Germany | +0.99 |
| 7 | Belgium | +0.97 |
| 8 | Colombia | +0.89 |
| 9 | England | +0.85 |
| 10 | Netherlands | +0.78 |
| 11 | Croatia | +0.67 |
| 12 | Austria | +0.65 |

## Method

- **Target:** the signed goal difference — its sign is the result (negative = away won), modelled with a **Gaussian**.
- **Strength prior:** `strength = beta_prior * prior_strength + residual`; `prior_strength` is the squad rating built from player attributes, and `beta_prior` is learned. See [notebooks/goal_difference_gaussian.ipynb](../notebooks/goal_difference_gaussian.ipynb) for the full teaching walkthrough.
- **Simpler cousin** of the production Poisson scoreline model ([CHAMPION_TRACKER.md](CHAMPION_TRACKER.md)); it forecasts the *margin* rather than full scorelines.

_Updated 2026-07-17 by the daily tracker._