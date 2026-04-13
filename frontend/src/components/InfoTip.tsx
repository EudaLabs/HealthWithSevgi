import React, { useState, useRef, useEffect, useCallback } from 'react'
import { Info } from 'lucide-react'
import { GLOSSARY } from '../data/glossary'
import '../styles/infotip.css'

interface InfoTipProps {
  /** Key from the glossary dictionary */
  term: string
  /** Optional: wrap existing text with the InfoTip */
  children?: React.ReactNode
}

export default function InfoTip({ term, children }: InfoTipProps) {
  const entry = GLOSSARY[term]
  const [open, setOpen] = useState(false)
  const [flipped, setFlipped] = useState(false)
  const wrapperRef = useRef<HTMLSpanElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)

  // If term is not in glossary, just render children
  if (!entry) return <>{children}</>

  const toggle = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()
    if (!open && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect()
      // Flip to show below if not enough space above
      setFlipped(rect.top < 200)
    }
    setOpen(prev => !prev)
  }, [open])

  // Close on click outside or Escape
  useEffect(() => {
    if (!open) return
    const handleClick = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    document.addEventListener('keydown', handleKey)
    return () => {
      document.removeEventListener('mousedown', handleClick)
      document.removeEventListener('keydown', handleKey)
    }
  }, [open])

  return (
    <span className="infotip" ref={wrapperRef}>
      {children}
      <button
        ref={triggerRef}
        className="infotip-trigger"
        onClick={toggle}
        aria-label={`Learn more about ${entry.title}`}
        aria-expanded={open}
        type="button"
      >
        <Info size={14} />
      </button>
      {open && (
        <div
          className={`infotip-popover ${flipped ? 'infotip-popover--below' : ''}`}
          role="tooltip"
        >
          <div className="infotip-header">{entry.title}</div>
          <div className="infotip-desc">{entry.description}</div>
          {entry.learnMoreUrl && (
            <a
              className="infotip-link"
              href={entry.learnMoreUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              Learn more &rarr;
            </a>
          )}
        </div>
      )}
    </span>
  )
}
