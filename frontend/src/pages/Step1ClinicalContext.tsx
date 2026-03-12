import React from 'react'
import { ArrowRight, Database, Tag } from 'lucide-react'
import type { Specialty } from '../types'

interface Props {
  specialty: Specialty
  onNext: () => void
}

export default function Step1ClinicalContext({ specialty, onNext }: Props) {
  return (
    <div className="step-page">
      <div className="step-page-header">
        <h2>Step 1 — Clinical Context</h2>
        <p>Understand the medical problem this AI is trying to solve.</p>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">{specialty.name}</div>
          <div className="card-subtitle">{specialty.description}</div>
        </div>
        <p style={{ lineHeight: 1.7, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          {specialty.clinical_context}
        </p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Database size={18} style={{ color: 'var(--primary)' }} />
            <span className="font-semibold">Clinical Facts</span>
          </div>
          <table className="data-table">
            <tbody>
              <tr>
                <td className="font-semibold" style={{ width: '45%', color: 'var(--text-secondary)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Specialty</td>
                <td>{specialty.name}</td>
              </tr>
              <tr>
                <td className="font-semibold" style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Data Source</td>
                <td>{specialty.data_source}</td>
              </tr>
              <tr>
                <td className="font-semibold" style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Target Variable</td>
                <td><code style={{ background: 'var(--background)', padding: '0.1rem 0.4rem', borderRadius: 4, fontSize: '0.85rem' }}>{specialty.target_variable}</code></td>
              </tr>
              <tr>
                <td className="font-semibold" style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Task Type</td>
                <td>
                  <span className={`badge ${specialty.target_type === 'binary' ? 'badge-success' : 'badge-primary'}`}>
                    {specialty.target_type === 'binary' ? 'Binary Classification' : 'Multi-class Classification'}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="font-semibold" style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>AI Predicts</td>
                <td>{specialty.what_ai_predicts}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Tag size={18} style={{ color: 'var(--primary)' }} />
            <span className="font-semibold">Clinical Features ({specialty.feature_names.length})</span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {specialty.feature_names.map((f) => (
              <span key={f} className="badge badge-neutral">{f.replace(/_/g, ' ')}</span>
            ))}
          </div>
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
