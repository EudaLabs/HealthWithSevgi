import React, { useState } from 'react'
import type { ModelType } from '../../../../frontend/src/types'
import type { ArenaModelConfig } from '../types/arena'
import { MODEL_LABELS } from '../types/arena'

interface Props {
  onBatchTrain: (models: ArenaModelConfig[]) => void
  isTraining: boolean
  disabled: boolean
}

const ALL_MODELS: ModelType[] = [
  'knn', 'svm', 'decision_tree', 'random_forest',
  'logistic_regression', 'naive_bayes', 'xgboost', 'lightgbm',
]

export default function RunSelector({ onBatchTrain, isTraining, disabled }: Props) {
  const [selected, setSelected] = useState<Set<ModelType>>(new Set())
  const [tune, setTune] = useState(false)
  const [trainingCount, setTrainingCount] = useState(0)

  const toggle = (model: ModelType) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(model)) next.delete(model)
      else next.add(model)
      return next
    })
  }

  const selectAll = () => setSelected(new Set(ALL_MODELS))
  const clearAll = () => setSelected(new Set())

  const handleTrain = () => {
    const models: ArenaModelConfig[] = Array.from(selected).map((model_type) => ({
      model_type,
      params: {},
      tune,
    }))
    setTrainingCount(models.length)
    onBatchTrain(models)
    setSelected(new Set())  // clear so user doesn't accidentally re-train
  }

  return (
    <div className="arena-selector">
      <div className="arena-selector-header">
        <h3 className="arena-section-title">Select Models to Train</h3>
        <div className="arena-selector-actions">
          <button className="btn btn-ghost btn-sm" onClick={selectAll}>Select All</button>
          <button className="btn btn-ghost btn-sm" onClick={clearAll}>Clear</button>
        </div>
      </div>

      <div className="arena-model-grid">
        {ALL_MODELS.map((model) => (
          <button
            key={model}
            className={`arena-model-chip ${selected.has(model) ? 'active' : ''}`}
            onClick={() => toggle(model)}
            disabled={disabled || isTraining}
          >
            <span className="arena-chip-check">{selected.has(model) ? '\u2713' : ''}</span>
            {MODEL_LABELS[model]}
          </button>
        ))}
      </div>

      <div className="arena-selector-footer">
        <label className="arena-toggle">
          <input type="checkbox" checked={tune} onChange={(e) => setTune(e.target.checked)} />
          <span>Auto-tune hyperparameters</span>
        </label>

        <button
          className="btn btn-primary"
          onClick={handleTrain}
          disabled={selected.size === 0 || isTraining || disabled}
        >
          {isTraining ? (
            <span className="arena-spinner">Training {trainingCount} models...</span>
          ) : (
            `Train ${selected.size} Model${selected.size !== 1 ? 's' : ''}`
          )}
        </button>
      </div>
    </div>
  )
}
