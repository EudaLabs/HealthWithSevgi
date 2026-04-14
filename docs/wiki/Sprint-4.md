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
| 6 | Full Pipeline Test Report | [PDF](../seng430-sprints/Sprint4_QA_Full_Pipeline_Test_Report.pdf) | DONE |
| 7 | Weekly Progress Report | [HTML](../reports/Sprint4_Weekly_Progress_Report.html) | DONE |

## Live Demo

- **Live Demo:** https://0xbatuhan4-healthwithsevgi.hf.space/
- **Hugging Face Space:** https://huggingface.co/spaces/0xBatuhan4/HealthWithSevgi
- **Docker:** `docker run -p 7860:7860 ghcr.io/eudalabs/healthwithsevgi:latest`

## Sprint 4 Metrics

| Metric | Target | Result |
|--------|--------|--------|
| Bias Detection Accuracy | Banner hidden at ≤10pp sensitivity gap; shown at >10pp | PASS |
| Checklist Toggle | All 8 items toggle correctly; 2 pre-checked on load | PASS |
| Certificate Content | Domain, model, 6 metrics, bias findings, checklist state included | PASS |
| Certificate Generation Time | < 10 seconds | PASS |
| End-to-End Flow | Steps 1–7 run with fresh CSV and no crashes | PASS |
| Clinical Language Audit | No raw database column names visible to the end user | PASS |
| Domain Count (Steps 6–7) | Explainability and ethics outputs update across all 20 domains | PASS |

## Step 6 — Explainability

### Features Delivered

- **SHAP-based global feature importance** — horizontal bars sorted descending, clinical names only, importance values 0.00–1.00
- **Clinical sense-check banner** — domain-specific top-feature explanation text that updates across all 20 medical specialties
- **Patient selector dropdown** — 3 representative test patients (low, medium, high risk)
- **Waterfall explanation chart** — red bars for risk-increasing features, green bars for risk-reducing features
- **Amber caution banner** — “These explanations show associations, not causation”
- **Blue What-If banner** — top-5 feature selector, new value input, instant probability shift simulation
- **Step navigation CTA** — Continue to Step 7 button after Step 6 review

## Step 7 — Ethics & Bias

### Features Delivered

- **Subgroup performance table** — male, female, and age-group rows with colour-coded Accuracy, Sensitivity, Specificity, Precision, and F1
- **Fairness status column** — OK / Review / ⚠ Action Needed labels
- **Bias auto-detection banner** — red full-width alert when subgroup sensitivity is more than 10 percentage points below overall
- **EU AI Act checklist** — 8 items, 2 pre-completed, progress bar, and completion badge
- **Training data representation chart** — compares dataset gender balance against population norms; warns when gap exceeds 15pp
- **AI failure case studies** — three clinically framed cards with severity-coded styling
- **PDF certificate generator** — downloadable compliance summary for the currently active model/domain

## Domain Clinical Review

The clinical justification table for all 20 specialties is documented separately on [[Domain Clinical Review]]. That page supports the Step 6 clinical sense-check banner by showing why the top predictive feature in each domain is medically plausible.

## Key Technical Decisions

- **Clinical-first language** — all labels shown to the user use plain clinical names, never raw database column names
- **Fast What-If analysis** — probability shifts are calculated with `predict_proba` instead of recomputing SHAP values for every simulation
- **Three-patient sampling strategy** — low-risk, mid-risk, and high-risk examples provide meaningful contrast in waterfall explanations
- **Bias thresholding** — fairness alert uses a strict >10pp sensitivity gap rule; representation warning uses a >15pp demographic gap rule
- **Certificate payload** — PDF output includes the active domain, selected model, six core metrics, bias findings, and checklist completion state

## Documentation Status

- **Wiki pages completed:** Sprint 4 summary, Domain Clinical Review
- **Reports intentionally deferred for now:** Full Pipeline Test Report PDF, Weekly Progress Report PDF

## Deadline

Wednesday, April 15, 2026 — 13:00
