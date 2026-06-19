"""Stage 4: Monte-Carlo simulate the bracket and report win probabilities."""

import arviz as az
import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, RAW, ensure_dirs
from wc2026.data.teams import TEAMS, by_group
from wc2026.models.bayesian_score import FitResult
from wc2026.models.simulate import simulate_tournament
from wc2026.viz.plots import plot_champion_probs

N_SIMS = 5000


def main() -> None:
    ensure_dirs()
    fixtures = pd.read_csv(RAW / "fixtures.csv")
    idata = az.from_netcdf(ARTIFACTS / "posterior.nc")

    teams = [t.name for t in TEAMS]
    fit_result = FitResult(idata=idata, teams=teams,
                           team_to_idx={t: i for i, t in enumerate(teams)})
    groups = {g: [t.name for t in ts] for g, ts in by_group().items()}

    print(f"Simulating {N_SIMS} tournaments (drawing fresh posterior params each)...")
    sim = simulate_tournament(fit_result, fixtures, groups, n_sims=N_SIMS)
    sim.to_csv(PROCESSED / "simulation_results.csv", index=False)

    print("\n=== Predicted World Cup 2026 — title probabilities (top 12) ===")
    show = sim.head(12).copy()
    for c in [col for col in show.columns if col.startswith("p_")]:
        show[c] = (100 * show[c]).round(1)
    print(show.to_string(index=False))

    plot_champion_probs(sim, ARTIFACTS / "champion_probs.png")
    print(f"\nsaved results -> {PROCESSED / 'simulation_results.csv'}")
    print(f"saved plot    -> {ARTIFACTS / 'champion_probs.png'}")


if __name__ == "__main__":
    main()
