# Sprint 5 QA Automation — Design Spec

**Status:** Draft (awaiting approval)
**Author:** Batuhan (with Claude as co-designer)
**Date:** 2026-04-21
**Scope:** Sprint 5 deliverables #14 (Full Domain Coverage — 20 specialties × Step 1–7) and #15 (E2E Regression — 3 CSVs × 0 crashes)
**Non-goals:** Replace real-user usability test (#11), replace signed consent form (#12), or replace human-recorded usability video (#13)

## Problem

Sprint 5 (Apr 16 – Apr 29, 2026) closes with four QA artefacts that today have placeholder rows on the wiki:

| # | Deliverable | Current status |
|---|-------------|---------------|
| #14 | Full Domain Coverage — 20 specialties Step 1–7 | PENDING (QA) |
| #15 | E2E Regression — 3 CSVs, 0 crashes | PENDING (QA) |
| #11 / #12 / #13 | User testing with real non-CS participant + consent + usability video | PENDING (QA) |

Deliverables #14 and #15 are **deterministic walkthrough proofs** — the same wizard flow executed against the 7-step pipeline, once per specialty or CSV, with evidence captured. They are therefore **automatable** and must be delivered before the Apr 29 jury showcase.

This spec defines an automation pipeline that uses `agent-browser` (Vercel Labs, v0.26.0, installed globally) to produce:

- `Sprint5_Full_Domain_Coverage.{html,pdf}` — 20 specialty × 13-screenshot walkthrough
- `Sprint5_E2E_Regression.{html,pdf}` — 3 CSV × 13-screenshot walkthrough (custom-upload variant)

Both reports must read as though a careful human performed the walkthrough by hand, with step-labelled screenshots, human-tone descriptions, per-step timings, and a final pass/fail summary table. Reports match the Sprint 2 house style (green gradient, cover + TOC + figure blocks + print-optimised CSS).

## Scope summary — decisions taken during brainstorming

| Dimension | Decision | Reason |
|-----------|----------|--------|
| Target environment | Live HuggingFace Space (`https://0xbatuhan4-healthwithsevgi.hf.space/`) | Jury-grade production evidence; not "works on my machine" |
| Report layout | Two separate HTML/PDF per deliverable | Matches Sprint-5.md deliverable rows; cleaner wiki links |
| Evidence depth | 13 screenshots per specialty | Matches Sprint 2 narrative depth; named `NN_specialty_stepN_action.png` |
| Parallelism | 4-parallel subagent batches (5 waves × 4 = 20) | Balances HF Space load vs. runtime; isolates failures |
| #15 CSV set | 3 different specialty CSVs (diabetes, cardiology_hf, oncology_breast) | Proves generic pipeline on custom-upload path |
| Worker design | Scripted worker + dumb subagent (Option A) | Reproducible evidence trumps self-healing adaptivity |
| PDF pipeline | Chrome headless `--print-to-pdf` | Existing Sprint 2 print CSS already tuned for Chrome |

## Architecture

Three layers, each with a narrow responsibility and a well-defined interface.

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1 — Capture                                          │
│  scripts/qa/walkthrough.sh <specialty_id> <out_dir>         │
│    - 13 deterministic agent-browser steps                   │
│    - Emits 13 PNGs + evidence.json + walkthrough.log        │
└─────────────────────────────────────────────────────────────┘
                       │  fan-out 4-wide
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2 — Orchestration (two modes, same output)           │
│                                                              │
│  Mode A: Claude subagents (interactive)                     │
│    parent fires 4× Agent(general-purpose) per wave          │
│    each subagent runs one walkthrough.sh invocation         │
│                                                              │
│  Mode B: scripts/qa/orchestrate.sh (CI / manual)            │
│    xargs -P4 bash walkthrough.sh                            │
│                                                              │
│  Both write per-specialty evidence.json; orchestrator       │
│  merges them into MANIFEST.json                             │
└─────────────────────────────────────────────────────────────┘
                       │  manifest + screenshots
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3 — Render                                           │
│  scripts/qa/render_report.py <run_dir>                      │
│    - jinja2 template + Sprint 2 CSS → HTML                  │
│    - google-chrome --headless --print-to-pdf → PDF          │
└─────────────────────────────────────────────────────────────┘
```

### Why three layers

- **Separation of concerns:** a flaky capture does not require re-rendering; a template change does not require re-capturing.
- **Reusability:** Mode A / Mode B orchestrators call the same worker, so CI and interactive runs stay equivalent.
- **Testability:** each layer has its own self-test (`tests/test_walkthrough_dry.sh`, `tests/test_render_fake.py`), so we can verify one layer without exercising the others.

## Directory layout

```
scripts/qa/
├── walkthrough.sh                 # Layer 1 — per-specialty worker (happy path)
├── walkthrough_upload.sh          # Layer 1 variant — custom-upload flow (#15)
├── orchestrate.sh                 # Layer 2 bash mode
├── merge_manifest.py              # Layer 2 aggregator (evidence.json → MANIFEST.json)
├── render_report.py               # Layer 3 — HTML + PDF rendering
├── lib/
│   ├── ab_helpers.sh              # click_pill, upload_csv, wait_step, ss, retry, log
│   ├── specialty_list.txt         # 20 IDs, newline-separated
│   ├── regression_csvs.txt        # 3 CSV paths for #15
│   └── wizard_step_labels.py      # shared constants for step names
├── templates/
│   ├── base.html.j2               # cover + TOC + global CSS (Sprint 2 reused)
│   ├── full_coverage.html.j2      # #14
│   ├── e2e_regression.html.j2     # #15
│   └── partials/
│       ├── _cover.html.j2
│       ├── _toc.html.j2
│       ├── _specialty_section.html.j2
│       ├── _figure_block.html.j2
│       └── _summary_table.html.j2
└── tests/
    ├── test_walkthrough_dry.sh    # --dry-run on walkthrough.sh
    ├── test_render_fake.py        # fake MANIFEST → HTML parse check
    ├── test_smoke_live.sh         # 1 specialty × 3 steps against live HF
    └── fixtures/
        └── fake_manifest.json

docs/reports/qa/
├── full-coverage-2026-04-21/      # committed
│   ├── screenshots/               # 260 PNGs (20 × 13)
│   ├── evidence/                  # 20 × evidence.json (per-specialty)
│   ├── MANIFEST.json              # merged aggregate
│   ├── Sprint5_Full_Domain_Coverage.html
│   └── Sprint5_Full_Domain_Coverage.pdf
└── e2e-regression-2026-04-21/
    ├── screenshots/               # 39 PNGs (3 × 13)
    ├── evidence/
    ├── MANIFEST.json
    ├── Sprint5_E2E_Regression.html
    └── Sprint5_E2E_Regression.pdf
```

`.gitignore` carve-out: keep `docs/reports/qa/**/*.log` ignored but commit everything else.

## Layer 1 — `walkthrough.sh` contract

### Signature

```bash
walkthrough.sh <specialty_id> <out_dir>
# $1 = one of the 20 IDs in specialty_list.txt
# $2 = absolute path; will contain screenshots/, evidence.json, walkthrough.log
```

### Resilience guarantees ("güzel yapmamız lazım, patlamayalım")

| # | Problem | Mitigation |
|---|---------|-----------|
| 1 | HF Space cold-start latency (up to 30 s) | First `nav_home` gets 120 s timeout; waits for "Select a specialty" text |
| 2 | Column Mapper sometimes auto-opens, sometimes manual | `wait_mapper()` tries auto-popup for 10 s, then clicks "Open Column Mapper" |
| 3 | Rate-limit 429s | 3-strike detector via `network requests`; if seen, 30 s cooldown |
| 4 | Training occasionally takes 90 s+ | `train_and_wait` uses 180 s timeout, polls progress every 10 s |
| 5 | Screenshot during animation | Every `ss` call waits for `network idle` + 500 ms stabilisation |
| 6 | Second run leaves stale PNGs | Script starts with `rm -rf "$OUT_DIR/screenshots"` |
| 7 | Orchestrator crash loses progress | Each `evidence.json` written atomically; orchestrator skips specialties whose `evidence.json.status == pass` |
| 8 | Binary versions drift | Start-of-run logs `agent-browser --version` and Chrome version; persisted in evidence.json |
| 9 | Indefinite wait on missing element | Every `wait` has mandatory `--timeout`; no unbounded blocking |
| 10 | Lost error context | Each step on failure dumps stderr tail + console-errors + network-failures into evidence.json |

### Step list (13 deterministic steps, one screenshot each)

```bash
run_step "01_homepage"              15000  'text_visible "Select a specialty"'      nav_home
run_step "02_specialty_selected"    15000  'text_visible "$(label $SPECIALTY)"'     select_pill
run_step "03_csv_uploaded"          60000  'text_visible "Column Mapper"'           upload_default_csv
run_step "04_mapper_default"        10000  'element_visible ".mapper-row"'          screenshot_as mapper-default
run_step "05_mapper_validated"      20000  'text_visible "Saved"'                   validate_and_save
run_step "06_prep_applied"          30000  'text_visible "Preparation applied"'     apply_prep_defaults
run_step "07_prep_banner"           10000  'text_visible "Step 4"'                  go_to_step4
run_step "08_model_params"          15000  'element_visible "[data-model=knn]"'     pick_knn_and_defaults
run_step "09_training_done"        180000  'text_visible "Training complete"'       train_and_wait
run_step "10_step5_metrics"         15000  'text_visible "Sensitivity"'             open_step5_capture
run_step "11_step6_top_feature"     30000  'element_visible ".feature-chart"'       open_step6_capture
run_step "12_step7_ethics"          30000  'text_visible "Ethics"'                  open_step7_capture
run_step "13_cert_downloaded"       30000  'file_exists "$OUT_DIR/cert.pdf"'        download_cert
```

### `run_step` wrapper

```bash
run_step <name> <timeout_ms> <sanity_check> <action...>
```

For each step:
1. Timeout-limit the action (`timeout <ms/1000>`).
2. Run the action; on success, evaluate `sanity_check`; on failure, retry up to 2× with 2 s / 4 s backoff.
3. Capture a post-state screenshot named `NN_specialty_stepWIZARD_action.png`.
4. If all retries failed, capture a `*_FAIL.png` and append `failures[]` to evidence.json.
5. Hard-exit the script for critical steps (`03_csv_uploaded`, `09_training_done`, `13_cert_downloaded`); continue-with-flag for soft steps.
6. Regardless of outcome, append `steps[]` entry with `{ seq, name, status, duration_ms, screenshot }`.

### Screenshot naming convention

```
NN_{specialty_id}_step{wizard_N}_{action}.png
```

- `NN` — zero-padded sequence within this specialty (01–13).
- `specialty_id` — snake_case from `specialty_list.txt` (e.g. `endocrinology_diabetes`).
- `wizard_N` — the wizard step the screenshot belongs to (1–7).
- `action` — kebab-case past-tense (`homepage`, `specialty-selected`, `csv-uploaded`, `mapper-default`, `mapper-validated`, `prep-applied`, `prep-banner`, `model-params`, `training-done`, `step5-metrics`, `step6-top-feature`, `step7-ethics`, `cert-downloaded`).

Examples:
- `01_endocrinology_diabetes_step1_homepage.png`
- `09_cardiology_hf_step4_training-done.png`
- `13_oncology_breast_step7_cert-downloaded.png`

### `evidence.json` schema

```json
{
  "specialty": "endocrinology_diabetes",
  "base_url": "https://0xbatuhan4-healthwithsevgi.hf.space",
  "started_at": "2026-04-21T10:15:03Z",
  "finished_at": "2026-04-21T10:16:29Z",
  "duration_ms": 86421,
  "agent_browser_version": "0.26.0",
  "chrome_version": "131.0.6778.204",
  "status": "pass",
  "steps": [
    {
      "seq": 1,
      "name": "01_homepage",
      "wizard_step": 1,
      "label": "Homepage loaded",
      "human_description": "Landing page rendered; domain pill bar visible with all 20 specialties.",
      "status": "pass",
      "duration_ms": 2131,
      "screenshot": "01_endocrinology_diabetes_step1_homepage.png"
    }
  ],
  "console_errors": [],
  "network_failures": [],
  "failures": []
}
```

## Layer 2 — Orchestrator contract

### Mode A — Claude subagents (interactive session)

The parent Claude runs 5 waves of 4 parallel `Agent(subagent_type=general-purpose)` calls. Each subagent receives a tightly constrained prompt:

```
Run exactly one bash command and report back in under 80 words.

Command:
  bash /home/batuhan4/HealthWithSevgi/scripts/qa/walkthrough.sh \
    {SPECIALTY_ID} \
    /home/batuhan4/HealthWithSevgi/docs/reports/qa/full-coverage-{DATE}/{SPECIALTY_ID}

After it finishes, read the evidence.json at:
  docs/reports/qa/full-coverage-{DATE}/{SPECIALTY_ID}/evidence.json

Report (in this exact shape):
  - specialty: {SPECIALTY_ID}
  - status: pass|fail
  - duration: {duration_ms}ms
  - failed_steps: list or none
  - screenshots_count: integer (13 expected)

RULES: Do not modify walkthrough.sh. Do not invent alternative commands.
Do not attempt self-healing. Run, read, report.
```

The tightly-scoped prompt is load-bearing — giving the subagent freedom to "fix" the flow destroys reproducibility.

### Mode B — `orchestrate.sh`

```bash
SPECIALTIES=$(grep -v '^#' lib/specialty_list.txt | grep -v '^$')
OUT_BASE="docs/reports/qa/full-coverage-$(date +%F)"

# Resume-safe: skip specialties whose evidence.json already says pass
PENDING=$(python3 scripts/qa/pending.py "$OUT_BASE" $SPECIALTIES)

# 4-wide parallel
echo "$PENDING" | xargs -P4 -I{} bash -c \
  'bash scripts/qa/walkthrough.sh "$1" "'"$OUT_BASE"'/$1" || echo "FAIL: $1"' _ {}

python3 scripts/qa/merge_manifest.py "$OUT_BASE"
python3 scripts/qa/render_report.py "$OUT_BASE"
```

### Orchestrator-level failure handling

| Scenario | Parent action |
|----------|---------------|
| Subagent reports `status: fail` | Record in MANIFEST, continue to next wave |
| 4/4 fail in one wave | Pause; ask user whether HF Space is down or to continue |
| Subagent exceeds 5 min (no return) | Kill session, record `failures: [{ reason: "subagent_timeout" }]` |
| Parent session compacts / restarts | Next invocation re-derives `PENDING` from existing evidence.json files |

### `MANIFEST.json` shape

```json
{
  "run_id": "full-coverage-2026-04-21",
  "started_at": "2026-04-21T10:00:00Z",
  "finished_at": "2026-04-21T10:35:12Z",
  "base_url": "https://0xbatuhan4-healthwithsevgi.hf.space",
  "summary": {
    "total": 20,
    "pass": 19,
    "fail": 1,
    "skipped": 0,
    "avg_duration_ms": 85412
  },
  "specialties": {
    "endocrinology_diabetes": { /* full evidence.json */ },
    "cardiology_hf":          { /* full evidence.json */ }
  }
}
```

## Layer 3 — `render_report.py` contract

### Pipeline

1. Load `MANIFEST.json`.
2. Render the jinja2 template (either `full_coverage.html.j2` or `e2e_regression.html.j2`).
3. Write the HTML to the run directory.
4. Invoke Chrome headless to produce the PDF.

```python
subprocess.run([
    "google-chrome", "--headless=new", "--disable-gpu",
    f"--print-to-pdf={pdf_path}",
    "--no-pdf-header-footer",      # let CSS @page handle margins
    "--virtual-time-budget=5000",  # give fonts time to load
    f"file://{html_path.resolve()}"
], check=True)
```

### HTML structure

Reuse the Sprint 2 Screenshot Report CSS verbatim (green gradient, A4 print tuning, figure blocks). The document structure:

1. **Cover page** — logo, title, sprint metadata, run timestamp, base URL, environment.
2. **TOC** — one entry per specialty, one per summary section.
3. **Specialty sections** (one per specialty, each on a new printed page):
   - Green section header with specialty name + pass/fail stamp + dataset + row count + duration.
   - `req-check` bar: "Step 1–7 completed · KNN trained · Certificate downloaded".
   - 13 figure blocks grouped by wizard step (§2 headers: "Step 1 — Clinical Context", etc.).
4. **Summary section** — 20-row table (specialty, dataset, duration, failed steps, status) with pass/fail stamps and an aggregate row.

### Template partials

- `partials/_cover.html.j2` — cover page.
- `partials/_toc.html.j2` — auto-generated TOC from `manifest.specialties.keys()`.
- `partials/_specialty_section.html.j2` — one specialty's 13 figures, grouped by wizard step.
- `partials/_figure_block.html.j2` — a single `figure-block` with title/desc/img/caption/timing.
- `partials/_summary_table.html.j2` — final summary table.

### "Looks like a human did it" signals

1. `evidence.json.steps[].human_description` — past-tense, observational: *"Selected the Diabetes pill; Step 1 indicator moved to the active state"*. The template prints this as `.figure-desc`.
2. Per-step timings in natural units: *"Training completed in 42.1 s"*.
3. Global `Figure 1 … Figure 260` numbering across the document, not restarted per specialty.
4. Per-specialty `observations[]` — anomalies called out in a short bullet list (e.g. *"Warning banner appeared during upload; cleared after retry"*).
5. Sprint 2 visual style — green gradient, cover page, A4 print margins make it read like an existing company document, not a CI dump.

## Failure handling end-to-end

### Layer 1 (script)
- `set -euo pipefail` + `trap ERR`
- `run_step` wraps every step with retry + screenshot-on-fail + evidence.json entry
- Critical-step failure triggers hard-exit; soft-step failure continues
- `finalize_evidence()` runs via `trap EXIT` so partial data is always persisted

### Layer 2 (orchestrator)
- 5-minute hard timeout per subagent
- Wave-level trip: 4/4 failures in a wave pauses the run and prompts the user
- Resume on re-invocation via `PENDING` derivation

### Layer 3 (render)
- Missing screenshot → placeholder PNG + caption "capture missed"
- `status == fail` step → `.figure-fail` class (red border)
- Missing `MANIFEST.json` → clear error, no partial output

### User-facing summary (printed by parent Claude after the run)

```
Full Coverage run — 2026-04-21T10:35:12Z complete
──────────────────────────────────────────────────
Total:      20 specialties
PASS:       19
FAIL:       1 (nephrology_ckd — step 09_training_done timeout)
Duration:   32m 14s (4-wide parallel)
Avg/spec:   1m 35s

Failure detail:
  nephrology_ckd
    └─ 09_training_done (180 s timeout) — training never completed
    └─ Screenshot: docs/reports/.../screenshots/09_nephrology_ckd_step4_training-done_FAIL.png
    └─ Console errors: "POST /api/train returned 500"

Recommendation: retry nephrology_ckd solo, or accept 19/20 for the report?
```

## #15 E2E Regression — deltas from #14

Reuses the same infrastructure, but the **entry point** differs: the user uploads a custom CSV instead of clicking a specialty pill.

| Dimension | #14 Full Coverage | #15 E2E Regression |
|-----------|-------------------|---------------------|
| Entry path | Specialty pill → pre-loaded CSV | Custom Upload CSV → user-chosen file |
| Count | 20 specialties | 3 CSVs |
| Screenshots/item | 13 | 13 |
| Model type | KNN only | Rotated: KNN + Random Forest + XGBoost (one per CSV) — broader assertion |
| Assertions | Training complete + certificate downloaded | Same **plus** 0 console errors **and** 0 network failures (regression-grade) |
| Template | `full_coverage.html.j2` | `e2e_regression.html.j2` (cover notes model type per CSV) |
| Script | `walkthrough.sh` | `walkthrough_upload.sh` (steps 01–02 differ, remainder reused) |
| Parallelism | 4-wide | Serial (only 3; parallel gives no wall-clock win) |

`walkthrough_upload.sh` overrides only the first two steps:
- `01_homepage` — asserts "Upload Custom CSV" button is visible.
- `02_csv_selected_via_file_picker` — uses `agent-browser upload` to feed the CSV, verifies auto-inferred specialty badge appears.

Steps 03–13 are sourced from the same `lib/ab_helpers.sh`.

## Self-tests

```
scripts/qa/tests/
├── test_walkthrough_dry.sh    # shellcheck + bash -n + agent-browser mocked
├── test_render_fake.py        # fake MANIFEST → render → html5lib parse
├── test_smoke_live.sh         # 1 specialty × 3 steps against live HF (CI daily)
└── fixtures/
    └── fake_manifest.json     # 20 specialties + 1 intentional fail scenario
```

- **`test_walkthrough_dry.sh`:** runs `bash -n walkthrough.sh` (syntax check), then invokes each helper under a mocked `agent-browser` stub that simply echoes its arguments. Catches typos and helper regressions without hitting the network.
- **`test_render_fake.py`:** loads `fake_manifest.json`, renders both templates, parses the result with `html5lib`, asserts every specialty section is present and no template placeholder (`{{ `) leaks through.
- **`test_smoke_live.sh`:** CI-friendly sanity check against live HF Space. Runs `endocrinology_diabetes` through the first three steps only (~30 s). Wired to `on: schedule: '0 6 * * *'` so we notice HF Space drift within 24 h.

## Output artefacts & commit policy

- `docs/reports/qa/full-coverage-YYYY-MM-DD/` — committed in full (evidence for jury + wiki).
- `docs/reports/qa/e2e-regression-YYYY-MM-DD/` — committed in full.
- `docs/reports/qa/**/*.log` — `.gitignore`-d.
- Expected sizes: #14 ≈ 55 MB (260 PNGs + 1 PDF), #15 ≈ 8 MB. Below Git LFS threshold; migrate to LFS if future sprints push repo past ~250 MB.

## Success criteria

The spec is delivered when:

1. `bash scripts/qa/walkthrough.sh endocrinology_diabetes /tmp/ab-sanity` produces 13 PNGs + `evidence.json` with `status: pass`.
2. Running Mode A orchestration (parent Claude + subagents) completes all 20 specialties in ≤ 40 minutes with ≥ 19/20 pass.
3. `Sprint5_Full_Domain_Coverage.pdf` renders to A4 with correct cover, TOC, 20 specialty sections, and a summary table.
4. `Sprint5_E2E_Regression.pdf` renders the 3 CSVs with 0 console errors and 0 network failures across all nine steps 10–13 (metrics, explainability, ethics, certificate).
5. Sprint-5.md rows #14 / #15 can be updated from `PENDING (QA)` → `DONE` with links to the committed PDFs.
6. Re-invoking `orchestrate.sh` after a partial failure completes only the missing specialties (resume-safe proved).

## Open questions / assumptions

- **Assumption:** the live HF Space accepts concurrent 4-session browser traffic without server-side throttling. If 429s dominate, step down to 2-wide; if still, serial. Mitigation is built into Layer 1 (rate-limit detector).
- **Assumption:** `agent-browser upload` can drive the `<input type="file">` on the CSV upload card. Verified against the v0.26.0 CLI docs; first dry-run of `walkthrough_upload.sh` will confirm against the real UI.
- **Open:** whether to fail the jury-grade report on a single specialty failure, or present it as "19/20 PASS + explained failure". Default: present the honest 19/20 with a visible failure section; jury values transparency over staged perfection.
- **Open:** do we also capture a single-take video recording of one specialty walkthrough (using `agent-browser video start/stop`) as a supplementary artefact for #13? Not strictly required by #13 (real user needed) but nice-to-have as a reference walkthrough.

## Non-goals

- Replacing a real non-CS participant for #11 — human SUS score cannot be automated.
- Producing the consent form for #12 — that is a legal/signature artefact, outside this spec.
- Producing the real usability video for #13 — a scripted walkthrough is not a substitute for observing an actual user.
- Automating anything inside Step 7's Gemma 4 insight path — LLM output variance is separate from the wizard walkthrough.

## Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| HF Space throttles 4 concurrent sessions | Step down to 2-wide via `orchestrate.sh --parallelism 2` |
| Chrome headless `--print-to-pdf` drops fonts or emoji | Test render early; fall back to WeasyPrint if needed |
| Jinja2 template escapes something in the Figma/brand strings | `autoescape=True` by default; tested in `test_render_fake.py` |
| `evidence.json.human_description` strings drift as helpers evolve | Keep them in `lib/wizard_step_labels.py`; single source of truth |
| Subagents self-heal and drift | Prompt explicitly forbids mutation; `RULES` block in subagent prompt |
| Screenshot commit bloats repo | Monitor; if repo crosses 200 MB, migrate `docs/reports/qa/**/*.png` to Git LFS |
| Real user-testing session slips | #14 + #15 are independent of #11/#12/#13; they proceed on their own track |

## Next step

On spec approval, the brainstorming flow hands off to the **writing-plans** skill, which produces the ordered, testable implementation plan (file creations, script writing, dry-run, live-run, render, commit, wiki update).
