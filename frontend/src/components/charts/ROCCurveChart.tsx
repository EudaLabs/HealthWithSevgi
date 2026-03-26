import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts';
import type { ROCPoint } from '../../types';

interface Props {
  points: ROCPoint[];
  auc: number;
}

const ROCCurveChart: React.FC<Props> = ({ points, auc }) => {
  const chartData = points.map((p) => ({
    fpr: Number(p.fpr.toFixed(4)),
    tpr: Number(p.tpr.toFixed(4)),
  }));

  return (
    <div style={{ width: '100%', minWidth: 0 }}>
      <div className="chart-card-title">
        ROC Curve
        <span className="chart-auc-badge">AUC = {auc.toFixed(3)}</span>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="fpr"
            type="number"
            domain={[0, 1]}
            tickCount={6}
            label={{ value: 'False Positive Rate', position: 'insideBottom', offset: -2, fontSize: 12 }}
            fontSize={11}
          />
          <YAxis
            dataKey="tpr"
            type="number"
            domain={[0, 1]}
            tickCount={6}
            label={{ value: 'True Positive Rate', angle: -90, position: 'insideLeft', offset: 10, fontSize: 12 }}
            fontSize={11}
          />
          <Tooltip
            formatter={(value: number) => value.toFixed(3)}
            labelFormatter={(label: number) => `FPR: ${label.toFixed(3)}`}
          />
          <ReferenceLine
            segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]}
            stroke="#999"
            strokeDasharray="6 4"
            label={{ value: 'Random', position: 'insideBottomRight', fontSize: 10, fill: '#999' }}
          />
          <Line
            type="monotone"
            dataKey="tpr"
            stroke="#1a7a4c"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#1a7a4c' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ROCCurveChart;
