import React, { useState } from 'react'
import { CheckCircle, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend,
} from 'recharts'
import { prepareData } from '../api/data'
import type { DataExplorationResponse, PrepResponse, PrepSettings, Specialty } from '../types'

interface Props {
  specialty: Specialty
  targetColumn: string
  uploadedFile: File | null
  explorationData: DataExplorationResponse | null
  settings: PrepSettings
  onSettingsChange: (s: PrepSettings) => void
  onPrepSuccess: (r: PrepResponse) => void
  onNext: () => void
}

export default function Step3DataPreparation({
  specialty,
  targetColumn,
  uploadedFile,
  explorationData,
  settings,
  onSettingsChange,
  onPrepSuccess,
  onNext,
}: Props) {
  const [loading, setLoading] = useState(false)
  const [prepResponse, setPrepResponse] = useState<PrepResponse | null>(null)

  const handleApply = async () => {
    setLoading(true)
    try {
      const resp = await prepareData({
        specialtyId: specialty.id,
        targetCol: targetColumn,
        testSize: settings.test_size,
        missingStrategy: settings.missing_strategy,
        normalization: settings.normalization,
        useSmote: settings.use_smote,
        file: uploadedFile,
      })
      setPrepResponse(resp)
      onPrepSuccess(resp)
      toast.success(`Data prepared — ${resp.train_size} training / ${resp.test_size} test patients`)
    } catch (err: unknown) {
      toast.error((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const trainPct = Math.round((1 - settings.test_size) * 100)
  const testPct = Math.round(settings.test_size * 100)

  const totalPatients = explorationData?.row_count ?? 0
  const trainPatients = prepResponse
    ? prepResponse.train_size
    : Math.round(totalPatients * (1 - settings.test_size))
  const testPatients = prepResponse
    ? prepResponse.test_size
    : Math.round(totalPatients * settings.test_size)

  const beforeData = explorationData
    ? Object.entries(explorationData.class_distribution).map(([k, v]) => ({ name: k, before: v, after: 0 }))
    : []
  const afterData = prepResponse
    ? Object.entries(prepResponse.class_distribution_after).map(([k, v]) => ({ name: k, after: v }))
    : []
  const comparisonData = beforeData.map((b) => ({
    name: b.name,
    Before: b.before,
    After: afterData.find((a) => a.name === b.name)?.after ?? 0,
  }))

  // Normalization comparison from real backend data
  const normSamples = prepResponse?.norm_samples ?? []

  return (
    <div className="step-page">
      {/* Header */}
      <div className="card" style={{ background: 'var(--primary-light)', border: '1px solid rgba(26,122,76,0.15)' }}>
        <span className="step-badge">STEP 3 · DATA PREPARATION</span>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginTop: '0.5rem' }}>
          Data Preparation &amp; Preprocessing
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
          Configure how your <strong>{specialty.name}</strong> dataset is cleaned, normalised and split before training.
        </p>
      </div>

      <div className="grid-2" style={{ alignItems: 'start' }}>
        {/* LEFT — Preprocessing Controls */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <div className="card-title">Preprocessing Controls</div>
            <div className="card-subtitle">Configure all preparation settings, then apply.</div>
          </div>

          {/* Train/Test Split */}
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.75rem' }}>Train / Test Split</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <span style={{ color: 'var(--primary)', fontWeight: 700, fontSize: '0.9rem' }}>Training: {trainPct}%</span>
              <span style={{ color: 'var(--text-secondary)', fontWeight: 700, fontSize: '0.9rem' }}>Testing: {testPct}%</span>
            </div>
            <input
              type="range"
              className="form-range"
              min={60}
              max={90}
              step={5}
              value={trainPct}
              onChange={(e) =>
                onSettingsChange({ ...settings, test_size: (100 - Number(e.target.value)) / 100 })
              }
            />
            {/* Visual split bar */}
            <div style={{
              display: 'flex', height: 10, borderRadius: 6, overflow: 'hidden', marginTop: '0.5rem',
            }}>
              <div style={{ width: `${trainPct}%`, background: 'var(--primary)', transition: 'width 200ms' }} />
              <div style={{ flex: 1, background: 'var(--border)' }} />
            </div>
            {/* Patient counts */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.4rem' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                {totalPatients > 0 ? `${trainPatients.toLocaleString()} patients` : `${trainPct}%`}
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                {totalPatients > 0 ? `${testPatients.toLocaleString()} patients` : `${testPct}%`}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
              <span>60/40</span><span>70/30</span><span>80/20</span><span>90/10</span>
            </div>
          </div>

          {/* Missing Values Strategy */}
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.6rem' }}>Missing Values Strategy</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {(['median', 'mode', 'drop'] as const).map((s) => (
                <label key={s} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    name="missing"
                    checked={settings.missing_strategy === s}
                    onChange={() => onSettingsChange({ ...settings, missing_strategy: s })}
                  />
                  <span style={{ fontSize: '0.875rem' }}>
                    <strong>{s === 'median' ? 'Median' : s === 'mode' ? 'Mode' : 'Remove patients'}</strong>
                  </span>
                  {s === 'median' && <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>Recommended</span>}
                </label>
              ))}
            </div>
          </div>

          {/* Normalisation */}
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.6rem' }}>Normalisation</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {([
                { v: 'zscore', label: 'Z-score', desc: 'Relative to average and spread' },
                { v: 'minmax', label: 'Min-Max', desc: 'Rescale to 0–1 range' },
                { v: 'none', label: 'None', desc: 'Use only if you have a specific reason' },
              ] as const).map(({ v, label, desc }) => (
                <label key={v} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    name="norm"
                    checked={settings.normalization === v}
                    onChange={() => onSettingsChange({ ...settings, normalization: v })}
                  />
                  <span style={{ fontSize: '0.875rem' }}>
                    <strong>{label}</strong>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginLeft: '0.4rem' }}>— {desc}</span>
                  </span>
                  {v === 'zscore' && <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>Recommended</span>}
                </label>
              ))}
            </div>
          </div>

          {/* SMOTE Oversampling toggle — always shown if imbalance warning, otherwise shown as disabled option */}
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.6rem' }}>SMOTE Oversampling</div>
            <label className="toggle" style={{ gap: '0.75rem' }}>
              <input
                type="checkbox"
                checked={settings.use_smote}
                disabled={!explorationData?.imbalance_warning}
                onChange={(e) => onSettingsChange({ ...settings, use_smote: e.target.checked })}
              />
              <div className="toggle-track">
                <div className="toggle-thumb" />
              </div>
              <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>
                {settings.use_smote ? 'SMOTE Enabled' : 'SMOTE Disabled'}
              </span>
            </label>
            <p style={{ marginTop: '0.5rem', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {explorationData?.imbalance_warning
                ? 'Creates synthetic examples of the rare outcome in training data only — never applied to test patients.'
                : 'SMOTE is available when class imbalance is detected in your dataset.'}
            </p>
          </div>

          {/* Apply button */}
          <button
            className="btn btn-primary btn-full btn-lg"
            onClick={handleApply}
            disabled={loading}
          >
            {loading ? 'Applying…' : 'Apply Preparation Settings'}
          </button>
        </div>

        {/* RIGHT — Normalization Comparison + SMOTE Effect */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Normalization Comparison table */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: '0.25rem' }}>Normalization Comparison</div>
            <div className="card-subtitle" style={{ marginBottom: '0.75rem' }}>
              Before and after feature scaling
            </div>
            {normSamples.length > 0 && prepResponse ? (
              <div className="data-table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Feature</th>
                      <th>Before</th>
                      <th>After</th>
                    </tr>
                  </thead>
                  <tbody>
                    {normSamples.map((s) => (
                      <tr key={s.feature}>
                        <td><code style={{ fontSize: '0.8rem' }}>{s.feature}</code></td>
                        <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{s.before}</td>
                        <td style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--primary)' }}>
                          {s.after}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{
                padding: '1.5rem',
                textAlign: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.85rem',
                background: 'var(--background)',
                borderRadius: '8px',
              }}>
                {prepResponse ? 'No numeric features available.' : 'Apply settings to see normalization comparison.'}
              </div>
            )}
          </div>

          {/* Class Balance — SMOTE Effect */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: '0.25rem' }}>Class Balance — SMOTE Effect</div>
            <div className="card-subtitle" style={{ marginBottom: '0.75rem' }}>
              Training set composition before and after preparation
            </div>
            {prepResponse ? (
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={comparisonData} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={70} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Before" fill="#8993a4" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="After" fill="var(--primary)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{
                padding: '1.5rem',
                textAlign: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.85rem',
                background: 'var(--background)',
                borderRadius: '8px',
              }}>
                Apply settings to see class balance comparison.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Imbalance warning */}
      {explorationData?.imbalance_warning && (
        <div className="alert alert-warning">
          <AlertTriangle size={18} className="alert-icon" />
          <div>
            <strong>Class imbalance detected</strong> (ratio {explorationData.imbalance_ratio}:1).
            {' '}Enable SMOTE above to create synthetic minority class samples during training.
          </div>
        </div>
      )}

      {prepResponse && (
        <>
          <div className="alert alert-success">
            <CheckCircle size={18} />
            <div>
              <strong>Preparation complete.</strong>{' '}
              {prepResponse.train_size} training patients · {prepResponse.test_size} test patients ·{' '}
              {prepResponse.features_count} features
              {prepResponse.smote_applied && ' · SMOTE applied'}
            </div>
          </div>

        </>
      )}
    </div>
  )
}
