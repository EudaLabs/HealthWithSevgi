import React from 'react'
import {
  Activity, Brain, Droplets, Eye, Heart, Microscope,
  Pill, Stethoscope, TestTube, Wind, Baby, Dna,
  FlaskConical, Zap, AlertCircle, Shield,
} from 'lucide-react'
import clsx from 'clsx'
import type { Specialty } from '../types'

const ICONS: Record<string, React.ReactNode> = {
  cardiology_hf: <Heart size={22} />,
  radiology_pneumonia: <Wind size={22} />,
  nephrology_ckd: <Droplets size={22} />,
  oncology_breast: <Microscope size={22} />,
  neurology_parkinsons: <Brain size={22} />,
  endocrinology_diabetes: <TestTube size={22} />,
  hepatology_liver: <FlaskConical size={22} />,
  cardiology_stroke: <Zap size={22} />,
  mental_health: <Brain size={22} />,
  pulmonology_copd: <Wind size={22} />,
  haematology_anaemia: <Droplets size={22} />,
  dermatology: <Shield size={22} />,
  ophthalmology: <Eye size={22} />,
  orthopaedics: <Activity size={22} />,
  icu_sepsis: <AlertCircle size={22} />,
  obstetrics_fetal: <Baby size={22} />,
  cardiology_arrhythmia: <Heart size={22} />,
  oncology_cervical: <Dna size={22} />,
  thyroid: <Stethoscope size={22} />,
  pharmacy_readmission: <Pill size={22} />,
}

interface Props {
  specialties: Specialty[]
  onSelect: (s: Specialty) => void
}

/**
 * Step-1 landing grid that presents the 20 clinical specialties as
 * cards. Rendered only when no specialty is selected; picking one
 * advances the wizard and triggers the Step 1 — Clinical Context
 * rendering via the parent callback.
 */
export default function SpecialtySelector({ specialties, onSelect }: Props) {
  if (specialties.length === 0) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', padding: '3rem' }}>
        <div className="skeleton" style={{ width: 200, height: 24, marginBottom: '0.5rem' }} />
        <div className="text-muted text-sm">Loading specialties…</div>
      </div>
    )
  }

  return (
    <div className="specialty-grid">
      {specialties.map((s) => (
        <button
          key={s.id}
          className="specialty-card"
          onClick={() => onSelect(s)}
        >
          <div className="specialty-icon">{ICONS[s.id] ?? <Stethoscope size={22} />}</div>
          <div className="specialty-name">{s.name}</div>
          <div className="specialty-predicts">{s.what_ai_predicts}</div>
        </button>
      ))}
    </div>
  )
}
