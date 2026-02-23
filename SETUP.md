# SETUP.md — Local Development Guide

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Node.js | ≥ 18.x | [nodejs.org](https://nodejs.org) |
| Python | ≥ 3.10 | [python.org](https://python.org) |
| Git | latest | [git-scm.com](https://git-scm.com) |

## Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

API docs will be available at: `http://localhost:8000/docs`

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The app will be available at: `http://localhost:5173`

## Environment Variables

Create a `.env` file in the project root (never commit this):

```env
# Backend
BACKEND_PORT=8000
DEBUG=true

# Frontend (Vite uses VITE_ prefix)
VITE_API_URL=http://localhost:8000
```

## Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Project Structure

See [README.md](README.md#-repository-structure) for full directory layout.

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | `lsof -ti:8000 \| xargs kill` or change port in `.env` |
| Python venv not activating | Make sure you're in the `backend/` directory |
| Node modules missing | Run `npm install` in `frontend/` |
| CORS errors | Backend must be running on port 8000 |

## IDE Recommendations

- **VS Code** with extensions: Python, ESLint, Prettier, Vite
- **PyCharm** for backend, **WebStorm** for frontend (JetBrains)
