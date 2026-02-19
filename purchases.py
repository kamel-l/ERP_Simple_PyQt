from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QHBoxLayout, QFrame, QGridLayout, QMessageBox, QDialog, QLineEdit, QFormLayout, QInputDialog
)
from PyQt6.QtGui import QFont
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
                padding: 0px;
            }}
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("📦 Créer un Nouveau Produit")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white; border: none;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Remplissez les informations du produit")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8); border: none;")
        header_layout.addWidget(subtitle)
        main_layout.addWidget(header)
        
        # Formulaire
        form_container = QFrame()
        form_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                padding: 0px;
            }}
        """)
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        def make_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
            return lbl
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Pantalon Jean")
        self.name_edit.setMinimumHeight(45)
        form_layout.addRow(make_label("Nom: *"), self.name_edit)
        
        self.purchase_price_edit = QLineEdit()
        self.purchase_price_edit.setPlaceholderText("Ex: 1500")
        self.purchase_price_edit.setMinimumHeight(45)
        form_layout.addRow(make_label("Prix d'achat: *"), self.purchase_price_edit)
        
        self.selling_price_edit = QLineEdit()
        self.selling_price_edit.setPlaceholderText("Ex: 2500")
        self.selling_price_edit.setMinimumHeight(45)
        form_layout.addRow(make_label("Prix de vente: *"), self.selling_price_edit)
        
        self.stock_edit = QLineEdit()
        self.stock_edit.setPlaceholderText("Ex: 10")
        self.stock_edit.setText("0")
        self.stock_edit.setMinimumHeight(45)
        form_layout.addRow(make_label("Stock initial:"), self.stock_edit)
        
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
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        save_btn = QPushButton("💾 Créer le Produit")
        save_btn.setStyleSheet(BUTTON_STYLES['success'])
        save_btn.setMinimumHeight(50)
        save_btn.setFixedWidth(200)
        save_btn.clicked.connect(self.validate_and_accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        """Valide et accepte le formulaire"""
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
            QLabel {{
                color: {COLORS['text_primary']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre et bouton nouveau produit
        header_layout = QHBoxLayout()
        
        title = QLabel("Sélectionnez un produit")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
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
        
        # Charger les produits
        self.load_products(products)
    
    def load_products(self, products):
        """Charge les produits dans la table"""
        self.table.setRowCount(0)
        for product in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Colonne 0 : Nom (on stocke l'objet produit complet dans UserRole)
            name_item = QTableWidgetItem(product['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, product)  # stocker le dict produit
            self.table.setItem(row, 0, name_item)
            
            # Colonne 1 : Catégorie
            cat_item = QTableWidgetItem(product.get('category_name', '-'))
            self.table.setItem(row, 1, cat_item)
            
            # Colonne 2 : Prix achat
            price_item = QTableWidgetItem(f"{product['purchase_price']:,.2f} DA")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 2, price_item)
            
            # Colonne 3 : Stock
            stock_item = QTableWidgetItem(str(product['stock_quantity']))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, stock_item)
    
    def filter_products(self, text):
        """Filtre les produits"""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)  # Chercher dans le nom (colonne 0)
            show = item and text.lower() in item.text().lower()
            self.table.setRowHidden(row, not show)
    
    def select_product(self):
        """Sélectionne le produit"""
        selected = self.table.currentRow()
        if selected >= 0:
            item = self.table.item(selected, 0)
            if item:
                self.selected_product = item.data(Qt.ItemDataRole.UserRole)
                self.accept()
    
    def create_new_product(self):
        """Crée un nouveau produit et l'ajoute automatiquement"""
        dialog = NewProductDialog()
        if dialog.exec():
            name = dialog.name_edit.text().strip()
            purchase_price = float(dialog.purchase_price_edit.text())
            selling_price = float(dialog.selling_price_edit.text())
            stock = int(dialog.stock_edit.text())
            
            # Ajouter le produit à la base de données
            product_id = self.db.add_product(
                name=name,
                selling_price=selling_price,
                purchase_price=purchase_price,
                stock_quantity=stock,
                category_id=None,
                min_stock=5
            )
            
            if product_id:
                QMessageBox.information(
                    self, "Succès",
                    f"Produit '{name}' créé avec succès!"
                )
                
                # Récupérer le produit complet depuis la base
                product = self.db.get_product_by_id(product_id)
                
                if product:
                    # Le définir comme produit sélectionné
                    self.selected_product = product
                    # Fermer le dialogue avec succès (accept)
                    self.accept()
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Impossible de créer le produit!"
                )


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
                padding: 15px;
            }}
        """)
        header_layout = QVBoxLayout(header)
        title = QLabel("🏢 Informations du Fournisseur")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white; border: none;")
        header_layout.addWidget(title)
        subtitle = QLabel("Remplissez les informations du nouveau fournisseur")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8); border: none;")
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
        form_layout = QFormLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        def make_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
            return lbl
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Société ABC")
        self.name_edit.setMinimumHeight(45)
        form_layout.addRow(make_label("Nom: *"), self.name_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Ex: 0555123456")
        self.phone_edit.setMinimumHeight(45)
        form_layout.addRow(make_label("Téléphone:"), self.phone_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Ex: contact@fournisseur.com")
        self.email_edit.setMinimumHeight(45)
        form_layout.addRow(make_label("Email:"), self.email_edit)
        
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Ex: 10 Rue Principale, Alger")
        self.address_edit.setMinimumHeight(45)
        form_layout.addRow(make_label("Adresse:"), self.address_edit)
        
        self.nif_edit = QLineEdit()
        self.nif_edit.setPlaceholderText("Numéro d'identification fiscale")
        self.nif_edit.setMinimumHeight(45)
        form_layout.addRow(make_label("NIF:"), self.nif_edit)
        
        main_layout.addWidget(form_container)
        
        note = QLabel("* Champ obligatoire")
        note.setFont(QFont("Segoe UI", 10))
        note.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        main_layout.addWidget(note)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet(BUTTON_STYLES['success'])
        save_btn.setMinimumHeight(50)
        save_btn.setFixedWidth(180)
        save_btn.clicked.connect(self.validate_and_accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        """Valide et accepte le formulaire"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du fournisseur est obligatoire!")
            return
        self.accept()


class PurchasesPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Connexion à la base de données
        self.db = get_database()

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
        self.supplier_combo.setStyleSheet(INPUT_STYLE)
        self.supplier_combo.setMinimumHeight(45)
        self.supplier_combo.setMinimumWidth(300)
        self.load_suppliers()

        # Bouton nouveau fournisseur
        self.new_supplier_btn = QPushButton("🏢 Nouveau Fournisseur")
        self.new_supplier_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.new_supplier_btn.setMinimumHeight(45)
        self.new_supplier_btn.setFixedWidth(200)
        self.new_supplier_btn.clicked.connect(self.add_supplier)
        self.new_supplier_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Bouton ajouter article
        self.add_item_btn = QPushButton("➕ Ajouter Article")
        self.add_item_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_item_btn.setMinimumHeight(45)
        self.add_item_btn.setFixedWidth(180)
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        supplier_layout.addWidget(supplier_label)
        supplier_layout.addWidget(self.supplier_combo)
        supplier_layout.addWidget(self.new_supplier_btn)
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
                padding: 0px;
            }}
        """)
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 15, 15, 15)
        table_layout.setSpacing(10)
        table_container.setLayout(table_layout)

        table_title = QLabel("📦 Articles d'Achat")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
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

        # ------------------- SUMMARY SECTION -------------------
        summary_card = QFrame()
        summary_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 2px solid {COLORS['warning']};
                padding: 0px;
            }}
        """)
        summary_main_layout = QVBoxLayout()
        summary_main_layout.setContentsMargins(25, 25, 25, 25)
        summary_main_layout.setSpacing(15)
        summary_card.setLayout(summary_main_layout)

        summary_title = QLabel("💰 Résumé de l'Achat")
        summary_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        summary_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        summary_main_layout.addWidget(summary_title)

        amounts_grid = QGridLayout()
        amounts_grid.setSpacing(15)
        amounts_grid.setColumnStretch(0, 1)   # colonne labels prend 1 part
        amounts_grid.setColumnStretch(1, 2)   # colonne valeurs prend 2 parts

        subtotal_label_text = QLabel("Sous-total:")
        subtotal_label_text.setFont(QFont("Segoe UI", 13))
        subtotal_label_text.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        self.subtotal_label = QLabel("0.00 DA")
        self.subtotal_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.subtotal_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.subtotal_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        amounts_grid.addWidget(subtotal_label_text, 0, 0)
        amounts_grid.addWidget(self.subtotal_label, 0, 1)

        tax_label_text = QLabel("Taxe (10%):")
        tax_label_text.setFont(QFont("Segoe UI", 13))
        tax_label_text.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        self.tax_label = QLabel("0.00 DA")
        self.tax_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.tax_label.setStyleSheet(f"color: {COLORS['warning']}; border: none;")
        
        self.tax_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        amounts_grid.addWidget(tax_label_text, 1, 0)
        amounts_grid.addWidget(self.tax_label, 1, 1)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; border: none;")
        amounts_grid.addWidget(separator, 2, 0, 1, 2)

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

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Enregistrer l'Achat")
        self.save_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.save_btn.setFixedSize(220, 50)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_purchase)
        button_layout.addWidget(self.save_btn)
        
        summary_main_layout.addLayout(button_layout)

        layout.addWidget(summary_card)

        self.table.itemChanged.connect(self.update_totals)

    def load_suppliers(self):
        """Charge les fournisseurs depuis la base de données"""
        self.supplier_combo.clear()
        self.supplier_combo.addItem("Sélectionner un fournisseur", None)
        
        suppliers = self.db.get_all_suppliers()
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier['name'], supplier['id'])

    def add_supplier(self):
        """Ouvre le dialogue pour ajouter un nouveau fournisseur"""
        dialog = SupplierDialog()
        if dialog.exec():
            name    = dialog.name_edit.text().strip()
            phone   = dialog.phone_edit.text().strip()
            email   = dialog.email_edit.text().strip()
            address = dialog.address_edit.text().strip()
            nif     = dialog.nif_edit.text().strip()
            
            supplier_id = self.db.add_supplier(name, phone, email, address, nif)
            
            if supplier_id:
                QMessageBox.information(
                    self, "Succès",
                    f"Fournisseur '{name}' ajouté avec succès!"
                )
                # Recharger la liste et sélectionner le nouveau fournisseur
                self.load_suppliers()
                index = self.supplier_combo.findData(supplier_id)
                if index >= 0:
                    self.supplier_combo.setCurrentIndex(index)
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Impossible d'ajouter le fournisseur!"
                )

    def add_item(self):
        """Ajoute un article à l'achat"""
        # Récupérer tous les produits
        products = self.db.get_all_products()
        
        
        
        if not products:
            QMessageBox.warning(
                self,
                "Attention",
                "Aucun produit disponible!\n\nVeuillez d'abord ajouter des produits."
            )
            return
        
        # Ouvrir le sélecteur de produit
        dialog = ProductSelectorDialog(products)
        if dialog.exec() and dialog.selected_product:
            product = dialog.selected_product
            
            
            
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Produit
            product_item = QTableWidgetItem(product['name'])
            product_item.setData(Qt.ItemDataRole.UserRole, product['id'])
            self.table.setItem(row, 0, product_item)

            # Quantité (utiliser la quantité saisie)
            qty_item = QTableWidgetItem(str(product.get('stock_quantity', 0)))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_item.setFlags(qty_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, qty_item)

            # Prix (éditable)
            price_item = QTableWidgetItem(f"{product['purchase_price']:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            price_item.setFlags(price_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, price_item)

            # Total (calculé avec la quantité saisie)
            total = product['stock_quantity'] * product['purchase_price']
            total_item = QTableWidgetItem(f"{total:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.table.setItem(row, 3, total_item)

            # Bouton Supprimer
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
            self.table.setCellWidget(row, 4, remove_btn)

            self.update_totals()

    def remove_item(self, row):
        """Supprime un article"""
        self.table.removeRow(row)
        self.update_totals()

    def update_totals(self):
        """Met à jour les totaux"""
        subtotal = 0
        
        for row in range(self.table.rowCount()):
            try:
                qty_item = self.table.item(row, 1)
                price_item = self.table.item(row, 2)
                
                qty = float(qty_item.text()) if qty_item else 0
                price = float(price_item.text()) if price_item else 0
                total_row = qty * price
                
                self.table.itemChanged.disconnect(self.update_totals)
                total_item = QTableWidgetItem(f"{total_row:,.2f}")
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                self.table.setItem(row, 3, total_item)
                self.table.itemChanged.connect(self.update_totals)
                
                subtotal += total_row
            except:
                pass

        tax = subtotal * 0.10
        total = subtotal + tax

        self.subtotal_label.setText(f"{subtotal:,.2f} DA")
        self.tax_label.setText(f"{tax:,.2f} DA")
        self.total_label.setText(f"{total:,.2f} DA")

    def save_purchase(self):
        """Enregistre l'achat dans la base de données"""
        # Vérifications
        if self.supplier_combo.currentIndex() == 0:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez sélectionner un fournisseur!"
            )
            return
        
        if self.table.rowCount() == 0:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez ajouter au moins un article!"
            )
            return
        
        # Récupérer le fournisseur
        supplier_id = self.supplier_combo.currentData()
        
        # Préparer les articles
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
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur dans les données de la ligne {row + 1}:\n{str(e)}"
                )
                return
        
        # Générer une référence unique
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        reference = f"ACH-{timestamp}"
        
        # Enregistrer l'achat
        purchase_id = self.db.create_purchase(
            reference=reference,
            supplier_id=supplier_id,
            items=items,
            payment_method="cash",
            tax_rate=10.0
        )
        
        if purchase_id:
            QMessageBox.information(
                self,
                "Succès",
                f"Achat enregistré avec succès!\n\nRéférence: {reference}"
            )
            
            # Réinitialiser le formulaire
            self.table.setRowCount(0)
            self.supplier_combo.setCurrentIndex(0)
            self.update_totals()
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                "Impossible d'enregistrer l'achat!"
            )