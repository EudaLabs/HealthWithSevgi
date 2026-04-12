import React, { useState, useCallback, useMemo, useRef } from 'react'
import ParallelCoordinatesChart from './ParallelCoordinatesChart'
import ParallelCoordsLegend from './ParallelCoordsLegend'
import type { CompareEntry } from '../../types'
import '../../styles/parallel-coordinates.css'

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */

interface ModelComparisonVizProps {
  entries: CompareEntry[]
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

const ModelComparisonViz: React.FC<ModelComparisonVizProps> = ({ entries }) => {
  /* ---- state ---------------------------------------------------- */
  const [hoveredId, setHoveredId] = useState<string | null>(null)
  const [pinnedIds, setPinnedIds] = useState<Set<string>>(new Set())
  const [hasBrushes, setHasBrushes] = useState(false)
  const [resetBrushSignal, setResetBrushSignal] = useState(0)

  const containerRef = useRef<HTMLDivElement>(null)

  /* ---- handlers ------------------------------------------------- */
  const handleHover = useCallback((modelId: string | null) => {
    setHoveredId(modelId)
  }, [])

  const handlePin = useCallback((modelId: string) => {
    setPinnedIds((prev) => {
      const next = new Set(prev)
      if (next.has(modelId)) {
        next.delete(modelId)
      } else {
        next.add(modelId)
      }
      return next
    })
  }, [])

  const handleResetBrushes = useCallback(() => {
    setResetBrushSignal((s) => s + 1)
  }, [])

  const handleClearPins = useCallback(() => {
    setPinnedIds(new Set())
  }, [])

  const handleBrushChange = useCallback((active: boolean) => {
    setHasBrushes(active)
  }, [])

  /* ---- empty state ---------------------------------------------- */
  if (entries.length === 0) {
    return (
      <div className="pc-container">
        <div className="pc-empty">
          <div className="pc-empty-icon">📊</div>
          <div className="pc-empty-text">
            Train models and click <strong>&quot;+ Compare&quot;</strong> to
            visualise them here.
            <br />
            Add at least 2 models for meaningful comparison.
          </div>
        </div>
      </div>
    )
  }

  /* ---- render --------------------------------------------------- */
  return (
    <div className="pc-container">
      <div className="pc-header">
        <div>
          <div className="pc-title">
            Model Comparison &mdash; Parallel Coordinates
          </div>
          <div className="pc-subtitle">
            Hover to inspect &middot; Click to pin &middot; Drag on axes to
            filter
          </div>
        </div>
      </div>

      <div className="pc-chart-area" ref={containerRef}>
        <ParallelCoordinatesChart
          entries={entries}
          onHover={handleHover}
          onPin={handlePin}
          pinnedIds={pinnedIds}
          hoveredId={hoveredId}
          onBrushChange={handleBrushChange}
          resetBrushSignal={resetBrushSignal}
          height={380}
        />
      </div>

      <ParallelCoordsLegend
        entries={entries}
        pinnedIds={pinnedIds}
        onTogglePin={handlePin}
        onResetBrushes={handleResetBrushes}
        onClearPins={handleClearPins}
        hasBrushes={hasBrushes}
      />
    </div>
  )
}

export default React.memo(ModelComparisonViz)
