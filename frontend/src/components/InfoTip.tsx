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

const POPOVER_WIDTH = 300

export default function InfoTip({ term, children }: InfoTipProps) {
  const entry = GLOSSARY[term]
  const [open, setOpen] = useState(false)
  const [pos, setPos] = useState({ top: 0, left: 0, flipped: false })
  const wrapperRef = useRef<HTMLSpanElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const popoverRef = useRef<HTMLDivElement>(null)

  // If term is not in glossary, just render children
  if (!entry) return <>{children}</>

  const toggle = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()
    if (!open && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect()
      const flipped = rect.top < 220
      // Clamp left so popover doesn't overflow viewport edges
      const halfW = POPOVER_WIDTH / 2
      const rawLeft = rect.left + rect.width / 2
      const clampedLeft = Math.max(halfW + 8, Math.min(rawLeft, window.innerWidth - halfW - 8))
      setPos({
        top: flipped ? rect.bottom + 10 : rect.top - 10,
        left: clampedLeft,
        flipped,
      })
    }
    setOpen(prev => !prev)
  }, [open])

  // Close on click outside (both wrapper AND popover) or Escape
  useEffect(() => {
    if (!open) return
    const handleClick = (e: MouseEvent) => {
      const target = e.target as Node
      const inWrapper = wrapperRef.current?.contains(target)
      const inPopover = popoverRef.current?.contains(target)
      if (!inWrapper && !inPopover) {
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
          ref={popoverRef}
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
              onClick={(e) => e.stopPropagation()}
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
