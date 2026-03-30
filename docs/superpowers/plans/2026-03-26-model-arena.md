# Model Arena Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `local/model-arena` — an MLflow-style model comparison dashboard with batch training, transposed comparison tables, and interactive charts (radar, parallel coordinates, bar, scatter).

**Architecture:** Self-contained extension under `local/model-arena/` with its own FastAPI router (`/api/arena/*`) and React components. Integrates into the main app via a NavBar button and shares the existing `MLService` for training. The arena maintains its own "run" store for batch training results and comparison state.

**Tech Stack:** FastAPI (backend), React 18 + TypeScript (frontend), Recharts (bar/scatter), Plotly.js via react-plotly.js (parallel coordinates), @nivo/radar (radar chart), existing axios client.

---

## File Structure

```
local/model-arena/
├── arena/                    # Python package (NOT named "backend" to avoid sys.path collision)
│   ├── __init__.py
│   ├── schemas.py          # Arena-specific Pydantic models (BatchTrainRequest, ArenaRun, etc.)
│   ├── service.py          # ArenaService (batch training orchestration, run storage)
│   └── router.py           # FastAPI router /api/arena/* (batch-train, runs, compare)
├── frontend/
│   ├── types/
│   │   └── arena.ts        # TypeScript interfaces for arena
│   ├── api/
│   │   └── arena.ts        # Axios API client for /api/arena/*
│   ├── hooks/
│   │   └── useArena.ts     # React hooks (useArenaRuns, useBatchTrain)
│   ├── components/
│   │   ├── ComparisonTable.tsx    # Transposed table with diff highlighting
│   │   ├── MetricBarChart.tsx     # Side-by-side metric bars (Recharts)
│   │   ├── RadarChart.tsx         # Multi-model radar overlay (@nivo/radar)
│   │   ├── ParallelCoords.tsx     # Param-to-metric parallel coordinates (Plotly)
│   │   └── RunSelector.tsx        # Model picker with checkboxes + "Train All"
│   └── pages/
│       └── ArenaPage.tsx          # Main dashboard orchestrator
└── README.md
```

**Main app integration files (modify):**
- `backend/app/main.py` — register arena router
- `frontend/src/App.tsx` — add arena view state + conditional render
- `frontend/src/components/NavBar.tsx` — add "Model Arena" button
- `frontend/package.json` — add react-plotly.js, plotly.js-basic-dist-min, @nivo/radar deps
- `frontend/tsconfig.json` — add `"../local/model-arena/frontend"` to `include`

---

## Task 1: Backend — Arena Schemas & Service

**Files:**
- Create: `local/model-arena/arena/__init__.py`
- Create: `local/model-arena/arena/schemas.py`
- Create: `local/model-arena/arena/service.py`

**Context:** The arena needs a batch-training endpoint that trains multiple models in sequence (not truly parallel — scikit-learn holds the GIL) and stores each as a "run" with full metrics. It reuses `MLService.train_and_evaluate()` internally.

- [ ] **Step 1: Create arena schemas**

Create `local/model-arena/arena/schemas.py`:

```python
"""Pydantic schemas for Model Arena."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.ml_schemas import MetricsResponse, ModelType


class ArenaModelConfig(BaseModel):
    """One model to train in a batch."""
    model_type: ModelType
    params: dict[str, Any] = Field(default_factory=dict)
    tune: bool = False
    use_feature_selection: bool = False


class BatchTrainRequest(BaseModel):
    """Request to train multiple models on the same session."""
    session_id: str
    models: list[ArenaModelConfig] = Field(..., min_length=1, max_length=8)


class ArenaRun(BaseModel):
    """A single trained model run in the arena."""
    run_id: str
    model_id: str
    model_type: ModelType
    params: dict[str, Any]
    metrics: MetricsResponse | None = None  # None for failed runs
    training_time_ms: float
    feature_names: list[str]
    status: str = "completed"  # completed | failed
    error: str | None = None


class BatchTrainResponse(BaseModel):
    """Response from batch training."""
    session_id: str
    runs: list[ArenaRun]
    total_training_time_ms: float
    best_run_id: str | None = None


class ArenaCompareRequest(BaseModel):
    """Request to compare specific runs."""
    run_ids: list[str] = Field(..., min_length=2, max_length=8)


class ArenaCompareResponse(BaseModel):
    """Comparison data for selected runs."""
    runs: list[ArenaRun]
    best_run_id: str
    metric_summary: dict[str, dict[str, float]]  # metric_name -> {run_id: value}
    param_diff: dict[str, dict[str, Any]]  # param_name -> {run_id: value} (only differing params)
```

- [ ] **Step 2: Create arena service**

Create `local/model-arena/arena/service.py`:

```python
"""Arena service — batch training and run management."""
from __future__ import annotations

import logging
import threading
import time
import uuid
from typing import Any

from app.models.ml_schemas import ModelType
from app.services.ml_service import MLService

from .schemas import (
    ArenaCompareResponse,
    ArenaModelConfig,
    ArenaRun,
    BatchTrainRequest,
    BatchTrainResponse,
)

logger = logging.getLogger(__name__)


class ArenaService:
    def __init__(self, ml_service: MLService) -> None:
        self._ml = ml_service
        self._lock = threading.Lock()
        # session_id -> list of ArenaRun
        self._runs: dict[str, list[ArenaRun]] = {}

    def batch_train(self, request: BatchTrainRequest) -> BatchTrainResponse:
        """Train multiple models sequentially on the same session."""
        session = self._ml.get_session(request.session_id)
        if session is None:
            raise ValueError(f"Session '{request.session_id}' not found")

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

        # Store runs
        with self._lock:
            if request.session_id not in self._runs:
                self._runs[request.session_id] = []
            self._runs[request.session_id].extend(runs)

        completed = [r for r in runs if r.status == "completed" and r.metrics is not None]
        best_id = None
        if completed:
            best = max(completed, key=lambda r: r.metrics.auc_roc)  # type: ignore[union-attr]
            best_id = best.run_id

        return BatchTrainResponse(
            session_id=request.session_id,
            runs=runs,
            total_training_time_ms=total_time,
            best_run_id=best_id,
        )

    def get_runs(self, session_id: str) -> list[ArenaRun]:
        """Get all arena runs for a session."""
        with self._lock:
            return list(self._runs.get(session_id, []))

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
            selected = [r for r in all_runs if r.run_id in run_ids and r.status == "completed"]

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

        best = max(selected, key=lambda r: r.metrics.auc_roc)

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
```

- [ ] **Step 3: Create `__init__.py`**

Create `local/model-arena/arena/__init__.py` (empty file).

- [ ] **Step 4: Verify imports work**

Run: `cd /Users/efecelik/Desktop/Projects/jira-healthWithSevgi && PYTHONPATH=./backend:./local/model-arena python -c "from arena.schemas import BatchTrainRequest; print('OK')"`

---

## Task 2: Backend — Arena Router & Main App Integration

**Files:**
- Create: `local/model-arena/arena/router.py`
- Modify: `backend/app/main.py:39-46`

- [ ] **Step 1: Create arena router**

Create `local/model-arena/arena/router.py`:

```python
"""Model Arena REST endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status

from .schemas import (
    ArenaCompareRequest,
    ArenaCompareResponse,
    BatchTrainRequest,
    BatchTrainResponse,
    ArenaRun,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/arena", tags=["arena"])


def _get_arena_service(request: Request):
    return request.app.state.arena_service


@router.post("/batch-train", response_model=BatchTrainResponse)
def batch_train(request: Request, body: BatchTrainRequest) -> BatchTrainResponse:
    """Train multiple models in one request."""
    arena = _get_arena_service(request)
    try:
        return arena.batch_train(body)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.exception("Batch training failed")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.get("/runs/{session_id}", response_model=list[ArenaRun])
def get_runs(request: Request, session_id: str) -> list[ArenaRun]:
    """Get all arena runs for a session."""
    return _get_arena_service(request).get_runs(session_id)


@router.post("/compare/{session_id}", response_model=ArenaCompareResponse)
def compare_runs(
    request: Request, session_id: str, body: ArenaCompareRequest
) -> ArenaCompareResponse:
    """Compare selected runs."""
    arena = _get_arena_service(request)
    try:
        return arena.compare_runs(session_id, body.run_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/runs/{session_id}", status_code=204)
def clear_runs(request: Request, session_id: str):
    """Clear all arena runs for a session."""
    from fastapi.responses import Response
    _get_arena_service(request).clear_runs(session_id)
    return Response(status_code=204)
```

- [ ] **Step 2: Register arena router in main.py**

In `backend/app/main.py`, after line 46 (`app.include_router(explain_router)`), add:

```python
# Model Arena extension
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'local', 'model-arena'))
from arena.router import router as arena_router  # noqa: E402
from arena.service import ArenaService  # noqa: E402

app.state.arena_service = ArenaService(app.state.ml_service)
app.include_router(arena_router)
```

- [ ] **Step 3: Verify backend starts without errors**

Run: `cd /Users/efecelik/Desktop/Projects/jira-healthWithSevgi/backend && python -c "from app.main import app; print('Routes:', [r.path for r in app.routes if hasattr(r, 'path') and 'arena' in r.path])"`

- [ ] **Step 4: Commit backend**

```bash
git add local/model-arena/arena/ backend/app/main.py
git commit -m "feat(arena): add Model Arena backend with batch training and comparison APIs"
```

---

## Task 3: Frontend — Dependencies, Types, API Client & Hooks

**Files:**
- Modify: `frontend/package.json` (add deps)
- Create: `local/model-arena/frontend/types/arena.ts`
- Create: `local/model-arena/frontend/api/arena.ts`
- Create: `local/model-arena/frontend/hooks/useArena.ts`

- [ ] **Step 1: Install new chart dependencies**

Run: `cd /Users/efecelik/Desktop/Projects/jira-healthWithSevgi/frontend && pnpm add react-plotly.js plotly.js-basic-dist-min @nivo/radar @nivo/core`

Note: We use `plotly.js-basic-dist-min` (~1MB) instead of full `plotly.js` (~3.5MB) — it includes parcoords, scatter, bar which is all we need. We'll also use dynamic imports for code-splitting.

- [ ] **Step 1b: Update tsconfig.json to include arena files**

In `frontend/tsconfig.json`, change `"include": ["src"]` to `"include": ["src", "../local/model-arena/frontend"]` so TypeScript compiles the arena components.

- [ ] **Step 2: Create TypeScript types**

Create `local/model-arena/frontend/types/arena.ts`:

```typescript
import type { MetricsResponse, ModelType } from '../../../../frontend/src/types'

export interface ArenaModelConfig {
  model_type: ModelType
  params: Record<string, unknown>
  tune?: boolean
  use_feature_selection?: boolean
}

export interface BatchTrainRequest {
  session_id: string
  models: ArenaModelConfig[]
}

export interface ArenaRun {
  run_id: string
  model_id: string
  model_type: ModelType
  params: Record<string, unknown>
  metrics: MetricsResponse | null  // null for failed runs
  training_time_ms: number
  feature_names: string[]
  status: 'completed' | 'failed'
  error?: string
}

export interface BatchTrainResponse {
  session_id: string
  runs: ArenaRun[]
  total_training_time_ms: number
  best_run_id: string | null
}

export interface ArenaCompareResponse {
  runs: ArenaRun[]
  best_run_id: string | null
  metric_summary: Record<string, Record<string, number>>
  param_diff: Record<string, Record<string, unknown>>
}

/** Labels for display */
export const MODEL_LABELS: Record<ModelType, string> = {
  knn: 'KNN',
  svm: 'SVM',
  decision_tree: 'Decision Tree',
  random_forest: 'Random Forest',
  logistic_regression: 'Logistic Regression',
  naive_bayes: 'Naive Bayes',
  xgboost: 'XGBoost',
  lightgbm: 'LightGBM',
}

export const METRIC_LABELS: Record<string, string> = {
  accuracy: 'Accuracy',
  sensitivity: 'Sensitivity',
  specificity: 'Specificity',
  precision: 'Precision',
  f1_score: 'F1 Score',
  auc_roc: 'AUC-ROC',
  mcc: 'MCC',
  train_accuracy: 'Train Accuracy',
  training_time_ms: 'Training Time (ms)',
}

/** Color palette for up to 8 models */
export const RUN_COLORS = [
  '#6366f1', '#f43f5e', '#10b981', '#f59e0b',
  '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6',
]
```

- [ ] **Step 3: Create API client**

Create `local/model-arena/frontend/api/arena.ts`:

```typescript
import { api } from '../../../../frontend/src/api/client'
import type {
  ArenaCompareResponse,
  ArenaRun,
  BatchTrainRequest,
  BatchTrainResponse,
} from '../types/arena'

export const batchTrain = (req: BatchTrainRequest): Promise<BatchTrainResponse> =>
  api.post<BatchTrainResponse>('/arena/batch-train', req).then((r) => r.data)

export const getArenaRuns = (sessionId: string): Promise<ArenaRun[]> =>
  api.get<ArenaRun[]>(`/arena/runs/${sessionId}`).then((r) => r.data)

export const compareRuns = (
  sessionId: string,
  runIds: string[]
): Promise<ArenaCompareResponse> =>
  api
    .post<ArenaCompareResponse>(`/arena/compare/${sessionId}`, { run_ids: runIds })
    .then((r) => r.data)

export const clearArenaRuns = (sessionId: string): Promise<void> =>
  api.delete(`/arena/runs/${sessionId}`).then(() => undefined)
```

- [ ] **Step 4: Create React hooks**

Create `local/model-arena/frontend/hooks/useArena.ts`:

```typescript
import { useCallback, useState } from 'react'
import type {
  ArenaCompareResponse,
  ArenaModelConfig,
  ArenaRun,
  BatchTrainResponse,
} from '../types/arena'
import * as arenaApi from '../api/arena'

export function useArena(sessionId: string | null) {
  const [runs, setRuns] = useState<ArenaRun[]>([])
  const [comparison, setComparison] = useState<ArenaCompareResponse | null>(null)
  const [isTraining, setIsTraining] = useState(false)
  const [isComparing, setIsComparing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchRuns = useCallback(async () => {
    if (!sessionId) return
    try {
      const data = await arenaApi.getArenaRuns(sessionId)
      setRuns(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch runs')
    }
  }, [sessionId])

  const batchTrain = useCallback(
    async (models: ArenaModelConfig[]): Promise<BatchTrainResponse | null> => {
      if (!sessionId) return null
      setIsTraining(true)
      setError(null)
      try {
        const result = await arenaApi.batchTrain({ session_id: sessionId, models })
        setRuns((prev) => [...prev, ...result.runs])
        return result
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Batch training failed')
        return null
      } finally {
        setIsTraining(false)
      }
    },
    [sessionId]
  )

  const compareSelected = useCallback(
    async (runIds: string[]) => {
      if (!sessionId) return
      setIsComparing(true)
      setError(null)
      try {
        const result = await arenaApi.compareRuns(sessionId, runIds)
        setComparison(result)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Comparison failed')
      } finally {
        setIsComparing(false)
      }
    },
    [sessionId]
  )

  const clearRuns = useCallback(async () => {
    if (!sessionId) return
    await arenaApi.clearArenaRuns(sessionId)
    setRuns([])
    setComparison(null)
  }, [sessionId])

  return {
    runs,
    comparison,
    isTraining,
    isComparing,
    error,
    fetchRuns,
    batchTrain,
    compareSelected,
    clearRuns,
  }
}
```

- [ ] **Step 5: Commit**

```bash
git add local/model-arena/frontend/ frontend/package.json frontend/pnpm-lock.yaml
git commit -m "feat(arena): add frontend types, API client, hooks, and chart deps"
```

---

## Task 4: Frontend — Chart Components

**Files:**
- Create: `local/model-arena/frontend/components/ComparisonTable.tsx`
- Create: `local/model-arena/frontend/components/MetricBarChart.tsx`
- Create: `local/model-arena/frontend/components/RadarChart.tsx`
- Create: `local/model-arena/frontend/components/ParallelCoords.tsx`

- [ ] **Step 1: Create ComparisonTable component**

Create `local/model-arena/frontend/components/ComparisonTable.tsx`:

This is the MLflow-style transposed table. Models are columns, metrics are rows. Key features:
- Diff-only toggle (W&B pattern) — hides identical params
- Best/worst cell highlighting (green/red)
- Sort by any metric column
- "Best" badge on winning model

```typescript
import React, { useMemo, useState } from 'react'
import type { ArenaRun } from '../types/arena'
import { MODEL_LABELS, METRIC_LABELS, RUN_COLORS } from '../types/arena'

interface Props {
  runs: ArenaRun[]
  bestRunId: string
}

const METRIC_KEYS = [
  'accuracy', 'sensitivity', 'specificity', 'precision',
  'f1_score', 'auc_roc', 'mcc', 'train_accuracy',
] as const

type SortKey = typeof METRIC_KEYS[number] | 'training_time_ms' | null

export default function ComparisonTable({ runs, bestRunId }: Props) {
  const [diffOnly, setDiffOnly] = useState(false)
  const [sortBy, setSortBy] = useState<SortKey>(null)
  const [sortDesc, setSortDesc] = useState(true)

  const sortedRuns = useMemo(() => {
    if (!sortBy) return runs
    return [...runs].sort((a, b) => {
      const aVal = sortBy === 'training_time_ms'
        ? a.training_time_ms
        : (a.metrics as Record<string, number>)[sortBy] ?? 0
      const bVal = sortBy === 'training_time_ms'
        ? b.training_time_ms
        : (b.metrics as Record<string, number>)[sortBy] ?? 0
      return sortDesc ? bVal - aVal : aVal - bVal
    })
  }, [runs, sortBy, sortDesc])

  // Collect all params across runs
  const allParamKeys = useMemo(() => {
    const keys = new Set<string>()
    runs.forEach((r) => Object.keys(r.params).forEach((k) => keys.add(k)))
    return Array.from(keys)
  }, [runs])

  // Identify params that differ
  const differingParams = useMemo(() => {
    return allParamKeys.filter((key) => {
      const values = runs.map((r) => JSON.stringify(r.params[key] ?? '—'))
      return new Set(values).size > 1
    })
  }, [runs, allParamKeys])

  const paramKeys = diffOnly ? differingParams : allParamKeys

  // Find best/worst per metric
  const bestWorst = useMemo(() => {
    const result: Record<string, { bestId: string; worstId: string }> = {}
    for (const metric of METRIC_KEYS) {
      let bestVal = -Infinity, worstVal = Infinity, bestId = '', worstId = ''
      for (const r of runs) {
        const val = (r.metrics as Record<string, number>)[metric] ?? 0
        if (val > bestVal) { bestVal = val; bestId = r.run_id }
        if (val < worstVal) { worstVal = val; worstId = r.run_id }
      }
      result[metric] = { bestId, worstId }
    }
    return result
  }, [runs])

  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortDesc(!sortDesc)
    } else {
      setSortBy(key)
      setSortDesc(true)
    }
  }

  const sortIndicator = (key: SortKey) => {
    if (sortBy !== key) return ''
    return sortDesc ? ' ▼' : ' ▲'
  }

  return (
    <div className="arena-table-wrapper">
      <div className="arena-table-toolbar">
        <h3 className="arena-section-title">Comparison Table</h3>
        <label className="arena-toggle">
          <input
            type="checkbox"
            checked={diffOnly}
            onChange={(e) => setDiffOnly(e.target.checked)}
          />
          <span>Diff only</span>
        </label>
      </div>

      <div className="arena-table-scroll">
        <table className="arena-table">
          <thead>
            <tr>
              <th className="arena-th-label">Model</th>
              {sortedRuns.map((r, i) => (
                <th key={r.run_id} style={{ borderTop: `3px solid ${RUN_COLORS[i % RUN_COLORS.length]}` }}>
                  <div className="arena-model-header">
                    <span className="arena-model-name">{MODEL_LABELS[r.model_type]}</span>
                    {r.run_id === bestRunId && <span className="arena-badge-best">Best</span>}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Metrics section */}
            <tr className="arena-section-row">
              <td colSpan={sortedRuns.length + 1}>Metrics</td>
            </tr>
            {METRIC_KEYS.map((metric) => (
              <tr key={metric}>
                <td
                  className="arena-th-label arena-sortable"
                  onClick={() => handleSort(metric)}
                >
                  {METRIC_LABELS[metric]}{sortIndicator(metric)}
                </td>
                {sortedRuns.map((r) => {
                  const val = (r.metrics as Record<string, number>)[metric] ?? 0
                  const isBest = bestWorst[metric]?.bestId === r.run_id
                  const isWorst = bestWorst[metric]?.worstId === r.run_id && runs.length > 1
                  return (
                    <td
                      key={r.run_id}
                      className={`arena-cell ${isBest ? 'arena-cell-best' : ''} ${isWorst ? 'arena-cell-worst' : ''}`}
                    >
                      {val.toFixed(4)}
                    </td>
                  )
                })}
              </tr>
            ))}
            {/* Training time */}
            <tr>
              <td
                className="arena-th-label arena-sortable"
                onClick={() => handleSort('training_time_ms')}
              >
                Training Time (ms){sortIndicator('training_time_ms')}
              </td>
              {sortedRuns.map((r) => (
                <td key={r.run_id} className="arena-cell">
                  {r.training_time_ms.toFixed(0)}
                </td>
              ))}
            </tr>

            {/* Parameters section */}
            {paramKeys.length > 0 && (
              <>
                <tr className="arena-section-row">
                  <td colSpan={sortedRuns.length + 1}>
                    Parameters {diffOnly && `(${differingParams.length} differing)`}
                  </td>
                </tr>
                {paramKeys.map((param) => {
                  const isDiffering = differingParams.includes(param)
                  return (
                    <tr key={param}>
                      <td className="arena-th-label">{param}</td>
                      {sortedRuns.map((r) => (
                        <td
                          key={r.run_id}
                          className={`arena-cell ${isDiffering ? 'arena-cell-diff' : ''}`}
                        >
                          {r.params[param] !== undefined ? String(r.params[param]) : '—'}
                        </td>
                      ))}
                    </tr>
                  )
                })}
              </>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create MetricBarChart component**

Create `local/model-arena/frontend/components/MetricBarChart.tsx`:

```typescript
import React, { useMemo, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell,
} from 'recharts'
import type { ArenaRun } from '../types/arena'
import { MODEL_LABELS, METRIC_LABELS, RUN_COLORS } from '../types/arena'

interface Props {
  runs: ArenaRun[]
}

const METRICS = [
  'accuracy', 'sensitivity', 'specificity', 'precision', 'f1_score', 'auc_roc', 'mcc',
] as const

export default function MetricBarChart({ runs }: Props) {
  const [selectedMetric, setSelectedMetric] = useState<string>('auc_roc')

  const data = useMemo(() => {
    return runs.map((r, i) => ({
      name: MODEL_LABELS[r.model_type],
      value: (r.metrics as Record<string, number>)[selectedMetric] ?? 0,
      color: RUN_COLORS[i % RUN_COLORS.length],
    }))
  }, [runs, selectedMetric])

  return (
    <div className="arena-chart-card">
      <div className="arena-chart-header">
        <h3 className="arena-section-title">Metric Comparison</h3>
        <select
          className="arena-select"
          value={selectedMetric}
          onChange={(e) => setSelectedMetric(e.target.value)}
        >
          {METRICS.map((m) => (
            <option key={m} value={m}>{METRIC_LABELS[m]}</option>
          ))}
        </select>
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light, #e2e8f0)" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value: number) => [value.toFixed(4), METRIC_LABELS[selectedMetric]]}
            contentStyle={{ borderRadius: 8, fontSize: 13 }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
```

- [ ] **Step 3: Create RadarChart component**

Create `local/model-arena/frontend/components/RadarChart.tsx`:

```typescript
import React, { useMemo } from 'react'
import { ResponsiveRadar } from '@nivo/radar'
import type { ArenaRun } from '../types/arena'
import { MODEL_LABELS, RUN_COLORS } from '../types/arena'

interface Props {
  runs: ArenaRun[]
}

const RADAR_METRICS = [
  'accuracy', 'sensitivity', 'specificity', 'precision', 'f1_score', 'auc_roc',
] as const

const RADAR_LABELS: Record<string, string> = {
  accuracy: 'Accuracy',
  sensitivity: 'Sensitivity',
  specificity: 'Specificity',
  precision: 'Precision',
  f1_score: 'F1',
  auc_roc: 'AUC-ROC',
}

export default function ArenaRadarChart({ runs }: Props) {
  const { data, keys } = useMemo(() => {
    const keys = runs.map((r) => MODEL_LABELS[r.model_type])
    const data = RADAR_METRICS.map((metric) => {
      const point: Record<string, string | number> = { metric: RADAR_LABELS[metric] }
      runs.forEach((r) => {
        point[MODEL_LABELS[r.model_type]] =
          (r.metrics as Record<string, number>)[metric] ?? 0
      })
      return point
    })
    return { data, keys }
  }, [runs])

  const colors = runs.map((_, i) => RUN_COLORS[i % RUN_COLORS.length])

  return (
    <div className="arena-chart-card">
      <h3 className="arena-section-title">Radar — Multi-Metric Overview</h3>
      <div style={{ height: 400 }}>
        <ResponsiveRadar
          data={data}
          keys={keys}
          indexBy="metric"
          maxValue={1}
          margin={{ top: 40, right: 80, bottom: 40, left: 80 }}
          borderWidth={2}
          borderColor={{ from: 'color' }}
          gridLevels={5}
          gridShape="circular"
          gridLabelOffset={16}
          dotSize={6}
          dotColor={{ theme: 'background' }}
          dotBorderWidth={2}
          dotBorderColor={{ from: 'color' }}
          colors={colors}
          fillOpacity={0.15}
          blendMode="normal"
          animate={true}
          legends={[
            {
              anchor: 'top-left',
              direction: 'column',
              translateX: -50,
              translateY: -40,
              itemWidth: 100,
              itemHeight: 20,
              itemTextColor: 'var(--text-secondary, #64748b)',
              symbolSize: 10,
              symbolShape: 'circle',
            },
          ]}
          theme={{
            text: { fill: 'var(--text-secondary, #64748b)', fontSize: 12 },
            grid: { line: { stroke: 'var(--border-light, #e2e8f0)' } },
          }}
        />
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create ParallelCoords component**

Create `local/model-arena/frontend/components/ParallelCoords.tsx`:

```typescript
import React, { useMemo } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-basic-dist-min'
import type { ArenaRun } from '../types/arena'

const Plot = createPlotlyComponent(Plotly)
import { MODEL_LABELS, RUN_COLORS } from '../types/arena'

interface Props {
  runs: ArenaRun[]
}

const DISPLAY_METRICS = [
  { key: 'accuracy', label: 'Accuracy', range: [0, 1] },
  { key: 'sensitivity', label: 'Sensitivity', range: [0, 1] },
  { key: 'specificity', label: 'Specificity', range: [0, 1] },
  { key: 'precision', label: 'Precision', range: [0, 1] },
  { key: 'f1_score', label: 'F1 Score', range: [0, 1] },
  { key: 'auc_roc', label: 'AUC-ROC', range: [0, 1] },
  { key: 'mcc', label: 'MCC', range: [-1, 1] },
] as const

export default function ParallelCoords({ runs }: Props) {
  const { dimensions, colorValues, tickText, tickVals } = useMemo(() => {
    // Build dimensions from metrics
    const dimensions = DISPLAY_METRICS.map((m) => ({
      label: m.label,
      values: runs.map((r) => (r.metrics as Record<string, number>)[m.key] ?? 0),
      range: m.range,
    }))

    // Also add differing params as dimensions
    const allParams = new Map<string, unknown[]>()
    runs.forEach((r) => {
      Object.entries(r.params).forEach(([k, v]) => {
        if (!allParams.has(k)) allParams.set(k, [])
        allParams.get(k)!.push(v)
      })
    })

    for (const [key, values] of allParams) {
      // Only add numeric params that differ
      if (values.every((v) => typeof v === 'number')) {
        const nums = values as number[]
        if (new Set(nums.map(String)).size > 1) {
          dimensions.push({
            label: key,
            values: nums,
            range: [Math.min(...nums) * 0.9, Math.max(...nums) * 1.1],
          })
        }
      }
    }

    // Color by AUC-ROC value
    const colorValues = runs.map((r) => r.metrics.auc_roc)

    // Tick labels for model names
    const tickVals = runs.map((_, i) => i)
    const tickText = runs.map((r) => MODEL_LABELS[r.model_type])

    return { dimensions, colorValues, tickText, tickVals }
  }, [runs])

  return (
    <div className="arena-chart-card">
      <h3 className="arena-section-title">Parallel Coordinates — Parameter-Metric Relationships</h3>
      <Plot
        data={[
          {
            type: 'parcoords',
            line: {
              color: colorValues,
              colorscale: [
                [0, '#f43f5e'],
                [0.5, '#f59e0b'],
                [1, '#10b981'],
              ],
              showscale: true,
              colorbar: { title: 'AUC-ROC', thickness: 15, len: 0.6 },
            },
            dimensions: dimensions as Plotly.ParcoordsDimension[],
          } as Plotly.Data,
        ]}
        layout={{
          width: undefined,
          height: 420,
          margin: { l: 80, r: 80, t: 30, b: 30 },
          font: { size: 11, color: '#64748b' },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  )
}
```

- [ ] **Step 5: Commit chart components**

```bash
git add local/model-arena/frontend/components/
git commit -m "feat(arena): add comparison table, bar, radar, and parallel coordinates charts"
```

---

## Task 5: Frontend — RunSelector, ArenaPage & Main App Integration

**Files:**
- Create: `local/model-arena/frontend/components/RunSelector.tsx`
- Create: `local/model-arena/frontend/pages/ArenaPage.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/NavBar.tsx`

- [ ] **Step 1: Create RunSelector component**

Create `local/model-arena/frontend/components/RunSelector.tsx`:

```typescript
import React, { useState } from 'react'
import type { ModelType } from '../../../../frontend/src/types'
import type { ArenaModelConfig } from '../types/arena'
import { MODEL_LABELS } from '../types/arena'

interface Props {
  onBatchTrain: (models: ArenaModelConfig[]) => void
  isTraining: boolean
  disabled: boolean
}

const ALL_MODELS: ModelType[] = [
  'knn', 'svm', 'decision_tree', 'random_forest',
  'logistic_regression', 'naive_bayes', 'xgboost', 'lightgbm',
]

export default function RunSelector({ onBatchTrain, isTraining, disabled }: Props) {
  const [selected, setSelected] = useState<Set<ModelType>>(new Set())
  const [tune, setTune] = useState(false)

  const toggle = (model: ModelType) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(model)) next.delete(model)
      else next.add(model)
      return next
    })
  }

  const selectAll = () => setSelected(new Set(ALL_MODELS))
  const clearAll = () => setSelected(new Set())

  const handleTrain = () => {
    const models: ArenaModelConfig[] = Array.from(selected).map((model_type) => ({
      model_type,
      params: {},
      tune,
    }))
    onBatchTrain(models)
  }

  return (
    <div className="arena-selector">
      <div className="arena-selector-header">
        <h3 className="arena-section-title">Select Models to Train</h3>
        <div className="arena-selector-actions">
          <button className="btn btn-ghost btn-sm" onClick={selectAll}>Select All</button>
          <button className="btn btn-ghost btn-sm" onClick={clearAll}>Clear</button>
        </div>
      </div>

      <div className="arena-model-grid">
        {ALL_MODELS.map((model) => (
          <button
            key={model}
            className={`arena-model-chip ${selected.has(model) ? 'active' : ''}`}
            onClick={() => toggle(model)}
            disabled={disabled}
          >
            <span className="arena-chip-check">{selected.has(model) ? '✓' : ''}</span>
            {MODEL_LABELS[model]}
          </button>
        ))}
      </div>

      <div className="arena-selector-footer">
        <label className="arena-toggle">
          <input type="checkbox" checked={tune} onChange={(e) => setTune(e.target.checked)} />
          <span>Auto-tune hyperparameters</span>
        </label>

        <button
          className="btn btn-primary"
          onClick={handleTrain}
          disabled={selected.size === 0 || isTraining || disabled}
        >
          {isTraining ? (
            <span className="arena-spinner">Training {selected.size} models...</span>
          ) : (
            `Train ${selected.size} Model${selected.size !== 1 ? 's' : ''}`
          )}
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create ArenaPage — the main dashboard**

Create `local/model-arena/frontend/pages/ArenaPage.tsx`:

```typescript
import React, { useEffect, useMemo, useState } from 'react'
import { useArena } from '../hooks/useArena'
import RunSelector from '../components/RunSelector'
import ComparisonTable from '../components/ComparisonTable'
import MetricBarChart from '../components/MetricBarChart'
import ArenaRadarChart from '../components/RadarChart'
import type { ArenaModelConfig, ArenaRun } from '../types/arena'
import { MODEL_LABELS, RUN_COLORS } from '../types/arena'

// Lazy-load Plotly (heavy dependency)
const ParallelCoords = React.lazy(() => import('../components/ParallelCoords'))

interface Props {
  sessionId: string | null
  onClose: () => void
}

export default function ArenaPage({ sessionId, onClose }: Props) {
  const {
    runs, comparison, isTraining, isComparing, error,
    fetchRuns, batchTrain, compareSelected, clearRuns,
  } = useArena(sessionId)

  const [selectedRunIds, setSelectedRunIds] = useState<Set<string>>(new Set())

  // Fetch existing runs on mount
  useEffect(() => {
    fetchRuns()
  }, [fetchRuns])

  const completedRuns = useMemo(() => runs.filter((r) => r.status === 'completed'), [runs])

  // Auto-select all completed runs
  useEffect(() => {
    setSelectedRunIds(new Set(completedRuns.map((r) => r.run_id)))
  }, [completedRuns])

  // Auto-compare when selection changes and has 2+ runs
  useEffect(() => {
    if (selectedRunIds.size >= 2) {
      compareSelected(Array.from(selectedRunIds))
    }
  }, [selectedRunIds, compareSelected])

  const toggleRun = (runId: string) => {
    setSelectedRunIds((prev) => {
      const next = new Set(prev)
      if (next.has(runId)) next.delete(runId)
      else next.add(runId)
      return next
    })
  }

  const handleBatchTrain = async (models: ArenaModelConfig[]) => {
    await batchTrain(models)
  }

  const comparedRuns = comparison?.runs ?? []

  return (
    <div className="arena-page">
      {/* Header */}
      <div className="arena-header">
        <div>
          <h2 className="arena-title">Model Arena</h2>
          <p className="arena-subtitle">
            Train and compare multiple models side by side
          </p>
        </div>
        <div className="arena-header-actions">
          {completedRuns.length > 0 && (
            <button className="btn btn-ghost btn-sm" onClick={clearRuns}>
              Clear All Runs
            </button>
          )}
          <button className="btn btn-ghost" onClick={onClose}>
            ← Back to Wizard
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="arena-error">{error}</div>
      )}

      {/* Model Selector */}
      <RunSelector
        onBatchTrain={handleBatchTrain}
        isTraining={isTraining}
        disabled={!sessionId}
      />

      {/* Run list with checkboxes */}
      {completedRuns.length > 0 && (
        <div className="arena-run-list">
          <h3 className="arena-section-title">
            Trained Runs ({completedRuns.length})
          </h3>
          <div className="arena-run-chips">
            {completedRuns.map((r, i) => (
              <label
                key={r.run_id}
                className={`arena-run-chip ${selectedRunIds.has(r.run_id) ? 'active' : ''}`}
                style={{ borderColor: RUN_COLORS[i % RUN_COLORS.length] }}
              >
                <input
                  type="checkbox"
                  checked={selectedRunIds.has(r.run_id)}
                  onChange={() => toggleRun(r.run_id)}
                />
                <span
                  className="arena-run-dot"
                  style={{ background: RUN_COLORS[i % RUN_COLORS.length] }}
                />
                <span>{MODEL_LABELS[r.model_type]}</span>
                <span className="arena-run-auc">
                  AUC: {r.metrics.auc_roc.toFixed(3)}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* No session warning */}
      {!sessionId && (
        <div className="arena-empty">
          <p>Complete Data Preparation (Step 3) first to enable model training.</p>
          <button className="btn btn-primary" onClick={onClose}>
            ← Back to Wizard
          </button>
        </div>
      )}

      {/* Comparison dashboard */}
      {comparedRuns.length >= 2 && (
        <div className="arena-dashboard">
          {/* Comparison Table */}
          <ComparisonTable
            runs={comparedRuns}
            bestRunId={comparison!.best_run_id}
          />

          {/* Charts grid */}
          <div className="arena-charts-grid">
            <MetricBarChart runs={comparedRuns} />
            <ArenaRadarChart runs={comparedRuns} />
          </div>

          {/* Parallel coordinates (full width, lazy loaded) */}
          <React.Suspense fallback={
            <div className="arena-chart-card" style={{ height: 420, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <p style={{ color: 'var(--text-muted)' }}>Loading parallel coordinates...</p>
            </div>
          }>
            <ParallelCoords runs={comparedRuns} />
          </React.Suspense>
        </div>
      )}

      {/* Waiting state */}
      {completedRuns.length === 1 && (
        <div className="arena-empty">
          <p>Train at least one more model to start comparing.</p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Add "Model Arena" button to NavBar**

In `frontend/src/components/NavBar.tsx`, add a new prop `onArena` and a button:

After the existing imports, the Props interface becomes:
```typescript
interface Props {
  specialty: Specialty | null
  specialties: Specialty[]
  onSpecialtyChange: (s: Specialty) => void
  onReset: () => void
  onGlossary: () => void
  glossaryOpen: boolean
  onGlossaryClose: () => void
  onArena?: () => void        // NEW
  arenaActive?: boolean       // NEW
}
```

In the navbar-actions div, before the reset button, add:
```tsx
{onArena && (
  <button
    className={`navbar-icon-btn ${arenaActive ? 'navbar-icon-btn-active' : ''}`}
    onClick={onArena}
    title="Model Arena"
    aria-label="Open Model Arena"
  >
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
      <line x1="4" y1="22" x2="4" y2="15"/>
    </svg>
  </button>
)}
```

- [ ] **Step 4: Integrate ArenaPage into App.tsx**

In `frontend/src/App.tsx`:

1. Add lazy import at top:
```typescript
const ArenaPage = React.lazy(() => import('../../local/model-arena/frontend/pages/ArenaPage'))
```

2. Add state for arena view:
```typescript
const [showArena, setShowArena] = useState(false)
```

3. Pass arena props to NavBar:
```tsx
<NavBar
  // ... existing props
  onArena={() => setShowArena(!showArena)}
  arenaActive={showArena}
/>
```

4. In the main-content div, conditionally render ArenaPage:
```tsx
<div className="main-content">
  <React.Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>}>
    {showArena ? (
      <ArenaPage
        sessionId={state.prepResponse?.session_id ?? null}
        onClose={() => setShowArena(false)}
      />
    ) : (
      renderStep()
    )}
  </React.Suspense>
  {/* ... privacy notice */}
</div>
```

- [ ] **Step 5: Commit the full integration**

```bash
git add local/model-arena/frontend/components/RunSelector.tsx \
  local/model-arena/frontend/pages/ArenaPage.tsx \
  frontend/src/App.tsx frontend/src/components/NavBar.tsx
git commit -m "feat(arena): add ArenaPage dashboard with NavBar integration"
```

---

## Task 6: Frontend — Arena CSS Styles

**Files:**
- Modify: `frontend/src/styles/globals.css` (append arena styles)

- [ ] **Step 1: Add arena styles to globals.css**

Append to `frontend/src/styles/globals.css`:

```css
/* =============================================
   MODEL ARENA
   ============================================= */

.arena-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.arena-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.arena-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.arena-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0.25rem 0 0;
}

.arena-header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.arena-section-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.arena-error {
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background: var(--danger-light, #fef2f2);
  color: var(--danger, #dc2626);
  font-size: 0.875rem;
  border: 1px solid var(--danger, #dc2626);
}

/* ---- Run Selector ---- */
.arena-selector {
  background: var(--bg-card, #fff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.arena-selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.arena-selector-actions {
  display: flex;
  gap: 0.5rem;
}

.arena-model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.arena-model-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.875rem;
  border: 2px solid var(--border, #e2e8f0);
  border-radius: 0.5rem;
  background: var(--bg-card, #fff);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 150ms ease;
}

.arena-model-chip:hover {
  border-color: var(--primary);
  color: var(--text-primary);
}

.arena-model-chip.active {
  border-color: var(--primary);
  background: var(--primary-light, #eef2ff);
  color: var(--primary);
  font-weight: 600;
}

.arena-chip-check {
  width: 16px;
  font-size: 0.75rem;
}

.arena-selector-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border, #e2e8f0);
}

.arena-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.arena-toggle input[type="checkbox"] {
  accent-color: var(--primary);
}

.arena-spinner {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.arena-spinner::before {
  content: '';
  width: 14px;
  height: 14px;
  border: 2px solid #fff4;
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ---- Run List ---- */
.arena-run-list {
  background: var(--bg-card, #fff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.arena-run-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.arena-run-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border: 2px solid var(--border, #e2e8f0);
  border-radius: 0.5rem;
  background: var(--bg-card, #fff);
  cursor: pointer;
  font-size: 0.82rem;
  transition: all 150ms ease;
}

.arena-run-chip.active {
  background: var(--bg-secondary, #f8fafc);
}

.arena-run-chip input[type="checkbox"] {
  display: none;
}

.arena-run-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.arena-run-auc {
  color: var(--text-muted);
  font-size: 0.78rem;
  margin-left: 0.25rem;
}

/* ---- Comparison Table ---- */
.arena-table-wrapper {
  background: var(--bg-card, #fff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 0.75rem;
  overflow: hidden;
}

.arena-table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border, #e2e8f0);
}

.arena-table-scroll {
  overflow-x: auto;
}

.arena-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
}

.arena-table th,
.arena-table td {
  padding: 0.6rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-light, #f1f5f9);
  white-space: nowrap;
}

.arena-table th {
  background: var(--bg-secondary, #f8fafc);
  font-weight: 600;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.arena-th-label {
  font-weight: 600;
  color: var(--text-secondary);
  position: sticky;
  left: 0;
  background: var(--bg-card, #fff);
  z-index: 1;
  min-width: 140px;
}

.arena-sortable {
  cursor: pointer;
  user-select: none;
}

.arena-sortable:hover {
  color: var(--primary);
}

.arena-model-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.arena-model-name {
  font-weight: 700;
  color: var(--text-primary);
}

.arena-badge-best {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  background: var(--success-light, #ecfdf5);
  color: var(--success, #059669);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.arena-section-row td {
  background: var(--bg-secondary, #f8fafc);
  font-weight: 700;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  padding: 0.5rem 1rem;
}

.arena-cell {
  font-variant-numeric: tabular-nums;
}

.arena-cell-best {
  background: var(--success-light, #ecfdf5);
  color: var(--success, #059669);
  font-weight: 700;
}

.arena-cell-worst {
  background: var(--danger-light, #fef2f2);
  color: var(--danger, #dc2626);
}

.arena-cell-diff {
  background: var(--warning-light, #fffbeb);
}

/* ---- Charts ---- */
.arena-dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.arena-charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .arena-charts-grid {
    grid-template-columns: 1fr;
  }
}

.arena-chart-card {
  background: var(--bg-card, #fff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.arena-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.arena-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 0.375rem;
  font-size: 0.82rem;
  color: var(--text-primary);
  background: var(--bg-card, #fff);
}

/* ---- Empty/Disabled State ---- */
.arena-empty {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--text-secondary);
  background: var(--bg-card, #fff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 0.75rem;
}

.arena-empty p {
  margin-bottom: 1rem;
}

/* ---- NavBar active state for arena ---- */
.navbar-icon-btn-active {
  color: var(--primary);
  background: var(--primary-light, #eef2ff);
}
```

- [ ] **Step 2: Commit styles**

```bash
git add frontend/src/styles/globals.css
git commit -m "feat(arena): add Model Arena CSS styles"
```

---

## Task 7: Verify & Polish

- [ ] **Step 1: Start backend and verify arena endpoints**

Run: `cd /Users/efecelik/Desktop/Projects/jira-healthWithSevgi/backend && python -m uvicorn app.main:app --reload --port 8001`

Test endpoint exists: `curl -s http://localhost:8001/docs | grep arena`

- [ ] **Step 2: Start frontend and verify arena renders**

Run: `cd /Users/efecelik/Desktop/Projects/jira-healthWithSevgi/frontend && pnpm dev`

Verify: NavBar shows arena button, clicking it shows ArenaPage.

- [ ] **Step 3: Test batch training flow**

1. Go through Steps 1-3 to get a session_id
2. Click "Model Arena" in navbar
3. Select 3+ models, click "Train"
4. Verify comparison table, bar chart, radar chart, and parallel coordinates render

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat(arena): complete Model Arena v1 — batch training, comparison table, interactive charts"
```

---

## Dependency Map

```
Task 1 (schemas + service) ─┐
                             ├── Task 2 (router + main.py integration)
                             │
Task 3 (types + API + hooks)─┤
                             ├── Task 4 (chart components)
                             │                │
                             │                ├── Task 5 (ArenaPage + App integration)
                             │                │         │
Task 6 (CSS styles) ─────────┘────────────────┘         │
                                                        ├── Task 7 (verify & polish)
```

**Parallelizable groups:**
- **Wave 1:** Task 1 + Task 3 + Task 6 (all independent)
- **Wave 2:** Task 2 (needs Task 1) + Task 4 (needs Task 3)
- **Wave 3:** Task 5 (needs Task 2 + Task 4 + Task 6)
- **Wave 4:** Task 7 (needs everything)
