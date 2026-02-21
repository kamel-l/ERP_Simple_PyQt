from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, 
    QGridLayout, QSizePolicy, QPushButton, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QFont, QPainter, QColor
from PyQt6.QtCore import Qt, QRectF
import pyqtgraph as pg
from styles import COLORS
from db_manager import get_database
from datetime import datetime, timedelta


class StatisticsPage(QWidget):
    """Page de statistiques moderne et professionnelle"""

    def __init__(self):
        super().__init__()
        self.db = get_database()
        
        # Scroll area pour tout le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: {COLORS['bg_dark']};
            }}
        """)
        
        # Widget conteneur principal
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ================= EN-TÊTE =================
        header_layout = QHBoxLayout()
        
        title_container = QVBoxLayout()
        title = QLabel("📊 Statistiques & Analytics")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        title_container.addWidget(title)
        
        subtitle = QLabel("Vue d'ensemble de votre activité commerciale")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        title_container.addWidget(subtitle)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Bouton refresh
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
        """)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh)
        refresh_btn.setMaximumHeight(40)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)

        # ================= CARTES KPI =================
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(15)
        
        self.revenue_card = self.create_kpi_card_large(
            "💰", "Chiffre d'Affaires", "0 DA", "Total des ventes", COLORS['primary']
        )
        kpi_grid.addWidget(self.revenue_card, 0, 0)
        
        self.profit_card = self.create_kpi_card_large(
            "📈", "Profit Net", "0 DA", "Marge bénéficiaire", COLORS['success']
        )
        kpi_grid.addWidget(self.profit_card, 0, 1)
        
        self.orders_card = self.create_kpi_card_large(
            "🛒", "Commandes", "0", "Total des achats", COLORS['info']
        )
        kpi_grid.addWidget(self.orders_card, 0, 2)
        
        self.clients_card = self.create_kpi_card_large(
            "👥", "Clients", "0", "Clients actifs", COLORS['secondary']
        )
        kpi_grid.addWidget(self.clients_card, 0, 3)
        
        main_layout.addLayout(kpi_grid)

        # ================= GRAPHIQUES PRINCIPAUX =================
        charts_row = QHBoxLayout()
        charts_row.setSpacing(15)
        
        # Graphique des ventes mensuelles
        sales_card = self.create_chart_card("📊 Évolution des Ventes", 250)
        self.sales_chart = sales_card['plot']
        charts_row.addWidget(sales_card['widget'])
        
        # Graphique des profits
        profit_card = self.create_chart_card("💹 Évolution du Profit", 250)
        self.profit_chart = profit_card['plot']
        charts_row.addWidget(profit_card['widget'])
        
        main_layout.addLayout(charts_row)

        # ================= SECTION ANALYSES =================
        analysis_row = QHBoxLayout()
        analysis_row.setSpacing(15)
        
        # Top produits
        products_card = self.create_chart_card("🏆 Top 5 Produits Vendus", 220)
        self.products_chart = products_card['plot']
        analysis_row.addWidget(products_card['widget'])
        
        # Top clients
        clients_card = self.create_chart_card("⭐ Top 5 Meilleurs Clients", 220)
        self.clients_chart = clients_card['plot']
        analysis_row.addWidget(clients_card['widget'])
        
        main_layout.addLayout(analysis_row)

        # ================= SECTION INFOS RAPIDES =================
        quick_info_layout = QHBoxLayout()
        quick_info_layout.setSpacing(15)
        
        self.stock_alert = self.create_info_card(
            "⚠️", "Stock Faible", "0 produits", COLORS['warning']
        )
        quick_info_layout.addWidget(self.stock_alert)
        
        self.best_day = self.create_info_card(
            "📅", "Meilleur Jour", "Lundi", COLORS['info']
        )
        quick_info_layout.addWidget(self.best_day)
        
        self.avg_order = self.create_info_card(
            "💳", "Panier Moyen", "0 DA", COLORS['secondary']
        )
        quick_info_layout.addWidget(self.avg_order)
        
        main_layout.addLayout(quick_info_layout)

        # Ajouter le stretch pour pousser tout en haut
        main_layout.addStretch()
        
        scroll.setWidget(container)
        
        # Layout principal de la page
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        
        # Charger les données
        self.refresh()

    def create_kpi_card_large(self, icon, title, value, subtitle, color):
        """Crée une grande carte KPI moderne"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
              
                padding: 0px;
            }}
        """)
        card.setMinimumHeight(90)
        card.setMaximumHeight(90)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(4)
        card.setLayout(layout)
        
        # En-tête avec icône
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        icon_label.setStyleSheet("border: none;")
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        
        # Titre à côté de l'icône
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        header_layout.addWidget(title_label)
        
        layout.addLayout(header_layout)
        
        # Valeur
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        layout.addWidget(value_label)
        
        # Sous-titre
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Segoe UI", 9))
        subtitle_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        layout.addWidget(subtitle_label)
        
        # Stocker les labels pour mise à jour
        card.value_label = value_label
        
        return card

    def create_chart_card(self, title, height):
        """Crée une carte avec graphique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 0px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)
        card.setLayout(layout)
        
        # Titre
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title_label)
        
        # Graphique
        plot = pg.PlotWidget()
        plot.setBackground(COLORS['bg_card'])
        plot.setMinimumHeight(height)
        plot.showGrid(x=True, y=True, alpha=0.15)
        plot.setMouseEnabled(x=False, y=False)
        plot.hideButtons()
        
        # Personnalisation des axes
        plot.getAxis('bottom').setPen(pg.mkPen(color=COLORS['border'], width=1))
        plot.getAxis('left').setPen(pg.mkPen(color=COLORS['border'], width=1))
        plot.getAxis('bottom').setTextPen(pg.mkPen(color=COLORS['text_tertiary']))
        plot.getAxis('left').setTextPen(pg.mkPen(color=COLORS['text_tertiary']))
        
        layout.addWidget(plot)
        
        return {'widget': card, 'plot': plot}

    def create_info_card(self, icon, title, value, color):
        """Crée une petite carte d'information"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
                
                padding: 0px;
            }}
        """)
        card.setMinimumHeight(100)
        card.setMaximumHeight(100)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        card.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icône
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("border: none;")
        layout.addWidget(icon_label)
        
        # Titre
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        layout.addWidget(title_label)
        
        # Valeur
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"color: {color}; border: none;")
        layout.addWidget(value_label)
        
        # Stocker le label pour mise à jour
        card.value_label = value_label
        
        return card

    def refresh(self):
        """Actualise toutes les statistiques"""
        self.load_kpis()
        self.load_sales_chart()
        self.load_profit_chart()
        self.load_top_products()
        self.load_top_clients()
        self.load_quick_info()

    def load_kpis(self):
        """Charge les KPIs principaux"""
        stats = self.db.get_statistics() or {}
        
        sales_total = float(stats.get('sales_total', 0))
        purchases_total = float(stats.get('purchases_total', 0))
        profit = sales_total - purchases_total
        
        num_clients = stats.get('total_clients', 0)
        num_purchases = stats.get('total_purchases', 0)
        
        # Mise à jour des cartes
        self.revenue_card.value_label.setText(f"{sales_total:,.0f} DA")
        self.profit_card.value_label.setText(f"{profit:,.0f} DA")
        self.orders_card.value_label.setText(f"{num_purchases}")
        self.clients_card.value_label.setText(f"{num_clients}")

    def load_sales_chart(self):
        """Charge le graphique des ventes mensuelles"""
        self.sales_chart.clear()
        
        year = datetime.now().year
        data = self.db.get_sales_by_month(year) or []
        
        months = list(range(1, 13))
        values = [0] * 12
        
        for row in data:
            idx = int(row.get("month", 0)) - 1
            if 0 <= idx < 12:
                values[idx] = float(row.get("total", 0))
        
        # Graphique en aire avec gradient
        pen = pg.mkPen(color=COLORS['primary'], width=3)
        brush = pg.mkBrush(color=(*self.hex_to_rgb(COLORS['primary']), 50))
        
        self.sales_chart.plot(months, values, pen=pen, fillLevel=0, brush=brush, symbol='o', symbolSize=8, symbolBrush=COLORS['primary'])
        
        # Noms des mois
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        self.sales_chart.getAxis('bottom').setTicks([list(zip(months, month_names))])

    def load_profit_chart(self):
        """Charge le graphique des profits"""
        self.profit_chart.clear()
        
        year = datetime.now().year
        data = self.db.get_profit_by_month(year) or []
        
        months = list(range(1, 13))
        values = [0] * 12
        
        for row in data:
            idx = int(row.get("month", 0)) - 1
            if 0 <= idx < 12:
                values[idx] = float(row.get("profit", 0))
        
        # Graphique en barres
        bars = pg.BarGraphItem(x=months, height=values, width=0.6, brush=COLORS['success'])
        self.profit_chart.addItem(bars)
        
        # Noms des mois
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        self.profit_chart.getAxis('bottom').setTicks([list(zip(months, month_names))])

    def load_top_products(self):
        """Charge le top 5 des produits"""
        self.products_chart.clear()
        
        data = self.db.get_top_products(limit=5) or []
        
        if not data:
            self.products_chart.setLabel('bottom', 'Aucune donnée')
            return
        
        names = [p.get("name", "")[:15] for p in data]
        values = [float(p.get("total_quantity", 0)) for p in data]
        
        # Barres horizontales avec couleurs dégradées
        colors = [COLORS['success'], COLORS['primary'], COLORS['info'], COLORS['warning'], COLORS['secondary']]
        
        for i, (val, color) in enumerate(zip(values, colors)):
            bar = pg.BarGraphItem(x=[i], height=[val], width=0.6, brush=color)
            self.products_chart.addItem(bar)
        
        self.products_chart.getAxis('bottom').setTicks([list(zip(range(len(names)), names))])
        self.products_chart.setXRange(-0.5, len(values))

    def load_top_clients(self):
        """Charge le top 5 des clients"""
        self.clients_chart.clear()
        
        data = self.db.get_top_clients(limit=5) or []
        
        if not data:
            self.clients_chart.setLabel('bottom', 'Aucune donnée')
            return
        
        names = [c.get("name", "")[:15] for c in data]
        values = [float(c.get("total_amount", 0)) for c in data]
        
        # Barres avec gradient
        colors = [COLORS['primary'], COLORS['secondary'], COLORS['info'], COLORS['success'], COLORS['warning']]
        
        for i, (val, color) in enumerate(zip(values, colors)):
            bar = pg.BarGraphItem(x=[i], height=[val], width=0.6, brush=color)
            self.clients_chart.addItem(bar)
        
        self.clients_chart.getAxis('bottom').setTicks([list(zip(range(len(names)), names))])
        self.clients_chart.setXRange(-0.5, len(values))

    def load_quick_info(self):
        """Charge les informations rapides"""
        # Stock faible
        low_stock = self.db.get_low_stock_products() or []
        self.stock_alert.value_label.setText(f"{len(low_stock)} produits")
        
        # Panier moyen
        stats = self.db.get_statistics() or {}
        sales_total = float(stats.get('sales_total', 0))
        num_sales = stats.get('total_sales', 1)
        avg_order = sales_total / max(num_sales, 1)
        self.avg_order.value_label.setText(f"{avg_order:,.0f} DA")
        
        # Meilleur jour (simulé pour l'instant)
        self.best_day.value_label.setText("Samedi")

    def hex_to_rgb(self, hex_color):
        """Convertit une couleur hex en RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    