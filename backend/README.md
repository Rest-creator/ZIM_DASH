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

## Database migrations (Alembic)

```bash
docker compose up -d db          # from the repo root
alembic upgrade head              # apply
alembic downgrade base            # roll all the way back
alembic revision --autogenerate -m "describe the change"   # new migration
alembic check                     # confirm models == migrated schema (no drift)
```

Tables live in the `iam`/`catalog`/`orders`/`ledger` schemas, never `public`
— see `database_design.md` Section 1 and `alembic/env.py`'s `MANAGED_SCHEMAS`
(also what keeps the postgis image's own `tiger`/`topology` extension
tables out of autogenerate's view).

## Quality gates

```bash
ruff check .
black --check .
pytest           # fast, no DB required
pytest -m db      # migration integration tests — needs `docker compose up -d db` first
```

## Local development (Docker Compose)

From the repo root — brings up Postgres (with PostGIS, ahead of ZD-M1-10),
Redis, and the API:

```bash
cp backend/.env.example backend/.env
docker compose up -d --build
curl http://127.0.0.1:8000/health
```
