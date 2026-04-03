import React, { useEffect, useState } from 'react'
import Markdown from 'react-markdown'
import { BookOpen, Brain, ChevronDown, ChevronUp, ClipboardCheck, Download, Shield, X } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { fetchEthics, fetchInsights, updateChecklist, downloadCertificate } from '../api/explain'
import type { InsightResponse, CaseStudyData } from '../api/explain'
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
  const [checklistState, setChecklistState] = useState<Record<string, boolean>>({})
  const [clinicianName, setClinicianName] = useState('')
  const [institution, setInstitution] = useState('')
  const [certLoading, setCertLoading] = useState(false)
  const [showChecklist, setShowChecklist] = useState(false)
  const [showCaseStudies, setShowCaseStudies] = useState(false)
  const [expandedStudy, setExpandedStudy] = useState<string | null>(null)
  const [insights, setInsights] = useState<InsightResponse | null>(null)
  const [insightsLoading, setInsightsLoading] = useState(false)

  useEffect(() => {
    if (!trainResponse) return
    setLoading(true)
    fetchEthics(trainResponse.model_id)
      .then(setEthics)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))

    // Fetch LLM insights in parallel (non-blocking)
    setInsightsLoading(true)
    fetchInsights(trainResponse.model_id)
      .then(setInsights)
      .catch(() => {}) // silent — insights are optional
      .finally(() => setInsightsLoading(false))
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

          {/* AI Clinical Insight */}
          {insightsLoading && (
            <div className="card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{
                width: 18, height: 18, border: '2px solid var(--primary)', borderTopColor: 'transparent',
                borderRadius: '50%', animation: 'spin 0.8s linear infinite',
              }} />
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Generating AI clinical assessment...</span>
            </div>
          )}
          {insights?.ethics_insight?.text && !insightsLoading && (
            <div className="card ai-insight-card" style={{ borderLeft: '4px solid var(--primary)', padding: 0, overflow: 'hidden' }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '0.5rem',
                padding: '0.75rem 1.25rem',
                background: 'var(--primary-light)', borderBottom: '1px solid var(--border)',
              }}>
                <Brain size={16} color="var(--primary)" />
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--primary)' }}>
                  AI Clinical Assessment
                </span>
                <span style={{
                  fontSize: '0.65rem', fontWeight: 600, color: 'var(--text-muted)',
                  background: 'var(--surface)', padding: '0.1rem 0.4rem', borderRadius: 4, marginLeft: 'auto',
                }}>
                  {insights.ethics_insight.source === 'medgemma' ? 'MedGemma' : 'Gemini 2.5 Flash'}
                </span>
              </div>
              <div className="ai-insight-content" style={{ padding: '1rem 1.25rem' }}>
                <Markdown>{insights.ethics_insight.text}</Markdown>
              </div>
            </div>
          )}

          {/* Subgroup Performance Table */}
          <div className="card">
            <div className="card-title">Subgroup Performance Table</div>
            <div className="card-subtitle" style={{ marginBottom: '0.75rem' }}>
              Overall sensitivity: <strong>{pct(ethics.overall_sensitivity)}</strong>
            </div>

            {/* Threshold legend */}
            <div style={{
              display: 'flex', gap: '1.25rem', flexWrap: 'wrap',
              padding: '0.6rem 0.85rem', background: 'var(--background)', borderRadius: 6,
              fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '1rem',
            }}>
              <span><span style={{ color: 'var(--success)', fontWeight: 700 }}>✓ OK</span> — all metrics above 65%, sensitivity gap &le; 10pp</span>
              <span><span style={{ color: '#b36800', fontWeight: 700 }}>⚠ Review</span> — any metric below 65% or sensitivity gap &gt; 10pp</span>
              <span><span style={{ color: 'var(--danger)', fontWeight: 700 }}>✗ Action Needed</span> — sensitivity below 50% or gap &gt; 20pp</span>
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
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                          <span style={{
                            display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
                            padding: '0.15rem 0.5rem', borderRadius: '100px', fontSize: '0.75rem', fontWeight: 700,
                            color: statusColor(sm.status), background: statusBg(sm.status),
                          }}>
                            {sm.status === 'acceptable' ? '✓ OK' : sm.status === 'review' ? '⚠ Review' : '✗ Action Needed'}
                          </span>
                          {sm.status !== 'acceptable' && sm.status_reason && (
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: 1.3, maxWidth: 200 }}>
                              {sm.status_reason}
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Training Data Representation + Action Buttons row */}
          <div className="grid-2">
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

            {/* Quick-access buttons for static content */}
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="card-title">Resources &amp; Compliance</div>
              <div className="card-subtitle">
                Review regulatory compliance and learn from real-world AI failures in healthcare.
              </div>

              {/* EU AI Act button */}
              <button
                className="btn btn-outline btn-lg"
                style={{ width: '100%', justifyContent: 'space-between', padding: '1rem 1.25rem' }}
                onClick={() => setShowChecklist(true)}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <ClipboardCheck size={18} />
                  EU AI Act Compliance
                </span>
                <span className="badge" style={{
                  background: checkedCount === ethics.eu_ai_act_items.length ? 'var(--success-light)' : 'var(--background)',
                  color: checkedCount === ethics.eu_ai_act_items.length ? 'var(--success)' : 'var(--text-secondary)',
                  fontWeight: 700,
                }}>
                  {checkedCount}/{ethics.eu_ai_act_items.length}
                </span>
              </button>

              {/* Case Studies button */}
              <button
                className="btn btn-outline btn-lg"
                style={{ width: '100%', justifyContent: 'space-between', padding: '1rem 1.25rem' }}
                onClick={() => setShowCaseStudies(true)}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <BookOpen size={18} />
                  AI Failure Case Studies
                </span>
                <span className="badge badge-neutral">{ethics.case_studies.length} cases</span>
              </button>
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

      {/* ── EU AI Act Checklist Modal ── */}
      {showChecklist && ethics && (
        <div className="modal-overlay" onClick={() => setShowChecklist(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 620 }}>
            <div className="modal-header">
              <div className="modal-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ClipboardCheck size={18} color="var(--primary)" />
                EU AI Act Compliance Checklist
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowChecklist(false)} style={{ padding: '0.25rem' }}>
                <X size={18} />
              </button>
            </div>
            <div className="modal-body">
              {/* Summary bar */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0.75rem 1rem', background: 'var(--background)', borderRadius: 8, marginBottom: '1.25rem',
              }}>
                <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>
                  {checkedCount} of {ethics.eu_ai_act_items.length} requirements met
                </span>
                <div style={{ width: 120, background: 'var(--border)', borderRadius: 4, height: 8 }}>
                  <div style={{
                    width: `${(checkedCount / ethics.eu_ai_act_items.length) * 100}%`,
                    background: checkedCount === ethics.eu_ai_act_items.length ? 'var(--success)' : 'var(--primary)',
                    borderRadius: 4, height: '100%', transition: 'width 0.3s',
                  }} />
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {ethics.eu_ai_act_items.map((item) => {
                  const isChecked = item.pre_checked || !!checklistState[item.id]
                  return (
                    <div key={item.id} style={{
                      display: 'flex', gap: '0.875rem',
                      padding: '0.875rem 1rem', borderRadius: 8,
                      background: isChecked ? 'var(--success-light)' : 'var(--background)',
                      border: `1px solid ${isChecked ? 'var(--success)' : 'var(--border)'}`,
                      alignItems: 'flex-start', transition: 'all 0.2s',
                    }}>
                      {item.pre_checked ? (
                        <div style={{
                          width: 22, height: 22, borderRadius: '50%', background: 'var(--success)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          flexShrink: 0, marginTop: 1, fontSize: '0.7rem', color: 'white', fontWeight: 700,
                        }}>✓</div>
                      ) : (
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={e => handleChecklistToggle(item.id, e.target.checked)}
                          style={{ accentColor: 'var(--primary)', width: 18, height: 18, marginTop: 3, cursor: 'pointer', flexShrink: 0 }}
                        />
                      )}
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                          <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{item.text}</span>
                          {item.article && (
                            <span style={{
                              fontSize: '0.65rem', fontWeight: 700, color: 'var(--primary)',
                              background: 'var(--primary-light)', padding: '0.1rem 0.4rem', borderRadius: 4,
                            }}>{item.article}</span>
                          )}
                          {item.pre_checked && (
                            <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>Auto</span>
                          )}
                        </div>
                        {item.description && (
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                            {item.description}
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Case Studies Modal ── */}
      {showCaseStudies && ethics && (() => {
        // Use LLM-generated case studies if available, otherwise fall back to static
        const llmCases = insights?.case_studies?.case_studies
        const hasLlmCases = llmCases && llmCases.length > 0
        const displayCases: CaseStudyData[] = hasLlmCases
          ? llmCases
          : ethics.case_studies.map(cs => ({
              title: cs.title,
              specialty: cs.specialty,
              year: cs.year,
              severity: cs.severity,
              what_happened: cs.what_happened,
              impact: cs.impact,
              lesson: cs.lesson,
            }))

        return (
        <div className="modal-overlay" onClick={() => setShowCaseStudies(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 700 }}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <BookOpen size={18} color="var(--primary)" />
                <span className="modal-title">AI Failure Case Studies</span>
                {hasLlmCases && (
                  <span style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--primary)', background: 'var(--primary-light)', padding: '0.1rem 0.4rem', borderRadius: 4 }}>
                    AI-Generated
                  </span>
                )}
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowCaseStudies(false)} style={{ padding: '0.25rem' }}>
                <X size={18} />
              </button>
            </div>
            <div className="modal-body">
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
                {hasLlmCases
                  ? 'Case studies generated by AI based on your model\'s specific weaknesses and clinical domain.'
                  : 'How AI tools have failed in clinical settings and what we can learn.'}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {displayCases.map((cs, idx) => {
                  const key = `cs-${idx}`
                  const severityColor = cs.severity === 'failure' ? 'var(--danger)' : cs.severity === 'near_miss' ? '#b36800' : 'var(--success)'
                  const severityBadge = cs.severity === 'failure' ? 'badge-danger' : cs.severity === 'near_miss' ? 'badge-warning' : 'badge-success'
                  const severityLabel = cs.severity === 'failure' ? 'Failure' : cs.severity === 'near_miss' ? 'Near-Miss' : 'Prevention'
                  return (
                    <div key={key} style={{
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
                      <button
                        className="btn btn-ghost btn-sm"
                        style={{ alignSelf: 'flex-start', padding: '0.2rem 0', fontSize: '0.78rem', color: severityColor, fontWeight: 700 }}
                        onClick={() => setExpandedStudy(expandedStudy === key ? null : key)}
                      >
                        {expandedStudy === key ? (
                          <><ChevronUp size={14} /> HIDE DETAILS</>
                        ) : (
                          <><ChevronDown size={14} /> VIEW DETAILS</>
                        )}
                      </button>
                      {expandedStudy === key && (
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
                  )
                })}
              </div>
            </div>
          </div>
        </div>)
      })()}
    </div>
  )
}
