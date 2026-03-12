import React, { useState, useEffect } from 'react'
import { ArrowRight, Brain, GitBranch, Layers, LineChart, Network, Zap } from 'lucide-react'
import toast from 'react-hot-toast'
import { trainModel, addToComparison } from '../api/ml'
import type { CompareEntry, ModelType, TrainResponse } from '../types'

const MODEL_CONFIGS = [
  {
    type: 'knn' as ModelType,
    name: 'K-Nearest Neighbors',
    icon: <Network size={22} />,
    desc: 'Compares a new patient to the K most similar historical patients and predicts the majority outcome.',
  },
  {
    type: 'svm' as ModelType,
    name: 'Support Vector Machine',
    icon: <Zap size={22} />,
    desc: 'Finds the clearest dividing line between patient groups. Good at separating complex patterns.',
  },
  {
    type: 'decision_tree' as ModelType,
    name: 'Decision Tree',
    icon: <GitBranch size={22} />,
    desc: 'Asks a series of yes/no questions about patient measurements — like a clinical decision pathway.',
  },
  {
    type: 'random_forest' as ModelType,
    name: 'Random Forest',
    icon: <Layers size={22} />,
    desc: 'Trains many decision trees simultaneously and takes a majority vote. More stable and accurate.',
  },
  {
    type: 'logistic_regression' as ModelType,
    name: 'Logistic Regression',
    icon: <LineChart size={22} />,
    desc: 'Calculates the probability a patient belongs to each outcome group based on weighted measurements.',
  },
  {
    type: 'naive_bayes' as ModelType,
    name: 'Naïve Bayes',
    icon: <Brain size={22} />,
    desc: 'Uses probability theory to estimate how likely each outcome is. Very fast and transparent.',
  },
]

const DEFAULT_PARAMS: Record<ModelType, Record<string, number | string>> = {
  knn: { n_neighbors: 5, metric: 'euclidean' },
  svm: { kernel: 'rbf', C: 1.0 },
  decision_tree: { max_depth: 5, criterion: 'gini' },
  random_forest: { n_estimators: 100, max_depth: 5 },
  logistic_regression: { C: 1.0, max_iter: 200 },
  naive_bayes: { var_smoothing: 1e-9 },
}

function pct(v: number) { return `${(v * 100).toFixed(1)}%` }

interface Props {
  sessionId: string
  trainResponse: TrainResponse | null
  comparedModels: CompareEntry[]
  onTrainSuccess: (r: TrainResponse) => void
  onAddToComparison: (e: CompareEntry) => void
  onNext: () => void
}

export default function Step4ModelParameters({
  sessionId,
  trainResponse,
  comparedModels,
  onTrainSuccess,
  onAddToComparison,
  onNext,
}: Props) {
  const [selectedType, setSelectedType] = useState<ModelType>('random_forest')
  const [params, setParams] = useState<Record<string, number | string>>(DEFAULT_PARAMS['random_forest'])
  const [autoRetrain, setAutoRetrain] = useState(true)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setParams(DEFAULT_PARAMS[selectedType])
  }, [selectedType])

  const handleTrain = async () => {
    setLoading(true)
    try {
      const resp = await trainModel(sessionId, selectedType, params)
      onTrainSuccess(resp)
      toast.success(`${MODEL_CONFIGS.find(m=>m.type===selectedType)?.name} trained — AUC ${pct(resp.metrics.auc_roc)}`)
    } catch (err: unknown) {
      toast.error((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handleParamChange = async (key: string, value: number | string) => {
    const newParams = { ...params, [key]: value }
    setParams(newParams)
    if (autoRetrain && !loading) {
      setLoading(true)
      try {
        const resp = await trainModel(sessionId, selectedType, newParams)
        onTrainSuccess(resp)
      } catch (_) { /* silent */ }
      finally { setLoading(false) }
    }
  }

  const handleAddToComparison = async () => {
    if (!trainResponse) return
    try {
      const resp = await addToComparison(trainResponse.model_id)
      const entry = resp.entries.find(e => e.model_id === trainResponse.model_id)
      if (entry) { onAddToComparison(entry); toast.success('Added to comparison') }
    } catch (err: unknown) {
      toast.error((err as Error).message)
    }
  }

  const renderParams = () => {
    switch (selectedType) {
      case 'knn':
        return (
          <>
            <SliderParam label="K — Number of neighbours" min={1} max={25} step={1}
              value={params.n_neighbors as number} onChange={v => handleParamChange('n_neighbors', v)} />
            <RadioParam label="Distance metric" options={['euclidean','manhattan']}
              value={params.metric as string} onChange={v => handleParamChange('metric', v)} />
          </>
        )
      case 'svm':
        return (
          <>
            <RadioParam label="Kernel" options={['rbf','linear','poly','sigmoid']}
              value={params.kernel as string} onChange={v => handleParamChange('kernel', v)} />
            <SliderParam label="C (Strictness)" min={0.01} max={10} step={0.1} decimals={2}
              value={params.C as number} onChange={v => handleParamChange('C', v)} />
          </>
        )
      case 'decision_tree':
        return (
          <>
            <SliderParam label="Maximum Depth" min={1} max={20} step={1}
              value={params.max_depth as number} onChange={v => handleParamChange('max_depth', v)} />
            <RadioParam label="Criterion" options={['gini','entropy']}
              value={params.criterion as string} onChange={v => handleParamChange('criterion', v)} />
          </>
        )
      case 'random_forest':
        return (
          <>
            <SliderParam label="Number of Trees" min={10} max={500} step={10}
              value={params.n_estimators as number} onChange={v => handleParamChange('n_estimators', v)} />
            <SliderParam label="Maximum Depth per Tree" min={1} max={20} step={1}
              value={params.max_depth as number} onChange={v => handleParamChange('max_depth', v)} />
          </>
        )
      case 'logistic_regression':
        return (
          <>
            <SliderParam label="C (Regularisation)" min={0.001} max={10} step={0.1} decimals={3}
              value={params.C as number} onChange={v => handleParamChange('C', v)} />
            <SliderParam label="Maximum Iterations" min={50} max={2000} step={50}
              value={params.max_iter as number} onChange={v => handleParamChange('max_iter', v)} />
          </>
        )
      case 'naive_bayes':
        return (
          <div className="alert alert-info">
            <span>ℹ️</span>
            <span>Naïve Bayes has minimal tuning requirements. Variance smoothing (1×10⁻⁹) is pre-set to the optimal default.</span>
          </div>
        )
    }
  }

  return (
    <div className="step-page">
      <div className="step-page-header">
        <h2>Step 4 — Model & Parameters</h2>
        <p>Choose an AI model type and tune its settings.</p>
      </div>

      {/* Model selection */}
      <div className="model-cards">
        {MODEL_CONFIGS.map((m) => (
          <button
            key={m.type}
            className={`model-card ${selectedType === m.type ? 'selected' : ''}`}
            onClick={() => setSelectedType(m.type)}
          >
            <div style={{ color: 'var(--primary)' }}>{m.icon}</div>
            <div className="model-card-name">{m.name}</div>
            <div className="model-card-desc">{m.desc}</div>
          </button>
        ))}
      </div>

      {/* Parameters */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <div className="card-title">Parameters — {MODEL_CONFIGS.find(m=>m.type===selectedType)?.name}</div>
            <div className="card-subtitle">Adjust settings using the controls below.</div>
          </div>
          <label className="toggle" style={{ gap: '0.6rem' }}>
            <input type="checkbox" checked={autoRetrain} onChange={e => setAutoRetrain(e.target.checked)} />
            <div className="toggle-track"><div className="toggle-thumb" /></div>
            <span style={{ fontSize: '0.85rem' }}>Auto-Retrain</span>
          </label>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {renderParams()}
        </div>

        <div style={{ marginTop: '1.25rem', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button className="btn btn-primary" onClick={handleTrain} disabled={loading}>
            {loading ? '⏳ Training…' : '▶ Train Model'}
          </button>
          {loading && <span className="text-sm text-muted">This may take a moment…</span>}
        </div>
      </div>

      {/* Results preview */}
      {trainResponse && (
        <>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div>
                <div className="card-title">Latest Training Results</div>
                <div className="card-subtitle" style={{ color: 'var(--text-muted)' }}>
                  {trainResponse.model_type.replace(/_/g,' ')} · {trainResponse.training_time_ms.toFixed(0)} ms
                </div>
              </div>
              <button className="btn btn-secondary btn-sm" onClick={handleAddToComparison}>
                + Add to Comparison
              </button>
            </div>
            <div className="grid-3">
              {([
                { label: 'Accuracy', v: trainResponse.metrics.accuracy, g: 0.65, a: 0.55 },
                { label: 'Sensitivity ⭐', v: trainResponse.metrics.sensitivity, g: 0.70, a: 0.50 },
                { label: 'Specificity', v: trainResponse.metrics.specificity, g: 0.65, a: 0.55 },
                { label: 'Precision', v: trainResponse.metrics.precision, g: 0.60, a: 0.50 },
                { label: 'F1 Score', v: trainResponse.metrics.f1_score, g: 0.65, a: 0.55 },
                { label: 'AUC-ROC', v: trainResponse.metrics.auc_roc, g: 0.75, a: 0.65 },
              ]).map(({ label, v, g, a }) => {
                const cls = v >= g ? 'metric-green' : v >= a ? 'metric-amber' : 'metric-red'
                const bgCls = v >= g ? 'metric-bg-green' : v >= a ? 'metric-bg-amber' : 'metric-bg-red'
                return (
                  <div key={label} className={`card ${bgCls}`} style={{ padding: '0.875rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>{label}</div>
                    <div className={`font-bold ${cls}`} style={{ fontSize: '1.5rem' }}>{pct(v)}</div>
                  </div>
                )
              })}
            </div>

            {trainResponse.metrics.low_sensitivity_warning && (
              <div className="alert alert-danger mt-3">
                <span>🚨</span>
                <span>
                  <strong>Low Sensitivity Warning:</strong> This model misses more than half of the patients who actually had the condition.
                  Try a different model or adjust parameters.
                </span>
              </div>
            )}
          </div>

          {/* Comparison table */}
          {comparedModels.length > 0 && (
            <div className="card">
              <div className="card-title">Model Comparison</div>
              <div className="data-table-wrapper mt-3">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Accuracy</th>
                      <th>Sensitivity</th>
                      <th>Specificity</th>
                      <th>AUC-ROC</th>
                      <th>Time (ms)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...comparedModels]
                      .sort((a,b) => b.metrics.auc_roc - a.metrics.auc_roc)
                      .map((e, i) => (
                        <tr key={e.model_id}>
                          <td>
                            {i === 0 && <span className="badge badge-success" style={{ marginRight: 6 }}>Best</span>}
                            {e.model_type.replace(/_/g,' ')}
                          </td>
                          <td>{pct(e.metrics.accuracy)}</td>
                          <td className={e.metrics.sensitivity >= 0.7 ? 'metric-green' : e.metrics.sensitivity >= 0.5 ? 'metric-amber' : 'metric-red'}>
                            {pct(e.metrics.sensitivity)}
                          </td>
                          <td>{pct(e.metrics.specificity)}</td>
                          <td className={e.metrics.auc_roc >= 0.75 ? 'metric-green' : e.metrics.auc_roc >= 0.65 ? 'metric-amber' : 'metric-red'}>
                            {pct(e.metrics.auc_roc)}
                          </td>
                          <td>{e.training_time_ms.toFixed(0)}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn btn-primary" onClick={onNext}>
              View Results <ArrowRight size={16} />
            </button>
          </div>
        </>
      )}
    </div>
  )
}

function SliderParam({ label, min, max, step, value, onChange, decimals = 0 }: {
  label: string; min: number; max: number; step: number; value: number;
  onChange: (v: number) => void; decimals?: number
}) {
  return (
    <div className="form-group">
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <label className="form-label">{label}</label>
        <span style={{ fontWeight: 700, color: 'var(--primary)' }}>{Number(value).toFixed(decimals)}</span>
      </div>
      <input
        type="range" className="form-range"
        min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        <span>{min}</span><span>{max}</span>
      </div>
    </div>
  )
}

function RadioParam({ label, options, value, onChange }: {
  label: string; options: string[]; value: string; onChange: (v: string) => void
}) {
  return (
    <div className="form-group">
      <label className="form-label">{label}</label>
      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
        {options.map(o => (
          <label key={o} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer', fontSize: '0.875rem' }}>
            <input type="radio" checked={value === o} onChange={() => onChange(o)} />
            <span>{o}</span>
          </label>
        ))}
      </div>
    </div>
  )
}
