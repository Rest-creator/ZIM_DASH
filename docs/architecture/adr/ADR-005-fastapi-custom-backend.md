# ADR-005: Custom FastAPI Backend for ZIM DASH

## Status
Accepted (Supercedes ADR-002)

## Context
Initially, ZIM DASH used Supabase (managed Postgres, Auth, and RLS) to rapidly build a prototype without backend code (ADR-002). However, as we approach Milestone 1 (MVP launch) involving real payment verification, order state machines, and named accounts, the limitations of having no dedicated server-side environment became apparent. Instead of relying on a patchwork of Supabase Edge Functions for secret operations and fighting vendor lock-in with Supabase Auth/RLS, the decision was made to build a fully custom backend.

## Decision
We will build a custom backend service using **FastAPI (Python)** backed by a self-hosted **PostgreSQL** database. 
- **API Framework**: FastAPI (chosen for high performance, async support which is excellent for WebSockets/live-tracking, and automatic OpenAPI schema generation).
- **ORM**: SQLAlchemy (async) or SQLModel.
- **Authentication**: Custom JWT-based authentication supporting both anonymous device-scoped tokens and named user accounts.
- **Real-time**: FastAPI WebSockets will replace Supabase Realtime for order state and live tracking updates.

## Consequences
- **Benefits**: Full control over the authentication lifecycle (especially the complex anonymous-to-named transition); secure environment for payment processing webhooks; no vendor lock-in; native Python ecosystem for future integrations (e.g., routing algorithms).
- **Drawbacks**: Increased operational overhead. We must now manually write API endpoints, handle connection pooling, implement JWT auth, manage database migrations (Alembic), and host the service on a VPS.
- **Action Required**: The Flutter application must be refactored to remove the `supabase_flutter` dependency and replace it with standard HTTP/REST calls and WebSocket connections.
