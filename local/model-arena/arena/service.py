"""Arena service -- batch training and run management."""
from __future__ import annotations

import logging
import threading
import uuid
from collections import OrderedDict
from typing import Any

from app.services.ml_service import MLService

from .schemas import (
    ArenaCompareResponse,
    ArenaModelConfig,
    ArenaRun,
    BatchTrainRequest,
    BatchTrainResponse,
)

logger = logging.getLogger(__name__)

_MAX_SESSIONS = 50


class ArenaService:
    def __init__(self, ml_service: MLService) -> None:
        self._ml = ml_service
        self._lock = threading.Lock()
        # session_id -> list of ArenaRun (LRU-evicted at _MAX_SESSIONS)
        self._runs: OrderedDict[str, list[ArenaRun]] = OrderedDict()
        # Track sessions currently being batch-trained to prevent duplicates
        self._in_flight: set[str] = set()

    def batch_train(self, request: BatchTrainRequest) -> BatchTrainResponse:
        """Train multiple models sequentially on the same session."""
        # Pre-flight: verify session exists (raises KeyError → router returns 404)
        if self._ml.get_session(request.session_id) is None:
            raise KeyError(f"Session '{request.session_id}' not found. Run /api/prepare first.")

        # Guard against concurrent batch_train for same session
        with self._lock:
            if request.session_id in self._in_flight:
                raise ValueError(
                    f"Batch training already in progress for session '{request.session_id}'"
                )
            self._in_flight.add(request.session_id)

        try:
            runs: list[ArenaRun] = []
            total_time = 0.0

            for model_cfg in request.models:
                run_id = str(uuid.uuid4())
                try:
                    response = self._ml.train_and_evaluate(
                        request.session_id,
                        model_cfg.model_type,
                        model_cfg.params,
                        tune=model_cfg.tune,
                        use_feature_selection=model_cfg.use_feature_selection,
                    )
                    self._ml.store_train_response_in_model(response.model_id, response)
                    run = ArenaRun(
                        run_id=run_id,
                        model_id=response.model_id,
                        model_type=model_cfg.model_type,
                        params=response.params,
                        metrics=response.metrics,
                        training_time_ms=response.training_time_ms,
                        feature_names=response.feature_names,
                    )
                    total_time += response.training_time_ms
                except (ImportError, MemoryError):
                    raise  # Non-recoverable — propagate to router as 500
                except Exception as exc:
                    logger.warning("Arena: model %s failed: %s", model_cfg.model_type.value, exc)
                    run = ArenaRun(
                        run_id=run_id,
                        model_id="",
                        model_type=model_cfg.model_type,
                        params=model_cfg.params,
                        metrics=None,
                        training_time_ms=0.0,
                        feature_names=[],
                        status="failed",
                        error=str(exc),
                    )
                runs.append(run)

            # Store runs with LRU eviction
            with self._lock:
                if request.session_id not in self._runs:
                    self._runs[request.session_id] = []
                self._runs[request.session_id].extend(runs)
                self._runs.move_to_end(request.session_id)
                while len(self._runs) > _MAX_SESSIONS:
                    self._runs.popitem(last=False)

                # Compute best across ALL session runs (not just this batch)
                all_completed = [
                    r for r in self._runs.get(request.session_id, [])
                    if r.status == "completed" and r.metrics is not None
                ]

            best_id = None
            if all_completed:
                best = max(all_completed, key=lambda r: r.metrics.auc_roc)  # type: ignore[union-attr]
                best_id = best.run_id

            return BatchTrainResponse(
                session_id=request.session_id,
                runs=runs,
                total_training_time_ms=total_time,
                best_run_id=best_id,
            )
        finally:
            with self._lock:
                self._in_flight.discard(request.session_id)

    def get_runs(self, session_id: str) -> list[ArenaRun]:
        """Get all arena runs for a session."""
        with self._lock:
            return list(self._runs.get(session_id, []))

    def has_session(self, session_id: str) -> bool:
        """Check if a session has any arena runs."""
        with self._lock:
            return session_id in self._runs

    def get_run(self, session_id: str, run_id: str) -> ArenaRun | None:
        """Get a specific run."""
        with self._lock:
            for run in self._runs.get(session_id, []):
                if run.run_id == run_id:
                    return run
        return None

    def compare_runs(self, session_id: str, run_ids: list[str]) -> ArenaCompareResponse:
        """Build comparison data for selected runs."""
        with self._lock:
            all_runs = self._runs.get(session_id, [])
            all_run_ids = {r.run_id for r in all_runs}
            selected = [
                r for r in all_runs
                if r.run_id in run_ids and r.status == "completed" and r.metrics is not None
            ]

        # Check for missing run IDs
        missing = [rid for rid in run_ids if rid not in all_run_ids]
        if missing:
            raise ValueError(f"Run IDs not found in session '{session_id}': {missing}")

        # Check for runs that exist but are failed
        selected_ids = {r.run_id for r in selected}
        failed = [rid for rid in run_ids if rid in all_run_ids and rid not in selected_ids]
        if failed:
            raise ValueError(f"Run IDs exist but are in failed state: {failed}")

        if len(selected) < 2:
            raise ValueError("Need at least 2 completed runs to compare")

        # Build metric summary: metric_name -> {run_id: value}
        metric_names = [
            "accuracy", "sensitivity", "specificity", "precision",
            "f1_score", "auc_roc", "mcc", "train_accuracy",
        ]
        metric_summary: dict[str, dict[str, float]] = {}
        for name in metric_names:
            metric_summary[name] = {
                r.run_id: getattr(r.metrics, name) for r in selected
            }

        # Build param diff: only params that differ across runs
        all_params: dict[str, dict[str, Any]] = {}
        for r in selected:
            for k, v in r.params.items():
                if k not in all_params:
                    all_params[k] = {}
                all_params[k][r.run_id] = v

        param_diff = {
            k: vals for k, vals in all_params.items()
            if len(set(str(v) for v in vals.values())) > 1
        }

        best = max(selected, key=lambda r: r.metrics.auc_roc)  # type: ignore[union-attr]

        return ArenaCompareResponse(
            runs=selected,
            best_run_id=best.run_id,
            metric_summary=metric_summary,
            param_diff=param_diff,
        )

    def clear_runs(self, session_id: str) -> None:
        """Clear all runs for a session."""
        with self._lock:
            self._runs.pop(session_id, None)
