"""
dashboard.py — Tableau de Bord DAR ELSSALEM
============================================
Structure 2×2 :
  ┌─────────────────────────────────────────┐
  │  KPI  KPI  KPI  KPI  (ligne complète)  │
  ├──────────────────┬──────────────────────┤
  │  Activités +     │  Top Clients         │
  │  Infos Rapides   │  (noms + barres)     │
  ├──────────────────┼──────────────────────┤
  │  Dernières       │  Alertes Stock       │
  │  Factures        │  Faible              │
  ├──────────────────┴──────────────────────┤
  │  Ventes — 7 derniers jours (pleine lrg) │
  └─────────────────────────────────────────┘
"""

import datetime

from PyQt6.QtWidgets import (
    QProgressBar, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QHeaderView, QTableWidget, QTableWidgetItem,
    QSizePolicy, QMessageBox, QScrollArea, QGridLayout
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation, QEasingCurve

from db_manager import get_database
from styles import COLORS
from currency import fmt_da, currency_manager

try:
    from sales_history import InvoiceDetailsDialog
    _DETAIL_AVAILABLE = True
except ImportError:
    _DETAIL_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════

def _clear_layout(layout):
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.deleteLater()
        elif item.layout() is not None:
            _clear_layout(item.layout())


def _sep():
    """Séparateur horizontal."""
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("background:rgba(255,255,255,0.10); border:none; max-height:1px;")
    return f


def _lbl(text, size=11, bold=False, color=""):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", size,
                    QFont.Weight.Bold if bold else QFont.Weight.Normal))
    c = color or COLORS.get("TXT_PRI", "#F0F4FF")
    l.setStyleSheet(f"color:{c}; background:transparent; border:none; padding:0;")
    return l


def _card(name="card", border_color=""):
    """Carte avec fond sombre et bordure optionnelle."""
    f = QFrame()
    f.setObjectName(name)
    bdr = border_color or "rgba(255,255,255,0.08)"
    f.setStyleSheet(f"""
        QFrame#{name} {{
            background:{COLORS.get('BG_CARD','#252535')};
            border-radius:14px;
            border:1px solid {bdr};
        }}
    """)
    return f


def _icon_box(icon, color, size=32, icon_size=14):
    """Icône dans un QFrame carré arrondi (évite l'aspect radio-button)."""
    frame = QFrame()
    frame.setFixedSize(size, size)
    frame.setStyleSheet(
        f"background:{color}28; border-radius:{size//4}px; border:none;")
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(0, 0, 0, 0)
    lbl = QLabel(icon)
    lbl.setFont(QFont("Segoe UI", icon_size))
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet("background:transparent; border:none;")
    lay.addWidget(lbl)
    return frame


# ══════════════════════════════════════════════════════════════════════════
#  ANIMATEUR KPI
# ══════════════════════════════════════════════════════════════════════════

class KpiAnimator(QObject):
    def __init__(self, label, suffix=""):
        super().__init__()
        self._value = 0
        self.label  = label
        self.suffix = suffix

    def get_value(self):  return self._value

    def set_value(self, v):
        self._value = v
        self.label.setText(f"{v:,.0f}{self.suffix}")

    value = pyqtProperty(float, get_value, set_value)


def animate_value(label, target, suffix=""):
    anim = KpiAnimator(label, suffix)
    a    = QPropertyAnimation(anim, b"value")
    a.setDuration(800)
    a.setStartValue(0.0)
    a.setEndValue(float(target))
    a.setEasingCurve(QEasingCurve.Type.OutCubic)
    label._anim_ref = a
    label._anim_obj = anim
    a.start()


# ══════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════

class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.setStyleSheet(f"background:{COLORS.get('BG_PAGE','#1E1E2E')};")
        self._build_ui()
        self.refresh()

    # ─────────────────────────────────────────────────────────────
    #  Construction de l'interface
    # ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none; background:transparent;}")

        container = QWidget()
        container.setStyleSheet("background:transparent;")
        self._main = QVBoxLayout(container)
        self._main.setSpacing(16)
        self._main.setContentsMargins(24, 18, 24, 20)

        # ── En-tête ──
        self._build_header()

        # ── Ligne KPI (4 cartes pleine largeur) ──
        self._build_kpi_row()

        # ── Grille 2×2 ──────────────────────────────────────────
        # ┌──────────────────────┬──────────────────────┐
        # │ Activités+Infos [L]  │  Top Clients     [R] │
        # ├──────────────────────┼──────────────────────┤
        # │ Dernières Factures[L]│  Alertes Stock   [R] │
        # └──────────────────────┴──────────────────────┘

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Ligne 0
        grid.addWidget(self._build_activity_info_card(), 0, 0)
        grid.addWidget(self._build_top_clients_card(),   0, 1)

        # Ligne 1
        grid.addWidget(self._build_invoices_card(),      1, 0)
        grid.addWidget(self._build_low_stock_card(),     1, 1)

        self._main.addLayout(grid)

        # ── Ventes 7 jours (pleine largeur) ──
        self._build_sales_chart_card()

        self._main.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)

    # ─────────────────────────────────────────────────────────────
    #  En-tête
    # ─────────────────────────────────────────────────────────────

    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        col = QVBoxLayout()
        col.setSpacing(2)
        title = QLabel("📊 Tableau de Bord")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color:{COLORS.get('TXT_PRI','#F0F4FF')}; background:transparent;")
        col.addWidget(title)
        self._subtitle = QLabel("Vue d'ensemble de l'activité")
        self._subtitle.setFont(QFont("Segoe UI", 10))
        self._subtitle.setStyleSheet(
            f"color:{COLORS.get('TXT_SEC','#A0AACC')}; background:transparent;")
        col.addWidget(self._subtitle)
        row.addLayout(col)
        row.addStretch()

        self._last_update_lbl = QLabel("")
        self._last_update_lbl.setFont(QFont("Segoe UI", 9))
        self._last_update_lbl.setStyleSheet(
            "color:rgba(160,170,204,0.45); background:transparent;")
        row.addWidget(self._last_update_lbl)

        btn = QPushButton("🔄  Rafraîchir")
        btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        btn.setFixedHeight(36)
        btn.setFixedWidth(130)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:rgba(59,130,246,0.15);
                color:{COLORS.get('primary','#3B82F6')};
                border:1.5px solid {COLORS.get('primary','#3B82F6')}88;
                border-radius:9px;
            }}
            QPushButton:hover  {{ background:rgba(59,130,246,0.28); }}
            QPushButton:pressed {{ background:rgba(59,130,246,0.42); }}
        """)
        btn.clicked.connect(self.refresh)
        row.addWidget(btn)
        self._main.addLayout(row)

    # ─────────────────────────────────────────────────────────────
    #  Ligne KPI
    # ─────────────────────────────────────────────────────────────

    def _build_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(14)
        sym = currency_manager.primary.symbol

        self._kpi_meta = [
            ("Ventes Totales", "#6366F1", "💳", f" {sym}"),
            ("Achats",         "#F59E0B", "🛒", f" {sym}"),
            ("Bénéfice Net",   "#10B981", "📈", f" {sym}"),
            ("Clients",        "#06B6D4", "👥", ""),
        ]
        self.kpi_cards = []
        for title, color, icon, suffix in self._kpi_meta:
            card = self._make_kpi_card(icon, title, color, suffix)
            row.addWidget(card)
            self.kpi_cards.append(card)
        self._main.addLayout(row)

    def _make_kpi_card(self, icon, title, color, suffix):
        card = QFrame()
        card.setObjectName("kpi")
        card.setFixedHeight(118)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(f"""
            QFrame#kpi {{
                background:{COLORS.get('BG_CARD','#252535')};
                border-radius:14px; border:1px solid {color}44;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 13, 18, 11)
        lay.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(_icon_box(icon, color, size=38, icon_size=16))

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 11))
        title_lbl.setStyleSheet(
            f"color:{COLORS.get('TXT_SEC','#A0AACC')}; "
            "background:transparent; border:none;")
        top.addWidget(title_lbl)
        top.addStretch()

        evol = QLabel("")
        evol.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        evol.setStyleSheet("background:transparent; border:none; color:transparent;")
        top.addWidget(evol)
        lay.addLayout(top)

        val_lbl = QLabel("0")
        val_lbl.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        val_lbl.setStyleSheet(f"color:{color}; background:transparent; border:none;")
        lay.addWidget(val_lbl)

        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {color}, stop:0.55 {color}77, stop:1 transparent);"
            "border-radius:2px; border:none;")
        lay.addWidget(bar)

        card.value_label = val_lbl
        card.evol_badge  = evol
        card.suffix      = suffix
        card.kpi_color   = color
        return card

    # ─────────────────────────────────────────────────────────────
    #  WIDGET GAUCHE / LIGNE 0
    #  Activités Récentes + Infos Rapides (fusionnés en 1 carte)
    # ─────────────────────────────────────────────────────────────

    def _build_activity_info_card(self):
        """Carte unique = Activités (haut) + Infos Rapides (bas)."""
        card = _card("actinfo")
        card.setMinimumHeight(280)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        # ── Section Activités ──────────────────────────────────
        lay.addWidget(_lbl("🕒  Activités Récentes", 13, bold=True))
        lay.addSpacing(8)
        lay.addWidget(_sep())
        lay.addSpacing(8)

        self.activities_layout = QVBoxLayout()
        self.activities_layout.setSpacing(7)
        lay.addLayout(self.activities_layout)

        lay.addSpacing(14)
        lay.addWidget(_sep())
        lay.addSpacing(10)

        # ── Section Infos Rapides ──────────────────────────────
        
        return card

    # ─────────────────────────────────────────────────────────────
    #  WIDGET DROIT / LIGNE 0
    #  Top Clients avec noms + montants + barres
    # ─────────────────────────────────────────────────────────────

    def _build_top_clients_card(self):
        card = _card("tc")
        card.setMinimumHeight(80)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("🏆  Top Clients", 13, bold=True))
        hdr.addStretch()
        self._tc_period_lbl = _lbl("Cette année", 9,
                                    color=COLORS.get("TXT_SEC","#A0AACC"))
        hdr.addWidget(self._tc_period_lbl)
        lay.addLayout(hdr)
        lay.addSpacing(0)
        lay.addWidget(_sep())
        lay.addSpacing(0)

        self.top_clients_layout = QVBoxLayout()
        self.top_clients_layout.setSpacing(0)
        lay.addLayout(self.top_clients_layout)
        lay.addStretch()
        return card

    # ─────────────────────────────────────────────────────────────
    #  WIDGET GAUCHE / LIGNE 1
    #  Dernières Factures
    # ─────────────────────────────────────────────────────────────

    def _build_invoices_card(self):
        card = _card("inv")
        card.setMinimumHeight(260)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("🧾  Dernières Factures", 13, bold=True))
        hdr.addStretch()
        hdr.addWidget(_lbl("10 dernières", 9,
                            color=COLORS.get("TXT_SEC","#A0AACC")))
        lay.addLayout(hdr)
        lay.addSpacing(8)
        lay.addWidget(_sep())
        lay.addSpacing(4)

        self.invoice_table = QTableWidget(0, 6)
        self.invoice_table.setHorizontalHeaderLabels(
            ["N° Facture", "Client", "Total TTC", "Date", "Paiement", ""])

        hv = self.invoice_table.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hv.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.invoice_table.setColumnWidth(5, 40)

        self.invoice_table.verticalHeader().setVisible(False)
        self.invoice_table.setAlternatingRowColors(True)
        self.invoice_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.invoice_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.invoice_table.setShowGrid(False)
        self.invoice_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.invoice_table.setStyleSheet(f"""
            QTableWidget {{
                background:transparent;
                alternate-background-color:rgba(255,255,255,0.03);
                color:{COLORS.get('TXT_PRI','#F0F4FF')};
                border:none; font-size:12px;
            }}
            QHeaderView::section {{
                background:{COLORS.get('BG_DEEP','#16161F')};
                color:{COLORS.get('primary','#3B82F6')};
                font-size:11px; font-weight:bold;
                padding:9px 8px; border:none;
                border-bottom:2px solid {COLORS.get('primary','#3B82F6')};
            }}
            QTableWidget::item {{
                padding:9px 8px;
                border-bottom:1px solid rgba(255,255,255,0.04);
            }}
            QTableWidget::item:selected {{
                background:rgba(99,102,241,0.22); color:white;
            }}
        """)
        lay.addWidget(self.invoice_table, 1)
        return card

    # ─────────────────────────────────────────────────────────────
    #  WIDGET DROIT / LIGNE 1
    #  Alertes Stock Faible
    # ─────────────────────────────────────────────────────────────

    def _build_low_stock_card(self):
        card = _card("ls")
        card.setMinimumHeight(260)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("⚠️  Alertes Stock Faible", 13, bold=True))
        hdr.addStretch()
        self._ls_count = _lbl("", 10,
                               color=COLORS.get("warning","#FBBF24"))
        hdr.addWidget(self._ls_count)
        lay.addLayout(hdr)
        lay.addSpacing(8)
        lay.addWidget(_sep())
        lay.addSpacing(10)

        self.low_stock_layout = QVBoxLayout()
        self.low_stock_layout.setSpacing(8)
        lay.addLayout(self.low_stock_layout)
        lay.addStretch()
        return card

    # ─────────────────────────────────────────────────────────────
    #  Graphique Ventes 7 jours (pleine largeur)
    # ─────────────────────────────────────────────────────────────

    def _build_sales_chart_card(self):
        card = _card("chart")
        card.setMinimumHeight(190)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("📈  Ventes — 7 derniers jours", 13, bold=True))
        hdr.addStretch()
        self._chart_total = _lbl("", 11, bold=True,
                                  color=COLORS.get("success","#22C55E"))
        hdr.addWidget(self._chart_total)
        lay.addLayout(hdr)
        lay.addSpacing(8)
        lay.addWidget(_sep())
        lay.addSpacing(10)

        self.sales_chart_layout = QVBoxLayout()
        self.sales_chart_layout.setSpacing(6)
        lay.addLayout(self.sales_chart_layout)
        self._main.addWidget(card)

    # ─────────────────────────────────────────────────────────────
    #  showEvent
    # ─────────────────────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    # ─────────────────────────────────────────────────────────────
    #  Rafraîchissement
    # ─────────────────────────────────────────────────────────────

    def refresh(self):
        self._load_kpis()
        self._load_activities()
        # self._load_info()
        self._load_invoices()
        self._load_low_stock()
        self._load_top_clients()
        self._load_sales_chart()
        now = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M")
        self._last_update_lbl.setText(f"Mis à jour le  {now}")

    # ─────────────────────────────────────────────────────────────
    #  KPI
    # ─────────────────────────────────────────────────────────────

    def _load_kpis(self):
        stats = self.db.get_statistics() or {}
        sales = float(stats.get("sales_total", 0))
        pur   = float(stats.get("purchases_total", 0))
        prof  = sales - pur
        cli   = int(stats.get("total_clients", 0))
        sym   = currency_manager.primary.symbol

        prev_sales = prev_pur = 0.0
        try:
            today      = datetime.date.today()
            first_this = today.replace(day=1)
            last_prev  = first_this - datetime.timedelta(days=1)
            first_prev = last_prev.replace(day=1)
            self.db.cursor.execute(
                "SELECT COALESCE(SUM(total),0) FROM sales "
                "WHERE DATE(sale_date) BETWEEN ? AND ?",
                (str(first_prev), str(last_prev)))
            prev_sales = float(self.db.cursor.fetchone()[0] or 0)
            self.db.cursor.execute(
                "SELECT COALESCE(SUM(total),0) FROM purchases "
                "WHERE DATE(purchase_date) BETWEEN ? AND ?",
                (str(first_prev), str(last_prev)))
            prev_pur = float(self.db.cursor.fetchone()[0] or 0)
        except Exception:
            pass

        prev_prof = prev_sales - prev_pur
        values   = [sales, pur, prof, float(cli)]
        prevs    = [prev_sales, prev_pur, prev_prof, None]
        suffixes = [f" {sym}", f" {sym}", f" {sym}", ""]

        for card, val, prev, suf in zip(self.kpi_cards, values, prevs, suffixes):
            if card is self.kpi_cards[2]:
                c = "#10B981" if val >= 0 else "#EF4444"
                card.value_label.setStyleSheet(
                    f"color:{c}; background:transparent; border:none;")
                card.setStyleSheet(f"""
                    QFrame#kpi {{
                        background:{COLORS.get('BG_CARD','#252535')};
                        border-radius:14px; border:1px solid {c}55;
                    }}
                """)

            animate_value(card.value_label, val, suf)

            if prev is not None and prev > 0:
                evol = ((val - prev) / prev) * 100
                if evol > 0.5:
                    txt, fg, bg = f"▲ +{evol:.0f}%", "#FFF", "#16A34A"
                elif evol < -0.5:
                    txt, fg, bg = f"▼ {evol:.0f}%",  "#FFF", "#DC2626"
                else:
                    txt, fg, bg = "→ stable", "#F0F4FF", "rgba(160,170,204,0.22)"
                card.evol_badge.setText(txt)
                card.evol_badge.setStyleSheet(
                    f"color:{fg}; background:{bg}; border-radius:5px; "
                    "padding:2px 8px; font-size:10px; font-weight:bold; border:none;")
            else:
                card.evol_badge.setText("")
                card.evol_badge.setStyleSheet(
                    "background:transparent; border:none; color:transparent;")

    # ─────────────────────────────────────────────────────────────
    #  Activités Récentes
    # ─────────────────────────────────────────────────────────────

    def _load_activities(self):
        _clear_layout(self.activities_layout)

        try:    sales = self.db.get_all_sales(limit=4) or []
        except Exception: sales = []
        try:    purs  = self.db.get_all_purchases(limit=3) or []
        except Exception: purs  = []

        if not sales and not purs:
            empty = QLabel("  Aucune activité récente")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                "color:rgba(160,170,204,0.60); padding:12px; border:none;")
            self.activities_layout.addWidget(empty)
            return

        def _row(icon, bg, text):
            row = QHBoxLayout()
            row.setSpacing(10)
            row.addWidget(_icon_box(icon, "", size=20, icon_size=10))
            # Override bg direct sur le frame
            frame = row.itemAt(0).widget()
            frame.setStyleSheet(
                f"background:{bg}; border-radius:8px; border:none;")
            tl = QLabel(text)
            tl.setFont(QFont("Segoe UI", 11))
            tl.setStyleSheet(
                f"color:{COLORS.get('TXT_PRI','#F0F4FF')}; "
                "background:transparent; border:none;")
            tl.setWordWrap(False)
            row.addWidget(tl, 1)
            self.activities_layout.addLayout(row)

        for s in sales:
            txt = f"Vente  {s.get('invoice_number','—')}"
            if s.get("client_name"):
                txt += f"  ·  {s['client_name'][:20]}"
            txt += f"  —  {fmt_da(float(s.get('total', 0)), 0)}"
            _row("🧾", "rgba(99,102,241,0.25)", txt)

        for p in purs:
            txt = f"Achat  {str(p.get('product_name','?'))[:22]}"
            if p.get("supplier_name"):
                txt += f"  ·  {p['supplier_name'][:16]}"
            txt += f"  —  {fmt_da(float(p.get('total', 0)), 0)}"
            _row("📦", "rgba(245,158,11,0.25)", txt)

    # ─────────────────────────────────────────────────────────────
    #  Infos Rapides
    # ─────────────────────────────────────────────────────────────

    

    # ─────────────────────────────────────────────────────────────
    #  Tableau Factures
    # ─────────────────────────────────────────────────────────────

    def _load_invoices(self):
        PAY = {
            "cash":"💵 Espèces","card":"💳 Carte",
            "check":"📝 Chèque","transfer":"🏦 Virement",
            "mobile":"📱 Mobile","credit":"🔄 Crédit",
        }
        STATUS_COLOR = {
            "paid":"#22C55E", "pending":"#FBBF24", "cancelled":"#EF4444"}

        try:    data = self.db.get_all_sales(limit=10) or []
        except Exception: data = []

        self.invoice_table.setRowCount(len(data))
        for r, sale in enumerate(data):
            client = sale.get("client_name") or "—"
            date   = str(sale.get("sale_date") or "—").split(" ")[0]
            pay    = PAY.get(sale.get("payment_method",""),
                             sale.get("payment_method") or "—")
            total  = float(sale.get("total") or 0)
            status = sale.get("payment_status", "paid")
            tc     = STATUS_COLOR.get(status, "#F0F4FF")

            cells = [
                (str(sale.get("invoice_number","—")), "#F0F4FF",
                 Qt.AlignmentFlag.AlignLeft),
                (str(client), "#F0F4FF",
                 Qt.AlignmentFlag.AlignLeft),
                (fmt_da(total), tc,
                 Qt.AlignmentFlag.AlignRight),
                (date, "#A0AACC",
                 Qt.AlignmentFlag.AlignCenter),
                (pay, "#D1D5DB",
                 Qt.AlignmentFlag.AlignLeft),
            ]
            for col, (val, color, align) in enumerate(cells):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(color))
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | align)
                if col == 2:
                    it.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                self.invoice_table.setItem(r, col, it)

            btn = QPushButton("👁")
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background:rgba(99,102,241,0.20);
                    border-radius:8px; font-size:13px; border:none;
                }
                QPushButton:hover { background:rgba(99,102,241,0.42); }
            """)
            btn.clicked.connect(
                lambda _, sid=sale["id"]: self._open_detail(sid))
            self.invoice_table.setCellWidget(r, 5, btn)
            self.invoice_table.setRowHeight(r, 40)

    # ─────────────────────────────────────────────────────────────
    #  Alertes Stock Faible
    # ─────────────────────────────────────────────────────────────

    def _load_low_stock(self):
        _clear_layout(self.low_stock_layout)
        try:    products = self.db.get_low_stock_products() or []
        except Exception: products = []

        nb = len(products)
        self._ls_count.setText(
            f"{nb} alerte{'s' if nb != 1 else ''}" if nb else "")

        if not products:
            self.low_stock_layout.addWidget(
                _lbl("✅  Tous les stocks sont suffisants", 11, color="#22C55E"))
            return

        for p in products[:8]:
            stock      = int(p.get("stock_quantity", 0))
            mini       = int(p.get("min_stock", 0))
            name       = str(p.get("name", "—"))
            is_rupture = (stock == 0)
            dot_color  = "#EF4444" if is_rupture else "#FBBF24"

            row_frame = QFrame()
            row_frame.setStyleSheet(
                f"background:{'rgba(239,68,68,0.08)' if is_rupture else 'rgba(251,191,36,0.07)'};"
                "border-radius:8px; border:none;")
            rh = QHBoxLayout(row_frame)
            rh.setContentsMargins(12, 8, 12, 8)
            rh.setSpacing(10)

            # Pastille ronde (QFrame, pas QLabel)
            dot = QFrame()
            dot.setFixedSize(13, 13)
            dot.setStyleSheet(
                f"background:{dot_color}; border-radius:7px; border:none;")
            rh.addWidget(dot)

            nl = QLabel(name[:34])
            nl.setFont(QFont("Segoe UI", 11))
            nl.setStyleSheet(
                f"color:{COLORS.get('TXT_PRI','#F0F4FF')}; "
                "background:transparent; border:none;")
            rh.addWidget(nl, 1)

            sl = QLabel("RUPTURE" if is_rupture else f"{stock} / {mini}")
            sl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            sl.setStyleSheet(
                f"color:{dot_color}; background:transparent; border:none;")
            sl.setAlignment(Qt.AlignmentFlag.AlignRight)
            rh.addWidget(sl)

            self.low_stock_layout.addWidget(row_frame)

    # ─────────────────────────────────────────────────────────────
    #  Top Clients  (noms + montants + barres)
    # ─────────────────────────────────────────────────────────────

    def _load_top_clients(self):
        _clear_layout(self.top_clients_layout)
        try:
            self.db.cursor.execute("""
                SELECT c.name,
                    COUNT(s.id)              AS nb_ventes,
                    COALESCE(SUM(s.total),0) AS ca
                FROM   sales s
                JOIN   clients c ON s.client_id = c.id
                GROUP  BY s.client_id
                ORDER  BY ca DESC
                LIMIT  5
            """)
            clients = [dict(r) for r in self.db.cursor.fetchall()]
        except Exception:
            clients = []

        if not clients:
            self.top_clients_layout.addWidget(
                _lbl("  Aucun client avec des ventes", 11,
                    color=COLORS.get("TXT_SEC","#A0AACC")))
            return

        MEDALS       = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        MEDAL_COLORS = ["#F59E0B","#94A3B8","#CD7F32","#6B7280","#6B7280"]
        max_ca       = max((c["ca"] for c in clients), default=1) or 1

        for rank, c in enumerate(clients):
            name  = str(c["name"])
            ca    = float(c["ca"])
            nb_v  = int(c["nb_ventes"])
            pct   = ca / max_ca
            mc    = MEDAL_COLORS[rank]

            # Conteneur principal
            client_container = QWidget()
            client_layout = QVBoxLayout(client_container)
            client_layout.setContentsMargins(0, 0, 0, 0)
            client_layout.setSpacing(4)

            # Ligne principale
            row_widget = QWidget()
            row_widget.setStyleSheet(
                "background:rgba(255,255,255,0.03); "
                "border-radius:10px; border:none;")
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(12, 10, 12, 10)
            row_layout.setSpacing(12)

            # Médaille
            medal_frame = QFrame()
            medal_frame.setFixedSize(30, 30)
            medal_frame.setStyleSheet(
                f"background:{mc}25; border-radius:10px; "
                f"border:1px solid {mc}50;")
            medal_layout = QVBoxLayout(medal_frame)
            medal_layout.setContentsMargins(0, 0, 0, 0)
            medal_label = QLabel(MEDALS[rank])
            medal_label.setFont(QFont("Segoe UI", 15))
            medal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            medal_label.setStyleSheet("background:transparent; border:none;")
            medal_layout.addWidget(medal_label)
            row_layout.addWidget(medal_frame)

            # Nom
            name_label = QLabel(name[:28])
            name_label.setFont(QFont("Segoe UI", 10, 
                                    QFont.Weight.Bold if rank == 0 
                                    else QFont.Weight.Normal))
            name_label.setStyleSheet(f"color:{COLORS.get('TXT_PRI','#F0F4FF')};")
            row_layout.addWidget(name_label, 1)

            # ✅ Montant et nombre ventes sur la même ligne mais avec un espace
            info_label = QLabel(f"{fmt_da(ca, 0)}  ·  ({nb_v} vente{'s' if nb_v > 1 else ''})")
            info_label.setFont(QFont("Segoe UI", 10))
            info_label.setStyleSheet(
                f"color:{COLORS.get('primary','#3B82F6')};")
            info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            row_layout.addWidget(info_label)

            client_layout.addWidget(row_widget)

            # Barre
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 1000)
            progress_bar.setValue(int(pct * 1000))
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(3)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background: rgba(255,255,255,0.08);
                    border-radius: 2px;
                    border: none;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {COLORS.get('primary','#3B82F6')},
                        stop:1 {COLORS.get('secondary','#A855F7')});
                    border-radius: 2px;
                }}
            """)
            client_layout.addWidget(progress_bar)

            self.top_clients_layout.addWidget(client_container)

    # ─────────────────────────────────────────────────────────────
    #  Graphique Ventes 7 jours
    # ─────────────────────────────────────────────────────────────

    def _load_sales_chart(self):
        _clear_layout(self.sales_chart_layout)
        try:
            self.db.cursor.execute("""
                SELECT DATE(sale_date) AS day,
                       SUM(total)      AS total,
                       COUNT(*)        AS nb
                FROM   sales
                WHERE  sale_date >= DATE('now', '-6 days')
                GROUP  BY day ORDER BY day
            """)
            rows_db = {r[0]: (float(r[1] or 0), int(r[2] or 0))
                       for r in self.db.cursor.fetchall()}
        except Exception:
            rows_db = {}

        today   = datetime.date.today()
        jours   = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"]
        days    = [today - datetime.timedelta(days=6-i) for i in range(7)]
        totals  = [rows_db.get(str(d),(0.0,0))[0] for d in days]
        max_val = max(totals, default=1) or 1
        grand   = sum(totals)

        self._chart_total.setText(
            f"Total semaine : {fmt_da(grand, 0)}" if grand > 0 else "")

        for day_date, total in zip(days, totals):
            nb       = rows_db.get(str(day_date),(0,0))[1]
            dn       = jours[day_date.weekday()]
            is_today = (day_date == today)

            rh = QHBoxLayout()
            rh.setSpacing(10)

            # Label jour — largeur fixe pour alignement des barres
            day_color = (COLORS.get("primary","#3B82F6")
                         if is_today
                         else COLORS.get("TXT_SEC","#A0AACC"))
            prefix = "▶ " if is_today else "   "
            dl = QLabel(f"{prefix}{dn} {day_date.strftime('%d/%m')}")
            dl.setFont(QFont("Segoe UI", 10,
                       QFont.Weight.Bold if is_today else QFont.Weight.Normal))
            dl.setFixedWidth(95)
            dl.setStyleSheet(
                f"color:{day_color}; background:transparent; border:none;")
            rh.addWidget(dl)

            # Barre
            bar = QProgressBar()
            bar.setRange(0, 1000)
            bar.setValue(int((total / max_val) * 1000) if total > 0 else 0)
            bar.setTextVisible(False)
            bar.setFixedHeight(14)

            if total == 0:
                chunk = "background:rgba(255,255,255,0.06); border-radius:5px;"
            elif is_today:
                chunk = (
                    f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                    f"stop:0 {COLORS.get('primary','#3B82F6')},"
                    f"stop:1 {COLORS.get('secondary','#A855F7')});"
                    "border-radius:5px;")
            else:
                chunk = (
                    f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                    f"stop:0 {COLORS.get('primary','#3B82F6')}99,"
                    f"stop:1 {COLORS.get('secondary','#A855F7')}99);"
                    "border-radius:5px;")

            bar.setStyleSheet(f"""
                QProgressBar {{
                    background:{COLORS.get('BG_DEEP','#16161F')};
                    border-radius:5px; border:none;
                }}
                QProgressBar::chunk {{ {chunk} }}
            """)
            rh.addWidget(bar, 1)

            # Montant
            amt_color = (COLORS.get("success","#22C55E")
                         if total > 0
                         else "rgba(160,170,204,0.35)")
            al = QLabel(fmt_da(total, 0) if total > 0 else "—")
            al.setFont(QFont("Segoe UI", 11,
                       QFont.Weight.Bold if total > 0 else QFont.Weight.Normal))
            al.setFixedWidth(135)
            al.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            al.setStyleSheet(
                f"color:{amt_color}; background:transparent; border:none;")
            rh.addWidget(al)

            # Nb ventes
            nbl = QLabel(f"({nb})" if nb > 0 else "")
            nbl.setFont(QFont("Segoe UI", 9))
            nbl.setFixedWidth(40)
            nbl.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            nbl.setStyleSheet(
                "color:rgba(160,170,204,0.60); background:transparent; border:none;")
            rh.addWidget(nbl)

            self.sales_chart_layout.addLayout(rh)

    # ─────────────────────────────────────────────────────────────
    #  Détail facture
    # ─────────────────────────────────────────────────────────────

    def _open_detail(self, sale_id: int):
        if not _DETAIL_AVAILABLE:
            QMessageBox.warning(self, "Module manquant",
                                "Le module sales_history.py est introuvable.")
            return
        try:
            sale = self.db.get_sale_by_id(sale_id)
            if sale:
                InvoiceDetailsDialog(sale, self).exec()
            else:
                QMessageBox.warning(self, "Introuvable",
                                    "Cette vente n'existe plus en base.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Impossible d'ouvrir la facture :\n{e}")
