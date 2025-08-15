from sqlalchemy import Column, Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)  # NBA ID
    full_name: Mapped[str] = mapped_column(String, index=True)
    team_abbrev: Mapped[str | None] = mapped_column(String, nullable=True)

class Game(Base):
    __tablename__ = "games"
    id: Mapped[str] = mapped_column(String, primary_key=True)  # GAME_ID
    game_date: Mapped[Date] = mapped_column(Date, index=True)
    home_team: Mapped[str] = mapped_column(String)
    away_team: Mapped[str] = mapped_column(String)

class PlayerGame(Base):
    __tablename__ = "player_games"
    __table_args__ = (
        UniqueConstraint("game_id", "player_id", name="uq_game_player"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(String, index=True)
    player_id: Mapped[int] = mapped_column(Integer, index=True)
    minutes: Mapped[float] = mapped_column(Float)
    pts: Mapped[float] = mapped_column(Float)
    reb: Mapped[float] = mapped_column(Float)
    ast: Mapped[float] = mapped_column(Float)
    stl: Mapped[float] = mapped_column(Float)
    blk: Mapped[float] = mapped_column(Float)
    tov: Mapped[float] = mapped_column(Float)
    fgm: Mapped[float] = mapped_column(Float)
    fga: Mapped[float] = mapped_column(Float)
    fg3m: Mapped[float] = mapped_column(Float)
    fg3a: Mapped[float] = mapped_column(Float)
    ftm: Mapped[float] = mapped_column(Float)
    fta: Mapped[float] = mapped_column(Float)