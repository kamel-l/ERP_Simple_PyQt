from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from styles import COLORS, get_kpi_card_style
from db_manager import get_database
from datetime import datetime


class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.db = get_database()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title = QLabel("📈 Statistiques & Analyses")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Analysez les performances de votre entreprise")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # KPI Cards Grid
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(15)
        layout.addLayout(kpi_grid)

        # Charger les statistiques
        self.load_kpi_cards(kpi_grid)

        # Graphique des ventes mensuelles
        sales_section = QVBoxLayout()
        sales_section.setSpacing(10)
        
        sales_title = QLabel("📊 Évolution des Ventes Mensuelles")
        sales_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        sales_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        sales_section.addWidget(sales_title)

        sales_container = QFrame()
        sales_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        sales_layout = QVBoxLayout()
        sales_container.setLayout(sales_layout)
        
        self.sales_chart = pg.PlotWidget()
        self.sales_chart.setBackground(COLORS['bg_dark'])
        self.sales_chart.showGrid(x=True, y=True, alpha=0.3)
        self.sales_chart.setMinimumHeight(250)
        
        self.sales_chart.getAxis('left').setPen(pg.mkPen(color=COLORS['border'], width=1))
        self.sales_chart.getAxis('bottom').setPen(pg.mkPen(color=COLORS['border'], width=1))
        self.sales_chart.getAxis('left').setTextPen(COLORS['text_tertiary'])
        self.sales_chart.getAxis('bottom').setTextPen(COLORS['text_tertiary'])
        
        sales_layout.addWidget(self.sales_chart)
        sales_section.addWidget(sales_container)
        layout.addLayout(sales_section)

        # Grille des graphiques comparatifs
        charts_grid = QGridLayout()
        charts_grid.setSpacing(15)
        layout.addLayout(charts_grid)

        # Top Clients
        customers_container = self.create_chart_container("👥 Top 5 Clients")
        customers_layout = QVBoxLayout()
        customers_container.setLayout(customers_layout)
        
        self.customers_chart = pg.PlotWidget()
        self.customers_chart.setBackground(COLORS['bg_dark'])
        self.customers_chart.setMinimumHeight(220)
        self.customers_chart.getAxis('left').setPen(pg.mkPen(color=COLORS['border'], width=1))
        self.customers_chart.getAxis('bottom').setPen(pg.mkPen(color=COLORS['border'], width=1))
        self.customers_chart.getAxis('left').setTextPen(COLORS['text_tertiary'])
        self.customers_chart.getAxis('bottom').setTextPen(COLORS['text_tertiary'])
        
        customers_layout.addWidget(self.customers_chart)
        charts_grid.addWidget(customers_container, 0, 0)

        # Top Produits
        products_container = self.create_chart_container("📦 Top 5 Produits")
        products_layout = QVBoxLayout()
        products_container.setLayout(products_layout)
        
        self.products_chart = pg.PlotWidget()
        self.products_chart.setBackground(COLORS['bg_dark'])
        self.products_chart.setMinimumHeight(220)
        self.products_chart.getAxis('left').setPen(pg.mkPen(color=COLORS['border'], width=1))
        self.products_chart.getAxis('bottom').setPen(pg.mkPen(color=COLORS['border'], width=1))
        self.products_chart.getAxis('left').setTextPen(COLORS['text_tertiary'])
        self.products_chart.getAxis('bottom').setTextPen(COLORS['text_tertiary'])
        
        products_layout.addWidget(self.products_chart)
        charts_grid.addWidget(products_container, 0, 1)

        # Charger les données
        self.load_charts_data()

    def load_kpi_cards(self, grid):
        """Charge les cartes KPI depuis la base"""
        stats = self.db.get_statistics()
        
        # Première ligne
        grid.addWidget(
            self.build_kpi_card(
                "💰 Ventes Totales",
                f"{stats['sales_total']:,.0f} DA",
                f"+{stats['total_sales']} ventes",
                "transactions enregistrées",
                COLORS['primary']
            ), 0, 0
        )
        grid.addWidget(
            self.build_kpi_card(
                "🛒 Achats Totaux",
                f"{stats['purchases_total']:,.0f} DA",
                f"{stats['total_purchases']} achats",
                "fournisseurs",
                COLORS['warning']
            ), 0, 1
        )
        grid.addWidget(
            self.build_kpi_card(
                "📈 Bénéfice Net",
                f"{stats['profit']:,.0f} DA",
                f"{((stats['profit'] / stats['sales_total'] * 100) if stats['sales_total'] > 0 else 0):.1f}%",
                "marge bénéficiaire",
                COLORS['success']
            ), 0, 2
        )

        # Deuxième ligne
        grid.addWidget(
            self.build_kpi_card(
                "👥 Clients",
                str(stats['total_clients']),
                "clients",
                "enregistrés",
                COLORS['secondary']
            ), 1, 0
        )
        grid.addWidget(
            self.build_kpi_card(
                "📦 Valeur Stock",
                f"{stats['stock_value']:,.0f} DA",
                f"{stats['total_products']} produits",
                "en inventaire",
                COLORS['info']
            ), 1, 1
        )
        grid.addWidget(
            self.build_kpi_card(
                "⚠️ Stock Faible",
                str(stats['low_stock_count']),
                "produits",
                "nécessitent réapprovisionnement",
                COLORS['danger']
            ), 1, 2
        )

    def load_charts_data(self):
        """Charge les données des graphiques"""
        current_year = datetime.now().year
        
        # Ventes mensuelles
        monthly_sales = self.db.get_sales_by_month(current_year)
        
        months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", 
                 "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        
        # Créer un dictionnaire avec tous les mois à 0
        sales_data = {i+1: 0 for i in range(12)}
        
        # Remplir avec les vraies données
        for sale in monthly_sales:
            month_num = int(sale['month'])
            sales_data[month_num] = sale['total']
        
        # Convertir en listes ordonnées
        x_data = list(range(12))
        y_data = [sales_data[i+1] for i in range(12)]
        
        # Tracer
        self.sales_chart.clear()
        self.sales_chart.plot(
            x_data, 
            y_data, 
            pen=pg.mkPen(color=COLORS['primary'], width=3),
            symbol='o',
            symbolSize=8,
            symbolBrush=COLORS['primary'],
            name="Ventes"
        )
        
        # Remplissage sous la courbe
        fillBrush = pg.mkBrush(COLORS['primary'] + '40')
        self.sales_chart.plot(
            x_data,
            y_data,
            fillLevel=0,
            fillBrush=fillBrush
        )
        
        self.sales_chart.getAxis('bottom').setTicks([list(zip(range(12), months))])
        
        # Top Clients
        top_clients = self.db.get_top_clients(limit=5)
        
        if top_clients:
            client_names = [c['name'][:15] for c in top_clients]  # Limiter à 15 caractères
            client_values = [c['total_amount'] for c in top_clients]
            
            self.customers_chart.clear()
            colors = [COLORS['primary'], COLORS['secondary'], COLORS['success'], 
                     COLORS['warning'], COLORS['info']]
            
            x = list(range(len(client_names)))
            for i, (val, color) in enumerate(zip(client_values, colors)):
                bg = pg.BarGraphItem(
                    x=[i], 
                    height=[val], 
                    width=0.6, 
                    brush=color
                )
                self.customers_chart.addItem(bg)
            
            self.customers_chart.getAxis('bottom').setTicks([list(zip(range(len(client_names)), client_names))])
        else:
            # Aucune donnée
            self.customers_chart.clear()
            text = pg.TextItem("Aucune donnée disponible", color=COLORS['text_tertiary'])
            text.setPos(0.5, 0.5)
            self.customers_chart.addItem(text)
        
        # Top Produits
        top_products = self.db.get_top_products(limit=5)
        
        if top_products:
            product_names = [p['name'][:15] for p in top_products]
            product_values = [p['total_quantity'] for p in top_products]
            
            self.products_chart.clear()
            colors = [COLORS['success'], COLORS['primary'], COLORS['secondary'], 
                     COLORS['warning'], COLORS['info']]
            
            x = list(range(len(product_names)))
            for i, (val, color) in enumerate(zip(product_values, colors)):
                bg = pg.BarGraphItem(
                    x=[i], 
                    height=[val], 
                    width=0.6, 
                    brush=color
                )
                self.products_chart.addItem(bg)
            
            self.products_chart.getAxis('bottom').setTicks([list(zip(range(len(product_names)), product_names))])
        else:
            # Aucune donnée
            self.products_chart.clear()
            text = pg.TextItem("Aucune donnée disponible", color=COLORS['text_tertiary'])
            text.setPos(0.5, 0.5)
            self.products_chart.addItem(text)

    def create_chart_container(self, title):
        """Crée un conteneur stylisé pour un graphique"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        
        main_layout = QVBoxLayout()
        container.setLayout(main_layout)
        main_layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        main_layout.addWidget(title_label)
        
        return container

    def build_kpi_card(self, title, value, change, change_desc, color):
        """Construit une carte KPI stylisée"""
        card = QFrame()
        card.setStyleSheet(get_kpi_card_style(color))
        card.setMinimumHeight(120)
        
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(18, 15, 18, 15)

        # Titre
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        card_layout.addWidget(title_label)

        # Valeur
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        card_layout.addWidget(value_label)

        # Description
        change_layout = QHBoxLayout()
        change_layout.setSpacing(5)
        
        change_label = QLabel(change)
        change_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        change_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        desc_label = QLabel(change_desc)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        change_layout.addWidget(change_label)
        change_layout.addWidget(desc_label)
        change_layout.addStretch()
        
        card_layout.addLayout(change_layout)

        return card

    def refresh(self):
        """Rafraîchit toutes les données"""
        # Effacer la grille KPI
        kpi_grid = self.layout().itemAt(2)
        while kpi_grid.count():
            child = kpi_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Recharger
        self.load_kpi_cards(kpi_grid)
        self.load_charts_data()