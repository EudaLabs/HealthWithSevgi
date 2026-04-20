import React, { useMemo } from 'react'

/* ------------------------------------------------------------------ */
/*  Color & label maps for the eight supported model types             */
/* ------------------------------------------------------------------ */

const MODEL_COLORS: Record<string, string> = {
  knn: '#36b5d8',
  svm: '#e8843c',
  decision_tree: '#f5c542',
  random_forest: '#4caf50',
  logistic_regression: '#ab47bc',
  naive_bayes: '#ef5350',
  xgboost: '#5c6bc0',
  lightgbm: '#26a69a',
}

const MODEL_LABELS: Record<string, string> = {
  knn: 'KNN',
  svm: 'SVM',
  decision_tree: 'Decision Tree',
  random_forest: 'Random Forest',
  logistic_regression: 'Logistic Reg',
  naive_bayes: 'Naive Bayes',
  xgboost: 'XGBoost',
  lightgbm: 'LightGBM',
}

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */

interface ParallelCoordsLegendProps {
  entries: Array<{ model_type: string; model_id: string }>
  pinnedIds: Set<string>
  onTogglePin: (modelId: string) => void
  onResetBrushes: () => void
  onClearPins: () => void
  hasBrushes: boolean
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

/**
 * Colour legend for the Parallel Coordinates chart.
 * Renders one swatch + label per model so the user can map coloured lines
 * on the chart back to classifier names. Clicking a swatch pins/unpins a
 * line; the other controls reset brushes and clear pinned lines.
 */
const ParallelCoordsLegend: React.FC<ParallelCoordsLegendProps> = ({
  entries,
  pinnedIds,
  onResetBrushes,
  onClearPins,
  hasBrushes,
}) => {
  const uniqueTypes = useMemo(() => {
    const seen = new Set<string>()
    const result: string[] = []
    for (const entry of entries) {
      if (!seen.has(entry.model_type)) {
        seen.add(entry.model_type)
        result.push(entry.model_type)
      }
    }
    return result
  }, [entries])

  return (
    <div className="pc-legend">
      {/* Left side: model type legend */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', flex: 1 }}>
        {uniqueTypes.map((type) => (
          <span className="pc-legend-item" key={type}>
            <span
              className="pc-legend-dot"
              style={{ backgroundColor: MODEL_COLORS[type] }}
            />
            {MODEL_LABELS[type] || type}
          </span>
        ))}
      </div>

      {/* Right side: control buttons */}
      <div style={{ display: 'flex', gap: '8px' }}>
        {hasBrushes && (
          <button className="pc-btn" onClick={onResetBrushes}>
            Reset Filters
          </button>
        )}
        {pinnedIds.size > 0 && (
          <button className="pc-btn" onClick={onClearPins}>
            Clear Pins ({pinnedIds.size})
          </button>
        )}
      </div>
    </div>
  )
}

export { MODEL_COLORS, MODEL_LABELS }
export type { ParallelCoordsLegendProps }
export default React.memo(ParallelCoordsLegend)
