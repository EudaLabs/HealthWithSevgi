import React, { useState, useRef, useEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
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
  const [pos, setPos] = useState<{ top: number; left: number; flipped: boolean }>({ top: 0, left: 0, flipped: false })
  const wrapperRef = useRef<HTMLSpanElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)

  // If term is not in glossary, just render children
  if (!entry) return <>{children}</>

  const toggle = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()
    if (!open && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect()
      const flipped = rect.top < 220
      setPos({
        top: flipped ? rect.bottom + 10 : rect.top - 10,
        left: rect.left + rect.width / 2,
        flipped,
      })
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
      {open && createPortal(
        <div
          className={`infotip-popover ${pos.flipped ? 'infotip-popover--below' : ''}`}
          role="tooltip"
          style={{
            position: 'fixed',
            top: pos.flipped ? pos.top : undefined,
            bottom: pos.flipped ? undefined : `calc(100vh - ${pos.top}px)`,
            left: pos.left,
            transform: 'translateX(-50%)',
          }}
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
        </div>,
        document.body
      )}
    </span>
  )
}
