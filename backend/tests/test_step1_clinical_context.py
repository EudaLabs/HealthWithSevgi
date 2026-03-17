"""
test_step1_clinical_context.py — Sprint 2, Step 1: Clinical Context

Tests for GET /api/specialties.

Coverage:
- Status code and response structure
- Exactly 20 specialties returned
- All required fields present and non-empty on every specialty
- clinical_context is meaningful (>50 chars)
- All 20 known specialty IDs and names are present
- Each specialty has a valid target_type ('binary' or 'multiclass')
- feature_names lists are non-empty
- Individual specialty lookup via GET /api/specialties/{id}
- Lookup of unknown specialty ID returns 404
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Expected specialty IDs — exactly the 20 defined in specialty_registry.py
# ---------------------------------------------------------------------------
EXPECTED_IDS = {
    "cardiology_hf",
    "radiology_pneumonia",
    "nephrology_ckd",
    "oncology_breast",
    "neurology_parkinsons",
    "endocrinology_diabetes",
    "hepatology_liver",
    "cardiology_stroke",
    "mental_health",
    "pulmonology_copd",
    "haematology_anaemia",
    "dermatology",
    "ophthalmology",
    "orthopaedics",
    "icu_sepsis",
    "obstetrics_fetal",
    "cardiology_arrhythmia",
    "oncology_cervical",
    "thyroid",
    "pharmacy_readmission",
}

EXPECTED_NAMES = {
    "Cardiology",
    "Radiology",
    "Nephrology",
    "Oncology — Breast",
    "Neurology — Parkinson's",
    "Endocrinology — Diabetes",
    "Hepatology — Liver",
    "Cardiology — Stroke",
    "Mental Health",
    "Pulmonology — COPD",
    "Haematology — Anaemia",
    "Dermatology",
    "Ophthalmology",
    "Orthopaedics — Spine",
    "ICU / Sepsis",
    "Obstetrics — Fetal Health",
    "Cardiology — Arrhythmia",
    "Oncology — Cervical",
    "Thyroid / Endocrinology",
    "Pharmacy — Readmission",
}

VALID_TARGET_TYPES = {"binary", "multiclass"}
MIN_CLINICAL_CONTEXT_CHARS = 50


class TestSpecialtiesEndpoint:
    """Tests for GET /api/specialties."""

    def test_get_specialties_returns_200(self, client: TestClient) -> None:
        """GET /api/specialties must return HTTP 200."""
        response = client.get("/api/specialties")
        assert response.status_code == 200

    def test_response_is_a_list(self, client: TestClient) -> None:
        """Response body must be a JSON array."""
        response = client.get("/api/specialties")
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"

    def test_exactly_20_specialties_returned(self, client: TestClient) -> None:
        """Exactly 20 specialties must be present — one per clinical domain."""
        response = client.get("/api/specialties")
        specialties = response.json()
        assert len(specialties) == 20, (
            f"Expected 20 specialties, got {len(specialties)}"
        )

    def test_all_required_fields_present(self, client: TestClient) -> None:
        """Every specialty object must contain all required schema fields."""
        required_fields = {
            "id", "name", "description", "target_variable",
            "target_type", "feature_names", "clinical_context",
            "data_source", "what_ai_predicts",
        }
        response = client.get("/api/specialties")
        for item in response.json():
            missing = required_fields - set(item.keys())
            assert not missing, (
                f"Specialty '{item.get('id', '?')}' is missing fields: {missing}"
            )

    def test_all_fields_non_empty_strings(self, client: TestClient) -> None:
        """String fields must be non-empty on every specialty."""
        string_fields = ["id", "name", "description", "target_variable",
                         "clinical_context", "data_source", "what_ai_predicts"]
        response = client.get("/api/specialties")
        for item in response.json():
            for field in string_fields:
                value = item.get(field, "")
                assert isinstance(value, str) and value.strip(), (
                    f"Specialty '{item.get('id')}': field '{field}' is empty or not a string"
                )

    def test_all_20_specialty_ids_present(self, client: TestClient) -> None:
        """All 20 expected specialty IDs must appear in the response."""
        response = client.get("/api/specialties")
        returned_ids = {item["id"] for item in response.json()}
        missing = EXPECTED_IDS - returned_ids
        extra = returned_ids - EXPECTED_IDS
        assert not missing, f"Missing specialty IDs: {missing}"
        assert not extra, f"Unexpected specialty IDs: {extra}"

    def test_all_20_specialty_names_present(self, client: TestClient) -> None:
        """All 20 expected specialty display names must appear in the response."""
        response = client.get("/api/specialties")
        returned_names = {item["name"] for item in response.json()}
        missing = EXPECTED_NAMES - returned_names
        assert not missing, f"Missing specialty names: {missing}"

    def test_clinical_context_is_meaningful(self, client: TestClient) -> None:
        """clinical_context must be at least 50 characters for every specialty."""
        response = client.get("/api/specialties")
        for item in response.json():
            ctx = item.get("clinical_context", "")
            assert len(ctx) >= MIN_CLINICAL_CONTEXT_CHARS, (
                f"Specialty '{item['id']}': clinical_context too short "
                f"({len(ctx)} chars, minimum {MIN_CLINICAL_CONTEXT_CHARS})"
            )

    def test_target_type_is_valid(self, client: TestClient) -> None:
        """target_type must be 'binary' or 'multiclass' for every specialty."""
        response = client.get("/api/specialties")
        for item in response.json():
            assert item["target_type"] in VALID_TARGET_TYPES, (
                f"Specialty '{item['id']}': invalid target_type '{item['target_type']}'"
            )

    def test_feature_names_is_non_empty_list(self, client: TestClient) -> None:
        """feature_names must be a non-empty list of strings for every specialty."""
        response = client.get("/api/specialties")
        for item in response.json():
            fn = item.get("feature_names", [])
            assert isinstance(fn, list) and len(fn) > 0, (
                f"Specialty '{item['id']}': feature_names must be a non-empty list"
            )
            for name in fn:
                assert isinstance(name, str) and name, (
                    f"Specialty '{item['id']}': empty string in feature_names"
                )

    def test_ids_are_unique(self, client: TestClient) -> None:
        """Every specialty ID must be unique within the response."""
        response = client.get("/api/specialties")
        ids = [item["id"] for item in response.json()]
        assert len(ids) == len(set(ids)), "Duplicate specialty IDs found in response"

    def test_no_null_values_in_top_level_fields(self, client: TestClient) -> None:
        """No top-level field value should be None/null."""
        response = client.get("/api/specialties")
        for item in response.json():
            for key, value in item.items():
                assert value is not None, (
                    f"Specialty '{item.get('id')}': field '{key}' is null"
                )


class TestSpecialtyLookupById:
    """Tests for GET /api/specialties/{specialty_id}."""

    @pytest.mark.parametrize("specialty_id", sorted(EXPECTED_IDS))
    def test_each_specialty_lookup_returns_200(
        self, client: TestClient, specialty_id: str
    ) -> None:
        """Each of the 20 specialty IDs must be retrievable individually."""
        response = client.get(f"/api/specialties/{specialty_id}")
        assert response.status_code == 200, (
            f"GET /api/specialties/{specialty_id} returned {response.status_code}"
        )

    def test_individual_lookup_returns_correct_id(self, client: TestClient) -> None:
        """The returned object's id field must match the requested specialty_id."""
        response = client.get("/api/specialties/oncology_breast")
        data = response.json()
        assert data["id"] == "oncology_breast"

    def test_individual_lookup_returns_correct_name(self, client: TestClient) -> None:
        """Spot-check: oncology_breast must return name 'Oncology — Breast'."""
        response = client.get("/api/specialties/oncology_breast")
        data = response.json()
        assert data["name"] == "Oncology — Breast"

    def test_individual_lookup_cardiology_hf_target(self, client: TestClient) -> None:
        """cardiology_hf must have target_variable 'DEATH_EVENT'."""
        response = client.get("/api/specialties/cardiology_hf")
        assert response.json()["target_variable"] == "DEATH_EVENT"

    def test_unknown_specialty_returns_404(self, client: TestClient) -> None:
        """Requesting an unknown specialty ID must return HTTP 404."""
        response = client.get("/api/specialties/nonexistent_specialty")
        assert response.status_code == 404

    def test_unknown_specialty_error_message(self, client: TestClient) -> None:
        """The 404 response must contain a detail message."""
        response = client.get("/api/specialties/does_not_exist")
        body = response.json()
        assert "detail" in body
        assert body["detail"]  # non-empty


class TestDomainCount:
    """
    Sprint 2 metric: All 20 domains return correct clinical context text.
    This class verifies each domain individually and is marked slow because
    it makes 20 HTTP calls.
    """

    @pytest.mark.slow
    @pytest.mark.parametrize("specialty_id", sorted(EXPECTED_IDS))
    def test_domain_clinical_context_non_empty(
        self, client: TestClient, specialty_id: str
    ) -> None:
        """
        For each of the 20 domains, clinical_context must be a non-null,
        non-empty string of at least 50 characters.
        """
        response = client.get(f"/api/specialties/{specialty_id}")
        assert response.status_code == 200
        ctx = response.json().get("clinical_context", "")
        assert isinstance(ctx, str) and len(ctx.strip()) >= MIN_CLINICAL_CONTEXT_CHARS, (
            f"'{specialty_id}': clinical_context has {len(ctx)} chars, "
            f"minimum required is {MIN_CLINICAL_CONTEXT_CHARS}"
        )
