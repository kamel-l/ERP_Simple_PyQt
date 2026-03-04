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
from statistics_view import StatisticsPage
from sales_history import SalesHistoryPage
from PyQt6.QtGui import QAction
from db_manager import get_database
from advanced_analytics_view import AdvancedAnalyticsPage

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
        """Crée la barre latérale avec icônes et labels"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QFrame#sidebar {{
                background: {COLORS['BG_PAGE']};
                border-right: 2px solid {COLORS['primary']}88;
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 16, 0, 16)

        # Logo section
        logo_frame = QFrame()
        logo_frame.setStyleSheet("background: transparent; border: none;")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(8, 0, 8, 12)
        logo_layout.setSpacing(0)
        
        logo_label = QLabel()
        logo_label.setFixedSize(90, 90)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet(f"""
            QLabel {{
                background: {COLORS['BG_CARD']};
                border-radius: 12px;
                border: 2px solid {COLORS['BORDER']};
            }}
        """)
        
        # Charger le logo depuis les settings
        db = get_database()
        logo_path = db.get_setting('logo_path', '')
        from PyQt6.QtGui import QPixmap
        if logo_path:
            try:
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaledToHeight(90, Qt.TransformationMode.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                    print(f"✅ Logo chargé: {logo_path}")
                else:
                    raise Exception("QPixmap invalide - image non reconnue")
            except Exception as e:
                print(f"⚠️ Erreur logo: {e}")
                logo_label.setText("ERP")
                logo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
                logo_label.setStyleSheet(f"""
                    QLabel {{
                        background: {COLORS['BG_CARD']};
                        border-radius: 12px;
                        border: 2px solid {COLORS['BORDER']};
                        color: {COLORS['primary']};
                    }}
                """)
        else:
            logo_label.setText("ERP")
            logo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            logo_label.setStyleSheet(f"""
                QLabel {{
                    background: {COLORS['BG_CARD']};
                    border-radius: 12px;
                    border: 2px solid {COLORS['BORDER']};
                    color: {COLORS['primary']};
                }}
            """)
        
        logo_layout.addWidget(logo_label)
        layout.addWidget(logo_frame)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {COLORS['BORDER']}; border: none;")
        layout.addWidget(sep)

        nav_widget = QWidget()
        nav_widget.setObjectName("nav_widget")
        nav_widget.setStyleSheet("QWidget#nav_widget { background: transparent; }")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setSpacing(4)
        nav_layout.setContentsMargins(8, 0, 8, 0)

        self.nav_buttons = {}

        main_items = [
            ("dashboard",  "📊", "Tableau de Bord",  COLORS['primary']),
            ("clients",    "👥", "Clients",           COLORS['secondary']),
            ("products",   "📦", "Produits",          COLORS['success']),
            ("sales",      "💰", "Point de Vente",    COLORS['warning']),
            ("purchases",  "🛒", "Achats",            COLORS['danger']),
        ]
        for key, icon, label, color in main_items:
            btn = self.create_compact_nav_button(icon, label, key, color)
            nav_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        nav_layout.addSpacing(12)

        report_items = [
            ("history",    "📂", "Historique Ventes", COLORS['info']),
            ("statistics", "📈", "Statistiques",      COLORS['info']),
        ]
        for key, icon, label, color in report_items:
            btn = self.create_compact_nav_button(icon, label, key, color)
            nav_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        nav_layout.addSpacing(12)
        settings_btn = self.create_compact_nav_button("⚙️", "Paramètres", "settings", COLORS['secondary_dark'])
        nav_layout.addWidget(settings_btn)
        self.nav_buttons["settings"] = settings_btn

        nav_layout.addStretch()
        layout.addWidget(nav_widget)
        layout.addStretch()

        return sidebar

    def create_compact_nav_button(self, icon, label, key, color):
        """Crée un bouton de navigation avec icône et label"""
        btn = QPushButton(f"{icon}  {label}")
        btn.setFont(QFont("Segoe UI", 11))
        btn.setFixedHeight(50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("nav_key", key)
        btn.setProperty("nav_color", color)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border-left: 4px solid transparent;
                color: {COLORS['TXT_SEC']};
                text-align: left;
                padding-left: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {color}15;
                border-left: 4px solid {color}66;
                color: {COLORS['TXT_PRI']};
            }}
        """)
        btn.clicked.connect(lambda: self.show_page(key))
        return btn

    def update_nav_buttons(self, active_key):
        """Met à jour l'apparence des onglets verticaux (barre colorée à gauche)"""
        for key, btn in self.nav_buttons.items():
            color = btn.property("nav_color")

            if key == active_key:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {color}20;
                        border-left: 4px solid {color};
                        color: {COLORS['TXT_PRI']};
                        text-align: left;
                        padding-left: 12px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background: {color}25;
                        border-left: 4px solid {color};
                        color: {COLORS['TXT_PRI']};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        border-left: 4px solid transparent;
                        color: {COLORS['TXT_SEC']};
                        text-align: left;
                        padding-left: 12px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background: {color}15;
                        border-left: 4px solid {color}66;
                        color: {COLORS['TXT_PRI']};
                    }}
                """)

    def show_page(self, key):
        """Affiche une page spécifique"""
        if key in self.pages:
            page_info = self.pages[key]
            self.stack.setCurrentIndex(page_info['index'])
            self.update_nav_buttons(key)
            
            # Mettre à jour le titre de la fenêtre
            self.setWindowTitle(f"ERP Pro - {page_info['title']}")
    
    def run_erp_cleanup(self):
        """
        Lance le nettoyage complet de la base de données ERP.

        Corrections Bug 1 :
          - L'import est local : plus d'ImportError au démarrage si le fichier manque.
          - Boîte de confirmation PyQt6 remplace les input() bloquants de clean_erp_data.py.
          - Le résultat renvoyé par run_full_cleanup() est affiché à l'utilisateur.
        """
        # ── Confirmation explicite avant toute suppression ────────────
        confirm = QMessageBox.warning(
            self,
            "⚠️  Nettoyage ERP — Confirmation requise",
            "Cette action va supprimer TOUTES les données de l'application :\n\n"
            "  • Clients, Produits, Catégories\n"
            "  • Ventes, Achats, Factures\n"
            "  • Historique des mouvements de stock\n\n"
            "Une sauvegarde automatique sera créée avant la suppression.\n\n"
            "⚠️  Cette opération est IRRÉVERSIBLE !\n\n"
            "Voulez-vous continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        # ── Import local : ne plante PAS si le fichier est absent ─────
        try:
            from clean_erp_data import run_full_cleanup
        except ImportError:
            QMessageBox.critical(
                self,
                "Module manquant",
                "Le fichier clean_erp_data.py est introuvable.\n"
                "Vérifiez qu'il est bien présent dans le même dossier que main.py."
            )
            return

        # ── Exécution ──────────────────────────────────────────────────
        try:
            result = run_full_cleanup(db_path="erp_database.db")

            if result.get("success"):
                total  = sum(result.get("cleaned", {}).values())
                backup = result.get("backup_path") or "non créée"
                QMessageBox.information(
                    self,
                    "✅ Nettoyage terminé",
                    f"Le nettoyage a été effectué avec succès.\n\n"
                    f"📊 {total} enregistrement(s) supprimé(s)\n"
                    f"💾 Sauvegarde : {backup}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "⚠️  Nettoyage partiel",
                    f"Le nettoyage s'est terminé avec des erreurs :\n\n"
                    f"{result.get('message', 'Erreur inconnue')}"
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur",
                f"Une erreur inattendue est survenue :\n\n{e}"
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
    # print("=" * 60)
    # print("🏢 ERP Pro - Version 2.0.0")
    # print("=" * 60)
    # print("✅ Application démarrée avec succès")
    # print("📊 Modules chargés:")
    # print("   - Tableau de bord")
    # print("   - Gestion clients")
    # print("   - Gestion produits (avec CSV)")
    # print("   - Point de vente (avec dialogue)")
    # print("   - Gestion achats")
    # print("   - Historique des ventes")
    # print("   - Statistiques")
    # print("   - Paramètres")
    # print("=" * 60)
    # print("💡 Conseil: Commencez par ajouter des produits dans 'Produits'")
    # print("=" * 60)
    
    # Lancer l'application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()