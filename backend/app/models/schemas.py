"""Pydantic schemas for data exploration and preparation endpoints."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SpecialtyInfo(BaseModel):
    """Descriptor for one of the 20 medical specialties — id, name, category, blurb, dataset pointers."""
    id: str
    name: str
    description: str
    target_variable: str
    target_type: Literal["binary", "multiclass"]
    feature_names: list[str]
    clinical_context: str
    data_source: str
    what_ai_predicts: str
    license_type: str = ""
    license_url: str = ""
    requires_attribution: bool = False


class ColumnStat(BaseModel):
    """
    Per-column summary computed during exploration (dtype, missing %, min/max/mean for
    numeric, top categories for categorical).
    """
    name: str
    dtype: str
    missing_count: int
    missing_pct: float
    unique_count: int
    sample_values: list[Any]


class DataExplorationResponse(BaseModel):
    """
    Response for `/api/data/explore` — column stats, row count, warnings, and the detected
    target column.
    """
    columns: list[ColumnStat]
    row_count: int
    class_distribution: dict[str, int]
    imbalance_warning: bool
    imbalance_ratio: float
    target_col: str


class PrepSettings(BaseModel):
    """
    Step-3 preparation settings (test split, normalisation, missing-value handling, SMOTE
    flag, outlier treatment).
    """
    test_size: float = Field(0.2, ge=0.1, le=0.4)
    missing_strategy: Literal["median", "mode", "drop"] = "median"
    normalization: Literal["zscore", "minmax", "none"] = "zscore"
    use_smote: bool = False
    outlier_handling: Literal["none", "iqr", "zscore_clip"] = "none"


class PrepResponse(BaseModel):
    """Response for `/api/data/prepare` — session id, train/test shapes, and any applied transformations."""
    session_id: str
    train_size: int
    test_size: int
    features_count: int
    class_distribution_before: dict[str, int]
    class_distribution_after: dict[str, int]
    smote_applied: bool
    normalization_applied: str
    norm_samples: list[dict[str, object]] = Field(default_factory=list)  # [{feature, before, after}, ...]
