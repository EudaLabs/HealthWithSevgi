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
uvicorn app.main:app --reload --port 8001
```

API docs will be available at: `http://localhost:8001/docs`

## Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Start dev server
pnpm dev
```

The app will be available at: `http://localhost:5173` (the Vite dev server proxies `/api` requests to the backend on `8001`).

## Environment Variables

Create a `.env` file in the project root (never commit this):

```env
# Backend
BACKEND_PORT=8001
DEBUG=true

# Frontend (Vite uses VITE_ prefix)
VITE_API_URL=http://localhost:8001
```

## Running Tests

```bash
# Backend tests (pytest)
cd backend
source venv/bin/activate
pytest -v
```

The frontend has no automated test suite yet; QA is manual.

## Project Structure

See [README.md](README.md#-repository-structure) for full directory layout.

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 8001 already in use | `lsof -ti:8001 \| xargs kill` or change port in `.env` |
| Python venv not activating | Make sure you're in the `backend/` directory |
| Node modules missing | Run `pnpm install` in `frontend/` |
| CORS errors | Backend must be running on port 8001 |
| `pnpm` not found | Install globally with `npm install -g pnpm` |

## IDE Recommendations

- **VS Code** with extensions: Python, ESLint, Prettier, Vite
- **PyCharm** for backend, **WebStorm** for frontend (JetBrains)
