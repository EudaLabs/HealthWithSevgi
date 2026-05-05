# Final Submission — Week 11 Jury Showcase

**Course:** SENG 430 · Çankaya University
**Due:** Tue 5 May 2026, 23:59
**Presentation slot:** 5 May 2026 — per HEALTH-AI panel schedule
**Team:** EudaLabs — Efe Çelik (PO + Dev) · Burak Aydoğmuş (UX) · Batuhan Bayazıt (Lead Dev + SM) · Berat Mert Gökkaya (Dev) · Berfin Duru Alkan (QA Lead)

## Live Surfaces (Grader Entry Points)

| What | Link |
|------|------|
| Live Demo (HuggingFace Spaces) | https://0xbatuhan4-healthwithsevgi.hf.space/ |
| Source (GitHub) | https://github.com/EudaLabs/HealthWithSevgi |
| Docker image (GHCR, no build needed) | `docker run -p 7860:7860 ghcr.io/eudalabs/healthwithsevgi:latest` |
| Docker Compose (one-liner) | `docker compose up` → http://localhost:7860 |
| Figma (wireframes + prototype) | https://www.figma.com/design/1K1Dw8PC6P98NZAa30DzII/430-HealthWithSevgi?node-id=0-1 |
| Jira board (velocity + burndown) | https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog |
| Wiki home | [[Home]] |

## Required Deliverables Checklist

| # | Deliverable | Status | Link |
|---|-------------|--------|------|
| 1 | Working 7-step web app (runnable) | DONE | Live demo above |
| 2 | GitHub repo (README + SETUP.md) | DONE | [README](https://github.com/EudaLabs/HealthWithSevgi#readme) · [SETUP.md](https://github.com/EudaLabs/HealthWithSevgi/blob/main/SETUP.md) |
| 3 | Docker image + `docker compose up` < 30s | DONE | [Dockerfile](https://github.com/EudaLabs/HealthWithSevgi/blob/main/hf-space/Dockerfile) · [GHCR](https://github.com/EudaLabs/HealthWithSevgi/pkgs/container/healthwithsevgi) |
| 4 | 2-page Project Report PDF (architecture, decisions, challenges, lessons) | DONE | [Final_Project_Report.pdf](Final_Project_Report.pdf) |
| 5 | Jira board — velocity + burndown charts | DONE | [Jira board](https://berfindurualkan.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog) · [Burndown](Sprint5_Burndown.jpg) · [Backlog screenshot](Sprint5_Jira_Backlog.jpg) |
| 6 | Figma — wireframes + interactive prototype | DONE | [Figma — All 7 Steps](https://www.figma.com/design/1K1Dw8PC6P98NZAa30DzII/430-HealthWithSevgi?node-id=0-1) |
| 7 | GitHub Wiki — all sprint reviews | DONE | [[Sprint 1]] · [[Sprint 2]] · [[Sprint 3]] · [[Sprint 4]] · [[Sprint 5]] |
| 8 | User testing report (non-CS participant, 7 tasks, SUS) | DONE | [Sprint5_User_Testing_Report.pdf](Sprint5_User_Testing_Report.pdf) — P1: 7 / 7 PASS, SUS 90 |
| 9 | Usability video (≤ 5 min) | DONE | [Google Drive — recorded on UserBrain](https://drive.google.com/file/d/1VjD9xwUgDmsVOWn-OX9clYOTsL9FxwGz/view?usp=drive_link) |
| 10 | Signed consent form | DONE | [Sprint5_Consent_Form.pdf](Sprint5_Consent_Form.pdf) — signed by P1 on 27.04.2026 |
| 11 | Test reports — all 4 prior sprints | DONE | [Sprint 2 QA](Sprint2_QA_Report_v2_Post-Fix.pdf) · [Sprint 3 QA](Sprint3_QA_Test_Cases.pdf) · [Sprint 4 QA](Sprint4_QA_Full_Pipeline_Test_Report.pdf) · [Sprint 5 Full Domain Coverage](Sprint5_Full_Domain_Coverage.pdf) · [Sprint 5 E2E Regression](Sprint5_E2E_Regression.pdf) |
| 12 | 10-min final jury slide deck | IN PROGRESS | Owned by team (frontend lead) |

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
| Gemini 2.5 Flash transient failure on Step 7 during demo | Medium | Pre-cache the insight by running the demo dataset once before jury; empty-state fallback already added |
| Figma prototype link requires viewer sign-in | Low | Switch share setting to "anyone with link can view" |
| Jira charts inaccessible to external graders | Low | Export PNG snapshots into wiki |
| Docker `compose up` fails on cold network (GHCR pull) | Low | Pre-pull on demo machine; keep local build as fallback |

## Open Questions / To-Finalise

- [ ] Exact jury room / order in panel
- [ ] Who narrates which part of the 10-min demo

---

*This is a living document — updated as deliverables land. Last edit: 5 May 2026 (final-submission day).*
