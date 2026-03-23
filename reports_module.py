"""
Module de Rapports ERP — DAR ELSSALEM
======================================
Rapports : Ventes · Achats · Stock · Clients · Bénéfices · Tendances · Alertes
Fonctions : Export PDF · Export CSV · Filtre par période · Envoi email
"""

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDateEdit, QStackedWidget, QScrollArea, QMessageBox, QFileDialog,
    QSizePolicy, QProgressBar, QLineEdit, QTextEdit, QSpacerItem
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime, timedelta
import csv
import os

from styles import COLORS, INPUT_STYLE, BUTTON_STYLES
from db_manager import get_database
from currency import fmt_da, currency_manager


# ══════════════════════════════════════════════════════════════════════════
#  CONSTANTES & HELPERS
# ══════════════════════════════════════════════════════════════════════════

PERIODS = [
    ("Aujourd'hui",       "today"),
    ("Cette semaine",     "week"),
    ("Ce mois",           "month"),
    ("3 derniers mois",   "3months"),
    ("Cette année",       "year"),
    ("Tout",              "all"),
    ("Période perso…",    "custom"),
]

PAY_LABELS = {
    "cash": "💵 Espèces", "card": "💳 Carte", "check": "📝 Chèque",
    "transfer": "🏦 Virement", "mobile": "📱 Mobile", "credit": "🔄 Crédit",
}


def _lbl(text, size=11, bold=False, color=""):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", size,
                    QFont.Weight.Bold if bold else QFont.Weight.Normal))
    c = color or COLORS.get("TXT_PRI", "#F0F4FF")
    l.setStyleSheet(f"color:{c}; background:transparent; border:none;")
    return l


def _divider():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background:{COLORS.get('BORDER','rgba(255,255,255,0.1)')};"
                    "border:none; max-height:1px;")
    return f


def _action_btn(text, color, outlined=False):
    b = QPushButton(text)
    b.setFixedHeight(38)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
    if outlined:
        b.setStyleSheet(f"""
            QPushButton {{background:transparent; color:{color};
                border:1.5px solid {color}77; border-radius:9px; padding:0 16px;}}
            QPushButton:hover {{background:{color}18;}}
            QPushButton:pressed {{background:{color}33;}}
        """)
    else:
        b.setStyleSheet(f"""
            QPushButton {{background:{color}; color:white;
                border:none; border-radius:9px; padding:0 16px;}}
            QPushButton:hover {{background:{color}CC;}}
            QPushButton:pressed {{background:{color}99;}}
        """)
    return b


def _get_dates(period_key, start_qdate=None, end_qdate=None):
    """Retourne (start_str, end_str) selon la période choisie."""
    today = datetime.now().date()
    if period_key == "today":
        s = e = today
    elif period_key == "week":
        s = today - timedelta(days=today.weekday())
        e = today
    elif period_key == "month":
        s = today.replace(day=1)
        e = today
    elif period_key == "3months":
        s = today - timedelta(days=90)
        e = today
    elif period_key == "year":
        s = today.replace(month=1, day=1)
        e = today
    elif period_key == "custom" and start_qdate and end_qdate:
        s = start_qdate.toPyDate()
        e = end_qdate.toPyDate()
    else:  # "all"
        return None, None
    return str(s), str(e)


# ══════════════════════════════════════════════════════════════════════════
#  BASE REPORT PAGE
# ══════════════════════════════════════════════════════════════════════════

class BaseReportPage(QWidget):
    """Page de rapport générique : filtres, tableau, export."""

    TABLE_HEADERS: list = []
    REPORT_TITLE:  str  = "Rapport"
    REPORT_ICON:   str  = "📄"
    FILENAME_BASE: str  = "rapport"

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet("background:transparent;")
        self._build_ui()
        self.load_data()

    # ── Construction UI ────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(self._build_filters_bar())
        root.addWidget(self._build_kpi_row())
        root.addWidget(self._build_table_card())
        root.addLayout(self._build_actions_bar())

    def _build_filters_bar(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{COLORS.get('BG_CARD','#252535')};
                border-radius:12px;
                border:1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
            }}
        """)
        h = QHBoxLayout(card)
        h.setContentsMargins(16, 12, 16, 12)
        h.setSpacing(12)

        h.addWidget(_lbl("📅 Période :", 11, bold=True))

        self.period_combo = QComboBox()
        self.period_combo.setStyleSheet(INPUT_STYLE)
        self.period_combo.setMinimumHeight(36)
        self.period_combo.setFixedWidth(180)
        for label, key in PERIODS:
            self.period_combo.addItem(label, key)
        self.period_combo.setCurrentIndex(2)  # Ce mois par défaut
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        h.addWidget(self.period_combo)

        self.start_edit = QDateEdit()
        self.start_edit.setCalendarPopup(True)
        self.start_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_edit.setStyleSheet(INPUT_STYLE)
        self.start_edit.setMinimumHeight(36)
        self.start_edit.setVisible(False)
        h.addWidget(self.start_edit)

        lbl_au = _lbl("au", 10, color=COLORS.get("TXT_SEC","#A0AACC"))
        lbl_au.setVisible(False)
        self._lbl_au = lbl_au
        h.addWidget(lbl_au)

        self.end_edit = QDateEdit()
        self.end_edit.setCalendarPopup(True)
        self.end_edit.setDate(QDate.currentDate())
        self.end_edit.setStyleSheet(INPUT_STYLE)
        self.end_edit.setMinimumHeight(36)
        self.end_edit.setVisible(False)
        h.addWidget(self.end_edit)

        apply_btn = _action_btn("🔄 Actualiser", COLORS.get("primary","#3B82F6"), outlined=True)
        apply_btn.setFixedWidth(130)
        apply_btn.clicked.connect(self.load_data)
        h.addWidget(apply_btn)

        h.addStretch()

        # Badge résultat
        self.result_badge = QLabel("—")
        self.result_badge.setFont(QFont("Segoe UI", 10))
        self.result_badge.setStyleSheet(f"""
            color:{COLORS.get('primary','#3B82F6')};
            background:rgba(59,130,246,0.10);
            border:1px solid rgba(59,130,246,0.25);
            border-radius:6px; padding:4px 12px;
        """)
        h.addWidget(self.result_badge)
        return card

    def _build_kpi_row(self):
        self.kpi_frame = QFrame()
        self.kpi_frame.setStyleSheet("background:transparent; border:none;")
        self.kpi_layout = QHBoxLayout(self.kpi_frame)
        self.kpi_layout.setSpacing(12)
        self.kpi_layout.setContentsMargins(0, 0, 0, 0)
        return self.kpi_frame

    def _make_kpi_card(self, icon, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{COLORS.get('BG_CARD','#252535')};
                border-radius:12px;
                border:1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
                border-left:4px solid {color};
            }}
        """)
        card.setFixedHeight(85)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(6)
        ic = QLabel(icon)
        ic.setFont(QFont("Segoe UI", 14))
        ic.setStyleSheet(f"background:{color}22; border-radius:8px; border:none; padding:2px 6px;")
        top.addWidget(ic)
        tl = _lbl(title, 10, color=COLORS.get("TXT_SEC","#A0AACC"))
        top.addWidget(tl)
        top.addStretch()
        lay.addLayout(top)

        vl = QLabel(str(value))
        vl.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        vl.setStyleSheet(f"color:{color}; background:transparent; border:none;")
        lay.addWidget(vl)
        return card, vl

    def _build_table_card(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{COLORS.get('BG_CARD','#252535')};
                border-radius:12px;
                border:1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.table = QTableWidget(0, len(self.TABLE_HEADERS))
        self.table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background:{COLORS.get('BG_DEEP','#16161F')};
                alternate-background-color:rgba(255,255,255,0.025);
                color:{COLORS.get('TXT_PRI','#F0F4FF')};
                border:none; font-size:12px;
            }}
            QHeaderView::section {{
                background:{COLORS.get('BG_CARD','#252535')};
                color:{COLORS.get('primary','#3B82F6')};
                font-size:11px; font-weight:bold;
                padding:10px 8px; border:none;
                border-bottom:2px solid {COLORS.get('primary','#3B82F6')};
            }}
            QTableWidget::item {{ padding:8px 10px; border-bottom:1px solid rgba(255,255,255,0.04); }}
            QTableWidget::item:selected {{
                background:rgba(59,130,246,0.20); color:white;
            }}
        """)
        lay.addWidget(self.table)
        return card

    def _build_actions_bar(self):
        h = QHBoxLayout()
        h.setSpacing(10)

        self.btn_csv = _action_btn("📤 Exporter CSV", COLORS.get("success","#22C55E"), outlined=True)
        self.btn_csv.clicked.connect(self.export_csv)

        self.btn_pdf = _action_btn("🖨️ Exporter PDF", "#8B5CF6", outlined=True)
        self.btn_pdf.clicked.connect(self.export_pdf)

        self.btn_email = _action_btn("📧 Envoyer par email", COLORS.get("info","#38BDF8"), outlined=True)
        self.btn_email.clicked.connect(self.send_email)

        h.addWidget(self.btn_csv)
        h.addWidget(self.btn_pdf)
        h.addWidget(self.btn_email)
        h.addStretch()
        return h

    # ── Période ────────────────────────────────────────────────────────

    def _on_period_changed(self, idx):
        is_custom = (self.period_combo.currentData() == "custom")
        self.start_edit.setVisible(is_custom)
        self._lbl_au.setVisible(is_custom)
        self.end_edit.setVisible(is_custom)
        if not is_custom:
            self.load_data()

    def _current_dates(self):
        key = self.period_combo.currentData()
        return _get_dates(key, self.start_edit.date(), self.end_edit.date())

    # ── À surcharger ───────────────────────────────────────────────────

    def load_data(self):
        """Surcharger pour charger les données et remplir le tableau."""
        pass

    def get_headers(self):
        return self.TABLE_HEADERS

    def get_rows(self):
        """Retourne les lignes du tableau pour export."""
        rows = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text() if item else "")
            rows.append(row)
        return rows

    # ── Export CSV ─────────────────────────────────────────────────────

    def export_csv(self):
        rows = self.get_rows()
        if not rows:
            QMessageBox.information(self, "Vide", "Aucune donnée à exporter.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV",
            f"{self.FILENAME_BASE}_{ts}.csv",
            "CSV (*.csv);;Tous (*.*)"
        )
        if not fname:
            return
        try:
            with open(fname, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(self.get_headers())
                w.writerows(rows)
            QMessageBox.information(self, "✅ Exporté",
                f"{len(rows)} ligne(s) exportée(s).\n\n📁 {fname}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export :\n{e}")

    # ── Export PDF ─────────────────────────────────────────────────────

    def export_pdf(self):
        rows = self.get_rows()
        if not rows:
            QMessageBox.information(self, "Vide", "Aucune donnée à exporter.")
            return
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib import colors as rl_colors
            from reportlab.lib.units import cm
            from reportlab.platypus import (SimpleDocTemplate, Table,
                                             TableStyle, Paragraph, Spacer)
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            QMessageBox.warning(self, "Module manquant",
                "ReportLab est requis.\nInstallez-le avec : pip install reportlab")
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname, _ = QFileDialog.getSaveFileName(
            self, "Exporter en PDF",
            f"{self.FILENAME_BASE}_{ts}.pdf",
            "PDF (*.pdf);;Tous (*.*)"
        )
        if not fname:
            return

        try:
            doc = SimpleDocTemplate(fname, pagesize=landscape(A4),
                                    rightMargin=1.5*cm, leftMargin=1.5*cm,
                                    topMargin=2*cm, bottomMargin=1.5*cm)
            styles = getSampleStyleSheet()
            C_NAVY = rl_colors.HexColor("#1E3A5F")
            C_GOLD = rl_colors.HexColor("#C9A84C")

            elems = []
            # Titre
            title_style = ParagraphStyle("Title", parent=styles["Title"],
                                          fontSize=16, textColor=C_NAVY,
                                          spaceAfter=6)
            sub_style = ParagraphStyle("Sub", parent=styles["Normal"],
                                        fontSize=9, textColor=rl_colors.HexColor("#6B7280"),
                                        spaceAfter=12)
            elems.append(Paragraph(f"{self.REPORT_ICON}  {self.REPORT_TITLE}", title_style))

            db = get_database()
            company = db.get_setting("company_name", "DAR ELSSALEM")
            period_lbl = self.period_combo.currentText()
            now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
            elems.append(Paragraph(
                f"{company}  ·  Période : {period_lbl}  ·  Généré le {now_str}",
                sub_style))

            # Tableau
            header_row = self.get_headers()
            data = [header_row] + rows

            col_count = len(header_row)
            page_w = landscape(A4)[0] - 3*cm
            col_w = [page_w / col_count] * col_count

            tbl = Table(data, colWidths=col_w, repeatRows=1)
            n = len(data)
            row_bgs = [
                ("BACKGROUND", (0, i), (-1, i),
                 rl_colors.white if i % 2 == 1 else rl_colors.HexColor("#F5F7FA"))
                for i in range(1, n)
            ]
            tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), C_NAVY),
                ("TEXTCOLOR",     (0, 0), (-1, 0), rl_colors.white),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, 0), 9),
                ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
                ("TOPPADDING",    (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE",      (0, 1), (-1, -1), 8),
                ("TEXTCOLOR",     (0, 1), (-1, -1), rl_colors.HexColor("#1A1A2E")),
                ("TOPPADDING",    (0, 1), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
                ("ALIGN",         (0, 1), (-1, -1), "LEFT"),
                ("BOX",           (0, 0), (-1, -1), 1, rl_colors.HexColor("#D1D9E6")),
                ("LINEBELOW",     (0, 0), (-1, 0), 1.5, C_NAVY),
                ("INNERGRID",     (0, 0), (-1, -1), 0.3, rl_colors.HexColor("#D1D9E6")),
                *row_bgs,
            ]))
            elems.append(tbl)

            # Pied
            elems.append(Spacer(0, 0.5*cm))
            footer_style = ParagraphStyle("Footer", parent=styles["Normal"],
                                           fontSize=8, textColor=rl_colors.HexColor("#9CA3AF"),
                                           alignment=TA_CENTER)
            elems.append(Paragraph(
                f"{company}  —  {self.REPORT_TITLE}  —  {now_str}",
                footer_style))

            doc.build(elems)
            QMessageBox.information(self, "✅ PDF généré",
                f"Rapport PDF créé avec succès.\n\n📄 {fname}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur PDF", f"Impossible de générer le PDF :\n{e}")

    # ── Envoi Email ────────────────────────────────────────────────────

    def send_email(self):
        """Génère le PDF puis envoie par email."""
        db = get_database()
        sender_email = db.get_setting("email_sender", "")
        sender_pwd   = db.get_setting("email_password", "")
        smtp_server  = db.get_setting("email_smtp_server", "smtp.gmail.com")
        smtp_port    = int(db.get_setting("email_smtp_port", "587") or 587)

        if not sender_email or not sender_pwd:
            QMessageBox.warning(self, "Email non configuré",
                "Veuillez d'abord configurer l'envoi d'emails dans :\n"
                "Menu ERP Tools → ⚙️ Configurer l'envoi d'emails")
            return

        dlg = SendEmailDialog(
            report_title=self.REPORT_TITLE,
            sender_email=sender_email,
            sender_pwd=sender_pwd,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            page=self,
            parent=self,
        )
        dlg.exec()


# ══════════════════════════════════════════════════════════════════════════
#  1. RAPPORT DES VENTES
# ══════════════════════════════════════════════════════════════════════════

class SalesReportPage(BaseReportPage):
    TABLE_HEADERS = ["N° Facture", "Date", "Client", "Sous-total HT",
                     "TVA", "Total TTC", "Paiement", "Statut"]
    REPORT_TITLE  = "Rapport des Ventes"
    REPORT_ICON   = "📊"
    FILENAME_BASE = "rapport_ventes"

    def _build_kpi_row(self):
        frame = super()._build_kpi_row()
        sym = currency_manager.primary.symbol
        self._kpi_vals = {}
        data = [
            ("💰", "Chiffre d'affaires", f"0 {sym}", COLORS.get("primary","#3B82F6")),
            ("🧾", "Nombre de ventes",   "0",          COLORS.get("success","#22C55E")),
            ("📋", "Panier moyen",        f"0 {sym}",  COLORS.get("warning","#FBBF24")),
            ("💳", "TVA collectée",       f"0 {sym}",  COLORS.get("secondary","#A855F7")),
        ]
        for icon, title, val, color in data:
            card, val_lbl = self._make_kpi_card(icon, title, val, color)
            self.kpi_layout.addWidget(card)
            self._kpi_vals[title] = val_lbl
        return frame

    def load_data(self):
        s, e = self._current_dates()
        try:
            if s and e:
                self.db.cursor.execute("""
                    SELECT s.invoice_number, s.sale_date,
                           COALESCE(c.name,'Client Anonyme') as client_name,
                           s.subtotal, s.tax_amount, s.total,
                           s.payment_method, COALESCE(s.payment_status,'paid')
                    FROM sales s
                    LEFT JOIN clients c ON s.client_id = c.id
                    WHERE DATE(s.sale_date) BETWEEN ? AND ?
                    ORDER BY s.sale_date DESC
                """, (s, e))
            else:
                self.db.cursor.execute("""
                    SELECT s.invoice_number, s.sale_date,
                           COALESCE(c.name,'Client Anonyme') as client_name,
                           s.subtotal, s.tax_amount, s.total,
                           s.payment_method, COALESCE(s.payment_status,'paid')
                    FROM sales s
                    LEFT JOIN clients c ON s.client_id = c.id
                    ORDER BY s.sale_date DESC
                """)
            rows = self.db.cursor.fetchall()
        except Exception:
            rows = []

        self.table.setRowCount(0)
        total_ca = total_tva = 0.0
        STATUS_COLOR = {"paid": "#22C55E", "pending": "#FBBF24", "cancelled": "#EF4444"}
        STATUS_LABEL = {"paid": "✅ Payée", "pending": "⏳ En attente", "cancelled": "❌ Annulée"}

        for row in rows:
            inv, date, client, sub, tva, total, pay, status = row
            total_ca  += float(total or 0)
            total_tva += float(tva or 0)
            date_str = str(date).split(" ")[0] if date else "—"
            pay_str  = PAY_LABELS.get(pay, pay or "—")
            status_c = STATUS_COLOR.get(status, "#A0AACC")
            status_l = STATUS_LABEL.get(status, status or "—")

            r = self.table.rowCount()
            self.table.insertRow(r)
            cells = [
                (str(inv or "—"),           "#F0F4FF"),
                (date_str,                   "#A0AACC"),
                (str(client),                "#F0F4FF"),
                (fmt_da(float(sub or 0)),   "#F0F4FF"),
                (fmt_da(float(tva or 0)),   "#FBBF24"),
                (fmt_da(float(total or 0)), "#22C55E"),
                (pay_str,                    "#A0AACC"),
                (status_l,                   status_c),
            ]
            for col, (val, color) in enumerate(cells):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(color))
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(r, col, it)
            self.table.setRowHeight(r, 36)

        nb = len(rows)
        avg = (total_ca / nb) if nb else 0
        sym = currency_manager.primary.symbol
        self._kpi_vals["Chiffre d'affaires"].setText(fmt_da(total_ca))
        self._kpi_vals["Nombre de ventes"].setText(str(nb))
        self._kpi_vals["Panier moyen"].setText(fmt_da(avg))
        self._kpi_vals["TVA collectée"].setText(fmt_da(total_tva))
        self.result_badge.setText(f"{nb} vente(s) trouvée(s)")


# ══════════════════════════════════════════════════════════════════════════
#  2. RAPPORT DES ACHATS
# ══════════════════════════════════════════════════════════════════════════

class PurchasesReportPage(BaseReportPage):
    TABLE_HEADERS = ["Référence", "Date", "Fournisseur", "Produit",
                     "Qté", "Prix Unit.", "Total HT", "TVA", "Total TTC"]
    REPORT_TITLE  = "Rapport des Achats"
    REPORT_ICON   = "🛒"
    FILENAME_BASE = "rapport_achats"

    def _build_kpi_row(self):
        frame = super()._build_kpi_row()
        self._kpi_vals = {}
        data = [
            ("🛒", "Total achats",       "0", COLORS.get("danger","#F87171")),
            ("📦", "Articles achetés",   "0", COLORS.get("warning","#FBBF24")),
            ("🏢", "Fournisseurs actifs","0", COLORS.get("info","#38BDF8")),
            ("💸", "TVA payée",          "0", COLORS.get("secondary","#A855F7")),
        ]
        for icon, title, val, color in data:
            card, vl = self._make_kpi_card(icon, title, val, color)
            self.kpi_layout.addWidget(card)
            self._kpi_vals[title] = vl
        return frame

    def load_data(self):
        s, e = self._current_dates()
        try:
            if s and e:
                self.db.cursor.execute("""
                    SELECT p.reference, p.purchase_date,
                           COALESCE(sup.name,'—') as supplier,
                           COALESCE(pr.name,'—') as product_name,
                           pi.quantity, pi.unit_price,
                           pi.quantity * pi.unit_price as subtotal,
                           p.tax_amount, p.total
                    FROM purchases p
                    LEFT JOIN suppliers sup ON p.supplier_id = sup.id
                    LEFT JOIN purchase_items pi ON pi.purchase_id = p.id
                    LEFT JOIN products pr ON pi.product_id = pr.id
                    WHERE DATE(p.purchase_date) BETWEEN ? AND ?
                    ORDER BY p.purchase_date DESC
                """, (s, e))
            else:
                self.db.cursor.execute("""
                    SELECT p.reference, p.purchase_date,
                           COALESCE(sup.name,'—') as supplier,
                           COALESCE(pr.name,'—') as product_name,
                           pi.quantity, pi.unit_price,
                           pi.quantity * pi.unit_price as subtotal,
                           p.tax_amount, p.total
                    FROM purchases p
                    LEFT JOIN suppliers sup ON p.supplier_id = sup.id
                    LEFT JOIN purchase_items pi ON pi.purchase_id = p.id
                    LEFT JOIN products pr ON pi.product_id = pr.id
                    ORDER BY p.purchase_date DESC
                """)
            rows = self.db.cursor.fetchall()
        except Exception:
            rows = []

        self.table.setRowCount(0)
        total_ach = total_tva = 0.0
        suppliers_seen = set()

        for row in rows:
            ref, date, sup, prod, qty, price, sub, tva, total = row
            total_ach += float(total or 0)
            total_tva += float(tva or 0)
            if sup: suppliers_seen.add(sup)
            date_str = str(date).split(" ")[0] if date else "—"

            r = self.table.rowCount()
            self.table.insertRow(r)
            cells = [
                (str(ref or "—"),              "#F0F4FF"),
                (date_str,                      "#A0AACC"),
                (str(sup),                      "#F0F4FF"),
                (str(prod),                     "#F0F4FF"),
                (str(int(qty or 0)),            "#38BDF8"),
                (fmt_da(float(price or 0)),    "#F0F4FF"),
                (fmt_da(float(sub or 0)),      "#F0F4FF"),
                (fmt_da(float(tva or 0)),      "#FBBF24"),
                (fmt_da(float(total or 0)),    "#F87171"),
            ]
            for col, (val, color) in enumerate(cells):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(color))
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(r, col, it)
            self.table.setRowHeight(r, 36)

        nb = self.table.rowCount()
        self._kpi_vals["Total achats"].setText(fmt_da(total_ach))
        self._kpi_vals["Articles achetés"].setText(str(nb))
        self._kpi_vals["Fournisseurs actifs"].setText(str(len(suppliers_seen)))
        self._kpi_vals["TVA payée"].setText(fmt_da(total_tva))
        self.result_badge.setText(f"{nb} ligne(s)")


# ══════════════════════════════════════════════════════════════════════════
#  3. RAPPORT STOCK & INVENTAIRE
# ══════════════════════════════════════════════════════════════════════════

class StockReportPage(BaseReportPage):
    TABLE_HEADERS = ["Produit", "Catégorie", "Stock", "Stock min",
                     "Statut", "Prix achat", "Prix vente", "Valeur stock"]
    REPORT_TITLE  = "Rapport Stock & Inventaire"
    REPORT_ICON   = "📦"
    FILENAME_BASE = "rapport_stock"

    def _build_filters_bar(self):
        """Pas de filtre date pour le stock — filtre par statut."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{COLORS.get('BG_CARD','#252535')};
                border-radius:12px;
                border:1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
            }}
        """)
        h = QHBoxLayout(card)
        h.setContentsMargins(16, 12, 16, 12)
        h.setSpacing(12)

        h.addWidget(_lbl("📦 Filtre :", 11, bold=True))

        self.stock_filter = QComboBox()
        self.stock_filter.setStyleSheet(INPUT_STYLE)
        self.stock_filter.setMinimumHeight(36)
        self.stock_filter.setFixedWidth(200)
        self.stock_filter.addItems([
            "Tous les produits",
            "Stock faible uniquement",
            "Rupture de stock (0)",
            "Stock normal",
        ])
        self.stock_filter.currentIndexChanged.connect(self.load_data)
        h.addWidget(self.stock_filter)

        apply_btn = _action_btn("🔄 Actualiser", COLORS.get("primary","#3B82F6"), outlined=True)
        apply_btn.setFixedWidth(130)
        apply_btn.clicked.connect(self.load_data)
        h.addWidget(apply_btn)

        h.addStretch()
        self.result_badge = QLabel("—")
        self.result_badge.setFont(QFont("Segoe UI", 10))
        self.result_badge.setStyleSheet(f"""
            color:{COLORS.get('primary','#3B82F6')};
            background:rgba(59,130,246,0.10);
            border:1px solid rgba(59,130,246,0.25);
            border-radius:6px; padding:4px 12px;
        """)
        h.addWidget(self.result_badge)

        # Stub pour compatibilité
        self.period_combo = QComboBox()
        self.start_edit   = QDateEdit()
        self.end_edit     = QDateEdit()
        self._lbl_au      = QLabel()
        return card

    def _current_dates(self):
        return None, None

    def _build_kpi_row(self):
        frame = super()._build_kpi_row()
        self._kpi_vals = {}
        data = [
            ("📦", "Total produits",     "0", COLORS.get("primary","#3B82F6")),
            ("💰", "Valeur du stock",    "0", COLORS.get("success","#22C55E")),
            ("⚠️", "Stock faible",       "0", COLORS.get("warning","#FBBF24")),
            ("🔴", "Rupture de stock",   "0", COLORS.get("danger","#F87171")),
        ]
        for icon, title, val, color in data:
            card, vl = self._make_kpi_card(icon, title, val, color)
            self.kpi_layout.addWidget(card)
            self._kpi_vals[title] = vl
        return frame

    def load_data(self):
        filt = self.stock_filter.currentIndex()
        try:
            self.db.cursor.execute("""
                SELECT p.name, COALESCE(c.name,'—') as cat,
                       p.stock_quantity, p.min_stock,
                       p.purchase_price, p.selling_price
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.stock_quantity ASC
            """)
            rows = self.db.cursor.fetchall()
        except Exception:
            rows = []

        self.table.setRowCount(0)
        total_val = low = rupture = 0

        for row in rows:
            name, cat, stock, mini, p_buy, p_sell = row
            stock = int(stock or 0)
            mini  = int(mini or 0)
            p_buy  = float(p_buy or 0)
            p_sell = float(p_sell or 0)
            val    = stock * p_sell

            is_rupture = (stock == 0)
            is_low     = (0 < stock <= mini)
            is_normal  = (stock > mini)

            if filt == 1 and not is_low:     continue
            if filt == 2 and not is_rupture: continue
            if filt == 3 and not is_normal:  continue

            total_val += val
            if is_rupture: rupture += 1
            elif is_low:   low += 1

            if is_rupture:
                status, s_color = "🔴 Rupture", "#EF4444"
            elif is_low:
                status, s_color = "🟡 Faible",  "#FBBF24"
            else:
                status, s_color = "🟢 Normal",  "#22C55E"

            r = self.table.rowCount()
            self.table.insertRow(r)
            cells = [
                (str(name),       "#F0F4FF"),
                (str(cat),        "#A0AACC"),
                (str(stock),      s_color),
                (str(mini),       "#A0AACC"),
                (status,          s_color),
                (fmt_da(p_buy),  "#A0AACC"),
                (fmt_da(p_sell), "#F0F4FF"),
                (fmt_da(val),    "#22C55E"),
            ]
            for col, (val_txt, color) in enumerate(cells):
                it = QTableWidgetItem(val_txt)
                it.setForeground(QColor(color))
                it.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter |
                    (Qt.AlignmentFlag.AlignRight if col >= 5 else Qt.AlignmentFlag.AlignLeft))
                self.table.setItem(r, col, it)
            self.table.setRowHeight(r, 36)

        nb = self.table.rowCount()
        self._kpi_vals["Total produits"].setText(str(len(rows)))
        self._kpi_vals["Valeur du stock"].setText(fmt_da(total_val))
        self._kpi_vals["Stock faible"].setText(str(low))
        self._kpi_vals["Rupture de stock"].setText(str(rupture))
        self.result_badge.setText(f"{nb} produit(s)")


# ══════════════════════════════════════════════════════════════════════════
#  4. RAPPORT CLIENTS
# ══════════════════════════════════════════════════════════════════════════

class ClientsReportPage(BaseReportPage):
    TABLE_HEADERS = ["#", "Client", "Téléphone", "Email",
                     "Nb ventes", "CA Total", "Panier moyen", "Dernière visite"]
    REPORT_TITLE  = "Rapport Clients"
    REPORT_ICON   = "👥"
    FILENAME_BASE = "rapport_clients"

    def _build_kpi_row(self):
        frame = super()._build_kpi_row()
        self._kpi_vals = {}
        data = [
            ("👥", "Total clients",     "0", COLORS.get("primary","#3B82F6")),
            ("🏆", "Meilleur client",   "—", COLORS.get("warning","#FBBF24")),
            ("💰", "CA moyen/client",   "0", COLORS.get("success","#22C55E")),
            ("📈", "Clients actifs",    "0", COLORS.get("info","#38BDF8")),
        ]
        for icon, title, val, color in data:
            card, vl = self._make_kpi_card(icon, title, val, color)
            self.kpi_layout.addWidget(card)
            self._kpi_vals[title] = vl
        return frame

    def load_data(self):
        s, e = self._current_dates()
        try:
            if s and e:
                self.db.cursor.execute("""
                    SELECT c.id, c.name, COALESCE(c.phone,'—'), COALESCE(c.email,'—'),
                           COUNT(s.id) as nb,
                           COALESCE(SUM(s.total),0) as ca,
                           COALESCE(AVG(s.total),0) as avg,
                           MAX(s.sale_date) as last_visit
                    FROM clients c
                    LEFT JOIN sales s ON s.client_id = c.id
                        AND DATE(s.sale_date) BETWEEN ? AND ?
                    GROUP BY c.id
                    ORDER BY ca DESC
                """, (s, e))
            else:
                self.db.cursor.execute("""
                    SELECT c.id, c.name, COALESCE(c.phone,'—'), COALESCE(c.email,'—'),
                           COUNT(s.id) as nb,
                           COALESCE(SUM(s.total),0) as ca,
                           COALESCE(AVG(s.total),0) as avg,
                           MAX(s.sale_date) as last_visit
                    FROM clients c
                    LEFT JOIN sales s ON s.client_id = c.id
                    GROUP BY c.id
                    ORDER BY ca DESC
                """)
            rows = self.db.cursor.fetchall()
        except Exception:
            rows = []

        self.table.setRowCount(0)
        total_ca = sum(float(r[5] or 0) for r in rows)
        best     = rows[0][1] if rows else "—"
        active   = sum(1 for r in rows if int(r[4] or 0) > 0)

        for rank, row in enumerate(rows, 1):
            cid, name, phone, email, nb, ca, avg, last = row
            nb   = int(nb or 0)
            ca   = float(ca or 0)
            avg  = float(avg or 0)
            last_str = str(last).split(" ")[0] if last else "Jamais"
            medal = ["🥇","🥈","🥉"][rank-1] if rank <= 3 else f"#{rank}"

            r = self.table.rowCount()
            self.table.insertRow(r)
            cells = [
                (medal,            "#FBBF24" if rank <= 3 else "#A0AACC"),
                (str(name),        "#F0F4FF"),
                (str(phone),       "#A0AACC"),
                (str(email),       "#A0AACC"),
                (str(nb),          "#38BDF8"),
                (fmt_da(ca),      "#22C55E"),
                (fmt_da(avg),     "#F0F4FF"),
                (last_str,         "#A0AACC"),
            ]
            for col, (val, color) in enumerate(cells):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(color))
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(r, col, it)
            self.table.setRowHeight(r, 36)

        nb_clients = len(rows)
        ca_moy = (total_ca / nb_clients) if nb_clients else 0
        self._kpi_vals["Total clients"].setText(str(nb_clients))
        self._kpi_vals["Meilleur client"].setText(str(best)[:20])
        self._kpi_vals["CA moyen/client"].setText(fmt_da(ca_moy))
        self._kpi_vals["Clients actifs"].setText(str(active))
        self.result_badge.setText(f"{nb_clients} client(s)")


# ══════════════════════════════════════════════════════════════════════════
#  5. RAPPORT BÉNÉFICES & MARGES
# ══════════════════════════════════════════════════════════════════════════

class ProfitReportPage(BaseReportPage):
    TABLE_HEADERS = ["Produit", "Qté vendue", "CA HT",
                     "Coût achat", "Bénéfice brut", "Marge %"]
    REPORT_TITLE  = "Rapport Bénéfices & Marges"
    REPORT_ICON   = "💰"
    FILENAME_BASE = "rapport_benefices"

    def _build_kpi_row(self):
        frame = super()._build_kpi_row()
        self._kpi_vals = {}
        data = [
            ("💰", "CA Total HT",       "0", COLORS.get("primary","#3B82F6")),
            ("🛒", "Coût des achats",   "0", COLORS.get("danger","#F87171")),
            ("📈", "Bénéfice brut",     "0", COLORS.get("success","#22C55E")),
            ("🎯", "Marge moyenne",     "0%", COLORS.get("warning","#FBBF24")),
        ]
        for icon, title, val, color in data:
            card, vl = self._make_kpi_card(icon, title, val, color)
            self.kpi_layout.addWidget(card)
            self._kpi_vals[title] = vl
        return frame

    def load_data(self):
        s, e = self._current_dates()
        try:
            if s and e:
                self.db.cursor.execute("""
                    SELECT p.name,
                           SUM(si.quantity) as qty,
                           SUM(si.quantity * si.unit_price * (1 - COALESCE(si.discount,0)/100.0)) as ca_ht,
                           SUM(si.quantity * COALESCE(p.purchase_price,0)) as cost,
                           SUM(si.quantity * si.unit_price * (1 - COALESCE(si.discount,0)/100.0))
                             - SUM(si.quantity * COALESCE(p.purchase_price,0)) as profit
                    FROM sale_items si
                    JOIN sales s ON si.sale_id = s.id
                    JOIN products p ON si.product_id = p.id
                    WHERE DATE(s.sale_date) BETWEEN ? AND ?
                    GROUP BY si.product_id
                    ORDER BY profit DESC
                """, (s, e))
            else:
                self.db.cursor.execute("""
                    SELECT p.name,
                           SUM(si.quantity) as qty,
                           SUM(si.quantity * si.unit_price * (1 - COALESCE(si.discount,0)/100.0)) as ca_ht,
                           SUM(si.quantity * COALESCE(p.purchase_price,0)) as cost,
                           SUM(si.quantity * si.unit_price * (1 - COALESCE(si.discount,0)/100.0))
                             - SUM(si.quantity * COALESCE(p.purchase_price,0)) as profit
                    FROM sale_items si
                    JOIN sales s ON si.sale_id = s.id
                    JOIN products p ON si.product_id = p.id
                    GROUP BY si.product_id
                    ORDER BY profit DESC
                """)
            rows = self.db.cursor.fetchall()
        except Exception:
            rows = []

        self.table.setRowCount(0)
        total_ca = total_cost = total_profit = 0.0

        for row in rows:
            name, qty, ca, cost, profit = row
            qty    = int(qty or 0)
            ca     = float(ca or 0)
            cost   = float(cost or 0)
            profit = float(profit or 0)
            marge  = (profit / ca * 100) if ca else 0

            total_ca     += ca
            total_cost   += cost
            total_profit += profit

            profit_color = "#22C55E" if profit >= 0 else "#EF4444"
            marge_color  = "#22C55E" if marge >= 20 else ("#FBBF24" if marge >= 0 else "#EF4444")

            r = self.table.rowCount()
            self.table.insertRow(r)
            cells = [
                (str(name),        "#F0F4FF"),
                (str(qty),         "#38BDF8"),
                (fmt_da(ca),      "#F0F4FF"),
                (fmt_da(cost),    "#F87171"),
                (fmt_da(profit),  profit_color),
                (f"{marge:.1f}%", marge_color),
            ]
            for col, (val, color) in enumerate(cells):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(color))
                it.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter |
                    (Qt.AlignmentFlag.AlignRight if col >= 1 else Qt.AlignmentFlag.AlignLeft))
                self.table.setItem(r, col, it)
            self.table.setRowHeight(r, 36)

        moy_marge = (total_profit / total_ca * 100) if total_ca else 0
        self._kpi_vals["CA Total HT"].setText(fmt_da(total_ca))
        self._kpi_vals["Coût des achats"].setText(fmt_da(total_cost))
        self._kpi_vals["Bénéfice brut"].setText(fmt_da(total_profit))
        self._kpi_vals["Marge moyenne"].setText(f"{moy_marge:.1f}%")
        self.result_badge.setText(f"{self.table.rowCount()} produit(s)")


# ══════════════════════════════════════════════════════════════════════════
#  6. RAPPORT TENDANCES & ÉVOLUTION
# ══════════════════════════════════════════════════════════════════════════

class TrendsReportPage(BaseReportPage):
    TABLE_HEADERS = ["Période", "Nb ventes", "CA Total",
                     "Nb achats", "Total achats", "Bénéfice net", "Évolution CA"]
    REPORT_TITLE  = "Rapport Tendances & Évolution"
    REPORT_ICON   = "📈"
    FILENAME_BASE = "rapport_tendances"

    def _build_filters_bar(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{COLORS.get('BG_CARD','#252535')};
                border-radius:12px;
                border:1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
            }}
        """)
        h = QHBoxLayout(card)
        h.setContentsMargins(16, 12, 16, 12)
        h.setSpacing(12)

        h.addWidget(_lbl("📅 Grouper par :", 11, bold=True))

        self.group_combo = QComboBox()
        self.group_combo.setStyleSheet(INPUT_STYLE)
        self.group_combo.setMinimumHeight(36)
        self.group_combo.setFixedWidth(160)
        self.group_combo.addItems(["Jour", "Semaine", "Mois", "Année"])
        self.group_combo.setCurrentIndex(2)
        self.group_combo.currentIndexChanged.connect(self.load_data)
        h.addWidget(self.group_combo)

        h.addWidget(_lbl("Période :", 11, bold=True))
        self.period_combo = QComboBox()
        self.period_combo.setStyleSheet(INPUT_STYLE)
        self.period_combo.setMinimumHeight(36)
        self.period_combo.setFixedWidth(180)
        for label, key in PERIODS[:-1]:  # Sans "Perso"
            self.period_combo.addItem(label, key)
        self.period_combo.setCurrentIndex(4)  # Cette année
        self.period_combo.currentIndexChanged.connect(self.load_data)
        h.addWidget(self.period_combo)

        apply_btn = _action_btn("🔄 Actualiser", COLORS.get("primary","#3B82F6"), outlined=True)
        apply_btn.setFixedWidth(130)
        apply_btn.clicked.connect(self.load_data)
        h.addWidget(apply_btn)
        h.addStretch()

        self.result_badge = QLabel("—")
        self.result_badge.setFont(QFont("Segoe UI", 10))
        self.result_badge.setStyleSheet(f"""
            color:{COLORS.get('primary','#3B82F6')};
            background:rgba(59,130,246,0.10);
            border:1px solid rgba(59,130,246,0.25);
            border-radius:6px; padding:4px 12px;
        """)
        h.addWidget(self.result_badge)

        # Stubs
        self.start_edit = QDateEdit()
        self.end_edit   = QDateEdit()
        self._lbl_au    = QLabel()
        return card

    def _current_dates(self):
        key = self.period_combo.currentData()
        return _get_dates(key)

    def _build_kpi_row(self):
        frame = super()._build_kpi_row()
        self._kpi_vals = {}
        data = [
            ("📊", "Meilleures ventes",  "—",  COLORS.get("primary","#3B82F6")),
            ("📈", "Croissance CA",      "0%",  COLORS.get("success","#22C55E")),
            ("🏆", "Meilleure période",  "—",  COLORS.get("warning","#FBBF24")),
            ("💰", "Bénéfice total",     "0",  COLORS.get("secondary","#A855F7")),
        ]
        for icon, title, val, color in data:
            card, vl = self._make_kpi_card(icon, title, val, color)
            self.kpi_layout.addWidget(card)
            self._kpi_vals[title] = vl
        return frame

    def load_data(self):
        s, e = self._current_dates()
        grp  = self.group_combo.currentIndex()  # 0=jour 1=sem 2=mois 3=an

        fmt_map = {0: "%Y-%m-%d", 1: "%Y-W%W", 2: "%Y-%m", 3: "%Y"}
        sql_fmt  = {0: "%Y-%m-%d", 1: "%Y-%W",  2: "%Y-%m", 3: "%Y"}
        fmt_str  = sql_fmt[grp]

        date_filter = ""
        params_s: list = []
        params_p: list = []
        if s and e:
            date_filter = "WHERE DATE(sale_date) BETWEEN ? AND ?"
            params_s    = [s, e]
            date_filter_p = "WHERE DATE(purchase_date) BETWEEN ? AND ?"
            params_p    = [s, e]
        else:
            date_filter_p = ""

        try:
            self.db.cursor.execute(f"""
                SELECT strftime('{fmt_str}', sale_date) as period,
                       COUNT(*) as nb, SUM(total) as ca
                FROM sales {date_filter}
                GROUP BY period ORDER BY period
            """, params_s)
            sales_rows = {r[0]: (int(r[1]), float(r[2] or 0))
                          for r in self.db.cursor.fetchall()}
        except Exception:
            sales_rows = {}

        try:
            self.db.cursor.execute(f"""
                SELECT strftime('{fmt_str}', purchase_date) as period,
                       COUNT(*) as nb, SUM(total) as total
                FROM purchases {date_filter_p if s else ''}
                GROUP BY period ORDER BY period
            """, params_p if s else [])
            pur_rows = {r[0]: (int(r[1]), float(r[2] or 0))
                        for r in self.db.cursor.fetchall()}
        except Exception:
            pur_rows = {}

        all_periods = sorted(set(list(sales_rows.keys()) + list(pur_rows.keys())))

        self.table.setRowCount(0)
        prev_ca = None
        best_period = ("—", 0)
        total_profit = 0.0
        all_cas = []

        for period in all_periods:
            nb_s, ca = sales_rows.get(period, (0, 0.0))
            nb_p, pa = pur_rows.get(period, (0, 0.0))
            profit   = ca - pa
            total_profit += profit

            if ca > best_period[1]:
                best_period = (period, ca)
            all_cas.append(ca)

            if prev_ca is not None and prev_ca > 0:
                evol = ((ca - prev_ca) / prev_ca) * 100
                evol_str  = f"+{evol:.1f}%" if evol >= 0 else f"{evol:.1f}%"
                evol_color = "#22C55E" if evol >= 0 else "#EF4444"
            else:
                evol_str, evol_color = "—", "#A0AACC"
            prev_ca = ca

            profit_color = "#22C55E" if profit >= 0 else "#EF4444"

            r = self.table.rowCount()
            self.table.insertRow(r)
            cells = [
                (str(period),      "#F0F4FF"),
                (str(nb_s),        "#38BDF8"),
                (fmt_da(ca),      "#F0F4FF"),
                (str(nb_p),        "#F87171"),
                (fmt_da(pa),      "#F87171"),
                (fmt_da(profit),  profit_color),
                (evol_str,         evol_color),
            ]
            for col, (val, color) in enumerate(cells):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(color))
                it.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter |
                    (Qt.AlignmentFlag.AlignRight if col >= 2 else Qt.AlignmentFlag.AlignLeft))
                self.table.setItem(r, col, it)
            self.table.setRowHeight(r, 36)

        # KPIs
        if len(all_cas) >= 2 and all_cas[0] > 0:
            global_evol = ((all_cas[-1] - all_cas[0]) / all_cas[0]) * 100
            evol_txt = f"+{global_evol:.1f}%" if global_evol >= 0 else f"{global_evol:.1f}%"
        else:
            evol_txt = "—"

        self._kpi_vals["Meilleures ventes"].setText(
            f"{max(all_cas, default=0):,.0f}" if all_cas else "—")
        self._kpi_vals["Croissance CA"].setText(evol_txt)
        self._kpi_vals["Meilleure période"].setText(str(best_period[0]))
        self._kpi_vals["Bénéfice total"].setText(fmt_da(total_profit))
        self.result_badge.setText(f"{len(all_periods)} période(s)")


# ══════════════════════════════════════════════════════════════════════════
#  7. ALERTES AUTOMATIQUES
# ══════════════════════════════════════════════════════════════════════════

class AlertsPage(QWidget):
    """Page d'alertes : stock faible, impayés, produits sans mouvement."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet("background:transparent;")
        self._build_ui()
        self.load_alerts()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(0, 0, 0, 0)

        # Barre actions
        h = QHBoxLayout()
        h.setSpacing(10)
        refresh_btn = _action_btn("🔄 Rafraîchir les alertes",
                                   COLORS.get("primary","#3B82F6"), outlined=True)
        refresh_btn.clicked.connect(self.load_alerts)
        h.addWidget(refresh_btn)

        export_btn = _action_btn("📤 Exporter CSV", COLORS.get("success","#22C55E"), outlined=True)
        export_btn.clicked.connect(self.export_all_csv)
        h.addWidget(export_btn)
        h.addStretch()

        self.summary_lbl = QLabel("Chargement…")
        self.summary_lbl.setFont(QFont("Segoe UI", 10))
        self.summary_lbl.setStyleSheet(f"color:{COLORS.get('TXT_SEC','#A0AACC')}; border:none;")
        h.addWidget(self.summary_lbl)
        root.addLayout(h)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none; background:transparent;}")
        container = QWidget()
        container.setStyleSheet("background:transparent;")
        self.alerts_layout = QVBoxLayout(container)
        self.alerts_layout.setSpacing(14)
        self.alerts_layout.setContentsMargins(0, 0, 4, 0)
        scroll.setWidget(container)
        root.addWidget(scroll)

    def _alert_section(self, icon, title, color, rows, headers, empty_msg):
        """Crée une section d'alerte avec tableau."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{COLORS.get('BG_CARD','#252535')};
                border-radius:12px;
                border:1px solid {color}44;
                border-left:4px solid {color};
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        hdr = QHBoxLayout()
        ic = QLabel(icon)
        ic.setFont(QFont("Segoe UI", 16))
        ic.setStyleSheet(f"background:{color}22; border-radius:8px; border:none; padding:4px 8px;")
        hdr.addWidget(ic)
        tl = _lbl(f"{title}  ({len(rows)})", 12, bold=True, color=color)
        hdr.addWidget(tl)
        hdr.addStretch()
        lay.addLayout(hdr)
        lay.addWidget(_divider())

        if not rows:
            ok = _lbl(f"✅ {empty_msg}", 11, color="#22C55E")
            ok.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ok.setStyleSheet(f"color:#22C55E; padding:12px; background:transparent; border:none;")
            lay.addWidget(ok)
            return card

        tbl = QTableWidget(len(rows), len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.verticalHeader().setVisible(False)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setShowGrid(False)
        tbl.setMaximumHeight(min(40 * len(rows) + 50, 300))
        tbl.setStyleSheet(f"""
            QTableWidget {{
                background:{COLORS.get('BG_DEEP','#16161F')};
                alternate-background-color:rgba(255,255,255,0.025);
                color:{COLORS.get('TXT_PRI','#F0F4FF')};
                border:none; font-size:11px;
            }}
            QHeaderView::section {{
                background:transparent; color:{color};
                font-size:10px; font-weight:bold;
                padding:8px; border:none;
                border-bottom:1px solid {color}55;
            }}
            QTableWidget::item {{ padding:6px 8px; }}
        """)

        for r, row_data in enumerate(rows):
            for c, (val, col) in enumerate(row_data):
                it = QTableWidgetItem(str(val))
                it.setForeground(QColor(col))
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                tbl.setItem(r, c, it)
            tbl.setRowHeight(r, 36)

        lay.addWidget(tbl)
        return card

    def load_alerts(self):
        while self.alerts_layout.count():
            item = self.alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # ── 1. Stock faible / rupture ──────────────────────────────
        try:
            self.db.cursor.execute("""
                SELECT name, stock_quantity, min_stock, selling_price
                FROM products
                WHERE stock_quantity <= min_stock
                ORDER BY stock_quantity ASC
            """)
            stock_rows_raw = self.db.cursor.fetchall()
        except Exception:
            stock_rows_raw = []

        stock_rows = []
        for name, qty, mini, price in stock_rows_raw:
            flag = "🔴 Rupture" if qty == 0 else "🟡 Faible"
            color = "#EF4444" if qty == 0 else "#FBBF24"
            stock_rows.append([
                (str(name),        "#F0F4FF"),
                (str(int(qty)),    color),
                (str(int(mini)),   "#A0AACC"),
                (flag,             color),
                (fmt_da(float(price or 0)), "#F0F4FF"),
            ])

        self.alerts_layout.addWidget(self._alert_section(
            "⚠️", "Alertes Stock", "#FBBF24", stock_rows,
            ["Produit", "Stock actuel", "Stock min", "Statut", "Prix vente"],
            "Tous les produits sont en stock suffisant."
        ))

        # ── 2. Impayés (paiements à crédit) ───────────────────────
        try:
            self.db.cursor.execute("""
                SELECT s.invoice_number, COALESCE(c.name,'Anonyme'), s.total,
                       s.sale_date, s.payment_status
                FROM sales s
                LEFT JOIN clients c ON s.client_id = c.id
                WHERE s.payment_method = 'credit'
                   OR s.payment_status = 'pending'
                ORDER BY s.sale_date DESC
            """)
            credit_raw = self.db.cursor.fetchall()
        except Exception:
            credit_raw = []

        credit_rows = []
        for inv, client, total, date, status in credit_raw:
            date_str = str(date).split(" ")[0] if date else "—"
            credit_rows.append([
                (str(inv or "—"),           "#F0F4FF"),
                (str(client),               "#F0F4FF"),
                (date_str,                  "#A0AACC"),
                (fmt_da(float(total or 0)), "#F87171"),
                ("⏳ En attente",           "#FBBF24"),
            ])

        self.alerts_layout.addWidget(self._alert_section(
            "💳", "Impayés & Paiements à Crédit", "#F87171", credit_rows,
            ["N° Facture", "Client", "Date", "Montant", "Statut"],
            "Aucun paiement en attente. Tout est réglé !"
        ))

        # ── 3. Produits sans mouvement (> 30 jours) ───────────────
        try:
            self.db.cursor.execute("""
                SELECT p.name, p.stock_quantity, p.selling_price,
                       MAX(s.sale_date) as last_sale
                FROM products p
                LEFT JOIN sale_items si ON si.product_id = p.id
                LEFT JOIN sales s ON si.sale_id = s.id
                GROUP BY p.id
                HAVING last_sale IS NULL
                    OR DATE(last_sale) < DATE('now', '-30 days')
                ORDER BY last_sale ASC
                LIMIT 20
            """)
            inactive_raw = self.db.cursor.fetchall()
        except Exception:
            inactive_raw = []

        inactive_rows = []
        for name, qty, price, last in inactive_raw:
            last_str = str(last).split(" ")[0] if last else "Jamais vendu"
            inactive_rows.append([
                (str(name),              "#F0F4FF"),
                (str(int(qty or 0)),     "#A0AACC"),
                (fmt_da(float(price or 0)), "#F0F4FF"),
                (last_str,               "#FBBF24"),
            ])

        self.alerts_layout.addWidget(self._alert_section(
            "📦", "Produits sans mouvement (+30 jours)", "#A855F7", inactive_rows,
            ["Produit", "Stock", "Prix vente", "Dernière vente"],
            "Tous les produits ont été vendus récemment."
        ))

        self.alerts_layout.addStretch()

        total_alerts = len(stock_rows) + len(credit_rows) + len(inactive_rows)
        self.summary_lbl.setText(f"⚠️ {total_alerts} alerte(s) détectée(s)")

    def export_all_csv(self):
        fname, _ = QFileDialog.getSaveFileName(
            self, "Exporter les alertes",
            f"alertes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv);;Tous (*.*)"
        )
        if not fname:
            return
        try:
            with open(fname, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["Type", "Détail", "Valeur", "Info"])
                # Stock
                self.db.cursor.execute(
                    "SELECT name, stock_quantity, min_stock FROM products WHERE stock_quantity <= min_stock")
                for r in self.db.cursor.fetchall():
                    w.writerow(["Stock faible", r[0], f"Stock:{r[1]}", f"Min:{r[2]}"])
                # Crédit
                self.db.cursor.execute(
                    "SELECT invoice_number, total FROM sales WHERE payment_method='credit' OR payment_status='pending'")
                for r in self.db.cursor.fetchall():
                    w.writerow(["Impayé", r[0], fmt_da(float(r[1] or 0)), "En attente"])
            QMessageBox.information(self, "✅ Exporté", f"Alertes exportées.\n\n📁 {fname}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


# ══════════════════════════════════════════════════════════════════════════
#  DIALOGUE ENVOI EMAIL
# ══════════════════════════════════════════════════════════════════════════

class SendEmailDialog(QDialog):
    def __init__(self, report_title, sender_email, sender_pwd,
                 smtp_server, smtp_port, page, parent=None):
        super().__init__(parent)
        self.report_title = report_title
        self.sender_email = sender_email
        self.sender_pwd   = sender_pwd
        self.smtp_server  = smtp_server
        self.smtp_port    = smtp_port
        self.page         = page

        self.setWindowTitle("📧 Envoyer le rapport par email")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"QDialog{{background:{COLORS.get('bg_medium','#252535')};}} "
                           f"QLabel{{color:{COLORS.get('text_primary','#F0F4FF')};font-size:13px;}}")

        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(24, 24, 24, 24)

        lay.addWidget(_lbl(f"📊 Rapport : {report_title}", 13, bold=True))
        lay.addWidget(_divider())

        # Destinataire
        lay.addWidget(_lbl("Destinataire(s) :", 11))
        self.to_edit = QLineEdit()
        self.to_edit.setPlaceholderText("email@exemple.com, email2@exemple.com")
        self.to_edit.setStyleSheet(INPUT_STYLE)
        self.to_edit.setMinimumHeight(40)
        lay.addWidget(self.to_edit)

        # Sujet
        lay.addWidget(_lbl("Sujet :", 11))
        self.subject_edit = QLineEdit(
            f"{report_title} — {datetime.now().strftime('%d/%m/%Y')}")
        self.subject_edit.setStyleSheet(INPUT_STYLE)
        self.subject_edit.setMinimumHeight(40)
        lay.addWidget(self.subject_edit)

        # Message
        lay.addWidget(_lbl("Message (optionnel) :", 11))
        self.msg_edit = QTextEdit()
        self.msg_edit.setPlaceholderText(
            "Bonjour,\n\nVeuillez trouver ci-joint le rapport demandé.\n\nCordialement.")
        self.msg_edit.setStyleSheet(INPUT_STYLE)
        self.msg_edit.setMaximumHeight(100)
        lay.addWidget(self.msg_edit)

        # Info
        info = _lbl(f"📤 Expéditeur : {sender_email}", 9,
                    color=COLORS.get("TXT_SEC","#A0AACC"))
        lay.addWidget(info)

        # Boutons
        h = QHBoxLayout()
        h.setSpacing(10)
        cancel = _action_btn("Annuler", COLORS.get("TXT_SEC","#A0AACC"), outlined=True)
        cancel.clicked.connect(self.reject)
        send = _action_btn("📧 Envoyer", COLORS.get("primary","#3B82F6"))
        send.setFixedWidth(140)
        send.clicked.connect(self._send)
        h.addWidget(cancel)
        h.addStretch()
        h.addWidget(send)
        lay.addLayout(h)

    def _send(self):
        to = self.to_edit.text().strip()
        if not to:
            QMessageBox.warning(self, "Champ manquant", "Veuillez renseigner le(s) destinataire(s).")
            return

        import tempfile, smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders

        # Générer PDF temporaire
        try:
            tmp = tempfile.NamedTemporaryFile(
                suffix=".pdf", delete=False,
                prefix=f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}_")
            tmp.close()
            self.page.export_pdf_to(tmp.name)
            pdf_path = tmp.name
        except Exception as e:
            QMessageBox.critical(self, "Erreur PDF",
                f"Impossible de générer le PDF :\n{e}")
            return

        try:
            msg = MIMEMultipart()
            msg["From"]    = self.sender_email
            msg["To"]      = to
            msg["Subject"] = self.subject_edit.toPlainText() if hasattr(
                self.subject_edit, "toPlainText") else self.subject_edit.text()

            body = self.msg_edit.toPlainText() or (
                f"Bonjour,\n\nVeuillez trouver ci-joint le rapport : {self.report_title}.\n\n"
                f"Date de génération : {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n"
                "Cordialement.")
            msg.attach(MIMEText(body, "plain", "utf-8"))

            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition",
                                f"attachment; filename={os.path.basename(pdf_path)}")
                msg.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15) as s:
                s.starttls()
                s.login(self.sender_email, self.sender_pwd)
                recipients = [r.strip() for r in to.split(",") if r.strip()]
                s.sendmail(self.sender_email, recipients, msg.as_string())

            QMessageBox.information(self, "✅ Envoyé",
                f"Rapport envoyé avec succès à :\n{to}")
            self.accept()

        except smtplib.SMTPAuthenticationError:
            QMessageBox.critical(self, "❌ Authentification",
                "Email ou mot de passe incorrect.")
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur envoi", str(e))
        finally:
            try:
                os.unlink(pdf_path)
            except Exception:
                pass


# Patch export_pdf_to sur BaseReportPage
def _export_pdf_to(self, fname):
    """Version silencieuse de export_pdf (sans dialogue)."""
    rows = self.get_rows()
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors as rc
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Table,
                                         TableStyle, Paragraph, Spacer)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        doc = SimpleDocTemplate(fname, pagesize=landscape(A4),
                                rightMargin=1.5*cm, leftMargin=1.5*cm,
                                topMargin=2*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        C_NAVY = rc.HexColor("#1E3A5F")

        elems = []
        t_style = ParagraphStyle("T", parent=styles["Title"],
                                  fontSize=14, textColor=C_NAVY, spaceAfter=8)
        s_style = ParagraphStyle("S", parent=styles["Normal"],
                                  fontSize=8, textColor=rc.HexColor("#6B7280"), spaceAfter=10)
        elems.append(Paragraph(f"{self.REPORT_ICON} {self.REPORT_TITLE}", t_style))
        elems.append(Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", s_style))

        data = [self.get_headers()] + rows
        col_w = [(landscape(A4)[0] - 3*cm) / len(self.get_headers())] * len(self.get_headers())
        tbl = Table(data, colWidths=col_w, repeatRows=1)
        n = len(data)
        rbs = [("BACKGROUND", (0, i), (-1, i),
                rc.white if i % 2 == 1 else rc.HexColor("#F5F7FA"))
               for i in range(1, n)]
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), C_NAVY),
            ("TEXTCOLOR",     (0, 0), (-1, 0), rc.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
            ("BOX",           (0, 0), (-1, -1), 0.8, rc.HexColor("#D1D9E6")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.3, rc.HexColor("#D1D9E6")),
            *rbs,
        ]))
        elems.append(tbl)
        doc.build(elems)
    except Exception as e:
        raise e

BaseReportPage.export_pdf_to = _export_pdf_to


# ══════════════════════════════════════════════════════════════════════════
#  FENÊTRE PRINCIPALE — REPORTS HUB
# ══════════════════════════════════════════════════════════════════════════

class ReportsHub(QDialog):
    """Fenêtre principale des rapports avec navigation latérale."""

    NAV_ITEMS = [
        ("📊", "Ventes",          "sales"),
        ("🛒", "Achats",          "purchases"),
        ("📦", "Stock",           "stock"),
        ("👥", "Clients",         "clients"),
        ("💰", "Bénéfices",       "profit"),
        ("📈", "Tendances",       "trends"),
        ("🔔", "Alertes",         "alerts"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.setWindowTitle("📊 Centre de Rapports — DAR ELSSALEM")
        self.setMinimumSize(1280, 820)
        self.setStyleSheet(f"QDialog{{background:{COLORS.get('BG_PAGE','#1E1E2E')};}}")
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background:{COLORS.get('BG_DEEP','#16161F')};
                border-right:1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
            }}
        """)
        s_lay = QVBoxLayout(sidebar)
        s_lay.setContentsMargins(0, 20, 0, 16)
        s_lay.setSpacing(0)

        # Titre sidebar
        s_lay.addWidget(_lbl("  📊  Rapports", 13, bold=True,
                              color=COLORS.get("primary","#3B82F6")))
        s_lay.addSpacing(8)
        sep = _divider()
        sep.setContentsMargins(12, 0, 12, 0)
        s_lay.addWidget(sep)
        s_lay.addSpacing(8)

        self.nav_btns = {}
        self.stack = QStackedWidget()

        pages = {
            "sales":     SalesReportPage(self.db),
            "purchases": PurchasesReportPage(self.db),
            "stock":     StockReportPage(self.db),
            "clients":   ClientsReportPage(self.db),
            "profit":    ProfitReportPage(self.db),
            "trends":    TrendsReportPage(self.db),
            "alerts":    AlertsPage(self.db),
        }

        for icon, label, key in self.NAV_ITEMS:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setFont(QFont("Segoe UI", 11))
            btn.setFixedHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("key", key)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:transparent;
                    border-left:4px solid transparent;
                    color:{COLORS.get('TXT_SEC','#A0AACC')};
                    text-align:left; padding-left:10px; font-weight:500;
                    border-right:none; border-top:none; border-bottom:none;
                }}
                QPushButton:hover {{
                    background:{COLORS.get('primary','#3B82F6')}18;
                    border-left:4px solid {COLORS.get('primary','#3B82F6')}66;
                    color:{COLORS.get('TXT_PRI','#F0F4FF')};
                }}
            """)
            btn.clicked.connect(lambda _, k=key: self._show_page(k))
            s_lay.addWidget(btn)
            self.nav_btns[key] = btn
            self.stack.addWidget(pages[key])

        s_lay.addStretch()

        # Bouton fermer
        close_btn = QPushButton("✖  Fermer")
        close_btn.setFixedHeight(40)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFont(QFont("Segoe UI", 10))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{COLORS.get('TXT_SEC','#A0AACC')};
                border:1px solid {COLORS.get('BORDER','rgba(255,255,255,0.08)')};
                border-radius:8px; margin:0 12px;
            }}
            QPushButton:hover {{background:rgba(239,68,68,0.15); color:#EF4444;}}
        """)
        close_btn.clicked.connect(self.accept)
        s_lay.addWidget(close_btn)

        root.addWidget(sidebar)

        # ── Contenu ────────────────────────────────────────────────
        content = QFrame()
        content.setStyleSheet("background:transparent;")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(24, 20, 24, 20)
        c_lay.setSpacing(0)
        c_lay.addWidget(self.stack)
        root.addWidget(content, 1)

        self._show_page("sales")

    def _show_page(self, key):
        idx = list(k for _, _, k in self.NAV_ITEMS).index(key)
        self.stack.setCurrentIndex(idx)
        for k, btn in self.nav_btns.items():
            if k == key:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background:{COLORS.get('primary','#3B82F6')}22;
                        border-left:4px solid {COLORS.get('primary','#3B82F6')};
                        color:{COLORS.get('primary','#3B82F6')};
                        text-align:left; padding-left:10px; font-weight:bold;
                        border-right:none; border-top:none; border-bottom:none;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background:transparent;
                        border-left:4px solid transparent;
                        color:{COLORS.get('TXT_SEC','#A0AACC')};
                        text-align:left; padding-left:10px; font-weight:500;
                        border-right:none; border-top:none; border-bottom:none;
                    }}
                    QPushButton:hover {{
                        background:{COLORS.get('primary','#3B82F6')}18;
                        border-left:4px solid {COLORS.get('primary','#3B82F6')}66;
                        color:{COLORS.get('TXT_PRI','#F0F4FF')};
                    }}
                """)


# ── Fonction d'ouverture rapide ────────────────────────────────────────
def open_reports(parent=None, page="sales"):
    """Ouvre le centre de rapports, positionné sur la page souhaitée."""
    hub = ReportsHub(parent)
    hub._show_page(page)
    hub.exec()
