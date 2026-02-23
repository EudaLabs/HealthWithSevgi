# HealthWithSevgi — ML Visualization Tool for Healthcare

> **SENG 430 · Software Quality Assurance**
> Çankaya University · Spring 2025-2026
> Instructor: Dr. Sevgi Koyuncu Tunç

An interactive, browser-based ML learning tool that guides healthcare professionals through a **7-step pipeline** — from choosing a medical specialty to training an AI model and checking it for fairness — with **no coding required**.

## 🏥 What It Does

| Step | Name | Description |
|------|------|-------------|
| 1 | Clinical Context | Introduces the medical problem the AI will tackle |
| 2 | Data Exploration | Upload patient data (CSV) or use a built-in dataset |
| 3 | Data Preparation | Handle missing values, normalise, split train/test |
| 4 | Model & Parameters | Pick one of 6 ML models and tune via sliders |
| 5 | Results | Accuracy, sensitivity, specificity, confusion matrix, ROC |
| 6 | Explainability | Feature importance + single-patient SHAP explanations |
| 7 | Ethics & Bias | Subgroup fairness audit + EU AI Act compliance checklist |

**20 clinical domains** supported (Cardiology, Nephrology, Oncology, Neurology, Diabetes, Pulmonology, Sepsis/ICU, Fetal Health, Dermatology, Stroke Risk, and more).

**6 ML models**: KNN, SVM, Decision Tree, Random Forest, Logistic Regression, Naïve Bayes.

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Vite |
| Backend | FastAPI (Python) |
| ML Engine | scikit-learn |
| Styling | CSS (DM Sans / DM Mono / Fraunces) |
| Diagrams | Figma + draw.io |
| PM | Jira |

## 📁 Repository Structure

```
HealthWithSevgi/
├── frontend/                # React 18 + Vite application
│   ├── public/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Step pages (Step1–Step7)
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # Helper functions
│   │   ├── styles/          # Global styles & theme
│   │   ├── assets/          # Static assets (icons, images)
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                 # FastAPI REST API
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── routers/         # API route modules
│   │   ├── services/        # ML training, preprocessing, prediction
│   │   ├── models/          # Pydantic schemas
│   │   └── utils/           # Helpers (certificate gen, etc.)
│   ├── datasets/            # Built-in clinical datasets (CSV)
│   ├── tests/               # pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/                    # Reference documents & design specs
│   ├── ML_Tool_User_Guide.docx
│   ├── GENERAL_DESIGN_SAMPLE_HTML.html
│   └── 6_MODEL_VISUALISATION_PAGES__SAMPLE_HTML.html
│
├── .github/                 # GitHub templates & workflows
│   └── pull_request_template.md
│
├── .gitignore
├── SETUP.md                 # Local development setup guide
└── README.md                # ← You are here
```

## 🚀 Quick Start

See **[SETUP.md](SETUP.md)** for full instructions.

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## 🌿 Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready, protected |
| `develop` | Integration branch for sprint work |
| `feature/US-XXX` | One branch per user story |

**Rules:**
- All changes go through Pull Requests
- PRs require at least 1 approval
- `main` and `develop` are protected — no direct pushes

## 👥 Team

| Role | Name |
|------|------|
| Product Owner + Developer | Efe |
| UX Designer | Burak |
| Lead Developer + Scrum Master | Batuhan |
| Developer | Berat |
| QA / Documentation Lead | Berfin |

## 📋 Links

- **Jira Board:** [TBD]
- **Figma Designs:** [TBD]
- **GitHub Wiki:** [Wiki →](../../wiki)
- **API Docs:** `http://localhost:8000/docs` (when running locally)

## 📄 License

This project is developed as part of the SENG 430 course at Çankaya University. All rights reserved.
