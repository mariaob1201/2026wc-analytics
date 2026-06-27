"""Adapter for the open rezarahiminia/worldcup2026 dataset (keyless GitHub).

It provides the 48-team metadata (name, FIFA code, group, flag) and a player-name
list — but NOT player skill attributes or any attack/defence ratings. So we use it
for official team metadata and pair it with FIFA attributes + the model's ratings
to build the player/team tables.

The other listed APIs (api-football, balldontlie FIFA, thestatsapi, worldcupapi)
require API keys / non-public endpoints — plug them in here behind the same return
shape when you have a key.
"""

from __future__ import annotations

import json
import urllib.request

import pandas as pd

REPO = "https://raw.githubusercontent.com/rezarahiminia/worldcup2026/HEAD"
_UA = "wc2026-analytics/0.1 (research) python-urllib"


def _get(path: str):
    req = urllib.request.Request(f"{REPO}/{path}", headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310
        return json.loads(r.read().decode("utf-8"))


def fetch_team_metadata() -> pd.DataFrame:
    """48 teams: name, fifa_code, group, flag (from football.teams.json)."""
    data = _get("football.teams.json")
    rows = [{"name": t.get("name_en"), "fifa_code": t.get("fifa_code"),
             "group": t.get("groups"), "flag": t.get("flag")} for t in data]
    return pd.DataFrame(rows)
