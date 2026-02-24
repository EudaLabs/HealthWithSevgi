# Sprint 1 Task Board — HealthWithSevgi

> **Sprint Deadline:** Wednesday, 4 March 2026 at 1:00 PM — No late submissions
> **Board:** [Jira SCRUM Board](https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards)
> **Last Updated:** 2026-02-24

---

## Team

| Name | Role | Initials |
|------|------|----------|
| Efe Çelik | Product Owner + Developer | EFE |
| Batuhan Bayazıt | Lead Developer + Scrum Master | BAT |
| Burak Aydoğmuş | UX Designer | BUR |
| Berat Mert Gökkaya | Developer | BER |
| Berfin Duru Alkan | QA / Documentation Lead | BRF |

---

## Status Legend

| Label | Meaning |
|-------|---------|
| ✅ Done | Completed and verified |
| 🔵 In Progress | Actively being worked on |
| 🟡 To Do | Not started, ready to pick up |
| 🔴 Blocked | Cannot proceed — needs action |

## Priority Legend

| Priority | Description |
|----------|-------------|
| 🔥 Critical | Blocks instructor gate / Sprint 2 start |
| 🔴 High | Must complete before deadline |
| 🟠 Medium | Important but not blocking |
| 🟢 Low | Nice to have this sprint |

---

## Sprint 1 Deliverables Board

### ✅ DONE

| Task | Assignee | Priority | Estimate | Notes |
|------|----------|----------|----------|-------|
| **D-003** Jira Product Backlog (25 user stories, all 7 steps) | EFE | 🔥 Critical | 4h | 25 stories, 102 pts, Gherkin AC |
| **D-004** User Story Standards — Gherkin AC format | EFE | 🔴 High | 2h | All stories have Given/When/Then |
| **D-005** GitHub Repository — README + SETUP + branch protection | BAT | 🔴 High | 3h | `feature/US-XXX` naming enforced |

---

### 🔵 IN PROGRESS

| Task | Assignee | Priority | Estimate | Due | Notes |
|------|----------|----------|----------|-----|-------|
| **D-002** Domain Coverage Plan — 20 domains PDF | EFE | 🔥 Critical | 4h | Feb 26 | 1-page PDF: domain name, dataset URL, target variable |
| **D-007** Sprint 1 Backlog in Jira — create sprint, assign stories | BAT | 🔥 Critical | 2h | Feb 25 | Sprint must exist before demo |

---

### 🟡 TO DO

| Task | Assignee | Priority | Estimate | Due | Notes |
|------|----------|----------|----------|-----|-------|
| **D-001** Team Charter | ALL | 🔴 High | 1h | Feb 27 | Submit to Google Forms link |
| **D-006** GitHub Wiki — Home Page | BRF | 🔴 High | 3h | Feb 28 | Member names, roles, Week 1 meeting notes |
| **D-008** Figma Wireframes — All 7 Steps | BUR | 🔥 Critical | 12h | Mar 2 | All steps + 20 domain pills + Column Mapper modal + confirmation dialog |
| **D-009** Architecture Diagram | BAT | 🔥 Critical | 4h | Mar 2 | Frontend ↔ Backend ↔ ML ↔ Session Storage ↔ API endpoints |
| **D-010** Frontend Scaffold — React 18 + Vite + Tailwind | EFE | 🔴 High | 4h | Mar 1 | pnpm workspace, routing skeleton (7 step pages), Tailwind green theme, ESLint + Prettier |
| **D-011** Backend Scaffold — FastAPI project structure | BER | 🔴 High | 4h | Mar 1 | `app/routers/`, `app/services/`, `app/models/`, CORS config, `/health` endpoint, Dockerfile |
| **D-012** API Contract — OpenAPI spec (first draft) | EFE + BER | 🟠 Medium | 3h | Mar 2 | Define request/response shapes for Steps 2–5 endpoints so frontend and backend can develop in parallel |
| **D-013** Dev Environment — docker-compose for full stack | BER | 🟠 Medium | 2h | Mar 2 | Single `docker-compose up` starts React dev server + FastAPI + hot-reload |

---

### 🔴 BLOCKED

_No blocked tasks currently._

---

## Per-Person Task View

### EFE — Product Owner + Developer
| Task | Status | Priority | Estimate |
|------|--------|----------|----------|
| D-003 Jira Product Backlog | ✅ Done | 🔥 Critical | — |
| D-004 User Story Standards | ✅ Done | 🔴 High | — |
| D-002 Domain Coverage Plan (20 domains PDF) | 🔵 In Progress | 🔥 Critical | 4h |
| D-001 Team Charter (contribute) | 🟡 To Do | 🔴 High | 20min |
| D-010 Frontend Scaffold — React 18 + Vite + Tailwind | 🟡 To Do | 🔴 High | 4h |
| D-012 API Contract — OpenAPI spec (with Berat) | 🟡 To Do | 🟠 Medium | 1.5h |

**Focus this week:** Domain Coverage Plan (Feb 26) → Frontend scaffold (Mar 1) → API contract (Mar 2).

Frontend scaffold checklist:
- [ ] `pnpm create vite health-with-sevgi --template react-ts`
- [ ] Install Tailwind CSS + configure green theme (`#16a34a` primary)
- [ ] Set up React Router v6 — 7 step routes (`/step-0` … `/step-6`)
- [ ] Shared layout: sidebar stepper, top nav with domain pill
- [ ] Placeholder page components for each step
- [ ] ESLint + Prettier config committed

---

### BAT — Lead Developer + Scrum Master
| Task | Status | Priority | Estimate |
|------|--------|----------|----------|
| D-005 GitHub Repo Setup | ✅ Done | 🔴 High | — |
| D-007 Sprint 1 Backlog in Jira | 🔵 In Progress | 🔥 Critical | 2h |
| D-009 Architecture Diagram | 🟡 To Do | 🔥 Critical | 4h |
| D-001 Team Charter (contribute) | 🟡 To Do | 🔴 High | 20min |

**Focus this week:** Sprint backlog first (unlocks team velocity), then architecture diagram.

---

### BUR — UX Designer
| Task | Status | Priority | Estimate |
|------|--------|----------|----------|
| D-008 Figma Wireframes — All 7 Steps | 🟡 To Do | 🔥 Critical | 12h |
| D-001 Team Charter (contribute) | 🟡 To Do | 🔴 High | 20min |

**Focus this week:** Wireframes are the biggest blocker for instructor approval. Start immediately.
Checklist for Figma:
- [ ] Step 0: Medical Specialty — 20 domain pills pill bar
- [ ] Step 1: Clinical Context
- [ ] Step 2: Data Exploration + Column Mapper modal
- [ ] Step 3: Data Preparation — split slider, imputation, normalisation
- [ ] Step 4: Model Selection + hyperparameter sliders
- [ ] Step 5: Results — metrics dashboard + confusion matrix + ROC
- [ ] Step 6: Explainability — feature importance + SHAP waterfall
- [ ] Step 7: Ethics & Bias — fairness table + EU AI Act checklist
- [ ] Domain-switch confirmation dialog
- [ ] Green theme applied throughout

---

### BER — Developer
| Task | Status | Priority | Estimate |
|------|--------|----------|----------|
| D-001 Team Charter (contribute) | 🟡 To Do | 🔴 High | 20min |
| **Review all 25 user stories & estimates** | 🟡 To Do | 🟠 Medium | 2h |
| D-011 Backend Scaffold — FastAPI project structure | 🟡 To Do | 🔴 High | 4h |
| D-012 API Contract — OpenAPI spec (with Efe) | 🟡 To Do | 🟠 Medium | 1.5h |
| D-013 Dev Environment — docker-compose full stack | 🟡 To Do | 🟠 Medium | 2h |

**Focus this week:** Backlog review (unlocks velocity data) → FastAPI scaffold (Mar 1) → docker-compose + API contract (Mar 2).

Backend scaffold checklist:
- [ ] `app/main.py` — FastAPI app + CORS middleware
- [ ] `app/routers/` — one router per step (`data.py`, `train.py`, `results.py`, `explain.py`, `ethics.py`)
- [ ] `app/services/` — business logic layer (separate from routes)
- [ ] `app/models/schemas.py` — Pydantic request/response models
- [ ] `GET /health` endpoint returns `{"status": "ok"}`
- [ ] `requirements.txt` — fastapi, uvicorn, scikit-learn, pandas, shap
- [ ] `Dockerfile` for backend container

---

### BRF — QA / Documentation Lead
| Task | Status | Priority | Estimate |
|------|--------|----------|----------|
| D-006 GitHub Wiki — Home Page | 🟡 To Do | 🔴 High | 3h |
| D-001 Team Charter (contribute) | 🟡 To Do | 🔴 High | 20min |
| **Draft test case template** | 🟡 To Do | 🟢 Low | 2h |

**Focus this week:** GitHub Wiki home page + team charter.
Wiki checklist:
- [ ] Team members table with names, roles, student IDs
- [ ] Week 1 meeting notes (date, attendees, decisions made)
- [ ] Links to Jira board, Figma, GitHub repo
- [ ] Branch naming convention documented

---

## Sprint 1 Burndown

| Day | Remaining Deliverables |
|-----|----------------------|
| Feb 24 (today) | 10 of 13 pending |
| Feb 25 | 9 of 13 (D-007 sprint done) |
| Feb 26 | 8 of 13 (D-002 domain plan done) |
| Feb 27 | 7 of 13 (D-001 team charter done) |
| Feb 28 | 6 of 13 (D-006 wiki done) |
| Mar 1 | 4 of 13 (D-010 frontend scaffold + D-011 backend scaffold done) |
| Mar 2 | 0 of 13 (D-008 wireframes + D-009 arch + D-012 API contract + D-013 docker done) |
| **Mar 4 @ 1 PM** | **Submission deadline** |

---

## Demo Agenda (Week 2 — 5 min slot)

1. **Team intro** — members, roles, Scrum Master, domain coverage plan overview
2. **Jira board** — show epics, top 5 user stories with acceptance criteria
3. **GitHub repo** structure + Wiki home page
4. **Figma walkthrough** — all 7 steps, 20 domain pills, Column Mapper modal, confirmation dialog
5. **Architecture diagram** — explain frontend ↔ backend ↔ ML layers

> **Instructor gate:** Wireframes + architecture must be approved before Sprint 2 coding begins.
