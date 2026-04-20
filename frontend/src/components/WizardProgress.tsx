import React from 'react'
import { Check, Lock } from 'lucide-react'
import clsx from 'clsx'

const STEPS = [
  { n: 1, label: 'Clinical Context', sub: 'Domain & objectives' },
  { n: 2, label: 'Data Exploration', sub: 'Inspect & visualize' },
  { n: 3, label: 'Data Preparation', sub: 'Clean, encode & split' },
  { n: 4, label: 'Model & Parameters', sub: 'Choose & configure' },
  { n: 5, label: 'Results', sub: 'Evaluate & compare' },
  { n: 6, label: 'Explainability', sub: 'Interpret predictions' },
  { n: 7, label: 'Ethics & Bias', sub: 'Audit fairness' },
]

interface Props {
  currentStep: number
  stepsCompleted: Set<number>
  targetConfirmed: boolean
  prepDone: boolean
  trainDone: boolean
  onStepClick: (step: number) => void
}

/**
 * Seven-step progress rail rendered under the top app bar.
 * Each pill reflects one of three states — locked / current / completed
 * — derived from `stepsCompleted` + `currentStep`. Completed steps are
 * clickable so the user can jump back; locked steps are visually dimmed
 * but WCAG-AA compliant (see the Sprint 5 Accessibility Log for the
 * contrast rationale).
 */
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
      <div className="wizard-progress-inner">
        {STEPS.map((step, idx) => {
          const locked = isLocked(step.n)
          const completed = isCompleted(step.n)
          const active = isActive(step.n)
          const pastStep = step.n < currentStep && completed

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
                  {locked
                    ? <Lock size={16} />
                    : completed && !active
                      ? <Check size={18} strokeWidth={2.5} />
                      : step.n}
                </div>
                <div className="step-item-labels">
                  <div className="step-item-name">{step.label}</div>
                  <div className="step-item-sub">{step.sub}</div>
                </div>
              </div>

              {idx < STEPS.length - 1 && (
                <div className="step-connector">
                  <div className={clsx('step-connector-line', { filled: pastStep || step.n < currentStep })} />
                </div>
              )}
            </React.Fragment>
          )
        })}
      </div>
    </div>
  )
}
