from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QHBoxLayout, QFrame, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE


class PurchasesPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # ------------------- HEADER -------------------
        header_layout = QVBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("🛒 Gestion des Achats")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        header_layout.addWidget(title)

        subtitle = QLabel("Gérez vos achats et vos fournisseurs")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        header_layout.addWidget(subtitle)

        # ------------------- SUPPLIER SELECTION CARD -------------------
        supplier_card = QFrame()
        supplier_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        supplier_layout = QHBoxLayout()
        supplier_card.setLayout(supplier_layout)
        supplier_layout.setSpacing(15)

        supplier_label = QLabel("🏢 Fournisseur:")
        supplier_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        supplier_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")

        self.supplier_combo = QComboBox()
        self.supplier_combo.addItems([
            "Sélectionner un fournisseur",
            "Fournisseur A - Électronique",
            "Fournisseur B - Informatique", 
            "Fournisseur C - Mobilier"
        ])
        self.supplier_combo.setStyleSheet(INPUT_STYLE)
        self.supplier_combo.setMinimumHeight(45)
        self.supplier_combo.setMinimumWidth(300)

        # Bouton ajouter article
        self.add_item_btn = QPushButton("➕ Ajouter Article")
        self.add_item_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_item_btn.setMinimumHeight(45)
        self.add_item_btn.setFixedWidth(180)
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        supplier_layout.addWidget(supplier_label)
        supplier_layout.addWidget(self.supplier_combo)
        supplier_layout.addStretch()
        supplier_layout.addWidget(self.add_item_btn)

        layout.addWidget(supplier_card)

        # ------------------- PURCHASE TABLE -------------------
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

        table_title = QLabel("📦 Articles d'Achat")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; margin-bottom: 10px;")
        table_layout.addWidget(table_title)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Produit", "Quantité", "Prix Unitaire", "Total", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 100)
        
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(300)

        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

        # ------------------- SUMMARY SECTION -------------------
        summary_card = QFrame()
        summary_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 2px solid {COLORS['warning']};
                padding: 25px;
            }}
        """)
        summary_main_layout = QVBoxLayout()
        summary_card.setLayout(summary_main_layout)
        summary_main_layout.setSpacing(15)

        # Titre de la section
        summary_title = QLabel("💰 Résumé de l'Achat")
        summary_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        summary_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        summary_main_layout.addWidget(summary_title)

        # Grille des montants
        amounts_grid = QGridLayout()
        amounts_grid.setSpacing(15)

        # Sous-total
        subtotal_label_text = QLabel("Sous-total:")
        subtotal_label_text.setFont(QFont("Segoe UI", 13))
        subtotal_label_text.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        self.subtotal_label = QLabel("0.00 DA")
        self.subtotal_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.subtotal_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.subtotal_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        amounts_grid.addWidget(subtotal_label_text, 0, 0)
        amounts_grid.addWidget(self.subtotal_label, 0, 1)

        # Taxe
        tax_label_text = QLabel("Taxe (10%):")
        tax_label_text.setFont(QFont("Segoe UI", 13))
        tax_label_text.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        self.tax_label = QLabel("0.00 DA")
        self.tax_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.tax_label.setStyleSheet(f"color: {COLORS['warning']}; border: none;")
        self.tax_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        amounts_grid.addWidget(tax_label_text, 1, 0)
        amounts_grid.addWidget(self.tax_label, 1, 1)

        # Ligne de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; border: none;")
        amounts_grid.addWidget(separator, 2, 0, 1, 2)

        # Total
        total_label_text = QLabel("TOTAL:")
        total_label_text.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        total_label_text.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.total_label = QLabel("0.00 DA")
        self.total_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['success']}; border: none;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        amounts_grid.addWidget(total_label_text, 3, 0)
        amounts_grid.addWidget(self.total_label, 3, 1)

        summary_main_layout.addLayout(amounts_grid)

        # Bouton sauvegarder
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Enregistrer l'Achat")
        self.save_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.save_btn.setFixedSize(220, 50)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.save_btn)
        
        summary_main_layout.addLayout(button_layout)

        layout.addWidget(summary_card)

        # Connect item changes
        self.table.itemChanged.connect(self.update_totals)

    # ------------------ AJOUTER ARTICLE ------------------
    def add_item(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Product Name
        product_item = QTableWidgetItem("Produit X")
        self.table.setItem(row, 0, product_item)

        # Quantity
        qty_item = QTableWidgetItem("1")
        qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, qty_item)

        # Price
        price_item = QTableWidgetItem("1000.00")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.table.setItem(row, 2, price_item)

        # Total
        total_item = QTableWidgetItem("1000.00")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.table.setItem(row, 3, total_item)

        # Remove Button
        remove_btn = QPushButton("🗑️")
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['danger']};
                border: none;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background: {COLORS['danger']};
                color: white;
                border-radius: 5px;
            }}
        """)
        remove_btn.clicked.connect(lambda _, r=row: self.remove_item(r))
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.table.setCellWidget(row, 4, remove_btn)

        # Update totals
        self.update_totals()

    # ------------------ SUPPRIMER ARTICLE ------------------
    def remove_item(self, row):
        self.table.removeRow(row)
        self.update_totals()

    # ------------------ METTRE À JOUR TOTAUX ------------------
    def update_totals(self):
        subtotal = 0
        
        for row in range(self.table.rowCount()):
            try:
                qty_item = self.table.item(row, 1)
                price_item = self.table.item(row, 2)
                
                qty = float(qty_item.text()) if qty_item else 0
                price = float(price_item.text()) if price_item else 0
                total_row = qty * price
                
                # Update total column
                self.table.itemChanged.disconnect(self.update_totals)
                total_item = QTableWidgetItem(f"{total_row:,.2f}")
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                self.table.setItem(row, 3, total_item)
                self.table.itemChanged.connect(self.update_totals)
                
                subtotal += total_row
            except:
                pass

        tax = subtotal * 0.10  # 10% tax
        total = subtotal + tax

        self.subtotal_label.setText(f"{subtotal:,.2f} DA")
        self.tax_label.setText(f"{tax:,.2f} DA")
        self.total_label.setText(f"{total:,.2f} DA")