"""Central paths and shared constants.

Keeping every filesystem location in one place means scripts never hard-code
strings and the whole pipeline can be relocated by editing this file alone.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path


def today() -> str:
    """Current date (ISO). The pipeline's cutoff, so it rolls forward each run."""
    return date.today().isoformat()

# Project root = two levels up from this file (src/wc2026/config.py -> repo root).
ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
ARTIFACTS = ROOT / "artifacts"

# Reproducibility: every stochastic step seeds off this.
SEED = 2026

# Synthetic-data sizing.
SQUAD_SIZE = 26          # FIFA allows 26-player squads in 2026
N_HISTORICAL_MATCHES = 1200  # friendlies + qualifiers used to fit team strengths


def ensure_dirs() -> None:
    """Create the data/artifact directories if they do not yet exist."""
    for d in (RAW, INTERIM, PROCESSED, ARTIFACTS):
        d.mkdir(parents=True, exist_ok=True)
