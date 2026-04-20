import React, { useRef, useLayoutEffect, useState } from 'react';
import type { CompareEntry } from '../../types';

interface ParallelCoordsTooltipProps {
  entry: CompareEntry | null;
  x: number;
  y: number;
  visible: boolean;
  color: string;
  containerRef: React.RefObject<HTMLDivElement>;
}

const MODEL_LABELS: Record<string, string> = {
  knn: 'K-Nearest Neighbours',
  svm: 'Support Vector Machine',
  decision_tree: 'Decision Tree',
  random_forest: 'Random Forest',
  logistic_regression: 'Logistic Regression',
  naive_bayes: 'Na\u00efve Bayes',
  xgboost: 'XGBoost',
  lightgbm: 'LightGBM',
};

function formatParamName(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatPct(value: number): string {
  return (value * 100).toFixed(1) + '%';
}

/**
 * Hover tooltip for a single polyline in the Parallel Coordinates chart.
 * Shows the classifier label plus every metric's value on that line so the
 * user can pick exact numbers without leaving the chart.
 */
const ParallelCoordsTooltip: React.FC<ParallelCoordsTooltipProps> = ({
  entry,
  x,
  y,
  visible,
  color,
  containerRef,
}) => {
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ left: x, top: y });

  useLayoutEffect(() => {
    if (!visible || !tooltipRef.current || !containerRef.current) {
      setPosition({ left: x, top: y });
      return;
    }

    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const containerRect = containerRef.current.getBoundingClientRect();

    let left = x;
    let top = y;

    if (x + tooltipRect.width > containerRect.width) {
      left = x - tooltipRect.width;
    }

    if (y + tooltipRect.height > containerRect.height) {
      top = y - tooltipRect.height;
    }

    setPosition({ left, top });
  }, [x, y, visible, containerRef]);

  if (!entry) return null;

  const { model_type, params, metrics, training_time_ms } = entry;
  const label = MODEL_LABELS[model_type] ?? model_type;

  const paramEntries = Object.entries(params);
  const hasParams = paramEntries.length > 0;

  const className = visible
    ? 'pc-tooltip pc-tooltip--visible'
    : 'pc-tooltip';

  return (
    <div
      ref={tooltipRef}
      className={className}
      style={{ left: position.left, top: position.top }}
    >
      <div className="pc-tooltip-title">
        <span
          className="pc-tooltip-dot"
          style={{ backgroundColor: color }}
        />
        {label}
      </div>

      <div style={{ borderTop: '1px solid #2d3a48', margin: '6px 0' }} />

      {hasParams && (
        <>
          {paramEntries.map(([key, value]) => (
            <div className="pc-tooltip-row" key={key}>
              <span>{formatParamName(key)}</span>
              <span className="pc-tooltip-value">{String(value)}</span>
            </div>
          ))}
          <div style={{ borderTop: '1px solid #2d3a48', margin: '6px 0' }} />
        </>
      )}

      <div className="pc-tooltip-row">
        <span>AUC-ROC</span>
        <span className="pc-tooltip-value">{formatPct(metrics.auc_roc)}</span>
      </div>
      <div className="pc-tooltip-row">
        <span>Accuracy</span>
        <span className="pc-tooltip-value">{formatPct(metrics.accuracy)}</span>
      </div>
      <div className="pc-tooltip-row">
        <span>F1 Score</span>
        <span className="pc-tooltip-value">{formatPct(metrics.f1_score)}</span>
      </div>
      <div className="pc-tooltip-row">
        <span>Sensitivity</span>
        <span className="pc-tooltip-value">
          {formatPct(metrics.sensitivity)}
        </span>
      </div>
      <div className="pc-tooltip-row">
        <span>Specificity</span>
        <span className="pc-tooltip-value">
          {formatPct(metrics.specificity)}
        </span>
      </div>
      <div className="pc-tooltip-row">
        <span>Precision</span>
        <span className="pc-tooltip-value">{formatPct(metrics.precision)}</span>
      </div>
      <div className="pc-tooltip-row">
        <span>MCC</span>
        <span className="pc-tooltip-value">{metrics.mcc.toFixed(3)}</span>
      </div>
      <div className="pc-tooltip-row">
        <span>Training Time</span>
        <span className="pc-tooltip-value">
          {Math.round(training_time_ms)}ms
        </span>
      </div>
    </div>
  );
};

export default React.memo(ParallelCoordsTooltip);
