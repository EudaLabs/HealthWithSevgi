# Final Submission — Week 11 Jury Showcase

**Course:** SENG 430 · Çankaya University
**Due:** Tue 5 May 2026, 23:59
**Presentation slot:** TBD (jury schedule)
**Team:** EudaLabs — Efe Celik (FE), Batuhan Ozturk (FE+DevOps), *+ BE/QA*

## Live Surfaces (Grader Entry Points)

| What | Link |
|------|------|
| Live Demo (HuggingFace Spaces) | https://0xbatuhan4-healthwithsevgi.hf.space/ |
| Source (GitHub) | https://github.com/EudaLabs/HealthWithSevgi |
| Docker image (GHCR, no build needed) | `docker run -p 7860:7860 ghcr.io/eudalabs/healthwithsevgi:latest` |
| Docker Compose (one-liner) | `docker compose up` → http://localhost:7860 |
| Figma (wireframes + prototype) | TBD — link to be inserted |
| Jira board (velocity + burndown) | TBD — public snapshot to be inserted |
| Wiki home | [[Home]] |

## Required Deliverables Checklist

| # | Deliverable | Status | Link |
|---|-------------|--------|------|
| 1 | Working 7-step web app (runnable) | DONE | Live demo above |
| 2 | GitHub repo (README + SETUP.md) | IN PROGRESS | [README](https://github.com/EudaLabs/HealthWithSevgi#readme) |
| 3 | Docker image + `docker compose up` < 30s | DONE | [Dockerfile](https://github.com/EudaLabs/HealthWithSevgi/blob/main/hf-space/Dockerfile) |
| 4 | 2-page Project Report PDF (architecture, decisions, challenges, lessons) | PENDING | `Final_Project_Report.pdf` (TBD) |
| 5 | Jira board — velocity + burndown charts | PENDING (BE) | TBD |
| 6 | Figma — wireframes + interactive prototype | PENDING (FE) | TBD |
| 7 | GitHub Wiki — all sprint reviews | DONE | [[Sprint 1]] · [[Sprint 2]] · [[Sprint 3]] · [[Sprint 4]] · [[Sprint 5]] |
| 8 | User testing report (non-CS participant, 7 tasks, SUS) | PENDING (QA) | `Sprint5_User_Testing_Report.pdf` (TBD) |
| 9 | Usability video (≤ 5 min) | PENDING (QA) | `Sprint5_Usability_Video.mp4` (TBD) |
| 10 | Signed consent form | PENDING (QA) | `Sprint5_Consent_Form.pdf` (TBD) |
| 11 | Test reports — all 4 prior sprints | DONE | [Sprint 2 QA](Sprint2_QA_Report_v2_Post-Fix.pdf) · [Sprint 3 QA](Sprint3_QA_Test_Cases.pdf) · [Sprint 4 QA](Sprint4_QA_Full_Pipeline_Test_Report.pdf) |
| 12 | 10-min final jury slide deck | PENDING (FE) | `Sprint5_Showcase.pdf` (TBD) |

## 10-Minute Jury Presentation Outline *(draft — to be finalised with team)*

| Slot | Duration | Owner | Content |
|------|----------|-------|---------|
| 1. Team intro | 0:30 | All | Members, roles, SENG 430 context |
| 2. Problem & motivation | 1:00 | BE | ML in healthcare education — why a 7-step guided wizard instead of raw notebooks |
| 3. Live demo | 4:00 | FE | Endocrinology/Diabetes E2E in ≤ 4 min: Steps 1 → 7, highlight SHAP + fairness audit |
| 4. Results interpretation | 1:00 | BE | How a clinician reads ROC / PR / confusion matrix on Step 5 |
| 5. Bias finding walk-through | 1:00 | BE | Sensitive-attribute audit on Step 7, fairness-gap delta, EU AI Act checklist |
| 6. Technical highlights | 1:30 | Batu | Architecture, in-memory state, SHAP, Gemma 4 LLM chain, Docker/CI, accessibility polish |
| 7. Lessons learned | 0:30 | All | What worked, what we'd do differently |
| 8. Q&A | 0:30 | All | Open floor |

## Frontend Team Prep (Efe + Batu) — Week-11 Checklist

*Status as of 21 April 2026 — owner column left blank for team assignment.*

- [ ] **README audit** — confirm it answers: what is it, how to run locally, how to run via Docker, how to contribute, license. Add a top banner with live demo + GHCR image pointer.
- [ ] **SETUP.md** — standalone "clean machine → running app in < 10 min" guide (prereqs, clone, pnpm install, uvicorn, or one-shot `docker compose up`).
- [ ] **Clean-machine Docker test** — on a throwaway VM/WSL: `docker compose up` from zero, time to first green page, screenshot for report.
- [ ] **Demo rehearsal** — run Steps 1 → 7 end-to-end for **3 domains** (Endocrinology, Cardiology, Oncology). Log any crash/warning. Target: 4-minute silent walkthrough.
- [ ] **Figma cleanup** — verify public share link works, organise frames by step, add arrow flow for prototype.
- [ ] **Slide deck** — 8 slides mapped to the outline above. Export as PDF for submission.
- [ ] **Accessibility final-pass** — tab through the entire wizard using only the keyboard, verify focus ring visibility on every interactive element.
- [ ] **Lighthouse re-audit** (if Perf/SEO/BP fixes are scoped in) — target Perf ≥ 95, SEO = 100, BP ≥ 98. Archive new HTML + JSON.

## Risk Register (Week-11 perspective)

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| HuggingFace Space cold-start latency during jury demo | Medium | Warm Space 10 min before, have Docker compose ready as fallback |
| Gemma 4 LLM transient failure on Step 7 during demo | Medium | Pre-cache the insight by running the demo dataset once before jury; empty-state fallback already added |
| Figma prototype link requires viewer sign-in | Low | Switch share setting to "anyone with link can view" |
| Jira charts inaccessible to external graders | Low | Export PNG snapshots into wiki |
| Docker `compose up` fails on cold network (GHCR pull) | Low | Pre-pull on demo machine; keep local build as fallback |

## Open Questions / To-Finalise

- [ ] Exact jury presentation slot + room
- [ ] Figma share URL (currently private)
- [ ] Who narrates which part of the 10-min demo
- [ ] Whether Lighthouse Perf/SEO/BP re-optimisation ships before freeze (see [[Sprint 5]] §Polish)

---

*This is a living document — updated as deliverables land. Last edit: 21 April 2026.*
