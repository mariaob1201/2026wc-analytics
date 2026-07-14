# Goal-difference forecast (Gaussian model)

_A simple Bayesian model of the **signed goal difference** (home - away): `goal_diff ~ Normal(mu, sigma)`, `mu = home_adv + strength[home] - strength[away]`, with a player-informed prior on strength. Refit daily on the latest results. Fit on **658 matches** through 2026-07-14._

_Player-data weight `beta_prior` = **0.70** (how much the model leans on squad ratings vs. results).

## Next games — predicted margin & outcome

_`E[margin]` = expected goal difference (sign = favourite). Probabilities are from the posterior-predictive margin._

| Date | Fixture | E[margin] | P(home) | P(draw) | P(away) |
|---|---|--:|--:|--:|--:|
| 2026-07-14 | France v Spain | +0.15 | 41% | 23% | 35% |
| 2026-07-15 | England v Argentina | -0.30 | 31% | 23% | 46% |

## Team strength (posterior mean, top 12)

| # | Team | strength |
|--:|---|--:|
| 1 | France | +1.40 |
| 2 | Portugal | +1.33 |
| 3 | Spain | +1.23 |
| 4 | Argentina | +1.14 |
| 5 | Brazil | +1.08 |
| 6 | Germany | +0.98 |
| 7 | Belgium | +0.96 |
| 8 | Colombia | +0.89 |
| 9 | England | +0.86 |
| 10 | Netherlands | +0.77 |
| 11 | Croatia | +0.67 |
| 12 | Austria | +0.66 |

## Method

- **Target:** the signed goal difference — its sign is the result (negative = away won), modelled with a **Gaussian**.
- **Strength prior:** `strength = beta_prior * prior_strength + residual`; `prior_strength` is the squad rating built from player attributes, and `beta_prior` is learned. See [notebooks/goal_difference_gaussian.ipynb](../notebooks/goal_difference_gaussian.ipynb) for the full teaching walkthrough.
- **Simpler cousin** of the production Poisson scoreline model ([CHAMPION_TRACKER.md](CHAMPION_TRACKER.md)); it forecasts the *margin* rather than full scorelines.

_Updated 2026-07-14 by the daily tracker._