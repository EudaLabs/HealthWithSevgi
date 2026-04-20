import React, { useState, useCallback, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchSpecialties } from './api/specialties'
import NavBar from './components/NavBar'
import WizardProgress from './components/WizardProgress'
import Step1ClinicalContext from './pages/Step1ClinicalContext'
const Step2DataExploration = React.lazy(() => import('./pages/Step2DataExploration'))
const Step3DataPreparation = React.lazy(() => import('./pages/Step3DataPreparation'))
const Step4ModelParameters = React.lazy(() => import('./pages/Step4ModelParameters'))
const Step5Results = React.lazy(() => import('./pages/Step5Results'))
const ArenaPage = React.lazy(() => import('../../local/model-arena/frontend/pages/ArenaPage'))
const Step6Explainability = React.lazy(() => import('./pages/Step6Explainability'))
const Step7Ethics = React.lazy(() => import('./pages/Step7Ethics'))
import type { WizardState, Specialty, CompareEntry } from './types'

const STEP_NAMES = [
  '', 'Clinical Context', 'Data Exploration', 'Data Preparation',
  'Model & Parameters', 'Results', 'Explainability', 'Ethics & Bias'
]

function BottomNav({ currentStep, canAdvance, onPrev, onNext }: { currentStep: number; canAdvance: boolean; onPrev: () => void; onNext: () => void }) {
  return (
    <div className="bottom-nav">
      <div className="bottom-nav-inner">
        <div className="bottom-nav-left">
          <span className="step-badge">Step {currentStep} / 7</span>
          <span className="bottom-nav-step-name">{STEP_NAMES[currentStep]}</span>
        </div>
        <div className="bottom-nav-right">
          <button className="btn-prev" onClick={onPrev} disabled={currentStep <= 1}>
            ← Previous
          </button>
          {currentStep < 7 && (
            <button className="btn-next" onClick={onNext} disabled={!canAdvance}>
              Next Step →
            </button>
          )}
        </div>
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
    outlier_handling: 'none',
  },
  trainResponse: null,
  comparedModels: [],
  stepsCompleted: new Set(),
  currentStep: 1,
})

export default function App() {
  const [state, setState] = useState<WizardState>(createDefaultState)
  const [glossaryOpen, setGlossaryOpen] = useState(false)
  const [showArena, setShowArena] = useState(false)
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
        <div style={{ padding: '2rem', minHeight: '60vh' }}>
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
            onExploreSuccess={(data) => update({ explorationData: data })}
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
            onNext={() => { completeStep(5); goToStep(6) }}
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
            trainResponse={state.trainResponse}
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
        onArena={() => setShowArena(!showArena)}
        arenaActive={showArena}
      />
      <WizardProgress
        currentStep={state.currentStep}
        stepsCompleted={state.stepsCompleted}
        targetConfirmed={!!state.targetColumn}
        prepDone={!!state.prepResponse}
        trainDone={!!state.trainResponse}
        onStepClick={goToStep}
      />
      <main className="main-content">
        <React.Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}><div className="skeleton" style={{ width: 200, height: 24, margin: '0 auto' }} /><p className="text-muted text-sm" style={{ marginTop: '0.5rem' }}>Loading...</p></div>}>
          {showArena ? (
            <ArenaPage
              sessionId={state.prepResponse?.session_id ?? null}
              onClose={() => setShowArena(false)}
            />
          ) : (
            renderStep()
          )}
        </React.Suspense>
        <div style={{ textAlign: 'center', fontSize: '0.78rem', color: 'var(--text-secondary)', padding: '1rem 0 0.5rem' }}>
          Patient data is processed locally within this session. No patient data is stored or transmitted.
        </div>
      </main>
      {!showArena && <BottomNav
        currentStep={state.currentStep}
        canAdvance={
          state.currentStep === 1 ? true :
          state.currentStep === 2 ? !!state.targetColumn :
          state.currentStep === 3 ? !!state.prepResponse :
          state.currentStep === 4 ? !!state.trainResponse :
          state.currentStep === 5 ? !!state.trainResponse :
          state.currentStep === 6 ? !!state.trainResponse :
          false
        }
        onPrev={() => goToStep(state.currentStep - 1)}
        onNext={() => {
          // Guard: only advance if the step's unlock condition is actually met
          const canGo =
            state.currentStep === 1 ? true :
            state.currentStep === 2 ? !!state.targetColumn :
            state.currentStep === 3 ? !!state.prepResponse :
            state.currentStep === 4 ? !!state.trainResponse :
            state.currentStep === 5 ? !!state.trainResponse :
            state.currentStep === 6 ? !!state.trainResponse :
            false
          if (!canGo) return
          completeStep(state.currentStep)
          goToStep(state.currentStep + 1)
        }}
      />}
      {confirmSwitch && (
        <div className="modal-overlay" onClick={() => setConfirmSwitch(null)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 420 }}>
            <div style={{ padding: '2rem', textAlign: 'center' }}>
              <div style={{
                width: 48, height: 48, borderRadius: '50%', margin: '0 auto 1rem',
                background: 'var(--warning-light)', display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <span style={{ fontSize: '1.5rem' }}>&#9888;</span>
              </div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                Switch Clinical Domain
              </h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '0.25rem' }}>
                Changing the clinical domain will reset the current machine learning workflow and clear the uploaded dataset and all results.
              </p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: 600, marginTop: '0.5rem' }}>
                This action cannot be undone.
              </p>
            </div>
            <div style={{
              display: 'flex', gap: '0.75rem', justifyContent: 'center',
              padding: '0 2rem 1.5rem',
            }}>
              <button className="btn btn-ghost" onClick={() => setConfirmSwitch(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={() => { handleSpecialtySelect(confirmSwitch); setConfirmSwitch(null) }}>
                Switch Domain
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
