# Product Requirements Document (PRD): ZimDash

- **Purpose:** Functional behaviors, user journeys, and acceptance criteria.
- **Phase:** 2 — Requirements Engineering.
- **Owner:** Product Champion.
- **Approver:** Lead Developer.

## 1. User Journeys

### Journey 1 — Place an order (primary flow, built today)

`Home → Restaurant → Cart → Checkout → Tracking → Orders`

1. User opens the app (no login required — identity is anonymous and device-scoped by default).
2. User browses restaurants/supermarkets via search, category chips, favourites filter, or sort
   (relevance, rating, delivery fee, speed).
3. User opens a restaurant, browses its menu grouped by category, adds items with quantity/notes to
   a cart that can span multiple restaurants.
4. User proceeds to checkout: fills delivery details (name, phone, address, Harare suburb picker),
   chooses a payment method (EcoCash, card, or cash on delivery), optionally redeems a promo code,
   selects a tip (15% default, quick-select percentages, or custom).
5. User confirms and sees the full fee breakdown (subtotal, delivery fee, service fee, tip, discount,
   total).
6. User tracks the order through a four-stage progress view (Confirmed → Cooking → Rider on the way →
   Delivered) with an ETA, and receives a toast notification on delivery.
7. The completed order persists in the user's Orders tab (order history).

### Journey 2 — Favourite a restaurant

User marks a restaurant as a favourite; it is scoped per (anonymous or named) user and can be used as
a browse filter.

### Journey 3 — Vendor receives and fulfills an order (not yet built)

No vendor-facing surface exists. See Section 3, Out-of-Scope.

### Journey 4 — Rider accepts and completes a delivery (not yet built)

No rider-facing surface exists. See Section 3, Out-of-Scope.

## 2. Functional Acceptance Criteria (BDD)

```gherkin
Feature: Place an order

Scenario: Customer places an order with EcoCash selected as payment method
  Given a customer has items from one restaurant in their cart
  When they complete checkout with payment method "EcoCash" and confirm
  Then an order record is created scoped to their user id
  And the order appears in their Orders tab
  And the order tracking view starts at stage "Confirmed"

Scenario: Customer redeems a promo code below the minimum subtotal
  Given a promo code requires a minimum subtotal of $10.00
  And the customer's cart subtotal is $6.00
  When they attempt to redeem the promo code at checkout
  Then the discount is not applied
  And the checkout summary shows the original total

Scenario: Anonymous customer's order history persists across app restarts
  Given a customer has never set a name/email profile
  And they have placed at least one order
  When they close and reopen the app on the same device
  Then their previous orders are still visible in the Orders tab

Feature: Row-level data isolation

Scenario: One user cannot read another user's orders
  Given two distinct anonymous or named users each have placed an order
  When user A queries the orders table
  Then only user A's own orders are returned, enforced by Postgres row-level security
```

## 3. Product Boundaries & Exclusions

**In-scope (Phase 0, built today):** browse/discover, restaurant detail, multi-restaurant cart,
checkout UI (payment method *selection*, not processing), promo code redemption against seeded
reference data, tip selection, simulated order tracking, order history, favourites, light/dark theme,
anonymous device-scoped identity, Postgres RLS-enforced data ownership.

**Explicitly out-of-scope until Phase 1 (MVP launch):**
- Real payment processing (EcoCash API / Paynow, card processing) — checkout today is a UI choice
  only; no money moves.
- Real order dispatch — a server-side state machine with vendor accept/reject and rider assignment,
  replacing the current fixed-length timer simulation.
- Live rider location feeding the tracking screen.
- Push notifications — status updates today are an in-app toast only, invisible if the app isn't open.
- Named accounts carrying order history across devices.
- Order cancellation/refund and human support contact.

**Explicitly out-of-scope until Phase 2 (Marketplace):**
- Vendor dashboard (menu/hours/availability management, order accept/reject).
- Rider app (job queue, navigation, proof of delivery, payout tracking).
- Admin/ops console (vendor approval, promo code management, dispute handling — currently all direct
  SQL-editor work).
- Ratings and reviews.

**Explicitly out-of-scope until Phase 3 (Scale):**
- Multi-city expansion beyond Harare.
- Scheduled/pre-orders, multiple saved addresses, loyalty program.
- Geofenced delivery zones with dynamic fee/ETA (today: fixed per-restaurant fee and time-range
  strings).
- Multi-currency handling (today: USD-only pricing).

---
*Traceability: child of `../discovery/vision_document.md`; parent of `srs.md`.*
