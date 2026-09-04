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

Derived from the product document's "Required before launch" table (Section 6) and Roadmap (Section 13). This covers the minimum to take a genuine paying order.

### Epic 1: Real Payment Processing
- Task 1.1: Select EcoCash aggregator (Paynow or equivalent) — blocked on Risk R-1.
- Task 1.2: Implement server-side payment verification before an order is confirmed (requires a new
  server-side component per ADR-002's open consequence).
- Task 1.3: Card processing integration.

### Epic 2: Real Order Dispatch
- Task 2.1: Design a server-side order state machine (replacing the client-side timer simulation).
- Task 2.2: Vendor order acceptance/rejection flow (initial non-dashboard mechanism).
- Task 2.3: Rider assignment logic — blocked on rider supply model decision (Risk R-2).

### Epic 3: Live Tracking
- Task 3.1: Real rider location tracking system.
- Task 3.2: Feed live coordinates to the customer order tracking screen.

### Epic 4: Named Accounts
- Task 4.1: Decide launch-blocker status (Risk R-4).
- Task 4.2: Implement named account creation/login alongside existing anonymous flow (additive, not a
  replacement — anonymous ordering should remain available per Vision Document Section 4).
- Task 4.3: Migrate order history from anonymous device identity to named account on upgrade.

### Epic 5: Push Notifications
- Task 5.1: Wire FCM (Android/web) and APNs (iOS) for order-status updates.
- Task 5.2: Replace/augment the current in-app toast with a real push notification on each tracking
  stage transition.

### Epic 6: Cancellations & Support
- Task 6.1: Order cancellation flow with defined cutoff (before vendor acceptance, e.g.).
- Task 6.2: Refund path tied to Epic 1's payment processor.
- Task 6.3: A reachable human-support contact point.

## 3. Work Breakdown Structure — Phase 2 (Marketplace)

Capabilities required for the platform to run itself without developer intervention, per the product roadmap.

### Epic 7: Vendor Dashboard
- Task 7.1: Named-account-gated vendor login (depends on Epic 4).
- Task 7.2: Menu/hours/availability CRUD, replacing manual SQL-editor edits (Risk R-5).
- Task 7.3: Incoming order accept/reject UI, replacing the Phase 1 MVP acceptance flow.

### Epic 8: Rider App
- Task 8.1: Job queue and acceptance UI.
- Task 8.2: Navigation and proof of delivery.
- Task 8.3: Payout tracking for couriers.

### Epic 9: Admin/Ops Console
- Task 9.1: Vendor approval workflow.
- Task 9.2: Promo code management UI (replacing manual `promo_codes` table edits).
- Task 9.3: Dispute handling workflow.

## 4. Sequencing Notes

Epic 4 (Named Accounts) and Epic 2 (Order Dispatch) are prerequisites for Epic 7 (Vendor Dashboard). Epic 7 is itself a soft prerequisite for scaling past the current hand-seeded restaurant set (Risk
R-5) — sequence accordingly rather than working all epics in parallel with a 1-4 person team.

---
*Traceability: parent of future Sprint Plans; risks tracked in `risk_register.md`.*
