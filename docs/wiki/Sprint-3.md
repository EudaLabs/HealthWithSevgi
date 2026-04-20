# Sprint 3

**Duration:** Mar 19 – Mar 30, 2026
**Goal:** Step 4 (Model Selection & Parameter Tuning) and Step 5 (Results & Performance Metrics) fully functional

## Deliverables

| # | Deliverable | Format | Status |
|---|-------------|--------|--------|
| 1 | Working App — Steps 4–5 | GitHub + Live Demo | DONE |
| 2 | 8 ML Model Tabs with Parameter Controls | KNN, SVM, DT, RF, LR, NB, XGBoost, LightGBM | DONE |
| 3 | Step 5 Performance Dashboard | Metrics, Confusion Matrix, ROC, PR, Comparison | DONE |
| 4 | Test Report — Sprint 3 | DOCX — 46 test cases, all PASS | DONE |
| 5 | Progress Report | Screenshot-Based Demonstration Report | DONE |

## Live Demo

- **HuggingFace Space:** https://huggingface.co/spaces/0xBatuhan4/HealthWithSevgi
- **Docker:** `docker run -p 7860:7860 ghcr.io/eudalabs/healthwithsevgi:latest`

## Sprint 3 Burndown (Jira)

| Metric | Value |
|--------|-------|
| Sprint Duration | March 19 – March 30, 2026 |
| Total Issues | 90 (56 Stories, 29 Tasks, 5 Bugs) |
| Points Completed | 28 SP |
| Points Remaining | 62 SP |
| Scope Change | +62 SP (53 tickets added, 3 removed, 33 modified) |
| Done | 49 issues |
| In Progress | 34 issues — QA test case verification |
| Dev Completion | All Step 4 & Step 5 features delivered |

> **Note:** Burndown shows scope increase because 46 QA test case tickets were created mid-sprint. All development work completed on schedule.

![Sprint 3 Burndown Chart](images/burndown-chart.png)

## Sprint 3 Metrics

| Metric | Target | Result |
|--------|--------|--------|
| Model Tab Count | Minimum 6 ML algorithms | 8 models — PASS |
| Parameter Controls | Each model has relevant sliders/radios | All 8 — PASS |
| Clinical Tooltips | Plain language, no raw ML jargon | All models — PASS |
| Auto-Retrain Debounce | Single API call on rapid changes | 300ms debounce — PASS |
| Training Latency | < 3 seconds per model | All under 3s — PASS |
| Performance Metrics | 6 color-coded cards with clinical interpretation | All 6 — PASS |
| Confusion Matrix | 2x2 with TN/FP/FN/TP labels and color coding | PASS |
| ROC Curve | SVG chart with AUC badge and reference line | PASS |
| Multi-Domain | Results update correctly on domain switch | 3 domains tested — PASS |
| Test Coverage | 100% of completed stories have passing tests | 46/46 — PASS |

## Step 4 — Model Selection & Parameter Tuning

### 8 ML Algorithm Tabs

| Model | Parameters | Notes |
|-------|-----------|-------|
| KNN | K slider (1–25), Distance metric (euclidean/manhattan) | Decision boundary visualization |
| SVM | Kernel (rbf/linear/poly/sigmoid), C slider | 4 kernel options |
| Decision Tree | Max depth (1–20), Criterion (gini/entropy) | |
| Random Forest | Number of trees (10–500), Max depth (1–20) | |
| Logistic Regression | C regularisation, Max iterations | |
| Naive Bayes | Pre-set variance smoothing (1e-10) | Informational only |
| XGBoost | Learning rate, Max depth, N estimators | Gradient boosting |
| LightGBM | Learning rate, Max depth, N estimators | Light gradient boosting |

![KNN Parameters](images/01-KNN-params.png)
![SVM Parameters](images/02-SVM-params.png)
![Decision Tree Parameters](images/03-DecisionTree-params.png)
![Random Forest Parameters](images/04-RandomForest-params.png)
![Logistic Regression Parameters](images/05-LogisticRegression-params.png)
![Naive Bayes Parameters](images/06-NaiveBayes-params.png)
![XGBoost Parameters](images/07-XGBoost-params.png)
![LightGBM Parameters](images/08-LightGBM-params.png)

### Key Features

- **Auto-Retrain Toggle:** ON by default, debounced at 300ms
- **KNN Decision Boundaries:** Canvas-based PCA scatter plot, redraws on K change
- **Model Comparison Table:** "+ Compare" button, sorted by AUC-ROC, "Best" badge, duplicate prevention
- **Clinical PARAM_HINTS:** Inline plain-language descriptions for every model

## Step 5 — Results & Performance Metrics

### 6 Performance Metric Cards

| Metric | Color Thresholds | Clinical Note |
|--------|-----------------|---------------|
| Accuracy | Green ≥ 65%, Amber ≥ 50%, Red < 50% | Overall correctness |
| Sensitivity | Green ≥ 70%, Amber ≥ 50%, Red < 50% | "Most important for screening" |
| Specificity | Green ≥ 65%, Amber ≥ 50%, Red < 50% | Avoiding false alarms |
| Precision | Green ≥ 60%, Amber ≥ 50%, Red < 50% | Positive predictive value |
| F1 Score | Green ≥ 65%, Amber ≥ 50%, Red < 50% | Balance of precision & sensitivity |
| AUC-ROC | Green ≥ 75%, Amber ≥ 60%, Red < 60% | Overall discrimination |

### Key Features

- **Confusion Matrix:** 2x2 grid with clinical labels — "Correctly called safe" (TN), "Unnecessary alarm" (FP), "MISSED — most dangerous" (FN), "Correctly flagged" (TP)
- **FN Danger Banner:** Red alert — "False Negatives are the most dangerous errors in clinical screening"
- **FP Info Banner:** Green info — unnecessary alarms explanation
- **Low Sensitivity Warning:** Triggered when sensitivity < 50%
- **ROC Curve:** Inline SVG (Recharts), diagonal reference line, AUC badge
- **PR Curve:** Precision-Recall curve with baseline reference
- **Training vs Test Accuracy:** Comparison chart with overfitting detection
- **Model Strengths & Improvements:** Auto-generated recommendations

### Multi-Domain Test Results

| Domain | Model | Accuracy | Sensitivity | AUC-ROC |
|--------|-------|----------|-------------|---------|
| Cardiology (Heart Failure) | KNN | 75.0% | 89.5% | 0.78 |
| Endocrinology (Diabetes) | RF | 75.3% | 81.5% | 0.82 |
| Neurology (Parkinson's) | RF | 92.3% | 96.5% | 0.95 |

## Reports

| Report | Date | Format |
|--------|------|--------|
| [Sprint 3 Weekly Progress Report](Sprint3_Weekly_Progress_Report.pdf) | 30.03.2026 | PDF |
| [Sprint 3 QA Report — 46 Test Cases](Sprint3_QA_Test_Cases.pdf) | 30.03.2026 | PDF |

### Test Case Summary

- **TC-S3-001 to TC-S3-012:** Step 4 UI — model tabs, parameter controls, tooltips
- **TC-S3-013 to TC-S3-017:** Auto-retrain toggle, debounce, loading states
- **TC-S3-018 to TC-S3-022:** KNN visualization, all models training, model switching
- **TC-S3-023 to TC-S3-028:** Step 5 metrics — 6 cards, color thresholds, clinical text
- **TC-S3-029 to TC-S3-033:** Confusion matrix, FN/FP banners
- **TC-S3-034 to TC-S3-040:** ROC curve, AUC annotation, sensitivity warnings
- **TC-S3-041 to TC-S3-046:** Comparison table, multi-domain testing

## Key Technical Decisions

- **8 models instead of 6** — Exceeded sprint spec; added XGBoost and LightGBM for gradient boosting coverage
- **Debounced auto-retrain** — 300ms debounce prevents API spam during rapid slider changes
- **Canvas-based decision boundaries** — KNN only; PCA projection for 2D visualization
- **Clinical-first language** — All tooltips and metric explanations written for non-technical healthcare users
- **Color-coded thresholds** — Green/amber/red system with clinically meaningful cutoffs

## Retrospective

### Keep
- Delivered **8** ML models — sprint spec was 6. XGBoost and LightGBM were added as stretch goals and still shipped with clinical tooltips and comparison-table support.
- Debounced auto-retrain (300 ms) held latency under 3 s per model across all 8 algorithms — every performance target PASSed.
- All 46 QA test cases passed; colour-coded metric thresholds and the FN/FP danger banners landed without rework.
- Multi-domain verification done on 3 domains (Cardiology, Endocrinology, Neurology) — early evidence the pipeline is truly domain-agnostic.

### Improve
- Mid-sprint scope change of **+62 SP** (53 tickets added, 3 removed, 33 modified) because 46 QA test-case tickets were created after the sprint started — the burndown chart no longer tells a useful story.
- Dev stories and QA stories were treated as separate planning phases instead of being paired at sprint planning, which is what produced the scope blow-up.
- Decision-boundary visualisation is still KNN-only; other models had no viz work planned, so Step 4 feels uneven between tabs.

### Try
- At sprint planning, every dev user story gets a paired QA test-case story created **in the same session** — no post-hoc QA ticket creation.
- Freeze sprint scope at the end of planning; any new tickets go to the backlog until the next sprint.
- Track two burndowns — dev-only and dev+QA — so scope changes from QA don't hide development progress.

## Deadline

Sunday, March 30, 2026
