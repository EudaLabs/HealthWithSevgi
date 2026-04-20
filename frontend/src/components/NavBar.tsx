import React, { useState, useRef, useEffect } from 'react'
import { Stethoscope, RefreshCw, Settings, Search, ChevronDown, Check } from 'lucide-react'
import type { Specialty } from '../types'

const GLOSSARY = [
  { term: 'Algorithm', def: 'A set of step-by-step instructions a computer follows to find patterns in patient data and make predictions — like a fast, data-driven decision checklist.' },
  { term: 'Training Data', def: 'Historical patient records the model learns from. Similar to a doctor reviewing past cases before seeing new patients.' },
  { term: 'Test Data', def: 'Patients the model has never seen, used to measure how well the AI performs. If a model only works on training data, it has memorised rather than learned.' },
  { term: 'Features', def: 'The input measurements (columns in your data) used to make predictions — for example, age, blood pressure, creatinine level, smoking status.' },
  { term: 'Target Variable', def: 'The outcome the model is trying to predict — for example, readmission, diagnosis, survival, or disease stage.' },
  { term: 'Overfitting', def: "When a model memorises the training cases so precisely that it fails on new patients. Like a student who memorises exam answers but cannot apply the knowledge." },
  { term: 'Underfitting', def: 'When a model is too simple to learn anything useful. Like a clinician who gives the same diagnosis regardless of symptoms.' },
  { term: 'Normalisation', def: 'Adjusting all measurements to the same scale so no single measurement dominates because of its units.' },
  { term: 'Class Imbalance', def: 'When one outcome is much rarer than the other in the training data. A model trained on 95% negative cases may simply predict negative for everyone.' },
  { term: 'SMOTE', def: 'Synthetic Minority Over-sampling Technique. Creates artificial examples of the rare outcome to balance the training data. Applied to training data only.' },
  { term: 'Sensitivity', def: 'Of all patients who truly have the condition, what fraction did the model correctly identify? Low sensitivity means the model misses real cases.' },
  { term: 'Specificity', def: 'Of all patients who truly do not have the condition, what fraction did the model correctly call healthy? Low specificity means too many false alarms.' },
  { term: 'Precision', def: 'Of all patients the model flagged as positive, what fraction actually were? Low precision means many unnecessary referrals or treatments.' },
  { term: 'F1 Score', def: 'A single number that balances Sensitivity and Precision. Useful when both false negatives and false positives have real clinical costs.' },
  { term: 'AUC-ROC', def: 'A score from 0.5 (random guessing) to 1.0 (perfect separation) summarising how well the model distinguishes between positive and negative patients.' },
  { term: 'Confusion Matrix', def: 'A table showing: correctly identified sick patients, correctly identified healthy patients, healthy patients incorrectly flagged as sick, and sick patients incorrectly called safe.' },
  { term: 'Feature Importance', def: 'A ranking of which patient measurements the model relied on most. Helps confirm whether the AI is using clinically meaningful signals.' },
  { term: 'Hyperparameter', def: 'A setting chosen before training that controls model behaviour — for example, K in KNN or tree depth in Decision Tree. Not learned from data.' },
  { term: 'Bias (AI)', def: 'When a model performs significantly worse for certain patient subgroups because they were under-represented in the training data.' },
  { term: 'Cross-Validation', def: 'Splitting the data multiple times and averaging results to get a more reliable performance estimate than a single train/test split.' },
]

interface Props {
  specialty: Specialty | null
  specialties: Specialty[]
  onSpecialtyChange: (s: Specialty) => void
  onReset: () => void
  onGlossary: () => void
  glossaryOpen: boolean
  onGlossaryClose: () => void
  onArena?: () => void
  arenaActive?: boolean
}

export default function NavBar({ specialty, specialties, onSpecialtyChange, onReset, onGlossary, glossaryOpen, onGlossaryClose, onArena, arenaActive }: Props) {
  const [search, setSearch] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [dropdownSearch, setDropdownSearch] = useState('')
  const dropdownRef = useRef<HTMLDivElement>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)

  // Bug #3: Reset glossary search when modal reopens
  useEffect(() => {
    if (glossaryOpen) setSearch('')
  }, [glossaryOpen])

  // Bug #4: Close glossary on Escape key
  useEffect(() => {
    if (!glossaryOpen) return
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onGlossaryClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [glossaryOpen, onGlossaryClose])

  const filtered = GLOSSARY.filter(
    (g) =>
      g.term.toLowerCase().includes(search.toLowerCase()) ||
      g.def.toLowerCase().includes(search.toLowerCase())
  )

  const filteredSpecialties = specialties.filter((s) =>
    s.name.toLowerCase().includes(dropdownSearch.toLowerCase())
  )

  // Close dropdown on outside click
  useEffect(() => {
    if (!dropdownOpen) return
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
        setDropdownSearch('')
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [dropdownOpen])

  // Focus search when dropdown opens
  useEffect(() => {
    if (dropdownOpen && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [dropdownOpen])

  return (
    <>
      {/* ---- Main header bar ---- */}
      <nav className="navbar">
        <div className="navbar-inner">
          <div className="navbar-brand">
            <img
              src="/logo.png"
              alt="HealthWithSevgi logo"
              className="navbar-logo"
              width={44}
              height={44}
            />
            <div>
              <div className="navbar-brand-title">HealthWithSevgi · ML Learning Tool</div>
              <div className="navbar-brand-sub">For Healthcare Professionals</div>
            </div>
          </div>

          <div className="navbar-actions">
            {/* Specialty dropdown */}
            {specialties.length > 0 && (
              <div className="navbar-dropdown-wrapper" ref={dropdownRef}>
                <button
                  className="navbar-dropdown-trigger"
                  onClick={() => { setDropdownOpen(!dropdownOpen); setDropdownSearch('') }}
                >
                  <Stethoscope size={14} />
                  <span className="navbar-dropdown-label">
                    {specialty ? specialty.name : 'Select Domain'}
                  </span>
                  <ChevronDown
                    size={14}
                    style={{
                      transition: 'transform 200ms ease',
                      transform: dropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                    }}
                  />
                </button>

                {dropdownOpen && (
                  <div className="navbar-dropdown-menu">
                    <div className="navbar-dropdown-search">
                      <Search size={13} className="navbar-dropdown-search-icon" />
                      <input
                        ref={searchInputRef}
                        className="navbar-dropdown-search-input"
                        placeholder="Search domains..."
                        value={dropdownSearch}
                        onChange={(e) => setDropdownSearch(e.target.value)}
                      />
                    </div>
                    <div className="navbar-dropdown-list">
                      {filteredSpecialties.map((s) => (
                        <button
                          key={s.id}
                          className={`navbar-dropdown-item${specialty?.id === s.id ? ' active' : ''}`}
                          onClick={() => {
                            onSpecialtyChange(s)
                            setDropdownOpen(false)
                            setDropdownSearch('')
                          }}
                        >
                          <span>{s.name}</span>
                          {specialty?.id === s.id && <Check size={14} />}
                        </button>
                      ))}
                      {filteredSpecialties.length === 0 && (
                        <div className="navbar-dropdown-empty">No domains found</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {onArena && (
              <button
                className={`navbar-icon-btn ${arenaActive ? 'navbar-icon-btn-active' : ''}`}
                onClick={onArena}
                title="Model Arena"
                aria-label="Open Model Arena"
              >
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
                  <line x1="4" y1="22" x2="4" y2="15"/>
                </svg>
              </button>
            )}
            <button
              className="navbar-icon-btn"
              onClick={onReset}
              title="Change specialty / reset"
              aria-label="Refresh / reset"
            >
              <RefreshCw size={17} />
            </button>
            <button
              className="navbar-icon-btn"
              onClick={onGlossary}
              title="Help / Glossary"
              aria-label="Settings / glossary"
            >
              <Settings size={17} />
            </button>
          </div>
        </div>
      </nav>

      {/* ---- Glossary modal ---- */}
      {glossaryOpen && (
        <div className="modal-overlay" onClick={onGlossaryClose}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 640 }}>
            <div className="modal-header">
              <span className="modal-title">Glossary — Key Terms</span>
              <button className="btn btn-ghost btn-sm" onClick={onGlossaryClose}>&#10005;</button>
            </div>
            <div className="modal-body">
              <div style={{ position: 'relative', marginBottom: '1rem' }}>
                <Search size={15} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  className="form-input"
                  style={{ paddingLeft: '2rem' }}
                  placeholder="Search terms..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  autoFocus
                />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                {filtered.map((g) => (
                  <div key={g.term}>
                    <div style={{ fontWeight: 700, color: 'var(--primary)', marginBottom: '0.2rem' }}>{g.term}</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{g.def}</div>
                  </div>
                ))}
                {filtered.length === 0 && (
                  <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>No terms match your search.</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
