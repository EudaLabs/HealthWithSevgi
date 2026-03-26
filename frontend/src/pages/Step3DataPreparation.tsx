import React, { useState } from 'react'
import { CheckCircle, AlertTriangle, ChevronDown } from 'lucide-react'
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
        outlierHandling: settings.outlier_handling,
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
  const truncName = (s: string, max: number) => s.length > max ? s.slice(0, max) + '…' : s
  const normChartData = normSamples.map((s) => ({
    feature: truncName(s.feature, 16),
    before: s.before,
    after: Number(s.after.toFixed(3)),
  }))
  const normChartH = normChartData.length * 34 + 28

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
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Missing Values Strategy</span>
              {settings.missing_strategy === 'median' && <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>Recommended</span>}
            </div>
            <div className="mapper-select-wrapper">
              <select
                className="form-select"
                value={settings.missing_strategy}
                onChange={(e) => onSettingsChange({ ...settings, missing_strategy: e.target.value as typeof settings.missing_strategy })}
              >
                <option value="median">Median Imputation</option>
                <option value="mode">Mode Imputation</option>
                <option value="drop">Remove Patients with Missing Data</option>
              </select>
              <ChevronDown size={14} className="mapper-select-icon" />
            </div>
            <p style={{ marginTop: '0.4rem', fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {settings.missing_strategy === 'median' && 'Replaces missing numeric values with the column median — robust to outliers.'}
              {settings.missing_strategy === 'mode' && 'Replaces missing values with the most frequent value in each column.'}
              {settings.missing_strategy === 'drop' && 'Removes any patient row that contains missing values.'}
            </p>
          </div>

          {/* Normalisation */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Normalisation</span>
              {settings.normalization === 'zscore' && <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>Recommended</span>}
            </div>
            <div className="mapper-select-wrapper">
              <select
                className="form-select"
                value={settings.normalization}
                onChange={(e) => onSettingsChange({ ...settings, normalization: e.target.value as typeof settings.normalization })}
              >
                <option value="zscore">Z-Score Standardisation</option>
                <option value="minmax">Min-Max Scaling (0–1)</option>
                <option value="none">None — Keep Original Scale</option>
              </select>
              <ChevronDown size={14} className="mapper-select-icon" />
            </div>
            <p style={{ marginTop: '0.4rem', fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {settings.normalization === 'zscore' && 'Centres features around zero with unit variance — best for most ML models.'}
              {settings.normalization === 'minmax' && 'Rescales each feature to the 0–1 range based on training data min/max.'}
              {settings.normalization === 'none' && 'No scaling applied — use only if features are already on comparable scales.'}
            </p>
          </div>

          {/* SMOTE Oversampling */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>SMOTE Oversampling</span>
            </div>
            <div className="mapper-select-wrapper">
              <select
                className="form-select"
                value={settings.use_smote ? 'enabled' : 'disabled'}
                disabled={false}
                onChange={(e) => onSettingsChange({ ...settings, use_smote: e.target.value === 'enabled' })}
              >
                <option value="disabled">Disabled</option>
                <option value="enabled">Enabled — Synthesise Minority Samples</option>
              </select>
              <ChevronDown size={14} className="mapper-select-icon" />
            </div>
            <p style={{ marginTop: '0.4rem', fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {!explorationData?.imbalance_warning
                ? 'SMOTE is available when class imbalance is detected in your dataset.'
                : settings.use_smote
                  ? 'Creates synthetic examples of the rare outcome in training data only — never applied to test patients.'
                  : 'Enable to balance class distribution using synthetic minority oversampling.'}
            </p>
          </div>

          {/* Outlier Handling */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Outlier Handling</span>
            </div>
            <div className="mapper-select-wrapper">
              <select
                className="form-select"
                value={settings.outlier_handling}
                onChange={(e) => onSettingsChange({ ...settings, outlier_handling: e.target.value as typeof settings.outlier_handling })}
              >
                <option value="none">None — Keep All Values</option>
                <option value="iqr">IQR Clipping (1.5 × IQR)</option>
                <option value="zscore_clip">Z-Score Clipping (± 3 Std)</option>
              </select>
              <ChevronDown size={14} className="mapper-select-icon" />
            </div>
            <p style={{ marginTop: '0.4rem', fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {settings.outlier_handling === 'none' && 'No outlier treatment — extreme values remain unchanged.'}
              {settings.outlier_handling === 'iqr' && 'Clips values outside Q1 − 1.5×IQR / Q3 + 1.5×IQR using training statistics.'}
              {settings.outlier_handling === 'zscore_clip' && 'Clips values beyond ± 3 standard deviations from the training mean.'}
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
          {/* Normalization Comparison — Before / After bar charts */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: '0.25rem' }}>Normalization Comparison</div>
            <div className="card-subtitle" style={{ marginBottom: '0.75rem' }}>
              Before and after feature scaling
            </div>
            {normChartData.length > 0 && prepResponse ? (
              <div style={{ display: 'flex', gap: '0.25rem' }}>
                {/* Before chart — with feature labels */}
                <div style={{ flex: 1.2 }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#8993a4', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.35rem', textAlign: 'center' }}>
                    Before
                  </div>
                  <ResponsiveContainer width="100%" height={normChartH}>
                    <BarChart data={normChartData} layout="vertical" margin={{ left: 0, right: 8, top: 0, bottom: 0 }}>
                      <XAxis type="number" tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                      <YAxis type="category" dataKey="feature" tick={{ fontSize: 9.5 }} width={110} tickLine={false} axisLine={false} />
                      <Tooltip formatter={(v: number) => [v, 'Raw value']} />
                      <Bar dataKey="before" fill="#8993a4" radius={[0, 4, 4, 0]} barSize={16} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                {/* After chart — no feature labels */}
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.35rem', textAlign: 'center' }}>
                    After
                  </div>
                  <ResponsiveContainer width="100%" height={normChartH}>
                    <BarChart data={normChartData} layout="vertical" margin={{ left: 0, right: 8, top: 0, bottom: 0 }}>
                      <XAxis type="number" tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                      <YAxis type="category" dataKey="feature" hide />
                      <Tooltip formatter={(v: number) => [v, 'Normalized']} />
                      <Bar dataKey="after" fill="var(--primary)" radius={[0, 4, 4, 0]} barSize={16} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
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
