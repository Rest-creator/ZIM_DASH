# Software Requirements Specification (SRS): ZimDash

- **Purpose:** Technical constraints, protocol schemas, and data structures.
- **Phase:** 2 — Requirements Engineering.
- **Owner:** Lead Developer.
- **Approver:** Principal Architect / Tech Lead.

## 1. Technical Interfaces

- **Client:** Flutter/Dart, single codebase targeting iOS, Android, and Web.
- **Backend transport:** Supabase client SDK over HTTPS (PostgREST-generated REST interface + realtime
  channel where used), not a custom OpenAPI-first backend.
- **Auth:** Supabase Auth, anonymous device-scoped sessions by default; no login screen required to
  place an order.
- **Local persistence:** `shared_preferences` caches cart, theme, and profile — a key-value cache, not
  a relational offline-first store (see System Design Document, Section 5, for the gap this leaves).

## 2. System Non-Functional Constraints

Carried directly from the product document's Section 11 (Non-functional expectations):

| Constraint | Requirement |
|---|---|
| Performance | Smooth scrolling and search on mid-range Android hardware; usable over constrained mobile data. |
| Reliability | A placed order must never silently disappear; local and server persistence must agree. |
| Security & privacy | Row-level security enforced in Postgres, not just the client. Only the anon key ships in the app — a service-role key must never be embedded client-side. |
| Accessibility | Legible type scale and adequate contrast in both light and dark themes; tap targets sized for one-handed phone use. |
| Localization | USD pricing and a Harare suburb list today; architecture must not assume a single city or currency permanently. |

The handbook's default latency/concurrency targets (e.g. "200ms P95", "50 concurrent connections")
are **not yet defined for ZimDash** — no load testing has been performed against the prototype. This
is an open item for the Test Strategy once Phase 1 development begins.

## 3. Security Specifications

- **Data-in-transit:** HTTPS to Supabase (TLS enforced by the platform).
- **Data-at-rest:** managed by Supabase; no independent verification performed yet — track under
  Threat Model, Section 2.
- **Client secret handling:** only the Supabase anon key is embedded in the client build; this is by
  design (RLS makes the anon key safe to ship) but must be re-verified any time a new Supabase feature
  or service-role-only operation is added.
- **PII handled today:** customer name, phone, delivery address (collected at checkout, stored in the
  `orders` table). No documented data-retention or Zimbabwe-specific data-protection compliance review
  has been performed — flagged as an open risk (see Risk Register R-3 and Threat Model Section 3).

## 4. Database Relational Constraints

See System Design Document Section 4 for the full entity list. Ownership/visibility rules:

- `restaurants`, `menu_items`, `promo_codes` — public, read-only reference data.
- `orders`, `order_items`, `favorites` — owned by the placing/favouriting user only, enforced via
  Postgres row-level security policies (not client-side filtering).
- `order_items` are snapshotted at purchase time so later menu changes do not rewrite order history.

## 5. Operational Metrics

No telemetry, structured logging, or health-check endpoints exist yet for the client or backend
(there is no backend service to instrument beyond Supabase itself). This is a deliberate gap at
Phase 0 and should be revisited once Phase 1 introduces a payment/dispatch backend component that
*is* something the team operates directly (see System Design Document, Section 6, Observability).

---
*Traceability: child of `prd.md`; parent of `../architecture/system_design.md`.*
