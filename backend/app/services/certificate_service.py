"""PDF certificate generation using ReportLab."""
from __future__ import annotations

import datetime
from io import BytesIO

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

from app.models.explain_schemas import CertificateRequest, EthicsResponse
from app.models.ml_schemas import MetricsResponse, ModelType

# Colour palette
PRIMARY = colors.HexColor("#1E6B9C")
SUCCESS = colors.HexColor("#00875A")
WARNING = colors.HexColor("#FFAB00")
DANGER = colors.HexColor("#DE350B")
LIGHT_GREY = colors.HexColor("#F4F7FB")
MID_GREY = colors.HexColor("#DDE3EC")
DARK_TEXT = colors.HexColor("#172B4D")

MODEL_LABELS = {
    ModelType.KNN: "K-Nearest Neighbours (KNN)",
    ModelType.SVM: "Support Vector Machine (SVM)",
    ModelType.DECISION_TREE: "Decision Tree",
    ModelType.RANDOM_FOREST: "Random Forest",
    ModelType.LOGISTIC_REGRESSION: "Logistic Regression",
    ModelType.NAIVE_BAYES: "Naïve Bayes",
}


def _metric_colour(value: float, green: float, amber: float) -> colors.Color:
    if value >= green:
        return SUCCESS
    if value >= amber:
        return WARNING
    return DANGER


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


class CertificateService:
    def generate_pdf(
        self,
        cert_request: CertificateRequest,
        metrics: MetricsResponse,
        ethics: EthicsResponse,
        specialty_name: str,
        model_type: ModelType,
    ) -> bytes:
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        h1 = ParagraphStyle(
            "H1", parent=styles["Heading1"],
            fontSize=22, textColor=PRIMARY, spaceAfter=4,
        )
        h2 = ParagraphStyle(
            "H2", parent=styles["Heading2"],
            fontSize=14, textColor=PRIMARY, spaceBefore=14, spaceAfter=4,
        )
        body = ParagraphStyle(
            "Body", parent=styles["Normal"],
            fontSize=10, textColor=DARK_TEXT, leading=14,
        )
        small = ParagraphStyle(
            "Small", parent=styles["Normal"],
            fontSize=8, textColor=colors.grey, leading=11,
        )
        caption = ParagraphStyle(
            "Caption", parent=styles["Normal"],
            fontSize=9, textColor=DARK_TEXT, alignment=1,
        )

        story = []

        # ---- HEADER ----
        story.append(Paragraph("ML Visualization Tool", h1))
        story.append(Paragraph("Learning Certificate", ParagraphStyle(
            "Sub", parent=styles["Normal"], fontSize=16,
            textColor=colors.HexColor("#5E6C84"), spaceAfter=2,
        )))
        story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
        story.append(Spacer(1, 0.3 * cm))

        issued_to = cert_request.clinician_name or "Healthcare Professional"
        institution = cert_request.institution or "Healthcare Institution"
        today = datetime.date.today().strftime("%d %B %Y")

        story.append(Paragraph(
            f"This certificate is issued to <b>{issued_to}</b> of <b>{institution}</b> "
            f"for completing the ML Visualization Tool educational exercise on {today}.",
            body,
        ))
        story.append(Spacer(1, 0.5 * cm))

        # ---- SECTION 1: Specialty & Model ----
        story.append(Paragraph("1. Clinical Specialty & AI Model", h2))
        info_data = [
            ["Medical Specialty", specialty_name],
            ["AI Model Type", MODEL_LABELS.get(model_type, str(model_type))],
            ["Model ID", cert_request.model_id[:16] + "…"],
        ]
        for k, v in (cert_request.checklist_state or {}).items():
            pass  # checklist processed below
        params_items = []
        info_table = Table(info_data, colWidths=[6 * cm, 11 * cm])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_GREY),
            ("TEXTCOLOR", (0, 0), (-1, -1), DARK_TEXT),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_GREY]),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
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

        metric_rows = [
            ["Metric", "Value", "Threshold", "Status"],
            ["Accuracy", _pct(metrics.accuracy), "≥ 65%",
             "✓ Acceptable" if metrics.accuracy >= 0.65 else "✗ Below threshold"],
            ["Sensitivity ★", _pct(metrics.sensitivity), "≥ 70%",
             "✓ Acceptable" if metrics.sensitivity >= 0.70 else "✗ Below threshold"],
            ["Specificity", _pct(metrics.specificity), "≥ 65%",
             "✓ Acceptable" if metrics.specificity >= 0.65 else "✗ Below threshold"],
            ["Precision", _pct(metrics.precision), "≥ 60%",
             "✓ Acceptable" if metrics.precision >= 0.60 else "✗ Below threshold"],
            ["F1 Score", _pct(metrics.f1_score), "≥ 65%",
             "✓ Acceptable" if metrics.f1_score >= 0.65 else "✗ Below threshold"],
            ["AUC-ROC", _pct(metrics.auc_roc), "≥ 75%",
             "✓ Acceptable" if metrics.auc_roc >= 0.75 else "✗ Below threshold"],
        ]

        def row_bg(val: float, green: float, amber: float) -> colors.Color:
            if val >= green:
                return colors.HexColor("#E3FCEF")
            if val >= amber:
                return colors.HexColor("#FFFAE6")
            return colors.HexColor("#FFEBE6")

        perf_table = Table(metric_rows, colWidths=[5 * cm, 3 * cm, 3.5 * cm, 5.5 * cm])
        metric_vals = [
            metrics.accuracy, metrics.sensitivity, metrics.specificity,
            metrics.precision, metrics.f1_score, metrics.auc_roc,
        ]
        green_thresh = [0.65, 0.70, 0.65, 0.60, 0.65, 0.75]
        amber_thresh = [0.55, 0.50, 0.55, 0.50, 0.55, 0.65]
        row_bgs = [colors.HexColor("#EBF2FA")]  # header
        for mv, gt, at in zip(metric_vals, green_thresh, amber_thresh):
            row_bgs.append(row_bg(mv, gt, at))

        ts = [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
        for i, bg in enumerate(row_bgs):
            ts.append(("BACKGROUND", (0, i), (-1, i), bg))
        perf_table.setStyle(TableStyle(ts))
        story.append(perf_table)
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("★ Sensitivity is the most critical metric for clinical screening tools.", small))
        story.append(Spacer(1, 0.4 * cm))

        # ---- SECTION 3: Bias Findings ----
        story.append(Paragraph("3. Bias & Fairness Findings", h2))
        if ethics.bias_warnings:
            for w in ethics.bias_warnings:
                story.append(Paragraph(f"⚠ {w.message}", ParagraphStyle(
                    "Warn", parent=body, textColor=DANGER,
                )))
        else:
            story.append(Paragraph("✓ No significant bias detected across patient subgroups.", ParagraphStyle(
                "OK", parent=body, textColor=SUCCESS,
            )))
        story.append(Spacer(1, 0.2 * cm))

        subgroup_data = [["Subgroup", "Sample n", "Accuracy", "Sensitivity", "Specificity", "Status"]]
        for sm in ethics.subgroup_metrics:
            status_sym = {"acceptable": "✓", "review": "⚠", "action_needed": "✗"}.get(sm.status, "?")
            subgroup_data.append([
                sm.group_label, str(sm.sample_size),
                _pct(sm.accuracy), _pct(sm.sensitivity), _pct(sm.specificity),
                f"{status_sym} {sm.status.replace('_', ' ').title()}",
            ])
        sg_table = Table(subgroup_data, colWidths=[3.5 * cm, 2 * cm, 2.5 * cm, 2.8 * cm, 2.8 * cm, 3.4 * cm])
        sg_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, MID_GREY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
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
                item["text"],
                "✓ Complete" if is_checked else "○ Pending",
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
        cl_table.setStyle(TableStyle(cl_ts))
        story.append(cl_table)
        story.append(Spacer(1, 0.5 * cm))

        # ---- FOOTER ----
        story.append(HRFlowable(width="100%", thickness=1, color=MID_GREY))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            f"Generated: {today}  ·  ML Visualization Tool v1.0  ·  Prepared by HealthWithSevgi Team",
            small,
        ))
        story.append(Paragraph(
            "<b>Important:</b> This certificate confirms completion of an educational exercise only. "
            "The AI model described herein is NOT validated for clinical use and must NOT be "
            "used to inform patient management decisions without appropriate clinical validation.",
            ParagraphStyle("Disclaimer", parent=small, textColor=DANGER),
        ))

        doc.build(story)
        return buf.getvalue()
