"""Pydantic schemas for Model Arena."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.models.ml_schemas import MetricsResponse, ModelType


class ArenaModelConfig(BaseModel):
    """One model to train in a batch."""
    model_type: ModelType
    params: dict[str, Any] = Field(default_factory=dict)
    tune: bool = False
    use_feature_selection: bool = False


class BatchTrainRequest(BaseModel):
    """Request to train multiple models on the same session."""
    session_id: str
    models: list[ArenaModelConfig] = Field(..., min_length=1, max_length=8)


class ArenaRun(BaseModel):
    """A single trained model run in the arena."""
    run_id: str
    model_id: str
    model_type: ModelType
    params: dict[str, Any]
    metrics: MetricsResponse | None = None  # None for failed runs
    training_time_ms: float
    feature_names: list[str]
    status: Literal["completed", "failed"] = "completed"
    error: str | None = None


class BatchTrainResponse(BaseModel):
    """Response from batch training."""
    session_id: str
    runs: list[ArenaRun]
    total_training_time_ms: float
    best_run_id: str | None = None


class ArenaCompareRequest(BaseModel):
    """Request to compare specific runs."""
    run_ids: list[str] = Field(..., min_length=2, max_length=8)

    @field_validator("run_ids")
    @classmethod
    def no_duplicates(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("run_ids must be unique")
        return v


class ArenaCompareResponse(BaseModel):
    """Comparison data for selected runs."""
    runs: list[ArenaRun]
    best_run_id: str
    metric_summary: dict[str, dict[str, float]]  # metric_name -> {run_id: value}
    param_diff: dict[str, dict[str, Any]]  # param_name -> {run_id: value} (only differing params)
