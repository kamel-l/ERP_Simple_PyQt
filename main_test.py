# ─────────────────────────────────────────────────────────────
#  main.py — PARTIE 1 / 3
# ─────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy, QStackedWidget, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from products import ProductsPage
from clients import ClientsPage
from purchases import PurchasesPage
from sales import SalesPage
from dashboard import DashboardPage
from sales_history import SalesHistoryPage
from statistics_view import StatisticsPage
from advanced_analytics_view import AdvancedAnalyticsPage   # ← IMPORTANT

# Couleurs globales
BG_MAIN   = "#0F1117"
BG_SIDEBAR = "#1A1D27"
BORDER     = "rgba(255,255,255,0.07)"
TXT_PRI    = "#F1F5F9"
TXT_SEC    = "rgba(255,255,255,0.55)"
ACCENT     = "#3B82F6"


# ─────────────────────────────────────────────────────────────
#  BOUTON DANS LA SIDEBAR
# ─────────────────────────────────────────────────────────────
class SidebarButton(QFrame):
    def __init__(self, icon, text, key, color="#3B82F6"):
        super().__init__()
        self.key = key
        self.color = color

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-radius: 8px;
            }}
            QLabel {{
                color: {TXT_PRI};
                background: transparent;
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)

        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setFont(QFont("Segoe UI Emoji", 16))
        lay.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(text)
        self.text_lbl.setFont(QFont("Segoe UI", 11))
        lay.addWidget(self.text_lbl)

        lay.addStretch()

    def activate(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {self.color}22;
                border-left: 4px solid {self.color};
                border-radius: 6px;
            }}
            QLabel {{
                color: {TXT_PRI};
            }}
        """)

    def deactivate(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-left: 4px solid transparent;
                border-radius: 6px;
            }}
            QLabel {{
                color: {TXT_PRI};
            }}
        """)


# ─────────────────────────────────────────────────────────────
#  FENÊTRE PRINCIPALE
# ─────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERP Simple — Interface Moderne")
        self.resize(1200, 750)
        self.setStyleSheet(f"background:{BG_MAIN};")

        # Layout général
        main_layout = QHBoxLayout()
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Pages
        self.pages = {}
        self.buttons = {}

        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar, 0)

        # Stack des pages
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        

        self.add_page("dashboard", DashboardPage(), "🧭 Dashboard")
        self.add_page("products", ProductsPage(), "📦 Produits")
        self.add_page("clients", ClientsPage(), "👥 Clients")
        self.add_page("purchases", PurchasesPage(), "👜 Achats")
        self.add_page("sales", SalesPage(), "🛒 Ventes")
        self.add_page("history", SalesHistoryPage(), "🗂 Historique")
        self.add_page("statistics", StatisticsPage(), "📈 Statistiques")

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
                btn.deactivate()

    # ─────────────────────────────────────────────────────────
    # Création de la Sidebar
    # ─────────────────────────────────────────────────────────
    def create_sidebar(self):
        frame = QFrame()
        frame.setFixedWidth(220)
        frame.setStyleSheet(f"""
            background: {BG_SIDEBAR};
            border-right: 1px solid {BORDER};
        """)

        lay = QVBoxLayout(frame)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Logo
        title = QLabel("ERP Simple")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{TXT_PRI};")
        lay.addWidget(title)
        lay.addSpacing(10)

        # GROUPES
        lay.addWidget(self.group_label("GESTION"))

        manage_items = [
            ("dashboard", "🧭", "Dashboard", "#3B82F6"),
            ("products",  "📦", "Produits",  "#06B6D4"),
            ("clients",   "👥", "Clients",   "#06B6D4"),
            ("purchases", "👜", "Achats",    "#10B981"),
            ("sales",     "🛒", "Ventes",    "#F59E0B"),
        ]

        for key, icon, text, color in manage_items:
            btn = SidebarButton(icon, text, key, color)
            btn.mousePressEvent = lambda e, k=key: self.show_page(k)
            lay.addWidget(btn)
            self.buttons[key] = btn

        lay.addSpacing(10)
        lay.addWidget(self.group_label("RAPPORTS"))

        report_items = [
            ("history",    "🗂", "Historique Ventes",    "#06B6D4"),
            ("statistics", "📈", "Statistiques",         "#3B82F6"),
            ("advanced",   "📊", "Advanced Analytics",   "#10B981"),  # ← NOUVEAU
        ]

        for key, icon, text, color in report_items:
            btn = SidebarButton(icon, text, key, color)
            btn.mousePressEvent = lambda e, k=key: self.show_page(k)
            lay.addWidget(btn)
            self.buttons[key] = btn

        lay.addStretch()
        return frame

    def group_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color:{TXT_SEC}; padding-left:4px;")
        return lbl
    
    # ─────────────────────────────────────────────────────────────
#  main.py — PARTIE 2 / 3
# ─────────────────────────────────────────────────────────────

    # Petite amélioration : rendre les pages scrollables automatiquement
    def make_scroll_area(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,0.25);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255,255,255,0.35);
            }
        """)
        scroll.setWidget(widget)
        return scroll

    # Override resizeEvent pour adapter les pages si besoin
    def resizeEvent(self, event):
        try:
            if hasattr(self.stack.currentWidget(), "updateGeometry"):
                self.stack.currentWidget().updateGeometry()
        except:
            pass
        super().resizeEvent(event)

    # Override showEvent pour appliquer le style
    def showEvent(self, event):
        try:
            if hasattr(self.stack.currentWidget(), "refresh"):
                self.stack.currentWidget().refresh()
        except:
            pass
        super().showEvent(event)
        
    # ─────────────────────────────────────────────────────────────
#  main.py — PARTIE 3 / 3 (FIN DU FICHIER)
# ─────────────────────────────────────────────────────────────

def main():
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()    