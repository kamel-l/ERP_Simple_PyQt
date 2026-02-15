from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QLineEdit, QFormLayout, QHBoxLayout, QFrame, QFileDialog, QMessageBox,
    QSpinBox, QDoubleSpinBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
import csv


class ProductDialog(QDialog):
    """Dialogue pour ajouter ou modifier un produit"""
    def __init__(self, product_data=None):
        super().__init__()

        # Si product_data est fourni, c'est une modification, sinon c'est un ajout
        self.is_edit = product_data is not None
        
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

        # Référence / Code
        ref_label = QLabel("Référence:")
        ref_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.reference = QLineEdit()
        self.reference.setPlaceholderText("Ex: HP-LAPTOP-001")
        self.reference.setStyleSheet(INPUT_STYLE)
        self.reference.setMinimumHeight(45)
        form_layout.addRow(ref_label, self.reference)

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

        # Catégorie
        cat_label = QLabel("Catégorie:")
        cat_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.category = QLineEdit()
        self.category.setPlaceholderText("Ex: Informatique, Électronique...")
        self.category.setStyleSheet(INPUT_STYLE)
        self.category.setMinimumHeight(45)
        form_layout.addRow(cat_label, self.category)

        # Fournisseur
        supplier_label = QLabel("Fournisseur:")
        supplier_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        self.supplier = QLineEdit()
        self.supplier.setPlaceholderText("Nom du fournisseur")
        self.supplier.setStyleSheet(INPUT_STYLE)
        self.supplier.setMinimumHeight(45)
        form_layout.addRow(supplier_label, self.supplier)

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

    def load_product_data(self, product):
        """Charge les données du produit pour modification"""
        self.name.setText(product.get("name", ""))
        self.reference.setText(product.get("reference", ""))
        self.quantity.setValue(product.get("quantity", 0))
        self.price_buy.setValue(product.get("price_buy", 0.0))
        self.price.setValue(product.get("price", 0.0))
        self.category.setText(product.get("category", ""))
        self.supplier.setText(product.get("supplier", ""))

    def validate_and_accept(self):
        """Valide les données avant d'accepter"""
        # Vérification des champs obligatoires
        if not self.name.text().strip():
            QMessageBox.warning(self, "Champ obligatoire", 
                              "Le nom du produit est obligatoire !")
            self.name.setFocus()
            return
        
        if self.price.value() <= 0:
            QMessageBox.warning(self, "Prix invalide", 
                              "Le prix de vente doit être supérieur à 0 !")
            self.price.setFocus()
            return

        self.accept()

    def get_product_data(self):
        """Retourne les données du produit"""
        return {
            "name": self.name.text().strip(),
            "reference": self.reference.text().strip(),
            "quantity": self.quantity.value(),
            "price_buy": self.price_buy.value(),
            "price": self.price.value(),
            "category": self.category.text().strip(),
            "supplier": self.supplier.text().strip()
        }


class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # ------------------- HEADER -------------------
        title = QLabel("📦 Gestion des Produits")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Gérez votre inventaire et vos stocks")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # ------------------- STATISTICS CARDS -------------------
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        layout.addLayout(stats_layout)

        self.total_products_card = self.build_stat_card("Total Produits", "0", COLORS['primary'])
        self.total_stock_card = self.build_stat_card("Stock Total", "0", COLORS['success'])
        self.total_value_card = self.build_stat_card("Valeur Stock", "0 DA", COLORS['warning'])
        self.low_stock_card = self.build_stat_card("Stock Faible", "0", COLORS['danger'])
        
        stats_layout.addWidget(self.total_products_card)
        stats_layout.addWidget(self.total_stock_card)
        stats_layout.addWidget(self.total_value_card)
        stats_layout.addWidget(self.low_stock_card)
        stats_layout.addStretch()

        # ------------------- ACTION BAR -------------------
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        layout.addLayout(action_layout)

        # Barre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un produit par nom, référence ou catégorie...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.setMinimumHeight(45)
        self.search_input.textChanged.connect(self.filter_products)
        action_layout.addWidget(self.search_input)

        # Bouton Importer CSV
        import_btn = QPushButton("📥 Importer CSV")
        import_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        import_btn.setFixedWidth(160)
        import_btn.setMinimumHeight(45)
        import_btn.clicked.connect(self.import_csv)
        import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_btn.setToolTip("Importer des produits depuis un fichier CSV")
        action_layout.addWidget(import_btn)

        # Bouton Ajouter
        add_btn = QPushButton("➕ Nouveau Produit")
        add_btn.setStyleSheet(BUTTON_STYLES['primary'])
        add_btn.setFixedWidth(200)
        add_btn.setMinimumHeight(45)
        add_btn.clicked.connect(self.add_product)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        action_layout.addWidget(add_btn)

        # ------------------- PRODUCT TABLE -------------------
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

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "Nom", "Catégorie", "Quantité", 
            "Prix Achat", "Prix Vente", "Valeur Stock"
        ])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nom
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Catégorie
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.verticalHeader().setVisible(False)
        
        # Double-clic pour modifier
        self.table.doubleClicked.connect(self.edit_product)

        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

        # ------------------- ACTION BUTTONS -------------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        layout.addLayout(btn_layout)

        edit_btn = QPushButton("✏️ Modifier")
        edit_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        edit_btn.setMinimumHeight(40)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(self.edit_product)
        
        delete_btn = QPushButton("🗑️ Supprimer")
        delete_btn.setStyleSheet(BUTTON_STYLES['danger'])
        delete_btn.setMinimumHeight(40)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(self.delete_product)

        export_btn = QPushButton("📤 Exporter CSV")
        export_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        export_btn.setMinimumHeight(40)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self.export_csv)

        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)

        # ------------------- DONNÉES EXEMPLE -------------------
        self.products_data = [
            {
                "id": 1, 
                "name": "Ordinateur Portable HP", 
                "reference": "HP-001",
                "category": "Informatique",
                "quantity": 15, 
                "price_buy": 65000.00,
                "price": 75000.00,
                "supplier": "HP Distribution"
            },
            {
                "id": 2, 
                "name": "Souris Sans Fil Logitech", 
                "reference": "LOG-MS-100",
                "category": "Accessoires",
                "quantity": 50, 
                "price_buy": 1200.00,
                "price": 1500.00,
                "supplier": "Logitech SARL"
            },
            {
                "id": 3, 
                "name": "Clavier Mécanique RGB", 
                "reference": "KB-RGB-001",
                "category": "Accessoires",
                "quantity": 30, 
                "price_buy": 4000.00,
                "price": 5000.00,
                "supplier": "Tech Import"
            },
        ]
        self.load_products()
        self.update_statistics()

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
        card.setFixedHeight(90)
        card.setMinimumWidth(160)

        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setSpacing(5)
        card_layout.setContentsMargins(15, 12, 15, 12)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        card_layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        card_layout.addWidget(value_label)

        return card

    def update_statistics(self):
        """Met à jour les statistiques"""
        total_products = len(self.products_data)
        total_stock = sum(p["quantity"] for p in self.products_data)
        total_value = sum(p["quantity"] * p["price"] for p in self.products_data)
        low_stock = sum(1 for p in self.products_data if p["quantity"] < 10)

        # Mettre à jour les cartes
        self.total_products_card.findChild(QLabel, options=Qt.FindChildOption.FindDirectChildrenOnly).setText(str(total_products))
        self.total_stock_card.findChildren(QLabel)[1].setText(f"{total_stock:,}")
        self.total_value_card.findChildren(QLabel)[1].setText(f"{total_value:,.0f} DA")
        self.low_stock_card.findChildren(QLabel)[1].setText(str(low_stock))

    # ------------------ AJOUTER PRODUIT ------------------
    def add_product(self):
        """Ouvre le dialogue pour ajouter un produit"""
        dialog = ProductDialog()
        if dialog.exec():
            product_data = dialog.get_product_data()
            
            # Générer un nouvel ID
            new_id = max([p["id"] for p in self.products_data]) + 1 if self.products_data else 1
            product_data["id"] = new_id
            
            # Ajouter à la liste
            self.products_data.append(product_data)
            
            # Recharger le tableau et les stats
            self.load_products()
            self.update_statistics()
            
            # Message de succès
            QMessageBox.information(self, "Succès", 
                                  f"Le produit '{product_data['name']}' a été ajouté avec succès !")

    # ------------------ MODIFIER PRODUIT ------------------
    def edit_product(self):
        """Modifie le produit sélectionné"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Aucune sélection", 
                              "Veuillez sélectionner un produit à modifier !")
            return
        
        # Récupérer le produit
        product = self.products_data[selected]
        
        # Ouvrir le dialogue avec les données
        dialog = ProductDialog(product)
        if dialog.exec():
            # Mettre à jour les données
            updated_data = dialog.get_product_data()
            updated_data["id"] = product["id"]  # Garder le même ID
            self.products_data[selected] = updated_data
            
            # Recharger
            self.load_products()
            self.update_statistics()
            
            QMessageBox.information(self, "Succès", 
                                  f"Le produit '{updated_data['name']}' a été modifié !")

    # ------------------ SUPPRIMER PRODUIT ------------------
    def delete_product(self):
        """Supprime le produit sélectionné"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Aucune sélection", 
                              "Veuillez sélectionner un produit à supprimer !")
            return
        
        product = self.products_data[selected]
        
        # Confirmation
        reply = QMessageBox.question(self, "Confirmation", 
                                    f"Voulez-vous vraiment supprimer le produit '{product['name']}' ?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.products_data[selected]
            self.load_products()
            self.update_statistics()
            QMessageBox.information(self, "Succès", "Produit supprimé !")

    # ------------------ IMPORTER CSV ------------------
    def import_csv(self):
        """Importe des produits depuis un fichier CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier CSV",
            "",
            "Fichiers CSV (*.csv);;Tous les fichiers (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            errors = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                # Vérifier les colonnes requises
                required_fields = ['name', 'quantity', 'price']
                if not all(field in csv_reader.fieldnames for field in required_fields):
                    QMessageBox.critical(self, "Erreur de format", 
                        f"Le fichier CSV doit contenir au minimum les colonnes : {', '.join(required_fields)}")
                    return
                
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        # Générer un nouvel ID
                        new_id = max([p["id"] for p in self.products_data]) + 1 if self.products_data else 1
                        
                        # Créer le produit
                        product = {
                            "id": new_id,
                            "name": row['name'].strip(),
                            "reference": row.get('reference', '').strip(),
                            "category": row.get('category', '').strip(),
                            "quantity": int(row['quantity']),
                            "price_buy": float(row.get('price_buy', 0)),
                            "price": float(row['price']),
                            "supplier": row.get('supplier', '').strip()
                        }
                        
                        # Validation basique
                        if not product['name']:
                            errors.append(f"Ligne {row_num}: Nom vide")
                            continue
                        
                        if product['price'] <= 0:
                            errors.append(f"Ligne {row_num}: Prix invalide")
                            continue
                        
                        # Ajouter le produit
                        self.products_data.append(product)
                        imported_count += 1
                        
                    except (ValueError, KeyError) as e:
                        errors.append(f"Ligne {row_num}: {str(e)}")
            
            # Recharger le tableau
            self.load_products()
            self.update_statistics()
            
            # Message de résultat
            message = f"✅ {imported_count} produit(s) importé(s) avec succès !"
            if errors:
                message += f"\n\n⚠️ {len(errors)} erreur(s) :\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    message += f"\n... et {len(errors) - 5} autres erreurs"
            
            QMessageBox.information(self, "Import terminé", message)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'import", 
                               f"Erreur lors de l'import du fichier :\n{str(e)}")

    # ------------------ EXPORTER CSV ------------------
    def export_csv(self):
        """Exporte les produits vers un fichier CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le fichier CSV",
            "produits.csv",
            "Fichiers CSV (*.csv);;Tous les fichiers (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['id', 'reference', 'name', 'category', 'quantity', 
                            'price_buy', 'price', 'supplier']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for product in self.products_data:
                    writer.writerow(product)
            
            QMessageBox.information(self, "Succès", 
                                  f"✅ {len(self.products_data)} produit(s) exporté(s) vers :\n{file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'export", 
                               f"Erreur lors de l'export :\n{str(e)}")

    # ------------------ FILTRER PRODUITS ------------------
    def filter_products(self, text):
        """Filtre les produits selon le texte de recherche"""
        text = text.lower()
        filtered = [
            p for p in self.products_data 
            if text in p["name"].lower() 
            or text in p.get("reference", "").lower()
            or text in p.get("category", "").lower()
        ]
        
        self.table.setRowCount(0)
        for product in filtered:
            self.add_product_to_table(product)

    # ------------------ CHARGER PRODUITS ------------------
    def load_products(self):
        """Charge tous les produits dans le tableau"""
        self.table.setRowCount(0)
        for product in self.products_data:
            self.add_product_to_table(product)

    def add_product_to_table(self, product):
        """Ajoute un produit au tableau"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # ID
        id_item = QTableWidgetItem(str(product["id"]))
        id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, id_item)
        
        # Référence
        ref_item = QTableWidgetItem(product.get("reference", "-"))
        self.table.setItem(row, 1, ref_item)
        
        # Nom
        name_item = QTableWidgetItem(product["name"])
        self.table.setItem(row, 2, name_item)
        
        # Catégorie
        cat_item = QTableWidgetItem(product.get("category", "-"))
        self.table.setItem(row, 3, cat_item)
        
        # Quantité
        qty_item = QTableWidgetItem(str(product["quantity"]))
        qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        # Colorier en rouge si stock faible
        if product["quantity"] < 10:
            qty_item.setForeground(Qt.GlobalColor.red)
        self.table.setItem(row, 4, qty_item)
        
        # Prix d'achat
        price_buy_item = QTableWidgetItem(f"{product.get('price_buy', 0):,.2f}")
        price_buy_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.table.setItem(row, 5, price_buy_item)
        
        # Prix de vente
        price_item = QTableWidgetItem(f"{product['price']:,.2f}")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.table.setItem(row, 6, price_item)
        
        # Valeur totale
        total_value = product["quantity"] * product["price"]
        value_item = QTableWidgetItem(f"{total_value:,.2f}")
        value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        value_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.table.setItem(row, 7, value_item)