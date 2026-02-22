from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QScrollArea
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS
from db_manager import get_database


class PurchasesPage(QWidget):
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
        title = QLabel("🛍 Achats")
        title.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        header.addWidget(title)
        header.addStretch()

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Rechercher un achat…")
        self.search.setFixedWidth(250)
        self.search.textChanged.connect(self.search_purchase)
        header.addWidget(self.search)

        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                padding: 10px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                color: black;
            }}
            QPushButton:hover {{
                background: {COLORS['accent_light']};
            }}
        """)
        refresh_btn.clicked.connect(self.load_purchases)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # ----------------------------------------------------------
        # PURCHASE FORM
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
        form_layout.setSpacing(12)

        form_title = QLabel("Ajouter / Modifier un Achat")
        form_title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        form_title.setStyleSheet(f"color: {COLORS['accent']};")
        form_layout.addWidget(form_title)

        self.input_supplier = QComboBox()
        self.input_supplier.addItems([c["name"] for c in self.db.get_all_clients()])
        form_layout.addWidget(self.input_supplier)

        self.input_product = QComboBox()
        self.input_product.addItems([p["product_name"] for p in self.db.get_all_products()])
        form_layout.addWidget(self.input_product)

        self.input_qty = QLineEdit()
        self.input_qty.setPlaceholderText("Quantité…")
        form_layout.addWidget(self.input_qty)

        self.input_price = QLineEdit()
        self.input_price.setPlaceholderText("Prix total…")
        form_layout.addWidget(self.input_price)

        # Buttons row
        btn_row = QHBoxLayout()
        add_btn = QPushButton("➕ Ajouter")
        add_btn.clicked.connect(self.add_purchase)
        btn_row.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Modifier")
        edit_btn.clicked.connect(self.update_purchase)
        btn_row.addWidget(edit_btn)

        del_btn = QPushButton("🗑 Supprimer")
        del_btn.clicked.connect(self.delete_purchase)
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
        # TABLE PURCHASES
        # ----------------------------------------------------------
        table_title = QLabel("📋 Liste des Achats")
        table_title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Fournisseur", "Produit", "Quantité", "Prix", "Date"])
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

        self.load_purchases()

    # ============================================================
    #                       DATA HANDLING
    # ============================================================

    def load_purchases(self):
        data = self.db.get_all_purchases()
        self.table.setRowCount(len(data))

        for r, p in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(p["supplier"]))
            self.table.setItem(r, 2, QTableWidgetItem(p["product"]))
            self.table.setItem(r, 3, QTableWidgetItem(str(p["quantity"])))
            self.table.setItem(r, 4, QTableWidgetItem(str(p["total"])))
            self.table.setItem(r, 5, QTableWidgetItem(str(p["date"])))

    def add_purchase(self):
        supplier = self.input_supplier.currentText()
        product = self.input_product.currentText()
        qty = self.input_qty.text()
        price = self.input_price.text()

        if not supplier or not product or not qty or not price:
            return

        self.db.add_purchase(supplier, product, qty, price)
        self.load_purchases()

    def update_purchase(self):
        row = self.table.currentRow()
        if row < 0:
            return
        purchase_id = int(self.table.item(row, 0).text())
        self.db.update_purchase(
            purchase_id,
            self.input_supplier.currentText(),
            self.input_product.currentText(),
            self.input_qty.text(),
            self.input_price.text()
        )
        self.load_purchases()

    def delete_purchase(self):
        row = self.table.currentRow()
        if row < 0:
            return
        purchase_id = int(self.table.item(row, 0).text())
        self.db.delete_purchase(purchase_id)
        self.load_purchases()

    def fill_form(self, row, col):
        self.input_supplier.setCurrentText(self.table.item(row, 1).text())
        self.input_product.setCurrentText(self.table.item(row, 2).text())
        self.input_qty.setText(self.table.item(row, 3).text())
        self.input_price.setText(self.table.item(row, 4).text())

    def search_purchase(self, text):
        data = self.db.search_purchases(text)
        self.table.setRowCount(len(data))
        for r, p in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(p["supplier"]))
            self.table.setItem(r, 2, QTableWidgetItem(p["product"]))
            self.table.setItem(r, 3, QTableWidgetItem(str(p["quantity"])))
            self.table.setItem(r, 4, QTableWidgetItem(str(p["total"])))
            self.table.setItem(r, 5, QTableWidgetItem(str(p["date"])))