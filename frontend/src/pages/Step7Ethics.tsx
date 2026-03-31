import React, { useEffect, useState } from 'react'
import { ChevronDown, ChevronUp, Download, Shield } from 'lucide-react'
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

function statusBg(s: string) {
  if (s === 'acceptable') return 'var(--success-light)'
  if (s === 'review') return 'var(--warning-light)'
  return 'var(--danger-light)'
}

function metricCell(v: number) {
  const color = v >= 0.65 ? 'var(--success)' : v >= 0.5 ? '#b36800' : 'var(--danger)'
  return <td style={{ color, fontWeight: 600 }}>{pct(v)}</td>
}

interface Props {
  trainResponse: TrainResponse | null
  specialty: Specialty
  stepsCompleted: Set<number>
}

export default function Step7Ethics({ trainResponse, specialty, stepsCompleted }: Props) {
  const [ethics, setEthics] = useState<EthicsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedStudy, setExpandedStudy] = useState<string | null>(null)
  const [checklistState, setChecklistState] = useState<Record<string, boolean>>({})
  const [clinicianName, setClinicianName] = useState('')
  const [institution, setInstitution] = useState('')
  const [certLoading, setCertLoading] = useState(false)

  useEffect(() => {
    if (!trainResponse) return
    setLoading(true)
    fetchEthics(trainResponse.model_id)
      .then(setEthics)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [trainResponse?.model_id])

  const handleChecklistToggle = async (itemId: string, checked: boolean) => {
    const next = { ...checklistState, [itemId]: checked }
    setChecklistState(next)
    if (!trainResponse) return
    try {
      await updateChecklist(trainResponse.model_id, itemId, checked)
    } catch (_) { /* silent */ }
  }

  const allStepsDone = stepsCompleted.has(1) && stepsCompleted.has(2) &&
    stepsCompleted.has(3) && stepsCompleted.has(4) && stepsCompleted.has(6)

  const handleDownloadCert = async () => {
    if (!trainResponse) return
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
      {/* Page header */}
      <div>
        <span className="step-badge">STEP 7 · ETHICS &amp; BIAS</span>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Shield size={22} color="var(--primary)" />
          Ethics &amp; Bias Assessment
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
          Is the model fair for all patient groups? Does it perform worse for certain demographics?
        </p>
      </div>

      {!trainResponse && (
        <div className="card" style={{ textAlign: 'center', padding: '2.5rem 2rem' }}>
          <Shield size={40} style={{ color: 'var(--text-muted)', marginBottom: '0.75rem' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            Train a model in <strong>Step 4</strong> to unlock the full ethics and bias assessment.
          </p>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            The subgroup fairness audit, EU AI Act checklist, and certificate require a trained model.
          </p>
        </div>
      )}

      {loading && (
        <div className="card text-center" style={{ padding: '2rem' }}>
          Analysing subgroup performance…
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

          {/* Subgroup Performance Table */}
          <div className="card">
            <div className="card-title">Subgroup Performance Table</div>
            <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
              Overall sensitivity: <strong>{pct(ethics.overall_sensitivity)}</strong> — colour coding indicates performance relative to clinical thresholds.
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
                    <th>Fairness</th>
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
                      <td>
                        <span style={{
                          display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
                          padding: '0.15rem 0.5rem', borderRadius: '100px', fontSize: '0.75rem', fontWeight: 700,
                          color: statusColor(sm.status), background: statusBg(sm.status),
                        }}>
                          {sm.status === 'acceptable' ? '✓ OK' : sm.status === 'review' ? '⚠ Review' : '✗ Action Needed'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Two-column: EU AI Act + Training Data Representation */}
          <div className="grid-2">
            {/* EU AI Act Compliance */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <div>
                  <div className="card-title">EU AI Act Compliance</div>
                  <div className="card-subtitle">{checkedCount} / {ethics.eu_ai_act_items.length} items completed</div>
                </div>
                {checkedCount === ethics.eu_ai_act_items.length && (
                  <span className="badge badge-success">All complete</span>
                )}
              </div>

              {/* Progress bar */}
              <div style={{ width: '100%', background: 'var(--border)', borderRadius: 4, height: 8, marginBottom: '1.25rem' }}>
                <div style={{
                  width: `${(checkedCount / ethics.eu_ai_act_items.length) * 100}%`,
                  background: 'var(--success)', borderRadius: 4, height: '100%', transition: 'width 0.3s',
                }} />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                {ethics.eu_ai_act_items.map((item, idx) => {
                  const isChecked = item.pre_checked || !!checklistState[item.id]
                  return (
                    <div key={item.id} style={{
                      display: 'flex', gap: '0.875rem', padding: '0.75rem 0',
                      borderBottom: '1px solid var(--border)', alignItems: 'flex-start',
                    }}>
                      <div style={{
                        width: 22, height: 22, borderRadius: '50%', border: `2px solid ${isChecked ? 'var(--success)' : 'var(--border)'}`,
                        background: isChecked ? 'var(--success)' : 'transparent',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0, marginTop: 1, fontSize: '0.7rem', color: 'white', fontWeight: 700,
                      }}>
                        {isChecked ? '✓' : <span style={{ color: 'var(--text-muted)', fontSize: '0.65rem' }}>{idx + 1}</span>}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '0.875rem' }}>{item.text}</div>
                        {item.pre_checked && (
                          <span className="badge badge-success" style={{ marginTop: '0.25rem', fontSize: '0.7rem' }}>
                            Auto-completed
                          </span>
                        )}
                      </div>
                      {!item.pre_checked && (
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={e => handleChecklistToggle(item.id, e.target.checked)}
                          style={{ accentColor: 'var(--primary)', width: 16, height: 16, marginTop: 2, cursor: 'pointer' }}
                        />
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Training Data Representation */}
            <div className="card">
              <div className="card-title">Training Data Representation</div>
              <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
                Gender distribution in training dataset vs. general population norms.
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={reprData}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `${v}%`} />
                  <Tooltip formatter={(v: number) => `${v}%`} />
                  <Legend />
                  <Bar dataKey="Dataset" fill="var(--primary)" radius={[4,4,0,0]} />
                  <Bar dataKey="Population Norm" fill="var(--border)" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
              {ethics.representation_warnings && ethics.representation_warnings.length > 0 && (
                <div className="alert alert-warning" style={{ marginTop: '0.75rem' }}>
                  <span>⚠️</span>
                  <div>
                    <strong>Representation Gap Warning</strong>
                    {ethics.representation_warnings.map((w, i) => (
                      <div key={i} style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>{w.message}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Real-World AI Failure Case Studies */}
          <div className="card">
            <div className="card-title">Real-World AI Failure Case Studies</div>
            <div className="card-subtitle" style={{ marginBottom: '1.25rem' }}>
              How AI tools have failed in clinical settings and what we can learn.
            </div>
            <div className="grid-3">
              {ethics.case_studies.map(cs => {
                const severityColor = cs.severity === 'failure' ? 'var(--danger)' : cs.severity === 'near_miss' ? '#b36800' : 'var(--success)'
                const severityBg = cs.severity === 'failure' ? 'var(--danger-light)' : cs.severity === 'near_miss' ? 'var(--warning-light)' : 'var(--success-light)'
                const severityBadge = cs.severity === 'failure' ? 'badge-danger' : cs.severity === 'near_miss' ? 'badge-warning' : 'badge-success'
                const severityLabel = cs.severity === 'failure' ? 'Failure' : cs.severity === 'near_miss' ? 'Near-Miss' : 'Prevention'
                return (
                <div key={cs.id} style={{
                  borderLeft: `4px solid ${severityColor}`, borderRadius: '0 8px 8px 0',
                  padding: '1rem', background: 'var(--background)',
                  display: 'flex', flexDirection: 'column', gap: '0.5rem',
                }}>
                  <div>
                    <div className="font-semibold" style={{ fontSize: '0.9rem', lineHeight: 1.3 }}>{cs.title}</div>
                    <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.35rem', flexWrap: 'wrap' }}>
                      <span className={`badge ${severityBadge}`}>{severityLabel}</span>
                      <span className="badge badge-neutral">{cs.specialty}</span>
                      <span className="badge badge-neutral">{cs.year}</span>
                    </div>
                  </div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5, flex: 1 }}>
                    {cs.what_happened.length > 120 ? cs.what_happened.slice(0, 120) + '…' : cs.what_happened}
                  </div>
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ alignSelf: 'flex-start', padding: '0.2rem 0', fontSize: '0.78rem', color: severityColor, fontWeight: 700 }}
                    onClick={() => setExpandedStudy(expandedStudy === cs.id ? null : cs.id)}
                  >
                    {expandedStudy === cs.id ? (
                      <><ChevronUp size={14} /> HIDE DETAILS</>
                    ) : (
                      <><ChevronDown size={14} /> FULL DETAILS</>
                    )}
                  </button>
                  {expandedStudy === cs.id && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem', borderTop: '1px solid var(--border)', paddingTop: '0.75rem' }}>
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
              )})}
            </div>
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
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1.25rem' }}>
              <button
                className="btn btn-primary btn-lg"
                onClick={handleDownloadCert}
                disabled={certLoading || !allStepsDone}
                title={!allStepsDone ? 'Complete all 7 steps first' : ''}
              >
                <Download size={18} />
                {certLoading ? 'Generating certificate…' : 'Download Summary Certificate (PDF)'}
              </button>
            </div>
            {!allStepsDone && (
              <div className="text-sm text-muted mt-2" style={{ textAlign: 'center' }}>
                Complete Steps 1–6 to unlock the certificate download.
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
