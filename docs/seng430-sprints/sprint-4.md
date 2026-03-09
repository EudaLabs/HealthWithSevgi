# Sprint 4 Submission

- **Source URL:** https://webonline.cankaya.edu.tr/mod/assign/view.php?id=24497
- **Opened:** Thursday, 19 February 2026, 12:00 AM
- **Due:** Wednesday, 15 April 2026, 1:00 PM

## Sprint Scope

**SPRINT 4: Full Pipeline — ML Tool’s Steps 6 & 7**

Explainability · Feature importance · Ethics checklist · Bias auto-detection

## Deliverables

| Artifact / Deliverable | Tool / Format |
|---|---|
| Sprint 4 Backlog (Jira) | Jira (submit URL) — Sprint 4 stories committed; story points; sub-tasks for Steps 6 and 7 |
| Feature Importance Chart | GitHub (submit URL) — horizontal bars sorted descending; clinical display names (not column names); values 0.00–1.00 |
| Clinical Sense-Check Banner | GitHub (submit URL) — domain-specific sense-check text for all 20 domains; correct text when switching domains |
| Patient Selector + Waterfall | GitHub (submit URL) — dropdown with 3 test patients; waterfall bars red/green; plain-language labels |
| Caution and Info Banners | GitHub (submit URL) — amber caution ('associations not causes'); blue what-if banner with probability shift |
| Domain Clinical Review | GitHub Wiki (submit URL) — table for 20 domains: Domain \| Top Feature \| Clinical Justification |
| Step 7 — Subgroup Table | GitHub — male/female/age rows; Sensitivity colour-coded; Fairness column with OK/Review/⚠ |
| Bias Auto-Detection Banner | GitHub (submit URL) — red full-width banner appears when subgroup Sensitivity is >10pp below overall; hides otherwise |
| EU AI Act Checklist | GitHub (submit URL) — 8 items; 2 pre-checked; toggleable with visible completion progress |
| Training Data Chart | GitHub (submit URL) — training vs real population bars; amber warning if >15pp gap |
| AI Failure Case Studies | GitHub (submit URL) — 3 cards: red failure, amber near-miss, green prevention |
| PDF Certificate Generation | GitHub (submit URL) — POST /api/generate-certificate; includes active domain, model, 6 metrics, bias findings, checklist status; tested for at least 3 domains |
| Full Pipeline Test Report | PDF in GitHub Wiki (submit URL) — end-to-end Steps 1–7 with fresh CSV; all acceptance criteria verified |
| Weekly Progress Report | PDF in GitHub Wiki (submit URL) — velocity, demo screenshots, Sprint 5 carryovers |

## Week 9 Showcase Agenda (Wednesday, 5 min per group)

- Show Jira board and burndown.
- Demo Step 6: feature importance, top-3 clinical explanation, patient waterfall.
- Switch across 3 different domains and verify clinical sense-check banner changes correctly.
- Show what-if info banner changing probability.
- Instructor checks: clinical labels (not DB columns) and domain-specific explanation quality.
- Full Step 7 demo: subgroup table, bias banner trigger, EU AI Act checklist, failure case cards.
- Download and show generated certificate PDF.
- Instructor gate: full 7-step pipeline must run end-to-end; missing Steps 6/7 carry into Sprint 5 with penalty.

## Sprint 4 Metrics

| Metric | What to Measure | Target / Threshold |
|---|---|---|
| Bias Detection Accuracy | Test subgroup gap at exactly 10pp and 11pp | Banner hidden at ≤10pp; appears at >10pp |
| Checklist Toggle | Click all 8 items | All toggle correctly; 2 pre-checked on load |
| Certificate Content | Download certificates for 3 domains | Each PDF has correct domain, model, 6 metrics, bias findings, checklist status |
| Certificate Generation Time | POST /api/generate-certificate timing | < 10 seconds |
| End-to-End Flow | Steps 1–7 with fresh CSV, no reload | Zero crashes; gates (schemaOK, step locks) work correctly |
| Clinical Language Audit | Count labels using raw DB column names | 0 raw column names visible to end user |
| Domain Count (Steps 6–7) | Run Steps 6 and 7 for multiple domains | Explainability and bias tables update correctly for all 20 domains |
