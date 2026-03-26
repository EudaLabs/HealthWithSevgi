"""HealthWithSevgi — FastAPI Backend Entry Point"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.certificate_service import CertificateService
from app.services.data_service import DataService
from app.services.ethics_service import EthicsService
from app.services.explain_service import ExplainService
from app.services.ml_service import MLService

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

app = FastAPI(
    title="HealthWithSevgi API",
    description="ML Visualization Tool for Healthcare — REST API",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton service instances
app.state.data_service = DataService()
app.state.ml_service = MLService()
app.state.explain_service = ExplainService()
app.state.ethics_service = EthicsService()
app.state.certificate_service = CertificateService()

# Routers
from app.routers.data_router import router as data_router  # noqa: E402
from app.routers.explain_router import router as explain_router  # noqa: E402
from app.routers.ml_router import router as ml_router  # noqa: E402

app.include_router(data_router)
app.include_router(ml_router)
app.include_router(explain_router)

# Model Arena extension
import sys
from pathlib import Path
_arena_path = str(Path(__file__).resolve().parent.parent.parent / "local" / "model-arena")
if _arena_path not in sys.path:
    sys.path.insert(0, _arena_path)
from arena.router import router as arena_router  # noqa: E402
from arena.service import ArenaService  # noqa: E402

app.state.arena_service = ArenaService(app.state.ml_service)
app.include_router(arena_router)


@app.get("/")
async def root() -> dict:
    return {"status": "ok", "project": "HealthWithSevgi", "version": "1.0.0"}


@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy"}
