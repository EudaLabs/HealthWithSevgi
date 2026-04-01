# Root Cause Analysis: "Target column not found" Error

**Date:** 2026-04-02
**Severity:** High — affects multiple clinical domains, misleading error message
**Reported in:** Step 2 (Data Exploration) — "Use Default Dataset" flow

---

## 1. Symptom

When selecting certain clinical domains (e.g., Mental Health, Pulmonology, ICU/Sepsis) and clicking **"Use Default Dataset"**, users see:

> **Target column not found**
> The expected target column was not found in your dataset.
> Upload your CSV and use the Column Mapper to select the correct target column.

The error is **misleading** — the actual problem has nothing to do with target columns.

---

## 2. Root Cause

The bug has **two layers** working together to produce the wrong error.

### Layer 1 — Backend: Missing dataset files

Several specialties require manually-downloaded CSV files in `backend/data_cache/`. These files are not bundled with the repository and are not auto-downloadable (Kaggle requires auth, PhysioNet requires credentials, etc.).

**Current `data_cache/` contents (6 of 20):**

| File | Specialty |
|------|-----------|
| `cardiology_hf.csv` | Cardiology |
| `endocrinology_diabetes.csv` | Endocrinology |
| `nephrology_ckd.csv` | Nephrology |
| `neurology_parkinsons.csv` | Neurology |
| `orthopaedics.arff` | Orthopaedics |
| `pharmacy_readmission.csv` | Pharmacy |

When a dataset file is missing, `DataService` raises `DatasetUnavailableError` with a message like:

```
Dataset 'mental_health' is unavailable: Real mental health dataset not found in data_cache/.
Download from kaggle.com/datasets/anthonytherrien/depression-dataset and save as
depression_data.csv in data_cache/
```

### Layer 2 — Frontend: Wrong error classification (the actual bug)

In `frontend/src/pages/Step2DataExploration.tsx:86`:

```typescript
} else if (msg.toLowerCase().includes('not found') || msg.toLowerCase().includes('target column')) {
  setUploadError('target_not_found')
}
```

This matches the substring **"not found"** in ANY error message. The `DatasetUnavailableError` message contains "not found" (referring to the **dataset file on disk**), but the frontend interprets it as a **target column** issue and shows the wrong modal.

### Exact Flow (Mental Health example)

```
1. User clicks "Use Default Dataset"
2. Frontend → POST /api/explore { specialty_id: "mental_health", target_col: "severity_class" }
3. Backend → _load_df() → get_example_dataset("mental_health") → _mental_health()
4. _mental_health() checks for depression_data.csv in data_cache/ → NOT FOUND
5. Raises DatasetUnavailableError("...not found in data_cache/...")
6. Router wraps it → HTTPException(422, detail="...not found...")
7. Frontend catches → msg.includes('not found') → TRUE
8. Shows 'target_not_found' error modal ← WRONG ERROR
```

---

## 3. Affected Domains

| Domain | Dataset Source | Status | Why |
|--------|--------------|--------|-----|
| Mental Health | Kaggle (auth required) | BROKEN | No cached CSV |
| Pulmonology (COPD) | Kaggle/PhysioNet | BROKEN | No cached CSV |
| ICU / Sepsis | PhysioNet (credentialed) | BROKEN | No cached CSV |
| Obstetrics (Fetal) | Manual download | BROKEN | No cached CSV |
| Dermatology | HAM10000 / fetch | FRAGILE | Depends on remote URL |
| Ophthalmology | UCI ARFF / fetch | FRAGILE | Depends on remote URL |
| Cardiology (Arrhythmia) | UCI / fetch | FRAGILE | Depends on remote URL |
| Oncology (Cervical) | UCI / fetch | FRAGILE | Depends on remote URL |
| Thyroid | UCI / fetch | FRAGILE | Depends on remote URL |

**Working domains** either have cached files or use reliable auto-download sources (sklearn bundled datasets, stable raw GitHub URLs).

---

## 4. Proposed Fixes

### Fix A: Correct the frontend error classification

**What:** Add a distinct error type for "dataset unavailable" and fix the string-matching logic in `Step2DataExploration.tsx` so that `DatasetUnavailableError` messages are not misclassified as `target_not_found`.

**Changes:**
- Add `dataset_unavailable` to `UploadErrorType` in `ErrorModal.tsx`
- Match on `"unavailable"` or `"data_cache"` before the generic `"not found"` check
- Show a proper error message: "Dataset not available — download instructions"

**Pros:**
- Minimal change (2 files, ~15 lines)
- Fixes the misleading UX immediately
- No backend changes needed

**Cons:**
- Does NOT fix the underlying problem — datasets are still missing
- Users still can't use affected domains without manual CSV downloads
- Only masks the symptom with a better error message

---

### Fix B: Bundle all datasets in `data_cache/` and commit to the repo

**What:** Download all 20 datasets manually, place them in `backend/data_cache/`, and commit them to the repository (or track via Git LFS).

**Changes:**
- Download and add ~14 missing CSV/ARFF files
- Add `.gitattributes` for LFS tracking if files are large
- Update `.gitignore` to stop ignoring `data_cache/`

**Pros:**
- Every domain works out of the box — zero setup for new developers
- No runtime dependency on external URLs
- Simplest fix for the actual data availability problem

**Cons:**
- Increases repo size significantly (some datasets are 50MB+)
- Licensing concerns — some datasets (PhysioNet, Kaggle) have redistribution restrictions
- Datasets become stale; no mechanism to update them
- Git LFS adds complexity to the CI/CD pipeline

---

### Fix C: Generate synthetic fallback datasets when real data is unavailable

**What:** For each specialty, add a synthetic data generator (using numpy/sklearn's `make_classification`) that produces a statistically representative dataset as a fallback when the real CSV is missing.

**Changes:**
- Add `_generate_synthetic(specialty_id)` method to `DataService`
- Each generator creates data matching the specialty's `feature_names` and `target_variable`
- `get_example_dataset()` falls back to synthetic instead of raising `DatasetUnavailableError`

**Pros:**
- Every domain always works, no external dependencies
- No licensing concerns — data is generated, not redistributed
- Keeps repo size small
- Good enough for educational/demo purposes

**Cons:**
- Synthetic data lacks real clinical distributions and correlations
- Model performance metrics will be unrealistic
- Students may draw wrong conclusions from artificial patterns
- Significant implementation effort (~20 generators with realistic feature ranges)

---

### Fix D: Seed the `data_cache/` at Docker build time

**What:** Add a build-time step in the Dockerfile that downloads and prepares all required datasets into `data_cache/` during `docker build`. Use a dedicated Python script (`scripts/seed_datasets.py`) that handles each specialty's download, extraction, and validation.

**Changes:**
- Create `scripts/seed_datasets.py` — a standalone script that downloads all 20 datasets
- Add a `RUN python scripts/seed_datasets.py` step in the Dockerfile after dependency installation
- For Kaggle datasets: use the Kaggle API with a build-arg for credentials, OR host mirrors on a project-controlled bucket (e.g., HuggingFace Hub, S3)
- For PhysioNet datasets: same approach — mirror or credential passthrough
- Add a health check that validates `data_cache/` completeness on startup

**Pros:**
- Every domain works in production with zero manual intervention
- Datasets are fresh at build time — can pin versions
- No repo bloat — data lives only in the Docker image layer
- Single source of truth for dataset procurement logic
- Aligns with the existing HuggingFace Spaces deployment model

**Cons:**
- Docker builds become slower and network-dependent
- Build fails if any upstream source is down (mitigate with mirrors + retry)
- Kaggle/PhysioNet credentials need to be available at build time (secret management)
- Adds a new script to maintain (~200-300 lines)
- Docker layer caching helps, but full rebuilds re-download everything

---

## 5. Recommendation

**Immediate (this sprint):** Apply **Fix A** to stop showing the misleading error. This is a 15-minute change.

**Short-term:** Apply **Fix D** for the Docker/HuggingFace deployment path, combined with **Fix C** as a graceful fallback for local development without credentials. This gives production reliability while keeping local dev frictionless.
