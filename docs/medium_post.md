# I Built a World Cup Predictor That Grades Itself Every Day — and Shows Its Work

### Most prediction posts hand you a bracket and disappear. I wanted one that has to face the scoreboard every morning.

Here's the thing that always bugged me about World Cup predictions: nobody ever comes back. Someone posts a confident bracket in June, the tournament does whatever it wants, and by July the prediction has quietly evaporated. There's no reckoning. No "here's what I said, here's what happened, here's how wrong I was."

So I built the opposite of that. A model that forecasts every match, writes the prediction down *before* kickoff, and then — automatically, every single day, out in the open — checks itself against reality. No hiding the misses. The whole point is the misses.

This is the story of what it does, what it got right, and the couple of things it taught me that I genuinely didn't expect.

## Start with goals, and the winners take care of themselves

The first decision was the most important one, and it sounds almost too simple: **predict goals, not winners.**

Every team carries two hidden numbers — an *attack* and a *defence*. Drop any two teams together and those numbers produce a full spread of scorelines: how likely 1–0 is, and 2–1, and the dreaded 0–0. Everything else I care about — who wins, who advances, who lifts the trophy — is just that scoreline spread, added up.

It sounds like a detour. It's actually the shortcut. Because I'm rating *teams* instead of *matchups*, the model can price a game that has never been played — Morocco vs. Uzbekistan in a knockout round that doesn't exist yet — which, in a 48-team tournament that invents new fixtures as the bracket fills in, turns out to be the whole ballgame. And because it's Bayesian, no rating is a single smug number; each one drags its uncertainty along behind it, all the way through to the final odds. The model is allowed to say "I think, but I'm not sure" — and it does, constantly.

## The plot I'd defend in a knife fight

![Calibration curve](../artifacts/calibration.png)

If I could only keep one chart, it's this one — and not because it's pretty. It's the one that can *catch me lying.*

It's a calibration curve. I trained the model only on pre-tournament data, then made it predict matches it had never seen, and plotted what it *said* would happen against what *actually* did. The diagonal is the line of honesty: if the model calls a bunch of things at 40%, those things should happen about 40% of the time. Lands on the line? Honest. Floats above or below it? Overconfident or shy.

Mine hugs the diagonal. I find that more satisfying than any bracket I could draw, because a bracket only ever flatters you. This plot is the one holding the knife.

## The plot that's just plain fun to watch

![Title odds over the tournament](../artifacts/champion_timeline.png)

If the calibration curve is conscience, this one is theatre.

Every line is a contender's chance of winning the whole thing, traced across the matches as they're played. And you can *watch the race breathe.* A favourite stalls after a limp draw and the line sags. A dark horse lands a statement win and spikes. Two heavyweights swap the lead like it's the closing laps of something. I'll admit I sat and stared at it longer than I'd like to confess — there's a moment where Argentina's line lurches upward and another where Brazil comes climbing back from nowhere late, and the chart just *feels* like the tournament.

But here's the part I care about: there's no cheating in it. At every point along that x-axis, the odds know only what had actually happened by then — the model never sneaks a look at games that hadn't been played. So the wobbles are honest wobbles. That's truly how nervous you should have been at each moment, not a tidy story told backwards from a result you already knew.

And it's powered by the *simple* engine on purpose — a recency-weighted Elo feeding a fast tournament simulation — because this thing has to re-run after every matchday without melting the laptop. It's the lightweight sibling of the heavy Bayesian model, and keeping both around means each one keeps the other honest.

## Three things the model taught me

Once it was running, it started arguing with my intuitions. Three times it won.

**Expected goals beat actual goals.** I backtested on the 2018 and 2022 World Cups using real shot-by-shot xG, and the model fed *expected* goals out-predicted the one fed *real* goals. It stung a little — actual goals are the literal truth of what happened — but that's exactly the trap. Goals are noisy; the *quality of the chances* you create is the steadier tell of who's actually better. The scoreboard lies more than the shot chart does.

**Form helps — but only the right kind of form.** Feeding the model a team's recent shots-on-target made it sharper. Feeding it recent *results* made it worse. So "they're playing well" carries real signal, while "they've been winning" is mostly luck wearing a convincing disguise. I had those two backwards going in.

**Two honest models can flat-out disagree.** My pooled Bayesian rating and my recency-weighted Elo regularly clash on the same team — one shrugs "mid-table," the other insists "red-hot." The lazy move is to pick the one that agrees with me and bury the other. I show both. The size of the gap between them *is* the information: it's the model telling you how shaky the pick really is.

## It doesn't need me anymore

The part I'm quietly proudest of: I'm not in the loop.

A GitHub Action wakes up every day, pulls the latest results, refits the model, forecasts the next round, fills in the ground truth for the games that just finished, refreshes the player and team tables, redraws every chart, and commits the lot. The "how accurate is it?" number isn't a one-time boast I get to frame and forget — it re-grades itself in public while I'm asleep, and it'll keep doing that right through the final.

## Where I'm keeping myself honest

A model that grades itself only earns the bragging rights if it admits where it's thin, so:

The in-tournament sample is still small — a handful of matchdays — so the *live* accuracy number is a direction, not a verdict; the 2018/2022 backtests are the part you should actually trust. Live xG for 2026 isn't public yet, so the day-to-day model runs on goals while xG stays validated on the old tournaments. And the fancy stuff I was sure would be magic — spatial play-style, social-media sentiment — barely twitched the needle once plain team strength was in the room. I kept those features anyway, clearly flagged as experiments, because the one rule the whole project lives by is simple and unsentimental: **a feature only earns its keep if it moves the score.**

That's the rule that turned this from a bracket into something I'm willing to be wrong in front of, every day.

If you want to poke at it — the code, the methodology, the live self-grading log — it's all here: [github.com/mariaob1201/2026-world-cup-analytics](https://github.com/mariaob1201/2026-world-cup-analytics)

---

> **Publishing notes (delete before posting):**
> - Two images: upload `artifacts/calibration.png` and `artifacts/champion_timeline.png` where the tags are. The timeline is the stronger social-preview/hero image.
> - Medium doesn't render Markdown on paste — paste into the editor, then promote the `##` lines to headings and re-apply the **bold**/*italics*.
> - Numbers reflect an in-progress tournament — illustrative, not betting advice.
