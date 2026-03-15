import React, { useState, useCallback, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchSpecialties } from './api/specialties'
import NavBar from './components/NavBar'
import WizardProgress from './components/WizardProgress'
import Step1ClinicalContext from './pages/Step1ClinicalContext'
import Step2DataExploration from './pages/Step2DataExploration'
import Step3DataPreparation from './pages/Step3DataPreparation'
import Step4ModelParameters from './pages/Step4ModelParameters'
const Step5Results = React.lazy(() => import('./pages/Step5Results'))
const Step6Explainability = React.lazy(() => import('./pages/Step6Explainability'))
import Step7Ethics from './pages/Step7Ethics'
import type { WizardState, Specialty, CompareEntry } from './types'

const STEP_NAMES = [
  '', 'Clinical Context', 'Data Exploration', 'Data Preparation',
  'Model & Parameters', 'Results', 'Explainability', 'Ethics & Bias'
]

function BottomNav({ currentStep, onPrev, onNext }: { currentStep: number; onPrev: () => void; onNext: () => void }) {
  return (
    <div className="bottom-nav">
      <div className="bottom-nav-left">
        <span className="step-badge">Step {currentStep} / 7</span>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginLeft: '0.5rem' }}>
          {STEP_NAMES[currentStep]}
        </span>
      </div>
      <div className="bottom-nav-right">
        <button className="btn btn-secondary" onClick={onPrev} disabled={currentStep <= 1}>
          ← Previous
        </button>
        <button className="btn btn-primary" onClick={onNext} disabled={currentStep >= 7}>
          Next Step →
        </button>
      </div>
    </div>
  )
}

const createDefaultState = (): WizardState => ({
  specialty: null,
  explorationData: null,
  targetColumn: null,
  uploadedFile: null,
  prepResponse: null,
  prepSettings: {
    test_size: 0.2,
    missing_strategy: 'median',
    normalization: 'zscore',
    use_smote: false,
  },
  trainResponse: null,
  comparedModels: [],
  stepsCompleted: new Set(),
  currentStep: 1,
})

export default function App() {
  const [state, setState] = useState<WizardState>(createDefaultState)
  const [glossaryOpen, setGlossaryOpen] = useState(false)
  const [confirmSwitch, setConfirmSwitch] = useState<Specialty | null>(null)

  const { data: specialties = [], isLoading: specialtiesLoading } = useQuery({
    queryKey: ['specialties'],
    queryFn: fetchSpecialties,
  })

  useEffect(() => {
    if (specialties.length > 0 && !state.specialty) {
      setState(prev => ({ ...prev, specialty: specialties[0], currentStep: 1 }))
    }
  }, [specialties, state.specialty])

  const update = useCallback((patch: Partial<WizardState>) => {
    setState((prev) => ({ ...prev, ...patch }))
  }, [])

  const completeStep = useCallback((step: number) => {
    setState((prev) => ({
      ...prev,
      stepsCompleted: new Set([...prev.stepsCompleted, step]),
    }))
  }, [])

  const goToStep = useCallback((step: number) => {
    setState((prev) => ({ ...prev, currentStep: step }))
  }, [])

  const handleSpecialtySelect = useCallback(
    (specialty: Specialty) => {
      setState({ ...createDefaultState(), specialty, currentStep: 1 })
    },
    []
  )

  const handleResetSpecialty = useCallback(() => {
    setState(createDefaultState())
  }, [])

  const handleSpecialtyChangeFromChip = useCallback((s: Specialty) => {
    if (state.specialty?.id === s.id) return
    if (state.stepsCompleted.size > 0) {
      setConfirmSwitch(s)
    } else {
      handleSpecialtySelect(s)
    }
  }, [state.specialty, state.stepsCompleted, handleSpecialtySelect])

  const addComparedModel = useCallback((entry: CompareEntry) => {
    setState((prev) => {
      const existing = prev.comparedModels.filter((e) => e.model_id !== entry.model_id)
      return { ...prev, comparedModels: [...existing, entry] }
    })
  }, [])

  const renderStep = () => {
    if (specialtiesLoading || !state.specialty) {
      return (
        <div style={{ padding: '2rem' }}>
          <div style={{ height: '2rem', width: '40%', marginBottom: '1rem', borderRadius: '0.5rem', background: 'var(--bg-secondary)', animation: 'pulse 1.5s ease-in-out infinite' }} />
          <div style={{ height: '1rem', width: '60%', marginBottom: '0.5rem', borderRadius: '0.5rem', background: 'var(--bg-secondary)', animation: 'pulse 1.5s ease-in-out infinite' }} />
          <div style={{ height: '1rem', width: '50%', borderRadius: '0.5rem', background: 'var(--bg-secondary)', animation: 'pulse 1.5s ease-in-out infinite' }} />
        </div>
      )
    }

    switch (state.currentStep) {
      case 1:
        return (
          <Step1ClinicalContext
            specialty={state.specialty!}
            onNext={() => { completeStep(1); goToStep(2) }}
          />
        )
      case 2:
        return (
          <Step2DataExploration
            specialty={state.specialty!}
            uploadedFile={state.uploadedFile}
            onFileChange={(file) => update({ uploadedFile: file })}
            explorationData={state.explorationData}
            onExploreSuccess={(data, targetCol) => update({ explorationData: data, targetColumn: targetCol })}
            onTargetConfirmed={(col) => { update({ targetColumn: col }); completeStep(2) }}
            onNext={() => goToStep(3)}
          />
        )
      case 3:
        return (
          <Step3DataPreparation
            specialty={state.specialty!}
            targetColumn={state.targetColumn!}
            uploadedFile={state.uploadedFile}
            explorationData={state.explorationData}
            settings={state.prepSettings}
            onSettingsChange={(s) => update({ prepSettings: s })}
            onPrepSuccess={(r) => { update({ prepResponse: r }); completeStep(3) }}
            onNext={() => goToStep(4)}
          />
        )
      case 4:
        if (!state.prepResponse) {
          return (
            <div className="card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
              <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                Please complete Data Preparation (Step 3) first.
              </p>
              <button className="btn btn-primary" onClick={() => goToStep(3)}>
                Go to Step 3
              </button>
            </div>
          )
        }
        return (
          <Step4ModelParameters
            sessionId={state.prepResponse.session_id}
            trainResponse={state.trainResponse}
            comparedModels={state.comparedModels}
            onTrainSuccess={(r) => { update({ trainResponse: r }); completeStep(4) }}
            onAddToComparison={addComparedModel}
            onNext={() => goToStep(5)}
          />
        )
      case 5:
        return (
          <Step5Results
            trainResponse={state.trainResponse!}
            onNext={() => goToStep(6)}
          />
        )
      case 6:
        return (
          <Step6Explainability
            trainResponse={state.trainResponse!}
            onNext={() => { completeStep(6); goToStep(7) }}
          />
        )
      case 7:
        return (
          <Step7Ethics
            trainResponse={state.trainResponse!}
            specialty={state.specialty!}
            stepsCompleted={state.stepsCompleted}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="app-layout">
      <NavBar
        specialty={state.specialty}
        specialties={specialties}
        onSpecialtyChange={handleSpecialtyChangeFromChip}
        onReset={handleResetSpecialty}
        onGlossary={() => setGlossaryOpen(true)}
        glossaryOpen={glossaryOpen}
        onGlossaryClose={() => setGlossaryOpen(false)}
      />
      <WizardProgress
        currentStep={state.currentStep}
        stepsCompleted={state.stepsCompleted}
        targetConfirmed={!!state.targetColumn}
        prepDone={!!state.prepResponse}
        trainDone={!!state.trainResponse}
        onStepClick={goToStep}
      />
      <div className="main-content">
        <React.Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}><div className="skeleton" style={{ width: 200, height: 24, margin: '0 auto' }} /><p className="text-muted text-sm" style={{ marginTop: '0.5rem' }}>Loading…</p></div>}>
          {renderStep()}
        </React.Suspense>
      </div>
      <BottomNav
        currentStep={state.currentStep}
        onPrev={() => goToStep(state.currentStep - 1)}
        onNext={() => {
          completeStep(state.currentStep)
          goToStep(state.currentStep + 1)
        }}
      />
      {confirmSwitch && (
        <div className="modal-overlay" onClick={() => setConfirmSwitch(null)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 420 }}>
            <div className="modal-header">
              <span className="modal-title">Switch Specialty?</span>
              <button className="btn btn-ghost btn-sm" onClick={() => setConfirmSwitch(null)}>✕</button>
            </div>
            <div className="modal-body">
              <p>Switching to <strong>{confirmSwitch.name}</strong> will reset your progress. Continue?</p>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setConfirmSwitch(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={() => { handleSpecialtySelect(confirmSwitch); setConfirmSwitch(null) }}>
                Switch Specialty
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
