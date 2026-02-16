from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QLineEdit, QFormLayout, QHBoxLayout, QFrame, QFileDialog, QMessageBox,
    QSpinBox, QDoubleSpinBox, QComboBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
import csv


class ProductDialog(QDialog):
    """Dialogue pour ajouter ou modifier un produit"""
    def __init__(self, product_data=None):
        super().__init__()
        
        self.db = get_database()
        self.is_edit = product_data is not None
        self.product_id = product_data.get('id') if product_data else None
        
        self.setWindowTitle("📝 " + ("Modifier le Produit" if self.is_edit else "Ajouter un Produit"))
        self.setMinimumWidth(550)
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
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        title = QLabel("📦 Informations du Produit")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 5px; border: none;")
        header_layout.addWidget(title)

        subtitle = QLabel("Remplissez tous les champs obligatoires")
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
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        

        # Nom du produit *
        name_label = QLabel("Nom du produit: *")
        name_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.name = QLineEdit()
        self.name.setPlaceholderText("Ex: Ordinateur Portable HP")
        self.name.setStyleSheet(INPUT_STYLE)
        self.name.setMinimumHeight(45)
        form_layout.addRow(name_label, self.name)

        # Catégorie
        cat_label = QLabel("Catégorie:")
        cat_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.category = QComboBox()
        self.category.setStyleSheet(INPUT_STYLE)
        self.category.setMinimumHeight(45)
        self.category.setEditable(True)
        self.load_categories()
        form_layout.addRow(cat_label, self.category)

        # Prix d'achat
        price_buy_label = QLabel("Prix d'achat (DA):")
        price_buy_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.price_buy = QDoubleSpinBox()
        self.price_buy.setMinimum(0.0)
        self.price_buy.setMaximum(9999999.99)
        self.price_buy.setDecimals(2)
        self.price_buy.setValue(0.0)
        self.price_buy.setStyleSheet(INPUT_STYLE)
        self.price_buy.setMinimumHeight(45)
        form_layout.addRow(price_buy_label, self.price_buy)

        # Prix de vente *
        price_label = QLabel("Prix de vente (DA): *")
        price_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.price = QDoubleSpinBox()
        self.price.setMinimum(0.0)
        self.price.setMaximum(9999999.99)
        self.price.setDecimals(2)
        self.price.setValue(0.0)
        self.price.setStyleSheet(INPUT_STYLE)
        self.price.setMinimumHeight(45)
        form_layout.addRow(price_label, self.price)

        # Quantité *
        qty_label = QLabel("Quantité en stock: *")
        qty_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.quantity = QSpinBox()
        self.quantity.setMinimum(0)
        self.quantity.setMaximum(999999)
        self.quantity.setValue(0)
        self.quantity.setStyleSheet(INPUT_STYLE)
        self.quantity.setMinimumHeight(45)
        form_layout.addRow(qty_label, self.quantity)

        # Stock minimum
        min_stock_label = QLabel("Stock minimum:")
        min_stock_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.min_stock = QSpinBox()
        self.min_stock.setMinimum(0)
        self.min_stock.setMaximum(999999)
        self.min_stock.setValue(5)
        self.min_stock.setStyleSheet(INPUT_STYLE)
        self.min_stock.setMinimumHeight(45)
        form_layout.addRow(min_stock_label, self.min_stock)

        main_layout.addWidget(form_container)

        # Note
        note = QLabel("* Champs obligatoires")
        note.setFont(QFont("Segoe UI", 10))
        note.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        main_layout.addWidget(note)

        # Boutons d'action
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

        # Si modification, remplir les champs
        if self.is_edit and product_data:
            self.load_product_data(product_data)

    def load_categories(self):
        """Charge les catégories depuis la base de données"""
        self.category.clear()
        self.category.addItem("")
        categories = self.db.get_all_categories()
        for cat in categories:
            self.category.addItem(cat['name'])

    def load_product_data(self, product):
        """Charge les données du produit pour modification"""
       
        self.name.setText(product.get("name", ""))
        self.category.setCurrentText(product.get("category_name", ""))
        self.quantity.setValue(product.get("stock_quantity", 0))
        self.price_buy.setValue(product.get("purchase_price", 0.0))
        self.price.setValue(product.get("selling_price", 0.0))
        self.min_stock.setValue(product.get("min_stock", 5))

    def validate_and_accept(self):
        """Valide les données avant d'accepter"""
        
        if not self.name.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du produit est obligatoire!")
            return
        
        if self.price.value() <= 0:
            QMessageBox.warning(self, "Erreur", "Le prix de vente doit être supérieur à 0!")
            return
        
        self.accept()


class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.db = get_database()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title = QLabel("📦 Gestion des Produits")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Gérez votre inventaire et vos produits")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # Statistics
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(15)
        layout.addLayout(self.stats_layout)
        
        self.update_statistics()
        self.stats_layout.addStretch()

        # Search & Actions
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)
        layout.addLayout(search_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un produit...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.filter_products)
        self.search_input.setMinimumHeight(45)
        search_layout.addWidget(self.search_input)

        self.add_btn = QPushButton("➕ Nouveau Produit")
        self.add_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_btn.setFixedWidth(180)
        self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_product)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(self.add_btn)

        # Table
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

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Catégorie", "Stock", 
            "Prix Achat", "Prix Vente", "Valeur Stock"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

        # Action Buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        layout.addLayout(actions_layout)

        self.edit_btn = QPushButton("✏️ Modifier")
        self.edit_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.edit_btn.clicked.connect(self.edit_product)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setMinimumHeight(40)
        
        self.delete_btn = QPushButton("🗑️ Supprimer")
        self.delete_btn.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_btn.clicked.connect(self.delete_product)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setMinimumHeight(40)

        self.import_btn = QPushButton("📥 Importer CSV")
        self.import_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.import_btn.clicked.connect(self.import_csv)
        self.import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.import_btn.setMinimumHeight(40)

        self.export_btn = QPushButton("📤 Exporter CSV")
        self.export_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.export_btn.clicked.connect(self.export_csv)
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.setMinimumHeight(40)

        actions_layout.addWidget(self.import_btn)
        actions_layout.addWidget(self.export_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.edit_btn)
        actions_layout.addWidget(self.delete_btn)

        self.load_products()

    def build_stat_card(self, title, value, color):
        """Construit une carte de statistique"""
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

    def update_statistics(self):
        """Met à jour les statistiques"""
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        stats = self.db.get_statistics()
        low_stock = self.db.get_low_stock_products()
        
        self.stats_layout.addWidget(
            self.build_stat_card("Total Produits", stats['total_products'], COLORS['primary'])
        )
        self.stats_layout.addWidget(
            self.build_stat_card("Valeur Stock", f"{stats['stock_value']:,.0f} DA", COLORS['success'])
        )
        self.stats_layout.addWidget(
            self.build_stat_card("Stock Faible", len(low_stock), COLORS['danger'])
        )

    def load_products(self):
        """Charge les produits depuis la base"""
        self.table.setRowCount(0)
        products = self.db.get_all_products()
        
        for product in products:
            self.add_product_to_table(product)

    def add_product_to_table(self, product):
        """Ajoute un produit au tableau"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        id_item = QTableWidgetItem(str(product["id"]))
        id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        id_item.setData(Qt.ItemDataRole.UserRole, product["id"])
        self.table.setItem(row, 0, id_item)
        
        name_item = QTableWidgetItem(product["name"])
        self.table.setItem(row, 1, name_item)
        
        cat_item = QTableWidgetItem(product.get("category_name", "-"))
        self.table.setItem(row, 2, cat_item)
        
        qty_item = QTableWidgetItem(str(product["stock_quantity"]))
        qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if product["stock_quantity"] <= product.get("min_stock", 0):
            qty_item.setForeground(Qt.GlobalColor.red)
        self.table.setItem(row, 3, qty_item)
        
        price_buy_item = QTableWidgetItem(f"{product.get('purchase_price', 0):,.2f}")
        price_buy_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.table.setItem(row, 4, price_buy_item)
        
        price_item = QTableWidgetItem(f"{product['selling_price']:,.2f}")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.table.setItem(row, 5, price_item)
        
        total_value = product["stock_quantity"] * product["selling_price"]
        value_item = QTableWidgetItem(f"{total_value:,.2f}")
        value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        value_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.table.setItem(row, 6, value_item)

    def add_product(self):
        """Ajoute un nouveau produit"""
        dialog = ProductDialog()
        if dialog.exec():
            # Vérifier si la catégorie existe
            category_name = dialog.category.currentText().strip()
            category_id = None
            
            if category_name:
                categories = self.db.get_all_categories()
                category = next((c for c in categories if c['name'] == category_name), None)
                if not category:
                    category_id = self.db.add_category(category_name)
                else:
                    category_id = category['id']
            
            product_id = self.db.add_product(
                name=dialog.name.text().strip(),
                selling_price=dialog.price.value(),
                category_id=category_id,
                purchase_price=dialog.price_buy.value(),
                stock_quantity=dialog.quantity.value(),
                min_stock=dialog.min_stock.value()
            )
            
            if product_id:
                QMessageBox.information(self, "Succès", "Produit ajouté avec succès!")
                self.load_products()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible d'ajouter le produit!")

    def edit_product(self):
        """Modifie un produit"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit!")
            return
        
        product_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        product = self.db.get_product_by_id(product_id)
        
        if not product:
            QMessageBox.critical(self, "Erreur", "Produit introuvable!")
            return
        
        dialog = ProductDialog(product)
        if dialog.exec():
            category_name = dialog.category.currentText().strip()
            category_id = None
            
            if category_name:
                categories = self.db.get_all_categories()
                category = next((c for c in categories if c['name'] == category_name), None)
                if not category:
                    category_id = self.db.add_category(category_name)
                else:
                    category_id = category['id']
            
            if self.db.update_product(
                product_id=product_id,
                name=dialog.name.text().strip(),
                selling_price=dialog.price.value(),
                category_id=category_id,
                purchase_price=dialog.price_buy.value(),
                stock_quantity=dialog.quantity.value(),
                min_stock=dialog.min_stock.value()
            ):
                QMessageBox.information(self, "Succès", "Produit modifié avec succès!")
                self.load_products()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de modifier le produit!")

    def delete_product(self):
        """Supprime un produit"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit!")
            return
        
        product_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        product_name = self.table.item(selected, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer '{product_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_product(product_id):
                QMessageBox.information(self, "Succès", "Produit supprimé!")
                self.load_products()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de supprimer!")

    def filter_products(self, text):
        """Filtre les produits"""
        if not text:
            self.load_products()
            return
        
        self.table.setRowCount(0)
        products = self.db.search_products(text)
        for product in products:
            self.add_product_to_table(product)

    def import_csv(self):
        """Importe des produits depuis un CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le fichier CSV", "", "Fichiers CSV (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            imported = 0
            updated = 0
            errors = []
            
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                csv_reader = csv.DictReader(file)
                
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        name = row.get('name', '').strip()
                        
                        # Vérifier que le nom est présent (obligatoire)
                        if not name:
                            errors.append(f"Ligne {row_num}: Nom manquant")
                            continue
                        
                        # Nettoyer et convertir les prix (gérer les formats avec espaces et "DA")
                        try:
                            selling_price_str = row.get('price', row.get('selling_price', '0'))
                            selling_price_str = selling_price_str.replace(' ', '').replace('DA', '').replace(',', '.')
                            selling_price = float(selling_price_str) if selling_price_str else 0.0
                        except:
                            selling_price = 0.0
                        
                        try:
                            purchase_price_str = row.get('price_buy', row.get('purchase_price', '0'))
                            purchase_price_str = purchase_price_str.replace(' ', '').replace('DA', '').replace(',', '.')
                            purchase_price = float(purchase_price_str) if purchase_price_str else 0.0
                        except:
                            purchase_price = 0.0
                        
                        try:
                            stock = int(row.get('quantity', row.get('stock_quantity', 0)))
                        except:
                            stock = 0
                        
                        try:
                            min_stock = int(row.get('min_stock', 5))
                        except:
                            min_stock = 5
                        
                        # Récupérer la catégorie
                        category_name = row.get('category', row.get('category_name', '')).strip()
                        category_id = None
                        
                        if category_name:
                            categories = self.db.get_all_categories()
                            category = next((c for c in categories if c['name'] == category_name), None)
                            if not category:
                                category_id = self.db.add_category(category_name)
                            else:
                                category_id = category['id']
                        
                        # Ajouter le produit (on n'essaie plus de vérifier l'existence)
                        self.db.add_product(
                            name, selling_price,
                            category_id, "", purchase_price, stock, min_stock
                        )
                        imported += 1
                            
                    except Exception as e:
                        errors.append(f"Ligne {row_num}: {str(e)}")
            
            self.load_products()
            self.update_statistics()
            
            message = f"✅ Importés: {imported}\n🔄 Mis à jour: {updated}"
            if errors:
                message += f"\n❌ Erreurs: {len(errors)}\n\nPremières erreurs:\n"
                message += "\n".join(errors[:5])
            
            QMessageBox.information(self, "Import terminé", message)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'import:\n{str(e)}")

    def export_csv(self):
        """Exporte les produits vers un CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le fichier CSV", "produits.csv", "Fichiers CSV (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            products = self.db.get_all_products()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['id', 'name', 'category', 'stock_quantity',
                            'purchase_price', 'selling_price', 'min_stock']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for product in products:
                    writer.writerow({
                        'id': product['id'],
                        'name': product['name'],
                        'category': product.get('category_name', ''),
                        'stock_quantity': product['stock_quantity'],
                        'purchase_price': product['purchase_price'],
                        'selling_price': product['selling_price'],
                        'min_stock': product.get('min_stock', 0)
                    })
            
            QMessageBox.information(self, "Succès", 
                f"✅ {len(products)} produit(s) exporté(s)!")
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'export:\n{str(e)}")