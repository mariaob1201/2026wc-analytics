# One Number to Predict a Football Match: A Bayesian Story

### I stopped predicting scores and started predicting the *margin* — a signed goal difference — and the model got simpler, more honest, and easier to explain. Here's the whole build.

Most match predictors try to guess a scoreline: 2–1, 1–0, the works. I went the other way and asked the smallest possible question that still contains the answer:

> **What is the goal difference — home goals minus away goals — and which side of zero does it land on?**

That one signed number, `goal_diff = home_goals − away_goals`, already tells you everything you care about: **positive means the home team won, negative means the away team won, zero is a draw.** The *sign is the result*, and the *size is the dominance.* This is the story of building a small Bayesian model around that idea — the data, the attributes, the formulation, the fit, and what it actually predicted.

---

## Act 1 — The data, and turning players into a number

Every model is only as good as what you feed it, so the first job was boring and important: **collect clean, public, reproducible data.**

**Match results.** I pulled every men's international since 1872 from an open dataset that updates within days of each game, then filtered to a recent window (2022 → today) and to the 48 World Cup teams — **656 matches**. Recent enough to reflect current squads, big enough to learn from. From each match I computed the one thing the model needs: the goal difference.

The distribution of that target is the first plot worth staring at. It's a tidy bell shape, roughly symmetric, centred a hair above zero — that little rightward nudge is **home advantage**, visible in the raw data before any model touches it. And a symmetric, bell-shaped target is a strong hint about which likelihood to use later (spoiler: a Gaussian).

**Player attributes — the interesting part.** Results tell you who *won*; they don't tell you how *good the squad* is. So I brought in a second source: per-player attributes (pace, shooting, passing, dribbling, defending, physicality, plus age and caps), joined to each nation's real, current roster. Those attributes get rolled up — the best 16 players by rating, weighted for skill, seniority, and an *age × role* twist (youth counts more for attacking pace, experience counts more for defensive solidity) — into a **single number per team: `prior_strength`.**

That's the key move. Twenty-six players and dozens of attributes collapse into *one standardized covariate* that says, before a single ball is kicked, *"this squad looks about this good."* Whether the model should believe it is a question I let the data answer — which brings us to the model.

---

## Act 2 — The model, as a generative story

I like to write a model as a little story about *how nature makes the number.*

Give every team one hidden value, its **strength** `s`. When home team *h* plays away team *a*, the *expected* margin is the strength gap plus a home bonus, and the *actual* margin scatters around that expectation with some noise. In two lines:

```
goal_diff ~ Normal(mu, sigma)
mu        = home_adv + strength[home] − strength[away]
```

- `mu` is the **center** of the bell curve — the expected margin. Only the *difference* of strengths appears, which is exactly right for a *goal difference*.
- `sigma` is the **noise** — how much a single match bounces around its expectation (football is noisy; underdogs win).
- `home_adv` is the small edge for playing at home.

And here's how the player data enters — not as a hard input, but as a **prior on strength**:

```
strength = beta_prior · prior_strength + tau · s_raw
```

Read that as two ingredients. `beta_prior · prior_strength` is the **squad-quality belief** — where a team *starts*. `tau · s_raw` is a **residual learned purely from results** — the freedom to move *away* from the squad estimate when a team over- or under-performs. The dial `beta_prior` decides **how much to trust the player data at all** — and, crucially, *it's learned, not assumed.* If squads had no predictive value, the fit would shrink it to zero.

Because it's **Bayesian**, nothing is a single smug number. Every strength, the home edge, the noise — each comes out as a *distribution*, and that uncertainty flows all the way through to the final match probabilities.

---

## Act 3 — Fitting it (and trusting the fit)

I fit the model with MCMC (the NUTS sampler in PyMC) — four chains exploring the posterior in parallel. On a model this clean it takes seconds.

But *sampling* isn't *believing.* Before reading a single result I checked the diagnostics: **R-hat ≈ 1.00** (the chains agree) and no divergences. Only then did the parameters mean anything. Two of them told a story on their own:

- **`home_adv` ≈ 0.30** — home advantage is worth about a third of a goal. Small, real, exactly the rightward nudge we saw in the raw histogram.
- **`sigma` ≈ 1.6** — the honest width of football. Even when the model is confident about *who's better*, a single match scatters by more than a goal. That number is why a "55% favourite" is not a sure thing.

And the headline dial:

- **`beta_prior` ≈ 0.69**, with a 94% credible interval comfortably above zero.

That's a genuine finding, not a setting. **The squad ratings carry real signal for the goal difference — and the model chose to lean on them by about 0.69.** The player data earned its place; the model didn't have to use it, and it did.

---

## Act 4 — The results

**Team strengths.** Ranked by learned strength, the top of the board reads like a sensible power ranking — France, Portugal, Spain, Argentina, Brazil. Nothing absurd, which is its own kind of validation.

**The most instructive plot** is strength-from-player-data versus strength-the-model-learned. Teams sit *near* the diagonal — the squad prior and the results mostly agree — but not *on* it. And where they diverge is the whole point:

> **Germany had the single highest player-data prior — the best squad on paper — but its results pulled it down the learned ranking. France started lower on paper and climbed above it.**

That gap *is* the model working. **Player data sets where a team starts; the match record decides where it ends up.** The correlation between the two is about **0.92** — strong, but deliberately not 1.0. A model that just parroted FIFA ratings would be useless; a model that ignored them would be naive. This one does the Bayesian thing in between.

**The forecasts.** For any upcoming fixture, the model produces a whole *distribution* of possible margins; its sign gives win/draw/loss. Two real examples from the day I write this:

| Fixture | Expected margin | P(home) | P(draw) | P(away) |
|---|---|---|---|---|
| Norway vs England | −0.54 | 25% | 25% | **50%** |
| Argentina vs Switzerland | +0.67 | **55%** | 21% | 25% |

Read the first row as *"England expected to win by about half a goal, and they take it 50% of the time — but it's an even-ish game."* The second is a clearer Argentina lean. Note what the model refuses to do: **it never pretends.** A 55% favourite loses plenty, and the model says so out loud with its probabilities instead of just naming a winner.

**And it doesn't need me.** The whole thing runs on a schedule: every day it pulls the newest results, refits, re-forecasts the next games, and publishes the table — so the numbers above aren't a one-time screenshot, they refresh themselves as the tournament unfolds.

---

## Why a "simpler" model was the right call

I could have modelled full scorelines with a Poisson (I did, elsewhere). But targeting the **margin** with a **Gaussian** bought three things I didn't want to give up: it models the *result* directly, it stays a clean linear model you can read line-by-line, and it made the player-data mechanism transparent — you can literally see `beta_prior` decide how much the squads matter.

The lesson I keep relearning: **the smallest model that still answers the question is usually the one you can trust — and explain.** One signed number, a bell curve, and a prior the data is allowed to overrule. That's the whole thing.

*The code, the daily forecast, and a step-by-step teaching notebook are all public:* [github.com/mariaob1201/2026-world-cup-analytics](https://github.com/mariaob1201/2026-world-cup-analytics)

---

> **Publishing notes (delete before posting):**
> - Suggested hero image: the **prior-vs-learned strength scatter** (Section 8 of the notebook) — it visually tells the "squads set the start, results decide the finish" story. The goal-difference histogram (Section 2) is a strong alternative opener.
> - Numbers reflect an in-progress tournament — illustrative, not betting advice.
> - Medium doesn't render Markdown on paste: paste into the editor, then promote the `##` lines to headings and re-apply **bold**/*italics*.
