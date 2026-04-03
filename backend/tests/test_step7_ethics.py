"""
Step 7 — Ethics, bias, and compliance endpoint tests.

Tests subgroup bias detection, EU AI Act checklist toggle,
case-study severity, and representation-gap warnings.
"""
from __future__ import annotations

import pytest

from tests.conftest import train_example_model


@pytest.fixture(scope="module")
def trained_model(client) -> dict:
    """Explore → Prepare → Train; reusable across this module."""
    return train_example_model(client)


# ===================================================================
# Ethics / bias analysis
# ===================================================================

class TestEthicsEndpoint:
    def test_returns_200(self, client, trained_model):
        r = client.get(f"/api/ethics/{trained_model['model_id']}")
        assert r.status_code == 200

    def test_response_schema(self, client, trained_model):
        r = client.get(f"/api/ethics/{trained_model['model_id']}")
        body = r.json()
        for key in (
            "model_id", "subgroup_metrics", "bias_warnings",
            "training_representation", "overall_sensitivity",
            "eu_ai_act_items", "case_studies",
        ):
            assert key in body, f"Missing key: {key}"

    def test_case_studies_have_severity(self, client, trained_model):
        r = client.get(f"/api/ethics/{trained_model['model_id']}")
        for cs in r.json()["case_studies"]:
            assert "severity" in cs, f"Case study '{cs.get('id')}' missing severity"
            assert cs["severity"] in ("failure", "near_miss", "prevention")

    def test_eu_ai_act_checklist_has_nine_items(self, client, trained_model):
        r = client.get(f"/api/ethics/{trained_model['model_id']}")
        items = r.json()["eu_ai_act_items"]
        assert len(items) == 9
        data_lic = [i for i in items if i["id"] == "data_licensing"]
        assert len(data_lic) == 1, "data_licensing item missing"
        assert data_lic[0]["pre_checked"] is True

    def test_representation_warnings_field_present(self, client, trained_model):
        r = client.get(f"/api/ethics/{trained_model['model_id']}")
        body = r.json()
        assert "representation_warnings" in body
        assert isinstance(body["representation_warnings"], list)

    def test_invalid_model_returns_404(self, client):
        r = client.get("/api/ethics/nonexistent_model")
        assert r.status_code == 404


# ===================================================================
# Checklist toggle
# ===================================================================

class TestChecklistToggle:
    def test_toggle_on(self, client, trained_model):
        r = client.post(
            "/api/ethics/checklist",
            json={
                "model_id": trained_model["model_id"],
                "item_id": "bias_audit",
                "checked": True,
            },
        )
        assert r.status_code == 200
        assert r.json()["bias_audit"] is True

    def test_toggle_off(self, client, trained_model):
        r = client.post(
            "/api/ethics/checklist",
            json={
                "model_id": trained_model["model_id"],
                "item_id": "bias_audit",
                "checked": False,
            },
        )
        assert r.status_code == 200
        assert r.json()["bias_audit"] is False

    def test_checklist_persists_across_calls(self, client, trained_model):
        mid = trained_model["model_id"]
        # Set two items
        client.post("/api/ethics/checklist", json={"model_id": mid, "item_id": "gdpr", "checked": True})
        client.post("/api/ethics/checklist", json={"model_id": mid, "item_id": "human_oversight", "checked": True})
        # Verify both are stored
        r = client.post("/api/ethics/checklist", json={"model_id": mid, "item_id": "monitoring", "checked": False})
        body = r.json()
        assert body["gdpr"] is True
        assert body["human_oversight"] is True
        assert body["monitoring"] is False
