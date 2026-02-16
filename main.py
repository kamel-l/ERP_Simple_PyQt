"""
Application ERP Simple - Fichier Principal
Système de gestion complet avec tous les modules intégrés
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel,
    QMessageBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import qdarktheme

# Importer le système de styles
from styles import COLORS, BUTTON_STYLES

# Importer les pages améliorées
from dashboard import DashboardPage
from clients import ClientsPage
from products import ProductsPage
from sales import SalesPage
from purchases import PurchasesPage
from settings import SettingsPage
from statistics import StatisticsPage
from sales_history import SalesHistoryPage
from PyQt6.QtGui import QAction
from clean_erp_data import run_full_cleanup
from db_manager import get_database



class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        
        self.db = get_database()
        print("✅ Base de données initialisée")
        self.setWindowTitle("🏢 Système de Gestion ERP - Version Professionnelle")
        self.setMinimumSize(1400, 800)
        
        # Appliquer le thème sombre
        # qdarktheme.setup_theme("dark")

        # Créer les pages
        self.clients_page = ClientsPage()
        self.sales_page = SalesPage()
        
        # IMPORTANT : Connecter le signal
        self.clients_page.client_added.connect(self.sales_page.load_clients)
        
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
        self.stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {COLORS['bg_dark']};
            }}
        """)
        
        # Ajouter les pages
        self.pages = {}
        self.add_page("dashboard", DashboardPage(), "📊 Tableau de Bord")
        self.add_page("clients", ClientsPage(), "👥 Clients")
        self.add_page("products", ProductsPage(), "📦 Produits")
        self.add_page("sales", SalesPage(), "💰 Ventes")
        self.add_page("purchases", PurchasesPage(), "🛒 Achats")
        self.add_page("history", SalesHistoryPage(), "📊 Historique")
        self.add_page("statistics", StatisticsPage(), "📈 Statistiques")
        self.add_page("settings", SettingsPage(), "⚙️ Paramètres")
        # New ERP Cleanup Menu
        cleanup_menu = self.menuBar().addMenu("ERP Tools")

        clean_action = QAction("Nettoyer les données ERP", self)
        clean_action.triggered.connect(self.run_erp_cleanup)

        cleanup_menu.addAction(clean_action)

        
        main_layout.addWidget(self.stack)
        
        # Afficher le dashboard par défaut
        self.show_page("dashboard")
        # Créer les pages
        clients_page = ClientsPage()
        sales_page = SalesPage()

        # AJOUTER CETTE LIGNE :
        clients_page.client_added.connect(sales_page.load_clients)


    def add_page(self, key, page, title):
        """Ajoute une page au stack"""
        index = self.stack.count()
        self.stack.addWidget(page)
        self.pages[key] = {
            'index': index,
            'page': page,
            'title': title
        }
    
    def create_sidebar(self):
        """Crée la barre latérale de navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_medium']}, stop:1 {COLORS['bg_dark']});
                border-right: 2px solid {COLORS['border']};
            }}
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 20, 10, 20)
        
        # ================= LOGO / TITRE =================
        logo_container = self.create_logo()
        layout.addWidget(logo_container)
        
        # ================= NAVIGATION BUTTONS =================
        nav_section = QLabel("📱 NAVIGATION")
        nav_section.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        nav_section.setStyleSheet(f"color: {COLORS['text_tertiary']}; padding: 10px 5px;")
        layout.addWidget(nav_section)
        
        # Boutons de navigation principaux
        nav_buttons = [
            ("📊 Tableau de Bord", "dashboard", COLORS['primary']),
            ("👥 Clients", "clients", COLORS['secondary']),
            ("📦 Produits", "products", COLORS['success']),
            ("💰 Point de Vente", "sales", COLORS['success']),
            ("🛒 Achats", "purchases", COLORS['warning']),
        ]
        
        self.nav_buttons = {}
        for text, key, color in nav_buttons:
            btn = self.create_nav_button(text, key, color)
            layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; margin: 10px 0;")
        layout.addWidget(separator)
        
        # Section Rapports
        reports_section = QLabel("📊 RAPPORTS")
        reports_section.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        reports_section.setStyleSheet(f"color: {COLORS['text_tertiary']}; padding: 10px 5px;")
        layout.addWidget(reports_section)
        
        # Boutons rapports
        report_buttons = [
            ("📊 Historique Ventes", "history", COLORS['info']),
            ("📈 Statistiques", "statistics", COLORS['info']),
        ]
        
        for text, key, color in report_buttons:
            btn = self.create_nav_button(text, key, color)
            layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        layout.addStretch()
        
        # Séparateur
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet(f"background-color: {COLORS['border']}; margin: 10px 0;")
        layout.addWidget(separator2)
        
        # Section Système
        system_section = QLabel("⚙️ SYSTÈME")
        system_section.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        system_section.setStyleSheet(f"color: {COLORS['text_tertiary']}; padding: 10px 5px;")
        layout.addWidget(system_section)
        
        # Bouton Paramètres
        settings_btn = self.create_nav_button("⚙️ Paramètres", "settings", COLORS['text_tertiary'])
        layout.addWidget(settings_btn)
        self.nav_buttons["settings"] = settings_btn
        
        # ================= USER INFO =================
        user_info = self.create_user_info()
        layout.addWidget(user_info)
        
        # ================= ABOUT BUTTON =================
        about_btn = QPushButton("ℹ️ À propos")
        about_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_tertiary']};
                border: none;
                padding: 8px;
                text-align: center;
                font-size: 11px;
            }}
            QPushButton:hover {{
                color: {COLORS['primary']};
            }}
        """)
        about_btn.clicked.connect(self.show_about)
        about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(about_btn)
        
        return sidebar
    
    def create_logo(self):
        """Crée le logo/titre de l'application"""
        logo_container = QFrame()
        logo_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 15px;
            }}
        """)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setSpacing(5)
        
        app_name = QLabel("🏢 ERP Pro")
        app_name.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        app_name.setStyleSheet("color: white; border: none;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(app_name)
        
        app_subtitle = QLabel("Gestion Complète")
        app_subtitle.setFont(QFont("Segoe UI", 11))
        app_subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        app_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(app_subtitle)
        
        version = QLabel("v2.0.0")
        version.setFont(QFont("Segoe UI", 9))
        version.setStyleSheet("color: rgba(255, 255, 255, 0.6); border: none;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(version)
        
        return logo_container
    
    def create_nav_button(self, text, key, color):
        """Crée un bouton de navigation"""
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn.setMinimumHeight(50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Stocker les informations
        btn.setProperty("nav_key", key)
        btn.setProperty("nav_color", color)
        
        # Style par défaut
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_tertiary']};
                border: none;
                border-left: 4px solid transparent;
                border-radius: 8px;
                text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.05);
                color: {COLORS['text_primary']};
            }}
        """)
        
        # Connecter le clic
        btn.clicked.connect(lambda: self.show_page(key))
        
        return btn
    
    def create_user_info(self):
        """Crée la section d'informations utilisateur"""
        user_info = QFrame()
        user_info.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_light']};
                border-radius: 10px;
                padding: 15px;
                margin-top: 10px;
            }}
        """)
        user_layout = QVBoxLayout(user_info)
        user_layout.setSpacing(5)
        
        user_icon = QLabel("👤")
        user_icon.setFont(QFont("Segoe UI", 24))
        user_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_icon.setStyleSheet("border: none;")
        user_layout.addWidget(user_icon)
        
        user_name = QLabel("Administrateur")
        user_name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        user_name.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_layout.addWidget(user_name)
        
        user_role = QLabel("Accès Complet")
        user_role.setFont(QFont("Segoe UI", 10))
        user_role.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        user_role.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_layout.addWidget(user_role)
        
        return user_info
    
    def show_page(self, key):
        """Affiche une page spécifique"""
        if key in self.pages:
            page_info = self.pages[key]
            self.stack.setCurrentIndex(page_info['index'])
            self.update_nav_buttons(key)
            
            # Mettre à jour le titre de la fenêtre
            self.setWindowTitle(f"ERP Pro - {page_info['title']}")
    
    def update_nav_buttons(self, active_key):
        """Met à jour l'apparence des boutons de navigation"""
        for key, btn in self.nav_buttons.items():
            color = btn.property("nav_color")
            
            if key == active_key:
                # Bouton actif
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(10, 132, 255, 0.2), 
                            stop:1 transparent);
                        color: {color};
                        border: none;
                        border-left: 4px solid {color};
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 20px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(10, 132, 255, 0.3), 
                            stop:1 transparent);
                    }}
                """)
            else:
                # Bouton inactif
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {COLORS['text_tertiary']};
                        border: none;
                        border-left: 4px solid transparent;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 20px;
                    }}
                    QPushButton:hover {{
                        background: rgba(255, 255, 255, 0.05);
                        color: {COLORS['text_primary']};
                    }}
                """)
    def run_erp_cleanup(self):
        from clean_erp_data import run_full_cleanup
        try:
            run_full_cleanup()
            QMessageBox.information(
                self,
                "Succès",
                "Le nettoyage ERP a été effectué avec succès."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Une erreur est survenue lors du nettoyage:\n{e}"
            )

    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        about_text = """
        <h2 style='color: #0A84FF;'>🏢 ERP Pro - Version 2.0.0</h2>
        <p><b>Système de Gestion Professionnel</b></p>
        
        <h3>✨ Fonctionnalités:</h3>
        <ul>
            <li>📊 Tableau de bord avec statistiques en temps réel</li>
            <li>👥 Gestion complète des clients</li>
            <li>📦 Gestion des produits avec import/export CSV</li>
            <li>💰 Point de vente avec dialogue d'ajout professionnel</li>
            <li>🛒 Gestion des achats et fournisseurs</li>
            <li>📊 Historique des ventes avec filtres avancés</li>
            <li>📈 Statistiques et graphiques détaillés</li>
            <li>📄 Génération de factures PDF (à venir)</li>
            <li>📧 Envoi d'emails automatique (à venir)</li>
            <li>💳 Gestion des paiements multi-modes (à venir)</li>
        </ul>
        
        <h3>🛠️ Technologies:</h3>
        <ul>
            <li>PyQt6 - Interface graphique moderne</li>
            <li>QDarkTheme - Thème professionnel</li>
            <li>PyQtGraph - Graphiques interactifs</li>
            <li>ReportLab - Génération de PDF</li>
        </ul>
        
        <p style='margin-top: 20px;'>
        <b>Développé avec ❤️ pour une gestion efficace</b><br>
        © 2026 - Tous droits réservés
        </p>
        """
        
        QMessageBox.about(self, "À propos d'ERP Pro", about_text)


def main():
    """Point d'entrée de l'application"""
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("ERP Pro")
    app.setOrganizationName("Ma Société")
    app.setApplicationVersion("2.0.0")
    
    # Créer et afficher la fenêtre principale
    window = MainWindow()
    window.show()
    
    # Message de bienvenue dans la console
    print("=" * 60)
    print("🏢 ERP Pro - Version 2.0.0")
    print("=" * 60)
    print("✅ Application démarrée avec succès")
    print("📊 Modules chargés:")
    print("   - Tableau de bord")
    print("   - Gestion clients")
    print("   - Gestion produits (avec CSV)")
    print("   - Point de vente (avec dialogue)")
    print("   - Gestion achats")
    print("   - Historique des ventes")
    print("   - Statistiques")
    print("   - Paramètres")
    print("=" * 60)
    print("💡 Conseil: Commencez par ajouter des produits dans 'Produits'")
    print("=" * 60)
    
    # Lancer l'application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()