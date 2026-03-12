from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


def generate_profit_loss_pdf(db, filename=None, parent_widget=None):
    """
    Génère un rapport PDF des profits et pertes.

    Args:
        db             : instance Database
        filename       : chemin du fichier (optionnel — si None, ouvre un dialogue)
        parent_widget  : widget parent pour le QFileDialog (optionnel)

    Returns:
        Chemin du fichier généré, ou None si annulé.
    """

    # ── Demander le chemin si non fourni ──────────────────────────────────
    if filename is None:
        try:
            from PyQt6.QtWidgets import QFileDialog
            default_name = f"rapport_profits_pertes_{datetime.now().strftime('%Y%m%d')}.pdf"
            filename, _ = QFileDialog.getSaveFileName(
                parent_widget,
                "Enregistrer le rapport PDF",
                default_name,
                "Fichiers PDF (*.pdf)"
            )
            if not filename:          # L'utilisateur a annulé
                return None
            if not filename.endswith(".pdf"):
                filename += ".pdf"
        except ImportError:
            # Pas de PyQt6 disponible (ex: tests unitaires) → nom par défaut
            filename = f"rapport_profits_pertes_{datetime.now().strftime('%Y%m%d')}.pdf"

    # ── Récupérer les données ─────────────────────────────────────────────
    stats = db.get_statistics() or {}

    sales     = float(stats.get("sales_total",     0))
    purchases = float(stats.get("purchases_total", 0))
    profit    = sales - purchases
    growth    = float(stats.get("growth_rate",     0))
    best_month = stats.get("best_month", "-")

    # Noms des mois pour l'affichage
    MOIS = {
        "01": "Janvier",  "02": "Février",   "03": "Mars",
        "04": "Avril",    "05": "Mai",        "06": "Juin",
        "07": "Juillet",  "08": "Août",       "09": "Septembre",
        "10": "Octobre",  "11": "Novembre",   "12": "Décembre",
    }
    best_month_label = MOIS.get(str(best_month).zfill(2), str(best_month))

    # ── Créer le document PDF ─────────────────────────────────────────────
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = []

    # Titre
    title = Paragraph("📊 Rapport Profits & Pertes", styles["Title"])
    date_str = Paragraph(
        f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        styles["Normal"]
    )
    elements.append(title)
    elements.append(Spacer(1, 20))
    elements.append(date_str)
    elements.append(Spacer(1, 30))

    # Tableau de données
    profit_color = colors.green if profit >= 0 else colors.red

    data = [
        ["Indicateur",         "Valeur (DA)"],
        ["Total des Ventes",   f"{sales:,.0f}"],
        ["Total des Achats",   f"{purchases:,.0f}"],
        ["Bénéfice Net",       f"{profit:,.0f}"],
        ["Taux de Croissance", f"{growth:.2f} %"],
        ["Meilleur Mois",      best_month_label],
    ]

    table = Table(data, colWidths=[280, 180])
    table.setStyle(TableStyle([
        # En-tête
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("TOPPADDING",    (0, 0), (-1, 0), 12),
        # Corps
        ("BACKGROUND",    (0, 1), (-1, -1), colors.whitesmoke),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 11),
        ("TOPPADDING",    (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        # Ligne Bénéfice Net en couleur
        ("TEXTCOLOR",     (1, 3), (1, 3),  profit_color),
        ("FONTNAME",      (1, 3), (1, 3),  "Helvetica-Bold"),
        # Bordures
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # Note de bas de page
    note = Paragraph(
        "<i>Ce rapport a été généré automatiquement par ERP Pro.</i>",
        styles["Normal"]
    )
    elements.append(note)

    # ── Construire le fichier ─────────────────────────────────────────────
    doc.build(elements)
    print(f"✅ Rapport PDF généré : {filename}")
    return filename