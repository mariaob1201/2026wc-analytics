"""Stage 2: engineer per-player features and the per-team prior covariate."""

import pandas as pd

from wc2026.config import PROCESSED, RAW, ensure_dirs
from wc2026.features.player_features import add_player_features, build_team_features


def main() -> None:
    ensure_dirs()
    players = pd.read_csv(RAW / "players.csv")

    players_feat = add_player_features(players)
    team_feat = build_team_features(players_feat)

    players_feat.to_csv(PROCESSED / "players_features.csv", index=False)
    team_feat.to_csv(PROCESSED / "team_features.csv", index=False)

    print(f"player features -> {PROCESSED / 'players_features.csv'} "
          f"({len(players_feat)} players)")
    print(f"team features   -> {PROCESSED / 'team_features.csv'} "
          f"({len(team_feat)} teams)")
    print("\nTop 10 teams by prior_strength (from player analytics):")
    cols = ["team", "skill_index", "longevity", "social_score", "prior_strength"]
    print(team_feat.sort_values("prior_strength", ascending=False)
          .head(10)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
