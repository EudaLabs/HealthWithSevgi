# HealthWithSevgi — Jira Product Backlog Report

> **Project:** HealthWithSevgi (SCRUM)
> **Course:** SENG 430 · Software Quality Assurance — Çankaya University Spring 2025-2026
> **Instructor:** Dr. Sevgi Koyuncu Tunç
> **Report Date:** 2026-02-24
> **Status:** 🟡 Sprint 1 — Backlog Setup Complete, Development Not Started

---

## Project Overview

An interactive, browser-based ML learning tool that guides healthcare professionals through a **7-step pipeline** — from choosing a medical specialty to training an AI model and auditing it for fairness — with no coding required.

**Tech Stack:** React 18 + Vite (Frontend) · FastAPI (Backend) · scikit-learn (ML Engine)

**Team:**

| Role | Name | Student ID |
|------|------|------------|
| Product Owner + Developer | Efe Çelik | 202128016 |
| UX Designer | Burak Aydoğmuş | 202128028 |
| Lead Developer + Scrum Master | Batuhan Bayazıt | 202228008 |
| Developer | Berat Mert Gökkaya | 202228019 |
| QA / Documentation Lead | Berfin Duru Alkan | 202228005 |

---

## Backlog Metrics

| Metric | Value |
|--------|-------|
| Total Epics | 8 |
| Total User Stories | 25 |
| Must Have stories | 14 |
| Should Have stories | 9 |
| Could Have stories | 1 |
| Won't Have stories | 0 |
| Total Story Points | 102 |
| Must Have points | 55 |
| Should Have points | 42 |
| Could Have points | 5 |
| Stories in To Do | 25 |
| Stories In Progress | 0 |
| Stories Done | 0 |

---

## Epic Breakdown

| Key | Epic | Jira Key | Stories | Points |
|-----|------|----------|---------|--------|
| E0 | Step 0: Medical Specialty Selection | SCRUM-17 | 2 | 5 |
| E1 | Step 1: Clinical Context | SCRUM-18 | 1 | 2 |
| E2 | Step 2: Data Exploration | SCRUM-19 | 4 | 16 |
| E3 | Step 3: Data Preparation | SCRUM-20 | 4 | 14 |
| E4 | Step 4: Model Selection & Configuration | SCRUM-21 | 4 | 15 |
| E5 | Step 5: Results & Evaluation | SCRUM-22 | 4 | 13 |
| E6 | Step 6: Explainability | SCRUM-23 | 2 | 13 |
| E7 | Step 7: Ethics & Bias | SCRUM-24 | 4 | 23 |
| **Total** | | | **25** | **101** |

---

## Full Product Backlog

### Epic: Step 0 — Medical Specialty Selection (SCRUM-17)

| ID | Summary | Priority | Points | Status |
|----|---------|----------|--------|--------|
| US-001 | Select medical specialty from pill bar | Must Have | 3 | To Do |
| US-002 | Confirm before switching specialty to prevent progress loss | Should Have | 2 | To Do |

**Acceptance Criteria highlights:**
- US-001: Given on home screen, When 'Cardiology' clicked, Then domain label updates and Step 1 shows heart failure content.
- US-002: Given pipeline started, When different specialty clicked, Then confirmation dialog shown before reset.

---

### Epic: Step 1 — Clinical Context (SCRUM-18)

| ID | Summary | Priority | Points | Status |
|----|---------|----------|--------|--------|
| US-003 | View clinical context for selected specialty | Must Have | 2 | To Do |

**Acceptance Criteria highlights:**
- US-003: Given specialty selected, When on Step 1, Then medical condition, patient population, and target outcome shown in plain clinical language.

---

### Epic: Step 2 — Data Exploration (SCRUM-19)

| ID | Summary | Priority | Points | Status |
|----|---------|----------|--------|--------|
| US-004 | Upload own CSV patient file | Must Have | 5 | To Do |
| US-005 | Use built-in example dataset for selected specialty | Must Have | 3 | To Do |
| US-006 | View column summary with missing value indicators | Must Have | 3 | To Do |
| US-007 | Map target column using Column Mapper modal | Must Have | 5 | To Do |

**Acceptance Criteria highlights:**
- US-004: Given valid CSV dragged, Then filename, size, column count shown with green banner.
- US-007: Given Column Mapper saved, Then Step 3 unlocks; without save, Step 3 stays locked.

---

### Epic: Step 3 — Data Preparation (SCRUM-20)

| ID | Summary | Priority | Points | Status |
|----|---------|----------|--------|--------|
| US-008 | Configure training and test data split ratio | Must Have | 3 | To Do |
| US-009 | Select missing value imputation strategy | Must Have | 3 | To Do |
| US-010 | Select normalisation method for patient measurements | Must Have | 3 | To Do |
| US-011 | Apply SMOTE to handle class imbalance in training data | Should Have | 5 | To Do |

**Acceptance Criteria highlights:**
- US-008: Given split slider moved, Then training % + test % always sum to 100%.
- US-011: Given SMOTE enabled, Then synthetic samples added to training set only, never test set.

---

### Epic: Step 4 — Model Selection & Configuration (SCRUM-21)

| ID | Summary | Priority | Points | Status |
|----|---------|----------|--------|--------|
| US-012 | Select ML model type for training | Must Have | 3 | To Do |
| US-013 | Tune model hyperparameters via interactive sliders | Must Have | 5 | To Do |
| US-014 | Toggle auto-retrain on hyperparameter change | Should Have | 2 | To Do |
| US-015 | Compare multiple trained models side by side | Should Have | 5 | To Do |

**Acceptance Criteria highlights:**
- US-013: Given KNN + Auto-Retrain on, When K slider moved, Then canvas redraws ≤16 ms, metrics update ≤300 ms.
- US-015: Given model trained, When '+ Compare' clicked, Then model added to comparison table with best metric highlighted.

---

### Epic: Step 5 — Results & Evaluation (SCRUM-22)

| ID | Summary | Priority | Points | Status |
|----|---------|----------|--------|--------|
| US-016 | View six performance metrics after model training | Must Have | 5 | To Do |
| US-017 | View confusion matrix with plain clinical labelling | Must Have | 3 | To Do |
| US-018 | View ROC curve for model discrimination ability | Should Have | 3 | To Do |
| US-019 | Display low sensitivity warning banner automatically | Should Have | 2 | To Do |

**Acceptance Criteria highlights:**
- US-016: Given training complete, Then Accuracy, Sensitivity, Specificity, Precision, F1, AUC shown with green/amber/red thresholds.
- US-019: Given Sensitivity < 50%, Then red warning banner appears recommending return to Step 4.

---

### Epic: Step 6 — Explainability (SCRUM-23)

| ID | Summary | Priority | Points | Status |
|----|---------|----------|--------|--------|
| US-020 | View feature importance chart with clinical names | Must Have | 5 | To Do |
| US-021 | View SHAP waterfall explanation for individual patient | Should Have | 8 | To Do |

**Acceptance Criteria highlights:**
- US-020: Given model trained, Then features ranked by importance using clinical names, with a sense-check note.
- US-021: Given patient selected, Then SHAP waterfall shows red (high-risk) and green (low-risk) bars in plain language.

---

### Epic: Step 7 — Ethics & Bias (SCRUM-24)

| ID | Summary | Priority | Points | Status |
|----|---------|----------|--------|--------|
| US-022 | View subgroup fairness performance table with bias alerts | Must Have | 8 | To Do |
| US-023 | Complete EU AI Act compliance checklist | Must Have | 5 | To Do |
| US-024 | View training data representation chart vs. hospital population | Could Have | 5 | To Do |
| US-025 | Download PDF summary certificate after completing all steps | Should Have | 5 | To Do |

**Acceptance Criteria highlights:**
- US-022: Given any subgroup Sensitivity > 10 pts below average, Then red bias banner auto-appears.
- US-023: Given Step 7 open, Then 8 checklist items shown, 2 pre-checked (Explainability + Data Source).
- US-025: Given Step 7 reached, When 'Download Certificate' clicked, Then PDF generated ≤10 seconds.

---

## MoSCoW Priority Summary

### Must Have (14 stories — 55 pts)
US-001, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-012, US-013, US-016, US-017, US-020, US-022, US-023

### Should Have (9 stories — 42 pts)
US-002, US-011, US-014, US-015, US-018, US-019, US-021, US-025

### Could Have (1 story — 5 pts)
US-024

### Won't Have
None defined for Sprint 1.

---

## Sprint 1 Deliverables Tracker

| # | Deliverable | Status | Owner |
|---|-------------|--------|-------|
| 1 | Team Charter | Pending | All |
| 2 | Domain Coverage Plan (20 domains PDF) | Pending | Product Owner |
| 3 | Jira Product Backlog (≥20 user stories) | ✅ Done | Product Owner |
| 4 | User Story Standards (Gherkin AC) | ✅ Done | Product Owner |
| 5 | GitHub Repository (README + SETUP) | ✅ Done | Lead Developer |
| 6 | GitHub Wiki — Home Page | Pending | QA Lead |
| 7 | Sprint 1 Backlog (sprint created in Jira) | Pending | Scrum Master |
| 8 | Figma Wireframes — All 7 Steps | Pending | UX Designer |
| 9 | Architecture Diagram | Pending | Lead Developer |

**Sprint 1 Deadline:** Wednesday, 4 March 2026 at 1:00 PM — No late submissions.

---

## Jira Board

**Project:** HealthWithSevgi
**Board:** [https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards](https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards)

**Branch naming convention:** `feature/US-XXX`
