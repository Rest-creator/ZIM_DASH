# ADR-002: Supabase (managed Postgres + Auth + RLS) instead of a self-hosted backend

## Status
Deprecated (Superceded by ADR-005: Custom FastAPI Backend).

## Context
This engineering handbook's default assumption is a self-hosted VPS running a custom backend (FastAPI/
Django/Laravel) against a self-managed Postgres instance. ZimDash instead uses Supabase: managed
Postgres, built-in anonymous auth, and Postgres row-level security (RLS) policies as the sole
authorization layer — there is no backend codebase serving HTTP requests today.

## Decision
Use Supabase as the entire backend for the Phase 0/1 prototype and MVP: Postgres for all six tables,
Supabase Auth for anonymous device-scoped identity, and RLS policies (not application code) to enforce
that a user can only read/write their own `orders`, `order_items`, and `favorites`.

## Consequences
- **Benefits:** zero backend infrastructure to operate for a 1-4 person team; RLS enforced at the
  database layer is genuinely stronger than a common alternative mistake (client-side-only filtering);
  fast to build the full customer journey without writing a REST API by hand; anon key is safe to ship
  precisely because RLS — not obscurity — is the security boundary.
- **Drawbacks:** any logic that must not be client-triggerable (payment verification, order-state
  transitions once a real dispatch system exists, vendor approval) has nowhere safe to live yet —
  Supabase's client-facing PostgREST layer is not a place to put a service-role-gated operation. Phase 1
  will very likely need to introduce *some* server-side component (Supabase Edge Functions or a small
  dedicated service) specifically for payment webhook handling and dispatch state transitions — this
  ADR does not resolve that; see System Design Document Section 6 and the Threat Model.
- **Vendor lock-in:** the data model and RLS policies are Postgres-portable, but Auth and the generated
  REST layer are Supabase-specific. Migrating off Supabase later is possible but not free.
