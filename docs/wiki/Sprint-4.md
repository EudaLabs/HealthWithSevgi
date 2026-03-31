# Sprint 4 Summary

**Project:** HealthWithSevgi — A clinical ML model selection and evaluation platform

**Duration:** March 31 – April 15, 2026

**Status:** All code deliverables completed on schedule

## Core Achievements

The team delivered a complete explainability and ethics pipeline covering Steps 6 and 7 of the clinical ML wizard. Step 6 provides SHAP-based global feature importance with clinical display names (never raw column names), single-patient waterfall explanations with plain-language risk factors, and a What-If analysis tool that simulates changing a clinical measurement to show how the predicted probability shifts in real time.

Step 7 implements a comprehensive fairness audit: subgroup performance tables broken down by gender and age, automatic bias detection that surfaces a red full-width banner when any subgroup's sensitivity falls more than 10 percentage points below overall, and training data representation charts comparing dataset demographics against population norms with amber warnings when gaps exceed 15 percentage points.

An EU AI Act compliance checklist with 8 items (2 pre-checked) lets users track regulatory requirements, and a PDF certificate generator produces downloadable compliance documents including domain, model type, six performance metrics, bias findings, and checklist status.

## Step 6 — Explainability

- SHAP-based global feature importance chart — horizontal bars sorted descending, clinical names only, importance values 0.00–1.00
- Clinical sense-check banner — domain-specific top-feature explanation text that updates when switching between all 20 medical specialties
- Patient selector dropdown — 3 representative test patients (low, medium, high risk) with automatic SHAP waterfall generation on selection
- Waterfall chart — bars colour-coded red (increases risk) and green (decreases risk) with plain-language labels
- Amber caution banner — "These explanations show associations, not causation"
- Blue What-If info banner — feature dropdown (top 5 by importance), new value input, Simulate button, probability shift display with directional colour coding
- Continue to Step 7 CTA button

## Step 7 — Ethics & Bias

- Subgroup performance table — Male, Female, and age-group rows; Accuracy, Sensitivity, Specificity, Precision, F1 all colour-coded; Fairness column showing OK / Review / ⚠ Action Needed
- Bias auto-detection banner — red full-width alert when subgroup sensitivity is >10pp below overall; hidden when all groups are within threshold
- EU AI Act checklist — 8 items, 2 auto-completed (explainability, data source), 6 toggleable; progress bar and "All complete" badge
- Training data representation chart — grouped bars comparing dataset gender distribution vs. population norms; amber warning alerts below the chart when any group deviates by >15pp
- AI failure case studies — 3 cards with severity-coded borders and badges: Pulse Oximeter Bias (red — failure), Sepsis Alert Over-Alerting (amber — near-miss), Dermatology AI Skin Tone Bias (green — prevention)
- PDF certificate download — POST /api/generate-certificate; tested across 3+ domains; includes all required sections

## Quality Metrics

Backend test suite expanded to 178 test cases, all passing. Three new test files cover Step 6 explainability (global importance, patient explanation, What-If, sample patients), Step 7 ethics (subgroup metrics, bias detection, checklist toggle, representation warnings, case study severity), and certificate generation (PDF output, content type, magic bytes, checklist state).

Frontend builds with zero errors and zero TypeScript type warnings.

## Technical Highlights

"What-If uses predict_proba only" — rather than recalculating SHAP values for each simulation (which would take seconds), the What-If endpoint copies the patient's feature vector, replaces a single value, and calls model.predict_proba directly for instant response suitable for live demo.

Sample patients are selected by risk stratification — the lowest probability patient (low risk), the patient closest to 0.5 (medium risk), and the highest probability patient (high risk) — providing meaningful clinical contrast in the dropdown.

Bias detection uses a strict >10pp sensitivity gap threshold aligned with clinical fairness literature, while training data representation uses a separate >15pp gap threshold against population norms.

**Live deployment:** HuggingFace Spaces and Docker container available
