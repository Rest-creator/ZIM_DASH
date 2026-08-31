# ZimDash

Harare's food, delivered — a multi-vendor delivery marketplace bringing restaurants and supermarkets
into one ordering experience, built for the way Harare actually pays and gets around.

- **Status:** Prototype · Pre-launch
- **Platform:** iOS · Android · Web (single Flutter codebase)
- **Product doc:** [`ZimDash_Product_Design_Document.pdf`](./ZimDash_Product_Design_Document.pdf)
  (v1.0.0, build 1, 26 August 2026)

## What's here

This directory holds the SDLC documentation for ZimDash, structured per the
[SDLC engineering handbook](/home/tino/Projects/dev-logs/PRINCIPAL%20ENGINEER/engineering-guides/1.%20SDLC.md)
in `dev-logs`, populated from the product design document above rather than left as templates. The
project's actual Flutter/Supabase codebase is not in this directory — this repo is the documentation
layer for it.

Where the handbook's default assumptions (self-hosted VPS, custom backend) didn't fit ZimDash's actual
stack (managed Supabase, no application server), each document says so explicitly rather than silently
following the template.

## Document index

| Phase | Document | Path |
|---|---|---|
| 1. Discovery | Vision Document | [`docs/discovery/vision_document.md`](./docs/discovery/vision_document.md) |
| 1. Discovery | Business Case | [`docs/discovery/business_case.md`](./docs/discovery/business_case.md) |
| 2. Requirements | Product Requirements Document | [`docs/requirements/prd.md`](./docs/requirements/prd.md) |
| 2. Requirements | Software Requirements Specification | [`docs/requirements/srs.md`](./docs/requirements/srs.md) |
| 3. Architecture | System Design Document | [`docs/architecture/system_design.md`](./docs/architecture/system_design.md) |
| 3. Architecture | ADR-001: Flutter single codebase | [`docs/architecture/adr/ADR-001-flutter-single-codebase.md`](./docs/architecture/adr/ADR-001-flutter-single-codebase.md) |
| 3. Architecture | ADR-002: Supabase managed Postgres + RLS | [`docs/architecture/adr/ADR-002-supabase-managed-postgres-rls.md`](./docs/architecture/adr/ADR-002-supabase-managed-postgres-rls.md) |
| 3. Architecture | ADR-003: Anonymous device-scoped identity | [`docs/architecture/adr/ADR-003-anonymous-device-scoped-identity.md`](./docs/architecture/adr/ADR-003-anonymous-device-scoped-identity.md) |
| 3. Architecture | ADR-004: Provider + shared_preferences | [`docs/architecture/adr/ADR-004-provider-state-shared-preferences-cache.md`](./docs/architecture/adr/ADR-004-provider-state-shared-preferences-cache.md) |
| 4. Planning | Project Plan | [`docs/planning/project_plan.md`](./docs/planning/project_plan.md) |
| 4. Planning | Risk Register | [`docs/planning/risk_register.md`](./docs/planning/risk_register.md) |
| 8. Security | Threat Model | [`docs/security/threat_model.md`](./docs/security/threat_model.md) |

## Current phase

**Phase 0 (Prototype) → Phase 1 (MVP launch).** The full customer journey is built against a real
Supabase Postgres backend with row-level security. What's missing — real payments, real dispatch,
push notifications, named accounts — is tracked as the literal Phase 1 backlog in the
[Project Plan](./docs/planning/project_plan.md), with blockers tracked in the
[Risk Register](./docs/planning/risk_register.md).

## Open questions

Carried from the product document (Section 14) and expanded in the Risk Register:
- EcoCash integration path — which aggregator, what settlement terms.
- Rider supply model — in-house, gig marketplace, or vendor-provided.
- Data protection compliance for storing customer PII in Zimbabwe.
- Whether named accounts must become a Phase 1 launch blocker rather than a Phase 1 candidate.

A companion document, referenced in the product design PDF, covers agreements and arrangements with
developers — not included in this documentation set.
