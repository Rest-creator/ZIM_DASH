# ADR-001: Flutter/Dart single codebase for iOS, Android, and Web

## Status
Accepted (reflects the existing prototype implementation).

## Context
ZimDash needs to reach customers across iOS, Android, and web with a small (1-4 person) team and no
dedicated platform-specific engineers. Building three native clients would triple UI and business-logic
maintenance for a marketplace app whose differentiation is Harare-specific payment/UX details
(EcoCash-first checkout, suburb-aware delivery), not platform-specific capability.

## Decision
Use a single Flutter/Dart codebase targeting iOS, Android, and web, with `go_router` for declarative,
URL-based navigation that behaves the same across web and mobile.

## Consequences
- **Benefits:** one team maintains one business-logic layer (cart, checkout, order tracking); web
  becomes a near-free additional distribution channel; `go_router`'s URL-based model means a web user
  can deep-link into a restaurant or order in a way a purely mobile-first stack would need extra work
  for.
- **Drawbacks:** any platform-specific capability (e.g. native EcoCash SDK integration, if one exists
  and is mobile-only) needs a Flutter plugin or platform channel, which is more work than calling a
  native SDK directly. Web performance/UX for a delivery-tracking, map-heavy flow needs separate
  validation from mobile — not yet done (see SRS Section 2, no load/perf testing performed).
