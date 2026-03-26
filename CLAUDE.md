# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HealthWithSevgi is a browser-based ML education tool for healthcare professionals. It walks users through a 7-step wizard pipeline (Clinical Context → Data Exploration → Data Preparation → Model & Parameters → Results → Explainability → Ethics & Bias) using real clinical datasets across 20 medical specialties. Academic project for SENG 430 at Cankaya University.

## Commands

### Backend (FastAPI + Python 3.12)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

### Frontend (React 18 + Vite + TypeScript)
```bash
cd frontend
pnpm install
pnpm dev          # starts on :5173, proxies /api → :8001
pnpm build        # production build
```

### Tests
```bash
cd backend
pytest -v                                        # all tests
pytest -v tests/test_step1_clinical_context.py   # single file
pytest -v -m slow                                # slow tests only
```

### Docker (single-process HuggingFace Spaces deployment)
```bash
docker build -t healthwithsevgi -f hf-space/Dockerfile . && docker run -p 7860:7860 healthwithsevgi
```

## Architecture

**Two-process local dev:** React SPA on :5173 ↔ Vite proxy (`/api`) ↔ FastAPI on :8001. In production (HuggingFace Spaces), `hf-space/main_hf.py` serves both the API and the static frontend build from a single uvicorn process on :7860.

**Backend service layer:** Singleton service instances are attached to `app.state` in `main.py` and accessed in routers via `request.app.state.<service>`. All session data lives in-memory (LRU caches) — no database.

| Service | Purpose |
|---------|---------|
| `DataService` | CSV upload, explore columns, preprocess (split/normalize/SMOTE) |
| `MLService` | Train 8 model types (KNN, SVM, DT, RF, LR, NB, XGBoost, LightGBM), evaluate, compare |
| `ExplainService` | SHAP global importance + single-patient waterfall |
| `EthicsService` | Subgroup fairness audit, bias detection |
| `CertificateService` | ReportLab PDF generation for EU AI Act compliance |
| `specialty_registry` | Static registry of 20 specialties with dataset configs |

**Routers** are prefixed with `/api` and split into three files: `data_router.py` (specialties, explore, prepare), `ml_router.py` (train, compare), `explain_router.py` (SHAP, ethics, certificate).

**Frontend state:** `App.tsx` holds a single `WizardState` object (via `useState`) that tracks current step, specialty, exploration data, prep settings/response, training response, and compared models. Steps 5 and 6 are lazy-loaded. Each step page lives in `frontend/src/pages/Step{N}*.tsx`.

**API client:** `frontend/src/api/client.ts` exports an Axios instance with `baseURL: '/api'` and 120s timeout. Endpoint modules (`specialties.ts`, `data.ts`, `ml.ts`, `explain.ts`) wrap specific calls. Server state is managed with TanStack React Query.

**Types:** All shared TypeScript interfaces are in `frontend/src/types/index.ts`.

## Key Patterns

- **No external database.** All session state (datasets, trained models, SHAP values) is in-memory with LRU eviction.
- **Pydantic schemas** in `backend/app/models/` define request/response DTOs: `schemas.py` (data), `ml_schemas.py` (training), `explain_schemas.py` (SHAP/ethics).
- **Tests** use FastAPI `TestClient` with a session-scoped fixture (`conftest.py`). CSV fixtures generate synthetic clinical data for the endocrinology_diabetes specialty.
- **CSS** is plain CSS with custom properties (CSS variables for theming) in `frontend/src/styles/globals.css` — no Tailwind or CSS-in-JS.
- **Charts** (ROC, PR, confusion matrix) use Recharts in `frontend/src/components/charts/`.

## Git Rules

- **Never add a Co-Authored-By line for Claude.** Commits must only credit human authors.

## Branch Strategy

- `main` — production, protected
- `develop` — integration branch
- `feature/US-XXX` — per user story
- PR titles: `feat/fix/docs(US-XXX): description`
