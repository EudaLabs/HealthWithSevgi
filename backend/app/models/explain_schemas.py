"""Pydantic schemas for explainability, ethics, and certificate endpoints."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FeatureImportanceItem(BaseModel):
    """One row of global SHAP importance — feature name + mean |SHAP value|."""
    feature_name: str
    clinical_name: str
    importance: float
    direction: Literal["positive", "negative", "neutral"]
    clinical_note: str


class GlobalExplainabilityResponse(BaseModel):
    """
    Payload for `/api/explain/global-importance` — the ranked feature list with the method
    used (tree or kernel SHAP) and a textual description for the UI.
    """
    model_id: str
    method: str
    feature_importances: list[FeatureImportanceItem]
    top_feature_clinical_note: str
    explained_variance_pct: float


class SHAPWaterfallPoint(BaseModel):
    """
    Single bar in the per-patient SHAP waterfall: which feature pushed the probability in
    which direction and by how much.
    """
    feature_name: str
    clinical_name: str
    feature_value: float | str
    shap_value: float
    direction: Literal["increases_risk", "decreases_risk"]
    plain_language: str


class SinglePatientExplainResponse(BaseModel):
    """
    Payload for `/api/explain/single-patient` — base value, final prediction, and the
    ordered waterfall points.
    """
    model_id: str
    patient_index: int
    predicted_class: str
    predicted_probability: float
    base_value: float
    waterfall: list[SHAPWaterfallPoint]
    clinical_summary: str


class SubgroupMetrics(BaseModel):
    """
    Fairness metrics computed for one subgroup of a sensitive attribute (accuracy,
    sensitivity, specificity, PPV, NPV, etc.).
    """
    group_name: str
    group_label: str
    sample_size: int
    accuracy: float
    sensitivity: float
    specificity: float
    precision: float
    f1_score: float
    status: Literal["acceptable", "review", "action_needed"]
    status_reason: str = ""


class BiasWarning(BaseModel):
    """
    Machine-readable flag emitted when a subgroup metric falls outside the configured
    tolerance relative to the overall cohort.
    """
    detected: bool
    message: str
    affected_group: str
    metric: str
    gap: float


class CaseStudy(BaseModel):
    """
    One narrative case study from the ethics LLM pass — a real-world regulatory/clinical
    incident with a short lesson.
    """
    id: str
    title: str
    specialty: str
    year: int
    what_happened: str
    impact: str
    lesson: str
    severity: Literal["failure", "near_miss", "prevention"]


class RepresentationWarning(BaseModel):
    """Flags a demographic group whose training-data proportion differs
    from the population norm by more than the configured threshold."""

    group: str
    attribute: str
    dataset_pct: float
    population_pct: float
    gap_pp: float
    message: str


class EthicsResponse(BaseModel):
    """
    Payload for `/api/explain/ethics` — overall metrics, subgroup breakdowns, warnings,
    LLM narrative, and the EU AI Act checklist state.
    """
    model_id: str
    subgroup_metrics: list[SubgroupMetrics]
    bias_warnings: list[BiasWarning]
    training_representation: dict
    representation_warnings: list[RepresentationWarning] = Field(default_factory=list)
    overall_sensitivity: float
    eu_ai_act_items: list[dict]
    case_studies: list[CaseStudy]
    demographics_available: bool = True
    demographics_note: str = ""


class WhatIfRequest(BaseModel):
    """Request body for `/api/explain/what-if` — the patient vector plus the feature/value edits to probe."""
    model_id: str
    patient_index: int
    feature_name: str
    new_value: float


class WhatIfResponse(BaseModel):
    """
    Response for `/api/explain/what-if` — probability delta and the explanatory SHAP
    waterfall after the edit.
    """
    feature_name: str
    original_value: float
    new_value: float
    original_prob: float
    new_prob: float
    shift: float
    direction: Literal["increased_risk", "decreased_risk", "no_change"]


class ChecklistUpdate(BaseModel):
    """Toggle payload used to persist a single EU AI Act checklist item for the active session."""
    model_id: str
    item_id: str
    checked: bool


class SamplePatient(BaseModel):
    """
    A single patient row picked from the trained dataset for use in Step 6 explainability
    or Step 7 ethics demos.
    """
    index: int
    risk_level: Literal["low", "medium", "high"]
    probability: float
    summary: str


class SamplePatientsResponse(BaseModel):
    """Wraps a small list of `SamplePatient` rows used to seed the Step 6 "single patient" picker."""
    model_id: str
    patients: list[SamplePatient]


class CertificateRequest(BaseModel):
    """
    Request body for `/api/explain/certificate` — the session id plus user-selected
    checklist items to embed in the EU AI Act PDF.
    """
    model_id: str
    session_id: str
    checklist_state: dict[str, bool] = Field(default_factory=dict)
    clinician_name: str = "Healthcare Professional"
    institution: str = "Healthcare Institution"
