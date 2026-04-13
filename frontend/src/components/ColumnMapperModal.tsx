import React, { useState, useMemo, useCallback } from 'react'
import {
  X, Star, ChevronDown, AlertTriangle, CheckCircle, Info,
  ShieldCheck, Save, Layers,
} from 'lucide-react'
import InfoTip from './InfoTip'
import type { DataExplorationResponse, Specialty, ColumnStat } from '../types'

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export type ColumnType = 'Identifier' | 'Number' | 'Category' | 'Binary' | 'Missing'
export type ColumnRole = 'Feature' | 'Target' | 'Ignore'

export interface ColumnMapping {
  name: string
  detectedType: ColumnType
  role: ColumnRole
  sampleValue: string
}

interface Props {
  explorationData: DataExplorationResponse
  specialty: Specialty
  onSave: (targetCol: string, mappings: ColumnMapping[]) => void
  onClose: () => void
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function detectColumnType(col: ColumnStat, rowCount: number): ColumnType {
  const nameLC = col.name.toLowerCase()

  // Missing: significant missing data
  if (col.missing_count > 0 && col.missing_pct > 5) return 'Missing'

  // Identifier: high cardinality or name-based
  if (
    nameLC.includes('_id') || nameLC === 'id' || nameLC === 'index' ||
    nameLC.includes('patient') && nameLC.includes('id') ||
    (col.unique_count / rowCount > 0.85 && col.dtype === 'object')
  ) return 'Identifier'

  // Binary: exactly 2 unique values
  if (col.unique_count === 2) return 'Binary'

  // Numeric
  if (col.dtype.includes('int') || col.dtype.includes('float')) return 'Number'

  // Default
  return 'Category'
}

function defaultRole(col: ColumnStat, detectedType: ColumnType, targetCol: string): ColumnRole {
  if (col.name === targetCol) return 'Target'
  if (detectedType === 'Identifier') return 'Ignore'
  return 'Feature'
}

const MAX_TARGET_CLASSES = 20

const TYPE_BADGE_CLASS: Record<ColumnType, string> = {
  Identifier: 'mapper-type-identifier',
  Number: 'mapper-type-number',
  Category: 'mapper-type-category',
  Binary: 'mapper-type-binary',
  Missing: 'mapper-type-missing',
}

/* ------------------------------------------------------------------ */
/*  Discard Changes sub-modal                                          */
/* ------------------------------------------------------------------ */

function DiscardModal({ onKeep, onDiscard }: { onKeep: () => void; onDiscard: () => void }) {
  return (
    <div className="modal-overlay" style={{ zIndex: 1100 }} onClick={onKeep}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 420 }}>
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <div style={{
            width: 48, height: 48, borderRadius: '50%', margin: '0 auto 1rem',
            background: 'var(--danger-light)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <AlertTriangle size={24} style={{ color: 'var(--danger)' }} />
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Discard mapping changes?
          </h3>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            You have unsaved schema mapping changes.
            If you leave now, those changes will be lost.
          </p>
        </div>
        <div style={{
          display: 'flex', gap: '0.75rem', justifyContent: 'center',
          padding: '0 2rem 1.5rem',
        }}>
          <button className="btn btn-secondary" onClick={onKeep}>Keep Editing</button>
          <button className="btn btn-danger" onClick={onDiscard}>Discard Changes</button>
        </div>
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/*  Main Component                                                     */
/* ------------------------------------------------------------------ */

export default function ColumnMapperModal({ explorationData, specialty, onSave, onClose }: Props) {
  // --- Build initial mappings ---
  const initialMappings = useMemo<ColumnMapping[]>(() => {
    return explorationData.columns.map((col) => {
      const detectedType = detectColumnType(col, explorationData.row_count)
      return {
        name: col.name,
        detectedType,
        role: defaultRole(col, detectedType, explorationData.target_col),
        sampleValue: col.sample_values.length > 0 ? String(col.sample_values[0]) : '—',
      }
    })
  }, [explorationData])

  const [mappings, setMappings] = useState<ColumnMapping[]>(initialMappings)
  const [problemType, setProblemType] = useState<string>(
    specialty.target_type === 'binary' ? 'Binary Classification' : 'Multiclass Classification'
  )
  const [targetCol, setTargetCol] = useState(explorationData.target_col)
  const [validated, setValidated] = useState(false)
  const [showDiscard, setShowDiscard] = useState(false)
  const [actionBlocked, setActionBlocked] = useState(false)

  // --- Derived data ---
  const identifierCount = mappings.filter(
    (m) => m.detectedType === 'Identifier' || m.role === 'Ignore'
  ).length
  const totalMissing = explorationData.columns.reduce((s, c) => s + c.missing_count, 0)
  const totalCells = explorationData.row_count * explorationData.columns.length
  const missingPct = totalCells > 0 ? ((totalMissing / totalCells) * 100).toFixed(1) : '0'

  const hasTarget = mappings.some((m) => m.role === 'Target')
  const identifiersIgnored = mappings
    .filter((m) => m.detectedType === 'Identifier')
    .every((m) => m.role === 'Ignore')

  // Guard: target column must not be continuous / high-cardinality
  const targetStat = explorationData.columns.find((c) => c.name === targetCol)
  const targetUniqueCount = targetStat?.unique_count ?? 0
  const targetTooManyClasses = targetUniqueCount > MAX_TARGET_CLASSES

  const schemaValid = hasTarget && identifiersIgnored && !targetTooManyClasses

  const isDirty = useMemo(() => {
    return JSON.stringify(mappings) !== JSON.stringify(initialMappings)
      || targetCol !== explorationData.target_col
  }, [mappings, initialMappings, targetCol, explorationData.target_col])

  // --- Handlers ---
  const handleRoleChange = useCallback((colName: string, newRole: ColumnRole) => {
    setValidated(false)
    setActionBlocked(false)
    setMappings((prev) => {
      const next = prev.map((m) => {
        if (m.name === colName) return { ...m, role: newRole }
        // If setting a new Target, unset previous target
        if (newRole === 'Target' && m.role === 'Target' && m.name !== colName) {
          return { ...m, role: 'Feature' as ColumnRole }
        }
        return m
      })
      return next
    })
    if (newRole === 'Target') {
      setTargetCol(colName)
    }
  }, [])

  const handleTargetColChange = useCallback((newTarget: string) => {
    setValidated(false)
    setActionBlocked(false)
    setTargetCol(newTarget)
    setMappings((prev) =>
      prev.map((m) => ({
        ...m,
        role: m.name === newTarget ? 'Target' : (m.role === 'Target' ? 'Feature' : m.role),
      }))
    )
  }, [])

  const handleValidate = useCallback(() => {
    setValidated(true)
    setActionBlocked(false)
  }, [])

  const handleSave = useCallback(() => {
    if (!validated) {
      setActionBlocked(true)
      return
    }
    if (!schemaValid) {
      setActionBlocked(true)
      return
    }
    onSave(targetCol, mappings)
  }, [validated, schemaValid, targetCol, mappings, onSave])

  const handleClose = useCallback(() => {
    if (isDirty) {
      setShowDiscard(true)
    } else {
      onClose()
    }
  }, [isDirty, onClose])

  return (
    <>
      <div className="modal-overlay" onClick={handleClose}>
        <div className="modal mapper-modal" onClick={(e) => e.stopPropagation()}>
          {/* Action Blocked Banner */}
          {actionBlocked && (
            <div className="mapper-blocked-banner">
              <AlertTriangle size={16} />
              <div>
                <div><strong>Action blocked</strong></div>
                <div>Save the column mapping before proceeding to Step 3: Data Preparation.</div>
              </div>
            </div>
          )}

          {/* Header */}
          <div className="modal-header">
            <div>
              <span className="modal-title">Column Mapper &amp; Schema Validator</span>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                Configure column roles and model settings before training
              </div>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={handleClose}>
              <X size={18} />
            </button>
          </div>

          {/* 3-column body */}
          <div className="mapper-grid">
            {/* ── Left: Model Settings ── */}
            <div className="mapper-section">
              <div className="mapper-section-header">
                <Star size={16} style={{ color: 'var(--primary)' }} />
                <span>Model Settings</span>
              </div>

              <div className="form-group" style={{ marginTop: '1rem' }}>
                <label className="form-label">Problem Type <InfoTip term="classification" /></label>
                <div className="mapper-select-wrapper">
                  <select
                    className="form-select"
                    value={problemType}
                    onChange={(e) => setProblemType(e.target.value)}
                  >
                    <option>Binary Classification</option>
                    <option>Multiclass Classification</option>
                  </select>
                  <ChevronDown size={14} className="mapper-select-icon" />
                </div>
                <p style={{ marginTop: '0.4rem', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                  {problemType === 'Binary Classification'
                    ? 'The model will predict one of two outcomes for each patient — e.g. "at risk" vs "not at risk".'
                    : 'The model will predict one of several possible categories for each patient — e.g. different diagnosis types.'}
                </p>
              </div>

              <div className="form-group" style={{ marginTop: '0.75rem' }}>
                <label className="form-label">Target Column <InfoTip term="target_variable" /></label>
                <div className="mapper-select-wrapper">
                  <select
                    className="form-select"
                    value={targetCol}
                    onChange={(e) => handleTargetColChange(e.target.value)}
                  >
                    {explorationData.columns.map((c) => (
                      <option key={c.name} value={c.name}>{c.name}</option>
                    ))}
                  </select>
                  <ChevronDown size={14} className="mapper-select-icon" />
                </div>
              </div>

              {/* Schema Status */}
              <div className="mapper-schema-status">
                <div className="mapper-schema-title">Schema Status</div>
                <div className="mapper-schema-row">
                  <span>Schema Validation</span>
                  <span style={{ color: schemaValid ? 'var(--success)' : 'var(--text-secondary)', fontWeight: 600 }}>
                    {schemaValid ? 'Valid' : 'Pending'}
                  </span>
                </div>
                <div className="mapper-schema-row">
                  <span>Identifiers Detected</span>
                  <span style={{
                    color: identifierCount > 0 ? '#c57600' : 'var(--text-secondary)',
                    fontWeight: 600,
                  }}>
                    {identifierCount > 0 ? `${identifierCount} Found` : 'None'}
                  </span>
                </div>
                <div className="mapper-schema-row">
                  <span>Target Classes</span>
                  <span style={{
                    color: targetTooManyClasses ? 'var(--danger)' : 'var(--text-secondary)',
                    fontWeight: 600,
                  }}>
                    {targetUniqueCount}{targetTooManyClasses ? ` (max ${MAX_TARGET_CLASSES})` : ''}
                  </span>
                </div>
                <div className="mapper-schema-row">
                  <span>Missing Values <InfoTip term="missing_values" /></span>
                  <span style={{ fontWeight: 600 }}>{missingPct}%</span>
                </div>
              </div>

              {/* Identifier Warning */}
              {identifierCount > 0 && (
                <div className="mapper-warning">
                  <AlertTriangle size={16} style={{ color: '#c57600', flexShrink: 0, marginTop: 2 }} />
                  <div>
                    <strong>Identifier Columns Detected</strong>
                    <p style={{ margin: 0, marginTop: 4 }}>
                      Patient IDs and unique identifiers should be set to
                      &quot;Ignore&quot; to prevent data leakage <InfoTip term="data_leakage" /> in your model.
                    </p>
                  </div>
                </div>
              )}

              {/* High-cardinality target warning */}
              {targetTooManyClasses && (
                <div className="mapper-warning" style={{ borderColor: 'var(--danger)' }}>
                  <AlertTriangle size={16} style={{ color: 'var(--danger)', flexShrink: 0, marginTop: 2 }} />
                  <div>
                    <strong>Target Column Is Not Suitable</strong>
                    <p style={{ margin: 0, marginTop: 4 }}>
                      &quot;{targetCol}&quot; has {targetUniqueCount} unique values,
                      which looks like a continuous measurement — not a classification
                      label. Pick a column with at most {MAX_TARGET_CLASSES} distinct
                      classes (e.g. a binary outcome like 0/1).
                    </p>
                  </div>
                </div>
              )}

              {/* Buttons */}
              <div style={{ marginTop: 'auto', paddingTop: '1rem' }}>
                {!validated ? (
                  <>
                    <button
                      className="btn btn-primary btn-full"
                      onClick={handleValidate}
                      disabled={!schemaValid}
                    >
                      <ShieldCheck size={15} /> Validate Schema
                    </button>
                    <button
                      className="btn btn-secondary btn-full"
                      style={{ marginTop: '0.5rem' }}
                      onClick={handleSave}
                      disabled
                    >
                      <Save size={15} /> Save Mapping
                    </button>
                    <div className="mapper-hint">
                      <Info size={14} />
                      <span>Validate the schema before saving the mapping.</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="mapper-validated-badge">
                      <CheckCircle size={15} /> Schema Validated
                    </div>
                    <button
                      className="btn btn-primary btn-full"
                      style={{ marginTop: '0.5rem' }}
                      onClick={handleSave}
                    >
                      <Save size={15} /> Save Mapping
                    </button>
                    <div className="mapper-hint mapper-hint-success">
                      <CheckCircle size={14} />
                      <span>Schema validated successfully. You can now save the mapping.</span>
                    </div>
                  </>
                )}
                <button
                  className="btn btn-ghost btn-full"
                  style={{ marginTop: '0.5rem' }}
                  onClick={handleClose}
                >
                  Cancel
                </button>
              </div>
            </div>

            {/* ── Middle: Column Role Configuration ── */}
            <div className="mapper-section mapper-section-middle">
              <div className="mapper-section-header">
                <Layers size={16} style={{ color: 'var(--primary)' }} />
                <span>Column Role Configuration</span>
              </div>

              <div className="mapper-table-wrapper">
                <table className="mapper-table">
                  <thead>
                    <tr>
                      <th>Column Name</th>
                      <th>Type</th>
                      <th>Role <InfoTip term="role_feature" /></th>
                    </tr>
                  </thead>
                  <tbody>
                    {mappings.map((m) => (
                      <tr key={m.name}>
                        <td className="mapper-col-name">{m.name}</td>
                        <td>
                          <span className={`mapper-type-badge ${TYPE_BADGE_CLASS[m.detectedType]}`}>
                            {m.detectedType}
                          </span>
                        </td>
                        <td>
                          <div className="mapper-role-select-wrapper">
                            <select
                              className="mapper-role-select"
                              value={m.role}
                              onChange={(e) => handleRoleChange(m.name, e.target.value as ColumnRole)}
                            >
                              <option value="Feature">Feature</option>
                              <option value="Target">Target</option>
                              <option value="Ignore">Ignore</option>
                            </select>
                            <ChevronDown size={12} className="mapper-role-select-icon" />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* ── Right: Data Preview ── */}
            <div className="mapper-section">
              <div className="mapper-section-header">
                <div style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: 'var(--primary)', flexShrink: 0,
                }} />
                <span>Data Preview</span>
              </div>

              <div className="mapper-preview-table-wrapper">
                <table className="mapper-preview-table">
                  <thead>
                    <tr>
                      <th>Column</th>
                      <th>Example Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mappings.map((m) => (
                      <tr key={m.name}>
                        <td style={{ fontWeight: 500 }}>{m.name}</td>
                        <td style={{ color: m.sampleValue === 'null' || m.sampleValue === '—' ? 'var(--text-muted)' : 'var(--text-primary)' }}>
                          {m.sampleValue === 'null' ? <em>null</em> : m.sampleValue}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Blocking Rules */}
              <div className="mapper-blocking-rules">
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                  <Info size={16} style={{ color: '#1a6b9a', flexShrink: 0, marginTop: 2 }} />
                  <div>
                    <strong>Blocking Rules</strong>
                    <p style={{ margin: 0, marginTop: 4 }}>
                      Model training will be prevented if no target column is selected,
                      identifier columns are not set to &#39;Ignore&#39;, or the target
                      column has more than {MAX_TARGET_CLASSES} unique values
                      (continuous data).
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Discard Changes Modal */}
      {showDiscard && (
        <DiscardModal
          onKeep={() => setShowDiscard(false)}
          onDiscard={onClose}
        />
      )}
    </>
  )
}
