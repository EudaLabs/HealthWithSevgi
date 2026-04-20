# Domain QA Test Results — Batch A

**Date:** 2026-04-14  
**App URL:** https://0xbatuhan4-healthwithsevgi.hf.space/  
**Domains tested:** Radiology, Nephrology, Oncology — Breast, Hepatology — Liver

---

## Results Summary

| Domain | Session | Step 6 Screenshot | Step 7 Screenshot | Status |
|--------|---------|-------------------|-------------------|--------|
| Radiology | domainA | domain_Radiology_step6.png | domain_Radiology_step7.png | PASS |
| Nephrology | domainB | domain_Nephrology_step6.png | domain_Nephrology_step7.png | PASS |
| Oncology — Breast | domainC | domain_OncologyBreast_step6.png | domain_OncologyBreast_step7.png | PASS |
| Hepatology — Liver | domainD | domain_HepatologyLiver_step6.png | domain_HepatologyLiver_step7.png | PASS |

---

## Domain Details

### 1. Radiology (domainA)
- **Step 6 (Explainability):** Captured — shows SHAP feature importance chart (top feature: `diag_kernel`), single patient explanation panel with "Explain This Patient" button, clinical sense-check banner ("Follow-up Visit Number is the most important feature").
- **Step 7 (Ethics & Bias):** Captured — shows bias alerts for age groups 61–75 and 76+, subgroup performance table. Bias detected with action needed.
- **Note:** Radiology dataset had an extreme class imbalance (196.78:1). SMOTE was enabled to resolve the `/api/prepare` call. The Apply Preparation Settings required a JS-triggered click to fire the API call successfully.

### 2. Nephrology (domainB)
- **Step 6 (Explainability):** Captured — shows SHAP feature importance chart (many kidney function features), patient explanation with "Explain This Patient" button, clinical sense-check ("Elevated serum creatinine reflects impaired kidney function").
- **Step 7 (Ethics & Bias):** Captured — shows "No significant bias detected" (green banner). Subgroup performance table shows all groups within acceptable sensitivity range (97–100%). Training data representation chart included.

### 3. Oncology — Breast (domainC)
- **Step 6 (Explainability):** Captured — shows SHAP feature importance chart (top feature: `World Tumour Radius (mm)`), single patient explanation panel. Clinical sense-check present.
- **Step 7 (Ethics & Bias):** Captured — shows "No significant bias detected" (green banner). Subgroup table visible. EU AI Act compliance link shown in Resources & Compliance section.

### 4. Hepatology — Liver (domainD)
- **Step 6 (Explainability):** Captured — shows SHAP feature importance chart (top feature: `Alkaline Phosphatase (IU/L)`), patient panel with "Explain This Patient" button. Clinical sense-check present.
- **Step 7 (Ethics & Bias):** Captured — shows bias alerts for age groups 61–75 and 76+. Subgroup performance table shows lower sensitivity in older age groups. Action required.

---

## Notes
- All 4 domains successfully completed the full 7-step wizard pipeline.
- Column Mapper modal required JS click (`eval`) in some sessions where the ref-based click didn't trigger the modal open.
- Radiology required SMOTE to be enabled due to severe class imbalance (196:1 ratio) before `/api/prepare` would succeed.
- HF Space was responsive; no timeouts or hard failures encountered.
