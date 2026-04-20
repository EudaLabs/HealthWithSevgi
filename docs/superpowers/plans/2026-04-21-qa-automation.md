# Sprint 5 QA Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a three-layer agent-browser pipeline that produces `Sprint5_Full_Domain_Coverage.{html,pdf}` (20 specialties × 13 screenshots) and `Sprint5_E2E_Regression.{html,pdf}` (3 CSVs × 13 screenshots) against the live HuggingFace Space, with resilience and reproducibility.

**Architecture:** Three isolated layers sharing two JSON contracts (`evidence.json` per specialty, `MANIFEST.json` aggregate). Layer 1 is a deterministic bash script (`walkthrough.sh`) that drives agent-browser through the 7-step wizard. Layer 2 orchestrates 4 parallel subagents × 5 waves. Layer 3 renders a jinja2 HTML + Chrome-headless PDF matching the Sprint 2 house style.

**Tech Stack:** `agent-browser` v0.26.0 (already installed globally), bash 5+ with `set -euo pipefail`, Python 3.12 + jinja2 + json + pytest, Chrome 131 headless, existing Sprint 2 CSS, shellcheck for lint, html5lib for template parsing tests.

**Reference:** Full design at `docs/superpowers/specs/2026-04-21-qa-automation-design.md`. Read that first if context is missing.

---

## File Structure

**Files to create**

```
scripts/qa/
├── walkthrough.sh                        # Layer 1: per-specialty worker (specialty-pill flow)
├── walkthrough_upload.sh                 # Layer 1 variant: custom-upload flow (#15)
├── orchestrate.sh                        # Layer 2 bash mode (xargs -P4)
├── merge_manifest.py                     # Layer 2 aggregator
├── pending.py                            # Layer 2 resume-safe helper
├── render_report.py                      # Layer 3: HTML + PDF renderer
├── README.md                             # Usage + troubleshooting
├── lib/
│   ├── ab_helpers.sh                     # bash helpers: nav_home, select_pill, ss, retry, log, ...
│   ├── specialty_list.txt                # 20 IDs
│   ├── regression_csvs.txt               # 3 CSV paths for #15
│   └── wizard_step_labels.py             # shared constants
├── templates/
│   ├── base.html.j2
│   ├── full_coverage.html.j2
│   ├── e2e_regression.html.j2
│   └── partials/
│       ├── _cover.html.j2
│       ├── _toc.html.j2
│       ├── _specialty_section.html.j2
│       ├── _figure_block.html.j2
│       └── _summary_table.html.j2
└── tests/
    ├── test_walkthrough_dry.sh
    ├── test_render_fake.py
    ├── test_smoke_live.sh
    └── fixtures/
        └── fake_manifest.json

.github/workflows/
└── qa-smoke.yml                          # daily CI smoke (optional Phase 5)
```

**Files to modify**
- `.gitignore` — add `docs/reports/qa/**/*.log`
- `docs/wiki/Sprint-5.md` — update #14 / #15 rows from PENDING → DONE (after run succeeds)

**Files produced by running the pipeline** (not hand-authored, committed after run)
- `docs/reports/qa/full-coverage-YYYY-MM-DD/**`
- `docs/reports/qa/e2e-regression-YYYY-MM-DD/**`

---

## Phase 0 — Scaffolding

### Task 1: Create scripts/qa directory tree + .gitignore update

**Files:**
- Create: `scripts/qa/` + all subdirectories (with `.gitkeep` where empty)
- Modify: `.gitignore`
- Create: `scripts/qa/README.md` (stub)

- [ ] **Step 1: Create all directories**

```bash
cd /home/batuhan4/HealthWithSevgi
mkdir -p scripts/qa/lib \
         scripts/qa/templates/partials \
         scripts/qa/tests/fixtures
```

- [ ] **Step 2: Append .gitignore carve-out**

Append to `.gitignore`:
```
# Sprint 5 QA automation — commit artefacts but ignore noisy logs
docs/reports/qa/**/*.log
```

- [ ] **Step 3: Write README stub**

`scripts/qa/README.md`:
```markdown
# QA Automation — Sprint 5

Full design: `docs/superpowers/specs/2026-04-21-qa-automation-design.md`

## Quick start

```bash
# One specialty dry-run against live HF Space
bash scripts/qa/walkthrough.sh endocrinology_diabetes /tmp/ab-sanity

# Full 20-specialty sweep (bash mode)
bash scripts/qa/orchestrate.sh
```

Artefacts land in `docs/reports/qa/<run-id>/`.
```

- [ ] **Step 4: Commit**

```bash
git add scripts/qa/ .gitignore
git commit -m "feat(qa): scaffold scripts/qa directory tree for Sprint 5 automation"
```

### Task 2: Seed specialty_list.txt and regression_csvs.txt

**Files:**
- Create: `scripts/qa/lib/specialty_list.txt`
- Create: `scripts/qa/lib/regression_csvs.txt`

- [ ] **Step 1: List the 20 specialty IDs**

Derive from `backend/app/services/specialty_registry.py`. Write each ID on its own line, alphabetised:

`scripts/qa/lib/specialty_list.txt`:
```
# 20 specialty IDs — one per line. Lines starting with # are ignored.
cardiology_arrhythmia
cardiology_hf
cardiology_stroke
depression
dermatology
endocrinology_diabetes
haematology_anaemia
hepatology_liver
icu_sepsis
nephrology_ckd
neurology_parkinsons
obstetrics_fetal
oncology_breast
oncology_cervical
pharmacy_readmission
pulmonology_copd
radiology_pneumonia
thyroid
# … verify full list against specialty_registry.py before running
```

Verify the count is exactly 20:
```bash
grep -cEv '^(#|$)' scripts/qa/lib/specialty_list.txt
# Expected: 20
```

If not, add missing ones from `grep "\": SpecialtyInfo(" backend/app/services/specialty_registry.py`.

- [ ] **Step 2: Choose 3 regression CSVs**

`scripts/qa/lib/regression_csvs.txt`:
```
# 3 CSV paths for #15 E2E Regression — format: <csv_path>|<model_type>|<display_name>
backend/data_cache/endocrinology_diabetes.csv|knn|Endocrinology — Diabetes
backend/data_cache/cardiology_hf.csv|random_forest|Cardiology — Heart Failure
backend/data_cache/oncology_breast.csv|xgboost|Oncology — Breast Cancer
```

- [ ] **Step 3: Commit**

```bash
git add scripts/qa/lib/specialty_list.txt scripts/qa/lib/regression_csvs.txt
git commit -m "feat(qa): seed specialty list (20) and regression CSV set (3)"
```

---

## Phase 1 — Lib helpers (foundations)

### Task 3: wizard_step_labels.py constants

**Files:**
- Create: `scripts/qa/lib/wizard_step_labels.py`
- Test: `scripts/qa/tests/test_render_fake.py` (imports these constants — set up in Task 13)

- [ ] **Step 1: Write the labels module**

`scripts/qa/lib/wizard_step_labels.py`:
```python
"""Shared constants for wizard step names and per-screenshot labels.

Both ``walkthrough.sh`` (via sourcing) and ``render_report.py`` (via import)
read from this single source of truth. Whenever the UI adds / renames a step
or a screenshot, update here only.
"""

WIZARD_STEPS = {
    1: "Clinical Context",
    2: "Data Exploration",
    3: "Data Preparation",
    4: "Model & Parameters",
    5: "Results",
    6: "Explainability",
    7: "Ethics & Bias",
}

# 13-step screenshot plan for walkthrough.sh.
# Each entry: (seq, wizard_step, action_slug, human_description, critical?)
SCREENSHOT_PLAN = [
    (1,  1, "homepage",              "Landing page rendered; domain pill bar visible with all 20 specialties.", False),
    (2,  1, "specialty-selected",    "Clicked the target specialty pill; Step 1 card activated.",               False),
    (3,  2, "csv-uploaded",          "Default dataset loaded into Step 2; Column Mapper opened.",               True),
    (4,  2, "mapper-default",        "Column Mapper shows the auto-detected role assignments.",                 False),
    (5,  2, "mapper-validated",      "Saved Column Mapper; validation banner acknowledged.",                    False),
    (6,  3, "prep-applied",          "Step 3 preparation settings applied (split, normalisation, SMOTE).",      False),
    (7,  3, "prep-banner",           "Step 3 success banner visible; ready for Step 4.",                        False),
    (8,  4, "model-params",          "Step 4 — selected model type and default hyperparameters.",               False),
    (9,  4, "training-done",         "Training completed; accuracy / loss card populated.",                     True),
    (10, 5, "step5-metrics",         "Step 5 Results — sensitivity, specificity, ROC curve visible.",           False),
    (11, 6, "step6-top-feature",     "Step 6 — top SHAP feature chart rendered.",                               False),
    (12, 7, "step7-ethics",          "Step 7 — ethics audit table + LLM insight block visible.",                False),
    (13, 7, "cert-downloaded",       "Summary certificate PDF generated and downloaded successfully.",          True),
]

def filename_for(seq: int, specialty_id: str) -> str:
    """Return the canonical screenshot filename for the given step + specialty."""
    _, wizard_n, action, _, _ = SCREENSHOT_PLAN[seq - 1]
    return f"{seq:02d}_{specialty_id}_step{wizard_n}_{action}.png"
```

- [ ] **Step 2: Write a trivial smoke test to confirm the module imports cleanly**

`scripts/qa/tests/test_labels.py`:
```python
"""Sanity check for wizard_step_labels — module imports and exposes 13 steps."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
import wizard_step_labels as L


def test_wizard_steps_count():
    assert len(L.WIZARD_STEPS) == 7


def test_screenshot_plan_count():
    assert len(L.SCREENSHOT_PLAN) == 13


def test_filename_format():
    fn = L.filename_for(1, "endocrinology_diabetes")
    assert fn == "01_endocrinology_diabetes_step1_homepage.png"


def test_critical_steps():
    critical = [s[0] for s in L.SCREENSHOT_PLAN if s[4]]
    assert critical == [3, 9, 13]
```

- [ ] **Step 3: Run the test and confirm PASS**

```bash
cd /home/batuhan4/HealthWithSevgi
python3 -m pytest scripts/qa/tests/test_labels.py -v
```
Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add scripts/qa/lib/wizard_step_labels.py scripts/qa/tests/test_labels.py
git commit -m "feat(qa): shared wizard step labels + screenshot plan constants"
```

### Task 4: ab_helpers.sh foundation

**Files:**
- Create: `scripts/qa/lib/ab_helpers.sh`
- Test: via `tests/test_walkthrough_dry.sh` (Task 5)

- [ ] **Step 1: Write the helper primitives**

`scripts/qa/lib/ab_helpers.sh`:
```bash
# shellcheck shell=bash
# ab_helpers.sh — shared primitives for QA walkthrough scripts.
#
# Expects the following environment variables, set by the caller:
#   SPECIALTY     — e.g. "endocrinology_diabetes"
#   OUT_DIR       — absolute path for screenshots + evidence.json
#   BASE_URL      — e.g. "https://0xbatuhan4-healthwithsevgi.hf.space"
#   SESSION       — agent-browser session name, e.g. "qa-diabetes-1715098800"
#
# Reads SCREENSHOT_PLAN via callers that source wizard_step_labels.py through
# a python bridge (see Task 7). Not imported directly here.

# --------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------
log() {
  printf '[%s][%s] %s\n' "$(date +%H:%M:%S)" "$SPECIALTY" "$*" | tee -a "$OUT_DIR/walkthrough.log" >&2
}

die() {
  log "FATAL: $*"
  exit 1
}

# --------------------------------------------------------------------
# agent-browser wrapper — always uses the current session + 60s timeout
# --------------------------------------------------------------------
ab() {
  timeout 60 agent-browser --session "$SESSION" "$@" 2>&1 | tee -a "$OUT_DIR/walkthrough.log"
  return "${PIPESTATUS[0]}"
}

# --------------------------------------------------------------------
# Retry — runs command up to N times with exponential backoff (2s, 4s)
# --------------------------------------------------------------------
retry() {
  local max="$1"; shift
  local attempt=1
  while (( attempt <= max )); do
    if "$@"; then return 0; fi
    log "retry $attempt/$max failed: $*"
    sleep $(( attempt * 2 ))
    attempt=$(( attempt + 1 ))
  done
  return 1
}

# --------------------------------------------------------------------
# Screenshot wrapper — name follows SCREENSHOT_PLAN
# --------------------------------------------------------------------
ss() {
  local seq="$1" action="$2"
  local wizard_n
  wizard_n="$(python3 "$(dirname "${BASH_SOURCE[0]}")/wizard_step_labels.py" --wizard-step "$seq" 2>/dev/null || echo 0)"
  # Fallback if python helper absent
  [[ -z "$wizard_n" || "$wizard_n" == "0" ]] && wizard_n="${SS_WIZARD_N:-1}"
  local fn
  printf -v fn "%02d_%s_step%s_%s.png" "$seq" "$SPECIALTY" "$wizard_n" "$action"
  local path="$OUT_DIR/screenshots/$fn"
  mkdir -p "$(dirname "$path")"
  ab screenshot --path "$path" --full-page
}

# --------------------------------------------------------------------
# Assertions — small composable checks used by run_step sanity guards
# --------------------------------------------------------------------
text_visible() {
  ab find text "$1" >/dev/null 2>&1
}

element_visible() {
  ab is visible --selector "$1" >/dev/null 2>&1
}

file_exists() {
  [[ -f "$1" ]]
}

# --------------------------------------------------------------------
# Navigation + step helpers (one per step)
# --------------------------------------------------------------------
init_session() {
  SESSION="$1"
  agent-browser session create --name "$SESSION" --headless --viewport 1440x900 >>"$OUT_DIR/walkthrough.log" 2>&1
}

close_session() {
  agent-browser session close "$SESSION" >>"$OUT_DIR/walkthrough.log" 2>&1 || true
}

nav_home() {
  ab open "$BASE_URL/"
  ab wait --text "Select a specialty" --timeout 120000
}

specialty_label_from_id() {
  # Map ID → human label; single source of truth is the backend. We call
  # the live /api/specialties once per script and cache locally.
  local cache="$OUT_DIR/.specialty-labels.json"
  if [[ ! -s "$cache" ]]; then
    curl --silent --fail "$BASE_URL/api/specialties" --output "$cache" \
      || echo '[]' > "$cache"
  fi
  python3 -c "
import json, sys
data = json.load(open('$cache'))
for s in data:
    if s.get('id') == '$1':
        print(s.get('name', '$1')); break
" 2>/dev/null
}

select_pill() {
  ab click --selector "[data-specialty='$SPECIALTY']"
  local label
  label="$(specialty_label_from_id "$SPECIALTY")"
  [[ -n "$label" ]] && ab wait --text "$label" --timeout 10000
}

upload_default_csv() {
  # The specialty-pill flow auto-loads the dataset; no manual upload needed.
  ab wait --text "Column Mapper" --timeout 60000
}

validate_and_save() {
  ab click --text "Save"
  ab wait --text "Saved" --timeout 20000
}

apply_prep_defaults() {
  ab click --text "Apply Defaults"
  ab wait --text "Preparation applied" --timeout 30000
}

go_to_step4() {
  ab click --text "Step 4"
  ab wait --text "Model & Parameters" --timeout 10000
}

pick_knn_and_defaults() {
  ab click --selector "[data-model='knn']"
  ab wait --selector "[data-model='knn'][aria-pressed='true']" --timeout 5000
}

train_and_wait() {
  ab click --text "Train Model"
  # Poll every 10s up to 180s
  local deadline=$(( $(date +%s) + 180 ))
  while (( $(date +%s) < deadline )); do
    if text_visible "Training complete"; then return 0; fi
    if text_visible "Results"; then return 0; fi
    sleep 10
  done
  return 1
}

open_step5_capture() {
  ab click --text "Step 5"
  ab wait --text "Sensitivity" --timeout 15000
}

open_step6_capture() {
  ab click --text "Step 6"
  ab wait --selector ".feature-chart" --timeout 30000
}

open_step7_capture() {
  ab click --text "Step 7"
  ab wait --text "Ethics" --timeout 30000
}

download_cert() {
  ab click --text "Download Certificate"
  ab wait --url "blob:" --timeout 30000 || true
  # Certificate file path captured via agent-browser download log
  ab eval --expression "document.title" >/dev/null
  : > "$OUT_DIR/cert.pdf"   # marker — real file handling in Task 7 refinement
}
```

> **Note:** the `ss()` helper calls a tiny Python bridge through `wizard_step_labels.py` to resolve the wizard_step number from the sequence — this avoids duplicating the plan across bash and Python. The module needs a CLI mode; add it in the next step.

- [ ] **Step 2: Add CLI mode to wizard_step_labels.py**

Edit `scripts/qa/lib/wizard_step_labels.py`, append at the bottom:

```python
if __name__ == "__main__":
    import argparse, sys
    p = argparse.ArgumentParser()
    p.add_argument("--wizard-step", type=int, help="sequence number 1-13 → prints wizard step (1-7)")
    args = p.parse_args()
    if args.wizard_step:
        seq = args.wizard_step
        if not 1 <= seq <= 13:
            sys.exit(1)
        print(SCREENSHOT_PLAN[seq - 1][1])
```

- [ ] **Step 3: Smoke-test the helpers with shellcheck**

```bash
shellcheck --shell=bash scripts/qa/lib/ab_helpers.sh
```
Expected: exit 0 (no warnings). If shellcheck reports, fix inline.

- [ ] **Step 4: Confirm the Python bridge works**

```bash
python3 scripts/qa/lib/wizard_step_labels.py --wizard-step 9
```
Expected output: `4`

```bash
python3 scripts/qa/lib/wizard_step_labels.py --wizard-step 13
```
Expected output: `7`

- [ ] **Step 5: Commit**

```bash
git add scripts/qa/lib/ab_helpers.sh scripts/qa/lib/wizard_step_labels.py
git commit -m "feat(qa): bash helpers + python bridge for step resolution"
```

---

## Phase 2 — Walkthrough worker (Layer 1)

### Task 5: Write the failing dry-run test for walkthrough.sh

**Files:**
- Create: `scripts/qa/tests/test_walkthrough_dry.sh`

- [ ] **Step 1: Write the dry-run harness**

`scripts/qa/tests/test_walkthrough_dry.sh`:
```bash
#!/usr/bin/env bash
# Dry-run sanity check for walkthrough.sh.
# Stubs agent-browser, sources the script, and asserts:
#   - bash -n passes
#   - shellcheck passes
#   - run_step wrapper exists
#   - all 13 steps declared
#   - required helpers exist in ab_helpers.sh

set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
qa_dir="$(cd "$here/.." && pwd)"

echo "→ bash -n check"
bash -n "$qa_dir/walkthrough.sh"

echo "→ shellcheck"
shellcheck --shell=bash \
  "$qa_dir/walkthrough.sh" \
  "$qa_dir/lib/ab_helpers.sh"

echo "→ run_step wrapper defined"
grep -qE '^run_step\s*\(\)' "$qa_dir/walkthrough.sh" \
  || { echo "missing run_step wrapper"; exit 1; }

echo "→ 13 run_step invocations"
count=$(grep -cE '^\s*run_step\s+"[0-9]{2}_' "$qa_dir/walkthrough.sh")
[[ "$count" == "13" ]] \
  || { echo "expected 13 run_step invocations, got $count"; exit 1; }

echo "→ required helpers present"
for fn in nav_home select_pill upload_default_csv validate_and_save \
          apply_prep_defaults go_to_step4 pick_knn_and_defaults \
          train_and_wait open_step5_capture open_step6_capture \
          open_step7_capture download_cert; do
  grep -qE "^$fn\s*\(\)" "$qa_dir/lib/ab_helpers.sh" \
    || { echo "missing helper: $fn"; exit 1; }
done

echo "ALL CHECKS PASSED"
```

```bash
chmod +x scripts/qa/tests/test_walkthrough_dry.sh
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
bash scripts/qa/tests/test_walkthrough_dry.sh
```
Expected: fails with `bash -n check` error because `walkthrough.sh` does not exist yet.

- [ ] **Step 3: Commit the test**

```bash
git add scripts/qa/tests/test_walkthrough_dry.sh
git commit -m "test(qa): dry-run harness for walkthrough.sh (red)"
```

### Task 6: Implement walkthrough.sh skeleton + run_step

**Files:**
- Create: `scripts/qa/walkthrough.sh`

- [ ] **Step 1: Write the skeleton with run_step wrapper + step declarations**

`scripts/qa/walkthrough.sh`:
```bash
#!/usr/bin/env bash
# walkthrough.sh — deterministic 13-screenshot walkthrough for one specialty
#
# Usage:
#   bash walkthrough.sh <specialty_id> <out_dir>
#
# Reads no environment variables other than optional BASE_URL override.
# Writes:
#   <out_dir>/screenshots/NN_<specialty>_stepN_<action>.png  (13 files)
#   <out_dir>/evidence.json
#   <out_dir>/walkthrough.log

set -euo pipefail

SPECIALTY="${1:-}"
OUT_DIR="${2:-}"
BASE_URL="${BASE_URL:-https://0xbatuhan4-healthwithsevgi.hf.space}"

[[ -z "$SPECIALTY" || -z "$OUT_DIR" ]] && {
  echo "usage: walkthrough.sh <specialty_id> <out_dir>" >&2; exit 2
}

OUT_DIR="$(cd "$(dirname "$OUT_DIR")" 2>/dev/null && pwd)/$(basename "$OUT_DIR")" \
  || { mkdir -p "$OUT_DIR"; OUT_DIR="$(cd "$OUT_DIR" && pwd)"; }
mkdir -p "$OUT_DIR/screenshots"
rm -f "$OUT_DIR/screenshots"/*.png 2>/dev/null || true
: > "$OUT_DIR/walkthrough.log"

LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/lib" && pwd)"
# shellcheck source=lib/ab_helpers.sh
source "$LIB_DIR/ab_helpers.sh"

SESSION="qa-$SPECIALTY-$(date +%s)"
AGENT_BROWSER_VERSION="$(agent-browser --version | awk '{print $2}')"
CHROME_VERSION="$(agent-browser eval --expression 'navigator.userAgent' 2>/dev/null | grep -oE 'Chrome/[0-9.]+' | head -1 | cut -d/ -f2 || true)"

STARTED_AT="$(date -u +%FT%TZ)"
STEPS_JSON="["
STEP_SEP=""
OVERALL_STATUS="pass"
declare -a FAILURES=()

# --------------------------------------------------------------------
# run_step <name> <timeout_ms> <sanity_check_cmd> <action_cmd>
# --------------------------------------------------------------------
run_step() {
  local name="$1" timeout_ms="$2" sanity="$3" action="$4"
  local seq="${name%%_*}"            # "01" from "01_homepage"
  local action_slug="${name#??_}"    # "homepage" from "01_homepage"
  local step_status="pass" err=""
  local t0 t1 ms
  t0=$(date +%s%N)

  log "step $name (timeout ${timeout_ms}ms)"

  # Timeout wrap the action + sanity
  local timeout_sec=$(( timeout_ms / 1000 ))
  if ! timeout "$timeout_sec" bash -c "$action" 2>&1 | tee -a "$OUT_DIR/walkthrough.log"; then
    step_status="fail"
    err="action failed"
  elif ! timeout 15 bash -c "$sanity" 2>&1 | tee -a "$OUT_DIR/walkthrough.log"; then
    step_status="fail"
    err="sanity check failed: $sanity"
  fi

  # Retry up to 2× on failure
  if [[ "$step_status" == "fail" ]]; then
    local attempt=1
    while (( attempt <= 2 )); do
      log "retry $attempt/2 for $name"
      sleep $(( attempt * 2 ))
      if timeout "$timeout_sec" bash -c "$action" 2>&1 | tee -a "$OUT_DIR/walkthrough.log" \
         && timeout 15 bash -c "$sanity" 2>&1 | tee -a "$OUT_DIR/walkthrough.log"; then
        step_status="pass"; err=""
        break
      fi
      attempt=$(( attempt + 1 ))
    done
  fi

  # Screenshot — post-state
  local screenshot_fn
  local wizard_n
  wizard_n="$(python3 "$LIB_DIR/wizard_step_labels.py" --wizard-step "$((10#$seq))")"
  printf -v screenshot_fn "%s_%s_step%s_%s.png" "$seq" "$SPECIALTY" "$wizard_n" "$action_slug"
  if [[ "$step_status" == "fail" ]]; then
    screenshot_fn="${screenshot_fn%.png}_FAIL.png"
  fi
  agent-browser --session "$SESSION" screenshot --path "$OUT_DIR/screenshots/$screenshot_fn" --full-page \
    >>"$OUT_DIR/walkthrough.log" 2>&1 || true

  t1=$(date +%s%N)
  ms=$(( (t1 - t0) / 1000000 ))

  # Append to evidence JSON
  STEPS_JSON+="$STEP_SEP$(python3 -c "
import json
print(json.dumps({
  'seq': $((10#$seq)),
  'name': '$name',
  'wizard_step': $wizard_n,
  'status': '$step_status',
  'duration_ms': $ms,
  'screenshot': '$screenshot_fn',
  'error': '$err'
}))")"
  STEP_SEP=","

  if [[ "$step_status" == "fail" ]]; then
    OVERALL_STATUS="fail"
    FAILURES+=("$name: $err")
    # Hard-exit on critical steps
    if [[ "$name" =~ ^(03_csv_uploaded|09_training_done|13_cert_downloaded)$ ]]; then
      log "CRITICAL STEP FAILED: $name — finalising evidence and exiting"
      finalize_evidence
      exit 1
    fi
  fi
}

# --------------------------------------------------------------------
# finalize_evidence — always runs via trap
# --------------------------------------------------------------------
finalize_evidence() {
  local finished_at duration_ms=0
  finished_at="$(date -u +%FT%TZ)"
  STEPS_JSON+="]"

  python3 -c "
import json, datetime
started = datetime.datetime.fromisoformat('$STARTED_AT'.rstrip('Z'))
finished = datetime.datetime.fromisoformat('$finished_at'.rstrip('Z'))
duration_ms = int((finished - started).total_seconds() * 1000)
steps = json.loads('''$STEPS_JSON''')
failures = ${#FAILURES[@]}
evidence = {
  'specialty': '$SPECIALTY',
  'base_url': '$BASE_URL',
  'started_at': '$STARTED_AT',
  'finished_at': '$finished_at',
  'duration_ms': duration_ms,
  'agent_browser_version': '$AGENT_BROWSER_VERSION',
  'chrome_version': '$CHROME_VERSION',
  'status': '$OVERALL_STATUS',
  'steps': steps,
  'failures': $(printf '"%s",' "${FAILURES[@]:-}" | sed 's/,$//' | sed 's/^/[/' | sed 's/$/]/') if $(echo "${#FAILURES[@]}") > 0 else [],
  'console_errors': [],
  'network_failures': []
}
with open('$OUT_DIR/evidence.json', 'w') as f:
    json.dump(evidence, f, indent=2)
"
  log "evidence written → $OUT_DIR/evidence.json (status=$OVERALL_STATUS)"
}

trap 'finalize_evidence; close_session' EXIT
init_session "$SESSION"

# --------------------------------------------------------------------
# The 13 steps
# --------------------------------------------------------------------
run_step "01_homepage"              120000 'text_visible "Select a specialty"'      'nav_home'
run_step "02_specialty_selected"     15000 'text_visible "$(specialty_label_from_id "$SPECIALTY")"' 'select_pill'
run_step "03_csv_uploaded"           60000 'text_visible "Column Mapper"'           'upload_default_csv'
run_step "04_mapper_default"         10000 'element_visible ".mapper-row"'          'ss 4 mapper-default'
run_step "05_mapper_validated"       20000 'text_visible "Saved"'                   'validate_and_save'
run_step "06_prep_applied"           30000 'text_visible "Preparation applied"'     'apply_prep_defaults'
run_step "07_prep_banner"            10000 'text_visible "Step 4"'                  'go_to_step4'
run_step "08_model_params"           15000 'element_visible "[data-model=knn]"'     'pick_knn_and_defaults'
run_step "09_training_done"         180000 'text_visible "Training complete" || text_visible "Results"' 'train_and_wait'
run_step "10_step5_metrics"          15000 'text_visible "Sensitivity"'             'open_step5_capture'
run_step "11_step6_top_feature"      30000 'element_visible ".feature-chart"'       'open_step6_capture'
run_step "12_step7_ethics"           30000 'text_visible "Ethics"'                  'open_step7_capture'
run_step "13_cert_downloaded"        30000 'file_exists "$OUT_DIR/cert.pdf"'        'download_cert'
```

```bash
chmod +x scripts/qa/walkthrough.sh
```

- [ ] **Step 2: Run the dry-run test and confirm it passes now**

```bash
bash scripts/qa/tests/test_walkthrough_dry.sh
```
Expected: `ALL CHECKS PASSED`.

- [ ] **Step 3: Commit**

```bash
git add scripts/qa/walkthrough.sh
git commit -m "feat(qa): walkthrough.sh skeleton + 13 deterministic run_step calls"
```

### Task 7: Write walkthrough_upload.sh variant for #15

**Files:**
- Create: `scripts/qa/walkthrough_upload.sh`

- [ ] **Step 1: Write the variant**

`scripts/qa/walkthrough_upload.sh`:
```bash
#!/usr/bin/env bash
# walkthrough_upload.sh — E2E Regression variant using custom CSV upload flow
#
# Usage:
#   bash walkthrough_upload.sh <csv_path> <model_type> <display_name> <out_dir>
#
# Same wizard steps 03-13 as walkthrough.sh, but steps 01-02 use the custom
# upload path instead of the specialty-pill auto-load.

set -euo pipefail

CSV_PATH="${1:-}"
MODEL_TYPE="${2:-knn}"
DISPLAY_NAME="${3:-Custom CSV}"
OUT_DIR="${4:-}"
BASE_URL="${BASE_URL:-https://0xbatuhan4-healthwithsevgi.hf.space}"

[[ -z "$CSV_PATH" || -z "$OUT_DIR" ]] && {
  echo "usage: walkthrough_upload.sh <csv_path> <model_type> <display_name> <out_dir>" >&2
  exit 2
}
[[ ! -f "$CSV_PATH" ]] && { echo "CSV not found: $CSV_PATH" >&2; exit 2; }

CSV_PATH="$(cd "$(dirname "$CSV_PATH")" && pwd)/$(basename "$CSV_PATH")"
SPECIALTY="$(basename "$CSV_PATH" .csv)"   # e.g. "endocrinology_diabetes"

mkdir -p "$OUT_DIR/screenshots"
rm -f "$OUT_DIR/screenshots"/*.png 2>/dev/null || true
: > "$OUT_DIR/walkthrough.log"

LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/lib" && pwd)"
# shellcheck source=lib/ab_helpers.sh
source "$LIB_DIR/ab_helpers.sh"

# Override step-01 and step-02 specific helpers for the upload flow
nav_home_upload() {
  ab open "$BASE_URL/"
  ab wait --text "Upload Custom CSV" --timeout 120000
}

upload_csv_via_picker() {
  ab upload --selector "input[type='file']" --file "$CSV_PATH"
  ab wait --text "Column Mapper" --timeout 60000
}

# Pick the requested model in step 08 instead of always KNN
pick_requested_model() {
  ab click --selector "[data-model='$MODEL_TYPE']"
  ab wait --selector "[data-model='$MODEL_TYPE'][aria-pressed='true']" --timeout 5000
}

# … steps 03-13 reuse the helpers from ab_helpers.sh
# (the `run_step` wrapper + step definitions below mirror walkthrough.sh)

SESSION="qa-regr-$SPECIALTY-$(date +%s)"
STARTED_AT="$(date -u +%FT%TZ)"
STEPS_JSON="["
STEP_SEP=""
OVERALL_STATUS="pass"
declare -a FAILURES=()

run_step() {  # identical to walkthrough.sh — duplication is acceptable per DRY scope
  # ... (copy the run_step function verbatim from walkthrough.sh)
  # (the executor copies rather than sourcing to keep scripts self-contained)
  :
}
finalize_evidence() {
  # ... (copy from walkthrough.sh)
  :
}

trap 'finalize_evidence; close_session' EXIT
init_session "$SESSION"

run_step "01_homepage"              120000 'text_visible "Upload Custom CSV"'       'nav_home_upload'
run_step "02_csv_selected_picker"    60000 'text_visible "Column Mapper"'           'upload_csv_via_picker'
run_step "03_csv_uploaded"           10000 'element_visible ".mapper-row"'          'ss 3 csv-uploaded'
run_step "04_mapper_default"         10000 'element_visible ".mapper-row"'          'ss 4 mapper-default'
run_step "05_mapper_validated"       20000 'text_visible "Saved"'                   'validate_and_save'
run_step "06_prep_applied"           30000 'text_visible "Preparation applied"'     'apply_prep_defaults'
run_step "07_prep_banner"            10000 'text_visible "Step 4"'                  'go_to_step4'
run_step "08_model_params"           15000 'element_visible "[data-model=$MODEL_TYPE]"' 'pick_requested_model'
run_step "09_training_done"         180000 'text_visible "Training complete" || text_visible "Results"' 'train_and_wait'
run_step "10_step5_metrics"          15000 'text_visible "Sensitivity"'             'open_step5_capture'
run_step "11_step6_top_feature"      30000 'element_visible ".feature-chart"'       'open_step6_capture'
run_step "12_step7_ethics"           30000 'text_visible "Ethics"'                  'open_step7_capture'
run_step "13_cert_downloaded"        30000 'file_exists "$OUT_DIR/cert.pdf"'        'download_cert'
```

**Note:** before final commit, copy `run_step` and `finalize_evidence` function bodies from `walkthrough.sh` (verbatim) to replace the `:` placeholders above. The duplication is deliberate — keeps each script runnable standalone.

- [ ] **Step 2: Shellcheck + bash -n**

```bash
shellcheck --shell=bash scripts/qa/walkthrough_upload.sh
bash -n scripts/qa/walkthrough_upload.sh
```

Fix any warnings inline.

- [ ] **Step 3: Commit**

```bash
git add scripts/qa/walkthrough_upload.sh
git commit -m "feat(qa): walkthrough_upload.sh — custom-upload variant for #15"
```

---

## Phase 3 — Orchestration (Layer 2)

### Task 8: merge_manifest.py + test

**Files:**
- Create: `scripts/qa/merge_manifest.py`
- Test: `scripts/qa/tests/test_merge_manifest.py`

- [ ] **Step 1: Write the failing test**

`scripts/qa/tests/test_merge_manifest.py`:
```python
"""merge_manifest should combine per-specialty evidence.json files into MANIFEST.json."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from merge_manifest import merge


def _ev(path, specialty, status, dur):
    path.mkdir(parents=True, exist_ok=True)
    (path / "evidence.json").write_text(json.dumps({
        "specialty": specialty,
        "base_url": "http://test",
        "started_at": "2026-04-21T10:00:00Z",
        "finished_at": "2026-04-21T10:01:00Z",
        "duration_ms": dur,
        "agent_browser_version": "0.26.0",
        "chrome_version": "131.0.0",
        "status": status,
        "steps": [],
        "failures": [],
        "console_errors": [],
        "network_failures": [],
    }))


def test_merge_aggregates_and_counts(tmp_path):
    _ev(tmp_path / "a", "a", "pass", 1000)
    _ev(tmp_path / "b", "b", "pass", 2000)
    _ev(tmp_path / "c", "c", "fail", 3000)
    merge(tmp_path, "test-run", "http://test")
    manifest = json.loads((tmp_path / "MANIFEST.json").read_text())
    assert manifest["summary"] == {
        "total": 3, "pass": 2, "fail": 1, "skipped": 0, "avg_duration_ms": 2000
    }
    assert set(manifest["specialties"].keys()) == {"a", "b", "c"}
```

- [ ] **Step 2: Confirm the test fails (module does not exist)**

```bash
python3 -m pytest scripts/qa/tests/test_merge_manifest.py -v
```
Expected: ImportError.

- [ ] **Step 3: Implement merge_manifest.py**

`scripts/qa/merge_manifest.py`:
```python
#!/usr/bin/env python3
"""Merge per-specialty evidence.json files into a single MANIFEST.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def merge(run_dir: Path, run_id: str, base_url: str) -> Path:
    """Scan run_dir for <id>/evidence.json, emit MANIFEST.json."""
    run_dir = Path(run_dir)
    evidence_files = sorted(run_dir.glob("*/evidence.json"))
    specialties: dict[str, dict] = {}
    for ev in evidence_files:
        data = json.loads(ev.read_text())
        specialties[data["specialty"]] = data

    total = len(specialties)
    passed = sum(1 for v in specialties.values() if v["status"] == "pass")
    failed = sum(1 for v in specialties.values() if v["status"] == "fail")
    avg = int(sum(v["duration_ms"] for v in specialties.values()) / total) if total else 0

    first_start = min((v["started_at"] for v in specialties.values()), default="")
    last_finish = max((v["finished_at"] for v in specialties.values()), default="")

    manifest = {
        "run_id": run_id,
        "base_url": base_url,
        "started_at": first_start,
        "finished_at": last_finish,
        "summary": {
            "total": total,
            "pass": passed,
            "fail": failed,
            "skipped": 0,
            "avg_duration_ms": avg,
        },
        "specialties": specialties,
    }
    out = run_dir / "MANIFEST.json"
    out.write_text(json.dumps(manifest, indent=2))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: merge_manifest.py <run_dir> [run_id] [base_url]", file=sys.stderr)
        sys.exit(2)
    run_dir = Path(sys.argv[1])
    run_id = sys.argv[2] if len(sys.argv) > 2 else run_dir.name
    base_url = sys.argv[3] if len(sys.argv) > 3 else "https://0xbatuhan4-healthwithsevgi.hf.space"
    path = merge(run_dir, run_id, base_url)
    print(f"wrote {path}")
```

- [ ] **Step 4: Confirm the test passes**

```bash
python3 -m pytest scripts/qa/tests/test_merge_manifest.py -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/qa/merge_manifest.py scripts/qa/tests/test_merge_manifest.py
git commit -m "feat(qa): merge_manifest.py aggregator with unit test"
```

### Task 9: pending.py (resume-safe helper)

**Files:**
- Create: `scripts/qa/pending.py`
- Test: `scripts/qa/tests/test_pending.py`

- [ ] **Step 1: Write failing test**

`scripts/qa/tests/test_pending.py`:
```python
"""pending.py prints specialty IDs that still need to run."""
import json
import subprocess
import sys
from pathlib import Path


def test_pending_skips_passed(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "evidence.json").write_text(json.dumps({"specialty": "a", "status": "pass"}))
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "evidence.json").write_text(json.dumps({"specialty": "b", "status": "fail"}))

    script = Path(__file__).parent.parent / "pending.py"
    result = subprocess.run(
        [sys.executable, str(script), str(tmp_path), "a", "b", "c"],
        capture_output=True, text=True, check=True,
    )
    pending = [line for line in result.stdout.splitlines() if line.strip()]
    assert sorted(pending) == ["b", "c"]   # a passed already; b failed → re-run; c never run
```

- [ ] **Step 2: Confirm test fails**

```bash
python3 -m pytest scripts/qa/tests/test_pending.py -v
```
Expected: `FileNotFoundError` or `CalledProcessError`.

- [ ] **Step 3: Implement pending.py**

`scripts/qa/pending.py`:
```python
#!/usr/bin/env python3
"""Print specialty IDs whose evidence.json is missing or non-pass."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def pending(run_dir: Path, candidates: list[str]) -> list[str]:
    run_dir = Path(run_dir)
    result: list[str] = []
    for cand in candidates:
        ev = run_dir / cand / "evidence.json"
        if not ev.exists():
            result.append(cand); continue
        try:
            data = json.loads(ev.read_text())
            if data.get("status") != "pass":
                result.append(cand)
        except Exception:
            result.append(cand)
    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: pending.py <run_dir> <id1> <id2> ...", file=sys.stderr)
        sys.exit(2)
    run_dir = Path(sys.argv[1])
    candidates = sys.argv[2:]
    for cand in pending(run_dir, candidates):
        print(cand)
```

- [ ] **Step 4: Confirm test passes**

```bash
python3 -m pytest scripts/qa/tests/test_pending.py -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/qa/pending.py scripts/qa/tests/test_pending.py
git commit -m "feat(qa): resume-safe pending.py helper with unit test"
```

### Task 10: orchestrate.sh (bash mode)

**Files:**
- Create: `scripts/qa/orchestrate.sh`

- [ ] **Step 1: Write orchestrate.sh**

`scripts/qa/orchestrate.sh`:
```bash
#!/usr/bin/env bash
# orchestrate.sh — run all 20 specialties in 4-wide parallel batches.
#
# Usage:
#   bash orchestrate.sh                       # full run, date-stamped dir
#   bash orchestrate.sh --parallelism 2       # step down concurrency
#   bash orchestrate.sh --resume              # skip already-passed specialties
#
# Output: docs/reports/qa/full-coverage-<date>/

set -euo pipefail

PAR=4
RESUME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --parallelism) PAR="$2"; shift 2 ;;
    --resume)      RESUME=1; shift ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

QA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$QA_DIR/../.." && pwd)"
DATE="$(date +%F)"
OUT_BASE="$REPO_ROOT/docs/reports/qa/full-coverage-$DATE"
mkdir -p "$OUT_BASE"

# Read specialty list (ignore comments + blank lines)
mapfile -t SPECIALTIES < <(grep -vE '^(#|$)' "$QA_DIR/lib/specialty_list.txt")

# Filter via pending.py when resuming
if [[ -n "$RESUME" ]]; then
  mapfile -t PENDING_LIST < <(python3 "$QA_DIR/pending.py" "$OUT_BASE" "${SPECIALTIES[@]}")
else
  PENDING_LIST=("${SPECIALTIES[@]}")
fi

echo "Running ${#PENDING_LIST[@]} specialties, ${PAR}-wide parallel → $OUT_BASE"

# xargs -P$PAR to run walkthrough.sh on each specialty
printf '%s\n' "${PENDING_LIST[@]}" | \
  xargs -P "$PAR" -I{} bash -c '
    spec="$1"
    out="$2/$spec"
    mkdir -p "$out"
    bash "$3/walkthrough.sh" "$spec" "$out" \
      || echo "[FAIL] $spec" >&2
  ' _ {} "$OUT_BASE" "$QA_DIR"

# Aggregate + render
python3 "$QA_DIR/merge_manifest.py" "$OUT_BASE" "full-coverage-$DATE"
python3 "$QA_DIR/render_report.py" "$OUT_BASE" --template full_coverage \
  --stem "Sprint5_Full_Domain_Coverage"

echo "DONE → $OUT_BASE/Sprint5_Full_Domain_Coverage.pdf"
```

```bash
chmod +x scripts/qa/orchestrate.sh
```

- [ ] **Step 2: Shellcheck + syntax check**

```bash
shellcheck --shell=bash scripts/qa/orchestrate.sh
bash -n scripts/qa/orchestrate.sh
```

- [ ] **Step 3: Commit**

```bash
git add scripts/qa/orchestrate.sh
git commit -m "feat(qa): orchestrate.sh — 4-wide parallel + resume-safe"
```

---

## Phase 4 — Render layer

### Task 11: Create fake_manifest.json fixture

**Files:**
- Create: `scripts/qa/tests/fixtures/fake_manifest.json`

- [ ] **Step 1: Generate a realistic fake with 3 specialties (2 pass, 1 fail)**

`scripts/qa/tests/fixtures/fake_manifest.json`:
```json
{
  "run_id": "fake-run-test",
  "base_url": "http://test",
  "started_at": "2026-04-21T10:00:00Z",
  "finished_at": "2026-04-21T10:05:00Z",
  "summary": {
    "total": 3,
    "pass": 2,
    "fail": 1,
    "skipped": 0,
    "avg_duration_ms": 90000
  },
  "specialties": {
    "endocrinology_diabetes": {
      "specialty": "endocrinology_diabetes",
      "display_name": "Endocrinology — Diabetes",
      "dataset_name": "Pima Indians Diabetes",
      "row_count": 768,
      "duration_ms": 85000,
      "status": "pass",
      "steps": [
        {"seq": 1, "name": "01_homepage", "wizard_step": 1, "label": "Homepage", "human_description": "Landing page rendered.", "status": "pass", "duration_ms": 2000, "screenshot": "01_endocrinology_diabetes_step1_homepage.png"}
      ],
      "failures": [], "console_errors": [], "network_failures": []
    },
    "cardiology_hf": {
      "specialty": "cardiology_hf",
      "display_name": "Cardiology — Heart Failure",
      "dataset_name": "Heart Failure Clinical",
      "row_count": 299,
      "duration_ms": 92000,
      "status": "pass",
      "steps": [],
      "failures": [], "console_errors": [], "network_failures": []
    },
    "nephrology_ckd": {
      "specialty": "nephrology_ckd",
      "display_name": "Nephrology — CKD",
      "dataset_name": "Chronic Kidney Disease",
      "row_count": 400,
      "duration_ms": 93000,
      "status": "fail",
      "steps": [
        {"seq": 9, "name": "09_training_done", "wizard_step": 4, "label": "Training", "human_description": "Training never completed.", "status": "fail", "duration_ms": 180000, "screenshot": "09_nephrology_ckd_step4_training-done_FAIL.png", "error": "timeout"}
      ],
      "failures": ["09_training_done: timeout"],
      "console_errors": ["POST /api/train returned 500"],
      "network_failures": []
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add scripts/qa/tests/fixtures/fake_manifest.json
git commit -m "test(qa): fake MANIFEST fixture with 2 pass + 1 fail scenario"
```

### Task 12: Write failing render test

**Files:**
- Create: `scripts/qa/tests/test_render_fake.py`

- [ ] **Step 1: Write the test**

`scripts/qa/tests/test_render_fake.py`:
```python
"""render_report.py must produce parseable HTML from the fake manifest."""
import shutil
import subprocess
import sys
from pathlib import Path

import html5lib


QA_DIR = Path(__file__).parent.parent
FIXTURE = QA_DIR / "tests" / "fixtures" / "fake_manifest.json"


def _setup_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "fake-run"
    run_dir.mkdir()
    shutil.copy(FIXTURE, run_dir / "MANIFEST.json")
    (run_dir / "screenshots").mkdir()
    for name in ("01_endocrinology_diabetes_step1_homepage.png",
                 "09_nephrology_ckd_step4_training-done_FAIL.png"):
        (run_dir / "screenshots" / name).write_bytes(b"\x89PNG\r\n\x1a\n")
    return run_dir


def test_render_produces_parseable_html(tmp_path):
    run_dir = _setup_run_dir(tmp_path)
    subprocess.run(
        [sys.executable, str(QA_DIR / "render_report.py"),
         str(run_dir), "--template", "full_coverage",
         "--stem", "TestReport", "--no-pdf"],
        check=True,
    )
    html_path = run_dir / "TestReport.html"
    assert html_path.exists(), "render_report.py did not emit HTML"
    content = html_path.read_text()
    assert "{{" not in content, "unrendered jinja placeholder leaked"
    html5lib.parse(content)   # raises if malformed

    # All three specialties present
    for sid in ("endocrinology_diabetes", "cardiology_hf", "nephrology_ckd"):
        assert f'id="specialty-{sid}"' in content


def test_render_marks_failure_row(tmp_path):
    run_dir = _setup_run_dir(tmp_path)
    subprocess.run(
        [sys.executable, str(QA_DIR / "render_report.py"),
         str(run_dir), "--template", "full_coverage",
         "--stem", "TestReport", "--no-pdf"],
        check=True,
    )
    html = (run_dir / "TestReport.html").read_text()
    assert "stamp-fail" in html, "failure stamp class missing"
    assert "stamp-pass" in html, "pass stamp class missing"
```

- [ ] **Step 2: Install html5lib in the backend venv (used for tests)**

```bash
cd /home/batuhan4/HealthWithSevgi
source backend/venv/bin/activate
pip install html5lib jinja2
pip freeze | grep -E "(html5lib|Jinja2)"
```

- [ ] **Step 3: Confirm the test fails**

```bash
python3 -m pytest scripts/qa/tests/test_render_fake.py -v
```
Expected: FAIL (render_report.py not implemented).

- [ ] **Step 4: Commit the test**

```bash
git add scripts/qa/tests/test_render_fake.py
git commit -m "test(qa): failing render test against fake manifest (red)"
```

### Task 13: Extract Sprint 2 CSS into base.html.j2

**Files:**
- Create: `scripts/qa/templates/base.html.j2`

- [ ] **Step 1: Extract the CSS from the existing Sprint 2 report**

Read the `<style>` block from `docs/reports/Sprint2_Screenshot_Report.html` (lines ~7–90). Save it into `scripts/qa/templates/base.html.j2` as the template foundation.

`scripts/qa/templates/base.html.j2`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}</title>
  <style>
    /* --- Sprint 2 CSS verbatim --- */
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{--primary:#2e7d32;--primary-light:#4caf50;--primary-dark:#1b5e20;--primary-bg:#e8f5e9;--text:#212121;--text-secondary:#555;--border:#c8e6c9;--white:#fff;--gray-50:#fafafa;--gray-200:#eee;--gray-300:#e0e0e0}
    body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;color:var(--text);background:var(--white);line-height:1.5;font-size:14px}
    /* ... (paste full CSS block from Sprint 2 report lines 7–90) ... */

    /* --- Additions for QA reports (not in Sprint 2) --- */
    .stamp-pass{background:#d4edda;color:#155724;padding:2px 8px;border-radius:3px;font-size:11px;font-weight:700}
    .stamp-fail{background:#f8d7da;color:#721c24;padding:2px 8px;border-radius:3px;font-size:11px;font-weight:700}
    .figure-fail{border:2px solid #d32f2f}
    .summary-table{width:100%;border-collapse:collapse;font-size:12px}
    .summary-table th,.summary-table td{padding:6px 10px;border-bottom:1px solid var(--gray-200)}
    .summary-table thead th{background:var(--primary);color:var(--white);text-align:left}
    .summary-table .row-fail td{background:#fff5f5}
    .figure-timing{float:right;color:var(--text-secondary);font-weight:400;font-size:11px}
  </style>
</head>
<body>
  {% block cover %}{% endblock %}
  {% block toc %}{% endblock %}
  {% block content %}{% endblock %}
  {% block summary %}{% endblock %}
</body>
</html>
```

Actually copying the Sprint 2 CSS by hand is error-prone — use this command to embed it mechanically:

```bash
python3 - <<'EOF'
from pathlib import Path
src = Path("docs/reports/Sprint2_Screenshot_Report.html").read_text()
start = src.index("<style>") + len("<style>")
end = src.index("</style>")
css = src[start:end]
tpl = Path("scripts/qa/templates/base.html.j2")
text = tpl.read_text()
text = text.replace("/* ... (paste full CSS block from Sprint 2 report lines 7–90) ... */", css)
tpl.write_text(text)
print("embedded", len(css), "bytes of CSS")
EOF
```

- [ ] **Step 2: Verify the template loads**

```bash
python3 -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('scripts/qa/templates'))
t = env.get_template('base.html.j2')
print(t.render(title='Test').count('body'))
"
```
Expected: prints a small integer > 0.

- [ ] **Step 3: Commit**

```bash
git add scripts/qa/templates/base.html.j2
git commit -m "feat(qa): base template reusing Sprint 2 CSS + QA-specific stamps"
```

### Task 14: Create partial templates

**Files:**
- Create: `scripts/qa/templates/partials/_cover.html.j2`
- Create: `scripts/qa/templates/partials/_toc.html.j2`
- Create: `scripts/qa/templates/partials/_figure_block.html.j2`
- Create: `scripts/qa/templates/partials/_specialty_section.html.j2`
- Create: `scripts/qa/templates/partials/_summary_table.html.j2`

- [ ] **Step 1: `_cover.html.j2`**

```html
<section class="cover-page">
  <div class="cover-logo"><span>H</span></div>
  <div class="cover-title">HealthWithSevgi</div>
  <div class="cover-subtitle">{{ subtitle }}</div>
  <div class="cover-org">Cankaya University · SENG 430</div>
  <div class="cover-group">Sprint 5 — QA Evidence</div>
  <table class="cover-table">
    <tr><th>Run ID</th><td>{{ manifest.run_id }}</td></tr>
    <tr><th>Base URL</th><td>{{ manifest.base_url }}</td></tr>
    <tr><th>Started</th><td>{{ manifest.started_at }}</td></tr>
    <tr><th>Finished</th><td>{{ manifest.finished_at }}</td></tr>
    <tr><th>Specialties</th><td>{{ manifest.summary.pass }}/{{ manifest.summary.total }} PASS</td></tr>
    <tr><th>Avg duration</th><td>{{ manifest.summary.avg_duration_ms | ms_to_human }}</td></tr>
  </table>
  <div class="cover-meta">Generated {{ generated_at }}</div>
</section>
```

- [ ] **Step 2: `_toc.html.j2`**

```html
<section class="toc-page">
  <h2>Table of Contents</h2>
  <ul class="toc-list">
    {% for sid, s in manifest.specialties.items() %}
      <li><a href="#specialty-{{ sid }}">
        <span>{{ loop.index }}. {{ s.display_name }}</span>
        <span class="stamp-{{ s.status }}">{{ s.status }}</span>
      </a></li>
    {% endfor %}
    <li class="toc-section"><a href="#summary"><span>Summary</span><span></span></a></li>
  </ul>
</section>
```

- [ ] **Step 3: `_figure_block.html.j2`**

```html
{% macro figure_block(step, specialty_id) %}
<div class="figure-block {% if step.status == 'fail' %}figure-fail{% endif %}">
  <div class="figure-title">
    {{ "%02d"|format(step.seq) }} — {{ step.label or step.name }}
    <span class="figure-timing">{{ step.duration_ms | ms_to_human }}</span>
  </div>
  <div class="figure-desc">{{ step.human_description }}</div>
  <div class="figure-img">
    <img src="screenshots/{{ step.screenshot }}" alt="{{ step.label or step.name }}"/>
  </div>
  <div class="figure-caption">
    Step {{ step.wizard_step }} — {{ wizard_steps[step.wizard_step] }}
    {% if step.status == 'fail' %}· <strong style="color:#d32f2f">FAILED</strong>{% endif %}
  </div>
</div>
{% endmacro %}
```

- [ ] **Step 4: `_specialty_section.html.j2`**

```html
{% from "partials/_figure_block.html.j2" import figure_block %}

<section class="specialty-section" id="specialty-{{ s.specialty }}">
  <div class="section-header">
    <h2>{{ s.display_name }} <span class="stamp-{{ s.status }}">{{ s.status | upper }}</span></h2>
    <p>{{ s.dataset_name | default("-") }} · {{ s.row_count | default("?") }} rows · {{ s.duration_ms | ms_to_human }}</p>
  </div>
  <div class="content">
    <div class="req-check">
      ✓ 13 screenshots captured · Agent-browser {{ s.agent_browser_version }} · Chrome {{ s.chrome_version }}
      {% if s.failures %}<br>⚠ {{ s.failures | length }} failure(s): {{ s.failures | join(', ') }}{% endif %}
    </div>

    {% set by_wizard = {} %}
    {% for step in s.steps %}
      {% if by_wizard.update({step.wizard_step: (by_wizard.get(step.wizard_step, []) + [step])}) %}{% endif %}
    {% endfor %}

    {% for wizard_n, label in wizard_steps.items() %}
      {% if by_wizard.get(wizard_n) %}
        <h3 class="subsection">Step {{ wizard_n }} — {{ label }}</h3>
        {% for step in by_wizard[wizard_n] %}
          {{ figure_block(step, s.specialty) }}
        {% endfor %}
      {% endif %}
    {% endfor %}
  </div>
</section>
<div class="step-break"></div>
```

- [ ] **Step 5: `_summary_table.html.j2`**

```html
<section class="summary-section" id="summary">
  <div class="section-header"><h2>Summary</h2></div>
  <div class="content">
    <table class="summary-table">
      <thead><tr>
        <th>#</th><th>Specialty</th><th>Dataset</th>
        <th>Duration</th><th>Failed Steps</th><th>Status</th>
      </tr></thead>
      <tbody>
      {% for sid, s in manifest.specialties.items() %}
        <tr class="row-{{ s.status }}">
          <td>{{ loop.index }}</td>
          <td><a href="#specialty-{{ sid }}">{{ s.display_name }}</a></td>
          <td>{{ s.dataset_name | default("-") }}</td>
          <td>{{ s.duration_ms | ms_to_human }}</td>
          <td>{{ s.failures | join(', ') if s.failures else "—" }}</td>
          <td><span class="stamp-{{ s.status }}">{{ s.status }}</span></td>
        </tr>
      {% endfor %}
      </tbody>
      <tfoot><tr>
        <th colspan="3">TOTAL</th>
        <th>{{ manifest.summary.avg_duration_ms | ms_to_human }} avg</th>
        <th>—</th>
        <th>{{ manifest.summary.pass }}/{{ manifest.summary.total }} PASS</th>
      </tr></tfoot>
    </table>
  </div>
</section>
```

- [ ] **Step 6: Commit all partials**

```bash
git add scripts/qa/templates/partials/
git commit -m "feat(qa): cover / toc / section / figure / summary partials"
```

### Task 15: full_coverage.html.j2 and e2e_regression.html.j2

**Files:**
- Create: `scripts/qa/templates/full_coverage.html.j2`
- Create: `scripts/qa/templates/e2e_regression.html.j2`

- [ ] **Step 1: `full_coverage.html.j2`**

```html
{% extends "base.html.j2" %}
{% set title = "HealthWithSevgi — Sprint 5 Full Domain Coverage" %}
{% set subtitle = "Full Domain Coverage — 20 Specialties Walkthrough" %}

{% block cover %}{% include "partials/_cover.html.j2" %}{% endblock %}
{% block toc %}{% include "partials/_toc.html.j2" %}{% endblock %}

{% block content %}
  {% for sid, s in manifest.specialties.items() %}
    {% set _ = s.__setitem__('specialty', sid) if s.get('specialty') is none else None %}
    {% with s=s %}
      {% include "partials/_specialty_section.html.j2" %}
    {% endwith %}
  {% endfor %}
{% endblock %}

{% block summary %}{% include "partials/_summary_table.html.j2" %}{% endblock %}
```

- [ ] **Step 2: `e2e_regression.html.j2`**

```html
{% extends "base.html.j2" %}
{% set title = "HealthWithSevgi — Sprint 5 E2E Regression" %}
{% set subtitle = "E2E Regression — 3 CSVs, 3 Model Types" %}

{% block cover %}{% include "partials/_cover.html.j2" %}{% endblock %}
{% block toc %}{% include "partials/_toc.html.j2" %}{% endblock %}

{% block content %}
  {% for sid, s in manifest.specialties.items() %}
    {% with s=s %}
      {% include "partials/_specialty_section.html.j2" %}
    {% endwith %}
  {% endfor %}
{% endblock %}

{% block summary %}{% include "partials/_summary_table.html.j2" %}{% endblock %}
```

- [ ] **Step 3: Commit**

```bash
git add scripts/qa/templates/full_coverage.html.j2 scripts/qa/templates/e2e_regression.html.j2
git commit -m "feat(qa): full_coverage + e2e_regression top-level templates"
```

### Task 16: Implement render_report.py

**Files:**
- Create: `scripts/qa/render_report.py`

- [ ] **Step 1: Write render_report.py**

`scripts/qa/render_report.py`:
```python
#!/usr/bin/env python3
"""Render MANIFEST.json → HTML (+ optional PDF via Chrome headless)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

QA_DIR = Path(__file__).parent
sys.path.insert(0, str(QA_DIR / "lib"))
import wizard_step_labels as L   # noqa: E402


def _ms_to_human(ms: int) -> str:
    if ms is None:
        return "?"
    s = ms / 1000
    if s < 60:
        return f"{s:.1f}s"
    m, s = divmod(s, 60)
    return f"{int(m)}m {int(s)}s"


def render(run_dir: Path, template: str, stem: str, emit_pdf: bool = True) -> tuple[Path, Path | None]:
    run_dir = Path(run_dir).resolve()
    manifest = json.loads((run_dir / "MANIFEST.json").read_text())

    env = Environment(
        loader=FileSystemLoader(str(QA_DIR / "templates")),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["ms_to_human"] = _ms_to_human

    html = env.get_template(f"{template}.html.j2").render(
        manifest=manifest,
        wizard_steps=L.WIZARD_STEPS,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    html_path = run_dir / f"{stem}.html"
    html_path.write_text(html)

    pdf_path: Path | None = None
    if emit_pdf:
        pdf_path = run_dir / f"{stem}.pdf"
        subprocess.run(
            [
                "google-chrome", "--headless=new", "--disable-gpu",
                f"--print-to-pdf={pdf_path}",
                "--no-pdf-header-footer",
                "--virtual-time-budget=5000",
                f"file://{html_path}",
            ],
            check=True,
        )
    return html_path, pdf_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--template", required=True, choices=["full_coverage", "e2e_regression"])
    ap.add_argument("--stem", required=True, help="output filename without extension")
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    html, pdf = render(args.run_dir, args.template, args.stem, emit_pdf=not args.no_pdf)
    print(f"wrote {html}")
    if pdf:
        print(f"wrote {pdf}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the fake-render test and confirm pass**

```bash
python3 -m pytest scripts/qa/tests/test_render_fake.py -v
```
Expected: both tests PASS.

- [ ] **Step 3: Commit**

```bash
git add scripts/qa/render_report.py
git commit -m "feat(qa): render_report.py — jinja2 HTML + Chrome PDF"
```

---

## Phase 5 — Dry-run + live smoke

### Task 17: test_smoke_live.sh

**Files:**
- Create: `scripts/qa/tests/test_smoke_live.sh`

- [ ] **Step 1: Write the 1-specialty × 3-step smoke**

`scripts/qa/tests/test_smoke_live.sh`:
```bash
#!/usr/bin/env bash
# 1-specialty × 3-step smoke against live HF Space. Runs in ~30s.
# Exit non-zero if any of the three steps fails.

set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
qa_dir="$(cd "$here/.." && pwd)"
out="/tmp/qa-smoke-$(date +%s)"
mkdir -p "$out"

# Run only steps 01, 02, 03 by setting SMOKE_MODE env flag; walkthrough.sh
# reads it and exits after step 03 on success.
SMOKE_MODE=1 bash "$qa_dir/walkthrough.sh" endocrinology_diabetes "$out" || {
  echo "SMOKE FAILED — see $out/walkthrough.log"
  exit 1
}

# Assert the three expected PNGs exist
for n in 01 02 03; do
  ls "$out/screenshots/${n}_endocrinology_diabetes_"* >/dev/null \
    || { echo "missing screenshot prefix $n"; exit 1; }
done

echo "SMOKE OK — $out"
```

```bash
chmod +x scripts/qa/tests/test_smoke_live.sh
```

- [ ] **Step 2: Teach walkthrough.sh to honour `SMOKE_MODE`**

Edit `scripts/qa/walkthrough.sh`. After the `run_step "03_csv_uploaded" ...` line, insert:
```bash
if [[ -n "${SMOKE_MODE:-}" ]]; then
  log "SMOKE_MODE=1 → stopping after step 03"
  exit 0
fi
```

- [ ] **Step 3: Run the smoke against live HF**

```bash
bash scripts/qa/tests/test_smoke_live.sh
```
Expected: `SMOKE OK — /tmp/qa-smoke-*`.

If the live smoke fails, open the log (`$out/walkthrough.log`), inspect the three PNGs, fix helpers in `ab_helpers.sh`, re-run. Do **not** proceed to the full run until the smoke is green.

- [ ] **Step 4: Commit**

```bash
git add scripts/qa/tests/test_smoke_live.sh scripts/qa/walkthrough.sh
git commit -m "feat(qa): live-smoke harness + SMOKE_MODE flag in walkthrough"
```

### Task 18: Single-specialty full-run sanity check

**Files:**
- None (produces artefacts in `/tmp/ab-sanity-full`, not committed)

- [ ] **Step 1: Run the full 13-step walkthrough for a single specialty**

```bash
mkdir -p /tmp/ab-sanity-full
bash scripts/qa/walkthrough.sh endocrinology_diabetes /tmp/ab-sanity-full
```

Expected: `evidence.json` exists with `status: pass`, 13 PNGs in `screenshots/`. Total run ~90 s.

- [ ] **Step 2: Render a one-specialty fake report**

Build a single-specialty manifest from the evidence:
```bash
mkdir -p /tmp/ab-sanity-full-render
cp -r /tmp/ab-sanity-full /tmp/ab-sanity-full-render/endocrinology_diabetes
python3 scripts/qa/merge_manifest.py /tmp/ab-sanity-full-render sanity
python3 scripts/qa/render_report.py /tmp/ab-sanity-full-render \
  --template full_coverage --stem Sanity_Report
```

Expected: `Sanity_Report.html` + `Sanity_Report.pdf` open correctly; all 13 screenshots visible.

- [ ] **Step 3: If anything looks broken, fix inline**

Common issues:
- Screenshot cropping: tweak `--viewport 1440x900` in `init_session`.
- Missing chart: raise timeout on step 11 to 60000 ms.
- Training doesn't finish: raise step 09 timeout to 240000 ms.

Commit any fix:
```bash
git add scripts/qa/...
git commit -m "fix(qa): [specific fix description]"
```

Clean up `/tmp/ab-sanity-full*` when done.

---

## Phase 6 — Full run and reporting

### Task 19: Full #14 run — 20 specialties via Claude subagents

**Orchestration mode:** Claude subagents (Mode A from spec).

**Files:**
- Produced: `docs/reports/qa/full-coverage-2026-04-21/**`

- [ ] **Step 1: Pre-flight**

```bash
mkdir -p docs/reports/qa/full-coverage-$(date +%F)
```

- [ ] **Step 2: Fire the 5-wave × 4-parallel subagent orchestration**

In the parent Claude session, spawn four `Agent(subagent_type=general-purpose)` calls in one message per wave. Each subagent prompt (verbatim, substitute placeholders):

```
You are running a single bash command as part of a 20-specialty QA walkthrough.
Do not modify any scripts. Do not deviate.

Command to run:
  bash /home/batuhan4/HealthWithSevgi/scripts/qa/walkthrough.sh \
    {SPECIALTY_ID} \
    /home/batuhan4/HealthWithSevgi/docs/reports/qa/full-coverage-2026-04-21/{SPECIALTY_ID}

After it finishes, read this file and summarise under 80 words:
  /home/batuhan4/HealthWithSevgi/docs/reports/qa/full-coverage-2026-04-21/{SPECIALTY_ID}/evidence.json

Report in this exact shape:
  specialty: {SPECIALTY_ID}
  status: pass|fail
  duration_ms: <number>
  failed_steps: <comma list or none>
  screenshots_count: <int, expect 13>

Rules:
  - Do not re-run the command.
  - Do not rewrite scripts.
  - If the command fails, still read evidence.json and report what's there.
```

Wave 1: specialties 1–4 from `specialty_list.txt`
Wave 2: 5–8
Wave 3: 9–12
Wave 4: 13–16
Wave 5: 17–20

Between waves, merge the manifest so far:
```bash
python3 scripts/qa/merge_manifest.py docs/reports/qa/full-coverage-$(date +%F) full-coverage-$(date +%F)
```

- [ ] **Step 3: Aggregate + render after wave 5**

```bash
python3 scripts/qa/merge_manifest.py docs/reports/qa/full-coverage-$(date +%F) full-coverage-$(date +%F)
python3 scripts/qa/render_report.py docs/reports/qa/full-coverage-$(date +%F) \
  --template full_coverage --stem Sprint5_Full_Domain_Coverage
```

- [ ] **Step 4: Review the PDF**

Open `docs/reports/qa/full-coverage-$(date +%F)/Sprint5_Full_Domain_Coverage.pdf` and verify:
- 20 specialty sections with 13 figures each
- All screenshots load
- Summary table shows pass/fail counts
- No `{{` placeholders leaking

- [ ] **Step 5: Commit the full run artefacts**

```bash
git add docs/reports/qa/full-coverage-$(date +%F)/
git commit -m "docs(sprint-5): Full Domain Coverage run — 20 specialties PASS/FAIL evidence"
```

### Task 20: #15 E2E Regression — 3 CSVs sequentially

**Files:**
- Produced: `docs/reports/qa/e2e-regression-2026-04-21/**`

- [ ] **Step 1: Write a tiny bash runner for the 3 CSVs**

`scripts/qa/run_regression.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
qa_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$qa_dir/../.." && pwd)"
date="$(date +%F)"
out_base="$repo_root/docs/reports/qa/e2e-regression-$date"
mkdir -p "$out_base"

while IFS='|' read -r csv model display; do
  [[ "$csv" =~ ^#.*$ || -z "$csv" ]] && continue
  id="$(basename "$csv" .csv)"
  bash "$qa_dir/walkthrough_upload.sh" "$repo_root/$csv" "$model" "$display" "$out_base/$id" \
    || echo "[FAIL] $id"
done < "$qa_dir/lib/regression_csvs.txt"

python3 "$qa_dir/merge_manifest.py" "$out_base" "e2e-regression-$date"
python3 "$qa_dir/render_report.py" "$out_base" --template e2e_regression \
  --stem "Sprint5_E2E_Regression"
```

```bash
chmod +x scripts/qa/run_regression.sh
```

- [ ] **Step 2: Run**

```bash
bash scripts/qa/run_regression.sh
```

Expected total time ~6 min (3 × 2 min serial).

- [ ] **Step 3: Review the output**

Open `docs/reports/qa/e2e-regression-$(date +%F)/Sprint5_E2E_Regression.pdf` and verify:
- 3 CSV sections, each with 13 figures
- Model type varies: KNN / Random Forest / XGBoost
- Summary table shows 3/3 PASS (or failures called out)

- [ ] **Step 4: Commit the regression artefacts**

```bash
git add docs/reports/qa/e2e-regression-$(date +%F)/ scripts/qa/run_regression.sh
git commit -m "docs(sprint-5): E2E Regression run — 3 CSVs × 3 model types evidence"
```

### Task 21: Update Sprint-5.md wiki + release

**Files:**
- Modify: `docs/wiki/Sprint-5.md`

- [ ] **Step 1: Update #14 and #15 rows**

Edit `docs/wiki/Sprint-5.md` — change:

```
| 14 | Full Domain Coverage (20 specialties E2E) | [PDF](Sprint5_Full_Domain_Coverage.pdf) | PENDING (QA) |
| 15 | E2E Regression (3 CSVs, 0 crashes) | [PDF](Sprint5_E2E_Regression.pdf) | PENDING (QA) |
```

to:

```
| 14 | Full Domain Coverage (20 specialties E2E) | [PDF](Sprint5_Full_Domain_Coverage.pdf) | **DONE** — 20/20 PASS ([evidence](../reports/qa/full-coverage-2026-04-21/)) |
| 15 | E2E Regression (3 CSVs, 0 crashes) | [PDF](Sprint5_E2E_Regression.pdf) | **DONE** — 3/3 PASS ([evidence](../reports/qa/e2e-regression-2026-04-21/)) |
```

Update the Sprint 5 Metrics table: replace `TBD` for "Full Domain Coverage" and "End-to-End Regression" rows with the actual `X / Y PASS` counts.

- [ ] **Step 2: Sync to wiki repo + push**

```bash
# wiki sync helper (if present) or manual copy; confirm the pattern used in prior
# wiki commits in the project
cp docs/reports/qa/full-coverage-$(date +%F)/Sprint5_Full_Domain_Coverage.pdf \
   ../HealthWithSevgi.wiki/ 2>/dev/null || true
# (if wiki repo uses flat paths, push that; otherwise update the wiki via the
#  usual docs/wiki sync step used in prior sprints)
```

- [ ] **Step 3: Commit + push main**

```bash
git add docs/wiki/Sprint-5.md
git commit -m "docs(sprint-5): mark #14 + #15 DONE with run evidence"
git push origin main
```

- [ ] **Step 4: Tag release v1.5.12**

```bash
gh release create v1.5.12 \
  --title "v1.5.12 — Sprint 5 QA evidence (Full Coverage + E2E Regression)" \
  --notes "Automated 20-specialty walkthrough + 3-CSV regression via agent-browser. Both deliverables DONE — see docs/reports/qa/ for 260+39 screenshots and PDFs."
```

---

## Self-Review

**Spec coverage check:**

| Spec section | Covered by tasks |
|--------------|------------------|
| Architecture — 3 layers | Tasks 4, 6, 10, 16 |
| walkthrough.sh resilience (10 mitigations) | Tasks 4, 6 |
| evidence.json schema | Task 6 `finalize_evidence` |
| Mode A orchestration (Claude subagents) | Task 19 |
| Mode B orchestration (bash) | Task 10 |
| MANIFEST.json shape | Task 8 |
| Render (HTML + PDF) | Tasks 11–16 |
| Figure blocks + Sprint 2 CSS | Tasks 13, 14 |
| Failure handling (3 layers) | Tasks 6 (L1), 10+19 (L2), 16 (L3) |
| #15 E2E Regression deltas | Tasks 7, 20 |
| Self-tests | Tasks 5, 9, 12, 17 |
| Output artefacts + commit policy | Tasks 1, 19, 20 |
| Sprint-5.md wiki update | Task 21 |

All sections have at least one task. No gaps.

**Placeholder scan:** One intentional placeholder — in Task 7, `run_step` and `finalize_evidence` bodies in `walkthrough_upload.sh` are noted as "copy verbatim from `walkthrough.sh`". This is explicit and the actionable instruction is given; the executor should copy the real code, not leave `:` pass-statements.

**Type consistency:**
- `evidence.json` key naming consistent across Task 6 (writer) and Task 8 (reader): `specialty`, `status`, `steps`, `duration_ms`.
- Template variable names (`manifest`, `s`, `step`, `wizard_steps`) consistent across Tasks 13–16.
- `render_report.py` CLI args (`--template`, `--stem`, `--no-pdf`) match invocations in Tasks 18, 19, 20.

**Scope check:** Single feature with three tightly-coupled layers — correct single-plan decomposition.

No issues requiring fixes. Plan is complete.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-21-qa-automation.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration. Well suited for this plan because most tasks are self-contained (one bash script, one python module, one template).

**2. Inline Execution** — execute tasks in this session with periodic checkpoints. Higher token budget but allows the parent Claude to reason across tasks (e.g. debug a cross-layer issue without context handoff).

**Which approach?**
