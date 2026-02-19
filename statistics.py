from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGridLayout, QSizePolicy
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from styles import COLORS
from db_manager import get_database
from datetime import datetime


class StatisticsPage(QWidget):
    """Dashboard SaaS compact et moderne"""

    def __init__(self):
        super().__init__()

        self.db = get_database()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 15, 20, 15)

        # ================= HEADER =================
        header_layout = QVBoxLayout()

        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        subtitle = QLabel("Analyse rapide de votre activité")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']};")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        # ================= KPI CARDS =================
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(12)
        main_layout.addLayout(self.kpi_layout)

        # ================= SALES CHART =================
        self.sales_plot = self.create_plot_card("Revenus mensuels", main_layout, height=220)

        # ================= LOWER GRID =================
        grid = QGridLayout()
        grid.setSpacing(12)

        self.clients_plot = self.create_plot_card("Top clients", grid, 0, 0, height=200)
        self.products_plot = self.create_plot_card("Top produits", grid, 0, 1, height=200)

        main_layout.addLayout(grid)

        self.refresh()

    # ==========================================================

    def create_kpi_card(self, title, value, subtitle, color):
        """Carte KPI compacte"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMaximumHeight(90)

        layout = QVBoxLayout(card)
        layout.setSpacing(4)

        t = QLabel(title)
        t.setStyleSheet(f"color: {COLORS['text_tertiary']}; font-size: 10px;")

        v = QLabel(value)
        v.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 700;")

        s = QLabel(subtitle)
        s.setStyleSheet(f"color: {COLORS['text_tertiary']}; font-size: 9px;")

        layout.addWidget(t)
        layout.addWidget(v)
        layout.addWidget(s)

        return card

    # ==========================================================

    def create_plot_card(self, title, parent_layout, row=None, col=None, height=200):
        """Carte graphique compacte"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 14px;
                padding: 10px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(6)

        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        plot = pg.PlotWidget()
        plot.setBackground(COLORS['bg_card'])
        plot.setMinimumHeight(height)
        plot.showGrid(x=True, y=True, alpha=0.12)
        plot.setMouseEnabled(x=False, y=False)
        plot.hideButtons()

        layout.addWidget(lbl)
        layout.addWidget(plot)

        if isinstance(parent_layout, QGridLayout):
            parent_layout.addWidget(card, row, col)
        else:
            parent_layout.addWidget(card)

        return plot

    # ==========================================================

    def refresh(self):
        self.load_kpis()
        self.load_sales()
        self.load_top_clients()
        self.load_top_products()

    # ==========================================================

    def load_kpis(self):
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        stats = self.db.get_statistics() or {}

        sales_total = float(stats.get('sales_total', 0))
        purchases_total = float(stats.get('purchases_total', 0))
        clients = int(stats.get('total_clients', 0))
        stock_value = float(stats.get('stock_value', 0))

        profit = sales_total - purchases_total
        margin = (profit / sales_total * 100) if sales_total > 0 else 0
        low_stock = len(self.db.get_low_stock_products() or [])

        self.kpi_layout.addWidget(self.create_kpi_card("Revenus", f"{sales_total:,.0f} DA", "Ventes", COLORS['primary']))
        self.kpi_layout.addWidget(self.create_kpi_card("Dépenses", f"{purchases_total:,.0f} DA", "Achats", COLORS['warning']))
        self.kpi_layout.addWidget(self.create_kpi_card("Profit", f"{profit:,.0f} DA", f"{margin:.0f}%", COLORS['success']))
        self.kpi_layout.addWidget(self.create_kpi_card("Clients", str(clients), "Actifs", COLORS['secondary']))
        self.kpi_layout.addWidget(self.create_kpi_card("Stock", f"{stock_value:,.0f} DA", "Valeur", COLORS['info']))
        self.kpi_layout.addWidget(self.create_kpi_card("Alertes", str(low_stock), "Faible", COLORS['danger']))

    # ==========================================================

    def load_sales(self):
        self.sales_plot.clear()

        year = datetime.now().year
        data = self.db.get_sales_by_month(year) or []

        months = list(range(1, 13))
        values = [0] * 12

        for row in data:
            try:
                idx = int(row.get("month", 0)) - 1
                if 0 <= idx < 12:
                    values[idx] = float(row.get("total", 0))
            except Exception:
                pass

        if any(values):
            pen = pg.mkPen(color=COLORS['primary'], width=2)
            self.sales_plot.plot(months, values, pen=pen, symbol='o', symbolSize=5)
        else:
            txt = pg.TextItem("Aucune donnée", color=COLORS['text_tertiary'])
            txt.setPos(6, 1)
            self.sales_plot.addItem(txt)

    # ==========================================================

    def load_top_clients(self):
        self.clients_plot.clear()

        data = self.db.get_top_clients(limit=5) or []
        data = [c for c in data if c.get("total_amount", 0) > 0]

        if not data:
            txt = pg.TextItem("Aucun", color=COLORS['text_tertiary'])
            txt.setPos(0, 0)
            self.clients_plot.addItem(txt)
            return

        names = [c.get("name", "")[:10] for c in data]
        values = [float(c.get("total_amount", 0)) for c in data]

        x_positions = list(range(len(values)))

        bars = pg.BarGraphItem(x=x_positions, height=values, width=0.4, brush=COLORS['primary'])
        self.clients_plot.addItem(bars)

        # afficher les noms sur l'axe X
        axis = self.clients_plot.getAxis('bottom')
        axis.setTicks([list(zip(x_positions, names))])

        # ajuster les limites pour voir les barres correctement
        self.clients_plot.setXRange(-0.5, len(values) - 0.5)
        self.clients_plot.setYRange(0, max(values) * 1.2)

    # ==========================================================

    def load_top_products(self):
        self.products_plot.clear()

        data = self.db.get_top_products(limit=5) or []
        data = [p for p in data if p.get("total_quantity", 0) > 0]

        if not data:
            txt = pg.TextItem("Aucun", color=COLORS['text_tertiary'])
            txt.setPos(0, 0)
            self.products_plot.addItem(txt)
            return

        names = [p.get("name", "")[:10] for p in data]
        values = [float(p.get("total_quantity", 0)) for p in data]

        x_positions = list(range(len(values)))

        bars = pg.BarGraphItem(x=x_positions, height=values, width=0.4, brush=COLORS['success'])
        self.products_plot.addItem(bars)

        # afficher les noms sur l'axe X
        axis = self.products_plot.getAxis('bottom')
        axis.setTicks([list(zip(x_positions, names))])

        # ajuster les limites
        self.products_plot.setXRange(-0.5, len(values) - 0.5)
        self.products_plot.setYRange(0, max(values) * 1.2)

        self.products_plot.clear()

        data = self.db.get_top_products(limit=5) or []
        data = [p for p in data if p.get("total_quantity", 0) > 0]

        if not data:
            txt = pg.TextItem("Aucun", color=COLORS['text_tertiary'])
            txt.setPos(1, 1)
            self.products_plot.addItem(txt)
            return

        names = [p.get("name", "")[:10] for p in data]
        values = [p.get("total_quantity", 0) for p in data]

        bars = pg.BarGraphItem(x=list(range(len(values))), height=values, width=0.4, brush=COLORS['success'])
        self.products_plot.addItem(bars)
        self.products_plot.getAxis('bottom').setTicks([list(zip(range(len(names)), names))])
