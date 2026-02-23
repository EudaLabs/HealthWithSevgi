"""HealthWithSevgi — FastAPI Backend Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HealthWithSevgi API",
    description="ML Visualization Tool for Healthcare — REST API",
    version="0.1.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "project": "HealthWithSevgi"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
