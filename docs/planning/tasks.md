# Zim Dash Engineering Tasks (Custom Backend - FastAPI)

Following ADR-005, we have migrated away from Supabase to a custom FastAPI backend. The SDLC flow remains identical, but the infrastructure and implementation tasks now reflect the Python/FastAPI ecosystem.

## Phase 3: Solution Architecture & Data Setup (SDLC Gates)

**Task ID**: ZD-M1-01
**Title**: `[DB] db: initialize alembic and create orders + users schema`
**Task Type**: Database Migration
**Priority**: P0-Blocker
**Owner**: mupezeni2001@gmail.com

**Objective**: 
Establish the foundational PostgreSQL data layer via Alembic migrations.
**In Scope**:
- Initialize Alembic environment.
- Create `users`, `orders` (with `order_status` ENUM), and `order_items` tables.
- Add `payment_status` and `payment_reference` columns.

## Phase 5: Engineering Standards & Infrastructure

**Task ID**: ZD-M1-02
**Title**: `[INFRA] chore(repo): initialize FastAPI boilerplate with strict linting`
**Task Type**: Chore
**Priority**: P0-Blocker
**Owner**: mupezeni2001@gmail.com

**Objective**:
Setup the custom backend repository.
**In Scope**:
- `pyproject.toml` with Ruff, Black, and Pytest.
- FastAPI initialization with `/health` endpoints.
- Dockerfile and `docker-compose.yml` for local Postgres/Redis.

## Phase 6: Development Workflow (Backend)

**Task ID**: ZD-M1-03
**Title**: `[AUTH] feat(api): implement JWT auth for anonymous and named accounts`
**Task Type**: Feature
**Priority**: P0-Blocker
**Owner**: mupezeni2001@gmail.com

**Objective**:
Replace Supabase Auth with custom JWT authentication.
**In Scope**:
- `/auth/anonymous` endpoint to issue device-scoped JWTs.
- `/auth/register` and `/auth/login` for named accounts.
- JWT middleware for route protection.

**Task ID**: ZD-M1-04
**Title**: `[PAY] feat(api): implement Paynow webhook verification endpoint`
**Task Type**: Feature
**Priority**: P1-High
**Owner**: mupezeni2001@gmail.com

**Objective**:
Handle the Paynow callback securely.
**In Scope**:
- FastAPI POST route for Paynow webhooks.
- Cryptographic signature verification.
- Update `orders.payment_status = PAID`.

**Task ID**: ZD-M1-05
**Title**: `[ORDER] feat(api): implement order state machine and websockets`
**Task Type**: Feature
**Priority**: P1-High
**Owner**: mupezeni2001@gmail.com

**Objective**:
Replace Supabase Realtime with FastAPI WebSockets.
**In Scope**:
- API endpoints to transition order status (`PENDING -> CONFIRMED`).
- WebSocket endpoint `/ws/orders/{id}` to broadcast status changes to the client.

## Phase 3: Solution Architecture (UI/UX Design)

*(Assigned to mambongowinston28@gmail.com)*

**Task ID**: ZD-M1-06
**Title**: `[DESIGN] ui: wireframes for named account registration and login`
**Task Type**: Design
**Priority**: P1-High
**Owner**: mambongowinston28@gmail.com

**Task ID**: ZD-M1-07
**Title**: `[DESIGN] ui: wireframes for live order tracking and dispatch map`
**Task Type**: Design
**Priority**: P0-Blocker
**Owner**: mambongowinston28@gmail.com

**Task ID**: ZD-M1-08
**Title**: `[DESIGN] ui: wireframes for order cancellation flow and support screen`
**Task Type**: Design
**Priority**: P2-Medium
**Owner**: mambongowinston28@gmail.com

## Phase 6: Development Workflow (Frontend)

**Task ID**: ZD-M1-09
**Title**: `[TRACK] feat(ui): integrate FastAPI WebSockets for live order tracking`
**Task Type**: Feature
**Priority**: P1-High
**Owner**: mupezeni2001@gmail.com

**Objective**:
Replace the client-side timer simulation and remove `supabase_flutter`.
**In Scope**:
- Refactor Flutter services to use standard HTTP REST calls.
- Implement WebSocket client for live order tracking.
