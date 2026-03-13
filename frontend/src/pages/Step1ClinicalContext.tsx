import React from 'react'
import { ArrowRight, Heart, AlertTriangle, CheckCircle, Brain, BarChart3, Settings, Lightbulb, Scale, Database, Tag } from 'lucide-react'
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

export default function Step1ClinicalContext({ specialty, onNext }: Props) {
  return (
    <div className="step-page">
      {/* Header */}
      <div className="card" style={{ background: 'var(--primary-light)', border: '1px solid rgba(26,122,76,0.15)' }}>
        <span className="step-badge">STEP 1 · CLINICAL CONTEXT</span>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '0.5rem' }}>Clinical Context & Problem Definition</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
          Understand the medical problem this AI is trying to solve and what each step of the ML pipeline will produce.
        </p>
      </div>

      <div className="grid-2">
        {/* Clinical Scenario */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: '1rem' }}>Clinical Scenario</div>
          <div className="info-card-green" style={{ marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Heart size={16} style={{ color: 'var(--primary)' }} />
              <span className="badge badge-success">{specialty.name}</span>
            </div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              CLINICAL QUESTION
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              {specialty.what_ai_predicts}
            </p>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--background)', borderRadius: '8px', marginBottom: '0.75rem' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>WHY THIS MATTERS</div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{specialty.clinical_context}</p>
          </div>
          <div className="info-card-green">
            <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.25rem' }}>DATA SOURCE</div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{specialty.data_source}</p>
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
              <span className="badge badge-success">{specialty.target_type === 'binary' ? 'Binary' : 'Multi-class'}</span>
              <span className="badge badge-neutral">Target: {specialty.target_variable}</span>
            </div>
          </div>
        </div>

        {/* Step Roadmap */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: '1rem' }}>What Will Be Produced in Each Step</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {STEP_ROADMAP.map(step => {
              const Icon = step.icon
              const isActive = step.n === 1
              return (
                <div key={step.n} style={{
                  display: 'flex', alignItems: 'center', gap: '0.75rem',
                  padding: '0.6rem 0.75rem', borderRadius: '8px',
                  background: isActive ? 'var(--primary)' : 'var(--background)',
                  color: isActive ? 'white' : 'var(--text-primary)',
                }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: isActive ? 'rgba(255,255,255,0.2)' : 'var(--surface)', border: isActive ? 'none' : '1px solid var(--border)',
                    fontSize: '0.75rem', fontWeight: 700, flexShrink: 0,
                  }}>
                    {step.n}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{step.title}</div>
                    <div style={{ fontSize: '0.75rem', opacity: isActive ? 0.85 : 0.65 }}>{step.desc}</div>
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
            <span style={{ fontWeight: 700, color: '#8a5200' }}>What ML Cannot Do</span>
          </div>
          <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            <li>ML cannot replace clinical judgment or doctor-patient relationships</li>
            <li>Models may reflect biases present in historical training data</li>
            <li>Predictions are probabilities, not diagnoses</li>
          </ul>
        </div>
        <div className="info-card-green">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <CheckCircle size={18} style={{ color: 'var(--primary)' }} />
            <span style={{ fontWeight: 700, color: 'var(--primary)' }}>Remember</span>
          </div>
          <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            <li>This is a learning tool — experiment freely with different models</li>
            <li>No real patient data leaves your browser session</li>
            <li>The goal is understanding, not building a production system</li>
          </ul>
        </div>
      </div>

      {/* Features list */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Tag size={18} style={{ color: 'var(--primary)' }} />
          <span className="font-semibold">Clinical Features ({specialty.feature_names.length})</span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
          {specialty.feature_names.map(f => (
            <span key={f} className="badge badge-neutral">{f.replace(/_/g, ' ')}</span>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button className="btn btn-primary" onClick={onNext}>
          Continue to Data Exploration <ArrowRight size={16} />
        </button>
      </div>
    </div>
  )
}
