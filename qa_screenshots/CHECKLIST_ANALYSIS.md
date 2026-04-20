# EU AI Act Checklist Discrepancy Analysis

**Date:** 2026-04-14  
**Investigator:** QA Agent  
**Issue:** Sprint 4 spec says 8 items / 2 pre-checked; code has 9 items / 3 pre-checked.

---

## 1. What the Spec Says

**Source:** `docs/seng430-sprints/sprint-4.md` (line 25) and `docs/wiki/Sprint-4.md` (lines 15 & 31)

Both documents state consistently:
- **8 items** in the EU AI Act checklist
- **2 pre-checked** (auto-completed) on load
- The Sprint 4 Metrics table (sprint-4.md line 48): "Click all **8 items** — All toggle correctly; **2 pre-checked** on load"
- The Wiki summary (Sprint-4.md line 15): "EU AI Act compliance checklist with **8 items (2 pre-checked)**"
- The Wiki Step 7 section (Sprint-4.md line 31): "EU AI Act checklist — **8 items**, 2 auto-completed (explainability, data source), 6 toggleable"

---

## 2. What the Code Actually Has

**Source:** `backend/app/services/ethics_service.py`, lines 25–90

The `EU_AI_ACT_ITEMS` list contains **9 items**, with **3 pre-checked**:

| # | id | text (short) | article | pre_checked |
|---|---|---|---|---|
| 1 | `explainability` | Model Explainability | Art. 13 | **True** |
| 2 | `data_source` | Data Transparency | Art. 10 | **True** |
| 3 | `bias_audit` | Subgroup Bias Audit | Art. 10(2f) | False |
| 4 | `human_oversight` | Human Oversight Plan | Art. 14 | False |
| 5 | `gdpr` | Patient Data Privacy (GDPR) | Art. 10(5) | False |
| 6 | `monitoring` | Post-Deployment Monitoring | Art. 72 | False |
| 7 | `incident_reporting` | Incident Reporting Pathway | Art. 73 | False |
| 8 | `clinical_validation` | Clinical Validation | Art. 9 | False |
| 9 | `data_licensing` | Dataset licensing verified — 18/20 datasets bundled... | (none) | **True** |

The test file `backend/tests/test_step7_ethics.py` (line 45–51) reflects this reality:
- Method is named `test_eu_ai_act_checklist_has_nine_items`
- Asserts `len(items) == 9`
- Explicitly asserts `data_licensing` is present and `pre_checked is True`

---

## 3. When and Why the 9th Item Was Added

### Timeline (from git log)

**2026-03-30** — commit `b00f368` (`test(B5): add backend tests for Steps 6-7`)  
The original test was named `test_eu_ai_act_checklist_has_eight_items` and asserted `len(items) == 8`. At this point the code matched the spec.

**2026-04-03** — commit `ca2c580` by Efe Çelik (`feat(ethics): add dataset licensing item to EU AI Act checklist`)  
A 9th item (`data_licensing`, `pre_checked: True`) was appended to `EU_AI_ACT_ITEMS` in `ethics_service.py`. This was part of PR #10 (`feat/dataset-licensing-docker-bundling`), which also added license metadata to the specialty registry and created `DATA_LICENSES.md`.

**2026-04-03** — commit `ebee9cd` by Batuhan4 (`fix: Docker build, arena in HF Spaces, licensing errors, and test alignment`)  
The ethics test was updated ("8→9 EU AI Act checklist items") to stop the test suite from failing. The test method was renamed from `test_eu_ai_act_checklist_has_eight_items` to `test_eu_ai_act_checklist_has_nine_items` and the assert was changed to `== 9`. The `data_licensing` assertion was also added.

**Root cause:** The `data_licensing` item was added as a genuine feature to document dataset license compliance (18/20 open-licensed, 2 runtime-fetched). It is factually pre-checked because the project has already done the licensing work. However, this spec-breaking change was never reflected back in the Sprint 4 spec documents.

---

## 4. Notable Structural Difference

The 9th item (`data_licensing`) differs structurally from the other 8:
- It has **no `article`** field (all others cite a specific EU AI Act article: Art. 9, 10, 13, 14, 72, 73).
- Its `text` is a long prose statement rather than a short label.
- It has **no `description`** field, while items 1–8 all have a `description` field.

This inconsistency suggests the item was added quickly without following the established schema pattern for the checklist.

---

## 5. Recommendation

**Update the spec documents — do NOT revert the code.**

### Reasoning

1. **The 9th item is factually correct and adds real value.** The project did license 18/20 datasets under open licenses (CC BY 4.0, CC0 1.0, etc.) and created DATA_LICENSES.md. Documenting this in the compliance checklist is accurate and professionally appropriate.

2. **Both spec documents are retrospective write-ups**, not binding contracts. `docs/wiki/Sprint-4.md` is a summary of what was delivered; `docs/seng430-sprints/sprint-4.md` describes the assignment scope. The `data_licensing` feature is a legitimate addition that improves the tool.

3. **Reverting the code would break passing tests and remove genuine compliance information** without any improvement to the product.

4. **The structural inconsistency of item 9 should be fixed**, but the fix is to make item 9 conform to the schema (add `article` and `description` fields), not to delete it.

---

## 6. Exact Changes Required

### A. Fix item 9 schema inconsistency in the code (recommended)

**File:** `backend/app/services/ethics_service.py`, lines 83–89

Replace the current `data_licensing` entry (which lacks `article` and `description`) with a properly structured entry:

```python
# Current (lines 83-89):
{
    "id": "data_licensing",
    "text": "Dataset licensing verified — 18/20 datasets bundled under open licenses "
            "(CC BY 4.0, CC0 1.0, CC BY-SA 4.0, CC BY-NC 4.0); "
            "2 datasets with unclear licensing fetched at runtime for educational use only "
            "(see DATA_LICENSES.md)",
    "pre_checked": True,
},

# Should become:
{
    "id": "data_licensing",
    "text": "Dataset Licensing Verified",
    "description": "18/20 datasets are bundled under open licenses (CC BY 4.0, CC0 1.0, "
                   "CC BY-SA 4.0, CC BY-NC 4.0). 2 datasets with unclear licensing are "
                   "fetched at runtime for educational use only (see DATA_LICENSES.md).",
    "article": "Art. 10(3)",
    "pre_checked": True,
},
```

### B. Update the spec documents to match the code

**File 1:** `docs/seng430-sprints/sprint-4.md`
- Line 25: Change `"8 items; 2 pre-checked"` → `"9 items; 3 pre-checked"`
- Line 48 (Metrics table): Change `"Click all 8 items"` → `"Click all 9 items"` and `"2 pre-checked on load"` → `"3 pre-checked on load"`

**File 2:** `docs/wiki/Sprint-4.md`
- Line 15: Change `"8 items (2 pre-checked)"` → `"9 items (3 pre-checked)"`
- Line 31: Change `"8 items, 2 auto-completed (explainability, data source), 6 toggleable"` → `"9 items, 3 auto-completed (explainability, data source, dataset licensing), 6 toggleable"`

---

## 7. Summary

| Dimension | Spec | Code | Verdict |
|---|---|---|---|
| Item count | 8 | 9 | Spec is outdated |
| Pre-checked count | 2 | 3 | Spec is outdated |
| Pre-checked items | explainability, data_source | explainability, data_source, data_licensing | Code is correct |
| Item 9 schema | N/A | Missing `article` and `description` | Code has minor defect |
| Test | (was) 8 items | 9 items | Test matches code |

**Action:** Update both spec docs (6 text changes). Optionally fix the `data_licensing` item schema to include `article` and `description` fields for consistency.
