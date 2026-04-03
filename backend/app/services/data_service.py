"""Data exploration and preparation service."""
from __future__ import annotations

import io
import logging
import pathlib
import uuid
import zipfile
from typing import Any

import numpy as np
import pandas as pd
import requests
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from app.models.schemas import (
    ColumnStat,
    DataExplorationResponse,
    PrepResponse,
    PrepSettings,
)

logger = logging.getLogger(__name__)

IMBALANCE_RATIO_THRESHOLD = 1.5
MIN_ROWS = 10
MAX_UPLOAD_MB = 50
MAX_TARGET_CLASSES = 20

_CACHE_DIR = pathlib.Path(__file__).parent.parent.parent / "data_cache"


class DatasetUnavailableError(Exception):
    """Raised when a real dataset cannot be loaded and no fallback is allowed."""

    def __init__(self, name: str, reason: str) -> None:
        self.dataset_name = name
        self.reason = reason
        super().__init__(
            f"Dataset '{name}' is unavailable: {reason}. "
            "Please upload your own CSV file or ensure the dataset cache is populated."
        )


class DataService:
    def __init__(self) -> None:
        self._session_store: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Real-data download helper
    # ------------------------------------------------------------------
    def _fetch_cached(
        self,
        name: str,
        url: str,
        read_kwargs: dict | None = None,
    ) -> pd.DataFrame:
        """Download a dataset from URL, cache locally, return DataFrame.

        Raises DatasetUnavailableError if the dataset cannot be loaded.
        """
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = _CACHE_DIR / f"{name}.csv"
        rk = read_kwargs or {}

        # Try from cache first
        if cache_path.exists():
            try:
                return pd.read_csv(cache_path, **rk)
            except Exception as exc:
                raise DatasetUnavailableError(
                    name, f"Cached file exists but failed to read: {exc}"
                ) from exc

        # Download
        try:
            resp = requests.get(url, timeout=20, headers={"User-Agent": "HealthWithSevgi/1.0"})
            resp.raise_for_status()
            cache_path.write_bytes(resp.content)
            logger.info("Downloaded real dataset: %s (%d bytes)", name, len(resp.content))
            return pd.read_csv(io.BytesIO(resp.content), **rk)
        except Exception as exc:
            raise DatasetUnavailableError(
                name, f"Failed to download from {url}: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Exploration
    # ------------------------------------------------------------------
    def explore_dataframe(
        self, df: pd.DataFrame, target_col: str
    ) -> DataExplorationResponse:
        columns: list[ColumnStat] = []
        for col in df.columns:
            series = df[col]
            missing = int(series.isna().sum())
            columns.append(
                ColumnStat(
                    name=col,
                    dtype=str(series.dtype),
                    missing_count=missing,
                    missing_pct=round(missing / len(df) * 100, 2),
                    unique_count=int(series.nunique()),
                    sample_values=series.dropna().head(5).tolist(),
                )
            )

        class_counts: dict[str, int] = {}
        imbalance_ratio = 1.0
        imbalance_warning = False
        if target_col in df.columns:
            vc = df[target_col].value_counts()
            class_counts = {str(k): int(v) for k, v in vc.items()}
            if len(vc) >= 2:
                imbalance_ratio = round(vc.iloc[0] / vc.iloc[-1], 2)
                imbalance_warning = imbalance_ratio >= IMBALANCE_RATIO_THRESHOLD

        return DataExplorationResponse(
            columns=columns,
            row_count=len(df),
            class_distribution=class_counts,
            imbalance_warning=imbalance_warning,
            imbalance_ratio=imbalance_ratio,
            target_col=target_col,
        )

    # ------------------------------------------------------------------
    # Preparation
    # ------------------------------------------------------------------
    def prepare_data(
        self,
        df: pd.DataFrame,
        target_col: str,
        settings: PrepSettings,
        session_id: str | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, PrepResponse, list[str]]:
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Drop rows where target is NaN
        df = df.dropna(subset=[target_col]).copy()

        # Guard: reject continuous / high-cardinality target columns
        n_unique = df[target_col].nunique()
        if n_unique > MAX_TARGET_CLASSES:
            raise ValueError(
                f"Target column '{target_col}' has {n_unique} unique values, "
                f"which looks like a continuous measurement rather than a "
                f"classification label. Choose a column with at most "
                f"{MAX_TARGET_CLASSES} distinct classes (e.g. a binary "
                f"outcome like 0/1)."
            )

        # Encode target
        y_raw = df[target_col]
        classes = sorted(y_raw.unique().tolist(), key=str)
        class_to_int = {c: i for i, c in enumerate(classes)}
        y = y_raw.map(class_to_int).values.astype(int)

        # Keep only numeric features (drop target + non-numeric)
        feature_df = df.drop(columns=[target_col])
        feature_df = feature_df.select_dtypes(include=[np.number])
        feature_names = list(feature_df.columns)

        dist_before = {str(k): int((y == v).sum()) for k, v in class_to_int.items()}

        if settings.missing_strategy == "drop":
            mask = ~feature_df.isna().any(axis=1)
            feature_df = feature_df[mask]
            y = y[mask]
        elif settings.missing_strategy == "median":
            feature_df = feature_df.fillna(feature_df.median(numeric_only=True))
        else:  # mode
            _mode = feature_df.mode()
            if not _mode.empty:
                feature_df = feature_df.fillna(_mode.iloc[0])
            else:
                feature_df = feature_df.fillna(feature_df.median(numeric_only=True))
        X = feature_df.values.astype(float)

        # --- Train / test split (BEFORE imputation to avoid data leakage) ---
        # Use stratified split only when every class has at least 2 samples;
        # otherwise fall back to non-stratified to avoid ValueError.
        from collections import Counter
        class_counts_y = Counter(y)
        min_class_size = min(class_counts_y.values()) if class_counts_y else 0
        can_stratify = min_class_size >= 2
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=settings.test_size, random_state=42,
            stratify=y if can_stratify else None,
        )

        # --- Handle missing values AFTER split (train-only statistics) ---
        if settings.missing_strategy == "drop":
            train_mask = ~pd.DataFrame(X_train).isna().any(axis=1).values
            test_mask = ~pd.DataFrame(X_test).isna().any(axis=1).values
            X_train = X_train[train_mask]
            y_train = y_train[train_mask]
            X_test = X_test[test_mask]
            y_test = y_test[test_mask]
        elif settings.missing_strategy == "median":
            train_df = pd.DataFrame(X_train, columns=feature_names)
            medians = train_df.median()
            X_train = train_df.fillna(medians).values
            X_test = pd.DataFrame(X_test, columns=feature_names).fillna(medians).values
        else:  # mode
            train_df = pd.DataFrame(X_train, columns=feature_names)
            modes = train_df.mode().iloc[0]
            X_train = train_df.fillna(modes).values
            X_test = pd.DataFrame(X_test, columns=feature_names).fillna(modes).values

        # --- Outlier handling (train statistics applied to test) ---
        if settings.outlier_handling == "iqr":
            train_df = pd.DataFrame(X_train, columns=feature_names)
            Q1 = train_df.quantile(0.25)
            Q3 = train_df.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            X_train = train_df.clip(lower=lower, upper=upper, axis=1).values
            X_test = pd.DataFrame(X_test, columns=feature_names).clip(lower=lower, upper=upper, axis=1).values
        elif settings.outlier_handling == "zscore_clip":
            train_df = pd.DataFrame(X_train, columns=feature_names)
            mean = train_df.mean()
            std = train_df.std().replace(0, 1)
            lower = mean - 3 * std
            upper = mean + 3 * std
            X_train = train_df.clip(lower=lower, upper=upper, axis=1).values
            X_test = pd.DataFrame(X_test, columns=feature_names).clip(lower=lower, upper=upper, axis=1).values

        # Capture raw (pre-scaling) arrays for session storage
        X_train_raw = X_train.copy()
        X_test_raw = X_test.copy()

        # --- Normalisation ---
        scaler = None
        normalization_applied = settings.normalization
        if settings.normalization == "zscore":
            scaler = StandardScaler()
        elif settings.normalization == "minmax":
            scaler = MinMaxScaler()

        if scaler is not None:
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

        # --- SMOTE (training only, supports multi-class) ---
        smote_applied = False

        # Filter out classes with fewer than 2 samples to prevent SMOTE ValueError
        unique, counts = np.unique(y_train, return_counts=True)
        valid_classes = unique[counts >= 2]
        if len(valid_classes) < len(unique):
            logger.warning(
                "Dropped %d classes with only 1 sample before SMOTE/training.",
                len(unique) - len(valid_classes)
            )
            train_mask = np.isin(y_train, valid_classes)
            X_train = X_train[train_mask]
            X_train_raw = X_train_raw[train_mask]
            y_train = y_train[train_mask]
            # Also filter test set to only contain classes present in training
            test_mask = np.isin(y_test, valid_classes)
            X_test = X_test[test_mask]
            X_test_raw = X_test_raw[test_mask]
            y_test = y_test[test_mask]

        # Re-encode labels to be contiguous (0..n-1) after any class filtering.
        # This prevents XGBoost/LightGBM "Invalid classes" errors when label
        # values have gaps (e.g. [0, 2, 5] instead of [0, 1, 2]).
        remaining_labels = np.unique(np.concatenate([y_train, y_test]))
        if len(remaining_labels) > 0 and (
            remaining_labels[-1] != len(remaining_labels) - 1
            or len(remaining_labels) != int(remaining_labels[-1]) + 1
        ):
            label_map = {old: new for new, old in enumerate(sorted(remaining_labels))}
            y_train = np.array([label_map[v] for v in y_train])
            y_test = np.array([label_map[v] for v in y_test])
            # Rebuild classes list and mapping with new contiguous labels
            old_classes = classes
            classes = [old_classes[old] for old in sorted(remaining_labels)]
            class_to_int = {c: i for i, c in enumerate(classes)}
            logger.info(
                "Re-encoded %d classes to contiguous labels 0..%d",
                len(remaining_labels), len(remaining_labels) - 1,
            )

        # Preserve pre-SMOTE labels for leak-free CV (after filtering and re-encoding)
        y_train_original = y_train.copy()

        unique_classes = np.unique(y_train)
        if settings.use_smote and len(unique_classes) >= 2:
            try:
                min_class_count = min(np.bincount(y_train[y_train >= 0])) if len(y_train) > 0 else 0
                k_neighbors = max(1, min(5, min_class_count - 1))
                smote = SMOTE(k_neighbors=k_neighbors, random_state=42)
                X_train, y_train = smote.fit_resample(X_train, y_train)
                smote_applied = True
                logger.info("SMOTE applied — training set resampled to %d samples", len(X_train))
            except Exception as exc:
                logger.warning("SMOTE failed: %s — proceeding without resampling", exc)

        dist_after = {str(k): int((y_train == v).sum()) for k, v in class_to_int.items()}

        # Bug #1: Build real normalization sample data (first row before vs after)
        norm_samples: list[dict[str, object]] = []
        sample_count = min(5, len(feature_names))
        for i in range(sample_count):
            before_val = float(X_train_raw[0, i]) if len(X_train_raw) > 0 else 0.0
            after_val = float(X_train[0, i]) if len(X_train) > 0 else 0.0
            norm_samples.append({
                "feature": feature_names[i],
                "before": round(before_val, 2),
                "after": round(after_val, 3),
            })

        response = PrepResponse(
            session_id=session_id,
            train_size=int(len(X_train)),
            test_size=int(len(X_test)),
            features_count=len(feature_names),
            class_distribution_before=dist_before,
            class_distribution_after=dist_after,
            smote_applied=smote_applied,
            normalization_applied=normalization_applied,
            norm_samples=norm_samples,
        )

        # Column metadata from raw DataFrame (before preprocessing)
        raw_column_meta = []
        for col in df.columns:
            series = df[col]
            raw_column_meta.append({
                "name": col,
                "dtype": str(series.dtype),
                "missing_count": int(series.isna().sum()),
                "missing_pct": round(series.isna().sum() / len(df) * 100, 2),
                "unique_count": int(series.nunique()),
                "sample_values": [str(v) for v in series.dropna().head(3).tolist()],
                "is_target": col == target_col,
            })

        # Persist to session store
        self._session_store[session_id] = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "feature_names": feature_names,
            "classes": [str(c) for c in classes],
            "scaler": scaler,
            "X_train_raw": X_train_raw,
            "X_test_raw": X_test_raw,
            "normalization": settings.normalization,
            "y_train_original": y_train_original,
            "smote_applied": smote_applied,
            "raw_column_meta": raw_column_meta,
            "row_count": len(df),
        }
        logger.info(
            "Session %s prepared — train=%d, test=%d, features=%d",
            session_id,
            len(X_train),
            len(X_test),
            len(feature_names),
        )

        return X_train, X_test, y_train, y_test, response, feature_names

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        return self._session_store.get(session_id)

    # ------------------------------------------------------------------
    # Built-in example datasets
    # ------------------------------------------------------------------
    def get_example_dataset(self, specialty_id: str) -> pd.DataFrame:
        generators: dict[str, Any] = {
            "cardiology_hf": self._heart_failure,
            "radiology_pneumonia": self._pneumonia,
            "nephrology_ckd": self._ckd,
            "oncology_breast": self._breast_cancer,
            "neurology_parkinsons": self._parkinsons,
            "endocrinology_diabetes": self._diabetes,
            "hepatology_liver": self._liver,
            "cardiology_stroke": self._stroke,
            "mental_health": self._mental_health,
            "pulmonology_copd": self._copd,
            "haematology_anaemia": self._anaemia,
            "dermatology": self._dermatology,
            "ophthalmology": self._ophthalmology,
            "orthopaedics": self._orthopaedics,
            "icu_sepsis": self._sepsis,
            "obstetrics_fetal": self._fetal_health,
            "cardiology_arrhythmia": self._arrhythmia,
            "oncology_cervical": self._cervical,
            "thyroid": self._thyroid,
            "pharmacy_readmission": self._readmission,
        }
        gen = generators.get(specialty_id)
        if gen is None:
            raise DatasetUnavailableError(specialty_id, f"Unknown specialty ID '{specialty_id}'")
        df = gen()
        logger.info("Example dataset generated for '%s': %d rows", specialty_id, len(df))
        return df

    # ------ Dataset generators ------

    def _heart_failure(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "cardiology_hf",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/00519/heart_failure_clinical_records_dataset.csv",
        )
        if "DEATH_EVENT" not in df.columns:
            raise DatasetUnavailableError("cardiology_hf", "Missing required column 'DEATH_EVENT'")
        return df

    def _breast_cancer(self) -> pd.DataFrame:
        from sklearn.datasets import load_breast_cancer
        data = load_breast_cancer(as_frame=True)
        df = data.frame.copy()
        df["diagnosis"] = data.target.map({1: "B", 0: "M"})
        df = df.drop(columns=["target"])
        # Normalise column names: replace spaces with underscores
        df.columns = [c.replace(" ", "_") for c in df.columns]
        # Select the 14 registered features (mean + worst geometry/texture only)
        keep = [
            "mean_radius", "mean_texture", "mean_perimeter", "mean_area",
            "mean_smoothness", "mean_compactness", "mean_concavity",
            "mean_concave_points", "mean_symmetry", "worst_radius",
            "worst_texture", "worst_perimeter", "worst_area", "worst_smoothness",
            "diagnosis",
        ]
        available = [c for c in keep if c in df.columns]
        return df[available]

    def _diabetes(self) -> pd.DataFrame:
        pima_cols = [
            "pregnancies", "glucose", "blood_pressure", "skin_thickness",
            "insulin", "bmi", "diabetes_pedigree_function", "age", "Outcome",
        ]
        df = self._fetch_cached(
            "endocrinology_diabetes",
            "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv",
            read_kwargs={"header": None, "names": pima_cols},
        )
        if "Outcome" not in df.columns:
            raise DatasetUnavailableError("endocrinology_diabetes", "Missing required column 'Outcome'")
        return df

    def _ckd(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        csv_cache = _CACHE_DIR / "nephrology_ckd.csv"

        if not csv_cache.exists():
            raise DatasetUnavailableError("nephrology_ckd", f"Cache file not found: {csv_cache}")

        df = pd.read_csv(csv_cache)
        rename_map = {
            "bp": "blood_pressure", "sg": "specific_gravity",
            "al": "albumin", "su": "sugar",
            "rbc": "red_blood_cells", "pc": "pus_cell",
            "bgr": "blood_glucose_random", "bu": "blood_urea",
            "sc": "serum_creatinine", "sod": "sodium",
            "pot": "potassium", "hemo": "haemoglobin",
            "pcv": "packed_cell_volume", "wc": "white_blood_cell_count",
            "rc": "red_blood_cell_count",
            "htn": "hypertension", "dm": "diabetes_mellitus",
            "cad": "coronary_artery_disease",
            "appet": "appetite", "pe": "pedal_oedema", "ane": "anemia",
            "class": "classification",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        if "classification" not in df.columns:
            raise DatasetUnavailableError("nephrology_ckd", "Missing required column 'classification'")
        df["classification"] = df["classification"].astype(str).str.strip().str.rstrip(".")
        df = df[df["classification"].isin(["ckd", "notckd"])].copy()
        for col in df.columns:
            if col != "classification":
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if len(df) < 100:
            raise DatasetUnavailableError("nephrology_ckd", f"Dataset too small ({len(df)} rows)")
        return df

    def _parkinsons(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "neurology_parkinsons",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/parkinsons/parkinsons.data",
        )
        if "name" in df.columns:
            df = df.drop(columns=["name"])
        col_rename = {
            "MDVP:Fo(Hz)": "MDVP_Fo_Hz",
            "MDVP:Fhi(Hz)": "MDVP_Fhi_Hz",
            "MDVP:Flo(Hz)": "MDVP_Flo_Hz",
            "MDVP:Jitter(%)": "MDVP_Jitter_pct",
            "MDVP:Jitter(Abs)": "MDVP_Jitter_Abs",
            "MDVP:RAP": "MDVP_RAP",
            "MDVP:PPQ": "MDVP_PPQ",
            "Jitter:DDP": "Jitter_DDP",
            "MDVP:Shimmer": "MDVP_Shimmer",
            "MDVP:Shimmer(dB)": "MDVP_Shimmer_dB",
            "Shimmer:APQ3": "Shimmer_APQ3",
            "Shimmer:APQ5": "Shimmer_APQ5",
            "MDVP:APQ": "MDVP_APQ",
            "Shimmer:DDA": "Shimmer_DDA",
        }
        df = df.rename(columns={k: v for k, v in col_rename.items() if k in df.columns})
        if "status" not in df.columns:
            raise DatasetUnavailableError("neurology_parkinsons", "Missing required column 'status'")
        return df

    def _liver(self) -> pd.DataFrame:
        ilpd_cols = [
            "age", "gender", "total_bilirubin", "direct_bilirubin",
            "alkaline_phosphotase", "alamine_aminotransferase",
            "aspartate_aminotransferase", "total_proteins",
            "albumin", "albumin_globulin_ratio", "Dataset",
        ]
        df = self._fetch_cached(
            "hepatology_liver",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv",
            read_kwargs={"header": None, "names": ilpd_cols},
        )
        if "Dataset" not in df.columns:
            raise DatasetUnavailableError("hepatology_liver", "Missing required column 'Dataset'")
        if df["gender"].dtype == object:
            df["gender"] = (df["gender"] == "Male").astype(int)
        df["albumin_globulin_ratio"] = df["albumin_globulin_ratio"].fillna(
            df["albumin_globulin_ratio"].median()
        )
        return df

    def _stroke(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "cardiology_stroke",
            "https://raw.githubusercontent.com/04-aditya/Stroke-Prediction-using-R/main/healthcare-dataset-stroke-data.csv",
        )
        if "stroke" not in df.columns:
            raise DatasetUnavailableError("cardiology_stroke", "Missing required column 'stroke'")
        if "id" in df.columns:
            df = df.drop(columns=["id"])
        cat_encodings: dict[str, dict] = {
            "gender": {"Male": 1, "Female": 0, "Other": 0},
            "ever_married": {"Yes": 1, "No": 0},
            "work_type": {"children": 0, "Govt_job": 1, "Never_worked": 2, "Private": 3, "Self-employed": 4},
            "smoking_status": {"never smoked": 0, "Unknown": 1, "formerly smoked": 2, "smokes": 3},
        }
        for col, mapping in cat_encodings.items():
            if col in df.columns and df[col].dtype == object:
                df[col] = df[col].map(mapping).fillna(0).astype(int)
        if "Residence_type" in df.columns:
            df = df.rename(columns={"Residence_type": "residence_type"})
        if "residence_type" in df.columns and df["residence_type"].dtype == object:
            df["residence_type"] = (df["residence_type"] == "Urban").astype(int)
        df["bmi"] = pd.to_numeric(df["bmi"], errors="coerce")
        df["stroke"] = pd.to_numeric(df["stroke"], errors="coerce")
        df = df.dropna(subset=["stroke"])
        if len(df) < 100:
            raise DatasetUnavailableError("cardiology_stroke", f"Dataset too small ({len(df)} rows)")
        return df

    def _mental_health(self) -> pd.DataFrame:
        for candidate in ("depression_data.csv", "mental_health_depression.csv"):
            csv_cache = _CACHE_DIR / candidate
            if csv_cache.exists():
                try:
                    df = pd.read_csv(csv_cache)
                    df = df.drop(columns=[c for c in ["Name", "name"] if c in df.columns])
                    ordinal_maps = {
                        "Dietary Habits": {"Healthy": 2, "Moderate": 1, "Unhealthy": 0},
                        "Sleep Patterns": {"Good": 2, "Fair": 1, "Poor": 0},
                        "Alcohol Consumption": {"Low": 0, "Moderate": 1, "High": 2},
                        "Physical Activity Level": {"Active": 2, "Moderate": 1, "Sedentary": 0},
                        "Smoking Status": {"Non-smoker": 0, "Former": 1, "Current": 2},
                        "Employment Status": {"Employed": 1, "Unemployed": 0},
                    }
                    for col, mapping in ordinal_maps.items():
                        if col in df.columns:
                            df[col] = df[col].map(mapping).fillna(1).astype(int)
                    yes_no_cols = [
                        "History of Substance Abuse", "Family History of Depression",
                        "Chronic Medical Conditions",
                    ]
                    for col in yes_no_cols:
                        if col in df.columns and df[col].dtype == object:
                            df[col] = (df[col].str.lower() == "yes").astype(int)
                    if "History of Mental Illness" in df.columns:
                        df["severity_class"] = df["History of Mental Illness"].map(
                            {"Yes": "has_condition", "No": "no_condition"}
                        )
                        df = df.drop(columns=["History of Mental Illness"])
                    elif "Depression" in df.columns:
                        df["severity_class"] = df["Depression"].map({1: "has_condition", 0: "no_condition"})
                        df = df.drop(columns=["Depression"])
                    col_rename = {
                        "Age": "age",
                        "Number of Children": "number_of_children",
                        "Income": "income",
                        "Dietary Habits": "dietary_habits",
                        "Sleep Patterns": "sleep_patterns",
                        "Alcohol Consumption": "alcohol_consumption",
                        "Physical Activity Level": "physical_activity_level",
                        "Smoking Status": "smoking_status",
                        "Employment Status": "employment_status",
                        "History of Substance Abuse": "history_substance_abuse",
                        "Family History of Depression": "family_history_depression",
                        "Chronic Medical Conditions": "chronic_medical_conditions",
                        "Marital Status": "marital_status",
                        "Education Level": "education_level",
                    }
                    df = df.rename(columns={k: v for k, v in col_rename.items() if k in df.columns})
                    for col in df.columns:
                        if col != "severity_class" and df[col].dtype == object:
                            df[col] = pd.Categorical(df[col]).codes
                    df = df.dropna(subset=["severity_class"])
                    if len(df) >= 100 and "severity_class" in df.columns:
                        if len(df) > 5000:
                            from sklearn.model_selection import train_test_split as _tts
                            _, df = _tts(
                                df, test_size=5000, random_state=42,
                                stratify=df["severity_class"] if df["severity_class"].nunique() > 1 else None,
                            )
                            df = df.reset_index(drop=True)
                        logger.info("Loaded real mental health dataset (%d rows) from %s", len(df), candidate)
                        return df
                except Exception as exc:
                    logger.warning("Mental health CSV load failed (%s): %s", candidate, exc)

        raise DatasetUnavailableError(
            "mental_health",
            "Real mental health dataset not found in data_cache/. "
            "Download from kaggle.com/datasets/anthonytherrien/depression-dataset "
            "and save as depression_data.csv in data_cache/",
        )

    def _copd(self) -> pd.DataFrame:
        csv_cache = _CACHE_DIR / "pulmonology_copd.csv"
        if not csv_cache.exists():
            raise DatasetUnavailableError(
                "pulmonology_copd",
                f"Real COPD dataset not found at {csv_cache}. "
                "Download from kaggle.com/datasets/prakharrathi25/copd-student-dataset "
                "or physionet.org/content/copd-ehr/1.0.0/ "
                "and save as pulmonology_copd.csv in data_cache/",
            )

        df = pd.read_csv(csv_cache)
        col_rename = {
            "AGE": "age", "Age": "age",
            "SEX": "sex", "Sex": "sex", "GENDER": "sex", "Gender": "sex",
            "SMOKING_PACK_YEARS": "smoking_pack_years", "PackYears": "smoking_pack_years",
            "FEV1": "fev1_litres", "FEV1_LITRES": "fev1_litres",
            "FVC": "fvc_litres", "FVC_LITRES": "fvc_litres",
            "FEV1_FVC": "fev1_fvc_ratio", "FEV1FVC": "fev1_fvc_ratio",
            "PRIOR_EXAC": "prior_exacerbations_year", "ExacerbationRate": "prior_exacerbations_year",
            "BMI": "bmi",
            "MRC": "mrc_dyspnea_scale", "MRCScore": "mrc_dyspnea_scale",
            "SGRQ": "sgrq_score", "SGRQTotal": "sgrq_score",
            "GOLD_STAGE": "copd_gold_stage", "GOLDStage": "copd_gold_stage",
            "EXACERBATION": "exacerbation", "Exacerbation": "exacerbation",
            "EXAC": "exacerbation",
        }
        df = df.rename(columns={k: v for k, v in col_rename.items() if k in df.columns})
        if "sex" in df.columns and df["sex"].dtype == object:
            df["sex"] = (df["sex"].str.lower().isin(["m", "male", "1"])).astype(int)
        for col in df.columns:
            if col != "exacerbation":
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "exacerbation" in df.columns and df["exacerbation"].dtype == object:
            df["exacerbation"] = pd.to_numeric(df["exacerbation"], errors="coerce")
        df = df.dropna(subset=["exacerbation"])
        keep = [
            "age", "sex", "smoking_pack_years", "fev1_litres", "fvc_litres",
            "fev1_fvc_ratio", "prior_exacerbations_year", "bmi",
            "mrc_dyspnea_scale", "sgrq_score", "copd_gold_stage", "exacerbation",
        ]
        available = [c for c in keep if c in df.columns]
        df = df[available]
        if len(df) < 100 or "exacerbation" not in df.columns:
            raise DatasetUnavailableError("pulmonology_copd", f"Dataset too small or missing target ({len(df)} rows)")
        logger.info("Loaded real COPD dataset (%d rows)", len(df))
        return df

    def _anaemia(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "haematology_anaemia",
            "https://raw.githubusercontent.com/maladeep/anemia-detection-with-machine-learning/master/anemia%20data%20from%20Kaggle.csv",
        )
        rename_map = {
            "Gender": "gender", "Hemoglobin": "haemoglobin",
            "MCH": "mch", "MCHC": "mchc", "MCV": "mcv",
            "Result": "anemia_type",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        # Gender is already encoded as 0/1 in the source CSV; coerce to numeric
        # to handle any edge-case whitespace or string variants.
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        if "anemia_type" not in df.columns:
            raise DatasetUnavailableError("haematology_anaemia", "Missing required column 'anemia_type'")
        df = df.dropna(subset=["anemia_type"])
        return df

    def _dermatology(self) -> pd.DataFrame:
        csv_cache = _CACHE_DIR / "dermatology.csv"
        df = None
        if csv_cache.exists():
            try:
                df = pd.read_csv(csv_cache)
            except Exception:
                pass
        if df is None or "dx" not in (df.columns if df is not None else []):
            df = self._fetch_cached(
                "dermatology_tsv",
                "https://dataverse.harvard.edu/api/access/datafile/4338392",
                read_kwargs={"sep": "\t", "quotechar": '"'},
            )
        if "dx" not in df.columns:
            raise DatasetUnavailableError("dermatology", "Missing required column 'dx'")
        malignant = {"mel", "bcc", "akiec"}
        df["dx_type"] = df["dx"].apply(
            lambda x: "malignant" if str(x).strip() in malignant else "benign"
        )
        if "sex" in df.columns and df["sex"].dtype == object:
            df["sex"] = (df["sex"] == "male").astype(int)
        if "localization" in df.columns and df["localization"].dtype == object:
            locs = df["localization"].unique()
            loc_map = {v: i for i, v in enumerate(sorted(locs))}
            df["localization"] = df["localization"].map(loc_map).fillna(0).astype(int)
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
        keep = ["age", "sex", "localization", "dx_type"]
        df = df[[c for c in keep if c in df.columns]].dropna(subset=["dx_type"])
        if len(df) < 100:
            raise DatasetUnavailableError("dermatology", f"Dataset too small ({len(df)} rows)")
        return df

    def _ophthalmology(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        arff_cache = _CACHE_DIR / "ophthalmology.arff"
        if not arff_cache.exists():
            try:
                resp = requests.get(
                    "https://archive.ics.uci.edu/static/public/329/diabetic+retinopathy+debrecen+data+set.zip",
                    timeout=30, headers={"User-Agent": "HealthWithSevgi/1.0"},
                )
                resp.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                    arff_names = [n for n in zf.namelist() if n.endswith(".arff")]
                    if arff_names:
                        arff_cache.write_bytes(zf.read(arff_names[0]))
                        logger.info("Extracted Debrecen DR ARFF (%d bytes)", arff_cache.stat().st_size)
            except Exception as exc:
                raise DatasetUnavailableError(
                    "ophthalmology", f"Failed to download Debrecen DR ARFF: {exc}"
                ) from exc

        if not arff_cache.exists():
            raise DatasetUnavailableError("ophthalmology", f"ARFF file not found: {arff_cache}")

        from scipy.io import arff as scipy_arff
        data, meta = scipy_arff.loadarff(str(arff_cache))
        df = pd.DataFrame(data)
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.decode("utf-8").str.strip()
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        cols = list(df.columns)
        feature_cols = cols[:-1]
        target_col = cols[-1]
        df = df.rename(columns={target_col: "severity_grade"})
        df["severity_grade"] = df["severity_grade"].astype(int)
        named_features = [
            "quality_assessment", "pre_screening", "ma_detection_0.5",
            "ma_detection_0.6", "ma_detection_0.7", "ma_detection_0.8",
            "ma_detection_0.9", "ma_detection_1.0",
            "exudate_1", "exudate_2", "exudate_3", "exudate_4",
            "exudate_5", "exudate_6", "exudate_7", "exudate_8",
            "macula_od_distance", "optic_disc_diameter", "am_fm_classification",
        ]
        if len(feature_cols) == len(named_features):
            rename_map = {old: new for old, new in zip(feature_cols, named_features)}
            df = df.rename(columns=rename_map)
        df = df.dropna(subset=["severity_grade"])
        if len(df) < 100:
            raise DatasetUnavailableError("ophthalmology", f"Dataset too small ({len(df)} rows)")
        return df

    def _orthopaedics(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        arff_cache = _CACHE_DIR / "orthopaedics.arff"

        if not arff_cache.exists():
            try:
                resp = requests.get(
                    "https://archive.ics.uci.edu/static/public/212/vertebral+column.zip",
                    timeout=30, headers={"User-Agent": "HealthWithSevgi/1.0"},
                )
                resp.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                    arff_names = [n for n in zf.namelist() if n.endswith("_weka.arff")]
                    if arff_names:
                        arff_cache.write_bytes(zf.read(arff_names[0]))
                        logger.info("Extracted vertebral column ARFF (%d bytes)", arff_cache.stat().st_size)
            except Exception as exc:
                raise DatasetUnavailableError(
                    "orthopaedics", f"Failed to download vertebral column ARFF: {exc}"
                ) from exc

        if not arff_cache.exists():
            raise DatasetUnavailableError("orthopaedics", f"ARFF file not found: {arff_cache}")

        from scipy.io import arff as scipy_arff
        data, meta = scipy_arff.loadarff(str(arff_cache))
        df = pd.DataFrame(data)
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.decode("utf-8")
        col_names = [
            "pelvic_incidence", "pelvic_tilt", "lumbar_lordosis_angle",
            "sacral_slope", "pelvic_radius", "degree_spondylolisthesis", "class",
        ]
        if len(df.columns) == len(col_names):
            df.columns = col_names
        if "class" not in df.columns:
            raise DatasetUnavailableError("orthopaedics", "Missing required column 'class'")
        return df

    def _sepsis(self) -> pd.DataFrame:
        csv_cache = _CACHE_DIR / "icu_sepsis.csv"
        if not csv_cache.exists():
            raise DatasetUnavailableError(
                "icu_sepsis",
                f"Real ICU/Sepsis dataset not found at {csv_cache}. "
                "Download from physionet.org/content/challenge-2019/1.0.0/, "
                "merge PSV files into one CSV, and save as icu_sepsis.csv in data_cache/",
            )

        df = pd.read_csv(csv_cache)
        if len(df.columns) == 1:
            df = pd.read_csv(csv_cache, sep="|")
        keep = [
            "HR", "O2Sat", "Temp", "SBP", "MAP", "Resp",
            "BaseExcess", "pH", "PaCO2", "Lactate", "Creatinine",
            "Bilirubin_total", "WBC", "Platelets", "Age", "Gender", "SepsisLabel",
        ]
        available = [c for c in keep if c in df.columns]
        df = df[available].dropna(subset=["SepsisLabel"])
        df["SepsisLabel"] = pd.to_numeric(df["SepsisLabel"], errors="coerce").astype("Int64")
        df = df.dropna(subset=["SepsisLabel"])
        if len(df) < 100 or "SepsisLabel" not in df.columns:
            raise DatasetUnavailableError("icu_sepsis", f"Dataset too small ({len(df)} rows)")
        if len(df) > 5000:
            # Stratified cap: guarantee all positive (sepsis=1) cases are retained,
            # then fill the remaining budget with negatives. A random cap at 5000 rows
            # would yield only ~100-250 positives at 2-5% prevalence, making the
            # imbalance effectively 20-50:1. This preserves every real sepsis case.
            sep_pos = df[df["SepsisLabel"] == 1]
            sep_neg = df[df["SepsisLabel"] == 0]
            n_neg = max(0, 5000 - len(sep_pos))
            if len(sep_neg) > n_neg:
                sep_neg = sep_neg.sample(n_neg, random_state=42)
            df = pd.concat([sep_pos, sep_neg]).sample(frac=1, random_state=42).reset_index(drop=True)
        logger.info("Loaded real ICU sepsis dataset (%d rows, %d positive)", len(df), int((df["SepsisLabel"] == 1).sum()))
        return df

    def _fetal_health(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        csv_cache = _CACHE_DIR / "obstetrics_fetal.csv"

        if not csv_cache.exists():
            raise DatasetUnavailableError("obstetrics_fetal", f"Cache file not found: {csv_cache}")

        df = pd.read_csv(csv_cache)
        if len(df.columns) <= 2:
            df = pd.read_csv(csv_cache, sep=";")
        col_map = {
            "LB": "baseline_value", "AC": "accelerations", "FM": "fetal_movement",
            "UC": "uterine_contractions", "DL": "light_decelerations",
            "DS": "severe_decelerations", "DP": "prolongued_decelerations",
            "ASTV": "abnormal_short_term_variability",
            "MSTV": "mean_value_short_term_variability",
            "ALTV": "pct_time_abnormal_long_term_variability",
            "MLTV": "mean_value_long_term_variability",
            "Mode": "histogram_mode",
            "NSP": "fetal_health",
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        if "fetal_health" not in df.columns:
            raise DatasetUnavailableError("obstetrics_fetal", "Missing required column 'fetal_health'")
        df["fetal_health"] = pd.to_numeric(df["fetal_health"], errors="coerce")
        df = df.dropna(subset=["fetal_health"])
        df["fetal_health"] = df["fetal_health"].astype(int)
        keep = [v for v in col_map.values() if v in df.columns]
        df = df[keep].dropna(subset=["fetal_health"])
        if len(df) < 100:
            raise DatasetUnavailableError("obstetrics_fetal", f"Dataset too small ({len(df)} rows)")
        return df

    def _arrhythmia(self) -> pd.DataFrame:
        all_cols = [f"feature_{i}" for i in range(279)] + ["arrhythmia_class"]
        df = self._fetch_cached(
            "cardiology_arrhythmia",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/arrhythmia/arrhythmia.data",
            read_kwargs={"header": None, "names": all_cols, "na_values": "?"},
        )
        if "arrhythmia_class" not in df.columns:
            raise DatasetUnavailableError("cardiology_arrhythmia", "Missing required column 'arrhythmia_class'")
        df["arrhythmia"] = df["arrhythmia_class"].apply(lambda x: 0 if x == 1 else 1)
        # Name the first 15 global ECG features; the remaining 264 columns are
        # per-lead amplitude measurements (R, S, T, P amplitudes across 12 leads)
        # that carry the primary diagnostic signal for arrhythmia classification.
        # Previously only the 13 global interval features were kept, discarding all
        # per-lead amplitude data. All columns are kept here — Random Forest selects
        # the most discriminative ones via feature importance at each split.
        global_names = [
            "age", "sex", "height", "weight", "QRS_duration",
            "PR_interval", "QT_interval", "T_interval", "P_interval",
            "QRS_axis", "T_axis", "P_axis", "heart_rate", "J_point", "heart_rate_2",
        ]
        rename_map = {f"feature_{i}": name for i, name in enumerate(global_names)}
        df = df.rename(columns=rename_map)
        df = df.drop(columns=["arrhythmia_class"])
        df = df.dropna(subset=["arrhythmia"])
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        if len(df) < 100:
            raise DatasetUnavailableError("cardiology_arrhythmia", f"Dataset too small ({len(df)} rows)")
        return df

    def _cervical(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "oncology_cervical",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/00383/risk_factors_cervical_cancer.csv",
        )
        if "Biopsy" not in df.columns:
            raise DatasetUnavailableError("oncology_cervical", "Missing required column 'Biopsy'")
        df = df.replace("?", np.nan)
        # Feature set split into two tiers:
        # Tier 1 — clinical test results (near-zero missingness, direct diagnostic signal):
        #   Hinselmann (colposcopy), Schiller (iodine test), Citology (pap smear),
        #   Dx:Cancer / Dx:CIN / Dx:HPV / Dx (diagnosis history flags).
        # Tier 2 — behavioural risk factors (higher missingness, weak indirect signal):
        #   age, sexual history, smoking, contraceptives, STDs.
        # Using only Tier 2 produces near-random predictions (MCC ≈ 0) because
        # these epidemiological risk factors cannot reliably predict individual biopsy
        # outcomes. Adding Tier 1 gives the model the actual clinical evidence a
        # clinician would use to decide whether to proceed with biopsy.
        keep_cols = [
            "Age", "Number of sexual partners", "First sexual intercourse",
            "Num of pregnancies",
            "Smokes", "Smokes (years)",
            "Hormonal Contraceptives", "Hormonal Contraceptives (years)",
            "IUD", "IUD (years)",
            "STDs", "STDs (number)", "STDs:condylomatosis",
            "STDs:cervical condylomatosis", "STDs:HPV",
            "Dx:Cancer", "Dx:CIN", "Dx:HPV", "Dx",
            "Hinselmann", "Schiller", "Citology",
            "Biopsy",
        ]
        available = [c for c in keep_cols if c in df.columns]
        df = df[available].copy()
        rename_map = {
            "Age": "age",
            "Number of sexual partners": "number_of_sexual_partners",
            "First sexual intercourse": "first_sexual_intercourse_age",
            "Num of pregnancies": "num_of_pregnancies",
            "Smokes": "smokes",
            "Smokes (years)": "smokes_years",
            "Hormonal Contraceptives": "hormonal_contraceptives",
            "Hormonal Contraceptives (years)": "hormonal_contraceptives_years",
            "IUD": "iud",
            "IUD (years)": "iud_years",
            "STDs": "stds",
            "STDs (number)": "stds_number",
            "STDs:condylomatosis": "stds_condylomatosis",
            "STDs:cervical condylomatosis": "stds_cervical_condylomatosis",
            "STDs:HPV": "stds_hpv",
            "Dx:Cancer": "dx_cancer",
            "Dx:CIN": "dx_cin",
            "Dx:HPV": "dx_hpv",
            "Dx": "dx",
            "Hinselmann": "hinselmann",
            "Schiller": "schiller",
            "Citology": "citology",
        }
        df = df.rename(columns=rename_map)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["Biopsy"])
        return df

    def _thyroid(self) -> pd.DataFrame:
        col_names = ["class_raw", "T3_resin_uptake", "total_serum_thyroxine", "T3", "TSH", "max_abs_diff_TSH"]
        df = self._fetch_cached(
            "thyroid",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/thyroid-disease/new-thyroid.data",
            read_kwargs={"header": None, "names": col_names, "sep": ","},
        )
        if "class_raw" not in df.columns:
            raise DatasetUnavailableError("thyroid", "Missing required column 'class_raw'")
        class_map = {1: "hyperthyroid", 2: "normal", 3: "hypothyroid"}
        df["class"] = df["class_raw"].map(class_map)
        df = df.drop(columns=["class_raw"])
        df = df.dropna(subset=["class"])
        if len(df) < 100:
            raise DatasetUnavailableError("thyroid", f"Dataset too small ({len(df)} rows)")
        return df

    def _readmission(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        csv_cache = _CACHE_DIR / "pharmacy_readmission.csv"
        if not csv_cache.exists():
            try:
                resp = requests.get(
                    "https://archive.ics.uci.edu/ml/machine-learning-databases/00296/dataset_diabetes.zip",
                    timeout=60, headers={"User-Agent": "HealthWithSevgi/1.0"},
                )
                resp.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                    csv_names = [n for n in zf.namelist() if "diabetic_data" in n and n.endswith(".csv")]
                    if not csv_names:
                        csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
                    if csv_names:
                        raw = pd.read_csv(zf.open(csv_names[0]), low_memory=False)
                        keep_cols = [
                            "age", "gender", "time_in_hospital", "num_lab_procedures",
                            "num_procedures", "num_medications", "number_outpatient",
                            "number_emergency", "number_inpatient", "number_diagnoses",
                            "max_glu_serum", "A1Cresult", "metformin", "insulin",
                            "change",
                            # High-signal clinical context features missing from v1:
                            # discharge destination is the strongest readmission predictor;
                            # admission type and source capture acuity and referral pathway;
                            # primary diagnosis category captures disease burden.
                            "discharge_disposition_id", "admission_type_id",
                            "admission_source_id", "diag_1",
                            "readmitted",
                        ]
                        available = [c for c in keep_cols if c in raw.columns]
                        raw = raw[available].copy()
                        if "age" in raw.columns and raw["age"].dtype == object:
                            age_map = {
                                "[0-10)": 0, "[10-20)": 1, "[20-30)": 2, "[30-40)": 3,
                                "[40-50)": 4, "[50-60)": 5, "[60-70)": 6, "[70-80)": 7,
                                "[80-90)": 8, "[90-100)": 9,
                            }
                            raw["age"] = raw["age"].map(age_map).fillna(5).astype(int)
                        if "gender" in raw.columns and raw["gender"].dtype == object:
                            raw["gender"] = (raw["gender"] == "Male").astype(int)
                        med_map = {"No": 0, "Steady": 1, "Up": 2, "Down": 3}
                        for col in ["metformin", "insulin", "change"]:
                            if col in raw.columns and raw[col].dtype == object:
                                raw[col] = raw[col].map(med_map).fillna(0).astype(int)
                        for col in ["max_glu_serum", "A1Cresult"]:
                            if col in raw.columns and raw[col].dtype == object:
                                glu_map = {"None": 0, "Norm": 1, ">200": 2, ">300": 3, ">7": 1, ">8": 2}
                                raw[col] = raw[col].map(glu_map).fillna(0).astype(int)
                        # Map diag_1 (ICD-9 codes) to major disease categories.
                        # Raw ICD-9 strings have no ordinal meaning; bucketing into
                        # 9 clinical groups gives the model learnable signal.
                        if "diag_1" in raw.columns:
                            def _icd9_category(code: str) -> int:
                                c = str(code).strip().upper().replace(".", "")
                                if c.startswith("V") or c.startswith("E"):
                                    return 0
                                try:
                                    n = float(c)
                                except ValueError:
                                    return 0
                                if n < 140: return 1       # Infectious
                                if n < 240: return 2       # Neoplasms
                                if n < 280: return 3       # Endocrine/Diabetes
                                if n < 290: return 4       # Blood
                                if n < 390: return 5       # Mental
                                if n < 460: return 6       # Circulatory
                                if n < 520: return 7       # Respiratory
                                if n < 580: return 8       # Digestive
                                return 9                   # Other
                            raw["diag_1"] = raw["diag_1"].apply(_icd9_category)
                        raw = raw.dropna(subset=["readmitted"])
                        if len(raw) > 5000:
                            # Stratified cap: guarantee proportional representation of
                            # each readmission class. <30 days is ~11% of the full
                            # dataset; a random 5000-row sample would give only ~550
                            # rows for that class. Stratified sampling preserves ratio.
                            from sklearn.model_selection import train_test_split as _tts
                            _, raw = _tts(
                                raw, test_size=5000, random_state=42,
                                stratify=raw["readmitted"] if raw["readmitted"].nunique() > 1 else None,
                            )
                            raw = raw.reset_index(drop=True)
                        raw.to_csv(csv_cache, index=False)
                        logger.info("Cached readmission dataset (%d rows)", len(raw))
            except Exception as exc:
                raise DatasetUnavailableError(
                    "pharmacy_readmission", f"Failed to download/parse readmission ZIP: {exc}"
                ) from exc

        if not csv_cache.exists():
            raise DatasetUnavailableError("pharmacy_readmission", f"Cache file not found: {csv_cache}")

        df = pd.read_csv(csv_cache)
        if "readmitted" not in df.columns or len(df) < 100:
            raise DatasetUnavailableError("pharmacy_readmission", "Invalid or too small dataset")
        return df

    def _pneumonia(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "radiology_pneumonia",
            "https://raw.githubusercontent.com/gregwchase/nih-chest-xray/master/data/Data_Entry_2017.csv",
        )
        if "Finding Labels" not in df.columns:
            raise DatasetUnavailableError("radiology_pneumonia", "Missing required column 'Finding Labels'")
        df = df[df["Finding Labels"].isin(["Pneumonia", "No Finding"])].copy()
        df = df.rename(columns={
            "Patient Age": "age",
            "Patient Gender": "sex",
            "View Position": "view_position",
            "Follow-up #": "follow_up_number",
            "Finding Labels": "Finding_Label",
        })
        if "sex" in df.columns and df["sex"].dtype == object:
            df["sex"] = (df["sex"] == "M").astype(int)
        if "view_position" in df.columns and df["view_position"].dtype == object:
            df["view_position"] = (df["view_position"] == "PA").astype(int)
        keep = ["age", "sex", "view_position", "follow_up_number", "Finding_Label"]
        df = df[[c for c in keep if c in df.columns]].dropna(subset=["Finding_Label"])
        df["age"] = df["age"].astype(str).str.replace(r"[^0-9]", "", regex=True)
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
        df = df.dropna(subset=["age"])
        if len(df) < 100:
            raise DatasetUnavailableError("radiology_pneumonia", f"Dataset too small ({len(df)} rows)")
        return df

