# Threat Model: ZimDash

- **Purpose:** Identifies security risks and STRIDE mitigations.
- **Phase:** 8 — Security & Compliance (drafted early, at Phase 3/4, because the product document
  itself flags payment and PII handling as open risks — see Vision Document Section 5 and Risk
  Register R-1/R-3/R-6).
- **Owner:** Security Champion (developer role-share).
- **Approver:** Technical Team (consensus).

## 1. System Trust Boundaries

- **Zone 1 (Client / Internet):** the Flutter app on an untrusted device, holding only the Supabase
  anon key.
- **Boundary (Supabase Auth + PostgREST + RLS):** the only enforcement point today. There is no
  application server the team operates — RLS policies *are* the authorization layer.
- **Zone 2 (Managed Supabase Postgres):** trusted, but its data-at-rest protections have not been
  independently reviewed (see SRS Section 3).
- **Zone 3 (Future, Phase 1): payment webhook / dispatch server** — does not exist yet. Whatever is
  built here becomes a new trust boundary and must never expose a service-role key or unauthenticated
  write path to order totals or payment state.

## 2. Asset Classifications

| Asset | Classification | Where it lives today |
|---|---|---|
| Customer name, phone, delivery address | PII | `orders` table, RLS-protected |
| Order contents, fee breakdown, totals | Financial/business data | `orders`, `order_items` |
| Promo codes | Business data (abuse-sensitive) | `promo_codes`, public read |
| Supabase anon key | Low sensitivity (safe to ship — RLS is the real boundary) | Client build |
| Supabase service-role key | Critical — must never ship client-side | Not present client-side today (verified per ADR-002) |

## 3. STRIDE Threat Mitigation Ledger

| Threat Class | Vector Description | Mitigation Strategy | Status |
|---|---|---|---|
| Spoofing | An attacker creates unlimited anonymous Supabase sessions to place fraudulent orders or abuse promo codes | Rate limiting on order/promo-redemption writes not yet confirmed configured at the Supabase project level | **Open — verify** |
| Tampering | Client-side checkout totals (subtotal, delivery fee, discount, tip, total) are computed and only *displayed* via UI today; because there is no real payment processing yet, nothing currently depends on this being tamper-proof — but this changes the moment Epic 1 (Real Payment Processing) ships | Server-side payment verification must recompute/validate the charged amount independently of whatever the client submits, before confirming an order | **Must be resolved before Epic 1 ships — see Project Plan Task 1.2** |
| Repudiation | A customer disputes placing an order with no audit trail beyond the `orders` row itself | `order_items` are snapshotted at purchase time (existing mitigation, confirmed in System Design Document Section 3) | Mitigated |
| Information Disclosure | Cross-user access to another customer's PII/orders via a missing or misconfigured RLS policy | RLS policies scope `orders`, `order_items`, `favorites` to the owning user; confirmed by design, not yet confirmed by an independent policy audit or automated test | **Open — add an automated RLS regression test (see PRD Section 2, "Row-level data isolation" scenario) before Phase 1** |
| Information Disclosure | Data protection compliance for Zimbabwe-based PII storage not reviewed | Legal/compliance review — Risk Register R-3 | **Open** |
| Denial of Service | No rate limiting confirmed on public read-only endpoints (`restaurants`, `menu_items`, `promo_codes`) | Rely on Supabase platform-level protections; not independently verified | **Open — verify** |
| Elevation of Privilege | A future admin/ops console (Phase 2) or payment webhook (Phase 1) accidentally exposes service-role-gated operations to the client | Any such operation must run behind a boundary the client cannot reach directly — this is a hard architectural constraint, not an implementation detail (see System Design Document Section 4) | **Design constraint for Epics 1, 2, 7** |

## 4. Mitigation Backlog

- [ ] Confirm Supabase rate limiting on writes (order creation, promo redemption) and public reads.
- [ ] Add an automated test asserting RLS policies reject cross-user reads of `orders`/`order_items`/
  `favorites` (ties to PRD Section 2's "Row-level data isolation" scenario).
- [ ] Commission a Zimbabwe data-protection compliance review before real user PII scales past pilot
  volume (Risk Register R-3).
- [ ] Design server-side payment verification (Epic 1, Task 1.2) so client-submitted totals are never
  trusted for the actual charge amount.

---
*Traceability: child of System Design Document; links to SRS Section 3 and Risk Register R-1/R-3/R-6.*
