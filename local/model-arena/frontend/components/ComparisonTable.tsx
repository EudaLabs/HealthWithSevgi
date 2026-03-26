import React, { useMemo, useState } from 'react'
import type { ArenaRun } from '../types/arena'
import { MODEL_LABELS, METRIC_LABELS, RUN_COLORS, getMetric } from '../types/arena'

interface Props {
  runs: ArenaRun[]
  bestRunId: string | null
  colorMap?: Map<string, string>
}

const METRIC_KEYS = [
  'accuracy', 'sensitivity', 'specificity', 'precision',
  'f1_score', 'auc_roc', 'mcc', 'train_accuracy',
] as const

type SortKey = typeof METRIC_KEYS[number] | 'training_time_ms' | null

export default function ComparisonTable({ runs, bestRunId, colorMap }: Props) {
  const [diffOnly, setDiffOnly] = useState(false)
  const [sortBy, setSortBy] = useState<SortKey>(null)
  const [sortDesc, setSortDesc] = useState(true)

  const sortedRuns = useMemo(() => {
    if (!sortBy) return runs
    return [...runs].sort((a, b) => {
      const aVal = sortBy === 'training_time_ms'
        ? a.training_time_ms
        : getMetric(a.metrics, sortBy)
      const bVal = sortBy === 'training_time_ms'
        ? b.training_time_ms
        : getMetric(b.metrics, sortBy)
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
        const val = getMetric(r.metrics, metric)
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
                <th key={r.run_id} style={{ borderTop: `3px solid ${colorMap?.get(r.run_id) ?? RUN_COLORS[i % RUN_COLORS.length]}` }}>
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
                  tabIndex={0}
                  role="button"
                  aria-label={`Sort by ${METRIC_LABELS[metric]}`}
                  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort(metric) } }}
                >
                  {METRIC_LABELS[metric]}{sortIndicator(metric)}
                </td>
                {sortedRuns.map((r) => {
                  const val = getMetric(r.metrics, metric)
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
                tabIndex={0}
                role="button"
                aria-label="Sort by Training Time"
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort('training_time_ms') } }}
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
