# Development Toolchain — HealthWithSevgi

> This document visualises the complete development toolchain used across the
> HealthWithSevgi project lifecycle — from design and planning through development,
> testing, and deployment.
>
> **This is NOT a C4 diagram.** It shows tools and their relationships in the development
> workflow, not the runtime software architecture.
>
> **Project:** HealthWithSevgi — ML Visualization Tool for Healthcare
> **Course:** SENG 430 · Software Quality Assurance · Cankaya University
> **Last Updated:** 2026-02-26

---

## Toolchain Overview

The toolchain is organized into seven functional categories. Each tool serves a specific
role in the software development lifecycle.

```mermaid
graph TB
    subgraph DESIGN["Design and Prototyping"]
        Figma["Figma<br/><i>UI/UX Wireframes</i>"]
        DrawIO["draw.io<br/><i>Architecture Diagrams</i>"]
        FigJam["FigJam / Miro<br/><i>Retrospective Boards</i>"]
    end

    subgraph PM["Project Management"]
        Jira["Jira<br/><i>Backlog, Sprints, Stories</i>"]
        GForms["Google Forms<br/><i>Team Charter</i>"]
    end

    subgraph VCS["Version Control"]
        Git["Git<br/><i>Local Version Control</i>"]
        GitHub["GitHub<br/><i>Remote Repo, PRs, Wiki</i>"]
        GHActions["GitHub Actions<br/><i>CI/CD Pipelines</i>"]
        PRTemplate["PR Template<br/><i>Linked to Jira US</i>"]
    end

    subgraph FRONTEND["Frontend Stack"]
        React["React 18<br/><i>Component UI Framework</i>"]
        Vite["Vite<br/><i>Build Tool and Dev Server</i>"]
        Tailwind["Tailwind CSS<br/><i>Utility-First Styling</i>"]
        RRouter["React Router v6<br/><i>Client-Side Routing</i>"]
        TypeScript["TypeScript<br/><i>Type Safety (Optional)</i>"]
    end

    subgraph BACKEND["Backend Stack"]
        Python["Python 3.10+<br/><i>Backend Language</i>"]
        FastAPI["FastAPI 0.110+<br/><i>REST API Framework</i>"]
        Uvicorn["Uvicorn 0.29+<br/><i>ASGI Server</i>"]
        Pydantic["Pydantic v2<br/><i>Data Validation</i>"]
    end

    subgraph ML["ML and Data Science"]
        ScikitLearn["scikit-learn 1.4+<br/><i>6 ML Algorithms</i>"]
        Pandas["pandas 2.2+<br/><i>Data Manipulation</i>"]
        NumPy["numpy 1.26+<br/><i>Numerical Computing</i>"]
        SHAP["SHAP 0.45+<br/><i>Model Explainability</i>"]
        SMOTE["imbalanced-learn 0.12+<br/><i>Class Imbalance (SMOTE)</i>"]
        ReportLab["reportlab 4.1+<br/><i>PDF Certificate Gen</i>"]
    end

    subgraph QUALITY["Quality and Testing"]
        ESLint["ESLint<br/><i>JS/TS Linting</i>"]
        Prettier["Prettier<br/><i>Code Formatting</i>"]
        Pytest["pytest<br/><i>Backend Unit Tests</i>"]
        Vitest["Vitest / Jest<br/><i>Frontend Unit Tests</i>"]
        Lighthouse["Lighthouse<br/><i>Performance Audit</i>"]
        Axe["axe<br/><i>Accessibility Audit</i>"]
    end

    subgraph INFRA["Infrastructure (Planned)"]
        Docker["Docker<br/><i>Containerisation</i>"]
        Compose["docker-compose<br/><i>Full-Stack Dev Env</i>"]
    end

    %% Cross-category relationships
    Figma -->|"Design handoff"| React
    Jira -->|"Story branch naming"| Git
    Git -->|"Push/Pull"| GitHub
    GitHub -->|"Triggers"| GHActions
    GitHub --- PRTemplate

    Vite -->|"Bundles"| React
    React --- RRouter
    React --- Tailwind
    Uvicorn -->|"Hosts"| FastAPI
    FastAPI --- Pydantic
    ScikitLearn --- Pandas
    ScikitLearn --- NumPy
    ScikitLearn --- SHAP
    Pandas --- SMOTE

    Compose -->|"Orchestrates"| Vite
    Compose -->|"Orchestrates"| Uvicorn
    Docker -->|"Builds images for"| Compose

    GHActions -->|"Runs"| Pytest
    GHActions -->|"Runs"| ESLint
    Lighthouse -->|"Audits"| React
    Axe -->|"Audits"| React

    style DESIGN fill:#e8f5e9,stroke:#2e7d32,color:#000
    style PM fill:#e3f2fd,stroke:#1565c0,color:#000
    style VCS fill:#fce4ec,stroke:#c62828,color:#000
    style FRONTEND fill:#fff3e0,stroke:#e65100,color:#000
    style BACKEND fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style ML fill:#e0f7fa,stroke:#00695c,color:#000
    style QUALITY fill:#fff9c4,stroke:#f9a825,color:#000
    style INFRA fill:#efebe9,stroke:#4e342e,color:#000
```

---

## Development Lifecycle Pipeline

This diagram shows the flow of work through the toolchain — from requirements
to deployment — and which tools are used at each stage.

```mermaid
graph LR
    subgraph PLAN["1. Plan"]
        A1["Jira<br/>Create User Stories"]
        A2["Jira<br/>Sprint Planning"]
        A3["Jira<br/>Estimate Points"]
    end

    subgraph DESIGN2["2. Design"]
        B1["Figma<br/>Create Wireframes"]
        B2["Figma<br/>Design Review"]
        B3["Figma<br/>Instructor Approval"]
    end

    subgraph DEVELOP["3. Develop"]
        C1["Git<br/>Create Feature Branch"]
        C2["VS Code<br/>Write Code"]
        C3["Vite / Uvicorn<br/>Run Dev Servers"]
        C4["ESLint + Prettier<br/>Auto-Format"]
    end

    subgraph TEST["4. Test"]
        D1["pytest<br/>Backend Unit Tests"]
        D2["Vitest<br/>Frontend Unit Tests"]
        D3["Lighthouse<br/>Performance Score"]
        D4["axe<br/>Accessibility Check"]
    end

    subgraph REVIEW["5. Review"]
        E1["GitHub<br/>Create Pull Request"]
        E2["GitHub<br/>Code Review"]
        E3["GitHub Actions<br/>CI Checks"]
    end

    subgraph DEPLOY["6. Deploy"]
        F1["Docker<br/>Build Images"]
        F2["docker-compose<br/>Start Full Stack"]
        F3["Uvicorn<br/>Serve API"]
    end

    subgraph RETRO["7. Retrospect"]
        G1["Miro / FigJam<br/>Keep-Improve-Try"]
        G2["GitHub Wiki<br/>Meeting Notes"]
        G3["Jira<br/>Velocity Review"]
    end

    PLAN --> DESIGN2
    DESIGN2 --> DEVELOP
    DEVELOP --> TEST
    TEST --> REVIEW
    REVIEW --> DEPLOY
    DEPLOY --> RETRO
    RETRO -->|"Next Sprint"| PLAN

    style PLAN fill:#e3f2fd,stroke:#1565c0,color:#000
    style DESIGN2 fill:#e8f5e9,stroke:#2e7d32,color:#000
    style DEVELOP fill:#fff3e0,stroke:#e65100,color:#000
    style TEST fill:#fff9c4,stroke:#f9a825,color:#000
    style REVIEW fill:#fce4ec,stroke:#c62828,color:#000
    style DEPLOY fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style RETRO fill:#e0f7fa,stroke:#00695c,color:#000
```

---

## Branch and CI/CD Workflow

This diagram shows how code flows from a developer's local environment
through the Git branching strategy to production.

```mermaid
graph TD
    DEV["Developer Local<br/>VS Code + Vite + Uvicorn"]
    FB["feature/US-XXX<br/>Feature Branch"]
    PR["Pull Request<br/>Linked to Jira Story"]
    CI["GitHub Actions CI<br/>Lint + Test + Build"]
    CR["Code Review<br/>1 Approval Required"]
    DEVELOP["develop branch<br/>Integration Branch"]
    MAIN["main branch<br/>Production-Ready"]

    DEV -->|"git checkout -b feature/US-XXX"| FB
    FB -->|"git push -u origin"| PR
    PR --> CI
    CI -->|"All checks pass"| CR
    CI -->|"Checks fail"| DEV
    CR -->|"Approved"| DEVELOP
    CR -->|"Changes requested"| DEV
    DEVELOP -->|"Sprint release merge"| MAIN

    style DEV fill:#fff3e0,stroke:#e65100,color:#000
    style FB fill:#e8f5e9,stroke:#2e7d32,color:#000
    style PR fill:#fce4ec,stroke:#c62828,color:#000
    style CI fill:#fff9c4,stroke:#f9a825,color:#000
    style CR fill:#e3f2fd,stroke:#1565c0,color:#000
    style DEVELOP fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style MAIN fill:#e0f2f1,stroke:#00695c,color:#000
```

---

## Frontend Build Pipeline

This diagram shows how the frontend source code is transformed
into production-ready static assets.

```mermaid
graph LR
    SRC["Source Files<br/>JSX + CSS + Assets"]
    ESLINT["ESLint<br/>Lint Check"]
    PRETTIER["Prettier<br/>Format Check"]
    VITE_DEV["Vite Dev Server<br/>HMR at :5173"]
    VITE_BUILD["Vite Build<br/>Production Bundle"]
    DIST["dist/<br/>Static HTML + JS + CSS"]
    BROWSER["Browser<br/>React SPA"]

    SRC --> ESLINT
    ESLINT --> PRETTIER
    PRETTIER --> VITE_DEV
    PRETTIER --> VITE_BUILD
    VITE_DEV -->|"Development"| BROWSER
    VITE_BUILD --> DIST
    DIST -->|"Production"| BROWSER

    style SRC fill:#fff3e0,stroke:#e65100,color:#000
    style ESLINT fill:#fff9c4,stroke:#f9a825,color:#000
    style PRETTIER fill:#fff9c4,stroke:#f9a825,color:#000
    style VITE_DEV fill:#e8f5e9,stroke:#2e7d32,color:#000
    style VITE_BUILD fill:#e8f5e9,stroke:#2e7d32,color:#000
    style DIST fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style BROWSER fill:#e3f2fd,stroke:#1565c0,color:#000
```

---

## Backend Runtime Pipeline

This diagram shows how a request flows through the backend technology stack
from the frontend to the ML engine and back.

```mermaid
graph LR
    REQ["HTTP Request<br/>from React SPA"]
    UVICORN["Uvicorn<br/>ASGI Server :8000"]
    CORS["CORS Middleware<br/>Origin Validation"]
    FASTAPI["FastAPI Router<br/>Path Matching"]
    PYDANTIC["Pydantic v2<br/>Request Validation"]
    SERVICE["Service Layer<br/>Business Logic"]
    SKLEARN["scikit-learn<br/>Model Train/Predict"]
    SHAP2["SHAP<br/>Explainability"]
    PANDAS["pandas<br/>Data Processing"]
    RESP["JSON Response<br/>to React SPA"]

    REQ --> UVICORN
    UVICORN --> CORS
    CORS --> FASTAPI
    FASTAPI --> PYDANTIC
    PYDANTIC --> SERVICE
    SERVICE --> SKLEARN
    SERVICE --> SHAP2
    SERVICE --> PANDAS
    SKLEARN --> RESP
    SHAP2 --> RESP
    PANDAS --> RESP

    style REQ fill:#e3f2fd,stroke:#1565c0,color:#000
    style UVICORN fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style CORS fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style FASTAPI fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style PYDANTIC fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style SERVICE fill:#fff3e0,stroke:#e65100,color:#000
    style SKLEARN fill:#e0f7fa,stroke:#00695c,color:#000
    style SHAP2 fill:#e0f7fa,stroke:#00695c,color:#000
    style PANDAS fill:#e0f7fa,stroke:#00695c,color:#000
    style RESP fill:#e8f5e9,stroke:#2e7d32,color:#000
```

---

## Docker Containerisation (Planned)

This diagram shows the **planned** Docker and docker-compose setup that will package
the full-stack application into containers. This is a Sprint 1 deliverable (D-013).

```mermaid
graph TB
    subgraph HOST["Host Machine"]
        subgraph COMPOSE["docker-compose.yml"]
            subgraph FE_CONTAINER["frontend container"]
                NODE["Node.js Runtime"]
                VITE_S["Vite Dev Server<br/>:5173"]
                REACT_APP["React 18 SPA<br/>+ Tailwind CSS"]
            end

            subgraph BE_CONTAINER["backend container"]
                PY_RT["Python 3.10+ Runtime"]
                UVI["Uvicorn ASGI<br/>:8000"]
                FA["FastAPI App"]
                SK["scikit-learn<br/>+ SHAP + pandas"]
                CSV["datasets/<br/>20 CSV files"]
            end
        end
    end

    BROWSER_EXT["Browser<br/>localhost:5173"]

    BROWSER_EXT -->|"HTTP"| VITE_S
    VITE_S -->|"API proxy"| UVI
    NODE --> VITE_S
    VITE_S --> REACT_APP
    PY_RT --> UVI
    UVI --> FA
    FA --> SK
    FA --> CSV

    style HOST fill:#efebe9,stroke:#4e342e,color:#000
    style COMPOSE fill:#f5f5f5,stroke:#616161,color:#000
    style FE_CONTAINER fill:#fff3e0,stroke:#e65100,color:#000
    style BE_CONTAINER fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style BROWSER_EXT fill:#e3f2fd,stroke:#1565c0,color:#000
```

---

## Complete Tool Reference

### Design and Collaboration

| Tool | Category | Purpose | Deliverable |
|------|----------|---------|-------------|
| **Figma** | UI/UX Design | Wireframes and high-fidelity mockups for all 7 steps, clickable prototype | Shared Figma link per sprint |
| **draw.io** | Architecture Diagrams | Architecture diagrams exported as PDF (alternative to Figma for diagrams) | PDF in docs or GitHub Wiki |
| **FigJam / Miro** | Retrospectives | Sprint retrospective boards (Keep / Improve / Try) | Screenshot in GitHub Wiki |
| **Google Forms** | Team Management | Team charter submission | Google Form response |

### Project Management

| Tool | Category | Purpose | Deliverable |
|------|----------|---------|-------------|
| **Jira** | Agile PM | Product backlog, sprint backlog, user stories, story points, velocity tracking, burndown | Shared board link for instructor |

### Version Control and CI/CD

| Tool | Category | Purpose | Deliverable |
|------|----------|---------|-------------|
| **Git** | VCS | Local version control, branching (`feature/US-XXX`), commits | Commit history |
| **GitHub** | Remote VCS | Repository hosting, pull requests, code review, branch protection | GitHub repo link |
| **GitHub Wiki** | Documentation | Architecture decisions, meeting notes, API docs, sprint notes | GitHub Wiki tab |
| **GitHub Actions** | CI/CD | Automated linting, testing, and build verification on every PR | Workflow status badges |
| **PR Template** | Process | Standardised PR format linked to Jira user stories | `.github/pull_request_template.md` |

### Frontend Technologies

| Tool | Version | Purpose | Configuration |
|------|---------|---------|---------------|
| **React** | 18.x | Component-based UI framework | — |
| **Vite** | Latest | Fast build tool with HMR, dev server at `:5173` | `vite.config.js` |
| **Tailwind CSS** | Latest | Utility-first CSS, green theme (`#16a34a` primary) | `tailwind.config.js` |
| **React Router** | v6 | Client-side routing for 8 step pages | `App.jsx` |
| **TypeScript** | Optional | Type safety for frontend code | `tsconfig.json` |
| **ESLint** | Latest | JavaScript/TypeScript linting | `.eslintrc.js` (to be configured) |
| **Prettier** | Latest | Consistent code formatting | `.prettierrc` (to be configured) |

### Backend Technologies

| Tool | Version | Purpose | Configuration |
|------|---------|---------|---------------|
| **Python** | 3.10+ | Backend programming language | — |
| **FastAPI** | 0.110+ | REST API framework with auto-generated OpenAPI docs at `/docs` | `app/main.py` |
| **Uvicorn** | 0.29+ | ASGI server with hot-reload for development | `--reload --port 8000` |
| **Pydantic** | v2 (2.6+) | Request/response data validation and serialisation | `app/models/schemas.py` |
| **python-multipart** | 0.0.9+ | Multipart file upload support for CSV files | `requirements.txt` |

### ML and Data Science

| Tool | Version | Purpose | Models/Features |
|------|---------|---------|-----------------|
| **scikit-learn** | 1.4+ | Core ML algorithms | KNN, SVM, Decision Tree, Random Forest, Logistic Regression, Naive Bayes |
| **pandas** | 2.2+ | Data manipulation and analysis | DataFrame operations, CSV I/O, missing value handling |
| **numpy** | 1.26+ | Numerical computing | Array operations, metrics computation |
| **SHAP** | 0.45+ | Model explainability | Feature importance rankings, per-patient waterfall explanations |
| **imbalanced-learn** | 0.12+ | Class imbalance handling | SMOTE oversampling for training data |
| **reportlab** | 4.1+ | PDF generation | Summary certificate with model results and completion date |

### Quality and Testing

| Tool | Category | Purpose | Target |
|------|----------|---------|--------|
| **pytest** | Backend Testing | Unit tests for API endpoints, services, and ML pipeline | Coverage target: 80%+ |
| **Vitest / Jest** | Frontend Testing | Unit tests for React components and hooks | Coverage target: 70%+ |
| **Lighthouse** | Performance | Performance audit score | Target: 80+ |
| **axe** | Accessibility | WCAG AA compliance, contrast ratio 4.5:1, keyboard navigation | Full compliance |
| **Google Forms / Maze** | User Testing | Usability testing with non-CS participants (Weeks 9-10) | PDF of feedback forms |

### Infrastructure (Planned — to be configured in Sprint 1)

| Tool | Category | Purpose | Configuration |
|------|----------|---------|---------------|
| **Docker** | Containerisation | Package backend into reproducible containers | `Dockerfile` (to be created) |
| **docker-compose** | Orchestration | Single command (`docker-compose up`) to start full stack | `docker-compose.yml` (to be created) |

### Typography (Design System)

| Font | Usage | Weight Variants |
|------|-------|-----------------|
| **DM Sans** | Primary UI text | Light, Regular, Medium, SemiBold, Bold |
| **DM Mono** | Code and data display | Regular, Medium |
| **Fraunces** | Heading serif accents | Regular, SemiBold |

---

## References

- [HealthWithSevgi Sprint 1 Assignment](../Sprint_1_Assignment.md) — Required toolchain table
- [C4 Architecture Diagrams](./c4-architecture.md) — Runtime software architecture (separate from this toolchain)
- [Mermaid Flowchart Syntax](https://mermaid.js.org/syntax/flowchart.html)
