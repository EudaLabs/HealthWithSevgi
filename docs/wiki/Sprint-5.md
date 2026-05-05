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
| 7 | JSDoc / docstring coverage ≥ 80% | Code + coverage report | **DONE** — frontend [JSDoc 100 %](Sprint5_Frontend_JSDoc_Coverage.txt), backend [interrogate 100 %](Sprint5_Backend_Docstring_Coverage.txt) |
| 8 | MIT License + metadata | `LICENSE` + `package.json` + `pyproject.toml` | DONE |
| 9 | Sprint 5 Backlog (Jira SCRUM-222..233) | Jira board + [screenshot](Sprint5_Jira_Backlog.jpg) | **DONE** — 12 / 12 stories closed (24 pts) |
| 10 | Bug Fix Log (Sprint 4 retro → Jira) | Jira filter + [screenshot](Sprint5_BugFix_Log.jpg) | **DONE** — 5 / 5 bugs closed (SCRUM-217..221, 11 pts) |
| 11 | User Testing (non-CS participant, 7 tasks, SUS) | [PDF](Sprint5_User_Testing_Report.pdf) | **DONE** — P1 (Ela Naz Ulusoy, Architecture, no CS): 7 / 7 PASS, SUS 90 |
| 12 | Signed Consent Forms | [PDF](Sprint5_Consent_Form.pdf) | **DONE** — signed by participant P1 on 27.04.2026 |
| 13 | Usability Test Video (≤ 5 min) | [Google Drive video](https://drive.google.com/file/d/1VjD9xwUgDmsVOWn-OX9clYOTsL9FxwGz/view?usp=drive_link) | **DONE** — recorded by QA on UserBrain |
| 14 | Full Domain Coverage (20 specialties E2E) | [PDF](Sprint5_Full_Domain_Coverage.pdf) | **DONE** — 140 / 140 cases pass (20 specialties × 7 steps) |
| 15 | E2E Regression (3 CSVs, 0 crashes) | [PDF](Sprint5_E2E_Regression.pdf) | **DONE** — 21 / 21 cases pass, 0 crashes |
| 16 | Week 9 Progress Report | [HTML](Sprint5_Weekly_Progress_Report.html) | **DONE** — 17 issues / 35 pts; burndown 0 remaining |

> The 10-min jury slide deck is tracked under **Final Submission**, not Sprint 5 — see [[Final Submission]] row #12.

## Live Demo

- **Live Demo:** https://0xbatuhan4-healthwithsevgi.hf.space/
- **Hugging Face Space:** https://huggingface.co/spaces/0xBatuhan4/HealthWithSevgi
- **Docker (GHCR):** `docker run -p 7860:7860 ghcr.io/eudalabs/healthwithsevgi:latest`
- **Docker Compose:** `docker compose up` → http://localhost:7860

## Project Surfaces

| Surface | Link |
|---------|------|
| GitHub Repository | https://github.com/EudaLabs/HealthWithSevgi |
| GitHub Wiki — Home | https://github.com/EudaLabs/HealthWithSevgi/wiki |
| Docker Image — GitHub Packages (GHCR) | https://github.com/EudaLabs/HealthWithSevgi/pkgs/container/healthwithsevgi |
| Figma Wireframes — All 7 Steps | https://www.figma.com/design/1K1Dw8PC6P98NZAa30DzII/430-HealthWithSevgi?node-id=0-1&t=A5k3xtuCwuaFsHMB-1 |
| Jira — Product Backlog (all sprints) | https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog |
| Jira — Sprint 1 Backlog | https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog?jql=Sprint%20%3D%2068 |
| Jira — Sprint 2 Backlog | https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog?jql=Sprint%20%3D%2069 |
| Jira — Sprint 3 Backlog | https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog?jql=Sprint%20%3D%2070 |
| Jira — Sprint 4 Backlog | https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog?jql=Sprint%20%3D%2071 |
| Jira — Sprint 5 Backlog | https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog?jql=Sprint%20%3D%2072 |

## Sprint 5 Metrics

| Metric | Target | Result |
|--------|--------|--------|
| Lighthouse Performance | ≥ 80 | **91** — PASS (re-audit 21 Apr; was 93 on 20 Apr baseline — see `Sprint5_Lighthouse.report.baseline.json`) |
| Lighthouse Accessibility | ≥ 85 | **100** — PASS |
| Lighthouse Best Practices | — | **100** (was 96 baseline) |
| Lighthouse SEO | — | **100** (was 91 baseline) |
| Docker Startup Time | ≤ 30 s (warm cache) | Healthcheck passes within 20 s — PASS |
| Usability Task Completion | ≥ 5 / 7 tasks independently | **7 / 7** — PASS (T1 41 s · T2 59 s · T3 70 s · T4 50 s · T5 80 s · T6 75 s · T7 35 s; no assistance) — see [User Testing Report](Sprint5_User_Testing_Report.pdf) |
| SUS Score | ≥ 68 | **90** — PASS (10 SUS questions: 10/9/9/9/10/9/9/9/10/6) — see User Testing Report |
| End-to-End Regression | 0 crashes across 3 CSVs | **0 crashes / 21 cases** — PASS — see [E2E Regression](Sprint5_E2E_Regression.pdf) |
| Code Documentation (JSDoc + docstring) | ≥ 80 % | **Frontend 100 %, Backend 100 %** — PASS ([frontend](Sprint5_Frontend_JSDoc_Coverage.txt) · [backend](Sprint5_Backend_Docstring_Coverage.txt) · ![badge](Sprint5_Backend_Docstring_Badge.svg)) |
| Full Domain Coverage | 20 / 20 specialties Step 1–7 | **20 / 20** — PASS (140 cases, 0 failures) — see [Full Domain Coverage](Sprint5_Full_Domain_Coverage.pdf) |
| Cross-Browser Compatibility | Chrome / Firefox / Safari / Edge | **4 / 4** — PASS — see [UT-03 audit (SCRUM-229)](https://berfindurualkan.atlassian.net/browse/SCRUM-229) |

**Re-audit (21 Apr 2026) — Perf 91 · A11y 100 · BP 100 · SEO 100**

![Sprint 5 Lighthouse Report — re-audit](Sprint5_Lighthouse_Report.png)

**Baseline (20 Apr 2026, pre-re-audit) — Perf 93 · A11y 100 · BP 96 · SEO 91**

![Sprint 5 Lighthouse Report — baseline](Sprint5_Lighthouse_Report.baseline.png)

## Polish Work Completed

### Docker & Deployment
- Added **healthcheck** to `docker-compose.yml` so the container is reported unhealthy if the FastAPI root returns non-2xx.
- Added **GHCR image fallback** — `docker compose up` pulls `ghcr.io/eudalabs/healthwithsevgi:latest` when the local build context is missing.
- Quick-start docs added to README (`docker compose up` → app on port 7860).

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

Sprint 5 board (15 Apr → 29 Apr 2026): **17 issues · 35 / 35 story points · all DONE**.
Live filter: [Jira board](https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog) · Frozen evidence: [`Sprint5_Jira_Backlog.jpg`](Sprint5_Jira_Backlog.jpg) · [`Sprint5_BugFix_Log.jpg`](Sprint5_BugFix_Log.jpg) · [`Sprint5_Burndown.jpg`](Sprint5_Burndown.jpg).

### Polish (Tasks · 8 pts)

| Jira Key | Title | Pts | Assignee | Done |
|----------|-------|-----|----------|------|
| [SCRUM-222](https://berfindurualkan.atlassian.net/browse/SCRUM-222) | Polish: Loading skeleton on Step 2 data exploration table | 2 | Burak Aydoğmuş | 2026-04-27 |
| [SCRUM-223](https://berfindurualkan.atlassian.net/browse/SCRUM-223) | Polish: Clinical hyperparameter tooltips in Step 4 model configuration | 2 | Efe Çelik | 2026-04-27 |
| [SCRUM-224](https://berfindurualkan.atlassian.net/browse/SCRUM-224) | Polish: Step 4 parallel coordinates chart responsive on mobile viewports | 2 | Batuhan Bayazıt | 2026-04-27 |
| [SCRUM-225](https://berfindurualkan.atlassian.net/browse/SCRUM-225) | Polish: Empty-state UI on Step 5 when no model has been trained | 1 | Burak Aydoğmuş | 2026-04-27 |
| [SCRUM-226](https://berfindurualkan.atlassian.net/browse/SCRUM-226) | Polish: CSV export button for Step 5 metrics comparison table | 1 | Berfin Duru Alkan | 2026-04-27 |

### Usability Testing (Stories · 9 pts)

| Jira Key | Title | Pts | Assignee | Done |
|----------|-------|-----|----------|------|
| [SCRUM-227](https://berfindurualkan.atlassian.net/browse/SCRUM-227) | UT-01: End-to-end usability test — clinician personas (T1–T7) | 3 | Berfin Duru Alkan | 2026-04-28 |
| [SCRUM-228](https://berfindurualkan.atlassian.net/browse/SCRUM-228) | UT-02: Stress test — 50 K-row CSV upload, no timeout / memory crash | 2 | Berfin Duru Alkan | 2026-04-28 |
| [SCRUM-229](https://berfindurualkan.atlassian.net/browse/SCRUM-229) | UT-03: Cross-browser compatibility audit (Chrome, Firefox, Safari, Edge) | 2 | Burak Aydoğmuş | 2026-04-28 |
| [SCRUM-230](https://berfindurualkan.atlassian.net/browse/SCRUM-230) | UT-04: WCAG 2.1 AA accessibility audit for full wizard | 2 | Berfin Duru Alkan | 2026-04-29 |

### Deployment & Documentation (Stories · 7 pts)

| Jira Key | Title | Pts | Assignee | Done |
|----------|-------|-----|----------|------|
| [SCRUM-231](https://berfindurualkan.atlassian.net/browse/SCRUM-231) | Docker: Compose file for local dev with hot-reload (frontend + backend) | 2 | Berat Mert Gökkaya | 2026-04-29 |
| [SCRUM-232](https://berfindurualkan.atlassian.net/browse/SCRUM-232) | DOC-01: Update ML Tool User Guide v1.0 → v1.4 (parallel coords, What-If, sample patients) | 3 | Efe Çelik | 2026-04-29 |
| [SCRUM-233](https://berfindurualkan.atlassian.net/browse/SCRUM-233) | DOC-02: Publish interactive OpenAPI documentation and link from README | 2 | Berat Mert Gökkaya | 2026-04-29 |

### Sprint 4 Retrospective Bug Fixes (Bugs · 11 pts)

| Jira Key | Title | Pts | Assignee | Done |
|----------|-------|-----|----------|------|
| [SCRUM-217](https://berfindurualkan.atlassian.net/browse/SCRUM-217) | Missing ErrorBoundary around lazy-loaded Step 5 & Step 6 crashes entire app on render error | 3 | Efe Çelik | 2026-04-26 |
| [SCRUM-218](https://berfindurualkan.atlassian.net/browse/SCRUM-218) | Silent error suppression in Step 6 sample-patients dropdown hides real backend failures | 2 | Efe Çelik | 2026-04-26 |
| [SCRUM-219](https://berfindurualkan.atlassian.net/browse/SCRUM-219) | Feature selection silently no-ops on `mutual_info` failure — model trains without expected reduction | 2 | Berat Mert Gökkaya | 2026-04-26 |
| [SCRUM-220](https://berfindurualkan.atlassian.net/browse/SCRUM-220) | Parallel coordinates chart crashes when a model metric is undefined or null | 3 | Batuhan Bayazıt | 2026-04-26 |
| [SCRUM-221](https://berfindurualkan.atlassian.net/browse/SCRUM-221) | Parallel coordinates chart renders broken state when fewer than 2 models are selected | 1 | Batuhan Bayazıt | 2026-04-26 |

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
| [Sprint 5 Lighthouse — re-audit (PNG)](Sprint5_Lighthouse_Report.png) | 21.04.2026 | PNG (91 / 100 / 100 / 100) |
| [Sprint 5 Lighthouse — baseline (PNG)](Sprint5_Lighthouse_Report.baseline.png) | 20.04.2026 | PNG (93 / 100 / 96 / 91) |
| Sprint 5 Lighthouse — re-audit (21 Apr, Perf 91 / A11y 100 / BP 100 / SEO 100) | 21.04.2026 | [HTML](Sprint5_Lighthouse.report.html) · [JSON](Sprint5_Lighthouse.report.json) |
| Sprint 5 Lighthouse — baseline snapshot (20 Apr, Perf 93 / A11y 100 / BP 96 / SEO 91) | 20.04.2026 | [HTML](Sprint5_Lighthouse.report.baseline.html) · [JSON](Sprint5_Lighthouse.report.baseline.json) |
| [Backend docstring coverage — `interrogate` 100 %](Sprint5_Backend_Docstring_Coverage.txt) | 21.04.2026 | TXT + [badge](Sprint5_Backend_Docstring_Badge.svg) |
| [Frontend JSDoc coverage — 100 %](Sprint5_Frontend_JSDoc_Coverage.txt) | 21.04.2026 | TXT |
| [Logo + Navbar screenshot](Sprint5_Logo_Navbar.png) | 20.04.2026 | PNG |
| [Sprint 5 User Testing Report](Sprint5_User_Testing_Report.pdf) | 27.04.2026 | PDF — P1 (non-CS): 7 / 7 PASS, SUS 90 |
| [Sprint 5 Consent Form](Sprint5_Consent_Form.pdf) | 27.04.2026 | PDF — signed by participant P1 |
| [Sprint 5 Usability Video](https://drive.google.com/file/d/1VjD9xwUgDmsVOWn-OX9clYOTsL9FxwGz/view?usp=drive_link) | 28.04.2026 | Google Drive — recorded by QA on UserBrain |
| [Sprint 5 Full Domain Coverage](Sprint5_Full_Domain_Coverage.pdf) | 28.04.2026 | PDF — 140 cases / 0 failures across 20 specialties |
| [Sprint 5 E2E Regression](Sprint5_E2E_Regression.pdf) | 28.04.2026 | PDF — 21 cases / 0 crashes across 3 CSVs |
| [Sprint 5 Weekly Progress Report](Sprint5_Weekly_Progress_Report.html) | 29.04.2026 | [HTML](Sprint5_Weekly_Progress_Report.html) (export → PDF for Moodle) |
| [Sprint 5 Jira Backlog screenshot](Sprint5_Jira_Backlog.jpg) | 29.04.2026 | JPG — 12 stories, 24 pts, all DONE |
| [Sprint 5 Bug Fix Log screenshot](Sprint5_BugFix_Log.jpg) | 29.04.2026 | JPG — 5 retro bugs, 11 pts, all DONE |
| [Sprint 5 Burndown screenshot](Sprint5_Burndown.jpg) | 29.04.2026 | JPG — 35 / 35 pts complete, 0 remaining |

## Releases Shipped in Sprint 5

| Tag | Date | Highlights |
|-----|------|-----------|
| v1.5.8 | 20.04.2026 | Gemma 4 default provider + MIT License + brand identity |
| v1.5.9 | 20.04.2026 | Step 7 insights reliability — 200 s timeout, retries, empty-response fallback |
| v1.5.10 | 20.04.2026 | Step 7 badge label fix (Gemini 2.5 Flash → Gemma 4) |
| v1.5.11 | 21.04.2026 | Lighthouse re-audit sweep (Perf 91 / A11y 100 / BP 100 / SEO 100) + JSDoc+docstring coverage 100 % both ends |

All four releases also shipped to Hugging Face Space and GHCR via the `Release — Deploy & Docker` workflow (~2 min each).

## Key Technical Decisions

- **Reasoning-aware response parsing** — Gemma 4's `thought=true` parts are filtered so the UI only renders the final answer. Prevents raw chain-of-thought from leaking into the clinical assessment card.
- **Retry envelope, not loop** — transient LLM failures retry once with jittered exponential backoff, then fall back to the template. Bounded worst-case endpoint time stays within the 450 s axios budget.
- **Graceful fallback UI** — if the LLM falls back to the template, Step 7 shows a "assessment unavailable, reload to retry" alert instead of a blank space. The rest of the fairness table, checklist, and certificate continue to work.
- **Accessibility without opacity** — locked wizard steps now use `--text-secondary` directly for text instead of blending via `opacity: 0.45`, because blending stacks with the parent surface and blew the 4.5 : 1 AA contrast target.
- **Brand via alpha centroid** — the logo mark is trimmed and optically centred using the alpha-channel centroid rather than a naive bounding-box centre, so the visually heavy `S` sits where the eye expects.
- **GHCR fallback in compose** — the repo's `docker-compose.yml` reaches for the pre-built GHCR image when the local build context is missing, so graders can run the app on a clean machine with `docker compose up` and no source checkout.

## Retrospective

### Keep
- Lighthouse scores cleared every target — Performance **91** (target ≥ 80), Accessibility **100** (target ≥ 85), BP **100**, SEO **100**. PageSpeed Insights re-run on 28 Apr from production HF Space scored **98 / 94 / 100 / 100** — both runs above target.
- v1.5.8 → v1.5.11 deployed cleanly across release days — every release ran the full `Release — Deploy & Docker` pipeline (build → Docker → HF Space → GHCR) within ~2 min.
- Test discipline scaled to the final sprint: **173 / 173 cases pass** across 140-case full-pipeline (20 specialties × 7 steps), 21-case 3-CSV E2E regression, and 7-task non-CS usability test. Zero failures.
- Step 7 reliability issue was caught, diagnosed (45 s timeout was masking `ReadTimeout('')`), fixed, verified (5 × 3 = 15/15 successful Gemini calls), and shipped in the same day.
- Accessibility work produced a proper before/after log with file:line CSS diffs — reusable as a pattern for future audits.
- Sprint 4 retro bug fixes (SCRUM-217..221, 11 pts) were re-prioritised into Sprint 5 and shipped in the **first half** of the sprint window — leaving the second half clean for polish + testing.

### Improve
- The usability test video and signed consent form slipped to the last 48 h of the sprint. Booking the recording window at the *start* of the sprint (not after polish work lands) would remove the last-minute scramble.
- Cross-browser audit (UT-03) caught one Safari-specific viewport regression late. A Playwright matrix in CI on every PR would have caught it before merge instead of during the audit.
- One non-CS user is the WebOnline minimum, not statistical evidence. For future iterations, run two more sessions with a clinician and a hospital administrator to triangulate the SUS figure.

### Try
- Gate `main` on a Lighthouse score floor (Perf ≥ 85, A11y ≥ 95) using a GitHub Action so future contributors cannot silently regress jury-grade scores.
- Add an automated 20-specialty smoke test to CI — a single Playwright spec that walks Steps 1–7 once per specialty and posts the matrix to the PR.
- Schedule a quarterly accessibility audit even after the academic project closes — the WCAG 2.1 AA findings are durable knowledge worth maintaining alongside the live HuggingFace Space.

## Deadline

Wednesday, April 29, 2026 — 13:00 (jury showcase — 5 min per group)
