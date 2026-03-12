"""Pydantic schemas for ML training and evaluation endpoints."""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ModelType(str, Enum):
    KNN = "knn"
    SVM = "svm"
    DECISION_TREE = "decision_tree"
    RANDOM_FOREST = "random_forest"
    LOGISTIC_REGRESSION = "logistic_regression"
    NAIVE_BAYES = "naive_bayes"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"


class KNNParams(BaseModel):
    n_neighbors: int = Field(5, ge=1, le=25)
    metric: Literal["euclidean", "manhattan"] = "euclidean"


class SVMParams(BaseModel):
    kernel: Literal["linear", "rbf", "poly", "sigmoid"] = "rbf"
    C: float = Field(1.0, ge=0.01, le=100.0)


class DecisionTreeParams(BaseModel):
    max_depth: int = Field(5, ge=1, le=20)
    criterion: Literal["gini", "entropy"] = "gini"


class RandomForestParams(BaseModel):
    n_estimators: int = Field(100, ge=10, le=500)
    max_depth: int = Field(5, ge=1, le=20)


class LogisticRegressionParams(BaseModel):
    C: float = Field(1.0, ge=0.001, le=100.0)
    max_iter: int = Field(200, ge=50, le=2000)


class NaiveBayesParams(BaseModel):
    var_smoothing: float = Field(1e-9, ge=1e-12, le=1e-3)


class XGBoostParams(BaseModel):
    n_estimators: int = Field(100, ge=10, le=500)
    max_depth: int = Field(5, ge=1, le=15)
    learning_rate: float = Field(0.1, ge=0.01, le=0.5)


class LightGBMParams(BaseModel):
    n_estimators: int = Field(100, ge=10, le=500)
    max_depth: int = Field(-1, ge=-1, le=15)
    learning_rate: float = Field(0.1, ge=0.01, le=0.5)


class TrainRequest(BaseModel):
    session_id: str
    model_type: ModelType
    params: dict[str, Any] = Field(default_factory=dict)
    tune: bool = False
    use_feature_selection: bool = False


class ConfusionMatrixData(BaseModel):
    tn: int = 0
    fp: int = 0
    fn: int = 0
    tp: int = 0
    matrix: list[list[int]]
    labels: list[str]


class ROCPoint(BaseModel):
    fpr: float
    tpr: float
    threshold: float


class MetricsResponse(BaseModel):
    accuracy: float
    sensitivity: float
    specificity: float
    precision: float
    f1_score: float
    auc_roc: float
    confusion_matrix: ConfusionMatrixData
    roc_curve: list[ROCPoint]
    pr_curve: list[dict[str, float]]
    train_accuracy: float
    cross_val_scores: list[float]
    low_sensitivity_warning: bool
    mcc: float = 0.0
    overfitting_warning: bool = False


class TrainResponse(BaseModel):
    model_id: str
    session_id: str
    model_type: ModelType
    params: dict[str, Any]
    metrics: MetricsResponse
    training_time_ms: float
    feature_names: list[str]


class CompareEntry(BaseModel):
    model_id: str
    model_type: ModelType
    params: dict[str, Any]
    metrics: MetricsResponse
    training_time_ms: float


class CompareResponse(BaseModel):
    entries: list[CompareEntry]
    best_model_id: str
