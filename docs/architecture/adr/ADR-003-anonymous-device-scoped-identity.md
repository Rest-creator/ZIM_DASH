# ADR-003: Anonymous, device-scoped identity for the Phase 0/1 customer flow

## Status
Accepted for Phase 0 (prototype). **Open for reconsideration before Phase 1 launch** — see the source
product document's own "Anonymous auth ceiling" open question.

## Context
The product document's core UX goal is a low-friction order flow — "no login screen required to place
an order." Supabase Auth supports anonymous, per-device sessions natively, which satisfies this without
building a registration flow.

## Decision
Use Supabase's anonymous auth as the default identity for customers; an optional name/email profile can
be set locally but is not required to browse, order, or track.

## Consequences
- **Benefits:** zero-friction first order; matches the product's explicit design principle of familiar
  interaction with local substance — customers get straight to ordering.
- **Drawbacks:** order history does not carry across devices or app reinstalls, since identity is
  device-scoped. This is explicitly called out as unresolved in the source document (Section 14,
  "Anonymous auth ceiling") and as a Phase 1 candidate feature (Section 6, "Named accounts"). It also
  means an anonymous identity **cannot** authenticate a vendor or rider — named accounts are a hard
  prerequisite for both the Vendor Dashboard and Rider App in Phase 2, not an optional enhancement.
- **Open decision:** whether named accounts must move up from "Phase 1 candidate" to a launch blocker.
  Recorded as Risk Register R-4.
