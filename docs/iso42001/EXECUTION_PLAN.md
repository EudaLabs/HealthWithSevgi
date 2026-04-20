# ISO/IEC 42001 First Submission — Execution Plan

**Due:** April 8, 2026 (Wednesday, 1:00 PM)
**Scope:** Chapters 1–3 only (AIMS Scope, AI Policy, Data Governance)
**Total Points:** 45 (15 per chapter)
**Deliverable:** Completed Word document based on `ISO42001_Report_Template_V4_FINAL`
**Course:** SENG 430 — Software Quality Assurance Laboratory, Cankaya University
**Instructor:** Dr. Sevgi Koyuncu Tunç

---

## Overview

This plan covers everything needed to complete the **first submission** of the ISO/IEC 42001 AI Management System Compliance Report. The final submission (Chapters 4–7 + Appendix A) is due May 5, 2026 — that is **not** in scope here.

The strategy is:
1. **Extract** all factual data from the codebase (specialties, models, dependencies, features)
2. **Draft** each chapter section by filling the template with project-specific content
3. **Cross-reference** every claim to actual code/features (the instructor values specificity)
4. **Review** against the grading rubric before submission

---

## Phase 0: Pre-Work — Data Extraction from Codebase

> These are mechanical extraction tasks. They produce raw material for all three chapters.

### Task 0.1: Extract Complete Specialty & Dataset Inventory

**Source:** `backend/app/services/specialty_registry.py`

Extract for each of the 20 specialties:
- Specialty name and ID
- Dataset name and original source (Kaggle, UCI, PhysioNet, Harvard Dataverse, etc.)
- Record count, feature count, feature names
- Target variable and type (binary/multiclass)
- Known limitations and biases (class imbalance ratios, demographic gaps, single-institution data)

**Output format:** A 20-row table ready for Section 3.1.

> **UPDATE (April 2026):** A comprehensive dataset licensing audit has been completed and documented in `DATA_LICENSES.md` and `ATTRIBUTION.md`. These files contain per-dataset license types, DOIs, citations, modification records, redistribution rights, and EU AI Act Article 10/11/52 compliance tables. Section 3.1 should cross-reference these documents. Key finding: 18 of 20 datasets are bundled in Docker; 2 (Stroke, Anaemia) are NOT bundled due to unverified licenses.

The 20 specialties are:
1. Cardiology — Heart Failure (UCI)
2. Cardiology — Stroke Prediction (Kaggle)
3. Cardiology — Arrhythmia (UCI)
4. Radiology (Kaggle)
5. Nephrology — Chronic Kidney Disease (UCI)
6. Oncology — Breast Cancer (UCI/Wisconsin)
7. Oncology — Cervical Cancer (UCI)
8. Neurology — Parkinson's (UCI)
9. Endocrinology — Diabetes (Kaggle/Pima)
10. Endocrinology — Thyroid Disease (UCI)
11. Hepatology — Liver Disease (UCI/Indian Liver Patient)
12. Mental Health — Depression (Kaggle)
13. Pulmonology — COPD (Kaggle)
14. Haematology (Kaggle)
15. Dermatology (Harvard Dataverse)
16. Ophthalmology — Diabetic Retinopathy (UCI)
17. Orthopaedics (Kaggle/UCI)
18. ICU — Sepsis Prediction (PhysioNet/Kaggle)
19. Obstetrics — Fetal Health / CTG (UCI)
20. Pharmacy — Hospital Readmission (UCI)

### Task 0.2: Extract ML Model Configuration

**Source:** `backend/app/services/ml_service.py`

Document for each of the **8** ML algorithms:
- Algorithm name
- Hyperparameter grid (names, ranges, defaults)
- Cross-validation strategy (RandomizedSearchCV, 20 iterations, 3-fold CV)
- SHAP explainer type used (TreeExplainer, LinearExplainer, KernelExplainer)

Models: KNN, SVM, Decision Tree, Random Forest, Logistic Regression, Naive Bayes, XGBoost, LightGBM

> **Note:** The template says "6 models" but our tool supports **8**. Document all 8 — this exceeds expectations.

### Task 0.3: Extract Data Validation & Preprocessing Rules

**Source:** `backend/app/services/data_service.py`, `backend/app/models/schemas.py`

Document:
- Upload constraints: `.csv` only, max 50 MB, min 10 rows, min 2 columns, max 20 target classes
- Missing value strategies: drop, median imputation, mode imputation
- Normalization methods: z-score, min-max, none
- Class imbalance handling: SMOTE with adaptive k_neighbors = max(1, min(5, min_class_count - 1))
- Outlier handling: IQR clipping, z-score clipping, none
- Train/test split: configurable ratio (default 80/20)

### Task 0.4: Extract Privacy & Session Architecture

**Source:** `backend/app/main.py`, `backend/app/services/data_service.py`

Document:
- In-memory session storage (LRU cache, max 50 concurrent sessions)
- No database, no persistent storage
- Session auto-eviction (LRU)
- CORS configuration (localhost:5173 in dev only)
- No PII storage by design
- PDF certificate export contains no raw patient data

### Task 0.5: Extract All Dependencies with Versions & Licenses

**Source:** `backend/requirements.txt`, `frontend/package.json`, `hf-space/Dockerfile`

Produce a register of at least 12 components:

| # | Component | Type | Version | License |
|---|-----------|------|---------|---------|
| 1 | scikit-learn | ML Library | (from requirements.txt) | BSD-3-Clause |
| 2 | pandas | Data Library | (from requirements.txt) | BSD-3-Clause |
| 3 | numpy | Numerical | (from requirements.txt) | BSD-3-Clause |
| 4 | SHAP | Explainability | (from requirements.txt) | MIT |
| 5 | XGBoost | ML Library | (from requirements.txt) | Apache 2.0 |
| 6 | LightGBM | ML Library | (from requirements.txt) | MIT |
| 7 | FastAPI | Web Framework | (from requirements.txt) | MIT |
| 8 | uvicorn | ASGI Server | (from requirements.txt) | BSD-3-Clause |
| 9 | ReportLab | PDF Generation | (from requirements.txt) | BSD |
| 10 | React | Frontend Framework | 18.x (from package.json) | MIT |
| 11 | Vite | Build Tool | (from package.json) | MIT |
| 12 | Recharts | Charting | (from package.json) | MIT |
| 13 | python:3.12-slim | Docker Base Image | 3.12 | PSF License |
| 14 | node:20-slim | Docker Build Image | 20 | MIT |
| 15 | imbalanced-learn (SMOTE) | ML Library | (from requirements.txt) | MIT |

For each: version (exact from lock files), license, security assessment, risk level, alternative, monitoring plan.

### Task 0.6: Extract Ethics & Explainability Features

**Source:** `backend/app/services/ethics_service.py`, `backend/app/services/explain_service.py`, `frontend/src/pages/Step6*.tsx`, `frontend/src/pages/Step7*.tsx`

Document:
- SHAP: global feature importance (top N), single-patient waterfall (top 15)
- Clinical name mapping (251 features mapped)
- Subgroup analysis: gender (Female/Male), age bands (18–60, 61–75, 76+)
- Bias detection threshold: 10% sensitivity gap
- EU AI Act checklist: 8 items (2 pre-checked, 6 user-checkable)
- 3 real-world bias case studies (pulse oximeter, sepsis alert, dermatology)

### Task 0.7: Identify Team Members from Git History

**Source:** `git log --all --format='%aN <%aE>' | sort -u`

Known contributors:
- Batuhan Bayazıt (lead developer)
- Efe Çelik (infrastructure/CI)
- BeratMert (features)
- (Others from git log)

> Each team member needs to be assigned an ISO 42001 governance role in Section 2.2.

---

## Phase 1: Chapter 1 — AIMS Scope, Context & Stakeholders (15 pts)

### Section 1.1: AI System Description (Quick Win)

Fill the 5-field table:

| Field | Content |
|-------|---------|
| **System Name** | HealthWithSevgi — ML Visualization Tool for Healthcare Professionals |
| **Purpose** | A browser-based educational tool that enables healthcare professionals and students to explore machine learning concepts through a guided 7-step wizard pipeline (Clinical Context → Data Exploration → Data Preparation → Model & Parameters → Results → Explainability → Ethics & Bias) using real clinical datasets across 20 medical specialties. The tool does NOT make clinical decisions — it teaches ML literacy. |
| **AI Techniques Used** | 8 supervised ML classification algorithms: K-Nearest Neighbors (KNN), Support Vector Machine (SVM), Decision Tree, Random Forest, Logistic Regression, Naive Bayes, XGBoost, LightGBM. Supporting techniques: SMOTE for class imbalance, SHAP for explainability, subgroup fairness analysis. |
| **Deployment Context** | Browser-based SPA (React + FastAPI), educational use only, no clinical decision-making, Docker containerized for HuggingFace Spaces deployment. No server-side data persistence. |
| **Lifecycle Stage** | Design, development, educational deployment — NOT clinical production. Course project lifecycle ends with SENG 430 completion (May 2026). |

**Effort:** ~15 minutes
**Risk:** None — straightforward factual fill.

### Section 1.2: AIMS Scope Statement (Critical — 4 pts)

This is called "the most important subsection in the entire report" by the instructor. Every OUT-OF-SCOPE item needs a WHY.

**IN SCOPE:**
| Item | Detail |
|------|--------|
| Pipeline Steps | All 7 steps (Clinical Context, Data Exploration, Data Preparation, Model & Parameters, Results, Explainability, Ethics & Bias) |
| Clinical Domains | 20 specialties (list all: Cardiology x3, Radiology, Nephrology, Oncology x2, Neurology, Endocrinology x2, Hepatology, Mental Health, Pulmonology, Haematology, Dermatology, Ophthalmology, Orthopaedics, ICU/Sepsis, Obstetrics, Pharmacy) |
| ML Models | 8 classification algorithms (KNN, SVM, DT, RF, LR, NB, XGBoost, LightGBM) |
| Users | Healthcare professionals learning ML; medical/nursing students; SENG 430 teaching staff |
| Lifecycle | Design through educational deployment (HuggingFace Spaces) |
| Data | 20 published clinical datasets (UCI, Kaggle, PhysioNet) + user CSV uploads |
| Explainability | SHAP-based global and single-patient explanations |
| Ethics | Subgroup fairness audit, bias detection, EU AI Act educational checklist |

**OUT OF SCOPE (with justification):**
| Excluded Item | WHY |
|---------------|-----|
| Clinical diagnosis or treatment decisions | Educational tool only — no clinical validation performed; users are explicitly warned via disclaimers |
| Real patient-identifiable data (PII/PHI) | Privacy by design — only published, de-identified datasets used; browser-only processing; no server persistence |
| Production hospital/clinic deployment | No regulatory approval (CE marking, FDA clearance); no clinical validation study conducted |
| Post-deployment monitoring in production | Educational lifecycle ends at course completion (May 2026); monitoring plan is documented theoretically in Ch. 5.3 |
| Deep learning / neural network models | Out of pedagogical scope — tool focuses on interpretable classical ML for healthcare professionals |
| Real-time streaming data or IoT device integration | Not applicable to educational CSV-based analysis workflow |
| Multi-language / internationalization | English-only interface; single-locale deployment |
| Regression or unsupervised learning tasks | Tool scope is limited to supervised classification to maintain focused learning objectives |

**Effort:** ~45 minutes
**Risk:** Medium — must be very specific and justified. Generic answers lose points.

### Section 1.3: Internal & External Issues (4 pts)

Need at least **4 external + 3 internal** issues, all project-specific.

**External Issues:**

| Issue | Description & Relevance to AIMS |
|-------|--------------------------------|
| **Regulatory: EU AI Act** | Classifies healthcare AI as high-risk (Article 6, Annex III). Though educational, our tool must demonstrate awareness of transparency, human oversight, and bias audit requirements. Step 7 EU AI Act checklist directly addresses this. |
| **Regulatory: GDPR/KVKK** | Turkish KVKK (Law No. 6698) and EU GDPR require data protection impact assessments for health data processing. Our tool mitigates by processing only published, de-identified datasets with no server-side persistence. |
| **Societal: Public concern about healthcare AI** | Growing distrust of AI in clinical settings (documented cases of biased pulse oximeters, discriminatory sepsis alerts). Our tool addresses this through Step 7 real-world bias case studies and explicit educational framing. |
| **Technological: Rapid evolution of XAI techniques** | Explainable AI methods evolve quickly (e.g., SHAP, LIME, counterfactual explanations). Our choice of SHAP is well-established but may need updating. Current implementation covers TreeExplainer, LinearExplainer, and KernelExplainer. |
| **Market: Increasing demand for AI-literate clinicians** | WHO and EU policy documents emphasize AI literacy for healthcare workers. Our tool directly serves this need across 20 medical specialties. |

**Internal Issues:**

| Issue | Description & Relevance to AIMS |
|-------|--------------------------------|
| **Competence: Team ML/AI experience** | Team of software engineering students (SENG 430) with varying ML experience. Mitigated by structured 7-step wizard that guides users and developers through proper ML workflow. |
| **Infrastructure: No GPU, browser-based execution** | All computation runs on CPU (FastAPI backend). Limits model complexity but appropriate for educational scope. Docker containerization ensures reproducible deployment. |
| **Timeline: 10-week sprint cycle** | 5 sprints across one semester with competing coursework. Risk of incomplete features mitigated by sprint gates and progressive feature delivery (Steps 1–7 delivered incrementally). |
| **Resource: In-memory architecture, no database** | LRU cache with max 50 concurrent sessions. Limits scalability but simplifies privacy compliance (no persistent data to manage/delete). |

**Effort:** ~30 minutes
**Risk:** Low — concrete issues with real project connections score well.

### Section 1.4: Stakeholder Register (4 pts)

Need at least **6 stakeholders** with needs↔response matching.

| Stakeholder | Role/Category | Key Needs & Expectations | How AIMS Addresses | Influence |
|-------------|---------------|--------------------------|-------------------|-----------|
| Healthcare Professionals | End User | Plain clinical language; trust model fairness; understand AI limitations; data privacy | No-code UI; Step 6 SHAP explanations with clinical names; Step 7 subgroup bias audit; privacy notice on every page; clinical disclaimers | High |
| Patients (indirect) | Affected Party | Fair treatment regardless of demographics; data not misused; AI not replacing clinical judgment | Step 7 subgroup analysis (gender, age bands); educational-only scope; no PII processing; bias case studies | High |
| Students / Development Team | Developer | Clear requirements; learn responsible AI; feasible workload | User Guide as spec; ISO deliverables as structured learning; sprint gates as checkpoints | Medium |
| Instructor (Dr. Sevgi Koyuncu Tunç) | Governance / Evaluator | Curriculum alignment; quality deliverables; ethical AI education demonstrated | Sprint gates as management review; ISO rubric compliance; PDCA cycle documented | High |
| Regulators (EU AI Act authorities) | External Oversight | Transparency; human oversight; bias documentation; compliance evidence | Step 7 EU AI Act checklist (8 items); all ISO deliverables; SHAP explainability; clinical disclaimers | High |
| Dataset Providers (UCI, Kaggle, PhysioNet) | Supplier | Proper attribution; ethical use within license terms; no misrepresentation of data | Provenance documentation in Section 3.1; `DATA_LICENSES.md` (per-dataset license audit); `ATTRIBUTION.md` (CC BY attributions); educational-use scope statement; license compliance in Section 3.4 | Low |
| Future Deployers (hypothetical hospitals) | Potential User | Production readiness evidence; risk documentation; monitoring plans | Theoretical monitoring plan (Ch. 5.3); risk register (Ch. 4); impact assessment (Ch. 4.2) — though not in first submission | Medium |
| General Public | Societal | Trust in healthcare AI; transparency about AI capabilities and limitations | Open educational tool; bias case studies; responsible AI principles embedded in tool design | Low |

**Effort:** ~30 minutes
**Risk:** Low — template provides good guidance; just need to be specific.

---

## Phase 2: Chapter 2 — AI Policy & Governance (15 pts)

### Section 2.1: AI Policy Statement (6 pts)

Must read like a **formal policy document**, not casual homework. Each principle must reference a **specific tool feature**.

| Section | Content |
|---------|---------|
| **Policy Title & Version** | "AI Policy for HealthWithSevgi ML Visualization Tool — Version 1.0, April 2026" |
| **Purpose** | This policy establishes the governance framework for responsible development and educational deployment of the HealthWithSevgi ML Visualization Tool. It ensures that all AI-related activities adhere to principles of fairness, transparency, human oversight, privacy, safety, and accountability throughout the AI system lifecycle. |
| **Scope** | This policy governs all AI/ML components within the HealthWithSevgi system as defined in Section 1.2, including: 8 classification algorithms, SHAP explainability engine, subgroup fairness analysis, 20 clinical datasets, and the 7-step wizard pipeline. It applies to all development team members across all project sprints. |
| **Principle 1: Fairness** | We commit to ensuring equitable AI performance across all patient demographic groups. **Implementation:** Step 7 subgroup analysis automatically evaluates model sensitivity across gender (Female/Male) and age bands (18–60, 61–75, 76+). A 10% sensitivity gap threshold triggers a red "action_needed" warning. SMOTE (Step 3) addresses training data class imbalance. Three real-world bias case studies educate users about AI fairness failures. |
| **Principle 2: Transparency** | We commit to making all AI model decisions interpretable and understandable to non-technical healthcare users. **Implementation:** Step 5 presents 6 evaluation metrics (accuracy, precision, recall, F1, AUC-ROC, AUC-PR) with clinical-language explanations and color-coded thresholds. Step 6 provides SHAP-based global feature importance and single-patient waterfall charts with 251 clinical name mappings. |
| **Principle 3: Human Oversight** | We commit to ensuring humans remain the ultimate decision-makers. No automated clinical actions are taken by the tool. **Implementation:** Step 7 EU AI Act checklist requires user confirmation of human oversight plan. Clinical disclaimers on Step 6 state "A clinician must always make the final decision." All model outputs require active human interpretation. |
| **Principle 4: Privacy** | We commit to protecting patient data through privacy-by-design architecture. **Implementation:** All data processing occurs in-memory on the server with no persistent storage (LRU cache, session-only lifecycle). Only published, de-identified clinical datasets are built-in. CSV upload processing uses no external APIs. Privacy notice is displayed in the tool interface. |
| **Principle 5: Safety** | We commit to preventing harmful AI outputs through explicit scope boundaries and user education. **Implementation:** Educational-only scope is declared throughout the tool and documentation. Step 5 sensitivity warnings flag models below 50% (red threshold). Model comparison feature encourages validation across multiple algorithms rather than relying on a single model. |
| **Principle 6: Accountability** | We commit to clear assignment of responsibility for all AI governance activities. **Implementation:** Governance roles mapped in Section 2.2. Sprint gates serve as management review checkpoints. This ISO 42001 report documents all governance decisions with traceability to specific code and features. |
| **Compliance Commitments** | ISO/IEC 42001:2023 (AI Management System); EU AI Act (educational alignment with Article 6, Annex III requirements); ISO/IEC 25059 (AI system quality); KVKK (Law No. 6698) / GDPR (data protection alignment) |
| **Review Schedule** | Policy reviewed: (1) at project completion (May 2026); (2) when bias detected above threshold in Step 7; (3) when scope changes (new specialties/models added); (4) when relevant regulations change (EU AI Act enforcement updates) |
| **Approval** | Team: [Team Name], AI System Owner: [PO Name], Date: April 2026 |

**Effort:** ~60 minutes (must be written as a formal document, not just table fill)
**Risk:** High — this is 6 points. Each principle MUST reference a concrete tool feature. Generic principles score poorly.

### Section 2.2: AI Governance Roles (4 pts)

Map real team members to ISO 42001 governance roles. The instructor explicitly requires **named people and specific responsibilities**.

| AI Governance Role | Scrum Equivalent | Assigned To | Key Responsibilities |
|-------------------|------------------|-------------|---------------------|
| AI System Owner | Product Owner | [Name — likely Batuhan] | Overall accountability for AI system; policy approval; scope decisions (Section 1.2); final authority on risk acceptance; ensures AIMS alignment with educational objectives |
| Data Steward | Developer / Data Lead | [Name] | Data quality oversight across 20 datasets (Section 3.1); provenance documentation; privacy compliance (Section 3.3); bias-in-data assessment; CSV upload validation rules |
| Ethics Reviewer | Developer / Ethics Lead | [Name] | Fairness analysis (Step 7); impact assessment lead (Ch. 4); EU AI Act checklist review; bias detection interpretation; case study selection |
| Technical Lead | Scrum Master / Lead Dev | [Name] | Model implementation oversight (8 algorithms); hyperparameter documentation; SHAP explainability quality; Docker deployment; CI/CD pipeline |
| QA & Compliance Lead | Developer / QA | [Name] | Test suite maintenance; sprint gate demos; ISO 42001 report quality; peer audit coordination (Ch. 6) |

> **Action needed:** Confirm real team member names and role assignments before finalizing.

**Effort:** ~20 minutes (once names are confirmed)
**Risk:** Low — but names MUST be real team members.

---

## Phase 3: Chapter 3 — Data Governance & Third-Party Management (15 pts)

### Section 3.1: Data Source Inventory (4 pts)

This is the most data-heavy section. Need a **20-row table** with detailed information per dataset.

**Strategy:** Extract directly from `specialty_registry.py` and cross-reference with original dataset sources.

Table columns for each of the 20 datasets:
- `#` (1–20)
- `Specialty`
- `Dataset Name & Source` (include URL or DOI)
- `Records` (exact count from registry)
- `Features` (exact count)
- `Target Variable` (name + type)
- `Known Limitations / Biases` (class imbalance ratio, demographic gaps, single-institution, sample size concerns)

**Known bias patterns to document per dataset:**
- Class imbalance (e.g., heart failure dataset: ~32% death events)
- Geographic bias (e.g., Indian Liver Patient dataset — single country)
- Demographic under-representation (e.g., Pima diabetes — only Pima Indian women)
- Temporal bias (e.g., older datasets may not reflect current clinical practices)
- Feature limitations (e.g., datasets missing socioeconomic or ethnic variables)

**Effort:** ~90 minutes (20 datasets, each needing research into limitations)
**Risk:** Medium — the instructor values **honest limitation analysis**, not just listing. Each dataset should have at least 2 specific limitations.

### Section 3.2: Data Quality & Validation (3 + 3 pts)

Four subsections:

**Quality Criteria:**
- Minimum rows: ≥10 patients (enforced in `data_service.py`)
- Required columns: ≥2 (at least 1 feature + 1 target)
- File format: `.csv` only
- Max file size: ≤50 MB
- Max target classes: ≤20
- Target variable: must be selected via Column Mapper in Step 2
- **Validation behavior when criteria fail:** Backend returns HTTP 400/422 with specific error message; user sees inline error in Step 2 UI

**Missing Value Handling (with clinical rationale):**
- **Median imputation:** Recommended for continuous clinical measurements (e.g., blood pressure, lab values) because the median is robust to outliers common in clinical data (e.g., extreme creatinine values in renal failure). Preserves central tendency without being skewed by pathological extremes.
- **Mode imputation:** Recommended for categorical variables (e.g., gender, diagnosis codes) where the most frequent value represents the typical case. Also appropriate for ordinal scales with limited values.
- **Drop rows (remove patients):** Recommended only when missingness is random and the dataset is large enough to absorb the loss. **Risk:** Systematic missingness (e.g., lab tests not ordered for low-risk patients) can introduce selection bias — the remaining data may over-represent sicker patients.

**Normalization (with clinical rationale):**
- **Z-score (standardization):** Recommended when features have different units/scales (e.g., combining age in years with creatinine in mg/dL). Essential for distance-based models (KNN, SVM). Maps to standard deviations from the mean — intuitive for clinicians who understand normal ranges.
- **Min-Max (0–1 scaling):** Recommended when the original value range is meaningful and bounded (e.g., satisfaction scores 1–10, percentages). Preserves zero values. Better for neural-network-style models (not used here) but still valid for SVM.
- **None:** Acceptable for tree-based models (Decision Tree, Random Forest, XGBoost, LightGBM) which are scale-invariant. **Risk:** KNN and SVM will be dominated by high-magnitude features if normalization is skipped.

**Class Imbalance — SMOTE:**
- **What it does:** Generates synthetic minority-class samples by interpolating between existing minority-class neighbors in feature space.
- **Why needed:** Clinical datasets often have severe class imbalance (e.g., sepsis prevalence ~10%, rare disease datasets <5% positive). Without SMOTE, models learn to predict the majority class and achieve high accuracy but miss the clinically important minority (e.g., 95% accuracy but 0% sensitivity for sepsis detection).
- **Why applied to training data only:** Applying SMOTE to test data would inflate performance metrics — the model would be tested on artificial data it implicitly learned from. Test data must reflect real-world class distribution.
- **How Step 3 displays it:** Before/after class distribution comparison chart showing original vs. SMOTE-balanced class counts.

**Effort:** ~45 minutes
**Risk:** Low-medium — clinical rationale is key. Must explain WHY, not just WHAT.

### Section 3.3: Data Privacy & Provenance (2 pts)

**Privacy Architecture:**
- **Browser-only upload → server-side in-memory processing:** User uploads CSV via browser; file is parsed by FastAPI backend into pandas DataFrame held in memory. No disk writes, no database storage, no external API calls with user data.
- **Session-only data lifecycle:** Each user session gets a UUID. Data is stored in an LRU cache (max 50 sessions). On eviction or browser close, all session data (datasets, trained models, SHAP values) is garbage-collected. No manual deletion needed.
- **Privacy notice:** Displayed in the tool interface informing users that data is processed in-session only.
- **What would change for real patient data under KVKK/GDPR:** Would need explicit consent mechanism (KVKK Article 5), data processing agreement, encryption at rest and in transit, right-to-deletion endpoint, data protection impact assessment (DPIA), appointed Data Protection Officer (DPO), audit trail for all data access.

**Provenance Tracking:**
- **Built-in datasets:** Source attribution documented in specialty registry (source URL, original authors, license). Step 2 UI displays dataset description and source.
- **User-uploaded data:** Upload timestamp, filename, row/column counts are captured per session. No persistent lineage tracking (out of educational scope).
- **What clinical deployment would need:** Automated data lineage system (e.g., Apache Atlas), immutable audit log, chain-of-custody documentation per KVKK Article 12.

**Bias in Data:**
- **Class imbalance:** Heart failure (~32% death), sepsis (~10% positive), several datasets have <30% minority class
- **Demographic representation:** Pima diabetes dataset contains only Pima Indian women; Indian Liver Patient dataset is single-country; several datasets lack ethnicity/race features entirely
- **Historical treatment disparities:** Datasets may encode historical biases (e.g., referral patterns, diagnostic thresholds that differ by gender)
- **Step 7 reference:** Training data representation chart shows per-subgroup sample sizes; auto-warning if subgroup has <30 samples

**Effort:** ~30 minutes
**Risk:** Low — factual documentation of existing architecture.

### Section 3.4: Third-Party & Dependency Register (3 pts)

Need at least **8 components** (aim for 12+ to exceed expectations).

| # | Component | Type | Version | License | Security Assessment | Risk Level | Alternative | Monitoring Plan |
|---|-----------|------|---------|---------|-------------------|------------|-------------|----------------|
| 1 | scikit-learn | ML Library | [from requirements.txt] | BSD-3-Clause | No known critical CVEs; actively maintained; 50k+ GitHub stars; monthly releases | L | TensorFlow, PyTorch | Pin version in requirements.txt; check release notes each sprint |
| 2 | XGBoost | ML Library | [from requirements.txt] | Apache 2.0 | Well-maintained; DMLC foundation; regular security patches | L | LightGBM, CatBoost | Pin version; monitor GitHub advisories |
| 3 | LightGBM | ML Library | [from requirements.txt] | MIT | Microsoft-maintained; active development; no known CVEs | L | XGBoost, CatBoost | Pin version; monitor GitHub advisories |
| 4 | SHAP | Explainability | [from requirements.txt] | MIT | Academic origin (Lundberg); widely adopted; some dependency chain risks | L | LIME, ELI5 | Pin version; monitor for breaking API changes |
| 5 | pandas | Data Library | [from requirements.txt] | BSD-3-Clause | NumFOCUS-sponsored; enterprise-grade; no critical vulnerabilities | L | Polars, Modin | Pin version; standard data library |
| 6 | FastAPI | Web Framework | [from requirements.txt] | MIT | Actively maintained by Tiangolo; Starlette-based; regular patches | L | Flask, Django | Pin version; monitor security advisories |
| 7 | imbalanced-learn | ML Library (SMOTE) | [from requirements.txt] | MIT | scikit-learn-contrib; well-tested; moderate release cadence | L | Custom SMOTE, ADASYN | Pin version; follows scikit-learn release cycle |
| 8 | ReportLab | PDF Generation | [from requirements.txt] | BSD | Established library; used in enterprise; occasional CVE patches | L | WeasyPrint, FPDF2 | Pin version; scan with pip-audit |
| 9 | React | Frontend Framework | 18.x [from package.json] | MIT | Meta-maintained; massive ecosystem; regular security patches | L | Vue, Svelte, Angular | Pin major version; monitor React security blog |
| 10 | Vite | Build Tool | [from package.json] | MIT | Evan You / team; fast iteration; active security response | L | Webpack, Turbopack | Pin version; monitor GitHub advisories |
| 11 | Recharts | Charting Library | [from package.json] | MIT | React-specific; moderate maintenance; no known CVEs | L | Chart.js, Plotly | Pin version; evaluate alternatives if unmaintained |
| 12 | python:3.12-slim | Docker Base Image | 3.12 | PSF License | Official Docker image; regular security rebuilds; scan with Trivy/Docker Scout | L | python:3.12-alpine | Rebuild on security advisories; scan in CI |
| 13 | node:20-slim | Docker Build Image | 20 (LTS) | MIT | Official Docker image; Node.js LTS; regular patches | L | node:22, alpine variant | Use LTS; rebuild on advisories |
| 14 | UCI ML Repository | Training Data Source | N/A | CC BY 4.0 / varies | Peer-reviewed datasets; academic standard; known limitations documented in 3.1 | M | Kaggle, PhysioNet | Check for dataset corrections/retractions annually |
| 15 | Kaggle Datasets | Training Data Source | N/A | Various (CC, Apache, etc.) | Community-sourced; quality varies; cross-reference with original publications | M | UCI, institutional data | Verify license compliance per dataset; monitor for takedowns |

**Effort:** ~45 minutes
**Risk:** Medium — need exact versions from lock files and honest security assessments.

---

## Phase 4: Assembly, Review & Submission

### Task 4.1: Compile into Word Template

- Open `ISO42001_Report_Template_V4_FINAL.docx`
- Fill cover page: Team Name, Team Members (all names)
- Fill Chapters 1–3 with content from Phases 1–3
- Keep all tables formatted consistently
- Remove all `[placeholder]` text — instructor will penalize unfilled brackets

### Task 4.2: Quality Review Against Grading Rubric

**Chapter 1 Checklist (15 pts):**
- [ ] Scope is clear and justified? IN/OUT boundaries explicit, every OUT has WHY (4 pts)
- [ ] At least 4 external + 3 internal issues, all project-specific, not generic (4 pts)
- [ ] Stakeholder register has ≥6 stakeholders, needs↔response mapping is consistent (4 pts)
- [ ] Professional writing quality, consistent formatting, no typos (3 pts)

**Chapter 2 Checklist (15 pts):**
- [ ] All 6 principles defined AND each references a specific tool feature (6 pts)
- [ ] Roles assigned with real names AND specific (not generic) responsibilities (4 pts)
- [ ] Policy references Section 1.2 scope; compliance commitments are logical; review schedule defined (3 pts)
- [ ] Professional writing quality (2 pts)

**Chapter 3 Checklist (15 pts):**
- [ ] All 20 datasets documented with provenance, limitations, and bias analysis (4 pts)
- [ ] Data quality criteria defined AND validation failure behavior explained (3 pts)
- [ ] Preprocessing strategies (missing values, normalization, SMOTE) have clinical rationale (3 pts)
- [ ] Privacy architecture and bias-in-data analysis are thorough, not surface-level (2 pts)
- [ ] Third-party register has ≥8 components with security assessment and monitoring plan (3 pts)

### Task 4.3: Cross-Reference Check

Verify every claim in the report can be traced to:
- A specific code file/function in the repository
- A specific Step in the 7-step wizard
- A specific feature visible in the UI

The instructor values **specificity** — "Step 7 bias detection" is better than "the tool checks for bias."

### Task 4.4: Final Submission

- Export as `.docx` (required format)
- Submit to WebOnline before **April 8, 2026, 1:00 PM**
- URL: https://webonline.cankaya.edu.tr/mod/assign/view.php?id=31025

---

## Execution Order & Time Estimates

| Order | Task | Dependency | Est. Time |
|-------|------|------------|-----------|
| 1 | Phase 0: Data extraction (all tasks parallel) | None | 2–3 hours |
| 2 | Phase 1: Chapter 1 (all sections) | Phase 0 | 2 hours |
| 3 | Phase 2: Chapter 2 (all sections) | Phase 0 + team name confirmation | 1.5 hours |
| 4 | Phase 3: Chapter 3 (all sections) | Phase 0 | 3 hours |
| 5 | Phase 4: Assembly + Review | Phases 1–3 | 1.5 hours |
| **Total** | | | **~10 hours** |

**Recommended approach:** Execute Phase 0 tasks with Claude (automated code extraction), then draft each chapter iteratively, filling the Word template section by section.

---

## Key Instructor Expectations (from the guidance notes)

1. **Specificity over generality:** Every claim must reference a concrete tool feature, Step number, or code artifact.
2. **Formal tone in Chapter 2:** The AI Policy must read like a real organizational policy, not student homework.
3. **Honest limitations in Chapter 3:** Don't pretend datasets are perfect — document known biases, imbalances, and gaps.
4. **Clinical rationale for technical choices:** Explain WHY median imputation suits clinical data, not just THAT you use it.
5. **All 20 datasets must be documented** — no shortcuts, no "see table for remaining."
6. **At least 8 third-party components** with security assessment — this is where most teams under-deliver.
7. **The OUT-OF-SCOPE column is as important as IN-SCOPE** — every exclusion needs a justification.

---

## What This Plan Does NOT Cover (Future Submission)

The following chapters are due May 5, 2026 (final submission) and are explicitly excluded from this plan:
- Chapter 4: Risk Management & AI Impact Assessment (15 pts)
- Chapter 5: Model Documentation, Lifecycle & Monitoring (15 pts)
- Chapter 6: Peer Audit, Self-Assessment & Lessons Learned (15 pts)
- Chapter 7: Individual Reflection (10 pts per person)
- Appendix A: Statement of Applicability (SoA)
- Appendix B: Instructor Feedback Form (filled by instructor)

These will be addressed after receiving instructor feedback on Chapters 1–3 (expected April 8–15).
