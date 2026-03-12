import React, { useEffect, useState } from 'react'
import { ChevronDown, ChevronUp, Download } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { fetchEthics, updateChecklist, downloadCertificate } from '../api/explain'
import type { EthicsResponse, Specialty, TrainResponse } from '../types'

function pct(v: number) { return `${(v * 100).toFixed(1)}%` }

function statusColor(s: string) {
  if (s === 'acceptable') return 'var(--success)'
  if (s === 'review') return '#b36800'
  return 'var(--danger)'
}

function metricCell(v: number) {
  const color = v >= 0.65 ? 'var(--success)' : v >= 0.5 ? '#b36800' : 'var(--danger)'
  return <td style={{ color, fontWeight: 600 }}>{pct(v)}</td>
}

interface Props {
  trainResponse: TrainResponse
  specialty: Specialty
  stepsCompleted: Set<number>
}

export default function Step7Ethics({ trainResponse, specialty, stepsCompleted }: Props) {
  const [ethics, setEthics] = useState<EthicsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedStudy, setExpandedStudy] = useState<string | null>(null)
  const [checklistState, setChecklistState] = useState<Record<string, boolean>>({})
  const [clinicianName, setClinicianName] = useState('')
  const [institution, setInstitution] = useState('')
  const [certLoading, setCertLoading] = useState(false)

  useEffect(() => {
    fetchEthics(trainResponse.model_id)
      .then(setEthics)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [trainResponse.model_id])

  const handleChecklistToggle = async (itemId: string, checked: boolean) => {
    const next = { ...checklistState, [itemId]: checked }
    setChecklistState(next)
    try {
      await updateChecklist(trainResponse.model_id, itemId, checked)
    } catch (_) { /* silent */ }
  }

  const allStepsDone = stepsCompleted.has(1) && stepsCompleted.has(2) &&
    stepsCompleted.has(3) && stepsCompleted.has(4) && stepsCompleted.has(6)

  const handleDownloadCert = async () => {
    setCertLoading(true)
    try {
      await downloadCertificate({
        model_id: trainResponse.model_id,
        session_id: trainResponse.session_id,
        checklist_state: checklistState,
        clinician_name: clinicianName || 'Healthcare Professional',
        institution: institution || 'Healthcare Institution',
      })
    } catch (e: unknown) {
      setError((e as Error).message)
    } finally {
      setCertLoading(false)
    }
  }

  const checkedCount = ethics
    ? ethics.eu_ai_act_items.filter(item =>
        item.pre_checked || checklistState[item.id]
      ).length
    : 0

  const reprData = ethics
    ? Object.entries(ethics.training_representation.gender.dataset).map(([k, v]) => ({
        name: k,
        Dataset: v,
        'Population Norm': ethics.training_representation.gender.population_norm[k] ?? 0,
      }))
    : []

  return (
    <div className="step-page">
      <div className="step-page-header">
        <h2>Step 7 — Ethics & Bias</h2>
        <p>Check whether the AI treats different patient groups equitably.</p>
      </div>

      {loading && (
        <div className="card text-center" style={{ padding: '2rem' }}>
          ⏳ Analysing subgroup performance…
        </div>
      )}
      {error && <div className="alert alert-danger">{error}</div>}

      {ethics && (
        <>
          {/* Bias warnings */}
          {ethics.bias_warnings.length > 0
            ? ethics.bias_warnings.map((w, i) => (
                <div key={i} className="alert alert-danger">
                  <span>🔴</span>
                  <span><strong>{w.message}</strong></span>
                </div>
              ))
            : (
              <div className="alert alert-success">
                <span>✅</span>
                <span><strong>No significant bias detected</strong> across patient subgroups. All sensitivity gaps are within 10 percentage points.</span>
              </div>
            )
          }

          {/* Subgroup table */}
          <div className="card">
            <div className="card-title">Subgroup Performance Table</div>
            <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
              Overall sensitivity: <strong>{pct(ethics.overall_sensitivity)}</strong>
            </div>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Patient Group</th>
                    <th>Sample n</th>
                    <th>Accuracy</th>
                    <th>Sensitivity</th>
                    <th>Specificity</th>
                    <th>Precision</th>
                    <th>F1</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {ethics.subgroup_metrics.map(sm => (
                    <tr key={`${sm.group_name}-${sm.group_label}`}>
                      <td className="font-semibold">{sm.group_label}</td>
                      <td>{sm.sample_size}</td>
                      {metricCell(sm.accuracy)}
                      {metricCell(sm.sensitivity)}
                      {metricCell(sm.specificity)}
                      {metricCell(sm.precision)}
                      {metricCell(sm.f1_score)}
                      <td style={{ color: statusColor(sm.status), fontWeight: 600 }}>
                        {sm.status === 'acceptable' ? '✓' : sm.status === 'review' ? '⚠' : '✗'}{' '}
                        {sm.status.replace('_', ' ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Training representation */}
          <div className="card">
            <div className="card-title">Training Data Representation</div>
            <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
              Gender distribution in training dataset vs. general population norms.
            </div>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={reprData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `${v}%`} />
                <Tooltip formatter={(v: number) => `${v}%`} />
                <Legend />
                <Bar dataKey="Dataset" fill="var(--primary)" radius={[4,4,0,0]} />
                <Bar dataKey="Population Norm" fill="var(--border)" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* EU AI Act Checklist */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div>
                <div className="card-title">EU AI Act Compliance Checklist</div>
                <div className="card-subtitle">{checkedCount} / {ethics.eu_ai_act_items.length} items completed</div>
              </div>
              {checkedCount === ethics.eu_ai_act_items.length && (
                <span className="badge badge-success">✅ All complete</span>
              )}
            </div>

            <div style={{ width: '100%', background: 'var(--border)', borderRadius: 4, height: 6, marginBottom: '1.25rem' }}>
              <div style={{
                width: `${(checkedCount / ethics.eu_ai_act_items.length) * 100}%`,
                background: 'var(--success)', borderRadius: 4, height: '100%', transition: 'width 0.3s',
              }} />
            </div>

            {ethics.eu_ai_act_items.map(item => {
              const isChecked = item.pre_checked || !!checklistState[item.id]
              return (
                <div key={item.id} style={{
                  display: 'flex', gap: '0.875rem', padding: '0.75rem 0',
                  borderBottom: '1px solid var(--border)', alignItems: 'flex-start',
                }}>
                  <input
                    type="checkbox"
                    checked={isChecked}
                    disabled={item.pre_checked}
                    onChange={e => !item.pre_checked && handleChecklistToggle(item.id, e.target.checked)}
                    style={{ marginTop: 2, accentColor: 'var(--primary)', width: 16, height: 16 }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.9rem' }}>{item.text}</div>
                    {item.pre_checked && (
                      <span className="badge badge-success" style={{ marginTop: '0.25rem', fontSize: '0.7rem' }}>
                        Auto-completed
                      </span>
                    )}
                  </div>
                  <span style={{ color: isChecked ? 'var(--success)' : 'var(--text-muted)', fontWeight: 700 }}>
                    {isChecked ? '✓' : '○'}
                  </span>
                </div>
              )
            })}
          </div>

          {/* Case studies */}
          <div className="card">
            <div className="card-title">Real-World AI Failure Case Studies</div>
            <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
              How AI tools have failed in clinical settings and what we can learn.
            </div>
            {ethics.case_studies.map(cs => (
              <div key={cs.id} style={{
                borderLeft: '4px solid var(--danger)', borderRadius: '0 8px 8px 0',
                padding: '1rem', marginBottom: '0.75rem', background: 'var(--background)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div className="font-semibold">{cs.title}</div>
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
                      <span className="badge badge-danger">{cs.specialty}</span>
                      <span className="badge badge-neutral">{cs.year}</span>
                    </div>
                  </div>
                  <button className="btn btn-ghost btn-sm" onClick={() =>
                    setExpandedStudy(expandedStudy === cs.id ? null : cs.id)
                  }>
                    {expandedStudy === cs.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>
                </div>
                {expandedStudy === cs.id && (
                  <div style={{ marginTop: '0.875rem', display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
                    <div>
                      <div className="text-xs font-semibold" style={{ color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.2rem' }}>What Happened</div>
                      <div style={{ fontSize: '0.875rem' }}>{cs.what_happened}</div>
                    </div>
                    <div>
                      <div className="text-xs font-semibold" style={{ color: 'var(--danger)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.2rem' }}>Impact</div>
                      <div style={{ fontSize: '0.875rem' }}>{cs.impact}</div>
                    </div>
                    <div>
                      <div className="text-xs font-semibold" style={{ color: 'var(--success)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.2rem' }}>Lesson Learned</div>
                      <div style={{ fontSize: '0.875rem' }}>{cs.lesson}</div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Certificate */}
          <div className="card">
            <div className="card-title">Download Summary Certificate</div>
            <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
              Generate a PDF certificate summarising your complete ML exercise.
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Your Name</label>
                <input
                  className="form-input"
                  placeholder="Dr. Jane Smith"
                  value={clinicianName}
                  onChange={e => setClinicianName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Institution</label>
                <input
                  className="form-input"
                  placeholder="City General Hospital"
                  value={institution}
                  onChange={e => setInstitution(e.target.value)}
                />
              </div>
            </div>
            <button
              className="btn btn-primary btn-lg mt-3"
              onClick={handleDownloadCert}
              disabled={certLoading || !allStepsDone}
              title={!allStepsDone ? 'Complete all 7 steps first' : ''}
            >
              <Download size={18} />
              {certLoading ? 'Generating certificate…' : 'Download Summary Certificate (PDF)'}
            </button>
            {!allStepsDone && (
              <div className="text-sm text-muted mt-2">
                Complete Steps 1–6 to unlock the certificate download.
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
