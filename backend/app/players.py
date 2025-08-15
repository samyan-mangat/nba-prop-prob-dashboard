from typing import List
import pandas as pd
from sqlalchemy import select
from .db import session_scope
from .models import Player
from rapidfuzz import process, fuzz
from nba_api.stats.static import players as nba_players

_players_df: pd.DataFrame | None = None

PROP_ALIASES = {
    "points": "pts", "pts": "pts", "p": "pts", "point": "pts",
    "rebounds": "reb", "reb": "reb", "boards": "reb",
    "assists": "ast", "ast": "ast", "dimes": "ast",
    "steals": "stl", "stl": "stl",
    "blocks": "blk", "blk": "blk",
    "turnovers": "tov", "tov": "tov",
    "threes": "fg3m", "3pm": "fg3m", "3pt": "fg3m", "fg3m": "fg3m",
}

def load_players_cache():
    global _players_df
    # Try DB first
    with session_scope() as s:
        players_db = s.execute(select(Player)).scalars().all()
    if players_db:
        _players_df = pd.DataFrame([{
            "id": p.id, "full_name": p.full_name, "team_abbrev": p.team_abbrev
        } for p in players_db])
        return
    # Fallback to live static list
    plist = nba_players.get_players()  # all (active+inactive)
    _players_df = pd.DataFrame([{
        "id": int(p["id"]), "full_name": p["full_name"], "team_abbrev": p.get("team_abbreviation")
    } for p in plist])

def search_players(q: str, limit: int = 10) -> List[dict]:
    global _players_df
    if _players_df is None or _players_df.empty:
        load_players_cache()
    if _players_df is None or _players_df.empty:
        return []
    choices = _players_df["full_name"].tolist()
    matches = process.extract(q, choices, scorer=fuzz.WRatio, limit=limit)
    rows = []
    for name, score, idx in matches:
        row = _players_df.iloc[idx].to_dict()
        row["score"] = int(score)
        rows.append(row)
    return rows
