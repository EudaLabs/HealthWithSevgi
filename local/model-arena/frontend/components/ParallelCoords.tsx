import React, { useMemo } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-basic-dist-min'
import type { ArenaRun } from '../types/arena'
import { MODEL_LABELS, RUN_COLORS, getMetric } from '../types/arena'

const Plot = createPlotlyComponent(Plotly)

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
    const dimensions: { label: string; values: number[]; range: readonly [number, number] | [number, number] }[] =
      DISPLAY_METRICS.map((m) => ({
        label: m.label,
        values: runs.map((r) => getMetric(r.metrics, m.key)),
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
          const minVal = Math.min(...nums)
          const maxVal = Math.max(...nums)
          const pad = (maxVal - minVal) * 0.1 || Math.abs(maxVal) * 0.1 || 1
          dimensions.push({
            label: key,
            values: nums,
            range: [minVal - pad, maxVal + pad],
          })
        }
      }
    }

    // Color by AUC-ROC value
    const colorValues = runs.map((r) => getMetric(r.metrics, 'auc_roc'))

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
            dimensions: dimensions,
          },
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
