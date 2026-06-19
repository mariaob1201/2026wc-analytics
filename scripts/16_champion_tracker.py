"""Stage 16: the Champion Tracker — a living, state-aware view.

This is the headline researcher-facing view. It follows the tournament as it
stands and answers two linked questions with the SAME Bayesian goals model:

  1. **Next games:** predicted goals for each upcoming fixture (posterior-
     predictive, with current-form momentum + scouted X/ESPN sentiment).
  2. **The trophy:** each team's probability of winning the World Cup —
     CONDITIONED on the matches already played (completed group games are held
     fixed; only the remaining fixtures and the knockouts are simulated).

Inputs reflect the current state: the posterior is fit on results up to today
(incl. tournament games), the player prior carries squad skill, and momentum
carries form + sentiment. Run after each matchday to refresh the tracker.

    python scripts/16_champion_tracker.py
"""

import arviz as az
import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, ROOT, ensure_dirs
from wc2026.data.scouting import MEXICO_SOCIAL
from wc2026.data.sources import build_real_matches, wc2026_matches
from wc2026.data.teams import HOSTS, TEAMS, by_group
from wc2026.models.bayesian_score import FitResult, predict_match
from wc2026.models.momentum import combined_shifts, momentum_label
from wc2026.models.simulate import simulate_tournament
from wc2026.viz.plots import plot_champion_probs

TODAY = "2026-06-19"
HORIZON = "2026-06-24"
N_SIMS = 6000


def main() -> None:
    ensure_dirs()
    teams = [t.name for t in TEAMS]
    idata = az.from_netcdf(ARTIFACTS / "posterior_real.nc")
    fit = FitResult(idata=idata, teams=teams,
                    team_to_idx={t: i for i, t in enumerate(teams)})
    groups = {g: [t.name for t in ts] for g, ts in by_group().items()}

    wc = wc2026_matches()
    scored = wc["home_score"].notna() & wc["away_score"].notna()
    played_df = wc[(wc["date"] <= TODAY) & scored]
    played = {(r.home, r.away): (int(r.home_score), int(r.away_score))
              for r in played_df.itertuples()}
    upcoming = wc[(wc["date"] > TODAY) & (wc["date"] <= HORIZON)]

    shifts = combined_shifts(build_real_matches(start="2022-01-01", end=TODAY), TODAY,
                             scouted={"Mexico": MEXICO_SOCIAL["net_mood"]})

    # --- 1. Next-game goal forecasts ---
    nxt = []
    for r in upcoming.itertuples():
        neutral = (bool(r.neutral) if "neutral" in wc.columns else True) and r.home not in HOSTS
        p = predict_match(idata, teams, r.home, r.away, neutral=neutral, shifts=shifts)
        nxt.append({"date": str(r.date.date()), "home": r.home, "away": r.away,
                    "xg": f"{p['exp_goals_home']:.1f}-{p['exp_goals_away']:.1f}",
                    "score": p["most_likely_score"],
                    "p_H": p["p_home_win"], "p_D": p["p_draw"], "p_A": p["p_away_win"],
                    "edge": momentum_label(shifts.get(r.home, 0))})
    nxt = pd.DataFrame(nxt)

    # --- 2. Title odds CONDITIONED on current results ---
    fixtures = _round_robin(groups)
    sim = simulate_tournament(fit, fixtures, groups, n_sims=N_SIMS,
                              shifts=shifts, played=played)
    sim.to_csv(PROCESSED / "champion_tracker.csv", index=False)
    plot_champion_probs(sim, ARTIFACTS / "champion_tracker.png")

    # Current group standings (from played games).
    standings = _standings(played_df, groups)

    md = _render(standings, nxt, sim, len(played))
    out = ROOT / "docs" / "CHAMPION_TRACKER.md"
    out.write_text(md)

    print(f"Conditioned on {len(played)} completed matches.")
    print("\nTitle odds (top 10, conditioned on current state):")
    print(sim.head(10)[["team", "p_quarter", "p_semi", "p_final", "p_champion"]]
          .assign(**{c: (100 * sim.head(10)[c]).round(1)
                     for c in ["p_quarter", "p_semi", "p_final", "p_champion"]})
          .to_string(index=False))
    print(f"\nsaved -> {out}, champion_tracker.csv, champion_tracker.png")


def _round_robin(groups):
    rows, fid = [], 0
    for g, members in groups.items():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                rows.append({"fixture_id": fid, "group": g,
                             "home_team": members[i], "away_team": members[j]})
                fid += 1
    return pd.DataFrame(rows)


def _standings(played_df, groups):
    pts = {t: 0 for g in groups.values() for t in g}
    gd = dict(pts); gf = dict(pts); pl = dict(pts)
    for r in played_df.itertuples():
        gh, ga = int(r.home_score), int(r.away_score)
        for team, s in ((r.home, gh - ga), (r.away, ga - gh)):
            gd[team] += s; pl[team] += 1
        gf[r.home] += gh; gf[r.away] += ga
        if gh > ga:
            pts[r.home] += 3
        elif ga > gh:
            pts[r.away] += 3
        else:
            pts[r.home] += 1; pts[r.away] += 1
    return {"pts": pts, "gd": gd, "gf": gf, "pl": pl}


def _pct(x):
    return f"{100*x:.0f}%"


def _render(st, nxt, sim, n_played) -> str:
    L = ["# 🏆 World Cup 2026 — Champion Tracker\n",
         f"_A living, state-aware forecast. Conditioned on the **{n_played} "
         "matches played so far**: completed group games are held fixed; the rest "
         "of the tournament is simulated from a Bayesian goals model (squad-skill "
         "prior + current form + X/ESPN sentiment). Updated 2026-06-19._\n"]

    L.append("## How to read this\n")
    L.append("1. **Next games** — predicted goals for the upcoming fixtures.")
    L.append("2. **The trophy** — each team's title probability, given everything "
             "that has already happened.\n")
    L.append("Both come from one model: goals are the primitive; the winner is a "
             "simulation over goals. See [METHODOLOGY.md](METHODOLOGY.md).\n")

    L.append("## Title odds — conditioned on current results\n")
    L.append("| Team | Quarter | Semi | Final | **Champion** |")
    L.append("|---|---|---|---|---|")
    for r in sim.head(12).itertuples():
        L.append(f"| {r.team} | {_pct(r.p_quarter)} | {_pct(r.p_semi)} | "
                 f"{_pct(r.p_final)} | **{_pct(r.p_champion)}** |")

    L.append("\n## Next games — predicted goals\n")
    L.append("| Date | Fixture | Pred goals (xG) | Likely | P(H/D/A) | Home form |")
    L.append("|---|---|---|---|---|---|")
    for r in nxt.itertuples():
        L.append(f"| {r.date} | {r.home} v {r.away} | {r.xg} | {r.score} | "
                 f"{_pct(r.p_H)}/{_pct(r.p_D)}/{_pct(r.p_A)} | {r.edge} |")

    L.append("\n## Current group standings (played)\n")
    L.append("| Team | P | Pts | GD |")
    L.append("|---|---|---|---|")
    order = sorted(st["pts"], key=lambda t: (st["pts"][t], st["gd"][t]), reverse=True)
    for t in order:
        if st["pl"][t]:
            L.append(f"| {t} | {st['pl'][t]} | {st['pts'][t]} | {st['gd'][t]:+d} |")

    L.append("\n## What feeds the prediction\n")
    L.append("- **Player skillsets** — squad ratings (pace/shooting/passing/…) and "
             "seniority form the model's prior, so squad quality shapes goals.")
    L.append("- **Current results** — the posterior is fit on matches through today "
             "and the simulation holds played games fixed.")
    L.append("- **Form + X/ESPN sentiment** — folded in as a small, capped goal-rate "
             "nudge (see `models/momentum.py`, `data/scouting.py`).")
    L.append("- **Charts:** `artifacts/champion_tracker.png` (title odds), "
             "`artifacts/forecast_probs.png`, `artifacts/calibration.png`.")
    return "\n".join(L)


if __name__ == "__main__":
    main()
