# Presenter's script — WC 2026 Data Pipeline & Model deck

Speaker notes for [`data_pipeline_slides.pptx`](data_pipeline_slides.pptx) /
[`data_pipeline_slides.tex`](data_pipeline_slides.tex). A story arc to
internalize, not slide-reading. The spine of the whole talk:

> **"We predict goals, grade ourselves in public every day, and only keep what
> beats the scoreboard."**

Everything ladders back to that.

## The three-act arc

1. **Act I — Trust the inputs** (Collection → Organization): messy public data,
   made clean and canonical. *"Garbage in is the real risk; here's how we avoid it."*
2. **Act II — From players to a prior** (Features → Aggregation): raw attributes
   become one honest number per team. *"Squad quality becomes a belief the data
   can override."*
3. **Act III — From goals to a champion, honestly** (Modeling → Results): the
   model, and proof it works. *"Here's how we know it's not just confident —
   it's calibrated."*

## Opening (30–45 sec) — set the tension

Don't start with the model. Start with the gripe:

> "Most World Cup predictions post a bracket in June and vanish. There's never a
> reckoning — nobody comes back to say *here's what I predicted and here's how
> wrong I was*. This project is the opposite: it forecasts every match, writes it
> down before kickoff, and grades itself automatically, in public, every day.
> Let me show you how the data becomes a prediction — and how we keep it honest."

## Act I — Collection & Organization

- **Pipeline-at-a-glance:** don't read the diagram. *"Four public sources on the
  left, two published tables on the right. Keyless, cached, re-run daily. Hold
  this shape in your head — everything else is detail."*
- **Design principles:** land one idea — *"Every stage has a fixed schema, so I
  can swap a source without touching anything downstream."*
- **Four collection slides:** spend real time on **(1) results** and **(3)
  squads**, skim (2) and (4).
  - Results → land the **TTL + offline fallback**: *"this is the fix for a real
    bug — the forecast was lagging reality because the cache never refreshed."*
  - Squads → *"we parse the live Wikipedia roster, which is why no retired
    players sneak in"* (the Ramos story, for a laugh).
- **Canonicalization:** *"The same country is spelled three different ways across
  three sources. If you don't normalize names, every join silently drops rows."*
- **Transition:** *"So now we have clean matches and clean rosters. But a roster
  is just names — how does player quality become something a model can use?"*

## Act II — Features & Aggregation

- **Per-player features:** keep light — *"standardized so no single scale
  dominates."*
- **Age × role weighting** (linger — this is a differentiator): *"Youth and pace:
  a 20-year-old's speed counts more. Experience and defending: a 32-year-old's
  positioning counts more. The same rating means different things by age and
  role."*
- **Aggregation → prior_strength** (the payoff, point at the boxed formula):
  *"All of that collapses into one number per team — its prior strength. And this
  is a prior, not a verdict. The match data is allowed to overrule it."* Say it
  slowly; it's the hinge into the model.

## Act III — Modeling & Results (the heart)

- **Goals as the primitive** (conceptual keystone): *"We never predict winners
  directly. We predict goals — attack and defence give a full distribution over
  scorelines. Winners, draws, the champion are just arithmetic on that
  distribution."* Then the why: *"Rating teams individually lets us price a game
  that has never been played — most matchups in a 48-team bracket don't exist yet."*
- **Player prior & pooling:** *"β_prior is learned — the model decides how much to
  trust FIFA ratings; it landed near 0.53."* And: *"partial pooling is how
  debutants get sensible, uncertain estimates instead of overconfident nonsense."*
- **Inference & the funnel** (the credibility slide — tell it as a war story):
  *"First version wouldn't converge — a classic funnel, R-hat 1.6, effective
  sample size in single digits, and cranking up the sampler made it worse. The
  fix is the textbook non-centered reparameterization: R-hat back to 1.0,
  effective samples up a hundredfold."*
- **From goals to winners:** *"Two layers. Per match: scoreline matrix per
  posterior draw, averaged — that's your 1X2. Whole tournament: simulate the real
  bracket thousands of times, holding played games fixed. The headline
  probability already carries our uncertainty about strengths."*
- **Cross-checks:** *"We also run a recency Elo and an LLM judge. When they
  disagree with the Bayesian model — Mexico 7th on Elo, 20th on the pooled model
  — that disagreement is the signal: it flags the teams the data is least sure
  about."*
- **Results — the scoreboard** (win the room, point at the table): *"Out-of-
  sample, trained only on data before each tournament. Lower is better. The
  Bayesian model beats both Elo and a naive baseline in every one. And the rule
  of the project is on this slide: any new feature has to lower this number to
  ship."*
- **Results — what moved the score** (the surprises make it memorable): *"Three
  findings that argued with my intuition and won. One: expected goals beat actual
  goals — chance quality is less noisy than the scoreboard. Two: recent form
  helps, but only shots on target — recent goals actually hurt. Three: the fancy
  stuff — spatial style, social sentiment — barely moved the needle, so I kept it
  but labelled it exploratory."*

## Closing (20 sec) — return to the spine

> "Clean public data becomes one honest prior per team; a Bayesian goals model
> turns that into scorelines; scorelines become winners and a champion; and every
> day it grades itself against reality in public. Not a bracket you have to trust
> — a system that's willing to be wrong in front of you."

## Q&A prep — the four you'll likely get

- **"Why not just Elo / a neural net?"** → Elo throws away goal margins and
  overfits sparse teams; the hierarchical Poisson keeps margins and pools
  debutants. It's a cross-check, not the core. A net needs far more data and
  won't give calibrated uncertainty.
- **"Isn't your FIFA data stale / the join fuzzy?"** → Yes — FIFA-22 vintage,
  surname join ~70%, flagged per row via `rating_source`. It's a *prior*,
  β_prior≈0.53 tempers it, match data overrides. Upgrade path (exact per-player
  feed) is a schema swap.
- **"Independent Poisson ignores 0-0/1-1 correlation."** → Correct, known
  limitation; Dixon-Coles / bivariate Poisson is the noted next step. Calibration
  is still good, so the effect is second-order here.
- **"2026 numbers — small sample?"** → Absolutely, directional. The 2018/2022
  backtests are the trustworthy evidence; 2026 is the live demonstration.

## Timing

~15 min: Act I 4, Act II 3, Act III 7, Q&A open. **Cut to 5 minutes?** →
pipeline-at-a-glance → goals-as-primitive → the scoreboard. Those three carry the
whole story.
