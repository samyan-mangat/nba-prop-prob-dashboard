# backend/app/router_admin.py
from __future__ import annotations
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import threading
import numpy as np
import pandas as pd
from datetime import date, timedelta

from .db import session_scope
from .models import Player, Game, PlayerGame
from .util_logging import get_logger
from .ingest import upsert_players, ingest_season

log = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

# ---- in-memory task registry (clears on server restart) ----
TASKS: dict[str, dict] = {}
LOCK = threading.Lock()

class IngestPayload(BaseModel):
    seasons: List[str]
    players_only: bool = False
    sleep: float = 0.6

@router.post("/ingest")
def start_ingest(payload: IngestPayload, bg: BackgroundTasks):
    """Start background ingestion for provided seasons."""
    task_id = uuid4().hex[:10]
    with LOCK:
        TASKS[task_id] = {"id": task_id, "status": "queued", "note": None}

    def worker():
        try:
            with LOCK:
                TASKS[task_id]["status"] = "running"
            upsert_players()
            if not payload.players_only:
                for season in payload.seasons:
                    log.info(f"[{task_id}] ingest_season({season})")
                    ingest_season(season, sleep=payload.sleep)
            with LOCK:
                TASKS[task_id]["status"] = "done"
        except Exception as e:
            log.exception("ingest worker failed")
            with LOCK:
                TASKS[task_id]["status"] = "error"
                TASKS[task_id]["note"] = str(e)

    bg.add_task(worker)
    return {"task_id": task_id, "status": "queued"}

@router.get("/tasks/{task_id}")
def get_task(task_id: str):
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="task not found (server may have restarted)")
    return t

@router.get("/db_stats")
def db_stats():
    with session_scope() as s:
        players = s.query(Player).count()
        games = s.query(Game).count()
        pgs = s.query(PlayerGame).count()
    return {"players": players, "games": games, "player_games": pgs}

@router.get("/player_games_count")
def player_games_count(player_id: int):
    with session_scope() as s:
        cnt = s.query(PlayerGame).filter(PlayerGame.player_id == player_id).count()
    return {"player_id": player_id, "player_games": cnt}

@router.post("/seed_demo")
def seed_demo(player_id: int, games: int = 200):
    """Create synthetic PlayerGame rows for a player so the UI can be demoed immediately."""
    rng = np.random.default_rng(7)
    with session_scope() as s:
        # Ensure player exists
        p = s.get(Player, player_id)
        if p is None:
            s.add(Player(id=player_id, full_name=f"Player {player_id}", team_abbrev=None))

        # Create synthetic games and player_games
        start = date(2023, 10, 1)
        for i in range(games):
            gid = f"DEMO{player_id:06d}{i:04d}"
            gd = start + timedelta(days=i)
            if s.get(Game, gid) is None:
                s.add(Game(id=gid, game_date=gd, home_team="HME", away_team="AWY"))
            # mildly realistic Curry-ish distribution
            pts = float(rng.normal(28, 6))
            reb = float(rng.normal(5.2, 2))
            ast = float(rng.normal(6.1, 2.5))
            stl = float(max(0, rng.normal(1.1, 0.6)))
            blk = float(max(0, rng.normal(0.3, 0.4)))
            tov = float(max(0, rng.normal(3.0, 1.2)))
            fg3m = float(max(0, rng.normal(4.6, 1.8)))
            if not s.query(PlayerGame).filter_by(game_id=gid, player_id=player_id).first():
                s.add(PlayerGame(
                    game_id=gid, player_id=player_id, minutes=34.0,
                    pts=pts, reb=reb, ast=ast, stl=stl, blk=blk, tov=tov,
                    fgm=pts/2.0, fga=18.0, fg3m=fg3m, fg3a=11.0, ftm=4.0, fta=4.5
                ))
    return {"inserted": games, "player_id": player_id}
