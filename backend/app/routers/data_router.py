"""Data exploration and preparation REST endpoints."""
from __future__ import annotations

import io
import logging
import uuid

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from app.models.schemas import (
    DataExplorationResponse,
    PrepResponse,
    PrepSettings,
    SpecialtyInfo,
)
from app.services.specialty_registry import get_specialty, list_specialties

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["data"])

_MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


def _get_data_service(request: Request):
    return request.app.state.data_service


def _get_ml_service(request: Request):
    return request.app.state.ml_service


def _load_df(file: UploadFile | None, specialty_id: str, data_service) -> pd.DataFrame:
    if file is not None and file.filename:
        content = file.file.read()
        # Enforce 50 MB limit
        if len(content) > _MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds 50 MB limit (uploaded: {len(content) // (1024 * 1024)} MB)",
            )
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Could not parse CSV file: {exc}",
            )
        return df
    return data_service.get_example_dataset(specialty_id)


# ------------------------------------------------------------------
# Specialties
# ------------------------------------------------------------------

@router.get("/specialties", response_model=list[SpecialtyInfo])
def get_specialties() -> list[SpecialtyInfo]:
    return list_specialties()


@router.get("/specialties/{specialty_id}", response_model=SpecialtyInfo)
def get_specialty_by_id(specialty_id: str) -> SpecialtyInfo:
    spec = get_specialty(specialty_id)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"Specialty '{specialty_id}' not found")
    return spec


# ------------------------------------------------------------------
# Exploration
# ------------------------------------------------------------------

@router.post("/explore", response_model=DataExplorationResponse)
def explore_data(
    request: Request,
    specialty_id: str = Form(...),
    target_col: str = Form(...),
    file: UploadFile | None = File(None),
) -> DataExplorationResponse:
    ds = _get_data_service(request)
    df = _load_df(file, specialty_id, ds)

    if target_col not in df.columns:
        # Try to find target from specialty registry
        spec = get_specialty(specialty_id)
        if spec and spec.target_variable in df.columns:
            target_col = spec.target_variable
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Target column '{target_col}' not found. Available: {list(df.columns)}",
            )

    return ds.explore_dataframe(df, target_col)


# ------------------------------------------------------------------
# Preparation
# ------------------------------------------------------------------

@router.post("/prepare", response_model=PrepResponse)
def prepare_data(
    request: Request,
    specialty_id: str = Form(...),
    target_col: str = Form(...),
    test_size: float = Form(0.2),
    missing_strategy: str = Form("median"),
    normalization: str = Form("zscore"),
    use_smote: bool = Form(False),
    session_id: str = Form(None),
    file: UploadFile | None = File(None),
) -> PrepResponse:
    ds = _get_data_service(request)
    ml_service = _get_ml_service(request)
    df = _load_df(file, specialty_id, ds)

    if target_col not in df.columns:
        spec = get_specialty(specialty_id)
        if spec and spec.target_variable in df.columns:
            target_col = spec.target_variable
        else:
            raise HTTPException(status_code=422, detail=f"Target column '{target_col}' not found")

    settings = PrepSettings(
        test_size=test_size,
        missing_strategy=missing_strategy,  # type: ignore[arg-type]
        normalization=normalization,  # type: ignore[arg-type]
        use_smote=use_smote,
    )

    new_session_id = session_id or str(uuid.uuid4())

    try:
        X_train, X_test, y_train, y_test, response, feature_names = ds.prepare_data(
            df, target_col, settings, new_session_id
        )
    except Exception as exc:
        logger.exception("Data preparation failed")
        raise HTTPException(status_code=422, detail=str(exc))

    # Share prepared data with ML service, including specialty_id for certificate generation
    session_data = ds.get_session(new_session_id)
    if session_data:
        session_data["specialty_id"] = specialty_id  # Fix: store for certificate generation
        ml_service.store_session_data(new_session_id, session_data)

    return response
