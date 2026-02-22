"""
Application ERP Pro - Fichier Principal
Système de gestion complet avec tous les modules intégrés
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel,
    QMessageBox
)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt

# Importer les fichiers de style et pages
from styles import COLORS
from dashboard import DashboardPage
from clients import ClientsPage
from products import ProductsPage
from sales import SalesPage
from purchases import PurchasesPage
from statistics import StatisticsPage
from settings import SettingsPage
# from sales_history import SalesHistoryPage
from clean_erp_data import run_full_cleanup
from db_manager import get_database
from db_manager import init_database


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application ERP Pro"""

    def __init__(self):
        super().__init__()

        self.db = get_database()
        print("✅ Base de données initialisée")
        self.setWindowTitle("🏢 ERP Pro - Version Professionnelle")
        self.setMinimumSize(1400, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ================= SIDEBAR =================
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # ================= CONTENT AREA =================
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"QStackedWidget {{ background-color: {COLORS['bg_dark']}; }}")
        main_layout.addWidget(self.stack)

        # Créer et ajouter les pages
        self.pages = {}
        self.init_pages()

        # Ajouter menu ERP Tools
        self.init_menu()

        # Afficher la page Dashboard par défaut
        self.show_page("dashboard")

    # ============================================================
    #                    INITIALISATION DES PAGES
    # ============================================================
    def init_pages(self):
        # Créer les instances des pages
        self.dashboard_page = DashboardPage()
        self.clients_page = ClientsPage()
        self.products_page = ProductsPage()
        self.sales_page = SalesPage()
        self.purchases_page = PurchasesPage()
        self.statistics_page = StatisticsPage()
        self.settings_page = SettingsPage()
        # self.sales_history_page = SalesHistoryPage()

        # Ajouter les pages au stack
        self.add_page("dashboard", self.dashboard_page, "📊 Tableau de Bord")
        self.add_page("clients", self.clients_page, "👥 Clients")
        self.add_page("products", self.products_page, "📦 Produits")
        self.add_page("sales", self.sales_page, "💰 Ventes")
        self.add_page("purchases", self.purchases_page, "🛒 Achats")
        self.add_page("history", self.sales_history_page, "📊 Historique Ventes")
        self.add_page("statistics", self.statistics_page, "📈 Statistiques")
        self.add_page("settings", self.settings_page, "⚙️ Paramètres")

    def add_page(self, key, page, title):
        """Ajoute une page au QStackedWidget"""
        index = self.stack.count()
        self.stack.addWidget(page)
        self.pages[key] = {"index": index, "page": page, "title": title}

    # ============================================================
    #                    CREATION SIDEBAR
    # ============================================================
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 {COLORS['bg_dark']});
                border-right: 2px solid {COLORS['border']};
            }}
        """)
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 20, 10, 20)

        # Logo
        layout.addWidget(self.create_logo())

        # Navigation principale
        nav_buttons = [
            ("📊 Tableau de Bord", "dashboard", COLORS['accent']),
            ("👥 Clients", "clients", COLORS['secondary']),
            ("📦 Produits", "products", COLORS['success']),
            ("💰 Ventes", "sales", COLORS['accent']),
            ("🛒 Achats", "purchases", COLORS['warning']),
            ("📊 Historique Ventes", "history", COLORS['info']),
            ("📈 Statistiques", "statistics", COLORS['info']),
            ("⚙️ Paramètres", "settings", COLORS['text_tertiary'])
        ]

        self.nav_buttons = {}
        for text, key, color in nav_buttons:
            btn = self.create_nav_button(text, key, color)
            layout.addWidget(btn)
            self.nav_buttons[key] = btn

        layout.addStretch()
        return sidebar

    def create_logo(self):
        logo = QLabel("🏢 ERP Pro")
        logo.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"color: {COLORS['accent']}; margin-bottom: 15px;")
        return logo

    def create_nav_button(self, text, key, color):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(50)
        btn.clicked.connect(lambda: self.show_page(key))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_tertiary']};
                border-left: 4px solid transparent;
                text-align: left;
                padding-left: 20px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.05);
                color: {COLORS['text_primary']};
            }}
        """)
        return btn

    # ============================================================
    #                    AFFICHER UNE PAGE
    # ============================================================
    def show_page(self, key):
        if key in self.pages:
            page_info = self.pages[key]
            self.stack.setCurrentIndex(page_info['index'])
            self.setWindowTitle(f"ERP Pro - {page_info['title']}")
            self.update_nav_buttons(key)

    def update_nav_buttons(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: rgba(0, 188, 212,0.2);
                        color: {COLORS['accent']};
                        border-left: 4px solid {COLORS['accent']};
                        text-align: left;
                        padding-left: 20px;
                        border-radius: 8px;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {COLORS['text_tertiary']};
                        border-left: 4px solid transparent;
                        text-align: left;
                        padding-left: 20px;
                        border-radius: 8px;
                    }}
                    QPushButton:hover {{
                        background: rgba(255,255,255,0.05);
                        color: {COLORS['text_primary']};
                    }}
                """)

    # ============================================================
    #                   MENU ERP TOOLS
    # ============================================================
    def init_menu(self):
        cleanup_menu = self.menuBar().addMenu("ERP Tools")
        clean_action = QAction("Nettoyer les données ERP", self)
        clean_action.triggered.connect(self.run_erp_cleanup)
        cleanup_menu.addAction(clean_action)

    def run_erp_cleanup(self):
        try:
            run_full_cleanup()
            QMessageBox.information(self, "Succès", "Le nettoyage ERP a été effectué avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue:\n{e}")


def main():
    init_database()
    app = QApplication(sys.argv)
    app.setApplicationName("ERP Pro")
    app.setOrganizationName("Ma Société")
    app.setApplicationVersion("2.0.0")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()