# ─────────────────────────────────────────────────────────────
#  statistics_view.py — Version PRO (Design + Export + Charts)
#  AVEC LE MÊME STYLE QUE DASHBOARD
# ─────────────────────────────────────────────────────────────


from PyQt6.QtWidgets import (
    QSplitter, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QFileDialog, QMessageBox,
    QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem, QComboBox,
    QProgressBar
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import csv
import datetime as _dt
from datetime import datetime
from db_manager import get_database
from currency import fmt_da, fmt, currency_manager

# Styles inspirés du dashboard
COLORS = {
    'BG_PAGE': '#1E1E2E',
    'BG_CARD': '#252535',
    'BG_DEEP': '#16161F',
    'TXT_PRI': '#F0F4FF',
    'TXT_SEC': '#A0AACC',
    'primary': '#3B82F6',
    'secondary': '#A855F7',
    'success': '#22C55E',
    'warning': '#FBBF24',
    'danger': '#EF4444',
    'info': '#06B6D4',
    'blue': '#3B82F6',
    'green': '#22C55E',
    'amber': '#F59E0B',
    'violet': '#8B5CF6',
    'cyan': '#06B6D4',
    'red': '#EF4444'
}

C_BLUE = COLORS['blue']
C_GREEN = COLORS['green']
C_AMBER = COLORS['amber']
C_VIOLET = COLORS['violet']
C_CYAN = COLORS['cyan']
C_RED = COLORS['red']
BG_PAGE = COLORS['BG_PAGE']
BG_CARD = COLORS['BG_CARD']
BG_DEEP = COLORS['BG_DEEP']
TXT_PRI = COLORS['TXT_PRI']
TXT_SEC = COLORS['TXT_SEC']

MONTHS_FR = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
CHART_COLORS = [C_BLUE, C_GREEN, C_AMBER, C_VIOLET, C_CYAN]


# ─────────────────────────────────────────────────────────────
#  HELPERS (comme dans dashboard)
# ─────────────────────────────────────────────────────────────

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
    l.setFont(QFont("Segoe UI", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    c = color or TXT_PRI
    l.setStyleSheet(f"color:{c}; background:transparent; border:none; padding:0;")
    return l


def _card(name="card", border_color=""):
    """Carte avec fond sombre et bordure optionnelle."""
    f = QFrame()
    f.setObjectName(name)
    bdr = border_color or "rgba(255,255,255,0.08)"
    f.setStyleSheet(f"""
        QFrame#{name} {{
            background:{BG_CARD};
            border-radius:14px;
            border:1px solid {bdr};
        }}
    """)
    return f


def _icon_box(icon, color, size=32, icon_size=14):
    """Icône dans un QFrame carré arrondi."""
    frame = QFrame()
    frame.setFixedSize(size, size)
    frame.setStyleSheet(f"background:{color}28; border-radius:{size//4}px; border:none;")
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(0, 0, 0, 0)
    lbl = QLabel(icon)
    lbl.setFont(QFont("Segoe UI", icon_size))
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet("background:transparent; border:none;")
    lay.addWidget(lbl)
    return frame


def _styled_plot(height=200):
    """Crée un graphique stylisé."""
    plot = pg.PlotWidget()
    plot.setBackground(BG_DEEP)
    plot.setMinimumHeight(height)
    plot.setStyleSheet("border: none;")
    
    # Style des axes
    plot.getAxis('bottom').setPen(pg.mkPen(color=TXT_SEC))
    plot.getAxis('left').setPen(pg.mkPen(color=TXT_SEC))
    plot.getAxis('bottom').setTextPen(pg.mkPen(color=TXT_SEC))
    plot.getAxis('left').setTextPen(pg.mkPen(color=TXT_SEC))
    
    # Grille
    plot.showGrid(x=True, y=True, alpha=0.2)
    
    return plot


def count_up(label, target, suffix=""):
    """Animation simple sans classe complexe."""
    label.setText(f"{target:,.0f}{suffix}")


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
        scroll.setStyleSheet("QScrollArea{border:none; background:transparent;}")

        container = QWidget()
        container.setStyleSheet("background:transparent;")

        self._lay = QVBoxLayout(container)
        self._lay.setSpacing(16)
        self._lay.setContentsMargins(24, 18, 24, 20)

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

    # ─────────────────────────────────────────────────────────
    #  Header (style dashboard)
    # ─────────────────────────────────────────────────────────
    
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
        
    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        col = QVBoxLayout()
        col.setSpacing(2)
        title = QLabel("📊 Statistiques & Analytique")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{TXT_PRI}; background:transparent;")
        col.addWidget(title)
        
        subtitle = QLabel("Vue générale de votre commerce")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color:{TXT_SEC}; background:transparent;")
        col.addWidget(subtitle)
        row.addLayout(col)
        row.addStretch()

        # Sélecteur d'année dynamique
        self.year_combo = QComboBox()
        self.year_combo.setFixedHeight(36)
        self.year_combo.setFixedWidth(100)
        self.year_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.year_combo.setStyleSheet(f"""
            QComboBox {{
                background:rgba(59,130,246,0.15);
                color:{C_BLUE};
                border:1.5px solid {C_BLUE}88;
                border-radius:9px;
                padding:0 12px;
                font-size:13px;
                font-weight:bold;
            }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background:{BG_CARD};
                color:{C_BLUE};
                selection-background-color:rgba(59,130,246,0.25);
                border:1px solid rgba(59,130,246,0.35);
            }}
        """)
        self._populate_years()
        self.year_combo.currentTextChanged.connect(self.refresh)
        row.addWidget(self.year_combo)

        # Export CSV
        csv_btn = QPushButton("📥 Export CSV")
        csv_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        csv_btn.setFixedHeight(36)
        csv_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        csv_btn.setStyleSheet(f"""
            QPushButton {{
                background:rgba(34,197,94,0.15);
                color:{C_GREEN};
                border:1.5px solid {C_GREEN}88;
                border-radius:9px;
                padding:0 14px;
            }}
            QPushButton:hover {{ background:rgba(34,197,94,0.28); }}
            QPushButton:pressed {{ background:rgba(34,197,94,0.42); }}
        """)
        csv_btn.clicked.connect(self._export_csv)
        row.addWidget(csv_btn)

        # Export Excel Ultimate
        xls_btn = QPushButton("📊 Export Excel PRO+")
        xls_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        xls_btn.setFixedHeight(36)
        xls_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        xls_btn.setStyleSheet(f"""
            QPushButton {{
                background:rgba(245,158,11,0.15);
                color:{C_AMBER};
                border:1.5px solid {C_AMBER}88;
                border-radius:9px;
                padding:0 14px;
            }}
            QPushButton:hover {{ background:rgba(245,158,11,0.28); }}
            QPushButton:pressed {{ background:rgba(245,158,11,0.42); }}
        """)
        xls_btn.clicked.connect(self._export_excel_pro_plus)
        row.addWidget(xls_btn)

        # Export PDF
        pdf_btn = QPushButton("📄 Export PDF PRO")
        pdf_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        pdf_btn.setFixedHeight(36)
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.setStyleSheet(f"""
            QPushButton {{
                background:rgba(139,92,246,0.15);
                color:{C_VIOLET};
                border:1.5px solid {C_VIOLET}88;
                border-radius:9px;
                padding:0 14px;
            }}
            QPushButton:hover {{ background:rgba(139,92,246,0.28); }}
            QPushButton:pressed {{ background:rgba(139,92,246,0.42); }}
        """)
        pdf_btn.clicked.connect(self._export_pdf_pro)
        row.addWidget(pdf_btn)

        self._lay.addLayout(row)
        self._lay.addSpacing(8)

    # ─────────────────────────────────────────────────────────
    #  KPI Row (style dashboard)
    # ─────────────────────────────────────────────────────────

    def _build_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        specs = [
            ("Chiffre d'Affaires", C_BLUE, "💳", f" {currency_manager.primary.symbol}"),
            ("Profit Net", C_GREEN, "📈", f" {currency_manager.primary.symbol}"),
            ("Commandes", C_AMBER, "🛒", ""),
            ("Clients Actifs", C_VIOLET, "👥", ""),
        ]

        for title, color, icon, suffix in specs:
            card = self._make_kpi(icon, title, color, suffix)
            row.addWidget(card)
            self._kpi_cards.append(card)

        self._lay.addLayout(row)

    def _make_kpi(self, icon, title, color, suffix):
        card = QFrame()
        card.setObjectName("kpi")
        card.setFixedHeight(118)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(f"""
            QFrame#kpi {{
                background:{BG_CARD};
                border-radius:14px;
                border:1px solid {color}44;
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
        title_lbl.setStyleSheet(f"color:{TXT_SEC}; background:transparent; border:none;")
        top.addWidget(title_lbl)
        top.addStretch()
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
        card._suffix = suffix

        return card

    # ─────────────────────────────────────────────────────────
    #  Charts Row (style dashboard)
    # ─────────────────────────────────────────────────────────

    def _build_charts_row(self):
        row = QHBoxLayout()
        row.setSpacing(14)

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
        hdr.addWidget(_lbl(title, 13, bold=True))
        hdr.addStretch()
        lay.addLayout(hdr)

        lay.addWidget(_sep())

        plot = _styled_plot(height=height)
        lay.addWidget(plot)

        return card, plot

    # ─────────────────────────────────────────────────────────
    #  Bottom Row (style dashboard)
    # ─────────────────────────────────────────────────────────

    def _build_bottom_row(self):
        """Version avec les KPI avancés style dashboard"""
        
        # Splitter pour permettre le redimensionnement
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: rgba(255,255,255,0.08); width: 1px; }")
        
        # =========================================================
        # Partie gauche : Graphiques (Top produits + Top clients)
        # =========================================================
        left_widget = QWidget()
        left_widget.setStyleSheet("background:transparent;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(14)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
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
        right_widget.setStyleSheet("background:transparent;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(14)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
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
    #  Quick Info Card (style dashboard)
    # ─────────────────────────────────────────────────────────

    def _build_quick_info_card(self):
        """
        Carte Infos Rapides avec sélecteur de période dynamique :
          • Semaine  → jours (Lundi … Dimanche)
          • Mois     → semaines (Sem. 1 … Sem. 4/5)
          • Année    → mois (Jan … Déc)
        """
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        # ── En-tête : titre + sélecteur de période ────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(8)
        hdr.addWidget(_lbl("⚡  Infos Rapides", 13, bold=True))
        hdr.addStretch()

        self._period_combo = QComboBox()
        self._period_combo.addItems(["📅  Semaine", "🗓  Mois", "📆  Année"])
        self._period_combo.setFixedHeight(28)
        self._period_combo.setFixedWidth(120)
        self._period_combo.setStyleSheet(f"""
            QComboBox {{
                background:{BG_DEEP};
                color:{TXT_PRI};
                border:1px solid {C_BLUE}55;
                border-radius:8px;
                padding:2px 10px;
                font-size:11px;
                font-family:'Segoe UI';
            }}
            QComboBox:focus {{ border:1px solid {C_BLUE}; }}
            QComboBox::drop-down {{ border:none; width:22px; }}
            QComboBox QAbstractItemView {{
                background:{BG_CARD};
                color:{TXT_PRI};
                selection-background-color:{C_BLUE}44;
                border:1px solid {C_BLUE}33;
                font-size:11px;
            }}
        """)
        self._period_combo.currentIndexChanged.connect(self._load_period_info)
        hdr.addWidget(self._period_combo)
        layout.addLayout(hdr)

        # ── Sous-titre dynamique (plage de dates) ─────────────
        self._period_subtitle_lbl = QLabel("")
        self._period_subtitle_lbl.setFont(QFont("Segoe UI", 9))
        self._period_subtitle_lbl.setStyleSheet(
            f"color:{TXT_SEC}; background:transparent; border:none;")
        layout.addWidget(self._period_subtitle_lbl)

        layout.addWidget(_sep())
        layout.addSpacing(4)

        # ── Zone des barres (remplie dynamiquement) ───────────
        self._period_bars_layout = QVBoxLayout()
        self._period_bars_layout.setSpacing(4)
        layout.addLayout(self._period_bars_layout)

        # ── Total de la période ───────────────────────────────
        layout.addSpacing(4)
        self._period_total_lbl = QLabel("")
        self._period_total_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._period_total_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._period_total_lbl.setStyleSheet(
            f"color:{C_GREEN}; background:transparent; border:none;")
        layout.addWidget(self._period_total_lbl)

        layout.addWidget(_sep())
        layout.addSpacing(6)

        # ── Section complémentaire : 4 métriques fixes ────────
        hdr2 = QHBoxLayout()
        hdr2.addWidget(_lbl("📌 Métriques Clés", 11, bold=True, color=TXT_SEC))
        hdr2.addStretch()
        layout.addLayout(hdr2)
        layout.addSpacing(6)

        infos = [
            ("Stock Faible",         "0 produit", C_RED,   "⚠️"),
            ("Panier Moyen",         "0 DA",      C_CYAN,  "💳"),
            ("Meilleur Jour Ventes", "—",         C_GREEN, "📅"),
            ("Meilleur Jour CA",     "—",         C_AMBER, "💰"),
        ]
        self._info_cards = []
        for info_title, val, color, icon in infos:
            w = self._make_info_card(icon, info_title, val, color)
            layout.addWidget(w)
            self._info_cards.append(w)

        return card

    def _make_info_card(self, icon, title, value, color):
        """Crée une petite carte d'information style dashboard"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{BG_DEEP};
                border-radius:10px;
                border:1px solid {color}33;
            }}
        """)
        card.setMinimumHeight(70)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        # Icône
        icon_frame = QFrame()
        icon_frame.setFixedSize(36, 36)
        icon_frame.setStyleSheet(f"background:{color}22; border-radius:10px; border:none;")
        icon_lay = QVBoxLayout(icon_frame)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 14))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"color:{color}; background:transparent;")
        icon_lay.addWidget(icon_label)
        layout.addWidget(icon_frame)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet(f"color:{TXT_SEC}; background:transparent;")
        text_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color:{color}; background:transparent;")
        text_layout.addWidget(value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        card.value_label = value_label
        return card

    # ─────────────────────────────────────────────────────────
    #  Advanced KPI Card (style dashboard)
    # ─────────────────────────────────────────────────────────

    def _build_advanced_kpi_card(self):
        """Construit la carte des KPI avancés style dashboard"""
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)
        
        # Titre
        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("📊 KPI Avancés", 13, bold=True))
        hdr.addStretch()
        layout.addLayout(hdr)
        layout.addWidget(_sep())
        layout.addSpacing(8)
        
        # Grille 2x2 pour les métriques avancées
        grid = QGridLayout()
        grid.setSpacing(10)
        
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
        layout.addSpacing(8)
        
        # Ligne des produits les plus rentables
        profit_title = QHBoxLayout()
        profit_title.addWidget(_lbl("💰 Top 5 Produits par Marge Brute", 11, bold=True, color=TXT_SEC))
        profit_title.addStretch()
        layout.addLayout(profit_title)
        layout.addSpacing(4)

        # Tableau des produits rentables
        self.profit_products_table = QTableWidget(0, 4)
        self.profit_products_table.setHorizontalHeaderLabels([
            "Produit", "Qté vendue", "Marge Unitaire", "Marge Totale"
        ])
        
        hv = self.profit_products_table.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hv.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hv.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hv.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.profit_products_table.setColumnWidth(1, 80)
        self.profit_products_table.setColumnWidth(2, 120)
        self.profit_products_table.setColumnWidth(3, 120)

        self.profit_products_table.verticalHeader().setVisible(False)
        self.profit_products_table.setAlternatingRowColors(True)
        self.profit_products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.profit_products_table.setShowGrid(False)
        self.profit_products_table.setStyleSheet(f"""
            QTableWidget {{
                background:transparent;
                alternate-background-color:rgba(255,255,255,0.03);
                color:{TXT_PRI};
                border:none;
                font-size:11px;
            }}
            QHeaderView::section {{
                background:{BG_DEEP};
                color:{C_VIOLET};
                font-size:10px;
                font-weight:bold;
                padding:8px 6px;
                border:none;
                border-bottom:2px solid {C_VIOLET};
            }}
            QTableWidget::item {{
                padding:8px 6px;
                border-bottom:1px solid rgba(255,255,255,0.04);
            }}
            QTableWidget::item:selected {{
                background:rgba(139,92,246,0.22);
                color:white;
            }}
        """)
        self.profit_products_table.setMinimumHeight(150)
        self.profit_products_table.setMaximumHeight(200)
        
        layout.addWidget(self.profit_products_table)
        
        return card

    def _create_metric_card(self, title, value, color):
        """Crée une petite carte de métrique style dashboard"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{BG_DEEP};
                border-radius:12px;
                border:1px solid {color}44;
            }}
        """)
        card.setMinimumHeight(80)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)
        
        # Titre
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 10))
        title_lbl.setStyleSheet(f"color:{TXT_SEC}; border: none;")
        layout.addWidget(title_lbl)
        
        # Valeur
        value_lbl = QLabel(value)
        value_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        value_lbl.setStyleSheet(f"color:{color}; border: none;")
        layout.addWidget(value_lbl)
        
        card.value_label = value_lbl
        return card

    # ─────────────────────────────────────────────────────────
    #  Gestion de l'année sélectionnée
    # ─────────────────────────────────────────────────────────

    def _populate_years(self):
        """Remplit le ComboBox avec toutes les années présentes en BDD."""
        years = []
        try:
            self.db.cursor.execute("""
                SELECT DISTINCT substr(sale_date, 1, 4) as yr
                FROM sales
                WHERE sale_date IS NOT NULL
                  AND length(sale_date) >= 4
                ORDER BY yr DESC
            """)
            for row in self.db.cursor.fetchall():
                try:
                    yr = row['yr'] if isinstance(row, dict) else row[0]
                    if yr and len(str(yr).strip()) == 4 and str(yr).strip().isdigit():
                        years.append(str(yr).strip())
                except Exception:
                    pass
        except Exception as e:
            print(f"⚠️ _populate_years erreur: {e}")

        current_year = str(datetime.now().year)
        if current_year not in years:
            years.insert(0, current_year)

        seen, unique_years = set(), []
        for y in years:
            if y not in seen:
                seen.add(y)
                unique_years.append(y)

        current_selection = self.year_combo.currentText() if self.year_combo.count() > 0 else current_year

        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        for y in unique_years:
            self.year_combo.addItem(y)

        idx = self.year_combo.findText(current_selection)
        if idx < 0:
            idx = self.year_combo.findText(current_year)
        self.year_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.year_combo.blockSignals(False)

    def _get_year(self):
        """Retourne l'année sélectionnée dans le ComboBox."""
        try:
            return int(self.year_combo.currentText())
        except (ValueError, AttributeError):
            return datetime.now().year

    # ─────────────────────────────────────────────────────────
    #  Refresh Data
    # ─────────────────────────────────────────────────────────

    def refresh(self):
        self._populate_years()
        self._load_kpis()
        self._load_sales_chart()
        self._load_profit_chart()
        self._load_top_products()
        self._load_top_clients()
        self._load_period_info()      # ← barres dynamiques par période
        self._load_quick_info()       # ← 4 métriques fixes (stock, panier, etc.)
        self._load_advanced_kpis()

    # ─────────────────────────────────────────────────────────
    #  KPI Loader
    # ─────────────────────────────────────────────────────────

    def _load_kpis(self):
        stats = self.db.get_statistics(year=self._get_year()) or {}

        sales_total = float(stats.get("sales_total", 0))
        purchases_total = float(stats.get("purchases_total", 0))
        profit = sales_total - purchases_total

        clients = int(stats.get("total_clients", 0))
        orders = int(stats.get("total_purchases", 0))

        values = [
            (sales_total, f" {currency_manager.primary.symbol}"),
            (profit, f" {currency_manager.primary.symbol}"),
            (orders, ""),
            (clients, "")
        ]

        for card, (val, suf) in zip(self._kpi_cards, values):
            count_up(card.value_label, val, suf)

    # ─────────────────────────────────────────────────────────
    #  Graph: Ventes Mensuelles
    # ─────────────────────────────────────────────────────────

    def _load_sales_chart(self):
        self.sales_chart.clear()
        year = self._get_year()
        data = self.db.get_sales_by_month(year) or []

        months = list(range(1, 13))
        values = [0] * 12

        for row in data:
            idx = int(row.get("month", 0)) - 1
            if 0 <= idx < 12:
                values[idx] = float(row.get("total", 0))

        pen = pg.mkPen(color=C_BLUE, width=2.5)
        brush = pg.mkBrush(color=(59, 130, 246, 40))

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
        self.sales_chart.getAxis('bottom').setTicks([list(zip(months, MONTHS_FR))])

    # ─────────────────────────────────────────────────────────
    #  Graph: Profit Mensuel
    # ─────────────────────────────────────────────────────────

    def _load_profit_chart(self):
        self.profit_chart.clear()
        year = self._get_year()
        data = self.db.get_profit_by_month(year) or []

        months = list(range(1, 13))
        values = [0] * 12

        for row in data:
            idx = int(row.get("month", 0)) - 1
            if 0 <= idx < 12:
                values[idx] = float(row.get("profit", 0))

        for i, v in enumerate(values):
            color = C_GREEN if v >= 0 else C_RED
            bar = pg.BarGraphItem(
                x=[i + 1], height=[v], width=0.55,
                brush=pg.mkBrush(color + "AA"),
                pen=pg.mkPen(color, width=0)
            )
            self.profit_chart.addItem(bar)

        self.profit_chart.getAxis('bottom').setTicks([list(zip(months, MONTHS_FR))])

    # ─────────────────────────────────────────────────────────
    #  Graph: Top Products
    # ─────────────────────────────────────────────────────────

    def _load_top_products(self):
        self.products_chart.clear()
        data = self.db.get_top_products(limit=5, year=self._get_year()) or []

        if not data:
            return

        names = [p["name"][:12] for p in data]
        values = [float(p["total_quantity"]) for p in data]

        for i, (v, c) in enumerate(zip(values, CHART_COLORS)):
            bar = pg.BarGraphItem(
                x=[i], height=[v], width=0.6,
                brush=pg.mkBrush(c + "CC"),
                pen=pg.mkPen(c, width=0)
            )
            self.products_chart.addItem(bar)

        self.products_chart.getAxis("bottom").setTicks([list(zip(range(len(names)), names))])
        self.products_chart.setXRange(-0.5, len(values) - 0.5)

    # ─────────────────────────────────────────────────────────
    #  Graph: Top Clients
    # ─────────────────────────────────────────────────────────

    def _load_top_clients(self):
        self.clients_chart.clear()
        data = self.db.get_top_clients(limit=5, year=self._get_year()) or []

        if not data:
            return

        names = [c["name"][:12] for c in data]
        values = [float(c["total_amount"]) for c in data]
        colors = [C_VIOLET, C_BLUE, C_CYAN, C_GREEN, C_AMBER]

        for i, (v, c) in enumerate(zip(values, colors)):
            bar = pg.BarGraphItem(
                x=[i], height=[v], width=0.6,
                brush=pg.mkBrush(c + "CC"),
                pen=pg.mkPen(c, width=0)
            )
            self.clients_chart.addItem(bar)

        self.clients_chart.getAxis("bottom").setTicks([list(zip(range(len(names)), names))])
        self.clients_chart.setXRange(-0.5, len(values) - 0.5)

    # ─────────────────────────────────────────────────────────
    #  Chargement des barres par période (NOUVEAU)
    # ─────────────────────────────────────────────────────────

    def _load_period_info(self):
        """
        Charge les barres selon la période sélectionnée :
          0 = Semaine  → affiche chaque jour (Lun → Dim)
          1 = Mois     → affiche chaque semaine (Sem. 1 … 4/5)
          2 = Année    → affiche chaque mois (Jan → Déc)
        """
        _clear_layout(self._period_bars_layout)

        idx   = self._period_combo.currentIndex()
        today = _dt.date.today()
        sym   = currency_manager.primary.symbol

        BAR_COLORS = [C_BLUE, C_VIOLET, C_CYAN, C_GREEN, C_AMBER]

        # ══════════════════════════════════════════════════════
        #  SEMAINE — un point par jour
        # ══════════════════════════════════════════════════════
        if idx == 0:
            debut = today - _dt.timedelta(days=today.weekday())
            fin   = debut + _dt.timedelta(days=6)
            self._period_subtitle_lbl.setText(
                f"{debut.strftime('%d/%m')} — {fin.strftime('%d/%m/%Y')}")

            JOURS  = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
            JICONS = ["💼","💼","💼","💼","💼","🌤","🌤"]

            totaux, rows = [], []
            for i in range(7):
                d = debut + _dt.timedelta(days=i)
                try:
                    self.db.cursor.execute(
                        "SELECT COALESCE(SUM(total),0), COUNT(*) "
                        "FROM sales WHERE DATE(sale_date)=?", (str(d),))
                    r = self.db.cursor.fetchone()
                    total, nb = float(r[0] or 0), int(r[1] or 0)
                except Exception:
                    total, nb = 0.0, 0
                rows.append((JICONS[i]+" "+JOURS[i], d.strftime("%d/%m"),
                             total, nb, d == today))
                totaux.append(total)

            max_v = max(totaux, default=1) or 1
            for label, sublbl, total, nb, is_cur in rows:
                self._add_info_bar(
                    label, sublbl, total, nb, max_v, is_cur,
                    BAR_COLORS[0] if is_cur else BAR_COLORS[2], sym)

            grand = sum(totaux)
            self._period_total_lbl.setText(
                f"Total semaine : {fmt_da(grand, 0)}" if grand else "Aucune vente cette semaine")
            if not grand:
                self._period_total_lbl.setStyleSheet(
                    f"color:{TXT_SEC}; background:transparent; border:none; font-size:10px;")
            else:
                self._period_total_lbl.setStyleSheet(
                    f"color:{C_GREEN}; background:transparent; border:none; font-weight:bold;")

        # ══════════════════════════════════════════════════════
        #  MOIS — un point par semaine
        # ══════════════════════════════════════════════════════
        elif idx == 1:
            debut_mois = today.replace(day=1)
            if today.month == 12:
                fin_mois = _dt.date(today.year + 1, 1, 1) - _dt.timedelta(days=1)
            else:
                fin_mois = _dt.date(today.year, today.month + 1, 1) - _dt.timedelta(days=1)

            MOIS_FR = ["Janvier","Février","Mars","Avril","Mai","Juin",
                       "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
            self._period_subtitle_lbl.setText(
                f"{MOIS_FR[today.month-1]} {today.year}")

            semaines, c, num = [], debut_mois, 1
            while c <= fin_mois:
                d_deb = c
                d_fin = min(d_deb + _dt.timedelta(days=6 - d_deb.weekday()), fin_mois)
                semaines.append((num, d_deb, d_fin))
                c = d_fin + _dt.timedelta(days=1)
                num += 1

            totaux, rows = [], []
            for num, d_deb, d_fin in semaines:
                try:
                    self.db.cursor.execute(
                        "SELECT COALESCE(SUM(total),0), COUNT(*) "
                        "FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?",
                        (str(d_deb), str(d_fin)))
                    r = self.db.cursor.fetchone()
                    total, nb = float(r[0] or 0), int(r[1] or 0)
                except Exception:
                    total, nb = 0.0, 0
                is_cur = (d_deb <= today <= d_fin)
                rows.append((f"Sem. {num}",
                             f"{d_deb.strftime('%d/%m')} → {d_fin.strftime('%d/%m')}",
                             total, nb, is_cur, (num-1) % len(BAR_COLORS)))
                totaux.append(total)

            max_v = max(totaux, default=1) or 1
            for label, sublbl, total, nb, is_cur, ci in rows:
                self._add_info_bar(
                    label, sublbl, total, nb, max_v, is_cur,
                    BAR_COLORS[0] if is_cur else BAR_COLORS[ci], sym)

            grand = sum(totaux)
            self._period_total_lbl.setText(
                f"Total mois : {fmt_da(grand, 0)}" if grand else "Aucune vente ce mois")
            if not grand:
                self._period_total_lbl.setStyleSheet(
                    f"color:{TXT_SEC}; background:transparent; border:none; font-size:10px;")
            else:
                self._period_total_lbl.setStyleSheet(
                    f"color:{C_GREEN}; background:transparent; border:none; font-weight:bold;")

        # ══════════════════════════════════════════════════════
        #  ANNÉE — un point par mois
        # ══════════════════════════════════════════════════════
        elif idx == 2:
            annee = self._get_year()
            self._period_subtitle_lbl.setText(f"Année {annee}")

            MOIS_C = ["Jan","Fév","Mar","Avr","Mai","Jun",
                      "Jul","Aoû","Sep","Oct","Nov","Déc"]
            MOIS_I = ["❄️","❄️","🌸","🌸","🌺","☀️",
                      "☀️","🌤","🍂","🍂","🌧","❄️"]

            totaux, rows = [], []
            for m in range(1, 13):
                d_deb = _dt.date(annee, m, 1)
                d_fin = (_dt.date(annee+1, 1, 1) if m == 12
                         else _dt.date(annee, m+1, 1)) - _dt.timedelta(days=1)
                try:
                    self.db.cursor.execute(
                        "SELECT COALESCE(SUM(total),0), COUNT(*) "
                        "FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?",
                        (str(d_deb), str(d_fin)))
                    r = self.db.cursor.fetchone()
                    total, nb = float(r[0] or 0), int(r[1] or 0)
                except Exception:
                    total, nb = 0.0, 0
                is_cur = (m == today.month and annee == today.year)
                rows.append((f"{MOIS_I[m-1]} {MOIS_C[m-1]}",
                             str(annee), total, nb, is_cur,
                             (m-1) % len(BAR_COLORS)))
                totaux.append(total)

            max_v = max(totaux, default=1) or 1
            for label, sublbl, total, nb, is_cur, ci in rows:
                self._add_info_bar(
                    label, sublbl, total, nb, max_v, is_cur,
                    BAR_COLORS[0] if is_cur else BAR_COLORS[ci], sym)

            grand = sum(totaux)
            self._period_total_lbl.setText(
                f"Total année : {fmt_da(grand, 0)}" if grand else "Aucune vente cette année")
            if not grand:
                self._period_total_lbl.setStyleSheet(
                    f"color:{TXT_SEC}; background:transparent; border:none; font-size:10px;")
            else:
                self._period_total_lbl.setStyleSheet(
                    f"color:{C_GREEN}; background:transparent; border:none; font-weight:bold;")

    def _add_info_bar(self, label, sublabel, total, nb,
                      max_val, is_current, bar_color, sym):
        """Ajoute une ligne label + barre proportionnelle + montant."""
        row_frame = QFrame()
        row_frame.setStyleSheet(
            f"background:{'rgba(59,130,246,0.08)' if is_current else 'transparent'};"
            "border-radius:7px; border:none;")
        rh = QHBoxLayout(row_frame)
        rh.setContentsMargins(6, 2, 6, 2)
        rh.setSpacing(8)

        # Label
        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 10,
                          QFont.Weight.Bold if is_current else QFont.Weight.Normal))
        lbl.setFixedWidth(90)
        lbl.setStyleSheet(
            f"color:{'#F0F4FF' if is_current else TXT_SEC}; "
            "background:transparent; border:none;")
        rh.addWidget(lbl)

        # Barre
        bar = QProgressBar()
        bar.setRange(0, 1000)
        bar.setValue(int((total / max_val) * 1000) if total > 0 else 0)
        bar.setTextVisible(False)
        bar.setFixedHeight(10)

        if total == 0:
            chunk = "background:rgba(255,255,255,0.06); border-radius:4px;"
        elif is_current:
            chunk = (f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                     f"stop:0 {C_BLUE},stop:1 {C_VIOLET});"
                     "border-radius:4px;")
        else:
            chunk = (f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                     f"stop:0 {bar_color}99,stop:1 {bar_color}55);"
                     "border-radius:4px;")

        bar.setStyleSheet(f"""
            QProgressBar {{background:{BG_DEEP};border-radius:4px;border:none;}}
            QProgressBar::chunk {{ {chunk} }}
        """)
        rh.addWidget(bar, 1)

        # Montant
        amt_color = C_GREEN if total > 0 else "rgba(160,170,204,0.30)"
        amt = QLabel(fmt_da(total, 0) if total > 0 else "—")
        amt.setFont(QFont("Segoe UI", 10,
                          QFont.Weight.Bold if total > 0 else QFont.Weight.Normal))
        amt.setFixedWidth(110)
        amt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        amt.setStyleSheet(f"color:{amt_color}; background:transparent; border:none;")
        rh.addWidget(amt)

        # Nb ventes
        if nb > 0:
            nbl = QLabel(f"({nb})")
            nbl.setFont(QFont("Segoe UI", 9))
            nbl.setFixedWidth(32)
            nbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            nbl.setStyleSheet("color:rgba(160,170,204,0.55); background:transparent; border:none;")
            rh.addWidget(nbl)

        self._period_bars_layout.addWidget(row_frame)

    # ─────────────────────────────────────────────────────────
    #  Info rapide
    # ─────────────────────────────────────────────────────────

    def _load_quick_info(self):
        """Charge les informations rapides"""
        try:
            if not hasattr(self, '_info_cards') or not self._info_cards:
                return

            stats = self.db.get_statistics(year=self._get_year()) or {}

            # Stock faible
            low = self.db.get_low_stock_products() or []
            n = len(low)
            self._info_cards[0].value_label.setText(f"{n} produit{'s' if n != 1 else ''}")

            # Panier moyen
            sales_total = float(stats.get("sales_total", 0))
            num_sales = int(stats.get("total_sales", 1)) or 1
            avg = sales_total / num_sales
            self._info_cards[1].value_label.setText(f"{fmt_da(avg, 0)}")

            # Meilleur jour (ventes et recette)
            best_days = self.db.get_best_days()
            self._info_cards[2].value_label.setText(f"{best_days['sales_day']} ({best_days['sales_count']})")
            self._info_cards[3].value_label.setText(f"{best_days['revenue_day']} ({fmt_da(best_days['revenue_amount'], 0)})")

        except Exception as e:
            print(f"❌ Erreur dans _load_quick_info: {e}")

    # ─────────────────────────────────────────────────────────
    #  Advanced KPIs
    # ─────────────────────────────────────────────────────────

    def _load_advanced_kpis(self):
        """Charge les données pour les KPI avancés"""
        try:
            # Panier moyen
            cart_data = self.db.get_average_cart_value()
            avg_cart = cart_data.get('avg_cart_value', 0)
            self.avg_cart_card.value_label.setText(f"{fmt_da(avg_cart, 0)}")

            # Marge brute globale
            stats = self.db.get_statistics(year=self._get_year()) or {}
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

            # Taux de transformation
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
            products = self.db.get_most_profitable_products(limit=5, year=self._get_year())
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
                margin_item = QTableWidgetItem(f"{fmt_da(unit_margin, 0)}")
                margin_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                margin_item.setForeground(QColor(C_GREEN))
                self.profit_products_table.setItem(row, 2, margin_item)

                # Marge totale
                total_margin_item = QTableWidgetItem(f"{fmt_da(product['gross_margin'], 0)}")
                total_margin_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                total_margin_item.setForeground(QColor(C_GREEN))
                total_margin_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                self.profit_products_table.setItem(row, 3, total_margin_item)

        except Exception as e:
            print(f"Erreur chargement produits rentables: {e}")

    # ─────────────────────────────────────────────────────────
    #  Interactions
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
            f"Panier moyen (30j): {fmt_da(cart_data['avg_cart'], 0)}\n"
            f"Nombre de ventes: {cart_data['num_sales']}\n"
            f"Période: {cart_data['period_days']} jours"
        )
        QMessageBox.information(self, "Panier Moyen", details)

    def _show_margin_details(self):
        """Affiche les détails de la marge globale"""
        stats = self.db.get_statistics(year=self._get_year()) or {}
        sales = float(stats.get("sales_total", 0))
        purchases = float(stats.get("purchases_total", 0))
        profit = sales - purchases
        margin_pct = (profit / sales * 100) if sales > 0 else 0

        details = (
            f"📈 Détails de la Marge Globale\n\n"
            f"Chiffre d'affaires: {fmt_da(sales, 0)}\n"
            f"Coût des achats: {fmt_da(purchases, 0)}\n"
            f"Bénéfice brut: {fmt_da(profit, 0)}\n"
            f"Taux de marge: {margin_pct:.1f}%"
        )
        QMessageBox.information(self, "Marge Globale", details)

    def _show_product_profit_details(self, index):
        """Affiche les détails de profit pour un produit sélectionné"""
        row = index.row()
        product_name = self.profit_products_table.item(row, 0).text()

        products = self.db.get_most_profitable_products(limit=20, year=self._get_year())
        product = next((p for p in products if p['name'].startswith(product_name)), None)

        if product:
            details = self.db.get_product_profit_details(product['id'])
            if details:
                msg = (
                    f"📈 Analyse de rentabilité: {details['name']}\n\n"
                    f"Prix achat: {fmt_da(details['purchase_price'], 0)}\n"
                    f"Prix vente: {fmt_da(details['selling_price'], 0)}\n"
                    f"Marge unitaire: {fmt_da(details['unit_margin'], 0)}\n"
                    f"Taux de marge: {details['margin_percentage']:.1f}%\n\n"
                    f"Quantité vendue: {details['total_sold']}\n"
                    f"Marge totale générée: {fmt_da(details['total_margin'], 0)}"
                )
                QMessageBox.information(self, "Rentabilité Produit", msg)

    # ─────────────────────────────────────────────────────────
    #  Export CSV (avec style dashboard)
    # ─────────────────────────────────────────────────────────

    def _export_csv(self):
        from datetime import datetime as dt

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter CSV",
            f"rapport_statistiques_{dt.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "Fichiers CSV (*.csv)"
        )
        if not path:
            return
        if not path.endswith(".csv"):
            path += ".csv"

        stats = self.db.get_statistics(year=self._get_year()) or {}
        year = self._get_year()

        MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=';')

                w.writerow(["RAPPORT STATISTIQUE ERP"])
                w.writerow(["Généré le", dt.now().strftime("%d/%m/%Y à %H:%M:%S")])
                w.writerow(["Période", f"Année {year}"])
                w.writerow([])

                # KPI GLOBAUX
                w.writerow(["=== KPI GLOBAUX ==="])
                w.writerow(["Indicateur", "Valeur", "Unité"])
                w.writerow(["Chiffre d'Affaires Total", f"{stats.get('sales_total', 0):,.0f}", f"{currency_manager.primary.symbol}"])
                w.writerow(["Achats Totaux", f"{stats.get('purchases_total', 0):,.0f}", f"{currency_manager.primary.symbol}"])
                w.writerow(["Profit Net", f"{stats.get('profit', 0):,.0f}", f"{currency_manager.primary.symbol}"])

                sales_total = float(stats.get("sales_total", 0))
                purchases_total = float(stats.get("purchases_total", 0))
                margin_pct = (stats.get("profit", 0) / sales_total * 100) if sales_total > 0 else 0
                w.writerow(["Taux de Marge", f"{margin_pct:.1f}", "%"])

                w.writerow(["Nombre de Clients", stats.get("total_clients", 0), "clients"])
                w.writerow(["Nombre de Produits", stats.get("total_products", 0), "produits"])
                w.writerow(["Nombre de Ventes", stats.get("total_sales", 0), "transactions"])
                w.writerow(["Nombre d'Achats", stats.get("total_purchases", 0), "commandes"])
                w.writerow(["Valeur du Stock", f"{stats.get('stock_value', 0):,.0f}", f"{currency_manager.primary.symbol}"])
                w.writerow(["Produits en Stock Faible", stats.get("low_stock_count", 0), "produits"])
                w.writerow([])

                # STATISTIQUES AVANCÉES
                w.writerow(["=== STATISTIQUES AVANCÉES ==="])

                num_sales = int(stats.get("total_sales", 1)) or 1
                avg_cart = sales_total / num_sales if num_sales > 0 else 0
                w.writerow(["Panier Moyen", f"{avg_cart:,.0f}", f"{currency_manager.primary.symbol}"])

                best_days = self.db.get_best_days()
                w.writerow(["Meilleur Jour (Ventes)", f"{best_days['sales_day']} ({best_days['sales_count']} ventes)", ""])
                w.writerow(["Meilleur Jour (Recette)", f"{best_days['revenue_day']} ({fmt_da(best_days['revenue_amount'], 0)})", ""])

                w.writerow(["Meilleur Mois", stats.get("best_month", "—"), ""])
                w.writerow(["Croissance Mensuelle", f"{stats.get('growth_rate', 0):.1f}", "%"])
                w.writerow([])

                # VENTES MENSUELLES
                w.writerow([f"=== VENTES MENSUELLES {year} ==="])
                w.writerow(["Mois", "Nombre de Ventes", "Montant (DA)", "Panier Moyen"])

                monthly = {int(r["month"]): r for r in (self.db.get_sales_by_month(year) or [])}

                for m in range(1, 13):
                    r = monthly.get(m, {"count": 0, "total": 0})
                    count = r.get("count", 0)
                    total = r.get("total", 0)
                    avg = total / count if count > 0 else 0
                    w.writerow([MOIS[m - 1], count, f"{total:,.0f}", f"{avg:,.0f}"])
                w.writerow([])

                # PROFITS MENSUELS
                w.writerow([f"=== PROFITS MENSUELS {year} ==="])
                w.writerow(["Mois", "Profit (DA)"])

                profits = {int(r["month"]): r for r in (self.db.get_profit_by_month(year) or [])}

                for m in range(1, 13):
                    p = profits.get(m, {"profit": 0})
                    w.writerow([MOIS[m - 1], f"{p.get('profit', 0):,.0f}"])
                w.writerow([])

                # TOP 5 PRODUITS
                w.writerow(["=== TOP 5 PRODUITS LES PLUS VENDUS ==="])
                w.writerow(["Rang", "Produit", "Quantité Vendue", "Montant (DA)"])

                top_products = self.db.get_top_products(limit=5, year=self._get_year()) or []
                for idx, prod in enumerate(top_products, 1):
                    w.writerow([idx, prod.get("name", "—"), int(prod.get("total_quantity", 0)), f"{prod.get('total_sales', 0):,.0f}"])
                w.writerow([])

                # TOP 5 CLIENTS
                w.writerow(["=== TOP 5 MEILLEURS CLIENTS ==="])
                w.writerow(["Rang", "Nom Client", "Nombre de Ventes", "Montant Total (DA)"])

                top_clients = self.db.get_top_clients(limit=5, year=self._get_year()) or []
                for idx, client in enumerate(top_clients, 1):
                    w.writerow([idx, client.get("name", "—"), int(client.get("sale_count", 0)), f"{client.get('total_amount', 0):,.0f}"])
                w.writerow([])

                # TOP 5 PRODUITS PAR MARGE
                w.writerow(["=== TOP 5 PRODUITS PAR MARGE BRUTE ==="])
                w.writerow(["Rang", "Produit", "Quantité", "Marge Unitaire (DA)", "Marge Totale (DA)"])

                profitable = self.db.get_most_profitable_products(limit=5, year=self._get_year()) or []
                for idx, prod in enumerate(profitable, 1):
                    w.writerow([idx, prod.get("name", "—"), int(prod.get("qty_sold", 0)), f"{prod.get('unit_margin', 0):,.0f}", f"{prod.get('total_margin', 0):,.0f}"])

            QMessageBox.information(self, "Export CSV ✅", f"Rapport généré avec succès :\n\n{path}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur Export", f"Impossible d'exporter :\n{e}")

    # ─────────────────────────────────────────────────────────
    #  Export Excel PRO+ (avec style dashboard)
    # ─────────────────────────────────────────────────────────

    def _export_excel_pro_plus(self):
        import tempfile, os
        import xlsxwriter
        import pyqtgraph.exporters as exporters
        from datetime import datetime as dt

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter Excel PRO+",
            f"rapport_complet_{dt.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return

        temp_dir = tempfile.mkdtemp()

        def save_chart(widget, filename):
            try:
                exporter = exporters.ImageExporter(widget.plotItem)
                exporter.export(filename)
                return filename
            except:
                return None

        wb = xlsxwriter.Workbook(path)

        # FORMATS
        title_fmt = wb.add_format({"bold": True, "font_size": 14, "bg_color": "#1F2937", "font_color": "white", "align": "center", "valign": "vcenter", "border": 1})
        header_fmt = wb.add_format({"bold": True, "bg_color": "#3B82F6", "font_color": "white", "border": 1, "align": "center", "valign": "vcenter"})
        data_fmt = wb.add_format({"border": 1, "align": "left", "num_format": "#,##0.00"})
        number_fmt = wb.add_format({"border": 1, "align": "center", "num_format": "#,##0"})

        # FEUILLE 1: TABLEAU DE BORD (KPI)
        ws = wb.add_worksheet("📊 Dashboard")
        ws.set_column("A:A", 25)
        ws.set_column("B:D", 18)

        row = 0
        ws.merge_range(row, 0, row, 3, "TABLEAU DE BORD KPI", title_fmt)
        row += 1
        ws.write(row, 0, f"Généré le : {dt.now().strftime('%d/%m/%Y %H:%M')}")
        row += 2

        ws.write(row, 0, "Indicateur", header_fmt)
        ws.write(row, 1, "Valeur", header_fmt)
        ws.write(row, 2, "Unité", header_fmt)
        row += 1

        stats = self.db.get_statistics(year=self._get_year()) or {}
        sales_total = float(stats.get("sales_total", 0))
        purchases_total = float(stats.get("purchases_total", 0))
        profit = sales_total - purchases_total
        margin_pct = (profit / sales_total * 100) if sales_total > 0 else 0

        kpis = [
            ("Chiffre d'Affaires", sales_total, f"{currency_manager.primary.symbol}"),
            ("Achats Totaux", purchases_total, f"{currency_manager.primary.symbol}"),
            ("Profit Net", profit, f"{currency_manager.primary.symbol}"),
            ("Taux de Marge", margin_pct, "%"),
            ("Nombre Clients", stats.get("total_clients", 0), "clients"),
            ("Nombre Produits", stats.get("total_products", 0), "produits"),
            ("Total Ventes", stats.get("total_sales", 0), "transactions"),
            ("Valeur du Stock", stats.get("stock_value", 0), f"{currency_manager.primary.symbol}"),
        ]

        for kpi_name, value, unit in kpis:
            ws.write(row, 0, kpi_name, data_fmt)
            if unit == f"{currency_manager.primary.symbol}":
                ws.write(row, 1, value, data_fmt)
            elif unit == "%":
                ws.write(row, 1, value, number_fmt)
            else:
                ws.write(row, 1, value, number_fmt)
            ws.write(row, 2, unit, data_fmt)
            row += 1

        # FEUILLE 2: VENTES MENSUELLES
        ws = wb.add_worksheet("📈 Ventes Mensuelles")
        ws.set_column("A:A", 20)
        ws.set_column("B:E", 18)

        row = 0
        year = self._get_year()
        ws.merge_range(row, 0, row, 4, f"VENTES MENSUELLES {year}", title_fmt)
        row += 2

        ws.write(row, 0, "Mois", header_fmt)
        ws.write(row, 1, "Nombre Ventes", header_fmt)
        ws.write(row, 2, "Montant (DA)", header_fmt)
        ws.write(row, 3, "Panier Moyen", header_fmt)
        ws.write(row, 4, "Croissance %", header_fmt)
        row += 1

        MOIS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        monthly = {int(r["month"]): r for r in (self.db.get_sales_by_month(year) or [])}

        prev_total = 0
        for m in range(1, 13):
            r = monthly.get(m, {"count": 0, "total": 0})
            count = r.get("count", 0)
            total = r.get("total", 0)
            avg = total / count if count > 0 else 0
            growth = ((total - prev_total) / prev_total * 100) if prev_total > 0 else 0

            ws.write(row, 0, MOIS[m - 1], data_fmt)
            ws.write(row, 1, count, number_fmt)
            ws.write(row, 2, total, data_fmt)
            ws.write(row, 3, avg, data_fmt)
            ws.write(row, 4, growth, data_fmt)
            row += 1
            prev_total = total

        # FEUILLE 3: PROFITS MENSUELS
        ws = wb.add_worksheet("💰 Profits Mensuels")
        ws.set_column("A:A", 20)
        ws.set_column("B:B", 20)

        row = 0
        ws.merge_range(row, 0, row, 1, f"PROFITS MENSUELS {year}", title_fmt)
        row += 2

        ws.write(row, 0, "Mois", header_fmt)
        ws.write(row, 1, "Profit (DA)", header_fmt)
        row += 1

        profits = {int(r["month"]): r for r in (self.db.get_profit_by_month(year) or [])}
        for m in range(1, 13):
            p = profits.get(m, {"profit": 0})
            ws.write(row, 0, MOIS[m - 1], data_fmt)
            ws.write(row, 1, p.get("profit", 0), data_fmt)
            row += 1

        # FEUILLE 4: TOP PRODUITS
        ws = wb.add_worksheet("🏆 Top Produits")
        ws.set_column("A:A", 5)
        ws.set_column("B:B", 40)
        ws.set_column("C:D", 18)

        row = 0
        ws.merge_range(row, 0, row, 3, "TOP 10 PRODUITS LES PLUS VENDUS", title_fmt)
        row += 2

        ws.write(row, 0, "Rang", header_fmt)
        ws.write(row, 1, "Produit", header_fmt)
        ws.write(row, 2, "Quantité", header_fmt)
        ws.write(row, 3, "Montant (DA)", header_fmt)
        row += 1

        top_products = self.db.get_top_products(limit=10, year=self._get_year()) or []
        for idx, prod in enumerate(top_products, 1):
            ws.write(row, 0, idx, number_fmt)
            ws.write(row, 1, prod.get("name", "—"), data_fmt)
            ws.write(row, 2, int(prod.get("total_quantity", 0)), number_fmt)
            ws.write(row, 3, prod.get("total_sales", 0), data_fmt)
            row += 1

        # FEUILLE 5: TOP CLIENTS
        ws = wb.add_worksheet("👥 Top Clients")
        ws.set_column("A:A", 5)
        ws.set_column("B:B", 35)
        ws.set_column("C:D", 18)

        row = 0
        ws.merge_range(row, 0, row, 3, "TOP 10 MEILLEURS CLIENTS", title_fmt)
        row += 2

        ws.write(row, 0, "Rang", header_fmt)
        ws.write(row, 1, "Nom Client", header_fmt)
        ws.write(row, 2, "Nombre Ventes", header_fmt)
        ws.write(row, 3, "Montant Total (DA)", header_fmt)
        row += 1

        top_clients = self.db.get_top_clients(limit=10, year=self._get_year()) or []
        for idx, client in enumerate(top_clients, 1):
            ws.write(row, 0, idx, number_fmt)
            ws.write(row, 1, client.get("name", "—"), data_fmt)
            ws.write(row, 2, int(client.get("sale_count", 0)), number_fmt)
            ws.write(row, 3, client.get("total_amount", 0), data_fmt)
            row += 1

        # FEUILLE 6: PRODUITS RENTABLES
        ws = wb.add_worksheet("💎 Rentabilité")
        ws.set_column("A:A", 5)
        ws.set_column("B:B", 35)
        ws.set_column("C:E", 18)

        row = 0
        ws.merge_range(row, 0, row, 4, "TOP 10 PRODUITS PAR MARGE BRUTE", title_fmt)
        row += 2

        ws.write(row, 0, "Rang", header_fmt)
        ws.write(row, 1, "Produit", header_fmt)
        ws.write(row, 2, "Quantité", header_fmt)
        ws.write(row, 3, "Marge Unit. (DA)", header_fmt)
        ws.write(row, 4, "Marge Totale (DA)", header_fmt)
        row += 1

        profitable = self.db.get_most_profitable_products(limit=10, year=self._get_year()) or []
        for idx, prod in enumerate(profitable, 1):
            ws.write(row, 0, idx, number_fmt)
            ws.write(row, 1, prod.get("name", "—"), data_fmt)
            ws.write(row, 2, int(prod.get("qty_sold", 0)), number_fmt)
            ws.write(row, 3, prod.get("unit_margin", 0), data_fmt)
            ws.write(row, 4, prod.get("total_margin", 0), data_fmt)
            row += 1

        # FEUILLE 7: GRAPHIQUES
        try:
            img_sales = save_chart(self.sales_chart, os.path.join(temp_dir, "sales.png"))
            img_profit = save_chart(self.profit_chart, os.path.join(temp_dir, "profit.png"))
            img_prod = save_chart(self.products_chart, os.path.join(temp_dir, "products.png"))
            img_clients = save_chart(self.clients_chart, os.path.join(temp_dir, "clients.png"))

            charts_data = [("📊 Ventes", img_sales), ("💹 Profit", img_profit), ("📦 Produits", img_prod), ("🎯 Clients", img_clients)]

            for sheet_name, img in charts_data:
                if img:
                    ws = wb.add_worksheet(sheet_name)
                    ws.set_column("A:A", 60)
                    ws.insert_image("A1", img, {"x_scale": 0.7, "y_scale": 0.7})
        except:
            pass

        wb.close()
        QMessageBox.information(self, "Excel Complet ✅", f"Rapport complet généré avec succès !\n\n📄 Fichier : {path}")

    # ─────────────────────────────────────────────────────────
    #  Export PDF Professionnel (avec style dashboard)
    # ─────────────────────────────────────────────────────────

    def _export_pdf_pro(self):
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from datetime import datetime as dt
        import tempfile, os
        import pyqtgraph.exporters as exporters

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter PDF Détaillé",
            f"rapport_complet_{dt.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        if not path:
            return

        temp_dir = tempfile.mkdtemp()

        def save_chart(widget, filename):
            try:
                exporter = exporters.ImageExporter(widget.plotItem)
                exporter.export(filename)
                return filename
            except:
                return None

        img_sales = save_chart(self.sales_chart, os.path.join(temp_dir, "sales.png"))
        img_profit = save_chart(self.profit_chart, os.path.join(temp_dir, "profit.png"))
        img_prod = save_chart(self.products_chart, os.path.join(temp_dir, "prod.png"))
        img_clients = save_chart(self.clients_chart, os.path.join(temp_dir, "clients.png"))

        doc = SimpleDocTemplate(path, pagesize=A4, topMargin=1 * cm, bottomMargin=1 * cm, leftMargin=1.5 * cm, rightMargin=1.5 * cm)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1F2937'), spaceAfter=6, alignment=1, fontName='Helvetica-Bold')
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#3B82F6'), spaceAfter=6, spaceBefore=8, fontName='Helvetica-Bold')

        # PAGE 1: COUVERTURE
        story.append(Spacer(1, 2 * cm))
        story.append(Paragraph("📊 RAPPORT STATISTIQUE ERP", title_style))
        story.append(Paragraph("Analyse Complète et Détaillée", styles['Heading2']))
        story.append(Spacer(1, 1 * cm))

        date_text = dt.now().strftime("%d/%m/%Y à %H:%M:%S")
        year = self._get_year()
        story.append(Paragraph(f"<b>Généré le :</b> {date_text}", styles['Normal']))
        story.append(Paragraph(f"<b>Période :</b> Année {year}", styles['Normal']))
        story.append(Spacer(1, 2 * cm))

        # RÉSUMÉ EXÉCUTIF (KPI)
        stats = self.db.get_statistics(year=self._get_year()) or {}
        sales_total = float(stats.get("sales_total", 0))
        purchases_total = float(stats.get("purchases_total", 0))
        profit = sales_total - purchases_total
        margin_pct = (profit / sales_total * 100) if sales_total > 0 else 0

        story.append(Paragraph("📌 RÉSUMÉ EXÉCUTIF", heading_style))

        kpi_data = [
            ["Indicateur", "Valeur"],
            ["Chiffre d'Affaires Total", f"{fmt_da(sales_total, 0)}"],
            ["Achats Totaux", f"{fmt_da(purchases_total, 0)}"],
            ["Profit Net", f"{fmt_da(profit, 0)}"],
            ["Taux de Marge", f"{margin_pct:.1f} %"],
            ["Nombre de Clients", f"{stats.get('total_clients', 0)}"],
            ["Nombre de Produits", f"{stats.get('total_products', 0)}"],
            ["Total des Ventes", f"{stats.get('total_sales', 0)}"],
        ]

        kpi_table = Table(kpi_data, colWidths=[8 * cm, 8 * cm])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')]),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.5 * cm))
        story.append(PageBreak())

        # PAGE 2: STATISTIQUES DÉTAILLÉES
        story.append(Paragraph("📊 STATISTIQUES MENSUELLES", heading_style))

        MOIS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        monthly_data = [["Mois", "Ventes", "Montant (DA)", "Panier Moyen"]]

        monthly = {int(r["month"]): r for r in (self.db.get_sales_by_month(year) or [])}
        for m in range(1, 13):
            r = monthly.get(m, {"count": 0, "total": 0})
            count = r.get("count", 0)
            total = r.get("total", 0)
            avg = total / count if count > 0 else 0
            monthly_data.append([MOIS[m - 1], str(count), f"{total:,.0f}", f"{avg:,.0f}"])

        monthly_table = Table(monthly_data, colWidths=[3 * cm, 3 * cm, 5 * cm, 5 * cm])
        monthly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')]),
        ]))
        story.append(monthly_table)
        story.append(Spacer(1, 0.5 * cm))

        if img_sales:
            story.append(Paragraph("📈 Évolution des Ventes", styles['Heading3']))
            story.append(Image(img_sales, width=15 * cm, height=7.5 * cm))
            story.append(Spacer(1, 0.3 * cm))

        story.append(PageBreak())

        # PAGE 3: TOP PRODUITS
        story.append(Paragraph("🏆 TOP 10 PRODUITS LES PLUS VENDUS", heading_style))

        top_products = self.db.get_top_products(limit=10, year=self._get_year()) or []
        prod_data = [["Rang", "Produit", "Quantité", "Montant (DA)"]]
        for idx, prod in enumerate(top_products, 1):
            prod_data.append([str(idx), prod.get("name", "—")[:30], str(int(prod.get("total_quantity", 0))), f"{prod.get('total_sales', 0):,.0f}"])

        prod_table = Table(prod_data, colWidths=[1.5 * cm, 8 * cm, 3 * cm, 4 * cm])
        prod_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFFBEB')]),
        ]))
        story.append(prod_table)
        story.append(Spacer(1, 0.5 * cm))

        if img_prod:
            story.append(Paragraph("📦 Visualisation", styles['Heading3']))
            story.append(Image(img_prod, width=15 * cm, height=7.5 * cm))

        story.append(PageBreak())

        # PAGE 4: TOP CLIENTS
        story.append(Paragraph("👥 TOP 10 MEILLEURS CLIENTS", heading_style))

        top_clients = self.db.get_top_clients(limit=10, year=self._get_year()) or []
        client_data = [["Rang", "Nom Client", "Ventes", "Montant Total (DA)"]]
        for idx, client in enumerate(top_clients, 1):
            client_data.append([str(idx), client.get("name", "—")[:30], str(int(client.get("sale_count", 0))), f"{client.get('total_amount', 0):,.0f}"])

        client_table = Table(client_data, colWidths=[1.5 * cm, 8 * cm, 3 * cm, 4 * cm])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B5CF6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F3FF')]),
        ]))
        story.append(client_table)
        story.append(Spacer(1, 0.5 * cm))

        if img_clients:
            story.append(Paragraph("📊 Visualisation", styles['Heading3']))
            story.append(Image(img_clients, width=15 * cm, height=7.5 * cm))

        story.append(PageBreak())

        # PAGE 5: RENTABILITÉ
        story.append(Paragraph("💎 TOP 10 PRODUITS PAR MARGE BRUTE", heading_style))

        profitable = self.db.get_most_profitable_products(limit=10, year=self._get_year()) or []
        profit_data = [["Rang", "Produit", "Quantité", "Marge Unit.", "Marge Totale"]]
        for idx, prod in enumerate(profitable, 1):
            profit_data.append([str(idx), prod.get("name", "—")[:28], str(int(prod.get("qty_sold", 0))), f"{prod.get('unit_margin', 0):,.0f}", f"{prod.get('total_margin', 0):,.0f}"])

        profit_table = Table(profit_data, colWidths=[1.5 * cm, 7 * cm, 2.5 * cm, 3.5 * cm, 3.5 * cm])
        profit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0FDF4')]),
        ]))
        story.append(profit_table)
        story.append(Spacer(1, 0.5 * cm))

        if img_profit:
            story.append(Paragraph("💹 Évolution du Profit", styles['Heading3']))
            story.append(Image(img_profit, width=15 * cm, height=7.5 * cm))

        doc.build(story)

        QMessageBox.information(self, "PDF Complet ✅", f"Rapport PDF détaillé généré avec succès !\n\n📄 Fichier : {path}")