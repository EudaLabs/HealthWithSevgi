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
    """FastAPI dependency — resolves data/ml/explain/ethics/insight/certificate services as a tuple."""
    return (
        request.app.state.ml_service,
        request.app.state.explain_service,
        request.app.state.ethics_service,
        request.app.state.certificate_service,
        request.app.state.insight_service,
    )


def _get_model_data(ml_service, model_id: str) -> dict:
    """Helper that pulls the trained model + split data for a session, raising 404 if absent."""
    data = ml_service.get_model(model_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found. Train a model first.")
    return data


@router.get("/explain/global/{model_id}", response_model=GlobalExplainabilityResponse)
def global_importance(request: Request, model_id: str) -> GlobalExplainabilityResponse:
    """Step-6 endpoint — computes global SHAP feature importance for the active model."""
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
    """Step-6 endpoint — returns a per-patient SHAP waterfall plus base/final probability."""
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
    """Step-6 endpoint — probes probability changes when specific feature values are altered."""
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
    """Step-6 helper — returns a handful of sample rows from the test split for quick picking."""
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
    """Step-7 endpoint — runs the bias audit and produces fairness deltas + warnings."""
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
    """Step-7 endpoint — toggles a single EU AI Act checklist item for the session."""
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
        """Inner helper used by `get_insights` to memoise the LLM call per task."""
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
        "raw_column_meta": ml_session.get("raw_column_meta", []) if ml_session else [],
        "row_count_original": ml_session.get("row_count", 0) if ml_session else 0,
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

    # Compared models (if user trained multiple models)
    compared_models = []
    if session_id:
        try:
            compare_data = ml.get_comparison(session_id)
            for entry in compare_data.entries:
                compared_models.append({
                    "model_type": entry.model_type.value.replace("_", " ").title(),
                    "model_id": entry.model_id,
                    "accuracy": entry.metrics.accuracy,
                    "sensitivity": entry.metrics.sensitivity,
                    "specificity": entry.metrics.specificity,
                    "auc_roc": entry.metrics.auc_roc,
                    "f1_score": entry.metrics.f1_score,
                    "mcc": entry.metrics.mcc,
                    "training_time_ms": entry.training_time_ms,
                })
        except Exception as exc:
            logger.warning("Comparison data unavailable: %s", exc)
    logger.info("Insights context: %d compared models", len(compared_models))
    context["compared_models"] = compared_models

    # Feature column statistics (distributions for clinical grounding)
    column_stats = []
    X_train = data["X_train"]
    for i, fname in enumerate(data["feature_names"]):
        col_info: dict[str, Any] = {"name": fname}
        try:
            col = X_train[:, i] if hasattr(X_train, "shape") else X_train.iloc[:, i]
            col_info["mean"] = round(float(np.mean(col)), 3)
            col_info["std"] = round(float(np.std(col)), 3)
            col_info["min"] = round(float(np.min(col)), 3)
            col_info["max"] = round(float(np.max(col)), 3)
        except Exception:
            pass
        column_stats.append(col_info)
    context["column_statistics"] = column_stats

    # Sample rows from test set (real patient data for LLM grounding)
    feature_names = data["feature_names"]
    classes = data["classes"]
    X_test = data["X_test"]
    y_test = data["y_test"]
    sample_rows = []
    n_samples = min(5, len(X_test))
    # Pick diverse samples: some positive, some negative
    try:
        pos_idx = [i for i in range(len(y_test)) if int(y_test[i]) == 1]
        neg_idx = [i for i in range(len(y_test)) if int(y_test[i]) == 0]
        pick = (pos_idx[:3] + neg_idx[:2])[:n_samples] if pos_idx and neg_idx else list(range(n_samples))
        for idx in pick:
            row = {}
            for j, fname in enumerate(feature_names):
                val = X_test[idx, j] if hasattr(X_test, "shape") else X_test.iloc[idx, j]
                row[fname] = round(float(val), 3)
            row["_actual_outcome"] = classes[int(y_test[idx])] if int(y_test[idx]) < len(classes) else str(y_test[idx])
            sample_rows.append(row)
    except Exception:
        pass
    context["sample_patients"] = sample_rows

    # EU AI Act static items for enrichment
    from app.services.ethics_service import EU_AI_ACT_ITEMS
    context["eu_ai_act_items"] = EU_AI_ACT_ITEMS

    try:
        ethics_task = insight_svc.generate_ethics_insight(context)
        cases_task = insight_svc.generate_case_studies(context)
        eu_act_task = insight_svc.generate_eu_ai_act_insights(context)
        ethics_result, cases_result, eu_act_result = await asyncio.gather(
            ethics_task, cases_task, eu_act_task
        )

        return {
            "ethics_insight": ethics_result,
            "case_studies": cases_result,
            "eu_ai_act_insights": eu_act_result,
        }
    except Exception as exc:
        logger.exception("Insight generation failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-certificate")
def generate_certificate(request: Request, body: CertificateRequest) -> StreamingResponse:
    """Step-7 endpoint — renders the EU AI Act compliance PDF via `CertificateService`."""
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
