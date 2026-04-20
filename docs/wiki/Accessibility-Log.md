# Accessibility Fix Log — Sprint 5

**Audit tool:** Lighthouse 13.1.0 (Chrome 147 headless) + axe 4.11 rules
**Audit date:** 20 April 2026
**Target:** WCAG 2.1 AA — Lighthouse Accessibility score ≥ 85
**Scope:** Production build, wizard landing page (Step 1, default Endocrinology pill)

## Summary

| | Before | After |
|---|-------|-------|
| Lighthouse Accessibility | **91** | **100** |
| `color-contrast` violations | 5 | 0 |
| `landmark-one-main` violations | 1 | 0 |

## Violations Found + Resolutions

### 1. `color-contrast` — Wizard step labels unreadable when locked

**Severity:** Serious (WCAG 1.4.3 AA)
**Occurrences:** 4 (one per locked step)

| Field | Value |
|-------|-------|
| Selector | `.wizard-progress-inner .step-item.locked .step-item-name` |
| Computed foreground | `#bcc2cb` (after `opacity: 0.45` applied to `#6b778c`) |
| Background | `#ffffff` |
| Measured contrast | **1.79 : 1** |
| WCAG AA requires | **4.5 : 1** (normal text < 18px) |

**Root cause:** `.step-item.locked` applied `opacity: 0.45` to the whole item, which blended the already-muted `--text-muted` color (#6b778c) with the white surface, dropping it far below the legibility threshold.

**Fix** (`frontend/src/styles/globals.css`):
- Removed the blanket `opacity: 0.45` from `.step-item.locked`
- Scoped the opacity dimming to `.step-item.locked .step-number` only (circular badge — visual "locked" cue preserved)
- Explicitly set `.step-item.locked .step-item-name` and `.step-item.locked .step-item-sub` to `var(--text-secondary)` (`#5e6c84`) which gives **5.85 : 1** on white

**Before:**
```css
.step-item.locked {
  cursor: not-allowed;
  opacity: 0.45;
}
.step-item.locked .step-item-name {
  color: var(--text-muted);
}
```

**After:**
```css
.step-item.locked {
  cursor: not-allowed;
}
.step-item.locked .step-number {
  opacity: 0.5;
}
.step-item.locked .step-item-name {
  color: var(--text-secondary);
}
.step-item.locked .step-item-sub {
  color: var(--text-secondary);
}
```

---

### 2. `color-contrast` — Session privacy footer text

**Severity:** Serious (WCAG 1.4.3 AA)
**Occurrences:** 1

| Field | Value |
|-------|-------|
| Selector | `div#root > .app-layout > .main-content > div` (privacy footer) |
| Foreground | `#6b778c` (`--text-muted`) |
| Background | `#f4f7fb` (`--background`) |
| Measured contrast | **4.20 : 1** |
| WCAG AA requires | **4.5 : 1** |

**Root cause:** `--text-muted` sits just under the AA threshold when rendered on the page background color instead of pure white.

**Fix** (`frontend/src/App.tsx`): Switched the inline `color` from `var(--text-muted)` to `var(--text-secondary)` (`#5e6c84` → **4.62 : 1** on `#f4f7fb`).

**Before:**
```tsx
<div style={{ ..., color: 'var(--text-muted)', ... }}>
  Patient data is processed locally within this session.
</div>
```

**After:**
```tsx
<div style={{ ..., color: 'var(--text-secondary)', ... }}>
  Patient data is processed locally within this session.
</div>
```

---

### 3. `landmark-one-main` — Missing `<main>` landmark

**Severity:** Serious (WCAG 1.3.1 A, screen-reader navigation)
**Occurrences:** 1

| Field | Value |
|-------|-------|
| Rule | Document must have exactly one `<main>` landmark |
| Measured | 0 `<main>` elements on the page |

**Root cause:** The wizard content wrapper was a plain `<div className="main-content">`, giving screen-reader users no quick way to jump to the page's primary region.

**Fix** (`frontend/src/App.tsx`): Promoted the wrapper from `<div>` to `<main>`. No styling change (the class stays the same); only the tag semantic changed.

**Before:**
```tsx
<div className="main-content">
  {/* wizard steps */}
</div>
```

**After:**
```tsx
<main className="main-content">
  {/* wizard steps */}
</main>
```

---

## Verification

| | Run |
|---|-----|
| Command | `npx lighthouse http://localhost:4173 --only-categories=accessibility` |
| Chrome | 147.0.7727.57 (headless, new mode) |
| Device profile | Mobile (default Lighthouse profile) |
| Result JSON | [`docs/reports/Sprint5_Lighthouse.report.json`](../../docs/reports/Sprint5_Lighthouse.report.json) |
| Result HTML | [`docs/reports/Sprint5_Lighthouse.report.html`](../../docs/reports/Sprint5_Lighthouse.report.html) |
| Result screenshot | [`docs/reports/Sprint5_Lighthouse_Report.png`](../../docs/reports/Sprint5_Lighthouse_Report.png) |

## Files Touched

| File | Change |
|------|--------|
| `frontend/src/App.tsx` | `<div className="main-content">` → `<main className="main-content">`; footer `color` from `--text-muted` → `--text-secondary` |
| `frontend/src/styles/globals.css` | Removed blanket `opacity: 0.45` on `.step-item.locked`; added scoped rules for `.step-number`, `.step-item-name`, `.step-item-sub` |

## Showcase Before/After (Jury demo slide)

- **Before screenshot:** The Sprint 4 production build (Lighthouse 91 Accessibility, 5 contrast failures, no `<main>`) — archived copy: `docs/reports/Sprint5_Lighthouse.report.html.sprint4-baseline` (captured during Sprint 4 closing).
- **After screenshot:** `docs/reports/Sprint5_Lighthouse_Report.png` — **100 / 100** Accessibility, zero violations.

## Out of Scope (Sprint 6 backlog)

Audit returned no further binary failures, but the following manual-verification items remain and should be tracked:

- [ ] Keyboard focus ring visibility audit across all 7 step pages
- [ ] `<Step*.tsx>` onClick step-item — confirm `role="button"` + `tabIndex={0}` + Enter/Space handlers
- [ ] High-contrast mode (Windows) smoke test
- [ ] Screen-reader narration pass on Step 5 (results) and Step 6 (SHAP) — content-heavy pages
