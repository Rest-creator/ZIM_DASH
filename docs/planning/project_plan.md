# Project Plan: ZimDash

- **Purpose:** Milestone dates, work breakdown, task assignments, overall schedule.
- **Phase:** 4 — Project Planning.
- **Owner:** Lead Engineer.
- **Approver:** Developer Team.
- **Update frequency:** bi-weekly.

## 1. Milestone Roadmap

Mirrors the product document's own roadmap (Section 13), restated as gated milestones:

- [x] **M-0: Prototype** — full customer UX built against a real Supabase Postgres database with RLS;
  static/seeded restaurant data; simulated tracking; no live payments. *(Complete — this is the
  current state.)*
- [ ] **M-1: MVP launch readiness** — real payment processing, real vendor order acceptance, named
  accounts, push notifications: the minimum to take a genuine paying order.
- [ ] **M-2: Marketplace** — vendor dashboard, rider app, ratings and reviews, admin/ops tooling — the
  platform runs without a developer in the loop.
- [ ] **M-3: Scale** — multi-city expansion, loyalty program, scheduled orders, dynamic zone-based fees
  and ETAs.

## 2. Work Breakdown Structure — Phase 1 (MVP Launch)

Taken directly from the product document's "Required before launch" table (Section 6), organized as
epics. This table *is* the Phase 1 backlog — see Risk Register R-9.

### Epic 1: Real Payment Processing
- Task 1.1: Select EcoCash aggregator (Paynow or equivalent) — blocked on Risk R-1.
- Task 1.2: Implement server-side payment verification before an order is confirmed (requires a new
  server-side component per ADR-002's open consequence).
- Task 1.3: Card processing integration.

### Epic 2: Real Order Dispatch
- Task 2.1: Design a server-side order state machine (replacing the client-side timer simulation).
- Task 2.2: Vendor order acceptance/rejection flow.
- Task 2.3: Rider assignment logic — blocked on rider supply model decision (Risk R-2).

### Epic 3: Named Accounts
- Task 3.1: Decide launch-blocker status (Risk R-4).
- Task 3.2: Implement named account creation/login alongside existing anonymous flow (additive, not a
  replacement — anonymous ordering should remain available per Vision Document Section 4).
- Task 3.3: Migrate order history from anonymous device identity to named account on upgrade.

### Epic 4: Push Notifications
- Task 4.1: Wire FCM (Android/web) and APNs (iOS) for order-status updates.
- Task 4.2: Replace/augment the current in-app toast with a real push notification on each tracking
  stage transition.

### Epic 5: Vendor Dashboard (menu/hours/availability, accept/reject orders)
- Task 5.1: Named-account-gated vendor login (depends on Epic 3).
- Task 5.2: Menu/hours/availability CRUD, replacing manual SQL-editor edits (Risk R-5).
- Task 5.3: Incoming order accept/reject UI, wired to Epic 2's state machine.

### Epic 6: Cancellations & Support
- Task 6.1: Order cancellation flow with defined cutoff (before vendor acceptance, e.g.).
- Task 6.2: Refund path tied to Epic 1's payment processor.
- Task 6.3: A reachable human-support contact point.

### Epic 7: Admin/Ops Console
- Task 7.1: Vendor approval workflow.
- Task 7.2: Promo code management UI (replacing manual `promo_codes` table edits).
- Task 7.3: Dispute handling workflow.

## 3. Sequencing Notes

Epics 3 (Named Accounts) and 2 (Order Dispatch) are prerequisites for Epic 5 (Vendor Dashboard) and
Epic 5 is itself a soft prerequisite for scaling past the current hand-seeded restaurant set (Risk
R-5) — sequence accordingly rather than working all seven epics in parallel with a 1-4 person team.

---
*Traceability: parent of future Sprint Plans; risks tracked in `risk_register.md`.*
