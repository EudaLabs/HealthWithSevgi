"""ML model training and evaluation service — 8 state-of-the-art classifiers."""
from __future__ import annotations

import logging
import time
import uuid
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
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from app.models.ml_schemas import (
    CompareEntry,
    CompareResponse,
    ConfusionMatrixData,
    MetricsResponse,
    ModelType,
    ROCPoint,
    TrainResponse,
)

logger = logging.getLogger(__name__)

_SENSITIVITY_WARNING_THRESHOLD = 0.5

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
        self._session_store: dict[str, dict[str, Any]] = {}
        self._model_store: dict[str, Any] = {}
        self._compare_store: dict[str, list[CompareEntry]] = {}

    # ------------------------------------------------------------------
    # Session management (called by data service / router)
    # ------------------------------------------------------------------
    def store_session_data(self, session_id: str, data: dict[str, Any]) -> None:
        self._session_store[session_id] = data
        # Evict oldest sessions if store exceeds 50 entries
        if len(self._session_store) > 50:
            oldest_key = next(iter(self._session_store))
            del self._session_store[oldest_key]
        logger.info("ML session stored: %s", session_id)

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        return self._session_store.get(session_id)

    def get_model(self, model_id: str) -> Any | None:
        return self._model_store.get(model_id)

    # ------------------------------------------------------------------
    # Model construction
    # ------------------------------------------------------------------
    def build_model(self, model_type: ModelType, params: dict[str, Any]) -> Any:
        if model_type == ModelType.KNN:
            return KNeighborsClassifier(
                n_neighbors=params.get("n_neighbors", 5),
                metric=params.get("metric", "euclidean"),
                weights=params.get("weights", "distance"),
                algorithm="auto",
                n_jobs=-1,
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
                n_jobs=-1,
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
                    n_jobs=-1,
                    verbosity=0,
                )
            except ImportError:
                logger.warning("xgboost not installed, falling back to RandomForest")
                return RandomForestClassifier(n_estimators=100, max_depth=5, class_weight="balanced", n_jobs=-1, random_state=42)
        if model_type == ModelType.LIGHTGBM:
            try:
                from lightgbm import LGBMClassifier
                return LGBMClassifier(
                    n_estimators=params.get("n_estimators", 100),
                    max_depth=params.get("max_depth", -1),
                    learning_rate=params.get("learning_rate", 0.1),
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                    verbose=-1,
                )
            except ImportError:
                logger.warning("lightgbm not installed, falling back to RandomForest")
                return RandomForestClassifier(n_estimators=100, max_depth=5, class_weight="balanced", n_jobs=-1, random_state=42)
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
        session = self._session_store.get(session_id)
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

        # --- Optional hyperparameter tuning ---
        best_params = dict(params)
        if tune:
            param_grid = _PARAM_GRIDS.get(model_type.value, {})
            if param_grid:
                try:
                    scoring = "roc_auc" if is_binary else "roc_auc_ovr_weighted"
                    rs = RandomizedSearchCV(
                        self.build_model(model_type, params),
                        param_grid,
                        n_iter=20,
                        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
                        scoring=scoring,
                        n_jobs=-1,
                        random_state=42,
                        error_score=0.0,
                    )
                    rs.fit(X_train, y_train)
                    best_params = {**params, **rs.best_params_}
                    logger.info("Hyperparameter tuning best params: %s (AUC=%.3f)", rs.best_params_, rs.best_score_)
                except Exception as exc:
                    logger.warning("Hyperparameter tuning failed: %s — using defaults", exc)

        model = self.build_model(model_type, best_params)

        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        training_time_ms = (time.perf_counter() - t0) * 1000

        y_pred = model.predict(X_test)
        y_prob = self._predict_proba(model, X_test)
        train_pred = model.predict(X_train)
        train_accuracy = float(accuracy_score(y_train, train_pred))

        metrics = self._compute_metrics(y_test, y_pred, y_prob, classes, is_binary)
        metrics.train_accuracy = train_accuracy
        metrics.overfitting_warning = (train_accuracy - metrics.accuracy) > 0.10

        # --- Leak-free cross-validation using Pipeline on raw data ---
        # If feature selection changed shape, use transformed data for CV instead
        if use_feature_selection and X_train.shape[1] != X_train_raw.shape[1]:
            X_cv_full = np.vstack([X_train, X_test])
        else:
            X_cv_full = np.vstack([X_train_raw, X_test_raw])

        y_full = np.concatenate([y_train, y_test])
        cv_scoring = "roc_auc" if is_binary else "roc_auc_ovr_weighted"

        # Build pipeline based on normalization type
        if normalization == "zscore":
            pipe_scaler = StandardScaler()
        elif normalization == "minmax":
            pipe_scaler = MinMaxScaler()
        else:
            pipe_scaler = None

        if pipe_scaler is not None:
            cv_pipe = Pipeline([("scaler", pipe_scaler), ("model", self.build_model(model_type, best_params))])
        else:
            cv_pipe = Pipeline([("model", self.build_model(model_type, best_params))])

        # Use RepeatedStratifiedKFold for small datasets (<500), else StratifiedKFold
        if len(X_cv_full) < 500:
            cv_splitter: Any = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
        else:
            cv_splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        try:
            cv_scores = cross_val_score(
                cv_pipe, X_cv_full, y_full, cv=cv_splitter,
                scoring=cv_scoring, n_jobs=-1, error_score=0.0,
            )
            metrics.cross_val_scores = cv_scores.tolist()
        except Exception as exc:
            logger.warning("Cross-validation failed: %s", exc)
            metrics.cross_val_scores = []

        model_id = str(uuid.uuid4())
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

        # Evict oldest models if store exceeds 50 entries
        if len(self._model_store) > 50:
            oldest_key = next(iter(self._model_store))
            del self._model_store[oldest_key]

        logger.info(
            "Trained %s in %.1f ms — AUC=%.3f acc=%.3f (train_acc=%.3f) cv_mean=%.3f",
            model_type, training_time_ms, metrics.auc_roc, metrics.accuracy, train_accuracy,
            float(np.mean(metrics.cross_val_scores)) if metrics.cross_val_scores else 0.0,
        )

        return TrainResponse(
            model_id=model_id,
            session_id=session_id,
            model_type=model_type,
            params=best_params,
            metrics=metrics,
            training_time_ms=round(training_time_ms, 1),
            feature_names=selected_feature_names,
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
        return np.zeros((len(X), 2))

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
            n_classes = len(classes)
            y_bin = label_binarize(y_true, classes=list(range(n_classes)))
            if y_prob.shape[1] >= n_classes:
                return float(
                    roc_auc_score(y_bin, y_prob, multi_class="ovr", average="macro")
                )
        except Exception as exc:
            logger.warning("AUC computation failed: %s", exc)
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
                # Downsample to <=200 points
                idx = np.linspace(0, len(fpr) - 1, min(200, len(fpr)), dtype=int)
                return [
                    ROCPoint(fpr=round(float(fpr[i]), 4), tpr=round(float(tpr[i]), 4),
                             threshold=round(float(thresholds[min(i, len(thresholds)-1)]), 4))
                    for i in idx
                ]
        except Exception:
            pass
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
        except Exception:
            pass
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

        if session_id not in self._compare_store:
            self._compare_store[session_id] = []

        # Replace existing entry for same model_id
        self._compare_store[session_id] = [
            e for e in self._compare_store[session_id] if e.model_id != model_id
        ]
        self._compare_store[session_id].append(entry)

        entries = sorted(
            self._compare_store[session_id],
            key=lambda e: e.metrics.auc_roc,
            reverse=True,
        )
        best = entries[0].model_id if entries else model_id
        return CompareResponse(entries=entries, best_model_id=best)

    def get_comparison(self, session_id: str) -> CompareResponse:
        entries = self._compare_store.get(session_id, [])
        entries = sorted(entries, key=lambda e: e.metrics.auc_roc, reverse=True)
        best = entries[0].model_id if entries else ""
        return CompareResponse(entries=entries, best_model_id=best)

    def clear_comparison(self, session_id: str) -> None:
        self._compare_store.pop(session_id, None)

    def store_train_response_in_model(self, model_id: str, response: "TrainResponse") -> None:
        """Cache metrics inside model store so comparison can retrieve them."""
        if model_id in self._model_store:
            self._model_store[model_id]["metrics"] = response.metrics
            self._model_store[model_id]["training_time_ms"] = response.training_time_ms
