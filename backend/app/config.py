from pydantic import BaseModel
import os

def _parse_bool(v: str | None, default: bool) -> bool:
    if v is None: 
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./nba.db")
    nba_api_timeout: int = int(os.getenv("NBA_API_TIMEOUT", "20"))
    nba_api_retries: int = int(os.getenv("NBA_API_RETRIES", "3"))
    proxy: str | None = os.getenv("PROXY") or None
    allow_origins: str = os.getenv("ALLOW_ORIGINS", "http://localhost:5173")

    # On-demand mode
    on_demand_fetch: bool = _parse_bool(os.getenv("ON_DEMAND_FETCH"), True)
    on_demand_seasons: list[str] = [s.strip() for s in os.getenv("ON_DEMAND_SEASONS", "2024-25,2023-24").split(",") if s.strip()]

settings = Settings()
