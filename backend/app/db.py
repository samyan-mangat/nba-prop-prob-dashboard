from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base."""
    pass


# Build engine (handle SQLite thread check for FastAPI workers)
DATABASE_URL = settings.database_url
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

# IMPORTANT: expire_on_commit=False avoids DetachedInstanceError after session closes
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
    expire_on_commit=False,
)


@contextmanager
def session_scope() -> Iterator[SessionLocal]:
    """Context-managed session with commit/rollback semantics."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Optional FastAPI dependency (if you ever want to use Depends(get_session))
def get_session() -> Iterator[SessionLocal]:
    with session_scope() as s:
        yield s
