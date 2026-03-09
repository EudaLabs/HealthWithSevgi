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
