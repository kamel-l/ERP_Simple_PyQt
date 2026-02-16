from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QLineEdit, QDialog, QFormLayout, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database

# ------------------ DIALOG POUR AJOUTER / MODIFIER CLIENT ------------------
class ClientDialog(QDialog):
    def __init__(self, name="", phone="", email="", address="", client_id=None):
        super().__init__()

        self.client_id = client_id
        self.setWindowTitle("📝 Détails du Client")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_medium']};
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
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
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
        table_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        table_layout = QVBoxLayout()
        table_container.setLayout(table_layout)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Téléphone", "Email", "Adresse"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

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
                border-left: 4px solid {color};
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
            
            # ID
            id_item = QTableWidgetItem(str(client["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setData(Qt.ItemDataRole.UserRole, client["id"])  # Stocker l'ID
            
            # Nom
            name_item = QTableWidgetItem(client["name"])
            
            # Téléphone
            phone_item = QTableWidgetItem(client["phone"] or "")
            
            # Email
            email_item = QTableWidgetItem(client["email"] or "")
            
            # Adresse
            address_item = QTableWidgetItem(client["address"] or "")
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, phone_item)
            self.table.setItem(row, 3, email_item)
            self.table.setItem(row, 4, address_item)

    # ------------------ RECHERCHE ------------------
    def filter_clients(self, text):
        """Filtre les clients par nom ou email"""
        if not text:
            self.load_clients()
            return
        
        self.table.setRowCount(0)
        clients = self.db.search_clients(text)
        
        for client in clients:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            id_item = QTableWidgetItem(str(client["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setData(Qt.ItemDataRole.UserRole, client["id"])
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(client["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(client["phone"] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(client["email"] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(client["address"] or ""))

    # ------------------ AJOUTER CLIENT ------------------
    def add_client(self):
        """Ajoute un nouveau client"""
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
        client_name = self.table.item(selected, 1).text()
        
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