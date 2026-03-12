import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { ArrowRight, CheckCircle, Lock, Upload, X } from 'lucide-react'
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

const CHART_COLORS = ['#1e6b9c', '#00875a', '#de350b', '#ffab00', '#6554c0', '#00b8d9']

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

  return (
    <div className="step-page">
      <div className="step-page-header">
        <h2>Step 2 — Data Exploration</h2>
        <p>Choose patient data to explore, then confirm your target outcome column.</p>
      </div>

      {/* Data source cards */}
      <div className="grid-2">
        <div className="card" style={{ cursor: 'pointer' }} onClick={handleUseExample}>
          <div className="card-title">📊 Use Built-in Example Dataset</div>
          <div className="card-subtitle" style={{ marginTop: '0.5rem' }}>
            Pre-loaded data from <strong>{specialty.data_source}</strong>. Ready to use immediately.
          </div>
          <button className="btn btn-primary mt-3" disabled={loading}>
            {loading ? 'Loading…' : 'Load Example Data'}
          </button>
        </div>

        <div className="card">
          <div className="card-title">📁 Upload Your Own CSV</div>
          <div className="card-subtitle" style={{ marginTop: '0.5rem' }}>
            One row per patient, one column per measurement. Max 50 MB.
          </div>
          <div
            {...getRootProps()}
            className={`dropzone mt-3 ${isDragActive ? 'active' : ''}`}
          >
            <input {...getInputProps()} />
            {uploadedFile ? (
              <div>
                <div style={{ fontWeight: 600 }}>{uploadedFile.name}</div>
                <div className="text-sm text-muted">{(uploadedFile.size / 1024).toFixed(0)} KB</div>
              </div>
            ) : (
              <div>
                <Upload size={24} style={{ margin: '0 auto 0.5rem', color: 'var(--text-muted)' }} />
                <div>{isDragActive ? 'Drop CSV here…' : 'Drag & drop a CSV, or click to browse'}</div>
              </div>
            )}
          </div>
          {uploadedFile && (
            <button
              className="btn btn-ghost btn-sm mt-2"
              onClick={(e) => { e.stopPropagation(); onFileChange(null) }}
            >
              <X size={14} /> Remove file
            </button>
          )}
        </div>
      </div>

      {/* Privacy notice */}
      <div className="alert alert-info">
        <span>🔒</span>
        <span>
          <strong>Your data is private.</strong> If you upload your own file, it is used only within your
          current browser session and is never saved to any server or shared with anyone.
        </span>
      </div>

      {/* Exploration results */}
      {loading && (
        <div className="card text-center" style={{ padding: '2rem' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⏳</div>
          <div>Loading dataset…</div>
        </div>
      )}

      {explorationData && !loading && (
        <>
          {/* Class distribution */}
          <div className="grid-2">
            <div className="card">
              <div className="card-title">Class Distribution</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
                Target: <code style={{ background: 'var(--background)', padding: '0.1rem 0.4rem', borderRadius: 4 }}>{explorationData.target_col}</code>
                {' · '}{explorationData.row_count} patients total
              </div>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={classDistData} layout="vertical" margin={{ left: 10 }}>
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={70} />
                  <Tooltip formatter={(v: number) => [`${v} patients`]} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {classDistData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
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

            <div className="card">
              <div className="card-title">Dataset Summary</div>
              <table className="data-table mt-2">
                <tbody>
                  <tr><td className="text-muted">Total patients</td><td><strong>{explorationData.row_count}</strong></td></tr>
                  <tr><td className="text-muted">Total columns</td><td><strong>{explorationData.columns.length}</strong></td></tr>
                  <tr><td className="text-muted">Target column</td><td><code>{explorationData.target_col}</code></td></tr>
                  <tr><td className="text-muted">Outcome classes</td><td><strong>{Object.keys(explorationData.class_distribution).length}</strong></td></tr>
                  <tr><td className="text-muted">Imbalance ratio</td><td>
                    <span className={explorationData.imbalance_warning ? 'metric-amber' : 'metric-green'}>
                      {explorationData.imbalance_ratio}:1
                    </span>
                  </td></tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Column stats */}
          <div className="card">
            <div className="card-title">Column Summary</div>
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
                        <code style={{ fontSize: '0.82rem' }}>{col.name}</code>
                        {col.name === explorationData.target_col && (
                          <span className="badge badge-primary" style={{ marginLeft: 6 }}>target</span>
                        )}
                      </td>
                      <td><span className="badge badge-neutral">{col.dtype}</span></td>
                      <td>
                        <span className={col.missing_pct > 20 ? 'metric-red' : col.missing_pct > 5 ? 'metric-amber' : 'metric-green'}>
                          {col.missing_count} ({col.missing_pct}%)
                        </span>
                      </td>
                      <td>{col.unique_count}</td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {col.sample_values.slice(0, 4).map(String).join(', ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Column Mapper */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div className="card-title">Target Column Confirmation</div>
                <div className="card-subtitle">Confirm which column represents the patient outcome to predict.</div>
              </div>
              {confirmed ? (
                <div className="flex items-center gap-2" style={{ color: 'var(--success)' }}>
                  <CheckCircle size={20} />
                  <span className="font-semibold">Confirmed: {targetCol}</span>
                </div>
              ) : (
                <button className="btn btn-primary" onClick={() => setMapperOpen(true)}>
                  Open Column Mapper
                </button>
              )}
            </div>
            {!confirmed && (
              <div className="alert alert-warning mt-3">
                <Lock size={16} />
                <span>Step 3 is locked until you confirm the target column.</span>
              </div>
            )}
          </div>

          {confirmed && (
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn btn-primary" onClick={onNext}>
                Continue to Data Preparation <ArrowRight size={16} />
              </button>
            </div>
          )}
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
