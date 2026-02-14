from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QListWidget, QListWidgetItem,
    QStackedWidget, QLabel, QVBoxLayout
)
from PyQt6.QtGui import QFont

from ui.dashboard import DashboardPage
from ui.products import ProductsPage
from ui.clients import ClientsPage
from ui.sales import SalesPage
from ui.purchases import PurchasesPage
from ui.statistics import StatisticsPage
from ui.settings import SettingsPage


class ERPApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ERP Simple — PyQt6 Professional Edition")
        self.resize(1400, 850)

        main_layout = QHBoxLayout(self)

        # --------------------------------------------
        # Sidebar
        # --------------------------------------------
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)

        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                color: white;
                font-size: 16px;
                padding-top: 20px;
                border: none;
            }
            QListWidget::item {
                height: 48px;
                padding-left: 20px;
            }
            QListWidget::item:selected {
                background-color: #0A84FF;
                color: white;
                border: none;
            }
        """)

        pages = [
            "📊 Dashboard",
            "📦 Products",
            "💰 Sales",
            "🧾 Purchases",
            "👥 Clients",
            "📈 Statistics",
            "⚙️ Settings"
        ]

        for p in pages:
            self.sidebar.addItem(QListWidgetItem(p))

        # --------------------------------------------
        # Pages Container (StackedWidget)
        # --------------------------------------------
        self.pages = QStackedWidget()

        self.pages.addWidget(DashboardPage())
        self.pages.addWidget(ProductsPage())
        self.pages.addWidget(SalesPage())
        self.pages.addWidget(PurchasesPage())
        self.pages.addWidget(ClientsPage())
        self.pages.addWidget(StatisticsPage())
        self.pages.addWidget(SettingsPage())

        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)
