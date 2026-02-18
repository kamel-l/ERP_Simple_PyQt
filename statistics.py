from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from styles import COLORS
from db_manager import get_database
from datetime import datetime


class StatisticsPage(QWidget):
    """Page Statistiques entièrement corrigée et stable"""

    def __init__(self):
        super().__init__()

        self.db = get_database()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ================= HEADER =================
        title = QLabel("📈 Statistiques & Analyses")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        main_layout.addWidget(title)

        subtitle = QLabel("Analysez les performances de votre entreprise")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        main_layout.addWidget(subtitle)

        # ================= KPI =================
        stats = self.db.get_statistics() or {}

        sales_total = float(stats.get('sales_total', 0))
        purchases_total = float(stats.get('purchases_total', 0))
        total_clients = int(stats.get('total_clients', 0))
        stock_value = float(stats.get('stock_value', 0))
        total_products = int(stats.get('total_products', 0))

        profit = sales_total - purchases_total
        profit_percent = (profit / sales_total * 100) if sales_total > 0 else 0

        low_stock_count = len(self.db.get_low_stock_products() or [])

        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        kpi_layout.addWidget(self.create_kpi_card("💰 Ventes Totales", f"{sales_total:,.0f} DA", "Total ventes", COLORS['primary']))
        kpi_layout.addWidget(self.create_kpi_card("🛒 Achats Totaux", f"{purchases_total:,.0f} DA", "Total achats", COLORS['warning']))
        kpi_layout.addWidget(self.create_kpi_card("📈 Bénéfice Net", f"{profit:,.0f} DA", f"{profit_percent:.1f}% marge", COLORS['success']))
        kpi_layout.addWidget(self.create_kpi_card("👥 Clients", str(total_clients), "Clients actifs", COLORS['secondary']))
        kpi_layout.addWidget(self.create_kpi_card("📦 Valeur Stock", f"{stock_value:,.0f} DA", f"{total_products} produits", COLORS['info']))
        kpi_layout.addWidget(self.create_kpi_card("⚠️ Stock Faible", str(low_stock_count), "Produits critiques", COLORS['danger']))

        main_layout.addLayout(kpi_layout)

        # ================= GRAPH VENTES =================
        self.sales_plot = self.create_plot("📊 Évolution des Ventes Mensuelles", main_layout)

        # ================= GRAPH GRID =================
        grid = QGridLayout()
        grid.setSpacing(15)

        self.clients_plot = self.create_plot("👥 Top 5 Clients", grid, 0, 0)
        self.products_plot = self.create_plot("📦 Top 5 Produits", grid, 0, 1)

        main_layout.addLayout(grid)

        # Charger les données
        self.refresh()

    # ==========================================================

    def create_kpi_card(self, title, value, subtitle, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                border-left: 4px solid {color};
                padding: 10px;
            }}
        """)
        card.setMinimumWidth(150)

        layout = QVBoxLayout(card)

        t = QLabel(title)
        t.setStyleSheet(f"color: {COLORS['text_tertiary']}; font-size: 11px;")
        layout.addWidget(t)

        v = QLabel(value)
        v.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
        layout.addWidget(v)

        s = QLabel(subtitle)
        s.setStyleSheet(f"color: {COLORS['text_tertiary']}; font-size: 10px;")
        layout.addWidget(s)

        return card

    # ==========================================================

    def create_plot(self, title, parent_layout, row=None, col=None):
        card = QFrame()
        card.setStyleSheet(f"background: {COLORS['bg_card']}; border-radius: 10px;")

        layout = QVBoxLayout(card)

        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(lbl)

        plot = pg.PlotWidget()
        plot.setBackground(COLORS['bg_dark'])
        plot.setMinimumHeight(250)
        plot.showGrid(x=True, y=True, alpha=0.3)
        plot.setMouseEnabled(x=False, y=False)
        plot.hideButtons()

        layout.addWidget(plot)

        if isinstance(parent_layout, QGridLayout):
            parent_layout.addWidget(card, row, col)
        else:
            parent_layout.addWidget(card)

        return plot

    # ==========================================================

    def refresh(self):
        """Recharge toutes les données graphiques"""
        self.load_sales()
        self.load_top_clients()
        self.load_top_products()

    # ==========================================================

    def load_sales(self):
        self.sales_plot.clear()

        year = datetime.now().year
        data = self.db.get_sales_by_month(year) or []

        months = list(range(12))
        values = [0] * 12

        for row in data:
            try:
                idx = int(row.get("month", 0)) - 1
                if 0 <= idx < 12:
                    values[idx] = float(row.get("total", 0))
            except Exception:
                pass

        if any(values):
            pen = pg.mkPen(color=COLORS['primary'], width=3)
            self.sales_plot.plot(months, values, pen=pen, symbol='o', symbolSize=7)
        else:
            txt = pg.TextItem("Aucune donnée", color=COLORS['text_tertiary'])
            txt.setPos(5, 1)
            self.sales_plot.addItem(txt)

    # ==========================================================

    def load_top_clients(self):
        self.clients_plot.clear()

        data = self.db.get_top_clients(limit=5) or []
        data = [c for c in data if c.get("total_amount", 0) > 0]

        if not data:
            txt = pg.TextItem("Aucun client", color=COLORS['text_tertiary'])
            txt.setPos(1, 1)
            self.clients_plot.addItem(txt)
            return

        names = [c.get("name", "")[:10] for c in data]
        values = [c.get("total_amount", 0) for c in data]

        for i, val in enumerate(values):
            bar = pg.BarGraphItem(x=i, height=val, width=0.6, brush=COLORS['primary'])
            self.clients_plot.addItem(bar)

        # afficher les noms sur l'axe X
        self.clients_plot.getAxis('bottom').setTicks([list(zip(range(len(names)), names))])

    # ==========================================================

    def load_top_products(self):
        self.products_plot.clear()

        data = self.db.get_top_products(limit=5) or []
        data = [p for p in data if p.get("total_quantity", 0) > 0]

        if not data:
            txt = pg.TextItem("Aucun produit", color=COLORS['text_tertiary'])
            txt.setPos(1, 1)
            self.products_plot.addItem(txt)
            return

        names = [p.get("name", "")[:10] for p in data]
        values = [p.get("total_quantity", 0) for p in data]

        for i, val in enumerate(values):
            bar = pg.BarGraphItem(x=i, height=val, width=0.6, brush=COLORS['success'])
            self.products_plot.addItem(bar)

        # afficher les noms sur l'axe X
        self.products_plot.getAxis('bottom').setTicks([list(zip(range(len(names)), names))])
        self.products_plot.clear()

        data = self.db.get_top_products(limit=5) or []
        data = [p for p in data if p.get("total_quantity", 0) > 0]

        if not data:
            txt = pg.TextItem("Aucun produit", color=COLORS['text_tertiary'])
            txt.setPos(1, 1)
            self.products_plot.addItem(txt)
            return

        for i, p in enumerate(data):
            bar = pg.BarGraphItem(x=i, height=p["total_quantity"], width=0.6, brush=COLORS['success'])
            self.products_plot.addItem(bar)
