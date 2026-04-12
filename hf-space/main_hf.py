"""HuggingFace Spaces entry — serves API + static frontend."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.services.certificate_service import CertificateService
from app.services.data_service import DataService
from app.services.ethics_service import EthicsService
from app.services.explain_service import ExplainService
from app.services.ml_service import MLService
from arena.service import ArenaService

app = FastAPI(title="HealthWithSevgi API", version="1.3.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.data_service = DataService()
app.state.ml_service = MLService()
app.state.explain_service = ExplainService()
app.state.ethics_service = EthicsService()
app.state.certificate_service = CertificateService()
app.state.arena_service = ArenaService(app.state.ml_service)

from app.routers.data_router import router as data_router
from app.routers.explain_router import router as explain_router
from app.routers.ml_router import router as ml_router
from arena.router import router as arena_router

app.include_router(data_router)
app.include_router(ml_router)
app.include_router(explain_router)
app.include_router(arena_router)

STATIC_DIR = Path(__file__).parent / "static"

# Health check — verify critical native libraries load correctly
@app.get("/health")
async def health_check() -> dict:
    errors: list[str] = []
    for lib in ("sklearn", "xgboost", "lightgbm", "shap", "scipy"):
        try:
            __import__(lib)
        except Exception as exc:
            errors.append(f"{lib}: {exc}")
    if errors:
        return {"status": "degraded", "errors": errors}
    return {"status": "healthy"}

# Serve frontend static files
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        file = STATIC_DIR / full_path
        if file.is_file():
            return FileResponse(file)
        return FileResponse(STATIC_DIR / "index.html")
