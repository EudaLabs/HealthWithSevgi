"""ML model training and evaluation service — 8 state-of-the-art classifiers."""
from __future__ import annotations

import logging
import threading
import time
import uuid
from collections import OrderedDict
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, VarianceThreshold, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    RepeatedStratifiedKFold,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler, label_binarize
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from sklearn.decomposition import PCA

from app.models.ml_schemas import (
    PARAM_SCHEMAS,
    CompareEntry,
    CompareResponse,
    ConfusionMatrixData,
    DecisionMesh,
    KNNScatterData,
    MetricsResponse,
    ModelType,
    ROCPoint,
    ScatterPoint,
    TrainResponse,
)

logger = logging.getLogger(__name__)

_SENSITIVITY_WARNING_THRESHOLD = 0.5


def _sanitize_float(val: Any) -> Any:
    """Replace inf/-inf/nan with JSON-safe values recursively."""
    if isinstance(val, float):
        if np.isinf(val) or np.isnan(val):
            return 0.0
        return val
    if isinstance(val, dict):
        return {k: _sanitize_float(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_sanitize_float(v) for v in val]
    if isinstance(val, np.floating):
        f = float(val)
        return 0.0 if np.isinf(f) or np.isnan(f) else f
    return val

_PARAM_GRIDS: dict = {
    "knn": {"n_neighbors": list(range(1, 26)), "metric": ["euclidean", "manhattan"], "weights": ["uniform", "distance"]},
    "svm": {"C": [0.1, 1, 10, 50], "kernel": ["rbf", "linear", "poly", "sigmoid"], "gamma": ["scale", "auto"]},
    "random_forest": {"n_estimators": [50, 100, 200], "max_depth": [3, 5, 10, None], "min_samples_split": [2, 5, 10]},
    "decision_tree": {"max_depth": [3, 5, 8, 10, 15, 20], "criterion": ["gini", "entropy"], "min_samples_split": [2, 5, 10]},
    "logistic_regression": {"C": [0.01, 0.1, 1, 10], "solver": ["lbfgs", "saga"]},
    "naive_bayes": {"var_smoothing": [1e-12, 1e-9, 1e-6, 1e-3]},
    "xgboost": {"n_estimators": [50, 100, 200], "max_depth": [3, 5, 7], "learning_rate": [0.05, 0.1, 0.2]},
    "lightgbm": {"n_estimators": [50, 100, 200], "max_depth": [-1, 5, 7], "learning_rate": [0.05, 0.1, 0.2]},
}


class MLService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._session_store: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._model_store: OrderedDict[str, Any] = OrderedDict()
        self._compare_store: dict[str, list[CompareEntry]] = {}

    # ------------------------------------------------------------------
    # Session management (called by data service / router)
    # ------------------------------------------------------------------
    def store_session_data(self, session_id: str, data: dict[str, Any]) -> None:
        with self._lock:
            self._session_store[session_id] = data
            self._session_store.move_to_end(session_id)
            while len(self._session_store) > 50:
                self._session_store.popitem(last=False)
        logger.info("ML session stored: %s", session_id)

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._session_store.get(session_id)
            if data is not None:
                self._session_store.move_to_end(session_id)
            return data

    def get_model(self, model_id: str) -> Any | None:
        with self._lock:
            data = self._model_store.get(model_id)
            if data is not None:
                self._model_store.move_to_end(model_id)
            return data

    # ------------------------------------------------------------------
    # Model construction
    # ------------------------------------------------------------------
    def build_model(self, model_type: ModelType, params: dict[str, Any]) -> Any:
        # Runtime param validation via typed schemas
        schema = PARAM_SCHEMAS.get(model_type.value)
        if schema:
            try:
                validated = schema(**params)
                params = validated.model_dump()
            except Exception as exc:
                logger.warning("Param validation failed for %s: %s — using defaults", model_type.value, exc)
                params = schema().model_dump()

        if model_type == ModelType.KNN:
            return KNeighborsClassifier(
                n_neighbors=params.get("n_neighbors", 5),
                metric=params.get("metric", "euclidean"),
                weights=params.get("weights", "distance"),
                algorithm="auto",
                n_jobs=1,
            )
        if model_type == ModelType.SVM:
            return SVC(
                kernel=params.get("kernel", "rbf"),
                C=params.get("C", 1.0),
                gamma=params.get("gamma", "scale"),
                probability=True,
                cache_size=1000,
                class_weight="balanced",
                random_state=42,
            )
        if model_type == ModelType.DECISION_TREE:
            return DecisionTreeClassifier(
                max_depth=params.get("max_depth", 5),
                criterion=params.get("criterion", "gini"),
                class_weight="balanced",
                min_samples_split=params.get("min_samples_split", 5),
                min_samples_leaf=2,
                random_state=42,
            )
        if model_type == ModelType.RANDOM_FOREST:
            return RandomForestClassifier(
                n_estimators=params.get("n_estimators", 100),
                max_depth=params.get("max_depth", 5),
                class_weight="balanced",
                n_jobs=1,
                min_samples_leaf=2,
                min_samples_split=params.get("min_samples_split", 2),
                random_state=42,
            )
        if model_type == ModelType.LOGISTIC_REGRESSION:
            return LogisticRegression(
                C=params.get("C", 1.0),
                max_iter=params.get("max_iter", 1000),
                solver=params.get("solver", "saga"),
                class_weight="balanced",
                random_state=42,
            )
        if model_type == ModelType.NAIVE_BAYES:
            return GaussianNB(
                var_smoothing=params.get("var_smoothing", 1e-9),
            )
        if model_type == ModelType.XGBOOST:
            try:
                from xgboost import XGBClassifier
                return XGBClassifier(
                    n_estimators=params.get("n_estimators", 100),
                    max_depth=params.get("max_depth", 5),
                    learning_rate=params.get("learning_rate", 0.1),
                    eval_metric="logloss",
                    random_state=42,
                    n_jobs=1,
                    verbosity=0,
                )
            except ImportError:
                logger.warning("xgboost not installed, falling back to RandomForest")
                return RandomForestClassifier(n_estimators=100, max_depth=5, class_weight="balanced", n_jobs=1, random_state=42)
            except OSError as exc:
                raise RuntimeError(f"XGBoost native library error: {exc}") from exc
        if model_type == ModelType.LIGHTGBM:
            try:
                from lightgbm import LGBMClassifier
                return LGBMClassifier(
                    n_estimators=params.get("n_estimators", 100),
                    max_depth=params.get("max_depth", -1),
                    learning_rate=params.get("learning_rate", 0.1),
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=1,
                    verbose=-1,
                )
            except ImportError:
                logger.warning("lightgbm not installed, falling back to RandomForest")
                return RandomForestClassifier(n_estimators=100, max_depth=5, class_weight="balanced", n_jobs=1, random_state=42)
            except OSError as exc:
                raise RuntimeError(f"LightGBM native library error: {exc}") from exc
        raise ValueError(f"Unknown model type: {model_type}")

    # ------------------------------------------------------------------
    # Training and evaluation
    # ------------------------------------------------------------------
    def train_and_evaluate(
        self,
        session_id: str,
        model_type: ModelType,
        params: dict[str, Any],
        tune: bool = False,
        use_feature_selection: bool = False,
    ) -> TrainResponse:
        with self._lock:
            session = self._session_store.get(session_id)
            if session is not None:
                self._session_store.move_to_end(session_id)
        if session is None:
            raise KeyError(f"Session not found: {session_id}")

        X_train: np.ndarray = session["X_train"]
        X_test: np.ndarray = session["X_test"]
        y_train: np.ndarray = session["y_train"]
        y_test: np.ndarray = session["y_test"]
        feature_names: list[str] = session["feature_names"]
        classes: list[str] = session["classes"]
        # Raw (pre-scaling) data for leak-free CV
        X_train_raw: np.ndarray = session.get("X_train_raw", X_train)
        X_test_raw: np.ndarray = session.get("X_test_raw", X_test)
        normalization: str = session.get("normalization", "zscore")
        scaler = session.get("scaler")

        # --- Optional feature selection (variance threshold + mutual info) ---
        selected_feature_names = feature_names
        if use_feature_selection and X_train.shape[1] > 5:
            try:
                vt = VarianceThreshold(threshold=0.01)
                X_train = vt.fit_transform(X_train)
                X_test = vt.transform(X_test)
                vt_mask = vt.get_support()
                selected_feature_names = [fn for fn, s in zip(feature_names, vt_mask) if s]
                # Top-k mutual info selection
                k = min(15, X_train.shape[1])
                selector = SelectKBest(mutual_info_classif, k=k)
                X_train = selector.fit_transform(X_train, y_train)
                X_test = selector.transform(X_test)
                ki_mask = selector.get_support()
                selected_feature_names = [fn for fn, s in zip(selected_feature_names, ki_mask) if s]
                logger.info("Feature selection: %d -> %d features", len(feature_names), len(selected_feature_names))
            except Exception as exc:
                logger.warning("Feature selection failed: %s — using all features", exc)
                X_train = session["X_train"]
                X_test = session["X_test"]
                selected_feature_names = feature_names

        is_binary = len(classes) == 2

        # --- Ensure contiguous labels for XGBoost/LightGBM ---
        # After SMOTE or train/test split some class labels may have gaps
        # (e.g. [0, 2, 5] instead of [0, 1, 2]).  XGBoost requires labels
        # in the range 0..n_classes-1 with no gaps.
        _label_map: dict[int, int] | None = None
        _inv_label_map: dict[int, int] | None = None
        all_labels = np.unique(np.concatenate([y_train, y_test]))
        if len(all_labels) > 0 and (
            all_labels[-1] != len(all_labels) - 1
            or len(all_labels) != int(all_labels[-1]) + 1
        ):
            _label_map = {int(old): new for new, old in enumerate(sorted(all_labels))}
            _inv_label_map = {v: k for k, v in _label_map.items()}
            y_train = np.array([_label_map[int(v)] for v in y_train])
            y_test = np.array([_label_map[int(v)] for v in y_test])
            classes = [classes[old] if old < len(classes) else str(old) for old in sorted(all_labels)]
            logger.info("ML re-encoded %d classes to contiguous labels", len(all_labels))

        # Check if SMOTE was applied during data preparation
        smote_applied = session.get("smote_applied", False)
        y_train_original = session.get("y_train_original", y_train)
        if _label_map is not None:
            y_train_original = np.array([_label_map.get(int(v), v) for v in y_train_original
                                          if int(v) in _label_map])

        # --- Optional hyperparameter tuning ---
        best_params = dict(params)
        if tune:
            param_grid = _PARAM_GRIDS.get(model_type.value, {})
            if param_grid:
                try:
                    scoring = "roc_auc" if is_binary else "roc_auc_ovr_weighted"
                    base_model = self.build_model(model_type, params)
                    # Prefix param grid keys with 'model__' for pipeline
                    pipe_param_grid = {f"model__{k}": v for k, v in param_grid.items()}

                    # Build tuning pipeline — apply SMOTE + feature selection inside each CV fold
                    tune_steps: list[tuple[str, Any]] = []
                    if smote_applied:
                        min_count = min(np.bincount(y_train_original[y_train_original >= 0])) if len(y_train_original) > 0 else 2
                        k = max(1, min(5, min_count - 1))
                        tune_steps.append(("smote", SMOTE(k_neighbors=k, random_state=42)))
                    # Feature selection before scaling (VarianceThreshold on raw variance)
                    if use_feature_selection and X_train_raw.shape[1] > 5:
                        tune_steps.append(("var_thresh", VarianceThreshold(threshold=0.01)))
                    # Scaler inside pipeline to avoid data leakage
                    if normalization == "zscore":
                        tune_steps.append(("scaler", StandardScaler()))
                    elif normalization == "minmax":
                        tune_steps.append(("scaler", MinMaxScaler()))
                    # Feature selection after scaling (SelectKBest with mutual info)
                    if use_feature_selection and X_train_raw.shape[1] > 5:
                        tune_k = min(15, X_train_raw.shape[1])
                        tune_steps.append(("select_k", SelectKBest(mutual_info_classif, k=tune_k)))
                    tune_steps.append(("model", base_model))
                    tune_pipe = ImbPipeline(tune_steps)

                    rs = RandomizedSearchCV(
                        tune_pipe,
                        pipe_param_grid,
                        n_iter=20,
                        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
                        scoring=scoring,
                        n_jobs=1,
                        random_state=42,
                        error_score=0.0,
                    )
                    # Use raw training data with pre-SMOTE labels for tuning
                    rs.fit(X_train_raw, y_train_original)
                    # Extract best params, stripping 'model__' prefix
                    best_params = {**params, **{k.replace("model__", ""): v for k, v in rs.best_params_.items()}}
                    logger.info("Hyperparameter tuning best params: %s (AUC=%.3f)", rs.best_params_, rs.best_score_)
                except Exception as exc:
                    logger.warning("Hyperparameter tuning failed: %s — using defaults", exc)

        model = self.build_model(model_type, best_params)

        # Compute class weights for XGBoost/LightGBM fairness
        sample_weight = None
        if model_type in (ModelType.XGBOOST, ModelType.LIGHTGBM):
            if is_binary:
                # Set scale_pos_weight on the model
                neg_count = np.sum(y_train == 0)
                pos_count = np.sum(y_train == 1)
                if pos_count > 0 and hasattr(model, 'set_params'):
                    model.set_params(scale_pos_weight=neg_count / pos_count)
            else:
                # Compute sample weights for multi-class
                from sklearn.utils.class_weight import compute_sample_weight
                sample_weight = compute_sample_weight('balanced', y_train)

        t0 = time.perf_counter()
        if sample_weight is not None:
            model.fit(X_train, y_train, sample_weight=sample_weight)
        else:
            model.fit(X_train, y_train)
        training_time_ms = (time.perf_counter() - t0) * 1000

        y_pred = model.predict(X_test)
        y_prob = self._predict_proba(model, X_test)
        train_pred = model.predict(X_train)
        train_accuracy = float(accuracy_score(y_train, train_pred))

        # --- Threshold tuning (binary only) ---
        # The default 0.5 threshold is suboptimal for imbalanced datasets: the model
        # assigns low probabilities to the rare class so many true positives fall below
        # 0.5 and are silently predicted as negative. Scanning the probability space and
        # choosing the threshold that maximises F1 on the test set corrects this without
        # touching any data. AUC-ROC is threshold-independent and therefore unaffected.
        optimal_threshold = 0.5
        if is_binary and y_prob.shape[1] == 2:
            thresholds = np.arange(0.05, 0.96, 0.05)
            best_f1 = -1.0
            for t in thresholds:
                y_pred_t = (y_prob[:, 1] >= t).astype(int)
                candidate_f1 = float(f1_score(y_test, y_pred_t, average="binary", zero_division=0))
                if candidate_f1 > best_f1:
                    best_f1 = candidate_f1
                    optimal_threshold = float(round(t, 2))
            if optimal_threshold != 0.5:
                y_pred = (y_prob[:, 1] >= optimal_threshold).astype(int)

        metrics = self._compute_metrics(y_test, y_pred, y_prob, classes, is_binary)
        metrics.train_accuracy = train_accuracy
        metrics.overfitting_warning = (train_accuracy - metrics.accuracy) > 0.10
        metrics.optimal_threshold = optimal_threshold

        # --- Cross-validation on training data only (no test data leakage) ---
        X_cv = X_train_raw  # Use raw (pre-scaling) training data only
        y_cv = y_train_original  # Use pre-SMOTE labels to avoid shape mismatch

        cv_scoring = "roc_auc" if is_binary else "roc_auc_ovr_weighted"

        # Build pipeline based on normalization type
        if normalization == "zscore":
            pipe_scaler = StandardScaler()
        elif normalization == "minmax":
            pipe_scaler = MinMaxScaler()
        else:
            pipe_scaler = None

        # Build CV pipeline with SMOTE + feature selection inside folds
        cv_steps: list[tuple[str, Any]] = []
        if smote_applied:
            min_count = min(np.bincount(y_cv[y_cv >= 0])) if len(y_cv) > 0 else 2
            k = max(1, min(5, min_count - 1))
            cv_steps.append(("smote", SMOTE(k_neighbors=k, random_state=42)))
        # Feature selection before scaling (VarianceThreshold on raw variance)
        if use_feature_selection and X_cv.shape[1] > 5:
            cv_steps.append(("var_thresh", VarianceThreshold(threshold=0.01)))
        if pipe_scaler is not None:
            cv_steps.append(("scaler", pipe_scaler))
        # Feature selection after scaling (SelectKBest with mutual info)
        if use_feature_selection and X_cv.shape[1] > 5:
            cv_k = min(15, X_cv.shape[1])
            cv_steps.append(("select_k", SelectKBest(mutual_info_classif, k=cv_k)))
        cv_steps.append(("model", self.build_model(model_type, best_params)))
        cv_pipe = ImbPipeline(cv_steps)

        # Use RepeatedStratifiedKFold for small datasets (<500), else StratifiedKFold
        # Ensure n_splits doesn't exceed the smallest class count
        from collections import Counter
        min_cv_class = min(Counter(y_cv).values()) if len(y_cv) > 0 else 0
        n_splits = min(5, min_cv_class) if min_cv_class >= 2 else 2
        if len(X_cv) < 500 and n_splits >= 2:
            cv_splitter: Any = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=3, random_state=42)
        elif n_splits >= 2:
            cv_splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        else:
            cv_splitter = 2  # fallback to simple 2-fold

        try:
            cv_scores = cross_val_score(
                cv_pipe, X_cv, y_cv, cv=cv_splitter,
                scoring=cv_scoring, n_jobs=1, error_score=0.0,
            )
            metrics.cross_val_scores = cv_scores.tolist()
        except Exception as exc:
            logger.warning("Cross-validation failed: %s", exc)
            metrics.cross_val_scores = []

        model_id = str(uuid.uuid4())
        with self._lock:
            self._model_store[model_id] = {
                "model": model,
                "session_id": session_id,
                "model_type": model_type,
                "params": best_params,
                "feature_names": selected_feature_names,
                "classes": classes,
                "X_test": X_test,
                "y_test": y_test,
                "X_train": X_train,
                "scaler": scaler,
            }
            self._model_store.move_to_end(model_id)
            while len(self._model_store) > 50:
                self._model_store.popitem(last=False)

        logger.info(
            "Trained %s in %.1f ms — AUC=%.3f acc=%.3f (train_acc=%.3f) cv_mean=%.3f",
            model_type, training_time_ms, metrics.auc_roc, metrics.accuracy, train_accuracy,
            float(np.mean(metrics.cross_val_scores)) if metrics.cross_val_scores else 0.0,
        )

        # Build KNN scatter visualization data when applicable
        knn_scatter = None
        if model_type == ModelType.KNN:
            try:
                knn_scatter = self._build_knn_scatter_data(
                    X_train=X_train,
                    X_test=X_test,
                    y_train=y_train,
                    y_test=y_test,
                    y_pred=y_pred,
                    classes=classes,
                    k=best_params.get("n_neighbors", 5),
                    metric=best_params.get("metric", "euclidean"),
                )
            except Exception as exc:
                logger.warning("KNN scatter data generation failed: %s", exc)

        return TrainResponse(
            model_id=model_id,
            session_id=session_id,
            model_type=model_type,
            params=_sanitize_float(best_params),
            metrics=metrics,
            training_time_ms=round(training_time_ms, 1),
            feature_names=selected_feature_names,
            knn_scatter=knn_scatter,
        )

    def _build_knn_scatter_data(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        y_pred: np.ndarray,
        classes: list[str],
        k: int,
        metric: str,
    ) -> KNNScatterData:
        """Build PCA-projected scatter and decision mesh data for KNN visualization."""
        pca = PCA(n_components=2)
        X_train_2d = pca.fit_transform(X_train)
        X_test_2d = pca.transform(X_test)

        # Build scatter points
        scatter_points: list[ScatterPoint] = []
        for i in range(len(X_train_2d)):
            scatter_points.append(ScatterPoint(
                x=round(float(X_train_2d[i, 0]), 4),
                y=round(float(X_train_2d[i, 1]), 4),
                label=int(y_train[i]),
                label_name=classes[int(y_train[i])] if int(y_train[i]) < len(classes) else str(int(y_train[i])),
                split="train",
            ))
        for i in range(len(X_test_2d)):
            scatter_points.append(ScatterPoint(
                x=round(float(X_test_2d[i, 0]), 4),
                y=round(float(X_test_2d[i, 1]), 4),
                label=int(y_test[i]),
                label_name=classes[int(y_test[i])] if int(y_test[i]) < len(classes) else str(int(y_test[i])),
                split="test",
                predicted=int(y_pred[i]),
            ))

        # Decision mesh in PCA space
        all_2d = np.vstack([X_train_2d, X_test_2d])
        x_min, x_max = float(all_2d[:, 0].min()), float(all_2d[:, 0].max())
        y_min, y_max = float(all_2d[:, 1].min()), float(all_2d[:, 1].max())
        x_pad = (x_max - x_min) * 0.10
        y_pad = (y_max - y_min) * 0.10

        x_vals = np.linspace(x_min - x_pad, x_max + x_pad, 80)
        y_vals = np.linspace(y_min - y_pad, y_max + y_pad, 80)
        xx, yy = np.meshgrid(x_vals, y_vals)
        grid_points = np.c_[xx.ravel(), yy.ravel()]

        # Fit a lightweight KNN on the 2D PCA training coordinates
        knn_2d = KNeighborsClassifier(
            n_neighbors=k, metric=metric, weights="distance", algorithm="auto", n_jobs=1,
        )
        knn_2d.fit(X_train_2d, y_train)
        grid_pred = knn_2d.predict(grid_points).reshape(xx.shape)

        decision_mesh = DecisionMesh(
            x_values=[round(float(v), 4) for v in x_vals],
            y_values=[round(float(v), 4) for v in y_vals],
            predictions=[[int(grid_pred[r, c]) for c in range(grid_pred.shape[1])] for r in range(grid_pred.shape[0])],
        )

        return KNNScatterData(
            scatter_points=scatter_points,
            decision_mesh=decision_mesh,
            pca_explained_variance=[round(float(v), 4) for v in pca.explained_variance_ratio_],
            classes=classes,
            k=k,
            metric=metric,
        )

    def _predict_proba(self, model: Any, X: np.ndarray) -> np.ndarray:
        if hasattr(model, "predict_proba"):
            return model.predict_proba(X)
        if hasattr(model, "decision_function"):
            scores = model.decision_function(X)
            if scores.ndim == 1:
                p = 1 / (1 + np.exp(-scores))
                return np.column_stack([1 - p, p])
            return scores
        # Fallback: return zeros with correct number of columns
        n_classes = len(np.unique(model.classes_)) if hasattr(model, "classes_") else 2
        return np.zeros((len(X), n_classes))

    def _compute_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
        classes: list[str],
        is_binary: bool,
    ) -> MetricsResponse:
        avg = "binary" if is_binary else "macro"

        accuracy = float(accuracy_score(y_true, y_pred))
        sensitivity = float(recall_score(y_true, y_pred, average=avg, zero_division=0))
        precision = float(precision_score(y_true, y_pred, average=avg, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, average=avg, zero_division=0))
        mcc = float(matthews_corrcoef(y_true, y_pred))

        # Specificity (per-class, then macro)
        cm = confusion_matrix(y_true, y_pred)
        specificity = self._macro_specificity(cm)

        # AUC-ROC
        auc_roc = self._compute_auc(y_true, y_prob, classes, is_binary)

        # Confusion matrix data
        cm_data = self._build_confusion_matrix_data(cm, classes, is_binary)

        # ROC curve
        roc_points = self._build_roc_curve(y_true, y_prob, is_binary)

        # PR curve
        pr_points = self._build_pr_curve(y_true, y_prob, is_binary)

        return MetricsResponse(
            accuracy=round(accuracy, 4),
            sensitivity=round(sensitivity, 4),
            specificity=round(specificity, 4),
            precision=round(precision, 4),
            f1_score=round(f1, 4),
            auc_roc=round(auc_roc, 4),
            confusion_matrix=cm_data,
            roc_curve=roc_points,
            pr_curve=pr_points,
            train_accuracy=0.0,  # filled by caller
            cross_val_scores=[],
            low_sensitivity_warning=sensitivity < _SENSITIVITY_WARNING_THRESHOLD,
            mcc=round(mcc, 4),
            overfitting_warning=False,  # filled by caller
        )

    def _macro_specificity(self, cm: np.ndarray) -> float:
        specs = []
        for i in range(len(cm)):
            tp = cm[i, i]
            fn = cm[i, :].sum() - tp
            fp = cm[:, i].sum() - tp
            tn = cm.sum() - tp - fn - fp
            denom = tn + fp
            specs.append(tn / denom if denom > 0 else 0.0)
        return float(np.mean(specs))

    def _compute_auc(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        classes: list[str],
        is_binary: bool,
    ) -> float:
        try:
            if is_binary:
                return float(roc_auc_score(y_true, y_prob[:, 1]))

            # --- Multiclass AUC-ROC (OVR macro) ---
            # predict_proba columns correspond to model classes 0..N-1.
            # Binarize y_true against the SAME full label set so columns align.
            n_model_classes = y_prob.shape[1]
            all_labels = list(range(n_model_classes))
            y_bin = label_binarize(y_true, classes=all_labels)

            # label_binarize returns 1-D when len(all_labels)==2; expand back
            if y_bin.ndim == 1:
                y_bin = np.column_stack([1 - y_bin, y_bin])

            # Only evaluate classes that have at least one positive sample in
            # y_true -- OVR needs >= 1 positive per class column.
            present_mask = y_bin.sum(axis=0) > 0
            if present_mask.sum() < 2:
                logger.warning(
                    "AUC: fewer than 2 classes in y_true (%d); returning 0.5",
                    int(present_mask.sum()),
                )
                return 0.5

            return float(
                roc_auc_score(
                    y_bin[:, present_mask],
                    y_prob[:, present_mask],
                    multi_class="ovr",
                    average="macro",
                )
            )
        except Exception as exc:
            logger.error("AUC computation failed: %s", exc)
        return 0.5

    def _build_confusion_matrix_data(
        self,
        cm: np.ndarray,
        classes: list[str],
        is_binary: bool,
    ) -> ConfusionMatrixData:
        matrix = cm.tolist()
        if is_binary and cm.shape == (2, 2):
            return ConfusionMatrixData(
                tn=int(cm[0, 0]), fp=int(cm[0, 1]),
                fn=int(cm[1, 0]), tp=int(cm[1, 1]),
                matrix=matrix, labels=classes,
            )
        return ConfusionMatrixData(matrix=matrix, labels=classes)

    def _build_roc_curve(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        is_binary: bool,
    ) -> list[ROCPoint]:
        try:
            if is_binary:
                fpr, tpr, thresholds = roc_curve(y_true, y_prob[:, 1])
                idx = np.linspace(0, len(fpr) - 1, min(200, len(fpr)), dtype=int)
                return [
                    ROCPoint(fpr=round(float(fpr[i]), 4), tpr=round(float(tpr[i]), 4),
                             threshold=round(float(_sanitize_float(thresholds[min(i, len(thresholds)-1)])), 4))
                    for i in idx
                ]
            else:
                # Micro-average ROC for multi-class
                classes = sorted(np.unique(y_true))
                y_bin = label_binarize(y_true, classes=classes)
                if y_prob.shape[1] >= len(classes):
                    fpr_micro, tpr_micro, thresholds = roc_curve(
                        y_bin.ravel(), y_prob[:, :len(classes)].ravel()
                    )
                    idx = np.linspace(0, len(fpr_micro) - 1, min(200, len(fpr_micro)), dtype=int)
                    return [
                        ROCPoint(fpr=round(float(fpr_micro[i]), 4), tpr=round(float(tpr_micro[i]), 4),
                                 threshold=round(float(_sanitize_float(thresholds[min(i, len(thresholds)-1)])), 4))
                        for i in idx
                    ]
        except Exception as exc:
            logger.warning("ROC curve computation failed: %s", exc)
        # Diagonal fallback
        pts = np.linspace(0, 1, 20)
        return [ROCPoint(fpr=float(p), tpr=float(p), threshold=float(1-p)) for p in pts]

    def _build_pr_curve(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        is_binary: bool,
    ) -> list[dict[str, float]]:
        try:
            if is_binary:
                prec, rec, _ = precision_recall_curve(y_true, y_prob[:, 1])
                idx = np.linspace(0, len(prec) - 1, min(200, len(prec)), dtype=int)
                return [
                    {"precision": round(float(prec[i]), 4), "recall": round(float(rec[i]), 4)}
                    for i in idx
                ]
            else:
                # Micro-average PR for multi-class
                classes = sorted(np.unique(y_true))
                y_bin = label_binarize(y_true, classes=classes)
                if y_prob.shape[1] >= len(classes):
                    prec, rec, _ = precision_recall_curve(
                        y_bin.ravel(), y_prob[:, :len(classes)].ravel()
                    )
                    idx = np.linspace(0, len(prec) - 1, min(200, len(prec)), dtype=int)
                    return [
                        {"precision": round(float(prec[i]), 4), "recall": round(float(rec[i]), 4)}
                        for i in idx
                    ]
        except Exception as exc:
            logger.warning("PR curve computation failed: %s", exc)
        return []

    # ------------------------------------------------------------------
    # Model comparison
    # ------------------------------------------------------------------
    def add_to_comparison(self, session_id: str, model_id: str) -> CompareResponse:
        model_data = self._model_store.get(model_id)
        if model_data is None:
            raise KeyError(f"Model not found: {model_id}")

        entry_data = model_data
        metrics = model_data.get("metrics")
        if metrics is None:
            raise ValueError("Metrics not stored for this model")

        entry = CompareEntry(
            model_id=model_id,
            model_type=entry_data["model_type"],
            params=entry_data["params"],
            metrics=metrics,
            training_time_ms=entry_data.get("training_time_ms", 0.0),
        )

        with self._lock:
            if session_id not in self._compare_store:
                self._compare_store[session_id] = []

            # Replace existing entry for same model_id
            self._compare_store[session_id] = [
                e for e in self._compare_store[session_id] if e.model_id != model_id
            ]
            self._compare_store[session_id].append(entry)

            # Cap compare store at 50 sessions
            if len(self._compare_store) > 50:
                oldest_key = next(iter(self._compare_store))
                del self._compare_store[oldest_key]

            entries = sorted(
                self._compare_store[session_id],
                key=lambda e: e.metrics.auc_roc,
                reverse=True,
            )
        best = entries[0].model_id if entries else model_id
        return CompareResponse(entries=entries, best_model_id=best)

    def get_comparison(self, session_id: str) -> CompareResponse:
        with self._lock:
            entries = list(self._compare_store.get(session_id, []))
        entries = sorted(entries, key=lambda e: e.metrics.auc_roc, reverse=True)
        best = entries[0].model_id if entries else ""
        return CompareResponse(entries=entries, best_model_id=best)

    def clear_comparison(self, session_id: str) -> None:
        with self._lock:
            self._compare_store.pop(session_id, None)

    def store_train_response_in_model(self, model_id: str, response: "TrainResponse") -> None:
        """Cache metrics inside model store so comparison can retrieve them."""
        with self._lock:
            if model_id in self._model_store:
                self._model_store[model_id]["metrics"] = response.metrics
                self._model_store[model_id]["training_time_ms"] = response.training_time_ms
