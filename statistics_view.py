# ─────────────────────────────────────────────────────────────
#  statistics_view.py — Version PRO (Design + Export + Charts)
#  AVEC TOUTES LES CORRECTIONS
# ─────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QSplitter, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QFileDialog, QMessageBox,
    QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation, QEasingCurve
import pyqtgraph as pg
import csv
from datetime import datetime
from db_manager import get_database


# ─────────────────────────────────────────────────────────────
#  Palette Colors
# ─────────────────────────────────────────────────────────────

BG_PAGE  = "#0F1117"
BG_CARD  = "#1A1D27"
BG_DEEP  = "#13151F"
BORDER   = "rgba(255,255,255,0.07)"
TXT_PRI  = "#F1F5F9"
TXT_SEC  = "rgba(255,255,255,0.45)"

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

MONTHS_FR = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']


# ─────────────────────────────────────────────────────────────
#  Counter Animation
# ─────────────────────────────────────────────────────────────

class _KpiAnim(QObject):
    def __init__(self, label, suffix=""):
        super().__init__()
        self._v = 0
        self.label = label
        self.suffix = suffix

    def _get(self):
        return self._v

    def _set(self, v):
        self._v = v
        self.label.setText(f"{v:,.0f}{self.suffix}")

    value = pyqtProperty(float, fget=_get, fset=_set)


def count_up(label, target, suffix="", ms=700):
    obj = _KpiAnim(label, suffix)
    anim = QPropertyAnimation(obj, b"value")
    anim.setDuration(ms)
    anim.setStartValue(0.0)
    anim.setEndValue(float(target))
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    label._anim = anim
    label._obj = obj


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
    l.setFont(QFont("Segoe UI", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color}; background:transparent;")
    return l

def _styled_plot(bg=BG_DEEP, height=220):
    plot = pg.PlotWidget()
    plot.setBackground(bg)
    plot.setMinimumHeight(height)
    plot.showGrid(x=True, y=True, alpha=0.08)
    plot.setMouseEnabled(x=False, y=False)
    plot.hideButtons()

    axis_pen  = pg.mkPen(color="#ffffff22", width=1)
    label_pen = pg.mkPen(color="#ffffff55")

    for axis in ("bottom", "left"):
        plot.getAxis(axis).setPen(axis_pen)
        plot.getAxis(axis).setTextPen(label_pen)
        plot.getAxis(axis).setStyle(tickFont=QFont("Segoe UI", 8))

    return plot


# ─────────────────────────────────────────────────────────────
#  Main Page Layout
# ─────────────────────────────────────────────────────────────

class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.db = get_database()
        self.setStyleSheet(f"background:{BG_PAGE};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent; border:none;")

        container = QWidget()
        container.setStyleSheet("background:transparent;")

        self._lay = QVBoxLayout(container)
        self._lay.setSpacing(22)
        self._lay.setContentsMargins(32, 28, 32, 28)

        # Initialisation des listes de cartes
        self._kpi_cards = []
        self._info_cards = []

        # Build Sections
        self._build_header()
        self._build_kpi_row()
        self._build_charts_row()
        self._build_bottom_row()

        self._lay.addStretch()
        scroll.setWidget(container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        # Load Data
        self.refresh()


    # ─────────────────────────────────────────────────────────
    #  Header
    # ─────────────────────────────────────────────────────────

    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        col = QVBoxLayout()
        col.addWidget(_lbl("Statistiques & Analytique", 24, bold=True))
        col.addWidget(_lbl("Vue générale de votre commerce", 11, color=TXT_SEC))
        row.addLayout(col)
        row.addStretch()

        # Année badge
        year_badge = QLabel(str(datetime.now().year))
        year_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        year_badge.setStyleSheet(f"""
            background: rgba(59,130,246,0.15);
            color: {C_BLUE};
            padding: 4px 14px;
            border-radius: 8px;
            border: 1px solid rgba(59,130,246,0.35);
        """)
        row.addWidget(year_badge)

        # Refresh Button
        btn = QPushButton("↻   Actualiser")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{C_BLUE}; color:white; border:none;
                border-radius:8px; padding:0 18px;
            }}
            QPushButton:hover {{ background:#2563EB; }}
        """)
        btn.clicked.connect(self.refresh)
        row.addWidget(btn)

        # Export CSV
        csv_btn = QPushButton("📥 Export CSV")
        csv_btn.setFixedHeight(36)
        csv_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        csv_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{C_GREEN};
                border:1.3px solid {C_GREEN};
                border-radius:8px;
                padding:0 14px;
            }}
        """)
        csv_btn.clicked.connect(self._export_csv)
        row.addWidget(csv_btn)

        # Export Excel Ultimate
        xls_btn = QPushButton("📊 Export Excel PRO+")
        xls_btn.setFixedHeight(36)
        xls_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        xls_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{C_AMBER};
                border:1.3px solid {C_AMBER};
                border-radius:8px;
                padding:0 14px;
            }}
        """)
        xls_btn.clicked.connect(self._export_excel_pro_plus)
        row.addWidget(xls_btn)

        # Export PDF
        pdf_btn = QPushButton("📄 Export PDF PRO")
        pdf_btn.setFixedHeight(36)
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{C_VIOLET};
                border:1.3px solid {C_VIOLET};
                border-radius:8px;
                padding:0 14px;
            }}
        """)
        pdf_btn.clicked.connect(self._export_pdf_pro)
        row.addWidget(pdf_btn)

        self._lay.addLayout(row)


    # ─────────────────────────────────────────────────────────
    # KPI Row
    # ─────────────────────────────────────────────────────────

    def _build_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        specs = [
            ("Chiffre d'Affaires", C_BLUE,   "💳", " DA"),
            ("Profit Net",         C_GREEN,  "📈", " DA"),
            ("Commandes",          C_AMBER,  "🛒", ""),
            ("Clients Actifs",     C_VIOLET, "👥", ""),
        ]

        for title, color, icon, suffix in specs:
            card = self._make_kpi(icon, title, color, suffix)
            row.addWidget(card)
            self._kpi_cards.append(card)

        self._lay.addLayout(row)


    def _make_kpi(self, icon, title, color, suffix):
        card = _card()
        card.setFixedHeight(120)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(8)

        top = QHBoxLayout()
        badge = QLabel(icon)
        badge.setFont(QFont("Segoe UI", 14))
        badge.setFixedSize(32, 32)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background:{color}22; border-radius:8px;")
        top.addWidget(badge)
        top.addSpacing(8)
        top.addWidget(_lbl(title, 10, color=TXT_SEC))
        top.addStretch()
        lay.addLayout(top)

        val_lbl = _lbl("0", 26, bold=True, color=color)
        lay.addWidget(val_lbl)

        card.value_label = val_lbl
        card._suffix = suffix

        return card


    # ─────────────────────────────────────────────────────────
    # Charts Row
    # ─────────────────────────────────────────────────────────

    def _build_charts_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        # Graphique des ventes
        sales_card, self.sales_chart = self._make_chart_card(
            "Évolution des Ventes", C_BLUE, 240
        )
        row.addWidget(sales_card, 3)

        # Graphique des profits
        profit_card, self.profit_chart = self._make_chart_card(
            "Profit Mensuel", C_GREEN, 240
        )
        row.addWidget(profit_card, 2)

        self._lay.addLayout(row)


    def _make_chart_card(self, title, accent, height):
        card = _card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(12)

        hdr = QHBoxLayout()
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background:{accent}; border-radius:4px;")
        hdr.addWidget(dot)
        hdr.addSpacing(8)
        hdr.addWidget(_lbl(title, 12, bold=True))
        hdr.addStretch()
        lay.addLayout(hdr)

        lay.addWidget(_sep())

        plot = _styled_plot(height=height)
        lay.addWidget(plot)

        return card, plot


    # ─────────────────────────────────────────────────────────
    # Bottom Row (avec Splitter)
    # ─────────────────────────────────────────────────────────

    def _build_bottom_row(self):
        """Version avec les KPI avancés"""
        
        # Splitter pour permettre le redimensionnement
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # =========================================================
        # Partie gauche : Graphiques (Top produits + Top clients)
        # =========================================================
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(12)
        
        # Top produits
        prod_card, self.products_chart = self._make_chart_card(
            "Top 5 Produits", C_AMBER, 180
        )
        left_layout.addWidget(prod_card)
        
        # Top clients
        cli_card, self.clients_chart = self._make_chart_card(
            "Top 5 Clients", C_VIOLET, 180
        )
        left_layout.addWidget(cli_card)
        
        splitter.addWidget(left_widget)
        
        # =========================================================
        # Partie droite : Infos rapides + KPI avancés
        # =========================================================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        
        # 1. Infos rapides
        infos_card = self._build_quick_info_card()
        right_layout.addWidget(infos_card)
        
        # 2. KPI avancés
        advanced_card = self._build_advanced_kpi_card()
        right_layout.addWidget(advanced_card)
        
        splitter.addWidget(right_widget)
        
        # Proportions initiales (60% - 40%)
        splitter.setSizes([600, 400])
        
        self._lay.addWidget(splitter)


    # ─────────────────────────────────────────────────────────
    # Quick Info Card
    # ─────────────────────────────────────────────────────────

    def _build_quick_info_card(self):
        """Construit la carte des infos rapides"""
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        
        # Titre
        title = QLabel("📌 Informations Rapides")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TXT_PRI};")
        layout.addWidget(title)
        
        # Grille d'infos
        infos = [
            ("Stock Faible", "0 produit", C_RED, "⚠️"),
            ("Panier Moyen", "0 DA", C_CYAN, "💳"),
            ("Meilleur Jour", "—", C_GREEN, "📅"),
        ]
        
        # Réinitialiser la liste des cartes d'info
        self._info_cards = []
        
        for info_title, val, color, icon in infos:
            info_widget = self._make_info_card(icon, info_title, val, color)
            layout.addWidget(info_widget)
            self._info_cards.append(info_widget)
        
        return card


    def _make_info_card(self, icon, title, value, color):
        """
        Crée une petite carte d'information pour les infos rapides
        """
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_DEEP};
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        card.setMinimumHeight(60)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # Icône
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 14))
        icon_label.setStyleSheet(f"color: {color};")
        layout.addWidget(icon_label)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 8))
        title_label.setStyleSheet(f"color: {TXT_SEC};")
        text_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        text_layout.addWidget(value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        card.value_label = value_label
        return card


    # ─────────────────────────────────────────────────────────
    # Advanced KPI Card
    # ─────────────────────────────────────────────────────────

    def _build_advanced_kpi_card(self):
        """Construit la carte des KPI avancés"""
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        
        # Titre
        title = QLabel("📊 KPI Avancés")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TXT_PRI};")
        layout.addWidget(title)
        
        # Grille 2x2 pour les métriques avancées
        grid = QGridLayout()
        grid.setSpacing(8)
        
        # Création des cartes de métriques
        self.avg_cart_card = self._create_metric_card("Panier Moyen", "0 DA", C_BLUE)
        self.margin_card = self._create_metric_card("Marge Globale", "0%", C_GREEN)
        self.turnover_card = self._create_metric_card("Rotation Stock", "0x", C_AMBER)
        self.conversion_card = self._create_metric_card("Conversion", "0%", C_VIOLET)
        
        grid.addWidget(self.avg_cart_card, 0, 0)
        grid.addWidget(self.margin_card, 0, 1)
        grid.addWidget(self.turnover_card, 1, 0)
        grid.addWidget(self.conversion_card, 1, 1)
        
        layout.addLayout(grid)
        
        # Ligne des produits les plus rentables
        profit_products_title = QLabel("💰 Top 5 Produits par Marge Brute")
        profit_products_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        profit_products_title.setStyleSheet(f"color: {TXT_PRI}; margin-top: 10px;")
        layout.addWidget(profit_products_title)

        # Tableau des produits rentables
        self.profit_products_table = QTableWidget(0, 4)
        self.profit_products_table.setHorizontalHeaderLabels([
            "Produit", "Qté vendue", "Marge Unitaire", "Marge Totale"
        ])
        self.profit_products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.profit_products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.profit_products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.profit_products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.profit_products_table.setColumnWidth(1, 80)
        self.profit_products_table.setColumnWidth(2, 120)
        self.profit_products_table.setColumnWidth(3, 120)
        
        self.profit_products_table.verticalHeader().setVisible(False)
        self.profit_products_table.setAlternatingRowColors(True)
        self.profit_products_table.setStyleSheet(f"""
            QTableWidget {{
                background: {BG_DEEP};
                alternate-background-color: rgba(255,255,255,0.03);
                color: {TXT_PRI};
                border: none;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background: {C_VIOLET}22;
                color: {C_VIOLET};
                font-size: 10px;
                font-weight: bold;
                padding: 6px;
                border: none;
                border-bottom: 2px solid {C_VIOLET};
            }}
        """)
        self.profit_products_table.setMinimumHeight(150)
        self.profit_products_table.setMaximumHeight(200)
        
        layout.addWidget(self.profit_products_table)
        
        return card


    def _create_metric_card(self, title, value, color):
        """Crée une petite carte de métrique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_DEEP};
                border-radius: 8px;
                border: 1px solid {color}33;
            }}
        """)
        card.setMinimumHeight(70)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        
        # Titre
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 9))
        title_lbl.setStyleSheet(f"color: {TXT_SEC}; border: none;")
        layout.addWidget(title_lbl)
        
        # Valeur
        value_lbl = QLabel(value)
        value_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        value_lbl.setStyleSheet(f"color: {color}; border: none;")
        layout.addWidget(value_lbl)
        
        card.value_label = value_lbl
        return card


    # ─────────────────────────────────────────────────────────
    # Refresh Data
    # ─────────────────────────────────────────────────────────

    def refresh(self):
        self._load_kpis()
        self._load_sales_chart()
        self._load_profit_chart()
        self._load_top_products()
        self._load_top_clients()
        self._load_quick_info()
        self._load_advanced_kpis()


    # ─────────────────────────────────────────────────────────
    # KPI Loader
    # ─────────────────────────────────────────────────────────

    def _load_kpis(self):
        stats = self.db.get_statistics() or {}

        sales_total = float(stats.get("sales_total", 0))
        purchases_total = float(stats.get("purchases_total", 0))
        profit = sales_total - purchases_total

        clients = int(stats.get("total_clients", 0))
        orders = int(stats.get("total_purchases", 0))

        values = [
            (sales_total, " DA"),
            (profit, " DA"),
            (orders, ""),
            (clients, "")
        ]

        for card, (val, suf) in zip(self._kpi_cards, values):
            count_up(card.value_label, val, suf)


    # ─────────────────────────────────────────────────────────
    # Graph: Ventes Mensuelles
    # ─────────────────────────────────────────────────────────

    def _load_sales_chart(self):
        self.sales_chart.clear()
        year = datetime.now().year
        data = self.db.get_sales_by_month(year) or []

        months = list(range(1,13))
        values = [0]*12

        for row in data:
            idx = int(row.get("month",0))-1
            if 0 <= idx < 12:
                values[idx] = float(row.get("total",0))

        pen = pg.mkPen(color=C_BLUE, width=2.5)
        brush = pg.mkBrush(color=(59,130,246,40))

        self.sales_chart.plot(
            months, values,
            pen=pen,
            fillLevel=0,
            brush=brush,
            symbol='o',
            symbolSize=6,
            symbolBrush=C_BLUE,
            symbolPen=pg.mkPen(color=BG_CARD, width=2)
        )
        self.sales_chart.getAxis('bottom').setTicks(
            [list(zip(months, MONTHS_FR))]
        )


    # ─────────────────────────────────────────────────────────
    # Graph: Profit Mensuel
    # ─────────────────────────────────────────────────────────

    def _load_profit_chart(self):
        self.profit_chart.clear()
        year = datetime.now().year
        data = self.db.get_profit_by_month(year) or []

        months = list(range(1,13))
        values = [0]*12

        for row in data:
            idx = int(row.get("month",0))-1
            if 0 <= idx < 12:
                values[idx] = float(row.get("profit",0))

        for i, v in enumerate(values):
            color = C_GREEN if v >= 0 else C_RED
            bar = pg.BarGraphItem(
                x=[i+1], height=[v], width=0.55,
                brush=pg.mkBrush(color+"AA"),
                pen=pg.mkPen(color, width=0)
            )
            self.profit_chart.addItem(bar)

        self.profit_chart.getAxis('bottom').setTicks(
            [list(zip(months, MONTHS_FR))]
        )


    # ─────────────────────────────────────────────────────────
    # Graph: Top Products
    # ─────────────────────────────────────────────────────────

    def _load_top_products(self):
        self.products_chart.clear()
        data = self.db.get_top_products(limit=5) or []

        if not data:
            return

        names  = [p["name"][:12] for p in data]
        values = [float(p["total_quantity"]) for p in data]

        for i, (v, c) in enumerate(zip(values, CHART_COLORS)):
            bar = pg.BarGraphItem(
                x=[i], height=[v], width=0.6,
                brush=pg.mkBrush(c+"CC"),
                pen=pg.mkPen(c, width=0)
            )
            self.products_chart.addItem(bar)

        self.products_chart.getAxis("bottom").setTicks(
            [list(zip(range(len(names)), names))]
        )
        self.products_chart.setXRange(-0.5, len(values)-0.5)


    # ─────────────────────────────────────────────────────────
    # Graph: Top Clients
    # ─────────────────────────────────────────────────────────

    def _load_top_clients(self):
        self.clients_chart.clear()
        data = self.db.get_top_clients(limit=5) or []

        if not data:
            return

        names  = [c["name"][:12] for c in data]
        values = [float(c["total_amount"]) for c in data]
        colors = [C_VIOLET, C_BLUE, C_CYAN, C_GREEN, C_AMBER]

        for i, (v, c) in enumerate(zip(values, colors)):
            bar = pg.BarGraphItem(
                x=[i], height=[v], width=0.6,
                brush=pg.mkBrush(c+"CC"),
                pen=pg.mkPen(c, width=0)
            )
            self.clients_chart.addItem(bar)

        self.clients_chart.getAxis("bottom").setTicks(
            [list(zip(range(len(names)), names))]
        )
        self.clients_chart.setXRange(-0.5, len(values)-0.5)


    # ─────────────────────────────────────────────────────────
    # Info rapide
    # ─────────────────────────────────────────────────────────

    def _load_quick_info(self):
        """Charge les informations rapides"""
        try:
            # Vérifier que _info_cards existe
            if not hasattr(self, '_info_cards') or not self._info_cards:
                print("⚠️ _info_cards n'est pas initialisé")
                return
                
            stats = self.db.get_statistics() or {}

            # Stock faible
            low = self.db.get_low_stock_products() or []
            n = len(low)
            self._info_cards[0].value_label.setText(
                f"{n} produit{'s' if n != 1 else ''}"
            )

            # Panier moyen
            sales_total = float(stats.get("sales_total", 0))
            num_sales = int(stats.get("total_sales", 1)) or 1
            avg = sales_total / num_sales
            self._info_cards[1].value_label.setText(f"{avg:,.0f} DA")

            # Meilleur jour
            best_day = self.db.get_best_day()
            self._info_cards[2].value_label.setText(best_day)
            
        except Exception as e:
            print(f"❌ Erreur dans _load_quick_info: {e}")


    # ─────────────────────────────────────────────────────────
    # Advanced KPIs
    # ─────────────────────────────────────────────────────────

    def _load_advanced_kpis(self):
        """Charge les données pour les KPI avancés"""
        try:
            # Panier moyen
            cart_data = self.db.get_average_cart_value()
            avg_cart = cart_data.get('avg_cart_value', 0)
            self.avg_cart_card.value_label.setText(f"{avg_cart:,.0f} DA")
            
            # Marge brute globale
            stats = self.db.get_statistics() or {}
            sales = float(stats.get("sales_total", 0))
            purchases = float(stats.get("purchases_total", 0))
            if sales > 0:
                global_margin = ((sales - purchases) / sales) * 100
            else:
                global_margin = 0
            self.margin_card.value_label.setText(f"{global_margin:.1f}%")
            
            # Rotation du stock
            turnover_data = self.db.get_inventory_turnover()
            turnover = turnover_data.get('turnover_rate', 0)
            self.turnover_card.value_label.setText(f"{turnover:.1f}x")
            
            # Taux de transformation (simplifié)
            conversion_data = self.db.get_conversion_rate()
            conversion_rate = conversion_data.get('conversion_rate', 0)
            self.conversion_card.value_label.setText(f"{conversion_rate:.1f}%")
            
            # Produits les plus rentables
            self._load_profitable_products()
            
        except Exception as e:
            print(f"Erreur chargement KPI avancés: {e}")


    def _load_profitable_products(self):
        """Charge le tableau des produits les plus rentables"""
        try:
            products = self.db.get_most_profitable_products(limit=5)
            self.profit_products_table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # Nom du produit
                name_item = QTableWidgetItem(product['name'][:30])
                name_item.setToolTip(product['name'])
                self.profit_products_table.setItem(row, 0, name_item)
                
                # Quantité vendue
                qty_item = QTableWidgetItem(str(product['quantity_sold']))
                qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.profit_products_table.setItem(row, 1, qty_item)
                
                # Marge unitaire
                unit_margin = product['selling_price'] - product['purchase_price']
                margin_item = QTableWidgetItem(f"{unit_margin:,.0f} DA")
                margin_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                margin_item.setForeground(QColor(C_GREEN))
                self.profit_products_table.setItem(row, 2, margin_item)
                
                # Marge totale
                total_margin_item = QTableWidgetItem(f"{product['gross_margin']:,.0f} DA")
                total_margin_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                total_margin_item.setForeground(QColor(C_GREEN))
                total_margin_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                self.profit_products_table.setItem(row, 3, total_margin_item)
                
        except Exception as e:
            print(f"Erreur chargement produits rentables: {e}")


    # ─────────────────────────────────────────────────────────
    # Interactions
    # ─────────────────────────────────────────────────────────

    def _connect_metric_clicks(self):
        """Connecte les événements de clic sur les métriques"""
        self.avg_cart_card.mousePressEvent = lambda e: self._show_cart_details()
        self.margin_card.mousePressEvent = lambda e: self._show_margin_details()
        self.profit_products_table.doubleClicked.connect(self._show_product_profit_details)


    def _show_cart_details(self):
        """Affiche les détails du panier moyen"""
        cart_data = self.db.get_cart_value_by_period(days=30)
        details = (
            f"📊 Détails du Panier Moyen\n\n"
            f"Panier moyen (30j): {cart_data['avg_cart']:,.0f} DA\n"
            f"Nombre de ventes: {cart_data['num_sales']}\n"
            f"Période: {cart_data['period_days']} jours"
        )
        QMessageBox.information(self, "Panier Moyen", details)


    def _show_margin_details(self):
        """Affiche les détails de la marge globale"""
        stats = self.db.get_statistics() or {}
        sales = float(stats.get("sales_total", 0))
        purchases = float(stats.get("purchases_total", 0))
        profit = sales - purchases
        margin_pct = (profit / sales * 100) if sales > 0 else 0
        
        details = (
            f"📈 Détails de la Marge Globale\n\n"
            f"Chiffre d'affaires: {sales:,.0f} DA\n"
            f"Coût des achats: {purchases:,.0f} DA\n"
            f"Bénéfice brut: {profit:,.0f} DA\n"
            f"Taux de marge: {margin_pct:.1f}%"
        )
        QMessageBox.information(self, "Marge Globale", details)


    def _show_product_profit_details(self, index):
        """Affiche les détails de profit pour un produit sélectionné"""
        row = index.row()
        product_name = self.profit_products_table.item(row, 0).text()
        
        # Trouver le produit dans la base
        products = self.db.get_most_profitable_products(limit=20)
        product = next((p for p in products if p['name'].startswith(product_name)), None)
        
        if product:
            details = self.db.get_product_profit_details(product['id'])
            if details:
                msg = (
                    f"📈 Analyse de rentabilité: {details['name']}\n\n"
                    f"Prix achat: {details['purchase_price']:,.0f} DA\n"
                    f"Prix vente: {details['selling_price']:,.0f} DA\n"
                    f"Marge unitaire: {details['unit_margin']:,.0f} DA\n"
                    f"Taux de marge: {details['margin_percentage']:.1f}%\n\n"
                    f"Quantité vendue: {details['total_sold']}\n"
                    f"Marge totale générée: {details['total_margin']:,.0f} DA"
                )
                QMessageBox.information(self, "Rentabilité Produit", msg)


    # ─────────────────────────────────────────────────────────
    # Export CSV
    # ─────────────────────────────────────────────────────────

    def _export_csv(self):
        from datetime import datetime as dt

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter CSV",
            f"statistiques_{dt.now().strftime('%Y%m%d')}.csv",
            "Fichiers CSV (*.csv)"
        )
        if not path:
            return
        if not path.endswith(".csv"):
            path += ".csv"

        stats = self.db.get_statistics() or {}
        year  = dt.now().year

        MOIS = [
            "Janvier","Février","Mars","Avril","Mai","Juin",
            "Juillet","Août","Septembre","Octobre","Novembre","Décembre"
        ]

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=';')

                w.writerow(["=== KPI GLOBAUX ==="])
                w.writerow(["Indicateur", "Valeur"])
                w.writerow(["CA Total", stats.get("sales_total", 0)])
                w.writerow(["Achats Totaux", stats.get("purchases_total", 0)])
                w.writerow(["Profit Net", stats.get("profit", 0)])
                w.writerow(["Clients", stats.get("total_clients", 0)])
                w.writerow(["Produits", stats.get("total_products", 0)])
                w.writerow([])

                w.writerow([f"=== VENTES MENSUELLES {year} ==="])
                w.writerow(["Mois", "Nombre", "Montant"])

                monthly = {
                    int(r["month"]): r
                    for r in (self.db.get_sales_by_month(year) or [])
                }

                for m in range(1,13):
                    r = monthly.get(m, {"count":0, "total":0})
                    w.writerow([
                        MOIS[m-1],
                        r.get("count",0),
                        r.get("total",0)
                    ])

            QMessageBox.information(self,"Export OK",f"Export réussi :\n{path}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'exporter :\n{e}")


    # ======================================================================
    # EXPORT EXCEL PRO+ (Feuilles séparées + Pivot Table + Dégradé + Images)
    # ======================================================================

    def _export_excel_pro_plus(self):
        import tempfile, os
        import xlsxwriter
        import pyqtgraph.exporters as exporters

        # Choisir chemin sortie
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter Excel PRO+",
            "rapport_erp.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return

        # Dossier temporaire
        temp_dir = tempfile.mkdtemp()

        # Fonction sauvegarde graphique
        def save_chart(widget, filename):
            exporter = exporters.ImageExporter(widget.plotItem)
            exporter.export(filename)

        # Sauvegarde images
        img_sales   = os.path.join(temp_dir, "sales.png")
        img_profit  = os.path.join(temp_dir, "profit.png")
        img_prod    = os.path.join(temp_dir, "products.png")
        img_clients = os.path.join(temp_dir, "clients.png")

        save_chart(self.sales_chart, img_sales)
        save_chart(self.profit_chart, img_profit)
        save_chart(self.products_chart, img_prod)
        save_chart(self.clients_chart, img_clients)

        # Créer Excel
        workbook = xlsxwriter.Workbook(path)

        # Styles
        title_fmt = workbook.add_format({
            "bold": True, "font_size": 18,
            "align": "center", "valign": "vcenter"
        })
        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#3B82F6",
            "font_color": "white", "border": 1,
            "align": "center"
        })
        normal_fmt = workbook.add_format({"border": 1})

        # ==================================================================
        # FEUILLE PRINCIPALE (DASHBOARD)
        # ==================================================================

        dash = workbook.add_worksheet("Dashboard")

        dash.merge_range("A1:E1", "Rapport Statistique – ERP", title_fmt)

        # KPI
        dash.write_row("A3", ["KPI", "Valeur"], header_fmt)

        kpi_names = ["CA Total", "Profit Net", "Commandes", "Clients Actifs"]

        for i, card in enumerate(self._kpi_cards):
            dash.write(i+3, 0, kpi_names[i], normal_fmt)
            dash.write(i+3, 1, card.value_label.text(), normal_fmt)

        # Dégradé automatique
        dash.conditional_format("B4:B7", {
            "type": "2_color_scale",
            "min_color": "#DBEAFE",
            "max_color": "#3B82F6"
        })

        # ==================================================================
        # FEUILLES DES GRAPHIQUES (1 feuille = 1 graphique)
        # ==================================================================

        charts = [
            ("Ventes", img_sales),
            ("Profit", img_profit),
            ("Top Produits", img_prod),
            ("Top Clients", img_clients)
        ]

        for sheet_name, img in charts:
            ws = workbook.add_worksheet(sheet_name)
            ws.set_column("A:A", 55)
            ws.insert_image("A1", img, {"x_scale": 0.8, "y_scale": 0.8})

        # ==================================================================
        # FEUILLE TABLEAU CROISÉ DYNAMIQUE (PIVOT TABLE)
        # ==================================================================

        pivot_raw = workbook.add_worksheet("Données Brut")
        pivot_tab = workbook.add_worksheet("Pivot")

        # Charger données mensuelles
        year = datetime.now().year
        rows = self.db.get_sales_by_month(year) or []

        # Écrire données brutes
        pivot_raw.write_row(0,0,["Mois","Total"])

        r = 1
        for row in rows:
            pivot_raw.write(r,0, row.get("month",0))
            pivot_raw.write(r,1, row.get("total",0))
            r += 1

        data_range = f"'Données Brut'!A1:B{r}"

        # Créer un tableau (base pivot)
        pivot_tab.add_table(0,0, r, 3, {
            "data": data_range,
            "columns": [
                {"header":"Mois"},
                {"header":"Total"}
            ]
        })

        # ==================================================================
        # FIN — sauvegarder
        # ==================================================================

        workbook.close()
        QMessageBox.information(self, "Export OK", f"Excel PRO+ généré :\n{path}")


    # ======================================================================
    # EXPORT PDF PROFESSIONNEL (avec images HD)
    # ======================================================================

    def _export_pdf_pro(self):
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        import tempfile, os
        import pyqtgraph.exporters as exporters

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter PDF",
            "rapport_erp.pdf",
            "PDF Files (*.pdf)"
        )
        if not path:
            return

        temp_dir = tempfile.mkdtemp()

        # Export charts
        def save_chart(widget, filename):
            exporter = exporters.ImageExporter(widget.plotItem)
            exporter.export(filename)

        img_sales   = os.path.join(temp_dir, "sales.png")
        img_profit  = os.path.join(temp_dir, "profit.png")
        img_prod    = os.path.join(temp_dir, "prod.png")
        img_clients = os.path.join(temp_dir, "clients.png")

        save_chart(self.sales_chart, img_sales)
        save_chart(self.profit_chart, img_profit)
        save_chart(self.products_chart, img_prod)
        save_chart(self.clients_chart, img_clients)

        # Build PDF
        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("<b>Rapport ERP — Analyse Professionnelle</b>", styles["Title"]))
        story.append(Spacer(1, 12))

        graphs = [
            ("Évolution des Ventes", img_sales),
            ("Profit Mensuel", img_profit),
            ("Top Produits", img_prod),
            ("Top Clients", img_clients)
        ]

        for title, img in graphs:
            story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
            story.append(Image(img, width=16*cm, height=8*cm))
            story.append(Spacer(1, 12))

        doc.build(story)

        QMessageBox.information(self,"PDF OK",f"PDF professionnel généré :\n{path}")