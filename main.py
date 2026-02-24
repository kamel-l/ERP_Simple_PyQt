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
        
        # Connecter le signal : quand un client est ajouté/modifié/supprimé,
        # la liste dans la page Ventes se rafraîchit automatiquement
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
        
        # Ajouter les pages (utiliser les instances déjà créées pour clients et sales)
        self.pages = {}
        self.add_page("dashboard", DashboardPage(), "📊 Tableau de Bord")
        self.add_page("clients", self.clients_page, "👥 Clients")
        self.add_page("products", ProductsPage(), "📦 Produits")
        self.add_page("sales", self.sales_page, "💰 Ventes")
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
        """Crée la barre latérale de navigation moderne"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background: #0F1117;
                border-right: 1px solid rgba(255,255,255,0.07);
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        logo = self.create_logo()
        layout.addWidget(logo)

        nav_widget = QWidget()
        nav_widget.setObjectName("nav_widget")
        nav_widget.setStyleSheet("QWidget#nav_widget { background: transparent; }")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setSpacing(2)
        nav_layout.setContentsMargins(12, 8, 12, 8)

        self.nav_buttons = {}

        self._add_section_label(nav_layout, "PRINCIPAL")
        main_items = [
            ("dashboard",  "📊", "Tableau de Bord",  "#3B82F6"),
            ("clients",    "👥", "Clients",           "#8B5CF6"),
            ("products",   "📦", "Produits",          "#10B981"),
            ("sales",      "💰", "Point de Vente",    "#F59E0B"),
            ("purchases",  "🛒", "Achats",            "#EF4444"),
        ]
        for key, icon, label, color in main_items:
            btn = self.create_nav_button(icon, label, key, color)
            nav_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        self._add_section_label(nav_layout, "RAPPORTS")
        report_items = [
            ("history",    "🗂", "Historique Ventes", "#06B6D4"),
            ("statistics", "📈", "Statistiques",      "#06B6D4"),
        ]
        for key, icon, label, color in report_items:
            btn = self.create_nav_button(icon, label, key, color)
            nav_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        self._add_section_label(nav_layout, "SYSTEME")
        settings_btn = self.create_nav_button("⚙️", "Paramètres", "settings", "#94A3B8")
        nav_layout.addWidget(settings_btn)
        self.nav_buttons["settings"] = settings_btn

        nav_layout.addStretch()
        layout.addWidget(nav_widget)
        layout.addStretch()
        layout.addWidget(self.create_user_info())

        return sidebar

    def _add_section_label(self, layout, text):
        """Ajoute un label de section dans la sidebar"""
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl.setStyleSheet("color: rgba(255,255,255,0.25); background: transparent; padding: 14px 8px 4px 8px;")
        layout.addWidget(lbl)

    def create_logo(self):
        """Logo moderne en haut de la sidebar"""
        logo_frame = QFrame()
        logo_frame.setObjectName("logo_frame")
        logo_frame.setFixedHeight(75)
        logo_frame.setStyleSheet("""
            QFrame#logo_frame {
                background: transparent;
                border-bottom: 1px solid rgba(255,255,255,0.07);
            }
        """)

        row = QHBoxLayout(logo_frame)
        row.setContentsMargins(16, 0, 16, 0)
        row.setSpacing(12)

        # Badge icône
        badge = QLabel("E")
        badge.setFixedSize(38, 38)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        badge.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3B82F6, stop:1 #1D4ED8);
            color: white;
            border-radius: 10px;
            border: none;
        """)
        row.addWidget(badge)

        # Texte
        text_col = QVBoxLayout()
        text_col.setSpacing(0)

        title = QLabel("ERP Pro")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent; border: none;")
        text_col.addWidget(title)

        subtitle = QLabel("Gestion Professionnelle")
        subtitle.setFont(QFont("Segoe UI", 8))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.35); background: transparent; border: none;")
        text_col.addWidget(subtitle)

        row.addLayout(text_col)
        row.addStretch()

        return logo_frame

    def create_nav_button(self, icon, label, key, color):
        """Crée un bouton de navigation moderne"""
        btn = QPushButton(f"  {icon}   {label}")
        btn.setFont(QFont("Segoe UI", 11))
        btn.setMinimumHeight(42)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("nav_key", key)
        btn.setProperty("nav_color", color)
        btn.setProperty("nav_icon", icon)
        btn.setProperty("nav_label", label)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: rgba(255,255,255,0.45);
                border: none;
                border-radius: 10px;
                text-align: left;
                padding-left: 10px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.06);
                color: rgba(255,255,255,0.85);
            }}
        """)
        btn.clicked.connect(lambda: self.show_page(key))
        return btn

    def create_user_info(self):
        """Carte utilisateur moderne en bas de la sidebar"""
        card = QFrame()
        card.setObjectName("user_card")
        card.setStyleSheet("""
            QFrame#user_card {
                background: rgba(255,255,255,0.05);
                border-top: 1px solid rgba(255,255,255,0.07);
            }
        """)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(12)

        # Avatar circulaire
        avatar = QLabel("👤")
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(QFont("Segoe UI", 18))
        avatar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3B82F6, stop:1 #8B5CF6);
            border-radius: 19px;
            border: none;
        """)
        card_layout.addWidget(avatar)

        # Infos texte
        info_col = QVBoxLayout()
        info_col.setSpacing(1)

        name_lbl = QLabel("Administrateur")
        name_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        name_lbl.setStyleSheet("color: rgba(255,255,255,0.90); background: transparent; border: none;")
        info_col.addWidget(name_lbl)

        role_lbl = QLabel("Accès Complet")
        role_lbl.setFont(QFont("Segoe UI", 9))
        role_lbl.setStyleSheet("color: rgba(255,255,255,0.35); background: transparent; border: none;")
        info_col.addWidget(role_lbl)

        card_layout.addLayout(info_col)
        card_layout.addStretch()

        # Bouton à propos compact
        about_btn = QPushButton("ℹ")
        about_btn.setFixedSize(28, 28)
        about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        about_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.07);
                color: rgba(255,255,255,0.4);
                border: none;
                border-radius: 14px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(59,130,246,0.3);
                color: white;
            }
        """)
        about_btn.clicked.connect(self.show_about)
        card_layout.addWidget(about_btn)

        return card

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
            icon  = btn.property("nav_icon")
            label = btn.property("nav_label")

            if key == active_key:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {color}22, stop:1 transparent);
                        color: {color};
                        border: none;
                        border-left: 3px solid {color};
                        border-radius: 10px;
                        text-align: left;
                        padding-left: 10px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {color}33, stop:1 transparent);
                    }}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: rgba(255,255,255,0.45);
                        border: none;
                        border-radius: 10px;
                        text-align: left;
                        padding-left: 10px;
                    }
                    QPushButton:hover {
                        background: rgba(255,255,255,0.06);
                        color: rgba(255,255,255,0.85);
                    }
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