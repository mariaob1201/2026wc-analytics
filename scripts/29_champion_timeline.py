"""Stage 29: champion-odds TIMELINE — how title probabilities moved.

The champion tracker is a snapshot; this is the movie. The x-axis is the number
of World Cup matches PLAYED (not an abstract t=1,2,3...), the y-axis is each
team's probability of winning the tournament, and every line shows a contender
rising or fading as results came in.

Honest, no look-ahead: at each checkpoint we use Elo updated through ONLY the
games played by then, and condition the simulation on exactly those results. So
the odds at "20 matches played" reflect what was knowable after 20 matches.

    python scripts/29_champion_timeline.py

Writes data/processed/champion_timeline.csv and artifacts/champion_timeline.png.
"""

import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, ensure_dirs
from wc2026.config import today as _today
from wc2026.data.sources import build_real_matches, wc2026_matches
from wc2026.data.teams import TEAMS, by_group
from wc2026.models.elo import BASE_RATING, HFA, _step
from wc2026.models.elo_sim import simulate_champion
from wc2026.viz.plots import plot_champion_timeline

TODAY = _today()
TOURNAMENT_START = "2026-06-11"
N_SIMS = 4000   # per checkpoint; many checkpoints, so keep it brisk


def main() -> None:
    ensure_dirs()
    groups = {g: [t.name for t in ts] for g, ts in by_group().items()}

    # Seed Elo on pre-tournament history, then we walk WC games chronologically.
    history = build_real_matches(start="2022-01-01", end="2026-06-10")
    ratings, games = {}, {}
    for m in history.sort_values("date").itertuples():
        _step(ratings, games, m, hfa=HFA)

    def current_elo() -> dict:
        return {t.name: round(ratings.get(t.name, BASE_RATING), 1) for t in TEAMS}

    wc = build_real_matches(start=TOURNAMENT_START, end=TODAY).copy()
    wc["date"] = pd.to_datetime(wc["date"])
    wc = wc.sort_values("date")
    # Canonical-name played results, accumulated as we walk.
    wc_named = wc2026_matches()
    scored = wc_named[wc_named["home_score"].notna() & (wc_named["date"] <= TODAY)]
    by_date = {d: g for d, g in scored.groupby(scored["date"].dt.date)}

    rows = []
    # Checkpoint 0: pre-tournament (no games played).
    sim = simulate_champion(current_elo(), groups, played={}, n_sims=N_SIMS)
    for r in sim.itertuples():
        rows.append({"games_played": 0, "date": "pre", "team": r.team,
                     "p_champion": r.p_champion})

    played: dict = {}
    n_games = 0
    # Walk match dates in order; checkpoint after each matchday.
    for day in sorted(by_date):
        # Update Elo with that day's games (chronological, no leakage).
        day_rows = wc[wc["date"].dt.date == day]
        for m in day_rows.itertuples():
            _step(ratings, games, m, hfa=HFA)
        # Accumulate canonical played results up to and including this day.
        for r in by_date[day].itertuples():
            played[(r.home, r.away)] = (int(r.home_score), int(r.away_score))
            n_games += 1
        sim = simulate_champion(current_elo(), groups, played=played, n_sims=N_SIMS)
        for r in sim.itertuples():
            rows.append({"games_played": n_games, "date": str(day),
                         "team": r.team, "p_champion": r.p_champion})

    timeline = pd.DataFrame(rows)
    timeline.to_csv(PROCESSED / "champion_timeline.csv", index=False)
    plot_champion_timeline(timeline, ARTIFACTS / "champion_timeline.png")

    last = timeline["games_played"].max()
    leaders = (timeline[timeline["games_played"] == last]
               .nlargest(8, "p_champion"))
    print(f"Timeline over {last} games played, "
          f"{timeline['games_played'].nunique()} checkpoints.")
    print("\nCurrent title odds (latest checkpoint):")
    print(leaders[["team", "p_champion"]]
          .assign(p_champion=(100 * leaders["p_champion"]).round(1))
          .to_string(index=False))
    print(f"\nsaved -> {PROCESSED/'champion_timeline.csv'}, "
          f"{ARTIFACTS/'champion_timeline.png'}")


if __name__ == "__main__":
    main()
