"""Adapter for per-match advanced stats (xG, possession, shots, SoT).

Contract: produce a tidy table with at least
``date, home_team, away_team, home_xg, away_xg`` (plus possession/shots/SoT when
available). The Bayesian xG model (``build_xg_model``) consumes that.

Sources
-------
* ``load_xg_csv(path)`` — load an xG-labelled table from ANY source you've
  harvested (the model doesn't care where the xG came from). This is the
  reliable path and what the backtest uses.
* ``fetch_fbref(comp, season)`` — best-effort pull via the ``soccerdata`` FBref
  scraper. **Heavy and flaky**: it drives a headless browser, is rate-limited,
  and the competition *schedule* does NOT expose xG (you must pull match-level
  team stats, which is slow). Treat this as an occasional harvester, not a
  per-run dependency — and prefer StatsBomb open data for bulk historical xG.

Honest note: a large-sample xG-vs-goals backtest needs xG for hundreds of
*training* matches. FBref scraping at that volume is impractical here, so the
backtest (stage 21) runs against a cached xG CSV you provide; the machinery is
verified on synthetic data in the tests.
"""

from __future__ import annotations

import pandas as pd

from ..config import RAW

REQUIRED = ["date", "home_team", "away_team", "home_xg", "away_xg"]


def load_xg_csv(path=None) -> pd.DataFrame:
    """Load a harvested xG table (default data/raw/xg_matches.csv)."""
    path = path or (RAW / "xg_matches.csv")
    df = pd.read_csv(path, parse_dates=["date"])
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"xG table missing columns: {missing}; need {REQUIRED}")
    return df


def fetch_fbref(comp: str = "INT-World Cup", season: str = "2022") -> pd.DataFrame:
    """Best-effort FBref pull of per-match team stats incl. xG (needs soccerdata).

    Raises a clear error if xG isn't available from the scrape (e.g. the
    competition schedule has no xG column and match-level stats can't be
    assembled) so the caller can fall back to ``load_xg_csv``.
    """
    try:
        import soccerdata as sd
    except ImportError as e:
        raise ImportError("pip install soccerdata to use fetch_fbref") from e

    fb = sd.FBref(leagues=comp, seasons=season)
    stats = fb.read_team_match_stats(stat_type="schedule")  # may include xg cols
    stats = stats.reset_index()
    cols = {c.lower(): c for c in stats.columns}
    if "xg" not in [c.lower() for c in stats.columns]:
        raise RuntimeError(
            "FBref scrape returned no xG column for this competition. Harvest xG "
            "another way (StatsBomb open data, or FBref match reports) and save it "
            "as data/raw/xg_matches.csv with columns: " + ", ".join(REQUIRED))
    # Normalisation left to the caller once a real xG column is confirmed.
    return stats
