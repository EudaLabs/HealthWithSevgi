# Sprint 5

**Duration:** Apr 16 – Apr 29, 2026
**Goal:** Polish, user testing, performance, Docker, accessibility, and final jury presentation

## Deliverables

| # | Deliverable | Format | Status |
|---|-------------|--------|--------|
| 1 | Working App — Polished v1.5.x | GitHub + Live Demo | DONE |
| 2 | Docker Quick Start (`docker compose up` < 30 s) | `docker-compose.yml` + README | DONE |
| 3 | Lighthouse Audit (Perf ≥ 80, A11y ≥ 85) | [PNG](Sprint5_Lighthouse_Report.png) · [HTML](Sprint5_Lighthouse.report.html) · [JSON](Sprint5_Lighthouse.report.json) | DONE |
| 4 | Accessibility Fix Log | [[Accessibility Log]] | DONE |
| 5 | Brand Identity (logo, favicon, navbar mark) | [Navbar PNG](Sprint5_Logo_Navbar.png) · [Logo PNG](https://raw.githubusercontent.com/EudaLabs/HealthWithSevgi/main/frontend/public/logo.png) · [Favicon](https://raw.githubusercontent.com/EudaLabs/HealthWithSevgi/main/frontend/public/favicon.ico) | DONE |
| 6 | LLM-Powered Clinical Insights (Step 7) | Gemma 4 integration | DONE |
| 7 | JSDoc / docstring coverage ≥ 80% | Code + coverage report | **DONE** — frontend [JSDoc 100 %](coverage/frontend-jsdoc-coverage.txt), backend [interrogate 100 %](coverage/backend-docstring-coverage.txt) |
| 8 | MIT License + metadata | `LICENSE` + `package.json` + `pyproject.toml` | DONE |
| 9 | Sprint 5 Backlog (Jira US-501..507) | Jira board + screenshot | IN PROGRESS |
| 10 | Bug Fix Log (Sprint 4 retro → Jira) | Jira | IN PROGRESS |
| 11 | User Testing (non-CS participant, 7 tasks, SUS) | [PDF](Sprint5_User_Testing_Report.pdf) | PENDING (QA) |
| 12 | Signed Consent Forms | [PDF](Sprint5_Consent_Form.pdf) | PENDING (QA) |
| 13 | Usability Test Video (≤ 5 min) | [MP4](Sprint5_Usability_Video.mp4) | PENDING (QA) |
| 14 | Full Domain Coverage (20 specialties E2E) | [PDF](Sprint5_Full_Domain_Coverage.pdf) | PENDING (QA) |
| 15 | E2E Regression (3 CSVs, 0 crashes) | [PDF](Sprint5_E2E_Regression.pdf) | PENDING (QA) |
| 16 | Week 9 Progress Report | [PDF](Sprint5_Weekly_Progress_Report.pdf) | PENDING (BE) |
| 17 | Final Jury Slide Deck | [PDF](Sprint5_Showcase.pdf) | PENDING (FE) |

## Live Demo

- **Live Demo:** https://0xbatuhan4-healthwithsevgi.hf.space/
- **Hugging Face Space:** https://huggingface.co/spaces/0xBatuhan4/HealthWithSevgi
- **Docker (GHCR):** `docker run -p 7860:7860 ghcr.io/eudalabs/healthwithsevgi:latest`
- **Docker Compose:** `docker compose up` → http://localhost:7860

## Sprint 5 Metrics

| Metric | Target | Result |
|--------|--------|--------|
| Lighthouse Performance | ≥ 80 | **91** — PASS (re-audit 21 Apr; was 93 on 20 Apr baseline — see `Sprint5_Lighthouse.report.baseline.json`) |
| Lighthouse Accessibility | ≥ 85 | **100** — PASS |
| Lighthouse Best Practices | — | **100** (was 96 baseline) |
| Lighthouse SEO | — | **100** (was 91 baseline) |
| Docker Startup Time | ≤ 30 s (warm cache) | Healthcheck passes within 20 s — PASS |
| Usability Task Completion | ≥ 5 / 7 tasks independently | TBD — see [User Testing Report](Sprint5_User_Testing_Report.pdf) |
| SUS Score | ≥ 68 | TBD — see User Testing Report |
| End-to-End Regression | 0 crashes across 3 CSVs | TBD — see [E2E Regression](Sprint5_E2E_Regression.pdf) |
| Code Documentation (JSDoc + docstring) | ≥ 80 % | **Frontend 100 %, Backend 100 %** — PASS ([frontend](coverage/frontend-jsdoc-coverage.txt) · [backend](coverage/backend-docstring-coverage.txt) · ![badge](coverage/backend-docstring-badge.svg)) |
| Full Domain Coverage | 20 / 20 specialties Step 1–7 | TBD — see [Full Domain Coverage](Sprint5_Full_Domain_Coverage.pdf) |

![Sprint 5 Lighthouse Report](Sprint5_Lighthouse_Report.png)

## Polish Work Completed

### Docker & Deployment
- Added **healthcheck** to `docker-compose.yml` so the container is reported unhealthy if the FastAPI root returns non-2xx.
- Added **GHCR image fallback** — `docker compose up` pulls `ghcr.io/eudalabs/healthwithsevgi:latest` when the local build context is missing.
- Quick-start docs added to README (`docker compose up` → app on port 7860).

![Docker compose up running](Sprint5_Docker_Running.png)

### Lighthouse Performance & Accessibility
- Audited the production build (`pnpm build` + `pnpm preview` on port 4173).
- Scores (re-audit 21 Apr 2026): Performance **91**, Accessibility **100**, Best Practices **100**, SEO **100** (Chrome 131 headless, Lighthouse latest).
- Accessibility score raised from **91 → 100** by resolving 5 `color-contrast` violations and 1 `landmark-one-main` violation. Full breakdown with before/after CSS in [[Accessibility Log]].
- Performance re-audit pass added **+4 BP** and **+9 SEO** via: valid `robots.txt`, Vite `sourcemap: true`, lazy-loading Steps 2/3/4/7 (recharts no longer eagerly preloaded — 70 KiB less landing JS), swapping navbar logo to `/logo-192.png` with `fetchPriority="high"`, and a `preview.proxy` config so `/api/*` resolves during audit.
- Baseline report (Sprint 5 closing, pre-re-audit): [HTML](Sprint5_Lighthouse.report.baseline.html) · [JSON](Sprint5_Lighthouse.report.baseline.json).

### Brand Identity
- Added `HealthWithSevgi` logo as favicon and navbar mark (alpha-centroid centering so the `S` sits optically middle).
- Logo served from the static frontend build and by `main_hf.py` on HuggingFace.

### LLM-Powered Step-7 Insights
- Switched default provider from Gemini 2.5 Flash to **Gemma 4** (`gemma-4-26b-a4b-it`) via Google AI Studio.
- Gemma 4 emits chain-of-thought parts alongside the final answer — the response parser filters out `thought=true` parts and joins only the answer text.
- Per-call HTTP timeout raised to **200 s** and one jittered retry added for transient failures (`ReadTimeout`, 429, 5xx). Axios client bumped to **450 s** accordingly.
- Step 7 now renders a graceful "assessment unavailable, reload to retry" alert when the LLM falls back to the template, instead of showing an empty card.
- Verified: 5 consecutive `/api/insights/<model_id>` calls returned `source=gemini` for all three sub-tasks (ethics, case studies, EU AI Act enrichment).

### Documentation
- **JSDoc** added to every exported frontend API module, every page component, and every chart component.
- **docstring** coverage improved across backend routers, services, and Pydantic models.
- ISO 42001 compliance draft — Chapters 1–3 written; `generate_docx` script added.

### Legal / Metadata
- Repository formally licensed under **MIT**. Metadata synchronised in `package.json`, `pyproject.toml`, and a new `LICENSE` file at the repo root.

## Accessibility Fix Log (Summary)

| Violation | Severity | Occurrences | Fix |
|-----------|----------|-------------|-----|
| `color-contrast` (WCAG 1.4.3 AA) — wizard locked step labels | Serious | 4 | Removed blanket `opacity: 0.45`; scoped opacity to step-number badge; used `--text-secondary` for names (5.85 : 1 on white) |
| `color-contrast` — CSV hint text in upload card | Serious | 1 | Switched from `--text-muted` to `--text-secondary` |
| `landmark-one-main` | Moderate | 1 | Wrapped wizard content in `<main id="main">` and added skip-to-content link |

Full before/after CSS and file:line references: [[Accessibility Log]].

## LLM Provider Chain

| Provider | Role | Activation | Notes |
|----------|------|-----------|-------|
| MedGemma (Vertex AI) | Primary clinical model | `MEDGEMMA_ENDPOINT_ID` + `GOOGLE_CLOUD_PROJECT` env | Optional; falls through to Gemini if unreachable |
| Gemma 4 (`gemma-4-26b-a4b-it`) | Default provider | `GEMINI_API_KEY` env | Reasoning model — `thought` parts filtered before rendering |
| Template fallback | Offline / rate-limit fallback | Always available | Frontend shows warning banner instead of blank card |

### Step 7 AI Tasks

| Task | Prompt size | Output format |
|------|-------------|---------------|
| `ethics_insight` | Large — specialty + metrics + SHAP top features + subgroup details | Markdown (300–550 words) |
| `case_studies` | Medium — domain + weaknesses + top features | JSON array of 3 case-study objects |
| `eu_ai_act_insights` | Medium — 8 checklist items + metrics | JSON array of `{id, enriched_description}` |

## Sprint 5 Jira Stories

| Story ID | Jira Key | Title | Assignee | Status |
|----------|----------|-------|----------|--------|
| US-501 | SCRUM-TBD | User Testing — 7-task protocol + SUS | Berfin Duru Alkan | IN PROGRESS |
| US-502 | SCRUM-TBD | Lighthouse Performance ≥ 80 | Batuhan / Burak | DONE |
| US-503 | SCRUM-TBD | Lighthouse Accessibility ≥ 85 | Batuhan / Burak | DONE (score 100) |
| US-504 | SCRUM-TBD | Docker compose startup ≤ 30 s | Batuhan / Burak | DONE |
| US-505 | SCRUM-TBD | Code documentation coverage ≥ 80 % | Efe + Berat (BE) / Batuhan + Burak (FE) | IN PROGRESS |
| US-506 | SCRUM-TBD | Full domain coverage — 20 specialties | Berfin | PENDING |
| US-507 | SCRUM-TBD | Final showcase + slide deck | Batuhan / Burak | PENDING |

> Jira keys will be backfilled once the Sprint 5 board screenshot is exported (`docs/reports/Sprint5_Sprint_Backlog.png`).

## User Testing Protocol

The structured usability test uses a non-CS participant with university-level education. Coaching is not allowed during task execution. Success threshold: ≥ 5 of 7 tasks completed independently within the time limits.

| Task | Scenario | Success Criterion | Time Limit |
|------|----------|-------------------|------------|
| T1 | Open the tool, locate the domain pill bar, switch between two specialties | Correct pills clicked; Step 1 updates; no errors | 90 s |
| T2 | Upload the provided sample CSV and open the Column Mapper | CSV accepted, Column Mapper opens | 3 min |
| T3 | Complete Column Mapper validation and proceed to Step 3 | Save → green banner → Step 3 opens | 2 min |
| T4 | Apply preparation settings in Step 3 and move to Step 4 | Apply → green banner → Step 4 opens | 3 min |
| T5 | Train a KNN model and find the Sensitivity score in Step 5 | Correctly names the Sensitivity value and its colour | 3 min |
| T6 | Find the top-influencing feature in Step 6 | Names the top feature in the importance chart | 2 min |
| T7 | Download the Summary Certificate | PDF downloads successfully | 1 min |

Full session results, participant quotes, and SUS questionnaire responses land in [Sprint 5 User Testing Report](Sprint5_User_Testing_Report.pdf).

## Reports

| Report | Date | Format |
|--------|------|--------|
| [Sprint 5 Lighthouse Report (PNG)](Sprint5_Lighthouse_Report.png) | 20.04.2026 | PNG + JSON + HTML |
| [Docker running screenshot](Sprint5_Docker_Running.png) | 20.04.2026 | PNG |
| [Logo + Navbar screenshot](Sprint5_Logo_Navbar.png) | 20.04.2026 | PNG |
| [Sprint 5 User Testing Report](Sprint5_User_Testing_Report.pdf) | TBD | PDF — pending QA session |
| [Sprint 5 Consent Form](Sprint5_Consent_Form.pdf) | TBD | PDF — pending QA session |
| [Sprint 5 Usability Video](Sprint5_Usability_Video.mp4) | TBD | MP4 — pending QA session |
| [Sprint 5 Full Domain Coverage](Sprint5_Full_Domain_Coverage.pdf) | TBD | PDF — pending QA 20-specialty run |
| [Sprint 5 E2E Regression](Sprint5_E2E_Regression.pdf) | TBD | PDF — pending QA 3-CSV run |
| [Sprint 5 Weekly Progress Report](Sprint5_Weekly_Progress_Report.pdf) | TBD | PDF — pending Jira burndown export |
| [Sprint 5 Showcase (Jury)](Sprint5_Showcase.pdf) | TBD | PDF slide deck — 28.04 |

## Releases Shipped in Sprint 5

| Tag | Date | Highlights |
|-----|------|-----------|
| v1.5.8 | 20.04.2026 | Gemma 4 default provider + MIT License + brand identity |
| v1.5.9 | 20.04.2026 | Step 7 insights reliability — 200 s timeout, retries, empty-response fallback |
| v1.5.10 | 20.04.2026 | Step 7 badge label fix (Gemini 2.5 Flash → Gemma 4) |

All three releases also shipped to Hugging Face Space and GHCR via the `Release — Deploy & Docker` workflow (~2 min each).

## Key Technical Decisions

- **Reasoning-aware response parsing** — Gemma 4's `thought=true` parts are filtered so the UI only renders the final answer. Prevents raw chain-of-thought from leaking into the clinical assessment card.
- **Retry envelope, not loop** — transient LLM failures retry once with jittered exponential backoff, then fall back to the template. Bounded worst-case endpoint time stays within the 450 s axios budget.
- **Graceful fallback UI** — if the LLM falls back to the template, Step 7 shows a "assessment unavailable, reload to retry" alert instead of a blank space. The rest of the fairness table, checklist, and certificate continue to work.
- **Accessibility without opacity** — locked wizard steps now use `--text-secondary` directly for text instead of blending via `opacity: 0.45`, because blending stacks with the parent surface and blew the 4.5 : 1 AA contrast target.
- **Brand via alpha centroid** — the logo mark is trimmed and optically centred using the alpha-channel centroid rather than a naive bounding-box centre, so the visually heavy `S` sits where the eye expects.
- **GHCR fallback in compose** — the repo's `docker-compose.yml` reaches for the pre-built GHCR image when the local build context is missing, so graders can run the app on a clean machine with `docker compose up` and no source checkout.

## Retrospective

### Keep
- Lighthouse scores cleared every target — Performance **93** (target ≥ 80), Accessibility **100** (target ≥ 85).
- v1.5.8 → v1.5.10 deployed cleanly on release day — every release ran the full `Release — Deploy & Docker` pipeline (build → Docker → HF Space → GHCR) within ~2 min.
- Step 7 reliability issue was caught, diagnosed (45 s timeout was masking `ReadTimeout('')`), fixed, verified (5 × 3 = 15/15 successful Gemini calls), and shipped in the same day.
- Accessibility work produced a proper before/after log with file:line CSS diffs — reusable as a pattern for future audits.

### Improve
- *To be filled after the user-testing session and the 20-specialty coverage run.* Known anticipated callouts: QA test-case stories still trail development by days; no smoke test yet iterates all 20 specialties on every PR.

### Try
- *To be decided at retrospective after Sprint 5 demo.* Candidate actions: add an automated 20-specialty smoke test to CI; lock scope 48 h before deadline; version-tag Sprint 5 wiki on each release.

## Deadline

Wednesday, April 29, 2026 — 13:00 (jury showcase — 5 min per group)
