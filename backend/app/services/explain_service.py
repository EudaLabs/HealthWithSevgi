"""SHAP-based explainability service."""
from __future__ import annotations

import logging
from typing import Any

import numpy as np

from app.models.explain_schemas import (
    FeatureImportanceItem,
    GlobalExplainabilityResponse,
    SHAPWaterfallPoint,
    SinglePatientExplainResponse,
)

logger = logging.getLogger(__name__)

CLINICAL_NAME_MAP: dict[str, str] = {
    # Demographics
    "age": "Patient Age (years)",
    "sex": "Patient Sex",
    "gender": "Patient Gender",
    "height": "Patient Height (cm)",
    "weight": "Patient Weight (kg)",
    "bmi": "Body Mass Index (kg/m²)",
    # Cardiology / HF
    "ejection_fraction": "Left Ventricular Ejection Fraction (%)",
    "serum_creatinine": "Serum Creatinine (mg/dL)",
    "serum_sodium": "Serum Sodium (mEq/L)",
    "creatinine_phosphokinase": "Creatine Phosphokinase (mcg/L)",
    "platelets": "Platelet Count (kiloplatelets/mL)",
    "anaemia": "Anaemia Present",
    "high_blood_pressure": "Hypertension Diagnosis",
    "smoking": "Smoking Status",
    "diabetes": "Diabetes History",
    "time": "Follow-up Period (days)",
    "DEATH_EVENT": "Death Event",
    # Diabetes
    "glucose": "Fasting Glucose (mg/dL)",
    "blood_pressure": "Diastolic Blood Pressure (mmHg)",
    "skin_thickness": "Triceps Skin Fold Thickness (mm)",
    "insulin": "Serum Insulin (mu U/mL)",
    "diabetes_pedigree_function": "Diabetes Pedigree Function",
    "pregnancies": "Number of Pregnancies",
    # Breast cancer
    "mean_radius": "Mean Tumour Radius (mm)",
    "mean_texture": "Mean Texture Score",
    "mean_perimeter": "Mean Tumour Perimeter (mm)",
    "mean_area": "Mean Tumour Area (mm²)",
    "mean_smoothness": "Mean Surface Smoothness",
    "mean_compactness": "Mean Compactness",
    "mean_concavity": "Mean Concavity",
    "mean_concave_points": "Mean Concave Points",
    "mean_symmetry": "Mean Symmetry",
    "worst_radius": "Worst Tumour Radius (mm)",
    "worst_texture": "Worst Texture Score",
    "worst_perimeter": "Worst Tumour Perimeter (mm)",
    "worst_area": "Worst Tumour Area (mm²)",
    "worst_smoothness": "Worst Surface Smoothness",
    # Parkinson's
    "MDVP_Fo_Hz": "Avg Vocal Fundamental Frequency (Hz)",
    "MDVP_Fhi_Hz": "Max Vocal Fundamental Frequency (Hz)",
    "MDVP_Flo_Hz": "Min Vocal Fundamental Frequency (Hz)",
    "MDVP_Jitter_pct": "Vocal Jitter (%)",
    "MDVP_Jitter_Abs": "Absolute Vocal Jitter",
    "MDVP_Shimmer": "Vocal Shimmer",
    "NHR": "Noise-to-Harmonics Ratio",
    "HNR": "Harmonics-to-Noise Ratio",
    "RPDE": "Recurrence Period Density Entropy",
    "DFA": "Detrended Fluctuation Analysis",
    "PPE": "Pitch Period Entropy",
    # Liver
    "total_bilirubin": "Total Bilirubin (mg/dL)",
    "direct_bilirubin": "Direct Bilirubin (mg/dL)",
    "alkaline_phosphotase": "Alkaline Phosphatase (U/L)",
    "alamine_aminotransferase": "Alanine Aminotransferase / ALT (U/L)",
    "aspartate_aminotransferase": "Aspartate Aminotransferase / AST (U/L)",
    "total_proteins": "Total Proteins (g/dL)",
    "albumin": "Serum Albumin (g/dL)",
    "albumin_globulin_ratio": "Albumin/Globulin Ratio",
    # Stroke
    "hypertension": "Hypertension",
    "heart_disease": "Heart Disease History",
    "avg_glucose_level": "Average Glucose Level (mg/dL)",
    "smoking_status": "Smoking Status",
    "work_type": "Work Type",
    "residence_type": "Residence Type",
    "ever_married": "Ever Married",
    # CKD
    "blood_pressure": "Blood Pressure (mmHg)",
    "specific_gravity": "Urine Specific Gravity",
    "albumin": "Urine Albumin",
    "sugar": "Urine Sugar",
    "red_blood_cells": "Red Blood Cells in Urine",
    "pus_cell": "Pus Cells in Urine",
    "blood_glucose_random": "Random Blood Glucose (mg/dL)",
    "blood_urea": "Blood Urea (mg/dL)",
    "sodium": "Serum Sodium (mEq/L)",
    "haemoglobin": "Haemoglobin (g/dL)",
    "hypertension": "Hypertension",
    "diabetes_mellitus": "Diabetes Mellitus",
    # Sepsis
    "HR": "Heart Rate (bpm)",
    "O2Sat": "Oxygen Saturation (%)",
    "Temp": "Body Temperature (°C)",
    "SBP": "Systolic Blood Pressure (mmHg)",
    "MAP": "Mean Arterial Pressure (mmHg)",
    "Resp": "Respiratory Rate (breaths/min)",
    "pH": "Arterial Blood pH",
    "Lactate": "Blood Lactate (mmol/L)",
    "Creatinine": "Serum Creatinine (mg/dL)",
    "WBC": "White Blood Cell Count (×10³/μL)",
    "Platelets": "Platelet Count (×10³/μL)",
    "Bilirubin_total": "Total Bilirubin (mg/dL)",
    # Orthopaedics
    "pelvic_incidence": "Pelvic Incidence (°)",
    "pelvic_tilt": "Pelvic Tilt (°)",
    "lumbar_lordosis_angle": "Lumbar Lordosis Angle (°)",
    "sacral_slope": "Sacral Slope (°)",
    "pelvic_radius": "Pelvic Radius (mm)",
    "degree_spondylolisthesis": "Degree of Spondylolisthesis (mm)",
    # Fetal health
    "baseline_value": "Fetal Heart Rate Baseline (bpm)",
    "accelerations": "Accelerations (per second)",
    "fetal_movement": "Fetal Movements (per second)",
    "uterine_contractions": "Uterine Contractions (per second)",
    "severe_decelerations": "Severe Decelerations (per second)",
    "prolongued_decelerations": "Prolonged Decelerations (per second)",
    "abnormal_short_term_variability": "Abnormal Short-Term Variability (%)",
    # Thyroid
    "TSH": "Thyroid Stimulating Hormone (mIU/L)",
    "T3": "Serum Triiodothyronine / T3 (ng/dL)",
    "TT4": "Total Thyroxine / T4 (μg/dL)",
    "T4U": "Thyroxine Utilisation Rate",
    "FTI": "Free Thyroxine Index",
}

TOP_FEATURE_NOTES: dict[str, str] = {
    "ejection_fraction": "Ejection fraction is a well-established predictor of heart failure outcomes — values below 35% indicate severely reduced cardiac function.",
    "serum_creatinine": "Elevated serum creatinine reflects impaired renal clearance, which commonly co-occurs with and worsens heart failure prognosis.",
    "glucose": "Fasting glucose is the primary biochemical marker of diabetes risk and insulin resistance.",
    "bmi": "BMI is a validated surrogate for adiposity and a major modifiable risk factor for type 2 diabetes.",
    "mean_radius": "Tumour radius is closely correlated with malignancy — larger tumours are associated with more aggressive histology.",
    "worst_area": "Worst-case tumour area captures the most severe regional cellular abnormality within the biopsy sample.",
    "TSH": "TSH is the most sensitive marker of thyroid dysfunction — a raised TSH indicates hypothyroidism, while a suppressed TSH indicates hyperthyroidism.",
    "Lactate": "Elevated lactate is a hallmark of cellular hypoperfusion and is a key diagnostic criterion for septic shock.",
    "HR": "Heart rate elevation is an early physiological response to infection and correlates with sepsis severity.",
    "pelvic_incidence": "Pelvic incidence is a morphological parameter that determines lumbar lordosis compensation and is key to spinal biomechanics.",
    "degree_spondylolisthesis": "Degree of spondylolisthesis directly quantifies vertebral slip and is the primary determinant of clinical severity.",
    "MDVP_Jitter_pct": "Jitter measures cycle-to-cycle variation in vocal fundamental frequency — pathological values indicate Parkinson's-related vocal instability.",
    "HNR": "A reduced harmonics-to-noise ratio reflects increased vocal noise and turbulence characteristic of neurological voice disorders.",
}


def _clinical_name(feature: str) -> str:
    return CLINICAL_NAME_MAP.get(feature, feature.replace("_", " ").title())


def _plain_language(feature: str, value: float, pctile: float) -> str:
    cname = _clinical_name(feature)
    if pctile < 0.25:
        level = "very low"
    elif pctile < 0.45:
        level = "below normal"
    elif pctile < 0.55:
        level = "normal"
    elif pctile < 0.75:
        level = "above normal"
    else:
        level = "elevated"
    return f"{cname} {level} ({value:.2f})"


class ExplainService:
    def _get_explainer(self, model: Any, X_train: np.ndarray, model_type: str) -> Any:
        import shap
        mt = model_type.lower()
        try:
            # Tree-based models (including XGBoost and LightGBM)
            if mt in ("random_forest", "decision_tree", "xgboost", "lightgbm"):
                return shap.TreeExplainer(model), "shap_tree"
            if mt == "logistic_regression":
                return shap.LinearExplainer(model, X_train), "shap_linear"
            # KNN, SVM, NaiveBayes → KernelExplainer with reduced background for speed
            bg = shap.sample(X_train, min(50, len(X_train)))  # Reduced from 100 to 50
            try:
                explainer = shap.Explainer(model.predict_proba, bg, algorithm="auto")
                return explainer, "shap_kernel"
            except Exception:
                return shap.KernelExplainer(model.predict_proba, bg), "shap_kernel"
        except Exception as exc:
            logger.warning("SHAP explainer creation failed: %s — using permutation", exc)
            return None, "permutation"

    def _shap_values_binary(
        self, explainer: Any, method: str, X: np.ndarray, model: Any
    ) -> np.ndarray:
        """Return 2-D SHAP array (n_samples, n_features) for the positive class."""
        import shap
        try:
            sv = explainer.shap_values(X)
            if isinstance(sv, list) and len(sv) == 2:
                return np.array(sv[1])
            if isinstance(sv, np.ndarray):
                if sv.ndim == 3:
                    return sv[:, :, 1]
                return sv
            return np.array(sv)
        except Exception as exc:
            logger.warning("SHAP value computation failed: %s — fallback", exc)
            return self._permutation_importance(model, X)

    def _permutation_importance(self, model: Any, X: np.ndarray) -> np.ndarray:
        """Rough fallback: feature std × coefficient magnitude."""
        try:
            if hasattr(model, "coef_"):
                coef = np.abs(model.coef_[0] if model.coef_.ndim > 1 else model.coef_)
                return np.outer(np.ones(len(X)), coef)
            if hasattr(model, "feature_importances_"):
                fi = model.feature_importances_
                return np.outer(np.ones(len(X)), fi)
        except Exception:
            pass
        return np.zeros((len(X), X.shape[1]))

    def global_importance(
        self,
        model_id: str,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: list[str],
        X_train: np.ndarray,
        model_type: str,
        classes: list[str],
    ) -> GlobalExplainabilityResponse:
        explainer, method = self._get_explainer(model, X_train, model_type)

        if explainer is not None:
            sv = self._shap_values_binary(explainer, method, X_test[:200], model)
        else:
            sv = self._permutation_importance(model, X_test[:200])
            method = "permutation"

        mean_abs = np.mean(np.abs(sv), axis=0)
        mean_signed = np.mean(sv, axis=0)

        total = mean_abs.sum() if mean_abs.sum() > 0 else 1.0
        indices = np.argsort(mean_abs)[::-1]

        items: list[FeatureImportanceItem] = []
        cumulative = 0.0
        top5_cumulative = 0.0
        for rank, idx in enumerate(indices):
            name = feature_names[idx] if idx < len(feature_names) else f"feature_{idx}"
            imp = float(mean_abs[idx])
            cumulative += imp / total
            if rank < 5:
                top5_cumulative = cumulative

            direction: str
            if mean_signed[idx] > 0.01:
                direction = "positive"
            elif mean_signed[idx] < -0.01:
                direction = "negative"
            else:
                direction = "neutral"

            note = TOP_FEATURE_NOTES.get(name, f"{_clinical_name(name)} influences the model's predictions.")
            items.append(FeatureImportanceItem(
                feature_name=name,
                clinical_name=_clinical_name(name),
                importance=round(imp, 6),
                direction=direction,
                clinical_note=note,
            ))

        top_name = items[0].feature_name if items else ""
        top_note = TOP_FEATURE_NOTES.get(
            top_name,
            f"{_clinical_name(top_name)} is the most influential variable in this model's decisions.",
        )

        return GlobalExplainabilityResponse(
            model_id=model_id,
            method=method,
            feature_importances=items,
            top_feature_clinical_note=top_note,
            explained_variance_pct=round(top5_cumulative * 100, 1),
        )

    def single_patient(
        self,
        model_id: str,
        model: Any,
        patient_idx: int,
        X_test: np.ndarray,
        feature_names: list[str],
        X_train: np.ndarray,
        model_type: str,
        classes: list[str],
        y_test: np.ndarray,
    ) -> SinglePatientExplainResponse:
        explainer, method = self._get_explainer(model, X_train, model_type)

        x_patient = X_test[patient_idx : patient_idx + 1]

        if explainer is not None:
            sv = self._shap_values_binary(explainer, method, x_patient, model)
        else:
            sv = self._permutation_importance(model, x_patient)

        shap_vals = sv[0] if sv.ndim > 1 else sv

        # Base value
        base_value = 0.5
        try:
            if hasattr(explainer, "expected_value"):
                ev = explainer.expected_value
                base_value = float(ev[1] if isinstance(ev, (list, np.ndarray)) else ev)
        except Exception:
            pass

        # Predicted probability
        prob_arr = self._model_predict_proba(model, x_patient)
        if prob_arr.shape[1] >= 2:
            pred_class_idx = int(np.argmax(prob_arr[0]))
            pred_prob = float(prob_arr[0, pred_class_idx])
        else:
            pred_class_idx = 0
            pred_prob = 0.5
        predicted_class = classes[pred_class_idx] if pred_class_idx < len(classes) else str(pred_class_idx)

        # Percentile for plain language
        pctiles = np.mean(X_train < x_patient[0], axis=0)

        waterfall: list[SHAPWaterfallPoint] = []
        sorted_idx = np.argsort(np.abs(shap_vals))[::-1]
        for i in sorted_idx[:15]:
            fname = feature_names[i] if i < len(feature_names) else f"feature_{i}"
            sv_val = float(shap_vals[i])
            fval = float(x_patient[0, i])
            pct = float(pctiles[i]) if i < len(pctiles) else 0.5
            waterfall.append(SHAPWaterfallPoint(
                feature_name=fname,
                clinical_name=_clinical_name(fname),
                feature_value=round(fval, 3),
                shap_value=round(sv_val, 5),
                direction="increases_risk" if sv_val > 0 else "decreases_risk",
                plain_language=_plain_language(fname, fval, pct),
            ))

        # Clinical summary
        top3 = waterfall[:3]
        risk_factors = [w.plain_language for w in top3 if w.direction == "increases_risk"]
        protect_factors = [w.plain_language for w in top3 if w.direction == "decreases_risk"]
        summary_parts = [
            f"This patient was classified as '{predicted_class}' with a probability of {pred_prob:.1%}."
        ]
        if risk_factors:
            summary_parts.append(f"Key risk-increasing factors: {'; '.join(risk_factors)}.")
        if protect_factors:
            summary_parts.append(f"Protective factors: {'; '.join(protect_factors)}.")
        summary_parts.append(
            "These associations are derived from the training data and do not imply causation."
        )

        return SinglePatientExplainResponse(
            model_id=model_id,
            patient_index=patient_idx,
            predicted_class=predicted_class,
            predicted_probability=round(pred_prob, 4),
            base_value=round(base_value, 4),
            waterfall=waterfall,
            clinical_summary=" ".join(summary_parts),
        )

    def _model_predict_proba(self, model: Any, X: np.ndarray) -> np.ndarray:
        if hasattr(model, "predict_proba"):
            return model.predict_proba(X)
        if hasattr(model, "decision_function"):
            scores = model.decision_function(X)
            if scores.ndim == 1:
                p = 1 / (1 + np.exp(-scores))
                return np.column_stack([1 - p, p])
        return np.array([[0.5, 0.5]])
