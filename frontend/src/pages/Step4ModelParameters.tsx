import React, { useState, useEffect, useRef, useCallback, useMemo, Suspense } from 'react'
import { BarChart3, Brain, GitBranch, Layers, LineChart, Network, TrendingUp, X, Zap, Settings } from 'lucide-react'
import InfoTip from '../components/InfoTip'
import toast from 'react-hot-toast'
import { trainModel, addToComparison } from '../api/ml'
import type { CompareEntry, ModelType, TrainResponse } from '../types'
import ConfusionMatrixChart from '../components/charts/ConfusionMatrixChart'
import ROCCurveChart from '../components/charts/ROCCurveChart'
import PRCurveChart from '../components/charts/PRCurveChart'
import KNNScatterCanvas from '../components/charts/KNNScatterCanvas'
/** Model comparison scatter/bar viz — lazy-loaded so Step 4 opens fast. */
const ModelComparisonViz = React.lazy(() => import('../components/charts/ModelComparisonViz'))

const MODEL_CONFIGS = [
  {
    type: 'knn' as ModelType,
    name: 'KNN',
    fullName: 'K-Nearest Neighbours (KNN)',
    icon: <Network size={16} />,
    desc: 'Finds the K most similar past patients and predicts the majority outcome. Simple, interpretable, no training phase.',
  },
  {
    type: 'svm' as ModelType,
    name: 'SVM',
    fullName: 'Support Vector Machine (SVM)',
    icon: <Zap size={16} />,
    desc: 'Finds the clearest dividing line between patient groups. Good at separating complex patterns.',
  },
  {
    type: 'decision_tree' as ModelType,
    name: 'Decision Tree',
    fullName: 'Decision Tree',
    icon: <GitBranch size={16} />,
    desc: 'Asks a series of yes/no questions about patient measurements — like a clinical decision pathway.',
  },
  {
    type: 'random_forest' as ModelType,
    name: 'Random Forest',
    fullName: 'Random Forest',
    icon: <Layers size={16} />,
    desc: 'Trains many decision trees simultaneously and takes a majority vote. More stable and accurate.',
  },
  {
    type: 'logistic_regression' as ModelType,
    name: 'Logistic Reg',
    fullName: 'Logistic Regression',
    icon: <LineChart size={16} />,
    desc: 'Calculates the probability a patient belongs to each outcome group based on weighted measurements.',
  },
  {
    type: 'naive_bayes' as ModelType,
    name: 'Naive Bayes',
    fullName: 'Naïve Bayes',
    icon: <Brain size={16} />,
    desc: 'Uses probability theory to estimate how likely each outcome is. Very fast and transparent.',
  },
  {
    type: 'xgboost' as ModelType,
    name: 'XGBoost',
    fullName: 'XGBoost',
    icon: <TrendingUp size={16} />,
    desc: 'Gradient-boosted decision trees — fast, powerful, and widely used in healthcare competitions and research.',
  },
  {
    type: 'lightgbm' as ModelType,
    name: 'LightGBM',
    fullName: 'LightGBM',
    icon: <BarChart3 size={16} />,
    desc: 'Light gradient boosting — handles large datasets efficiently with lower memory usage.',
  },
]

const PARAM_HINTS: Partial<Record<ModelType, string>> = {
  knn: 'K = number of Similar Patients to Compare — lower K = more flexible but noisy; higher K = smoother but may miss patterns.',
  svm: 'C = strictness of the decision boundary — higher C fits training data more tightly but may overfit.',
  decision_tree: 'Max Depth controls how many questions the tree can ask — deeper trees can overfit.',
  random_forest: 'More trees = more stable predictions; deeper trees can overfit.',
  logistic_regression: 'C = inverse regularisation strength — lower C applies more regularisation.',
  naive_bayes: 'Naïve Bayes has minimal tuning requirements. Variance smoothing is pre-set to the optimal default.',
  xgboost: 'Lower learning rate + more trees generally improves generalisation.',
  lightgbm: 'Light gradient boosting — efficient for large datasets with low memory usage.',
}

const DEFAULT_PARAMS: Record<ModelType, Record<string, number | string>> = {
  knn: { n_neighbors: 5, metric: 'euclidean' },
  svm: { kernel: 'rbf', C: 1.0 },
  decision_tree: { max_depth: 5, criterion: 'gini' },
  random_forest: { n_estimators: 100, max_depth: 5 },
  logistic_regression: { C: 1.0, max_iter: 200 },
  naive_bayes: { var_smoothing: 1e-9 },
  xgboost: { n_estimators: 100, max_depth: 5, learning_rate: 0.1 },
  lightgbm: { n_estimators: 100, max_depth: -1, learning_rate: 0.1 },
}

function pct(v: number) { return `${(v * 100).toFixed(1)}%` }

/** Build unique display labels for compared models (e.g. "Random Forest #1 (n=100, d=5)"). */
function buildModelLabels(entries: CompareEntry[]): Map<string, string> {
  const typeCounts = new Map<string, number>()
  const typeIndices = new Map<string, number>()
  for (const e of entries) typeCounts.set(e.model_type, (typeCounts.get(e.model_type) ?? 0) + 1)
  const labels = new Map<string, string>()
  for (const e of entries) {
    const base = e.model_type.replace(/_/g, ' ')
    const count = typeCounts.get(e.model_type) ?? 1
    if (count === 1) {
      labels.set(e.model_id, base)
    } else {
      const idx = (typeIndices.get(e.model_type) ?? 0) + 1
      typeIndices.set(e.model_type, idx)
      const hints: string[] = []
      const p = e.params
      if (p.n_neighbors != null) hints.push(`k=${p.n_neighbors}`)
      if (p.kernel != null) hints.push(`${p.kernel}`)
      if (p.C != null) hints.push(`C=${p.C}`)
      if (p.n_estimators != null) hints.push(`n=${p.n_estimators}`)
      if (p.max_depth != null) hints.push(`d=${p.max_depth}`)
      if (p.learning_rate != null) hints.push(`lr=${p.learning_rate}`)
      const hint = hints.length > 0 ? ` (${hints.join(', ')})` : ''
      labels.set(e.model_id, `${base} #${idx}${hint}`)
    }
  }
  return labels
}

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
  const [tune, setTune] = useState(false)
  const [useFeatureSelection, setUseFeatureSelection] = useState(false)
  const [loading, setLoading] = useState(false)
  const [autoTrainError, setAutoTrainError] = useState<string | null>(null)

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
      if (abortRef.current) abortRef.current.abort()
    }
  }, [])

  useEffect(() => {
    const newParams = DEFAULT_PARAMS[selectedType]
    setParams(newParams)
    // Bug #10: Auto-retrain when switching model tabs (if auto-retrain is on)
    if (autoRetrain) {
      if (debounceRef.current) clearTimeout(debounceRef.current)
      debounceRef.current = setTimeout(() => {
        fireAutoRetrain(selectedType, newParams)
      }, 300)
    }
  }, [selectedType, autoRetrain]) // eslint-disable-line react-hooks/exhaustive-deps

  const resultsRef = useRef<HTMLDivElement>(null)

  const handleTrain = async () => {
    // Cancel any pending auto-retrain
    if (debounceRef.current) clearTimeout(debounceRef.current)
    if (abortRef.current) abortRef.current.abort()
    setAutoTrainError(null)
    setLoading(true)
    try {
      const resp = await trainModel(sessionId, selectedType, params, { tune, useFeatureSelection })
      onTrainSuccess(resp)
      toast.success(`${MODEL_CONFIGS.find(m=>m.type===selectedType)?.fullName} trained — AUC ${pct(resp.metrics.auc_roc)}`)
      // Bug #12: Scroll to results after training (use rAF to wait for DOM update)
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        })
      })
    } catch (err: unknown) {
      toast.error((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const fireAutoRetrain = useCallback(async (modelType: ModelType, newParams: Record<string, number | string>) => {
    // Abort any previous in-flight auto-retrain request
    if (abortRef.current) abortRef.current.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setAutoTrainError(null)
    setLoading(true)
    try {
      const resp = await trainModel(sessionId, modelType, newParams, { tune, useFeatureSelection, signal: controller.signal })
      // Only apply if this controller was not aborted (i.e. it is still the latest)
      if (!controller.signal.aborted) {
        onTrainSuccess(resp)
      }
    } catch (err: unknown) {
      // Ignore aborted requests — they are expected during rapid slider changes
      if (err instanceof Error && err.name === 'CanceledError') return
      if (err instanceof DOMException && err.name === 'AbortError') return
      if (!controller.signal.aborted) {
        setAutoTrainError((err as Error).message || 'Auto-retrain failed')
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false)
      }
    }
  }, [sessionId, onTrainSuccess, tune, useFeatureSelection])

  const handleParamChange = (key: string, value: number | string) => {
    const newParams = { ...params, [key]: value }
    setParams(newParams)
    if (autoRetrain) {
      if (debounceRef.current) clearTimeout(debounceRef.current)
      debounceRef.current = setTimeout(() => {
        fireAutoRetrain(selectedType, newParams)
      }, 300)
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
            <span aria-hidden="true">ℹ️</span>
            <span>Naïve Bayes has minimal tuning requirements. Variance smoothing (1×10⁻⁹) is pre-set to the optimal default.</span>
          </div>
        )
      case 'xgboost':
        return (
          <>
            <SliderParam label="Number of Trees" min={10} max={500} step={10}
              value={params.n_estimators as number} onChange={v => handleParamChange('n_estimators', v)} />
            <SliderParam label="Maximum Depth" min={1} max={15} step={1}
              value={params.max_depth as number} onChange={v => handleParamChange('max_depth', v)} />
            <SliderParam label="Learning Rate" min={0.01} max={0.5} step={0.01} decimals={2}
              value={params.learning_rate as number} onChange={v => handleParamChange('learning_rate', v)} />
          </>
        )
      case 'lightgbm':
        return (
          <>
            <SliderParam label="Number of Trees" min={10} max={500} step={10}
              value={params.n_estimators as number} onChange={v => handleParamChange('n_estimators', v)} />
            <SliderParam label="Maximum Depth (-1 = no limit)" min={-1} max={15} step={1}
              value={params.max_depth as number} onChange={v => handleParamChange('max_depth', v)} />
            <SliderParam label="Learning Rate" min={0.01} max={0.5} step={0.01} decimals={2}
              value={params.learning_rate as number} onChange={v => handleParamChange('learning_rate', v)} />
          </>
        )
    }
  }

  const sortedModels = useMemo(
    () => [...comparedModels].sort((a, b) => b.metrics.auc_roc - a.metrics.auc_roc),
    [comparedModels]
  )

  const modelLabels = useMemo(() => buildModelLabels(comparedModels), [comparedModels])

  const selectedConfig = MODEL_CONFIGS.find(m => m.type === selectedType)!
  const paramHint = PARAM_HINTS[selectedType]

  return (
    <div className="step-page">
      {/* Page header */}
      <div>
        <span className="step-badge">STEP 4 OF 7</span>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Settings size={22} color="var(--primary)" />
          Model Selection &amp; Parameter Tuning
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
          Choose a machine learning algorithm, adjust its settings, and train it on your prepared dataset.
        </p>
      </div>

      {/* Algorithm tab selector */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.75rem' }}>
          Choose Algorithm
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0', borderBottom: '2px solid var(--border)' }}>
          {MODEL_CONFIGS.map((m) => (
            <button
              key={m.type}
              onClick={() => setSelectedType(m.type)}
              disabled={loading}
              aria-disabled={loading}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.55rem 0.9rem',
                background: 'transparent',
                border: 'none',
                borderBottom: selectedType === m.type ? '2.5px solid var(--primary)' : '2.5px solid transparent',
                marginBottom: '-2px',
                cursor: loading ? 'not-allowed' : 'pointer',
                color: selectedType === m.type ? 'var(--primary)' : 'var(--text-secondary)',
                fontWeight: selectedType === m.type ? 700 : 500,
                fontSize: '0.82rem',
                whiteSpace: 'nowrap',
                transition: 'color 150ms ease, border-color 150ms ease',
                opacity: loading ? 0.6 : 1,
              }}
            >
              <span style={{ color: selectedType === m.type ? 'var(--primary)' : 'var(--text-muted)' }}>{m.icon}</span>
              {m.name}
            </button>
          ))}
        </div>

        {/* Selected model info box */}
        <div style={{
          marginTop: '1rem',
          borderLeft: '4px solid var(--primary)',
          background: 'var(--primary-light)',
          borderRadius: '0 8px 8px 0',
          padding: '0.875rem 1rem',
        }}>
          <div style={{ fontWeight: 700, color: 'var(--primary)', fontSize: '0.95rem' }}>
            {selectedConfig.fullName} <InfoTip term={selectedType} />
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.3rem', lineHeight: 1.5 }}>
            {selectedConfig.desc}
          </div>
          {paramHint && (
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem', fontStyle: 'italic' }}>
              {paramHint}
            </div>
          )}
        </div>
      </div>

      {/* Parallel Coordinates Visualization — full width */}
      {comparedModels.length > 0 && (
        <Suspense fallback={<div className="card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading comparison chart...</div>}>
          <ModelComparisonViz entries={comparedModels} />
        </Suspense>
      )}

      {/* Parameters + comparison side by side */}
      <div style={{ display: 'grid', gridTemplateColumns: comparedModels.length > 0 ? '1fr 1fr' : '1fr', gap: '1rem' }}>
        {/* Parameters card */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div>
              <div className="card-title">Parameters — {selectedConfig.fullName}</div>
              <div className="card-subtitle">Adjust settings using the controls below.</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'flex-end' }}>
              <label className="toggle" style={{ gap: '0.5rem' }}>
                <input type="checkbox" checked={autoRetrain} onChange={e => setAutoRetrain(e.target.checked)} />
                <div className="toggle-track"><div className="toggle-thumb" /></div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Auto-Retrain <InfoTip term="auto_retrain" /></span>
              </label>
              <label className="toggle" style={{ gap: '0.5rem' }}>
                <input type="checkbox" checked={tune} onChange={e => setTune(e.target.checked)} />
                <div className="toggle-track"><div className="toggle-thumb" /></div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Tune <InfoTip term="hyperparameter_tuning" /></span>
              </label>
              <label className="toggle" style={{ gap: '0.5rem' }}>
                <input type="checkbox" checked={useFeatureSelection} onChange={e => setUseFeatureSelection(e.target.checked)} />
                <div className="toggle-track"><div className="toggle-thumb" /></div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Feature Selection <InfoTip term="feature_selection" /></span>
              </label>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {renderParams()}
          </div>

          <div style={{ marginTop: '1.25rem', display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={handleTrain} disabled={loading} aria-busy={loading}>
              {loading ? '⏳ Training…' : tune ? '▶ Train & Tune' : '▶ Train Model'}
            </button>
            {trainResponse && (
              <button className="btn btn-secondary" onClick={handleAddToComparison} disabled={loading}>
                + Compare
              </button>
            )}
            {loading && <span className="text-sm text-muted">This may take a moment…</span>}
          </div>

          {autoTrainError && (
            <div className="alert alert-danger" role="alert" style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>Auto-retrain failed: {autoTrainError}</span>
              <button
                onClick={() => setAutoTrainError(null)}
                aria-label="Dismiss error"
                style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0.25rem' }}
              >
                <X size={16} />
              </button>
            </div>
          )}
        </div>

        {/* Model Comparison table — shown only when there are compared models */}
        {comparedModels.length > 0 && (
          <div className="card">
            <div className="card-title">Model Comparison</div>
            <div className="card-subtitle" style={{ marginBottom: '0.75rem' }}>
              Sorted by AUC-ROC (best first)
            </div>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Accuracy <InfoTip term="accuracy" /></th>
                    <th>Sensitivity <InfoTip term="sensitivity" /></th>
                    <th>Specificity <InfoTip term="specificity" /></th>
                    <th>Precision <InfoTip term="precision" /></th>
                    <th>F1 <InfoTip term="f1_score" /></th>
                    <th>MCC <InfoTip term="mcc" /></th>
                    <th>AUC-ROC <InfoTip term="auc_roc" /></th>
                    <th>Time (ms)</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedModels.map((e, i) => (
                    <tr key={e.model_id}>
                      <td>
                        {i === 0 && <span className="badge badge-success" style={{ marginRight: 6 }}>Best</span>}
                        {modelLabels.get(e.model_id) ?? e.model_type.replace(/_/g,' ')}
                      </td>
                      <td>{pct(e.metrics.accuracy)}</td>
                      <td className={e.metrics.sensitivity >= 0.7 ? 'metric-green' : e.metrics.sensitivity >= 0.5 ? 'metric-amber' : 'metric-red'}>
                        {pct(e.metrics.sensitivity)}
                      </td>
                      <td>{pct(e.metrics.specificity)}</td>
                      <td className={e.metrics.precision >= 0.6 ? 'metric-green' : e.metrics.precision >= 0.5 ? 'metric-amber' : 'metric-red'}>
                        {pct(e.metrics.precision)}
                      </td>
                      <td className={e.metrics.f1_score >= 0.65 ? 'metric-green' : e.metrics.f1_score >= 0.55 ? 'metric-amber' : 'metric-red'}>
                        {pct(e.metrics.f1_score)}
                      </td>
                      <td className={e.metrics.mcc >= 0.4 ? 'metric-green' : e.metrics.mcc >= 0.2 ? 'metric-amber' : 'metric-red'}>
                        {e.metrics.mcc.toFixed(3)}
                      </td>
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
      </div>

      {/* Results preview */}
      {trainResponse && (
        <>
          <div className="card" ref={resultsRef}>
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
            <div className="grid-3" key={trainResponse?.model_id}>
              {([
                { label: 'Accuracy', v: trainResponse.metrics.accuracy, g: 0.65, a: 0.55 },
                { label: 'Train Accuracy', v: trainResponse.metrics.train_accuracy, g: 0.65, a: 0.55 },
                { label: 'Sensitivity', starred: true, v: trainResponse.metrics.sensitivity, g: 0.70, a: 0.50 },
                { label: 'Specificity', v: trainResponse.metrics.specificity, g: 0.65, a: 0.55 },
                { label: 'Precision', v: trainResponse.metrics.precision, g: 0.60, a: 0.50 },
                { label: 'F1 Score', v: trainResponse.metrics.f1_score, g: 0.65, a: 0.55 },
                { label: 'AUC-ROC', v: trainResponse.metrics.auc_roc, g: 0.75, a: 0.65 },
                { label: 'MCC', v: trainResponse.metrics.mcc, g: 0.4, a: 0.2, raw: true },
              ] as { label: string; v: number; g: number; a: number; starred?: boolean; raw?: boolean }[]).map(({ label, v, g, a, starred, raw }) => {
                const cls = v >= g ? 'metric-green' : v >= a ? 'metric-amber' : 'metric-red'
                const bgCls = v >= g ? 'metric-bg-green' : v >= a ? 'metric-bg-amber' : 'metric-bg-red'
                return (
                  <div key={label} className={`card ${bgCls} metric-card-enter`} style={{ padding: '0.875rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>{label}{starred && <>{" "}<span aria-hidden="true">⭐</span></>}</div>
                    <div className={`font-bold ${cls}`} style={{ fontSize: '1.5rem' }}>{raw ? v.toFixed(3) : pct(v)}</div>
                  </div>
                )
              })}
            </div>

            {trainResponse.metrics.optimal_threshold !== undefined && trainResponse.metrics.optimal_threshold !== 0.5 && (
              <div style={{ marginTop: '0.75rem', padding: '0.6rem 1rem', background: 'var(--surface)', borderRadius: '8px', fontSize: '0.82rem', color: 'var(--text-secondary)', borderLeft: '3px solid var(--accent)' }}>
                <strong style={{ color: 'var(--text-primary)' }}>Threshold tuned:</strong>{' '}
                Default 0.5 → <strong style={{ color: 'var(--accent)' }}>{trainResponse.metrics.optimal_threshold.toFixed(2)}</strong>
                {' — adjusted to maximise F1 score for this class distribution.'}
              </div>
            )}

            {trainResponse.metrics.cross_val_scores.length > 0 && (
              <div className="cv-summary" style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: 'var(--surface)', borderRadius: '8px', fontSize: '0.85rem' }}>
                <strong>Cross-Validation <InfoTip term="cross_validation" /> (AUC):</strong>{' '}
                {(trainResponse.metrics.cross_val_scores.reduce((a,b)=>a+b,0) / trainResponse.metrics.cross_val_scores.length).toFixed(3)}
                {' \u00b1 '}
                {Math.sqrt(trainResponse.metrics.cross_val_scores.reduce((sum, v, _, arr) => sum + Math.pow(v - arr.reduce((a,b)=>a+b,0)/arr.length, 2), 0) / trainResponse.metrics.cross_val_scores.length).toFixed(3)}
                <span style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                  ({trainResponse.metrics.cross_val_scores.length} folds)
                </span>
              </div>
            )}

            {trainResponse.metrics.low_sensitivity_warning && (
              <div className="alert alert-danger mt-3">
                <span aria-hidden="true">🚨</span>
                <span>
                  <strong>Low Sensitivity Warning:</strong> This model misses more than half of the patients who actually had the condition.
                  Try a different model or adjust parameters.
                </span>
              </div>
            )}

            {trainResponse.metrics.overfitting_warning && (
              <div className="alert alert-warning mt-3">
                <span aria-hidden="true">⚠️</span>
                <span>
                  <strong>Overfitting Warning <InfoTip term="overfitting" />:</strong> Training accuracy ({pct(trainResponse.metrics.train_accuracy)}) is significantly higher than test accuracy ({pct(trainResponse.metrics.accuracy)}). The model may not generalise well to new patients.
                </span>
              </div>
            )}
          </div>

          {/* Diagnostic Charts — KNN Visualisation */}
          <div className="card">
            <div style={{ marginBottom: '0.25rem' }}>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                {trainResponse.model_type.replace(/_/g, ' ').toUpperCase()} Visualisation — How the Algorithm Thinks
              </div>
              <div className="card-title" style={{ marginTop: '0.2rem' }}>Diagnostic Charts</div>
            </div>
            <div className="charts-grid">
              <div className="chart-cell">
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Shows how many patients the model classified correctly vs incorrectly — each cell is a combination of actual and predicted outcome. <InfoTip term="confusion_matrix" />
                </div>
                <ConfusionMatrixChart data={trainResponse.metrics.confusion_matrix} />
              </div>
              <div className="chart-cell">
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Plots Sensitivity vs False Positive Rate at every threshold — the further the curve bows toward the top-left, the better. <InfoTip term="roc_curve" />
                </div>
                <ROCCurveChart points={trainResponse.metrics.roc_curve} auc={trainResponse.metrics.auc_roc} />
              </div>
              <div className="chart-cell">
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Plots Precision vs Recall — a higher area means the model finds true positives without generating too many false alarms. <InfoTip term="pr_curve" />
                </div>
                <PRCurveChart points={trainResponse.metrics.pr_curve} />
              </div>
              {trainResponse.knn_scatter && trainResponse.model_type === 'knn' && (
                <div className="chart-cell" style={{ gridColumn: '1 / -1' }}>
                  <KNNScatterCanvas data={trainResponse.knn_scatter} />
                </div>
              )}
            </div>
          </div>

        </>
      )}
    </div>
  )
}

const SliderParam = React.memo(function SliderParam({ label, min, max, step, value, onChange, decimals = 0 }: {
  label: string; min: number; max: number; step: number; value: number;
  onChange: (v: number) => void; decimals?: number
}) {
  const sliderId = `slider-${label.replace(/\s+/g, '-').toLowerCase()}`
  // Bug #9: Fallback to min when value is undefined during model switch
  const safeValue = value ?? min
  return (
    <div className="form-group">
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <label className="form-label" htmlFor={sliderId}>{label}</label>
        <span style={{ fontWeight: 700, color: 'var(--primary)' }}>{Number(safeValue).toFixed(decimals)}</span>
      </div>
      <input
        id={sliderId}
        type="range" className="form-range"
        min={min} max={max} step={step} value={safeValue}
        onChange={e => onChange(Number(e.target.value))}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        <span>{min}</span><span>{max}</span>
      </div>
    </div>
  )
})

const RadioParam = React.memo(function RadioParam({ label, options, value, onChange }: {
  label: string; options: string[]; value: string; onChange: (v: string) => void
}) {
  return (
    <fieldset className="form-group" style={{ border: 'none', padding: 0, margin: 0 }}>
      <legend className="form-label">{label}</legend>
      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
        {options.map(o => (
          <label key={o} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer', fontSize: '0.875rem' }}>
            <input type="radio" checked={value === o} onChange={() => onChange(o)} />
            <span>{o}</span>
          </label>
        ))}
      </div>
    </fieldset>
  )
})
