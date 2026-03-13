import React, { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchSpecialties } from './api/specialties'
import NavBar from './components/NavBar'
import WizardProgress from './components/WizardProgress'
import SpecialtySelector from './components/SpecialtySelector'
import Step1ClinicalContext from './pages/Step1ClinicalContext'
import Step2DataExploration from './pages/Step2DataExploration'
import Step3DataPreparation from './pages/Step3DataPreparation'
import Step4ModelParameters from './pages/Step4ModelParameters'
import Step5Results from './pages/Step5Results'
import Step6Explainability from './pages/Step6Explainability'
import Step7Ethics from './pages/Step7Ethics'
import type { WizardState, Specialty, CompareEntry } from './types'

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

  const { data: specialties = [] } = useQuery({
    queryKey: ['specialties'],
    queryFn: fetchSpecialties,
  })

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

  const addComparedModel = useCallback((entry: CompareEntry) => {
    setState((prev) => {
      const existing = prev.comparedModels.filter((e) => e.model_id !== entry.model_id)
      return { ...prev, comparedModels: [...existing, entry] }
    })
  }, [])

  if (!state.specialty) {
    return (
      <div className="app-layout">
        <NavBar
          specialty={null}
          onReset={handleResetSpecialty}
          onGlossary={() => setGlossaryOpen(true)}
          glossaryOpen={glossaryOpen}
          onGlossaryClose={() => setGlossaryOpen(false)}
        />
        <div className="main-content">
          <div style={{ marginBottom: '1.5rem' }}>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              ML Visualization Tool
            </h1>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.4rem', maxWidth: 600 }}>
              Explore how artificial intelligence works in clinical settings — no technical
              background required. Choose a medical specialty to begin.
            </p>
          </div>
          <SpecialtySelector specialties={specialties} onSelect={handleSpecialtySelect} />
        </div>
      </div>
    )
  }

  const renderStep = () => {
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
        return (
          <Step4ModelParameters
            sessionId={state.prepResponse!.session_id}
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
        {renderStep()}
      </div>
    </div>
  )
}
