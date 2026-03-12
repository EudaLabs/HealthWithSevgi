import React from 'react'
import { Check, Lock } from 'lucide-react'
import clsx from 'clsx'

const STEPS = [
  { n: 1, label: 'Clinical Context' },
  { n: 2, label: 'Data Exploration' },
  { n: 3, label: 'Data Preparation' },
  { n: 4, label: 'Model & Parameters' },
  { n: 5, label: 'Results' },
  { n: 6, label: 'Explainability' },
  { n: 7, label: 'Ethics & Bias' },
]

interface Props {
  currentStep: number
  stepsCompleted: Set<number>
  targetConfirmed: boolean
  prepDone: boolean
  trainDone: boolean
  onStepClick: (step: number) => void
}

export default function WizardProgress({
  currentStep,
  stepsCompleted,
  targetConfirmed,
  prepDone,
  trainDone,
  onStepClick,
}: Props) {
  const isLocked = (n: number): boolean => {
    if (n === 1 || n === 2 || n === 7) return false
    if (n === 3) return !targetConfirmed
    if (n === 4) return !prepDone
    if (n === 5) return !trainDone
    if (n === 6) return !trainDone
    return false
  }

  const isCompleted = (n: number) => stepsCompleted.has(n)
  const isActive = (n: number) => currentStep === n

  return (
    <div className="wizard-progress">
      {STEPS.map((step, idx) => {
        const locked = isLocked(step.n)
        const completed = isCompleted(step.n)
        const active = isActive(step.n)
        return (
          <React.Fragment key={step.n}>
            <div
              className={clsx('step-item', {
                active,
                completed: completed && !active,
                locked,
              })}
              onClick={() => !locked && onStepClick(step.n)}
              title={locked ? 'Complete the previous step first' : step.label}
            >
              <div className="step-number">
                {locked ? <Lock size={11} /> : completed && !active ? <Check size={12} /> : step.n}
              </div>
              <span>{step.label}</span>
            </div>
            {idx < STEPS.length - 1 && <div className="step-connector" />}
          </React.Fragment>
        )
      })}
    </div>
  )
}
