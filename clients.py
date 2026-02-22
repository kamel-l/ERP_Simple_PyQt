from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QScrollArea
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS
from db_manager import get_database


class ClientsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.db = get_database()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)

        # ----------------------------------------------------------
        # HEADER
        # ----------------------------------------------------------
        header = QHBoxLayout()
        title = QLabel("👥 Clients")
        title.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")

        header.addWidget(title)
        header.addStretch()

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Rechercher un client…")
        self.search.textChanged.connect(self.search_client)
        self.search.setFixedWidth(250)
        header.addWidget(self.search)

        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                padding: 10px 22px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                color: black;
            }}
            QPushButton:hover {{
                background: {COLORS['accent_light']};
            }}
        """)
        refresh_btn.clicked.connect(self.load_clients)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # ----------------------------------------------------------
        # CLIENT FORM
        # ----------------------------------------------------------
        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(16)

        form_title = QLabel("Ajouter / Modifier un Client")
        form_title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        form_title.setStyleSheet(f"color: {COLORS['accent']};")
        form_layout.addWidget(form_title)

        # Inputs
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Nom du client…")
        form_layout.addWidget(self.input_name)

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Téléphone…")
        form_layout.addWidget(self.input_phone)

        self.input_address = QLineEdit()
        self.input_address.setPlaceholderText("Adresse…")
        form_layout.addWidget(self.input_address)

        # Buttons
        btn_row = QHBoxLayout()

        add_btn = QPushButton("➕ Ajouter")
        add_btn.clicked.connect(self.add_client)
        btn_row.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Modifier")
        edit_btn.clicked.connect(self.update_client)
        btn_row.addWidget(edit_btn)

        del_btn = QPushButton("🗑 Supprimer")
        del_btn.clicked.connect(self.delete_client)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['danger']};
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #ff6b6b;
            }}
        """)
        btn_row.addWidget(del_btn)

        form_layout.addLayout(btn_row)
        layout.addWidget(form_card)

        # ----------------------------------------------------------
        # TABLE CLIENTS
        # ----------------------------------------------------------
        table_title = QLabel("📋 Liste des Clients")
        table_title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Téléphone", "Adresse"])
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(350)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {COLORS['bg_card']};
                border-radius: 8px;
                gridline-color: {COLORS['border']};
            }}
        """)

        self.table.cellClicked.connect(self.fill_form)
        layout.addWidget(self.table)

        scroll.setWidget(container)
        page_layout = QVBoxLayout(self)
        page_layout.addWidget(scroll)

        self.load_clients()

    # ============================================================
    #                          DATA
    # ============================================================

    def load_clients(self):
        data = self.db.get_all_clients()
        self.table.setRowCount(len(data))

        for r, c in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(str(c["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(c["name"]))
            self.table.setItem(r, 2, QTableWidgetItem(c["phone"]))
            self.table.setItem(r, 3, QTableWidgetItem(c["address"]))

    def add_client(self):
        name = self.input_name.text()
        phone = self.input_phone.text()
        address = self.input_address.text()

        if not name:
            return

        self.db.add_client(name, phone, address)
        self.load_clients()

    def update_client(self):
        row = self.table.currentRow()
        if row < 0:
            return

        client_id = int(self.table.item(row, 0).text())

        self.db.update_client(
            client_id,
            self.input_name.text(),
            self.input_phone.text(),
            self.input_address.text(),
        )
        self.load_clients()

    def delete_client(self):
        row = self.table.currentRow()
        if row < 0:
            return

        client_id = int(self.table.item(row, 0).text())
        self.db.delete_client(client_id)
        self.load_clients()

    def fill_form(self, row, col):
        self.input_name.setText(self.table.item(row, 1).text())
        self.input_phone.setText(self.table.item(row, 2).text())
        self.input_address.setText(self.table.item(row, 3).text())

    def search_client(self, text):
        data = self.db.search_clients(text)
        self.table.setRowCount(len(data))

        for r, c in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(str(c["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(c["name"]))
            self.table.setItem(r, 2, QTableWidgetItem(c["phone"]))
            self.table.setItem(r, 3, QTableWidgetItem(c["address"]))