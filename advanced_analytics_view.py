from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from datetime import datetime
from db_manager import get_database

# Reuse your theme
BG_PAGE  = "#0F1117"
BG_CARD  = "#1A1D27"
BORDER   = "rgba(255,255,255,0.07)"
TXT_PRI  = "#F1F5F9"
TXT_SEC  = "rgba(255,255,255,0.45)"

C_BLUE   = "#3B82F6"
C_GREEN  = "#10B981"
C_AMBER  = "#F59E0B"
C_CYAN   = "#06B6D4"
C_VIOLET = "#8B5CF6"


def _card():
    f = QFrame()
    f.setStyleSheet(f"""
        background:{BG_CARD};
        border-radius:14px;
        border:1px solid {BORDER};
    """)
    return f


def _lbl(text, size, bold=False, color=TXT_PRI):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color}; background:transparent;")
    return l


def _styled_plot(height=260):
    plot = pg.PlotWidget()
    plot.setBackground("#13151F")
    plot.setMinimumHeight(height)
    plot.showGrid(x=True, y=True, alpha=0.08)
    plot.getPlotItem().layout.setContentsMargins(4, 4, 12, 4)
    return plot


class AdvancedAnalyticsPage(QWidget):
    """A full new tab for extended analytics."""
    def __init__(self):
        super().__init__()

        self.db = get_database()
        self.setStyleSheet(f"background:{BG_PAGE};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        # Title
        layout.addWidget(_lbl("Advanced Analytics", 24, bold=True))
        layout.addWidget(_lbl("Deep insights into your sales data", 11, color=TXT_SEC))

        # Build each chart block
        layout.addWidget(self._build_sales_by_client())
        layout.addWidget(self._build_sales_by_product())
        layout.addWidget(self._build_weekly_sales())

    # ----------------------------------------------------------
    # SALES BY CLIENT
    # ----------------------------------------------------------
    def _build_sales_by_client(self):
        card = _card()
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)

        lay.addWidget(_lbl("Sales by Client", 14, bold=True))

        plot = _styled_plot()
        lay.addWidget(plot)

        data = self.db.get_top_clients(limit=20) or []
        names = [d["name"] for d in data]
        values = [float(d["total_amount"]) for d in data]

        colors = [C_VIOLET, C_BLUE, C_CYAN, C_AMBER, C_GREEN]

        for i, v in enumerate(values):
            plot.addItem(
                pg.BarGraphItem(
                    x=[i], height=[v], width=0.6,
                    brush=pg.mkBrush(colors[i % len(colors)] + "AA")
                )
            )

        plot.getAxis("bottom").setTicks(
            [list(zip(range(len(names)), [n[:12] for n in names]))]
        )
        plot.setXRange(-0.5, len(values) - 0.5)

        return card

    # ----------------------------------------------------------
    # SALES BY PRODUCT
    # ----------------------------------------------------------
    def _build_sales_by_product(self):
        card = _card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)

        lay.addWidget(_lbl("Sales by Product", 14, bold=True))

        plot = _styled_plot()
        lay.addWidget(plot)

        data = self.db.get_top_products(limit=20) or []
        names = [d["name"] for d in data]
        values = [float(d["total_sales"]) for d in data]

        colors = [C_AMBER, C_BLUE, C_GREEN, C_VIOLET, C_CYAN]

        for i, v in enumerate(values):
            plot.addItem(
                pg.BarGraphItem(
                    x=[i], height=[v], width=0.6,
                    brush=pg.mkBrush(colors[i % len(colors)] + "AA")
                )
            )

        plot.getAxis("bottom").setTicks(
            [list(zip(range(len(names)), [n[:12] for n in names]))]
        )
        plot.setXRange(-0.5, len(values) - 0.5)

        return card

    # ----------------------------------------------------------
    # WEEKLY SALES (52 weeks)
    # ----------------------------------------------------------
    def _build_weekly_sales(self):
        card = _card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)

        lay.addWidget(_lbl("Weekly Sales", 14, bold=True))

        plot = _styled_plot()
        lay.addWidget(plot)

        year = datetime.now().year
        data = self.db.get_sale_by_id(year) or []

        weeks = list(range(1, 53))
        values = [0] * 52

        for row in data:
            w = int(row.get("week", 0))
            if 1 <= w <= 52:
                values[w - 1] = float(row.get("total", 0))

        pen = pg.mkPen(color=C_GREEN, width=2)
        brush = pg.mkBrush(color=(16,185,129,40))

        plot.plot(
            weeks, values,
            pen=pen,
            fillLevel=0,
            brush=brush,
            symbol='o', symbolSize=5, symbolBrush=C_GREEN
        )

        return card
    """
    
    from advanced_analytics_view import AdvancedAnalyticsPage   # ← IMPORTANT
    
     # ❗ NOUVEL ONGLET — ADVANCED ANALYTICS ❗
        self.add_page("advanced", AdvancedAnalyticsPage(), "📊 Advanced Analytics")

        # Page par défaut
        self.show_page("dashboard")
        
        
        
         # ─────────────────────────────────────────────────────────
    # Ajouter une page dans la stack
    # ─────────────────────────────────────────────────────────
    def add_page(self, key, widget, title):
        self.pages[key] = widget
        self.stack.addWidget(widget)

    # ─────────────────────────────────────────────────────────
    # Changer de page
    # ─────────────────────────────────────────────────────────
    def show_page(self, key):
        if key not in self.pages:
            return
        page = self.pages[key]
        self.stack.setCurrentWidget(page)

        # Activer le bouton correspondant
        for k, btn in self.buttons.items():
            if k == key:
                btn.activate()
            else:
                btn.deactivate() """