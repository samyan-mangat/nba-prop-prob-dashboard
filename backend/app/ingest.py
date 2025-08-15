"""Data ingestion from nba_api into local DB.
Now callable from code (API) with optional date filters.
"""

from __future__ import annotations
import time
from datetime import date, datetime
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerGameLog
from sqlalchemy import select

from .db import session_scope
from .models import Player, PlayerGame, Game
from .util_logging import get_logger

log = get_logger(__name__)

def _to_date(v) -> date:
    if v is None:
        return None
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        return datetime.strptime(v, "%Y-%m-%d").date()
    raise ValueError("Invalid date")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def fetch_player_games(player_id: int, season: str) -> pd.DataFrame:
    gl = PlayerGameLog(player_id=player_id, season=season, season_type_all_star="Regular Season")
    return gl.get_data_frames()[0]

def upsert_players() -> int:
    log.info("Fetching players list...")
    plist = players.get_active_players() + players.get_inactive_players()
    with session_scope() as s:
        for p in plist:
            pid = int(p["id"])
            row = s.get(Player, pid)
            if row is None:
                s.add(Player(id=pid, full_name=p["full_name"], team_abbrev=p.get("team_abbreviation")))
            else:
                row.full_name = p["full_name"]
                row.team_abbrev = p.get("team_abbreviation")
    log.info(f"Upserted {len(plist)} players.")
    return len(plist)

def ingest_season(
    season: str,
    *,
    sleep: float = 0.6,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> int:
    """Ingest player game logs for a season. Optional date filter (inclusive)."""
    start_date = _to_date(start_date) if start_date else None
    end_date = _to_date(end_date) if end_date else None

    upsert_players()
    # Get all player ids once
    with session_scope() as s:
        pids = [r[0] for r in s.execute(select(Player.id)).all()]

    total_rows = 0
    for pid in pids:
        try:
            df = fetch_player_games(pid, season)
        except Exception as e:
            log.warning(f"player {pid} failed: {e}")
            continue
        if df.empty:
            time.sleep(sleep); continue

        df.rename(columns=str.lower, inplace=True)
        df["game_date"] = pd.to_datetime(df["game_date"]).dt.date

        if start_date or end_date:
            mask = pd.Series(True, index=df.index)
            if start_date: mask &= (df["game_date"] >= start_date)
            if end_date:   mask &= (df["game_date"] <= end_date)
            df = df[mask]
            if df.empty:
                time.sleep(sleep); continue

        with session_scope() as s:
            for _, r in df.iterrows():
                gid = str(r["game_id"])
                if s.get(Game, gid) is None:
                    # Basic home/away placeholders (fine for our purposes)
                    matchup = str(r.get("matchup", ""))  # e.g., "BOS @ NYK"
                    parts = matchup.split()
                    away, home = (parts[0] if parts else ""), (parts[-1] if parts else "")
                    s.add(Game(id=gid, game_date=r["game_date"], home_team=home, away_team=away))

                exists = s.execute(
                    select(PlayerGame).where(PlayerGame.game_id == gid, PlayerGame.player_id == pid)
                ).scalar_one_or_none()
                if exists:
                    continue

                s.add(PlayerGame(
                    game_id=gid,
                    player_id=pid,
                    minutes=float(r.get("min", 0) or 0),
                    pts=float(r.get("pts", 0) or 0),
                    reb=float(r.get("reb", 0) or 0),
                    ast=float(r.get("ast", 0) or 0),
                    stl=float(r.get("stl", 0) or 0),
                    blk=float(r.get("blk", 0) or 0),
                    tov=float(r.get("tov", 0) or 0),
                    fgm=float(r.get("fgm", 0) or 0),
                    fga=float(r.get("fga", 0) or 0),
                    fg3m=float(r.get("fg3m", 0) or 0),
                    fg3a=float(r.get("fg3a", 0) or 0),
                    ftm=float(r.get("ftm", 0) or 0),
                    fta=float(r.get("fta", 0) or 0),
                ))
        total_rows += len(df)
        time.sleep(sleep)  # be nice to the API

    log.info(f"Ingested ~{total_rows} rows for season {season} (range {start_date}..{end_date}).")
    return total_rows
