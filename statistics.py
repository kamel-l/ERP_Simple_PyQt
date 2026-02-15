from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import random
from styles import COLORS, get_kpi_card_style

class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # ------------------- HEADER -------------------
        header_layout = QVBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("📈 Statistiques & Analyses")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        header_layout.addWidget(title)

        subtitle = QLabel("Analysez les performances de votre entreprise")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        header_layout.addWidget(subtitle)

        # ------------------- KPI CARDS -------------------
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(15)
        layout.addLayout(kpi_grid)

        # Première ligne
        kpi_grid.addWidget(
            self.build_kpi_card(
                "💰 Ventes Totales",
                "120 000 DA",
                "+12.5% vs mois dernier",
                COLORS['primary']
            ), 0, 0
        )
        kpi_grid.addWidget(
            self.build_kpi_card(
                "🛒 Achats Totaux",
                "37 000 DA",
                "-5.2% optimisation",
                COLORS['warning']
            ), 0, 1
        )
        kpi_grid.addWidget(
            self.build_kpi_card(
                "📈 Bénéfice Net",
                "83 000 DA",
                "+18.3% croissance",
                COLORS['success']
            ), 0, 2
        )

        # Deuxième ligne
        kpi_grid.addWidget(
            self.build_kpi_card(
                "👥 Clients Actifs",
                "59",
                "+7 nouveaux",
                COLORS['secondary']
            ), 1, 0
        )
        kpi_grid.addWidget(
            self.build_kpi_card(
                "📦 Valeur Stock",
                "200 000 DA",
                "1,250 articles",
                COLORS['info']
            ), 1, 1
        )
        kpi_grid.addWidget(
            self.build_kpi_card(
                "🎯 Objectif Mensuel",
                "85%",
                "17 000 DA restants",
                COLORS['danger']
            ), 1, 2
        )

        # ------------------- GRAPHIQUES -------------------
        
        # Section Ventes Mensuelles
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
        
        # Style de la grille
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

        # Ventes vs Achats
        comparison_container = self.create_chart_container("💰 Ventes vs Achats")
        comparison_layout = QVBoxLayout()
        comparison_container.setLayout(comparison_layout)
        
        self.comparison_chart = pg.PlotWidget()
        self.comparison_chart.setBackground(COLORS['bg_dark'])
        self.comparison_chart.showGrid(x=True, y=True, alpha=0.3)
        self.comparison_chart.setMinimumHeight(220)
        self.comparison_chart.getAxis('left').setPen(pg.mkPen(color=COLORS['border'], width=1))
        self.comparison_chart.getAxis('bottom').setPen(pg.mkPen(color=COLORS['border'], width=1))
        self.comparison_chart.getAxis('left').setTextPen(COLORS['text_tertiary'])
        self.comparison_chart.getAxis('bottom').setTextPen(COLORS['text_tertiary'])
        
        # Légende
        self.comparison_chart.addLegend(offset=(10, 10))
        
        comparison_layout.addWidget(self.comparison_chart)
        charts_grid.addWidget(comparison_container, 0, 1)

        # ------------------- Charger Données Demo -------------------
        self.load_demo_data()

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
        
        # Titre
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        main_layout.addWidget(title_label)
        
        return container

    def build_kpi_card(self, title, value, description, color):
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
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        card_layout.addWidget(desc_label)

        return card

    # ------------------- CHARGER DONNÉES DEMO -------------------
    def load_demo_data(self):
        # Ventes Mensuelles
        months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", 
                 "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        sales = [random.randint(5000, 20000) for _ in range(12)]
        
        # Ligne avec gradient
        self.sales_chart.plot(
            list(range(12)), 
            sales, 
            pen=pg.mkPen(color=COLORS['primary'], width=3),
            symbol='o',
            symbolSize=8,
            symbolBrush=COLORS['primary'],
            name="Ventes"
        )
        
        # Remplissage sous la courbe
        fillBrush = pg.mkBrush(COLORS['primary'] + '40')  # Transparence
        self.sales_chart.plot(
            list(range(12)),
            sales,
            fillLevel=0,
            fillBrush=fillBrush
        )
        
        self.sales_chart.getAxis('bottom').setTicks([list(zip(range(12), months))])

        # Top Clients (Graphique à barres)
        customers = ["John", "Alice", "Entreprise X", "Bob", "Marie"]
        values = sorted([random.randint(1000, 10000) for _ in customers], reverse=True)
        
        # Créer des barres avec des couleurs dégradées
        colors = [COLORS['primary'], COLORS['secondary'], COLORS['success'], 
                 COLORS['warning'], COLORS['info']]
        
        x = list(range(len(customers)))
        for i, (val, color) in enumerate(zip(values, colors)):
            bg = pg.BarGraphItem(
                x=[i], 
                height=[val], 
                width=0.6, 
                brush=color
            )
            self.customers_chart.addItem(bg)
        
        self.customers_chart.getAxis('bottom').setTicks([list(zip(range(len(customers)), customers))])

        # Ventes vs Achats (Comparaison)
        sales_values = [random.randint(5000, 20000) for _ in range(12)]
        purchase_values = [random.randint(3000, 15000) for _ in range(12)]
        
        self.comparison_chart.plot(
            list(range(12)), 
            sales_values, 
            pen=pg.mkPen(color=COLORS['success'], width=3),
            symbol='o',
            symbolSize=6,
            symbolBrush=COLORS['success'],
            name="Ventes"
        )
        
        self.comparison_chart.plot(
            list(range(12)), 
            purchase_values, 
            pen=pg.mkPen(color=COLORS['danger'], width=3),
            symbol='s',
            symbolSize=6,
            symbolBrush=COLORS['danger'],
            name="Achats"
        )
        
        self.comparison_chart.getAxis('bottom').setTicks([list(zip(range(12), months))])