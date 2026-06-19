"""Stage 1: write synthetic players, matches, and fixtures to data/raw/."""

from wc2026.config import RAW, ensure_dirs
from wc2026.data.generate_synthetic import (
    generate_fixtures,
    generate_matches,
    generate_players,
)


def main() -> None:
    ensure_dirs()
    players = generate_players()
    matches = generate_matches()
    fixtures = generate_fixtures()

    players.to_csv(RAW / "players.csv", index=False)
    matches.to_csv(RAW / "matches.csv", index=False)
    fixtures.to_csv(RAW / "fixtures.csv", index=False)

    print(f"players : {len(players):>5} rows -> {RAW / 'players.csv'}")
    print(f"matches : {len(matches):>5} rows -> {RAW / 'matches.csv'}")
    print(f"fixtures: {len(fixtures):>5} rows -> {RAW / 'fixtures.csv'}")


if __name__ == "__main__":
    main()
