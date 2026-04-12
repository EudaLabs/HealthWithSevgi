import React, { useRef, useEffect, useCallback, useMemo } from 'react';
import * as d3 from 'd3';
import type { CompareEntry, ModelType } from '../../types';

/* ------------------------------------------------------------------ */
/*  Constants                                                         */
/* ------------------------------------------------------------------ */

const MODEL_COLORS: Record<string, string> = {
  knn: '#36b5d8',
  svm: '#e8843c',
  decision_tree: '#f5c542',
  random_forest: '#4caf50',
  logistic_regression: '#ab47bc',
  naive_bayes: '#ef5350',
  xgboost: '#5c6bc0',
  lightgbm: '#26a69a',
};

const MODEL_LABELS: Record<ModelType, string> = {
  knn: 'KNN',
  svm: 'SVM',
  decision_tree: 'Decision Tree',
  random_forest: 'Random Forest',
  logistic_regression: 'Logistic Reg.',
  naive_bayes: 'Naive Bayes',
  xgboost: 'XGBoost',
  lightgbm: 'LightGBM',
};

const MARGIN = { top: 40, right: 40, bottom: 20, left: 40 };

const TRANSITION_MS = 200;

const OPACITY_DEFAULT = 0.65;
const OPACITY_DIM = 0.15;
const OPACITY_HIGHLIGHT = 1;

/* ------------------------------------------------------------------ */
/*  Axis definitions                                                  */
/* ------------------------------------------------------------------ */

interface AxisDef {
  key: string;
  label: string;
  type: 'numeric' | 'categorical';
  domain?: [number, number]; // fixed domain for numeric axes
}

const AXES: AxisDef[] = [
  { key: 'model_type', label: 'Model Type', type: 'categorical' },
  { key: 'auc_roc', label: 'AUC-ROC', type: 'numeric', domain: [0, 1] },
  { key: 'accuracy', label: 'Accuracy', type: 'numeric', domain: [0, 1] },
  { key: 'f1_score', label: 'F1 Score', type: 'numeric', domain: [0, 1] },
  { key: 'sensitivity', label: 'Sensitivity', type: 'numeric', domain: [0, 1] },
  { key: 'specificity', label: 'Specificity', type: 'numeric', domain: [0, 1] },
  { key: 'precision', label: 'Precision', type: 'numeric', domain: [0, 1] },
  { key: 'mcc', label: 'MCC', type: 'numeric', domain: [-1, 1] },
  { key: 'training_time_ms', label: 'Train Time (ms)', type: 'numeric' },
];

/* ------------------------------------------------------------------ */
/*  Props                                                             */
/* ------------------------------------------------------------------ */

interface ParallelCoordinatesChartProps {
  entries: CompareEntry[];
  onHover?: (modelId: string | null) => void;
  onPin?: (modelId: string) => void;
  pinnedIds?: Set<string>;
  hoveredId?: string | null;
  onTooltipMove?: (x: number, y: number) => void;
  onBrushChange?: (active: boolean) => void;
  resetBrushSignal?: number;
  height?: number;
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */

type RowValue = string | number;

/** Flatten a CompareEntry into a flat record keyed by axis key. */
function flattenEntry(entry: CompareEntry, displayLabel: string): Record<string, RowValue> {
  return {
    model_type: displayLabel,
    auc_roc: entry.metrics.auc_roc,
    accuracy: entry.metrics.accuracy,
    f1_score: entry.metrics.f1_score,
    sensitivity: entry.metrics.sensitivity,
    specificity: entry.metrics.specificity,
    precision: entry.metrics.precision,
    mcc: entry.metrics.mcc,
    training_time_ms: entry.training_time_ms,
  };
}

/** Build unique display labels for entries (e.g. "Random Forest #1", "Random Forest #2"). */
function buildDisplayLabels(entries: CompareEntry[]): Map<string, string> {
  const typeCounts = new Map<string, number>();
  const typeIndices = new Map<string, number>();
  for (const e of entries) {
    typeCounts.set(e.model_type, (typeCounts.get(e.model_type) ?? 0) + 1);
  }
  const labels = new Map<string, string>();
  for (const e of entries) {
    const base = MODEL_LABELS[e.model_type as ModelType] ?? e.model_type;
    const count = typeCounts.get(e.model_type) ?? 1;
    if (count === 1) {
      labels.set(e.model_id, base);
    } else {
      const idx = (typeIndices.get(e.model_type) ?? 0) + 1;
      typeIndices.set(e.model_type, idx);
      // Show key param values to help distinguish
      const paramHint = formatParamHint(e);
      labels.set(e.model_id, `${base} #${idx}${paramHint}`);
    }
  }
  return labels;
}

/** Format a short param hint for distinguishing duplicate model types. */
function formatParamHint(entry: CompareEntry): string {
  const p = entry.params;
  const parts: string[] = [];
  if (p.n_neighbors != null) parts.push(`k=${p.n_neighbors}`);
  if (p.kernel != null) parts.push(`${p.kernel}`);
  if (p.C != null) parts.push(`C=${p.C}`);
  if (p.n_estimators != null) parts.push(`n=${p.n_estimators}`);
  if (p.max_depth != null) parts.push(`d=${p.max_depth}`);
  if (p.learning_rate != null) parts.push(`lr=${p.learning_rate}`);
  if (parts.length === 0) return '';
  return ` (${parts.join(', ')})`;
}

type NumericScale = d3.ScaleLinear<number, number>;
type CategoricalScale = d3.ScalePoint<string>;
type AxisScale = NumericScale | CategoricalScale;

function isNumericScale(scale: AxisScale): scale is NumericScale {
  return 'invert' in scale;
}

/* ------------------------------------------------------------------ */
/*  Component                                                         */
/* ------------------------------------------------------------------ */

const ParallelCoordinatesChart: React.FC<ParallelCoordinatesChartProps> = ({
  entries,
  onHover,
  onPin,
  pinnedIds = new Set<string>(),
  onBrushChange,
  resetBrushSignal,
  height = 420,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const brushStateRef = useRef<Map<string, [number, number]>>(new Map());
  const widthRef = useRef<number>(800);

  /* ---- memoised flat data with unique labels ---- */
  const displayLabels = useMemo(() => buildDisplayLabels(entries), [entries]);
  const rows = useMemo(
    () => entries.map((e) => ({
      id: e.model_id,
      type: e.model_type,
      label: displayLabels.get(e.model_id) ?? e.model_type,
      values: flattenEntry(e, displayLabels.get(e.model_id) ?? e.model_type),
    })),
    [entries, displayLabels],
  );

  /* ---- build scales for every axis ---- */
  const buildScales = useCallback(
    (innerHeight: number) => {
      const scales = new Map<string, AxisScale>();

      for (const axis of AXES) {
        if (axis.type === 'categorical') {
          const categories = Array.from(new Set(rows.map((r) => String(r.values[axis.key]))));
          scales.set(
            axis.key,
            d3.scalePoint<string>().domain(categories).range([0, innerHeight]).padding(0.5),
          );
        } else {
          const vals = rows.map((r) => Number(r.values[axis.key]));
          const domain: [number, number] = axis.domain ?? [
            d3.min(vals) ?? 0,
            d3.max(vals) ?? 1,
          ];
          // For dynamic domains, add 5 % padding
          const padded: [number, number] = axis.domain
            ? domain
            : [domain[0] - (domain[1] - domain[0]) * 0.05, domain[1] + (domain[1] - domain[0]) * 0.05];
          scales.set(
            axis.key,
            d3.scaleLinear().domain(padded).range([innerHeight, 0]).nice(),
          );
        }
      }

      return scales;
    },
    [rows],
  );

  /* ---- main render ---- */
  const render = useCallback(() => {
    const svg = d3.select(svgRef.current);
    const container = containerRef.current;
    if (!container || !svgRef.current) return;

    const totalWidth = container.clientWidth;
    widthRef.current = totalWidth;
    const innerWidth = totalWidth - MARGIN.left - MARGIN.right;
    const innerHeight = height - MARGIN.top - MARGIN.bottom;

    if (innerWidth <= 0 || innerHeight <= 0) return;

    svg.attr('width', totalWidth).attr('height', height);

    // Clear previous render
    svg.selectAll('*').remove();

    // Drop-shadow filter for pinned lines
    const defs = svg.append('defs');
    const filter = defs.append('filter').attr('id', 'pc-glow');
    filter
      .append('feDropShadow')
      .attr('dx', 0)
      .attr('dy', 0)
      .attr('stdDeviation', 3)
      .attr('flood-opacity', 0.35);

    const g = svg
      .append('g')
      .attr('transform', `translate(${MARGIN.left},${MARGIN.top})`);

    // X position for each axis
    const xScale = d3
      .scalePoint<string>()
      .domain(AXES.map((a) => a.key))
      .range([0, innerWidth])
      .padding(0);

    const scales = buildScales(innerHeight);

    /* ---- helper: y-position of a value on its axis ---- */
    function yPos(axisKey: string, value: RowValue): number | undefined {
      const scale = scales.get(axisKey);
      if (!scale) return undefined;
      if (isNumericScale(scale)) {
        return scale(Number(value));
      }
      return scale(String(value));
    }

    /* ---- helper: is a row within all active brushes? ---- */
    function isRowBrushed(values: Record<string, RowValue>): boolean {
      for (const [axisKey, extent] of brushStateRef.current.entries()) {
        const scale = scales.get(axisKey);
        if (!scale || !isNumericScale(scale)) continue;
        const val = Number(values[axisKey]);
        const lo = scale.invert(extent[1]); // pixel extent is inverted (top < bottom)
        const hi = scale.invert(extent[0]);
        if (val < lo || val > hi) return false;
      }
      return true;
    }

    /* ---- draw axis lines and labels ---- */
    const axisGroups = g
      .selectAll<SVGGElement, AxisDef>('.pc-axis')
      .data(AXES)
      .enter()
      .append('g')
      .attr('class', 'pc-axis')
      .attr('transform', (d) => `translate(${xScale(d.key)},0)`);

    // Axis vertical line
    axisGroups
      .append('line')
      .attr('y1', 0)
      .attr('y2', innerHeight)
      .attr('stroke', '#dde3ec')
      .attr('stroke-width', 1);

    // Axis label
    axisGroups
      .append('text')
      .attr('class', 'pc-label')
      .attr('y', -14)
      .attr('text-anchor', 'middle')
      .attr('fill', '#5e6c84')
      .style('font-size', '0.75rem')
      .text((d) => d.label);

    // Tick marks
    axisGroups.each(function (axisDef) {
      const group = d3.select(this);
      const scale = scales.get(axisDef.key);
      if (!scale) return;

      if (axisDef.type === 'categorical') {
        const catScale = scale as CategoricalScale;
        catScale.domain().forEach((cat) => {
          const y = catScale(cat);
          if (y === undefined) return;
          group
            .append('text')
            .attr('class', 'pc-tick')
            .attr('x', 8)
            .attr('y', y)
            .attr('dy', '0.35em')
            .attr('text-anchor', 'start')
            .attr('fill', '#6b778c')
            .style('font-size', '0.7rem')
            .text(cat);
        });
      } else {
        const numScale = scale as NumericScale;
        const ticks = numScale.ticks(5);
        ticks.forEach((t) => {
          group
            .append('text')
            .attr('class', 'pc-tick')
            .attr('x', -8)
            .attr('y', numScale(t))
            .attr('dy', '0.35em')
            .attr('text-anchor', 'end')
            .attr('fill', '#6b778c')
            .style('font-size', '0.7rem')
            .text(axisDef.key === 'training_time_ms' ? d3.format(',.0f')(t) : d3.format('.2f')(t));
        });
      }
    });

    /* ---- draw polylines ---- */
    const lineGenerator = (values: Record<string, RowValue>) => {
      const points: [number, number][] = [];
      for (const axis of AXES) {
        const x = xScale(axis.key);
        const y = yPos(axis.key, values[axis.key]);
        if (x !== undefined && y !== undefined) {
          points.push([x, y]);
        }
      }
      return d3.line()(points);
    };

    const linesGroup = g.append('g').attr('class', 'pc-lines');

    const lines = linesGroup
      .selectAll<SVGPathElement, (typeof rows)[number]>('.pc-line')
      .data(rows, (d) => d.id)
      .enter()
      .append('path')
      .attr('class', 'pc-line')
      .attr('d', (d) => lineGenerator(d.values))
      .attr('fill', 'none')
      .attr('stroke', (d) => MODEL_COLORS[d.type] ?? '#888')
      .attr('stroke-linecap', 'round')
      .attr('stroke-linejoin', 'round')
      .style('stroke-width', (d) => (pinnedIds.has(d.id) ? 2.5 : 2))
      .style('opacity', (d) => {
        if (!isRowBrushed(d.values)) return '0';
        return String(pinnedIds.has(d.id) ? OPACITY_HIGHLIGHT : OPACITY_DEFAULT);
      })
      .style('filter', (d) => (pinnedIds.has(d.id) ? 'url(#pc-glow)' : 'none'))
      .style('cursor', 'pointer')
      .style('pointer-events', 'stroke');

    /* ---- tooltip helpers ---- */
    function showTooltip(event: MouseEvent, row: (typeof rows)[number]) {
      const tooltip = d3.select(tooltipRef.current);
      if (!tooltip.node()) return;

      const vals = row.values;
      const html = `
        <div class="pc-tooltip-title" style="color:${MODEL_COLORS[row.type] ?? '#888'}">
          ${row.label}
        </div>
        <div class="pc-tooltip-row">AUC-ROC: <b>${Number(vals.auc_roc).toFixed(4)}</b></div>
        <div class="pc-tooltip-row">Accuracy: <b>${Number(vals.accuracy).toFixed(4)}</b></div>
        <div class="pc-tooltip-row">F1: <b>${Number(vals.f1_score).toFixed(4)}</b></div>
        <div class="pc-tooltip-row">Sensitivity: <b>${Number(vals.sensitivity).toFixed(4)}</b></div>
        <div class="pc-tooltip-row">Specificity: <b>${Number(vals.specificity).toFixed(4)}</b></div>
        <div class="pc-tooltip-row">Precision: <b>${Number(vals.precision).toFixed(4)}</b></div>
        <div class="pc-tooltip-row">MCC: <b>${Number(vals.mcc).toFixed(4)}</b></div>
        <div class="pc-tooltip-row">Train Time: <b>${Number(vals.training_time_ms).toFixed(1)} ms</b></div>
      `;
      tooltip.html(html);

      const containerRect = containerRef.current?.getBoundingClientRect();
      if (!containerRect) return;
      const x = event.clientX - containerRect.left + 14;
      const y = event.clientY - containerRect.top - 10;
      tooltip
        .style('left', `${x}px`)
        .style('top', `${y}px`)
        .style('opacity', '1')
        .style('pointer-events', 'none');
    }

    function hideTooltip() {
      d3.select(tooltipRef.current).style('opacity', '0');
    }

    /* ---- hover / click interactions ---- */
    function handleMouseEnter(_event: MouseEvent, row: (typeof rows)[number]) {
      // Highlight hovered line, dim others (unless pinned)
      lines
        .transition()
        .duration(TRANSITION_MS)
        .ease(d3.easeQuadOut)
        .style('opacity', (d) => {
          if (!isRowBrushed(d.values)) return '0';
          if (d.id === row.id || pinnedIds.has(d.id)) return String(OPACITY_HIGHLIGHT);
          return String(OPACITY_DIM);
        })
        .style('stroke-width', (d) => {
          if (d.id === row.id) return '3';
          if (pinnedIds.has(d.id)) return '2.5';
          return '2';
        });

      onHover?.(row.id);
    }

    function handleMouseLeave() {
      lines
        .transition()
        .duration(TRANSITION_MS)
        .ease(d3.easeQuadOut)
        .style('opacity', (d) => {
          if (!isRowBrushed(d.values)) return '0';
          return String(pinnedIds.has(d.id) ? OPACITY_HIGHLIGHT : OPACITY_DEFAULT);
        })
        .style('stroke-width', (d) => (pinnedIds.has(d.id) ? '2.5' : '2'));

      hideTooltip();
      onHover?.(null);
    }

    function handleClick(_event: MouseEvent, row: (typeof rows)[number]) {
      onPin?.(row.id);
    }

    lines
      .on('mouseenter', function (event, d) {
        handleMouseEnter(event as MouseEvent, d);
        showTooltip(event as MouseEvent, d);
      })
      .on('mousemove', function (event, d) {
        showTooltip(event as MouseEvent, d);
      })
      .on('mouseleave', function () {
        handleMouseLeave();
      })
      .on('click', function (event, d) {
        handleClick(event as MouseEvent, d);
      });

    /* ---- brush on numeric axes (drawn on top layer so drag is never blocked) ---- */
    const brushWidth = 30;
    const brushLayer = g.append('g').attr('class', 'pc-brush-layer');

    AXES.filter((a) => a.type === 'numeric').forEach((axisDef) => {
      const axisX = xScale(axisDef.key);
      if (axisX === undefined) return;

      const brush = d3
        .brushY()
        .extent([
          [-brushWidth / 2, 0],
          [brushWidth / 2, innerHeight],
        ])
        .on('brush end', function (event: d3.D3BrushEvent<AxisDef>) {
          if (event.selection) {
            brushStateRef.current.set(axisDef.key, event.selection as [number, number]);
          } else {
            brushStateRef.current.delete(axisDef.key);
          }

          // Update line visibility
          lines
            .transition()
            .duration(TRANSITION_MS)
            .style('opacity', (d) => {
              if (!isRowBrushed(d.values)) return '0';
              return String(pinnedIds.has(d.id) ? OPACITY_HIGHLIGHT : OPACITY_DEFAULT);
            });
          onBrushChange?.(brushStateRef.current.size > 0);
        });

      const brushG = brushLayer
        .append('g')
        .attr('class', 'pc-brush')
        .attr('transform', `translate(${axisX},0)`)
        .call(brush);

      // Restore brush if previously set
      const prev = brushStateRef.current.get(axisDef.key);
      if (prev) {
        brushG.call(brush.move, prev);
      }

      // Style the brush selection rectangle
      brushG
        .selectAll('.selection')
        .attr('fill', '#1a7a4c')
        .attr('fill-opacity', 0.12)
        .attr('stroke', '#1a7a4c')
        .attr('stroke-width', 1);
    });
  }, [rows, buildScales, height, pinnedIds, onHover, onPin, onBrushChange]);

  /* ---- effect: render on data/size changes ---- */
  useEffect(() => {
    render();
  }, [render]);

  /* ---- effect: reset brushes from parent ---- */
  useEffect(() => {
    if (resetBrushSignal === undefined) return;
    brushStateRef.current.clear();
    onBrushChange?.(false);
    render();
  }, [resetBrushSignal, onBrushChange, render]);

  /* ---- effect: ResizeObserver ---- */
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const observer = new ResizeObserver(() => {
      render();
    });

    observer.observe(container);

    return () => {
      observer.disconnect();
    };
  }, [render]);

  /* ---- early return for empty data ---- */
  if (entries.length === 0) {
    return (
      <div className="parallel-coords-chart pc-empty">
        <p>No models to compare. Train at least two models to see the parallel coordinates chart.</p>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="parallel-coords-chart" style={{ position: 'relative' }}>
      <svg ref={svgRef} />
      <div ref={tooltipRef} className="pc-tooltip" style={{ opacity: 0 }} />
    </div>
  );
};

export default ParallelCoordinatesChart;
