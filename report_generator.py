from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


def generate_profit_loss_pdf(db, filename="profit_loss_report.pdf"):
    """Génère un rapport PDF des profits et pertes"""

    # ===== جلب البيانات =====
    stats = db.get_statistics() or {}

    sales = float(stats.get("sales_total", 0))
    purchases = float(stats.get("purchases_total", 0))
    profit = sales - purchases
    growth = float(stats.get("growth_rate", 0))
    best_month = stats.get("best_month", "-")

    # ===== إنشاء ملف PDF =====
    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()
    elements = []

    # ===== العنوان =====
    title = Paragraph("Profit & Loss Report", styles["Title"])
    date = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"])

    elements.append(title)
    elements.append(Spacer(1, 20))
    elements.append(date)
    elements.append(Spacer(1, 30))

    # ===== جدول البيانات =====
    data = [
        ["Metric", "Value (DA)"],
        ["Total Sales", f"{sales:,.0f}"],
        ["Total Purchases", f"{purchases:,.0f}"],
        ["Net Profit", f"{profit:,.0f}"],
        ["Growth Rate %", f"{growth:.2f}%"],
        ["Best Month", best_month],
    ]

    table = Table(data, colWidths=[250, 150])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)

    # ===== بناء الملف =====
    doc.build(elements)

    return filename
