import React, { useState } from 'react'
import { ArrowRight, CheckCircle } from 'lucide-react'
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

const CHART_COLORS = ['#1e6b9c', '#00875a', '#de350b', '#ffab00', '#6554c0']

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

  return (
    <div className="step-page">
      <div className="step-page-header">
        <h2>Step 3 — Data Preparation</h2>
        <p>Clean and prepare your patient data before training the AI model.</p>
      </div>

      <div className="grid-2">
        {/* Split slider */}
        <div className="card">
          <div className="card-title">Training / Testing Split</div>
          <div className="card-subtitle">What percentage of patients the AI learns from vs. is tested on.</div>
          <div style={{ marginTop: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: 'var(--primary)', fontWeight: 700 }}>Training: {trainPct}%</span>
              <span style={{ color: 'var(--text-secondary)', fontWeight: 700 }}>Testing: {testPct}%</span>
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
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span>60/40</span><span>70/30</span><span>80/20</span><span>90/10</span>
            </div>
          </div>
        </div>

        {/* Missing values */}
        <div className="card">
          <div className="card-title">Missing Values</div>
          <div className="card-subtitle">How to handle patients with missing measurements.</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', marginTop: '1rem' }}>
            {(['median', 'mode', 'drop'] as const).map((s) => (
              <label key={s} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="missing"
                  checked={settings.missing_strategy === s}
                  onChange={() => onSettingsChange({ ...settings, missing_strategy: s })}
                />
                <span>
                  {s === 'median' ? 'Median' : s === 'mode' ? 'Mode' : 'Remove patients'}
                </span>
                {s === 'median' && <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>Recommended</span>}
              </label>
            ))}
          </div>
        </div>

        {/* Normalisation */}
        <div className="card">
          <div className="card-title">Normalisation</div>
          <div className="card-subtitle">Rescale measurements so no single feature dominates.</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', marginTop: '1rem' }}>
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
                <span>
                  <strong>{label}</strong>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginLeft: '0.4rem' }}>— {desc}</span>
                </span>
                {v === 'zscore' && <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>Recommended</span>}
              </label>
            ))}
          </div>
        </div>

        {/* SMOTE */}
        {explorationData?.imbalance_warning && (
          <div className="card">
            <div className="card-title">Class Imbalance (SMOTE)</div>
            <div className="card-subtitle">Your dataset has imbalanced classes. SMOTE can help.</div>
            <div style={{ marginTop: '1rem' }}>
              <label className="toggle" style={{ gap: '0.75rem' }}>
                <input
                  type="checkbox"
                  checked={settings.use_smote}
                  onChange={(e) => onSettingsChange({ ...settings, use_smote: e.target.checked })}
                />
                <div className="toggle-track">
                  <div className="toggle-thumb" />
                </div>
                <span style={{ fontWeight: 600 }}>
                  {settings.use_smote ? 'SMOTE Enabled' : 'SMOTE Disabled'}
                </span>
              </label>
              <p style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Creates synthetic examples of the rare outcome in training data only — never applied to test patients.
              </p>
            </div>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <button
          className="btn btn-primary btn-lg"
          onClick={handleApply}
          disabled={loading}
          style={{ minWidth: 240 }}
        >
          {loading ? 'Applying…' : 'Apply Preparation Settings'}
        </button>
      </div>

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

          <div className="card">
            <div className="card-title">Before / After Class Distribution</div>
            <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
              Training set composition after preparation.
            </div>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={comparisonData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Before" fill="#8993a4" radius={[4,4,0,0]} />
                <Bar dataKey="After" fill="#1e6b9c" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn btn-primary" onClick={onNext}>
              Continue to Model Selection <ArrowRight size={16} />
            </button>
          </div>
        </>
      )}
    </div>
  )
}
