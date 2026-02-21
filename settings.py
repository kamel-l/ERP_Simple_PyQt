from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QFormLayout, QLineEdit, QComboBox, QFrame, QTabWidget, QMessageBox,
    QFileDialog, QInputDialog, QApplication
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import qdarktheme
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE
from db_manager import get_database
from datetime import datetime
import time


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Récupérer l'instance de la base de données
        self.db = get_database()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # ------------------- HEADER -------------------
        header_layout = QVBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("⚙️ Paramètres")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        header_layout.addWidget(title)

        subtitle = QLabel("Configuration de votre système")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        header_layout.addWidget(subtitle)

        # ------------------- TABS -------------------
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background: {COLORS['bg_card']};
                padding: 0px;
            }}
            QTabBar::tab {{
                background: {COLORS['bg_medium']};
                color: {COLORS['text_tertiary']};
                padding: 12px 24px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['bg_card']};
                color: {COLORS['primary']};
                border-bottom: 3px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover {{
                background: {COLORS['bg_light']};
            }}
        """)

        # ------------------- ONGLET SYSTÈME -------------------
        system_tab = QWidget()
        system_layout = QVBoxLayout()
        system_tab.setLayout(system_layout)
        system_layout.setContentsMargins(20, 20, 20, 20)
        system_layout.setSpacing(20)

        # Charger les paramètres depuis la base
        company_name = self.db.get_setting('company_name', 'My Company')
        company_address = self.db.get_setting('company_address', '123 Rue Example, Alger')
        company_phone = self.db.get_setting('company_phone', '0555123456')
        company_email = self.db.get_setting('company_email', 'contact@mycompany.dz')
        currency = self.db.get_setting('currency', 'DA (Dinar Algérien)')
        vat = self.db.get_setting('vat', '19')
        vat_number = self.db.get_setting('vat_number', '123456789012345')

        # Section Entreprise
        company_section = self.create_section(
            "🏢 Informations de l'Entreprise",
            [
                ("Nom de l'entreprise:", company_name, "company_name"),
                ("Adresse:", company_address, "address"),
                ("Téléphone:", company_phone, "company_phone"),
                ("Email:", company_email, "company_email"),
            ]
        )
        system_layout.addWidget(company_section)

        # Section Devise et Taxes
        finance_section = self.create_section(
            "💰 Configuration Financière",
            [
                ("Devise:", currency, "currency"),
                ("TVA (%):", vat, "vat"),
                ("Numéro de TVA:", vat_number, "vat_number"),
            ]
        )
        system_layout.addWidget(finance_section)

        system_layout.addStretch()
        tabs.addTab(system_tab, "🏢 Système")

        # ------------------- ONGLET APPARENCE -------------------
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout()
        appearance_tab.setLayout(appearance_layout)
        appearance_layout.setContentsMargins(20, 20, 20, 20)
        appearance_layout.setSpacing(20)

        # Section Thème
        theme_card = QFrame()
        theme_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 0px;
            }}
        """)
        theme_layout = QVBoxLayout()
        theme_layout.setContentsMargins(20, 20, 20, 20)
        theme_card.setLayout(theme_layout)
        theme_layout.setSpacing(15)

        theme_title = QLabel("🎨 Thème de l'Application")
        theme_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        theme_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        theme_layout.addWidget(theme_title)

        theme_desc = QLabel("Choisissez le thème qui vous convient le mieux")
        theme_desc.setFont(QFont("Segoe UI", 12))
        theme_desc.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        theme_layout.addWidget(theme_desc)

        theme_select_layout = QHBoxLayout()
        theme_select_layout.setSpacing(15)

        theme_label = QLabel("Thème:")
        theme_label.setFont(QFont("Segoe UI", 13))
        theme_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["🌙 Mode Sombre", "☀️ Mode Clair"])
        self.theme_combo.setStyleSheet(INPUT_STYLE)
        self.theme_combo.setMinimumHeight(45)
        self.theme_combo.currentIndexChanged.connect(self.change_theme)

        theme_select_layout.addWidget(theme_label)
        theme_select_layout.addWidget(self.theme_combo)
        theme_select_layout.addStretch()

        theme_layout.addLayout(theme_select_layout)
        appearance_layout.addWidget(theme_card)

        appearance_layout.addStretch()
        tabs.addTab(appearance_tab, "🎨 Apparence")

        # ------------------- ONGLET BASE DE DONNÉES -------------------
        database_tab = QWidget()
        database_layout = QVBoxLayout()
        database_tab.setLayout(database_layout)
        database_layout.setContentsMargins(20, 20, 20, 20)
        database_layout.setSpacing(10)

        # Section Sauvegarde
        backup_card = QFrame()
        backup_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
              
                padding: 0px;
            }}
        """)
        backup_layout = QVBoxLayout()
        backup_card.setLayout(backup_layout)
        backup_layout.setContentsMargins(20, 20, 20, 20)
        backup_layout.setSpacing(15)

        backup_title = QLabel("💾 Sauvegarde des Données")
        backup_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        backup_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        backup_layout.addWidget(backup_title)

        backup_desc = QLabel("Créez une copie de sécurité de toutes vos données")
        backup_desc.setFont(QFont("Segoe UI", 12))
        backup_desc.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        backup_layout.addWidget(backup_desc)

        # Informations sur la dernière sauvegarde
        last_backup = self.db.get_setting('last_backup_date', 'Aucune')
        self.last_backup_label = QLabel(f"📅 Dernière sauvegarde: {last_backup}")
        self.last_backup_label.setFont(QFont("Segoe UI", 11))
        self.last_backup_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none; margin-top: 10px;")
        backup_layout.addWidget(self.last_backup_label)

        # Boutons de sauvegarde
        backup_btn_layout = QHBoxLayout()
        backup_btn_layout.setSpacing(10)

        self.backup_btn = QPushButton("💾 Créer une Sauvegarde")
        self.backup_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.backup_btn.setMinimumHeight(45)
        self.backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.backup_btn.clicked.connect(self.create_backup)

        self.restore_btn = QPushButton("📂 Restaurer une Sauvegarde")
        self.restore_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.restore_btn.setMinimumHeight(45)
        self.restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restore_btn.clicked.connect(self.restore_backup)

        backup_btn_layout.addWidget(self.backup_btn)
        backup_btn_layout.addWidget(self.restore_btn)
        backup_layout.addLayout(backup_btn_layout)

        database_layout.addWidget(backup_card)

        # Section Nettoyage de la Base de Données
        cleanup_card = QFrame()
        cleanup_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
               
                padding: 0px;
            }}
        """)
        cleanup_layout = QVBoxLayout()
        cleanup_card.setLayout(cleanup_layout)
        cleanup_layout.setContentsMargins(20, 20, 20, 20)
        cleanup_layout.setSpacing(10)

        cleanup_title = QLabel("🗑️ Nettoyage de la Base de Données")
        cleanup_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        cleanup_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        cleanup_layout.addWidget(cleanup_title)

        cleanup_desc = QLabel("⚠️ Attention: Cette action est irréversible!")
        cleanup_desc.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        cleanup_desc.setStyleSheet(f"color: {COLORS['danger']}; border: none;")
        cleanup_layout.addWidget(cleanup_desc)

        cleanup_info = QLabel(
            "Le nettoyage de la base de données supprimera définitivement:\n"
            "• Tous les clients\n"
            "• Tous les produits\n"
            "• Toutes les ventes\n"
            "• Tous les achats\n"
            "• Tout l'historique\n\n"
            "⚠️ Assurez-vous d'avoir créé une sauvegarde avant de continuer!"
        )
        cleanup_info.setFont(QFont("Segoe UI", 11))
        cleanup_info.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none; margin-top: 10px;")
        cleanup_layout.addWidget(cleanup_info)

        # Bouton de nettoyage
        self.cleanup_btn = QPushButton("🗑️ NETTOYER LA BASE DE DONNÉES")
        self.cleanup_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['danger']}, stop:1 #D93D32);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 15px;
                font-weight: bold;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF5549, stop:1 {COLORS['danger']});
            }}
            QPushButton:pressed {{
                background: #D93D32;
            }}
        """)
        self.cleanup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cleanup_btn.clicked.connect(self.cleanup_database)
        cleanup_layout.addWidget(self.cleanup_btn)

        database_layout.addWidget(cleanup_card)

        # Section Statistiques de la Base
        stats_card = QFrame()
        stats_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
              
                padding: 0px;
            }}
        """)
        stats_layout = QVBoxLayout()
        stats_card.setLayout(stats_layout)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        stats_layout.setSpacing(10)

        stats_title = QLabel("📊 Statistiques de la Base")
        stats_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        stats_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        stats_layout.addWidget(stats_title)

        # Grille de statistiques
        self.stats_grid = QHBoxLayout()
        self.stats_grid.setSpacing(20)
        stats_layout.addLayout(self.stats_grid)

        # Charger les statistiques initiales
        self.load_statistics()

        # Bouton rafraîchir
        refresh_stats_btn = QPushButton("🔄 Rafraîchir les Statistiques")
        refresh_stats_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        refresh_stats_btn.setMinimumHeight(40)
        refresh_stats_btn.setFixedWidth(250)
        refresh_stats_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_stats_btn.clicked.connect(self.refresh_stats)
        stats_layout.addWidget(refresh_stats_btn)

        # Bouton données de test
        test_data_btn = QPushButton("🧪 Générer des Données de Test")
        test_data_btn.setStyleSheet(BUTTON_STYLES['primary'])
        test_data_btn.setMinimumHeight(40)
        test_data_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        test_data_btn.clicked.connect(self.generate_test_data)
        stats_layout.addWidget(test_data_btn)

        database_layout.addWidget(stats_card)

        database_layout.addStretch()
        tabs.addTab(database_tab, "🗄️ Base de Données")

        layout.addWidget(tabs)

        # ------------------- ACTION BUTTONS -------------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        layout.addLayout(btn_layout)

        self.reset_btn = QPushButton("♻️ Réinitialiser")
        self.reset_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.reset_btn.setMinimumHeight(45)
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.clicked.connect(self.reset_settings)
        
        self.save_btn = QPushButton("💾 Enregistrer les Paramètres")
        self.save_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setFixedWidth(250)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_settings)

        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)

    def create_section(self, title, fields):
        """Crée une section de paramètres avec des champs"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 0px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        card.setLayout(card_layout)

        section_title = QLabel(title)
        section_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        section_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        card_layout.addWidget(section_title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        for label_text, default_value, field_name in fields:
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 12))
            label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
            
            field = QLineEdit(str(default_value))
            field.setStyleSheet(INPUT_STYLE)
            field.setMinimumHeight(40)
            setattr(self, field_name, field)
            
            form.addRow(label, field)

        card_layout.addLayout(form)
        return card

    def create_stat_item(self, icon, label, value, color):
        """Crée un item de statistique"""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_medium']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
              
                padding: 0px;
            }}
        """)
        item_layout = QVBoxLayout()
        item.setLayout(item_layout)
        item_layout.setContentsMargins(20, 20, 20, 20)
        item_layout.setSpacing(8)
        item_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 28))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("border: none;")
        item_layout.addWidget(icon_label)

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(value_label)

        text_label = QLabel(label)
        text_label.setFont(QFont("Segoe UI", 11))
        text_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(text_label)

        return item

    def load_statistics(self):
        """Charge les statistiques de la base de données"""
        # Effacer les anciens widgets
        while self.stats_grid.count():
            child = self.stats_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Récupérer les stats
        stats = self.db.get_statistics()
        
        stats_items = [
            ("👥", "Clients", stats['total_clients'], COLORS['secondary']),
            ("📦", "Produits", stats['total_products'], COLORS['success']),
            ("💰", "Ventes", stats['total_sales'], COLORS['primary']),
            ("🛒", "Achats", stats['total_purchases'], COLORS['warning']),
        ]

        for icon, label, value, color in stats_items:
            stat_item = self.create_stat_item(icon, label, value, color)
            self.stats_grid.addWidget(stat_item)

    def change_theme(self, index):
        """Change le thème de l'application"""
        if index == 0:
            qdarktheme.setup_theme("dark")
        else:
            qdarktheme.setup_theme("light")

    def cleanup_database(self):
        """Nettoie complètement la base de données"""
        reply = QMessageBox.warning(
            self,
            "⚠️ ATTENTION - Nettoyage de la Base",
            "🗑️ Vous êtes sur le point de SUPPRIMER DÉFINITIVEMENT toutes les données!\n\n"
            "Cette action supprimera:\n"
            "• Tous les clients\n"
            "• Tous les produits\n"
            "• Toutes les ventes\n"
            "• Tous les achats\n"
            "• Tout l'historique\n\n"
            "⚠️ CETTE ACTION EST IRRÉVERSIBLE!\n\n"
            "Êtes-vous absolument certain de vouloir continuer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        text, ok = QInputDialog.getText(
            self,
            "🔒 Confirmation Finale",
            "Pour confirmer le nettoyage, tapez exactement le mot:\n\nSUPPRIMER\n\n"
            "(en majuscules)",
            QLineEdit.EchoMode.Normal,
            ""
        )
        
        if not ok or text != "SUPPRIMER":
            QMessageBox.information(
                self,
                "❌ Annulé",
                "Le nettoyage de la base de données a été annulé."
            )
            return
        
        try:
            progress = QMessageBox(self)
            progress.setWindowTitle("🗑️ Nettoyage en cours...")
            progress.setText("Suppression des données...\n\nVeuillez patienter.")
            progress.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress.show()
            QApplication.processEvents()
            
            # Nettoyer la base de données
            success = self.db.clear_all_data()
            
            progress.close()
            
            if success:
                QMessageBox.information(
                    self,
                    "✅ Nettoyage Terminé",
                    "🗑️ La base de données a été nettoyée avec succès!"
                )
                self.refresh_stats()
            else:
                QMessageBox.critical(
                    self,
                    "❌ Erreur",
                    "Une erreur s'est produite lors du nettoyage."
                )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erreur",
                f"Erreur lors du nettoyage:\n\n{str(e)}"
            )

    def create_backup(self):
        """Crée une sauvegarde de la base de données"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"erp_backup_{timestamp}.db"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "💾 Sauvegarder la Base de Données",
            default_name,
            "Base de données (*.db);;Tous les fichiers (*.*)"
        )
        
        if filename:
            try:
                if self.db.backup_database(filename):
                    # Enregistrer la date de sauvegarde
                    self.db.set_setting('last_backup_date', 
                                      datetime.now().strftime("%d/%m/%Y %H:%M"))
                    self.last_backup_label.setText(
                        f"📅 Dernière sauvegarde: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                    )
                    
                    QMessageBox.information(
                        self,
                        "✅ Sauvegarde Créée",
                        f"✅ Sauvegarde créée avec succès!\n\n"
                        f"Fichier: {filename}"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "❌ Erreur",
                    f"Impossible de créer la sauvegarde:\n\n{str(e)}"
                )

    def restore_backup(self):
        """Restaure une sauvegarde"""
        reply = QMessageBox.warning(
            self,
            "⚠️ Restauration",
            "⚠️ La restauration remplacera toutes les données actuelles!\n\n"
            "Voulez-vous continuer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "📂 Restaurer une Sauvegarde",
            "",
            "Base de données (*.db);;Tous les fichiers (*.*)"
        )
        
        if filename:
            try:
                if self.db.restore_database(filename):
                    QMessageBox.information(
                        self,
                        "✅ Restauration Réussie",
                        "✅ Les données ont été restaurées!\n\n"
                        "💡 Redémarrez l'application pour voir les changements."
                    )
                    self.refresh_stats()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "❌ Erreur",
                    f"Impossible de restaurer:\n\n{str(e)}"
                )

    def refresh_stats(self):
        """Rafraîchit les statistiques"""
        self.load_statistics()
        QMessageBox.information(
            self,
            "🔄 Statistiques Actualisées",
            "Les statistiques ont été mises à jour."
        )

    def generate_test_data(self):
        """Génère des données de test"""
        reply = QMessageBox.question(
            self,
            "🧪 Données de Test",
            "Voulez-vous générer des données de test?\n\n"
            "Cela ajoutera:\n"
            "• Des clients exemples\n"
            "• Des produits exemples\n"
            "• Des catégories\n"
            "• Des fournisseurs",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.populate_test_data()
                QMessageBox.information(
                    self,
                    "✅ Données Créées",
                    "Les données de test ont été générées avec succès!"
                )
                self.refresh_stats()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "❌ Erreur",
                    f"Erreur lors de la génération:\n\n{str(e)}"
                )

    def save_settings(self):
        """Enregistre les paramètres"""
        try:
            self.db.set_setting('company_name', self.company_name.text())
            self.db.set_setting('company_address', self.address.text())
            self.db.set_setting('company_phone', self.company_phone.text())
            self.db.set_setting('company_email', self.company_email.text())
            self.db.set_setting('currency', self.currency.text())
            self.db.set_setting('vat', self.vat.text())
            self.db.set_setting('vat_number', self.vat_number.text())
            
            QMessageBox.information(
                self,
                "✅ Paramètres Enregistrés",
                "Vos paramètres ont été enregistrés avec succès!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erreur",
                f"Erreur lors de l'enregistrement:\n\n{str(e)}"
            )

    def reset_settings(self):
        """Réinitialise les paramètres"""
        reply = QMessageBox.question(
            self,
            "♻️ Réinitialiser",
            "Voulez-vous réinitialiser tous les paramètres?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.company_name.setText("My Company")
            self.address.setText("123 Rue Example, Alger")
            self.company_phone.setText("0555123456")
            self.company_email.setText("contact@mycompany.dz")
            self.currency.setText("DA (Dinar Algérien)")
            self.vat.setText("19")
            self.vat_number.setText("123456789012345")