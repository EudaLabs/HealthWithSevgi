"""Data exploration and preparation service."""
from __future__ import annotations

import io
import logging
import pathlib
import uuid
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

IMBALANCE_RATIO_THRESHOLD = 3.0
MIN_ROWS = 10
MAX_UPLOAD_MB = 50

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

        # Encode target
        y_raw = df[target_col]
        classes = sorted(y_raw.unique().tolist(), key=str)
        class_to_int = {c: i for i, c in enumerate(classes)}
        y = y_raw.map(class_to_int).values.astype(int)

        # Keep only numeric features (drop target + non-numeric)
        feature_df = df.drop(columns=[target_col])
        feature_df = feature_df.select_dtypes(include=[np.number])
        feature_names = list(feature_df.columns)

        # --- Handle missing values ---
        dist_before = {str(k): int((y == v).sum()) for k, v in class_to_int.items()}

        if settings.missing_strategy == "drop":
            mask = ~feature_df.isna().any(axis=1)
            feature_df = feature_df[mask]
            y = y[mask]
        elif settings.missing_strategy == "median":
            feature_df = feature_df.fillna(feature_df.median(numeric_only=True))
        else:  # mode
            feature_df = feature_df.fillna(feature_df.mode().iloc[0])

        X = feature_df.values.astype(float)

        # --- Train / test split ---
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=settings.test_size, random_state=42, stratify=y
        )

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

        response = PrepResponse(
            session_id=session_id,
            train_size=int(len(X_train)),
            test_size=int(len(X_test)),
            features_count=len(feature_names),
            class_distribution_before=dist_before,
            class_distribution_after=dist_after,
            smote_applied=smote_applied,
            normalization_applied=normalization_applied,
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
        return df

    def _diabetes(self) -> pd.DataFrame:
        pima_cols = [
            "pregnancies", "glucose", "blood_pressure", "skin_thickness",
            "insulin", "bmi", "diabetes_pedigree_function", "age", "Outcome",
        ]
        df = self._fetch_cached(
            "endocrinology_diabetes",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/pima-indians-diabetes/pima-indians-diabetes.data",
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
        shimmer = rng.uniform(0.009, 0.119, n).round(3)
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
            "MDVP_Shimmer": shimmer, "NHR": nhr, "HNR": hnr,
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
        rng = self._rng()
        n = 500
        age = rng.integers(18, 65, n)
        gender = rng.integers(0, 2, n)
        work_pressure = rng.integers(1, 6, n)
        job_satisfaction = rng.integers(1, 6, n)
        sleep_duration = rng.uniform(3.0, 9.0, n).round(1)
        dietary_habits = rng.integers(1, 4, n)
        suicidal_thoughts = rng.integers(0, 2, n)
        work_hours = rng.integers(20, 80, n)
        financial_stress = rng.integers(1, 6, n)
        family_history = rng.integers(0, 2, n)
        score = (
            work_pressure * 2 + financial_stress * 2
            - sleep_duration * 1.5 + suicidal_thoughts * 5
            + family_history * 2 - job_satisfaction
        )
        severity = np.digitize(score, bins=[10, 15, 20])  # 0=minimal,1=mild,2=moderate,3=severe
        severity_class = np.array(["minimal", "mild", "moderate", "severe"])[severity]
        return pd.DataFrame({
            "age": age, "gender": gender, "work_pressure": work_pressure,
            "job_satisfaction": job_satisfaction, "sleep_duration": sleep_duration,
            "dietary_habits": dietary_habits, "suicidal_thoughts": suicidal_thoughts,
            "work_hours": work_hours, "financial_stress": financial_stress,
            "family_history_mental_illness": family_history, "severity_class": severity_class,
        })

    def _copd(self) -> pd.DataFrame:
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
        rng = self._rng()
        n = 400
        age = rng.integers(0, 85, n)
        sex = rng.integers(0, 2, n)
        localization = rng.integers(0, 15, n)
        diam = rng.uniform(1.0, 20.0, n).round(1)
        asymmetry = rng.uniform(0.0, 1.0, n).round(2)
        border = rng.uniform(0.0, 1.0, n).round(2)
        colour = rng.uniform(0.0, 1.0, n).round(2)
        structures = rng.integers(0, 5, n)
        pattern = rng.integers(0, 8, n)
        log_odds = (
            -2 + 3 * asymmetry + 2 * border + 1.5 * colour
            + 0.02 * age - 0.1 * diam
        )
        prob = 1 / (1 + np.exp(-log_odds))
        dx_type = np.where(rng.uniform(0, 1, n) < prob, "malignant", "benign")
        return pd.DataFrame({
            "age": age, "sex": sex, "localization": localization,
            "lesion_diameter_mm": diam, "asymmetry_score": asymmetry,
            "border_irregularity": border, "colour_variation": colour,
            "differential_structures": structures, "dermoscopy_pattern": pattern,
            "dx_type": dx_type,
        })

    def _ophthalmology(self) -> pd.DataFrame:
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
                    "https://archive.ics.uci.edu/ml/machine-learning-databases/00212/column_2C_weka.arff",
                    timeout=20,
                    headers={"User-Agent": "HealthWithSevgi/1.0"},
                )
                resp.raise_for_status()
                arff_cache.write_bytes(resp.content)
                logger.info("Downloaded vertebral column ARFF (%d bytes)", len(resp.content))
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
        rng = self._rng()
        n = 700
        age = rng.integers(1, 90, n)
        sex = rng.integers(0, 2, n)
        on_thyroxine = rng.integers(0, 2, n)
        on_antithyroid = rng.integers(0, 2, n)
        sick = rng.integers(0, 2, n)
        pregnant = rng.integers(0, 2, n)
        thyroid_surgery = rng.integers(0, 2, n)
        tsh = rng.uniform(0.005, 530.0, n).round(3)
        t3 = rng.uniform(0.05, 10.6, n).round(2)
        tt4 = rng.uniform(2.0, 430.0, n).round(1)
        t4u = rng.uniform(0.17, 2.33, n).round(2)
        fti = rng.uniform(2.0, 395.0, n).round(1)
        cls = []
        for i in range(n):
            if tsh[i] > 10:
                cls.append("hypothyroid")
            elif tsh[i] < 0.3:
                cls.append("hyperthyroid")
            else:
                cls.append("normal")
        return pd.DataFrame({
            "age": age, "sex": sex, "on_thyroxine": on_thyroxine,
            "on_antithyroid_medication": on_antithyroid,
            "sick": sick, "pregnant": pregnant, "thyroid_surgery": thyroid_surgery,
            "TSH": tsh, "T3": t3, "TT4": tt4, "T4U": t4u, "FTI": fti, "class": cls,
        })

    def _readmission(self) -> pd.DataFrame:
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
        rng = self._rng()
        n = 400
        age = rng.integers(1, 90, n)
        sex = rng.integers(0, 2, n)
        view_position = rng.integers(0, 2, n)
        follow_up = rng.integers(0, 5, n)
        consolidation = rng.uniform(0.0, 1.0, n).round(3)
        infiltration = rng.uniform(0.0, 1.0, n).round(3)
        effusion = rng.uniform(0.0, 1.0, n).round(3)
        atelectasis = rng.uniform(0.0, 1.0, n).round(3)
        nodule = rng.uniform(0.0, 1.0, n).round(3)
        mass = rng.uniform(0.0, 1.0, n).round(3)
        pneumothorax = rng.uniform(0.0, 1.0, n).round(3)
        cardiomegaly = rng.uniform(0.0, 1.0, n).round(3)
        log_odds = (
            -2 + 5 * consolidation + 3 * infiltration + 2 * effusion
            + 0.01 * age
        )
        prob = 1 / (1 + np.exp(-log_odds))
        finding = np.where(rng.uniform(0, 1, n) < prob, "Pneumonia", "No Finding")
        return pd.DataFrame({
            "age": age, "sex": sex, "view_position": view_position,
            "follow_up_number": follow_up, "consolidation": consolidation,
            "infiltration": infiltration, "effusion": effusion,
            "atelectasis": atelectasis, "nodule": nodule, "mass": mass,
            "pneumothorax": pneumothorax, "cardiomegaly": cardiomegaly,
            "Finding_Label": finding,
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
