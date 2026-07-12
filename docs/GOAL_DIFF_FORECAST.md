# Goal-difference forecast (Gaussian model)

_A simple Bayesian model of the **signed goal difference** (home - away): `goal_diff ~ Normal(mu, sigma)`, `mu = home_adv + strength[home] - strength[away]`, with a player-informed prior on strength. Refit daily on the latest results. Fit on **656 matches** through 2026-07-12._

_Player-data weight `beta_prior` = **0.69** (how much the model leans on squad ratings vs. results).

## Next games — predicted margin & outcome

_No upcoming fixtures in the feed right now._


## Team strength (posterior mean, top 12)

| # | Team | strength |
|--:|---|--:|
| 1 | France | +1.40 |
| 2 | Portugal | +1.32 |
| 3 | Spain | +1.23 |
| 4 | Argentina | +1.11 |
| 5 | Brazil | +1.09 |
| 6 | Germany | +0.99 |
| 7 | Belgium | +0.97 |
| 8 | Colombia | +0.89 |
| 9 | England | +0.85 |
| 10 | Netherlands | +0.77 |
| 11 | Croatia | +0.67 |
| 12 | Austria | +0.66 |

## Method

- **Target:** the signed goal difference — its sign is the result (negative = away won), modelled with a **Gaussian**.
- **Strength prior:** `strength = beta_prior * prior_strength + residual`; `prior_strength` is the squad rating built from player attributes, and `beta_prior` is learned. See [notebooks/goal_difference_gaussian.ipynb](../notebooks/goal_difference_gaussian.ipynb) for the full teaching walkthrough.
- **Simpler cousin** of the production Poisson scoreline model ([CHAMPION_TRACKER.md](CHAMPION_TRACKER.md)); it forecasts the *margin* rather than full scorelines.

_Updated 2026-07-12 by the daily tracker._