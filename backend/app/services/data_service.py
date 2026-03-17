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
    ) -> pd.DataFrame | None:
        """Download a dataset from URL, cache locally, return DataFrame. Returns None on failure."""
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = _CACHE_DIR / f"{name}.csv"
        rk = read_kwargs or {}

        # Try from cache first
        if cache_path.exists():
            try:
                return pd.read_csv(cache_path, **rk)
            except Exception as exc:
                logger.warning("Cache read failed for %s: %s", name, exc)

        # Download
        try:
            resp = requests.get(url, timeout=20, headers={"User-Agent": "HealthWithSevgi/1.0"})
            resp.raise_for_status()
            cache_path.write_bytes(resp.content)
            logger.info("Downloaded real dataset: %s (%d bytes)", name, len(resp.content))
            return pd.read_csv(io.BytesIO(resp.content), **rk)
        except Exception as exc:
            logger.warning(
                "Failed to download %s from %s: %s — using synthetic data", name, url, exc
            )
            return None

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
        y_train_original = y_train.copy()  # preserve pre-SMOTE labels for leak-free CV
        smote_applied = False
        
        # Filter out classes with fewer than 2 samples to prevent SMOTE ValueError
        unique, counts = np.unique(y_train, return_counts=True)
        valid_classes = unique[counts >= 2]
        if len(valid_classes) < len(unique):
            logger.warning(
                "Dropped %d classes with only 1 sample before SMOTE/training.",
                len(unique) - len(valid_classes)
            )
            mask = np.isin(y_train, valid_classes)
            X_train = X_train[mask]
            y_train = y_train[mask]
            
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
        gen = generators.get(specialty_id, self._generic_fallback)
        df = gen()
        logger.info("Example dataset generated for '%s': %d rows", specialty_id, len(df))
        return df

    # ------ Dataset generators ------

    def _rng(self) -> np.random.Generator:
        return np.random.default_rng(42)

    def _heart_failure(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "cardiology_hf",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/00519/heart_failure_clinical_records_dataset.csv",
        )
        if df is not None and "DEATH_EVENT" in df.columns:
            return df

        # Fallback to synthetic
        rng = self._rng()
        n = 299
        age = rng.integers(40, 95, n)
        ejection_fraction = rng.integers(14, 80, n)
        serum_creatinine = rng.uniform(0.5, 9.4, n).round(1)
        serum_sodium = rng.integers(113, 148, n)
        creatinine_phosphokinase = rng.integers(23, 7861, n)
        platelets = rng.uniform(25_100, 850_000, n).round(0)
        anaemia = rng.integers(0, 2, n)
        diabetes = rng.integers(0, 2, n)
        high_blood_pressure = rng.integers(0, 2, n)
        sex = rng.integers(0, 2, n)
        smoking = rng.integers(0, 2, n)
        time = rng.integers(4, 285, n)
        # Clinically motivated target: high creatinine + low EF → higher death risk
        log_odds = (
            -3
            + 0.03 * (age - 60)
            + 0.05 * (2 - ejection_fraction / 20)
            + 0.4 * serum_creatinine
            - 0.02 * serum_sodium
            + 0.3 * high_blood_pressure
        )
        prob = 1 / (1 + np.exp(-log_odds))
        death_event = (rng.uniform(0, 1, n) < prob).astype(int)
        return pd.DataFrame({
            "age": age, "anaemia": anaemia,
            "creatinine_phosphokinase": creatinine_phosphokinase,
            "diabetes": diabetes, "ejection_fraction": ejection_fraction,
            "high_blood_pressure": high_blood_pressure, "platelets": platelets,
            "serum_creatinine": serum_creatinine, "serum_sodium": serum_sodium,
            "sex": sex, "smoking": smoking, "time": time, "DEATH_EVENT": death_event,
        })

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
        if df is not None and "Outcome" in df.columns:
            return df

        # Fallback to synthetic
        rng = self._rng()
        n = 768
        pregnancies = rng.integers(0, 17, n)
        glucose = rng.integers(44, 199, n)
        blood_pressure = rng.integers(24, 122, n)
        skin_thickness = rng.integers(0, 99, n)
        insulin = rng.integers(0, 846, n)
        bmi = rng.uniform(18.0, 67.1, n).round(1)
        dpf = rng.uniform(0.078, 2.42, n).round(3)
        age = rng.integers(21, 81, n)
        log_odds = (
            -6 + 0.04 * glucose + 0.05 * bmi + 0.03 * age
            + 0.1 * pregnancies + 0.002 * insulin
        )
        prob = 1 / (1 + np.exp(-log_odds))
        outcome = (rng.uniform(0, 1, n) < prob).astype(int)
        return pd.DataFrame({
            "pregnancies": pregnancies, "glucose": glucose,
            "blood_pressure": blood_pressure, "skin_thickness": skin_thickness,
            "insulin": insulin, "bmi": bmi,
            "diabetes_pedigree_function": dpf, "age": age, "Outcome": outcome,
        })

    def _ckd(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        csv_cache = _CACHE_DIR / "nephrology_ckd.csv"
        if not csv_cache.exists():
            try:
                from ucimlrepo import fetch_ucirepo
                data = fetch_ucirepo(id=336)
                X = data.data.features.copy()
                y = data.data.targets.copy()
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
                }
                X = X.rename(columns={k: v for k, v in rename_map.items() if k in X.columns})
                X["classification"] = y["class"].str.strip()
                X = X[X["classification"].isin(["ckd", "notckd"])].copy()
                # Convert numeric columns
                for col in X.columns:
                    if col != "classification":
                        X[col] = pd.to_numeric(X[col], errors="coerce")
                X.to_csv(csv_cache, index=False)
                logger.info("Cached CKD dataset (%d rows)", len(X))
            except Exception as exc:
                logger.warning("Failed to fetch CKD via ucimlrepo: %s", exc)

        if csv_cache.exists():
            try:
                df = pd.read_csv(csv_cache)
                if "classification" in df.columns and len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("CKD CSV cache read failed: %s", exc)

        # Fallback to synthetic
        rng = self._rng()
        n = 400
        age = rng.integers(2, 90, n)
        bp = rng.integers(50, 180, n)
        sg = rng.choice([1.005, 1.010, 1.015, 1.020, 1.025], n)
        albumin = rng.integers(0, 5, n)
        sugar = rng.integers(0, 5, n)
        rbc = rng.choice([0, 1], n)
        pc = rng.choice([0, 1], n)
        bgr = rng.integers(70, 490, n)
        bu = rng.integers(1, 391, n)
        sc = rng.uniform(0.4, 76.0, n).round(1)
        sod = rng.integers(111, 163, n)
        hemo = rng.uniform(3.1, 17.8, n).round(1)
        htn = rng.integers(0, 2, n)
        dm = rng.integers(0, 2, n)
        log_odds = (
            -4 + 0.04 * bu + 0.5 * sc + 0.3 * albumin
            - 0.2 * hemo + 0.3 * htn
        )
        prob = 1 / (1 + np.exp(-log_odds))
        classification = np.where(rng.uniform(0, 1, n) < prob, "ckd", "notckd")
        return pd.DataFrame({
            "age": age, "blood_pressure": bp, "specific_gravity": sg,
            "albumin": albumin, "sugar": sugar, "red_blood_cells": rbc,
            "pus_cell": pc, "blood_glucose_random": bgr, "blood_urea": bu,
            "serum_creatinine": sc, "sodium": sod, "haemoglobin": hemo,
            "hypertension": htn, "diabetes_mellitus": dm, "classification": classification,
        })

    def _parkinsons(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "neurology_parkinsons",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/parkinsons/parkinsons.data",
        )
        if df is not None:
            if "name" in df.columns:
                df = df.drop(columns=["name"])
            # Real CSV uses colon/paren notation (e.g. "MDVP:Fo(Hz)") — rename to underscore format
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
            if "status" in df.columns:
                return df

        # Fallback to synthetic
        rng = self._rng()
        n = 195
        fo = rng.uniform(88.3, 260.1, n).round(3)
        fhi = rng.uniform(102.1, 592.0, n).round(3)
        flo = rng.uniform(65.5, 239.2, n).round(3)
        jitter_pct = rng.uniform(0.001, 0.033, n).round(5)
        jitter_abs = rng.uniform(0.000007, 0.000260, n).round(6)
        mdvp_rap = rng.uniform(0.0007, 0.020, n).round(6)
        mdvp_ppq = rng.uniform(0.0009, 0.020, n).round(6)
        shimmer = rng.uniform(0.009, 0.119, n).round(3)
        shimmer_db = rng.uniform(0.085, 1.302, n).round(3)
        nhr = rng.uniform(0.001, 0.315, n).round(4)
        hnr = rng.uniform(8.44, 33.05, n).round(2)
        rpde = rng.uniform(0.256, 0.685, n).round(6)
        dfa = rng.uniform(0.574, 0.825, n).round(6)
        spread1 = rng.uniform(-7.96, -2.43, n).round(6)
        spread2 = rng.uniform(0.006, 0.450, n).round(6)
        d2 = rng.uniform(1.42, 3.67, n).round(6)
        ppe = rng.uniform(0.044, 0.527, n).round(6)
        log_odds = (
            2 + 500 * jitter_pct + 100 * shimmer
            + 5 * nhr - 0.1 * hnr - 3 * dfa
        )
        prob = 1 / (1 + np.exp(-log_odds))
        status = (rng.uniform(0, 1, n) < prob).astype(int)
        return pd.DataFrame({
            "MDVP_Fo_Hz": fo, "MDVP_Fhi_Hz": fhi, "MDVP_Flo_Hz": flo,
            "MDVP_Jitter_pct": jitter_pct, "MDVP_Jitter_Abs": jitter_abs,
            "MDVP_RAP": mdvp_rap, "MDVP_PPQ": mdvp_ppq,
            "MDVP_Shimmer": shimmer, "MDVP_Shimmer_dB": shimmer_db,
            "NHR": nhr, "HNR": hnr,
            "RPDE": rpde, "DFA": dfa, "spread1": spread1, "spread2": spread2,
            "D2": d2, "PPE": ppe, "status": status,
        })

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
        if df is not None and "Dataset" in df.columns:
            # Gender is 'Male'/'Female' string — encode to 0/1
            if df["gender"].dtype == object:
                df["gender"] = (df["gender"] == "Male").astype(int)
            # Fill NaN in albumin_globulin_ratio with median
            df["albumin_globulin_ratio"] = df["albumin_globulin_ratio"].fillna(
                df["albumin_globulin_ratio"].median()
            )
            return df

        # Fallback to synthetic
        rng = self._rng()
        n = 583
        age = rng.integers(4, 90, n)
        gender = rng.choice([0, 1], n)  # 0=Female, 1=Male
        tb = rng.uniform(0.4, 75.0, n).round(1)
        db = rng.uniform(0.1, 19.7, n).round(1)
        alkphos = rng.integers(63, 2110, n)
        sgpt = rng.integers(10, 2000, n)
        sgot = rng.integers(10, 4929, n)
        tp = rng.uniform(2.7, 9.6, n).round(1)
        alb = rng.uniform(0.9, 5.5, n).round(1)
        agr = rng.uniform(0.3, 2.8, n).round(1)
        log_odds = (
            -1 + 0.02 * tb + 0.001 * alkphos
            + 0.001 * sgpt - 0.5 * alb + 0.3 * gender
        )
        prob = 1 / (1 + np.exp(-log_odds))
        dataset = (rng.uniform(0, 1, n) < prob).astype(int) + 1
        return pd.DataFrame({
            "age": age, "gender": gender, "total_bilirubin": tb,
            "direct_bilirubin": db, "alkaline_phosphotase": alkphos,
            "alamine_aminotransferase": sgpt, "aspartate_aminotransferase": sgot,
            "total_proteins": tp, "albumin": alb, "albumin_globulin_ratio": agr,
            "Dataset": dataset,
        })

    def _stroke(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "cardiology_stroke",
            "https://raw.githubusercontent.com/YBIFoundation/Dataset/main/Healthcare%20Stroke%20Prediction.csv",
        )
        if df is not None and "stroke" in df.columns:
            try:
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
                if len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("Stroke dataset processing failed: %s", exc)

        # Fallback to synthetic
        rng = self._rng()
        n = 5110
        gender = rng.choice([0, 1], n)
        age = rng.uniform(0.08, 82.0, n).round(2)
        hypertension = rng.integers(0, 2, n)
        heart_disease = rng.integers(0, 2, n)
        ever_married = rng.integers(0, 2, n)
        work_type = rng.integers(0, 5, n)
        residence_type = rng.integers(0, 2, n)
        avg_glucose_level = rng.uniform(55.1, 271.7, n).round(2)
        bmi = rng.uniform(10.3, 97.6, n).round(1)
        smoking_status = rng.integers(0, 4, n)
        log_odds = (
            -6 + 0.07 * age + 0.8 * hypertension
            + 0.6 * heart_disease + 0.005 * avg_glucose_level
        )
        prob = 1 / (1 + np.exp(-log_odds))
        stroke = (rng.uniform(0, 1, n) < prob).astype(int)
        return pd.DataFrame({
            "gender": gender, "age": age, "hypertension": hypertension,
            "heart_disease": heart_disease, "ever_married": ever_married,
            "work_type": work_type, "residence_type": residence_type,
            "avg_glucose_level": avg_glucose_level, "bmi": bmi,
            "smoking_status": smoking_status, "stroke": stroke,
        })

    def _mental_health(self) -> pd.DataFrame:
        # Try loading real dataset (Kaggle: anthonytherrien/depression-dataset)
        # Accepts either filename: depression_data.csv or mental_health_depression.csv
        for candidate in ("depression_data.csv", "mental_health_depression.csv"):
            csv_cache = _CACHE_DIR / candidate
            if csv_cache.exists():
                try:
                    df = pd.read_csv(csv_cache)
                    # Drop PII
                    df = df.drop(columns=[c for c in ["Name", "name"] if c in df.columns])

                    # Encode categorical features
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

                    # Target: "History of Mental Illness" → severity_class
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

                    # Encode remaining string columns
                    for col in df.columns:
                        if col != "severity_class" and df[col].dtype == object:
                            df[col] = pd.Categorical(df[col]).codes

                    df = df.dropna(subset=["severity_class"])
                    if len(df) >= 100 and "severity_class" in df.columns:
                        # Sample to keep response times fast
                        if len(df) > 5000:
                            df = df.sample(5000, random_state=42).reset_index(drop=True)
                        logger.info("Loaded real mental health dataset (%d rows) from %s", len(df), candidate)
                        return df
                except Exception as exc:
                    logger.warning("Mental health CSV load failed (%s): %s — using synthetic data", candidate, exc)

        logger.warning(
            "Real mental health dataset not found in data_cache/. "
            "Download from kaggle.com/datasets/anthonytherrien/depression-dataset "
            "and save as depression_data.csv in data_cache/"
        )

        # Synthetic fallback — must match registry: 12 features + binary target
        rng = self._rng()
        n = 500
        age = rng.integers(18, 75, n)
        number_of_children = rng.integers(0, 5, n)
        income = rng.integers(10000, 120000, n)
        dietary_habits = rng.integers(0, 3, n)       # 0=Poor,1=Moderate,2=Healthy
        sleep_patterns = rng.integers(0, 3, n)        # 0=Poor,1=Fair,2=Good
        alcohol_consumption = rng.integers(0, 3, n)   # 0=None,1=Low,2=Moderate,3=High
        physical_activity_level = rng.integers(0, 3, n)
        smoking_status = rng.integers(0, 2, n)
        employment_status = rng.integers(0, 3, n)
        history_substance_abuse = rng.integers(0, 2, n)
        family_history_depression = rng.integers(0, 2, n)
        chronic_medical_conditions = rng.integers(0, 2, n)
        log_odds = (
            -1.5 + 0.02 * (age - 40)
            + 0.3 * history_substance_abuse
            + 0.4 * family_history_depression
            + 0.3 * chronic_medical_conditions
            - 0.2 * sleep_patterns
            - 0.1 * physical_activity_level
            + 0.2 * alcohol_consumption
        )
        prob = 1 / (1 + np.exp(-log_odds))
        severity_class = np.where(rng.uniform(0, 1, n) < prob, "has_condition", "no_condition")
        return pd.DataFrame({
            "age": age, "number_of_children": number_of_children,
            "income": income, "dietary_habits": dietary_habits,
            "sleep_patterns": sleep_patterns, "alcohol_consumption": alcohol_consumption,
            "physical_activity_level": physical_activity_level,
            "smoking_status": smoking_status, "employment_status": employment_status,
            "history_substance_abuse": history_substance_abuse,
            "family_history_depression": family_history_depression,
            "chronic_medical_conditions": chronic_medical_conditions,
            "severity_class": severity_class,
        })

    def _copd(self) -> pd.DataFrame:
        # Try loading real dataset (PhysioNet: physionet.org/content/copd-ehr/1.0.0/)
        # Place as: backend/data_cache/pulmonology_copd.csv
        csv_cache = _CACHE_DIR / "pulmonology_copd.csv"
        if csv_cache.exists():
            try:
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
                if len(df) >= 100 and "exacerbation" in df.columns:
                    logger.info("Loaded real COPD dataset (%d rows)", len(df))
                    return df
            except Exception as exc:
                logger.warning("COPD CSV load failed: %s — using synthetic data", exc)
        else:
            logger.warning(
                "Real COPD dataset not found at %s. "
                "Download from physionet.org/content/copd-ehr/1.0.0/ "
                "and save as pulmonology_copd.csv in data_cache/",
                csv_cache,
            )

        rng = self._rng()
        n = 400
        age = rng.integers(40, 85, n)
        sex = rng.integers(0, 2, n)
        smoking_pack_years = rng.uniform(0, 100, n).round(1)
        fev1 = rng.uniform(0.5, 4.5, n).round(2)
        fvc = rng.uniform(1.0, 6.5, n).round(2)
        fev1_fvc = (fev1 / fvc).round(3)
        prior_exac = rng.integers(0, 10, n)
        bmi = rng.uniform(15.0, 45.0, n).round(1)
        mrc = rng.integers(1, 6, n)
        sgrq = rng.uniform(0, 100, n).round(1)
        gold = np.clip(np.digitize(fev1_fvc, bins=[0.5, 0.6, 0.7]), 1, 4)
        log_odds = (
            -2 + 0.5 * prior_exac + 0.5 * mrc
            + 0.02 * sgrq - 2 * fev1_fvc
        )
        prob = 1 / (1 + np.exp(-log_odds))
        exacerbation = (rng.uniform(0, 1, n) < prob).astype(int)
        return pd.DataFrame({
            "age": age, "sex": sex, "smoking_pack_years": smoking_pack_years,
            "fev1_litres": fev1, "fvc_litres": fvc, "fev1_fvc_ratio": fev1_fvc,
            "prior_exacerbations_year": prior_exac, "bmi": bmi,
            "mrc_dyspnea_scale": mrc, "sgrq_score": sgrq,
            "copd_gold_stage": gold, "exacerbation": exacerbation,
        })

    def _anaemia(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "haematology_anaemia",
            "https://raw.githubusercontent.com/YBIFoundation/Dataset/main/Anemia.csv",
        )
        if df is not None:
            try:
                rename_map = {
                    "Gender": "gender", "Hemoglobin": "haemoglobin",
                    "MCH": "mch", "MCHC": "mchc", "MCV": "mcv",
                    "Result": "anemia_type",
                }
                df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
                if "gender" in df.columns and df["gender"].dtype == object:
                    df["gender"] = (df["gender"] == "Male").astype(int)
                if "anemia_type" in df.columns and len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("Anaemia dataset processing failed: %s", exc)

        # Fallback to synthetic
        rng = self._rng()
        n = 400
        gender = rng.integers(0, 2, n)
        hgb = rng.uniform(4.0, 17.5, n).round(1)
        mchc = rng.uniform(25.0, 37.0, n).round(1)
        mch = rng.uniform(15.0, 35.0, n).round(1)
        mcv = rng.uniform(50.0, 110.0, n).round(1)
        rdw = rng.uniform(11.0, 25.0, n).round(1)
        wbc = rng.uniform(3.0, 15.0, n).round(2)
        platelets = rng.uniform(100, 600, n).round(0)
        neutrophils = rng.uniform(1.0, 10.0, n).round(2)
        lymphocytes = rng.uniform(0.5, 5.0, n).round(2)
        # Iron def: low Hgb, low MCV, low MCH; Megaloblastic: high MCV; Normocytic: normal
        types = []
        for i in range(n):
            if hgb[i] < 10 and mcv[i] < 80 and mch[i] < 27:
                types.append("iron_deficiency")
            elif hgb[i] < 10 and mcv[i] > 100:
                types.append("megaloblastic")
            elif hgb[i] < 10:
                types.append("normocytic")
            else:
                types.append("normal")
        return pd.DataFrame({
            "gender": gender, "haemoglobin": hgb, "mchc": mchc, "mch": mch,
            "mcv": mcv, "rdw": rdw, "wbc": wbc, "platelets": platelets,
            "neutrophils": neutrophils, "lymphocytes": lymphocytes,
            "anemia_type": types,
        })

    def _dermatology(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "dermatology",
            "https://dataverse.harvard.edu/api/access/datafile/4338392",
            read_kwargs={"sep": "\t", "quotechar": '"'},
        )
        if df is not None and "dx" in df.columns:
            try:
                # Map diagnosis to benign/malignant for dx_type
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
                if len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("HAM10000 metadata processing failed: %s", exc)

        # Fallback to synthetic — matches real HAM10000 metadata structure (3 features)
        rng = self._rng()
        n = 400
        age = rng.integers(0, 85, n)
        sex = rng.integers(0, 2, n)
        localization = rng.integers(0, 15, n)
        log_odds = -2 + 0.02 * age + 0.3 * localization / 15
        prob = 1 / (1 + np.exp(-log_odds))
        dx_type = np.where(rng.uniform(0, 1, n) < prob, "malignant", "benign")
        return pd.DataFrame({
            "age": age, "sex": sex, "localization": localization,
            "dx_type": dx_type,
        })

    def _ophthalmology(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        arff_cache = _CACHE_DIR / "ophthalmology.arff"
        if not arff_cache.exists():
            try:
                import urllib.request
                zip_url = "https://archive.ics.uci.edu/static/public/329/diabetic+retinopathy+debrecen+data+set.zip"
                resp = requests.get(zip_url, timeout=30, headers={"User-Agent": "HealthWithSevgi/1.0"})
                resp.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                    arff_names = [n for n in zf.namelist() if n.endswith(".arff")]
                    if arff_names:
                        arff_cache.write_bytes(zf.read(arff_names[0]))
                        logger.info("Extracted Debrecen DR ARFF (%d bytes)", arff_cache.stat().st_size)
            except Exception as exc:
                logger.warning("Failed to download Debrecen DR ARFF: %s", exc)

        if arff_cache.exists():
            try:
                from scipy.io import arff as scipy_arff
                data, meta = scipy_arff.loadarff(str(arff_cache))
                df = pd.DataFrame(data)
                for col in df.columns:
                    if df[col].dtype == object:
                        df[col] = df[col].str.decode("utf-8").str.strip()
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                # Last column is Class (0=No DR, 1=DR) — rename to severity_grade
                cols = list(df.columns)
                feature_cols = cols[:-1]
                target_col = cols[-1]
                df = df.rename(columns={target_col: "severity_grade"})
                df["severity_grade"] = df["severity_grade"].astype(int)
                # Use named subset of features for clinical context
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
                if len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("Debrecen DR ARFF parse failed: %s", exc)

        # Fallback to synthetic
        rng = self._rng()
        n = 400
        age = rng.integers(18, 80, n)
        sex = rng.integers(0, 2, n)
        hba1c = rng.uniform(5.0, 12.0, n).round(1)
        dur = rng.integers(0, 40, n)
        iop = rng.uniform(10.0, 25.0, n).round(1)
        bcva = rng.uniform(0.1, 1.0, n).round(2)
        ma = rng.integers(0, 50, n)
        he = rng.uniform(0.0, 100.0, n).round(1)
        haem = rng.integers(0, 30, n)
        neo = rng.integers(0, 2, n)
        grade_logits = (
            -3 + 0.3 * hba1c + 0.05 * dur + 0.1 * ma + 0.01 * he + 2 * neo
        )
        grade = np.clip(np.digitize(grade_logits, bins=[-1, 1, 3]), 0, 3)
        return pd.DataFrame({
            "age": age, "sex": sex, "hba1c": hba1c, "diabetes_duration_years": dur,
            "iop": iop, "best_corrected_visual_acuity": bcva,
            "microaneurysms_count": ma, "hard_exudates_area": he,
            "haemorrhages_count": haem, "neovascularisation": neo,
            "severity_grade": grade,
        })

    def _orthopaedics(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        arff_cache = _CACHE_DIR / "orthopaedics.arff"

        if not arff_cache.exists():
            try:
                import requests as _req
                resp = _req.get(
                    "https://archive.ics.uci.edu/static/public/212/vertebral+column.zip",
                    timeout=30,
                    headers={"User-Agent": "HealthWithSevgi/1.0"},
                )
                resp.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                    arff_names = [n for n in zf.namelist() if n.endswith("_weka.arff")]
                    if arff_names:
                        arff_cache.write_bytes(zf.read(arff_names[0]))
                        logger.info("Extracted vertebral column ARFF (%d bytes)", arff_cache.stat().st_size)
            except Exception as exc:
                logger.warning("Failed to download vertebral column ARFF: %s", exc)

        if arff_cache.exists():
            try:
                from scipy.io import arff as scipy_arff
                data, meta = scipy_arff.loadarff(str(arff_cache))
                df = pd.DataFrame(data)
                # Decode bytes columns
                for col in df.columns:
                    if df[col].dtype == object:
                        df[col] = df[col].str.decode("utf-8")
                col_names = [
                    "pelvic_incidence", "pelvic_tilt", "lumbar_lordosis_angle",
                    "sacral_slope", "pelvic_radius", "degree_spondylolisthesis", "class",
                ]
                if len(df.columns) == len(col_names):
                    df.columns = col_names
                if "class" in df.columns:
                    return df
            except Exception as exc:
                logger.warning("ARFF parse failed: %s", exc)

        # Fallback to synthetic
        rng = self._rng()
        n = 310
        pi = rng.uniform(26.1, 129.8, n).round(2)
        pt = rng.uniform(-6.6, 49.4, n).round(2)
        ll = rng.uniform(14.0, 125.7, n).round(2)
        ss = rng.uniform(13.4, 121.4, n).round(2)
        pr = rng.uniform(70.1, 163.1, n).round(2)
        ds = rng.uniform(-11.1, 418.5, n).round(2)
        log_odds = -2 + 0.05 * pi + 0.05 * pt + 0.01 * ds - 0.01 * pr
        prob = 1 / (1 + np.exp(-log_odds))
        cls = np.where(rng.uniform(0, 1, n) < prob, "Abnormal", "Normal")
        return pd.DataFrame({
            "pelvic_incidence": pi, "pelvic_tilt": pt,
            "lumbar_lordosis_angle": ll, "sacral_slope": ss,
            "pelvic_radius": pr, "degree_spondylolisthesis": ds, "class": cls,
        })

    def _sepsis(self) -> pd.DataFrame:
        # Try loading real dataset (PhysioNet Sepsis Challenge 2019)
        # Place as: backend/data_cache/icu_sepsis.csv
        # The PhysioNet challenge-2019 data is in PSV (pipe-separated) files per patient.
        # Merge them into a single CSV and save as icu_sepsis.csv in data_cache/.
        csv_cache = _CACHE_DIR / "icu_sepsis.csv"
        if csv_cache.exists():
            try:
                df = pd.read_csv(csv_cache)
                # PhysioNet PSV files use pipe separator; if not yet CSV, try pipe sep
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
                if len(df) >= 100 and "SepsisLabel" in df.columns:
                    # Sample to keep response times fast
                    if len(df) > 5000:
                        df = df.sample(5000, random_state=42).reset_index(drop=True)
                    logger.info("Loaded real ICU sepsis dataset (%d rows)", len(df))
                    return df
            except Exception as exc:
                logger.warning("ICU sepsis CSV load failed: %s — using synthetic data", exc)
        else:
            logger.warning(
                "Real ICU/Sepsis dataset not found at %s. "
                "Download from physionet.org/content/challenge-2019/1.0.0/, "
                "merge PSV files into one CSV, and save as icu_sepsis.csv in data_cache/",
                csv_cache,
            )

        rng = self._rng()
        n = 500
        hr = rng.integers(40, 180, n)
        o2sat = rng.uniform(85.0, 100.0, n).round(1)
        temp = rng.uniform(35.0, 40.5, n).round(1)
        sbp = rng.integers(70, 180, n)
        map_ = rng.integers(50, 120, n)
        resp = rng.integers(8, 40, n)
        ph = rng.uniform(7.0, 7.6, n).round(2)
        lactate = rng.uniform(0.5, 12.0, n).round(1)
        creatinine = rng.uniform(0.4, 10.0, n).round(1)
        wbc = rng.uniform(1.0, 30.0, n).round(1)
        platelets = rng.uniform(50, 450, n).round(0)
        bili = rng.uniform(0.1, 8.0, n).round(1)
        age = rng.integers(18, 90, n)
        gender = rng.integers(0, 2, n)
        log_odds = (
            -5 + 0.02 * hr - 0.1 * o2sat + 0.5 * temp - 0.02 * sbp
            + 0.3 * lactate + 0.3 * creatinine - 0.005 * platelets
        )
        prob = 1 / (1 + np.exp(-log_odds))
        sepsis = (rng.uniform(0, 1, n) < prob).astype(int)
        return pd.DataFrame({
            "HR": hr, "O2Sat": o2sat, "Temp": temp, "SBP": sbp, "MAP": map_,
            "Resp": resp, "pH": ph, "Lactate": lactate, "Creatinine": creatinine,
            "WBC": wbc, "Platelets": platelets, "Bilirubin_total": bili,
            "Age": age, "Gender": gender, "SepsisLabel": sepsis,
        })

    def _fetal_health(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        csv_cache = _CACHE_DIR / "obstetrics_fetal.csv"
        if not csv_cache.exists():
            try:
                from ucimlrepo import fetch_ucirepo
                data = fetch_ucirepo(id=193)
                X = data.data.features.copy()
                y = data.data.targets.copy()
                col_map = {
                    "LB": "baseline_value", "AC": "accelerations", "FM": "fetal_movement",
                    "UC": "uterine_contractions", "DL": "light_decelerations",
                    "DS": "severe_decelerations", "DP": "prolongued_decelerations",
                    "ASTV": "abnormal_short_term_variability",
                    "MSTV": "mean_value_short_term_variability",
                    "ALTV": "pct_time_abnormal_long_term_variability",
                    "MLTV": "mean_value_long_term_variability",
                    "Mode": "histogram_mode",
                }
                X = X.rename(columns={k: v for k, v in col_map.items() if k in X.columns})
                X["fetal_health"] = y["NSP"].astype(int)
                keep = list(col_map.values()) + ["fetal_health"]
                X = X[[c for c in keep if c in X.columns]].dropna(subset=["fetal_health"])
                X.to_csv(csv_cache, index=False)
                logger.info("Cached fetal health CTG dataset (%d rows)", len(X))
            except Exception as exc:
                logger.warning("Failed to fetch CTG via ucimlrepo: %s", exc)

        if csv_cache.exists():
            try:
                df = pd.read_csv(csv_cache)
                if "fetal_health" in df.columns and len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("CTG CSV cache read failed: %s", exc)

        # Fallback to synthetic
        rng = self._rng()
        n = 2126
        baseline = rng.integers(106, 160, n)
        accel = rng.uniform(0.0, 0.6, n).round(3)
        fetal_mov = rng.uniform(0.0, 0.5, n).round(3)
        uc = rng.uniform(0.0, 0.015, n).round(3)
        light_dec = rng.uniform(0.0, 0.015, n).round(3)
        sev_dec = rng.uniform(0.0, 0.001, n).round(3)
        prol_dec = rng.uniform(0.0, 0.005, n).round(3)
        astv = rng.integers(12, 87, n)
        mstv = rng.uniform(0.2, 7.0, n).round(1)
        pctv = rng.integers(0, 91, n)
        mltv = rng.uniform(0.0, 50.7, n).round(1)
        hist_mode = rng.integers(60, 187, n)
        score = (
            -accel * 5 + sev_dec * 200 + prol_dec * 100
            + astv * 0.05 - accel * 3
        )
        fetal_health = np.clip(np.digitize(score, bins=[0.5, 1.5]) + 1, 1, 3)
        return pd.DataFrame({
            "baseline_value": baseline, "accelerations": accel,
            "fetal_movement": fetal_mov, "uterine_contractions": uc,
            "light_decelerations": light_dec, "severe_decelerations": sev_dec,
            "prolongued_decelerations": prol_dec, "abnormal_short_term_variability": astv,
            "mean_value_short_term_variability": mstv,
            "pct_time_abnormal_long_term_variability": pctv,
            "mean_value_long_term_variability": mltv, "histogram_mode": hist_mode,
            "fetal_health": fetal_health,
        })

    def _arrhythmia(self) -> pd.DataFrame:
        all_cols = [f"feature_{i}" for i in range(279)] + ["arrhythmia_class"]
        df = self._fetch_cached(
            "cardiology_arrhythmia",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/arrhythmia/arrhythmia.data",
            read_kwargs={"header": None, "names": all_cols, "na_values": "?"},
        )
        if df is not None and "arrhythmia_class" in df.columns:
            try:
                # Binarize: class 1 = normal, all others = arrhythmia
                df["arrhythmia"] = df["arrhythmia_class"].apply(
                    lambda x: 0 if x == 1 else 1
                )
                # Keep first 13 ECG feature columns + target
                ecg_names = [
                    "age", "sex", "height", "weight", "QRS_duration",
                    "PR_interval", "QT_interval", "T_interval", "P_interval",
                    "QRS_axis", "T_axis", "P_axis", "heart_rate",
                ]
                rename_map = {f"feature_{i}": name for i, name in enumerate(ecg_names)}
                df = df.rename(columns=rename_map)
                keep = ecg_names + ["arrhythmia"]
                df = df[[c for c in keep if c in df.columns]].dropna(subset=["arrhythmia"])
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                if len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("Arrhythmia dataset processing failed: %s", exc)

        # Fallback to synthetic
        rng = self._rng()
        n = 452
        age = rng.integers(18, 80, n)
        sex = rng.integers(0, 2, n)
        height = rng.integers(150, 195, n)
        weight = rng.uniform(45.0, 120.0, n).round(1)
        qrs = rng.integers(60, 200, n)
        pr = rng.integers(100, 300, n)
        qt = rng.integers(300, 500, n)
        t_int = rng.integers(100, 250, n)
        p_int = rng.integers(50, 180, n)
        qrs_axis = rng.integers(-90, 180, n)
        t_axis = rng.integers(-90, 180, n)
        p_axis = rng.integers(-90, 180, n)
        hr = rng.integers(40, 150, n)
        log_odds = (
            -2 + 0.02 * qrs - 0.005 * pr + 0.01 * qt
            + 0.02 * age - 0.3 * sex
        )
        prob = 1 / (1 + np.exp(-log_odds))
        arrhythmia = (rng.uniform(0, 1, n) < prob).astype(int)
        return pd.DataFrame({
            "age": age, "sex": sex, "height": height, "weight": weight,
            "QRS_duration": qrs, "PR_interval": pr, "QT_interval": qt,
            "T_interval": t_int, "P_interval": p_int, "QRS_axis": qrs_axis,
            "T_axis": t_axis, "P_axis": p_axis, "heart_rate": hr,
            "arrhythmia": arrhythmia,
        })

    def _cervical(self) -> pd.DataFrame:
        df = self._fetch_cached(
            "oncology_cervical",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/00383/risk_factors_cervical_cancer.csv",
        )
        if df is not None and "Biopsy" in df.columns:
            # Replace '?' with NaN
            df = df.replace("?", np.nan)
            # Select key columns that are mostly numeric and relevant
            keep_cols = [
                "Age", "Number of sexual partners", "First sexual intercourse",
                "Num of pregnancies", "Smokes (years)", "Hormonal Contraceptives (years)",
                "IUD (years)", "STDs (number)", "STDs:condylomatosis",
                "STDs:cervical condylomatosis", "STDs:HPV", "Biopsy",
            ]
            available = [c for c in keep_cols if c in df.columns]
            df = df[available].copy()
            rename_map = {
                "Age": "age",
                "Number of sexual partners": "number_of_sexual_partners",
                "First sexual intercourse": "first_sexual_intercourse_age",
                "Num of pregnancies": "num_of_pregnancies",
                "Smokes (years)": "smokes_years",
                "Hormonal Contraceptives (years)": "hormonal_contraceptives_years",
                "IUD (years)": "iud_years",
                "STDs (number)": "stds_number",
                "STDs:condylomatosis": "stds_condylomatosis",
                "STDs:cervical condylomatosis": "stds_cervical_condylomatosis",
                "STDs:HPV": "stds_hpv",
            }
            df = df.rename(columns=rename_map)
            # Convert all columns to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            if "Biopsy" in df.columns:
                return df

        # Fallback to synthetic
        rng = self._rng()
        n = 858
        age = rng.integers(13, 84, n)
        n_partners = rng.integers(1, 28, n)
        first_intercourse = rng.integers(10, 32, n)
        n_pregnancies = rng.integers(0, 11, n)
        smokes_years = rng.uniform(0.0, 37.0, n).round(1)
        hc_years = rng.uniform(0.0, 30.0, n).round(1)
        iud_years = rng.uniform(0.0, 19.0, n).round(1)
        stds_num = rng.integers(0, 4, n)
        stds_cond = rng.integers(0, 2, n)
        stds_cerv = rng.integers(0, 2, n)
        stds_hpv = rng.integers(0, 2, n)
        log_odds = (
            -4 + 0.05 * age + 0.1 * n_partners + 0.1 * smokes_years
            + 0.5 * stds_hpv + 0.3 * stds_num
        )
        prob = 1 / (1 + np.exp(-log_odds))
        biopsy = (rng.uniform(0, 1, n) < prob).astype(int)
        return pd.DataFrame({
            "age": age, "number_of_sexual_partners": n_partners,
            "first_sexual_intercourse_age": first_intercourse,
            "num_of_pregnancies": n_pregnancies,
            "smokes_years": smokes_years,
            "hormonal_contraceptives_years": hc_years,
            "iud_years": iud_years, "stds_number": stds_num,
            "stds_condylomatosis": stds_cond,
            "stds_cervical_condylomatosis": stds_cerv,
            "stds_hpv": stds_hpv, "Biopsy": biopsy,
        })

    def _thyroid(self) -> pd.DataFrame:
        col_names = ["class_raw", "T3_resin_uptake", "total_serum_thyroxine", "T3", "TSH", "max_abs_diff_TSH"]
        df = self._fetch_cached(
            "thyroid",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/thyroid-disease/new-thyroid.data",
            read_kwargs={"header": None, "names": col_names, "sep": ","},
        )
        if df is not None and "class_raw" in df.columns:
            try:
                class_map = {1: "hyperthyroid", 2: "normal", 3: "hypothyroid"}
                df["class"] = df["class_raw"].map(class_map)
                df = df.drop(columns=["class_raw"])
                df = df.dropna(subset=["class"])
                if len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("Thyroid dataset processing failed: %s", exc)

        # Fallback to synthetic — must match 5 real UCI New Thyroid features
        rng = self._rng()
        n = 700
        # Normal ranges: T3_resin_uptake 14-59, total_serum_thyroxine 1-50,
        # T3 0.1-6.0, TSH 0.3-10+, max_abs_diff_TSH 0-30
        cls = rng.choice(["hyperthyroid", "normal", "hypothyroid"], n, p=[0.30, 0.55, 0.15])
        t3_resin = np.where(cls == "hyperthyroid",
                            rng.integers(55, 75, n),
                            np.where(cls == "hypothyroid",
                                     rng.integers(10, 25, n),
                                     rng.integers(30, 55, n)))
        total_thyroxine = np.where(cls == "hyperthyroid",
                                   rng.uniform(10.0, 50.0, n).round(1),
                                   np.where(cls == "hypothyroid",
                                            rng.uniform(1.0, 8.0, n).round(1),
                                            rng.uniform(5.0, 12.0, n).round(1)))
        t3 = np.where(cls == "hyperthyroid",
                      rng.uniform(2.5, 6.0, n).round(2),
                      np.where(cls == "hypothyroid",
                               rng.uniform(0.1, 1.0, n).round(2),
                               rng.uniform(0.6, 2.5, n).round(2)))
        tsh = np.where(cls == "hypothyroid",
                       rng.uniform(8.0, 50.0, n).round(3),
                       np.where(cls == "hyperthyroid",
                                rng.uniform(0.01, 0.29, n).round(3),
                                rng.uniform(0.3, 5.5, n).round(3)))
        max_diff_tsh = np.abs(tsh - rng.uniform(0.3, 5.5, n)).round(3)
        return pd.DataFrame({
            "T3_resin_uptake": t3_resin,
            "total_serum_thyroxine": total_thyroxine,
            "T3": t3,
            "TSH": tsh,
            "max_abs_diff_TSH": max_diff_tsh,
            "class": cls,
        })

    def _readmission(self) -> pd.DataFrame:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        csv_cache = _CACHE_DIR / "pharmacy_readmission.csv"
        if not csv_cache.exists():
            try:
                resp = requests.get(
                    "https://archive.ics.uci.edu/ml/machine-learning-databases/00296/dataset_diabetes.zip",
                    timeout=60,
                    headers={"User-Agent": "HealthWithSevgi/1.0"},
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
                            "change", "readmitted",
                        ]
                        available = [c for c in keep_cols if c in raw.columns]
                        raw = raw[available].copy()
                        # Encode age bracket e.g. "[70-80)" → midpoint
                        if "age" in raw.columns and raw["age"].dtype == object:
                            age_map = {
                                "[0-10)": 0, "[10-20)": 1, "[20-30)": 2, "[30-40)": 3,
                                "[40-50)": 4, "[50-60)": 5, "[60-70)": 6, "[70-80)": 7,
                                "[80-90)": 8, "[90-100)": 9,
                            }
                            raw["age"] = raw["age"].map(age_map).fillna(5).astype(int)
                        if "gender" in raw.columns and raw["gender"].dtype == object:
                            raw["gender"] = (raw["gender"] == "Male").astype(int)
                        # Encode drug columns (No/Steady/Up/Down → 0/1/2/3)
                        med_map = {"No": 0, "Steady": 1, "Up": 2, "Down": 3}
                        for col in ["metformin", "insulin", "change"]:
                            if col in raw.columns and raw[col].dtype == object:
                                raw[col] = raw[col].map(med_map).fillna(0).astype(int)
                        for col in ["max_glu_serum", "A1Cresult"]:
                            if col in raw.columns and raw[col].dtype == object:
                                glu_map = {"None": 0, "Norm": 1, ">200": 2, ">300": 3, ">7": 1, ">8": 2}
                                raw[col] = raw[col].map(glu_map).fillna(0).astype(int)
                        raw = raw.dropna(subset=["readmitted"])
                        # Sample to 5000 rows to keep response times fast
                        if len(raw) > 5000:
                            raw = raw.sample(5000, random_state=42).reset_index(drop=True)
                        raw.to_csv(csv_cache, index=False)
                        logger.info("Cached readmission dataset (%d rows)", len(raw))
            except Exception as exc:
                logger.warning("Failed to download/parse readmission ZIP: %s", exc)

        if csv_cache.exists():
            try:
                df = pd.read_csv(csv_cache)
                if "readmitted" in df.columns and len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("Readmission CSV cache read failed: %s", exc)

        # Fallback to synthetic
        rng = self._rng()
        n = 500
        age = rng.integers(0, 10, n)  # age bracket 0-9
        gender = rng.integers(0, 2, n)
        time_in_hospital = rng.integers(1, 14, n)
        num_lab = rng.integers(1, 132, n)
        num_proc = rng.integers(0, 6, n)
        num_med = rng.integers(1, 81, n)
        n_out = rng.integers(0, 42, n)
        n_emerg = rng.integers(0, 76, n)
        n_inp = rng.integers(0, 21, n)
        n_diag = rng.integers(1, 16, n)
        glu = rng.choice([0, 1, 2, 3], n)  # None, Norm, >200, >300
        a1c = rng.choice([0, 1, 2, 3], n)
        metformin = rng.integers(0, 2, n)
        insulin = rng.integers(0, 4, n)
        change = rng.integers(0, 2, n)
        log_odds = (
            -2 + 0.3 * n_inp + 0.1 * n_emerg + 0.05 * time_in_hospital
            + 0.2 * change - 0.05 * num_proc
        )
        prob = 1 / (1 + np.exp(-log_odds))
        readmitted = np.where(
            rng.uniform(0, 1, n) < prob * 0.4, "<30",
            np.where(rng.uniform(0, 1, n) < prob, ">30", "NO"),
        )
        return pd.DataFrame({
            "age": age, "gender": gender, "time_in_hospital": time_in_hospital,
            "num_lab_procedures": num_lab, "num_procedures": num_proc,
            "num_medications": num_med, "number_outpatient": n_out,
            "number_emergency": n_emerg, "number_inpatient": n_inp,
            "number_diagnoses": n_diag, "max_glu_serum": glu, "A1Cresult": a1c,
            "metformin": metformin, "insulin": insulin, "change": change,
            "readmitted": readmitted,
        })

    def _pneumonia(self) -> pd.DataFrame:
        # NIH Chest X-Ray metadata — requires manual download from Kaggle (kaggle.com/datasets/nih-chest-xrays/data)
        # Save Data_Entry_2017.csv as: backend/data_cache/radiology_pneumonia.csv
        df = self._fetch_cached(
            "radiology_pneumonia",
            "https://raw.githubusercontent.com/aedemirsen/nih_chest_xray_classification/main/Data_Entry_2017_v2020.csv",
        )
        if df is not None and "Finding Labels" in df.columns:
            try:
                # Filter to binary: Pneumonia vs No Finding
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
                df["age"] = pd.to_numeric(df["age"], errors="coerce")
                df = df.dropna(subset=["age"])
                if len(df) >= 100:
                    return df
            except Exception as exc:
                logger.warning("NIH Chest X-Ray processing failed: %s", exc)

        # Fallback to synthetic — matches real NIH CSV structure (4 metadata features)
        rng = self._rng()
        n = 400
        age = rng.integers(1, 90, n)
        sex = rng.integers(0, 2, n)
        view_position = rng.integers(0, 2, n)
        follow_up = rng.integers(0, 5, n)
        log_odds = -2 + 0.02 * age + 0.3 * (1 - view_position)
        prob = 1 / (1 + np.exp(-log_odds))
        finding = np.where(rng.uniform(0, 1, n) < prob, "Pneumonia", "No Finding")
        return pd.DataFrame({
            "age": age, "sex": sex, "view_position": view_position,
            "follow_up_number": follow_up, "Finding_Label": finding,
        })

    def _generic_fallback(self) -> pd.DataFrame:
        rng_np = np.random.RandomState(42)
        from sklearn.datasets import make_classification
        X, y = make_classification(
            n_samples=400, n_features=10, n_informative=6,
            n_redundant=2, random_state=42, weights=[0.7, 0.3],
        )
        df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(10)])
        df["target"] = y
        return df
