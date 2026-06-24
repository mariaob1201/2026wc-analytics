# I Built a Bayesian World Cup 2026 Predictor That Grades Itself Every Day

### Predicting goals, not winners — and keeping an honest scoreboard of how often it's right.

Most World Cup prediction posts show you a bracket and move on. I wanted to build something that does the harder, more honest thing: forecast every match, write the prediction down *before* kickoff, and then score it against what actually happened — automatically, every day, in public.

So I built a hierarchical Bayesian model for the 2026 World Cup. Here's what I learned, including a few results that surprised me.

## Goals first, winners second

The core idea is that **goals are the primitive, not winners**. Each team gets a latent "attack" and "defence" rating; for any fixture those combine into a full distribution over scorelines (how likely 1–0, 2–1, 1–1, and so on). Win/draw/loss probabilities and title odds are just sums over that scoreline distribution.

Rating teams *individually* — rather than rating matchups — means the model can predict games that have never been played, which matters a lot in a 48-team tournament full of fixtures that don't exist until the bracket fills in. And because it's Bayesian, every rating carries uncertainty, which flows all the way through to the final probabilities instead of pretending one number is exact.

## The plot I find most interesting: is it actually honest?

![Calibration curve](../artifacts/calibration.png)

This is a **calibration (reliability) curve** from an out-of-sample backtest — the model was trained only on pre-tournament data, then asked to predict matches it had never seen. The x-axis is what the model predicted; the y-axis is what actually happened. Points on the diagonal mean the probabilities are *honest*: events it called at 40% happened about 40% of the time.

I like this plot more than any bracket, because it's the one that can prove the model wrong. It hugs the diagonal — which means the forecasts are calibrated, not just confident.

## A few findings that surprised me

**Expected goals beat actual goals.** When I backtested on the 2018 and 2022 World Cups (using real shot-level xG from StatsBomb), a model fit on *expected* goals predicted future results better than one fit on actual goals. Goals are noisy; xG — the quality of chances created — is a steadier signal of who's really better.

**Recent form helps, but only the right kind.** Conditioning predictions on a team's recent shots-on-target improved accuracy. Conditioning on recent *results* (goals) made it slightly worse. In other words: *how* a team has been playing carries signal; recent scorelines are mostly noise.

**Two reasonable models can strongly disagree.** A pooled Bayesian rating and a recency-weighted Elo often diverge on a team's level (one says mid-table, the other says red-hot). Instead of hiding that, I show both — the gap is itself information about how uncertain a pick is.

## It runs itself

A GitHub Action runs daily: it pulls the latest results, refits, forecasts the next round, fills in the ground truth for matches just played, and commits a refreshed forecast log. So the "how accurate is it?" number isn't a one-time claim — it updates on its own as the tournament unfolds.

## The honest caveats

The in-tournament sample is tiny (a couple of matchdays), so live accuracy figures are directional, not definitive — the 2018/2022 backtests are the trustworthy part. Live expected-goals data for 2026 isn't publicly available yet, so the live model runs on goals while xG stays validated on past tournaments. And the fancier features I tried — spatial play-style, social sentiment — barely moved the needle once team strength was already in the model. I kept them, clearly labelled as exploratory, because the discipline of the whole project is: **a feature only earns its place if it improves the score.**

If you want to dig in — the code, the methodology write-up, and the live forecast log are all on GitHub: [github.com/mariaob1201/2026-world-cup-analytics](https://github.com/mariaob1201/2026-world-cup-analytics)

---

> **Publishing notes (delete before posting):**
> - Upload `artifacts/calibration.png` where the image tag is.
> - Medium doesn't render Markdown on paste — paste into the Medium editor, then promote the `##` lines to headings and re-apply bold.
> - Numbers are illustrative of an in-progress tournament, not betting advice.
