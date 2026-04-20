import React from 'react'
import { Heart, AlertTriangle, CheckCircle, Brain, BarChart3, Settings, Lightbulb, Scale, Database, Stethoscope } from 'lucide-react'
import InfoTip from '../components/InfoTip'
import type { Specialty } from '../types'

const STEP_ROADMAP = [
  { n: 1, title: 'Clinical Context', desc: 'Define the medical problem and objectives', icon: Heart },
  { n: 2, title: 'Data Exploration', desc: 'Inspect dataset structure and distributions', icon: Database },
  { n: 3, title: 'Data Preparation', desc: 'Clean, encode, normalize, and split data', icon: Settings },
  { n: 4, title: 'Model & Parameters', desc: 'Select algorithm and tune hyperparameters', icon: Brain },
  { n: 5, title: 'Results', desc: 'Evaluate metrics, ROC curves, confusion matrix', icon: BarChart3 },
  { n: 6, title: 'Explainability', desc: 'Understand feature importance and SHAP values', icon: Lightbulb },
  { n: 7, title: 'Ethics & Bias', desc: 'Audit fairness across patient subgroups', icon: Scale },
]

interface Props {
  specialty: Specialty
  onNext: () => void
}

/**
 * Step 1 — Clinical Context.
 * Landing step that previews the chosen specialty and shows a 7-step roadmap
 * so the user understands what the wizard will ask of them. Pure presentation:
 * `specialty` is fetched upstream and `onNext` unlocks Step 2.
 */
export default function Step1ClinicalContext({ specialty, onNext }: Props) {
  return (
    <div className="step-page">
      {/* Header */}
      <div className="card" style={{ background: 'var(--primary-light)', border: '1px solid rgba(26,122,76,0.15)' }}>
        <span className="step-badge">STEP 1 · CLINICAL CONTEXT</span>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.75rem', fontWeight: 700, marginTop: '0.5rem' }}>
          <Stethoscope size={28} style={{ color: 'var(--primary)' }} />
          Clinical Context &amp; Problem Definition
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
          Before we look at any data, we define the clinical problem, understand why it matters, and map out every step of the ML workflow.
        </p>
      </div>

      <div className="grid-2">
        {/* Clinical Scenario */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: '1rem' }}>Clinical Scenario</div>

          {/* Medical Specialty */}
          <div style={{ marginBottom: '0.75rem' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.4rem' }}>
              MEDICAL SPECIALTY
            </div>
            <span className="badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
              <Heart size={12} />
              {specialty.name}
            </span>
          </div>

          {/* Clinical Question */}
          <div style={{ marginBottom: '0.75rem' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.4rem' }}>
              CLINICAL QUESTION
            </div>
            <div style={{
              borderLeft: '3px solid var(--primary)',
              paddingLeft: '0.75rem',
              fontSize: '0.9rem',
              color: 'var(--text-primary)',
              lineHeight: 1.5,
            }}>
              {specialty.what_ai_predicts}
            </div>
          </div>

          {/* Why This Matters */}
          <div style={{
            background: 'var(--background)',
            borderRadius: '8px',
            padding: '0.75rem',
            marginBottom: '0.75rem',
          }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.4rem' }}>
              WHY THIS MATTERS
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {specialty.clinical_context}
            </p>
          </div>

          {/* Impact */}
          <div style={{
            background: 'var(--primary-light)',
            border: '1px solid rgba(26,122,76,0.2)',
            borderRadius: '8px',
            padding: '0.75rem',
          }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.4rem' }}>
              IMPACT
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Source: <strong style={{ color: 'var(--text-primary)' }}>{specialty.data_source}</strong>
            </p>
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
              <span className="badge badge-success">{specialty.target_type === 'binary' ? 'Binary Classification' : 'Multi-class'} <InfoTip term={specialty.target_type === 'binary' ? 'binary_classification' : 'multiclass'} /></span>
              <span className="badge badge-neutral">Target: {specialty.target_variable} <InfoTip term="target_variable" /></span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem', lineHeight: 1.5 }}>
              {specialty.target_type === 'binary'
                ? 'The AI will predict one of two outcomes for each patient — for example, "at risk" or "not at risk". This is the most common type of clinical prediction task.'
                : 'The AI will predict one of several possible categories for each patient. Each category represents a distinct clinical outcome or diagnosis.'}
            </p>
          </div>
        </div>

        {/* Step Roadmap */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: '0.25rem' }}>What Will Be Produced in Each Step</div>
          <div className="card-subtitle" style={{ marginBottom: '1rem' }}>
            Outputs you will collect as you progress through the 7 steps
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {STEP_ROADMAP.map(step => {
              const Icon = step.icon
              const isActive = step.n === 1
              const isCompleted = step.n < 1
              return (
                <div key={step.n} style={{
                  display: 'flex', alignItems: 'center', gap: '0.75rem',
                  padding: '0.6rem 0.75rem', borderRadius: '8px',
                  background: isActive ? 'var(--primary)' : 'var(--background)',
                  color: isActive ? 'white' : 'var(--text-primary)',
                }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: isActive ? 'rgba(255,255,255,0.2)' : 'var(--surface)',
                    border: isActive ? 'none' : '1px solid var(--border)',
                    fontSize: '0.75rem', fontWeight: 700, flexShrink: 0,
                    color: isActive ? 'white' : 'var(--text-secondary)',
                  }}>
                    {isCompleted ? <CheckCircle size={14} style={{ color: 'var(--primary)' }} /> : step.n}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{step.title}</div>
                    <div style={{ fontSize: '0.75rem', opacity: isActive ? 1 : 0.75 }}>{step.desc}</div>
                  </div>
                  <Icon size={16} style={{ opacity: 0.6, flexShrink: 0 }} />
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Warning cards */}
      <div className="grid-2">
        <div className="info-card-amber">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <AlertTriangle size={18} style={{ color: '#8a5200' }} />
            <span style={{ fontWeight: 700, color: '#8a5200' }}>What ML Cannot Do <InfoTip term="machine_learning" /></span>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            ML cannot replace clinical judgment or doctor-patient relationships.{' '}
            <strong style={{ color: 'var(--text-primary)' }}>Models may reflect biases present in historical training data</strong>{' '}
            and predictions are probabilities, not diagnoses.
          </p>
        </div>
        <div className="info-card-green">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <CheckCircle size={18} style={{ color: 'var(--primary)' }} />
            <span style={{ fontWeight: 700, color: 'var(--primary)' }}>Remember</span>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            This is a learning tool — experiment freely with different models.{' '}
            <strong style={{ color: 'var(--text-primary)' }}>No real patient data leaves your browser session.</strong>{' '}
            The goal is understanding, not building a production system.
          </p>
        </div>
      </div>

    </div>
  )
}
