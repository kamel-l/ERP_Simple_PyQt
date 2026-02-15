from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QLineEdit, QDialog, QFormLayout, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE

# ------------------ DIALOG POUR AJOUTER / MODIFIER CLIENT ------------------
class ClientDialog(QDialog):
    def __init__(self, name="", phone="", email=""):
        super().__init__()

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
        title = QLabel("Informations du Client")
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

        form.addRow("Nom:", self.name_edit)
        form.addRow("Téléphone:", self.phone_edit)
        form.addRow("Email:", self.email_edit)

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
    def __init__(self):
        super().__init__()

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
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        layout.addLayout(stats_layout)

        stats_layout.addWidget(self.build_stat_card("Total Clients", "59", COLORS['primary']))
        stats_layout.addWidget(self.build_stat_card("Nouveaux ce mois", "+7", COLORS['success']))
        stats_layout.addWidget(self.build_stat_card("Clients actifs", "52", COLORS['secondary']))
        stats_layout.addStretch()

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
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Téléphone", "Email"])
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

        # ------------------- DONNÉES EXEMPLE -------------------
        self.clients_data = [
            {"id": 1, "name": "John Doe", "phone": "0555123456", "email": "john@example.com"},
            {"id": 2, "name": "Alice Smith", "phone": "0555987654", "email": "alice@example.com"},
            {"id": 3, "name": "Entreprise X", "phone": "0555001122", "email": "contact@companyx.com"},
            {"id": 4, "name": "Bob Martin", "phone": "0555445566", "email": "bob@example.com"},
            {"id": 5, "name": "Marie Dupont", "phone": "0555778899", "email": "marie@example.com"},
        ]
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

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        card_layout.addWidget(value_label)

        return card

    # ------------------ CHARGEMENT DES DONNÉES ------------------
    def load_clients(self):
        self.table.setRowCount(0)
        for client in self.clients_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Style pour chaque cellule
            id_item = QTableWidgetItem(str(client["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            name_item = QTableWidgetItem(client["name"])
            phone_item = QTableWidgetItem(client["phone"])
            email_item = QTableWidgetItem(client["email"])
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, phone_item)
            self.table.setItem(row, 3, email_item)

    # ------------------ RECHERCHE ------------------
    def filter_clients(self, text):
        text = text.lower()
        filtered = [c for c in self.clients_data 
                   if text in c["name"].lower() or text in c["email"].lower()]
        
        self.table.setRowCount(0)
        for client in filtered:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            id_item = QTableWidgetItem(str(client["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(client["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(client["phone"]))
            self.table.setItem(row, 3, QTableWidgetItem(client["email"]))

    # ------------------ AJOUTER CLIENT ------------------
    def add_client(self):
        dialog = ClientDialog()
        if dialog.exec():
            new_id = max([c["id"] for c in self.clients_data]) + 1 if self.clients_data else 1
            self.clients_data.append({
                "id": new_id,
                "name": dialog.name_edit.text(),
                "phone": dialog.phone_edit.text(),
                "email": dialog.email_edit.text()
            })
            self.load_clients()

    # ------------------ MODIFIER CLIENT ------------------
    def edit_client(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        client = self.clients_data[selected]
        dialog = ClientDialog(client["name"], client["phone"], client["email"])
        if dialog.exec():
            client["name"] = dialog.name_edit.text()
            client["phone"] = dialog.phone_edit.text()
            client["email"] = dialog.email_edit.text()
            self.load_clients()

    # ------------------ SUPPRIMER CLIENT ------------------
    def delete_client(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        del self.clients_data[selected]
        self.load_clients()