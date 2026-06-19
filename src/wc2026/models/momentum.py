"""Match-level momentum / sentiment nudges for the goals model.

The brief: let *current* signals (recent results, and where available public
sentiment) adjust a fixture's predicted goals — not just sit in a side report.

How (and why it's deliberately small)
-------------------------------------
We compute a per-team **form** signal: a recency-weighted average goal
difference over recent matches, standardized across the field, then scaled and
**clipped** to a small log-rate shift. A hot team's attack rate is nudged up a
little; a cold team's down. The cap (``MAX_SHIFT``) keeps this a nudge, not an
override — form and sentiment are weak signals next to fitted strength, so they
should refine, never dominate.

A ``sentiment`` hook adds an optional tiny shift for teams with scouted
public-source sentiment (e.g. Mexico). Default 0 for everyone else, so the
adjustment is purely form-based until per-team sentiment is supplied.
"""

from __future__ import annotations

import math

import pandas as pd

from ..data.teams import TEAMS

MAX_SHIFT = 0.18        # cap on the log-rate nudge (~ ±20% on the goal rate)
FORM_SCALE = 0.11       # how strongly standardized form maps to a shift
HALF_LIFE_DAYS = 120.0  # recency half-life for weighting matches

# Scouted public-sentiment → a tiny attacking nudge. Intentionally minimal.
SENTIMENT_SHIFT = {
    "strongly positive": 0.05, "leaning positive": 0.03,
    "tempered / cautiously positive": 0.02, "euphoric in the street, impatient in the stadium": 0.02,
    "mixed": 0.0, "leaning negative": -0.03, "strongly negative": -0.05,
}


def momentum_label(shift: float) -> str:
    """Human label for a form/sentiment shift."""
    if shift >= 0.12:
        return "red-hot"
    if shift >= 0.05:
        return "rising"
    if shift <= -0.12:
        return "cold"
    if shift <= -0.05:
        return "dipping"
    return "steady"


def match_sentiment(home: str, away: str, shifts: dict) -> dict:
    """Per-fixture momentum/sentiment readout: each side's label + the edge."""
    sh, sa = shifts.get(home, 0.0), shifts.get(away, 0.0)
    edge = home if sh - sa > 0.04 else away if sa - sh > 0.04 else "even"
    return {
        "home_form": momentum_label(sh), "home_shift": round(sh, 2),
        "away_form": momentum_label(sa), "away_shift": round(sa, 2),
        "momentum_edge": edge,
    }


def _days(a, b) -> float:
    return abs((pd.Timestamp(a) - pd.Timestamp(b)).days)


def form_shifts(matches: pd.DataFrame, asof: str, lookback_days: int = 540) -> dict:
    """Per-team recency-weighted form, standardized and clipped to a log shift.

    ``matches`` needs date/home_team/away_team/home_goals/away_goals. Only games
    within ``lookback_days`` before ``asof`` count, weighted by recency.
    """
    asof = pd.Timestamp(asof)
    df = matches.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df[(df["date"] <= asof) & (df["date"] >= asof - pd.Timedelta(days=lookback_days))]

    wsum: dict[str, float] = {}
    gdsum: dict[str, float] = {}
    for r in df.itertuples():
        w = 0.5 ** (_days(asof, r.date) / HALF_LIFE_DAYS)
        gd = int(r.home_goals) - int(r.away_goals)
        for team, sign in ((r.home_team, 1), (r.away_team, -1)):
            wsum[team] = wsum.get(team, 0.0) + w
            gdsum[team] = gdsum.get(team, 0.0) + w * sign * gd

    # Weighted mean GD per team, then z-score across our 48.
    avg = {t: (gdsum.get(t, 0.0) / wsum[t]) for t in wsum if wsum[t] > 0}
    names = [t.name for t in TEAMS]
    vals = [avg.get(n, 0.0) for n in names]
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    sd = math.sqrt(var) or 1.0

    shifts = {}
    for n, v in zip(names, vals):
        z = (v - mean) / sd
        shifts[n] = max(-MAX_SHIFT, min(MAX_SHIFT, FORM_SCALE * z))
    return shifts


def sentiment_shifts(scouted: dict[str, str] | None = None) -> dict:
    """Optional per-team sentiment nudge from scouted public-source mood."""
    out = {}
    for team, mood in (scouted or {}).items():
        out[team] = SENTIMENT_SHIFT.get(mood, 0.0)
    return out


def combined_shifts(matches: pd.DataFrame, asof: str,
                    scouted: dict[str, str] | None = None) -> dict:
    """Form + sentiment, clipped to MAX_SHIFT."""
    form = form_shifts(matches, asof)
    sent = sentiment_shifts(scouted)
    out = {}
    for t in set(form) | set(sent):
        v = form.get(t, 0.0) + sent.get(t, 0.0)
        out[t] = max(-MAX_SHIFT, min(MAX_SHIFT, v))
    return out
