## Stage 1 — install dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --no-compile --target=/build/deps -r requirements.txt \
    && find /build/deps -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /build/deps -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true

## Stage 2 — slim runtime
FROM python:3.12-slim

# Native libs required by scikit-learn, xgboost, lightgbm, scipy, shap
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libopenblas0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages

COPY app ./app
COPY datasets ./datasets
COPY data_cache ./data_cache
COPY arena ./arena
COPY static ./static
COPY main_hf.py .

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "main_hf:app", "--host", "0.0.0.0", "--port", "7860"]
