import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { CheckCircle, Lock, Upload, X, Database, Users, Layers, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { exploreData } from '../api/data'
import type { DataExplorationResponse, Specialty } from '../types'

interface Props {
  specialty: Specialty
  uploadedFile: File | null
  onFileChange: (file: File | null) => void
  explorationData: DataExplorationResponse | null
  onExploreSuccess: (data: DataExplorationResponse, targetCol: string) => void
  onTargetConfirmed: (col: string) => void
  onNext: () => void
}

const CLASS_BAR_COLOR = '#c89a2d'

export default function Step2DataExploration({
  specialty,
  uploadedFile,
  onFileChange,
  explorationData,
  onExploreSuccess,
  onTargetConfirmed,
  onNext,
}: Props) {
  const [loading, setLoading] = useState(false)
  const [targetCol, setTargetCol] = useState(specialty.target_variable)
  const [mapperOpen, setMapperOpen] = useState(false)
  const [confirmed, setConfirmed] = useState(false)
  const [tempTarget, setTempTarget] = useState(specialty.target_variable)

  const runExplore = useCallback(
    async (file: File | null, col: string) => {
      setLoading(true)
      try {
        const data = await exploreData(specialty.id, col, file)
        onExploreSuccess(data, col)
        setTargetCol(col)
        toast.success(`Loaded ${data.row_count} patients with ${data.columns.length} features`)
      } catch (err: unknown) {
        toast.error((err as Error).message)
      } finally {
        setLoading(false)
      }
    },
    [specialty.id, onExploreSuccess]
  )

  const onDrop = useCallback(
    (accepted: File[]) => {
      const file = accepted[0]
      if (!file) return
      onFileChange(file)
      runExplore(file, targetCol)
    },
    [onFileChange, runExplore, targetCol]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxSize: 50 * 1024 * 1024,
    multiple: false,
  })

  const handleUseExample = () => {
    onFileChange(null)
    runExplore(null, targetCol)
  }

  const handleConfirmTarget = () => {
    setTargetCol(tempTarget)
    setConfirmed(true)
    setMapperOpen(false)
    onTargetConfirmed(tempTarget)
    toast.success('Target column confirmed')
    // Re-explore with new target
    runExplore(uploadedFile, tempTarget)
  }

  const classDistData = explorationData
    ? Object.entries(explorationData.class_distribution).map(([k, v]) => ({ name: k, value: v }))
    : []

  const totalPatients = explorationData?.row_count ?? 0
  const totalFeatures = explorationData ? explorationData.columns.length : 0
  const missingPct = explorationData
    ? (
        explorationData.columns.reduce((sum, c) => sum + c.missing_count, 0) /
        Math.max(1, explorationData.row_count * explorationData.columns.length) *
        100
      ).toFixed(1)
    : '—'

  const classValues = explorationData ? Object.values(explorationData.class_distribution) : []
  const classTotal = classValues.reduce((s, v) => s + v, 0)
  const classBalanceStr = classTotal > 0
    ? classValues.map(v => Math.round((v / classTotal) * 100)).join(':')
    : '—'

  return (
    <div className="step-page">
      {/* Header */}
      <div className="card" style={{ background: 'var(--primary-light)', border: '1px solid rgba(26,122,76,0.15)' }}>
        <span className="step-badge">STEP 2 · DATA EXPLORATION</span>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginTop: '0.5rem' }}>
          Data Exploration &amp; Understanding
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
          Explore the <strong>{specialty.name}</strong> dataset — inspect structure, distributions, and data quality before any preprocessing.
        </p>
      </div>

      {/* Data Source card — single row with integrated upload */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{
            width: 40, height: 40, borderRadius: '50%', flexShrink: 0,
            background: 'var(--primary-light)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Database size={20} style={{ color: 'var(--primary)' }} />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="card-title">Data Source</div>
            <div className="card-subtitle">Choose how to load your dataset</div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0, alignItems: 'center' }}>
            <button
              className="btn btn-primary"
              onClick={handleUseExample}
              disabled={loading}
            >
              {loading ? 'Loading…' : 'Use Default Dataset'}
            </button>
            <div {...getRootProps()} style={{ display: 'inline-flex' }}>
              <input {...getInputProps()} />
              <button
                className="btn btn-secondary"
                type="button"
                disabled={loading}
                onClick={(e) => e.stopPropagation()}
              >
                <Upload size={15} />
                {uploadedFile ? uploadedFile.name : 'Upload Your CSV'}
              </button>
            </div>
            {uploadedFile && (
              <button
                className="btn btn-ghost btn-sm"
                onClick={(e) => { e.stopPropagation(); onFileChange(null) }}
                title="Remove uploaded file"
              >
                <X size={14} />
              </button>
            )}
          </div>
        </div>

        {/* Dropzone hint when drag is active */}
        {isDragActive && (
          <div style={{
            marginTop: '0.75rem',
            border: '2px dashed var(--primary)',
            borderRadius: '8px',
            padding: '1rem',
            textAlign: 'center',
            background: 'var(--primary-light)',
            color: 'var(--primary)',
            fontSize: '0.9rem',
          }}>
            Drop your CSV here…
          </div>
        )}
      </div>

      {/* Open Column Mapper button */}
      {explorationData && !loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {confirmed ? (
            <div className="flex items-center gap-2" style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle size={18} />
              <span style={{ fontWeight: 600 }}>Target confirmed: {targetCol}</span>
            </div>
          ) : (
            <button className="btn btn-primary" onClick={() => setMapperOpen(true)}>
              Open Column Mapper
            </button>
          )}
          {!confirmed && (
            <div className="alert alert-warning" style={{ flex: 1, margin: 0 }}>
              <Lock size={16} />
              <span>Step 3 is locked until you confirm the target column.</span>
            </div>
          )}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="card text-center" style={{ padding: '2rem' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⏳</div>
          <div>Loading dataset…</div>
        </div>
      )}

      {explorationData && !loading && (
        <>
          {/* Stats row — 4 green-circled stat cards */}
          <div className="grid-4">
            {[
              { label: 'Patients', value: totalPatients.toLocaleString(), icon: <Users size={18} style={{ color: 'var(--primary)' }} /> },
              { label: 'Features', value: totalFeatures.toString(), icon: <Layers size={18} style={{ color: 'var(--primary)' }} /> },
              { label: 'Missing %', value: `${missingPct}%`, icon: <AlertCircle size={18} style={{ color: 'var(--primary)' }} /> },
              { label: 'Class Balance', value: classBalanceStr, icon: <BarChart3Icon size={18} style={{ color: 'var(--primary)' }} /> },
            ].map(({ label, value, icon }) => (
              <div key={label} className="card" style={{ textAlign: 'center', padding: '1rem' }}>
                <div style={{
                  width: 40, height: 40, borderRadius: '50%',
                  background: 'var(--primary-light)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 0.5rem',
                }}>
                  {icon}
                </div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-primary)' }}>{value}</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>{label}</div>
              </div>
            ))}
          </div>

          {/* Class Balance card with warm-color horizontal bars */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: '0.25rem' }}>Class Balance</div>
            <div className="card-subtitle" style={{ marginBottom: '0.75rem' }}>
              Target: <code style={{ background: 'var(--background)', padding: '0.1rem 0.4rem', borderRadius: 4 }}>{explorationData.target_col}</code>
              {' · '}{explorationData.row_count} patients total
            </div>
            <ResponsiveContainer width="100%" height={120}>
              <BarChart data={classDistData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fontSize: 11 }}
                  width={90}
                  tickFormatter={(v) => v === '0' ? 'Negative (0)' : v === '1' ? 'Positive (1)' : v}
                />
                <Tooltip formatter={(v: number) => [`${v} patients`]} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} fill={CLASS_BAR_COLOR}>
                  {classDistData.map((_, i) => (
                    <Cell key={i} fill={i === 0 ? CLASS_BAR_COLOR : '#a07820'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            {explorationData.imbalance_warning && (
              <div className="alert alert-warning mt-3">
                <span>⚠️</span>
                <span>
                  <strong>Class imbalance detected</strong> (ratio {explorationData.imbalance_ratio}:1).
                  Consider enabling SMOTE in Step 3.
                </span>
              </div>
            )}
          </div>

          {/* Patient Measurements table (formerly Column Summary) */}
          <div className="card">
            <div className="card-title">Patient Measurements</div>
            <div className="data-table-wrapper mt-3">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Column Name</th>
                    <th>Type</th>
                    <th>Missing</th>
                    <th>Unique Values</th>
                    <th>Sample Values</th>
                  </tr>
                </thead>
                <tbody>
                  {explorationData.columns.map((col) => (
                    <tr key={col.name}>
                      <td>
                        <code style={{ fontSize: '0.82rem', fontFamily: 'monospace' }}>{col.name}</code>
                        {col.name === explorationData.target_col && (
                          <span className="badge badge-primary" style={{ marginLeft: 6 }}>target</span>
                        )}
                      </td>
                      <td><span className="badge badge-neutral">{col.dtype}</span></td>
                      <td>
                        {col.missing_count > 0 ? (
                          <span style={{
                            background: 'var(--warning-light)',
                            color: '#7a5200',
                            fontWeight: 600,
                            fontSize: '0.78rem',
                            padding: '0.15rem 0.5rem',
                            borderRadius: '4px',
                            border: '1px solid var(--warning)',
                          }}>
                            Missing ({col.missing_pct}%)
                          </span>
                        ) : (
                          <span className="metric-green" style={{ fontSize: '0.85rem' }}>
                            {col.missing_count} ({col.missing_pct}%)
                          </span>
                        )}
                      </td>
                      <td>{col.unique_count}</td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                        {col.sample_values.slice(0, 4).map(String).join(', ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </>
      )}

      {/* Column Mapper Modal */}
      {mapperOpen && explorationData && (
        <div className="modal-overlay" onClick={() => setMapperOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span className="modal-title">Column Mapper</span>
              <button className="btn btn-ghost btn-sm" onClick={() => setMapperOpen(false)}>✕</button>
            </div>
            <div className="modal-body">
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '0.9rem' }}>
                Select the column that contains the patient outcome you want the AI to predict.
              </p>
              <div className="form-group">
                <label className="form-label">Target / Outcome Column</label>
                <select
                  className="form-select"
                  value={tempTarget}
                  onChange={(e) => setTempTarget(e.target.value)}
                >
                  {explorationData.columns.map((c) => (
                    <option key={c.name} value={c.name}>{c.name} ({c.dtype})</option>
                  ))}
                </select>
              </div>
              <div className="alert alert-info mt-3">
                <span>ℹ️</span>
                <span>Recommended for this specialty: <strong>{specialty.target_variable}</strong></span>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setMapperOpen(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleConfirmTarget}>
                <CheckCircle size={15} /> Save Selection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Inline icon component to avoid extra import name collision
function BarChart3Icon({ size, style }: { size: number; style?: React.CSSProperties }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={style}
    >
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  )
}
