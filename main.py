"""
Application ERP Simple - Fichier Principal
Système de gestion complet avec tous les modules intégrés
"""

import sys
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel,
    QMessageBox, QDialog, QGraphicsDropShadowEffect, QSizePolicy,
    QFileDialog, QLineEdit
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QLinearGradient, QPainter, QBrush

from styles import COLORS, BUTTON_STYLES
from dashboard import DashboardPage
from clients import ClientsPage
from products import ProductsPage
from sales import SalesPage
from purchases import PurchasesPage
from settings import SettingsPage
from statistics_view import StatisticsPage
from sales_history import SalesHistoryPage
from returns import ReturnsPage
from PyQt6.QtGui import QAction
from db_manager import get_database
from auth import session
from login_dialog import LoginDialog, UsersPage, UserBadge
from currency import currency_manager
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
        currency_manager.load(self.db)
        self.setWindowTitle("🏢 Système de Gestion ERP - Version Professionnelle")
        self.setMinimumSize(1400, 800)

        self.clients_page = ClientsPage()
        self.sales_page = SalesPage()
        self.clients_page.client_added.connect(self.sales_page.load_clients)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {COLORS['bg_dark']};
                border: 2px solid {COLORS['border']};
            }}
        """)

        self.pages = {}
        self.users_page = UsersPage()
        self.add_page("dashboard",  DashboardPage(),    "📊 Tableau de Bord")
        self.add_page("clients",    self.clients_page,  "👥 Clients")
        self.add_page("products",   ProductsPage(),     "📦 Produits")
        self.add_page("sales",      self.sales_page,    "💰 Ventes")
        self.add_page("purchases",  PurchasesPage(),    "🛒 Achats")
        self.add_page("history",    SalesHistoryPage(), "📊 Historique")
        self.add_page("returns",    ReturnsPage(),      "📦 Retours & Avoirs")
        self.add_page("statistics", StatisticsPage(),   "📈 Statistiques")
        self.add_page("settings",   SettingsPage(),     "⚙️ Paramètres")
        self.add_page("users",      self.users_page,    "👥 Utilisateurs")

        # ══════════════════════════════════════════════════════════════
        #  MENU ERP TOOLS
        # ══════════════════════════════════════════════════════════════
        erp_menu = self.menuBar().addMenu("🛠️ ERP Tools")

        # ── Groupe 1 : Rapports ───────────────────────────────────────
        erp_menu.addSection("📊 Rapports")

        all_reports_action = QAction("📊  Centre de Rapports (tout)", self)
        all_reports_action.setShortcut("Ctrl+Shift+R")
        all_reports_action.setStatusTip("Ouvre le centre de rapports complet")
        all_reports_action.triggered.connect(lambda: self._open_report("sales"))
        erp_menu.addAction(all_reports_action)

        erp_menu.addSeparator()

        r_sales = QAction("📊  Rapport des Ventes", self)
        r_sales.setShortcut("Ctrl+1")
        r_sales.triggered.connect(lambda: self._open_report("sales"))
        erp_menu.addAction(r_sales)

        r_purchases = QAction("🛒  Rapport des Achats", self)
        r_purchases.setShortcut("Ctrl+2")
        r_purchases.triggered.connect(lambda: self._open_report("purchases"))
        erp_menu.addAction(r_purchases)

        r_stock = QAction("📦  Rapport Stock & Inventaire", self)
        r_stock.setShortcut("Ctrl+3")
        r_stock.triggered.connect(lambda: self._open_report("stock"))
        erp_menu.addAction(r_stock)

        r_clients = QAction("👥  Rapport Clients", self)
        r_clients.setShortcut("Ctrl+4")
        r_clients.triggered.connect(lambda: self._open_report("clients"))
        erp_menu.addAction(r_clients)

        r_profit = QAction("💰  Rapport Bénéfices & Marges", self)
        r_profit.setShortcut("Ctrl+5")
        r_profit.triggered.connect(lambda: self._open_report("profit"))
        erp_menu.addAction(r_profit)

        r_trends = QAction("📈  Rapport Tendances & Évolution", self)
        r_trends.setShortcut("Ctrl+6")
        r_trends.triggered.connect(lambda: self._open_report("trends"))
        erp_menu.addAction(r_trends)

        r_alerts = QAction("🔔  Alertes automatiques", self)
        r_alerts.setShortcut("Ctrl+7")
        r_alerts.setStatusTip("Stock faible, impayés, produits sans mouvement")
        r_alerts.triggered.connect(lambda: self._open_report("alerts"))
        erp_menu.addAction(r_alerts)

        # ── Groupe 2 : Sauvegarde ─────────────────────────────────────
        erp_menu.addSeparator()
        erp_menu.addSection("💾 Sauvegarde")

        backup_action = QAction("💾  Sauvegarder la base de données", self)
        backup_action.setShortcut("Ctrl+B")
        backup_action.triggered.connect(self.run_backup_database)
        erp_menu.addAction(backup_action)

        restore_action = QAction("📂  Restaurer une sauvegarde", self)
        restore_action.triggered.connect(self.run_restore_database)
        erp_menu.addAction(restore_action)

        # ── Groupe 3 : Données ────────────────────────────────────────
        erp_menu.addSeparator()
        erp_menu.addSection("📦 Données")

        gen_test_action = QAction("🧪  Générer des données de test", self)
        gen_test_action.triggered.connect(self.run_generate_test_data)
        erp_menu.addAction(gen_test_action)

        clean_action = QAction("🗑️  Nettoyer toutes les données", self)
        clean_action.triggered.connect(self.run_erp_cleanup)
        erp_menu.addAction(clean_action)

        # ── Groupe 4 : Email ──────────────────────────────────────────
        erp_menu.addSeparator()
        erp_menu.addSection("📧 Email")

        email_config_action = QAction("⚙️  Configurer l'envoi d'emails", self)
        email_config_action.triggered.connect(self.run_email_config)
        erp_menu.addAction(email_config_action)

        # ── Groupe 5 : Divers ─────────────────────────────────────────
        erp_menu.addSeparator()
        erp_menu.addSection("🔧 Divers")

        integrity_action = QAction("🔍  Vérifier l'intégrité de la base", self)
        integrity_action.triggered.connect(self.run_integrity_check)
        erp_menu.addAction(integrity_action)

        about_action = QAction("ℹ️  À propos de l'application", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.show_about)
        erp_menu.addAction(about_action)

        main_layout.addWidget(self.stack)
        self.show_page("dashboard")

    # ─────────────────────────────────────────────────────────────────────
    #  Navigation
    # ─────────────────────────────────────────────────────────────────────

    def add_page(self, key, page, title):
        index = self.stack.count()
        self.stack.addWidget(page)
        self.pages[key] = {'index': index, 'page': page, 'title': title}

    def create_sidebar(self):
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

        logo_frame = QFrame()
        logo_frame.setStyleSheet("background: transparent; border: none;")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(8, 0, 8, 12)
        logo_layout.setSpacing(0)

        logo_label = QLabel()
        logo_label.setFixedSize(90, 90)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        db = get_database()
        logo_path = db.get_setting('logo_path', '')
        from PyQt6.QtCore import QFileInfo

        if logo_path and QFileInfo.exists(logo_path):
            try:
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaledToHeight(90, Qt.TransformationMode.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                else:
                    logo_label.setText("📦")
                    logo_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
            except Exception as e:
                logo_label.setText("📦")
                logo_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        else:
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
            ("returns",    "📦", "Retours & Avoirs",  "#EF4444"),
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

        if session.can("manage_users"):
            users_btn = self.create_compact_nav_button("👤", "Utilisateurs", "users", COLORS['danger'])
            nav_layout.addWidget(users_btn)
            self.nav_buttons["users"] = users_btn

        nav_layout.addStretch()

        sep_user = QFrame()
        sep_user.setFrameShape(QFrame.Shape.HLine)
        sep_user.setFixedHeight(1)
        sep_user.setStyleSheet(f"background: {COLORS['BORDER']}; border: none; margin: 0 4px;")
        nav_layout.addWidget(sep_user)

        self._user_badge = UserBadge()
        self._user_badge.logout_requested.connect(self._do_logout)
        nav_layout.addWidget(self._user_badge)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {COLORS['BORDER']}; border: none; margin: 0 8px;")
        nav_layout.addWidget(sep2)

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
        if not session.can_access_page(key):
            QMessageBox.warning(
                self, "Accès refusé",
                f"Votre rôle ({session.role_label}) ne permet pas d'accéder à cette section.")
            return
        if key in self.pages:
            page_info = self.pages[key]
            self.stack.setCurrentIndex(page_info['index'])
            self.update_nav_buttons(key)
            self.setWindowTitle(f"ERP Pro — {page_info['title']}")

    def _do_logout(self) -> None:
        reply = QMessageBox.question(
            self, "Déconnexion",
            f"Déconnecter {session.display_name} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        session.logout()
        self.hide()
        login = LoginDialog()
        if login.exec() == QDialog.DialogCode.Accepted:
            old_sidebar = self.findChild(QFrame, "sidebar")
            if old_sidebar:
                old_sidebar.deleteLater()
            new_sidebar = self.create_sidebar()
            self.centralWidget().layout().insertWidget(0, new_sidebar)
            self.show_page("dashboard")
            self.show()
        else:
            self.close()

    # ─────────────────────────────────────────────────────────────────────
    #  Actions ERP Tools
    # ─────────────────────────────────────────────────────────────────────

    def _open_report(self, page="sales"):
        """Ouvre le centre de rapports sur la page demandée."""
        try:
            from reports_module import ReportsHub
        except ImportError as e:
            QMessageBox.critical(self, "Module manquant",
                f"Le fichier reports_module.py est introuvable.\n\n{e}")
            return
        hub = ReportsHub(self)
        hub._show_page(page)
        hub.exec()

    def run_erp_cleanup(self):
        """Nettoyage complet de la base de données."""
        confirm = QMessageBox.warning(
            self, "⚠️  Nettoyage ERP — Confirmation requise",
            "Cette action va supprimer TOUTES les données de l'application :\n\n"
            "  • Clients, Produits, Catégories\n"
            "  • Ventes, Achats, Factures\n"
            "  • Historique des mouvements de stock\n\n"
            "Une sauvegarde automatique sera créée avant la suppression.\n\n"
            "⚠️  Cette opération est IRRÉVERSIBLE !\n\nVoulez-vous continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            from clean_erp_data import run_full_cleanup
        except ImportError:
            QMessageBox.critical(self, "Module manquant",
                "Le fichier clean_erp_data.py est introuvable.")
            return
        try:
            result = run_full_cleanup(db_path="erp_database.db")
            if result.get("success"):
                total = sum(result.get("cleaned", {}).values())
                backup = result.get("backup_path") or "non créée"
                QMessageBox.information(self, "✅ Nettoyage terminé",
                    f"Nettoyage effectué avec succès.\n\n"
                    f"📊 {total} enregistrement(s) supprimé(s)\n"
                    f"💾 Sauvegarde : {backup}")
            else:
                QMessageBox.warning(self, "⚠️  Nettoyage partiel",
                    f"{result.get('message', 'Erreur inconnue')}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur inattendue :\n\n{e}")

    def run_generate_test_data(self):
        """Génère des données de test (clients, produits, ventes)."""
        reply = QMessageBox.question(
            self, "🧪 Données de Test",
            "Générer des clients, produits, catégories et fournisseurs exemples ?\n\n"
            "Les données existantes ne seront pas supprimées.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.populate_test_data()
                QMessageBox.information(self, "✅ Données générées",
                    "Données de test créées avec succès.\n"
                    "Rechargez les pages pour voir les nouvelles données.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération :\n{e}")

    def run_backup_database(self):
        """Sauvegarde rapide de la base de données."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename, _ = QFileDialog.getSaveFileName(
            self, "💾 Sauvegarder la base de données",
            f"erp_backup_{timestamp}.db",
            "Base de données (*.db);;Tous (*.*)"
        )
        if filename:
            try:
                if self.db.backup_database(filename):
                    now = datetime.now().strftime("%d/%m/%Y %H:%M")
                    self.db.set_setting('last_backup_date', now)
                    QMessageBox.information(self, "✅ Sauvegarde créée",
                        f"Base de données sauvegardée avec succès.\n\n📁 {filename}")
                else:
                    QMessageBox.critical(self, "Erreur", "Échec de la sauvegarde.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer la sauvegarde :\n{e}")

    def run_restore_database(self):
        """Restaure la base depuis une sauvegarde."""
        reply = QMessageBox.warning(
            self, "⚠️ Restauration",
            "La restauration remplacera TOUTES les données actuelles.\n\n"
            "Cette action est irréversible. Continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return
        filename, _ = QFileDialog.getOpenFileName(
            self, "📂 Restaurer une sauvegarde", "",
            "Base de données (*.db);;Tous (*.*)"
        )
        if filename:
            try:
                if self.db.restore_database(filename):
                    QMessageBox.information(self, "✅ Restauration réussie",
                        "Données restaurées avec succès.\n\n"
                        "Veuillez redémarrer l'application pour appliquer les changements.")
                else:
                    QMessageBox.critical(self, "Erreur", "Échec de la restauration.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de restaurer :\n{e}")

    def run_quick_stats(self):
        """Affiche un rapport de statistiques rapide."""
        try:
            stats = self.db.get_statistics()
            from currency import fmt_da
            from datetime import datetime
            now = datetime.now().strftime("%d/%m/%Y à %H:%M")

            msg = (
                f"📊  RAPPORT RAPIDE — {now}\n"
                f"{'─' * 42}\n\n"
                f"👥  Clients enregistrés   :  {stats.get('total_clients', 0)}\n"
                f"📦  Produits en catalogue  :  {stats.get('total_products', 0)}\n"
                f"💰  Nombre de ventes       :  {stats.get('total_sales', 0)}\n"
                f"🛒  Nombre d'achats        :  {stats.get('total_purchases', 0)}\n\n"
                f"{'─' * 42}\n\n"
                f"💳  Chiffre d'affaires     :  {fmt_da(float(stats.get('sales_total', 0)))}\n"
                f"🛍️  Total achats           :  {fmt_da(float(stats.get('purchases_total', 0)))}\n"
                f"📈  Bénéfice net estimé    :  "
                f"{fmt_da(float(stats.get('sales_total', 0)) - float(stats.get('purchases_total', 0)))}\n\n"
                f"{'─' * 42}\n\n"
                f"📦  Valeur du stock        :  {fmt_da(float(stats.get('stock_value', 0)))}\n"
            )

            low_stock = self.db.get_low_stock_products()
            msg += f"⚠️   Produits stock faible  :  {len(low_stock)} produit(s)\n"

            QMessageBox.information(self, "📊 Rapport Rapide", msg)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de générer le rapport :\n{e}")

    def run_low_stock_report(self):
        """Affiche et permet d'exporter le rapport de stock faible."""
        try:
            products = self.db.get_low_stock_products()
            from currency import fmt_da

            if not products:
                QMessageBox.information(self, "✅ Stock en ordre",
                    "Aucun produit n'est sous le seuil de stock minimum.\n"
                    "Votre inventaire est en bonne santé !")
                return

            lines = [f"{'Produit':<30} {'Stock':>7} {'Min':>7} {'Prix vente':>14}"]
            lines.append("─" * 62)
            for p in products:
                name  = str(p.get('name', ''))[:28]
                stock = int(p.get('stock_quantity', 0))
                mini  = int(p.get('min_stock', 0))
                price = float(p.get('selling_price', 0))
                flag  = "🔴" if stock == 0 else "🟡"
                lines.append(f"{flag} {name:<28} {stock:>7} {mini:>7} {fmt_da(price):>14}")

            msg = (
                f"⚠️  RAPPORT STOCK FAIBLE — {len(products)} produit(s)\n\n"
                + "\n".join(lines)
            )

            reply = QMessageBox.warning(
                self, f"⚠️ Stock Faible ({len(products)} produit(s))", msg,
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Close,
                QMessageBox.StandardButton.Close
            )

            if reply == QMessageBox.StandardButton.Save:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "Exporter rapport stock", "rapport_stock_faible.csv",
                    "CSV (*.csv);;Tous (*.*)"
                )
                if filename:
                    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow(["Produit", "Stock actuel", "Stock minimum",
                                         "Prix vente", "Statut"])
                        for p in products:
                            writer.writerow([
                                p.get('name', ''),
                                p.get('stock_quantity', 0),
                                p.get('min_stock', 0),
                                p.get('selling_price', 0),
                                "Rupture" if p.get('stock_quantity', 0) == 0 else "Stock faible"
                            ])
                    QMessageBox.information(self, "✅ Exporté", f"Rapport enregistré :\n{filename}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du rapport stock :\n{e}")

    def run_export_clients_csv(self):
        """Exporte tous les clients en fichier CSV."""
        try:
            clients = self.db.get_all_clients()
            if not clients:
                QMessageBox.information(self, "Info", "Aucun client à exporter.")
                return

            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les clients", "clients_export.csv",
                "CSV (*.csv);;Tous (*.*)"
            )
            if not filename:
                return

            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Nom", "Téléphone", "Email", "Adresse", "Date création"])
                for c in clients:
                    writer.writerow([
                        c.get('id', ''),
                        c.get('name', ''),
                        c.get('phone', ''),
                        c.get('email', ''),
                        c.get('address', ''),
                        str(c.get('created_at', '')).split(' ')[0],
                    ])

            QMessageBox.information(self, "✅ Export réussi",
                f"{len(clients)} client(s) exporté(s) avec succès.\n\n📁 {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export :\n{e}")

    def run_email_config(self):
        """Dialogue de configuration email pour l'envoi de factures."""
        dialog = EmailConfigDialog(self.db, parent=self)
        dialog.exec()

    def run_integrity_check(self):
        """Vérifie l'intégrité et la cohérence de la base de données."""
        try:
            issues = []
            warnings = []

            # 1. Intégrité SQLite
            self.db.cursor.execute("PRAGMA integrity_check")
            result = self.db.cursor.fetchone()
            if result and result[0] != "ok":
                issues.append(f"❌ Intégrité SQLite : {result[0]}")
            else:
                warnings.append("✅ Intégrité SQLite : OK")

            # 2. Ventes sans client
            self.db.cursor.execute("""
                SELECT COUNT(*) FROM sales
                WHERE client_id IS NOT NULL
                  AND client_id NOT IN (SELECT id FROM clients)
            """)
            orphan_sales = self.db.cursor.fetchone()[0]
            if orphan_sales:
                issues.append(f"⚠️ {orphan_sales} vente(s) avec client introuvable")
            else:
                warnings.append("✅ Cohérence ventes/clients : OK")

            # 3. Articles de vente sans produit
            self.db.cursor.execute("""
                SELECT COUNT(*) FROM sale_items
                WHERE product_id NOT IN (SELECT id FROM products)
            """)
            orphan_items = self.db.cursor.fetchone()[0]
            if orphan_items:
                issues.append(f"⚠️ {orphan_items} article(s) de vente sans produit associé")
            else:
                warnings.append("✅ Cohérence articles/produits : OK")

            # 4. Produits avec stock négatif
            self.db.cursor.execute("""
                SELECT COUNT(*) FROM products WHERE stock_quantity < 0
            """)
            neg_stock = self.db.cursor.fetchone()[0]
            if neg_stock:
                issues.append(f"⚠️ {neg_stock} produit(s) avec stock négatif")
            else:
                warnings.append("✅ Stocks : aucun négatif")

            # 5. Taille de la base
            self.db.cursor.execute("PRAGMA page_count")
            pages = self.db.cursor.fetchone()[0]
            self.db.cursor.execute("PRAGMA page_size")
            page_size = self.db.cursor.fetchone()[0]
            db_size_kb = (pages * page_size) / 1024
            warnings.append(f"📦 Taille de la base : {db_size_kb:.1f} Ko")

            # Rapport final
            status_icon = "❌" if issues else "✅"
            title = f"{status_icon} Rapport d'intégrité"

            report = "🔍  VÉRIFICATION DE LA BASE DE DONNÉES\n"
            report += "─" * 44 + "\n\n"
            report += "\n".join(warnings) + "\n"
            if issues:
                report += "\n⚠️  PROBLÈMES DÉTECTÉS :\n"
                report += "\n".join(issues) + "\n"
            else:
                report += "\n✅  Aucun problème détecté. La base est saine."

            if issues:
                QMessageBox.warning(self, title, report)
            else:
                QMessageBox.information(self, title, report)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la vérification :\n{e}")

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()


# ─────────────────────────────────────────────────────────────────────────
#  Dialogue configuration email
# ─────────────────────────────────────────────────────────────────────────

class EmailConfigDialog(QDialog):
    """Configuration du compte email pour l'envoi de factures."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("⚙️ Configuration Email")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"""
            QDialog {{ background: {COLORS['bg_medium']}; }}
            QLabel  {{ color: {COLORS['text_primary']}; font-size: 13px; }}
        """)

        lay = QVBoxLayout(self)
        lay.setSpacing(16)
        lay.setContentsMargins(28, 28, 28, 28)

        # En-tête
        hdr = QFrame()
        hdr.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                border-radius: 10px;
            }}
        """)
        hdr_lay = QVBoxLayout(hdr)
        hdr_lay.setContentsMargins(16, 14, 16, 14)
        t = QLabel("📧 Configuration de l'envoi d'emails")
        t.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        t.setStyleSheet("color: white; border: none;")
        hdr_lay.addWidget(t)
        s = QLabel("Ces paramètres sont utilisés pour envoyer les factures par email")
        s.setFont(QFont("Segoe UI", 10))
        s.setStyleSheet("color: rgba(255,255,255,0.80); border: none;")
        hdr_lay.addWidget(s)
        lay.addWidget(hdr)

        # Formulaire
        form = QFrame()
        form.setStyleSheet(f"background: {COLORS['bg_card']}; border-radius: 10px;")
        from PyQt6.QtWidgets import QFormLayout, QComboBox
        fl = QFormLayout(form)
        fl.setContentsMargins(20, 18, 20, 18)
        fl.setSpacing(14)

        from styles import INPUT_STYLE

        # Fournisseur
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Gmail", "Outlook", "Yahoo", "Autre (SMTP manuel)"])
        self.provider_combo.setStyleSheet(INPUT_STYLE)
        self.provider_combo.setMinimumHeight(40)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        fl.addRow("Fournisseur :", self.provider_combo)

        # Champs SMTP (masqués par défaut sauf si "Autre")
        self.smtp_server = QLineEdit(self.db.get_setting('email_smtp_server', 'smtp.gmail.com'))
        self.smtp_server.setStyleSheet(INPUT_STYLE)
        self.smtp_server.setMinimumHeight(40)
        self.smtp_row_label = QLabel("Serveur SMTP :")
        fl.addRow(self.smtp_row_label, self.smtp_server)

        self.smtp_port = QLineEdit(self.db.get_setting('email_smtp_port', '587'))
        self.smtp_port.setStyleSheet(INPUT_STYLE)
        self.smtp_port.setMinimumHeight(40)
        self.smtp_port_label = QLabel("Port SMTP :")
        fl.addRow(self.smtp_port_label, self.smtp_port)

        # Email expéditeur
        self.email_edit = QLineEdit(self.db.get_setting('email_sender', ''))
        self.email_edit.setPlaceholderText("votre.email@gmail.com")
        self.email_edit.setStyleSheet(INPUT_STYLE)
        self.email_edit.setMinimumHeight(40)
        fl.addRow("Email expéditeur :", self.email_edit)

        # Mot de passe
        self.password_edit = QLineEdit(self.db.get_setting('email_password', ''))
        self.password_edit.setPlaceholderText("Mot de passe ou mot de passe d'application")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet(INPUT_STYLE)
        self.password_edit.setMinimumHeight(40)
        fl.addRow("Mot de passe :", self.password_edit)

        lay.addWidget(form)

        # Info Gmail
        info = QLabel(
            "💡 Pour Gmail : activez la validation en 2 étapes et utilisez un\n"
            "     «Mot de passe d'application» généré depuis votre compte Google."
        )
        info.setFont(QFont("Segoe UI", 9))
        info.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            background: rgba(59,130,246,0.08);
            border: 1px solid rgba(59,130,246,0.25);
            border-radius: 8px;
            padding: 10px 14px;
        """)
        lay.addWidget(info)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        test_btn = QPushButton("📨  Tester la connexion")
        test_btn.setFixedHeight(42)
        test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {COLORS['primary']};
                border: 1.5px solid {COLORS['primary']}66;
                border-radius: 9px; padding: 0 18px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {COLORS['primary']}18; }}
        """)
        test_btn.clicked.connect(self._test_connection)

        save_btn = QPushButton("💾  Enregistrer")
        save_btn.setFixedHeight(42)
        save_btn.setFixedWidth(140)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['success']}; color: white;
                border: none; border-radius: 9px; padding: 0 18px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {COLORS['success']}CC; }}
        """)
        save_btn.clicked.connect(self._save)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setFixedHeight(42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 9px; padding: 0 16px;
            }}
            QPushButton:hover {{ background: rgba(255,255,255,0.05); }}
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(test_btn)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        lay.addLayout(btn_row)

        self._on_provider_changed(0)

    def _on_provider_changed(self, index):
        """Met à jour serveur/port selon le fournisseur sélectionné."""
        presets = {
            0: ('smtp.gmail.com',          '587'),   # Gmail
            1: ('smtp-mail.outlook.com',   '587'),   # Outlook
            2: ('smtp.mail.yahoo.com',     '587'),   # Yahoo
            3: (self.smtp_server.text(),   self.smtp_port.text()),  # Manuel
        }
        server, port = presets.get(index, ('', '587'))
        is_manual = (index == 3)
        self.smtp_server.setEnabled(is_manual)
        self.smtp_port.setEnabled(is_manual)
        self.smtp_row_label.setStyleSheet(
            f"color: {COLORS['text_primary'] if is_manual else COLORS['text_secondary']};"
        )
        if index != 3:
            self.smtp_server.setText(server)
            self.smtp_port.setText(port)

    def _save(self):
        self.db.set_setting('email_smtp_server', self.smtp_server.text().strip())
        self.db.set_setting('email_smtp_port',   self.smtp_port.text().strip())
        self.db.set_setting('email_sender',       self.email_edit.text().strip())
        self.db.set_setting('email_password',     self.password_edit.text())
        QMessageBox.information(self, "✅ Enregistré",
            "Configuration email sauvegardée avec succès.")
        self.accept()

    def _test_connection(self):
        """Teste la connexion SMTP."""
        import smtplib
        server = self.smtp_server.text().strip()
        port   = int(self.smtp_port.text().strip() or 587)
        email  = self.email_edit.text().strip()
        pwd    = self.password_edit.text()

        if not email or not pwd:
            QMessageBox.warning(self, "Champs manquants",
                "Veuillez renseigner l'email et le mot de passe.")
            return

        try:
            with smtplib.SMTP(server, port, timeout=10) as s:
                s.starttls()
                s.login(email, pwd)
            QMessageBox.information(self, "✅ Connexion réussie",
                f"Connexion au serveur {server}:{port} établie avec succès !\n"
                "Vous pouvez enregistrer la configuration.")
        except smtplib.SMTPAuthenticationError:
            QMessageBox.critical(self, "❌ Échec d'authentification",
                "Email ou mot de passe incorrect.\n\n"
                "Pour Gmail, utilisez un 'Mot de passe d'application'.")
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur de connexion",
                f"Impossible de se connecter au serveur SMTP :\n\n{e}")


# ─────────────────────────────────────────────────────────────────────────
#  Dialogue À propos
# ─────────────────────────────────────────────────────────────────────────

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("À propos")
        self.setFixedSize(480, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self._build_ui()

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

        card = QFrame()
        card.setObjectName("about_card")
        card.setStyleSheet(f"""
            QFrame#about_card {{
                background: {COLORS['bg_dark']};
                border-radius: 18px;
                border: 1.5px solid {COLORS['primary']}55;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 24)
        layout.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(160)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                border-radius: 16px 16px 0 0;
            }}
        """)
        header_lay = QVBoxLayout(header)
        header_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_lay.setSpacing(6)

        logo_lbl = QLabel()
        logo_lbl.setFixedSize(72, 72)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet("""
            QLabel { background:rgba(255,255,255,0.18); border-radius:18px;
                     border:2px solid rgba(255,255,255,0.35); }
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
        app_name.setStyleSheet("color:white; background:transparent; border:none;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version_lbl = QLabel("Version 2.0.0  •  2026")
        version_lbl.setFont(QFont("Segoe UI", 10))
        version_lbl.setStyleSheet("color:rgba(255,255,255,0.75); background:transparent; border:none;")
        version_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_lay.addWidget(logo_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        header_lay.addWidget(app_name)
        header_lay.addWidget(version_lbl)
        layout.addWidget(header)

        body = QWidget()
        body.setStyleSheet("background:transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(28, 20, 28, 0)
        body_lay.setSpacing(16)

        dev_card = self._info_card(
            "👨‍💼  Développé par",
            "Équipe DAR ELSSALEM\n© 2026 — Tous droits réservés",
            COLORS['primary']
        )
        body_lay.addWidget(dev_card)

        feat_title = QLabel("✨  Fonctionnalités")
        feat_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        feat_title.setStyleSheet(f"color:{COLORS['secondary']}; background:transparent;")
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
            QFrame {{ background:{COLORS.get('bg_medium', COLORS['bg_dark'])};
                     border-radius:10px; border:1px solid {COLORS['primary']}22; }}
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
            ico.setStyleSheet("background:transparent; border:none;")
            lbl = QLabel(txt)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color:{COLORS.get('TXT_PRI','#F0F4FF')}; background:transparent; border:none;")
            row.addWidget(ico)
            row.addWidget(lbl)
            row.addStretch()
            feat_lay.addLayout(row)
        body_lay.addWidget(feat_frame)
        layout.addWidget(body)

        close_btn = QPushButton("Fermer")
        close_btn.setFixedHeight(42)
        close_btn.setFixedWidth(140)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        close_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['primary']}; color:white;
                           border:none; border-radius:10px; }}
            QPushButton:hover {{ background:{COLORS.get('primary_dark', COLORS['primary'])}; }}
        """)
        close_btn.clicked.connect(self.accept)
        layout.addSpacing(4)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(card)

    def _info_card(self, title, body_text, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background:{color}15; border-radius:10px; border:1px solid {color}44; }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(3)
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{color}; background:transparent; border:none;")
        b = QLabel(body_text)
        b.setFont(QFont("Segoe UI", 10))
        b.setStyleSheet(f"color:{COLORS.get('TXT_PRI','#F0F4FF')}; background:transparent; border:none;")
        lay.addWidget(t)
        lay.addWidget(b)
        return frame


# ─────────────────────────────────────────────────────────────────────────
#  Point d'entrée
# ─────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ERP Pro")
    app.setOrganizationName("DAR ELSSALEM")
    app.setApplicationVersion("2.0.0")

    login = LoginDialog()
    if login.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
