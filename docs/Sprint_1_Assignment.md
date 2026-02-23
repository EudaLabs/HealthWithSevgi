# Sprint 1 Submission

> **SENG 430 · Software Quality Assurance**
> Çankaya University · Spring 2025-2026
> Source: WebOnline Assignment Page

**Opened:** Thursday, 19 February 2026, 12:00 AM
**Due:** Wednesday, 4 March 2026, 1:00 PM
**⚠️ No late submissions.**

---

We have attached User Manual and Sample UI HTML code for ML Visualisation Tool. Please submit the artifacts listed below until deadline. No late submissions.

## Artifact / Deliverables

### 1. Team Charter

Add here: https://forms.gle/VUDfi3rfnR4o8dCr6

Groups of 4/5 are formed in Week 1. Every group builds the same full system — all 20 clinical domains must be functional in every group's application.

Each group must assign the following roles:

| Role | Responsibilities |
|------|-----------------|
| Product Owner | Writes / refines user stories, prioritizes backlog, signs off on done criteria |
| UX Designer | Create UI designs |
| Lead Developer | Owns technical architecture decisions, code review, GitHub merge approvals |
| Scrum Master (one of the developers can do this) | Runs stand-ups, maintains Jira board, clears blockers, presents at showcase |
| Developer | Review user stories & estimate, develop features |
| QA / Documentation Lead | Writes test cases, runs manual tests, maintains GitHub Wiki, writes progress report |

### 2. Domain Coverage Plan

1-page PDF — lists all 20 domains with their dataset sources URLs, target variable

### 3. Jira Product Backlog

Jira board URL — create minimum 20 user stories across all 7 steps, prioritized, estimated (extracted from user manual)

### 4. User Story Standards (Jira)

All user stories are derived from the User Manual. Students read the manual (attached `ML_Tool_User_Guide.docx`), identify every feature from the end-user perspective, and create Jira tickets before the sprint begins. Each ticket must have acceptance criteria written in Gherkin (Given / When / Then) format.

**📝 Standard User Story Format**

- **Title:** `US-[number]: [short imperative statement]`
- **Story:** `As a [healthcare professional / student], I want to [action], so that [benefit].`
- **Priority:** Must Have / Should Have / Could Have / Won't Have (MoSCoW)
- **Acceptance Criteria:** Gherkin format — `Given [context] / When [action] / Then [expected outcome].`
- **Sprint:** Assigned at Sprint Planning; moved to Done only when all acceptance criteria are verified.

### Example User Stories — Sprint 1

| ID | Story | Acceptance Criteria (summary) |
|----|-------|-------------------------------|
| US-001 | As a doctor, I want to select my medical specialty from a pill bar, so that all content updates to my clinical context. | Given I am on the home screen, When I click 'Cardiology', Then the domain label updates and Step 1 text shows heart failure content. |
| US-002 | As a nurse, I want to upload my own CSV patient file, so that I can use real data instead of the example dataset. | Given I click 'Upload Your CSV', When I drag a valid .csv file, Then I see the filename, size, and column count with a green success banner. |
| US-003 | As a clinical researcher, I want to see which columns have missing values, so that I can decide how to handle them before training. | Given data is loaded, When I view the feature table, Then each column shows type, missing %, and a colour-coded action tag. |
| US-004 | As a student learning ML, I want to move a slider to change the K value in KNN and see the scatter plot update instantly, so that I understand how K affects predictions. | Given KNN is selected, When I move the K slider, Then the canvas redraws within 16 ms and the metrics update within 300 ms. |
| US-005 | As a healthcare educator, I want to download a PDF summary certificate after completing all 7 steps, so that I have evidence of the exercise. | Given Step 7 is reached, When I click 'Download Certificate', Then a PDF is generated within 10 seconds with all 6 metric values included. |

### 5. GitHub Repository

GitHub URL — `README.md` with repo structure, `SETUP.md` skeleton, branch protection rules set

### 6. GitHub Wiki — Home Page

GitHub Wiki URL — team page created, member names and roles, Week 1 meeting notes

### 7. Sprint 1 Backlog

Jira Sprint URL — sprint created, stories committed to Sprint 1 with estimates

### 8. Figma Wireframes — All 7 Steps

Figma URL — high-fidelity screens for every step; domain pill bar showing all 20 domain pills; stepper; footer nav; domain-switch confirmation dialog. Green theme applied.

Sample HTML Design (`GENERAL_DESIGN_SAMPLE_HTML.html`) and data visualisation designs for each model (`6_MODEL_VISUALISATION_PAGES__SAMPLE_HTML.html`) with minimum requirements is attached. You are free to create better designs with new or extra features.

### 9. Architecture Diagram

Figma or draw.io PDF — shows frontend, backend, scikit-learn layer, session storage, API endpoints

---

## Required Toolchain

All groups must use the following tools throughout the course. Instructors will verify tool usage during semi-weekly showcase check-ins. (If you have another tech-stack preference, write it in architecture doc.)

| Tool | Category | Purpose in This Project | What to Submit |
|------|----------|------------------------|----------------|
| Jira | Project Management | Product backlog, sprint backlog, user stories, story points, velocity tracking, burndown charts | Shared board link (read access for instructor) |
| Figma | UI/UX Design | Wireframes and high-fidelity mockups for all 7 steps; clickable prototype | Shared Figma link per sprint design review |
| GitHub | Version Control | All source code, branching strategy (feature branches), pull requests, code review | GitHub repo link; branch naming: `feature/US-XXX` |
| GitHub Wiki | Documentation | Architecture decisions, meeting notes, retrospective boards, API docs, sprint notes. Free with GitHub. | GitHub Wiki tab in team repo |
| React 18 + Vite | Frontend | Browser-based UI — all 7 steps, domain pill bar, stepper, sliders, charts | Deployed URL or localhost demo |
| FastAPI | Backend | REST API endpoints for training, prediction, preprocessing, certificate generation | API docs via `/docs` endpoint |
| scikit-learn | ML Engine | 6 model implementations: KNN, SVM, Decision Tree, Random Forest, Logistic Regression, Naive Bayes | Included in backend repo |
| Google Forms / Maze | User Testing | Usability testing with non-CS participants (Weeks 9–10) | PDF of completed feedback forms |
| Lighthouse / axe | Accessibility & Perf. | Performance score ≥ 80; contrast ratio 4.5:1; keyboard navigation | Screenshot of Lighthouse report |
| Miro (or FigJam) | Retrospectives | Sprint retrospective boards (Keep / Improve / Try) | Screenshot uploaded to GitHub Wiki or pinned in group WhatsApp/Discord |

---

## 📋 Week 2 Demo Agenda (Wednesday, 5 min per group)

1. **Team introduction:** members, roles, Scrum Master for this sprint, and domain coverage plan.
2. **Walk through Jira board:** show epics, top 5 user stories with acceptance criteria.
3. **Show GitHub repo structure** and GitHub Wiki home page.
4. **Walk through Figma wireframes:** show all 7 steps, domain pill bar with all 20 domain pills, domain-switch confirmation dialog, Column Mapper modal.
5. **Show architecture diagram:** explain frontend ↔ backend ↔ ML layers.

**Instructor gate:** Wireframes & architecture must be approved before Sprint 2 starts. Unapproved groups may not proceed to coding.

**Review questions:**
- Are user stories specific enough and prioritized?
- Are all Jira tickets linked to the User Manual features?

---

## Attached Files

- [ML_Tool_User_Guide.md](ML_Tool_User_Guide.md) — Full user manual (converted from docx)
- [GENERAL_DESIGN_SAMPLE_HTML.html](GENERAL_DESIGN_SAMPLE_HTML.html) — General UI design sample
- [6_MODEL_VISUALISATION_PAGES__SAMPLE_HTML.html](6_MODEL_VISUALISATION_PAGES__SAMPLE_HTML.html) — Model visualization page designs
