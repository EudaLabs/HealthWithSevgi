"""Pydantic schemas for ML training and evaluation endpoints."""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ModelType(str, Enum):
    """Enum of the eight classifiers the backend can train."""
    KNN = "knn"
    SVM = "svm"
    DECISION_TREE = "decision_tree"
    RANDOM_FOREST = "random_forest"
    LOGISTIC_REGRESSION = "logistic_regression"
    NAIVE_BAYES = "naive_bayes"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"


class KNNParams(BaseModel):
    """Hyperparameters for K-Nearest-Neighbours (neighbour count, distance metric)."""
    n_neighbors: int = Field(5, ge=1, le=25)
    metric: Literal["euclidean", "manhattan"] = "euclidean"


class SVMParams(BaseModel):
    """Hyperparameters for Support Vector Machine (kernel, C, gamma)."""
    kernel: Literal["linear", "rbf", "poly", "sigmoid"] = "rbf"
    C: float = Field(1.0, ge=0.01, le=100.0)


class DecisionTreeParams(BaseModel):
    """Hyperparameters for a single Decision Tree (max depth, split criterion)."""
    max_depth: int = Field(5, ge=1, le=20)
    criterion: Literal["gini", "entropy"] = "gini"


class RandomForestParams(BaseModel):
    """Hyperparameters for Random Forest ensemble (n_estimators, max depth)."""
    n_estimators: int = Field(100, ge=10, le=500)
    max_depth: int = Field(5, ge=1, le=20)


class LogisticRegressionParams(BaseModel):
    """Hyperparameters for Logistic Regression (regularisation strength, penalty)."""
    C: float = Field(1.0, ge=0.001, le=100.0)
    max_iter: int = Field(200, ge=50, le=2000)


class NaiveBayesParams(BaseModel):
    """Hyperparameters for Gaussian Naive Bayes (variance smoothing)."""
    var_smoothing: float = Field(1e-9, ge=1e-12, le=1e-3)


class XGBoostParams(BaseModel):
    """Hyperparameters for XGBoost (n_estimators, max depth, learning rate)."""
    n_estimators: int = Field(100, ge=10, le=500)
    max_depth: int = Field(5, ge=1, le=15)
    learning_rate: float = Field(0.1, ge=0.01, le=0.5)


class LightGBMParams(BaseModel):
    """Hyperparameters for LightGBM (n_estimators, num_leaves, learning rate)."""
    n_estimators: int = Field(100, ge=10, le=500)
    max_depth: int = Field(-1, ge=-1, le=15)
    learning_rate: float = Field(0.1, ge=0.01, le=0.5)


PARAM_SCHEMAS: dict[str, type[BaseModel]] = {
    "knn": KNNParams,
    "svm": SVMParams,
    "decision_tree": DecisionTreeParams,
    "random_forest": RandomForestParams,
    "logistic_regression": LogisticRegressionParams,
    "naive_bayes": NaiveBayesParams,
    "xgboost": XGBoostParams,
    "lightgbm": LightGBMParams,
}


class TrainRequest(BaseModel):
    """Request body for `/api/ml/train` — session id + model type + its hyperparameter bundle."""
    session_id: str
    model_type: ModelType
    params: dict[str, Any] = Field(default_factory=dict)
    tune: bool = False
    use_feature_selection: bool = False

    @model_validator(mode='after')
    def validate_params(self) -> 'TrainRequest':
        """Cross-field validator ensuring the `params` object matches the chosen `model_type`."""
        schema = PARAM_SCHEMAS.get(self.model_type.value)
        if schema and self.params:
            try:
                validated = schema(**self.params)
                self.params = validated.model_dump()
            except Exception:
                pass  # Allow through with raw params; build_model has its own defaults
        return self


class ConfusionMatrixData(BaseModel):
    """Confusion matrix counts plus labels, ready for the Step-5 chart."""
    tn: int = 0
    fp: int = 0
    fn: int = 0
    tp: int = 0
    matrix: list[list[int]]
    labels: list[str]


class ROCPoint(BaseModel):
    """One threshold sample of the ROC curve (FPR, TPR, threshold)."""
    fpr: float
    tpr: float
    threshold: float


class MetricsResponse(BaseModel):
    """
    Bundle of evaluation metrics returned after a training run (accuracy, precision,
    recall, F1, AUC, confusion matrix, ROC/PR points).
    """
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
    optimal_threshold: float = 0.5


class ScatterPoint(BaseModel):
    """Single 2-D point used by the KNN scatter visualisation in Step 4."""
    x: float
    y: float
    label: int
    label_name: str
    split: str  # "train" or "test"
    predicted: int | None = None  # only for test points


class DecisionMesh(BaseModel):
    """Grid of predictions used to shade the KNN decision boundary in Step 4."""
    x_values: list[float]  # unique x coordinates of the grid
    y_values: list[float]  # unique y coordinates of the grid
    predictions: list[list[int]]  # 2D array [y][x] of predicted class indices


class KNNScatterData(BaseModel):
    """Bundle of scatter points + decision mesh shipped to the KNN visualisation."""
    scatter_points: list[ScatterPoint]
    decision_mesh: DecisionMesh
    pca_explained_variance: list[float]
    classes: list[str]
    k: int
    metric: str


class TrainResponse(BaseModel):
    """Complete payload returned by `/api/ml/train` — session id, model id, metrics, ROC/PR, scatter data."""
    model_id: str
    session_id: str
    model_type: ModelType
    params: dict[str, Any]
    metrics: MetricsResponse
    training_time_ms: float
    feature_names: list[str]
    knn_scatter: KNNScatterData | None = None


class CompareEntry(BaseModel):
    """A single model entry in the cross-model comparison list (Step 4 "Add to comparison")."""
    model_id: str
    model_type: ModelType
    params: dict[str, Any]
    metrics: MetricsResponse
    training_time_ms: float


class CompareResponse(BaseModel):
    """Response for `/api/ml/comparison` — the current list of compared models for the session."""
    entries: list[CompareEntry]
    best_model_id: str
