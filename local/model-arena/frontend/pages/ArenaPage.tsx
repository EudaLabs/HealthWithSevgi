import React, { useEffect, useMemo, useState } from 'react'
import { useArena } from '../hooks/useArena'
import RunSelector from '../components/RunSelector'
import ComparisonTable from '../components/ComparisonTable'
import MetricBarChart from '../components/MetricBarChart'
import ArenaRadarChart from '../components/RadarChart'
import type { ArenaModelConfig } from '../types/arena'
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
  const failedRuns = useMemo(() => runs.filter((r) => r.status === 'failed'), [runs])

  // Stable color map keyed by run_id (preserves colors across sorts)
  const runColorMap = useMemo(() => {
    const map = new Map<string, string>()
    completedRuns.forEach((r, i) => map.set(r.run_id, RUN_COLORS[i % RUN_COLORS.length]))
    return map
  }, [completedRuns])

  // Auto-select all completed runs (guard against Set reference churn)
  useEffect(() => {
    const newIds = completedRuns.map((r) => r.run_id)
    setSelectedRunIds((prev) => {
      const same = newIds.length === prev.size && newIds.every((id) => prev.has(id))
      if (same) return prev  // preserve reference — no downstream effect
      return new Set(newIds)
    })
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
            &larr; Back to Wizard
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="arena-error">{error}</div>
      )}

      {/* Failed runs banner */}
      {failedRuns.length > 0 && (
        <div className="arena-error" style={{ background: 'var(--warning-light)', borderColor: 'var(--warning)', color: 'var(--text-primary)' }}>
          <strong>{failedRuns.length} model{failedRuns.length > 1 ? 's' : ''} failed:</strong>{' '}
          {failedRuns.map((r) => `${MODEL_LABELS[r.model_type]}${r.error ? ` (${r.error})` : ''}`).join(', ')}
        </div>
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
            {completedRuns.map((r) => (
              <label
                key={r.run_id}
                className={`arena-run-chip ${selectedRunIds.has(r.run_id) ? 'active' : ''}`}
                style={{ borderColor: runColorMap.get(r.run_id) }}
              >
                <input
                  type="checkbox"
                  checked={selectedRunIds.has(r.run_id)}
                  onChange={() => toggleRun(r.run_id)}
                />
                <span
                  className="arena-run-dot"
                  style={{ background: runColorMap.get(r.run_id) }}
                />
                <span>{MODEL_LABELS[r.model_type]}</span>
                <span className="arena-run-auc">
                  AUC: {r.metrics?.auc_roc != null ? r.metrics.auc_roc.toFixed(3) : 'N/A'}
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
            &larr; Back to Wizard
          </button>
        </div>
      )}

      {/* Comparison dashboard */}
      {comparedRuns.length >= 2 && (
        <div className="arena-dashboard" style={{ position: 'relative' }}>
          {/* Loading overlay during comparison fetch */}
          {isComparing && (
            <div style={{
              position: 'absolute', inset: 0, zIndex: 10,
              background: 'rgba(255,255,255,0.7)', borderRadius: 'var(--radius-md)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <p style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>Updating comparison...</p>
            </div>
          )}

          {/* Comparison Table */}
          <ComparisonTable
            runs={comparedRuns}
            bestRunId={comparison!.best_run_id ?? null}
            colorMap={runColorMap}
          />

          {/* Charts grid */}
          <div className="arena-charts-grid">
            <MetricBarChart runs={comparedRuns} colorMap={runColorMap} />
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
