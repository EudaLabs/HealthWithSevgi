# Sprint 4

**Duration:** Mar 31 – Apr 15, 2026
**Goal:** Step 6 (Explainability) and Step 7 (Ethics & Bias) fully functional

## Deliverables

| # | Deliverable | Format | Status |
|---|-------------|--------|--------|
| 1 | Working App — Steps 6–7 | GitHub + Live Demo | DONE |
| 2 | Step 6 Explainability Suite | Feature importance + clinical sense-check + patient waterfall + What-If | DONE |
| 3 | Step 7 Ethics & Bias Audit | Subgroup table + bias banner + EU AI Act checklist + representation chart + case studies | DONE |
| 4 | Domain Clinical Review | [[Domain Clinical Review]] | DONE |
| 5 | Sprint 4 Summary | This wiki page | DONE |
| 6 | Full Pipeline Test Report | [PDF](Sprint4_QA_Full_Pipeline_Test_Report.pdf) | DONE |
| 7 | Weekly Progress Report | [PDF](Sprint4_Weekly_Progress_Report.pdf) | DONE |

## Live Demo

- **Live Demo:** https://0xbatuhan4-healthwithsevgi.hf.space/
- **Hugging Face Space:** https://huggingface.co/spaces/0xBatuhan4/HealthWithSevgi
- **Docker:** `docker run -p 7860:7860 ghcr.io/eudalabs/healthwithsevgi:latest`

## Sprint 4 Burndown (Jira)

| Metric | Value |
|--------|-------|
| Sprint Duration | March 31 – April 15, 2026 |
| Total Issues | 26 (10 backlog stories + 16 new Sprint 4 stories) |
| Stories Completed | 26 / 26 |
| Points Completed | 117 SP |
| Points Remaining | 0 SP |
| Commits | 52 commits to main |
| Dev Completion | All Step 6 & Step 7 features delivered |

> **Note:** Sprint scope increased mid-sprint as QA test execution stories (US-042 to US-047) and ISO 42001 documentation stories were added. All development and QA work completed on schedule.

![Sprint 4 Burndown Chart](images/sprint4-burndown.jpg)

## Sprint 4 Metrics

| Metric | Target | Result |
|--------|--------|--------|
| Bias Detection Accuracy | Banner hidden at ≤10pp; shown at >10pp | Cardiology 25.2pp gap → visible; Neurology within threshold → hidden — PASS |
| Checklist Toggle | All 8 items toggle correctly; 2 pre-checked on load | 8 items, 2 pre-checked (Explainability + Data Transparency), all toggle — PASS |
| Certificate Content | Domain, model, 6 metrics, bias findings, checklist state | Verified for Cardiology and Neurology PDFs — PASS |
| Certificate Generation Time | < 10 seconds | 0.69s measured via curl — PASS |
| End-to-End Flow | Steps 1–7 with fresh CSV, no crashes | 3 domains tested (Cardiology, Neurology, Endocrinology) — PASS |
| Clinical Language Audit | 0 raw database column names visible | All feature labels use clinical display names — PASS |
| Domain Count (Steps 6–7) | All 20 domains update correctly | All 20 visible in selector, charts update on switch — PASS |
| QA Test Coverage | 100% of Sprint 4 scope has passing tests | 84/84 test cases — PASS |

## Step 6 — Explainability

### Features Delivered

- **SHAP-based global feature importance** — horizontal bars sorted descending, clinical names only, mean absolute SHAP values
- **Clinical sense-check banner** — top-feature explanation text with feature-specific clinical notes for high-impact measurements
- **Patient selector dropdown** — 3 representative test patients (low, medium, high risk)
- **Waterfall explanation chart** — red bars for risk-increasing features, green bars for risk-reducing features
- **Amber caution banner** — "These explanations show associations, not causation"
- **Blue What-If banner** — top-5 feature selector, new value input, instant probability shift simulation
- **Step navigation CTA** — Continue to Step 7 button after Step 6 review

### Step 6 Feature Details

| Feature | Implementation | Notes |
|---------|---------------|-------|
| Global Importance | Horizontal bar chart (Recharts), sorted descending | Top-5 cumulative explained variance shown as percentage |
| Clinical Names | `CLINICAL_NAME_MAP` — 100+ feature translations | e.g., `serum_creatinine` → "Serum Creatinine (mg/dL)" |
| Patient Sampling | Low-risk (min prob), Mid-risk (closest to 0.5), High-risk (max prob) | Auto-selected from test set |
| Waterfall | Top 8 SHAP features shown, expandable to 15 | Red = increases risk, Green = reduces risk |
| What-If | `predict_proba` for instant simulation | Handles feature scaling/inverse-transform |
| Caution Banner | Two variants — patient-level and page-bottom reminder | Yellow/amber background |

## Step 7 — Ethics & Bias

### Features Delivered

- **Subgroup performance table** — male, female, and age-group rows with colour-coded Accuracy, Sensitivity, Specificity, Precision, and F1
- **Fairness status column** — OK / Review / ⚠ Action Needed labels
- **Bias auto-detection banner** — red full-width alert when subgroup sensitivity is more than 10 percentage points below overall
- **EU AI Act checklist** — 8 items, 2 pre-completed, progress bar, and completion badge
- **Training data representation chart** — compares dataset gender balance against population norms; warns when gap exceeds 15pp
- **AI failure case studies** — three clinically framed cards with severity-coded styling
- **PDF certificate generator** — downloadable compliance summary for the currently active model/domain

### EU AI Act Checklist Items

| # | Item | Pre-Checked | Article |
|---|------|-------------|---------|
| 1 | Model Explainability | Yes | Art. 13 |
| 2 | Data Transparency | Yes | Art. 10 |
| 3 | Subgroup Bias Audit | No | Art. 10 |
| 4 | Human Oversight Plan | No | Art. 14 |
| 5 | Patient Data Privacy (GDPR) | No | Art. 10 |
| 6 | Post-Deployment Monitoring | No | Art. 72 |
| 7 | Incident Reporting Pathway | No | Art. 62 |
| 8 | Clinical Validation | No | Art. 43 |

### AI Failure Case Studies

| # | Title | Severity | Domain | Year |
|---|-------|----------|--------|------|
| 1 | Pulse Oximeter Bias in COVID-19 Patients | Failure (red) | Critical Care | 2020 |
| 2 | Sepsis Alert Algorithm Over-Alerting | Near Miss (amber) | ICU/Emergency | 2021 |
| 3 | Dermatology AI Underperforming on Dark Skin Tones | Prevention (green) | Dermatology | 2019 |

### Bias Thresholds

| Threshold | Value | Trigger |
|-----------|-------|---------|
| Sensitivity Gap | >10pp below overall | Red bias warning banner |
| Representation Gap | >15pp from population norm | Amber representation warning |
| Fairness — Action Needed | Sensitivity <50% OR gap >20pp | Red status badge |
| Fairness — Review | Gap >10pp OR any metric <65% | Amber status badge |
| Fairness — OK | All metrics meet thresholds | Green status badge |

### Subgroup Metric Colour Thresholds

| Metric | Green | Amber | Red |
|--------|-------|-------|-----|
| All metrics | ≥ 65% | 50–64% | < 50% |

## Domain Clinical Review

The clinical justification table for all 20 specialties is documented separately on [[Domain Clinical Review]]. That page supports the Step 6 clinical sense-check banner by showing why the top predictive feature in each domain is medically plausible.

## Sprint 4 Jira Stories

### Step 6 & Step 7 User Stories

| Story ID | Jira Key | Title | Assignee | Completed |
|----------|----------|-------|----------|-----------|
| US-020 | SCRUM-45 | View feature importance chart with clinical names | Batuhan Bayazıt | 2026-04-09 |
| US-021 | SCRUM-46 | View SHAP waterfall explanation for individual patient | Berat Mert | 2026-04-09 |
| US-022 | SCRUM-47 | View subgroup fairness performance table with bias alerts | Berat Mert | 2026-04-12 |
| US-023 | SCRUM-48 | Complete EU AI Act compliance checklist | Berfin Duru Alkan | 2026-04-12 |
| US-024 | SCRUM-49 | View training data representation chart vs. hospital population | Efe Çelik | 2026-04-12 |
| US-025 | SCRUM-50 | Download PDF summary certificate after completing all steps | Efe Çelik | 2026-04-13 |
| US-027 | SCRUM-57 | View real-world AI failure case studies in Step 7 | Efe Çelik | 2026-04-13 |
| US-029 | SCRUM-142 | Display correlation vs. causation disclaimer on Step 6 | Batuhan Bayazıt | 2026-04-09 |

### Sprint 4 Enhancement Stories

| Story ID | Jira Key | Title | Assignee | Completed |
|----------|----------|-------|----------|-----------|
| US-030 | SCRUM-199 | Interactive parallel coordinates chart for model comparison | Batuhan Bayazıt | 2026-04-12 |
| US-031 | SCRUM-200 | Sanitize inf/nan floats and optimize ML training pipeline | Berat Mert | 2026-04-12 |
| US-032 | SCRUM-201 | InsightService backend — LLM-powered clinical insights | Berat Mert | 2026-04-13 |
| US-033 | SCRUM-202 | AI clinical assessment UI and enriched ethics modals | Efe Çelik | 2026-04-14 |
| US-040 | SCRUM-209 | UI/UX design for model comparison chart & clinical insights UI | Burak Aydoğmuş | 2026-04-12 |

### QA Test Execution Stories

| Story ID | Jira Key | Title | Assignee | Completed |
|----------|----------|-------|----------|-----------|
| US-042 | SCRUM-211 | QA — Step 6 feature importance & clinical sense-check (TC-S4-001 to TC-S4-013) | Burak Aydoğmuş | 2026-04-15 |
| US-043 | SCRUM-212 | QA — Step 6 patient waterfall, what-if & domain coverage (TC-S4-014 to TC-S4-030) | Batuhan Bayazıt | 2026-04-15 |
| US-044 | SCRUM-213 | QA — Step 7 subgroup table & bias detection (TC-S4-031 to TC-S4-040) | Berat Mert | 2026-04-15 |
| US-045 | SCRUM-214 | QA — Step 7 EU AI Act checklist, representation & case studies (TC-S4-041 to TC-S4-054) | Efe Çelik | 2026-04-13 |
| US-046 | SCRUM-215 | QA — Certificate PDF validation & cross-step consistency (TC-S4-055 to TC-S4-069) | Berat Mert | 2026-04-15 |
| US-047 | SCRUM-216 | QA — End-to-end pipeline & deliverable verification (TC-S4-070 to TC-S4-084) | Berfin Duru Alkan | 2026-04-15 |

## Reports

| Report | Date | Format |
|--------|------|--------|
| [Sprint 4 QA Full Pipeline Test Report](Sprint4_QA_Full_Pipeline_Test_Report.pdf) | 15.04.2026 | PDF |
| [Sprint 4 Weekly Progress Report](Sprint4_Weekly_Progress_Report.pdf) | 15.04.2026 | PDF |

### Test Case Summary

- **TC-S4-001 to TC-S4-013:** Step 6 — Feature importance chart, clinical names, sorting, sense-check banner
- **TC-S4-014 to TC-S4-030:** Step 6 — Patient selector, waterfall chart, What-If analysis, domain coverage
- **TC-S4-031 to TC-S4-040:** Step 7 — Subgroup table, colour coding, fairness column, bias detection banner
- **TC-S4-041 to TC-S4-054:** Step 7 — EU AI Act checklist, representation chart, AI failure case studies
- **TC-S4-055 to TC-S4-069:** Certificate — PDF content validation, generation time, cross-step consistency
- **TC-S4-070 to TC-S4-084:** End-to-end — Full 7-step pipeline, domain switching, deliverable verification

## Key Technical Decisions

- **Clinical-first language** — all labels shown to the user use plain clinical names, never raw database column names
- **Fast What-If analysis** — probability shifts are calculated with `predict_proba` instead of recomputing SHAP values for every simulation
- **Three-patient sampling strategy** — low-risk, mid-risk, and high-risk examples provide meaningful contrast in waterfall explanations
- **Bias thresholding** — fairness alert uses a strict >10pp sensitivity gap rule; representation warning uses a >15pp demographic gap rule
- **Certificate payload** — PDF output includes the active domain, selected model, six core metrics, bias findings, and checklist completion state
- **LLM-powered insights** — MedGemma and Gemini integration for domain-specific clinical interpretations of model results

## Retrospective

### Keep
- 26 / 26 stories delivered; 117 SP cleared; all 84 QA test cases PASSed on the final run.
- Full Step 6 (Explainability) + Step 7 (Ethics & Bias) + downloadable PDF certificate shipped, with a live HuggingFace Spaces demo.
- Certificate generation measured at 0.69 s — well under the 10 s target.
- Clinical-language audit passed end-to-end: no raw database column names visible in the UI across all 20 specialties.
- Bias detection banner behaved correctly on both positive (Cardiology 25.2 pp gap) and negative (Neurology within threshold) cases — evidence the >10 pp rule generalises.

### Improve
- Same pattern as Sprint 3: QA stories (US-042 to US-047) and ISO 42001 documentation were added **mid-sprint**. This is now a repeating process issue, not a one-off.
- No formal submission-stabilisation buffer was planned — late feature work (US-032 InsightService, US-033 AI assessment UI) landed within 48 h of the deadline.
- Explainability "What-If" and LLM insights are unit-tested but have no dedicated regression test across all 20 specialties — coverage still depends on manual multi-domain runs.
- Meeting Notes page only contains Week 1; Sprint 4 stand-ups are unrecorded.

### Try
- Freeze new stories ≥ 48 h before the sprint deadline; anything later goes to the next sprint unless the PO formally approves it.
- At sprint planning, pair every dev story with its QA test-case story (continue the Sprint 3 action — it wasn't applied consistently here).
- Add an automated smoke test that iterates all 20 specialties through `/prepare` → `/train` → `/explain/global` → `/ethics` so multi-domain coverage is checked every PR.
- Ship a short Sprint 4 → Sprint 5 handoff note, and update [[Meeting Notes]] weekly for the remaining sprints.

## Deadline

Wednesday, April 15, 2026 — 13:00
