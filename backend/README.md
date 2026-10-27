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

## Auth (`/auth/*`)

`/auth/anonymous` (device-scoped, no login screen — ADR-003) issues a token
for a client-generated `device_id`, upserting so the same device always maps
back to the same `iam.users` row. `/auth/register` upgrades *that same row*
to a named account (requires the anonymous token as Bearer auth);
`/auth/login` authenticates an existing named account; `/auth/me` is the
first route behind the JWT dependency (`app/api/deps.get_current_user`) —
reuse it for every future route that needs the caller's identity rather than
rolling a new check.

`/auth/anonymous` is rate-limited per source IP (Redis-backed, fixed window;
`settings.anonymous_auth_rate_limit*`) per the threat model's open finding —
order-creation and promo-redemption will need the same treatment once they
exist (`app/core/rate_limit.rate_limit` is written to be reused, not
auth-specific).

## Payments (`/payments/paynow/webhook`)

Paynow's aggregator choice itself is still open per the Risk Register (R-1)
— this implements their real, published API (ADR-005/Task 1.1 names them
specifically), not a placeholder, since it's well-documented and the open
item is the commercial/contract decision, not the integration shape.

Hash verification (`app/core/paynow.verify_and_parse`) is checked against
Paynow's own worked example from their docs — not just matched to a written
description of the algorithm — before being trusted (see
`tests/test_paynow.py`). For a status update that reports money moved
(Paid/Awaiting Delivery/Delivered/Cancelled/Refunded), the handler also
polls the transaction's `pollurl` back to Paynow and trusts *that* response,
per Paynow's own guidance to re-confirm rather than act on the pushed
message alone. This endpoint only ever writes `orders.orders.payment_status`
— the order-lifecycle state machine (ZD-M1-05) and ledger posting
(ZD-M1-14) are separate, later tasks that react to that column, not part of
this one.

## Quality gates

```bash
ruff check .
black --check .
pytest                       # fast, no DB required
pytest -m db                  # migration + auth integration tests —
                               # needs `docker compose up -d db redis` first
```

## Local development (Docker Compose)

From the repo root — brings up Postgres (with PostGIS, ahead of ZD-M1-10),
Redis, and the API:

```bash
cp backend/.env.example backend/.env
docker compose up -d --build
curl http://127.0.0.1:8000/health
```
