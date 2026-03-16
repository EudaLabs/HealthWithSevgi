FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY datasets ./datasets
COPY static ./static
COPY main_hf.py .

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "main_hf:app", "--host", "0.0.0.0", "--port", "7860"]
