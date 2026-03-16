FROM python:3.12-slim

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/app ./app
COPY backend/datasets ./datasets

# Copy pre-built frontend
COPY frontend/dist ./static

# Copy HF-specific entrypoint
COPY hf-space/main_hf.py .

# HuggingFace Spaces requires port 7860
EXPOSE 7860

CMD ["python", "-m", "uvicorn", "main_hf:app", "--host", "0.0.0.0", "--port", "7860"]
