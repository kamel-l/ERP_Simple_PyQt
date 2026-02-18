from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QHBoxLayout, QFrame, QDialog,
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
from datetime import datetime


class AddProductDialog(QDialog):
    """Dialogue pour ajouter un produit à la facture"""
    def __init__(self):
        super().__init__()
        
        self.db = get_database()
        self.selected_product = None
        
        self.setWindowTitle("🛒 Ajouter un Article à la Facture")
        self.setMinimumWidth(600)
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

        # En-tête
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['success']}, stop:1 {COLORS['primary']});
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        title = QLabel("🛒 Ajouter un Article")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 5px; border: none;")
        header_layout.addWidget(title)

        subtitle = QLabel("Sélectionnez le produit et la quantité souhaitée")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8); border: none;")
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        # Formulaire
        form_container = QFrame()
        form_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        form_layout = QFormLayout()
        form_container.setLayout(form_layout)
        form_layout.setSpacing(18)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Sélection du produit
        product_label = QLabel("Produit: *")
        product_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; font-weight: bold;")
        
        self.product_combo = QComboBox()
        self.product_combo.setStyleSheet(INPUT_STYLE)
        self.product_combo.setMinimumHeight(45)
        
        # Charger les produits
        self.load_products()
        
        self.product_combo.currentIndexChanged.connect(self.on_product_selected)
        form_layout.addRow(product_label, self.product_combo)


        # Prix unitaire
        price_label = QLabel("Prix unitaire:")
        price_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.price_display = QLabel("0.00 DA")
        self.price_display.setStyleSheet(f"""
            color: {COLORS['success']}; 
            border: none;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            background: {COLORS['bg_light']};
            border-radius: 5px;
        """)
        form_layout.addRow(price_label, self.price_display)

        # Stock disponible
        stock_label = QLabel("Stock disponible:")
        stock_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.stock_display = QLabel("0")
        self.stock_display.setStyleSheet(f"""
            color: {COLORS['warning']}; 
            border: none;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            background: {COLORS['bg_light']};
            border-radius: 5px;
        """)
        form_layout.addRow(stock_label, self.stock_display)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; border: none; margin: 10px 0;")
        form_layout.addRow(separator)

        # Quantité
        qty_label = QLabel("Quantité: *")
        qty_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; font-weight: bold;")
        
        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(9999)
        self.quantity.setValue(1)
        self.quantity.setStyleSheet(INPUT_STYLE)
        self.quantity.setMinimumHeight(45)
        self.quantity.valueChanged.connect(self.update_total)
        form_layout.addRow(qty_label, self.quantity)

        # Remise
        discount_label = QLabel("Remise (%):")
        discount_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.discount = QDoubleSpinBox()
        self.discount.setMinimum(0.0)
        self.discount.setMaximum(100.0)
        self.discount.setDecimals(2)
        self.discount.setValue(0.0)
        self.discount.setStyleSheet(INPUT_STYLE)
        self.discount.setMinimumHeight(45)
        self.discount.setSuffix(" %")
        self.discount.valueChanged.connect(self.update_total)
        form_layout.addRow(discount_label, self.discount)

        main_layout.addWidget(form_container)

        # Résumé du total
        total_container = QFrame()
        total_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 10px;
                border: 2px solid {COLORS['primary']};
                padding: 15px;
            }}
        """)
        total_layout = QHBoxLayout()
        total_container.setLayout(total_layout)

        total_text = QLabel("TOTAL:")
        total_text.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        total_text.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.total_display = QLabel("0.00 DA")
        self.total_display.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.total_display.setStyleSheet(f"color: {COLORS['success']}; border: none;")
        self.total_display.setAlignment(Qt.AlignmentFlag.AlignRight)

        total_layout.addWidget(total_text)
        total_layout.addStretch()
        total_layout.addWidget(self.total_display)

        main_layout.addWidget(total_container)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        add_btn = QPushButton("✅ Ajouter")
        add_btn.setStyleSheet(BUTTON_STYLES['success'])
        add_btn.setMinimumHeight(50)
        add_btn.setFixedWidth(180)
        add_btn.clicked.connect(self.validate_and_accept)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn)
        
        main_layout.addLayout(btn_layout)

    def load_products(self):
        """Charge les produits depuis la base"""
        self.product_combo.clear()
        self.product_combo.addItem("-- Sélectionner un produit --", None)
        
        products = self.db.get_all_products()
        for product in products:
            if product['stock_quantity'] > 0:
                display_text = f"{product['name']})"
                self.product_combo.addItem(display_text, product)

    def on_product_selected(self, index):
        """Quand un produit est sélectionné"""
        product = self.product_combo.currentData()
        
        if product:
            self.selected_product = product
            self.price_display.setText(f"{product['selling_price']:,.2f} DA")
            self.stock_display.setText(str(product['stock_quantity']))
            self.quantity.setMaximum(product['stock_quantity'])
            self.update_total()
        else:
            self.selected_product = None
            self.price_display.setText("0.00 DA")
            self.stock_display.setText("0")

    def update_total(self):
        """Met à jour le total"""
        if self.selected_product:
            qty = self.quantity.value()
            price = self.selected_product['selling_price']
            discount = self.discount.value()
            
            total = qty * price * (1 - discount / 100)
            self.total_display.setText(f"{total:,.2f} DA")

    def validate_and_accept(self):
        """Valide et accepte"""
        if not self.selected_product:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit!")
            return
        
        if self.quantity.value() > self.selected_product['stock_quantity']:
            QMessageBox.warning(self, "Erreur", "Stock insuffisant!")
            return
        
        self.accept()


class SalesPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.db = get_database()
        self.cart_items = []  # Articles dans le panier
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title = QLabel("💰 Point de Vente")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Gestion des ventes et facturation")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # Client Selection
        client_card = QFrame()
        client_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        client_layout = QHBoxLayout()
        client_card.setLayout(client_layout)
        client_layout.setSpacing(15)

        client_label = QLabel("👤 Client:")
        client_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        client_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")

        self.client_combo = QComboBox()
        self.client_combo.setStyleSheet(INPUT_STYLE)
        self.client_combo.setMinimumHeight(45)
        self.client_combo.setMinimumWidth(300)
        self.load_clients()

        # Bouton ajouter article
        self.add_item_btn = QPushButton("➕ Ajouter Article")
        self.add_item_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_item_btn.setMinimumHeight(45)
        self.add_item_btn.setFixedWidth(180)
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        client_layout.addWidget(client_label)
        client_layout.addWidget(self.client_combo)
        client_layout.addStretch()
        client_layout.addWidget(self.add_item_btn)

        layout.addWidget(client_card)

        # Cart Table
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 0px;
            }}
        """)
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 15, 15, 15)
        table_layout.setSpacing(10)
        table_container.setLayout(table_layout)

        table_title = QLabel("🛒 Panier")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        table_layout.addWidget(table_title)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Produit", "Quantité", "Prix Unit.", "Remise", "Total", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 80)
        
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(300)
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

        # Summary Section
        summary_card = QFrame()
        summary_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 2px solid {COLORS['success']};
                padding: 25px;
            }}
        """)
        summary_main_layout = QVBoxLayout()
        summary_card.setLayout(summary_main_layout)
        summary_main_layout.setSpacing(15)

        summary_title = QLabel("💰 Résumé de la Vente")
        summary_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        summary_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        summary_main_layout.addWidget(summary_title)

        amounts_grid = QGridLayout()
        amounts_grid.setSpacing(15)

        # Sous-total
        subtotal_label_text = QLabel("Sous-total HT:")
        subtotal_label_text.setFont(QFont("Segoe UI", 13))
        subtotal_label_text.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        self.subtotal_label = QLabel("0.00 DA")
        self.subtotal_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.subtotal_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.subtotal_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        amounts_grid.addWidget(subtotal_label_text, 0, 0)
        amounts_grid.addWidget(self.subtotal_label, 0, 1)

        # TVA
        tax_label_text = QLabel("TVA (19%):")
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
        total_label_text = QLabel("TOTAL TTC:")
        total_label_text.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        total_label_text.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.total_label = QLabel("0.00 DA")
        self.total_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['success']}; border: none;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)

         
        
        amounts_grid.addWidget(total_label_text, 3, 0)
        amounts_grid.addWidget(self.total_label, 3, 1)

        summary_main_layout.addLayout(amounts_grid)

        # Boutons d'action
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.clear_btn = QPushButton("🗑️ Vider le Panier")
        self.clear_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.clear_btn.setMinimumHeight(50)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_cart)
        
        self.save_btn = QPushButton("💾 Enregistrer la Vente")
        self.save_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.save_btn.setFixedSize(220, 50)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_sale)
        
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        
        summary_main_layout.addLayout(button_layout)

        layout.addWidget(summary_card)

    def load_clients(self):
        """Charge les clients (peut être appelée depuis l'extérieur pour rafraîchir)"""
        self.client_combo.clear()
        self.client_combo.addItem("Client Anonyme", None)
        
        clients = self.db.get_all_clients()
        for client in clients:
            self.client_combo.addItem(client['name'], client['id'])

    def add_item(self):
        """Ajoute un article au panier"""
        dialog = AddProductDialog()
        if dialog.exec() and dialog.selected_product:
            product = dialog.selected_product
            quantity = dialog.quantity.value()
            discount = dialog.discount.value()
            unit_price = product['selling_price']
            total = quantity * unit_price * (1 - discount / 100)
            
            # Ajouter au panier
            self.cart_items.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'quantity': quantity,
                'unit_price': unit_price,
                'discount': discount,
                'total': total
            })
            
            # Ajouter à la table
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Produit
            product_item = QTableWidgetItem(product['name'])
            self.table.setItem(row, 0, product_item)
            
            # Quantité
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, qty_item)
            
            # Prix unitaire
            price_item = QTableWidgetItem(f"{unit_price:,.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 2, price_item)
            
            # Remise
            discount_item = QTableWidgetItem(f"{discount:.2f}%")
            discount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, discount_item)
            
            # Total
            total_item = QTableWidgetItem(f"{total:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.table.setItem(row, 4, total_item)
            
            # Bouton supprimer
            remove_btn = QPushButton("🗑️")
            remove_btn.setFont(QFont("Segoe UI", 14))
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {COLORS['danger']};
                    border: none;
                }}
                QPushButton:hover {{
                    background: {COLORS['danger']};
                    color: white;
                    border-radius: 5px;
                }}
            """)
            remove_btn.clicked.connect(lambda _, r=row: self.remove_item(r))
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.table.setCellWidget(row, 5, remove_btn)
            
            self.update_totals()

    def remove_item(self, row):
        """Supprime un article"""
        if row < len(self.cart_items):
            del self.cart_items[row]
        self.table.removeRow(row)
        self.update_totals()

    def clear_cart(self):
        """Vide le panier"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment vider le panier?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.cart_items = []
            self.table.setRowCount(0)
            self.update_totals()

    def update_totals(self):
        """Met à jour les totaux"""
        subtotal = sum(item['total'] for item in self.cart_items)
        tax = subtotal * 0.19  # TVA 19%
        total = subtotal + tax
        
        self.subtotal_label.setText(f"{subtotal:,.2f} DA")
        self.tax_label.setText(f"{tax:,.2f} DA")
        self.total_label.setText(f"{total:,.2f} DA")

    def save_sale(self):
        """Enregistre la vente"""
        if not self.cart_items:
            QMessageBox.warning(self, "Attention", "Le panier est vide!")
            return
        
        client_id = self.client_combo.currentData()
        
        # Générer un numéro de facture
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        invoice_number = f"FAC-{timestamp}"
        
        # Préparer les articles
        items = []
        for item in self.cart_items:
            items.append({
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'unit_price': item['unit_price'],
                'discount': item['discount']
            })
        
        # Enregistrer dans la base
        sale_id = self.db.create_sale(
            invoice_number=invoice_number,
            client_id=client_id,
            items=items,
            payment_method="cash",
            tax_rate=19.0,
            discount=0
        )
        
        if sale_id:
            QMessageBox.information(
                self,
                "Succès",
                f"Vente enregistrée avec succès!\n\nFacture N° {invoice_number}"
            )
            
            # Réinitialiser
            self.cart_items = []
            self.table.setRowCount(0)
            self.update_totals()
            self.client_combo.setCurrentIndex(0)
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                "Impossible d'enregistrer la vente!"
            )