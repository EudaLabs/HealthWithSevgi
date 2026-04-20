import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react'
import type { KNNScatterData, ScatterPoint } from '../../types'

interface KNNScatterCanvasProps {
  data: KNNScatterData
}

/* ---- Color palette for up to 8 classes ---- */
const CLASS_COLORS = [
  { solid: 'rgba(59, 130, 246, 1)',   fill: 'rgba(59, 130, 246, 0.15)',  ring: 'rgba(59, 130, 246, 0.5)'  },  // blue
  { solid: 'rgba(239, 68, 68, 1)',    fill: 'rgba(239, 68, 68, 0.15)',   ring: 'rgba(239, 68, 68, 0.5)'   },  // red
  { solid: 'rgba(16, 185, 129, 1)',   fill: 'rgba(16, 185, 129, 0.15)', ring: 'rgba(16, 185, 129, 0.5)' },  // emerald
  { solid: 'rgba(245, 158, 11, 1)',   fill: 'rgba(245, 158, 11, 0.15)', ring: 'rgba(245, 158, 11, 0.5)' },  // amber
  { solid: 'rgba(139, 92, 246, 1)',   fill: 'rgba(139, 92, 246, 0.15)', ring: 'rgba(139, 92, 246, 0.5)' },  // violet
  { solid: 'rgba(236, 72, 153, 1)',   fill: 'rgba(236, 72, 153, 0.15)', ring: 'rgba(236, 72, 153, 0.5)' },  // pink
  { solid: 'rgba(20, 184, 166, 1)',   fill: 'rgba(20, 184, 166, 0.15)', ring: 'rgba(20, 184, 166, 0.5)' },  // teal
  { solid: 'rgba(107, 114, 128, 1)',  fill: 'rgba(107, 114, 128, 0.15)', ring: 'rgba(107, 114, 128, 0.5)' }, // gray
]

function getColor(classIdx: number) {
  return CLASS_COLORS[classIdx % CLASS_COLORS.length]
}

/* ---- Euclidean distance ---- */
function euclidean(a: { x: number; y: number }, b: { x: number; y: number }) {
  return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)
}

/* ---- Tooltip data structure ---- */
interface HoverInfo {
  point: ScatterPoint
  canvasX: number
  canvasY: number
  neighbors: ScatterPoint[]
}

const CANVAS_W = 720
const CANVAS_H = 500
const PAD = { top: 44, right: 24, bottom: 60, left: 56 }

/**
 * KNN 2-D decision-boundary scatter (Step 5, KNN-only).
 * Canvas-based for speed on large meshes. Shows the PCA-projected test set
 * as coloured dots over the decision-region heatmap, plus hover popovers
 * that highlight the k-nearest-neighbours of the hovered point.
 */
const KNNScatterCanvas: React.FC<KNNScatterCanvasProps> = ({ data }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [hover, setHover] = useState<HoverInfo | null>(null)

  const { scatter_points, decision_mesh, pca_explained_variance, classes, k, metric } = data

  /* ---- Precompute coordinate mapping ---- */
  const mapping = useMemo(() => {
    const allX = scatter_points.map(p => p.x)
    const allY = scatter_points.map(p => p.y)
    // Include mesh bounds for a complete picture
    const meshXMin = Math.min(...decision_mesh.x_values)
    const meshXMax = Math.max(...decision_mesh.x_values)
    const meshYMin = Math.min(...decision_mesh.y_values)
    const meshYMax = Math.max(...decision_mesh.y_values)

    const xMin = Math.min(Math.min(...allX), meshXMin)
    const xMax = Math.max(Math.max(...allX), meshXMax)
    const yMin = Math.min(Math.min(...allY), meshYMin)
    const yMax = Math.max(Math.max(...allY), meshYMax)

    // Add 5% padding
    const xPad = (xMax - xMin) * 0.05 || 1
    const yPad = (yMax - yMin) * 0.05 || 1

    return {
      xMin: xMin - xPad,
      xMax: xMax + xPad,
      yMin: yMin - yPad,
      yMax: yMax + yPad,
    }
  }, [scatter_points, decision_mesh])

  const plotW = CANVAS_W - PAD.left - PAD.right
  const plotH = CANVAS_H - PAD.top - PAD.bottom

  const toCanvasX = useCallback((v: number) => PAD.left + ((v - mapping.xMin) / (mapping.xMax - mapping.xMin)) * plotW, [mapping, plotW])
  const toCanvasY = useCallback((v: number) => PAD.top + plotH - ((v - mapping.yMin) / (mapping.yMax - mapping.yMin)) * plotH, [mapping, plotH])

  /* ---- Separate train/test points ---- */
  const trainPoints = useMemo(() => scatter_points.filter(p => p.split === 'train'), [scatter_points])
  const testPoints = useMemo(() => scatter_points.filter(p => p.split === 'test'), [scatter_points])

  /* ---- KNN neighbor lookup for a test point ---- */
  const findKNeighbors = useCallback(
    (point: ScatterPoint, kVal: number) => {
      const distances = trainPoints.map(tp => ({
        point: tp,
        dist: euclidean(point, tp),
      }))
      distances.sort((a, b) => a.dist - b.dist)
      return distances.slice(0, kVal).map(d => d.point)
    },
    [trainPoints],
  )

  /* ---- Draw ---- */
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const dpr = window.devicePixelRatio || 1
    canvas.width = CANVAS_W * dpr
    canvas.height = CANVAS_H * dpr
    canvas.style.width = `${CANVAS_W}px`
    canvas.style.height = `${CANVAS_H}px`
    const ctx = canvas.getContext('2d')!
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

    // Clear
    ctx.clearRect(0, 0, CANVAS_W, CANVAS_H)

    // Background
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H)

    // ---- Decision mesh background ----
    const { x_values, y_values, predictions } = decision_mesh
    const meshRows = y_values.length
    const meshCols = x_values.length

    if (meshRows > 1 && meshCols > 1) {
      // Compute cell dimensions in canvas space
      // Use half-step extension so cells fill edge-to-edge
      const stepX = x_values.length > 1 ? (x_values[1] - x_values[0]) : 1
      const stepY = y_values.length > 1 ? (y_values[1] - y_values[0]) : 1

      for (let row = 0; row < meshRows; row++) {
        for (let col = 0; col < meshCols; col++) {
          const classIdx = predictions[row][col]
          const color = getColor(classIdx)

          const cx = toCanvasX(x_values[col] - stepX / 2)
          const cy = toCanvasY(y_values[row] + stepY / 2)
          const cw = toCanvasX(x_values[col] + stepX / 2) - cx
          const ch = toCanvasY(y_values[row] - stepY / 2) - cy

          ctx.fillStyle = color.fill
          ctx.fillRect(cx, cy, cw + 1, ch + 1)  // +1 to avoid hairline gaps
        }
      }
    }

    // ---- Grid lines ----
    ctx.strokeStyle = 'rgba(0,0,0,0.06)'
    ctx.lineWidth = 0.5
    const nGridLines = 6
    for (let i = 0; i <= nGridLines; i++) {
      const frac = i / nGridLines
      // Horizontal
      const gy = PAD.top + frac * plotH
      ctx.beginPath()
      ctx.moveTo(PAD.left, gy)
      ctx.lineTo(PAD.left + plotW, gy)
      ctx.stroke()
      // Vertical
      const gx = PAD.left + frac * plotW
      ctx.beginPath()
      ctx.moveTo(gx, PAD.top)
      ctx.lineTo(gx, PAD.top + plotH)
      ctx.stroke()
    }

    // ---- Plot border ----
    ctx.strokeStyle = 'rgba(0,0,0,0.12)'
    ctx.lineWidth = 1
    ctx.strokeRect(PAD.left, PAD.top, plotW, plotH)

    // ---- Axis tick labels ----
    ctx.fillStyle = '#6b778c'
    ctx.font = '10px -apple-system, BlinkMacSystemFont, sans-serif'
    ctx.textAlign = 'center'
    for (let i = 0; i <= nGridLines; i++) {
      const frac = i / nGridLines
      const xVal = mapping.xMin + frac * (mapping.xMax - mapping.xMin)
      ctx.fillText(xVal.toFixed(1), PAD.left + frac * plotW, PAD.top + plotH + 14)
      const yVal = mapping.yMax - frac * (mapping.yMax - mapping.yMin)
      ctx.textAlign = 'right'
      ctx.fillText(yVal.toFixed(1), PAD.left - 6, PAD.top + frac * plotH + 4)
      ctx.textAlign = 'center'
    }

    // ---- Hover: draw neighbor lines BEFORE points so points render on top ----
    if (hover && hover.point.split === 'test') {
      hover.neighbors.forEach(nb => {
        const nx = toCanvasX(nb.x)
        const ny = toCanvasY(nb.y)
        ctx.beginPath()
        ctx.moveTo(hover.canvasX, hover.canvasY)
        ctx.lineTo(nx, ny)
        ctx.strokeStyle = 'rgba(107, 114, 128, 0.35)'
        ctx.lineWidth = 1
        ctx.setLineDash([4, 3])
        ctx.stroke()
        ctx.setLineDash([])
      })
    }

    // ---- Train points ----
    trainPoints.forEach(p => {
      const cx = toCanvasX(p.x)
      const cy = toCanvasY(p.y)
      ctx.beginPath()
      ctx.arc(cx, cy, 3, 0, Math.PI * 2)
      ctx.fillStyle = getColor(p.label).solid
      ctx.globalAlpha = 0.75
      ctx.fill()
      ctx.globalAlpha = 1
    })

    // ---- Test points ----
    testPoints.forEach(p => {
      const cx = toCanvasX(p.x)
      const cy = toCanvasY(p.y)
      const isMisclassified = p.predicted !== null && p.predicted !== p.label

      // Filled circle
      ctx.beginPath()
      ctx.arc(cx, cy, 4.5, 0, Math.PI * 2)
      ctx.fillStyle = getColor(p.label).solid
      ctx.fill()

      // White border to distinguish from train
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 1.5
      ctx.stroke()

      // Misclassification indicator: red ring
      if (isMisclassified) {
        ctx.beginPath()
        ctx.arc(cx, cy, 7, 0, Math.PI * 2)
        ctx.strokeStyle = 'rgba(220, 53, 69, 0.85)'
        ctx.lineWidth = 1.8
        ctx.stroke()

        // Small X marker
        const s = 3
        ctx.beginPath()
        ctx.moveTo(cx - s, cy - s)
        ctx.lineTo(cx + s, cy + s)
        ctx.moveTo(cx + s, cy - s)
        ctx.lineTo(cx - s, cy + s)
        ctx.strokeStyle = 'rgba(220, 53, 69, 0.9)'
        ctx.lineWidth = 1.5
        ctx.stroke()
      }
    })

    // ---- Hover highlight ----
    if (hover) {
      const hx = hover.canvasX
      const hy = hover.canvasY
      // Highlight ring
      ctx.beginPath()
      ctx.arc(hx, hy, 9, 0, Math.PI * 2)
      ctx.strokeStyle = 'rgba(23, 43, 77, 0.6)'
      ctx.lineWidth = 2
      ctx.stroke()

      // Highlight neighbor points
      if (hover.point.split === 'test') {
        hover.neighbors.forEach(nb => {
          const nx = toCanvasX(nb.x)
          const ny = toCanvasY(nb.y)
          ctx.beginPath()
          ctx.arc(nx, ny, 6, 0, Math.PI * 2)
          ctx.strokeStyle = 'rgba(23, 43, 77, 0.5)'
          ctx.lineWidth = 1.5
          ctx.stroke()
        })
      }
    }

    // ---- Axis labels ----
    const pc1Var = pca_explained_variance[0] != null ? (pca_explained_variance[0] * 100).toFixed(1) : '?'
    const pc2Var = pca_explained_variance[1] != null ? (pca_explained_variance[1] * 100).toFixed(1) : '?'

    ctx.fillStyle = '#5e6c84'
    ctx.font = '11px -apple-system, BlinkMacSystemFont, sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(`PC1 (${pc1Var}%)`, PAD.left + plotW / 2, CANVAS_H - 10)

    ctx.save()
    ctx.translate(14, PAD.top + plotH / 2)
    ctx.rotate(-Math.PI / 2)
    ctx.fillText(`PC2 (${pc2Var}%)`, 0, 0)
    ctx.restore()

    // ---- Title ----
    ctx.fillStyle = '#172b4d'
    ctx.font = 'bold 13px -apple-system, BlinkMacSystemFont, sans-serif'
    ctx.textAlign = 'left'
    ctx.fillText(`KNN Decision Boundaries (K=${k})`, PAD.left, 18)

    // ---- Info badge ----
    const infoText = `${trainPoints.length} train \u00b7 ${testPoints.length} test points`
    ctx.font = '10px -apple-system, BlinkMacSystemFont, sans-serif'
    ctx.fillStyle = '#6b778c'
    ctx.textAlign = 'right'
    ctx.fillText(infoText, CANVAS_W - PAD.right, 18)

    // ---- Legend ----
    const legendY = CANVAS_H - 8
    const legendStartX = PAD.left
    ctx.textAlign = 'left'
    ctx.font = '10px -apple-system, BlinkMacSystemFont, sans-serif'
    let lx = legendStartX
    classes.forEach((cls, i) => {
      const color = getColor(i)
      // Swatch
      ctx.fillStyle = color.solid
      ctx.beginPath()
      ctx.arc(lx + 5, legendY - 3, 4, 0, Math.PI * 2)
      ctx.fill()
      // Label
      ctx.fillStyle = '#5e6c84'
      ctx.fillText(cls, lx + 13, legendY)
      lx += ctx.measureText(cls).width + 26
    })

    // Legend: train vs test indicator
    lx += 8
    // Train dot
    ctx.fillStyle = '#6b778c'
    ctx.beginPath()
    ctx.arc(lx + 4, legendY - 3, 3, 0, Math.PI * 2)
    ctx.fill()
    ctx.fillStyle = '#6b778c'
    ctx.fillText('Train', lx + 11, legendY)
    lx += ctx.measureText('Train').width + 22

    // Test dot (with white border)
    ctx.fillStyle = '#6b778c'
    ctx.beginPath()
    ctx.arc(lx + 4, legendY - 3, 4, 0, Math.PI * 2)
    ctx.fill()
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 1.5
    ctx.stroke()
    ctx.fillStyle = '#6b778c'
    ctx.fillText('Test', lx + 12, legendY)
    lx += ctx.measureText('Test').width + 22

    // Misclassified indicator
    ctx.strokeStyle = 'rgba(220, 53, 69, 0.85)'
    ctx.lineWidth = 1.5
    ctx.beginPath()
    ctx.arc(lx + 4, legendY - 3, 5, 0, Math.PI * 2)
    ctx.stroke()
    ctx.fillStyle = '#6b778c'
    ctx.fillText('Misclassified', lx + 13, legendY)
  }, [data, hover, mapping, toCanvasX, toCanvasY, trainPoints, testPoints, plotW, plotH, findKNeighbors, classes, k, pca_explained_variance, decision_mesh])

  /* ---- Mouse move handler ---- */
  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      const canvas = canvasRef.current
      if (!canvas) return
      const rect = canvas.getBoundingClientRect()
      const scaleX = CANVAS_W / rect.width
      const scaleY = CANVAS_H / rect.height
      const mx = (e.clientX - rect.left) * scaleX
      const my = (e.clientY - rect.top) * scaleY

      let bestIdx = -1
      let closestDist = Infinity
      let closestCX = 0
      let closestCY = 0

      for (let i = 0; i < scatter_points.length; i++) {
        const p = scatter_points[i]
        const cx = toCanvasX(p.x)
        const cy = toCanvasY(p.y)
        const d = Math.sqrt((mx - cx) ** 2 + (my - cy) ** 2)
        if (d < closestDist) {
          closestDist = d
          bestIdx = i
          closestCX = cx
          closestCY = cy
        }
      }

      if (bestIdx >= 0 && closestDist < 15) {
        const pt = scatter_points[bestIdx]
        const neighbors = pt.split === 'test' ? findKNeighbors(pt, k) : []
        setHover({ point: pt, canvasX: closestCX, canvasY: closestCY, neighbors })
      } else {
        setHover(null)
      }
    },
    [scatter_points, toCanvasX, toCanvasY, findKNeighbors, k],
  )

  const handleMouseLeave = useCallback(() => setHover(null), [])

  /* ---- Tooltip position (CSS-based overlay) ---- */
  const tooltipStyle = useMemo((): React.CSSProperties | null => {
    if (!hover || !containerRef.current) return null
    const containerRect = containerRef.current.getBoundingClientRect()
    const canvasEl = canvasRef.current
    if (!canvasEl) return null
    const canvasRect = canvasEl.getBoundingClientRect()

    const scaleX = canvasRect.width / CANVAS_W
    const scaleY = canvasRect.height / CANVAS_H
    const absX = canvasRect.left - containerRect.left + hover.canvasX * scaleX
    const absY = canvasRect.top - containerRect.top + hover.canvasY * scaleY

    // Position tooltip to the right, unless near edge
    const rightSide = absX < containerRect.width * 0.65
    return {
      position: 'absolute' as const,
      left: rightSide ? absX + 14 : undefined,
      right: rightSide ? undefined : containerRect.width - absX + 14,
      top: Math.max(0, absY - 20),
      pointerEvents: 'none' as const,
      zIndex: 10,
    }
  }, [hover])

  const trainCount = trainPoints.length
  const testCount = testPoints.length

  return (
    <div ref={containerRef} style={{ position: 'relative', width: '100%' }}>
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          maxWidth: CANVAS_W,
          height: 'auto',
          display: 'block',
          margin: '0 auto',
          borderRadius: 'var(--radius-md)',
          cursor: hover ? 'crosshair' : 'default',
        }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      />

      {/* Tooltip overlay */}
      {hover && tooltipStyle && (
        <div
          style={{
            ...tooltipStyle,
            background: 'var(--surface, #fff)',
            border: '1px solid var(--border, #dde3ec)',
            borderRadius: 'var(--radius-sm, 6px)',
            padding: '8px 11px',
            fontSize: '0.78rem',
            lineHeight: 1.55,
            color: 'var(--text-primary, #172b4d)',
            boxShadow: 'var(--shadow-md, 0 4px 12px rgba(0,0,0,0.1))',
            maxWidth: 220,
            whiteSpace: 'nowrap',
          }}
        >
          <div style={{ fontWeight: 600, marginBottom: 2 }}>
            <span
              style={{
                display: 'inline-block',
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: getColor(hover.point.label).solid,
                marginRight: 5,
                verticalAlign: 'middle',
              }}
            />
            {hover.point.label_name}
          </div>
          <div style={{ color: 'var(--text-secondary, #5e6c84)' }}>
            {hover.point.split === 'train' ? 'Training' : 'Test'} point
          </div>
          <div style={{ color: 'var(--text-muted, #6b778c)', fontSize: '0.72rem' }}>
            PC1: {hover.point.x.toFixed(2)}, PC2: {hover.point.y.toFixed(2)}
          </div>
          {hover.point.split === 'test' && hover.point.predicted !== null && (
            <div style={{ marginTop: 3 }}>
              <span style={{ color: 'var(--text-secondary)' }}>Predicted: </span>
              <span
                style={{
                  fontWeight: 600,
                  color:
                    hover.point.predicted === hover.point.label
                      ? 'var(--success, #1a7a4c)'
                      : 'var(--danger, #de350b)',
                }}
              >
                {classes[hover.point.predicted] || `Class ${hover.point.predicted}`}
                {hover.point.predicted === hover.point.label ? ' (correct)' : ' (wrong)'}
              </span>
            </div>
          )}
          {hover.point.split === 'test' && hover.neighbors.length > 0 && (
            <div style={{ marginTop: 3, fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              Showing {hover.neighbors.length} nearest neighbors
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default React.memo(KNNScatterCanvas)
