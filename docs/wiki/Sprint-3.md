# Sprint 3 — Summary

> **Project:** HealthWithSevgi — SENG 430
> **Sprint Period:** 18 March – 1 April 2026
> **Scope:** Steps 4 (Model & Parameters) and 5 (Results)

---

## Sprint Goals

- Implement model training (8 algorithms: KNN, SVM, Decision Tree, Random Forest, Logistic Regression, Naive Bayes, XGBoost, LightGBM)
- Build interactive parameter panels for each model type
- Display comprehensive evaluation metrics: accuracy, sensitivity, specificity, precision, F1-score, AUC-ROC, MCC
- Visualise confusion matrix, ROC curve, and precision-recall curve
- Implement model comparison arena with parallel coordinates
- Detect and flag overfitting (train-test accuracy gap > 10pp)
- Low sensitivity warnings when recall drops below 60%

## Deliverables Completed

| Deliverable | Status |
|---|---|
| Step 4 — Train any of 8 model types with customisable hyperparameters | ✅ Done |
| Step 4 — Parameter panels per model (KNN: k/metric, SVM: kernel/C, DT: depth/criterion, etc.) | ✅ Done |
| Step 5 — Full metrics dashboard (accuracy, sensitivity, specificity, precision, F1, AUC, MCC) | ✅ Done |
| Step 5 — Confusion matrix heatmap | ✅ Done |
| Step 5 — ROC curve with AUC annotation | ✅ Done |
| Step 5 — Precision-Recall curve | ✅ Done |
| Step 5 — Overfitting warning banner (>10pp train-test gap) | ✅ Done |
| Step 5 — Low sensitivity warning banner (<60% recall) | ✅ Done |
| Model Comparison Arena — compare up to 5 models side-by-side | ✅ Done |
| Arena — Parallel coordinates chart for multi-metric comparison | ✅ Done |
| KNN decision boundary visualisation (PCA 2D) | ✅ Done |
| Backend tests for Steps 1–3 (expanded) | ✅ Done |
| 20 domain datasets with clinical context | ✅ Done |

## Key Technical Decisions

- **In-memory model storage** with LRU caching — no database dependency
- **Session-based architecture** — each user gets a unique session_id from data preparation, which carries through training and results
- **Lazy-loaded Step 5** — code-split for performance since it includes heavy chart libraries
- **Clinical names** used throughout — all raw column names mapped to human-readable clinical labels

## Metrics

| Metric | Result |
|---|---|
| Backend tests passing | 145+ |
| Model types supported | 8 |
| Medical specialties | 20 |
| Evaluation metrics per model | 7 + confusion matrix + ROC + PR curve |
