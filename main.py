"""
Application ERP Simple - Fichier Principal
Système de gestion complet avec tous les modules intégrés
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel,
    QMessageBox, QDialog, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QLinearGradient, QPainter, QBrush
# import qdarktheme

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
try:
    from advanced_analytics_view import AdvancedAnalyticsPage
except ImportError:
    AdvancedAnalyticsPage = None
    print("⚠️ advanced_analytics_view non trouvé, module désactivé")

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        
        self.db = get_database()
        self.setWindowTitle("🏢 Système de Gestion ERP - Version Professionnelle")
        self.setMinimumSize(1400, 800)
        
        # Appliquer le thème sombre
        # qdarktheme.setup_theme("dark")

        # Créer les pages
        self.clients_page = ClientsPage()
        self.sales_page = SalesPage()
        
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
                border: 2px solid {COLORS['border']};
            }}
        """)
        
        # Ajouter les pages (utiliser les instances déjà créées pour clients et sales)
        self.pages = {}
        self.dashboard_page   = DashboardPage()
        self.products_page    = ProductsPage()
        self.purchases_page   = PurchasesPage()
        self.history_page     = SalesHistoryPage()
        self.statistics_page  = StatisticsPage()
        self.settings_page    = SettingsPage()

        self.add_page("dashboard",  self.dashboard_page,  "📊 Tableau de Bord")
        self.add_page("clients",    self.clients_page,    "👥 Clients")
        self.add_page("products",   self.products_page,   "📦 Produits")
        self.add_page("sales",      self.sales_page,      "💰 Ventes")
        self.add_page("purchases",  self.purchases_page,  "🛒 Achats")
        self.add_page("history",    self.history_page,    "📊 Historique")
        self.add_page("statistics", self.statistics_page, "📈 Statistiques")
        self.add_page("settings",   self.settings_page,   "⚙️ Paramètres")

        # ── Signaux inter-pages ──────────────────────────────────────────
        # Client ajouté/modifié → rafraîchir la liste clients dans Ventes
        self.clients_page.client_added.connect(self.sales_page.load_clients)

        # Vente enregistrée → dashboard + historique + statistiques
        self.sales_page.sale_saved.connect(self.dashboard_page.refresh)
        self.sales_page.sale_saved.connect(self.history_page.load_sales)
        self.sales_page.sale_saved.connect(self.statistics_page.refresh)

        # Produit ajouté/modifié/supprimé → dashboard + statistiques
        self.products_page.product_changed.connect(self.dashboard_page.refresh)
        self.products_page.product_changed.connect(self.statistics_page.refresh)

        # Achat enregistré → dashboard + produits (stock mis à jour) + stats
        self.purchases_page.purchase_saved.connect(self.dashboard_page.refresh)
        self.purchases_page.purchase_saved.connect(self.products_page.refresh_page)
        self.purchases_page.purchase_saved.connect(self.statistics_page.refresh)

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
        from PyQt6.QtCore import QFileInfo
        
        if logo_path and QFileInfo.exists(logo_path):
            try:
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaledToHeight(90, Qt.TransformationMode.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                    print(f"✅ Logo chargé: {logo_path}")
                else:
                    logo_label.setText("📦")
                    logo_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
            except Exception as e:
                print(f"⚠️ Erreur logo: {e}")
                logo_label.setText("📦")
                logo_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        else:
            # Aucun logo défini - afficher icône par défaut
            logo_label.setText("📦")
            logo_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        
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
            ("dashboard",  "📊", "Tableau de Bord",  COLORS['info']),
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

        # Séparateur avant About
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {COLORS['BORDER']}; border: none; margin: 0 8px;")
        nav_layout.addWidget(sep2)

        # Bouton À propos
        about_btn = QPushButton("ℹ️  À propos")
        about_btn.setFont(QFont("Segoe UI", 10))
        about_btn.setFixedHeight(40)
        about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        about_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border-left: 4px solid transparent;
                color: {COLORS['TXT_SEC']};
                text-align: left;
                padding-left: 12px;
                font-weight: 400;
                font-style: italic;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.05);
                border-left: 4px solid {COLORS['TXT_SEC']}55;
                color: {COLORS['TXT_PRI']};
            }}
        """)
        about_btn.clicked.connect(self.show_about)
        nav_layout.addWidget(about_btn)

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
                background: {color}18;
                border-left: 4px solid {color}55;
                color: {COLORS['TXT_PRI']};
            }}
        """)
        btn.clicked.connect(lambda checked=False, k=key: self.show_page(k))
        return btn

    def update_nav_buttons(self, active_key):
        """Met à jour l'apparence des onglets verticaux (barre colorée à gauche)"""
        for key, btn in self.nav_buttons.items():
            color = btn.property("nav_color")

            if key == active_key:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {color}22;
                        border-left: 4px solid {color};
                        color: {color};
                        text-align: left;
                        padding-left: 12px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background: {color}30;
                        border-left: 4px solid {color};
                        color: {color};
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
                        background: {color}18;
                        border-left: 4px solid {color}55;
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
        """Affiche la fenêtre À propos moderne"""
        dialog = AboutDialog(self)
        dialog.exec()



class AboutDialog(QDialog):
    """Fenêtre À propos moderne avec fond sombre"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("À propos")
        self.setFixedSize(480, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self._build_ui()

    # ── Drag pour déplacer la fenêtre ──────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Carte principale ────────────────────────────────────
        card = QFrame()
        card.setObjectName("about_card")
        card.setStyleSheet(f"""
            QFrame#about_card {{
                background: {COLORS['bg_dark']};
                border-radius: 18px;
                border: 1.5px solid {COLORS['primary']}55;
            }}
        """)

        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 24)
        layout.setSpacing(0)

        # ── Bandeau header dégradé ──────────────────────────────
        header = QFrame()
        header.setFixedHeight(160)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['primary']},
                    stop:1 {COLORS['secondary']}
                );
                border-radius: 16px 16px 0 0;
            }}
        """)
        header_lay = QVBoxLayout(header)
        header_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_lay.setSpacing(6)

        # Logo / icône
        logo_lbl = QLabel()
        logo_lbl.setFixedSize(72, 72)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.18);
                border-radius: 18px;
                border: 2px solid rgba(255,255,255,0.35);
            }
        """)
        db = get_database()
        logo_path = db.get_setting('logo_path', '')
        from PyQt6.QtCore import QFileInfo
        if logo_path and QFileInfo.exists(logo_path):
            try:
                px = QPixmap(logo_path)
                if not px.isNull():
                    logo_lbl.setPixmap(px.scaled(64, 64,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation))
            except Exception:
                logo_lbl.setText("🏢")
                logo_lbl.setFont(QFont("Segoe UI", 28))
        else:
            logo_lbl.setText("🏢")
            logo_lbl.setFont(QFont("Segoe UI", 28))

        app_name = QLabel("DAR ELSSALEM ERP")
        app_name.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        app_name.setStyleSheet("color: white; background: transparent; border: none;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version_lbl = QLabel("Version 2.0.0  •  2026")
        version_lbl.setFont(QFont("Segoe UI", 10))
        version_lbl.setStyleSheet("color: rgba(255,255,255,0.75); background: transparent; border: none;")
        version_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_lay.addWidget(logo_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        header_lay.addWidget(app_name)
        header_lay.addWidget(version_lbl)
        layout.addWidget(header)

        # ── Corps ───────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(28, 20, 28, 0)
        body_lay.setSpacing(16)

        # Développeur / Société
        dev_card = self._info_card(
            "👨‍💼  Développé par",
            "Équipe DAR ELSSALEM\n© 2026 — Tous droits réservés",
            COLORS['primary']
        )
        body_lay.addWidget(dev_card)

        # Fonctionnalités
        feat_title = QLabel("✨  Fonctionnalités")
        feat_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        feat_title.setStyleSheet(f"color: {COLORS['secondary']}; background: transparent;")
        body_lay.addWidget(feat_title)

        features = [
            ("📊", "Tableau de bord temps réel"),
            ("👥", "Gestion clients & fournisseurs"),
            ("📦", "Gestion produits & stock"),
            ("💰", "Point de vente & facturation"),
            ("🛒", "Gestion des achats"),
            ("📈", "Statistiques & graphiques"),
            ("📂", "Import/Export factures .DAT"),
        ]
        feat_frame = QFrame()
        feat_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_medium'] if 'bg_medium' in COLORS else COLORS['bg_dark']};
                border-radius: 10px;
                border: 1px solid {COLORS['primary']}22;
            }}
        """)
        feat_lay = QVBoxLayout(feat_frame)
        feat_lay.setContentsMargins(14, 10, 14, 10)
        feat_lay.setSpacing(5)

        for icon, txt in features:
            row = QHBoxLayout()
            row.setSpacing(10)
            ico = QLabel(icon)
            ico.setFont(QFont("Segoe UI", 11))
            ico.setFixedWidth(22)
            ico.setStyleSheet("background: transparent; border: none;")
            lbl = QLabel(txt)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color: {COLORS['TXT_PRI'] if 'TXT_PRI' in COLORS else '#F0F4FF'}; background: transparent; border: none;")
            row.addWidget(ico)
            row.addWidget(lbl)
            row.addStretch()
            feat_lay.addLayout(row)

        body_lay.addWidget(feat_frame)
        layout.addWidget(body)

        # ── Bouton Fermer ───────────────────────────────────────
        close_btn = QPushButton("Fermer")
        close_btn.setFixedHeight(42)
        close_btn.setFixedWidth(140)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark'] if 'primary_dark' in COLORS else COLORS['primary']};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        layout.addSpacing(4)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addWidget(card)

    def _info_card(self, title, body, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {color}15;
                border-radius: 10px;
                border: 1px solid {color}44;
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(3)

        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {color}; background: transparent; border: none;")

        b = QLabel(body)
        b.setFont(QFont("Segoe UI", 10))
        txt_color = COLORS.get('TXT_PRI', '#F0F4FF')
        b.setStyleSheet(f"color: {txt_color}; background: transparent; border: none;")

        lay.addWidget(t)
        lay.addWidget(b)
        return frame


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