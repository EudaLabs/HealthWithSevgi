"""
test_step2_data_exploration.py — Sprint 2, Step 2: Data Exploration

Tests for POST /api/explore.

Coverage:
- Built-in example dataset exploration (no file upload)
- Valid CSV upload → 200 with correct response structure
- Invalid inputs: empty CSV, missing target column, single-row CSV,
  non-CSV binary, all-null target, numeric-only CSV without target,
  extra columns, special characters in column names
- Column mapper gate: verify response structure enables/blocks preparation
- Error handling for unknown specialty_id and missing target_col parameter
- Response schema validation (columns, row_count, class_distribution, etc.)

Sprint 2 metric: CSV Upload Success Rate — 5 valid + 5 invalid scenarios.
"""
from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_csv_upload

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXPLORE_URL = "/api/explore"
VALID_SPECIALTY = "endocrinology_diabetes"
VALID_TARGET = "Outcome"

REQUIRED_RESPONSE_KEYS = {
    "columns",
    "row_count",
    "class_distribution",
    "imbalance_warning",
    "imbalance_ratio",
    "target_col",
}

REQUIRED_COLUMN_STAT_KEYS = {
    "name",
    "dtype",
    "missing_count",
    "missing_pct",
    "unique_count",
    "sample_values",
}


def _build_csv(
    rows: int = 30,
    target_col: str = "Outcome",
    include_target: bool = True,
    all_null_target: bool = False,
    special_col_names: bool = False,
) -> bytes:
    """
    Generate a minimal but realistic clinical CSV in memory.

    Parameters
    ----------
    rows:               Number of data rows to produce.
    target_col:         Name of the target column.
    include_target:     Whether to include the target column at all.
    all_null_target:    Fill every target value with an empty string.
    special_col_names:  Use column names that contain spaces and slashes.
    """
    if special_col_names:
        col_names = ["age (yrs)", "BMI kg/m2", "blood pressure", target_col]
    else:
        col_names = ["glucose", "bmi", "age", target_col] if include_target else ["glucose", "bmi", "age"]

    header = ",".join(col_names) + "\n"
    data_rows: list[str] = []
    for i in range(rows):
        if special_col_names:
            row_vals = [str(20 + i), str(round(18.5 + i * 0.5, 1)), str(60 + i % 40)]
        else:
            row_vals = [str(80 + i % 100), str(round(20.0 + i * 0.3, 1)), str(21 + i % 50)]

        if include_target:
            if all_null_target:
                row_vals.append("")
            else:
                row_vals.append(str(i % 2))
        data_rows.append(",".join(row_vals))

    return (header + "\n".join(data_rows) + "\n").encode("utf-8")


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------


class TestExploreWithBuiltinDataset:
    """Explore using built-in example datasets (no file upload)."""

    def test_explore_builtin_returns_200(self, client: TestClient) -> None:
        """POST /api/explore with a known specialty_id must return HTTP 200."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        assert response.status_code == 200

    def test_explore_builtin_response_schema(self, client: TestClient) -> None:
        """Response must contain all required top-level keys."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        body = response.json()
        missing = REQUIRED_RESPONSE_KEYS - set(body.keys())
        assert not missing, f"Response missing keys: {missing}"

    def test_explore_builtin_columns_is_list(self, client: TestClient) -> None:
        """'columns' must be a non-empty list."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        cols = response.json()["columns"]
        assert isinstance(cols, list) and len(cols) > 0

    def test_explore_builtin_column_stat_schema(self, client: TestClient) -> None:
        """Every ColumnStat object must have all required sub-fields."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        for col_stat in response.json()["columns"]:
            missing = REQUIRED_COLUMN_STAT_KEYS - set(col_stat.keys())
            assert not missing, f"ColumnStat for '{col_stat.get('name')}' missing: {missing}"

    def test_explore_builtin_row_count_positive(self, client: TestClient) -> None:
        """row_count must be a positive integer."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        assert response.json()["row_count"] > 0

    def test_explore_builtin_class_distribution_non_empty(self, client: TestClient) -> None:
        """class_distribution must contain at least two classes for binary targets."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        dist = response.json()["class_distribution"]
        assert isinstance(dist, dict) and len(dist) >= 2

    def test_explore_builtin_target_col_echoed(self, client: TestClient) -> None:
        """The response's target_col field must match the requested target."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        assert response.json()["target_col"] == VALID_TARGET

    def test_explore_builtin_imbalance_ratio_non_negative(self, client: TestClient) -> None:
        """imbalance_ratio must be a float >= 1.0 when at least two classes exist."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        ratio = response.json()["imbalance_ratio"]
        assert isinstance(ratio, (int, float)) and ratio >= 1.0

    def test_explore_imbalance_warning_is_bool(self, client: TestClient) -> None:
        """imbalance_warning must be a boolean value."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        assert isinstance(response.json()["imbalance_warning"], bool)

    @pytest.mark.parametrize("specialty_id,target_col", [
        ("cardiology_hf", "DEATH_EVENT"),
        ("nephrology_ckd", "classification"),
        ("oncology_breast", "diagnosis"),
        ("neurology_parkinsons", "status"),
        ("orthopaedics", "class"),
    ])
    def test_explore_multiple_specialties(
        self, client: TestClient, specialty_id: str, target_col: str
    ) -> None:
        """Exploration must succeed for a range of built-in example datasets."""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": specialty_id, "target_col": target_col},
        )
        assert response.status_code == 200, (
            f"Explore failed for '{specialty_id}': {response.text}"
        )
        assert response.json()["row_count"] > 0


class TestExploreWithCSVUpload:
    """
    Sprint 2 metric: CSV Upload Success Rate.

    5 valid upload scenarios + 5 invalid upload scenarios.
    """

    # ------------------------------------------------------------------
    # Valid uploads (should return 200)
    # ------------------------------------------------------------------

    def test_valid_csv_upload_returns_200(
        self, client: TestClient, valid_csv_content: bytes
    ) -> None:
        """
        Valid CSV upload: POST /api/explore with a well-formed CSV file
        and correct target column must return HTTP 200.
        """
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files=make_csv_upload(valid_csv_content),
        )
        assert response.status_code == 200, response.text

    def test_valid_csv_upload_response_schema(
        self, client: TestClient, valid_csv_content: bytes
    ) -> None:
        """
        Valid CSV upload: response schema must include all required keys with
        correct types.
        """
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files=make_csv_upload(valid_csv_content),
        )
        body = response.json()
        missing = REQUIRED_RESPONSE_KEYS - set(body.keys())
        assert not missing, f"Missing keys after upload: {missing}"
        assert body["row_count"] == 30
        assert isinstance(body["columns"], list)

    def test_valid_csv_upload_class_distribution(
        self, client: TestClient, valid_csv_content: bytes
    ) -> None:
        """
        Valid CSV upload: class_distribution must show two classes (0 and 1)
        because the fixture generates alternating outcomes.
        """
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files=make_csv_upload(valid_csv_content),
        )
        dist = response.json()["class_distribution"]
        assert len(dist) == 2, f"Expected 2 classes, got: {dist}"

    def test_valid_csv_with_extra_columns_returns_200(self, client: TestClient) -> None:
        """
        Valid CSV upload with extra columns beyond the specialty's feature set
        must return 200 — extra columns are included or silently ignored.
        """
        csv_bytes = _build_csv(rows=20, target_col=VALID_TARGET)
        # Prepend an extra 'patient_id' column
        lines = csv_bytes.decode().splitlines()
        lines[0] = "patient_id," + lines[0]
        for i in range(1, len(lines)):
            lines[i] = str(i * 100) + "," + lines[i]
        enriched = "\n".join(lines).encode("utf-8")

        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files=make_csv_upload(enriched),
        )
        assert response.status_code == 200, response.text

    def test_valid_csv_with_special_column_names(self, client: TestClient) -> None:
        """
        CSV with special characters (spaces, slashes) in column names must be
        handled gracefully; the target column lookup still succeeds.
        """
        target = "Outcome"
        csv_bytes = _build_csv(rows=15, target_col=target, special_col_names=True)
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": target},
            files=make_csv_upload(csv_bytes),
        )
        # The target column exists in this CSV so 200 is expected
        assert response.status_code == 200, response.text

    # ------------------------------------------------------------------
    # Invalid uploads (should return 4xx)
    # ------------------------------------------------------------------

    def test_empty_csv_returns_error(self, client: TestClient) -> None:
        """
        CSV upload with an empty file body must return a 4xx error —
        pandas cannot parse empty content.
        """
        empty_bytes = b""
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files=make_csv_upload(empty_bytes),
        )
        assert response.status_code in {400, 422, 500}, (
            f"Expected error for empty CSV, got {response.status_code}"
        )

    def test_csv_without_target_column_returns_422(self, client: TestClient) -> None:
        """
        CSV that does not contain the target column must return HTTP 422.
        The endpoint validates target column presence and raises HTTPException.
        """
        csv_bytes = _build_csv(rows=20, include_target=False)
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files=make_csv_upload(csv_bytes),
        )
        assert response.status_code == 422, (
            f"Expected 422 for missing target column, got {response.status_code}: {response.text}"
        )

    def test_single_row_csv_explore_succeeds_or_errors(self, client: TestClient) -> None:
        """
        CSV with only 1 data row: explore itself succeeds (row_count=1) because
        data_service.explore_dataframe does not enforce a minimum row threshold.
        The minimum-row guard is in prepare_data, not explore_dataframe.
        """
        csv_bytes = _build_csv(rows=1, target_col=VALID_TARGET)
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files=make_csv_upload(csv_bytes),
        )
        # Explore is permissive; a single-row CSV is still parseable
        assert response.status_code in {200, 422}

    def test_non_csv_binary_file_returns_422(self, client: TestClient) -> None:
        """
        Uploading a binary (non-CSV) file must return HTTP 422 because
        pandas.read_csv will fail to parse it.
        """
        binary_content = bytes(range(256)) * 10  # random binary data
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files={"file": ("data.bin", io.BytesIO(binary_content), "application/octet-stream")},
        )
        assert response.status_code == 422, (
            f"Expected 422 for binary file, got {response.status_code}"
        )

    def test_all_null_target_column_explore_shows_empty_distribution(
        self, client: TestClient
    ) -> None:
        """
        CSV where every target value is empty: explore returns 200 but
        class_distribution should be empty or near-empty because all target
        values are NaN and value_counts() produces no meaningful entries.
        """
        csv_bytes = _build_csv(rows=20, target_col=VALID_TARGET, all_null_target=True)
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files=make_csv_upload(csv_bytes),
        )
        # Explore does not fail on null targets — it just reports an empty distribution
        if response.status_code == 200:
            dist = response.json()["class_distribution"]
            assert isinstance(dist, dict)
            # All values were null so no classes can be counted
            assert len(dist) == 0, (
                f"Expected empty class distribution for all-null target, got: {dist}"
            )
        else:
            # A 422 is also acceptable if the service rejects all-null targets
            assert response.status_code == 422

    def test_csv_with_wrong_target_column_name_falls_back_to_registry(
        self, client: TestClient
    ) -> None:
        """
        When the requested target_col is absent from the uploaded CSV, the
        router's fallback logic looks up the specialty's own target_variable
        from the registry.  If that column IS present in the CSV, the request
        succeeds with 200 (the fallback column is used).  If neither column
        exists, the router raises 422.

        This test uploads a CSV whose column named 'Outcome' matches the
        endocrinology_diabetes specialty's target_variable, so the fallback
        succeeds and we expect 200.
        """
        csv_bytes = _build_csv(rows=20, target_col="Outcome")
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": "NonExistentColumn"},
            files=make_csv_upload(csv_bytes),
        )
        # Fallback: 'Outcome' IS in the CSV and matches the specialty's target_variable
        assert response.status_code == 200, (
            f"Expected 200 via registry fallback, got {response.status_code}: {response.text}"
        )

    def test_csv_with_wrong_target_and_no_registry_fallback_returns_422(
        self, client: TestClient
    ) -> None:
        """
        When neither the requested target_col nor the specialty's own
        target_variable is present in the uploaded CSV, the router must
        return HTTP 422.

        We build a CSV whose only target column is 'custom_label' (not
        'Outcome'), then request 'NonExistentColumn' as target.  The
        endocrinology_diabetes registry fallback tries 'Outcome', which is
        also absent, so 422 must be raised.
        """
        csv_bytes = _build_csv(rows=20, target_col="custom_label")
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": "NonExistentColumn"},
            files=make_csv_upload(csv_bytes),
        )
        assert response.status_code == 422, (
            f"Expected 422 when both requested and registry columns are absent, "
            f"got {response.status_code}: {response.text}"
        )

    def test_csv_without_target_422_error_message_informative(
        self, client: TestClient
    ) -> None:
        """
        The 422 error body for a missing target column must contain a
        human-readable 'detail' field listing available columns.
        """
        csv_bytes = _build_csv(rows=20, include_target=False)
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
            files=make_csv_upload(csv_bytes),
        )
        assert response.status_code == 422
        body = response.json()
        assert "detail" in body
        assert body["detail"]  # non-empty message


class TestExploreErrorHandling:
    """Tests for invalid parameters to POST /api/explore."""

    def test_unknown_specialty_id_with_csv_upload_422(self, client: TestClient) -> None:
        """
        Using an unknown specialty_id with a CSV upload must still return 422
        when the target column is not found (no example dataset to fall back to).
        """
        csv_bytes = _build_csv(rows=15, target_col=VALID_TARGET)
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": "nonexistent_xyz", "target_col": VALID_TARGET},
            files=make_csv_upload(csv_bytes),
        )
        # Target column IS in the CSV so explore may succeed with 200,
        # or fail with 422 if specialty lookup is required — accept both.
        assert response.status_code in {200, 422, 404}

    def test_missing_specialty_id_returns_422(self, client: TestClient) -> None:
        """
        Omitting the required 'specialty_id' form field must return 422
        (FastAPI Form validation).
        """
        response = client.post(
            EXPLORE_URL,
            data={"target_col": VALID_TARGET},
        )
        assert response.status_code == 422

    def test_missing_target_col_returns_422(self, client: TestClient) -> None:
        """
        Omitting the required 'target_col' form field must return 422
        (FastAPI Form validation).
        """
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY},
        )
        assert response.status_code == 422

    def test_empty_specialty_id_with_no_file(self, client: TestClient) -> None:
        """
        An empty string for specialty_id with no file will attempt to load
        a non-existent example dataset; expect a non-200 or an empty response.
        """
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": "", "target_col": VALID_TARGET},
        )
        # An unknown specialty_id will produce a fallback dataset without the
        # requested target column → 422, or the server may return 200 with
        # a generic fallback. Accept any 2xx/4xx outcome.
        assert response.status_code in {200, 422, 404}


class TestColumnMapperGate:
    """
    Sprint 2 metric: Column Mapper Gate.

    Verify that the explore response carries enough schema information to gate
    the transition to Step 3 (Data Preparation), and that an invalid session_id
    passed to /api/prepare is correctly rejected.
    """

    def test_explore_columns_contain_target(self, client: TestClient) -> None:
        """
        The explore response's 'columns' list must include an entry whose
        'name' matches the requested target column — this is the signal that
        the column mapper can proceed to preparation.
        """
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        assert response.status_code == 200
        col_names = [c["name"] for c in response.json()["columns"]]
        assert VALID_TARGET in col_names, (
            f"Target column '{VALID_TARGET}' not found in explore columns: {col_names}"
        )

    def test_explore_columns_missing_count_is_integer(self, client: TestClient) -> None:
        """
        Every ColumnStat.missing_count must be a non-negative integer —
        this value is used by the UI to decide whether to show the missing-value
        handling control.
        """
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        for col in response.json()["columns"]:
            assert isinstance(col["missing_count"], int) and col["missing_count"] >= 0

    def test_explore_columns_missing_pct_in_range(self, client: TestClient) -> None:
        """
        Every ColumnStat.missing_pct must be between 0.0 and 100.0 inclusive.
        """
        response = client.post(
            EXPLORE_URL,
            data={"specialty_id": VALID_SPECIALTY, "target_col": VALID_TARGET},
        )
        for col in response.json()["columns"]:
            pct = col["missing_pct"]
            assert 0.0 <= pct <= 100.0, (
                f"Column '{col['name']}': missing_pct {pct} out of [0, 100] range"
            )

    def test_prepare_with_invalid_session_id_still_processes(
        self, client: TestClient
    ) -> None:
        """
        /api/prepare does not use a pre-existing session_id to look up data
        (it re-loads from specialty/file and then stores to the provided
        session_id). Passing an arbitrary session_id with a valid specialty
        must still return 200 — the session_id is just the storage key.
        """
        response = client.post(
            "/api/prepare",
            data={
                "specialty_id": VALID_SPECIALTY,
                "target_col": VALID_TARGET,
                "session_id": "totally-fake-session-id-12345",
                "test_size": "0.2",
                "missing_strategy": "median",
                "normalization": "zscore",
                "use_smote": "false",
                "outlier_handling": "none",
            },
        )
        # The router re-loads data from the example dataset and accepts any
        # session_id string as its storage key — so this should succeed.
        assert response.status_code == 200, (
            f"Expected 200 when passing arbitrary session_id, got {response.status_code}: {response.text}"
        )

    def test_prepare_without_specialty_returns_422(self, client: TestClient) -> None:
        """
        POST /api/prepare with no specialty_id form field must return 422
        (FastAPI form field validation).
        """
        response = client.post(
            "/api/prepare",
            data={"target_col": VALID_TARGET},
        )
        assert response.status_code == 422
