"""Pydantic schemas for data exploration and preparation endpoints."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SpecialtyInfo(BaseModel):
    id: str
    name: str
    description: str
    target_variable: str
    target_type: Literal["binary", "multiclass"]
    feature_names: list[str]
    clinical_context: str
    data_source: str
    what_ai_predicts: str


class ColumnStat(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_pct: float
    unique_count: int
    sample_values: list[Any]


class DataExplorationResponse(BaseModel):
    columns: list[ColumnStat]
    row_count: int
    class_distribution: dict[str, int]
    imbalance_warning: bool
    imbalance_ratio: float
    target_col: str


class PrepSettings(BaseModel):
    test_size: float = Field(0.2, ge=0.1, le=0.4)
    missing_strategy: Literal["median", "mode", "drop"] = "median"
    normalization: Literal["zscore", "minmax", "none"] = "zscore"
    use_smote: bool = False


class PrepResponse(BaseModel):
    session_id: str
    train_size: int
    test_size: int
    features_count: int
    class_distribution_before: dict[str, int]
    class_distribution_after: dict[str, int]
    smote_applied: bool
    normalization_applied: str
    norm_samples: list[dict[str, object]] = Field(default_factory=list)  # [{feature, before, after}, ...]
