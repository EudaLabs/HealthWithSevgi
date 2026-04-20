# Domain QA Test Results — Missing Domains

**Date:** 2026-04-14  
**Tester:** Claude agent-browser automation  
**App URL:** https://0xbatuhan4-healthwithsevgi.hf.space/

---

## Summary

| Domain | Status | Step 6 Screenshot | Step 7 Screenshot |
|--------|--------|-------------------|-------------------|
| Dermatology | PASS | domain_dermatology_step6.png (146 KB) | domain_dermatology_step7.png (155 KB) |
| Ophthalmology | PASS | domain_ophthalmology_step6.png (146 KB) | domain_ophthalmology_step7.png (81 KB) |
| Pharmacy — Readmission | PASS | domain_pharmacy_readmission_step6.png (146 KB) | domain_pharmacy_readmission_step7.png (155 KB) |

**Overall Status: ALL 3 DOMAINS PASSED**

---

## Detailed Test Execution

### 1. Dermatology (Session: dermSession)

- **Step 1 (Clinical Context):** Selected Dermatology from specialty dropdown. Next Step enabled immediately.
- **Step 2 (Data Exploration):** Clicked "Use Default Dataset". Dataset loaded successfully. Column Mapper opened, Validate Schema clicked (ok), Save Mapping clicked (ok).
- **Step 3 (Data Preparation):** Apply Preparation Settings required two attempts (first attempt left Next disabled; scrolled 300px and clicked Apply again — Next Step became enabled on second attempt).
- **Step 4 (Model & Parameters):** Train Model text appeared. Next Step was enabled without manual training trigger.
- **Step 5 (Results):** Loaded successfully, Next Step available.
- **Step 6 (Explainability):** Loaded successfully. Screenshot captured.
- **Step 7 (Ethics & Bias):** Loaded successfully. Screenshot captured.

### 2. Ophthalmology (Session: ophthSession)

- **Step 1 (Clinical Context):** Selected Ophthalmology from specialty dropdown. Next Step enabled.
- **Step 2 (Data Exploration):** Clicked "Use Default Dataset". Column Mapper → Validate Schema (ok) → Save Mapping (ok).
- **Step 3 (Data Preparation):** Same pattern as Dermatology — first Apply left Next disabled; second Apply after scrolling 300px enabled Next Step.
- **Step 4 (Model & Parameters):** Train Model text appeared. Next Step available.
- **Step 5 (Results):** Loaded successfully.
- **Step 6 (Explainability):** Loaded successfully. Screenshot captured.
- **Step 7 (Ethics & Bias):** Loaded successfully. Screenshot captured (81 KB — lighter content than other domains).

### 3. Pharmacy — Readmission (Session: pharmaSession)

- **Step 1 (Clinical Context):** Selected "Pharmacy — Readmission" from specialty dropdown. Next Step enabled.
- **Step 2 (Data Exploration):** Clicked "Use Default Dataset". Column Mapper → Validate Schema (ok) → Save Mapping (ok).
- **Step 3 (Data Preparation):** Same Apply double-click pattern required. Next Step enabled on second Apply.
- **Step 4 (Model & Parameters):** Train Model text appeared. Next Step available.
- **Step 5 (Results):** Loaded successfully.
- **Step 6 (Explainability):** Loaded successfully. Screenshot captured.
- **Step 7 (Ethics & Bias):** Loaded successfully. Screenshot captured.

---

## Observations & Notes

1. **Apply Preparation Settings requires two clicks** on all 3 tested domains. First click via direct button ref leaves Next Step disabled. Scrolling 300px down and clicking Apply a second time consistently enables Next Step. This is a reproducible UX issue across all domains.

2. **Column Mapper JS automation worked reliably** for all 3 domains — `Column Mapper` open, `Validate Schema`, and `Save Mapping` all returned "ok" on first attempt.

3. **Training auto-triggered** on Step 4 for all domains (Auto-Retrain checkbox was pre-checked). No manual "Train Model" button click was needed.

4. **No domain failures.** All 3 previously untested domains passed the full 7-step wizard flow.

---

## Screenshots Captured

| File | Size | Timestamp |
|------|------|-----------|
| domain_dermatology_step6.png | 146 KB | 2026-04-14 01:33 |
| domain_dermatology_step7.png | 155 KB | 2026-04-14 01:33 |
| domain_ophthalmology_step6.png | 146 KB | 2026-04-14 01:36 |
| domain_ophthalmology_step7.png | 81 KB | 2026-04-14 01:36 |
| domain_pharmacy_readmission_step6.png | 146 KB | 2026-04-14 01:39 |
| domain_pharmacy_readmission_step7.png | 155 KB | 2026-04-14 01:39 |
