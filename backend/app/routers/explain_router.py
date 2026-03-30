"""Explainability, ethics, and certificate REST endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.models.explain_schemas import (
    CertificateRequest,
    ChecklistUpdate,
    EthicsResponse,
    GlobalExplainabilityResponse,
    SamplePatientsResponse,
    SinglePatientExplainResponse,
    WhatIfRequest,
    WhatIfResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["explain"])


def _get_services(request: Request):
    return (
        request.app.state.ml_service,
        request.app.state.explain_service,
        request.app.state.ethics_service,
        request.app.state.certificate_service,
    )


def _get_model_data(ml_service, model_id: str) -> dict:
    data = ml_service.get_model(model_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found. Train a model first.")
    return data


@router.get("/explain/global/{model_id}", response_model=GlobalExplainabilityResponse)
def global_importance(request: Request, model_id: str) -> GlobalExplainabilityResponse:
    ml, explain, *_ = _get_services(request)
    data = _get_model_data(ml, model_id)
    try:
        return explain.global_importance(
            model_id=model_id,
            model=data["model"],
            X_test=data["X_test"],
            y_test=data["y_test"],
            feature_names=data["feature_names"],
            X_train=data["X_train"],
            model_type=str(data["model_type"]),
            classes=data["classes"],
        )
    except Exception as exc:
        logger.exception("Global explainability failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/explain/patient/{model_id}/{patient_index}", response_model=SinglePatientExplainResponse)
def single_patient_explain(
    request: Request, model_id: str, patient_index: int
) -> SinglePatientExplainResponse:
    ml, explain, *_ = _get_services(request)
    data = _get_model_data(ml, model_id)
    n_test = len(data["X_test"])
    if patient_index < 0 or patient_index >= n_test:
        raise HTTPException(status_code=422, detail=f"Patient index {patient_index} out of range [0, {n_test-1}]")
    try:
        return explain.single_patient(
            model_id=model_id,
            model=data["model"],
            patient_idx=patient_index,
            X_test=data["X_test"],
            feature_names=data["feature_names"],
            X_train=data["X_train"],
            model_type=str(data["model_type"]),
            classes=data["classes"],
            y_test=data["y_test"],
            scaler=data.get("scaler"),
        )
    except Exception as exc:
        logger.exception("Single-patient explanation failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/explain/what-if", response_model=WhatIfResponse)
def what_if(request: Request, body: WhatIfRequest) -> WhatIfResponse:
    ml, explain, *_ = _get_services(request)
    data = _get_model_data(ml, body.model_id)

    n_test = len(data["X_test"])
    if body.patient_index < 0 or body.patient_index >= n_test:
        raise HTTPException(
            status_code=400,
            detail=f"Patient index {body.patient_index} out of range [0, {n_test - 1}]",
        )
    if body.feature_name not in data["feature_names"]:
        raise HTTPException(
            status_code=400,
            detail=f"Feature '{body.feature_name}' not found. Available: {data['feature_names']}",
        )

    try:
        return explain.what_if(
            model_id=body.model_id,
            model=data["model"],
            patient_index=body.patient_index,
            feature_name=body.feature_name,
            new_value=body.new_value,
            X_test=data["X_test"],
            feature_names=data["feature_names"],
            scaler=data.get("scaler"),
        )
    except Exception as exc:
        logger.exception("What-if analysis failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/explain/sample-patients/{model_id}", response_model=SamplePatientsResponse)
def sample_patients(request: Request, model_id: str) -> SamplePatientsResponse:
    ml, explain, *_ = _get_services(request)
    data = _get_model_data(ml, model_id)
    try:
        return explain.sample_patients(
            model_id=model_id,
            model=data["model"],
            X_test=data["X_test"],
        )
    except Exception as exc:
        logger.exception("Sample patients retrieval failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/ethics/{model_id}", response_model=EthicsResponse)
def get_ethics(request: Request, model_id: str) -> EthicsResponse:
    ml, _, ethics, _ = _get_services(request)
    data = _get_model_data(ml, model_id)
    try:
        return ethics.analyze_bias(
            model_id=model_id,
            model=data["model"],
            X_test=data["X_test"],
            y_test=data["y_test"],
            feature_names=data["feature_names"],
            classes=data["classes"],
            X_train=data["X_train"],
            scaler=data.get("scaler"),
        )
    except Exception as exc:
        logger.exception("Ethics analysis failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/ethics/checklist")
def update_checklist(request: Request, body: ChecklistUpdate) -> dict:
    _, _, ethics, _ = _get_services(request)
    return ethics.update_checklist(body.model_id, body.item_id, body.checked)


@router.post("/generate-certificate")
def generate_certificate(request: Request, body: CertificateRequest) -> StreamingResponse:
    ml, _, ethics, cert_svc = _get_services(request)
    data = _get_model_data(ml, body.model_id)

    # Rebuild metrics from stored model
    metrics = data.get("metrics")
    if metrics is None:
        raise HTTPException(status_code=422, detail="Model metrics not available. Train the model first.")

    ethics_data = ethics.analyze_bias(
        model_id=body.model_id,
        model=data["model"],
        X_test=data["X_test"],
        y_test=data["y_test"],
        feature_names=data["feature_names"],
        classes=data["classes"],
        X_train=data["X_train"],
        scaler=data.get("scaler"),
    )

    session_id = data.get("session_id", "")
    specialty_name = "Healthcare ML"
    ml_session = ml.get_session(session_id)
    if ml_session:
        from app.services.specialty_registry import SPECIALTIES
        sid = ml_session.get("specialty_id", "")
        spec = SPECIALTIES.get(sid)
        if spec:
            specialty_name = spec.name

    try:
        pdf_bytes = cert_svc.generate_pdf(
            cert_request=body,
            metrics=metrics,
            ethics=ethics_data,
            specialty_name=specialty_name,
            model_type=data["model_type"],
        )
    except Exception as exc:
        logger.exception("Certificate generation failed")
        raise HTTPException(status_code=500, detail=str(exc))

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="ml_certificate_{body.model_id[:8]}.pdf"'},
    )
