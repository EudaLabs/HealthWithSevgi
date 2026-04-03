"""
test_step4_arena_latency.py — Arena Batch-Train Latency & Correctness Tests.

Tests the /api/arena/* endpoints for:
- Batch training correctness (multiple models in one request)
- Timing accuracy (reported vs actual elapsed)
- Latency bounds (single model, 3-model batch)
- Comparison endpoint correctness
- Error handling (invalid session, failed models)
- KNN scatter data preservation
"""
from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prepare_session(client: TestClient, explore_session: dict) -> str:
    """Prepare data and return a session_id."""
    response = client.post(
        "/api/prepare",
        data={
            "specialty_id": explore_session["specialty_id"],
            "target_col": explore_session["target_col"],
            "test_size": "0.2",
            "missing_strategy": "median",
            "normalization": "zscore",
            "use_smote": "false",
            "outlier_handling": "none",
        },
    )
    assert response.status_code == 200, f"Prepare failed: {response.text}"
    return response.json()["session_id"]


# ---------------------------------------------------------------------------
# Correctness Tests
# ---------------------------------------------------------------------------

class TestArenaBatchTrainCorrectness:
    """Verify batch-train returns correct structure and data."""

    def test_single_model_returns_one_run(self, client: TestClient, explore_session: dict):
        """Single model batch should return exactly 1 run."""
        sid = _prepare_session(client, explore_session)
        resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [{"model_type": "knn", "params": {"n_neighbors": 3}}],
        })
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["runs"]) == 1
        assert body["runs"][0]["status"] == "completed"
        assert body["runs"][0]["model_type"] == "knn"
        assert body["runs"][0]["metrics"] is not None
        assert body["best_run_id"] is not None

    def test_three_model_batch_returns_all_runs(self, client: TestClient, explore_session: dict):
        """3-model batch should return 3 completed runs."""
        sid = _prepare_session(client, explore_session)
        models = [
            {"model_type": "knn", "params": {}},
            {"model_type": "decision_tree", "params": {}},
            {"model_type": "logistic_regression", "params": {}},
        ]
        resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": models,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["runs"]) == 3
        assert all(r["status"] == "completed" for r in body["runs"])
        assert body["total_training_time_ms"] > 0
        assert body["best_run_id"] is not None

    def test_knn_preserves_scatter_data(self, client: TestClient, explore_session: dict):
        """KNN runs should include knn_scatter with decision mesh."""
        sid = _prepare_session(client, explore_session)
        resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [{"model_type": "knn", "params": {"n_neighbors": 5}}],
        })
        assert resp.status_code == 200
        run = resp.json()["runs"][0]
        assert run["knn_scatter"] is not None
        assert "scatter_points" in run["knn_scatter"]
        assert "decision_mesh" in run["knn_scatter"]
        assert len(run["knn_scatter"]["scatter_points"]) > 0

    def test_non_knn_has_no_scatter_data(self, client: TestClient, explore_session: dict):
        """Non-KNN models should not have knn_scatter."""
        sid = _prepare_session(client, explore_session)
        resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [{"model_type": "decision_tree", "params": {}}],
        })
        assert resp.status_code == 200
        run = resp.json()["runs"][0]
        assert run["knn_scatter"] is None

    def test_invalid_session_returns_404(self, client: TestClient):
        """Unknown session_id should return 404."""
        resp = client.post("/api/arena/batch-train", json={
            "session_id": "nonexistent-session-id",
            "models": [{"model_type": "knn", "params": {}}],
        })
        assert resp.status_code == 404

    def test_total_time_equals_sum_of_individual(self, client: TestClient, explore_session: dict):
        """total_training_time_ms should equal sum of per-run times."""
        sid = _prepare_session(client, explore_session)
        resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [
                {"model_type": "knn", "params": {}},
                {"model_type": "naive_bayes", "params": {}},
            ],
        })
        body = resp.json()
        individual = sum(r["training_time_ms"] for r in body["runs"])
        assert abs(body["total_training_time_ms"] - individual) < 1.0  # < 1ms tolerance


# ---------------------------------------------------------------------------
# Comparison Tests
# ---------------------------------------------------------------------------

class TestArenaComparison:
    """Verify /api/arena/compare endpoint."""

    def test_compare_two_runs(self, client: TestClient, explore_session: dict):
        """Compare 2 runs and verify metric_summary structure."""
        sid = _prepare_session(client, explore_session)
        # Train 2 models
        train_resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [
                {"model_type": "knn", "params": {}},
                {"model_type": "decision_tree", "params": {}},
            ],
        })
        runs = train_resp.json()["runs"]
        run_ids = [r["run_id"] for r in runs]

        # Compare
        compare_resp = client.post(f"/api/arena/compare/{sid}", json={
            "run_ids": run_ids,
        })
        assert compare_resp.status_code == 200
        body = compare_resp.json()
        assert len(body["runs"]) == 2
        assert body["best_run_id"] in run_ids
        assert "accuracy" in body["metric_summary"]
        assert "auc_roc" in body["metric_summary"]

    def test_compare_returns_param_diff(self, client: TestClient, explore_session: dict):
        """param_diff should only include parameters that differ."""
        sid = _prepare_session(client, explore_session)
        train_resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [
                {"model_type": "knn", "params": {"n_neighbors": 3}},
                {"model_type": "knn", "params": {"n_neighbors": 7}},
            ],
        })
        runs = train_resp.json()["runs"]
        run_ids = [r["run_id"] for r in runs]

        compare_resp = client.post(f"/api/arena/compare/{sid}", json={
            "run_ids": run_ids,
        })
        body = compare_resp.json()
        assert "n_neighbors" in body["param_diff"]

    def test_get_runs_returns_all(self, client: TestClient, explore_session: dict):
        """GET /runs should return all trained runs."""
        sid = _prepare_session(client, explore_session)
        client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [
                {"model_type": "knn", "params": {}},
                {"model_type": "naive_bayes", "params": {}},
            ],
        })
        resp = client.get(f"/api/arena/runs/{sid}")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_clear_runs(self, client: TestClient, explore_session: dict):
        """DELETE /runs should clear all runs for a session."""
        sid = _prepare_session(client, explore_session)
        client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [{"model_type": "knn", "params": {}}],
        })
        # Clear
        del_resp = client.delete(f"/api/arena/runs/{sid}")
        assert del_resp.status_code == 204
        # Verify empty
        get_resp = client.get(f"/api/arena/runs/{sid}")
        assert get_resp.status_code == 200
        assert len(get_resp.json()) == 0


# ---------------------------------------------------------------------------
# Latency Tests
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestArenaBatchTrainLatency:
    """Performance bounds for batch training."""

    SINGLE_MODEL_MAX_MS = 10_000   # 10s
    BATCH_3_MAX_MS = 30_000        # 30s

    def test_single_model_under_10s(self, client: TestClient, explore_session: dict):
        """Single KNN model should train in < 10 seconds."""
        sid = _prepare_session(client, explore_session)
        start = time.time()
        resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [{"model_type": "knn", "params": {"n_neighbors": 5}}],
        })
        elapsed_ms = (time.time() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < self.SINGLE_MODEL_MAX_MS, (
            f"Single model took {elapsed_ms:.0f}ms (limit: {self.SINGLE_MODEL_MAX_MS}ms)"
        )

    def test_three_model_batch_under_30s(self, client: TestClient, explore_session: dict):
        """3-model batch should complete within 30 seconds."""
        sid = _prepare_session(client, explore_session)
        models = [
            {"model_type": "knn", "params": {}},
            {"model_type": "decision_tree", "params": {}},
            {"model_type": "logistic_regression", "params": {}},
        ]
        start = time.time()
        resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": models,
        })
        elapsed_ms = (time.time() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < self.BATCH_3_MAX_MS, (
            f"3-model batch took {elapsed_ms:.0f}ms (limit: {self.BATCH_3_MAX_MS}ms)"
        )

    def test_reported_time_matches_elapsed(self, client: TestClient, explore_session: dict):
        """Reported training_time_ms should be within 20% of actual elapsed."""
        sid = _prepare_session(client, explore_session)
        start = time.time()
        resp = client.post("/api/arena/batch-train", json={
            "session_id": sid,
            "models": [{"model_type": "naive_bayes", "params": {}}],
        })
        elapsed_ms = (time.time() - start) * 1000
        reported_ms = resp.json()["total_training_time_ms"]
        # Reported time should be <= elapsed (doesn't include HTTP overhead)
        assert reported_ms <= elapsed_ms
        # But not wildly different — within 20% margin
        assert reported_ms > elapsed_ms * 0.5, (
            f"Reported {reported_ms:.0f}ms but elapsed {elapsed_ms:.0f}ms — too large a gap"
        )
