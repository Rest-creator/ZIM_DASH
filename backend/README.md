# ZIM DASH API

FastAPI backend (ADR-005), Postgres + Redis, custom JWT auth, SSE realtime (ADR-006).

## Local development (native)

```bash
cd backend
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env   # then edit DATABASE_URL/REDIS_URL for localhost, not db/redis
uvicorn app.main:app --reload
```

## Quality gates

```bash
ruff check .
black --check .
pytest
```

## Local development (Docker Compose)

From the repo root — brings up Postgres (with PostGIS, ahead of ZD-M1-10),
Redis, and the API:

```bash
cp backend/.env.example backend/.env
docker compose up -d --build
curl http://127.0.0.1:8000/health
```
