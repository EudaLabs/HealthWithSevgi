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
