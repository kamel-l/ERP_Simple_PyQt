from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QHBoxLayout, QFrame, 
    QMessageBox, QDialog, QLineEdit, QFormLayout, QInputDialog
)
from PyQt6.QtGui import QFont, QDoubleValidator, QIntValidator
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
from datetime import datetime


# ------------------ DIALOG POUR CRÉER UN NOUVEAU PRODUIT ------------------
class NewProductDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("📦 Nouveau Produit")
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
        
        # En-tête
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                border-radius: 10px;
            }}
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("📦 Créer un Nouveau Produit")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Remplissez les informations du produit")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8);")
        header_layout.addWidget(subtitle)
        main_layout.addWidget(header)
        
        # Formulaire
        form_container = QFrame()
        form_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
            }}
        """)
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Pantalon Jean")
        self.name_edit.setMinimumHeight(40)
        form_layout.addRow("Nom: *", self.name_edit)
        
        self.purchase_price_edit = QLineEdit()
        self.purchase_price_edit.setPlaceholderText("Ex: 1500")
        self.purchase_price_edit.setMinimumHeight(40)
        self.purchase_price_edit.setValidator(QDoubleValidator(0.01, 9999999.99, 2))
        form_layout.addRow("Prix d'achat: *", self.purchase_price_edit)
        
        self.selling_price_edit = QLineEdit()
        self.selling_price_edit.setPlaceholderText("Ex: 2500")
        self.selling_price_edit.setMinimumHeight(40)
        self.selling_price_edit.setValidator(QDoubleValidator(0.01, 9999999.99, 2))
        form_layout.addRow("Prix de vente: *", self.selling_price_edit)
        
        self.stock_edit = QLineEdit()
        self.stock_edit.setPlaceholderText("Ex: 10")
        self.stock_edit.setText("0")
        self.stock_edit.setMinimumHeight(40)
        self.stock_edit.setValidator(QIntValidator(0, 999999))
        form_layout.addRow("Stock initial:", self.stock_edit)
        
        main_layout.addWidget(form_container)
        
        note = QLabel("* Champs obligatoires")
        note.setFont(QFont("Segoe UI", 10))
        note.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        main_layout.addWidget(note)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        save_btn = QPushButton("💾 Créer")
        save_btn.setStyleSheet(BUTTON_STYLES['success'])
        save_btn.setMinimumHeight(45)
        save_btn.setFixedWidth(150)
        save_btn.clicked.connect(self.validate_and_accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du produit est obligatoire!")
            return
        try:
            float(self.purchase_price_edit.text())
        except:
            QMessageBox.warning(self, "Erreur", "Le prix d'achat doit être un nombre valide!")
            return
        try:
            float(self.selling_price_edit.text())
        except:
            QMessageBox.warning(self, "Erreur", "Le prix de vente doit être un nombre valide!")
            return
        try:
            int(self.stock_edit.text())
        except:
            QMessageBox.warning(self, "Erreur", "Le stock doit être un nombre entier!")
            return
        self.accept()


# ------------------ DIALOG POUR SÉLECTIONNER UN PRODUIT ------------------
class ProductSelectorDialog(QDialog):
    def __init__(self, products):
        super().__init__()
        
        self.selected_product = None
        self.products = products
        self.db = get_database()
        
        self.setWindowTitle("📦 Sélectionner un Produit")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_medium']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre et bouton nouveau produit
        header_layout = QHBoxLayout()
        title = QLabel("Sélectionnez un produit")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        new_product_btn = QPushButton("➕ Nouveau Produit")
        new_product_btn.setStyleSheet(BUTTON_STYLES['primary'])
        new_product_btn.setMinimumHeight(40)
        new_product_btn.setFixedWidth(180)
        new_product_btn.clicked.connect(self.create_new_product)
        new_product_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout.addWidget(new_product_btn)
        layout.addLayout(header_layout)
        
        # Barre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un produit...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.filter_products)
        layout.addWidget(self.search_input)
        
        # Table des produits
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nom", "Catégorie", "Prix Achat", "Stock"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.select_product)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)
        
        # Boutons
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("✅ Sélectionner")
        select_btn.setStyleSheet(BUTTON_STYLES['success'])
        select_btn.clicked.connect(self.select_product)
        select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(select_btn)
        layout.addLayout(btn_layout)
        
        self.load_products(products)
    
    def load_products(self, products):
        self.table.setRowCount(0)
        for product in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            name_item = QTableWidgetItem(product['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, product)
            self.table.setItem(row, 0, name_item)
            
            cat_item = QTableWidgetItem(product.get('category_name', '-'))
            self.table.setItem(row, 1, cat_item)
            
            price_item = QTableWidgetItem(f"{product['purchase_price']:,.2f} DA")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 2, price_item)
            
            stock_item = QTableWidgetItem(str(product['stock_quantity']))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, stock_item)
    
    def filter_products(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            show = item and text.lower() in item.text().lower()
            self.table.setRowHidden(row, not show)
    
    def select_product(self):
        selected = self.table.currentRow()
        if selected >= 0:
            item = self.table.item(selected, 0)
            if item:
                self.selected_product = item.data(Qt.ItemDataRole.UserRole)
                self.accept()
    
    def create_new_product(self):
        dialog = NewProductDialog()
        if dialog.exec():
            name = dialog.name_edit.text().strip()
            purchase_price = float(dialog.purchase_price_edit.text())
            selling_price = float(dialog.selling_price_edit.text())
            stock = int(dialog.stock_edit.text())
            
            product_id = self.db.add_product(
                name=name,
                selling_price=selling_price,
                purchase_price=purchase_price,
                stock_quantity=stock,
                category_id=None,
                min_stock=5
            )
            
            if product_id:
                QMessageBox.information(self, "Succès", f"Produit '{name}' créé!")
                product = self.db.get_product_by_id(product_id)
                if product:
                    self.selected_product = product
                    self.accept()


# ------------------ DIALOG POUR AJOUTER UN FOURNISSEUR ------------------
class SupplierDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("🏢 Nouveau Fournisseur")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_medium']};
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
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                border-radius: 10px;
            }}
        """)
        header_layout = QVBoxLayout(header)
        title = QLabel("🏢 Nouveau Fournisseur")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        main_layout.addWidget(header)
        
        # Formulaire
        form_container = QFrame()
        form_container.setStyleSheet(f"background: {COLORS['bg_card']}; border-radius: 10px;")
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom du fournisseur")
        self.name_edit.setMinimumHeight(40)
        form_layout.addRow("Nom: *", self.name_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Téléphone")
        self.phone_edit.setMinimumHeight(40)
        form_layout.addRow("Téléphone:", self.phone_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        self.email_edit.setMinimumHeight(40)
        form_layout.addRow("Email:", self.email_edit)
        
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Adresse")
        self.address_edit.setMinimumHeight(40)
        form_layout.addRow("Adresse:", self.address_edit)
        
        self.nif_edit = QLineEdit()
        self.nif_edit.setPlaceholderText("NIF")
        self.nif_edit.setMinimumHeight(40)
        form_layout.addRow("NIF:", self.nif_edit)
        
        main_layout.addWidget(form_container)
        
        # Boutons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet(BUTTON_STYLES['success'])
        save_btn.setMinimumHeight(45)
        save_btn.setFixedWidth(150)
        save_btn.clicked.connect(self.validate_and_accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du fournisseur est obligatoire!")
            return
        self.accept()


# ------------------ PAGE PRINCIPALE DES ACHATS ------------------
class PurchasesPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.db = get_database()

        # Layout principal - comme dans products.py
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ==================== HEADER ====================
        title = QLabel("🛒 Gestion des Achats")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        main_layout.addWidget(title)

        subtitle = QLabel("Gérez vos achats et vos fournisseurs")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        main_layout.addWidget(subtitle)

        # ==================== SECTION FOURNISSEUR ====================
        supplier_card = QFrame()
        supplier_card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        supplier_layout = QHBoxLayout()
        supplier_layout.setContentsMargins(15, 12, 15, 12)
        supplier_layout.setSpacing(15)
        supplier_card.setLayout(supplier_layout)

        # Label fournisseur
        supplier_label = QLabel("🏢 Fournisseur:")
        supplier_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        supplier_label.setStyleSheet(f"color: {COLORS['text_primary']};")

        # Combo fournisseur
        self.supplier_combo = QComboBox()
        self.supplier_combo.setStyleSheet(INPUT_STYLE)
        self.supplier_combo.setMinimumHeight(40)
        self.supplier_combo.setMinimumWidth(250)
        self.load_suppliers()

        # Bouton nouveau fournisseur
        self.new_supplier_btn = QPushButton("➕ Nouveau Fournisseur")
        self.new_supplier_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.new_supplier_btn.setMinimumHeight(40)
        self.new_supplier_btn.setFixedWidth(180)
        self.new_supplier_btn.clicked.connect(self.add_supplier)
        self.new_supplier_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Bouton ajouter article
        self.add_item_btn = QPushButton("➕ Ajouter Article")
        self.add_item_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_item_btn.setMinimumHeight(40)
        self.add_item_btn.setFixedWidth(160)
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        supplier_layout.addWidget(supplier_label)
        supplier_layout.addWidget(self.supplier_combo)
        supplier_layout.addWidget(self.new_supplier_btn)
        supplier_layout.addStretch()
        supplier_layout.addWidget(self.add_item_btn)

        main_layout.addWidget(supplier_card)

        # ==================== TABLE DES ARTICLES ====================
        table_card = QFrame()
        table_card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 15, 15, 15)
        table_layout.setSpacing(10)
        table_card.setLayout(table_layout)

        # Titre de la table
        table_title = QLabel("📦 Articles d'Achat")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        table_layout.addWidget(table_title)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Produit", "Quantité", "Prix Unitaire", "Total", ""])
        
        # Configuration des colonnes
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 60)
        
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(200)
        self.table.setStyleSheet(TABLE_STYLE)
        
        table_layout.addWidget(self.table)
        
        # La table prend tout l'espace disponible (stretch factor = 1)
        main_layout.addWidget(table_card, 1)

        # ==================== RÉSUMÉ ====================
        summary_card = QFrame()
        summary_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #252525);
                border-radius: 10px;
                border: 2px solid {COLORS['warning']};
            }}
        """)
        
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(20, 15, 20, 25)
        summary_layout.setSpacing(8)
        summary_card.setLayout(summary_layout)

        # Titre du résumé
        summary_title = QLabel("💰 Résumé de l'Achat")
        summary_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        summary_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        summary_layout.addWidget(summary_title)

        # Ligne Sous-total
        subtotal_line = QHBoxLayout()
        subtotal_line.setSpacing(10)
        
        subtotal_label = QLabel("Sous-total")
        subtotal_label.setFont(QFont("Segoe UI", 12))
        subtotal_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        
        self.subtotal_label = QLabel("0.00 DA")
        self.subtotal_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.subtotal_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        self.subtotal_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        subtotal_line.addWidget(subtotal_label)
        subtotal_line.addStretch()
        subtotal_line.addWidget(self.subtotal_label)
        summary_layout.addLayout(subtotal_line)

        # Ligne Taxe
        tax_line = QHBoxLayout()
        tax_line.setSpacing(10)
        
        tax_label = QLabel("Taxe (10%)")
        tax_label.setFont(QFont("Segoe UI", 12))
        tax_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        
        self.tax_label = QLabel("0.00 DA")

        self.tax_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.tax_label.setStyleSheet(f"color: {COLORS['warning']}; border: none;")
        

        self.tax_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.tax_label.setStyleSheet(f"color: {COLORS['warning']};")

        self.tax_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        tax_line.addWidget(tax_label)
        tax_line.addStretch()
        tax_line.addWidget(self.tax_label)
        summary_layout.addLayout(tax_line)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; min-height: 1px; max-height: 1px; margin: 5px 0;")
        summary_layout.addWidget(separator)

        # Ligne Total
        total_line = QHBoxLayout()
        total_line.setSpacing(10)
        
        total_text = QLabel("TOTAL")
        total_text.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        total_text.setStyleSheet(f"color: {COLORS['text_primary']};")
        
        self.total_label = QLabel("0.00 DA")
        self.total_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['success']};")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_line.addWidget(total_text)
        total_line.addStretch()
        total_line.addWidget(self.total_label)
        summary_layout.addLayout(total_line)

        # Bouton Enregistrer
        btn_line = QHBoxLayout()
        btn_line.addStretch()
        
        self.save_btn = QPushButton("💾 Enregistrer l'Achat")
        self.save_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.save_btn.setFixedSize(220, 45)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_purchase)
        btn_line.addWidget(self.save_btn)
        
        summary_layout.addLayout(btn_line)

        # Ajouter le résumé au layout principal
        main_layout.addWidget(summary_card)

        # Connexion du signal pour mettre à jour les totaux
        self.table.itemChanged.connect(self.update_totals)

    def load_suppliers(self):
        self.supplier_combo.clear()
        self.supplier_combo.addItem("Sélectionner un fournisseur", None)
        
        suppliers = self.db.get_all_suppliers()
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier['name'], supplier['id'])

    def add_supplier(self):
        dialog = SupplierDialog()
        if dialog.exec():
            name = dialog.name_edit.text().strip()
            phone = dialog.phone_edit.text().strip()
            email = dialog.email_edit.text().strip()
            address = dialog.address_edit.text().strip()
            nif = dialog.nif_edit.text().strip()
            
            supplier_id = self.db.add_supplier(name, phone, email, address, nif)
            
            if supplier_id:
                QMessageBox.information(self, "Succès", f"Fournisseur '{name}' ajouté!")
                self.load_suppliers()
                index = self.supplier_combo.findData(supplier_id)
                if index >= 0:
                    self.supplier_combo.setCurrentIndex(index)

    def add_item(self):
        products = self.db.get_all_products()
        
        if not products:
            QMessageBox.warning(self, "Attention", "Aucun produit disponible!")
            return
        
        dialog = ProductSelectorDialog(products)
        if dialog.exec() and dialog.selected_product:
            product = dialog.selected_product
            
            quantity, ok = QInputDialog.getInt(
                self, "Quantité", f"Quantité de '{product['name']}':",
                value=1, min=1, max=9999
            )
            
            if not ok:
                return
            
            # Vérifier si le produit existe déjà
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.data(Qt.ItemDataRole.UserRole) == product['id']:
                    qty_item = self.table.item(row, 1)
                    current_qty = int(qty_item.text())
                    qty_item.setText(str(current_qty + quantity))
                    self.update_totals()
                    return
            
            # Nouveau produit
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Produit
            product_item = QTableWidgetItem(product['name'])
            product_item.setData(Qt.ItemDataRole.UserRole, product['id'])
            product_item.setFlags(product_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, product_item)

            # Quantité
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, qty_item)

            # Prix
            price_item = QTableWidgetItem(f"{product['purchase_price']:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 2, price_item)

            # Total
            total = quantity * product['purchase_price']
            total_item = QTableWidgetItem(f"{total:.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, total_item)

            # Bouton Supprimer
            remove_btn = QPushButton("🗑️")
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {COLORS['danger']};
                    border: none;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background: {COLORS['danger']};
                    color: white;
                    border-radius: 4px;
                }}
            """)
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.table.setCellWidget(row, 4, remove_btn)

            self.update_totals()

    def remove_item(self, row):
        self.table.removeRow(row)
        self.update_totals()

    def update_totals(self):
        try:
            self.table.itemChanged.disconnect(self.update_totals)
        except:
            pass
        
        subtotal = 0.0
        
        for row in range(self.table.rowCount()):
            try:
                qty = float(self.table.item(row, 1).text() or "0")
                price = float(self.table.item(row, 2).text() or "0")
                total_row = qty * price
                
                total_item = self.table.item(row, 3)
                if total_item:
                    total_item.setText(f"{total_row:.2f}")
                
                subtotal += total_row
            except:
                continue

        tax = subtotal * 0.10
        total = subtotal + tax

        self.subtotal_label.setText(f"{subtotal:,.2f} DA")
        self.tax_label.setText(f"{tax:,.2f} DA")
        self.total_label.setText(f"{total:,.2f} DA")
        
        self.table.itemChanged.connect(self.update_totals)

    def save_purchase(self):
        if self.supplier_combo.currentIndex() == 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez un fournisseur!")
            return
        
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Attention", "Ajoutez au moins un article!")
            return
        
        supplier_id = self.supplier_combo.currentData()
        
        items = []
        for row in range(self.table.rowCount()):
            try:
                product_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                quantity = int(float(self.table.item(row, 1).text()))
                unit_price = float(self.table.item(row, 2).text())
                
                items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price
                })
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Ligne {row + 1}: {str(e)}")
                return
        
        reference = f"ACH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        purchase_id = self.db.create_purchase(
            reference=reference,
            supplier_id=supplier_id,
            items=items,
            payment_method="cash",
            tax_rate=10.0
        )
        
        if purchase_id:
            QMessageBox.information(self, "Succès", f"Achat enregistré!\nRéf: {reference}")
            self.table.setRowCount(0)
            self.supplier_combo.setCurrentIndex(0)
            self.update_totals()
        else:
            QMessageBox.critical(self, "Erreur", "Impossible d'enregistrer l'achat!")