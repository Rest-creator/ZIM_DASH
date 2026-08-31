# Vision Document: ZimDash

- **Purpose:** Establishes product vision, market analysis, and success parameters.
- **Phase:** 1 — Product Discovery & Ideation.
- **Owner:** Product Champion.
- **Approver:** Principal Architect / Lead Engineer.
- **Source:** `ZimDash_Product_Design_Document.pdf` (v1.0.0, build 1, 26 August 2026).
- **Status:** Prototype · Pre-launch.

## 1. Executive Summary

ZimDash is a food-and-grocery delivery app for Harare, Zimbabwe. Customers browse restaurants and
supermarkets, order from a shared cart, and pay by EcoCash, card, or cash on delivery — the same
on-demand pattern proven by platforms like DoorDash, adapted for a market those platforms don't yet
serve. A fully designed, working prototype exists today: every screen in the customer journey is
implemented against a real Supabase Postgres backend with row-level security. What is missing is the
operational machinery — real payments, real dispatch, vendor and rider tooling.

## 2. Problem Statement

**Problem context.** Most Harare restaurants that deliver today do it over WhatsApp or phone calls,
with a rider dispatched ad hoc. This caps how many orders a kitchen can handle at once, gives
customers no visibility into where their order is, and gives no restaurant a way to be discovered
beyond word of mouth.

**Affected users.** Urban Harare residents ordering to home or work; independent restaurants and
supermarkets with no online ordering channel of their own; informal and traditional-cuisine vendors
underserved by global platforms.

**Current alternatives.** WhatsApp/phone ordering with ad-hoc rider dispatch; global delivery
platforms (DoorDash-style) that assume card-first payment and don't localize for EcoCash or
traditional-cuisine vendors.

**Proposed solution.** A single multi-vendor marketplace app, EcoCash-first, with delivery fee/ETA
shown up front and order tracking — combining restaurants and supermarkets in one app deliberately,
to give customers a reason to open it more than once a week and to give the business two demand pools
while the marketplace is still building density.

## 3. Target Personas

| Persona | Description | Status |
|---|---|---|
| Customers | Urban Harare residents (initial suburbs: Avondale, Borrowdale, Mount Pleasant, Belvedere, Greendale, CBD) ordering to home or work. Pay by EcoCash, card, or cash; want fee/ETA up front and order tracking. | Full journey built |
| Restaurants & supermarkets | Vendors wanting an online ordering/delivery channel without building their own app or dispatch system. | Reference data only — no vendor-facing tooling |
| Riders | Motorbike and bicycle couriers, paid per delivery. | Not yet built |
| Ops / admin | Internal team approving vendors, managing promo codes, handling disputes. | Not yet built — currently manual SQL editing in Supabase |

## 4. Product Vision & Goals

**Vision statement.** Bring Harare's restaurants and supermarkets into one ordering experience built
for the way Harare actually pays and gets around — EcoCash first, not an afterthought — with a visual
identity drawn from the Zimbabwean flag and the flame lily rather than a generic delivery-app template.

**Technical goals:**
- One Flutter/Dart codebase serving iOS, Android, and web.
- Managed backend (Supabase Postgres) with row-level security enforced server-side, not just
  client-side filtering.
- Graceful degradation to bundled local data when the backend isn't configured.
- An architecture that does not assume a single city or currency permanently, even though Harare/USD
  is the day-one scope.

## 5. Infrastructural & Operational Constraints

Unlike the self-hosted-VPS default this handbook otherwise assumes, ZimDash's backend is a **managed**
platform (Supabase), which changes several downstream documents (see the Business Case's cost model
and the System Design Document's deployment topology).

- **Hosting target:** Supabase managed Postgres (region TBD), not a self-hosted VPS.
- **Client distribution:** iOS App Store, Google Play, and web — each with its own release review
  process and lead time, unlike a self-hosted deploy that the team fully controls.
- **Payment rails:** must integrate a Zimbabwean payment aggregator (e.g. Paynow) for EcoCash and card
  processing; no such integration exists yet (see Section 14 of the source PDF, carried into the Risk
  Register).
- **Security boundary:** only the Supabase anon key ships in the client; a service-role key must never
  be embedded client-side.

## 6. Success Criteria

| Metric | Baseline (Phase 0) | Target Success Threshold | Target Horizon |
|---|---|---|---|
| Full customer journey implemented against real backend | Done | Maintained | Continuous |
| Live payment processing | 0% (UI choice only, no money moves) | 100% of orders server-verified before confirmation | Phase 1 (MVP launch) |
| Order dispatch reaching a real kitchen/rider | 0% (client-side timer simulation) | Server-side state machine live | Phase 1 |
| Orders placed per week / GMV | N/A (pre-launch) | Tracked from first real order | Phase 1 onward |
| Active restaurants/supermarkets on platform | Manually seeded reference data | Vendor-managed via dashboard | Phase 2 |
| Repeat customer rate (7-day / 30-day) | N/A | Tracked | Phase 1 onward |

## 7. Discovery Review Notes

- **Lead Engineer / Architect** should size the Supabase plan tier and Paynow/EcoCash aggregator
  settlement terms before Gate 1 sign-off (see Business Case, Section 2, Risk Matrix).
- **Product Champion** owns the differentiation statement above (EcoCash-first, dual-vendor-pool
  density strategy) and should re-validate it against real order data once Phase 1 launches.

---
*Traceability: this document is the parent of `business_case.md` and `../requirements/prd.md`.*
