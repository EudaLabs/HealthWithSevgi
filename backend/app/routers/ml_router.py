"""ML model training and evaluation REST endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.models.ml_schemas import (
    CompareResponse,
    ModelType,
    TrainRequest,
    TrainResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["ml"])


def _get_ml_service(request: Request):
    return request.app.state.ml_service


@router.post("/train", response_model=TrainResponse)
async def train_model(request: Request, body: TrainRequest) -> TrainResponse:
    ml = _get_ml_service(request)
    session = ml.get_session(body.session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{body.session_id}' not found. Run /api/prepare first.",
        )
    try:
        response = ml.train_and_evaluate(
            body.session_id, body.model_type, body.params,
            tune=body.tune,
            use_feature_selection=body.use_feature_selection,
        )
    except Exception as exc:
        logger.exception("Model training failed")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    # Cache metrics for comparison
    ml.store_train_response_in_model(response.model_id, response)
    return response


@router.post("/compare/{model_id}", response_model=CompareResponse)
async def add_to_comparison(request: Request, model_id: str) -> CompareResponse:
    ml = _get_ml_service(request)
    model_data = ml.get_model(model_id)
    if model_data is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    session_id = model_data.get("session_id", "")
    try:
        return ml.add_to_comparison(session_id, model_id)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/compare/{session_id}", response_model=CompareResponse)
async def get_comparison(request: Request, session_id: str) -> CompareResponse:
    ml = _get_ml_service(request)
    return ml.get_comparison(session_id)


@router.delete("/compare/{session_id}", status_code=204)
async def clear_comparison(request: Request, session_id: str) -> None:
    _get_ml_service(request).clear_comparison(session_id)


@router.get("/models/{model_id}")
async def get_model_info(request: Request, model_id: str) -> dict:
    ml = _get_ml_service(request)
    data = ml.get_model(model_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    return {
        "model_id": model_id,
        "model_type": data.get("model_type"),
        "params": data.get("params"),
        "session_id": data.get("session_id"),
        "feature_names": data.get("feature_names"),
        "classes": data.get("classes"),
    }
