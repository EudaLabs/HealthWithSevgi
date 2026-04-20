import React, { useEffect, useState } from 'react'
import { AlertTriangle, Eye } from 'lucide-react'
import InfoTip from '../components/InfoTip'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, ReferenceLine, ComposedChart,
} from 'recharts'
import { fetchGlobalExplainability, fetchPatientExplanation, fetchSamplePatients, fetchWhatIf } from '../api/explain'
import type { GlobalExplainabilityResponse, SinglePatientExplainResponse, TrainResponse, SamplePatient, WhatIfResponse } from '../types'

interface Props {
  trainResponse: TrainResponse
  onNext: () => void
}

/**
 * Step 6 — Explainability.
 * SHAP global feature importance chart, per-patient waterfall for a
 * selectable test-set patient, clinical sense-check banner, and the
 * What-If simulator that shifts a single feature and re-runs the model.
 */
export default function Step6Explainability({ trainResponse, onNext }: Props) {
  const [global, setGlobal] = useState<GlobalExplainabilityResponse | null>(null)
  const [globalLoading, setGlobalLoading] = useState(true)
  const [globalError, setGlobalError] = useState<string | null>(null)

  const [patientIdx, setPatientIdx] = useState<number | null>(null)
  const [patient, setPatient] = useState<SinglePatientExplainResponse | null>(null)
  const [patientLoading, setPatientLoading] = useState(false)
  const [showAll, setShowAll] = useState(false)

  const [samplePatients, setSamplePatients] = useState<SamplePatient[]>([])

  // What-If state
  const [whatIfFeature, setWhatIfFeature] = useState('')
  const [whatIfValue, setWhatIfValue] = useState('')
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResponse | null>(null)
  const [whatIfLoading, setWhatIfLoading] = useState(false)

  useEffect(() => {
    setGlobalLoading(true)
    fetchGlobalExplainability(trainResponse.model_id)
      .then(setGlobal)
      .catch((e) => setGlobalError(e.message))
      .finally(() => setGlobalLoading(false))

    fetchSamplePatients(trainResponse.model_id)
      .then((res) => {
        setSamplePatients(res.patients)
        if (res.patients.length > 0) {
          setPatientIdx(res.patients[0].index)
        }
      })
      .catch(() => { /* silent — dropdown will be empty */ })
  }, [trainResponse.model_id])

  const handleExplainPatient = async (idx?: number) => {
    const targetIdx = idx ?? patientIdx
    if (targetIdx === null) return
    setPatientLoading(true)
    setWhatIfResult(null)
    try {
      const data = await fetchPatientExplanation(trainResponse.model_id, targetIdx)
      setPatient(data)
    } catch (e: unknown) {
      setGlobalError((e as Error).message)
    } finally {
      setPatientLoading(false)
    }
  }

  const handleWhatIf = async () => {
    if (patientIdx === null || !whatIfFeature || !whatIfValue) return
    setWhatIfLoading(true)
    try {
      const res = await fetchWhatIf({
        model_id: trainResponse.model_id,
        patient_index: patientIdx,
        feature_name: whatIfFeature,
        new_value: Number(whatIfValue),
      })
      setWhatIfResult(res)
    } catch (e: unknown) {
      setGlobalError((e as Error).message)
    } finally {
      setWhatIfLoading(false)
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

  const top5Features = global ? global.feature_importances.slice(0, 5) : []

  // Build patient attribute badges from clinical_summary if available
  const patientBadges = patient ? [
    { label: `Patient #${patientIdx}`, color: 'var(--primary)', bg: 'var(--primary-light)' },
    { label: patient.predicted_class, color: patient.predicted_probability >= 0.5 ? 'var(--danger)' : 'var(--success)', bg: patient.predicted_probability >= 0.5 ? 'var(--danger-light)' : 'var(--success-light)' },
    { label: `${(patient.predicted_probability * 100).toFixed(1)}% probability`, color: '#7a5200', bg: 'var(--warning-light)' },
  ] : []

  return (
    <div className="step-page">
      {/* Page header */}
      <div>
        <span className="step-badge">STEP 6 OF 7</span>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Eye size={22} color="var(--primary)" />
          Explainability — Why Did the Model Make This Prediction?
        </h2>
        <div className="alert alert-danger" style={{ marginTop: '0.75rem' }}>
          <AlertTriangle size={16} />
          <span>
            <strong>A model that cannot explain itself should not be trusted in clinical practice.</strong>{' '}
            Understanding why an AI made a prediction is essential before acting on it.
          </span>
        </div>
      </div>

      {/* Two-column layout: global importance + patient card */}
      <div className="grid-2">
        {/* LEFT: Global Feature Importance */}
        <div className="card">
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.25rem' }}>
            Most Important Patient Measurements (Overall) <InfoTip term="feature_importance" />
          </div>
          <div className="card-subtitle" style={{ marginBottom: '0.75rem' }}>
            Which patient measurements had the most influence across all predictions.
            Method: <strong>{global?.method ?? '…'}</strong>
          </div>

          {globalLoading && (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Computing feature importance values…
            </div>
          )}

          {globalError && (
            <div className="alert alert-danger mt-3">{globalError}</div>
          )}

          {global && !globalLoading && (
            <>
              <ResponsiveContainer width="100%" height={Math.max(300, features.length * 30)} style={{ marginTop: '0.5rem' }}>
                <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 40 }}>
                  <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={v => v.toFixed(4)} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={220} />
                  <Tooltip formatter={(v: number) => v.toFixed(5)} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {chartData.map((d, i) => (
                      <Cell key={i} fill={d.direction === 'positive' ? 'var(--primary)' : d.direction === 'negative' ? '#1e6b9c' : '#8993a4'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', fontSize: '0.78rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <span style={{ width: 12, height: 12, background: 'var(--primary)', borderRadius: 2, display: 'inline-block' }} />
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

        {/* RIGHT: Patient explanation card */}
        <div className="card">
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.25rem' }}>
            Why Was Patient #{patientIdx} Flagged?
          </div>
          <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
            Select a test patient to see why the AI made a specific prediction.
          </div>

          {/* Patient attribute badges */}
          {patient && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '0.75rem' }}>
              {patientBadges.map((b, i) => (
                <span key={i} style={{
                  padding: '0.2rem 0.6rem', borderRadius: '100px',
                  fontSize: '0.75rem', fontWeight: 600,
                  color: b.color, background: b.bg,
                  border: `1px solid ${b.color}33`,
                }}>
                  {b.label}
                </span>
              ))}
            </div>
          )}

          {patient && (
            <div className="alert alert-warning" style={{ marginBottom: '0.75rem', fontSize: '0.82rem' }}>
              <AlertTriangle size={14} />
              <span>Individual explanations reflect statistical associations only — always apply clinical judgement.</span>
            </div>
          )}

          {patient && (
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6, padding: '0.75rem', background: 'var(--background)', borderRadius: '8px' }}>
                {patient.clinical_summary}
              </div>
            </div>
          )}

          {patient && waterfallData.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
                Key Risk Factors
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                {waterfallData.filter(d => Math.abs(d.value) > 0).slice(0, 5).map((d, i) => (
                  <div key={i} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', fontSize: '0.85rem' }}>
                    <span style={{ color: d.direction === 'increases_risk' ? 'var(--danger)' : 'var(--primary)', fontWeight: 700, flexShrink: 0 }}>
                      {d.direction === 'increases_risk' ? '▲' : '▼'}
                    </span>
                    <span>{d.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div style={{ marginTop: 'auto', paddingTop: '0.5rem' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.5rem' }}>
              Single Patient Explanation
            </div>
            {patient && (
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
                Patient #{patientIdx} · Probability {(patient.predicted_probability * 100).toFixed(1)}%
              </div>
            )}
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end' }}>
              <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                <label className="form-label">Select test patient</label>
                <select
                  className="form-input"
                  value={patientIdx ?? ''}
                  onChange={e => {
                    const idx = Number(e.target.value)
                    setPatientIdx(idx)
                    handleExplainPatient(idx)
                  }}
                >
                  <option value="" disabled>Choose a patient…</option>
                  {samplePatients.map(sp => (
                    <option key={sp.index} value={sp.index}>
                      {sp.summary}
                    </option>
                  ))}
                </select>
              </div>
              <button className="btn btn-danger" onClick={() => handleExplainPatient()} disabled={patientLoading || patientIdx === null}>
                {patientLoading ? 'Explaining…' : 'Explain This Patient'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* SHAP Waterfall — full width when available */}
      {patient && waterfallData.length > 0 && (
        <div className="card">
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.25rem' }}>
            SHAP Waterfall <InfoTip term="shap_values" /> — Feature Contributions for Patient #{patientIdx}
          </div>
          <div className="card-subtitle" style={{ marginBottom: '0.75rem' }}>
            Each bar shows how much a feature pushed the prediction toward or away from risk.
          </div>
          <ResponsiveContainer width="100%" height={Math.max(250, waterfallData.length * 35)}>
            <BarChart data={waterfallData} layout="vertical" margin={{ left: 20, right: 40 }}>
              <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={v => v.toFixed(3)} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={250} />
              <Tooltip formatter={(v: number) => v.toFixed(5)} />
              <ReferenceLine x={0} stroke="var(--border)" />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {waterfallData.map((d, i) => (
                  <Cell key={i} fill={d.direction === 'increases_risk' ? 'var(--danger)' : 'var(--primary)'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <button className="btn btn-ghost btn-sm mt-2" onClick={() => setShowAll(p => !p)}>
            {showAll ? 'Show Top 8' : 'Show All Features'}
          </button>
        </div>
      )}

      {/* What-If Banner */}
      {patient && top5Features.length > 0 && (
        <div className="card" style={{ borderLeft: '4px solid var(--info, #2563eb)', background: 'var(--info-light, #eff6ff)' }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--info, #2563eb)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.25rem' }}>
            🔍 What-If Analysis <InfoTip term="what_if_analysis" />
          </div>
          <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
            Simulate changing a single clinical measurement and see how the predicted probability shifts.
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div className="form-group" style={{ flex: 1, minWidth: '180px', marginBottom: 0 }}>
              <label className="form-label">Feature</label>
              <select
                className="form-input"
                value={whatIfFeature}
                onChange={e => { setWhatIfFeature(e.target.value); setWhatIfResult(null) }}
              >
                <option value="" disabled>Select a feature…</option>
                {top5Features.map(f => (
                  <option key={f.feature_name} value={f.feature_name}>{f.clinical_name}</option>
                ))}
              </select>
            </div>
            <div className="form-group" style={{ flex: 0.5, minWidth: '120px', marginBottom: 0 }}>
              <label className="form-label">New Value</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 200"
                value={whatIfValue}
                onChange={e => { setWhatIfValue(e.target.value); setWhatIfResult(null) }}
              />
            </div>
            <button
              className="btn btn-primary"
              onClick={handleWhatIf}
              disabled={whatIfLoading || !whatIfFeature || !whatIfValue}
            >
              {whatIfLoading ? 'Simulating…' : 'Simulate'}
            </button>
          </div>
          {whatIfResult && (
            <div style={{
              marginTop: '1rem', padding: '0.75rem 1rem', borderRadius: '8px',
              background: whatIfResult.direction === 'no_change' ? 'var(--background)' : whatIfResult.direction === 'increased_risk' ? 'var(--danger-light)' : 'var(--success-light)',
              border: `1px solid ${whatIfResult.direction === 'no_change' ? 'var(--border)' : whatIfResult.direction === 'increased_risk' ? 'var(--danger)' : 'var(--success)'}`,
              fontSize: '0.9rem',
            }}>
              <strong>
                {whatIfResult.direction === 'increased_risk' ? '▲ Risk Increased' : whatIfResult.direction === 'decreased_risk' ? '▼ Risk Decreased' : '— No Change'}
              </strong>
              <div style={{ marginTop: '0.3rem' }}>
                If <strong>{top5Features.find(f => f.feature_name === whatIfResult.feature_name)?.clinical_name ?? whatIfResult.feature_name}</strong> changed
                from <strong>{whatIfResult.original_value.toFixed(2)}</strong> to <strong>{whatIfResult.new_value.toFixed(2)}</strong>,
                the predicted probability would shift
                from <strong>{(whatIfResult.original_prob * 100).toFixed(1)}%</strong> to <strong>{(whatIfResult.new_prob * 100).toFixed(1)}%</strong> ({whatIfResult.shift > 0 ? '+' : ''}{(whatIfResult.shift * 100).toFixed(1)}pp).
              </div>
            </div>
          )}
        </div>
      )}

      {/* Bottom reminder */}
      <div className="alert alert-warning">
        <span>⚕️</span>
        <div>
          <strong>Important Clinical Reminder:</strong> These explanations show associations between
          measurements and outcomes in the training data — they do not prove causation. A clinician must
          always decide whether and how to act on any AI prediction. This tool is an educational aid,
          not a diagnostic device.
        </div>
      </div>

      {/* Continue to Step 7 */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '0.5rem' }}>
        <button className="btn btn-primary btn-lg" onClick={onNext}>
          Continue to Step 7 — Ethics &amp; Bias →
        </button>
      </div>

    </div>
  )
}
