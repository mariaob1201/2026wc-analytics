"""Stage 3: fit the hierarchical Bayesian score model and save the posterior."""

import arviz as az
import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, RAW, ensure_dirs
from wc2026.data.teams import TEAMS
from wc2026.models.bayesian_score import fit, posterior_strength_table
from wc2026.viz.plots import plot_strength


def main() -> None:
    ensure_dirs()
    matches = pd.read_csv(RAW / "matches.csv")
    team_feat = pd.read_csv(PROCESSED / "team_features.csv")

    # Stable team ordering shared by model + simulation.
    teams = [t.name for t in TEAMS]
    prior = (team_feat.set_index("team")["prior_strength"]
             .reindex(teams).fillna(0.0).to_numpy())

    print("Sampling posterior (NUTS)... this can take a couple of minutes.")
    result = fit(matches, teams, prior_strength=prior, draws=1000, tune=1000, chains=4)

    # Persist the posterior for the simulation stage.
    result.idata.to_netcdf(ARTIFACTS / "posterior.nc")

    # Convergence diagnostics: R-hat should be ~1.0 for all parameters.
    summary = az.summary(result.idata,
                         var_names=["intercept", "home_adv", "beta_prior",
                                    "sigma_att", "sigma_def"])
    print("\nKey-parameter posterior summary:")
    print(summary.to_string())
    max_rhat = summary["r_hat"].max()
    print(f"\nmax R-hat among key params: {max_rhat:.3f} "
          f"({'OK' if max_rhat <= 1.01 else 'CHECK — may need more tuning'})")

    strength = posterior_strength_table(result)
    strength.to_csv(PROCESSED / "posterior_strength.csv", index=False)
    print("\nTop 10 teams by posterior net strength:")
    print(strength.head(10).to_string(index=False))

    plot_strength(strength, ARTIFACTS / "team_strength.png")
    print(f"\nsaved posterior  -> {ARTIFACTS / 'posterior.nc'}")
    print(f"saved strengths  -> {PROCESSED / 'posterior_strength.csv'}")
    print(f"saved plot       -> {ARTIFACTS / 'team_strength.png'}")


if __name__ == "__main__":
    main()
