# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HealthWithSevgi is a browser-based ML education tool for healthcare professionals. It walks users through a 7-step wizard pipeline (Clinical Context → Data Exploration → Data Preparation → Model & Parameters → Results → Explainability → Ethics & Bias) using real clinical datasets across 20 medical specialties. Academic project for SENG 430 at Cankaya University.

## Repository Map

Top-level layout — every directory below has a distinct purpose; do not relocate code without checking the deploy workflow (`.github/workflows/deploy-hf.yml`) which copies specific paths.

```
HealthWithSevgi/
├── backend/                 FastAPI app, datasets, pytest suite (Python 3.12 + venv)
│   ├── app/
│   │   ├── main.py          App factory; mounts services + 3 routers + Model Arena
│   │   ├── routers/         data_router, ml_router, explain_router (all /api/*)
│   │   ├── services/        Singleton services attached to app.state
│   │   ├── models/          Pydantic request/response schemas (3 files)
│   │   └── utils/           (currently empty placeholder)
│   ├── data_cache/          ⚠️ Real bundled CSV/ARFF datasets live HERE, not in datasets/
│   ├── datasets/            Empty placeholder (kept for legacy path references)
│   ├── tests/               pytest — one file per wizard step + certificate + arena
│   ├── pytest.ini           Defines slow marker; addopts = -v --tb=short
│   └── requirements.txt
├── frontend/                React 18 + Vite + TS SPA (uses pnpm, NOT npm)
│   ├── src/
│   │   ├── App.tsx          Holds the single WizardState object
│   │   ├── pages/           Step1-Step7 wizard pages (one per step)
│   │   ├── components/      NavBar, WizardProgress, modals, charts/
│   │   ├── components/charts/  Recharts + custom canvases (ROC, PR, confusion, KNN, parallel coords)
│   │   ├── api/             Axios client + endpoint modules (specialties/data/ml/explain)
│   │   ├── types/index.ts   ALL shared TS interfaces (single barrel file)
│   │   ├── styles/globals.css  Plain CSS with CSS custom properties — no Tailwind
│   │   ├── data/glossary.ts Static term glossary used by InfoTip
│   │   └── hooks/, utils/   Currently empty placeholders
│   └── vite.config.ts       Aliases force shared deps to resolve from frontend/node_modules
│                            (so the local/model-arena frontend uses the same React copy)
├── local/model-arena/       Model-comparison sub-feature mounted onto the same FastAPI app
│   ├── arena/               Python: router (prefix=/api/arena), service, schemas
│   └── frontend/            React components imported by the main wizard at build time
├── hf-space/                Single-process HuggingFace Spaces deployment target
│   ├── Dockerfile           Used by both `docker build` AND the GitHub Release workflow
│   ├── main_hf.py           Replaces backend main.py: serves API + static frontend on :7860
│   └── README.md            HF Space metadata header
├── scripts/qa/              QA automation pipeline (Sprint 5 deliverables #14, #15)
│   ├── walkthrough.sh       agent-browser worker — 13 deterministic steps per specialty
│   ├── orchestrate.sh       Mode B: xargs -P4 fan-out (Mode A = Claude subagents)
│   ├── render_report.py     jinja2 → HTML → Chrome --print-to-pdf → PDF
│   ├── lib/                 Shared constants (step labels, screenshot names)
│   ├── tests/               Self-tests per layer (walkthrough_dry, render_fake)
│   └── runs/<run-id>/       Per-run evidence: screenshots/, evidence.json, walkthrough.log
├── docs/                    All written deliverables — see "Docs Map" below
├── .github/workflows/       Single workflow: deploy-hf.yml (triggers on Release publish)
├── jira/                    Sprint 1 task board snapshots (historical)
├── qa_screenshots/          Sprint 4 manual QA screenshots (historical)
├── sprint4_submission/      Sprint 4 final-submission artefact
├── temp/                    Scratch area: Figma captures, design drafts (not deployed)
├── Dockerfile               Two-process compose target (separate from hf-space/Dockerfile)
├── docker-compose.yml       Dev/prod compose: backend + frontend
├── README.md                User-facing project description
├── SETUP.md                 Local-dev quickstart (mostly redundant with this file)
├── ATTRIBUTION.md, DATA_LICENSES.md, LICENSE
└── CLAUDE.md                THIS FILE
```

## Where to Find What

| Looking for… | Path |
|---|---|
| The 7 wizard step pages (UI) | `frontend/src/pages/Step{1..7}*.tsx` |
| Backend service for a feature | `backend/app/services/{data,ml,explain,ethics,certificate,insight}_service.py` |
| Pydantic schema for an endpoint | `backend/app/models/{schemas,ml_schemas,explain_schemas}.py` |
| The 20 specialties registry | `backend/app/services/specialty_registry.py` |
| Bundled clinical datasets | `backend/data_cache/*.csv` and `*.arff` (NOT `backend/datasets/`) |
| API client + endpoint wrappers | `frontend/src/api/{client,specialties,data,ml,explain}.ts` |
| Shared TS types | `frontend/src/types/index.ts` (single barrel) |
| CSS variables / theming | `frontend/src/styles/globals.css` |
| Charts (ROC/PR/Confusion/KNN/parallel) | `frontend/src/components/charts/` |
| Model Arena (compare-many-models) backend | `local/model-arena/arena/{router,service,schemas}.py` |
| Model Arena UI components | `local/model-arena/frontend/` (imported by main wizard) |
| HF Space production entry | `hf-space/main_hf.py` (≠ `backend/app/main.py`) |
| Two-process Dockerfile | `Dockerfile` at repo root |
| Single-process (HF) Dockerfile | `hf-space/Dockerfile` |
| Tests (per wizard step) | `backend/tests/test_step{1..7}_*.py` |
| Test fixtures / TestClient setup | `backend/tests/conftest.py` |
| QA automation entry script | `scripts/qa/walkthrough.sh` (Sprint 5 #14/#15 deliverable) |
| QA automation design + plan | `docs/superpowers/specs/2026-04-21-qa-automation-design.md` + `docs/superpowers/plans/2026-04-21-qa-automation.md` |
| Per-run QA evidence | `scripts/qa/runs/<run-id>/screenshots/` + `evidence.json` |
| C4 architecture diagrams (PDFs) | `docs/diagrams/c4-level{1,2,3a,3b,4a,4b}-*.drawio.pdf` |
| Editable C4 source | `docs/drawio/*.drawio` (open in draw.io) |
| Mermaid versions of diagrams | `docs/mermaid/{c4-architecture,toolchain}.md` |
| Sprint reports (master narrative) | `docs/seng430-sprints/sprint-{2..5}.md`, `master.md`, `final-submission.md` |
| Wiki pages (delivered to course) | `docs/wiki/{Sprint-3,Sprint-4,Sprint-5,Final-Submission}.md` |
| Sprint progress reports + screenshots | `docs/reports/Sprint{N}_*.{pdf,html,png,jpg}` |
| ISO 42001 deliverable | `docs/iso42001/ISO42001_Report_Ch1-3_FILLED.docx` (+ DRAFT.md, generators) |
| Lighthouse audit (current + baseline) | `docs/reports/Sprint5_Lighthouse.report.{html,json,png}` (+ `.baseline.*`) |
| GitHub release → HF Space deploy | `.github/workflows/deploy-hf.yml` |

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

**Model Arena extension:** `local/model-arena/` is mounted onto the same FastAPI app at runtime — `backend/app/main.py` adds `local/model-arena` to `sys.path`, imports `arena.router` (prefix `/api/arena`), and instantiates `ArenaService(app.state.ml_service)`. The deploy workflow copies `local/model-arena/arena/` into the container next to `app/`. The arena's frontend code lives in `local/model-arena/frontend/` and is imported directly into the main React build (no separate bundle), which is why `frontend/vite.config.ts` aliases shared deps (react, recharts, nivo, plotly) to `frontend/node_modules` — otherwise resolving fails for files outside `frontend/src/`.

**Two production targets, two entry points:**

- `Dockerfile` + `docker-compose.yml` at repo root → two containers (backend + frontend), used for local prod-like runs.
- `hf-space/Dockerfile` + `hf-space/main_hf.py` → single uvicorn process serving API and static frontend on `:7860`. This is what `.github/workflows/deploy-hf.yml` builds and force-pushes to the HuggingFace Space on every GitHub Release. The two `main.py` files are **not** kept in sync automatically — when adding a service, register it in both.

## Key Patterns

- **No external database.** All session state (datasets, trained models, SHAP values) is in-memory with LRU eviction.
- **Pydantic schemas** in `backend/app/models/` define request/response DTOs: `schemas.py` (data), `ml_schemas.py` (training), `explain_schemas.py` (SHAP/ethics).
- **Tests** use FastAPI `TestClient` with a session-scoped fixture (`conftest.py`). CSV fixtures generate synthetic clinical data for the endocrinology_diabetes specialty.
- **CSS** is plain CSS with custom properties (CSS variables for theming) in `frontend/src/styles/globals.css` — no Tailwind or CSS-in-JS.
- **Charts** (ROC, PR, confusion matrix) use Recharts in `frontend/src/components/charts/`.
- **Datasets at runtime** are read from `backend/data_cache/`, not the (empty) `backend/datasets/` directory. The deploy workflow copies both into the container.
- **Frontend uses pnpm exclusively.** Both `package-lock.json` and `pnpm-lock.yaml` exist; `pnpm-lock.yaml` is authoritative — the GitHub workflow runs `pnpm install --frozen-lockfile`.

## Docs Map

`docs/` is large because the project ships academic deliverables alongside the codebase. Subdirectory purposes:

| Path | Purpose |
|---|---|
| `docs/wiki/` | Final pages handed to the course wiki — one per sprint plus `Final-Submission.md`, `Accessibility-Log.md`, `Domain-Clinical-Review.md`. Hyperparameter screenshots `01..08-*-params.png` document the 8 model-type forms. |
| `docs/seng430-sprints/` | Sprint planning + retrospective markdown (`sprint-2.md`…`sprint-5.md`, `master.md`, `final-submission.md`). Source-of-truth narrative; the wiki pages are derived from these. |
| `docs/reports/` | Every generated artefact (PDF/HTML/PNG): weekly progress reports, screenshot reports, Lighthouse audits (current + `.baseline.*`), Sprint 5 burndown, bug-fix log, consent form, E2E regression PDF. |
| `docs/reports/coverage/`, `docs/reports/qa/`, `docs/reports/media/` | Coverage HTML, QA evidence subsets, embedded media. |
| `docs/diagrams/` | Rendered C4 model PDFs (Levels 1–4) + toolchain diagrams. |
| `docs/drawio/` | Editable `.drawio` source for the PDFs above. |
| `docs/mermaid/` | Plain-text Mermaid versions of the same diagrams (for inline embedding in markdown). |
| `docs/iso42001/` | ISO/IEC 42001 deliverable: clean + draft DOCX, presentation, generator scripts (`generate_docx.py`, `clean_docx.py`), execution plan. |
| `docs/qa/sprint-{2,3}/` | Historical QA reports + Sprint 3 report-generator scripts. |
| `docs/superpowers/specs/` | Approved design specs for major features. |
| `docs/superpowers/plans/` | Multi-phase implementation plans corresponding to those specs. |
| `docs/sprint2-check/` | Sprint 2 verification screenshots. |
| `docs/media/` | Embedded media for QA test cases. |
| Root-level docs (`docs/*.md`, `*.html`, `*.pdf`) | Standalone references: `ML_Tool_User_Guide.md`, `ROOT-CAUSE-target-column-not-found.md`, `ml-specialty-fixes.md`, `Sprint_1_Assignment.md`, sample HTML mockups, the Clinical Specialties Dataset Collection PDF. |

## QA Automation Pipeline

`scripts/qa/` implements the Sprint 5 deliverable for "20 specialties × 7 steps" coverage and "3 CSVs × 0 crashes" E2E regression. Three layers, each independently testable:

1. **Capture** — `walkthrough.sh <specialty_id> <out_dir>` drives `agent-browser` (Vercel Labs CLI, installed globally) through 13 deterministic wizard steps against the live HF Space, emitting `screenshots/NN_specialty_stepN_action.png`, `evidence.json`, and `walkthrough.log`. Step labels and screenshot names are centralised in `scripts/qa/lib/` so adding/renaming a step touches one file.
2. **Orchestration** — Mode A: parent Claude session fires 4 parallel `Agent` subagents per wave. Mode B: `orchestrate.sh` uses `xargs -P4`. Both write per-specialty `evidence.json`; the orchestrator merges into `MANIFEST.json`.
3. **Render** — `render_report.py <run_dir>` produces HTML via jinja2 + Sprint 2 print CSS, then PDF via Chrome `--headless --print-to-pdf`.

Per-run artefacts land in `scripts/qa/runs/<run-id>/`. Final reports are committed to `docs/reports/Sprint5_Full_Domain_Coverage.pdf` and `docs/reports/Sprint5_E2E_Regression.pdf`.

The full design + plan are in `docs/superpowers/specs/2026-04-21-qa-automation-design.md` and `docs/superpowers/plans/2026-04-21-qa-automation.md` — read these before modifying any of the three layers.

## Git Rules

- **Never add a Co-Authored-By line for Claude.** Commits must only credit human authors.

## Branch Strategy

- `main` — production, protected
- `develop` — integration branch
- `feature/US-XXX` — per user story
- PR titles: `feat/fix/docs(US-XXX): description`
