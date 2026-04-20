"""PDF certificate generation using ReportLab."""
from __future__ import annotations

import datetime
import math
from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable

from app.models.explain_schemas import CertificateRequest, EthicsResponse
from app.models.ml_schemas import MetricsResponse, ModelType

# Colour palette — using the app's green as PRIMARY
PRIMARY = colors.HexColor("#1A7A4C")
PRIMARY_DARK = colors.HexColor("#145E39")
PRIMARY_LIGHT = colors.HexColor("#E8F5EE")
SUCCESS = colors.HexColor("#1A7A4C")
SUCCESS_BG = colors.HexColor("#F0FDF4")
WARNING = colors.HexColor("#92400E")
WARNING_BG = colors.HexColor("#FFF7ED")
DANGER = colors.HexColor("#991B1B")
DANGER_BG = colors.HexColor("#FFF1F2")
LIGHT_GREY = colors.HexColor("#F4F7FB")
MID_GREY = colors.HexColor("#DDE3EC")
DARK_TEXT = colors.HexColor("#172B4D")
ACCENT = colors.HexColor("#0EA5E9")

MODEL_LABELS = {
    ModelType.KNN: "K-Nearest Neighbours (KNN)",
    ModelType.SVM: "Support Vector Machine (SVM)",
    ModelType.DECISION_TREE: "Decision Tree",
    ModelType.RANDOM_FOREST: "Random Forest",
    ModelType.LOGISTIC_REGRESSION: "Logistic Regression",
    ModelType.NAIVE_BAYES: "Naïve Bayes",
    ModelType.XGBOOST: "XGBoost (Extreme Gradient Boosting)",
    ModelType.LIGHTGBM: "LightGBM (Light Gradient Boosting)",
}


# ---------------------------------------------------------------------------
# Custom flowable: full-width coloured banner block
# ---------------------------------------------------------------------------

class _BannerBlock(Flowable):
    """Draws a filled rectangle spanning the full page width at the top."""

    def __init__(self, width: float, height: float, bg_color: colors.Color,
                 title: str):
        """Store the label + colour so the flowable is self-contained during layout."""
        super().__init__()
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.title = title

    def draw(self):
        """Render the rectangle + label onto the current canvas."""
        c = self.canv
        c.setFillColor(self.bg_color)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        c.setFillColor(PRIMARY_DARK)
        c.rect(0, 0, self.width, 3, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(self.width / 2, self.height / 2 + 2, self.title)


class _BorderFrame(Flowable):
    """Draws a decorative double-line border around the page."""

    def __init__(self, page_width: float, page_height: float,
                 margin: float, color: colors.Color):
        """Store the inner flowables + border colour."""
        super().__init__()
        self.page_width = page_width
        self.page_height = page_height
        self.margin = margin
        self.color = color
        self.width = 0
        self.height = 0

    def draw(self):
        """Draw the border + delegate inner rendering to the wrapped flowables."""
        c = self.canv
        m = self.margin
        pw, ph = self.page_width, self.page_height
        c.setStrokeColor(self.color)
        # Outer border
        c.setLineWidth(2.5)
        c.rect(m - 8, m - 8, pw - 2 * (m - 8), ph - 2 * (m - 8),
               fill=0, stroke=1)
        # Inner border (inset by 4 pts)
        c.setLineWidth(0.8)
        c.rect(m - 4, m - 4, pw - 2 * (m - 4), ph - 2 * (m - 4),
               fill=0, stroke=1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _metric_colour(value: float, green: float, amber: float) -> colors.Color:
    """Pick a banner colour for a metric value (green/amber/red) based on configured thresholds."""
    if value >= green:
        return SUCCESS
    if value >= amber:
        return WARNING
    return DANGER


def _pct(value: float) -> str:
    """Format a 0..1 number as a one-decimal percentage string."""
    return f"{value * 100:.1f}%"


def _row_bg(val: float, green: float, amber: float) -> colors.Color:
    """Alternate row background colour for zebra-striped tables."""
    if val >= green:
        return SUCCESS_BG
    if val >= amber:
        return WARNING_BG
    return DANGER_BG


def _compute_mcc(tp: int, tn: int, fp: int, fn: int) -> Optional[float]:
    """Compute Matthews Correlation Coefficient from a confusion matrix row."""
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    if denom == 0:
        return None
    return (tp * tn - fp * fn) / denom


def _generate_takeaways(metrics: MetricsResponse, model_type: ModelType) -> list[str]:
    """Auto-generate bullet-point takeaways from model metrics."""
    bullets: list[str] = []
    model_label = MODEL_LABELS.get(model_type, str(model_type))

    # Sensitivity (clinical priority)
    if metrics.sensitivity >= 0.85:
        bullets.append(
            f"Excellent sensitivity ({_pct(metrics.sensitivity)}): the model correctly identifies the "
            "large majority of positive cases, making it well-suited for clinical screening."
        )
    elif metrics.sensitivity >= 0.70:
        bullets.append(
            f"Acceptable sensitivity ({_pct(metrics.sensitivity)}): most positive cases are detected, "
            "though some missed diagnoses remain possible."
        )
    else:
        bullets.append(
            f"Low sensitivity ({_pct(metrics.sensitivity)}): the model misses a substantial proportion "
            "of positive cases — not recommended for screening without further tuning."
        )

    # Specificity
    if metrics.specificity >= 0.85:
        bullets.append(
            f"High specificity ({_pct(metrics.specificity)}): very few healthy patients are incorrectly "
            "flagged, reducing unnecessary follow-up burden."
        )
    elif metrics.specificity < 0.65:
        bullets.append(
            f"Below-average specificity ({_pct(metrics.specificity)}): a notable false-positive rate "
            "could lead to unnecessary investigations in healthy patients."
        )

    # AUC
    if metrics.auc_roc >= 0.90:
        bullets.append(
            f"Outstanding discrimination (AUC = {_pct(metrics.auc_roc)}): the model reliably ranks "
            "positive cases above negative ones across all decision thresholds."
        )
    elif metrics.auc_roc >= 0.75:
        bullets.append(
            f"Good discriminative ability (AUC = {_pct(metrics.auc_roc)}): the model provides useful "
            "separation between classes across operating points."
        )
    else:
        bullets.append(
            f"Weak discrimination (AUC = {_pct(metrics.auc_roc)}): the model struggles to separate "
            "positive from negative cases and should be improved before deployment."
        )

    # Overfitting warning
    if metrics.overfitting_warning:
        gap = metrics.train_accuracy - metrics.accuracy
        bullets.append(
            f"Overfitting detected: training accuracy ({_pct(metrics.train_accuracy)}) is considerably "
            f"higher than test accuracy ({_pct(metrics.accuracy)}, gap = {gap * 100:.1f} pp). "
            "Consider regularisation, pruning, or collecting more data."
        )
    else:
        bullets.append(
            f"Generalisation is healthy: the gap between training ({_pct(metrics.train_accuracy)}) "
            f"and test accuracy ({_pct(metrics.accuracy)}) is within acceptable bounds."
        )

    # MCC
    if hasattr(metrics, "mcc") and metrics.mcc is not None:
        mcc = metrics.mcc
        if mcc >= 0.6:
            bullets.append(
                f"Strong overall balance (MCC = {mcc:.3f}): the model performs well even if class "
                "sizes are imbalanced."
            )
        elif mcc >= 0.3:
            bullets.append(
                f"Moderate overall balance (MCC = {mcc:.3f}): the model shows some robustness to "
                "class imbalance, but there is room for improvement."
            )
        else:
            bullets.append(
                f"Poor balance score (MCC = {mcc:.3f}): the model may be biased toward the majority "
                "class. Consider resampling or adjusted class weights."
            )

    # Cross-val stability
    if metrics.cross_val_scores:
        cv_mean = sum(metrics.cross_val_scores) / len(metrics.cross_val_scores)
        cv_std = math.sqrt(
            sum((x - cv_mean) ** 2 for x in metrics.cross_val_scores)
            / len(metrics.cross_val_scores)
        )
        if cv_std <= 0.03:
            bullets.append(
                f"{len(metrics.cross_val_scores)}-fold cross-validation shows very stable performance "
                f"(mean {_pct(cv_mean)} ± {cv_std * 100:.1f} pp), indicating the result is unlikely "
                "to be a lucky split."
            )
        elif cv_std <= 0.06:
            bullets.append(
                f"{len(metrics.cross_val_scores)}-fold cross-validation shows moderate variability "
                f"(mean {_pct(cv_mean)} ± {cv_std * 100:.1f} pp). "
                "The model is reasonably stable across data splits."
            )
        else:
            bullets.append(
                f"{len(metrics.cross_val_scores)}-fold cross-validation shows high variability "
                f"(mean {_pct(cv_mean)} ± {cv_std * 100:.1f} pp). "
                "Performance may depend heavily on how the data is split."
            )

    # Model-specific notes
    if model_type in (ModelType.RANDOM_FOREST, ModelType.XGBOOST, ModelType.LIGHTGBM):
        bullets.append(
            f"{model_label} is an ensemble method that aggregates many weak learners; "
            "feature-importance outputs are available for clinical interpretability."
        )
    elif model_type == ModelType.LOGISTIC_REGRESSION:
        bullets.append(
            "Logistic Regression produces calibrated probabilities and fully interpretable "
            "coefficients, making it a strong baseline for clinical audit."
        )
    elif model_type == ModelType.DECISION_TREE:
        bullets.append(
            "Decision Trees are highly interpretable but prone to overfitting on small datasets; "
            "examine the max-depth parameter if overfitting is observed."
        )

    return bullets


# ---------------------------------------------------------------------------
# Certificate service
# ---------------------------------------------------------------------------

class CertificateService:
    """
    Produces the EU AI Act compliance PDF (overview, fairness, explainability, checklist,
    signatures) via reportlab.
    """
    def generate_pdf(
        self,
        cert_request: CertificateRequest,
        metrics: MetricsResponse,
        ethics: EthicsResponse,
        specialty_name: str,
        model_type: ModelType,
        training_time_ms: Optional[float] = None,
    ) -> bytes:
        """Main entrypoint — build the full PDF for a session and return it as bytes."""
        buf = BytesIO()
        PAGE_W, PAGE_H = A4
        MARGIN = 2 * cm

        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=2.2 * cm,
        )
        CONTENT_W = PAGE_W - 2 * MARGIN

        styles = getSampleStyleSheet()

        h2 = ParagraphStyle(
            "H2", parent=styles["Heading2"],
            fontSize=13, textColor=PRIMARY_DARK, spaceBefore=16, spaceAfter=5,
            borderPad=3,
        )
        body = ParagraphStyle(
            "Body", parent=styles["Normal"],
            fontSize=10, textColor=DARK_TEXT, leading=14,
        )
        body_center = ParagraphStyle(
            "BodyCenter", parent=body,
            alignment=1,
        )
        small = ParagraphStyle(
            "Small", parent=styles["Normal"],
            fontSize=8, textColor=colors.HexColor("#6B7280"), leading=11,
        )
        small_center = ParagraphStyle(
            "SmallCenter", parent=small,
            alignment=1,
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer", parent=small,
            textColor=DANGER, alignment=1, leading=11,
        )
        bullet_style = ParagraphStyle(
            "Bullet", parent=styles["Normal"],
            fontSize=9, textColor=DARK_TEXT, leading=13,
            leftIndent=14, firstLineIndent=-10,
        )
        cell8 = ParagraphStyle(
            "Cell8", parent=styles["Normal"],
            fontSize=8, textColor=DARK_TEXT, leading=10,
        )

        story = []

        # ---- PAGE BORDER (drawn via canvas callback — we approximate with a table border) ----
        # We'll use a single-cell table at the very start to act as a framing border.
        # This works because SimpleDocTemplate renders top to bottom.
        # A more robust approach uses page templates; here we use a thin top-rule trick.

        # ---- GREEN HEADER BANNER ----
        banner = _BannerBlock(
            width=CONTENT_W,
            height=1.8 * cm,
            bg_color=PRIMARY,
            title="HEALTH-AI · ML Learning Tool",
        )
        story.append(banner)
        story.append(Spacer(1, 0.4 * cm))

        issued_to = cert_request.clinician_name or "Healthcare Professional"
        institution = cert_request.institution or "Healthcare Institution"
        today = datetime.date.today().strftime("%d %B %Y")

        story.append(Paragraph(
            f"This certificate is issued to <b>{issued_to}</b> of <b>{institution}</b> "
            f"for completing the HEALTH-AI ML Learning Tool educational exercise on <b>{today}</b>.",
            body_center,
        ))
        story.append(Spacer(1, 0.4 * cm))

        # ---- SECTION 1: Specialty & Model ----
        story.append(Paragraph("1. Clinical Specialty &amp; AI Model", h2))

        info_data = [
            ["Medical Specialty", specialty_name],
            ["AI Model Type", MODEL_LABELS.get(model_type, str(model_type))],
            ["Model ID", cert_request.model_id[:24] + ("…" if len(cert_request.model_id) > 24 else "")],
        ]
        if training_time_ms is not None:
            if training_time_ms >= 1000:
                time_str = f"{training_time_ms / 1000:.2f} s"
            else:
                time_str = f"{training_time_ms:.0f} ms"
            info_data.append(["Training Time", time_str])

        info_table = Table(info_data, colWidths=[5.5 * cm, 11.5 * cm])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), PRIMARY_LIGHT),
            ("TEXTCOLOR", (0, 0), (-1, -1), DARK_TEXT),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_GREY]),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, -1), (-1, -1), 1.5, PRIMARY),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.4 * cm))

        # ---- SECTION 2: Performance Metrics ----
        story.append(Paragraph("2. Model Performance Summary", h2))
        story.append(Paragraph(
            "Performance measured on held-out test patients the model had never seen during training.",
            body,
        ))
        story.append(Spacer(1, 0.2 * cm))

        # Resolve MCC: prefer the field on MetricsResponse, fall back to computing from CM
        mcc_value: Optional[float] = getattr(metrics, "mcc", None)
        cm_data = metrics.confusion_matrix
        if mcc_value is None or mcc_value == 0.0:
            mcc_value = _compute_mcc(cm_data.tp, cm_data.tn, cm_data.fp, cm_data.fn)

        metric_rows = [
            ["Metric", "Value", "Threshold", "Status"],
            ["Accuracy", _pct(metrics.accuracy), "≥ 65 %",
             "✓  Acceptable" if metrics.accuracy >= 0.65 else "✗  Below threshold"],
            ["Sensitivity ★", _pct(metrics.sensitivity), "≥ 70 %",
             "✓  Acceptable" if metrics.sensitivity >= 0.70 else "✗  Below threshold"],
            ["Specificity", _pct(metrics.specificity), "≥ 65 %",
             "✓  Acceptable" if metrics.specificity >= 0.65 else "✗  Below threshold"],
            ["Precision (PPV)", _pct(metrics.precision), "≥ 60 %",
             "✓  Acceptable" if metrics.precision >= 0.60 else "✗  Below threshold"],
            ["F1 Score", _pct(metrics.f1_score), "≥ 65 %",
             "✓  Acceptable" if metrics.f1_score >= 0.65 else "✗  Below threshold"],
            ["AUC-ROC", _pct(metrics.auc_roc), "≥ 75 %",
             "✓  Acceptable" if metrics.auc_roc >= 0.75 else "✗  Below threshold"],
        ]

        if mcc_value is not None:
            metric_rows.append([
                "MCC †", f"{mcc_value:.3f}", "≥ 0.30",
                "✓  Acceptable" if mcc_value >= 0.30 else "✗  Below threshold",
            ])

        # Build per-row background colours
        perf_vals_thresholds = [
            (metrics.accuracy, 0.65, 0.55),
            (metrics.sensitivity, 0.70, 0.50),
            (metrics.specificity, 0.65, 0.55),
            (metrics.precision, 0.60, 0.50),
            (metrics.f1_score, 0.65, 0.55),
            (metrics.auc_roc, 0.75, 0.65),
        ]
        if mcc_value is not None:
            perf_vals_thresholds.append((mcc_value, 0.30, 0.10))

        row_bgs = [PRIMARY]  # header row
        for val, gt, at in perf_vals_thresholds:
            row_bgs.append(_row_bg(val, gt, at))

        perf_table = Table(metric_rows, colWidths=[5 * cm, 2.8 * cm, 3.2 * cm, 6 * cm])
        ts = [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ALIGN", (1, 0), (2, -1), "CENTER"),
        ]
        for i, bg in enumerate(row_bgs):
            ts.append(("BACKGROUND", (0, i), (-1, i), bg))
        # Colour the Value and Status columns
        for i, (val, gt, at) in enumerate(perf_vals_thresholds, start=1):
            col = SUCCESS if val >= gt else (WARNING if val >= at else DANGER)
            ts.append(("TEXTCOLOR", (1, i), (1, i), col))
            ts.append(("FONTNAME", (1, i), (1, i), "Helvetica-Bold"))
            ts.append(("TEXTCOLOR", (3, i), (3, i), col))
            ts.append(("FONTNAME", (3, i), (3, i), "Helvetica-Bold"))
        perf_table.setStyle(TableStyle(ts))
        story.append(perf_table)
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            "★ Sensitivity (recall) is the most critical metric for clinical screening tools.  "
            "† MCC (Matthews Correlation Coefficient) accounts for class imbalance.",
            small,
        ))
        story.append(Spacer(1, 0.3 * cm))

        # ---- Confusion matrix summary ----
        story.append(Paragraph(
            "<b>Confusion Matrix Summary</b>",
            ParagraphStyle("CMHead", parent=body, textColor=PRIMARY_DARK, spaceAfter=4),
        ))
        cm_rows = [
            ["", "Predicted Positive", "Predicted Negative"],
            [
                "Actual Positive",
                f"TP = {cm_data.tp}",
                f"FN = {cm_data.fn}",
            ],
            [
                "Actual Negative",
                f"FP = {cm_data.fp}",
                f"TN = {cm_data.tn}",
            ],
        ]
        cm_table = Table(cm_rows, colWidths=[4.5 * cm, 4.5 * cm, 4.5 * cm])
        cm_ts = [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("BACKGROUND", (0, 0), (0, -1), PRIMARY_LIGHT),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("TEXTCOLOR", (0, 1), (0, -1), PRIMARY_DARK),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            # TP cell — green
            ("BACKGROUND", (1, 1), (1, 1), SUCCESS_BG),
            ("TEXTCOLOR", (1, 1), (1, 1), SUCCESS),
            ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
            # TN cell — green
            ("BACKGROUND", (2, 2), (2, 2), SUCCESS_BG),
            ("TEXTCOLOR", (2, 2), (2, 2), SUCCESS),
            ("FONTNAME", (2, 2), (2, 2), "Helvetica-Bold"),
            # FP cell — amber
            ("BACKGROUND", (1, 2), (1, 2), WARNING_BG),
            ("TEXTCOLOR", (1, 2), (1, 2), WARNING),
            ("FONTNAME", (1, 2), (1, 2), "Helvetica-Bold"),
            # FN cell — red
            ("BACKGROUND", (2, 1), (2, 1), DANGER_BG),
            ("TEXTCOLOR", (2, 1), (2, 1), DANGER),
            ("FONTNAME", (2, 1), (2, 1), "Helvetica-Bold"),
        ]
        cm_table.setStyle(TableStyle(cm_ts))
        story.append(cm_table)
        story.append(Spacer(1, 0.2 * cm))

        # Cross-val summary
        if metrics.cross_val_scores:
            cv = metrics.cross_val_scores
            cv_mean = sum(cv) / len(cv)
            cv_std = math.sqrt(sum((x - cv_mean) ** 2 for x in cv) / len(cv))
            cv_min = min(cv)
            cv_max = max(cv)
            story.append(Paragraph(
                f"<b>{len(cv)}-Fold Cross-Validation:</b>  "
                f"mean accuracy = <b>{_pct(cv_mean)}</b>  |  "
                f"std = {cv_std * 100:.1f} pp  |  "
                f"range [{_pct(cv_min)} – {_pct(cv_max)}]",
                ParagraphStyle("CVLine", parent=small,
                               textColor=DARK_TEXT, leading=12),
            ))
            story.append(Spacer(1, 0.1 * cm))

        story.append(Spacer(1, 0.4 * cm))

        # ---- SECTION 3: Bias Findings ----
        story.append(Paragraph("3. Bias &amp; Fairness Findings", h2))
        if ethics.bias_warnings:
            for w in ethics.bias_warnings:
                story.append(Paragraph(f"⚠  {w.message}", ParagraphStyle(
                    "Warn", parent=body, textColor=DANGER, spaceAfter=3,
                )))
        else:
            story.append(Paragraph(
                "✓  No significant bias detected across patient subgroups.",
                ParagraphStyle("OK", parent=body, textColor=SUCCESS),
            ))
        story.append(Spacer(1, 0.2 * cm))

        subgroup_data = [["Subgroup", "n", "Accuracy", "Sens.", "Spec.", "F1", "Status"]]
        for sm in ethics.subgroup_metrics:
            status_sym = {"acceptable": "✓", "review": "⚠", "action_needed": "✗"}.get(sm.status, "?")
            subgroup_data.append([
                Paragraph(sm.group_label, cell8),
                str(sm.sample_size),
                _pct(sm.accuracy), _pct(sm.sensitivity), _pct(sm.specificity),
                _pct(sm.f1_score),
                f"{status_sym}  {sm.status.replace('_', ' ').title()}",
            ])
        sg_table = Table(
            subgroup_data,
            colWidths=[3.2 * cm, 1.2 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm, 4.2 * cm],
        )
        sg_ts = [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, MID_GREY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ]
        for i, sm in enumerate(ethics.subgroup_metrics, 1):
            col = (SUCCESS if sm.status == "acceptable"
                   else WARNING if sm.status == "review" else DANGER)
            sg_ts.append(("TEXTCOLOR", (6, i), (6, i), col))
            sg_ts.append(("FONTNAME", (6, i), (6, i), "Helvetica-Bold"))
        sg_table.setStyle(TableStyle(sg_ts))
        story.append(sg_table)
        story.append(Spacer(1, 0.4 * cm))

        # ---- SECTION 4: EU AI Act Checklist ----
        story.append(Paragraph("4. EU AI Act Compliance Checklist", h2))
        checklist_state = cert_request.checklist_state or {}
        checklist_data = [["#", "Requirement", "Status"]]
        for i, item in enumerate(ethics.eu_ai_act_items, 1):
            is_checked = item.get("pre_checked") or checklist_state.get(item["id"], False)
            checklist_data.append([
                str(i),
                Paragraph(item["text"], cell8),
                "✓  Complete" if is_checked else "○  Pending",
            ])
        cl_table = Table(checklist_data, colWidths=[1 * cm, 14 * cm, 2 * cm])
        cl_ts = [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, MID_GREY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
        for i, item in enumerate(ethics.eu_ai_act_items, 1):
            is_checked = item.get("pre_checked") or checklist_state.get(item["id"], False)
            if is_checked:
                cl_ts.append(("TEXTCOLOR", (2, i), (2, i), SUCCESS))
                cl_ts.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))
            else:
                cl_ts.append(("TEXTCOLOR", (2, i), (2, i), colors.HexColor("#9CA3AF")))
        cl_table.setStyle(TableStyle(cl_ts))
        story.append(cl_table)
        story.append(Spacer(1, 0.4 * cm))

        # ---- SECTION 5: Key Takeaways ----
        story.append(Paragraph("5. Key Takeaways", h2))
        story.append(Paragraph(
            "Auto-generated insights based on this model's performance metrics:",
            ParagraphStyle("TkIntro", parent=body, textColor=colors.HexColor("#4B5563"),
                           spaceAfter=5),
        ))
        takeaways = _generate_takeaways(metrics, model_type)
        for idx, bullet in enumerate(takeaways, 1):
            story.append(Paragraph(f"<b>{idx}.</b>  {bullet}", bullet_style))
            story.append(Spacer(1, 0.1 * cm))
        story.append(Spacer(1, 0.3 * cm))

        # ---- FOOTER ----
        story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY,
                                spaceAfter=4))
        story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY,
                                spaceAfter=5))

        story.append(Paragraph(
            f"Generated: <b>{today}</b>  ·  HEALTH-AI ML Learning Tool v1.5  "
            "·  Prepared by the HealthWithSevgi Team",
            small_center,
        ))
        story.append(Spacer(1, 0.15 * cm))
        story.append(Paragraph(
            "<b>IMPORTANT DISCLAIMER:</b>  This certificate confirms completion of an educational "
            "exercise only. The AI model described herein is <b>NOT</b> validated for clinical use "
            "and must <b>NOT</b> be used to inform patient management decisions without appropriate "
            "prospective clinical validation and regulatory clearance.",
            disclaimer_style,
        ))

        def _add_page_number(canvas, doc_template):
            """Inner canvas callback that stamps `Page X / N` on every page."""
            canvas.saveState()
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(colors.HexColor("#9CA3AF"))
            canvas.drawCentredString(
                PAGE_W / 2, 1.0 * cm,
                f"Page {canvas.getPageNumber()}"
            )
            canvas.restoreState()

        doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
        return buf.getvalue()
