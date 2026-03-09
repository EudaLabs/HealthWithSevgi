# SENG430 Sprint Documents

## Contents
- [Sprint 2](#sprint-2)
- [Sprint 3](#sprint-3)
- [Sprint 4](#sprint-4)
- [Sprint 5](#sprint-5)
- [Final Submission](#final-submission)

---

## Sprint 2

# Sprint 2 Submission

- **Source URL:** https://webonline.cankaya.edu.tr/mod/assign/view.php?id=24493
- **Opened:** Thursday, 19 February 2026, 12:00 AM
- **Due:** Wednesday, 18 March 2026, 1:00 PM

## Sprint Scope

**SPRINT 2**

First 3 steps of ML Visualisation Tool will be completed:

- Clinical Context
- Data Exploration
- Data Preparation

## Deliverables

| Artifact / Deliverable | Tool / Format |
|---|---|
| Working App — Steps 1–3 Complete | GitHub + live demo URL — all Step 2 right panel content; Column Mapper save gates Step 3; Step 3 controls all functional |
| Column Mapper Modal | GitHub — validate → save flow; schemaOK state gates navigation to Step 3; red blocked banner on bypass attempt |
| Step 3 Before/After Charts | GitHub — before/after normalisation bars; before/after SMOTE class balance bars; green success banner |
| Test Report — Sprint 2 | PDF uploaded to GitHub Wiki — manual test cases for all Step 2 + Step 3 user stories; pass/fail status per story |
| Progress Report | Weekly progress report with required sections |

## Weekly Progress Report — Required Sections

- Header: Group name, Week number, Scrum Master name, Date submitted, Domains implemented so far (cumulative count out of 20).
- Burndown Chart — screenshot from Jira showing remaining story points vs. ideal burndown line.
- Completed This Week — each user story ID + title + story points moved to Done.
- In Progress — each story currently in progress with % completion.
- Blocked / At Risk — blockers and resolution plan.
- Key Decisions Made — 2–3 sentences on technical/design decisions.
- Test Results — acceptance criteria status (Pass / Fail / Partial) with evidence screenshot.
- Metrics — current sprint metrics table.
- Next Week Plan — stories planned for next week with assignees.
- Retrospective Note (even weeks only) — 1 Keep, 1 Improve, 1 Try.

## Sprint 2 Metrics

| Metric | What to Measure | Target / Threshold |
|---|---|---|
| CSV Upload Success Rate | Test with 5 valid + 5 invalid files | 100% correct handling (accept valid, reject invalid with friendly error) |
| Column Mapper Gate | Attempt Step 3 before and after save | Step 3 blocked before save; accessible after save — 0 bypass bugs |
| Step 3 Controls | All 4 dropdowns + slider functional | All options selectable; apply button triggers API call |
| Domain Count (Step 1) | How many domains update Step 1 text correctly | All 20 domains return correct clinical context text |
| Test Coverage | User stories with passing test cases ÷ total done stories | 100% of completed stories have passing tests |

---

## Sprint 3

# Sprint 3 Submission

- **Source URL:** https://webonline.cankaya.edu.tr/mod/assign/view.php?id=24496
- **Opened:** Thursday, 19 February 2026, 12:00 AM
- **Due:** Wednesday, 1 April 2026, 12:00 AM

## Sprint Scope

**SPRINT 3: ML TOOL’S STEPS 4 (MODEL & PARAMETERS) – 5 (RESULTS)**

## Deliverables

| Artifact / Deliverable | Tool / Format |
|---|---|
| Sprint 3 Backlog (Jira) | Jira — Sprint 3 stories committed |
| 6-Model Tab Bar | GitHub — all 6 tabs render; clicking switches active tab; parameter panel shows/hides per model |
| Model Parameter Panel | GitHub — e.g. K slider (1–25); distance dropdown; KNN scatter canvas redraws on K change ≤ 16 ms; all model sliders/dropdowns functional; clinical plain-language tooltips |
| Auto-Retrain Toggle | GitHub — debounced API call after 300 ms on slider change; banner shows/hides correctly |
| Clinical Tooltip Review | GitHub Wiki — screenshot of each model's parameter tooltips; instructor reviews clinical accuracy |
| Step 5 Metrics | GitHub — all 6 metrics with colour thresholds (green/amber/red); clinical interpretation sentence per metric |
| Confusion Matrix | GitHub — 2×2 grid with TN/FP/FN/TP; colour coding; plain-language labels; FN red banner; FP info banner |
| ROC Curve | GitHub — SVG inline ROC curve; diagonal reference line; AUC annotated; explanatory note below chart |
| Low Sensitivity Danger Banner | GitHub — red banner auto-appears when Sensitivity < 50%; hides otherwise |
| Model Comparison Table | GitHub — + Compare adds row; Sensitivity column colour-coded; no duplicate rows |
| Test Report — Sprint 3 | PDF uploaded to GitHub Wiki — test cases for all Step 4 + Step 5 stories; performance timing tests (model train < 3s) |
| Weekly Progress Report | Same structure as Sprint 2 |

## Week 5 Showcase Agenda (Wednesday, 5 min per group)

- Show Jira Sprint 3 board and burndown chart.
- Full demo: train KNN → metrics update → confusion matrix → ROC curve → switch to Random Forest → + Compare → comparison table.
- Trigger Low Sensitivity danger banner (e.g., high K or bad split).
- Instructor gate: all 6 models must train successfully and all 6 metrics must update before Sprint 4.
- Instructor checks: KNN canvas redraw smoothness and plain clinical language in tooltips.

## Sprint 3 Metrics

| Metric | What to Measure | Target / Threshold |
|---|---|---|
| Model Training Latency | POST /api/train response time | < 3,000 ms for dataset ≤ 50,000 rows |
| Slider Debounce | Time from slider release to API call | 300 ms ± 50 ms |
| KNN Canvas Redraw | Time from K change to canvas repaint | ≤ 16 ms (single animation frame) |
| Danger Banner Trigger | Sensitivity < 50% scenario tested | Banner appears; hides when Sensitivity ≥ 50% |
| Metric Colour Thresholds | All 6 metrics tested at boundary values | Green/amber/red correct for all 6 metrics |
| Comparison Table | Add 6 models one by one | No duplicates; Sensitivity colour-coded correctly |
| Domain Switching (Steps 4–5) | Switch domain, retrain, check metrics update | Results/metrics update correctly for at least 5 domains tested |

---

## Sprint 4

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

---

## Sprint 5

# Sprint 5 Submission

- **Source URL:** https://webonline.cankaya.edu.tr/mod/assign/view.php?id=24498
- **Opened:** Thursday, 19 February 2026, 12:00 AM
- **Due:** Wednesday, 29 April 2026, 1:00 PM

## Sprint Scope

**SPRINT 5**

Polish, User Testing

Usability testing · Performance · Docker · Accessibility · Final jury presentation

## User Testing Protocol

Each group must conduct a structured usability test. The participant must be a non-computer-science person with university-level education. The test must be completed independently (no coaching during the task).

### Required Tasks

| Task | What the Participant Must Do | Success Criterion | Time Limit |
|---|---|---|---|
| T1 | Open the tool, locate the domain pill bar, switch between two different medical specialties | Correct pills clicked; Step 1 updates for each; no errors | 90 sec |
| T2 | Upload sample CSV and open Column Mapper | CSV accepted and Column Mapper opens without error | 3 min |
| T3 | Complete Column Mapper validation and proceed to Step 3 | Save clicked; green banner appears; Step 3 opens | 2 min |
| T4 | Apply preparation settings in Step 3 and move to Step 4 | Apply clicked; green success banner appears; Step 4 opens | 3 min |
| T5 | Train a KNN model and find Sensitivity score in Step 5 | Correct Sensitivity value and colour identified | 3 min |
| T6 | Find top patient measurement influence in Step 6 | Top feature in importance chart identified | 2 min |
| T7 | Download Summary Certificate | PDF downloads successfully | 1 min |

## Week 10 Deliverables

| Artifact / Deliverable | Tool / Format | Owner |
|---|---|---|
| Sprint 5 Backlog (Jira) | Jira — remaining bugs, polish tasks, user testing stories, Docker story, documentation stories | Scrum Master |
| User Testing Report | PDF — participant profile, 7-task completion table, failure notes, participant quotes, SUS score | QA/Docs Lead |
| Signed Consent Forms | PDF — participant consent for video/observation (can be anonymised) | QA/Docs Lead |
| Usability Test Video | MP4 (max 5 min) — participant completes T1–T7 | QA/Docs Lead |
| Lighthouse Report Screenshot | PNG/PDF — Performance, Accessibility, Best Practices, SEO scores | Lead Developer |
| Accessibility Fix Log | GitHub Wiki — violations found and how each was fixed | Lead Developer |
| Bug Fix Log | Jira — Sprint 4 retrospective bugs closed/documented | Lead Developer |
| Week 9 Progress Report | PDF in GitHub Wiki — burndown, user testing status, performance scores, Docker status | Scrum Master |

## Week 10 Showcase Agenda (Wednesday, 5 min per group)

- Show 3-minute excerpt from usability test video and report independent task completion count.
- Show Lighthouse performance and accessibility scores.
- Show one accessibility fix before/after.
- Run `docker-compose up` live and show app loading.
- Instructor checks: real non-CS participant completed Steps 1–5 unassisted; Lighthouse score ≥ 80.

## Sprint 5 Metrics

| Metric | What to Measure | Target / Threshold |
|---|---|---|
| Usability Task Completion | T1–T7 completed by non-CS participant | ≥ 5/7 tasks independently within time limits |
| SUS Score | System Usability Scale (10-question form) | ≥ 68 |
| Lighthouse Performance | Production build audit | ≥ 80 |
| Lighthouse Accessibility | Accessibility audit | ≥ 85 |
| Docker Startup | `docker-compose up` timing | App fully loaded within 30 seconds |
| End-to-End Regression | Steps 1–7 with 3 different CSV files | Zero crashes across all 3 runs |
| Code Documentation | Functions with JSDoc/docstrings ÷ total functions | ≥ 80% documented |
| Full Domain Coverage | End-to-end test of all 20 domains | All 20 domains complete full pipeline without errors |

---

## Final Submission

# Final Submission & Jury Showcase

- **Source URL:** https://webonline.cankaya.edu.tr/mod/assign/view.php?id=24499
- **Opened:** Thursday, 19 February 2026, 12:00 AM
- **Due:** Tuesday, 5 May 2026, 11:59 PM

## Week 11 Scope

**Final Submission & Jury Showcase**

## Final Submission Checklist

| Final Deliverable | Format / Location |
|---|---|
| Working web application — all 7 steps functional, no crashes | Live URL or `docker-compose up` |
| GitHub repository — clean code, commented, README + SETUP.md complete | GitHub link |
| Docker image — `docker-compose up` starts app without errors | Docker Hub or GitHub Packages |
| 2-page project report — architecture, decisions, challenges, lessons learned | PDF uploaded to GitHub |
| Jira board — full sprint history, velocity charts, all stories with status | Jira link (read access) |
| Figma wireframes + prototype — all 7 steps designed | Figma link |
| GitHub Wiki — architecture, API docs, all sprint reviews, retros | GitHub Wiki link |
| User testing evidence — report + video + consent forms | PDF + MP4 in GitHub repo |
| Test reports — all 4 sprints; pass/fail per user story | PDFs in GitHub Wiki |
| Final jury presentation — 10-min live demo to HEALTH-AI panel | In-class presentation |

## Final Jury Presentation Format (10 minutes per group)

| Time | Content | Format |
|---|---|---|
| 0:00 | Team introduction — members, roles, and overview (20 domains, 7 steps, 6 models) | Slide |
| 1:00 | Live demo — full Steps 1–7; switch at least 3 domain pills; no errors | Live app |
| 5:00 | Results interpretation — explain best model's Sensitivity in clinical terms | Slide + app |
| 7:00 | Bias finding — show subgroup table and explain disparities | Live app |
| 8:00 | What we learned — technical lessons | Slide |
| 9:00 | Q&A from jury panel | Open |

---

