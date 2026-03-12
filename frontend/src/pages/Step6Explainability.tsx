import React, { useEffect, useState } from 'react'
import { ArrowRight } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, ReferenceLine, ComposedChart,
} from 'recharts'
import { fetchGlobalExplainability, fetchPatientExplanation } from '../api/explain'
import type { GlobalExplainabilityResponse, SinglePatientExplainResponse, TrainResponse } from '../types'

interface Props {
  trainResponse: TrainResponse
  onNext: () => void
}

export default function Step6Explainability({ trainResponse, onNext }: Props) {
  const [global, setGlobal] = useState<GlobalExplainabilityResponse | null>(null)
  const [globalLoading, setGlobalLoading] = useState(true)
  const [globalError, setGlobalError] = useState<string | null>(null)

  const [patientIdx, setPatientIdx] = useState(0)
  const [patient, setPatient] = useState<SinglePatientExplainResponse | null>(null)
  const [patientLoading, setPatientLoading] = useState(false)
  const [showAll, setShowAll] = useState(false)

  const testSize = trainResponse.metrics.confusion_matrix.matrix.reduce(
    (acc, row) => acc + row.reduce((a, b) => a + b, 0), 0
  )

  useEffect(() => {
    setGlobalLoading(true)
    fetchGlobalExplainability(trainResponse.model_id)
      .then(setGlobal)
      .catch((e) => setGlobalError(e.message))
      .finally(() => setGlobalLoading(false))
  }, [trainResponse.model_id])

  const handleExplainPatient = async () => {
    setPatientLoading(true)
    try {
      const data = await fetchPatientExplanation(trainResponse.model_id, patientIdx)
      setPatient(data)
    } catch (e: unknown) {
      setGlobalError((e as Error).message)
    } finally {
      setPatientLoading(false)
    }
  }

  const features = global ? (showAll ? global.feature_importances : global.feature_importances.slice(0, 10)) : []
  const chartData = features.map(f => ({
    name: f.clinical_name.length > 28 ? f.clinical_name.slice(0, 28) + '…' : f.clinical_name,
    value: f.importance,
    direction: f.direction,
  }))

  const waterfallData = patient
    ? patient.waterfall.slice(0, showAll ? undefined : 8).map(p => ({
        name: p.plain_language.length > 35 ? p.plain_language.slice(0, 35) + '…' : p.plain_language,
        value: p.shap_value,
        direction: p.direction,
      }))
    : []

  return (
    <div className="step-page">
      <div className="step-page-header">
        <h2>Step 6 — Explainability</h2>
        <p>Which measurements drove the AI's predictions, and why?</p>
      </div>

      {/* Global Feature Importance */}
      <div className="card">
        <div className="card-title">Overall Feature Importance</div>
        <div className="card-subtitle">
          Which patient measurements had the most influence across all predictions.
          Method: <strong>{global?.method ?? '…'}</strong>
        </div>

        {globalLoading && (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            ⏳ Computing SHAP values…
          </div>
        )}

        {globalError && (
          <div className="alert alert-danger mt-3">{globalError}</div>
        )}

        {global && !globalLoading && (
          <>
            <ResponsiveContainer width="100%" height={Math.max(300, features.length * 30)} style={{ marginTop: '1rem' }}>
              <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 40 }}>
                <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={v => v.toFixed(4)} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={220} />
                <Tooltip formatter={(v: number) => v.toFixed(5)} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {chartData.map((d, i) => (
                    <Cell key={i} fill={d.direction === 'positive' ? '#de350b' : d.direction === 'negative' ? '#1e6b9c' : '#8993a4'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', fontSize: '0.78rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <span style={{ width: 12, height: 12, background: '#de350b', borderRadius: 2, display: 'inline-block' }} />
                Increases risk
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <span style={{ width: 12, height: 12, background: '#1e6b9c', borderRadius: 2, display: 'inline-block' }} />
                Decreases risk
              </span>
            </div>

            <button className="btn btn-ghost btn-sm mt-2" onClick={() => setShowAll(p => !p)}>
              {showAll ? 'Show Top 10 Only' : `Show All ${global.feature_importances.length} Features`}
            </button>

            <div className="alert alert-success mt-3">
              <span>⚕️</span>
              <div>
                <strong>Clinical sense-check:</strong> {global.top_feature_clinical_note}
                <div style={{ marginTop: '0.3rem', fontSize: '0.82rem' }}>
                  Top 5 features explain <strong>{global.explained_variance_pct}%</strong> of model decisions.
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Single Patient Explanation */}
      <div className="card">
        <div className="card-title">Single-Patient Explanation</div>
        <div className="card-subtitle">Select a test patient to see why the AI made a specific prediction.</div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end', marginTop: '1rem' }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Select test patient</label>
            <input
              type="number"
              className="form-input"
              min={0}
              max={testSize - 1}
              value={patientIdx}
              onChange={e => setPatientIdx(Number(e.target.value))}
            />
          </div>
          <button className="btn btn-primary" onClick={handleExplainPatient} disabled={patientLoading}>
            {patientLoading ? '⏳ Explaining…' : 'Explain This Patient'}
          </button>
        </div>

        {patient && (
          <>
            <div className="card mt-3" style={{ background: 'var(--background)' }}>
              <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Predicted Class</div>
                  <span className="badge badge-primary" style={{ fontSize: '0.9rem', marginTop: '0.2rem' }}>
                    {patient.predicted_class}
                  </span>
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Probability</div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--primary)' }}>
                    {(patient.predicted_probability * 100).toFixed(1)}%
                  </div>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    {patient.clinical_summary}
                  </div>
                </div>
              </div>
            </div>

            <div style={{ marginTop: '1rem' }}>
              <div className="card-subtitle" style={{ marginBottom: '0.5rem' }}>
                SHAP Waterfall — contributions per feature
              </div>
              <ResponsiveContainer width="100%" height={Math.max(250, waterfallData.length * 35)}>
                <BarChart data={waterfallData} layout="vertical" margin={{ left: 20, right: 40 }}>
                  <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={v => v.toFixed(3)} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={250} />
                  <Tooltip formatter={(v: number) => v.toFixed(5)} />
                  <ReferenceLine x={0} stroke="var(--border)" />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {waterfallData.map((d, i) => (
                      <Cell key={i} fill={d.direction === 'increases_risk' ? '#de350b' : '#1e6b9c'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <button className="btn btn-ghost btn-sm mt-2" onClick={() => setShowAll(p => !p)}>
                {showAll ? 'Show Top 8' : 'Show All Features'}
              </button>
            </div>
          </>
        )}
      </div>

      <div className="alert alert-warning">
        <span>⚕️</span>
        <div>
          <strong>Important Clinical Reminder:</strong> These explanations show associations between
          measurements and outcomes in the training data — they do not prove causation. A clinician must
          always decide whether and how to act on any AI prediction. This tool is an educational aid,
          not a diagnostic device.
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button className="btn btn-primary" onClick={onNext}>
          View Ethics & Bias <ArrowRight size={16} />
        </button>
      </div>
    </div>
  )
}
