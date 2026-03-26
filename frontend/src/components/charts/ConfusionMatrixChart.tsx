import React from 'react';
import type { ConfusionMatrixData } from '../../types';

interface Props {
  data: ConfusionMatrixData;
}

const BINARY_LABELS: [string, string, string, string] = [
  'True Negative',
  'False Positive',
  'False Negative',
  'True Positive',
];

function cellColor(value: number, max: number, isDiagonal: boolean): string {
  const intensity = max > 0 ? value / max : 0;
  if (isDiagonal) {
    return `rgba(26,122,76,${0.1 + intensity * 0.35})`;
  }
  return `rgba(220,53,69,${0.06 + intensity * 0.25})`;
}

const ConfusionMatrixChart: React.FC<Props> = ({ data }) => {
  const { matrix, labels } = data;
  const n = matrix.length;
  const isBinary = n === 2;
  const allValues = matrix.flat();
  const maxVal = Math.max(...allValues, 1);

  if (isBinary) {
    // Binary: render labeled 2x2 with clinical names
    const cells = [
      { value: data.tn, label: BINARY_LABELS[0], diag: true },
      { value: data.fp, label: BINARY_LABELS[1], diag: false },
      { value: data.fn, label: BINARY_LABELS[2], diag: false },
      { value: data.tp, label: BINARY_LABELS[3], diag: true },
    ];

    return (
      <div className="cm-container">
        <div className="cm-title">Confusion Matrix</div>
        <div style={{ display: 'inline-grid', gridTemplateColumns: 'auto auto auto', gap: 0, alignItems: 'center' }}>
          {/* Top-left empty corner */}
          <div />
          {/* Column headers */}
          <div className="cm-axis-label" style={{ textAlign: 'center', paddingBottom: 6 }}>
            Predicted {labels[0]}
          </div>
          <div className="cm-axis-label" style={{ textAlign: 'center', paddingBottom: 6 }}>
            Predicted {labels[1]}
          </div>

          {/* Row 0: Actual Negative */}
          <div className="cm-axis-label cm-axis-y" style={{ paddingRight: 8 }}>
            Actual {labels[0]}
          </div>
          <div className={`cm-cell ${cells[0].diag ? 'cm-cell-diag' : 'cm-cell-off'}`}>
            {cells[0].value}
            <span className="cm-cell-label">{cells[0].label}</span>
          </div>
          <div className={`cm-cell ${cells[1].diag ? 'cm-cell-diag' : 'cm-cell-off'}`}>
            {cells[1].value}
            <span className="cm-cell-label">{cells[1].label}</span>
          </div>

          {/* Row 1: Actual Positive */}
          <div className="cm-axis-label cm-axis-y" style={{ paddingRight: 8 }}>
            Actual {labels[1]}
          </div>
          <div className={`cm-cell ${cells[2].diag ? 'cm-cell-diag' : 'cm-cell-off'}`}>
            {cells[2].value}
            <span className="cm-cell-label">{cells[2].label}</span>
          </div>
          <div className={`cm-cell ${cells[3].diag ? 'cm-cell-diag' : 'cm-cell-off'}`}>
            {cells[3].value}
            <span className="cm-cell-label">{cells[3].label}</span>
          </div>
        </div>
      </div>
    );
  }

  // Multi-class: generic NxN grid
  return (
    <div className="cm-container">
      <div className="cm-title">Confusion Matrix</div>
      <div
        className="cm-grid"
        style={{
          display: 'inline-grid',
          gridTemplateColumns: `auto repeat(${n}, minmax(${n > 10 ? '28px' : '40px'}, 1fr))`,
          gap: n > 10 ? 1 : 3,
          maxWidth: '100%',
        }}
      >
        {/* Top-left corner */}
        <div />
        {/* Column headers */}
        {labels.map((label) => (
          <div key={`col-${label}`} className="cm-axis-label" style={{ textAlign: 'center', fontSize: '0.65rem' }}>
            {label}
          </div>
        ))}

        {/* Rows */}
        {matrix.map((row, i) => (
          <React.Fragment key={`row-${i}`}>
            <div className="cm-axis-label cm-axis-y" style={{ fontSize: '0.65rem' }}>
              {labels[i]}
            </div>
            {row.map((val, j) => {
              const isDiag = i === j;
              return (
                <div
                  key={`cell-${i}-${j}`}
                  className={`cm-cell ${isDiag ? 'cm-cell-diag' : 'cm-cell-off'}`}
                  style={{
                    background: cellColor(val, maxVal, isDiag),
                    minWidth: n > 10 ? 24 : 40,
                    minHeight: n > 10 ? 24 : 36,
                    fontSize: n > 10 ? '0.6rem' : '0.85rem',
                    padding: n > 10 ? '2px' : '0.5rem',
                  }}
                >
                  {val}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default ConfusionMatrixChart;
