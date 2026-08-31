# Business Case: ZimDash

- **Purpose:** Financial modeling, hosting cost estimates, resource constraints, and ROI timelines.
- **Phase:** 1 — Product Discovery & Ideation.
- **Owner:** Product Champion.
- **Approver:** Lead Engineer / Tech Lead.

> **Adaptation note:** the handbook's default Business Case template assumes a self-hosted VPS cost
> model (Hetzner/DigitalOcean + Backblaze). ZimDash runs on managed Supabase and multi-platform app
> store distribution instead, so the cost table below is reshaped accordingly. Dollar figures the
> source product document does not specify are marked **TBD** rather than invented — resolve them
> before Gate 1 sign-off.

## 1. Cost & Resource Analysis

### Operational Infrastructure Estimates

| Service | Quantity | Estimated Cost/Month | Provider | Notes |
|---|---|---|---|---|
| Managed Postgres + Auth + RLS | 1 project | TBD (Free tier today; Pro tier required before real user load) | Supabase | Current prototype likely on free tier — confirm before MVP traffic |
| Payment aggregator fees | Per transaction | TBD (% of GMV) | Paynow or equivalent EcoCash aggregator | Open question — see Risk Register R-1 |
| App store distribution | Annual | $99/yr (Apple Developer) + $25 one-time (Google Play) | Apple / Google | Standard published fees |
| Domain / web hosting for Flutter web build | 1 | TBD | TBD | Web is a build target per Section 9 of the product doc; hosting target not yet chosen |
| Push notification delivery (Phase 1 requirement) | 1 | Likely free tier (FCM/APNs) initially | Firebase / Apple | Required before launch per product doc Section 6 |
| **Total (known)** | — | **~$10/month fixed + variable transaction fees** | — | Excludes unresolved TBDs above |

### Resource Constraints

- Current team composition and hours: not specified in the source product document — **TBD**, owner
  to fill in during Gate 1 review.
- No dedicated QA, security, or ops headcount assumed (consistent with the handbook's 1–4 developer
  target profile) — Section 5 "Roles & Responsibilities" role-shares apply.

## 2. Risk Matrix & Mitigations

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| EcoCash/Paynow settlement terms unworkable for an early-stage business | High | Medium | Resolve aggregator choice before Phase 1 commitment (tracked as Open Question in the source doc, Section 14) |
| Supabase free-tier limits hit under real order volume | Medium | Medium | Monitor usage; budget for Pro-tier upgrade as a Phase 1 launch cost, not a surprise |
| No admin/ops console means vendor onboarding is a manual, error-prone SQL-editor task | Medium | High | Prioritize Admin/ops console per product doc Section 6 "Required before launch" table |
| App store review delays block release timing | Medium | Low–Medium | Submit builds with buffer time ahead of any committed launch date |
| Anonymous per-device identity loses order history on reinstall/device change | Low–Medium | Medium | Named accounts already flagged as a Phase 1 candidate in the source doc — see Open Questions |

## 3. ROI Timeline

The source product document does not provide revenue projections, take-rate assumptions, or a
break-even model — this section is intentionally left as an open item rather than populated with
invented numbers.

- [ ] Define ZimDash's take rate (commission per order) — feeds GMV-to-revenue conversion.
- [ ] Define expected order volume ramp for the initial six suburbs (Section 3 of the Vision
  Document) post-MVP launch.
- [ ] Re-run this section once Phase 1 success metrics (Vision Document Section 6) have at least
  4 weeks of real data.

---
*Traceability: direct child of `vision_document.md`.*
