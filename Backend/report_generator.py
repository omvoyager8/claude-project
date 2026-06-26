import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

OUTPUT_DIR = "static/output"


def generate_report(filename, stats, image_path):

    report_path = os.path.join(OUTPUT_DIR, "anomaly_report.pdf")

    doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    title_style   = ParagraphStyle("title",    parent=styles["Title"],   fontSize=17, textColor=colors.HexColor("#003366"), spaceAfter=5,  alignment=TA_CENTER)
    subtitle_style = ParagraphStyle("subtitle", parent=styles["Normal"],  fontSize=10, textColor=colors.HexColor("#555555"), spaceAfter=4,  alignment=TA_CENTER)
    heading_style  = ParagraphStyle("heading",  parent=styles["Heading2"],fontSize=13, textColor=colors.HexColor("#003366"), spaceBefore=12, spaceAfter=6)
    normal_style   = ParagraphStyle("normal",   parent=styles["Normal"],  fontSize=10, spaceAfter=4)
    note_style     = ParagraphStyle("note",     parent=styles["Normal"],  fontSize=9,  textColor=colors.HexColor("#777777"), spaceAfter=4, alignment=TA_CENTER)

    elements = []

    # ── HEADER ──────────────────────────────────────────────────────────────
    elements.append(Paragraph("Anomaly Target Detection in Hyperspectral Images", title_style))
    elements.append(Paragraph("Department of Computer Engineering | Dr. D. Y. Patil COEI, Pune", subtitle_style))
    elements.append(Paragraph("Team: Kartik Ghule, Om Gonjari, Shankar Gawali, Mahesh Pawar  |  Guide: Dr. Suresh Mali", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#003366"), spaceAfter=10))

    # ── REPORT META ─────────────────────────────────────────────────────────
    elements.append(Paragraph("Detection Report", heading_style))
    meta_data = [
        ["File Analyzed",    filename],
        ["Report Generated", datetime.now().strftime("%Y-%m-%d  %H:%M:%S")],
        ["Image Dimensions", f"{stats['shape'][0]} × {stats['shape'][1]} pixels"],
        ["Spectral Bands",   str(stats["bands"])],
    ]
    meta_table = Table(meta_data, colWidths=[5*cm, 11*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, -1), colors.HexColor("#e8f0fe")),
        ("TEXTCOLOR",   (0, 0), (0, -1), colors.HexColor("#003366")),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("PADDING",     (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.4*cm))

    # ── ANOMALY STATISTICS ───────────────────────────────────────────────────
    elements.append(Paragraph("Anomaly Detection Statistics", heading_style))
    stats_data = [
        ["Metric",                  "Value"],
        ["Total Pixels",            f"{stats['total_pixels']:,}"],
        ["Anomaly Pixels Detected", f"{stats['anomaly_pixels']:,}"],
        ["Anomaly Coverage",        f"{stats['anomaly_percent']} %"],
        ["Anomaly Score Min",       str(stats["anomaly_min"])],
        ["Anomaly Score Max",       str(stats["anomaly_max"])],
        ["Anomaly Score Mean",      str(stats["anomaly_mean"])],
        ["Anomaly Score Std Dev",   str(stats["anomaly_std"])],
    ]
    stats_table = Table(stats_data, colWidths=[8*cm, 8*cm])
    stats_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("ALIGN",       (1, 0), (1, -1), "CENTER"),
        ("PADDING",     (0, 0), (-1, -1), 7),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 0.4*cm))

    # ── CLASSIFICATION METRICS (only if GT available) ────────────────────────
    if stats.get("roc_auc") is not None:
        elements.append(Paragraph("Classification Metrics", heading_style))
        cls_data = [
            ["Metric",    "Value"],
            ["AUC-ROC",   str(stats["roc_auc"])],
            ["Precision", str(stats["precision"])],
            ["Recall (TPR)", str(stats["recall"])],
            ["F1 Score",  str(stats["f1_score"])],
            ["True Positives",  str(stats["tp"])],
            ["False Positives", str(stats["fp"])],
            ["True Negatives",  str(stats["tn"])],
            ["False Negatives", str(stats["fn"])],
        ]
        cls_table = Table(cls_data, colWidths=[8*cm, 8*cm])
        cls_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1a3a5c")),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
            ("ALIGN",       (1, 0), (1, -1), "CENTER"),
            ("PADDING",     (0, 0), (-1, -1), 7),
        ]))
        elements.append(cls_table)
        elements.append(Spacer(1, 0.4*cm))

    # ── ANOMALY OUTPUT IMAGE ─────────────────────────────────────────────────
    elements.append(Paragraph("Anomaly Detection Output", heading_style))
    elements.append(Paragraph(
        "Detected anomaly regions overlaid on the hyperspectral RGB composite. "
        "Bright highlighted regions indicate detected anomalies.", normal_style))
    elements.append(Spacer(1, 0.3*cm))
    if os.path.exists(image_path):
        img = Image(image_path, width=12*cm, height=12*cm)
        img.hAlign = "CENTER"
        elements.append(img)
    elements.append(Spacer(1, 0.5*cm))

    # ── ROC CURVE + CONFUSION MATRIX ────────────────────────────────────────
    roc_path = stats.get("roc_path")
    cm_path  = stats.get("cm_path")

    if roc_path and cm_path and os.path.exists(roc_path) and os.path.exists(cm_path):
        elements.append(PageBreak())
        elements.append(Paragraph("ROC Curve & Confusion Matrix", heading_style))
        elements.append(Paragraph(
            "The ROC curve shows the trade-off between True Positive Rate and False Positive Rate "
            "across all thresholds. The confusion matrix is computed at the optimal threshold "
            "(Youden's J statistic).", normal_style))
        elements.append(Spacer(1, 0.4*cm))

        # side-by-side table
        roc_img = Image(roc_path, width=8.5*cm, height=7*cm)
        cm_img  = Image(cm_path,  width=7*cm,   height=6*cm)
        img_table = Table([[roc_img, cm_img]], colWidths=[9*cm, 8*cm])
        img_table.setStyle(TableStyle([
            ("ALIGN",   (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",  (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(img_table)
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(
            f"AUC = {stats['roc_auc']}  |  Threshold selected by Youden's J index", note_style))
        elements.append(Spacer(1, 0.5*cm))
    elif roc_path is None:
        elements.append(Paragraph(
            "Note: No ground truth map found in the uploaded file. "
            "ROC curve and confusion matrix require a 'map' key in the .mat file.", note_style))

    # ── METHODOLOGY ─────────────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=6))
    elements.append(Paragraph("Pipeline Methodology", heading_style))
    steps = [
        ("1. Preprocessing",  "Hyperspectral cube normalized and resampled to 200 spectral bands."),
        ("2. PCA + RF + SVM", "PCA reduces to 30 components. Random Forest and SVM produce probability/decision scores as ensemble features."),
        ("3. LRaSMD",         "Low Rank and Sparse Matrix Decomposition separates background (low-rank) from anomalies (sparse) via SVD."),
        ("4. Autoencoder",    "Deep autoencoder reconstructs background. Pixels with high reconstruction error are flagged as anomalies."),
    ]
    for step_title, step_desc in steps:
        elements.append(Paragraph(f"<b>{step_title}:</b> {step_desc}", normal_style))

    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=6))
    elements.append(Paragraph("© 2026 D.Y. Patil College of Engineering | Team MOkaSha", subtitle_style))

    doc.build(elements)
    return report_path