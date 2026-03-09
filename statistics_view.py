# ─────────────────────────────────────────────────────────────
#  statistics_view.py — Version PRO (Design + Export + Charts)
#  AVEC TOUTES LES CORRECTIONS
# ─────────────────────────────────────────────────────────────
def fmt_da(value, decimals=2):
    """Format monétaire algérien : 1,200.00 DA"""
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = 0.0
    if decimals == 0:
        return f"{v:,.0f} DA"
    return f"{v:,.2f} DA"


from PyQt6.QtWidgets import (
    QSplitter, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QFileDialog, QMessageBox,
    QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem, QComboBox
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import csv
from datetime import datetime
from db_manager import get_database
from ui_components import (
    BG_PAGE, BG_CARD, BG_DEEP, BORDER, TXT_PRI, TXT_SEC,
    C_BLUE, C_GREEN, C_AMBER, C_VIOLET, C_CYAN, C_RED,
    CARD_STYLE, MONTHS_FR, CHART_COLORS,
    _KpiAnim, count_up, _card, _lbl, _sep, _styled_plot
)


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

        # Sélecteur d'année dynamique
        self.year_combo = QComboBox()
        self.year_combo.setFixedHeight(36)
        self.year_combo.setFixedWidth(100)
        self.year_combo.setStyleSheet(f"""
            QComboBox {{
                background: rgba(59,130,246,0.15);
                color: {C_BLUE};
                border: 1px solid rgba(59,130,246,0.35);
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                font-weight: bold;
            }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background: {BG_CARD};
                color: {C_BLUE};
                selection-background-color: rgba(59,130,246,0.25);
                border: 1px solid rgba(59,130,246,0.35);
            }}
        """)
        # Remplir avec les années présentes en BDD + année courante
        self._populate_years()
        self.year_combo.currentTextChanged.connect(self.refresh)
        row.addWidget(self.year_combo)

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
            ("Meilleur Jour (Ventes)", "—", C_GREEN, "📅"),
            ("Meilleur Jour (Recette)", "—", C_AMBER, "💰"),
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
    # Gestion de l'année sélectionnée
    # ─────────────────────────────────────────────────────────

    def _populate_years(self):
        """Remplit le ComboBox avec toutes les années présentes en BDD."""
        years = []
        try:
            # Utiliser substr pour compatibilité maximale avec tous les formats de date
            self.db.cursor.execute("""
                SELECT DISTINCT substr(sale_date, 1, 4) as yr
                FROM sales
                WHERE sale_date IS NOT NULL
                  AND length(sale_date) >= 4
                ORDER BY yr DESC
            """)
            for row in self.db.cursor.fetchall():
                try:
                    # Compatibilité sqlite3.Row et tuple
                    try:
                        yr = row['yr']
                    except (IndexError, TypeError):
                        yr = row[0]
                    if yr and len(str(yr).strip()) == 4 and str(yr).strip().isdigit():
                        years.append(str(yr).strip())
                except Exception:
                    pass
        except Exception as e:
            print(f"⚠️ _populate_years erreur: {e}")

        current_year = str(datetime.now().year)
        # Toujours inclure l'année courante
        if current_year not in years:
            years.insert(0, current_year)

        # Supprimer doublons en gardant l'ordre
        seen, unique_years = set(), []
        for y in years:
            if y not in seen:
                seen.add(y)
                unique_years.append(y)

        # Mémoriser la sélection courante avant de vider
        current_selection = self.year_combo.currentText() if self.year_combo.count() > 0 else current_year

        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        for y in unique_years:
            self.year_combo.addItem(y)

        # Restaurer la sélection précédente, sinon l'année courante
        idx = self.year_combo.findText(current_selection)
        if idx < 0:
            idx = self.year_combo.findText(current_year)
        self.year_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.year_combo.blockSignals(False)
        print(f"✅ Années en BDD : {unique_years}")

    def _get_year(self):
        """Retourne l'année sélectionnée dans le ComboBox."""
        try:
            return int(self.year_combo.currentText())
        except (ValueError, AttributeError):
            return datetime.now().year

    # ─────────────────────────────────────────────────────────
    # Refresh Data
    # ─────────────────────────────────────────────────────────

    def refresh(self):
        self._populate_years()   # Mettre à jour la liste des années à chaque refresh
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
        stats = self.db.get_statistics(year=self._get_year()) or {}

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
        year = self._get_year()
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
        year = self._get_year()
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
        data = self.db.get_top_products(limit=5,  year=self._get_year()) or []

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
        data = self.db.get_top_clients(limit=5,  year=self._get_year()) or []

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
                
            stats = self.db.get_statistics(year=self._get_year()) or {}

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
            self._info_cards[1].value_label.setText(f"{fmt_da(avg, 0)}")

            # Meilleur jour (ventes et recette)
            best_days = self.db.get_best_days()
            self._info_cards[2].value_label.setText(
                f"{best_days['sales_day']} ({best_days['sales_count']})"
            )
            self._info_cards[3].value_label.setText(
                f"{best_days['revenue_day']} ({fmt_da(best_days['revenue_amount'], 0)})"
            )
            
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
            products = self.db.get_most_profitable_products(limit=5,  year=self._get_year())
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
        
        # Trouver le produit dans la base
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
    # Export CSV
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
        year  = self._get_year()

        MOIS = [
            "Janvier","Février","Mars","Avril","Mai","Juin",
            "Juillet","Août","Septembre","Octobre","Novembre","Décembre"
        ]

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=';')

                # En-tête rapport
                w.writerow(["RAPPORT STATISTIQUE ERP"])
                w.writerow(["Généré le", dt.now().strftime("%d/%m/%Y à %H:%M:%S")])
                w.writerow(["Période", f"Année {year}"])
                w.writerow([])

                # ============== KPI GLOBAUX ==============
                w.writerow(["=== KPI GLOBAUX ==="])
                w.writerow(["Indicateur", "Valeur", "Unité"])
                w.writerow(["Chiffre d'Affaires Total", f"{stats.get('sales_total', 0):,.0f}", "DA"])
                w.writerow(["Achats Totaux", f"{stats.get('purchases_total', 0):,.0f}", "DA"])
                w.writerow(["Profit Net", f"{stats.get('profit', 0):,.0f}", "DA"])
                
                # Calcul marges
                sales_total = float(stats.get("sales_total", 0))
                purchases_total = float(stats.get("purchases_total", 0))
                margin_pct = (stats.get("profit", 0) / sales_total * 100) if sales_total > 0 else 0
                w.writerow(["Taux de Marge", f"{margin_pct:.1f}", "%"])
                
                w.writerow(["Nombre de Clients", stats.get("total_clients", 0), "clients"])
                w.writerow(["Nombre de Produits", stats.get("total_products", 0), "produits"])
                w.writerow(["Nombre de Ventes", stats.get("total_sales", 0), "transactions"])
                w.writerow(["Nombre d'Achats", stats.get("total_purchases", 0), "commandes"])
                w.writerow(["Valeur du Stock", f"{stats.get('stock_value', 0):,.0f}", "DA"])
                w.writerow(["Produits en Stock Faible", stats.get("low_stock_count", 0), "produits"])
                w.writerow([])

                # ============== STATISTIQUES AVANCÉES ==============
                w.writerow(["=== STATISTIQUES AVANCÉES ==="])
                
                # Panier moyen
                num_sales = int(stats.get("total_sales", 1)) or 1
                avg_cart = sales_total / num_sales if num_sales > 0 else 0
                w.writerow(["Panier Moyen", f"{avg_cart:,.0f}", "DA"])
                
                # Meilleur jour
                best_days = self.db.get_best_days()
                w.writerow(["Meilleur Jour (Ventes)", f"{best_days['sales_day']} ({best_days['sales_count']} ventes)", ""])
                w.writerow(["Meilleur Jour (Recette)", f"{best_days['revenue_day']} ({fmt_da(best_days['revenue_amount'], 0)})", ""])
                
                w.writerow(["Meilleur Mois", stats.get("best_month", "—"), ""])
                w.writerow(["Croissance Mensuelle", f"{stats.get('growth_rate', 0):.1f}", "%"])
                w.writerow([])

                # ============== VENTES MENSUELLES ==============
                w.writerow([f"=== VENTES MENSUELLES {year} ==="])
                w.writerow(["Mois", "Nombre de Ventes", "Montant (DA)", "Panier Moyen"])

                monthly = {
                    int(r["month"]): r
                    for r in (self.db.get_sales_by_month(year) or [])
                }

                for m in range(1,13):
                    r = monthly.get(m, {"count":0, "total":0})
                    count = r.get("count", 0)
                    total = r.get("total", 0)
                    avg = total / count if count > 0 else 0
                    w.writerow([
                        MOIS[m-1],
                        count,
                        f"{total:,.0f}",
                        f"{avg:,.0f}"
                    ])
                w.writerow([])

                # ============== PROFITS MENSUELS ==============
                w.writerow([f"=== PROFITS MENSUELS {year} ==="])
                w.writerow(["Mois", "Profit (DA)"])
                
                profits = {
                    int(r["month"]): r
                    for r in (self.db.get_profit_by_month(year) or [])
                }
                
                for m in range(1, 13):
                    p = profits.get(m, {"profit": 0})
                    w.writerow([
                        MOIS[m-1],
                        f"{p.get('profit', 0):,.0f}"
                    ])
                w.writerow([])

                # ============== TOP 5 PRODUITS ==============
                w.writerow(["=== TOP 5 PRODUITS LES PLUS VENDUS ==="])
                w.writerow(["Rang", "Produit", "Quantité Vendue", "Montant (DA)"])
                
                top_products = self.db.get_top_products(limit=5,  year=self._get_year()) or []
                for idx, prod in enumerate(top_products, 1):
                    w.writerow([
                        idx,
                        prod.get("name", "—"),
                        int(prod.get("total_quantity", 0)),
                        f"{prod.get('total_sales', 0):,.0f}"
                    ])
                w.writerow([])

                # ============== TOP 5 CLIENTS ==============
                w.writerow(["=== TOP 5 MEILLEURS CLIENTS ==="])
                w.writerow(["Rang", "Nom Client", "Nombre de Ventes", "Montant Total (DA)"])
                
                top_clients = self.db.get_top_clients(limit=5,  year=self._get_year()) or []
                for idx, client in enumerate(top_clients, 1):
                    w.writerow([
                        idx,
                        client.get("name", "—"),
                        int(client.get("sale_count", 0)),
                        f"{client.get('total_amount', 0):,.0f}"
                    ])
                w.writerow([])

                # ============== TOP 5 PRODUITS PAR MARGE ==============
                w.writerow(["=== TOP 5 PRODUITS PAR MARGE BRUTE ==="])
                w.writerow(["Rang", "Produit", "Quantité", "Marge Unitaire (DA)", "Marge Totale (DA)"])
                
                profitable = self.db.get_most_profitable_products(limit=5,  year=self._get_year()) or []
                for idx, prod in enumerate(profitable, 1):
                    w.writerow([
                        idx,
                        prod.get("name", "—"),
                        int(prod.get("qty_sold", 0)),
                        f"{prod.get('unit_margin', 0):,.0f}",
                        f"{prod.get('total_margin', 0):,.0f}"
                    ])

            QMessageBox.information(self, "Export CSV ✅", f"Rapport généré avec succès :\n\n{path}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur Export", f"Impossible d'exporter :\n{e}")


    # ======================================================================
    # EXPORT EXCEL PRO+ (Feuilles séparées + Tableaux structurés)
    # ======================================================================

    def _export_excel_pro_plus(self):
        import tempfile, os
        import xlsxwriter
        import pyqtgraph.exporters as exporters
        from datetime import datetime as dt

        # Choisir chemin sortie
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter Excel PRO+",
            f"rapport_complet_{dt.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return

        # Dossier temporaire pour les images
        temp_dir = tempfile.mkdtemp()

        # Fonction sauvegarde graphique
        def save_chart(widget, filename):
            try:
                exporter = exporters.ImageExporter(widget.plotItem)
                exporter.export(filename)
                return filename
            except:
                return None

        # Créer Excel
        wb = xlsxwriter.Workbook(path)

        # ====== FORMATS ======
        title_fmt = wb.add_format({
            "bold": True, "font_size": 14,
            "bg_color": "#1F2937", "font_color": "white",
            "align": "center", "valign": "vcenter",
            "border": 1
        })
        
        header_fmt = wb.add_format({
            "bold": True, "bg_color": "#3B82F6",
            "font_color": "white", "border": 1,
            "align": "center", "valign": "vcenter"
        })
        
        data_fmt = wb.add_format({
            "border": 1, "align": "left",
            "num_format": "#,##0.00"
        })
        
        number_fmt = wb.add_format({
            "border": 1, "align": "center",
            "num_format": "#,##0"
        })

        # ====== FEUILLE 1: TABLEAU DE BORD (KPI) ======
        ws = wb.add_worksheet("📊 Dashboard")
        ws.set_column("A:A", 25)
        ws.set_column("B:D", 18)

        row = 0
        ws.merge_range(row, 0, row, 3, "TABLEAU DE BORD KPI", title_fmt)
        row += 1
        ws.write(row, 0, f"Généré le : {dt.now().strftime('%d/%m/%Y %H:%M')}")
        row += 2

        # Headers
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
            ("Chiffre d'Affaires", sales_total, "DA"),
            ("Achats Totaux", purchases_total, "DA"),
            ("Profit Net", profit, "DA"),
            ("Taux de Marge", margin_pct, "%"),
            ("Nombre Clients", stats.get("total_clients", 0), "clients"),
            ("Nombre Produits", stats.get("total_products", 0), "produits"),
            ("Total Ventes", stats.get("total_sales", 0), "transactions"),
            ("Valeur du Stock", stats.get("stock_value", 0), "DA"),
        ]

        for kpi_name, value, unit in kpis:
            ws.write(row, 0, kpi_name, data_fmt)
            if unit == "DA":
                ws.write(row, 1, value, data_fmt)
            elif unit == "%":
                ws.write(row, 1, value, number_fmt)
            else:
                ws.write(row, 1, value, number_fmt)
            ws.write(row, 2, unit, data_fmt)
            row += 1

        # ====== FEUILLE 2: VENTES MENSUELLES ======
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

        # ====== FEUILLE 3: PROFITS MENSUELS ======
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

        # ====== FEUILLE 4: TOP PRODUITS ======
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

        # ====== FEUILLE 5: TOP CLIENTS ======
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

        # ====== FEUILLE 6: PRODUITS RENTABLES ======
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

        # ====== FEUILLE 7: GRAPHIQUES ======
        try:
            img_sales = save_chart(self.sales_chart, os.path.join(temp_dir, "sales.png"))
            img_profit = save_chart(self.profit_chart, os.path.join(temp_dir, "profit.png"))
            img_prod = save_chart(self.products_chart, os.path.join(temp_dir, "products.png"))
            img_clients = save_chart(self.clients_chart, os.path.join(temp_dir, "clients.png"))

            charts_data = [
                ("📊 Ventes", img_sales),
                ("💹 Profit", img_profit),
                ("📦 Produits", img_prod),
                ("🎯 Clients", img_clients)
            ]

            for sheet_name, img in charts_data:
                if img:
                    ws = wb.add_worksheet(sheet_name)
                    ws.set_column("A:A", 60)
                    ws.insert_image("A1", img, {"x_scale": 0.7, "y_scale": 0.7})
        except:
            pass

        # Sauvegarde
        wb.close()
        QMessageBox.information(
            self,
            "Excel Complet ✅",
            f"Rapport complet généré avec succès !\n\n"
            f"📄 Fichier : {path}\n\n"
            f"Feuilles :\n"
            f"📊 Dashboard\n"
            f"📈 Ventes Mensuelles\n"
            f"💰 Profits\n"
            f"🏆 Top Produits\n"
            f"👥 Top Clients\n"
            f"💎 Rentabilité\n"
            f"📉 Graphiques"
        )


    # ======================================================================
    # EXPORT PDF PROFESSIONNEL (Rapport détaillé avec tableaux)
    # ======================================================================

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

        # Export charts
        def save_chart(widget, filename):
            try:
                exporter = exporters.ImageExporter(widget.plotItem)
                exporter.export(filename)
                return filename
            except:
                return None

        img_sales   = save_chart(self.sales_chart, os.path.join(temp_dir, "sales.png"))
        img_profit  = save_chart(self.profit_chart, os.path.join(temp_dir, "profit.png"))
        img_prod    = save_chart(self.products_chart, os.path.join(temp_dir, "prod.png"))
        img_clients = save_chart(self.clients_chart, os.path.join(temp_dir, "clients.png"))

        # Build PDF
        doc = SimpleDocTemplate(path, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
        styles = getSampleStyleSheet()
        story = []

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=6,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3B82F6'),
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#3B82F6'),
            borderWidth=2,
            borderPadding=4
        )

        # ====== PAGE 1: COUVERTURE ======
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph("📊 RAPPORT STATISTIQUE ERP", title_style))
        story.append(Paragraph("Analyse Complète et Détaillée", styles['Heading2']))
        story.append(Spacer(1, 1*cm))
        
        date_text = dt.now().strftime("%d/%m/%Y à %H:%M:%S")
        year = self._get_year()
        story.append(Paragraph(f"<b>Généré le :</b> {date_text}", styles['Normal']))
        story.append(Paragraph(f"<b>Période :</b> Année {year}", styles['Normal']))
        story.append(Spacer(1, 2*cm))

        # ====== RÉSUMÉ EXÉCUTIF (KPI) ======
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

        kpi_table = Table(kpi_data, colWidths=[8*cm, 8*cm])
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
        story.append(Spacer(1, 0.5*cm))
        story.append(PageBreak())

        # ====== PAGE 2: STATISTIQUES DÉTAILLÉES ======
        story.append(Paragraph("📊 STATISTIQUES MENSUELLES", heading_style))

        MOIS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        monthly_data = [["Mois", "Ventes", "Montant (DA)", "Panier Moyen"]]
        
        monthly = {int(r["month"]): r for r in (self.db.get_sales_by_month(year) or [])}
        for m in range(1, 13):
            r = monthly.get(m, {"count": 0, "total": 0})
            count = r.get("count", 0)
            total = r.get("total", 0)
            avg = total / count if count > 0 else 0
            monthly_data.append([MOIS[m-1], str(count), f"{total:,.0f}", f"{avg:,.0f}"])

        monthly_table = Table(monthly_data, colWidths=[3*cm, 3*cm, 5*cm, 5*cm])
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
        story.append(Spacer(1, 0.5*cm))

        # Graphique ventes
        if img_sales:
            story.append(Paragraph("📈 Évolution des Ventes", styles['Heading3']))
            story.append(Image(img_sales, width=15*cm, height=7.5*cm))
            story.append(Spacer(1, 0.3*cm))
        
        story.append(PageBreak())

        # ====== PAGE 3: TOP PRODUITS ======
        story.append(Paragraph("🏆 TOP 10 PRODUITS LES PLUS VENDUS", heading_style))

        top_products = self.db.get_top_products(limit=10, year=self._get_year()) or []
        prod_data = [["Rang", "Produit", "Quantité", "Montant (DA)"]]
        for idx, prod in enumerate(top_products, 1):
            prod_data.append([
                str(idx),
                prod.get("name", "—")[:30],
                str(int(prod.get("total_quantity", 0))),
                f"{prod.get('total_sales', 0):,.0f}"
            ])

        prod_table = Table(prod_data, colWidths=[1.5*cm, 8*cm, 3*cm, 4*cm])
        prod_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFFBEB')]),
        ]))
        story.append(prod_table)
        story.append(Spacer(1, 0.5*cm))

        if img_prod:
            story.append(Paragraph("📦 Visualisation", styles['Heading3']))
            story.append(Image(img_prod, width=15*cm, height=7.5*cm))

        story.append(PageBreak())

        # ====== PAGE 4: TOP CLIENTS ======
        story.append(Paragraph("👥 TOP 10 MEILLEURS CLIENTS", heading_style))

        top_clients = self.db.get_top_clients(limit=10, year=self._get_year()) or []
        client_data = [["Rang", "Nom Client", "Ventes", "Montant Total (DA)"]]
        for idx, client in enumerate(top_clients, 1):
            client_data.append([
                str(idx),
                client.get("name", "—")[:30],
                str(int(client.get("sale_count", 0))),
                f"{client.get('total_amount', 0):,.0f}"
            ])

        client_table = Table(client_data, colWidths=[1.5*cm, 8*cm, 3*cm, 4*cm])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B5CF6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F3FF')]),
        ]))
        story.append(client_table)
        story.append(Spacer(1, 0.5*cm))

        if img_clients:
            story.append(Paragraph("📊 Visualisation", styles['Heading3']))
            story.append(Image(img_clients, width=15*cm, height=7.5*cm))

        story.append(PageBreak())

        # ====== PAGE 5: RENTABILITÉ ======
        story.append(Paragraph("💎 TOP 10 PRODUITS PAR MARGE BRUTE", heading_style))

        profitable = self.db.get_most_profitable_products(limit=10, year=self._get_year()) or []
        profit_data = [["Rang", "Produit", "Quantité", "Marge Unit.", "Marge Totale"]]
        for idx, prod in enumerate(profitable, 1):
            profit_data.append([
                str(idx),
                prod.get("name", "—")[:28],
                str(int(prod.get("qty_sold", 0))),
                f"{prod.get('unit_margin', 0):,.0f}",
                f"{prod.get('total_margin', 0):,.0f}"
            ])

        profit_table = Table(profit_data, colWidths=[1.5*cm, 7*cm, 2.5*cm, 3.5*cm, 3.5*cm])
        profit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0FDF4')]),
        ]))
        story.append(profit_table)
        story.append(Spacer(1, 0.5*cm))

        if img_profit:
            story.append(Paragraph("💹 Évolution du Profit", styles['Heading3']))
            story.append(Image(img_profit, width=15*cm, height=7.5*cm))

        # Build PDF
        doc.build(story)
        
        QMessageBox.information(
            self,
            "PDF Complet ✅",
            f"Rapport PDF détaillé généré avec succès !\n\n"
            f"📄 Fichier : {path}\n\n"
            f"Contenu :\n"
            f"✓ Résumé des KPI\n"
            f"✓ Statistiques mensuelles\n"
            f"✓ Top 10 Produits\n"
            f"✓ Top 10 Clients\n"
            f"✓ Analyses de Rentabilité\n"
            f"✓ Graphiques professionnels"
        )