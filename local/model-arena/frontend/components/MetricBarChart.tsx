import React, { useMemo, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell,
} from 'recharts'
import type { ArenaRun } from '../types/arena'
import { MODEL_LABELS, METRIC_LABELS, RUN_COLORS, getMetric } from '../types/arena'

interface Props {
  runs: ArenaRun[]
  colorMap?: Map<string, string>
}

const METRICS = [
  'accuracy', 'sensitivity', 'specificity', 'precision', 'f1_score', 'auc_roc', 'mcc',
] as const

export default function MetricBarChart({ runs, colorMap }: Props) {
  const [selectedMetric, setSelectedMetric] = useState<string>('auc_roc')

  const data = useMemo(() => {
    return runs.map((r, i) => ({
      name: MODEL_LABELS[r.model_type],
      value: getMetric(r.metrics, selectedMetric),
      color: colorMap?.get(r.run_id) ?? RUN_COLORS[i % RUN_COLORS.length],
    }))
  }, [runs, selectedMetric])

  const yDomain = useMemo((): [number, number] => {
    if (selectedMetric === 'mcc') return [-1, 1]
    return [0, 1]
  }, [selectedMetric])

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
          <YAxis domain={yDomain} tick={{ fontSize: 12 }} />
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
