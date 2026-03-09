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
