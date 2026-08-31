# ADR-004: Provider for state management; shared_preferences for local cache

## Status
Accepted (reflects the existing prototype implementation).

## Context
ZimDash needs to manage cart state, app-wide state (auth/theme/favourites), and restaurant data across
a moderately complex UI (browse, detail, cart, checkout, tracking, orders, favourites) with a small
team, and needs the app to start fast and work reasonably offline on constrained mobile data.

## Decision
Use `Provider` with `ChangeNotifier`-based stores for cart, app state, and restaurant data. Use
`shared_preferences` to cache cart contents, theme choice, and profile locally so the app works offline
and starts fast, and to power the "degrades gracefully" fallback to bundled local data when Supabase
isn't configured.

## Consequences
- **Benefits:** `Provider` is a well-understood, low-ceremony state management choice appropriate for
  a small team; `shared_preferences` is trivial to reason about and sufficient for the current
  read-mostly, cache-shaped data (cart, theme, profile).
- **Drawbacks:** `shared_preferences` is a key-value cache, not a relational offline-first store —
  it cannot support true offline order composition with later sync/conflict resolution if that becomes
  a real requirement (constrained mobile data is already a named non-functional expectation). If
  offline order placement becomes a Phase 1/2 requirement, this decision should be revisited in favor
  of a reactive SQLite layer (e.g. Drift), per the mobile-engineering offline-first standard — see
  System Design Document Section 6.
- Not evaluated against alternatives (Riverpod, Bloc) in the source document — this ADR records what
  was built, not a comparative evaluation; re-litigating the choice is out of scope unless a concrete
  pain point emerges.
