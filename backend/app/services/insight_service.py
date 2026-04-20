"""LLM-powered clinical insight generation.

Provider chain: MedGemma (Vertex AI) → Gemini (Google AI) → static template fallback.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Timeout per LLM call (seconds)
_LLM_TIMEOUT = 45.0


def _build_column_stats_block(context: dict) -> str:
    """Build feature statistics section for prompts."""
    stats = context.get("column_statistics", [])
    if not stats:
        return ""
    lines = "FEATURE STATISTICS (training set distributions):\n"
    for cs in stats:
        if "mean" in cs:
            lines += f"  {cs['name']}: mean={cs['mean']}, std={cs['std']}, range=[{cs['min']}, {cs['max']}]\n"
        else:
            lines += f"  {cs['name']}: (statistics unavailable)\n"
    return lines + "\n"


def _build_comparison_block(context: dict) -> str:
    """Build compared models section for prompts."""
    models = context.get("compared_models", [])
    if not models:
        return ""
    current = context.get("model_type", "unknown")
    lines = "MODEL COMPARISON (other models trained on same dataset):\n"
    for m in models:
        lines += (
            f"  - {m['model_type']}: AUC={m['auc_roc']:.3f}, "
            f"Acc={m['accuracy']:.3f}, Sens={m['sensitivity']:.3f}, "
            f"F1={m['f1_score']:.3f}, MCC={m['mcc']:.3f}\n"
        )
    lines += f"\n  The model being assessed is: {current}.\n"
    lines += f"  There are {len(models)} models total. Reference ALL of them by name with their key metrics.\n"
    lines += "  Compare the current model's strengths and weaknesses against each alternative.\n\n"
    return lines


def _build_raw_columns_block(context: dict) -> str:
    """Build raw dataset column overview (from Step 2 explore)."""
    cols = context.get("raw_column_meta", [])
    if not cols:
        return ""
    row_count = context.get("row_count_original", "?")
    lines = f"RAW DATASET OVERVIEW ({row_count} rows before preprocessing):\n"
    for c in cols:
        role = "TARGET" if c.get("is_target") else "feature"
        missing = f", missing={c['missing_count']} ({c['missing_pct']}%)" if c["missing_count"] > 0 else ""
        samples = ", ".join(c.get("sample_values", []))
        lines += (
            f"  {c['name']} [{role}]: dtype={c['dtype']}, "
            f"unique={c['unique_count']}{missing}, "
            f"samples=[{samples}]\n"
        )
    lines += "\n"
    return lines


def _build_sample_patients_block(context: dict) -> str:
    """Build sample patient rows for LLM grounding."""
    patients = context.get("sample_patients", [])
    if not patients:
        return ""
    lines = "SAMPLE PATIENTS FROM TEST SET (real data, not synthetic):\n"
    for i, row in enumerate(patients):
        outcome = row.pop("_actual_outcome", "?")
        vals = ", ".join(f"{k}={v}" for k, v in row.items())
        lines += f"  Patient {i+1}: {vals} → actual outcome: {outcome}\n"
        row["_actual_outcome"] = outcome  # restore
    lines += "  Use these real patient profiles to ground your clinical reasoning.\n\n"
    return lines


def _build_ethics_prompt(context: dict) -> str:
    """Build a structured prompt with full clinical context for ethics/bias insight."""
    specialty = context.get("specialty_name", "Unknown")
    prediction_task = context.get("what_ai_predicts", "clinical outcome")
    clinical_bg = context.get("clinical_context", "")
    model_type = context.get("model_type", "unknown")
    features = context.get("feature_names", [])
    target = context.get("target_variable", "outcome")
    classes = context.get("classes", [])

    # Model hyperparameters
    params = context.get("model_params", {})
    params_block = ", ".join(f"{k}={v}" for k, v in params.items()) if params else "defaults"

    # Class distribution in training set
    class_dist = context.get("class_distribution_train", {})
    dist_block = ", ".join(f"{k}: {v}" for k, v in class_dist.items()) if class_dist else "unknown"

    # Confusion matrix
    cm = context.get("confusion_matrix", {})
    if "TP" in cm:
        cm_block = f"TP={cm['TP']}, FP={cm['FP']}, FN={cm['FN']}, TN={cm['TN']}"
    else:
        cm_block = "multiclass (see subgroup data)"

    metrics_block = (
        f"  Accuracy:    {context.get('accuracy', 'N/A')}\n"
        f"  Sensitivity: {context.get('sensitivity', 'N/A')}  (recall — how many true positives found)\n"
        f"  Specificity: {context.get('specificity', 'N/A')}\n"
        f"  Precision:   {context.get('precision', 'N/A')}\n"
        f"  F1 Score:    {context.get('f1_score', 'N/A')}\n"
        f"  AUC-ROC:     {context.get('auc_roc', 'N/A')}\n"
        f"  MCC:         {context.get('mcc', 'N/A')}\n"
        f"  Train Acc:   {context.get('train_accuracy', 'N/A')}\n"
        f"  CV Mean:     {context.get('cv_mean', 'N/A')} (std: {context.get('cv_std', 'N/A')})\n"
        f"  Optimal threshold: {context.get('optimal_threshold', 0.5)}\n"
        f"  Confusion matrix: {cm_block}\n"
    )

    bias_lines = ""
    for sg in context.get("subgroup_details", []):
        bias_lines += (
            f"  - {sg['group']}: sensitivity={sg['sensitivity']:.1%}, "
            f"accuracy={sg['accuracy']:.1%}, n={sg['sample_size']}, "
            f"status={sg['status']}"
        )
        if sg.get("status_reason"):
            bias_lines += f" ({sg['status_reason']})"
        bias_lines += "\n"

    warnings_block = ""
    for w in context.get("bias_warnings", []):
        warnings_block += f"  - {w['group']}: {w['metric']} gap = {w['gap']:.1%}\n"

    # SHAP / Feature importance
    fi_block = ""
    for fi in context.get("feature_importances", []):
        direction_label = "increases risk" if fi["direction"] == "positive" else "decreases risk" if fi["direction"] == "negative" else "neutral"
        fi_block += f"  {fi['importance']:.3f}  {fi['clinical_name']} ({direction_label})\n"

    shap_note = context.get("top_feature_clinical_note", "")
    explained_pct = context.get("explained_variance_top5_pct", 0)

    # --- DATA BLOCK (always present) ---
    data_block = (
        f"CLINICAL DOMAIN: {specialty}\n"
        f"PREDICTION TASK: {prediction_task}\n"
        f"TARGET VARIABLE: '{target}' with classes: {classes}\n"
        f"DATA SOURCE: {context.get('data_source', 'unknown')}\n"
        f"CLINICAL BACKGROUND: {clinical_bg}\n\n"
        f"{_build_raw_columns_block(context)}"
        f"DATASET (after preprocessing):\n"
        f"  Features ({len(features)}): {', '.join(features)}\n"
        f"  Training samples: {context.get('train_size', '?')}\n"
        f"  Test samples: {context.get('test_size', '?')}\n"
        f"  Class distribution (train): {dist_block}\n"
        f"  SMOTE applied: {context.get('use_smote', False)}\n"
        f"  Normalization: {context.get('normalization', 'N/A')}\n\n"
        f"{_build_column_stats_block(context)}"
        f"{_build_sample_patients_block(context)}"
        f"CURRENT MODEL: {model_type}\n"
        f"  Hyperparameters: {params_block}\n"
        f"  Training time: {context.get('training_time_ms', 'N/A')} ms\n\n"
        f"PERFORMANCE:\n{metrics_block}\n"
        f"FEATURE IMPORTANCE (SHAP — {context.get('shap_method', 'N/A')}):\n"
        f"  Top 5 features explain {explained_pct:.1f}% of model decisions.\n"
        f"{fi_block}"
        f"  Clinical note: {shap_note}\n\n"
        f"SUBGROUP FAIRNESS:\n"
        f"  Overall sensitivity: {context.get('overall_sensitivity', 'N/A')}\n"
        f"{bias_lines}\n"
        f"BIAS WARNINGS:\n{warnings_block if warnings_block else '  None detected\n'}\n"
        f"OVERFITTING: {'YES (train={} vs test={})'.format(context.get('train_accuracy', '?'), context.get('accuracy', '?')) if context.get('overfitting_warning') else 'No significant gap'}\n\n"
    )

    # --- COMPARISON BLOCK (dynamic) ---
    comparison_block = _build_comparison_block(context)

    # --- INSTRUCTION BLOCK (adapts to available data) ---
    has_comparison = len(context.get("compared_models", [])) > 1

    if has_comparison:
        instruction = (
            "You have data from MULTIPLE models trained on the same clinical dataset. "
            "Write an insightful clinical analysis (400-550 words) in markdown.\n\n"
            "## Overall Verdict\n"
            "Give a verdict: 🟢 Deployable with monitoring, 🟡 Needs improvement, or 🔴 Not ready. "
            "Name the best model and explain WHY it wins. "
            "Use the sample patient data to illustrate — e.g., 'Patient 1 (age=75, EF=20%) died and was correctly flagged, "
            "but Patient 3 with similar risk factors was missed.'\n\n"
            "## Model Comparison\n"
            "Create a clear ranking of ALL models. For each one:\n"
            "  - Name, AUC-ROC, sensitivity, accuracy (copy exact values from MODEL COMPARISON above)\n"
            "  - One-line strength and one-line weakness\n"
            "Explain what the ranking reveals about the dataset — why do certain model families perform better?\n\n"
            "## Data & Feature Insights\n"
            "Analyze the feature statistics and sample patients together:\n"
            "  - Are features clinically meaningful for this prediction task?\n"
            "  - Any red flags? (data leakage, extreme ranges, suspicious correlations)\n"
            "  - What do the SHAP importances + actual patient profiles reveal?\n"
            "  - Class imbalance impact on results?\n\n"
            f"## Recommendations for {specialty}\n"
            "3-4 numbered, specific, actionable recommendations tied to the comparison results.\n\n"
        )
    else:
        instruction = (
            f"You have one {model_type} model trained for {prediction_task}. "
            "Write an insightful clinical analysis (300-400 words) in markdown.\n\n"
            "## Overall Verdict\n"
            "Is this model ready? Verdict: 🟢 Deployable with monitoring, 🟡 Needs improvement, or 🔴 Not ready. "
            "Use sample patient data to illustrate real impact — show how specific patients would be affected.\n\n"
            "## Data & Feature Insights\n"
            "Analyze features, their distributions, and SHAP importances:\n"
            "  - Are the top features clinically sound for this domain?\n"
            "  - Any suspicious patterns? (data leakage, features that shouldn't be available at prediction time)\n"
            "  - What do the sample patient profiles reveal about model behavior?\n"
            "  - Subgroup fairness: which patients are most at risk of being missed?\n\n"
            f"## Recommendations for {specialty}\n"
            "3-4 numbered, actionable recommendations tied to THIS model's results.\n\n"
        )

    rules = (
        "STRICT DATA RULES — VIOLATIONS WILL INVALIDATE THE ASSESSMENT:\n"
        "- NEVER invent, estimate, or round any number. Every metric you cite MUST appear exactly in the data above.\n"
        "- If you write a percentage, accuracy, sensitivity, AUC, or any number — it must be copy-pasted from the data.\n"
        "- If you mention a patient, use their exact feature values from SAMPLE PATIENTS.\n"
        "- If a piece of data is not provided above, say 'not available' — do NOT fabricate it.\n"
        "- You may provide clinical INTERPRETATION of the numbers, but the numbers themselves must be verbatim.\n\n"
        "FORMAT RULES:\n"
        "- Use markdown: **bold** key metrics, bullet points, numbered lists\n"
        "- Be direct and clinical, not academic\n"
        "- Focus on insights a clinician would find genuinely valuable\n"
    )

    return data_block + comparison_block + instruction + rules


def _build_case_study_prompt(context: dict) -> str:
    """Build prompt for case studies tied to this model's domain and weaknesses."""
    specialty = context.get("specialty_name", "Unknown")
    prediction_task = context.get("what_ai_predicts", "clinical outcome")
    features = context.get("feature_names", [])
    model_type = context.get("model_type", "unknown")

    weak_groups = [
        sg for sg in context.get("subgroup_details", [])
        if sg.get("status") != "acceptable"
    ]
    weakness_block = ""
    for sg in weak_groups:
        weakness_block += f"  - {sg['group']}: sensitivity={sg['sensitivity']:.1%}, status={sg['status']}\n"

    has_demo_features = any(f in [fn.lower() for fn in features] for f in ["sex", "gender", "age", "race", "ethnicity"])

    # Top driving features
    top_features_block = ""
    for fi in context.get("feature_importances", [])[:5]:
        top_features_block += f"  - {fi['clinical_name']} (importance: {fi['importance']:.3f}, {fi['direction']})\n"

    cm = context.get("confusion_matrix", {})
    cm_block = f"FN={cm.get('FN', '?')}, FP={cm.get('FP', '?')}" if "FN" in cm else ""

    return (
        f"A {model_type} model was trained in {specialty} "
        f"to predict: {prediction_task}.\n\n"
        f"Features used: {', '.join(features)}\n"
        f"{'Demographic features present: model uses patient demographics (sex/age) which creates fairness risk.' if has_demo_features else 'No demographic features in model.'}\n\n"
        f"TOP DRIVING FEATURES (SHAP):\n{top_features_block if top_features_block else '  Not available\n'}\n"
        f"MODEL WEAKNESSES:\n"
        f"  Accuracy: {context.get('accuracy', 'N/A')}, Sensitivity: {context.get('sensitivity', 'N/A')}, AUC: {context.get('auc_roc', 'N/A')}\n"
        f"  {cm_block}\n"
        f"  Subgroups at risk:\n{weakness_block if weakness_block else '  None identified\n'}\n"
        f"{_build_column_stats_block(context)}"
        f"{_build_sample_patients_block(context)}"
        f"{_build_comparison_block(context)}"
        "Generate exactly 3 real-world AI failure case studies RELEVANT to:\n"
        f"  - The clinical domain: {specialty}\n"
        "  - The specific weaknesses listed above\n"
        "  - The type of bias or error this model is susceptible to\n\n"
        "For each case, provide a JSON object with these exact keys:\n"
        '  "title": specific real incident title,\n'
        f'  "specialty": medical specialty (prefer {specialty} or related),\n'
        '  "year": integer 2015-2024,\n'
        '  "severity": "failure" | "near_miss" | "prevention",\n'
        '  "what_happened": 2-3 factual sentences,\n'
        '  "impact": 2-3 sentences with numbers on patient impact,\n'
        f'  "lesson": 2-3 sentences tying back to THIS {model_type} model\'s weaknesses\n\n'
        "Return ONLY a JSON array of 3 objects. No markdown, no explanation, no code fences.\n"
    )


def _strip_markdown(text: str) -> str:
    """Remove common markdown formatting from LLM output."""
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)   # **bold**
    text = re.sub(r'\*(.+?)\*', r'\1', text)         # *italic*
    text = re.sub(r'^#{1,4}\s+', '', text, flags=re.MULTILINE)  # headings
    return text.strip()


def _build_eu_ai_act_prompt(context: dict) -> str:
    """Build prompt for EU AI Act compliance enrichment."""
    specialty = context.get("specialty_name", "Unknown")
    model_type = context.get("model_type", "unknown")
    prediction_task = context.get("what_ai_predicts", "clinical outcome")

    items_block = ""
    for item in context.get("eu_ai_act_items", []):
        items_block += f'  - id: "{item["id"]}", text: "{item["text"]}", article: "{item["article"]}"\n'

    return (
        f"A {model_type} model in {specialty} predicts: {prediction_task}.\n\n"
        f"Model metrics: Accuracy={context.get('accuracy', 'N/A')}, "
        f"Sensitivity={context.get('sensitivity', 'N/A')}, "
        f"AUC-ROC={context.get('auc_roc', 'N/A')}, "
        f"MCC={context.get('mcc', 'N/A')}\n"
        f"Features: {', '.join(context.get('feature_names', []))}\n"
        f"SHAP top feature: {context.get('top_feature_clinical_note', 'N/A')}\n"
        f"Explained variance (top 5): {context.get('explained_variance_top5_pct', 0):.1f}%\n"
        f"Overall sensitivity: {context.get('overall_sensitivity', 'N/A')}\n"
        f"Overfitting: {'YES' if context.get('overfitting_warning') else 'No'}\n"
        f"Bias warnings: {len(context.get('bias_warnings', []))} detected\n\n"
        f"{_build_column_stats_block(context)}"
        "EU AI ACT COMPLIANCE ITEMS to enrich:\n"
        f"{items_block}\n"
        "For each item, write a model-specific description (2-3 sentences) that:\n"
        "- References actual metrics, features, or findings from THIS model\n"
        "- Explains the compliance status in concrete terms\n"
        "- Is written for a clinician, not a lawyer\n\n"
        "Return ONLY a JSON array of objects with keys: \"id\", \"enriched_description\"\n"
        "Return exactly one object per item above, in the same order.\n"
        "No markdown, no explanation, no code fences.\n"
    )


class InsightService:
    """Generates clinical insights using MedGemma or Gemini with template fallback."""

    def __init__(self) -> None:
        # Vertex AI MedGemma config
        self._vertex_project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        self._vertex_location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self._medgemma_endpoint = os.getenv("MEDGEMMA_ENDPOINT_ID", "")

        # Gemini API config
        self._gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self._gemini_model = os.getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it")

        self._provider = self._detect_provider()
        logger.info("InsightService initialized — provider: %s", self._provider)

    def _detect_provider(self) -> str:
        if self._medgemma_endpoint and self._vertex_project:
            return "medgemma"
        if self._gemini_api_key:
            return "gemini"
        return "template"

    async def generate_ethics_insight(self, context: dict) -> dict[str, Any]:
        """Generate clinical insight for ethics/bias assessment."""
        prompt = _build_ethics_prompt(context)
        system = (
            "You are a clinical AI safety specialist reviewing ML models in healthcare. "
            "CRITICAL: You must ONLY cite numbers that appear in the provided data. "
            "Never invent, estimate, approximate, or round any metric. "
            "If a number is not in the data, say 'not available'. "
            "You provide clinical interpretation of real metrics — you do not generate synthetic data. "
            "Be direct, evidence-based, and clinically insightful."
        )
        return await self._call_llm(prompt, "ethics", system)

    async def generate_case_studies(self, context: dict) -> dict[str, Any]:
        """Generate relevant case studies based on model metrics."""
        prompt = _build_case_study_prompt(context)
        system = (
            "You are a clinical AI safety educator. "
            "Generate domain-relevant AI failure case studies tied to this model's real weaknesses. "
            "When referencing model metrics (sensitivity, accuracy, etc.), use ONLY the exact values from the provided data. "
            "The scenarios are illustrative but all cited numbers must come from the actual model data. "
            "Return only valid JSON."
        )
        result = await self._call_llm(prompt, "case_studies", system)

        # Parse JSON array from LLM response
        if result["source"] != "template":
            try:
                import re
                text = result["text"].strip()
                # Strip markdown code fences if present
                if "```" in text:
                    match = re.search(r'```(?:json)?\s*\n?(.*?)```', text, re.DOTALL)
                    if match:
                        text = match.group(1).strip()
                # Find JSON array in text (LLM may add prose before/after)
                bracket_start = text.find("[")
                bracket_end = text.rfind("]")
                if bracket_start != -1 and bracket_end != -1:
                    text = text[bracket_start:bracket_end + 1]
                cases = json.loads(text)
                if isinstance(cases, list) and len(cases) > 0:
                    result["case_studies"] = cases
                    return result
            except (json.JSONDecodeError, IndexError, ValueError) as exc:
                logger.warning("Failed to parse case studies JSON from LLM: %s", exc)

        # Fallback: return empty so frontend uses existing static cases
        result["case_studies"] = []
        return result

    async def generate_eu_ai_act_insights(self, context: dict) -> dict[str, Any]:
        """Generate model-specific EU AI Act compliance descriptions."""
        prompt = _build_eu_ai_act_prompt(context)
        system = (
            "You are a regulatory compliance specialist for the EU AI Act. "
            "You write model-specific compliance assessments for healthcare AI systems. "
            "Reference actual metrics and findings. Return only valid JSON."
        )
        result = await self._call_llm(prompt, "eu_ai_act", system)

        if result["source"] != "template":
            try:
                import re
                text = result["text"].strip()
                if "```" in text:
                    match = re.search(r'```(?:json)?\s*\n?(.*?)```', text, re.DOTALL)
                    if match:
                        text = match.group(1).strip()
                bracket_start = text.find("[")
                bracket_end = text.rfind("]")
                if bracket_start != -1 and bracket_end != -1:
                    text = text[bracket_start:bracket_end + 1]
                items = json.loads(text)
                if isinstance(items, list) and len(items) > 0:
                    result["items"] = items
                    return result
            except (json.JSONDecodeError, IndexError, ValueError) as exc:
                logger.warning("Failed to parse EU AI Act JSON from LLM: %s", exc)

        result["items"] = []
        return result

    async def _call_llm(self, prompt: str, task: str, system: str = "") -> dict[str, Any]:
        """Try MedGemma → Gemini → template."""
        # Try MedGemma via Vertex AI
        if self._provider == "medgemma" or (self._medgemma_endpoint and self._vertex_project):
            try:
                text = await self._call_medgemma(prompt, system)
                return {"source": "medgemma", "text": text}
            except Exception as exc:
                logger.warning("MedGemma failed (%s), falling back to Gemini: %s", task, exc)

        # Try Gemini API
        if self._gemini_api_key:
            try:
                text = await self._call_gemini(prompt, system)
                return {"source": "gemini", "text": text}
            except Exception as exc:
                logger.warning("Gemini failed (%s), falling back to template: %s", task, exc)

        # Template fallback
        return {"source": "template", "text": ""}

    async def _call_medgemma(self, prompt: str, system: str = "") -> str:
        """Call MedGemma deployed on Vertex AI (vLLM container with OpenAI-compatible API)."""
        import subprocess
        token_result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True, text=True, timeout=5,
        )
        if token_result.returncode != 0:
            raise RuntimeError("Failed to get gcloud access token")
        token = token_result.stdout.strip()

        # vLLM container exposes OpenAI-compatible /v1/chat/completions via rawPredict
        url = (
            f"https://{self._vertex_location}-aiplatform.googleapis.com/v1/"
            f"projects/{self._vertex_project}/locations/{self._vertex_location}/"
            f"endpoints/{self._medgemma_endpoint}:rawPredict"
        )

        async with httpx.AsyncClient(timeout=_LLM_TIMEOUT) as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "model": "google/medgemma-4b-it",
                    "messages": [
                        {"role": "system", "content": system or "You are a clinical AI safety specialist."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            # Fallback: try predict format
            predictions = data.get("predictions", [])
            if predictions:
                return predictions[0] if isinstance(predictions[0], str) else str(predictions[0])
            raise RuntimeError(f"Empty MedGemma response: {data}")

    async def _call_gemini(self, prompt: str, system: str = "") -> str:
        """Call Gemini via Google AI Studio REST API."""
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self._gemini_model}:generateContent"
            f"?key={self._gemini_api_key}"
        )

        body: dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 8192,
                "temperature": 0.3,
            },
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}

        async with httpx.AsyncClient(timeout=_LLM_TIMEOUT) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                finish_reason = candidates[0].get("finishReason", "UNKNOWN")
                parts = candidates[0].get("content", {}).get("parts", [])
                # Gemma 4 (and any reasoning model) returns a separate part with
                # thought=True containing chain-of-thought; skip those and take
                # only the final-answer parts.
                answer_parts = [p for p in parts if not p.get("thought", False)]
                text = "".join(p.get("text", "") for p in answer_parts)
                logger.info(
                    "Gemini response: %d chars, finishReason=%s, parts=%d (%d answer)",
                    len(text), finish_reason, len(parts), len(answer_parts),
                )
                if finish_reason == "MAX_TOKENS":
                    logger.warning("Gemini output was truncated (MAX_TOKENS)")
                if text:
                    return text
            raise RuntimeError("Empty Gemini response")
