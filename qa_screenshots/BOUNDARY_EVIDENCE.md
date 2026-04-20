# Boundary Test Evidence

## Bias Detection (10pp Threshold)

- Code location: `backend/app/services/ethics_service.py:161` (constant), `ethics_service.py:369` (_detect_bias method)
- Constant: `BIAS_SENSITIVITY_GAP_THRESHOLD = 0.10`
- Comparison (line 369): `if sm.sensitivity < overall_sensitivity - BIAS_SENSITIVITY_GAP_THRESHOLD:`
- Behavior:
  - Gap = 10.0pp → banner HIDDEN (condition is strict `<`; `0.100 < 0.100` is False)
  - Gap = 10.1pp → banner VISIBLE (condition `0.899 < 1.000 - 0.10` → `0.899 < 0.900` is True)
  - Gap = 9.9pp → banner HIDDEN (`0.901 < 0.900` is False)
- Frontend confirmation (Step7Ethics.tsx:147–157): `ethics.bias_warnings.length > 0` controls rendering; when the array is empty (gap ≤ 10pp) the red alert-danger banner is replaced with a green "No significant bias detected — all sensitivity gaps are within 10 percentage points" success banner (line 157).

Note: a secondary check at line 323 inside `_compute_subgroup_metrics` uses `gap > BIAS_SENSITIVITY_GAP_THRESHOLD` (strict `>`) to set status to "review", but this does NOT trigger the red bias banner — it only affects the per-row status badge in the subgroup table.

## Training Data Representation (15pp Threshold)

- Code location: `backend/app/services/ethics_service.py:170` (constant), `ethics_service.py:417` (sex check), `ethics_service.py:471` (age-group check)
- Constant: `REPRESENTATION_GAP_THRESHOLD_PP = 15.0`
- Comparison (lines 417 and 471): `if gap_pp > REPRESENTATION_GAP_THRESHOLD_PP:`
  - Where `gap_pp = round(abs(dataset_pct - norm_pct), 1)`
- Behavior:
  - Gap = 15.0pp → warning HIDDEN (strict `>`; `15.0 > 15.0` is False)
  - Gap = 15.1pp → warning VISIBLE (`15.1 > 15.0` is True)
  - Gap = 14.9pp → warning HIDDEN (`14.9 > 15.0` is False)
- Frontend confirmation (Step7Ethics.tsx:279–286): `ethics.representation_warnings && ethics.representation_warnings.length > 0` controls an amber `alert-warning` block labelled "Representation Gap Warning". Each `RepresentationWarning.message` string (e.g. "Female representation (30.0%) deviates from population norm (50.0%) by 20.0pp") is rendered inside it. When the array is empty the block is not rendered at all.
