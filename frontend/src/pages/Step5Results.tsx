import React, { useMemo } from 'react'
import { ArrowRight, AlertTriangle, CheckCircle, XCircle, Info, BarChart2 } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ReferenceLine, CartesianGrid, Legend, Bar, BarChart,
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
  const cvFoldData = useMemo(
    () => metrics.cross_val_scores.map((s, i) => ({ fold: `Fold ${i + 1}`, score: s })),
    [metrics.cross_val_scores]
  )
  const overfitGap = metrics.train_accuracy - metrics.accuracy

  // Derive strengths and areas for improvement from metrics
  const strengths: string[] = []
  const improvements: string[] = []
  if (metrics.accuracy >= 0.65) strengths.push(`Strong overall accuracy (${pct(metrics.accuracy)})`)
  else improvements.push(`Overall accuracy could be higher (${pct(metrics.accuracy)})`)
  if (metrics.sensitivity >= 0.70) strengths.push(`Good sensitivity — catches most positive cases (${pct(metrics.sensitivity)})`)
  else improvements.push(`Sensitivity is low — misses some positive cases (${pct(metrics.sensitivity)})`)
  if (metrics.specificity >= 0.65) strengths.push(`Good specificity — few false alarms (${pct(metrics.specificity)})`)
  else improvements.push(`Specificity needs improvement — too many false alarms (${pct(metrics.specificity)})`)
  if (metrics.auc_roc >= 0.75) strengths.push(`Excellent AUC-ROC discriminability (${metrics.auc_roc.toFixed(2)})`)
  else if (metrics.auc_roc >= 0.65) strengths.push(`Reasonable AUC-ROC (${metrics.auc_roc.toFixed(2)})`)
  else improvements.push(`AUC-ROC indicates limited discriminability (${metrics.auc_roc.toFixed(2)})`)
  if (overfitGap <= 0.05) strengths.push('Good generalisation — train/test gap is small')
  else improvements.push(`Possible overfitting — train/test gap of ${pct(overfitGap)}`)

  return (
    <div className="step-page" aria-live="polite">
      {/* Page header */}
      <div>
        <span className="step-badge">STEP 5 · RESULTS</span>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BarChart2 size={22} color="var(--primary)" />
          Model Results &amp; Performance Metrics
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
          How well did the AI perform on patients it had never seen before?
        </p>
      </div>

      {/* Low sensitivity warning */}
      {metrics.low_sensitivity_warning && (
        <div className="alert alert-danger">
          <AlertTriangle size={20} />
          <div>
            <strong>Low Sensitivity Warning.</strong> This model missed more than half the patients who
            actually had the condition (Sensitivity {pct(metrics.sensitivity)}). Return to Step 4 and try a
            different model or adjust parameters before drawing any conclusions.
          </div>
        </div>
      )}

      {/* 6 large metric cards in 3x2 grid */}
      <div className="grid-3" key={trainResponse.model_id}>
        {METRIC_DEFS.map(({ key, label, green, amber, starred, meaning }) => {
          const v = metrics[key]
          const isGreen = v >= green
          const isAmber = !isGreen && v >= amber
          const bgCls = isGreen ? 'metric-bg-green' : isAmber ? 'metric-bg-amber' : 'metric-bg-red'
          const textCls = isGreen ? 'metric-green' : isAmber ? 'metric-amber' : 'metric-red'
          const Icon = isGreen ? CheckCircle : isAmber ? Info : XCircle
          const isAUC = key === 'auc_roc'
          return (
            <div key={key} className={`card ${bgCls}`} style={{ padding: '1.25rem' }} title={meaning}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600, lineHeight: 1.3, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  {label}{starred && <>{" "}<span aria-hidden="true">⭐</span></>}
                </div>
                <Icon size={16} className={textCls} aria-label={isGreen ? 'Good' : isAmber ? 'Warning' : 'Poor'} />
              </div>
              <div className={`font-bold ${textCls}`} style={{ fontSize: '2rem', marginTop: '0.4rem', lineHeight: 1 }}>
                {isAUC ? v.toFixed(2) : pct(v)}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                Target: ≥{pct(green)}
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
          {metrics.cross_val_scores.length > 0 && (
            <div style={{ marginTop: '0.75rem' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                Cross-Validation Fold Scores (mean: <strong style={{ color: 'var(--primary)' }}>{cvMean !== null ? pct(cvMean) : 'N/A'}</strong>)
              </div>
              <ResponsiveContainer width="100%" height={100}>
                <BarChart data={cvFoldData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="fold" tick={{ fontSize: 10 }} />
                  <YAxis domain={[0, 1]} tick={{ fontSize: 10 }} />
                  <Tooltip formatter={(v: number) => pct(v)} />
                  {cvMean !== null && <ReferenceLine y={cvMean} stroke="var(--primary)" strokeDasharray="5 5" label={{ value: 'Mean', fontSize: 10 }} />}
                  <Bar dataKey="score" fill="var(--primary)" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                High variance across folds may indicate unstable model performance.
              </div>
            </div>
          )}
        </div>

        {/* ROC Curve */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <div className="card-title" style={{ margin: 0 }}>ROC Curve</div>
            <span className="chart-auc-badge">AUC {metrics.auc_roc.toFixed(2)}</span>
          </div>
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

      {/* Confusion Matrix + PR Curve side by side */}
      <div className="grid-2">
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
                    <div className="cm-label" style={{ color: 'var(--primary)' }}>TN — True Negative</div>
                    <div className="cm-desc">Correctly called safe</div>
                  </div>
                  <div className="cm-cell cm-cell-fp" style={{ flex: 1 }}>
                    <div className="cm-count">{cm.fp}</div>
                    <div className="cm-label" style={{ color: '#7a5200' }}>FP — False Positive</div>
                    <div className="cm-desc">Unnecessary alarm</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'stretch' }}>
                  <div style={{ width: 120, display: 'flex', alignItems: 'center', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>Actually: At Risk</div>
                  <div className="cm-cell cm-cell-fn" style={{ flex: 1 }}>
                    <div className="cm-count">{cm.fn}</div>
                    <div className="cm-label" style={{ color: 'var(--danger)' }}>FN — False Negative</div>
                    <div className="cm-desc">MISSED — most dangerous</div>
                  </div>
                  <div className="cm-cell cm-cell-tp" style={{ flex: 1 }}>
                    <div className="cm-count">{cm.tp}</div>
                    <div className="cm-label" style={{ color: 'var(--success)' }}>TP — True Positive</div>
                    <div className="cm-desc">Correctly flagged</div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table" style={{ minWidth: cm.labels.length > 5 ? '600px' : undefined }}>
                <thead>
                  <tr>
                    <th style={{ minWidth: 80 }}>True \ Pred</th>
                    {cm.labels.map(l => (
                      <th key={l} style={{ maxWidth: 100, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={l}>{l}</th>
                    ))}
                    <th style={{ fontStyle: 'italic', color: 'var(--primary)' }}>Recall</th>
                  </tr>
                </thead>
                <tbody>
                  {cm.matrix.map((row, i) => {
                    const rowTotal = row.reduce((a, b) => a + b, 0)
                    const recall = rowTotal > 0 ? row[i] / rowTotal : 0
                    return (
                      <tr key={i}>
                        <td className="font-semibold" style={{ maxWidth: 100, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={cm.labels[i]}>{cm.labels[i]}</td>
                        {row.map((v, j) => {
                          const norm = rowTotal > 0 ? v / rowTotal : 0
                          const isDiag = i === j
                          const bg = isDiag
                            ? `rgba(26, 122, 76, ${Math.max(0.1, norm * 0.7)})`
                            : norm > 0 ? `rgba(222, 53, 11, ${Math.max(0.05, norm * 0.5)})` : undefined
                          return (
                            <td key={j} style={{ background: bg, fontWeight: isDiag ? 700 : undefined, textAlign: 'center' }}>
                              {v}
                            </td>
                          )
                        })}
                        <td style={{ fontWeight: 600, color: recall >= 0.7 ? 'var(--success)' : recall >= 0.5 ? '#8a5200' : 'var(--danger)' }}>
                          {(recall * 100).toFixed(1)}%
                        </td>
                      </tr>
                    )
                  })}
                  {/* Precision row */}
                  <tr>
                    <td className="font-semibold" style={{ fontStyle: 'italic', color: 'var(--primary)' }}>Precision</td>
                    {cm.matrix[0]?.map((_, j) => {
                      const colTotal = cm.matrix.reduce((sum, row) => sum + row[j], 0)
                      const precision = colTotal > 0 ? cm.matrix[j]?.[j] / colTotal : 0
                      return (
                        <td key={j} style={{ fontWeight: 600, color: precision >= 0.7 ? 'var(--success)' : precision >= 0.5 ? '#8a5200' : 'var(--danger)' }}>
                          {(precision * 100).toFixed(1)}%
                        </td>
                      )
                    })}
                    <td />
                  </tr>
                </tbody>
              </table>
            </div>
          )}
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
      </div>

      {/* Strengths and Areas for Improvement */}
      <div className="grid-2">
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <CheckCircle size={18} color="var(--success)" />
            <div className="card-title" style={{ margin: 0, color: 'var(--success)' }}>Model Strengths</div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {strengths.length > 0 ? strengths.map((s, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start', fontSize: '0.875rem' }}>
                <CheckCircle size={14} color="var(--success)" style={{ flexShrink: 0, marginTop: 2 }} />
                <span>{s}</span>
              </div>
            )) : (
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>No notable strengths identified with current thresholds.</div>
            )}
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <XCircle size={18} color="var(--danger)" />
            <div className="card-title" style={{ margin: 0, color: 'var(--danger)' }}>Areas for Improvement</div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {improvements.length > 0 ? improvements.map((s, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start', fontSize: '0.875rem' }}>
                <XCircle size={14} color="var(--danger)" style={{ flexShrink: 0, marginTop: 2 }} />
                <span>{s}</span>
              </div>
            )) : (
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>No significant areas for improvement identified.</div>
            )}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button className="btn btn-primary" onClick={onNext}>
          View Explainability <ArrowRight size={16} />
        </button>
      </div>
    </div>
  )
}
