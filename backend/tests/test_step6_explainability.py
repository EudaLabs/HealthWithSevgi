"""
Step 6 — Explainability endpoint tests.

Tests SHAP-based global feature importance, single-patient waterfall
explanations, What-If analysis, and sample-patient retrieval.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Shared fixture: train a lightweight model so explain endpoints have data
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def trained_model(client) -> dict:
    """Explore → Prepare → Train a logistic-regression model; return IDs."""
    # 1. Explore
    resp = client.post(
        "/api/explore",
        data={"specialty_id": "endocrinology_diabetes", "target_col": "Outcome"},
    )
    assert resp.status_code == 200

    # 2. Prepare
    resp = client.post(
        "/api/prepare",
        json={
            "specialty_id": "endocrinology_diabetes",
            "target_col": "Outcome",
            "test_size": 0.3,
            "missing_strategy": "median",
            "normalization": "zscore",
            "apply_smote": False,
            "handle_outliers": False,
        },
    )
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    # 3. Train (logistic regression — fast + SHAP-linear-friendly)
    resp = client.post(
        "/api/train",
        json={
            "session_id": session_id,
            "model_type": "logistic_regression",
            "params": {"C": 1.0, "max_iter": 200},
            "tune": False,
            "use_feature_selection": False,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    return {"model_id": body["model_id"], "session_id": session_id}


# ===================================================================
# Global feature-importance tests
# ===================================================================

class TestGlobalImportance:
    def test_returns_200(self, client, trained_model):
        r = client.get(f"/api/explain/global/{trained_model['model_id']}")
        assert r.status_code == 200

    def test_response_schema(self, client, trained_model):
        r = client.get(f"/api/explain/global/{trained_model['model_id']}")
        body = r.json()
        assert "feature_importances" in body
        assert "top_feature_clinical_note" in body
        assert "explained_variance_pct" in body
        assert isinstance(body["feature_importances"], list)
        assert len(body["feature_importances"]) > 0

    def test_feature_importance_item_fields(self, client, trained_model):
        r = client.get(f"/api/explain/global/{trained_model['model_id']}")
        item = r.json()["feature_importances"][0]
        for key in ("feature_name", "clinical_name", "importance", "direction", "clinical_note"):
            assert key in item, f"Missing key: {key}"
        assert item["direction"] in ("positive", "negative", "neutral")

    def test_invalid_model_returns_404(self, client):
        r = client.get("/api/explain/global/nonexistent_model")
        assert r.status_code == 404


# ===================================================================
# Single-patient explanation tests
# ===================================================================

class TestSinglePatientExplanation:
    def test_returns_200(self, client, trained_model):
        r = client.get(f"/api/explain/patient/{trained_model['model_id']}/0")
        assert r.status_code == 200

    def test_response_schema(self, client, trained_model):
        r = client.get(f"/api/explain/patient/{trained_model['model_id']}/0")
        body = r.json()
        for key in ("predicted_class", "predicted_probability", "waterfall", "clinical_summary"):
            assert key in body
        assert isinstance(body["waterfall"], list)
        assert len(body["waterfall"]) <= 15  # max 15 features in waterfall

    def test_waterfall_point_fields(self, client, trained_model):
        r = client.get(f"/api/explain/patient/{trained_model['model_id']}/0")
        point = r.json()["waterfall"][0]
        for key in ("feature_name", "clinical_name", "feature_value", "shap_value", "direction", "plain_language"):
            assert key in point
        assert point["direction"] in ("increases_risk", "decreases_risk")

    def test_invalid_patient_index_returns_422(self, client, trained_model):
        r = client.get(f"/api/explain/patient/{trained_model['model_id']}/99999")
        assert r.status_code == 422


# ===================================================================
# What-If analysis tests
# ===================================================================

class TestWhatIf:
    def test_returns_200(self, client, trained_model):
        r = client.post(
            "/api/explain/what-if",
            json={
                "model_id": trained_model["model_id"],
                "patient_index": 0,
                "feature_name": "glucose",
                "new_value": 200.0,
            },
        )
        assert r.status_code == 200

    def test_response_fields(self, client, trained_model):
        r = client.post(
            "/api/explain/what-if",
            json={
                "model_id": trained_model["model_id"],
                "patient_index": 0,
                "feature_name": "glucose",
                "new_value": 200.0,
            },
        )
        body = r.json()
        for key in ("feature_name", "original_value", "new_value", "original_prob", "new_prob", "shift", "direction"):
            assert key in body
        assert body["direction"] in ("increased_risk", "decreased_risk", "no_change")

    def test_invalid_feature_returns_400(self, client, trained_model):
        r = client.post(
            "/api/explain/what-if",
            json={
                "model_id": trained_model["model_id"],
                "patient_index": 0,
                "feature_name": "nonexistent_feature",
                "new_value": 1.0,
            },
        )
        assert r.status_code == 400


# ===================================================================
# Sample patients tests
# ===================================================================

class TestSamplePatients:
    def test_returns_200(self, client, trained_model):
        r = client.get(f"/api/explain/sample-patients/{trained_model['model_id']}")
        assert r.status_code == 200

    def test_returns_three_risk_levels(self, client, trained_model):
        r = client.get(f"/api/explain/sample-patients/{trained_model['model_id']}")
        body = r.json()
        assert "patients" in body
        levels = {p["risk_level"] for p in body["patients"]}
        assert levels == {"low", "medium", "high"}

    def test_patient_fields(self, client, trained_model):
        r = client.get(f"/api/explain/sample-patients/{trained_model['model_id']}")
        patient = r.json()["patients"][0]
        for key in ("index", "risk_level", "probability", "summary"):
            assert key in patient
