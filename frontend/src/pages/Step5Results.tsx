import React, { useMemo } from 'react'
import { ArrowRight, AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ReferenceLine, CartesianGrid, Legend,
} from 'recharts'
import type { TrainResponse } from '../types'

function pct(v: number) { return `${(v * 100).toFixed(1)}%` }

const METRIC_DEFS = [
  { key: 'accuracy' as const, label: 'Accuracy', green: 0.65, amber: 0.55, starred: false,
    meaning: 'Out of all test patients, what percentage did the AI classify correctly?' },
  { key: 'sensitivity' as const, label: 'Sensitivity', green: 0.70, amber: 0.50, starred: true,
    meaning: 'Of patients who WERE positive, how many did the AI catch? Most important for screening.' },
  { key: 'specificity' as const, label: 'Specificity', green: 0.65, amber: 0.55, starred: false,
    meaning: 'Of patients who were NOT positive, how many did the AI correctly identify as safe?' },
  { key: 'precision' as const, label: 'Precision', green: 0.60, amber: 0.50, starred: false,
    meaning: 'Of all patients the AI flagged, how many actually were positive?' },
  { key: 'f1_score' as const, label: 'F1 Score', green: 0.65, amber: 0.55, starred: false,
    meaning: 'A combined score balancing Sensitivity and Precision.' },
  { key: 'auc_roc' as const, label: 'AUC-ROC', green: 0.75, amber: 0.65, starred: false,
    meaning: '0.5 = no better than chance, 1.0 = perfect. Measures overall separability.' },
]

const DIAG_DATA = [{ fpr: 0, tpr: 0 }, { fpr: 1, tpr: 1 }]

interface Props {
  trainResponse: TrainResponse
  onNext: () => void
}

export default function Step5Results({ trainResponse, onNext }: Props) {
  const { metrics } = trainResponse
  const cm = metrics.confusion_matrix
  const isBinary = cm.labels.length === 2

  const rocData = useMemo(
    () => metrics.roc_curve.map(p => ({ fpr: p.fpr, tpr: p.tpr })),
    [metrics.roc_curve]
  )

  const prData = useMemo(
    () => metrics.pr_curve.map(p => ({ recall: p.recall, precision: p.precision })),
    [metrics.pr_curve]
  )

  const cvMean = metrics.cross_val_scores.length
    ? metrics.cross_val_scores.reduce((a, b) => a + b, 0) / metrics.cross_val_scores.length
    : null
  const overfitGap = metrics.train_accuracy - metrics.accuracy

  return (
    <div className="step-page" aria-live="polite">
      <div className="step-page-header">
        <h2>Step 5 — Results</h2>
        <p>How well did the AI perform on patients it had never seen before?</p>
      </div>

      {/* Low sensitivity warning */}
      {metrics.low_sensitivity_warning && (
        <div className="alert alert-danger">
          <AlertTriangle size={20} />
          <div>
            <strong>⚠ Low Sensitivity Warning.</strong> This model missed more than half the patients who
            actually had the condition (Sensitivity {pct(metrics.sensitivity)}). Return to Step 4 and try a
            different model or adjust parameters before drawing any conclusions.
          </div>
        </div>
      )}

      {/* 6 metric cards */}
      <div className="grid-3" key={trainResponse.model_id}>
        {METRIC_DEFS.map(({ key, label, green, amber, starred, meaning }) => {
          const v = metrics[key]
          const isGreen = v >= green
          const isAmber = !isGreen && v >= amber
          const bgCls = isGreen ? 'metric-bg-green' : isAmber ? 'metric-bg-amber' : 'metric-bg-red'
          const textCls = isGreen ? 'metric-green' : isAmber ? 'metric-amber' : 'metric-red'
          const Icon = isGreen ? CheckCircle : isAmber ? Info : XCircle
          return (
            <div key={key} className={`card ${bgCls}`} style={{ padding: '1rem' }} title={meaning}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, lineHeight: 1.3 }}>
                  {label}{starred && <>{" "}<span aria-hidden="true">⭐</span></>}
                </div>
                <Icon size={16} className={textCls} aria-label={isGreen ? 'Good' : isAmber ? 'Warning' : 'Poor'} />
              </div>
              <div className={`font-bold ${textCls}`} style={{ fontSize: '1.8rem', marginTop: '0.3rem' }}>
                {pct(v)}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Threshold: ≥{pct(green)}
              </div>
            </div>
          )
        })}
      </div>

      {/* Overfitting / CV */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title">Training vs. Test Accuracy</div>
          <div style={{ marginTop: '0.5rem', display: 'flex', gap: '2rem' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Train</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{pct(metrics.train_accuracy)}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Test</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{pct(metrics.accuracy)}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Gap</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: overfitGap > 0.1 ? 'var(--warning)' : 'var(--success)' }}>
                {pct(overfitGap)}
              </div>
            </div>
          </div>
          {overfitGap > 0.1 && (
            <div className="alert alert-warning mt-3" style={{ fontSize: '0.8rem' }}>
              <AlertTriangle size={14} />
              <span>Gap &gt;10% suggests possible overfitting. Try reducing model complexity.</span>
            </div>
          )}
          {cvMean !== null && (
            <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              5-fold Cross-Validation AUC: <strong>{pct(cvMean)}</strong>
            </div>
          )}
        </div>

        {/* ROC Curve */}
        <div className="card">
          <div className="card-title">ROC Curve</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
            AUC = <strong style={{ color: 'var(--primary)' }}>{metrics.auc_roc.toFixed(3)}</strong>
          </div>
          {rocData.length < 2 ? (
            <div className="alert alert-info">
              <Info size={16} />
              <span>ROC curve not available for this classification type. The chart requires binary probability scores.</span>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="fpr" type="number" domain={[0,1]} tick={{ fontSize: 10 }} label={{ value: 'FPR', position: 'insideBottomRight', offset: -5, fontSize: 11 }} />
                <YAxis domain={[0,1]} tick={{ fontSize: 10 }} label={{ value: 'TPR', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                <Tooltip formatter={(v: number) => [v.toFixed(3)]} />
                <Legend verticalAlign="bottom" height={24} />
                <Line data={DIAG_DATA} dataKey="tpr" stroke="var(--border)" strokeDasharray="5 5" dot={false} name="Random" />
                <Line data={rocData} dataKey="tpr" stroke="var(--primary)" strokeWidth={2} dot={false} name="Model" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* PR Curve */}
      <div className="card">
        <div className="card-title">Precision-Recall Curve</div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
          Higher area = better at finding true positives without false alarms.
        </div>
        {prData.length < 2 ? (
          <div className="alert alert-info">
            <Info size={16} />
            <span>PR curve not available — requires binary probability scores.</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="recall" type="number" domain={[0, 1]} tick={{ fontSize: 10 }} label={{ value: 'Recall', position: 'insideBottomRight', offset: -5, fontSize: 11 }} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 10 }} label={{ value: 'Precision', angle: -90, position: 'insideLeft', fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [v.toFixed(3)]} />
              <Legend verticalAlign="bottom" height={24} />
              <Line data={prData} dataKey="precision" stroke="var(--primary)" strokeWidth={2} dot={false} name="PR Curve" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Confusion Matrix */}
      <div className="card">
        <div className="card-title">Confusion Matrix</div>
        <div className="card-subtitle" style={{ marginBottom: '1.25rem' }}>
          What the AI got right and wrong on test patients.
        </div>
        {isBinary ? (
          <div>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <div style={{ width: 120 }} />
              <div style={{ flex: 1, textAlign: 'center', fontWeight: 600 }}>AI: Not at Risk</div>
              <div style={{ flex: 1, textAlign: 'center', fontWeight: 600 }}>AI: At Risk</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'stretch' }}>
                <div style={{ width: 120, display: 'flex', alignItems: 'center', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>Actually: Safe</div>
                <div className="cm-cell cm-cell-tn" style={{ flex: 1 }}>
                  <div className="cm-count">{cm.tn}</div>
                  <div className="cm-label" style={{ color: 'var(--primary)' }}><span aria-hidden="true">✅</span> True Negative</div>
                  <div className="cm-desc">Correctly called safe</div>
                </div>
                <div className="cm-cell cm-cell-fp" style={{ flex: 1 }}>
                  <div className="cm-count">{cm.fp}</div>
                  <div className="cm-label" style={{ color: '#7a5200' }}><span aria-hidden="true">⚠️</span> False Positive</div>
                  <div className="cm-desc">Unnecessary alarm</div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'stretch' }}>
                <div style={{ width: 120, display: 'flex', alignItems: 'center', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>Actually: At Risk</div>
                <div className="cm-cell cm-cell-fn" style={{ flex: 1 }}>
                  <div className="cm-count">{cm.fn}</div>
                  <div className="cm-label" style={{ color: 'var(--danger)' }}><span aria-hidden="true">❌</span> False Negative</div>
                  <div className="cm-desc">MISSED — most dangerous</div>
                </div>
                <div className="cm-cell cm-cell-tp" style={{ flex: 1 }}>
                  <div className="cm-count">{cm.tp}</div>
                  <div className="cm-label" style={{ color: 'var(--success)' }}><span aria-hidden="true">✅</span> True Positive</div>
                  <div className="cm-desc">Correctly flagged</div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>True \ Pred</th>
                  {cm.labels.map(l => <th key={l}>{l}</th>)}
                </tr>
              </thead>
              <tbody>
                {cm.matrix.map((row, i) => (
                  <tr key={i}>
                    <td className="font-semibold">{cm.labels[i]}</td>
                    {row.map((v, j) => (
                      <td key={j} style={{ background: i === j ? 'var(--success-light)' : undefined, fontWeight: i === j ? 700 : undefined }}>
                        {v}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button className="btn btn-primary" onClick={onNext}>
          View Explainability <ArrowRight size={16} />
        </button>
      </div>
    </div>
  )
}
