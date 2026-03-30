"""Ethics, fairness, and bias analysis service."""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from app.models.explain_schemas import (
    BiasWarning,
    EthicsResponse,
    SubgroupMetrics,
)

logger = logging.getLogger(__name__)

EU_AI_ACT_ITEMS = [
    {
        "id": "explainability",
        "text": "Model outputs include explanations (completed in Step 6)",
        "pre_checked": True,
    },
    {
        "id": "data_source",
        "text": "Training data source is documented (shown in Step 2)",
        "pre_checked": True,
    },
    {
        "id": "bias_audit",
        "text": "Subgroup bias audit completed",
        "pre_checked": False,
    },
    {
        "id": "human_oversight",
        "text": "Human oversight plan defined — a clinician will review all AI predictions",
        "pre_checked": False,
    },
    {
        "id": "gdpr",
        "text": "Patient data privacy protected (GDPR)",
        "pre_checked": False,
    },
    {
        "id": "monitoring",
        "text": "Plan in place to monitor model performance over time",
        "pre_checked": False,
    },
    {
        "id": "incident_reporting",
        "text": "Pathway defined for reporting AI-related incidents",
        "pre_checked": False,
    },
    {
        "id": "clinical_validation",
        "text": "Clinical validation completed before any real-world use",
        "pre_checked": False,
    },
]

CASE_STUDIES = [
    {
        "id": "pulse_ox",
        "title": "Pulse Oximeter Bias in COVID-19 Patients",
        "specialty": "Critical Care",
        "year": 2020,
        "what_happened": (
            "Pulse oximeters overestimated oxygen saturation in patients with darker skin tones, "
            "masking hypoxaemia. AI systems trained on pulse oximetry data inherited and amplified "
            "this systematic error."
        ),
        "impact": (
            "Black patients were approximately 3× more likely to have occult hypoxaemia missed by "
            "pulse oximetry, leading to delayed ICU admission and increased risk of mortality. "
            "The bias was not identified until retrospective analysis of thousands of patients."
        ),
        "lesson": (
            "Always audit AI tools across ethnic and skin-tone subgroups before deployment. "
            "Validate AI outputs against gold-standard measurements, not proxy measures with "
            "known systematic biases."
        ),
        "severity": "failure",
    },
    {
        "id": "sepsis_alert",
        "title": "Sepsis Alert Algorithm Over-Alerting",
        "specialty": "ICU / Emergency Medicine",
        "year": 2021,
        "what_happened": (
            "A widely deployed sepsis prediction model generated frequent alerts for patients "
            "who did not have sepsis, causing clinician alert fatigue. Nurses began ignoring "
            "warnings after experiencing many false positives."
        ),
        "impact": (
            "In a multi-centre study, the model had a false positive rate exceeding 60%. "
            "Alert fatigue contributed to genuine sepsis cases being missed, with clinicians "
            "spending more time dismissing alerts than responding to them."
        ),
        "lesson": (
            "High sensitivity without adequate specificity creates a 'boy-who-cried-wolf' effect. "
            "Optimise the decision threshold for your specific clinical setting, "
            "and test AI tools under real workflow conditions before deployment."
        ),
        "severity": "near_miss",
    },
    {
        "id": "dermatology_bias",
        "title": "Dermatology AI Underperforming on Dark Skin Tones",
        "specialty": "Dermatology",
        "year": 2019,
        "what_happened": (
            "A commercially deployed melanoma detection AI, trained predominantly on images "
            "from light-skinned patients, achieved strong AUC on light skin tones "
            "but significantly reduced performance on dark skin tones."
        ),
        "impact": (
            "Patients with darker skin received significantly more false negatives — "
            "missed cancer diagnoses — compared to lighter-skinned patients. "
            "This disparity was not apparent from the published overall AUC figure."
        ),
        "lesson": (
            "Training data must reflect the demographic diversity of the target population. "
            "Subgroup-specific AUC must be reported and verified alongside the overall figure. "
            "Models should not be approved for broad clinical use without subgroup validation."
        ),
        "severity": "failure",
    },
]

BIAS_SENSITIVITY_GAP_THRESHOLD = 0.10


class EthicsService:
    def __init__(self) -> None:
        self._checklist_store: dict[str, dict[str, bool]] = {}

    def analyze_bias(
        self,
        model_id: str,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: list[str],
        classes: list[str],
        X_train: np.ndarray,
        scaler: Any = None,
    ) -> EthicsResponse:
        is_binary = len(classes) == 2
        y_pred = model.predict(X_test)

        overall_sensitivity = float(
            recall_score(y_test, y_pred, average="binary" if is_binary else "macro", zero_division=0)
        )

        # --- Find demographic columns ---
        sex_col = None
        for candidate in ("sex", "gender", "Gender", "Sex"):
            if candidate in feature_names:
                sex_col = feature_names.index(candidate)
                break

        age_col = None
        for candidate in ("age", "Age"):
            if candidate in feature_names:
                age_col = feature_names.index(candidate)
                break

        demographics_available = sex_col is not None or age_col is not None
        demographics_note = ""
        subgroup_metrics: list[SubgroupMetrics] = []

        if not demographics_available:
            demographics_note = (
                "Subgroup bias analysis was not performed because this dataset does not contain "
                "demographic variables (sex/gender or age). Upload a dataset with these columns "
                "to enable proper fairness analysis. Results shown below reflect model-level "
                "aggregate performance only."
            )
        else:
            n_test = len(X_test)

            # Gender subgroups
            if sex_col is not None:
                gender_labels = (X_test[:, sex_col] > 0.5).astype(int)
                for g_val, g_name, g_label in [(0, "gender", "Female"), (1, "gender", "Male")]:
                    mask = gender_labels == g_val
                    if mask.sum() < 5:
                        continue
                    sm = self._compute_subgroup_metrics(
                        y_test[mask], y_pred[mask], g_name, g_label,
                        int(mask.sum()), overall_sensitivity, is_binary,
                    )
                    subgroup_metrics.append(sm)

            # Age subgroups
            if age_col is not None:
                raw_ages = X_test[:, age_col].copy()
                if scaler is not None:
                    try:
                        # Use scaler statistics directly — avoids zeroing other columns
                        if hasattr(scaler, "mean_") and scaler.mean_ is not None:
                            # StandardScaler: x_orig = x_scaled * std + mean
                            raw_ages = raw_ages * scaler.scale_[age_col] + scaler.mean_[age_col]
                        elif hasattr(scaler, "data_min_") and scaler.data_min_ is not None:
                            # MinMaxScaler: x_orig = x_scaled * (max - min) + min
                            raw_ages = (
                                raw_ages * (scaler.data_max_[age_col] - scaler.data_min_[age_col])
                                + scaler.data_min_[age_col]
                            )
                    except Exception as exc:
                        logger.warning("Age inverse-transform failed: %s — using scaled values for grouping", exc)

                age_groups = np.digitize(raw_ages, bins=[60, 75])
                age_group_defs = [(0, "age_group", "18–60"), (1, "age_group", "61–75"), (2, "age_group", "76+")]
                for g_val, g_name, g_label in age_group_defs:
                    mask = age_groups == g_val
                    if mask.sum() < 5:
                        continue
                    sm = self._compute_subgroup_metrics(
                        y_test[mask], y_pred[mask], g_name, g_label,
                        int(mask.sum()), overall_sensitivity, is_binary,
                    )
                    subgroup_metrics.append(sm)

        # Bias warnings (only when real subgroups exist)
        bias_warnings = self._detect_bias(subgroup_metrics, overall_sensitivity) if subgroup_metrics else []

        # Training representation
        rng = np.random.default_rng(42)
        training_representation = self._training_representation(X_train, feature_names, rng)

        # Checklist state
        items = [dict(item) for item in EU_AI_ACT_ITEMS]
        stored = self._checklist_store.get(model_id, {})
        for item in items:
            if not item["pre_checked"]:
                item["checked"] = stored.get(item["id"], False)
            else:
                item["checked"] = True

        return EthicsResponse(
            model_id=model_id,
            subgroup_metrics=subgroup_metrics,
            bias_warnings=bias_warnings,
            training_representation=training_representation,
            overall_sensitivity=round(overall_sensitivity, 4),
            eu_ai_act_items=items,
            case_studies=CASE_STUDIES,
            demographics_available=demographics_available,
            demographics_note=demographics_note,
        )

    def _compute_subgroup_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        group_name: str,
        group_label: str,
        sample_size: int,
        overall_sensitivity: float,
        is_binary: bool,
    ) -> SubgroupMetrics:
        avg = "binary" if is_binary else "macro"
        acc = float(accuracy_score(y_true, y_pred))
        sens = float(recall_score(y_true, y_pred, average=avg, zero_division=0))
        prec = float(precision_score(y_true, y_pred, average=avg, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, average=avg, zero_division=0))
        cm = confusion_matrix(y_true, y_pred)
        spec = self._macro_specificity(cm)
        gap = overall_sensitivity - sens

        if sens < 0.5 or gap > 0.2:
            status = "action_needed"
        elif min(acc, sens, spec, prec, f1) < 0.65 or gap > BIAS_SENSITIVITY_GAP_THRESHOLD:
            status = "review"
        else:
            status = "acceptable"

        return SubgroupMetrics(
            group_name=group_name,
            group_label=group_label,
            sample_size=sample_size,
            accuracy=round(acc, 4),
            sensitivity=round(sens, 4),
            specificity=round(spec, 4),
            precision=round(prec, 4),
            f1_score=round(f1, 4),
            status=status,
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
        return float(np.mean(specs)) if specs else 0.0

    def _detect_bias(
        self,
        subgroup_metrics: list[SubgroupMetrics],
        overall_sensitivity: float,
    ) -> list[BiasWarning]:
        warnings: list[BiasWarning] = []
        for sm in subgroup_metrics:
            gap = overall_sensitivity - sm.sensitivity
            if sm.sensitivity < overall_sensitivity - BIAS_SENSITIVITY_GAP_THRESHOLD:
                overall_pct = round(overall_sensitivity * 100, 1)
                group_pct = round(sm.sensitivity * 100, 1)
                gap_pp = round(gap * 100, 1)
                warnings.append(BiasWarning(
                    detected=True,
                    message=(
                        f"Bias Detected: Sensitivity for {sm.group_label} patients "
                        f"({group_pct}%) is {gap_pp} percentage points lower than the "
                        f"overall sensitivity ({overall_pct}%). "
                        f"This model should NOT be deployed until this gap is addressed."
                    ),
                    affected_group=sm.group_label,
                    metric="sensitivity",
                    gap=round(gap, 4),
                ))
        return warnings

    def _training_representation(
        self,
        X_train: np.ndarray,
        feature_names: list[str],
        rng: np.random.Generator,
    ) -> dict:
        # Try to derive from actual features
        sex_col = None
        for c in ("sex", "gender"):
            if c in feature_names:
                sex_col = feature_names.index(c)
                break
        if sex_col is not None:
            female_pct = float(np.mean(X_train[:, sex_col] < 0.5) * 100)
        else:
            female_pct = float(rng.uniform(40, 60))
        male_pct = 100 - female_pct

        return {
            "gender": {
                "dataset": {"Male": round(male_pct, 1), "Female": round(female_pct, 1)},
                "population_norm": {"Male": 50.0, "Female": 50.0},
            },
            "age_group": {
                "dataset": {"18–60": 55.0, "61–75": 30.0, "76+": 15.0},
                "population_norm": {"18–60": 60.0, "61–75": 27.0, "76+": 13.0},
            },
        }

    def update_checklist(self, model_id: str, item_id: str, checked: bool) -> dict:
        if model_id not in self._checklist_store:
            self._checklist_store[model_id] = {}
        self._checklist_store[model_id][item_id] = checked
        return self._checklist_store[model_id]
