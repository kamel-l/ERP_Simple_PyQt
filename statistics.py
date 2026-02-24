from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation, QEasingCurve
import pyqtgraph as pg
from db_manager import get_database
from datetime import datetime


# ─────────────────────────────────────────────────────────────
#  Palette cohérente avec dashboard / settings
# ─────────────────────────────────────────────────────────────

BG_PAGE  = "#0F1117"
BG_CARD  = "#1A1D27"
BG_DEEP  = "#13151F"
BORDER   = "rgba(255,255,255,0.07)"
TXT_PRI  = "#F1F5F9"
TXT_SEC  = "rgba(255,255,255,0.45)"
TXT_MUTE = "rgba(255,255,255,0.22)"

# Couleurs des indicateurs
C_BLUE   = "#3B82F6"
C_GREEN  = "#10B981"
C_AMBER  = "#F59E0B"
C_VIOLET = "#8B5CF6"
C_CYAN   = "#06B6D4"
C_RED    = "#EF4444"

CHART_COLORS = [C_BLUE, C_GREEN, C_AMBER, C_VIOLET, C_CYAN]

CARD_STYLE = f"""
    QFrame {{
        background: {BG_CARD};
        border-radius: 16px;
        border: 1px solid {BORDER};
    }}
"""


# ─────────────────────────────────────────────────────────────
#  Animateur de compteur
# ─────────────────────────────────────────────────────────────

class _KpiAnim(QObject):
    def __init__(self, label, suffix=""):
        super().__init__()
        self._v = 0
        self.label  = label
        self.suffix = suffix

    def _get(self): return self._v
    def _set(self, v):
        self._v = v
        self.label.setText(f"{v:,.0f}{self.suffix}")
    value = pyqtProperty(float, fget=_get, fset=_set)


def count_up(label, target, suffix="", ms=700):
    obj  = _KpiAnim(label, suffix)
    anim = QPropertyAnimation(obj, b"value")
    anim.setDuration(ms)
    anim.setStartValue(0.0)
    anim.setEndValue(float(target))
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    label._anim = anim
    label._obj  = obj


# ─────────────────────────────────────────────────────────────
#  Helpers UI
# ─────────────────────────────────────────────────────────────

def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background:{BORDER}; border:none;")
    return f


def _card():
    f = QFrame()
    f.setStyleSheet(CARD_STYLE)
    return f


def _lbl(text, size, bold=False, color=TXT_PRI):
    l = QLabel(text)
    w = QFont.Weight.Bold if bold else QFont.Weight.Normal
    l.setFont(QFont("Segoe UI", size, w))
    l.setStyleSheet(f"color:{color}; background:transparent; border:none;")
    return l


def _styled_plot(bg=BG_DEEP, height=220):
    """Crée un PlotWidget avec le style sombre cohérent."""
    plot = pg.PlotWidget()
    plot.setBackground(bg)
    plot.setMinimumHeight(height)
    plot.showGrid(x=True, y=True, alpha=0.08)
    plot.setMouseEnabled(x=False, y=False)
    plot.hideButtons()

    axis_pen  = pg.mkPen(color="#ffffff22", width=1)
    label_pen = pg.mkPen(color="#ffffff44")
    for axis in ("bottom", "left"):
        plot.getAxis(axis).setPen(axis_pen)
        plot.getAxis(axis).setTextPen(label_pen)
        plot.getAxis(axis).setStyle(tickFont=QFont("Segoe UI", 8))

    plot.getPlotItem().layout.setContentsMargins(4, 4, 12, 4)
    return plot


MONTHS_FR = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']


# ─────────────────────────────────────────────────────────────
#  Page Statistiques
# ─────────────────────────────────────────────────────────────

class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.setStyleSheet(f"background:{BG_PAGE};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none; background:transparent;}")

        container = QWidget()
        container.setStyleSheet("background:transparent;")
        self._lay = QVBoxLayout(container)
        self._lay.setSpacing(22)
        self._lay.setContentsMargins(32, 28, 32, 28)

        self._build_header()
        self._build_kpi_row()
        self._build_charts_row()
        self._build_bottom_row()

        self._lay.addStretch()
        scroll.setWidget(container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        self.refresh()

    # ── En-tête ──────────────────────────────────────────────
    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        col = QVBoxLayout()
        col.setSpacing(3)
        col.addWidget(_lbl("Statistiques & Analytiques", 24, bold=True))
        col.addWidget(_lbl("Vue d'ensemble de votre activité commerciale", 11, color=TXT_SEC))
        row.addLayout(col)
        row.addStretch()

        # Badge année courante
        year_badge = QLabel(str(datetime.now().year))
        year_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        year_badge.setStyleSheet(f"""
            background: rgba(59,130,246,0.15);
            color: {C_BLUE};
            border: 1px solid rgba(59,130,246,0.30);
            border-radius: 8px;
            padding: 4px 14px;
        """)
        row.addWidget(year_badge)

        btn = QPushButton("↻   Actualiser")
        btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        btn.setFixedHeight(38)
        btn.setFixedWidth(130)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{ background:{C_BLUE}; color:white; border:none;
                border-radius:10px; padding:0 18px; }}
            QPushButton:hover   {{ background:#2563EB; }}
            QPushButton:pressed {{ background:#1D4ED8; }}
        """)
        btn.clicked.connect(self.refresh)
        row.addWidget(btn)

        self._lay.addLayout(row)

    # ── Rangée KPI ───────────────────────────────────────────
    def _build_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        specs = [
            ("Chiffre d'Affaires", C_BLUE,   "💳", " DA"),
            ("Profit Net",         C_GREEN,  "📈", " DA"),
            ("Commandes",          C_AMBER,  "🛒", ""),
            ("Clients Actifs",     C_VIOLET, "👥", ""),
        ]

        self._kpi_cards = []
        for title, color, icon, suffix in specs:
            card = self._make_kpi(icon, title, color, suffix)
            row.addWidget(card)
            self._kpi_cards.append(card)

        self._lay.addLayout(row)

    def _make_kpi(self, icon, title, color, suffix):
        card = _card()
        card.setFixedHeight(118)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(6)

        # Ligne supérieure : badge + titre
        top = QHBoxLayout()
        badge = QLabel(icon)
        badge.setFont(QFont("Segoe UI", 13))
        badge.setFixedSize(34, 34)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background:{color}1A; border-radius:9px; border:none;")
        top.addWidget(badge)
        top.addSpacing(8)
        top.addWidget(_lbl(title, 10, color=TXT_SEC))
        top.addStretch()
        lay.addLayout(top)

        # Valeur
        val_lbl = _lbl("0", 26, bold=True, color=color)
        lay.addWidget(val_lbl)

        # Barre dégradée
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {color}, stop:1 transparent);
            border-radius:2px; border:none;
        """)
        lay.addWidget(bar)

        card.value_label = val_lbl
        card._suffix = suffix
        return card

    # ── Graphiques principaux ────────────────────────────────
    def _build_charts_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        # Ventes mensuelles (ligne + aire)
        sales_card, self.sales_chart = self._make_chart_card(
            "Évolution des Ventes", C_BLUE, 230)
        row.addWidget(sales_card, 3)

        # Profits mensuels (barres)
        profit_card, self.profit_chart = self._make_chart_card(
            "Profit Mensuel", C_GREEN, 230)
        row.addWidget(profit_card, 2)

        self._lay.addLayout(row)

    def _make_chart_card(self, title, accent, height):
        card = _card()
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(12)

        # En-tête carte
        hdr = QHBoxLayout()
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background:{accent}; border-radius:4px; border:none;")
        hdr.addWidget(dot)
        hdr.setAlignment(dot, Qt.AlignmentFlag.AlignVCenter)
        hdr.addSpacing(8)
        hdr.addWidget(_lbl(title, 12, bold=True))
        hdr.addStretch()
        lay.addLayout(hdr)
        lay.addWidget(_sep())

        plot = _styled_plot(height=height)
        lay.addWidget(plot)

        return card, plot

    # ── Rangée du bas : top produits + top clients + infos ───
    def _build_bottom_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        # Top 5 produits
        prod_card, self.products_chart = self._make_chart_card(
            "Top 5 Produits", C_AMBER, 200)
        row.addWidget(prod_card, 2)

        # Top 5 clients
        cli_card, self.clients_chart = self._make_chart_card(
            "Top 5 Clients", C_VIOLET, 200)
        row.addWidget(cli_card, 2)

        # Métriques rapides (colonne)
        info_col = QVBoxLayout()
        info_col.setSpacing(12)

        infos = [
            ("Stock Faible",  "0 produit",  C_RED,    "⚠️"),
            ("Panier Moyen",  "0 DA",       C_CYAN,   "💳"),
            ("Meilleur Jour", "—",          C_GREEN,  "📅"),
        ]
        self._info_cards = []
        for title, val, color, icon in infos:
            c = self._make_metric(icon, title, val, color)
            info_col.addWidget(c)
            self._info_cards.append(c)

        row.addLayout(info_col, 1)
        self._lay.addLayout(row)

    def _make_metric(self, icon, title, value, color):
        card = _card()
        card.setFixedHeight(88)

        lay = QHBoxLayout(card)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)

        badge = QLabel(icon)
        badge.setFont(QFont("Segoe UI", 16))
        badge.setFixedSize(38, 38)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background:{color}1A; border-radius:11px; border:none;")
        lay.addWidget(badge)

        txt = QVBoxLayout()
        txt.setSpacing(2)
        txt.addWidget(_lbl(title, 9, color=TXT_SEC))
        val_lbl = _lbl(value, 13, bold=True, color=color)
        txt.addWidget(val_lbl)
        lay.addLayout(txt)
        lay.addStretch()

        card.value_label = val_lbl
        return card

    # ─────────────────────────────────────────────────────────
    #  Chargement des données
    # ─────────────────────────────────────────────────────────

    def refresh(self):
        self._load_kpis()
        self._load_sales_chart()
        self._load_profit_chart()
        self._load_top_products()
        self._load_top_clients()
        self._load_quick_info()

    def _load_kpis(self):
        stats     = self.db.get_statistics() or {}
        sales     = float(stats.get("sales_total", 0))
        purchases = float(stats.get("purchases_total", 0))
        profit    = sales - purchases
        clients   = int(stats.get("total_clients", 0))
        orders    = int(stats.get("total_purchases", 0))

        pairs = [(sales, " DA"), (profit, " DA"), (float(orders), ""), (float(clients), "")]
        for card, (val, suf) in zip(self._kpi_cards, pairs):
            count_up(card.value_label, val, suf)

    def _load_sales_chart(self):
        self.sales_chart.clear()
        year = datetime.now().year
        data = self.db.get_sales_by_month(year) or []

        months = list(range(1, 13))
        values = [0.0] * 12
        for row in data:
            idx = int(row.get("month", 0)) - 1
            if 0 <= idx < 12:
                values[idx] = float(row.get("total", 0))

        pen   = pg.mkPen(color=C_BLUE, width=2.5)
        brush = pg.mkBrush(color=(*self._hex_rgb(C_BLUE), 35))
        self.sales_chart.plot(
            months, values,
            pen=pen, fillLevel=0, brush=brush,
            symbol='o', symbolSize=7,
            symbolBrush=C_BLUE, symbolPen=pg.mkPen(color=BG_CARD, width=2)
        )
        self.sales_chart.getAxis('bottom').setTicks(
            [list(zip(months, MONTHS_FR))])

    def _load_profit_chart(self):
        self.profit_chart.clear()
        year = datetime.now().year
        data = self.db.get_profit_by_month(year) or []

        months = list(range(1, 13))
        values = [0.0] * 12
        for row in data:
            idx = int(row.get("month", 0)) - 1
            if 0 <= idx < 12:
                values[idx] = float(row.get("profit", 0))

        # Barres vertes / rouges selon le signe
        for i, v in enumerate(values):
            color = C_GREEN if v >= 0 else C_RED
            bar = pg.BarGraphItem(
                x=[i + 1], height=[v], width=0.55,
                brush=pg.mkBrush(color + "CC"),
                pen=pg.mkPen(color, width=0)
            )
            self.profit_chart.addItem(bar)

        self.profit_chart.getAxis('bottom').setTicks(
            [list(zip(months, MONTHS_FR))])

    def _load_top_products(self):
        self.products_chart.clear()
        data = self.db.get_top_products(limit=5) or []
        if not data:
            return

        names  = [p.get("name", "")[:12] for p in data]
        values = [float(p.get("total_quantity", 0)) for p in data]

        for i, (v, c) in enumerate(zip(values, CHART_COLORS)):
            bar = pg.BarGraphItem(
                x=[i], height=[v], width=0.6,
                brush=pg.mkBrush(c + "CC"),
                pen=pg.mkPen(c, width=0)
            )
            self.products_chart.addItem(bar)

        self.products_chart.getAxis('bottom').setTicks(
            [list(zip(range(len(names)), names))])
        self.products_chart.setXRange(-0.5, len(values) - 0.5)

    def _load_top_clients(self):
        self.clients_chart.clear()
        data = self.db.get_top_clients(limit=5) or []
        if not data:
            return

        names  = [c.get("name", "")[:12] for c in data]
        values = [float(c.get("total_amount", 0)) for c in data]
        colors = [C_VIOLET, C_BLUE, C_CYAN, C_GREEN, C_AMBER]

        for i, (v, c) in enumerate(zip(values, colors)):
            bar = pg.BarGraphItem(
                x=[i], height=[v], width=0.6,
                brush=pg.mkBrush(c + "CC"),
                pen=pg.mkPen(c, width=0)
            )
            self.clients_chart.addItem(bar)

        self.clients_chart.getAxis('bottom').setTicks(
            [list(zip(range(len(names)), names))])
        self.clients_chart.setXRange(-0.5, len(values) - 0.5)

    def _load_quick_info(self):
        stats = self.db.get_statistics() or {}

        # Stock faible
        low = self.db.get_low_stock_products() or []
        n   = len(low)
        self._info_cards[0].value_label.setText(
            f"{n} produit{'s' if n != 1 else ''}")

        # Panier moyen
        sales_total = float(stats.get("sales_total", 0))
        num_sales   = max(int(stats.get("total_sales", 1)), 1)
        avg         = sales_total / num_sales
        self._info_cards[1].value_label.setText(f"{avg:,.0f} DA")

        # Meilleur jour
        self._info_cards[2].value_label.setText("Samedi")

    # ─────────────────────────────────────────────────────────
    #  Utilitaires
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _hex_rgb(hex_color):
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))