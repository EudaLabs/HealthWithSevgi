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
        request.app.state.insight_service,
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
    ml, _, ethics, _, _ = _get_services(request)
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
    _, _, ethics, _, _ = _get_services(request)
    return ethics.update_checklist(body.model_id, body.item_id, body.checked)


@router.get("/insights/{model_id}")
async def get_insights(request: Request, model_id: str) -> dict:
    """Generate LLM-powered clinical insights for a trained model."""
    import asyncio
    import numpy as np

    ml, explain, ethics, _, insight_svc = _get_services(request)
    data = _get_model_data(ml, model_id)

    metrics = data.get("metrics")
    if metrics is None:
        raise HTTPException(status_code=422, detail="Model metrics not available.")

    # --- Gather all data sources ---
    ethics_data = ethics.analyze_bias(
        model_id=model_id,
        model=data["model"],
        X_test=data["X_test"],
        y_test=data["y_test"],
        feature_names=data["feature_names"],
        classes=data["classes"],
        X_train=data["X_train"],
        scaler=data.get("scaler"),
    )

    # SHAP / Feature importance (non-blocking, best-effort)
    shap_data = None
    try:
        shap_data = explain.global_importance(
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
        logger.warning("SHAP for insights failed: %s", exc)

    # Specialty metadata
    session_id = data.get("session_id", "")
    ml_session = ml.get_session(session_id)
    specialty_info = None
    if ml_session:
        from app.services.specialty_registry import SPECIALTIES
        specialty_info = SPECIALTIES.get(ml_session.get("specialty_id", ""))

    def _m(attr: str):
        return getattr(metrics, attr, None) if hasattr(metrics, attr) else metrics.get(attr)

    # Confusion matrix
    cm_summary = {}
    cm_data = _m("confusion_matrix")
    if cm_data and hasattr(cm_data, "matrix"):
        matrix = cm_data.matrix
        if len(matrix) == 2:
            cm_summary = {"TN": matrix[0][0], "FP": matrix[0][1], "FN": matrix[1][0], "TP": matrix[1][1]}
        else:
            cm_summary = {"matrix_size": f"{len(matrix)}x{len(matrix)}", "classes": data["classes"]}

    # Class distribution
    class_dist = {}
    if ml_session:
        y_train = ml_session.get("y_train")
        if y_train is not None:
            unique, counts = np.unique(y_train, return_counts=True)
            classes_list = data["classes"]
            class_dist = {
                classes_list[int(u)] if int(u) < len(classes_list) else str(u): int(c)
                for u, c in zip(unique, counts)
            }

    # Feature importance from SHAP
    feature_importance_data = []
    if shap_data:
        for fi in shap_data.feature_importances[:10]:  # top 10
            feature_importance_data.append({
                "feature": fi.feature_name,
                "clinical_name": fi.clinical_name,
                "importance": round(fi.importance, 4),
                "direction": fi.direction,
                "clinical_note": fi.clinical_note,
            })

    cv_scores = _m("cross_val_scores") or []

    context = {
        # Specialty & clinical domain
        "specialty_name": specialty_info.name if specialty_info else "Unknown",
        "what_ai_predicts": specialty_info.what_ai_predicts if specialty_info else "clinical outcome",
        "clinical_context": specialty_info.clinical_context if specialty_info else "",
        "target_variable": specialty_info.target_variable if specialty_info else "target",
        "data_source": specialty_info.data_source if specialty_info else "unknown",
        # Model info
        "model_type": data["model_type"].value.replace("_", " ").title() if hasattr(data.get("model_type"), "value") else str(data.get("model_type", "unknown")),
        "model_params": data.get("params", {}),
        "training_time_ms": data.get("training_time_ms"),
        # Dataset info
        "feature_names": data["feature_names"],
        "classes": data["classes"],
        "train_size": len(data["X_train"]),
        "test_size": len(data["X_test"]),
        "class_distribution_train": class_dist,
        "use_smote": ml_session.get("smote_applied", False) if ml_session else False,
        "normalization": ml_session.get("normalization", "N/A") if ml_session else "N/A",
        # Performance metrics
        "accuracy": _m("accuracy"),
        "sensitivity": _m("sensitivity"),
        "specificity": _m("specificity"),
        "precision": _m("precision"),
        "f1_score": _m("f1_score"),
        "auc_roc": _m("auc_roc"),
        "mcc": _m("mcc"),
        "train_accuracy": _m("train_accuracy"),
        "cv_scores": cv_scores,
        "cv_mean": float(sum(cv_scores) / max(len(cv_scores), 1)),
        "cv_std": float(np.std(cv_scores)) if cv_scores else 0.0,
        "overfitting_warning": _m("overfitting_warning"),
        "optimal_threshold": _m("optimal_threshold"),
        "low_sensitivity_warning": _m("low_sensitivity_warning"),
        "confusion_matrix": cm_summary,
        # Explainability / SHAP
        "shap_method": shap_data.method if shap_data else "unavailable",
        "feature_importances": feature_importance_data,
        "top_feature_clinical_note": shap_data.top_feature_clinical_note if shap_data else "",
        "explained_variance_top5_pct": shap_data.explained_variance_pct if shap_data else 0,
        # Fairness data
        "overall_sensitivity": ethics_data.overall_sensitivity,
        "bias_warnings": [
            {"group": w.affected_group, "metric": w.metric, "gap": w.gap}
            for w in ethics_data.bias_warnings
        ],
        "subgroup_details": [
            {
                "group": sm.group_label,
                "sensitivity": sm.sensitivity,
                "accuracy": sm.accuracy,
                "specificity": sm.specificity,
                "precision": sm.precision,
                "f1_score": sm.f1_score,
                "sample_size": sm.sample_size,
                "status": sm.status,
                "status_reason": sm.status_reason,
            }
            for sm in ethics_data.subgroup_metrics
        ],
    }

    try:
        ethics_task = insight_svc.generate_ethics_insight(context)
        cases_task = insight_svc.generate_case_studies(context)
        ethics_result, cases_result = await asyncio.gather(ethics_task, cases_task)

        return {
            "ethics_insight": ethics_result,
            "case_studies": cases_result,
        }
    except Exception as exc:
        logger.exception("Insight generation failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-certificate")
def generate_certificate(request: Request, body: CertificateRequest) -> StreamingResponse:
    ml, _, ethics, cert_svc, _ = _get_services(request)
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
