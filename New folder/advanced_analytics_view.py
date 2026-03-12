from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from datetime import datetime
from db_manager import get_database
from ui_components import (
    BG_PAGE, BG_CARD, C_BLUE, C_GREEN, C_AMBER, C_CYAN, C_VIOLET,
    TXT_PRI, TXT_SEC,
    _card, _lbl, _styled_plot
)


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