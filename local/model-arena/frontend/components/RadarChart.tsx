import React, { useMemo } from 'react'
import { ResponsiveRadar } from '@nivo/radar'
import type { ArenaRun } from '../types/arena'
import { MODEL_LABELS, RUN_COLORS, getMetric } from '../types/arena'

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
          getMetric(r.metrics, metric)
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
