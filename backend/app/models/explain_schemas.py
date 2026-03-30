"""Pydantic schemas for explainability, ethics, and certificate endpoints."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FeatureImportanceItem(BaseModel):
    feature_name: str
    clinical_name: str
    importance: float
    direction: Literal["positive", "negative", "neutral"]
    clinical_note: str


class GlobalExplainabilityResponse(BaseModel):
    model_id: str
    method: str
    feature_importances: list[FeatureImportanceItem]
    top_feature_clinical_note: str
    explained_variance_pct: float


class SHAPWaterfallPoint(BaseModel):
    feature_name: str
    clinical_name: str
    feature_value: float | str
    shap_value: float
    direction: Literal["increases_risk", "decreases_risk"]
    plain_language: str


class SinglePatientExplainResponse(BaseModel):
    model_id: str
    patient_index: int
    predicted_class: str
    predicted_probability: float
    base_value: float
    waterfall: list[SHAPWaterfallPoint]
    clinical_summary: str


class SubgroupMetrics(BaseModel):
    group_name: str
    group_label: str
    sample_size: int
    accuracy: float
    sensitivity: float
    specificity: float
    precision: float
    f1_score: float
    status: Literal["acceptable", "review", "action_needed"]


class BiasWarning(BaseModel):
    detected: bool
    message: str
    affected_group: str
    metric: str
    gap: float


class CaseStudy(BaseModel):
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
    model_id: str
    patient_index: int
    feature_name: str
    new_value: float


class WhatIfResponse(BaseModel):
    feature_name: str
    original_value: float
    new_value: float
    original_prob: float
    new_prob: float
    shift: float
    direction: Literal["increased_risk", "decreased_risk", "no_change"]


class ChecklistUpdate(BaseModel):
    model_id: str
    item_id: str
    checked: bool


class CertificateRequest(BaseModel):
    model_id: str
    session_id: str
    checklist_state: dict[str, bool] = Field(default_factory=dict)
    clinician_name: str = "Healthcare Professional"
    institution: str = "Healthcare Institution"
