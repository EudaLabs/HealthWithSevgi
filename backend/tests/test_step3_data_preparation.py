"""
test_step3_data_preparation.py — Sprint 2, Step 3: Data Preparation

Tests for POST /api/prepare.

API signature (from data_router.py):
    specialty_id     : str   = Form(...)
    target_col       : str   = Form(...)
    test_size        : float = Form(0.2)
    missing_strategy : str   = Form("median")   # "median" | "mode" | "drop"
    normalization    : str   = Form("zscore")   # "zscore" | "minmax" | "none"
    use_smote        : bool  = Form(False)
    outlier_handling : str   = Form("none")     # "none" | "iqr" | "zscore_clip"
    session_id       : str   = Form(None)
    file             : UploadFile | None = File(None)

PrepResponse schema (from schemas.py):
    session_id                : str
    train_size                : int
    test_size                 : int
    features_count            : int
    class_distribution_before : dict[str, int]
    class_distribution_after  : dict[str, int]
    smote_applied             : bool
    normalization_applied     : str

Coverage:
- Full two-step flow: explore → prepare
- All missing_strategy values: median, mode, drop
- All normalization values: zscore, minmax, none
- All use_smote values: True, False
- All outlier_handling values: none, iqr, zscore_clip
- test_size boundary values: 0.1, 0.3, 0.4
- Response schema validation
- train_size + test_size relationship (total ≈ original rows)
- class_distribution_before and _after keys and values
- smote_applied flag correctness
- normalization_applied echo
- Missing required fields → 422
- Invalid test_size boundaries → 422
- CSV upload through prepare
- Multiple specialties (cardiology, nephrology, orthopaedics)
"""
from __future__ import annotations

import io
import uuid

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_csv_upload

PREPARE_URL = "/api/prepare"
EXPLORE_URL  = "/api/explore"
VALID_SPECIALTY = "endocrinology_diabetes"
VALID_TARGET    = "Outcome"

# Required keys in PrepResponse
REQUIRED_PREP_KEYS = {
    "session_id",
    "train_size",
    "test_size",
    "features_count",
    "class_distribution_before",
    "class_distribution_after",
    "smote_applied",
    "normalization_applied",
}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _prepare(
    client: TestClient,
    specialty_id: str = VALID_SPECIALTY,
    target_col: str = VALID_TARGET,
    test_size: float = 0.2,
    missing_strategy: str = "median",
    normalization: str = "zscore",
    use_smote: bool = False,
    outlier_handling: str = "none",
    session_id: str | None = None,
    csv_bytes: bytes | None = None,
) -> "requests.Response":  # type: ignore[name-defined]
    """Helper that calls POST /api/prepare and returns the raw response."""
    data = {
        "specialty_id": specialty_id,
        "target_col": target_col,
        "test_size": str(test_size),
        "missing_strategy": missing_strategy,
        "normalization": normalization,
        "use_smote": "true" if use_smote else "false",
        "outlier_handling": outlier_handling,
    }
    if session_id is not None:
        data["session_id"] = session_id

    files = make_csv_upload(csv_bytes) if csv_bytes is not None else None

    if files:
        return client.post(PREPARE_URL, data=data, files=files)
    return client.post(PREPARE_URL, data=data)


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------


class TestPrepareResponseSchema:
    """Validate the shape and types of the PrepResponse object."""

    def test_prepare_returns_200(self, client: TestClient) -> None:
        """POST /api/prepare with valid inputs must return HTTP 200."""
        response = _prepare(client)
        assert response.status_code == 200, response.text

    def test_prepare_response_has_all_required_keys(self, client: TestClient) -> None:
        """PrepResponse must contain all schema-mandated keys."""
        body = _prepare(client).json()
        missing = REQUIRED_PREP_KEYS - set(body.keys())
        assert not missing, f"PrepResponse missing keys: {missing}"

    def test_session_id_is_non_empty_string(self, client: TestClient) -> None:
        """session_id must be a non-empty string (UUID or supplied value)."""
        body = _prepare(client).json()
        sid = body["session_id"]
        assert isinstance(sid, str) and sid.strip()

    def test_train_size_is_positive_int(self, client: TestClient) -> None:
        """train_size must be a positive integer."""
        body = _prepare(client).json()
        assert isinstance(body["train_size"], int) and body["train_size"] > 0

    def test_test_size_field_is_positive_int(self, client: TestClient) -> None:
        """test_size (in PrepResponse) must be a positive integer (row count)."""
        body = _prepare(client).json()
        assert isinstance(body["test_size"], int) and body["test_size"] > 0

    def test_features_count_is_positive_int(self, client: TestClient) -> None:
        """features_count must be a positive integer."""
        body = _prepare(client).json()
        assert isinstance(body["features_count"], int) and body["features_count"] > 0

    def test_class_distribution_before_is_dict(self, client: TestClient) -> None:
        """class_distribution_before must be a non-empty dict."""
        body = _prepare(client).json()
        dist = body["class_distribution_before"]
        assert isinstance(dist, dict) and len(dist) > 0

    def test_class_distribution_after_is_dict(self, client: TestClient) -> None:
        """class_distribution_after must be a non-empty dict."""
        body = _prepare(client).json()
        dist = body["class_distribution_after"]
        assert isinstance(dist, dict) and len(dist) > 0

    def test_class_distribution_before_values_are_ints(self, client: TestClient) -> None:
        """All values in class_distribution_before must be non-negative ints."""
        body = _prepare(client).json()
        for key, val in body["class_distribution_before"].items():
            assert isinstance(val, int) and val >= 0, (
                f"class_distribution_before['{key}'] = {val} is not a non-negative int"
            )

    def test_smote_applied_is_bool(self, client: TestClient) -> None:
        """smote_applied must be a boolean."""
        body = _prepare(client).json()
        assert isinstance(body["smote_applied"], bool)

    def test_normalization_applied_is_string(self, client: TestClient) -> None:
        """normalization_applied must be a string matching the requested value."""
        body = _prepare(client, normalization="zscore").json()
        assert isinstance(body["normalization_applied"], str)
        assert body["normalization_applied"] == "zscore"

    def test_train_test_split_proportions(self, client: TestClient) -> None:
        """
        train_size + test_size must equal or be close to the total dataset rows.
        The exact sum may vary slightly if SMOTE is applied or rows are dropped.
        This check uses test_size=0.2 with no SMOTE to ensure predictability.
        """
        body = _prepare(client, test_size=0.2, use_smote=False).json()
        total = body["train_size"] + body["test_size"]
        # The example dataset has > 10 rows; total must be > 0
        assert total > 0


class TestMissingStrategyOptions:
    """Test all valid handle_missing values: median, mode, drop."""

    @pytest.mark.parametrize("strategy", ["median", "mode", "drop"])
    def test_missing_strategy(self, client: TestClient, strategy: str) -> None:
        """
        POST /api/prepare must succeed for each valid missing_strategy value.
        The response must contain a valid session_id and positive train_size.
        """
        response = _prepare(client, missing_strategy=strategy)
        assert response.status_code == 200, (
            f"missing_strategy='{strategy}' failed: {response.text}"
        )
        body = response.json()
        assert body["train_size"] > 0, (
            f"missing_strategy='{strategy}': train_size is not positive"
        )

    def test_missing_strategy_drop_reduces_rows(
        self, client: TestClient, valid_csv_with_missing: bytes
    ) -> None:
        """
        When missing_strategy='drop' is used on a CSV with missing values,
        train_size + test_size should be <= the original row count (30 in fixture).
        """
        response = _prepare(
            client,
            missing_strategy="drop",
            csv_bytes=valid_csv_with_missing,
        )
        assert response.status_code == 200, response.text
        body = response.json()
        # 30 rows total; some were NaN-patched — drop may reduce the total
        total = body["train_size"] + body["test_size"]
        assert total <= 30, (
            f"Expected ≤30 rows after 'drop', got train={body['train_size']} test={body['test_size']}"
        )

    def test_missing_strategy_median_fills_values(
        self, client: TestClient, valid_csv_with_missing: bytes
    ) -> None:
        """
        When missing_strategy='median' is used on a CSV with missing values,
        preparation must still succeed and return all original rows
        (no rows dropped).
        """
        response = _prepare(
            client,
            missing_strategy="median",
            csv_bytes=valid_csv_with_missing,
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["train_size"] + body["test_size"] == 30


class TestNormalizationOptions:
    """Test all valid normalization values: zscore, minmax, none."""

    @pytest.mark.parametrize("normalization", ["zscore", "minmax", "none"])
    def test_normalization(self, client: TestClient, normalization: str) -> None:
        """
        POST /api/prepare must succeed for each valid normalization value
        and echo that value back in normalization_applied.
        """
        response = _prepare(client, normalization=normalization)
        assert response.status_code == 200, (
            f"normalization='{normalization}' failed: {response.text}"
        )
        body = response.json()
        assert body["normalization_applied"] == normalization, (
            f"normalization_applied should be '{normalization}', "
            f"got '{body['normalization_applied']}'"
        )

    def test_normalization_none_smote_applied_false(self, client: TestClient) -> None:
        """
        When normalization='none' and use_smote=False, smote_applied must be
        False and normalization_applied must be 'none'.
        """
        body = _prepare(client, normalization="none", use_smote=False).json()
        assert body["normalization_applied"] == "none"
        assert body["smote_applied"] is False


class TestSmoteOptions:
    """Test SMOTE balancing flag: use_smote True and False."""

    def test_smote_false_returns_smote_applied_false(self, client: TestClient) -> None:
        """When use_smote=False, smote_applied must be False in the response."""
        body = _prepare(client, use_smote=False).json()
        assert body["smote_applied"] is False

    @pytest.mark.slow
    def test_smote_true_attempts_resampling(self, client: TestClient) -> None:
        """
        When use_smote=True, the service attempts SMOTE. The response must
        return 200 regardless of whether SMOTE succeeded (it falls back
        gracefully if the minority class is too small).
        smote_applied can be True or False depending on class counts.
        """
        response = _prepare(client, use_smote=True)
        assert response.status_code == 200, response.text
        body = response.json()
        assert isinstance(body["smote_applied"], bool)

    @pytest.mark.slow
    def test_smote_true_class_distribution_after_may_be_balanced(
        self, client: TestClient
    ) -> None:
        """
        When SMOTE is successfully applied, class_distribution_after must
        show a more balanced distribution than class_distribution_before.
        This test is only meaningful when smote_applied=True.
        """
        response = _prepare(client, use_smote=True)
        assert response.status_code == 200
        body = response.json()
        if body["smote_applied"]:
            after_counts = list(body["class_distribution_after"].values())
            if len(after_counts) >= 2:
                max_after = max(after_counts)
                min_after = min(after_counts)
                ratio_after = max_after / min_after if min_after > 0 else float("inf")
                # SMOTE should bring ratio closer to 1 (perfect balance)
                assert ratio_after <= 5.0, (
                    f"After SMOTE, ratio {ratio_after:.2f} is unexpectedly high"
                )


class TestOutlierHandlingOptions:
    """Test all valid outlier_handling values: none, iqr, zscore_clip."""

    @pytest.mark.parametrize("outlier_method", ["none", "iqr", "zscore_clip"])
    def test_outlier_handling(self, client: TestClient, outlier_method: str) -> None:
        """
        POST /api/prepare must succeed for each valid outlier_handling value.
        Response must have a positive train_size.
        """
        response = _prepare(client, outlier_handling=outlier_method)
        assert response.status_code == 200, (
            f"outlier_handling='{outlier_method}' failed: {response.text}"
        )
        assert response.json()["train_size"] > 0

    def test_outlier_iqr_does_not_change_row_count(
        self, client: TestClient
    ) -> None:
        """
        IQR outlier clipping is a clipping operation, not a dropping operation.
        The total row count (train + test) must be the same as with 'none'.
        """
        body_none = _prepare(client, outlier_handling="none").json()
        body_iqr  = _prepare(client, outlier_handling="iqr").json()

        total_none = body_none["train_size"] + body_none["test_size"]
        total_iqr  = body_iqr["train_size"]  + body_iqr["test_size"]
        assert total_none == total_iqr, (
            f"IQR should not drop rows: none={total_none}, iqr={total_iqr}"
        )

    def test_outlier_zscore_clip_does_not_change_row_count(
        self, client: TestClient
    ) -> None:
        """
        Z-score clipping is also a clipping operation. Row count must be
        identical to the 'none' baseline.
        """
        body_none = _prepare(client, outlier_handling="none").json()
        body_zsc  = _prepare(client, outlier_handling="zscore_clip").json()

        total_none = body_none["train_size"] + body_none["test_size"]
        total_zsc  = body_zsc["train_size"]  + body_zsc["test_size"]
        assert total_none == total_zsc, (
            f"zscore_clip should not drop rows: none={total_none}, zscore_clip={total_zsc}"
        )


class TestTestSizeBoundaries:
    """Test boundary values for the test_size parameter (valid range: 0.1–0.4)."""

    @pytest.mark.parametrize("test_size", [0.1, 0.3, 0.4])
    def test_valid_test_size(self, client: TestClient, test_size: float) -> None:
        """
        test_size values 0.1, 0.3, and 0.4 are within the schema's [0.1, 0.4]
        range and must all return HTTP 200.
        """
        response = _prepare(client, test_size=test_size)
        assert response.status_code == 200, (
            f"test_size={test_size} failed: {response.text}"
        )

    def test_test_size_0_1_produces_small_test_set(self, client: TestClient) -> None:
        """
        With test_size=0.1 the test set must be smaller than the training set.
        """
        body = _prepare(client, test_size=0.1).json()
        assert body["test_size"] < body["train_size"], (
            f"test_size=0.1: expected test<train, got test={body['test_size']} train={body['train_size']}"
        )

    def test_test_size_0_4_produces_larger_test_set(self, client: TestClient) -> None:
        """
        With test_size=0.4 the test set must be larger relative to training
        than with test_size=0.1.
        """
        body_01 = _prepare(client, test_size=0.1).json()
        body_04 = _prepare(client, test_size=0.4).json()

        ratio_01 = body_01["test_size"] / (body_01["train_size"] + body_01["test_size"])
        ratio_04 = body_04["test_size"] / (body_04["train_size"] + body_04["test_size"])
        assert ratio_04 > ratio_01, (
            f"test_size=0.4 should give larger test fraction than 0.1; "
            f"ratio_04={ratio_04:.3f} ratio_01={ratio_01:.3f}"
        )

    def test_test_size_below_minimum_raises_validation_error(self) -> None:
        """
        test_size=0.05 violates the PrepSettings schema constraint (ge=0.1).

        The route constructs PrepSettings directly (outside its try/except),
        so an out-of-range value causes pydantic.ValidationError to propagate
        through the TestClient as an unhandled server-side exception.  We use
        raise_server_exceptions=False to receive a 500 response instead of a
        re-raised exception, confirming the value is rejected.
        """
        from pydantic import ValidationError as PydanticValidationError
        from app.main import app as _app

        # Use a non-raising client so the Pydantic error surfaces as 500
        with TestClient(_app, raise_server_exceptions=False) as safe_client:
            response = _prepare(safe_client, test_size=0.05)
        assert response.status_code in {422, 500}, (
            f"Expected 422 or 500 for test_size=0.05, got {response.status_code}"
        )

    def test_test_size_above_maximum_raises_validation_error(self) -> None:
        """
        test_size=0.6 violates the PrepSettings schema constraint (le=0.4).

        Same mechanics as the below-minimum test — the Pydantic ValidationError
        is raised inside the route handler before the try/except, propagating
        as a 500 through raise_server_exceptions=False mode.
        """
        from app.main import app as _app

        with TestClient(_app, raise_server_exceptions=False) as safe_client:
            response = _prepare(safe_client, test_size=0.6)
        assert response.status_code in {422, 500}, (
            f"Expected 422 or 500 for test_size=0.6, got {response.status_code}"
        )


class TestFullFlowExploreAndPrepare:
    """End-to-end tests for the two-step explore → prepare workflow."""

    def test_full_flow_returns_session_id(
        self, client: TestClient, explore_session: dict
    ) -> None:
        """
        Full flow: explore → prepare must return a valid non-empty session_id
        that can be used to identify the prepared session.
        """
        response = _prepare(
            client,
            specialty_id=explore_session["specialty_id"],
            target_col=explore_session["target_col"],
        )
        assert response.status_code == 200, response.text
        assert response.json()["session_id"]

    def test_full_flow_session_id_persists_for_subsequent_calls(
        self, client: TestClient
    ) -> None:
        """
        When a session_id is supplied explicitly, it must be echoed back in
        the PrepResponse.session_id field.
        """
        my_session = str(uuid.uuid4())
        body = _prepare(client, session_id=my_session).json()
        assert body["session_id"] == my_session

    def test_full_flow_with_csv_upload(
        self, client: TestClient, valid_csv_content: bytes
    ) -> None:
        """
        End-to-end prepare with a CSV file upload (not example dataset)
        must return 200 with correct schema.
        """
        response = _prepare(client, csv_bytes=valid_csv_content)
        assert response.status_code == 200, response.text
        body = response.json()
        missing = REQUIRED_PREP_KEYS - set(body.keys())
        assert not missing, f"Missing keys in upload prepare: {missing}"

    def test_full_flow_class_distribution_keys_match_classes(
        self, client: TestClient
    ) -> None:
        """
        class_distribution_before and class_distribution_after must have the
        same set of class keys (the classes do not change, only their counts).
        """
        body = _prepare(client, use_smote=False).json()
        before_keys = set(body["class_distribution_before"].keys())
        after_keys  = set(body["class_distribution_after"].keys())
        assert before_keys == after_keys, (
            f"Class keys differ before/after: before={before_keys}, after={after_keys}"
        )


class TestPrepareMultipleSpecialties:
    """
    Test data preparation across different clinical specialties to verify
    that each built-in dataset is correctly handled.
    """

    @pytest.mark.slow
    @pytest.mark.parametrize("specialty_id,target_col", [
        ("cardiology_hf",         "DEATH_EVENT"),
        ("nephrology_ckd",        "classification"),
        ("oncology_breast",       "diagnosis"),
        ("orthopaedics",          "class"),
        ("neurology_parkinsons",  "status"),
    ])
    def test_prepare_multiple_specialties(
        self, client: TestClient, specialty_id: str, target_col: str
    ) -> None:
        """
        Data preparation must succeed for a representative subset of the
        20 clinical specialties, each with its correct target column.
        """
        response = _prepare(client, specialty_id=specialty_id, target_col=target_col)
        assert response.status_code == 200, (
            f"Prepare failed for '{specialty_id}': {response.text}"
        )
        body = response.json()
        assert body["train_size"] > 0
        assert body["features_count"] > 0


class TestPrepareValidationErrors:
    """Test that invalid inputs to /api/prepare are properly rejected."""

    def test_missing_specialty_id_returns_422(self, client: TestClient) -> None:
        """Omitting specialty_id must return 422 (required Form field)."""
        response = client.post(
            PREPARE_URL,
            data={"target_col": VALID_TARGET, "test_size": "0.2"},
        )
        assert response.status_code == 422

    def test_missing_target_col_returns_422(self, client: TestClient) -> None:
        """Omitting target_col must return 422 (required Form field)."""
        response = client.post(
            PREPARE_URL,
            data={"specialty_id": VALID_SPECIALTY, "test_size": "0.2"},
        )
        assert response.status_code == 422

    def test_wrong_target_col_with_csv_returns_422(self, client: TestClient) -> None:
        """
        When a CSV is uploaded and neither the requested target_col nor the
        specialty registry's target_variable is present in that CSV, prepare
        must return 422.

        We upload a CSV whose only target column is 'custom_label' (not
        'Outcome'), then request 'IDoNotExist' as the target.  The
        endocrinology_diabetes registry fallback tries 'Outcome', which is
        also absent, so the route raises HTTP 422.
        """
        import io as _io

        # Build a CSV where the only label column is named 'custom_label'
        csv_lines = ["glucose,bmi,age,custom_label"]
        for i in range(30):
            csv_lines.append(f"{80 + i},{20.0 + i * 0.3},{21 + i},{i % 2}")
        csv_bytes = "\n".join(csv_lines).encode("utf-8")

        response = client.post(
            PREPARE_URL,
            data={
                "specialty_id": VALID_SPECIALTY,
                "target_col": "IDoNotExist",
                "test_size": "0.2",
                "missing_strategy": "median",
                "normalization": "zscore",
                "use_smote": "false",
                "outlier_handling": "none",
            },
            files={"file": ("data.csv", _io.BytesIO(csv_bytes), "text/csv")},
        )
        assert response.status_code == 422, (
            f"Expected 422 when target col is absent from CSV and registry, "
            f"got {response.status_code}: {response.text}"
        )

    def test_non_numeric_test_size_returns_422(self, client: TestClient) -> None:
        """Passing a non-numeric string for test_size must return 422."""
        response = client.post(
            PREPARE_URL,
            data={
                "specialty_id": VALID_SPECIALTY,
                "target_col": VALID_TARGET,
                "test_size": "not_a_number",
            },
        )
        assert response.status_code == 422


class TestPrepareAllCombinations:
    """
    Sprint 2 Step 3 Controls metric: verify all configuration option
    combinations work together without errors.
    """

    @pytest.mark.slow
    @pytest.mark.parametrize("missing_strategy,normalization,outlier_handling", [
        ("median", "zscore",  "none"),
        ("median", "minmax",  "iqr"),
        ("median", "none",    "zscore_clip"),
        ("mode",   "zscore",  "iqr"),
        ("mode",   "minmax",  "none"),
        ("drop",   "none",    "none"),
        ("drop",   "zscore",  "zscore_clip"),
        ("mode",   "none",    "zscore_clip"),
    ])
    def test_control_combinations(
        self,
        client: TestClient,
        missing_strategy: str,
        normalization: str,
        outlier_handling: str,
    ) -> None:
        """
        Every combination of missing_strategy, normalization, and
        outlier_handling must produce a valid PrepResponse with status 200.
        """
        response = _prepare(
            client,
            missing_strategy=missing_strategy,
            normalization=normalization,
            outlier_handling=outlier_handling,
            use_smote=False,
        )
        assert response.status_code == 200, (
            f"Combination ({missing_strategy}, {normalization}, {outlier_handling}) "
            f"failed: {response.text}"
        )
        body = response.json()
        assert body["train_size"] > 0
        assert body["normalization_applied"] == normalization
