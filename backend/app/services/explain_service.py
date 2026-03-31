"""SHAP-based explainability service."""
from __future__ import annotations

import logging
from typing import Any

import numpy as np

from app.models.explain_schemas import (
    FeatureImportanceItem,
    GlobalExplainabilityResponse,
    SamplePatient,
    SamplePatientsResponse,
    SHAPWaterfallPoint,
    SinglePatientExplainResponse,
    WhatIfResponse,
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
    "MDVP_RAP": "Relative Average Perturbation",
    "MDVP_PPQ": "Five-Point Period Perturbation Quotient",
    "Jitter_DDP": "Average Absolute Difference of Differences (Jitter)",
    "MDVP_Shimmer": "Vocal Shimmer",
    "MDVP_Shimmer_dB": "Vocal Shimmer (dB)",
    "Shimmer_APQ3": "Three-Point Amplitude Perturbation Quotient",
    "Shimmer_APQ5": "Five-Point Amplitude Perturbation Quotient",
    "MDVP_APQ": "MDVP Amplitude Perturbation Quotient",
    "Shimmer_DDA": "Average Absolute Differences of Consecutive Shimmer",
    "NHR": "Noise-to-Harmonics Ratio",
    "HNR": "Harmonics-to-Noise Ratio",
    "RPDE": "Recurrence Period Density Entropy",
    "DFA": "Detrended Fluctuation Analysis",
    "spread1": "Nonlinear Frequency Variation (spread1)",
    "spread2": "Nonlinear Frequency Variation (spread2)",
    "D2": "D2 Nonlinear Dynamical Complexity",
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
    "T3_resin_uptake": "T3 Resin Uptake (%)",
    "total_serum_thyroxine": "Total Serum Thyroxine (μg/dL)",
    "max_abs_diff_TSH": "Max Absolute Difference in TSH",
    # Anaemia / haematology
    "mch": "Mean Corpuscular Haemoglobin (pg)",
    "mchc": "Mean Corpuscular Haemoglobin Concentration (g/dL)",
    "mcv": "Mean Corpuscular Volume (fL)",
    "rdw": "Red Cell Distribution Width (%)",
    "wbc": "White Blood Cell Count (×10³/μL)",
    "neutrophils": "Neutrophil Count (×10³/μL)",
    "lymphocytes": "Lymphocyte Count (×10³/μL)",
    # COPD / pulmonology
    "smoking_pack_years": "Smoking Pack-Years",
    "fev1_litres": "FEV1 — Forced Expiratory Volume in 1s (L)",
    "fvc_litres": "FVC — Forced Vital Capacity (L)",
    "fev1_fvc_ratio": "FEV1/FVC Ratio",
    "prior_exacerbations_year": "Prior COPD Exacerbations (per year)",
    "mrc_dyspnea_scale": "MRC Dyspnea Scale Score",
    "sgrq_score": "SGRQ Quality-of-Life Score",
    "copd_gold_stage": "COPD GOLD Stage",
    # Arrhythmia / ECG
    "QRS_duration": "QRS Duration (ms)",
    "PR_interval": "PR Interval (ms)",
    "QT_interval": "QT Interval (ms)",
    "T_interval": "T Wave Interval (ms)",
    "P_interval": "P Wave Interval (ms)",
    "QRS_axis": "QRS Axis (°)",
    "T_axis": "T Wave Axis (°)",
    "P_axis": "P Wave Axis (°)",
    "heart_rate": "Heart Rate (bpm)",
    # Radiology
    "view_position": "X-Ray View Position",
    "follow_up_number": "Follow-up Visit Number",
    "Finding_Label": "Radiological Finding",
    # Fetal health / CTG
    "light_decelerations": "Light Decelerations (per second)",
    "mean_value_short_term_variability": "Mean Short-Term Variability (ms)",
    "pct_time_abnormal_long_term_variability": "% Time with Abnormal Long-Term Variability",
    "mean_value_long_term_variability": "Mean Long-Term Variability (ms)",
    "histogram_mode": "CTG Histogram Mode",
    # Ophthalmology / diabetic retinopathy
    "quality_assessment": "Image Quality Assessment",
    "pre_screening": "Pre-Screening Result",
    "ma_detection_0.5": "Microaneurysm Detection (threshold 0.5)",
    "ma_detection_0.6": "Microaneurysm Detection (threshold 0.6)",
    "ma_detection_0.7": "Microaneurysm Detection (threshold 0.7)",
    "ma_detection_0.8": "Microaneurysm Detection (threshold 0.8)",
    "ma_detection_0.9": "Microaneurysm Detection (threshold 0.9)",
    "ma_detection_1.0": "Microaneurysm Detection (threshold 1.0)",
    "exudate_1": "Exudate Feature 1",
    "exudate_2": "Exudate Feature 2",
    "exudate_3": "Exudate Feature 3",
    "exudate_4": "Exudate Feature 4",
    "exudate_5": "Exudate Feature 5",
    "exudate_6": "Exudate Feature 6",
    "exudate_7": "Exudate Feature 7",
    "exudate_8": "Exudate Feature 8",
    "macula_od_distance": "Macula to Optic Disc Distance",
    "optic_disc_diameter": "Optic Disc Diameter",
    "am_fm_classification": "AM-FM Classification",
    # Dermatology
    "localization": "Lesion Localization",
    # Cervical cancer
    "number_of_sexual_partners": "Number of Sexual Partners",
    "first_sexual_intercourse_age": "Age at First Sexual Intercourse",
    "num_of_pregnancies": "Number of Pregnancies",
    "smokes_years": "Years of Smoking",
    "hormonal_contraceptives_years": "Years Using Hormonal Contraceptives",
    "iud_years": "Years Using IUD",
    "stds_number": "Number of STDs Diagnosed",
    "stds_condylomatosis": "STDs: Condylomatosis",
    "stds_cervical_condylomatosis": "STDs: Cervical Condylomatosis",
    "stds_hpv": "STDs: HPV",
    # Pharmacy / readmission
    "time_in_hospital": "Hospital Length of Stay (days)",
    "num_lab_procedures": "Number of Lab Procedures",
    "num_procedures": "Number of Procedures",
    "num_medications": "Number of Medications",
    "number_outpatient": "Number of Outpatient Visits",
    "number_emergency": "Number of Emergency Visits",
    "number_inpatient": "Number of Inpatient Visits",
    "number_diagnoses": "Number of Diagnoses",
    "max_glu_serum": "Max Glucose Serum Level",
    "A1Cresult": "HbA1c Test Result",
    "metformin": "Metformin Dosage",
    "change": "Change in Medication",
    # Sepsis / ICU
    "BaseExcess": "Base Excess (mEq/L)",
    "PaCO2": "Partial Pressure of CO2 (mmHg)",
    "Age": "Patient Age (years)",
    "Gender": "Patient Gender",
    # Mental health
    "number_of_children": "Number of Children",
    "income": "Annual Income",
    "dietary_habits": "Dietary Habits Score",
    "sleep_patterns": "Sleep Quality Score",
    "alcohol_consumption": "Alcohol Consumption Level",
    "physical_activity_level": "Physical Activity Level",
    "employment_status": "Employment Status",
    "history_substance_abuse": "History of Substance Abuse",
    "family_history_depression": "Family History of Depression",
    "chronic_medical_conditions": "Chronic Medical Conditions",
    "marital_status": "Marital Status",
    "education_level": "Education Level",
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
        mt = model_type.lower()
        try:
            import shap
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
        scaler: Any = None,
    ) -> SinglePatientExplainResponse:
        explainer, method = self._get_explainer(model, X_train, model_type)

        x_patient = X_test[patient_idx : patient_idx + 1]

        # Inverse-transform to get clinical (unscaled) values for display
        if scaler is not None:
            try:
                x_patient_raw = scaler.inverse_transform(x_patient)[0]
            except Exception as exc:
                logger.warning("Inverse-transform failed in single_patient: %s — using scaled values", exc)
                x_patient_raw = x_patient[0]
        else:
            x_patient_raw = x_patient[0]

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
            fval_raw = float(x_patient_raw[i]) if i < len(x_patient_raw) else float(x_patient[0, i])
            pct = float(pctiles[i]) if i < len(pctiles) else 0.5
            waterfall.append(SHAPWaterfallPoint(
                feature_name=fname,
                clinical_name=_clinical_name(fname),
                feature_value=round(fval_raw, 3),
                shap_value=round(sv_val, 5),
                direction="increases_risk" if sv_val > 0 else "decreases_risk",
                plain_language=_plain_language(fname, fval_raw, pct),
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

    # ------------------------------------------------------------------
    # What-If analysis
    # ------------------------------------------------------------------
    def what_if(
        self,
        model_id: str,
        model: Any,
        patient_index: int,
        feature_name: str,
        new_value: float,
        X_test: np.ndarray,
        feature_names: list[str],
        scaler: Any | None,
    ) -> WhatIfResponse:
        """Simulate changing a single feature and return the probability shift."""
        if feature_name not in feature_names:
            raise ValueError(f"Feature '{feature_name}' not found. Available: {feature_names}")

        n_test = len(X_test)
        if patient_index < 0 or patient_index >= n_test:
            raise IndexError(f"Patient index {patient_index} out of range [0, {n_test - 1}]")

        feat_idx = feature_names.index(feature_name)

        # Original row (already scaled if scaler was applied during training)
        original_row = X_test[patient_index : patient_index + 1].copy()

        # Get original clinical value by inverse-transforming
        if scaler is not None:
            try:
                original_clinical = scaler.inverse_transform(original_row)[0, feat_idx]
            except Exception:
                original_clinical = float(original_row[0, feat_idx])
        else:
            original_clinical = float(original_row[0, feat_idx])

        # Build modified row: start from scaled original, replace the feature
        modified_row = original_row.copy()
        if scaler is not None:
            # new_value is in clinical space; we need to scale only that feature.
            # Build a full clinical row, replace the feature, then re-scale.
            try:
                clinical_row = scaler.inverse_transform(original_row)
                clinical_row[0, feat_idx] = new_value
                modified_row = scaler.transform(clinical_row)
            except Exception:
                # Fallback: inject raw value directly
                modified_row[0, feat_idx] = new_value
        else:
            modified_row[0, feat_idx] = new_value

        # Predict probabilities
        original_probs = self._model_predict_proba(model, original_row)
        modified_probs = self._model_predict_proba(model, modified_row)

        # For binary: use class-1 probability; for multiclass: use max probability
        if original_probs.shape[1] == 2:
            original_prob = float(original_probs[0, 1])
            new_prob = float(modified_probs[0, 1])
        else:
            original_prob = float(np.max(original_probs[0]))
            new_prob = float(np.max(modified_probs[0]))

        shift = new_prob - original_prob

        if abs(shift) < 1e-6:
            direction = "no_change"
        elif shift > 0:
            direction = "increased_risk"
        else:
            direction = "decreased_risk"

        return WhatIfResponse(
            feature_name=feature_name,
            original_value=round(float(original_clinical), 4),
            new_value=round(new_value, 4),
            original_prob=round(original_prob, 4),
            new_prob=round(new_prob, 4),
            shift=round(shift, 4),
            direction=direction,
        )

    # ------------------------------------------------------------------
    # Sample patients for dropdown picker
    # ------------------------------------------------------------------
    def sample_patients(
        self,
        model_id: str,
        model: Any,
        X_test: np.ndarray,
    ) -> SamplePatientsResponse:
        """Return up to 3 representative patients (low/medium/high risk)."""
        n = len(X_test)
        if n == 0:
            return SamplePatientsResponse(model_id=model_id, patients=[])

        probs = self._model_predict_proba(model, X_test)
        # Use class-1 probability for binary; max probability otherwise
        if probs.shape[1] == 2:
            scores = probs[:, 1]
        else:
            scores = np.max(probs, axis=1)

        sorted_indices = np.argsort(scores)

        picks: list[tuple[int, str]] = []

        # Low risk: lowest probability patient
        low_idx = int(sorted_indices[0])
        picks.append((low_idx, "low"))

        if n >= 2:
            # High risk: highest probability patient
            high_idx = int(sorted_indices[-1])
            picks.append((high_idx, "high"))

        if n >= 3:
            # Medium risk: patient closest to 0.5
            diffs = np.abs(scores - 0.5)
            med_idx = int(np.argmin(diffs))
            # Avoid duplicating low or high pick
            if med_idx in (low_idx, high_idx):
                # Fall back to the median-ranked patient
                med_idx = int(sorted_indices[n // 2])
            picks.append((med_idx, "medium"))

        patients: list[SamplePatient] = []
        for idx, level in picks:
            prob = float(scores[idx])
            label = level.capitalize()
            patients.append(SamplePatient(
                index=idx,
                risk_level=level,
                probability=round(prob, 4),
                summary=f"Patient #{idx} — {label} Risk ({prob:.0%})",
            ))

        # Sort by risk level order: low, medium, high
        order = {"low": 0, "medium": 1, "high": 2}
        patients.sort(key=lambda p: order[p.risk_level])

        return SamplePatientsResponse(model_id=model_id, patients=patients)
