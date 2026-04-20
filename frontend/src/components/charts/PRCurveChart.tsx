import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

interface Props {
  points: { precision: number; recall: number }[];
}

/**
 * Precision–Recall curve (Step 5).
 * Useful companion to the ROC curve for imbalanced datasets where ROC can
 * look falsely optimistic. Points are `{recall, precision}` pairs from the
 * training response; the x-axis is recall, the y-axis is precision.
 */
const PRCurveChart: React.FC<Props> = ({ points }) => {
  const chartData = points.map((p) => ({
    recall: Number(p.recall.toFixed(4)),
    precision: Number(p.precision.toFixed(4)),
  }));

  return (
    <div style={{ width: '100%', minWidth: 0 }}>
      <div className="chart-card-title">Precision-Recall Curve</div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="recall"
            type="number"
            domain={[0, 1]}
            tickCount={6}
            label={{ value: 'Recall', position: 'insideBottom', offset: -2, fontSize: 12 }}
            fontSize={11}
          />
          <YAxis
            dataKey="precision"
            type="number"
            domain={[0, 1]}
            tickCount={6}
            label={{ value: 'Precision', angle: -90, position: 'insideLeft', offset: 10, fontSize: 12 }}
            fontSize={11}
          />
          <Tooltip
            formatter={(value: number) => value.toFixed(3)}
            labelFormatter={(label: number) => `Recall: ${label.toFixed(3)}`}
          />
          <Line
            type="monotone"
            dataKey="precision"
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

export default PRCurveChart;
