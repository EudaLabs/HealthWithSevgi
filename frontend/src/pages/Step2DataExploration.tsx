import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  CheckCircle, Lock, Upload, X, Database, Users, Layers, AlertCircle,
} from 'lucide-react'
import toast from 'react-hot-toast'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { exploreData } from '../api/data'
import ColumnMapperModal from '../components/ColumnMapperModal'
import type { ColumnMapping } from '../components/ColumnMapperModal'
import ErrorModal from '../components/ErrorModal'
import type { UploadErrorType } from '../components/ErrorModal'
import type { DataExplorationResponse, Specialty } from '../types'

interface Props {
  specialty: Specialty
  uploadedFile: File | null
  onFileChange: (file: File | null) => void
  explorationData: DataExplorationResponse | null
  onExploreSuccess: (data: DataExplorationResponse) => void
  onTargetConfirmed: (col: string) => void
  onNext: () => void
}

const CLASS_BAR_COLOR = '#c89a2d'
const MAX_FILE_SIZE = 50 * 1024 * 1024

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
  const [savedMappings, setSavedMappings] = useState<ColumnMapping[] | null>(null)

  // Error modal state
  const [uploadError, setUploadError] = useState<UploadErrorType | null>(null)

  // Bug #8: Keep refs in sync to avoid stale closures
  const specialtyRef = React.useRef(specialty)
  const onExploreSuccessRef = React.useRef(onExploreSuccess)
  specialtyRef.current = specialty
  onExploreSuccessRef.current = onExploreSuccess

  const runExplore = useCallback(
    async (file: File | null, col: string) => {
      setLoading(true)
      try {
        const data = await exploreData(specialtyRef.current.id, col, file)

        // Check for no numeric columns
        const numericCols = data.columns.filter(
          (c) => c.dtype.includes('int') || c.dtype.includes('float')
        )
        if (numericCols.length === 0) {
          setUploadError('no_numeric_columns')
          setLoading(false)
          return
        }

        // Check for dataset too small
        if (data.row_count < 10) {
          setUploadError('dataset_too_small')
          setLoading(false)
          return
        }

        onExploreSuccessRef.current(data)
        setTargetCol(col)
      } catch (err: unknown) {
        const msg = (err as Error).message || ''
        // Map backend errors to error modals
        if (msg.toLowerCase().includes('too small') || msg.toLowerCase().includes('at least 10 row')) {
          setUploadError('dataset_too_small')
        } else if (msg.toLowerCase().includes('numeric')) {
          setUploadError('no_numeric_columns')
        } else if (msg.toLowerCase().includes('unavailable') || msg.toLowerCase().includes('data_cache')) {
          setUploadError('dataset_unavailable')
        } else if (msg.toLowerCase().includes('target column')) {
          setUploadError('target_not_found')
        } else if (msg.toLowerCase().includes('parse') || msg.toLowerCase().includes('empty') || msg.toLowerCase().includes('no columns')) {
          setUploadError('empty_file')
        } else {
          toast.error(msg)
        }
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const onDrop = useCallback(
    (accepted: File[], rejected: unknown[]) => {
      // Handle rejected files
      if (rejected && (rejected as Array<unknown>).length > 0) {
        const firstReject = (rejected as Array<{ file: File; errors: Array<{ code: string }> }>)[0]
        if (firstReject?.errors?.[0]?.code === 'file-too-large') {
          setUploadError('file_too_large')
          return
        }
        if (firstReject?.errors?.[0]?.code === 'file-invalid-type') {
          setUploadError('invalid_format')
          return
        }
      }

      const file = accepted[0]
      if (!file) return

      // Double-check file type
      if (!file.name.toLowerCase().endsWith('.csv')) {
        setUploadError('invalid_format')
        return
      }

      // Double-check file size
      if (file.size > MAX_FILE_SIZE) {
        setUploadError('file_too_large')
        return
      }

      // Check for empty file
      if (file.size === 0) {
        setUploadError('empty_file')
        return
      }

      onFileChange(file)
      setConfirmed(false)
      setSavedMappings(null)
      runExplore(file, targetCol)
    },
    [onFileChange, runExplore, targetCol]
  )

  const { getRootProps, getInputProps, isDragActive, open: openFileDialog } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxSize: MAX_FILE_SIZE,
    multiple: false,
    noClick: true,
  })

  const handleUseExample = () => {
    onFileChange(null)
    setConfirmed(false)
    setSavedMappings(null)
    runExplore(null, targetCol)
  }

  const handleMapperSave = useCallback((newTargetCol: string, mappings: ColumnMapping[]) => {
    setTargetCol(newTargetCol)
    setSavedMappings(mappings)
    setConfirmed(true)
    setMapperOpen(false)
    onTargetConfirmed(newTargetCol)

    // Re-explore with new target if changed
    if (newTargetCol !== targetCol) {
      runExplore(uploadedFile, newTargetCol)
    }
  }, [targetCol, uploadedFile, runExplore, onTargetConfirmed])

  const handleErrorRetry = useCallback(() => {
    setUploadError(null)
    onFileChange(null)
    openFileDialog()
  }, [openFileDialog, onFileChange])

  // --- Derived data ---
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
    ? classValues.map(v => Math.round((v / classTotal) * 100)).join(' : ')
    : '—'

  // File info for success banner
  const fileName = uploadedFile?.name || `${specialty.id}_clinical_records.csv`
  const fileSizeStr = uploadedFile
    ? (uploadedFile.size / 1024).toFixed(0) + ' KB'
    : explorationData ? '—' : '—'
  const numericColCount = explorationData
    ? explorationData.columns.filter(c => c.dtype.includes('int') || c.dtype.includes('float')).length
    : 0

  return (
    <div className="step-page" {...getRootProps()}>
      <input {...getInputProps()} />

      {/* Header */}
      <div className="card" style={{ background: 'var(--primary-light)', border: '1px solid rgba(26,122,76,0.15)' }}>
        <span className="step-badge">STEP 2 · DATA EXPLORATION</span>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginTop: '0.5rem' }}>
          Data Exploration &amp; Understanding
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
          Upload and explore your patient dataset for <strong>{specialty.name}</strong>. Understanding your data distribution,
          quality, and patterns is crucial before building any ML model.
        </p>
      </div>

      {/* Data Source card */}
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
              {loading ? 'Loading...' : 'Use Default Dataset'}
            </button>
            <button
              className="btn btn-secondary"
              type="button"
              disabled={loading}
              onClick={openFileDialog}
            >
              <Upload size={15} />
              {uploadedFile ? uploadedFile.name : 'Upload Your CSV'}
            </button>
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
            Drop your CSV here...
          </div>
        )}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="card text-center" style={{ padding: '2rem' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>&#8987;</div>
          <div>Loading dataset...</div>
        </div>
      )}

      {explorationData && !loading && (
        <>
          {/* Dataset Success Banner or Schema Saved Banner */}
          {confirmed && savedMappings ? (
            <div className="schema-saved-banner">
              <CheckCircle size={20} style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong>Schema mapping saved successfully</strong>
                <p>
                  Target column has been configured: &ldquo;<strong>{targetCol}</strong>&rdquo;
                </p>
                <p>
                  You can now continue to Step 3: Data Preparation.{' '}
                  <a onClick={() => setMapperOpen(true)}>Edit mapping</a>
                </p>
              </div>
            </div>
          ) : (
            <div className="dataset-success-banner">
              <CheckCircle size={20} style={{ flexShrink: 0, marginTop: 2 }} />
              <div style={{ flex: 1 }}>
                <strong>Dataset successfully loaded</strong>
                <p>Open the Column Mapper for data exploration and schema mapping.</p>

                {/* Dataset Information + Dataset Preview */}
                <div className="dataset-info-grid">
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                      Dataset Information
                    </div>
                    <table className="dataset-info-table">
                      <tbody>
                        <tr><th>Dataset Name</th><td>{fileName}</td></tr>
                        {uploadedFile && <tr><th>File Size</th><td>{fileSizeStr}</td></tr>}
                        <tr><th>Rows</th><td>{totalPatients.toLocaleString()}</td></tr>
                        <tr><th>Columns</th><td>{totalFeatures}</td></tr>
                        <tr><th>Numeric Columns</th><td>{numericColCount}</td></tr>
                      </tbody>
                    </table>
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                      Dataset Preview
                    </div>
                    <table className="dataset-info-table">
                      <tbody>
                        {explorationData.columns.slice(0, 6).map((col) => (
                          <tr key={col.name}>
                            <th>{col.name}</th>
                            <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                              {col.sample_values.length > 0 ? String(col.sample_values[0]) : '—'}
                            </td>
                          </tr>
                        ))}
                        {explorationData.columns.length > 6 && (
                          <tr>
                            <th colSpan={2} style={{ textAlign: 'center', fontStyle: 'italic' }}>
                              Showing first 6 of {explorationData.columns.length} columns
                            </th>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Open Column Mapper button */}
                <div style={{ marginTop: '0.75rem', display: 'flex', justifyContent: 'flex-end' }}>
                  <button className="btn btn-primary" onClick={() => setMapperOpen(true)}>
                    Open Column Mapper
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Lock warning if not confirmed */}
          {!confirmed && (
            <div className="alert alert-warning" style={{ margin: 0 }}>
              <Lock size={16} />
              <span>Step 3 is locked until you confirm the target column via the Column Mapper.</span>
            </div>
          )}

          {/* Stats row — 4 green-circled stat cards */}
          <div className="grid-4">
            {[
              { label: 'PATIENTS', value: totalPatients.toLocaleString(), icon: <Users size={18} style={{ color: 'var(--primary)' }} /> },
              { label: 'FEATURES', value: totalFeatures.toString(), icon: <Layers size={18} style={{ color: 'var(--primary)' }} /> },
              { label: 'MISSING %', value: `${missingPct}%`, icon: <AlertCircle size={18} style={{ color: 'var(--primary)' }} /> },
              { label: 'CLASS BALANCE', value: classBalanceStr, icon: <BarChart3Icon size={18} style={{ color: 'var(--primary)' }} /> },
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

          {/* Class Balance card */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: '0.25rem' }}>Class Balance</div>
            <div className="card-subtitle" style={{ marginBottom: '0.75rem' }}>
              Distribution of target variable classes
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
                <span>&#9888;&#65039;</span>
                <span>
                  <strong>Class imbalance detected</strong> (ratio {explorationData.imbalance_ratio}:1).
                  Consider enabling SMOTE in Step 3.
                </span>
              </div>
            )}
          </div>

          {/* Patient Measurements table */}
          <div className="card">
            <div className="card-title">Patient Measurements</div>
            <div className="card-subtitle">Sample rows from the dataset — missing values are highlighted</div>
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
        <ColumnMapperModal
          explorationData={explorationData}
          specialty={specialty}
          onSave={handleMapperSave}
          onClose={() => setMapperOpen(false)}
        />
      )}

      {/* Error Modal */}
      {uploadError && (
        <ErrorModal
          errorType={uploadError}
          onRetry={handleErrorRetry}
          onClose={() => setUploadError(null)}
        />
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
