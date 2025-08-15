# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import engine, Base
from .config import settings
from .util_logging import get_logger
from . import router_players, router_props, router_chat, router_admin  # <-- include admin

log = get_logger(__name__)
app = FastAPI(title="NBA Prop Probability API", version="0.1.0")

origins = [o.strip() for o in settings.allow_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    log.info(f"DB tables ensured. CORS allow_origins={origins}")

# Routers
app.include_router(router_players.router)
app.include_router(router_props.router)
app.include_router(router_chat.router)
app.include_router(router_admin.router)  # <-- wire it

@app.get("/")
def root():
    return {"status": "ok"}
