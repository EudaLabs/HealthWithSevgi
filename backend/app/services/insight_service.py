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
_LLM_TIMEOUT = 15.0


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

    return (
        f"You are a clinical AI safety specialist reviewing a {model_type} model.\n\n"
        f"CLINICAL DOMAIN: {specialty}\n"
        f"PREDICTION TASK: {prediction_task}\n"
        f"TARGET VARIABLE: '{target}' with classes: {classes}\n"
        f"DATA SOURCE: {context.get('data_source', 'unknown')}\n"
        f"CLINICAL BACKGROUND: {clinical_bg}\n\n"
        f"DATASET:\n"
        f"  Features ({len(features)}): {', '.join(features)}\n"
        f"  Training samples: {context.get('train_size', '?')}\n"
        f"  Test samples: {context.get('test_size', '?')}\n"
        f"  Class distribution (train): {dist_block}\n"
        f"  SMOTE applied: {context.get('use_smote', False)}\n"
        f"  Normalization: {context.get('normalization', 'N/A')}\n\n"
        f"MODEL CONFIGURATION:\n"
        f"  Algorithm: {model_type}\n"
        f"  Hyperparameters: {params_block}\n"
        f"  Training time: {context.get('training_time_ms', 'N/A')} ms\n\n"
        f"MODEL PERFORMANCE:\n{metrics_block}\n"
        f"FEATURE IMPORTANCE (SHAP — {context.get('shap_method', 'N/A')}):\n"
        f"  Top 5 features explain {explained_pct:.1f}% of model decisions.\n"
        f"{fi_block}"
        f"  Clinical note: {shap_note}\n\n"
        f"SUBGROUP FAIRNESS (test set):\n"
        f"  Overall sensitivity: {context.get('overall_sensitivity', 'N/A')}\n"
        f"{bias_lines}\n"
        f"BIAS WARNINGS:\n{warnings_block if warnings_block else '  None detected\n'}\n"
        "OVERFITTING: "
        f"{'YES — train accuracy is significantly higher than test accuracy' if context.get('overfitting_warning') else 'No significant overfitting detected'}\n"
        f"{'LOW SENSITIVITY WARNING: model misses too many positive cases' if context.get('low_sensitivity_warning') else ''}\n\n"
        "Write a structured clinical assessment (250-350 words) using this EXACT markdown format:\n\n"
        "## Model Reliability\n"
        f"Assess whether this {model_type} is reliable for {prediction_task}. "
        "Include a verdict: one of 🟢 Deployable with monitoring, 🟡 Needs improvement before deployment, or 🔴 Not ready for clinical use. "
        "Cite accuracy, AUC-ROC, sensitivity, confusion matrix (especially FN count — missed patients). "
        "Mention overfitting risk if train vs test gap is large.\n\n"
        "## Key Risk Factors\n"
        "List the top 3-4 SHAP features driving predictions. For each, explain in plain clinical language "
        "what it means and whether the model's reliance on it is clinically sound or concerning. "
        "Use bullet points.\n\n"
        "## Bias & Fairness Concerns\n"
        "Which patient subgroups have the worst sensitivity? Cite the exact percentages. "
        "Explain what this means in practice (e.g., 'Female patients with heart failure are 2x more likely to be missed'). "
        "Relate demographic gaps to the feature importances if relevant.\n\n"
        f"## Recommendations for {specialty} Clinicians\n"
        "Give 3-4 specific, actionable recommendations. Not generic — tied to THIS model's metrics and domain. "
        "Use numbered list.\n\n"
        "RULES:\n"
        "- Use markdown: **bold** for key numbers, bullet points, numbered lists\n"
        "- Reference actual numbers from the data above, not approximations\n"
        "- Be direct and clinical, not academic\n"
        "- Each section should be 2-4 sentences or bullet points\n"
    )


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
        f"You are a clinical AI safety educator. A {model_type} model was trained in {specialty} "
        f"to predict: {prediction_task}.\n\n"
        f"Features used: {', '.join(features)}\n"
        f"{'Demographic features present: model uses patient demographics (sex/age) which creates fairness risk.' if has_demo_features else 'No demographic features in model.'}\n\n"
        f"TOP DRIVING FEATURES (SHAP):\n{top_features_block if top_features_block else '  Not available\n'}\n"
        f"MODEL WEAKNESSES:\n"
        f"  Accuracy: {context.get('accuracy', 'N/A')}, Sensitivity: {context.get('sensitivity', 'N/A')}, AUC: {context.get('auc_roc', 'N/A')}\n"
        f"  {cm_block}\n"
        f"  Subgroups at risk:\n{weakness_block if weakness_block else '  None identified\n'}\n"
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


class InsightService:
    """Generates clinical insights using MedGemma or Gemini with template fallback."""

    def __init__(self) -> None:
        # Vertex AI MedGemma config
        self._vertex_project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        self._vertex_location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self._medgemma_endpoint = os.getenv("MEDGEMMA_ENDPOINT_ID", "")

        # Gemini API config
        self._gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self._gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

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
        return await self._call_llm(prompt, "ethics")

    async def generate_case_studies(self, context: dict) -> dict[str, Any]:
        """Generate relevant case studies based on model metrics."""
        prompt = _build_case_study_prompt(context)
        result = await self._call_llm(prompt, "case_studies")

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

    async def _call_llm(self, prompt: str, task: str) -> dict[str, Any]:
        """Try MedGemma → Gemini → template."""
        # Try MedGemma via Vertex AI
        if self._provider == "medgemma" or (self._medgemma_endpoint and self._vertex_project):
            try:
                text = await self._call_medgemma(prompt)
                return {"source": "medgemma", "text": text}
            except Exception as exc:
                logger.warning("MedGemma failed (%s), falling back to Gemini: %s", task, exc)

        # Try Gemini API
        if self._gemini_api_key:
            try:
                text = await self._call_gemini(prompt)
                return {"source": "gemini", "text": text}
            except Exception as exc:
                logger.warning("Gemini failed (%s), falling back to template: %s", task, exc)

        # Template fallback
        return {"source": "template", "text": ""}

    async def _call_medgemma(self, prompt: str) -> str:
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
                        {"role": "system", "content": "You are a clinical AI safety specialist."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.7,
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

    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini via Google AI Studio REST API."""
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self._gemini_model}:generateContent"
            f"?key={self._gemini_api_key}"
        )

        async with httpx.AsyncClient(timeout=_LLM_TIMEOUT) as client:
            resp = await client.post(url, json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": 1024,
                    "temperature": 0.7,
                },
            })
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                finish_reason = candidates[0].get("finishReason", "UNKNOWN")
                parts = candidates[0].get("content", {}).get("parts", [])
                text = parts[0].get("text", "") if parts else ""
                logger.info(
                    "Gemini response: %d chars, finishReason=%s",
                    len(text), finish_reason,
                )
                if finish_reason == "MAX_TOKENS":
                    logger.warning("Gemini output was truncated (MAX_TOKENS)")
                if text:
                    return text
            raise RuntimeError("Empty Gemini response")
