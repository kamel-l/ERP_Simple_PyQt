from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QLineEdit, QComboBox, QFrame, QScrollArea, QMessageBox,
    QFileDialog, QInputDialog, QApplication, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QSize
import qdarktheme
from styles import COLORS, SETTINGS_CARD_STYLE, SETTINGS_INPUT_STYLE, SETTINGS_COMBO_STYLE
from db_manager import get_database
from datetime import datetime


# ─────────────────────────────────────────────
#  Styles importés depuis styles.py (centralisés)
# ─────────────────────────────────────────────

# Alias locaux pour rétro-compatibilité avec le reste du module
CARD_STYLE  = SETTINGS_CARD_STYLE
INPUT_STYLE = SETTINGS_INPUT_STYLE
COMBO_STYLE = SETTINGS_COMBO_STYLE

def make_btn(text, color="#6366F1", text_color="white", outlined=False):
    """Crée un bouton stylisé."""
    btn = QPushButton(text)
    btn.setMinimumHeight(42)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    if outlined:
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: 1.5px solid {color};
                border-radius: 9px;
                padding: 0 22px;
            }}
            QPushButton:hover {{ background: {color}22; }}
            QPushButton:pressed {{ background: {color}44; }}
        """)
    else:
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: {text_color};
                border: none;
                border-radius: 9px;
                padding: 0 22px;
            }}
            QPushButton:hover {{ background: {color}CC; }}
            QPushButton:pressed {{ background: {color}99; }}
        """)
    return btn


class SectionCard(QFrame):
    """Carte de section avec titre et icône."""
    def __init__(self, icon, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 20, 24, 24)
        self._layout.setSpacing(18)

        # En-tête
        hdr = QHBoxLayout()
        hdr.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 18))
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent; border: none;")
        hdr.addWidget(title_lbl)
        hdr.addStretch()

        self._layout.addLayout(hdr)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {COLORS['BORDER']}; border: none;")
        self._layout.addWidget(sep)

    def body(self):
        return self._layout


class FieldRow(QHBoxLayout):
    """Ligne label + champ."""
    def __init__(self, label_text, field_widget, parent=None):
        super().__init__()
        self.setSpacing(0)

        lbl = QLabel(label_text)
        lbl.setFont(QFont("Segoe UI", 11))
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none;")
        lbl.setFixedWidth(170)

        self.addWidget(lbl)
        self.addWidget(field_widget)


# ─────────────────────────────────────────────
#  Onglets personnalisés (boutons-onglets)
# ─────────────────────────────────────────────

class TabBar(QFrame):
    def __init__(self, tabs_data, parent=None):
        super().__init__(parent)
        self.setObjectName("tabbar")
        self.setStyleSheet("QFrame#tabbar { background: transparent; border: none; }")
        self._btns = []
        self._callbacks = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        for i, (icon, label, callback) in enumerate(tabs_data):
            btn = QPushButton(f"{icon}  {label}")
            btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setProperty("tab_index", i)
            btn.clicked.connect(lambda checked, idx=i: self._activate(idx))
            self._btns.append(btn)
            self._callbacks.append(callback)
            layout.addWidget(btn)

        layout.addStretch()
        self._activate(0)

    def _activate(self, idx):
        for i, btn in enumerate(self._btns):
            if i == idx:
                btn.setChecked(True)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {COLORS['primary']};
                        color: white;
                        border: none;
                        border-radius: 9px;
                        padding: 0 20px;
                    }}
                """)
            else:
                btn.setChecked(False)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: rgba(255,255,255,0.06);
                        color: {COLORS['text_secondary']};
                        border: none;
                        border-radius: 9px;
                        padding: 0 20px;
                    }}
                    QPushButton:hover {{
                        background: rgba(255,255,255,0.10);
                        color: {COLORS['text_primary']};
                    }}
                """)
        self._callbacks[idx]()


# ─────────────────────────────────────────────
#  Page Paramètres principale
# ─────────────────────────────────────────────

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.setStyleSheet(f"background: {COLORS['BG_PAGE']};")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(0)

        # ── EN-TÊTE ───────────────────────────────────────
        hdr_row = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        page_title = QLabel("Paramètres")
        page_title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        page_title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        title_col.addWidget(page_title)

        page_sub = QLabel("Configuration de votre système ERP")
        page_sub.setFont(QFont("Segoe UI", 12))
        page_sub.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        title_col.addWidget(page_sub)

        hdr_row.addLayout(title_col)
        hdr_row.addStretch()

        # Boutons d'action globaux (en-tête)
        self.reset_btn = make_btn("↺  Réinitialiser", COLORS['secondary_dark'], outlined=True)
        self.reset_btn.setFixedWidth(150)
        self.reset_btn.clicked.connect(self.reset_settings)

        self.save_btn = make_btn("✓  Enregistrer", COLORS['success'])
        self.save_btn.setFixedWidth(170)
        self.save_btn.clicked.connect(self.save_settings)

        hdr_row.addWidget(self.reset_btn)
        hdr_row.addSpacing(10)
        hdr_row.addWidget(self.save_btn)

        root.addLayout(hdr_row)
        root.addSpacing(24)

        # ── BARRE D'ONGLETS ───────────────────────────────
        # Zone de contenu (stacké manuellement)
        self.content_system = self._build_system_tab()
        self.content_appearance = self._build_appearance_tab()
        self.content_database = self._build_database_tab()

        self.all_contents = [
            self.content_system,
            self.content_appearance,
            self.content_database,
        ]

        tab_bar = TabBar([
            ("🏢", "Système",      lambda: self._show_tab(0)),
            ("🎨", "Apparence",    lambda: self._show_tab(1)),
            ("🗄️", "Base de Données", lambda: self._show_tab(2)),
        ])
        root.addWidget(tab_bar)
        root.addSpacing(20)

        # Conteneur de contenu
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("background: transparent; border: none;")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        for c in self.all_contents:
            c.hide()
            self.content_layout.addWidget(c)

        root.addWidget(self.content_frame)
        self._show_tab(0)

    # ── Navigation onglets ────────────────────────────────
    def _show_tab(self, idx):
        for i, c in enumerate(self.all_contents):
            c.setVisible(i == idx)

    # ── Onglet SYSTÈME ────────────────────────────────────
    def _build_system_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 12, 0)

        # Charger les valeurs
        company_name    = self.db.get_setting('company_name',    'My Company')
        company_address = self.db.get_setting('company_address', '123 Rue Example, Alger')
        company_phone   = self.db.get_setting('company_phone',   '0555123456')
        company_email   = self.db.get_setting('company_email',   'contact@mycompany.dz')
        currency        = self.db.get_setting('currency',        'DA (Dinar Algérien)')
        vat             = self.db.get_setting('vat',             '19')
        vat_number      = self.db.get_setting('vat_number',      '123456789012345')

        # ── Carte Entreprise ──
        card_ent = SectionCard("🏢", "Informations de l'Entreprise")
        body = card_ent.body()

        # Logo preview
        logo_layout = QHBoxLayout()
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(80, 80)
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setStyleSheet(f"""
            QLabel {{
                background: {COLORS['BG_CARD']};
                border-radius: 10px;
                border: 2px solid {COLORS['BORDER']};
            }}
        """)
        
        logo_path = self.db.get_setting('logo_path', '')
        from PyQt6.QtGui import QPixmap
        if logo_path:
            try:
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation)
                    self.logo_preview.setPixmap(scaled_pixmap)
                else:
                    self.logo_preview.setText("📷")
                    self.logo_preview.setFont(QFont("Segoe UI", 32))
            except Exception as e:
                print(f"Erreur chargement logo: {e}")
                self.logo_preview.setText("📷")
                self.logo_preview.setFont(QFont("Segoe UI", 32))
        else:
            self.logo_preview.setText("📷")
            self.logo_preview.setFont(QFont("Segoe UI", 32))
        
        logo_btn = make_btn("🖼️  Changer Logo", COLORS['primary'], outlined=True)
        logo_btn.clicked.connect(self.change_logo)
        
        logo_layout.addWidget(self.logo_preview)
        logo_layout.addWidget(logo_btn)
        logo_layout.addStretch()
        body.addLayout(logo_layout)
        body.addSpacing(12)

        fields_ent = [
            ("Nom de l'entreprise",  company_name,    "company_name"),
            ("Adresse",              company_address, "address"),
            ("Téléphone",            company_phone,   "company_phone"),
            ("Email",                company_email,   "company_email"),
        ]
        for lbl_text, val, attr in fields_ent:
            field = QLineEdit(str(val))
            field.setStyleSheet(INPUT_STYLE)
            field.setMinimumHeight(42)
            setattr(self, attr, field)
            row = FieldRow(lbl_text, field)
            body.addLayout(row)

        layout.addWidget(card_ent)

        # ── Carte Finance ──
        card_fin = SectionCard("💰", "Configuration Financière")
        body2 = card_fin.body()

        fields_fin = [
            ("Devise",        currency,   "currency"),
            ("TVA (%)",       vat,        "vat"),
            ("Numéro de TVA", vat_number, "vat_number"),
        ]
        for lbl_text, val, attr in fields_fin:
            field = QLineEdit(str(val))
            field.setStyleSheet(INPUT_STYLE)
            field.setMinimumHeight(42)
            setattr(self, attr, field)
            row = FieldRow(lbl_text, field)
            body2.addLayout(row)

        layout.addWidget(card_fin)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    # ── Onglet APPARENCE ─────────────────────────────────
    def _build_appearance_tab(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        card = SectionCard("🎨", "Thème de l'Application")
        body = card.body()

        desc = QLabel("Choisissez le thème qui vous convient le mieux.")
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none;")
        body.addWidget(desc)

        row = QHBoxLayout()
        lbl = QLabel("Thème actif")
        lbl.setFont(QFont("Segoe UI", 11))
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none;")
        lbl.setFixedWidth(170)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["🌙  Mode Sombre", "☀️  Mode Clair"])
        self.theme_combo.setStyleSheet(COMBO_STYLE)
        self.theme_combo.setFont(QFont("Segoe UI", 11))
        self.theme_combo.currentIndexChanged.connect(self.change_theme)

        row.addWidget(lbl)
        row.addWidget(self.theme_combo)
        body.addLayout(row)

        layout.addWidget(card)
        layout.addStretch()
        return container

    # ── Onglet BASE DE DONNÉES ───────────────────────────
    def _build_database_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 12, 0)

        # ── Carte Sauvegarde ──
        card_bk = SectionCard("💾", "Sauvegarde des Données")
        body_bk = card_bk.body()

        desc_bk = QLabel("Créez ou restaurez une copie de sécurité complète de vos données.")
        desc_bk.setFont(QFont("Segoe UI", 11))
        desc_bk.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none;")
        body_bk.addWidget(desc_bk)

        last_backup = self.db.get_setting('last_backup_date', 'Aucune sauvegarde')
        self.last_backup_label = QLabel(f"📅 Dernière sauvegarde : {last_backup}")
        self.last_backup_label.setFont(QFont("Segoe UI", 10))
        self.last_backup_label.setStyleSheet(
            f"color: {COLORS['TXT_MUTED']}; background: transparent; border: none;")
        body_bk.addWidget(self.last_backup_label)

        bk_btns = QHBoxLayout()
        bk_btns.setSpacing(10)
        btn_create = make_btn("💾  Créer une Sauvegarde", COLORS['success'])
        btn_create.clicked.connect(self.create_backup)
        btn_restore = make_btn("📂  Restaurer", COLORS['primary'], outlined=True)
        btn_restore.clicked.connect(self.restore_backup)
        bk_btns.addWidget(btn_create)
        bk_btns.addWidget(btn_restore)
        bk_btns.addStretch()
        body_bk.addLayout(bk_btns)

        layout.addWidget(card_bk)

        # ── Carte Statistiques ──
        card_stats = SectionCard("📊", "Statistiques de la Base")
        body_stats = card_stats.body()

        self.stats_grid = QHBoxLayout()
        self.stats_grid.setSpacing(12)
        body_stats.addLayout(self.stats_grid)
        self.load_statistics()

        stats_btns = QHBoxLayout()
        stats_btns.setSpacing(10)
        btn_refresh = make_btn("🔄  Actualiser", COLORS['secondary_dark'], outlined=True)
        btn_refresh.setFixedWidth(160)
        btn_refresh.clicked.connect(self.refresh_stats)
        btn_test = make_btn("🧪  Données de Test", COLORS['secondary'])
        btn_test.setFixedWidth(200)
        btn_test.clicked.connect(self.generate_test_data)
        stats_btns.addWidget(btn_refresh)
        stats_btns.addWidget(btn_test)
        stats_btns.addStretch()
        body_stats.addLayout(stats_btns)

        layout.addWidget(card_stats)

        # ── Carte Danger ──
        card_danger = SectionCard("⚠️", "Zone de Danger")
        body_danger = card_danger.body()
        card_danger.setStyleSheet(f"""
            QFrame {{
                background: rgba(239,68,68,0.10);
                border-radius: 14px;
                border: 1px solid {COLORS['danger']}33;
            }}
        """)

        warn_lbl = QLabel("Cette action supprimera définitivement toutes les données (clients, produits, ventes, achats, historique). Elle est irréversible.")
        warn_lbl.setWordWrap(True)
        warn_lbl.setFont(QFont("Segoe UI", 11))
        warn_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none;")
        body_danger.addWidget(warn_lbl)

        btn_clean = make_btn("🗑️  Nettoyer la Base de Données", COLORS['danger'])
        btn_clean.setFixedWidth(280)
        btn_clean.clicked.connect(self.cleanup_database)
        body_danger.addWidget(btn_clean)

        layout.addWidget(card_danger)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    # ─────────────────────────────────────────────────────
    #  Méthodes métier (inchangées)
    # ─────────────────────────────────────────────────────

    def create_stat_item(self, icon, label, value, color):
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['BG_CARD']};
                border-radius: 10px;
                border: 1px solid {COLORS['BORDER']};
            }}
        """)
        il = QVBoxLayout(item)
        il.setContentsMargins(16, 16, 16, 16)
        il.setSpacing(6)
        il.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ic = QLabel(icon)
        ic.setFont(QFont("Segoe UI", 24))
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet("border: none; background: transparent;")
        il.addWidget(ic)

        vl = QLabel(str(value))
        vl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        vl.setStyleSheet(f"color: {color}; border: none; background: transparent;")
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(vl)

        tl = QLabel(label)
        tl.setFont(QFont("Segoe UI", 10))
        tl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none; background: transparent;")
        tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(tl)

        return item

    def load_statistics(self):
        while self.stats_grid.count():
            child = self.stats_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        stats = self.db.get_statistics()
        items = [
            ("👥", "Clients",  stats['total_clients'],   COLORS['secondary']),
            ("📆", "Produits", stats['total_products'],  COLORS['success']),
            ("💰", "Ventes",   stats['total_sales'],     COLORS['primary']),
            ("🛍️", "Achats",   stats['total_purchases'], COLORS['warning']),
        ]
        for icon, label, value, color in items:
            self.stats_grid.addWidget(self.create_stat_item(icon, label, value, color))

    def change_theme(self, index):
        qdarktheme.setup_theme("dark" if index == 0 else "light")

    def cleanup_database(self):
        reply = QMessageBox.warning(
            self, "⚠️ Confirmation",
            "Vous allez supprimer DÉFINITIVEMENT toutes les données.\n\nCette action est irréversible. Continuer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return

        text, ok = QInputDialog.getText(
            self, "Confirmation finale",
            'Tapez exactement  SUPPRIMER  pour confirmer :',
            QLineEdit.EchoMode.Normal, ""
        )
        if not ok or text != "SUPPRIMER":
            QMessageBox.information(self, "Annulé", "Le nettoyage a été annulé.")
            return

        try:
            prog = QMessageBox(self)
            prog.setWindowTitle("Nettoyage…")
            prog.setText("Suppression en cours, veuillez patienter.")
            prog.setStandardButtons(QMessageBox.StandardButton.NoButton)
            prog.show()
            QApplication.processEvents()
            success = self.db.clear_all_data()
            prog.close()
            if success:
                QMessageBox.information(self, "✅ Terminé", "Base de données nettoyée avec succès.")
                self.refresh_stats()
            else:
                QMessageBox.critical(self, "Erreur", "Une erreur est survenue lors du nettoyage.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{e}")

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder", f"erp_backup_{timestamp}.db",
            "Base de données (*.db);;Tous (*.*)"
        )
        if filename:
            try:
                if self.db.backup_database(filename):
                    now = datetime.now().strftime("%d/%m/%Y %H:%M")
                    self.db.set_setting('last_backup_date', now)
                    self.last_backup_label.setText(f"📅 Dernière sauvegarde : {now}")
                    QMessageBox.information(self, "✅ Sauvegarde créée", f"Fichier : {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer la sauvegarde :\n{e}")

    def restore_backup(self):
        reply = QMessageBox.warning(
            self, "⚠️ Restauration",
            "La restauration remplacera toutes les données actuelles. Continuer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return
        filename, _ = QFileDialog.getOpenFileName(
            self, "Restaurer", "", "Base de données (*.db);;Tous (*.*)"
        )
        if filename:
            try:
                if self.db.restore_database(filename):
                    QMessageBox.information(self, "✅ Restauré",
                                            "Données restaurées. Redémarrez l'application.")
                    self.refresh_stats()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de restaurer :\n{e}")

    def refresh_stats(self):
        self.load_statistics()

    def generate_test_data(self):
        reply = QMessageBox.question(
            self, "🧪 Données de Test",
            "Générer des clients, produits, catégories et fournisseurs exemples?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.populate_test_data()
                QMessageBox.information(self, "✅ Généré", "Données de test créées avec succès.")
                self.refresh_stats()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur:\n{e}")

    def save_settings(self):
        try:
            self.db.set_setting('company_name',    self.company_name.text())
            self.db.set_setting('company_address', self.address.text())
            self.db.set_setting('company_phone',   self.company_phone.text())
            self.db.set_setting('company_email',   self.company_email.text())
            self.db.set_setting('currency',        self.currency.text())
            self.db.set_setting('vat',             self.vat.text())
            self.db.set_setting('vat_number',      self.vat_number.text())
            QMessageBox.information(self, "✅ Enregistré", "Paramètres enregistrés avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement:\n{e}")

    def reset_settings(self):
        reply = QMessageBox.question(
            self, "Réinitialiser",
            "Réinitialiser tous les paramètres aux valeurs par défaut?",
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

    def change_logo(self):
        """Change le logo de l'entreprise"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Choisir un logo", "",
            "Images (*.png *.jpg *.jpeg *.bmp);;Tous (*.*)"
        )
        if filename:
            try:
                from PyQt6.QtGui import QPixmap
                
                # Chargez et validez l'image avec QPixmap
                pixmap = QPixmap(filename)
                if pixmap.isNull():
                    QMessageBox.critical(self, "❌ Erreur", "La file n'est pas une image valide.")
                    return
                
                # Resize et affichage
                scaled_pixmap = pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation)
                self.logo_preview.setPixmap(scaled_pixmap)
                
                # Sauvegardez le chemin complet
                self.db.set_setting('logo_path', filename)
                print(f"✅ Logo sauvegardé: {filename}")
                QMessageBox.information(self, "✅ Logo changé", f"Logo mis à jour avec succès.\n\nChemin: {filename}")
            except Exception as e:
                print(f"Erreur: {e}")
                QMessageBox.critical(self, "❌ Erreur", f"Impossible de charger l'image :\n{str(e)}")