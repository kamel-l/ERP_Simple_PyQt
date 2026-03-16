from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QLineEdit, QDialog, QFormLayout,
    QFrame, QMessageBox, QTabWidget, QScrollArea, QGridLayout, QSizePolicy,
    QSpacerItem, QProgressBar
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from auth import session
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
from currency import fmt_da, fmt, currency_manager  # IMPORT DE LA FONCTION DE FORMATAGE

# ------------------ DIALOG POUR AJOUTER / MODIFIER CLIENT ------------------
class ClientDialog(QDialog):
    def __init__(self, name="", phone="", email="", address="", client_id=None):
        super().__init__()

        self.client_id = client_id
        self.setWindowTitle("📝 Détails du Client") 
        self.setMinimumWidth(500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['BG_CARD']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            {INPUT_STYLE}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Titre
        title_text = "Modifier le Client" if client_id else "Nouveau Client"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Entrez le nom du client")
        
        self.phone_edit = QLineEdit(phone)
        self.phone_edit.setPlaceholderText("Ex: 0555123456")
        
        self.email_edit = QLineEdit(email)
        self.email_edit.setPlaceholderText("email@exemple.com")
        
        self.address_edit = QLineEdit(address)
        self.address_edit.setPlaceholderText("Adresse du client")

        form.addRow("Nom:", self.name_edit)
        form.addRow("Téléphone:", self.phone_edit)
        form.addRow("Email:", self.email_edit)
        form.addRow("Adresse:", self.address_edit)

        main_layout.addLayout(form)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet(BUTTON_STYLES['success'])
        save_btn.clicked.connect(self.accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)


# ------------------ PAGE CLIENTS ------------------
class ClientsPage(QWidget):
    # Signal émis quand un client est ajouté ou modifié
    client_added = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Connexion à la base de données
        self.db = get_database()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ------------------- HEADER -------------------
        title = QLabel("👥 Gestion des Clients")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['BG_CARD']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Gérez vos clients et leurs informations")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # ------------------- STATISTICS CARDS -------------------
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(15)
        layout.addLayout(self.stats_layout)

        # Les cartes seront créées dans load_statistics()
        self.load_statistics()
        self.stats_layout.addStretch()

        # ------------------- SEARCH & ACTIONS BAR -------------------
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)
        layout.addLayout(search_layout)

        # Barre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom ou email...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.filter_clients)
        self.search_input.setMinimumHeight(45)
        search_layout.addWidget(self.search_input)

        # Bouton Ajouter
        self.add_btn = QPushButton("➕ Nouveau Client")
        self.add_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_btn.setFixedWidth(180)
        self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_client)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(self.add_btn)

        # ------------------- CLIENT TABLE -------------------
        table_container = QFrame()
        table_container.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 0px;
            }}
        """
        )
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        table_container.setLayout(table_layout)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nom", "Téléphone", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 120)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(TABLE_STYLE + f"""
            QHeaderView::section {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid {COLORS['border']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
        """)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_container)
        
        self.load_clients()  # Charger les clients à l'affichage de la page

        # ------------------- ACTIONS BUTTONS -------------------
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        layout.addLayout(actions_layout)

        self.edit_btn = QPushButton("✏️ Modifier")
        self.edit_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.edit_btn.clicked.connect(self.edit_client)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setMinimumHeight(40)
        
        self.delete_btn = QPushButton("🗑️ Supprimer")
        self.delete_btn.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_btn.clicked.connect(self.delete_client)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setMinimumHeight(40)

        actions_layout.addStretch()
        actions_layout.addWidget(self.edit_btn)
        actions_layout.addWidget(self.delete_btn)

        # Charger les données
        self.load_clients()

    def build_stat_card(self, title, value, color):
        """Construit une petite carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        card.setFixedHeight(80)
        card.setMinimumWidth(180)

        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setSpacing(5)
        card_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        card_layout.addWidget(title_label)

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        card_layout.addWidget(value_label)

        return card

    def load_statistics(self):
        """Charge les statistiques depuis la base de données"""
        # Effacer les anciennes cartes
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Récupérer les stats
        stats = self.db.get_statistics()
        
        # Créer les cartes
        self.stats_layout.addWidget(
            self.build_stat_card("Total Clients", stats['total_clients'], COLORS['primary'])
        )
        self.stats_layout.addWidget(
            self.build_stat_card("Clients actifs", stats['total_clients'], COLORS['success'])
        )

    # ------------------ CHARGEMENT DES DONNÉES ------------------
    def load_clients(self):
        """Charge tous les clients depuis la base de données"""
        self.table.setRowCount(0)
        clients = self.db.get_all_clients()
        
        for client in clients:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Stocker l'ID dans la colonne Nom (UserRole invisible)
            name_item = QTableWidgetItem(client["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, client["id"])
            name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

            phone_item = QTableWidgetItem(client["phone"] or "—")

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, phone_item)
            
            # Bouton Fiche
            btn = QPushButton("📋 Voir Fiche")
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0,180,255,0.15); color: #00B4FF;
                    border: 1px solid rgba(0,180,255,0.4);
                    border-radius: 6px; font-size: 11px; font-weight: bold; padding: 0 10px;
                }
                QPushButton:hover { background: rgba(0,180,255,0.3); color: white; }
            """)
            cid = client["id"]
            btn.clicked.connect(lambda _, i=cid: self.open_fiche(i))
            self.table.setCellWidget(row, 2, btn)
            self.table.setRowHeight(row, 46)

    # ------------------ RECHERCHE ------------------
    def filter_clients(self, text):
        """Filtre les clients par nom ou email"""
        if not text:
            self.load_clients()
            return
        
        self.table.setRowCount(0)
        # Si la recherche est une lettre unique (a-z, A-Z)
        if len(text) == 1 and text.isalpha():
            clients = self.db.search_clients_by_first_letter(text)
        else:
            clients = self.db.search_clients(text)
        
        for client in clients:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            name_item = QTableWidgetItem(client["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, client["id"])
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, QTableWidgetItem(client["phone"] or "—"))
            
            # Bouton Fiche
            btn = QPushButton("📋 Voir Fiche")
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0,180,255,0.15); color: #00B4FF;
                    border: 1px solid rgba(0,180,255,0.4);
                    border-radius: 6px; font-size: 11px; font-weight: bold; padding: 0 10px;
                }
                QPushButton:hover { background: rgba(0,180,255,0.3); color: white; }
            """)
            cid = client["id"]
            btn.clicked.connect(lambda _, i=cid: self.open_fiche(i))
            self.table.setCellWidget(row, 2, btn)
            self.table.setRowHeight(row, 46)

    # ------------------ FICHE CLIENT ------------------
    def open_fiche(self, client_id: int) -> None:
        """Ouvre la fiche détaillée d'un client."""
        client = self.db.get_client_by_id(client_id)
        if not client:
            QMessageBox.warning(self, "Erreur", "Client introuvable.")
            return
        dlg = ClientFicheDialog(client, self.db, parent=self)
        dlg.exec()

    # ------------------ AJOUTER CLIENT ------------------
    def add_client(self):
        """Ajoute un nouveau client"""
        if not session.can('add_client'):
            QMessageBox.warning(self, "Accès refusé", "Votre rôle ne permet pas d'ajouter des clients.")
            return
        dialog = ClientDialog()
        if dialog.exec():
            name = dialog.name_edit.text().strip()
            phone = dialog.phone_edit.text().strip()
            email = dialog.email_edit.text().strip()
            address = dialog.address_edit.text().strip()
            
            if not name:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Le nom du client est obligatoire!"
                )
                return
            
            client_id = self.db.add_client(name, phone, email, address)
            
            if client_id:
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Client '{name}' ajouté avec succès!"
                )
                self.load_clients()
                self.load_statistics()
                # Émettre le signal pour notifier les autres modules
                self.client_added.emit()
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible d'ajouter le client!"
                )

    # ------------------ MODIFIER CLIENT ------------------
    def edit_client(self):
        """Modifie un client existant"""
        if not session.can('edit_client'):
            QMessageBox.warning(self, "Accès refusé", "Votre rôle ne permet pas de modifier des clients.")
            return
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez sélectionner un client à modifier!"
            )
            return
        
        # Récupérer l'ID du client
        client_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        
        # Récupérer les données du client
        client = self.db.get_client_by_id(client_id)
        
        if not client:
            QMessageBox.critical(
                self,
                "Erreur",
                "Client introuvable!"
            )
            return
        
        # Ouvrir le dialogue avec les données existantes
        dialog = ClientDialog(
            name=client["name"],
            phone=client["phone"] or "",
            email=client["email"] or "",
            address=client["address"] or "",
            client_id=client_id
        )
        
        if dialog.exec():
            name = dialog.name_edit.text().strip()
            phone = dialog.phone_edit.text().strip()
            email = dialog.email_edit.text().strip()
            address = dialog.address_edit.text().strip()
            
            if not name:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Le nom du client est obligatoire!"
                )
                return
            
            if self.db.update_client(client_id, name, phone, email, address):
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Client '{name}' modifié avec succès!"
                )
                self.load_clients()
                # Émettre le signal pour notifier les autres modules
                self.client_added.emit()
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible de modifier le client!"
                )

    # ------------------ SUPPRIMER CLIENT ------------------
    def delete_client(self):
        """Supprime un client"""
        if not session.can('delete_client'):
            QMessageBox.warning(self, "Accès refusé", "Seul un administrateur peut supprimer des clients.")
            return
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez sélectionner un client à supprimer!"
            )
            return
        
        # Récupérer l'ID et le nom du client
        client_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        client_name = self.table.item(selected, 0).text()
        
        # Confirmation
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer le client '{client_name}'?\n\n"
            "Cette action est irréversible!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_client(client_id):
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Client '{client_name}' supprimé avec succès!"
                )
                self.load_clients()
                self.load_statistics()
                # Émettre le signal pour notifier les autres modules
                self.client_added.emit()
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible de supprimer le client!"
                )

# ═══════════════════════════════════════════════════════════════
#  FICHE CLIENT — Dialog avec onglets complets
# ═══════════════════════════════════════════════════════════════

class ClientFicheDialog(QDialog):
    """Fiche détaillée d'un client : infos, factures, paiements, statistiques."""

    _CARD_STYLE = """
        QFrame {{
            background: {bg};
            border-radius: 10px;
            border: 1px solid {border};
        }}
    """

    def __init__(self, client: dict, db, parent=None):
        super().__init__(parent)
        self.client = client
        self.db     = db
        self.setWindowTitle(f"📋 Fiche Client — {client.get('name','')}")
        self.setMinimumSize(820, 620)
        self.setStyleSheet(f"""
            QDialog {{
                background: {COLORS.get('bg_page', '#1E1E2E')};
            }}
            QTabWidget::pane {{
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 10px;
                background: {COLORS.get('bg_card', '#252535')};
            }}
            QTabBar::tab {{
                background: {COLORS.get('bg_deep', '#16161F')};
                color: {COLORS.get('text_secondary', '#A0AACC')};
                padding: 10px 22px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px 8px 0 0;
                margin-right: 3px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS.get('primary', '#00B4FF')};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background: rgba(0,180,255,0.15);
                color: white;
            }}
            QLabel {{ color: {COLORS.get('text_primary', '#F0F4FF')}; background: transparent; }}
            QTableWidget {{
                background: {COLORS.get('bg_deep', '#16161F')};
                color: {COLORS.get('text_primary', '#F0F4FF')};
                border: none;
                gridline-color: rgba(255,255,255,0.05);
                font-size: 11px;
            }}
            QHeaderView::section {{
                background: rgba(0,180,255,0.12);
                color: #00B4FF;
                font-size: 11px;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #00B4FF;
            }}
            QTableWidget::item {{ padding: 6px 8px; }}
            QTableWidget::item:selected {{
                background: rgba(0,180,255,0.18);
                color: white;
            }}
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── En-tête ────────────────────────────────────────────
        hdr = self._build_header()
        main.addWidget(hdr)

        # ── Onglets ────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.addTab(self._tab_infos(),      "👤  Informations")
        tabs.addTab(self._tab_factures(),   "🧾  Factures")
        tabs.addTab(self._tab_paiements(),  "💳  Paiements")
        tabs.addTab(self._tab_statistiques(), "📊  Statistiques")
        main.addWidget(tabs)

        # ── Bouton fermer ──────────────────────────────────────
        close_btn = QPushButton("✖  Fermer")
        close_btn.setFixedHeight(38)
        close_btn.setFixedWidth(130)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.07); color: #A0AACC;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 8px; font-size: 12px;
            }
            QPushButton:hover { background: rgba(255,80,80,0.18); color: #FF6060; }
        """)
        close_btn.clicked.connect(self.accept)
        row_close = QHBoxLayout()
        row_close.addStretch()
        row_close.addWidget(close_btn)
        main.addLayout(row_close)

    # ── En-tête coloré ─────────────────────────────────────────
    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0,180,255,0.18), stop:1 rgba(0,229,255,0.08));
                border-radius: 12px;
                border: 1px solid rgba(0,180,255,0.25);
            }}
        """)
        frame.setFixedHeight(90)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(20, 12, 20, 12)
        lay.setSpacing(18)

        avatar = QLabel(self.client.get('name','?')[0].upper())
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        avatar.setStyleSheet("""
            background: #00B4FF; color: white;
            border-radius: 28px; border: none;
        """)
        lay.addWidget(avatar)

        col = QVBoxLayout()
        col.setSpacing(2)
        name_lbl = QLabel(self.client.get('name', '—'))
        name_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        name_lbl.setStyleSheet("color: #F0F4FF;")
        col.addWidget(name_lbl)

        sub_parts = []
        if self.client.get('phone'): sub_parts.append(f"📞 {self.client['phone']}")
        if self.client.get('email'): sub_parts.append(f"✉ {self.client['email']}")
        sub_lbl = QLabel("   ·   ".join(sub_parts) if sub_parts else "Aucune coordonnée")
        sub_lbl.setFont(QFont("Segoe UI", 10))
        sub_lbl.setStyleSheet("color: rgba(160,170,204,0.85);")
        col.addWidget(sub_lbl)
        lay.addLayout(col, 1)

        # Badge ID
        id_lbl = QLabel(f"#{self.client.get('id','')}")
        id_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        id_lbl.setStyleSheet("""
            color: #00B4FF; background: rgba(0,180,255,0.12);
            border-radius: 8px; padding: 4px 12px; border: 1px solid rgba(0,180,255,0.3);
        """)
        lay.addWidget(id_lbl)
        return frame

    # ── Onglet 1 : Informations ────────────────────────────────
    def _tab_infos(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        def info_row(icon, label, value):
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: {COLORS.get('bg_deep','#16161F')};
                    border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 10, 14, 10)
            rl.setSpacing(12)

            ico = QLabel(icon)
            ico.setFixedWidth(24)
            ico.setFont(QFont("Segoe UI", 14))
            ico.setStyleSheet("border:none; background:transparent;")
            rl.addWidget(ico)

            lbl = QLabel(label)
            lbl.setFixedWidth(130)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: rgba(160,170,204,0.8); border:none; background:transparent;")
            rl.addWidget(lbl)

            val = QLabel(str(value) if value else "—")
            val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            val.setStyleSheet("color: #F0F4FF; border:none; background:transparent;")
            val.setWordWrap(True)
            rl.addWidget(val, 1)
            return row

        lay.addWidget(info_row("👤", "Nom complet",  self.client.get('name')))
        lay.addWidget(info_row("📞", "Téléphone",    self.client.get('phone')))
        lay.addWidget(info_row("✉️",  "Email",        self.client.get('email')))
        lay.addWidget(info_row("📍", "Adresse",      self.client.get('address')))
        lay.addWidget(info_row("🗓️", "Créé le",      str(self.client.get('created_at','—')).split(' ')[0]))
        lay.addStretch()
        return w

    # ── Onglet 2 : Factures ────────────────────────────────────
    def _tab_factures(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        # Récupérer les factures du client
        try:
            self.db.cursor.execute("""
                SELECT id, invoice_number, sale_date, total,
                       payment_method, payment_status
                FROM sales
                WHERE client_id = ?
                ORDER BY sale_date DESC
            """, (self.client['id'],))
            rows = [dict(r) for r in self.db.cursor.fetchall()]
        except Exception:
            rows = []

        # Résumé
        total_ca = sum(float(r.get('total',0)) for r in rows)
        summary = QHBoxLayout()
        for txt, val, col in [
            ("Nombre de factures", str(len(rows)), "#00B4FF"),
            ("Chiffre d'affaires total", fmt_da(total_ca), "#10B981"),  # 🔴 FORMATAGE ICI
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ background: rgba(0,0,0,0.2); border-radius:8px;
                          border: 1px solid {col}33; }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)
            vl = QLabel(val)
            vl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            vl.setStyleSheet(f"color:{col};border:none;")
            tl = QLabel(txt)
            tl.setFont(QFont("Segoe UI", 9))
            tl.setStyleSheet("color:rgba(160,170,204,0.8);border:none;")
            cl.addWidget(vl)
            cl.addWidget(tl)
            summary.addWidget(card)
        summary.addStretch()
        lay.addLayout(summary)

        # Tableau
        tbl = QTableWidget(len(rows), 5)
        tbl.setHorizontalHeaderLabels(["N° Facture","Date","Total","Paiement","Statut"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.verticalHeader().setVisible(False)
        tbl.setAlternatingRowColors(True)

        STATUS_COLOR = {
            'paid': ('#10B981', '✅ Payée'),
            'pending': ('#F59E0B', '⏳ En attente'),
            'cancelled': ('#EF4444', '❌ Annulée'),
        }

        for i, r in enumerate(rows):
            date = str(r.get('sale_date','—')).split(' ')[0]
            total = float(r.get('total') or 0)
            status = r.get('payment_status','paid')
            col_s, lbl_s = STATUS_COLOR.get(status, ('#A0AACC', status))

            cells = [
                (r.get('invoice_number','—'), '#F0F4FF'),
                (date,                        '#A0AACC'),
                (fmt_da(total),                '#10B981'),  # 🔴 FORMATAGE ICI
                (r.get('payment_method','—'), '#A0AACC'),
                (lbl_s,                       col_s),
            ]
            for j, (val, color) in enumerate(cells):
                item = QTableWidgetItem(str(val))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                tbl.setItem(i, j, item)
            tbl.setRowHeight(i, 38)

        if not rows:
            tbl.setRowCount(1)
            msg = QTableWidgetItem("Aucune facture pour ce client")
            msg.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setForeground(QColor('#A0AACC'))
            msg.setFlags(msg.flags() & ~Qt.ItemFlag.ItemIsEditable)
            tbl.setItem(0, 0, msg)
            tbl.setSpan(0, 0, 1, 5)

        lay.addWidget(tbl)
        return w

    # ── Onglet 3 : Paiements ───────────────────────────────────
    def _tab_paiements(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        try:
            self.db.cursor.execute("""
                SELECT invoice_number, sale_date, total,
                       payment_method, payment_status
                FROM sales
                WHERE client_id = ?
                ORDER BY sale_date DESC
            """, (self.client['id'],))
            rows = [dict(r) for r in self.db.cursor.fetchall()]
        except Exception:
            rows = []

        # Regrouper par mode de paiement
        from collections import defaultdict
        by_method = defaultdict(lambda: {'count': 0, 'total': 0.0})
        for r in rows:
            m = r.get('payment_method') or 'Autre'
            by_method[m]['count'] += 1
            by_method[m]['total'] += float(r.get('total') or 0)

        METHOD_ICON = {'cash': '💵', 'credit': '💳', 'cheque': '🏦',
                       'virement': '🔄', 'Autre': '❓'}
        METHOD_COLOR = {'cash': '#10B981', 'credit': '#6366F1',
                        'cheque': '#F59E0B', 'virement': '#00B4FF', 'Autre': '#A0AACC'}

        # Cartes par méthode
        cards_row = QHBoxLayout()
        for method, data in by_method.items():
            icon  = METHOD_ICON.get(method, '💰')
            color = METHOD_COLOR.get(method, '#A0AACC')
            card  = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ background: rgba(0,0,0,0.2);
                          border-radius: 10px; border: 1px solid {color}44; }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(4)
            
            lbl_m = QLabel(f"{icon} {method.capitalize()}")
            lbl_m.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            lbl_m.setStyleSheet(f"color:{color};border:none;")
            cl.addWidget(lbl_m)
            
            # 🔴 UTILISATION DE fmt_da POUR LE MONTANT
            lbl_v = QLabel(fmt_da(data['total']))
            lbl_v.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            lbl_v.setStyleSheet(f"color:#F0F4FF;border:none;")
            cl.addWidget(lbl_v)
            
            lbl_c = QLabel(f"{data['count']} transaction{'s' if data['count']>1 else ''}")
            lbl_c.setFont(QFont("Segoe UI", 9))
            lbl_c.setStyleSheet("color:rgba(160,170,204,0.8);border:none;")
            cl.addWidget(lbl_c)
            cards_row.addWidget(card)

        if not by_method:
            no_lbl = QLabel("Aucun paiement enregistré")
            no_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_lbl.setStyleSheet("color:#A0AACC;font-size:12px;")
            cards_row.addWidget(no_lbl)

        cards_row.addStretch()
        lay.addLayout(cards_row)

        # Tableau historique paiements
        tbl = QTableWidget(len(rows), 4)
        tbl.setHorizontalHeaderLabels(["N° Facture","Date","Mode de Paiement","Montant"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.verticalHeader().setVisible(False)
        tbl.setAlternatingRowColors(True)

        for i, r in enumerate(rows):
            date   = str(r.get('sale_date','—')).split(' ')[0]
            method = r.get('payment_method') or '—'
            total  = float(r.get('total') or 0)
            icon   = METHOD_ICON.get(method, '💰')
            color  = METHOD_COLOR.get(method, '#A0AACC')

            for j, (val, col) in enumerate([
                (r.get('invoice_number','—'), '#F0F4FF'),
                (date,                        '#A0AACC'),
                (f"{icon} {method}",          color),
                (fmt_da(total),                '#10B981'),  # 🔴 FORMATAGE ICI
            ]):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(col))
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                tbl.setItem(i, j, it)
            tbl.setRowHeight(i, 38)

        lay.addWidget(tbl)
        return w

    # ── Onglet 4 : Statistiques ────────────────────────────────
    def _tab_statistiques(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)

        try:
            self.db.cursor.execute("""
                SELECT COUNT(*) as nb_ventes,
                       COALESCE(SUM(total),0) as ca_total,
                       COALESCE(AVG(total),0) as panier_moyen,
                       COALESCE(MAX(total),0) as plus_grosse,
                       COALESCE(MIN(total),0) as plus_petite,
                       MIN(sale_date) as premiere_vente,
                       MAX(sale_date) as derniere_vente
                FROM sales WHERE client_id = ?
            """, (self.client['id'],))
            st = dict(self.db.cursor.fetchone() or {})
        except Exception:
            st = {}

        # Meilleure catégorie de produits achetés
        try:
            self.db.cursor.execute("""
                SELECT p.name, SUM(si.quantity) as qty
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                LEFT JOIN products p ON si.product_id = p.id
                WHERE s.client_id = ?
                GROUP BY si.product_id
                ORDER BY qty DESC LIMIT 5
            """, (self.client['id'],))
            top_products = self.db.cursor.fetchall()
        except Exception:
            top_products = []

        def stat_card(icon, label, value, color='#00B4FF'):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ background: rgba(0,0,0,0.25);
                          border-radius: 10px; border: 1px solid {color}33; }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(3)
            il = QLabel(f"{icon}")
            il.setFont(QFont("Segoe UI", 20))
            il.setStyleSheet("border:none;")
            cl.addWidget(il)
            vl = QLabel(str(value))
            vl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            vl.setStyleSheet(f"color:{color};border:none;")
            cl.addWidget(vl)
            tl = QLabel(label)
            tl.setFont(QFont("Segoe UI", 9))
            tl.setStyleSheet("color:rgba(160,170,204,0.8);border:none;")
            cl.addWidget(tl)
            return card

        grid = QGridLayout()
        grid.setSpacing(10)

        nb   = int(st.get('nb_ventes', 0))
        ca   = float(st.get('ca_total', 0))
        avg  = float(st.get('panier_moyen', 0))
        big  = float(st.get('plus_grosse', 0))
        prem = str(st.get('premiere_vente','—')).split(' ')[0]
        last = str(st.get('derniere_vente','—')).split(' ')[0]

        grid.addWidget(stat_card("🧾", "Nb de ventes",        str(nb),                 '#00B4FF'), 0, 0)
        # 🔴 UTILISATION DE fmt_da POUR TOUS LES MONTANTS
        grid.addWidget(stat_card("💰", "Chiffre d'affaires",  fmt_da(ca),              '#10B981'), 0, 1)
        grid.addWidget(stat_card("🛒", "Panier moyen",        fmt_da(avg),             '#6366F1'), 0, 2)
        grid.addWidget(stat_card("🏆", "Plus grosse facture", fmt_da(big),             '#F59E0B'), 1, 0)
        grid.addWidget(stat_card("📅", "Première visite",     prem,                    '#A0AACC'), 1, 1)
        grid.addWidget(stat_card("🕐", "Dernière visite",     last,                    '#A0AACC'), 1, 2)
        lay.addLayout(grid)

        # Top produits achetés
        if top_products:
            top_lbl = QLabel("🛍️  Produits les plus achetés")
            top_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            top_lbl.setStyleSheet("color:#F0F4FF;")
            lay.addWidget(top_lbl)

            max_qty = max(int(r[1] if not hasattr(r,'keys') else r['qty']) for r in top_products) or 1
            for r in top_products:
                name = str(r[0] if not hasattr(r,'keys') else r['name']) or 'Produit supprimé'
                qty  = int(r[1] if not hasattr(r,'keys') else r['qty'])
                rw = QFrame()
                rw.setStyleSheet("QFrame{background:rgba(0,0,0,0.18);border-radius:8px;border:1px solid rgba(255,255,255,0.05);}")
                rl = QHBoxLayout(rw)
                rl.setContentsMargins(12, 8, 12, 8)
                rl.setSpacing(10)
                nl = QLabel(name[:32])
                nl.setFont(QFont("Segoe UI", 10))
                nl.setStyleSheet("color:#F0F4FF;border:none;")
                rl.addWidget(nl, 1)
                bar = QProgressBar()
                bar.setRange(0, max_qty)
                bar.setValue(qty)
                bar.setTextVisible(False)
                bar.setFixedHeight(8)
                bar.setFixedWidth(160)
                bar.setStyleSheet("""
                    QProgressBar{background:rgba(0,180,255,0.1);border-radius:4px;border:none;}
                    QProgressBar::chunk{background:#00B4FF;border-radius:4px;}
                """)
                rl.addWidget(bar)
                ql = QLabel(f"{qty} u.")
                ql.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                ql.setStyleSheet("color:#00B4FF;border:none;")
                ql.setFixedWidth(45)
                rl.addWidget(ql)
                lay.addWidget(rw)

        lay.addStretch()
        return w