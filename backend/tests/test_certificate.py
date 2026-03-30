"""
Certificate PDF generation endpoint tests.

Tests that the /api/generate-certificate endpoint produces a valid PDF
with correct headers and content-type.
"""
from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def trained_model(client) -> dict:
    """Explore → Prepare → Train; reusable across this module."""
    resp = client.post(
        "/api/explore",
        data={"specialty_id": "endocrinology_diabetes", "target_col": "Outcome"},
    )
    assert resp.status_code == 200

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
# Certificate generation
# ===================================================================

class TestCertificateGeneration:
    def test_returns_200_pdf(self, client, trained_model):
        r = client.post(
            "/api/generate-certificate",
            json={
                "model_id": trained_model["model_id"],
                "session_id": trained_model["session_id"],
                "clinician_name": "Dr. Test",
                "institution": "Test Hospital",
                "checklist_state": {},
            },
        )
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"

    def test_pdf_starts_with_magic_bytes(self, client, trained_model):
        r = client.post(
            "/api/generate-certificate",
            json={
                "model_id": trained_model["model_id"],
                "session_id": trained_model["session_id"],
                "clinician_name": "Dr. Test",
                "institution": "Test Hospital",
                "checklist_state": {},
            },
        )
        assert r.content[:5] == b"%PDF-"

    def test_content_disposition_header(self, client, trained_model):
        r = client.post(
            "/api/generate-certificate",
            json={
                "model_id": trained_model["model_id"],
                "session_id": trained_model["session_id"],
            },
        )
        assert r.status_code == 200
        assert "attachment" in r.headers.get("content-disposition", "")
        assert ".pdf" in r.headers.get("content-disposition", "")

    def test_invalid_model_returns_404(self, client):
        r = client.post(
            "/api/generate-certificate",
            json={
                "model_id": "nonexistent_model",
                "session_id": "fake_session",
            },
        )
        assert r.status_code == 404

    def test_with_checklist_state(self, client, trained_model):
        """Certificate should still generate when checklist items are checked."""
        r = client.post(
            "/api/generate-certificate",
            json={
                "model_id": trained_model["model_id"],
                "session_id": trained_model["session_id"],
                "clinician_name": "Dr. Efe Celik",
                "institution": "Cankaya University",
                "checklist_state": {
                    "bias_audit": True,
                    "human_oversight": True,
                    "gdpr": True,
                },
            },
        )
        assert r.status_code == 200
        assert len(r.content) > 1000  # a real PDF is at least a few KB
