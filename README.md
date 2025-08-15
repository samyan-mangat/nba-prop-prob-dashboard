# NBA Player Prop Probability Dashboard with Parlay Chat

A full-stack FastAPI + React app that ingests historical NBA box scores via `nba_api`, estimates per-player prop probabilities, computes correlated same-game parlay (SGP) probabilities via a Gaussian copula, and exposes an NLP chat for queries such as:

> "Tatum 30+ pts and 8+ reb on 2025-11-03?"

## Features
- **Data ingestion** from `stats.nba.com` using `nba_api` (player game logs + box scores).
- **SQLite** persistence (easily swap to Postgres) with SQLAlchemy.
- **Prop probabilities** using empirical CDFs and bootstrap smoothing.
- **Same-game parlay** support using a **Gaussian copula** to model correlation between legs.
- **Chat interface** with a lightweight regex + fuzzy parser for natural language queries.
- **React dashboard** with parlay builder, probability cards, and correlation heatmap.
- **Docker** for one-command startup.

## Quick Start (Docker)
```bash
# 1) Clone and configure
cp .env.example .env
# (Optionally set PROXY / NBA headers if needed.)

# 2) Build + run
docker-compose up --build

# Backend: http://localhost:8000/docs
# Frontend: http://localhost:5173