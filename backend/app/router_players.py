from fastapi import APIRouter
from .players import search_players
from .schemas import PlayerOut

router = APIRouter(prefix="/players", tags=["players"])

@router.get("/search", response_model=list[PlayerOut])
def player_search(q: str, limit: int = 8):
    matches = search_players(q, limit=limit) or []   # <-- ensure list
    return [{"id": m["id"], "full_name": m["full_name"], "team_abbrev": m.get("team_abbrev")} for m in matches]
