# ── Stage 1: Build React frontend ─────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN npm i -g pnpm && pnpm install --frozen-lockfile || pnpm install
COPY frontend/ .
RUN pnpm build

# ── Stage 2: Install Python deps ─────────────────────────────
FROM python:3.12-slim AS py-builder

WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --no-compile --target=/build/deps -r requirements.txt \
    && find /build/deps -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /build/deps -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true

# ── Stage 3: Slim runtime ────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Python deps
COPY --from=py-builder /build/deps /usr/local/lib/python3.12/site-packages

# Backend source
COPY backend/app ./app
COPY backend/datasets ./datasets
COPY backend/data_cache ./data_cache

# HF entrypoint
COPY hf-space/main_hf.py .

# Built frontend → /app/static (served by main_hf.py)
COPY --from=frontend-builder /frontend/dist ./static

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "main_hf:app", "--host", "0.0.0.0", "--port", "7860"]
