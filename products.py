from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QScrollArea
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS
from db_manager import get_database


class ProductsPage(QWidget):
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
        title = QLabel("📦 Produits")
        title.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")

        header.addWidget(title)
        header.addStretch()

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
        refresh_btn.clicked.connect(self.load_products)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # ----------------------------------------------------------
        # PRODUCT FORM
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

        form_title = QLabel("Ajouter / Modifier un Produit")
        form_title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        form_title.setStyleSheet(f"color: {COLORS['accent']};")
        form_layout.addWidget(form_title)

        # name
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Nom du produit…")
        form_layout.addWidget(self.input_name)

        # category
        self.input_category = QComboBox()
        self.input_category.addItems(["Général", "Accessoires", "Alimentaire", "Électronique"])
        form_layout.addWidget(self.input_category)

        # price
        self.input_price = QLineEdit()
        self.input_price.setPlaceholderText("Prix (DA)…")
        form_layout.addWidget(self.input_price)

        # quantity
        self.input_quantity = QLineEdit()
        self.input_quantity.setPlaceholderText("Quantité…")
        form_layout.addWidget(self.input_quantity)

        # buttons row
        btn_row = QHBoxLayout()

        add_btn = QPushButton("➕ Ajouter")
        add_btn.clicked.connect(self.add_product)
        btn_row.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Modifier")
        edit_btn.clicked.connect(self.update_product)
        btn_row.addWidget(edit_btn)

        del_btn = QPushButton("🗑 Supprimer")
        del_btn.clicked.connect(self.delete_product)
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
        # TABLE PRODUCTS
        # ----------------------------------------------------------
        table_title = QLabel("📋 Liste des Produits")
        table_title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Catégorie", "Prix", "Stock"])
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(350)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {COLORS['bg_card']};
                border-radius: 8px;
                gridline-color: {COLORS['border']};
            }}
        """)

        self.table.cellClicked.connect(self.fill_form_from_table)
        layout.addWidget(self.table)

        scroll.setWidget(container)
        page_layout = QVBoxLayout(self)
        page_layout.addWidget(scroll)

        self.load_products()

    # =====================================================================
    #                         DATA HANDLING
    # =====================================================================

    def load_products(self):
        data = self.db.get_all_products()
        self.table.setRowCount(len(data))

        for r, product in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(str(product["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(product["product_name"]))
            self.table.setItem(r, 2, QTableWidgetItem(product["category"]))
            self.table.setItem(r, 3, QTableWidgetItem(str(product["price"])))
            self.table.setItem(r, 4, QTableWidgetItem(str(product["Quantitee"])))

    def add_product(self):
        name = self.input_name.text()
        cat = self.input_category.currentText()
        price = self.input_price.text()
        qty = self.input_quantity.text()

        if not name or not price or not qty:
            print("Champs incomplets")
            return

        self.db.add_product(name, cat, price, qty)
        self.load_products()

    def update_product(self):
        row = self.table.currentRow()
        if row < 0:
            return

        product_id = int(self.table.item(row, 0).text())

        self.db.update_product(
            product_id,
            self.input_name.text(),
            self.input_category.currentText(),
            self.input_price.text(),
            self.input_quantity.text()
        )
        self.load_products()

    def delete_product(self):
        row = self.table.currentRow()
        if row < 0:
            return

        product_id = int(self.table.item(row, 0).text())
        self.db.delete_product(product_id)
        self.load_products()

    def fill_form_from_table(self, row, col):
        self.input_name.setText(self.table.item(row, 1).text())
        self.input_category.setCurrentText(self.table.item(row, 2).text())
        self.input_price.setText(self.table.item(row, 3).text())
        self.input_quantity.setText(self.table.item(row, 4).text())