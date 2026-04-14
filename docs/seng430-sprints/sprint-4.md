# Sprint 4 Submission

- **Source URL:** https://webonline.cankaya.edu.tr/mod/assign/view.php?id=24497
- **Course:** B-SENG-430
- **Assignment:** SPRINT 4 SUBMISSION
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
| Clinical Sense-Check Banner | GitHub (submit URL) — domain-specific clinical sense-check text implemented for all 20 domains; correct text appears when switching domains |
| Patient Selector + Waterfall | GitHub (submit URL) — dropdown shows 3 test patients; waterfall bars in red (risk) / green (safe); plain-language labels |
| Caution and Info Banners | GitHub (submit URL) — amber caution: 'associations not causes'; blue what-if banner with probability shift |
| Domain Clinical Review | GitHub Wiki page (submit URL) — for each of the 20 domains, team documents why the top 3 predicted features make clinical sense. Organised as a table: Domain \| Top Feature \| Clinical Justification. |
| Step 7 — Subgroup Table | GitHub — rows for male/female/age groups; Sensitivity colour-coded; Fairness column with OK/Review/⚠ tags |
| Bias Auto-Detection Banner | GitHub (submit URL) — red full-width banner auto-appears when any subgroup Sensitivity is > 10 pp below overall; hides otherwise |
| EU AI Act Checklist | GitHub (submit URL) — 8 items; 2 pre-checked; clicking toggles; visually shows completion progress |
| Training Data Chart | GitHub (submit URL) — training vs. real population comparison bars; amber warning if > 15 pp gap in any group |
| AI Failure Case Studies | GitHub (submit URL) — 3 cards: 1 red failure, 1 amber near-miss, 1 green prevention; plain clinical language |
| PDF Certificate Generation | GitHub (submit URL) — POST /api/generate-certificate working; PDF includes the currently active domain, model, 6 metrics, bias findings, checklist status; tested for at least 3 different domains |
| Full Pipeline Test Report | PDF uploaded to GitHub Wiki (submit URL) — end-to-end test: Steps 1–7 with a fresh CSV; all acceptance criteria verified |
| Weekly Progress Report | PDF uploaded to GitHub Wiki (submit URL) — velocity, demo screenshots, any stories carried over to Sprint 5 |

## Week 9 Showcase Agenda (Wednesday, 5 min per group)

- Show Jira board and burndown.
- Demo Step 6: show feature importance chart, explain the top 3 features clinically, select a patient, and show waterfall bars.
- Switch between 3 different domains and show that the clinical sense-check banner text changes correctly for each.
- Show the what-if info banner changing probability.
- Instructor checks: Are feature names clinical (not database column names)? Does the clinical explanation change correctly across different domains?
- Full demo of Step 7: show subgroup table, trigger the bias banner (use manipulated data if needed), tick EU AI Act checklist items, and show failure case study cards.
- Click Download Certificate and show the generated PDF.
- Instructor gate: the full 7-step pipeline must work end-to-end. Groups missing Steps 6 or 7 carry stories into Sprint 5 with penalty.

## Sprint 4 Metrics

| Metric | What to Measure | Target / Threshold |
|---|---|---|
| Bias Detection Accuracy | Test with subgroup gap exactly at 10 pp and 11 pp | Banner hidden at ≤ 10 pp; appears at > 10 pp |
| Checklist Toggle | Click all 8 items | All toggle correctly; 2 are pre-checked on load |
| Certificate Content | Download certificate for 3 different domains | Each PDF shows the correct domain name, model, 6 metrics, bias findings, checklist status |
| Certificate Generation Time | POST /api/generate-certificate timing | < 10 seconds |
| End-to-End Flow | Steps 1–7 with a fresh CSV, no page reload | Zero crashes; all gates (schemaOK, step locks) work correctly |
| Clinical Language Audit | Count feature labels using database column names | 0 raw column names visible to end user |
| Domain Count (Steps 6–7) | Run Steps 6 and 7 for multiple domains | Explainability and bias tables update correctly for all 20 domains |

## Submission Status

| Field | Value |
|---|---|
| Submission status | No submissions have been made yet |
| Grading status | Not graded |
| Time remaining | 1 day remaining |
| Last modified | - |
| Submission comments | 0 comments |

## Available Action on Page

- Add submission
