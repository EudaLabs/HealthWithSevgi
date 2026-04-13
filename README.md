<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React_18-61DAFB?logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white" alt="scikit-learn" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Python_3.12-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/SHAP-blueviolet" alt="SHAP" />
  <img src="https://img.shields.io/badge/License-Academic-lightgrey" alt="License" />
</p>

# HealthWithSevgi

**An interactive, browser-based machine learning education tool for healthcare professionals.**

> **SENG 430 - Software Quality Assurance**
> Cankaya University - Spring 2025-2026
> Instructor: Dr. Sevgi Koyuncu Tunç

HealthWithSevgi guides clinicians through a complete ML pipeline in **7 steps** — from selecting a medical specialty to training a model, interpreting predictions with SHAP, and auditing fairness — all with **zero coding required**.

<p align="center">
  <a href="https://0xbatuhan4-healthwithsevgi.hf.space/"><strong>Live Demo</strong></a> &nbsp;|&nbsp;
  <a href="https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1"><strong>Jira Board</strong></a> &nbsp;|&nbsp;
  <a href="https://www.figma.com/design/1K1Dw8PC6P98NZAa30DzII/430-HealthWithSevgi"><strong>Figma Designs</strong></a> &nbsp;|&nbsp;
  <a href="SETUP.md"><strong>Setup Guide</strong></a>
</p>

---

## Table of Contents

- [Overview](#overview)
- [The 7-Step Pipeline](#the-7-step-pipeline)
- [Supported Specialties](#supported-specialties)
- [ML Models](#ml-models)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Deployment](#deployment)
- [Branch Strategy](#branch-strategy)
- [Team](#team)
- [License](#license)

---

## Overview

Healthcare professionals increasingly encounter AI/ML in clinical settings but rarely get hands-on experience with how these systems work. HealthWithSevgi bridges that gap by providing an intuitive, wizard-style interface that walks users through every stage of the machine learning lifecycle using real clinical datasets.

**Key capabilities:**

- **20 medical specialties** with real-world clinical datasets (Cardiology, Oncology, Nephrology, Neurology, ICU/Sepsis, Dermatology, and more)
- **8 ML classifiers** with interactive hyperparameter tuning via sliders
- **SHAP-based explainability** — global feature importance and single-patient waterfall explanations
- **Fairness auditing** — subgroup performance analysis across demographics with bias detection
- **EU AI Act compliance checklist** with downloadable PDF certificate
- **No server-side data storage** — all session data is held in-memory and evicted automatically

---

## The 7-Step Pipeline

| Step | Name | What Happens |
|:----:|------|-------------|
| **1** | **Clinical Context** | Introduces the medical problem the AI will address. Displays the clinical question, why it matters, and the 7-step roadmap. |
| **2** | **Data Exploration** | Upload a CSV file (up to 50 MB) or load a built-in clinical dataset. Inspect column statistics, missing values, and class distribution. Confirm the target variable. |
| **3** | **Data Preparation** | Configure preprocessing: train/test split ratio, missing value strategy (median/mode/drop), normalization (z-score/min-max), SMOTE for class imbalance, and outlier handling (IQR/z-score clipping). |
| **4** | **Model & Parameters** | Choose from 8 ML models. Adjust hyperparameters with intuitive sliders. Optionally enable hyperparameter tuning (RandomizedSearchCV) and feature selection (VarianceThreshold + SelectKBest). |
| **5** | **Results & Evaluation** | View accuracy, sensitivity, specificity, precision, F1, AUC-ROC, and MCC. Explore interactive ROC curves, precision-recall curves, and confusion matrices. Detect overfitting via cross-validation comparison. |
| **6** | **Explainability** | Global feature importance ranking with clinical name mapping. Single-patient SHAP waterfall charts with plain-language summaries (e.g., _"High glucose increases diabetes risk by 0.23"_). |
| **7** | **Ethics & Bias** | Subgroup fairness audit (by age, gender, ethnicity). Bias warnings for performance gaps >10%. EU AI Act compliance checklist. Real-world case studies of AI bias in healthcare. Downloadable PDF compliance certificate. |

---

## Supported Specialties

| # | Specialty | Prediction Task | Dataset | Samples |
|---|-----------|-----------------|---------|--------:|
| 1 | Cardiology | 30-day heart failure mortality | Heart Failure Clinical Records | ~300 |
| 2 | Radiology | Pneumonia detection (chest X-ray metadata) | NIH Chest X-ray | 100K+ |
| 3 | Nephrology | Chronic kidney disease detection | UCI CKD | 400 |
| 4 | Oncology - Breast | Malignant vs. benign biopsy | Wisconsin Breast Cancer | 569 |
| 5 | Neurology - Parkinson's | Parkinson's from voice biomarkers | UCI Parkinson's | 195 |
| 6 | Endocrinology - Diabetes | Diabetes onset within 5 years | Pima Indians | 768 |
| 7 | Hepatology - Liver | Liver disease detection | Indian Liver Patient | 583 |
| 8 | Cardiology - Stroke | Stroke risk prediction | Kaggle Stroke Prediction | 5,110 |
| 9 | Mental Health | Depression severity (PHQ-9) | Kaggle Depression | ~1,000 |
| 10 | Pulmonology - COPD | COPD exacerbation risk | PhysioNet + Kaggle | ~1,000 |
| 11 | Haematology - Anaemia | Anaemia type classification | Kaggle Anaemia | ~400 |
| 12 | Dermatology | Benign vs. malignant skin lesion | HAM10000 metadata | ~10K |
| 13 | Ophthalmology | Diabetic retinopathy detection | UCI Diabetic Retinopathy | 1,151 |
| 14 | Orthopaedics - Spine | Disc herniation / spondylolisthesis | UCI Vertebral Column | 310 |
| 15 | ICU / Sepsis | Sepsis onset within 6 hours | PhysioNet Sepsis | ~40K |
| 16 | Obstetrics - Fetal Health | Fetal health classification (CTG) | UCI Fetal Health | 2,126 |
| 17 | Cardiology - Arrhythmia | Arrhythmia detection (ECG) | UCI Arrhythmia | 452 |
| 18 | Oncology - Cervical | Cervical cancer risk | UCI Cervical Cancer | 858 |
| 19 | Thyroid / Endocrinology | Thyroid function classification | UCI Thyroid | 9,172 |
| 20 | Pharmacy - Readmission | Hospital readmission risk | UCI Diabetes 130-US | 101,766 |

---

## ML Models

| Model | Category | Key Hyperparameters |
|-------|----------|---------------------|
| **K-Nearest Neighbors** | Instance-based | k (1-25), distance metric |
| **Support Vector Machine** | Boundary-based | C (0.01-100), kernel (linear/rbf/poly) |
| **Decision Tree** | Tree-based | max_depth (1-20), criterion (gini/entropy) |
| **Random Forest** | Ensemble | n_estimators (10-500), max_depth |
| **Logistic Regression** | Linear | C (0.001-100), solver (lbfgs/saga) |
| **Naive Bayes** | Probabilistic | var_smoothing (1e-12 to 1e-3) |
| **XGBoost** | Gradient Boosting | n_estimators, max_depth, learning_rate |
| **LightGBM** | Gradient Boosting | n_estimators, max_depth, learning_rate |

All models are trained with balanced class weights where supported. Optional hyperparameter tuning uses RandomizedSearchCV (20 iterations, 3-fold CV). Feature selection combines VarianceThreshold with SelectKBest (mutual information).

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, TypeScript, Vite | Single-page wizard application |
| **UI Components** | Recharts, Lucide Icons, react-dropzone | Charts, icons, file uploads |
| **State Management** | TanStack React Query | Server state caching and synchronization |
| **Backend** | FastAPI, Python 3.12 | REST API with auto-generated OpenAPI docs |
| **ML Engine** | scikit-learn, XGBoost, LightGBM | Model training, evaluation, cross-validation |
| **Explainability** | SHAP | TreeExplainer (tree models), KernelExplainer (linear), permutation importance |
| **Data Processing** | pandas, numpy, imbalanced-learn | Data cleaning, normalization, SMOTE |
| **PDF Generation** | ReportLab | Compliance certificate export |
| **Containerization** | Docker (multi-stage) | Production deployment |
| **Hosting** | HuggingFace Spaces | Live demo environment |
| **Package Manager** | pnpm (frontend), pip (backend) | Dependency management |

---

## Architecture

📐 **[Full Architecture Diagrams (Google Drive)](https://drive.google.com/drive/folders/1AkMxaaPLizfPlfJDjkP7YISSiOEiL9tV?usp=sharing)** — C4 model diagrams (System Context, Container, Component, Code levels), toolchain diagrams, and data flow sequences.

```
                          +---------------------+
                          |   Browser (React)   |
                          |   Wizard UI (SPA)   |
                          +----------+----------+
                                     |
                            HTTP/REST (JSON)
                                     |
                          +----------v----------+
                          |   FastAPI Backend    |
                          +----------+----------+
                                     |
              +----------------------+----------------------+
              |              |              |                |
     +--------v---+  +------v-----+  +-----v------+  +-----v--------+
     | DataService|  | MLService  |  |ExplainSvc  |  | EthicsService|
     |            |  |            |  |            |  |              |
     | - Explore  |  | - Train    |  | - SHAP     |  | - Subgroup   |
     | - Prepare  |  | - Evaluate |  | - Waterfall|  | - Bias detect|
     | - SMOTE    |  | - Compare  |  | - Clinical |  | - EU AI Act  |
     +-----+------+  +------+-----+  +------+-----+  +------+-------+
           |                |                |                |
           v                v                v                v
     +-----------+   +------------+   +------------+   +-----------+
     | In-Memory |   | In-Memory  |   |   SHAP     |   | ReportLab |
     | Sessions  |   | Models     |   |  Library   |   |  PDF Gen  |
     | (LRU 50)  |   | (LRU 100+)|   |            |   |           |
     +-----------+   +------------+   +------------+   +-----------+
```

**Data flow:** Upload CSV -> Explore columns -> Preprocess (split, normalize, SMOTE) -> Train model -> Evaluate metrics -> SHAP explanations -> Fairness audit -> PDF certificate

---

## Project Structure

```
HealthWithSevgi/
|
+-- frontend/                         # React 18 + Vite + TypeScript
|   +-- src/
|   |   +-- pages/                    # Step 1-7 wizard pages
|   |   |   +-- Step1ClinicalContext.tsx
|   |   |   +-- Step2DataExploration.tsx
|   |   |   +-- Step3DataPreparation.tsx
|   |   |   +-- Step4ModelParameters.tsx
|   |   |   +-- Step5Results.tsx
|   |   |   +-- Step6Explainability.tsx
|   |   |   +-- Step7Ethics.tsx
|   |   +-- components/               # Reusable UI components
|   |   |   +-- NavBar.tsx            # Specialty switcher, glossary
|   |   |   +-- WizardProgress.tsx    # Step progress tracker
|   |   |   +-- SpecialtySelector.tsx # 20-specialty grid
|   |   |   +-- ColumnMapperModal.tsx # Target column confirmation
|   |   |   +-- ErrorModal.tsx       # Error display modal
|   |   |   +-- charts/              # Visualization components
|   |   |       +-- ConfusionMatrixChart.tsx  # 2x2 confusion matrix
|   |   |       +-- KNNScatterCanvas.tsx     # KNN decision boundary
|   |   |       +-- PRCurveChart.tsx         # Precision-Recall curve
|   |   |       +-- ROCCurveChart.tsx        # ROC curve with AUC badge
|   |   +-- api/                      # API client layer
|   |   |   +-- client.ts            # Axios instance + interceptors
|   |   |   +-- specialties.ts       # Specialty endpoints
|   |   |   +-- data.ts              # Explore + Prepare endpoints
|   |   |   +-- ml.ts                # Train + Compare endpoints
|   |   |   +-- explain.ts           # Explainability + Ethics + Certificate
|   |   +-- types/index.ts           # Shared TypeScript interfaces
|   |   +-- styles/globals.css        # Global CSS + theme variables
|   |   +-- App.tsx                   # Main wizard state manager
|   |   +-- main.tsx                  # Application entry point
|   +-- package.json
|   +-- vite.config.ts
|
+-- backend/                          # FastAPI REST API + ML engine
|   +-- app/
|   |   +-- main.py                   # FastAPI setup, CORS, routers
|   |   +-- routers/
|   |   |   +-- data_router.py        # /specialties, /explore, /prepare
|   |   |   +-- ml_router.py          # /train, /compare, /models
|   |   |   +-- explain_router.py     # /explain/*, /ethics, /certificate
|   |   +-- services/
|   |   |   +-- data_service.py       # Dataset loading, exploration, preprocessing
|   |   |   +-- ml_service.py         # Model building, training, evaluation
|   |   |   +-- explain_service.py    # SHAP explanations, clinical mapping
|   |   |   +-- ethics_service.py     # Fairness audit, bias detection
|   |   |   +-- certificate_service.py # PDF certificate generation
|   |   |   +-- specialty_registry.py # 20 specialty definitions + datasets
|   |   +-- models/
|   |   |   +-- schemas.py            # Data exploration/preparation DTOs
|   |   |   +-- ml_schemas.py         # Training/evaluation DTOs
|   |   |   +-- explain_schemas.py    # Explainability/ethics DTOs
|   |   +-- utils/                    # Utility modules
|   +-- data_cache/                   # Cached clinical CSV datasets
|   +-- datasets/                     # Additional dataset storage
|   +-- tests/                        # pytest test suite (178 tests)
|   |   +-- conftest.py              # Shared fixtures
|   |   +-- test_step1_clinical_context.py
|   |   +-- test_step2_data_exploration.py
|   |   +-- test_step3_data_preparation.py
|   |   +-- test_step6_explainability.py
|   |   +-- test_step7_ethics.py
|   |   +-- test_certificate.py
|   +-- pytest.ini
|   +-- requirements.txt
|
+-- hf-space/                         # HuggingFace Spaces deployment
|   +-- main_hf.py                    # Combined API + SPA entrypoint
|   +-- Dockerfile                    # HF-specific Docker build
|   +-- README.md                     # HF Space metadata
|
+-- docs/                             # Documentation & design specs
|   +-- ML_Tool_User_Guide.md         # Course user manual
|   +-- Sprint_1_Assignment.md        # Sprint 1 requirements
|   +-- Clinical_Specialties_Dataset_Collection.pdf
|   +-- diagrams/                     # C4 architecture + toolchain PDFs
|   +-- drawio/                       # Editable draw.io source files
|   +-- mermaid/                      # C4 architecture (Mermaid source)
|   +-- iso42001/                     # ISO 42001 AI governance report
|   +-- seng430-sprints/              # Sprint requirements from instructor
|   +-- qa/                           # QA test reports (PDF)
|   +-- reports/                      # Progress reports + screenshots
|
+-- jira/                             # Jira backlog documentation
|   +-- JIRA.md                       # Product backlog report
|   +-- SPRINT_1_TASK_BOARD.md        # Sprint 1 task breakdown
|
+-- local/                            # Local-only extensions
|   +-- model-arena/                  # Model Arena comparison feature
|       +-- arena/                    # Backend (router, service, schemas)
|       +-- frontend/                 # Frontend (ArenaPage, charts, hooks)
|
+-- .github/
|   +-- pull_request_template.md      # PR template linked to Jira
|   +-- workflows/deploy-hf.yml      # Auto-deploy to HuggingFace on release
|
+-- Dockerfile                        # Multi-stage build (Node + Python)
+-- docker-compose.yml                # Local development orchestration
+-- .dockerignore
+-- .gitignore
+-- CLAUDE.md                         # AI coding assistant context
+-- SETUP.md                          # Local development setup guide
+-- README.md
```

---

## Live Demo & Docker

### 🌐 Live Demo

The application is deployed on HuggingFace Spaces — no installation required:

**➡️ [0xbatuhan4-healthwithsevgi.hf.space](https://0xbatuhan4-healthwithsevgi.hf.space/)**

### 🐳 Docker (single command)

Pull and run the pre-built container image from GitHub Container Registry:

```bash
docker run -p 7860:7860 ghcr.io/eudalabs/healthwithsevgi:latest
```

Open **http://localhost:7860** — that's it.

Alternatively, build from source:

```bash
git clone https://github.com/EudaLabs/HealthWithSevgi.git
cd HealthWithSevgi
docker build -t healthwithsevgi .
docker run -p 7860:7860 healthwithsevgi
```

### Docker Compose (local development)

```bash
git clone https://github.com/EudaLabs/HealthWithSevgi.git
cd HealthWithSevgi
docker-compose up --build
```

This starts both the backend API and frontend dev server with hot-reload.

---

## Quick Start

### Prerequisites (for local development)

| Tool | Version | Required For |
|------|---------|-------------|
| Python | >= 3.10 | Backend |
| Node.js | >= 18 | Frontend |
| Git | latest | Version control |

### Local Development

**Backend:**

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8001
```

API docs available at: **http://localhost:8001/docs** (Swagger UI)

**Frontend** (in a separate terminal):

```bash
cd frontend

# Install dependencies
pnpm install

# Start the dev server
pnpm dev
```

App available at: **http://localhost:5173** (proxies `/api` requests to port 8001)

### Environment Variables

Create a `.env` file in the project root:

```env
# Backend
BACKEND_PORT=8001
DEBUG=true

# Frontend (Vite uses VITE_ prefix)
VITE_API_URL=http://localhost:8001
```

---

## API Reference

All endpoints are prefixed with `/api`. Full interactive documentation is available at `/docs` when the backend is running.

### Specialties

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/specialties` | List all 20 specialties |
| `GET` | `/api/specialties/{id}` | Get specialty details (description, features, clinical context) |

### Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/explore` | Upload CSV or load built-in dataset; returns column stats + class distribution |
| `POST` | `/api/prepare` | Preprocess data (split, normalize, SMOTE); returns `session_id` |

### ML Training

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/train` | Train a model; returns `model_id` + evaluation metrics |
| `POST` | `/api/compare/{model_id}` | Add model to comparison table |
| `GET` | `/api/compare/{session_id}` | Get all compared models for a session |
| `DELETE` | `/api/compare/{session_id}` | Clear comparison table |
| `GET` | `/api/models/{model_id}` | Get model metadata |

### Explainability

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/explain/global/{model_id}` | Global feature importance (top 10 features + clinical names) |
| `GET` | `/api/explain/patient/{model_id}/{index}` | Single-patient SHAP waterfall explanation |

### Ethics & Certificate

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ethics/{model_id}` | Subgroup fairness audit + bias warnings + checklist |
| `POST` | `/api/ethics/checklist` | Update EU AI Act checklist item |
| `POST` | `/api/certificate` | Generate and download PDF compliance certificate |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Status check (`{status: "ok"}`) |
| `GET` | `/health` | Health probe (`{status: "healthy"}`) |

---

## Testing

The project includes a comprehensive pytest suite covering all 7 steps of the pipeline — **178 tests** across 6 test files.

```bash
cd backend

# Run all tests
pytest -v

# Run a specific test file
pytest -v tests/test_step1_clinical_context.py

# Run only slow tests (domain context validation)
pytest -v -m slow
```

**Test coverage:**

| Test File | Covers | Key Assertions |
|-----------|--------|----------------|
| `test_step1_clinical_context.py` | Specialty registry | All 20 specialties present, required fields non-empty, clinical context > 50 chars, 404 handling |
| `test_step2_data_exploration.py` | Data exploration | CSV upload validation, missing value detection, class distribution, imbalance warnings |
| `test_step3_data_preparation.py` | Preprocessing | Missing strategies (median/mode/drop), normalization, train/test split, SMOTE, data leakage prevention |
| `test_step6_explainability.py` | SHAP explanations | Global importance, patient explanation, What-If analysis, sample patient selection |
| `test_step7_ethics.py` | Fairness audit | Ethics endpoint, case study severity, checklist toggle, bias detection thresholds |
| `test_certificate.py` | PDF generation | Certificate content type, PDF magic bytes, checklist state persistence |

**Total: 178 tests — all passing.**

---

## Deployment

### HuggingFace Spaces

The production deployment runs on HuggingFace Spaces as a Docker container. The multi-stage Dockerfile:

1. **Stage 1** — Builds the React frontend with pnpm
2. **Stage 2** — Installs Python dependencies
3. **Stage 3** — Combines both into a slim Python 3.12 runtime serving the SPA + API on port 7860

`hf-space/main_hf.py` serves both the FastAPI backend and the static React build from a single process.

**Live demo:** [0xbatuhan4-healthwithsevgi.hf.space](https://0xbatuhan4-healthwithsevgi.hf.space/)

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready, protected |
| `develop` | Integration branch for sprint work |
| `feature/US-XXX` | One branch per user story |

**Rules:**
- All changes go through Pull Requests (use the [PR template](.github/pull_request_template.md))
- PRs require at least 1 approval
- `main` and `develop` are protected — no direct pushes
- PR titles follow: `feat/fix/docs(US-XXX): description`

---

## Team

| Role | Name | Student ID |
|------|------|:----------:|
| Product Owner + Developer | Efe Çelik | 202128016 |
| UX Designer | Burak Aydoğmuş | 202128028 |
| Lead Developer + Scrum Master | Batuhan Bayazıt | 202228008 |
| Developer | Berat Mert Gökkaya | 202228019 |
| QA / Documentation Lead | Berfin Duru Alkan | 202228005 |

---

## Links

- **Jira Board:** [Jira](https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog)
- **Figma Designs:** [Figma](https://www.figma.com/design/1K1Dw8PC6P98NZAa30DzII/430-HealthWithSevgi?node-id=0-1)
- **GitHub Wiki:** [Wiki](../../wiki)
- **API Docs:** `http://localhost:8001/docs` (when running locally)

---

## License

This project is developed as part of the **SENG 430 Software Quality Assurance** course at Cankaya University. All rights reserved.
