# Risk Register: ZimDash

- **Purpose:** Tracks and mitigates project risks.
- **Phase:** 4 — Project Planning.
- **Owner:** Lead Engineer.
- **Approver:** Developer Team.
- **Update frequency:** weekly during active sprints.

## Risk Matrix

| ID | Risk Description | Probability | Impact | Score | Mitigation Plan | Owner | Source |
|---|---|---|---|---|---|---|---|
| R-1 | No EcoCash aggregator (e.g. Paynow) integration chosen; settlement terms for an early-stage business unknown | High | Critical | 9 | Resolve aggregator choice and settlement terms before committing to a Phase 1 launch date | Lead Engineer | Product doc §14 |
| R-2 | Rider supply model undecided (in-house, gig marketplace, or vendor's own staff) — shapes the entire Phase 2 rider app | High | High | 8 | Decide model before starting Phase 2 rider-app design work, not during it | Product Champion | Product doc §14 |
| R-3 | Data protection compliance for storing customer PII (name, phone, address) in Zimbabwe not reviewed | Medium | Critical | 7 | Legal/compliance review of current Supabase/RLS setup before real user PII scales past pilot volume | Lead Engineer | Product doc §14 |
| R-4 | Anonymous per-device identity may be insufficient through MVP launch — no order history across devices, cannot authenticate vendors/riders | Medium | Medium | 5 | Decide whether named accounts move from "Phase 1 candidate" to launch blocker before Gate 2 sign-off | Product Champion | Product doc §14, ADR-003 |
| R-5 | Vendor onboarding and reference-data edits require direct SQL-editor access — a single mistyped update can corrupt live menu/pricing data with no audit trail | Medium | High | 6 | Prioritize the Admin/ops console (product doc §6) ahead of scaling vendor count beyond what one person can hand-edit safely | Lead Engineer | Derived — Vision Doc §3 |
| R-6 | No server-side component exists for payment verification or order dispatch; introducing one is a new attack surface and new operational dependency | Medium | High | 6 | Design the Phase 1 payment/dispatch component with the same telemetry/health-check baseline as this handbook's Phase 5/10 standards, even though it sits outside the current Supabase-only architecture | Lead Architect | Derived — SDD §5/§6 |
| R-7 | Supabase free-tier limits could be hit unexpectedly once real order volume starts | Low | Medium | 3 | Monitor usage against tier limits; budget Pro-tier upgrade as a planned Phase 1 cost, not a surprise | Lead Engineer | Derived — Business Case §1 |
| R-8 | App store review timelines (iOS/Android) are outside the team's control and can delay a committed launch date | Low–Medium | Medium | 4 | Submit builds with buffer time ahead of any external launch commitment | Release Manager | Derived — Business Case §2 |
| R-9 | Push notifications, cancellations/refunds, and named accounts are all listed "Required before launch" (product doc §6) but none exist yet — scope risk for Phase 1 timeline | High | High | 8 | Treat the product doc's "Required before launch" table as the literal Phase 1 backlog (see `project_plan.md`); do not let scope grow beyond it before MVP | Lead Engineer | Product doc §6 |

**Scoring:** Probability × Impact on a 1–3 scale each (Low=1, Medium=2, High=3; Impact Critical=3).

---
*Traceability: child of `project_plan.md`.*
