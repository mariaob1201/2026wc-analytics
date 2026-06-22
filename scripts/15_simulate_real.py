"""Stage 15: simulate the real 2026 tournament from the real-data posterior,
with the current-form momentum nudge folded in.

Uses the real groups (teams.py), the posterior fit on real results (stage 06),
and form/sentiment shifts (as of today) so the championship odds reflect who is
hot right now — not just pooled strength.

    python scripts/15_simulate_real.py

Run stage 06 first (produces artifacts/posterior_real.nc).
"""

import arviz as az
import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, ensure_dirs
from wc2026.data.scouting import MEXICO_SOCIAL
from wc2026.data.sources import build_real_matches
from wc2026.data.teams import TEAMS, by_group
from wc2026.models.bayesian_score import FitResult
from wc2026.models.momentum import combined_shifts
from wc2026.models.simulate import simulate_tournament
from wc2026.viz.plots import plot_champion_probs

from wc2026.config import today as _today
TODAY = _today()
N_SIMS = 5000


def main() -> None:
    ensure_dirs()
    teams = [t.name for t in TEAMS]
    idata = az.from_netcdf(ARTIFACTS / "posterior_real.nc")
    fit = FitResult(idata=idata, teams=teams,
                    team_to_idx={t: i for i, t in enumerate(teams)})

    groups = {g: [t.name for t in ts] for g, ts in by_group().items()}
    # Real within-group fixtures (round-robin per real group).
    fixtures = []
    fid = 0
    for g, members in groups.items():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                fixtures.append({"fixture_id": fid, "group": g,
                                 "home_team": members[i], "away_team": members[j]})
                fid += 1
    fixtures = pd.DataFrame(fixtures)

    shifts = combined_shifts(build_real_matches(start="2022-01-01", end=TODAY), TODAY,
                             scouted={"Mexico": MEXICO_SOCIAL["net_mood"]})

    print(f"Simulating {N_SIMS} tournaments (real posterior + real groups + "
          f"current-form momentum)...")
    sim = simulate_tournament(fit, fixtures, groups, n_sims=N_SIMS, shifts=shifts)
    sim.to_csv(PROCESSED / "simulation_real.csv", index=False)
    plot_champion_probs(sim, ARTIFACTS / "champion_probs_real.png")

    print("\n=== Title probabilities (real data + momentum, top 12) ===")
    show = sim.head(12).copy()
    for c in [col for col in show.columns if col.startswith("p_")]:
        show[c] = (100 * show[c]).round(1)
    print(show[["team", "p_round16", "p_quarter", "p_semi", "p_final",
                "p_champion"]].to_string(index=False))
    mex = sim[sim["team"] == "Mexico"]
    if len(mex):
        print(f"\nMexico: champion {100*float(mex['p_champion'].iloc[0]):.1f}%, "
              f"reach final {100*float(mex['p_final'].iloc[0]):.1f}%")
    print(f"\nsaved -> {PROCESSED / 'simulation_real.csv'}, "
          f"{ARTIFACTS / 'champion_probs_real.png'}")


if __name__ == "__main__":
    main()
