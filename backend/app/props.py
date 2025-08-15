# backend/app/props.py

import numpy as np
import pandas as pd
from sqlalchemy import select
from datetime import date
from .db import session_scope
from .models import PlayerGame

SUPPORTED_PROPS = ["pts", "reb", "ast", "stl", "blk", "tov", "fg3m"]

def _empty_hist() -> pd.DataFrame:
    # Always return these columns so downstream code never KeyErrors
    return pd.DataFrame(columns=["pts","reb","ast","stl","blk","tov","fg3m","minutes","game_id"])

def _get_player_history(player_id: int, cutoff: date | None = None) -> pd.DataFrame:
    with session_scope() as s:
        stmt = select(PlayerGame).where(PlayerGame.player_id == player_id)
        rows = s.execute(stmt).scalars().all()
    if not rows:
        return _empty_hist()
    df = pd.DataFrame([{
        "pts": r.pts, "reb": r.reb, "ast": r.ast, "stl": r.stl, "blk": r.blk,
        "tov": r.tov, "fg3m": r.fg3m, "minutes": r.minutes, "game_id": r.game_id
    } for r in rows])
    return df

def marginal_over_probability(player_id: int, prop: str, threshold: float, cutoff: date | None = None) -> tuple[float, int, dict]:
    if prop not in SUPPORTED_PROPS:
        raise ValueError(f"Unsupported prop: {prop}")
    hist = _get_player_history(player_id, cutoff)

    # Guard: no data or missing column -> return 0 with sample_size=0
    if hist.empty or prop not in hist.columns:
        return 0.0, 0, {"note": "no history"}

    x = pd.to_numeric(hist[prop], errors="coerce").to_numpy(dtype=float)
    x = x[~np.isnan(x)]
    n = x.size
    if n == 0:
        return 0.0, 0, {"note": "no history"}

    # slight smoothing for n>=10
    if n >= 10:
        x = x + np.random.normal(0, 0.05, size=x.shape)

    prob = float((x >= float(threshold)).mean())
    details = {
        "mean": float(x.mean()),
        "std": float(x.std(ddof=1)) if n > 1 else 0.0,
        "median": float(np.median(x)),
    }
    return prob, int(n), details

def build_joint_dataset(legs: list[dict], cutoff: date | None = None) -> pd.DataFrame:
    frames = []
    with session_scope() as s:
        for leg in legs:
            rows = s.execute(
                select(PlayerGame).where(PlayerGame.player_id == leg["player_id"])
            ).scalars().all()
            if not rows:
                # still create an empty frame with expected columns so merges work
                frames.append(pd.DataFrame(columns=["game_id", leg["prop"]]))
                continue
            f = pd.DataFrame([{ "game_id": r.game_id, leg["prop"]: getattr(r, leg["prop"]) } for r in rows])
            f = f.dropna()
            frames.append(f)

    if not frames:
        return pd.DataFrame()

    df = frames[0]
    for f in frames[1:]:
        df = pd.merge(df, f, on=["game_id"], how="inner")
    return df
