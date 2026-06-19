"""Extract REAL player data by team from a public source, engineer features,
and produce a semantic interpretation report.

Outputs
-------
* data/raw/players_real.csv            -- real squads in the project schema
* data/processed/players_real_features.csv
* data/processed/team_features_real.csv
* data/processed/team_interpretation.csv
* data/processed/team_profiles.md      -- the human-readable report

After this you can point stages 3/4 at the real team features to fit + simulate.
"""

from wc2026.config import PROCESSED, RAW, ensure_dirs
from wc2026.data.sources import build_real_squads
from wc2026.features.interpretation import (
    add_player_interpretation,
    interpret_all_teams,
    team_profiles_markdown,
)
from wc2026.features.player_features import add_player_features, build_team_features


def main() -> None:
    ensure_dirs()

    print("Extracting real squads from the public FIFA dataset (by nationality)...")
    players = build_real_squads()
    players.to_csv(RAW / "players_real.csv", index=False)
    print(f"  -> {len(players)} players across "
          f"{players['team'].nunique()} teams -> {RAW / 'players_real.csv'}")

    # Engineered numeric features (longevity/skill_index/social_score/...).
    players_feat = add_player_features(players)
    players_feat = add_player_interpretation(players_feat)
    players_feat.to_csv(PROCESSED / "players_real_features.csv", index=False)

    team_feat = build_team_features(players_feat)
    team_feat.to_csv(PROCESSED / "team_features_real.csv", index=False)

    # Semantic interpretation.
    interp = interpret_all_teams(players)
    interp.to_csv(PROCESSED / "team_interpretation.csv", index=False)
    report = team_profiles_markdown(interp, players)
    (PROCESSED / "team_profiles.md").write_text(report)

    print("\nTop 10 squads by quality (semantic tier):")
    cols = ["team", "tier", "avg_overall", "age_profile", "style", "depth",
            "star_player"]
    print(interp.head(10)[cols].to_string(index=False))

    print(f"\nsaved interpretation -> {PROCESSED / 'team_interpretation.csv'}")
    print(f"saved profiles report -> {PROCESSED / 'team_profiles.md'}")
    print("\nExample narratives:")
    for _, r in interp.head(3).iterrows():
        print(f"\n• {r['narrative']}")


if __name__ == "__main__":
    main()
